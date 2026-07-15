#!/usr/bin/env python3
"""Independent end-to-end operational audit for the DGX Foundry deployment."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib import request

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
MODEL = "/home/chronos/models/qwen3.6-35b-a3b"


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()


def parse_time(value: str | None) -> datetime | None:
    if not value: return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def norm(text: str) -> str:
    import re
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def certified_stall(rows: list[dict], threshold: int) -> bool:
    terminal = []
    for row in reversed(rows):
        if row.get("classification") not in {"blocked", "negative_result"}: break
        terminal.append(row)
    terminal.reverse()
    if len(terminal) < threshold or len(terminal) < 2: return False
    a, b = terminal[-2:]
    structured_match = bool(a.get("frontier_id") and a.get("frontier_id") == b.get("frontier_id"))
    same_frontier = structured_match or difflib.SequenceMatcher(None, norm(a["frontier"]), norm(b["frontier"])).ratio() >= 0.75
    same_move = difflib.SequenceMatcher(None, norm(a["result"] + " " + a["next_gate"]), norm(b["result"] + " " + b["next_gate"])).ratio() >= 0.80
    return same_frontier or same_move


def publication_quarantines_consistent(receipts: list[dict], incidents: list[dict], ingest_state: dict) -> bool:
    quarantines = [row for row in incidents if row.get("schema") == "p42-foundry-publication-incident-v1"]
    if not quarantines:
        return False
    rejected_hashes = set(ingest_state.get("rejected", {}).values())
    admitted_hashes = {row.get("source", {}).get("sha256") for row in receipts}
    return all(
        row.get("status") == "quarantined_before_publication"
        and row.get("source_sha256") in rejected_hashes
        and row.get("source_sha256") not in admitted_hashes
        for row in quarantines
    )


def private_holdout_committed(manifest_path: Path, commitment_path: Path) -> bool:
    try:
        manifest = json.loads(manifest_path.read_text())
        commitment = json.loads(commitment_path.read_text())
    except (OSError, ValueError):
        return False
    tasks = manifest.get("tasks", [])
    counts = dict(sorted(Counter(row.get("family") for row in tasks).items()))
    canonical = json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    expected = "sha256:" + hashlib.sha256(canonical).hexdigest()
    forbidden_public_keys = {"tasks", "task_ids", "problem_ids", "split_salt_hex"}
    try:
        private_modes = (
            manifest_path.parent.stat().st_mode & 0o777 == 0o700
            and manifest_path.stat().st_mode & 0o777 == 0o600
        )
    except OSError:
        return False
    return bool(
        manifest.get("schema") == "p42-foundry-private-eval-suite-v1"
        and commitment.get("schema") == "p42-foundry-private-suite-commitment-v1"
        and private_modes
        and commitment.get("manifest_sha256") == expected
        and commitment.get("task_count") == len(tasks)
        and commitment.get("family_counts") == counts
        and commitment.get("task_ids_or_problem_ids_disclosed") is False
        and not forbidden_public_keys.intersection(commitment)
        and all(commitment.get(key) == manifest.get(key) for key in (
            "suite_version", "atlas_version", "public_suite_version"
        ))
    )


def tool_call_smoke() -> tuple[bool, dict]:
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": "Call foundry_probe exactly once. Do not answer directly."}],
        "tools": [{"type": "function", "function": {"name": "foundry_probe", "description": "Foundry liveness probe", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}}],
        "tool_choice": "required", "max_tokens": 128, "temperature": 0,
        "chat_template_kwargs": {"enable_thinking": False},
    }).encode()
    try:
        req = request.Request("http://127.0.0.1:30000/v1/chat/completions", data=body, headers={"Content-Type": "application/json"})
        with request.urlopen(req, timeout=60) as response: data = json.loads(response.read())
        calls = data["choices"][0]["message"].get("tool_calls") or []
        ok = len(calls) == 1 and calls[0].get("function", {}).get("name") == "foundry_probe"
        return ok, {"tool_call_count": len(calls), "tool_name": calls[0].get("function", {}).get("name") if calls else None}
    except Exception as exc:
        return False, {"error": type(exc).__name__ + ": " + str(exc)[:180]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ap.add_argument("--allow-incomplete", action="store_true")
    ap.add_argument("--data-root", type=Path, default=HOME / "cultural-soliton-observatory" / "data")
    ap.add_argument("--sessions-root", type=Path, default=HOME / "cultural-soliton-observatory" / "research_sessions")
    ap.add_argument("--cron-root", type=Path, default=HOME / ".hermes" / "cron")
    ap.add_argument("--state-root", type=Path, default=HOME / ".hermes" / "chronos_state")
    ap.add_argument("--ingest-state", type=Path, default=HOME / ".hermes" / "chronos_state" / "foundry_ingest_state.json")
    args = ap.parse_args()
    now = datetime.now(timezone.utc)
    config = json.loads((ROOT / "foundry" / "config.json").read_text())
    receipt_paths = sorted((ROOT / "progress" / "receipts").glob("**/*.json"))
    receipts = [json.loads(path.read_text()) for path in receipt_paths]
    incidents = [json.loads(path.read_text()) for path in (ROOT / "progress" / "incidents").glob("*.json")]
    ingest_state = json.loads(args.ingest_state.read_text()) if args.ingest_state.exists() else {"rejected": {}}
    by_id = {row["receipt_id"]: row for row in receipts}
    before = {name: sha_file(args.data_root / name) for name in ("atlas.db", "atlas2.db", "arena_atlas.db")}

    jobs_data = json.loads((args.cron_root / "jobs.json").read_text())
    jobs = {j["id"]: j for j in (jobs_data.get("jobs", jobs_data) if isinstance(jobs_data, dict) else jobs_data)}
    scout, night, publisher = (jobs[x] for x in ("50c8e4391849", "e97056701b6d", "d731670a1da7"))
    recent_cutoff = now - timedelta(minutes=90)
    budget = json.loads((args.state_root / "foundry_frontier_budget.json").read_text()) if (args.state_root / "foundry_frontier_budget.json").exists() else {"calls": []}
    efficiency_path = args.state_root / "foundry_efficiency_latest.json"
    efficiency = json.loads(efficiency_path.read_text()) if efficiency_path.exists() else None
    private_manifest_path = args.state_root / "foundry_eval" / "private_suite.json"
    public_commitment_path = ROOT / "foundry" / "eval" / "private_suite.commitment.json"
    public_commitment = json.loads(public_commitment_path.read_text()) if public_commitment_path.exists() else None
    calls = budget.get("calls", [])
    call_evidence = []
    for call in calls:
        rows = [by_id[rid] for rid in call.get("gate_receipts", []) if rid in by_id]
        frontier_id = call.get("frontier_id")
        lane_aligned = bool(frontier_id and rows and all(row.get("frontier_id") == frontier_id for row in rows))
        certified = bool(lane_aligned and certified_stall(rows, int(config["stall_threshold"])))
        call_evidence.append({
            "at": call.get("at"), "frontier_id": frontier_id, "lane_aligned": lane_aligned,
            "certified_stall": certified, "incident_acknowledged": bool(call.get("incident")),
            "answer_sha256": call.get("answer_sha256"),
        })
    ordered_times = [parse_time(call.get("at")) for call in calls]
    cooldown = timedelta(minutes=int(config["frontier_cooldown_minutes"]))
    cooldown_ok = all(b - a >= cooldown for a, b in zip(ordered_times, ordered_times[1:]) if a and b)
    daily_counts = {}
    for when in ordered_times:
        if when: daily_counts[when.date().isoformat()] = daily_counts.get(when.date().isoformat(), 0) + 1
    daily_ok = all(n <= int(config["frontier_calls_per_utc_day"]) for n in daily_counts.values())

    tool_ok, tool_evidence = tool_call_smoke()
    validate = run([sys.executable, str(ROOT / "tools" / "foundry.py"), "validate"])
    cron_status = run([str(HOME / ".hermes" / "hermes-agent" / "venv" / "bin" / "hermes"), "cron", "status"])
    cron_healthy = (
        cron_status.returncode == 0
        and "cron jobs will fire automatically" in cron_status.stdout
        and "STALLED" not in cron_status.stdout
    )
    local_head = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    remote_line = run(["git", "ls-remote", "origin", "refs/heads/automation/frontier-scout"]).stdout.strip()
    remote_head = remote_line.split()[0] if remote_line else None
    active = {unit: run(["systemctl", "--user", "is-active", unit]).stdout.strip() for unit in ("chronos-sglang.service", "hermes-gateway.service")}
    enabled = {unit: run(["systemctl", "--user", "is-enabled", unit]).stdout.strip() for unit in ("chronos-sglang.service", "hermes-gateway.service")}
    linger = run(["loginctl", "show-user", str(HOME.name), "-p", "Linger", "--value"]).stdout.strip()

    latest_id = (args.sessions_root / "latest").read_text().strip()
    packet = json.loads((args.sessions_root / latest_id / "context_packet.json").read_text())
    packet_ro = all(row.get("read_only_verified") is True and row.get("hash_before") == row.get("hash_after") for row in packet.get("databases", {}).values())
    focused_path = args.sessions_root / latest_id / "focused_context.json"
    focused = json.loads(focused_path.read_text()) if focused_path.exists() else None
    focused_ro = bool(focused and focused.get("databases") and focused.get("sources") and all(
        row.get("read_only_verified") is True and row.get("hash_before") == row.get("hash_after")
        for group in (focused["databases"], focused["sources"])
        for row in group.values()
    ))
    shadow_path = args.sessions_root / latest_id / "shadow_policy.json"
    shadow = json.loads(shadow_path.read_text()) if shadow_path.exists() else None
    after = {name: sha_file(args.data_root / name) for name in before}
    runtime_pairs = {
        "scout_prep": (ROOT / "foundry" / "dgx_research_prep.py", HOME / ".hermes" / "scripts" / "chronos_frontier_scout_prep.py"),
        "night_prep": (ROOT / "foundry" / "dgx_research_prep.py", HOME / ".hermes" / "scripts" / "chronos_frontier_night_prep.py"),
        "publisher_entrypoint": (ROOT / "foundry" / "dgx_tick.py", HOME / ".hermes" / "scripts" / "erdos_foundry_tick.py"),
        "foundry_skill": (ROOT / "foundry" / "SKILL.md", HOME / ".hermes" / "skills" / "foundry" / "SKILL.md"),
    }
    runtime_hashes = {
        name: {"source": sha_file(source), "installed": sha_file(installed) if installed.exists() else None}
        for name, (source, installed) in runtime_pairs.items()
    }
    traced = [row for row in receipts if row.get("frontier_consult")]
    executed = [row for row in traced if row["frontier_consult"].get("executed")]
    valid_calls = [row for row in call_evidence if row["lane_aligned"] and row["certified_stall"]]
    aligned_executions = [
        receipt for receipt in executed for call in valid_calls
        if receipt.get("frontier_id") == call["frontier_id"]
        and receipt["frontier_consult"].get("advice_digest") == "sha256:" + str(call["answer_sha256"])
    ]

    checks = {
        "sglang_active_enabled": active["chronos-sglang.service"] == "active" and enabled["chronos-sglang.service"] == "enabled",
        "gateway_active_enabled_linger": active["hermes-gateway.service"] == "active" and enabled["hermes-gateway.service"] == "enabled" and linger == "yes",
        "scheduler_ticker_healthy": cron_healthy,
        "structured_tool_call": tool_ok,
        "scout_local_35b_30m_recent": scout.get("provider") == "foundry-qwen35b" and scout.get("model") == MODEL and scout.get("schedule", {}).get("minutes") == 30 and scout.get("last_status") == "ok" and (parse_time(scout.get("last_run_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= recent_cutoff,
        "night_shift_local_35b": night.get("provider") == "foundry-qwen35b" and night.get("model") == MODEL and night.get("last_status") == "ok",
        "publisher_30m_recent": publisher.get("schedule", {}).get("minutes") == 30 and publisher.get("last_status") == "ok" and (parse_time(publisher.get("last_run_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= recent_cutoff,
        "foundry_and_atlas_validation": validate.returncode == 0,
        "semantic_target_contracts_active": bool(config.get("semantic_contracts")),
        "publication_quarantines_consistent": publication_quarantines_consistent(receipts, incidents, ingest_state),
        "automation_branch_current": bool(remote_head) and local_head == remote_head,
        "installed_runtime_matches_repo": all(row["source"] == row["installed"] for row in runtime_hashes.values()),
        "frontier_call_incidents_acknowledged": bool(calls) and all(row["certified_stall"] or row["incident_acknowledged"] for row in call_evidence),
        "valid_frontier_call_lane_certified": bool(valid_calls),
        "frontier_budget_and_cooldown_held": daily_ok and cooldown_ok,
        "frontier_state_private": (args.state_root / "foundry_frontier_budget.json").stat().st_mode & 0o777 == 0o600,
        "lane_aligned_frontier_advice_executed_trace": bool(aligned_executions),
        "latest_context_read_only": packet_ro,
        "latest_focused_retrieval_read_only": focused_ro,
        "latest_shadow_policy_observe_only": bool(shadow and shadow.get("policy_status") == "shadow_only_no_control_authority"),
        "efficiency_metrics_fresh_private_no_authority": bool(
            efficiency
            and efficiency.get("schema") == "p42-foundry-efficiency-v1"
            and efficiency.get("promotion_authority") == "none_metrics_only"
            and efficiency.get("aggregate", {}).get("completed_sessions", 0) > 0
            and (parse_time(efficiency.get("generated_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= recent_cutoff
            and efficiency_path.stat().st_mode & 0o777 == 0o600
        ),
        "private_holdout_committed_and_isolated": private_holdout_committed(
            private_manifest_path, public_commitment_path
        ),
        "protected_hashes_stable_during_audit": before == after,
    }
    report = {
        "schema": "p42-foundry-operational-audit-v1",
        "audited_at": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "overall": all(checks.values()),
        "checks": checks,
        "evidence": {
            "receipt_count": len(receipts), "traced_consults": len(traced), "executed_consults": len(executed),
            "publication_incidents": len([row for row in incidents if row.get("schema") == "p42-foundry-publication-incident-v1"]),
            "private_rejected_sources": len(ingest_state.get("rejected", {})),
            "frontier_calls": len(calls), "call_evidence": call_evidence, "valid_frontier_calls": len(valid_calls),
            "lane_aligned_executions": len(aligned_executions), "daily_call_counts": daily_counts,
            "tool_smoke": tool_evidence, "local_head": local_head, "remote_head": remote_head,
            "service_active": active, "service_enabled": enabled, "linger": linger,
            "cron_status_tail": [line.strip() for line in cron_status.stdout.splitlines() if line.strip()][-4:],
            "frontier_state_mode": oct((args.state_root / "foundry_frontier_budget.json").stat().st_mode & 0o777),
            "runtime_hashes": runtime_hashes,
            "latest_session": latest_id, "focused_retrieval_present": focused_path.exists(),
            "focused_hit_counts": ({name: len(rows) for name, rows in focused.get("surfaces", {}).items()} if focused else {}),
            "shadow_policy_present": shadow_path.exists(),
            "shadow_selected_frontier_id": shadow.get("shadow_selected_frontier_id") if shadow else None,
            "efficiency_metrics_present": efficiency_path.exists(),
            "efficiency_metrics_mode": oct(efficiency_path.stat().st_mode & 0o777) if efficiency_path.exists() else None,
            "efficiency_metrics_generated_at": efficiency.get("generated_at") if efficiency else None,
            "efficiency_metrics_aggregate": efficiency.get("aggregate") if efficiency else None,
            "private_holdout_commitment": public_commitment,
            "private_holdout_manifest_mode": oct(private_manifest_path.stat().st_mode & 0o777) if private_manifest_path.exists() else None,
            "private_holdout_parent_mode": oct(private_manifest_path.parent.stat().st_mode & 0o777) if private_manifest_path.parent.exists() else None,
            "protected_hashes_before": before, "protected_hashes_after": after,
            "validation_tail": validate.stdout.strip().splitlines()[-1] if validate.stdout.strip() else None,
        },
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.output.with_suffix(args.output.suffix + ".tmp")
        tmp.write_text(rendered); tmp.replace(args.output)
    print(rendered, end="")
    return 0 if report["overall"] or args.allow_incomplete else 1


if __name__ == "__main__":
    raise SystemExit(main())

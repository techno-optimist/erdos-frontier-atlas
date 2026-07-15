#!/usr/bin/env python3
"""Independent end-to-end operational audit for the DGX Foundry deployment."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
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


def configured_api_retry_budget(path: Path) -> int:
    try:
        match = re.search(r"(?m)^\s*api_max_retries:\s*(\d+)\s*$", path.read_text())
    except OSError:
        return 0
    return int(match.group(1)) if match else 0


def parser_source_digest() -> str:
    return "sha256:" + sha_file(ROOT / "tools" / "foundry_efficiency.py")


def telemetry_contract_digest(config: dict) -> str:
    canonical = json.dumps(
        {
            "runtime_budget": config.get("runtime_budget"),
            "parser_source_sha256": parser_source_digest(),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def semantic_contract_digest(config: dict) -> str:
    canonical = json.dumps(
        {
            "semantic_contracts": config.get("semantic_contracts", {}),
            "milestone_policy": config.get("milestone_policy", {}),
            "runtime_budget": config.get("runtime_budget"),
            "runtime_telemetry_contract_digest": telemetry_contract_digest(config),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def runtime_budget_digest(config: dict) -> str | None:
    budget = config.get("runtime_budget")
    if not isinstance(budget, dict):
        return None
    canonical = json.dumps(
        budget, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def scheduled_worker_policy_current(job: dict, config: dict) -> bool:
    runtime = config.get("runtime_budget", {})
    milestone = config.get("milestone_policy", {})
    prompt = str(job.get("prompt", ""))
    normalized = " ".join(prompt.split())
    turns = runtime.get("scheduled_job_max_turns")
    receipt_call = milestone.get("receipt_deadline_call")
    return bool(
        job.get("enabled") is True
        and job.get("state") != "paused"
        and prompt.count("FOUNDRY HARD RUNTIME BUDGET") == 1
        and prompt.count("FOUNDRY MILESTONE CONTRACT") == 1
        and job.get("finalize_no_tools_after") == milestone.get("final_replay_call")
        and f"at most {turns} model calls" in normalized
        and f"rejects a run above {turns} calls" in normalized
        and f"assistant response by call {receipt_call}" in normalized
        and "Do not write the final receipt to a file" in normalized
    )


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


def structured_quarantine_feedback_consistent(
    ingest_state: dict, contract_digest: str | None = None
) -> bool:
    rejected = ingest_state.get("rejected", {})
    details = ingest_state.get("rejected_details", {})
    if not rejected:
        return False
    return all(
        isinstance(details.get(key), dict)
        and details[key].get("schema") == "p42-foundry-quarantine-feedback-v1"
        and details[key].get("source_sha256") == source_sha
        and isinstance(details[key].get("errors"), list)
        and bool(details[key]["errors"])
        and (
            contract_digest is None
            or details[key].get("semantic_contract_digest") == contract_digest
        )
        and key not in ingest_state.get("accepted", {})
        for key, source_sha in rejected.items()
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


def model_transport_verified(report: dict | None, path: Path, cutoff: datetime) -> bool:
    try:
        private_mode = path.stat().st_mode & 0o777 == 0o600
    except OSError:
        return False
    return bool(
        report
        and report.get("schema") == "p42-foundry-model-transport-v1"
        and report.get("ok") is True
        and report.get("mode") == "smoke"
        and report.get("candidate_network") == "none"
        and report.get("model_transport") == "mounted_unix_socket_only"
        and report.get("model_upstream") == "evaluator_loopback_only"
        and report.get("model_upstream_host") == "127.0.0.1"
        and report.get("model_upstream_port") == 30000
        and report.get("private_manifest_mounted") is False
        and report.get("docker_socket_mounted") is False
        and report.get("budget", {}).get("budget_ok") is True
        and report.get("promotion_authority") == "none_pending_independent_replay"
        and private_mode
        and (parse_time(report.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= cutoff
    )


def independent_replay_verified(report: dict | None, path: Path, cutoff: datetime) -> bool:
    try:
        private_mode = path.stat().st_mode & 0o777 == 0o600
    except OSError:
        return False
    boundary = report.get("replay_boundary", {}) if report else {}
    replays = report.get("replays", []) if report else []
    artifacts = report.get("artifact_inventory", []) if report else []
    return bool(
        report
        and report.get("schema") == "p42-foundry-independent-replay-v1"
        and report.get("mode") == "synthetic_boundary_smoke_no_rsi_claim"
        and report.get("scope") == "contract_smoke"
        and report.get("ok") is True
        and report.get("verified_utility_units") == 0
        and report.get("artifact_replay_ok") is True
        and report.get("canonical_math_verdict") == "pending_evaluator_owned_verifier"
        and report.get("promotion_authority") == "none_smoke_only"
        and report.get("evaluator_tree_clean") is True
        and str(report.get("image_id", "")).startswith("sha256:")
        and boundary.get("candidate_network") == "none"
        and boundary.get("root_filesystem") == "read_only"
        and boundary.get("candidate_workspace_mounted") is False
        and boundary.get("model_transport_mounted") is False
        and boundary.get("private_manifest_mounted") is False
        and boundary.get("docker_socket_mounted") is False
        and bool(artifacts)
        and all(str(row.get("sha256", "")).startswith("sha256:") for row in artifacts)
        and bool(replays)
        and all(row.get("ok") is True for row in replays)
        and private_mode
        and (parse_time(report.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= cutoff
    )


def paired_evaluation_verified(report: dict | None, path: Path, cutoff: datetime) -> bool:
    try:
        private_mode = path.stat().st_mode & 0o777 == 0o600
    except OSError:
        return False
    return bool(
        report
        and report.get("schema") == "p42-foundry-paired-evaluation-v1"
        and report.get("paired_runs", 0) > 0
        and report.get("fixed_budget_evidence_matched") is True
        and report.get("all_replays_operational") is True
        and report.get("automatic_production_promotion") is False
        and report.get("promotion_authority") == "none_human_review_required"
        and report.get("claim_status") in {
            "development_evidence_only", "promotion_candidate_human_review_required"
        }
        and private_mode
        and (parse_time(report.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= cutoff
    )


def canonical_reward_boundary_locked(
    protocol: dict | None, contracts: dict | None, verifier_path: Path
) -> bool:
    registered = {"1", "21", "138", "552"}
    rows = contracts.get("contracts", {}) if contracts else {}
    return bool(
        protocol
        and protocol.get("schema") == "p42-foundry-adjudication-protocol-v1"
        and protocol.get("generic_replay_utility_cap") == 0
        and protocol.get("paired_comparison", {}).get("automatic_production_promotion") is False
        and protocol.get("paired_comparison", {}).get("human_review_required") is True
        and contracts
        and contracts.get("schema") == "p42-foundry-canonical-contract-registry-v1"
        and set(rows) == registered
        and all(rows[key].get("verifier_id") for key in registered)
        and verifier_path.is_file()
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
    api_retry_budget = configured_api_retry_budget(HOME / ".hermes" / "config.yaml")
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
    model_transport_path = args.state_root / "foundry_eval" / "model_transport_smoke.json"
    model_transport = json.loads(model_transport_path.read_text()) if model_transport_path.exists() else None
    replay_smoke_path = args.state_root / "foundry_eval" / "replay_smoke.json"
    replay_smoke = json.loads(replay_smoke_path.read_text()) if replay_smoke_path.exists() else None
    paired_eval_path = args.state_root / "foundry_eval" / "paired_evaluation_latest.json"
    paired_eval = json.loads(paired_eval_path.read_text()) if paired_eval_path.exists() else None
    adjudication_protocol_path = ROOT / "foundry" / "adjudication_protocol.json"
    adjudication_protocol = json.loads(adjudication_protocol_path.read_text()) if adjudication_protocol_path.exists() else None
    canonical_contracts_path = ROOT / "foundry" / "eval" / "canonical_contracts.json"
    canonical_contracts = json.loads(canonical_contracts_path.read_text()) if canonical_contracts_path.exists() else None
    canonical_verifier_path = ROOT / "tools" / "foundry_canonical_verify.py"
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
    runtime_budget = config.get("runtime_budget", {})
    scheduler_path = HOME / ".hermes" / "hermes-agent" / "cron" / "scheduler.py"
    scheduler_text = scheduler_path.read_text() if scheduler_path.exists() else ""
    conversation_loop_path = HOME / ".hermes" / "hermes-agent" / "agent" / "conversation_loop.py"
    conversation_loop_text = (
        conversation_loop_path.read_text() if conversation_loop_path.exists() else ""
    )
    runtime_budget_enforced = bool(
        runtime_budget
        and efficiency
        and efficiency.get("runtime_budget_digest") == runtime_budget_digest(config)
        and efficiency.get("telemetry_contract_digest") == telemetry_contract_digest(config)
        and "FOUNDRY_JOB_MAX_TURNS_V1" in scheduler_text
        and "FOUNDRY_JOB_MAX_WALL_SECONDS_V1" in scheduler_text
        and "FOUNDRY_JOB_FINALIZE_NO_TOOLS_V2" in scheduler_text
        and "FOUNDRY_REQUIRED_RECEIPT_RETRY_V1" in conversation_loop_text
        and all(
            job.get("max_turns") == runtime_budget.get("scheduled_job_max_turns")
            and job.get("max_wall_seconds") == runtime_budget.get("max_wall_seconds")
            and job.get("finalize_no_tools_after") == config.get("milestone_policy", {}).get("final_replay_call")
            for job in (scout, night)
        )
    )
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
        "gateway_retry_budget_covers_cold_restart": api_retry_budget >= 8,
        "structured_tool_call": tool_ok,
        "scout_local_35b_30m_recent": scout.get("enabled") is True and scout.get("state") != "paused" and scout.get("provider") == "foundry-qwen35b" and scout.get("model") == MODEL and scout.get("schedule", {}).get("minutes") == 30 and scout.get("last_status") == "ok" and (parse_time(scout.get("last_run_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= recent_cutoff,
        "night_shift_local_35b": night.get("enabled") is True and night.get("state") != "paused" and night.get("provider") == "foundry-qwen35b" and night.get("model") == MODEL and night.get("last_status") == "ok",
        "publisher_30m_recent": publisher.get("enabled") is True and publisher.get("state") != "paused" and publisher.get("schedule", {}).get("minutes") == 30 and publisher.get("last_status") == "ok" and (parse_time(publisher.get("last_run_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= recent_cutoff,
        "scheduled_worker_policy_current": all(
            scheduled_worker_policy_current(job, config) for job in (scout, night)
        ),
        "foundry_and_atlas_validation": validate.returncode == 0,
        "semantic_target_contracts_active": bool(config.get("semantic_contracts")),
        "publication_quarantines_consistent": publication_quarantines_consistent(receipts, incidents, ingest_state),
        "structured_quarantine_feedback_consistent": structured_quarantine_feedback_consistent(
            ingest_state, semantic_contract_digest(config)
        ),
        "automation_branch_current": bool(remote_head) and local_head == remote_head,
        "installed_runtime_matches_repo": all(row["source"] == row["installed"] for row in runtime_hashes.values()),
        "runtime_budget_membrane_enforced": runtime_budget_enforced,
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
        "model_only_eval_transport_verified": model_transport_verified(
            model_transport, model_transport_path, now - timedelta(hours=24)
        ),
        "independent_replay_adjudicator_verified": independent_replay_verified(
            replay_smoke, replay_smoke_path, now - timedelta(hours=24)
        ),
        "paired_fixed_budget_evaluation_executed": paired_evaluation_verified(
            paired_eval, paired_eval_path, now - timedelta(hours=24)
        ),
        "canonical_verifier_reward_boundary_locked": canonical_reward_boundary_locked(
            adjudication_protocol, canonical_contracts, canonical_verifier_path
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
            "structured_quarantine_feedback": len(ingest_state.get("rejected_details", {})),
            "frontier_calls": len(calls), "call_evidence": call_evidence, "valid_frontier_calls": len(valid_calls),
            "lane_aligned_executions": len(aligned_executions), "daily_call_counts": daily_counts,
            "tool_smoke": tool_evidence, "local_head": local_head, "remote_head": remote_head,
            "service_active": active, "service_enabled": enabled, "linger": linger,
            "api_max_retries": api_retry_budget,
            "cron_status_tail": [line.strip() for line in cron_status.stdout.splitlines() if line.strip()][-4:],
            "frontier_state_mode": oct((args.state_root / "foundry_frontier_budget.json").stat().st_mode & 0o777),
            "runtime_hashes": runtime_hashes,
            "runtime_budget": runtime_budget,
            "runtime_budget_digest": runtime_budget_digest(config),
            "efficiency_runtime_budget_digest": efficiency.get("runtime_budget_digest") if efficiency else None,
            "telemetry_contract_digest": telemetry_contract_digest(config),
            "efficiency_telemetry_contract_digest": efficiency.get("telemetry_contract_digest") if efficiency else None,
            "efficiency_parser_source_sha256": efficiency.get("parser_source_sha256") if efficiency else None,
            "scheduler_job_max_turns_marker": "FOUNDRY_JOB_MAX_TURNS_V1" in scheduler_text,
            "scheduler_job_max_wall_marker": "FOUNDRY_JOB_MAX_WALL_SECONDS_V1" in scheduler_text,
            "scheduler_job_finalize_no_tools_marker": "FOUNDRY_JOB_FINALIZE_NO_TOOLS_V2" in scheduler_text,
            "conversation_loop_receipt_retry_marker": "FOUNDRY_REQUIRED_RECEIPT_RETRY_V1" in conversation_loop_text,
            "scheduled_job_max_turns": {job["id"]: job.get("max_turns") for job in (scout, night)},
            "scheduled_job_max_wall_seconds": {job["id"]: job.get("max_wall_seconds") for job in (scout, night)},
            "scheduled_job_finalize_no_tools_after": {job["id"]: job.get("finalize_no_tools_after") for job in (scout, night)},
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
            "model_transport_smoke": ({
                key: model_transport.get(key) for key in (
                    "schema", "created_at", "ok", "mode", "image_id", "candidate_network",
                    "model_transport", "model_upstream", "model_upstream_host",
                    "model_upstream_port", "private_manifest_mounted",
                    "docker_socket_mounted", "budget", "promotion_authority",
                )
            } if model_transport else None),
            "model_transport_report_mode": oct(model_transport_path.stat().st_mode & 0o777) if model_transport_path.exists() else None,
            "independent_replay_smoke": ({
                key: replay_smoke.get(key) for key in (
                    "schema", "created_at", "mode", "ok", "scope", "image_id",
                    "evaluator_revision", "evaluator_tree_clean", "artifact_replay_ok",
                    "verified_utility_units",
                    "canonical_math_verdict", "replay_boundary", "promotion_authority",
                )
            } if replay_smoke else None),
            "independent_replay_report_mode": oct(replay_smoke_path.stat().st_mode & 0o777) if replay_smoke_path.exists() else None,
            "paired_evaluation": ({
                key: paired_eval.get(key) for key in (
                    "schema", "created_at", "baseline_id", "candidate_id", "paired_runs",
                    "private_paired_runs", "public_paired_runs", "private_wins",
                    "bootstrap_lower_bound", "fixed_budget_evidence_matched",
                    "all_replays_operational",
                    "promotion_eligible", "claim_status", "automatic_production_promotion",
                    "promotion_authority",
                )
            } if paired_eval else None),
            "paired_evaluation_report_mode": oct(paired_eval_path.stat().st_mode & 0o777) if paired_eval_path.exists() else None,
            "canonical_verifier_registry": {
                "protocol_schema": adjudication_protocol.get("schema") if adjudication_protocol else None,
                "generic_replay_utility_cap": adjudication_protocol.get("generic_replay_utility_cap") if adjudication_protocol else None,
                "contract_count": len(canonical_contracts.get("contracts", {})) if canonical_contracts else 0,
                "verifier_source_sha256": sha_file(canonical_verifier_path) if canonical_verifier_path.exists() else None,
            },
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

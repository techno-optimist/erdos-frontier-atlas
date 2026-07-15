#!/usr/bin/env python3
"""Independent end-to-end operational audit for the DGX Foundry deployment."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import subprocess
import sys
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
    same_frontier = difflib.SequenceMatcher(None, norm(a["frontier"]), norm(b["frontier"])).ratio() >= 0.75
    same_move = difflib.SequenceMatcher(None, norm(a["result"] + " " + a["next_gate"]), norm(b["result"] + " " + b["next_gate"])).ratio() >= 0.80
    return same_frontier or same_move


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
    args = ap.parse_args()
    now = datetime.now(timezone.utc)
    config = json.loads((ROOT / "foundry" / "config.json").read_text())
    receipt_paths = sorted((ROOT / "progress" / "receipts").glob("**/*.json"))
    receipts = [json.loads(path.read_text()) for path in receipt_paths]
    by_id = {row["receipt_id"]: row for row in receipts}
    before = {name: sha_file(args.data_root / name) for name in ("atlas.db", "atlas2.db", "arena_atlas.db")}

    jobs_data = json.loads((args.cron_root / "jobs.json").read_text())
    jobs = {j["id"]: j for j in (jobs_data.get("jobs", jobs_data) if isinstance(jobs_data, dict) else jobs_data)}
    scout, night, publisher = (jobs[x] for x in ("50c8e4391849", "e97056701b6d", "d731670a1da7"))
    recent_cutoff = now - timedelta(minutes=90)
    budget = json.loads((args.state_root / "foundry_frontier_budget.json").read_text()) if (args.state_root / "foundry_frontier_budget.json").exists() else {"calls": []}
    calls = budget.get("calls", [])
    call_stalls = []
    for call in calls:
        rows = [by_id[rid] for rid in call.get("gate_receipts", []) if rid in by_id]
        call_stalls.append(bool(rows) and certified_stall(rows, int(config["stall_threshold"])))
    ordered_times = [parse_time(call.get("at")) for call in calls]
    cooldown = timedelta(minutes=int(config["frontier_cooldown_minutes"]))
    cooldown_ok = all(b - a >= cooldown for a, b in zip(ordered_times, ordered_times[1:]) if a and b)
    daily_counts = {}
    for when in ordered_times:
        if when: daily_counts[when.date().isoformat()] = daily_counts.get(when.date().isoformat(), 0) + 1
    daily_ok = all(n <= int(config["frontier_calls_per_utc_day"]) for n in daily_counts.values())

    tool_ok, tool_evidence = tool_call_smoke()
    validate = run([sys.executable, str(ROOT / "tools" / "foundry.py"), "validate"])
    local_head = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    remote_line = run(["git", "ls-remote", "origin", "refs/heads/automation/frontier-scout"]).stdout.strip()
    remote_head = remote_line.split()[0] if remote_line else None
    active = {unit: run(["systemctl", "--user", "is-active", unit]).stdout.strip() for unit in ("chronos-sglang.service", "hermes-gateway.service")}
    enabled = {unit: run(["systemctl", "--user", "is-enabled", unit]).stdout.strip() for unit in ("chronos-sglang.service", "hermes-gateway.service")}
    linger = run(["loginctl", "show-user", str(HOME.name), "-p", "Linger", "--value"]).stdout.strip()

    latest_id = (args.sessions_root / "latest").read_text().strip()
    packet = json.loads((args.sessions_root / latest_id / "context_packet.json").read_text())
    packet_ro = all(row.get("read_only_verified") is True and row.get("hash_before") == row.get("hash_after") for row in packet.get("databases", {}).values())
    after = {name: sha_file(args.data_root / name) for name in before}
    traced = [row for row in receipts if row.get("frontier_consult")]
    executed = [row for row in traced if row["frontier_consult"].get("executed")]

    checks = {
        "sglang_active_enabled": active["chronos-sglang.service"] == "active" and enabled["chronos-sglang.service"] == "enabled",
        "gateway_active_enabled_linger": active["hermes-gateway.service"] == "active" and enabled["hermes-gateway.service"] == "enabled" and linger == "yes",
        "structured_tool_call": tool_ok,
        "scout_local_35b_30m_recent": scout.get("provider") == "foundry-qwen35b" and scout.get("model") == MODEL and scout.get("schedule", {}).get("minutes") == 30 and scout.get("last_status") == "ok" and (parse_time(scout.get("last_run_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= recent_cutoff,
        "night_shift_local_35b": night.get("provider") == "foundry-qwen35b" and night.get("model") == MODEL and night.get("last_status") == "ok",
        "publisher_30m_recent": publisher.get("schedule", {}).get("minutes") == 30 and publisher.get("last_status") == "ok" and (parse_time(publisher.get("last_run_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= recent_cutoff,
        "foundry_and_atlas_validation": validate.returncode == 0,
        "automation_branch_current": bool(remote_head) and local_head == remote_head,
        "all_frontier_calls_certified_stalls": bool(calls) and all(call_stalls),
        "frontier_budget_and_cooldown_held": daily_ok and cooldown_ok,
        "frontier_advice_executed_trace": bool(executed),
        "latest_context_read_only": packet_ro,
        "protected_hashes_stable_during_audit": before == after,
    }
    report = {
        "schema": "p42-foundry-operational-audit-v1",
        "audited_at": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "overall": all(checks.values()),
        "checks": checks,
        "evidence": {
            "receipt_count": len(receipts), "traced_consults": len(traced), "executed_consults": len(executed),
            "frontier_calls": len(calls), "call_certified_stalls": call_stalls, "daily_call_counts": daily_counts,
            "tool_smoke": tool_evidence, "local_head": local_head, "remote_head": remote_head,
            "service_active": active, "service_enabled": enabled, "linger": linger,
            "latest_session": latest_id, "protected_hashes_before": before, "protected_hashes_after": after,
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


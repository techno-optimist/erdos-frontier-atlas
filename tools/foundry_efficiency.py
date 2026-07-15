#!/usr/bin/env python3
"""Extract first-turn Foundry resource telemetry from Hermes agent logs.

This module deliberately does not compute a recursive-improvement reward.
Receipt classifications are model-adjacent telemetry, not independent evidence.
The frozen evaluator described in ``foundry/RSI_PROTOCOL.md`` owns utility
adjudication and promotion authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "foundry" / "config.json"

LINE_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+"
    r"\S+\s+\[(?P<session>cron_(?P<job>[a-f0-9]{12})_[^\]]+)\]\s+"
    r"[^:]+:\s+(?P<message>.*)$"
)
API_RE = re.compile(
    r"API call #(?P<number>\d+):.*?\bin=(?P<input>\d+)\s+"
    r"out=(?P<output>\d+)\s+total=(?P<total>\d+)\s+"
    r"latency=(?P<latency>[0-9.]+)s"
)
TURN_END_RE = re.compile(
    r"Turn ended: reason=(?P<reason>.+?)\s+model=\S+\s+"
    r"api_calls=(?P<used>\d+)/(?P<limit>\d+)"
)
FIRST_TURN_RE = re.compile(r"conversation turn:.*\bhistory=0\b")
TERMINAL_RE = re.compile(
    r"(?:tool|Tool) terminal (?P<outcome>completed|returned error) "
    r"\((?P<duration>[0-9.]+)s,"
)


def parse_wall_time(value: str, source_timezone: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S,%f").replace(
        tzinfo=ZoneInfo(source_timezone)
    )


def iso(value: datetime) -> str:
    return value.isoformat(timespec="milliseconds")


def parse_log_lines(
    lines: list[str], job_ids: set[str], source_timezone: str
) -> list[dict]:
    """Parse only the first conversation turn for each cron session.

    Hermes starts a background skill-curation turn under the same session ID
    after the research turn ends. Once the first ``Turn ended`` marker is seen,
    every later line for that session is ignored. This prevents background
    review tokens from contaminating research-efficiency measurements.
    """
    states: dict[str, dict] = {}
    for line in lines:
        match = LINE_RE.match(line.rstrip("\n"))
        if not match or match.group("job") not in job_ids:
            continue
        session_id = match.group("session")
        timestamp = parse_wall_time(match.group("timestamp"), source_timezone)
        message = match.group("message")
        state = states.get(session_id)
        if state is None:
            # Fail closed on truncated logs. A background review uses the same
            # session ID and restarts API numbering, so API lines without the
            # explicit history=0 research-turn marker are ambiguous.
            if not FIRST_TURN_RE.search(message):
                continue
            state = {
                "session_id": session_id,
                "job_id": match.group("job"),
                "started": timestamp,
                "ended": None,
                "finish_reason": None,
                "reported_api_calls": None,
                "api_budget": None,
                "calls": {},
                "terminal_calls": {},
                "closed": False,
            }
            states[session_id] = state
        if state["closed"]:
            continue
        state["started"] = min(state["started"], timestamp)
        api = API_RE.search(message)
        if api:
            number = int(api.group("number"))
            # Log copies or rotations may repeat a line. The first instance is
            # authoritative; call numbers cannot repeat inside a single turn.
            state["calls"].setdefault(
                number,
                {
                    "number": number,
                    "at": timestamp,
                    "input": int(api.group("input")),
                    "output": int(api.group("output")),
                    "total": int(api.group("total")),
                    "latency": float(api.group("latency")),
                },
            )
        terminal = TERMINAL_RE.search(message)
        if terminal:
            terminal_row = {
                "at": iso(timestamp),
                "duration_seconds": float(terminal.group("duration")),
                "outcome": terminal.group("outcome").replace(" ", "_"),
            }
            terminal_key = (
                terminal_row["at"], terminal_row["duration_seconds"],
                terminal_row["outcome"],
            )
            state["terminal_calls"].setdefault(terminal_key, terminal_row)
        ended = TURN_END_RE.search(message)
        if ended:
            state["ended"] = timestamp
            state["finish_reason"] = ended.group("reason")
            state["reported_api_calls"] = int(ended.group("used"))
            state["api_budget"] = int(ended.group("limit"))
            state["closed"] = True

    sessions = []
    for state in states.values():
        calls = [state["calls"][key] for key in sorted(state["calls"])]
        if not calls:
            continue
        started = state["started"]
        ended = state["ended"]
        input_tokens = sum(row["input"] for row in calls)
        output_tokens = sum(row["output"] for row in calls)
        total_tokens = sum(row["total"] for row in calls)
        terminal_calls = [
            state["terminal_calls"][key]
            for key in sorted(state["terminal_calls"])
        ]
        expensive_terminal_calls = [
            row for row in terminal_calls if row["duration_seconds"] > 30.0
        ]
        sessions.append(
            {
                "session_id": state["session_id"],
                "job_id": state["job_id"],
                "status": "complete" if ended else "incomplete",
                "started_at": iso(started),
                "ended_at": iso(ended) if ended else None,
                "wall_seconds": round((ended - started).total_seconds(), 3) if ended else None,
                "finish_reason": state["finish_reason"],
                "api_call_count": len(calls),
                "reported_api_calls": state["reported_api_calls"],
                "api_budget": state["api_budget"],
                "sum_input_tokens": input_tokens,
                "sum_output_tokens": output_tokens,
                "sum_total_tokens": total_tokens,
                "initial_input_tokens": calls[0]["input"],
                "final_input_tokens": calls[-1]["input"],
                "max_input_tokens": max(row["input"] for row in calls),
                "context_growth_tokens": calls[-1]["input"] - calls[0]["input"],
                "sum_api_latency_seconds": round(sum(row["latency"] for row in calls), 3),
                "terminal_call_count": len(terminal_calls),
                "sum_terminal_seconds": round(
                    sum(row["duration_seconds"] for row in terminal_calls), 3
                ),
                "expensive_terminal_threshold_seconds": 30.0,
                "expensive_terminal_call_count": len(expensive_terminal_calls),
                "expensive_terminal_calls": expensive_terminal_calls,
                "token_accounting_consistent": all(
                    row["input"] + row["output"] == row["total"] for row in calls
                ),
                "first_turn_only": True,
                "receipt_telemetry": None,
            }
        )
    return sorted(sessions, key=lambda row: (row["started_at"], row["session_id"]))


def load_receipts(root: Path) -> list[dict]:
    return [json.loads(path.read_text()) for path in sorted(root.glob("**/*.json"))]


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def attach_receipt_telemetry(
    sessions: list[dict], receipts: list[dict], window_seconds: int = 300
) -> None:
    """Attach the nearest same-job receipt without treating it as a reward."""
    used: set[str] = set()
    for session in sessions:
        if session["status"] != "complete":
            continue
        ended = parse_iso(session["ended_at"])
        candidates = []
        for receipt in receipts:
            receipt_id = receipt.get("receipt_id")
            if not receipt_id or receipt_id in used:
                continue
            if receipt.get("source", {}).get("job_id") != session["job_id"]:
                continue
            delta = abs((parse_iso(receipt["occurred_at"]) - ended).total_seconds())
            if delta <= window_seconds:
                candidates.append((delta, receipt_id, receipt))
        if not candidates:
            continue
        delta, receipt_id, receipt = min(candidates, key=lambda row: (row[0], row[1]))
        used.add(receipt_id)
        session["receipt_telemetry"] = {
            "receipt_id": receipt_id,
            "frontier_id": receipt.get("frontier_id"),
            "classification": receipt.get("classification"),
            "evidence_class": receipt.get("evidence_class"),
            "source_sha256": receipt.get("source", {}).get("sha256"),
            "end_delta_seconds": round(delta, 3),
            "telemetry_only_not_reward": True,
        }


def aggregate(sessions: list[dict]) -> dict:
    completed = [row for row in sessions if row["status"] == "complete"]
    matched = [row for row in completed if row["receipt_telemetry"]]
    classes = Counter(
        row["receipt_telemetry"]["classification"] for row in matched
    )
    return {
        "sessions": len(sessions),
        "completed_sessions": len(completed),
        "incomplete_sessions": len(sessions) - len(completed),
        "matched_receipts": len(matched),
        "receipt_classifications": {
            key: classes.get(key, 0) for key in ("progress", "negative_result", "blocked")
        },
        "sum_input_tokens": sum(row["sum_input_tokens"] for row in sessions),
        "sum_output_tokens": sum(row["sum_output_tokens"] for row in sessions),
        "sum_total_tokens": sum(row["sum_total_tokens"] for row in sessions),
        "sum_api_calls": sum(row["api_call_count"] for row in sessions),
        "sum_api_latency_seconds": round(
            sum(row["sum_api_latency_seconds"] for row in sessions), 3
        ),
        "sum_completed_wall_seconds": round(
            sum(row["wall_seconds"] for row in completed), 3
        ),
        "utility_score": None,
        "utility_reason": "independent frozen adjudicator required",
    }


def git_revision() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def runtime_budget_digest(config: dict) -> str | None:
    budget = config.get("runtime_budget")
    if not isinstance(budget, dict):
        return None
    canonical = json.dumps(
        budget, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    # Telemetry includes internal session identifiers. Set the final mode on
    # the temporary inode before the atomic rename; never expose a 0644 race.
    tmp.chmod(0o600)
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", nargs="*", type=Path)
    parser.add_argument("--job-id", action="append", dest="job_ids")
    parser.add_argument("--source-timezone")
    parser.add_argument("--receipts-root", type=Path, default=ROOT / "progress" / "receipts")
    parser.add_argument("--receipt-window-seconds", type=int, default=300)
    parser.add_argument("--since", help="inclusive ISO-8601 start time")
    parser.add_argument("--candidate-id", default="observed-production")
    parser.add_argument("--harness-revision")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--allow-empty", action="store_true")
    args = parser.parse_args()

    config = json.loads(CONFIG.read_text())
    job_ids = set(args.job_ids or config["source_job_ids"])
    source_timezone = args.source_timezone or config["source_timezone"]
    logs = args.logs or [Path.home() / ".hermes" / "logs" / "agent.log"]
    lines: list[str] = []
    for path in logs:
        lines.extend(path.read_text(errors="replace").splitlines())
    sessions = parse_log_lines(lines, job_ids, source_timezone)
    if args.since:
        since = parse_iso(args.since)
        sessions = [row for row in sessions if parse_iso(row["started_at"]) >= since]
    receipts = load_receipts(args.receipts_root) if args.receipts_root.exists() else []
    attach_receipt_telemetry(sessions, receipts, args.receipt_window_seconds)
    report = {
        "schema": "p42-foundry-efficiency-v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "candidate_id": args.candidate_id,
        "harness_revision": args.harness_revision or git_revision(),
        "source_timezone": source_timezone,
        "job_ids": sorted(job_ids),
        "measurement_boundary": "first Hermes conversation turn per cron session",
        "promotion_authority": "none_metrics_only",
        "runtime_budget": config.get("runtime_budget"),
        "runtime_budget_digest": runtime_budget_digest(config),
        "sessions": sessions,
        "aggregate": aggregate(sessions),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        atomic_json(args.output, report)
    print(rendered, end="")
    return 0 if sessions or args.allow_empty else 2


if __name__ == "__main__":
    raise SystemExit(main())

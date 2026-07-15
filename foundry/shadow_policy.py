#!/usr/bin/env python3
"""Observe-only evidence-yield policy for Foundry frontier selection."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = Path.home() / ".hermes" / "chronos_state" / "frontier_queue.json"
RECEIPTS = ROOT / "progress" / "receipts"
REWARD = {"progress": 1.0, "negative_result": 0.45, "blocked": 0.0}


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def rank_shadow(queue: dict, receipts: list[dict], now: datetime, window: int = 8) -> list[dict]:
    by_lane: dict[str, list[dict]] = defaultdict(list)
    for row in receipts:
        if row.get("frontier_id"):
            by_lane[row["frontier_id"]].append(row)
    for rows in by_lane.values():
        rows.sort(key=lambda row: row.get("occurred_at", ""))
    total = sum(len(rows) for rows in by_lane.values())
    ranked = []
    for item in queue.get("items", []):
        lane = item.get("id")
        rows = by_lane.get(lane, [])[-window:]
        reward = sum(REWARD.get(row.get("classification"), 0.0) for row in rows)
        posterior = (1.0 + reward) / (2.0 + len(rows))
        exploration = min(0.12, 0.05 * math.sqrt(math.log(total + 2.0) / (len(rows) + 1.0)))
        last = parse_time(item.get("last_context_at")) or parse_time(item.get("last_touched"))
        age_hours = 168.0 if last is None else max(0.0, (now - last).total_seconds() / 3600.0)
        age_bonus = min(0.08, age_hours / 48.0 * 0.08)
        blocked_tail = 0
        for row in reversed(rows):
            if row.get("classification") != "blocked":
                break
            blocked_tail += 1
        repeat_penalty = min(0.09, max(0, blocked_tail - 1) * 0.03)
        base_priority = float(item.get("priority", 0.0))
        score = posterior + exploration + age_bonus + base_priority - repeat_penalty
        ranked.append({
            "frontier_id": lane,
            "shadow_score": round(score, 6),
            "attempts_in_window": len(rows),
            "evidence_reward": round(reward, 3),
            "posterior_yield": round(posterior, 6),
            "exploration_bonus": round(exploration, 6),
            "age_bonus": round(age_bonus, 6),
            "repeat_block_penalty": round(repeat_penalty, 6),
            "base_priority": base_priority,
        })
    ranked.sort(key=lambda row: (-row["shadow_score"], str(row["frontier_id"])))
    return ranked


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", type=Path, default=QUEUE)
    ap.add_argument("--receipts", type=Path, default=RECEIPTS)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--now", help="UTC ISO timestamp for deterministic replay")
    args = ap.parse_args()
    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    if now is None:
        raise SystemExit("invalid --now timestamp")
    receipts = [json.loads(path.read_text()) for path in args.receipts.glob("**/*.json")]
    ranked = rank_shadow(json.loads(args.queue.read_text()), receipts, now)
    value = {
        "schema": "p42-foundry-shadow-policy-v1",
        "policy_status": "shadow_only_no_control_authority",
        "evaluated_at": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "shadow_selected_frontier_id": ranked[0]["frontier_id"] if ranked else None,
        "ranked": ranked,
        "reward_contract": REWARD,
    }
    rendered = json.dumps(value, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.output.with_suffix(args.output.suffix + ".tmp")
        tmp.write_text(rendered)
        tmp.replace(args.output)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

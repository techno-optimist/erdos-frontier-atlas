#!/usr/bin/env python3
"""Deterministic recency-aware selector for the Foundry frontier queue."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

QUEUE = Path.home() / ".hermes" / "chronos_state" / "frontier_queue.json"
RECENCY_PENALTY = 0.05
CLOSED_PENALTY = 0.01
CLOSED_MARKERS = ("rotate", "control_plane", "control-plane", "closed", "exhausted", "no_viable")


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def rank_items(queue: dict, now: datetime, cooldown_hours: float = 4.0) -> list[dict]:
    ranked = []
    for item in queue.get("items", []):
        last = parse_time(item.get("last_context_at")) or parse_time(item.get("last_touched"))
        age_hours = None if last is None else max(0.0, (now - last).total_seconds() / 3600)
        recency = 0.0 if age_hours is None else max(0.0, 1.0 - age_hours / cooldown_hours) * RECENCY_PENALTY
        status_text = " ".join(str(item.get(k, "")).lower() for k in ("status", "next_gate", "next_action"))
        closed = any(marker in status_text for marker in CLOSED_MARKERS)
        score = float(item.get("priority", 0.0)) - recency - (CLOSED_PENALTY if closed else 0.0)
        ranked.append({
            "frontier_id": item.get("id"), "base_priority": float(item.get("priority", 0.0)),
            "effective_priority": round(score, 6), "age_hours": None if age_hours is None else round(age_hours, 3),
            "recent_penalty": round(recency, 6), "closed_lane_penalty": CLOSED_PENALTY if closed else 0.0,
        })
    ranked.sort(key=lambda row: (-row["effective_priority"], -(row["age_hours"] if row["age_hours"] is not None else 1e12), str(row["frontier_id"])))
    return ranked


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", type=Path, default=QUEUE)
    ap.add_argument("--cooldown-hours", type=float, default=4.0)
    ap.add_argument("--now", help="UTC ISO timestamp for deterministic replay")
    args = ap.parse_args()
    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    if now is None:
        raise SystemExit("invalid --now timestamp")
    ranked = rank_items(json.loads(args.queue.read_text()), now, args.cooldown_hours)
    if not ranked:
        raise SystemExit("frontier queue is empty")
    print(json.dumps({
        "schema": "p42-foundry-selector-v1", "selected_frontier_id": ranked[0]["frontier_id"],
        "selected": ranked[0], "ranked": ranked,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

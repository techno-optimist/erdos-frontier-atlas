#!/usr/bin/env python3
"""Plan or atomically materialize provenance-tagged frontier seeds."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "foundry" / "frontier_seeds.json"
QUEUE = Path.home() / ".hermes" / "chronos_state" / "frontier_queue.json"
REQUIRED = {"id", "atlas_problem_id", "source", "title", "class", "compute_profile", "priority", "risk", "status", "query", "falsifier", "next_action", "next_gate", "avoid"}


def plan_materialization(queue: dict, seed_doc: dict, atlas_problem_ids: set[int] | None = None) -> list[dict]:
    existing = {item.get("id") for item in queue.get("items", [])}
    planned = []
    for seed in seed_doc.get("seeds", []):
        missing = REQUIRED - set(seed)
        if missing:
            raise ValueError(f"seed {seed.get('id')} missing: {', '.join(sorted(missing))}")
        if atlas_problem_ids is not None and seed["atlas_problem_id"] not in atlas_problem_ids:
            raise ValueError(f"seed {seed['id']} has unknown atlas_problem_id {seed['atlas_problem_id']}")
        if seed["id"] not in existing:
            planned.append(dict(seed))
    return planned


def apply_materialization(queue_path: Path, queue: dict, planned: list[dict], now: datetime) -> Path | None:
    if not planned:
        return None
    stamp = now.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = queue_path.with_name(queue_path.name + ".bak." + stamp)
    mode = queue_path.stat().st_mode & 0o777
    if backup.exists():
        raise FileExistsError(f"refusing to overwrite queue backup: {backup}")
    backup.write_bytes(queue_path.read_bytes())
    backup.chmod(mode)
    value = dict(queue)
    value["items"] = [*queue.get("items", []), *planned]
    value["updated_at"] = now.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    tmp = queue_path.with_suffix(queue_path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.chmod(mode)
    os.replace(tmp, queue_path)
    return backup


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", type=Path, default=QUEUE)
    ap.add_argument("--seeds", type=Path, default=SEEDS)
    ap.add_argument("--atlas", type=Path, default=ROOT / "atlas" / "problems.json")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    queue = json.loads(args.queue.read_text())
    seed_doc = json.loads(args.seeds.read_text())
    atlas = json.loads(args.atlas.read_text())
    atlas_problem_ids = {int(row["id"]) for row in atlas.get("problems", [])}
    planned = plan_materialization(queue, seed_doc, atlas_problem_ids)
    backup = apply_materialization(args.queue, queue, planned, datetime.now(timezone.utc)) if args.apply else None
    print(json.dumps({
        "schema": "p42-foundry-materialization-plan-v1",
        "applied": bool(args.apply and planned),
        "planned_frontier_ids": [row["id"] for row in planned],
        "backup": str(backup) if backup else None,
        "atlas_writes": False
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Provenance-preserving repair of receipts from their immutable raw runs."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import foundry  # noqa: E402


def destination(receipt: dict) -> Path:
    suffix = receipt["receipt_id"].split(":", 1)[1][:12]
    timestamp = receipt["occurred_at"].replace("-", "").replace(":", "")
    return foundry.RECEIPTS / receipt["occurred_at"][:4] / receipt["occurred_at"][5:7] / f"{timestamp}_{receipt['source']['job_id']}_{suffix}.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-root", type=Path, default=Path.home() / ".hermes" / "cron" / "output")
    ap.add_argument("--state", type=Path)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    config = foundry.load_json(foundry.CONFIG)
    timezone_name = config.get("source_timezone", "Etc/GMT+7")
    repairs = []
    retained = []
    planned = []
    id_map = {}
    destinations = set()
    for old_path in foundry.receipt_files():
        old = foundry.load_json(old_path)
        src = old["source"]
        raw = args.raw_root / src["job_id"] / src["run_file"]
        if not raw.exists():
            retained.append({"receipt_id": old["receipt_id"], "run_file": src["run_file"], "reason": "raw source unavailable"})
            continue
        if foundry.sha(raw.read_bytes()) != src["sha256"]:
            raise SystemExit(f"source hash mismatch: {src['job_id']}/{src['run_file']}")
        new = foundry.build_receipt(raw, src["job_id"], timezone_name)
        errors = foundry.validate_receipt(new)
        if errors:
            raise SystemExit(f"rebuilt receipt invalid: {src['run_file']}: {'; '.join(errors)}")
        new_path = destination(new)
        if new_path in destinations:
            raise SystemExit(f"repair destination collision: {new_path}")
        destinations.add(new_path)
        id_map[old["receipt_id"]] = new["receipt_id"]
        if old != new or old_path != new_path:
            record = {
                "old_receipt_id": old["receipt_id"], "new_receipt_id": new["receipt_id"],
                "run_file": src["run_file"], "old_occurred_at": old["occurred_at"],
                "new_occurred_at": new["occurred_at"], "old_classification": old["classification"],
                "new_classification": new["classification"],
            }
            repairs.append(record)
            planned.append((old_path, new_path, new))
    report = {
        "schema": "p42-foundry-receipt-truth-repair-v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_timezone": timezone_name,
        "applied": args.apply,
        "repair_count": len(repairs),
        "retained_count": len(retained),
        "repairs": repairs,
        "retained": retained,
    }
    if not args.apply:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    for old_path, new_path, new in planned:
        foundry.atomic_json(new_path, new)
        if old_path != new_path:
            old_path.unlink()
    if args.state and args.state.exists():
        state = foundry.load_json(args.state)
        for call in state.get("calls", []):
            call["gate_receipts"] = [id_map.get(receipt_id, receipt_id) for receipt_id in call.get("gate_receipts", [])]
        foundry.atomic_json(args.state, state)
        args.state.chmod(0o600)
    manifest = foundry.PROGRESS / "migrations" / f"{report['generated_at'].replace(':', '').replace('-', '')}_receipt_truth_repair.json"
    foundry.atomic_json(manifest, report)
    foundry.rebuild_index()
    foundry.validate()
    print(json.dumps({**report, "manifest": str(manifest.relative_to(ROOT))}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

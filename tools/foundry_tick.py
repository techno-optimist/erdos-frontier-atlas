#!/usr/bin/env python3
"""Ingest completed CHRONOS runs, expose the stall gate, and publish receipts."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def source_is_watermarked(state: dict, key: str, source_sha: str) -> bool:
    """Return true only when this exact immutable source was already handled."""
    return any(state.get(bucket, {}).get(key) == source_sha for bucket in ("accepted", "rejected"))


def inspect_run(tool: Path, source: Path, job_id: str, repo: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(tool), "inspect", str(source), "--job-id", job_id],
        cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        value = json.loads(proc.stdout)
    except (TypeError, ValueError):
        value = {
            "schema": "p42-foundry-inspection-v1", "valid": False,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "receipt": None,
            "errors": [proc.stderr.strip().splitlines()[-1][:500] if proc.stderr.strip() else "inspection failed"],
        }
    return value


def rejection_detail(inspection: dict, fallback_reason: str) -> dict:
    receipt = inspection.get("receipt") or {}
    errors = [str(row)[:500] for row in inspection.get("errors", []) if str(row).strip()]
    return {
        "schema": "p42-foundry-quarantine-feedback-v1",
        "recorded_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_sha256": inspection.get("source_sha256"),
        "receipt_id": receipt.get("receipt_id"),
        "frontier_id": receipt.get("frontier_id"),
        "classification": receipt.get("classification"),
        "occurred_at": receipt.get("occurred_at"),
        "errors": errors or [fallback_reason[:500]],
        "remediation": "replay the bounded evidence, then correct scope; never claim the quarantined receipt was published",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--cron-output", type=Path, default=Path.home() / ".hermes" / "cron" / "output")
    ap.add_argument("--state", type=Path, default=Path.home() / ".hermes" / "chronos_state" / "foundry_frontier_budget.json")
    ap.add_argument("--ingest-state", type=Path, default=Path.home() / ".hermes" / "chronos_state" / "foundry_ingest_state.json")
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()
    lock_path = args.state.with_name("foundry_tick.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_handle = lock_path.open("a+")
    lock_path.chmod(0o600)
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({"skipped": True, "reason": "another Foundry tick holds the publication lock"}))
        return 0
    config = json.loads((args.repo / "foundry" / "config.json").read_text())
    tool = args.repo / "tools" / "foundry.py"
    created = []
    rejected = []
    ingest_state = json.loads(args.ingest_state.read_text()) if args.ingest_state.exists() else {}
    ingest_state.setdefault("accepted", {})
    ingest_state.setdefault("rejected", {})
    ingest_state.setdefault("rejected_details", {})
    # Backfill structured feedback for old hash-only quarantines. If a current
    # contract now accepts an old source, clear its watermark so normal ingest
    # can reconsider it below.
    for key, source_sha in list(ingest_state["rejected"].items()):
        detail = ingest_state["rejected_details"].get(key, {})
        if detail.get("source_sha256") == source_sha:
            continue
        job_id, separator, filename = key.partition("/")
        source = args.cron_output / job_id / filename
        if not separator or not source.exists() or hashlib.sha256(source.read_bytes()).hexdigest() != source_sha:
            continue
        inspection = inspect_run(tool, source, job_id, args.repo)
        if inspection.get("valid"):
            ingest_state["rejected"].pop(key, None)
            ingest_state["rejected_details"].pop(key, None)
        else:
            ingest_state["rejected_details"][key] = rejection_detail(inspection, "ingest failed")
    for job_id in config["source_job_ids"]:
        source_dir = args.cron_output / job_id
        if not source_dir.exists(): continue
        for source in sorted(source_dir.glob("*.md")):
            source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
            key = f"{job_id}/{source.name}"
            if source_is_watermarked(ingest_state, key, source_sha):
                continue
            inspection = inspect_run(tool, source, job_id, args.repo)
            if not inspection.get("valid"):
                detail = rejection_detail(inspection, "ingest failed")
                rejected.append({"run_file": source.name, "reason": detail["errors"][0][:240]})
                ingest_state["rejected"][key] = source_sha
                ingest_state["rejected_details"][key] = detail
                ingest_state["accepted"].pop(key, None)
                continue
            proc = subprocess.run([sys.executable, str(tool), "ingest", str(source), "--job-id", job_id], cwd=args.repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode == 0:
                if json.loads(proc.stdout).get("created"): created.append(source.name)
                ingest_state["accepted"][key] = source_sha
                ingest_state["rejected"].pop(key, None)
                ingest_state["rejected_details"].pop(key, None)
            elif proc.returncode != 0:
                reason = proc.stderr.strip().splitlines()[-1][:240] if proc.stderr.strip() else "ingest failed"
                rejected.append({"run_file": source.name, "reason": reason})
                ingest_state["rejected"][key] = source_sha
                ingest_state["rejected_details"][key] = rejection_detail(inspection, reason)
                ingest_state["accepted"].pop(key, None)
    args.ingest_state.parent.mkdir(parents=True, exist_ok=True)
    ingest_tmp = args.ingest_state.with_suffix(args.ingest_state.suffix + ".tmp")
    ingest_tmp.write_text(json.dumps(ingest_state, indent=2) + "\n")
    os.replace(ingest_tmp, args.ingest_state)
    args.ingest_state.chmod(0o600)
    frontier_ids = sorted({
        row.get("frontier_id")
        for path in (args.repo / "progress" / "receipts").glob("**/*.json")
        for row in [json.loads(path.read_text())]
        if row.get("frontier_id")
    })
    lane_gates = {}
    for frontier_id in frontier_ids:
        proc = subprocess.run(
            [sys.executable, str(tool), "gate", "--state", str(args.state), "--frontier-id", frontier_id],
            cwd=args.repo, text=True, stdout=subprocess.PIPE, check=True,
        )
        lane_gates[frontier_id] = json.loads(proc.stdout)
    gate = {"schema": "p42-foundry-stall-summary-v1", "lanes": lane_gates}
    gate_path = args.state.with_name("foundry_stall_gate.json")
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.write_text(json.dumps(gate, indent=2) + "\n")
    publish_result = {"published": False, "reason": "no-push mode"}
    if not args.no_push:
        published = subprocess.run([sys.executable, str(tool), "publish"], cwd=args.repo, text=True, stdout=subprocess.PIPE, check=True)
        try: publish_result = json.loads(published.stdout.strip().splitlines()[-1])
        except Exception: publish_result = {"published": False, "reason": "unparseable publisher output"}
    print(json.dumps({"ingested": created, "rejected": rejected, "gate": gate, "publication": publish_result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

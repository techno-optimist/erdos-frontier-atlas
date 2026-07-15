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
from pathlib import Path


def source_is_watermarked(state: dict, key: str, source_sha: str) -> bool:
    """Return true only when this exact immutable source was already handled."""
    return any(state.get(bucket, {}).get(key) == source_sha for bucket in ("accepted", "rejected"))


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
    for job_id in config["source_job_ids"]:
        source_dir = args.cron_output / job_id
        if not source_dir.exists(): continue
        for source in sorted(source_dir.glob("*.md")):
            source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
            key = f"{job_id}/{source.name}"
            if source_is_watermarked(ingest_state, key, source_sha):
                continue
            proc = subprocess.run([sys.executable, str(tool), "ingest", str(source), "--job-id", job_id], cwd=args.repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode == 0:
                if json.loads(proc.stdout).get("created"): created.append(source.name)
                ingest_state["accepted"][key] = source_sha
                ingest_state["rejected"].pop(key, None)
            elif proc.returncode != 0:
                rejected.append({"run_file": source.name, "reason": proc.stderr.strip().splitlines()[-1][:240] if proc.stderr.strip() else "ingest failed"})
                ingest_state["rejected"][key] = source_sha
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

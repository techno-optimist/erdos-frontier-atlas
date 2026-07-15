#!/usr/bin/env python3
"""Ingest completed CHRONOS runs, expose the stall gate, and publish receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--cron-output", type=Path, default=Path.home() / ".hermes" / "cron" / "output")
    ap.add_argument("--state", type=Path, default=Path.home() / ".hermes" / "chronos_state" / "foundry_frontier_budget.json")
    ap.add_argument("--ingest-state", type=Path, default=Path.home() / ".hermes" / "chronos_state" / "foundry_ingest_state.json")
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()
    config = json.loads((args.repo / "foundry" / "config.json").read_text())
    tool = args.repo / "tools" / "foundry.py"
    created = []
    rejected = []
    ingest_state = json.loads(args.ingest_state.read_text()) if args.ingest_state.exists() else {"rejected": {}}
    for job_id in config["source_job_ids"]:
        source_dir = args.cron_output / job_id
        if not source_dir.exists(): continue
        for source in sorted(source_dir.glob("*.md")):
            source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
            if ingest_state.get("rejected", {}).get(f"{job_id}/{source.name}") == source_sha:
                continue
            proc = subprocess.run([sys.executable, str(tool), "ingest", str(source), "--job-id", job_id], cwd=args.repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode == 0 and json.loads(proc.stdout).get("created"): created.append(source.name)
            elif proc.returncode != 0:
                rejected.append({"run_file": source.name, "reason": proc.stderr.strip().splitlines()[-1][:240] if proc.stderr.strip() else "ingest failed"})
                ingest_state.setdefault("rejected", {})[f"{job_id}/{source.name}"] = source_sha
    args.ingest_state.parent.mkdir(parents=True, exist_ok=True)
    args.ingest_state.write_text(json.dumps(ingest_state, indent=2) + "\n")
    gate = subprocess.run([sys.executable, str(tool), "gate", "--state", str(args.state)], cwd=args.repo, text=True, stdout=subprocess.PIPE, check=True)
    gate_path = args.state.with_name("foundry_stall_gate.json")
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.write_text(gate.stdout)
    if created and not args.no_push:
        subprocess.run([sys.executable, str(tool), "publish"], cwd=args.repo, check=True)
    print(json.dumps({"ingested": created, "rejected": rejected, "gate": json.loads(gate.stdout), "pushed": bool(created and not args.no_push)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

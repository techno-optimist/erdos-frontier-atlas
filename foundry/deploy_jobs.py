#!/usr/bin/env python3
"""One-time DGX scheduler migration for the Foundry research jobs."""
from __future__ import annotations

import fcntl
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
CRON = HOME / ".hermes" / "cron"
JOBS = CRON / "jobs.json"
LOCK = CRON / ".jobs.lock"
TARGETS = {"50c8e4391849", "e97056701b6d"}
MODEL = "/home/chronos/models/qwen3.6-35b-a3b"
SUFFIX = """

FOUNDRY RECURSION (operator-authorized): Read
~/.hermes/chronos_state/foundry_stall_gate.json before choosing the action. The
primary researcher for this job is the local Qwen 35B. If and only if
frontier_call_allowed is true, make exactly one strategy consultation with:
python3 ~/erdos-frontier-atlas/tools/foundry.py consult --state
~/.hermes/chronos_state/foundry_frontier_budget.json '<public-safe frontier,
failed routes, falsifier, desired executable test>'. Treat its answer as
provisional strategy, execute the smallest discriminating test locally, and
verify it before reporting. Never place secrets or local paths in the six
labelled final receipt fields. Git publication is handled by a separate
no-agent membrane; do not run git here.
""".strip()


def main() -> int:
    LOCK.touch(exist_ok=True)
    with LOCK.open("r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data = json.loads(JOBS.read_text())
        rows = data["jobs"] if isinstance(data, dict) else data
        changed = []
        for job in rows:
            if job.get("id") not in TARGETS:
                continue
            job["provider"] = "foundry-qwen35b"
            job["model"] = MODEL
            job["base_url"] = "http://127.0.0.1:30000/v1"
            if "FOUNDRY RECURSION (operator-authorized)" not in job.get("prompt", ""):
                job["prompt"] = job.get("prompt", "").rstrip() + "\n\n" + SUFFIX
            changed.append(job["id"])
        if changed != sorted(TARGETS):
            raise SystemExit(f"expected jobs {sorted(TARGETS)}, found {sorted(changed)}")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        shutil.copy2(JOBS, JOBS.with_name(f"jobs.pre-foundry-{stamp}.json"))
        tmp = JOBS.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        os.replace(tmp, JOBS)
    print(json.dumps({"updated": changed, "provider": "foundry-qwen35b", "model": MODEL}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


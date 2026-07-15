#!/usr/bin/env python3
"""DGX no-agent cron entrypoint for the Foundry publication membrane."""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path.home() / "erdos-frontier-atlas"
STATE = Path.home() / ".hermes" / "chronos_state"
AGENT_LOG = Path.home() / ".hermes" / "logs" / "agent.log"


def main() -> int:
    proc = subprocess.run(
        [sys.executable, str(REPO / "tools" / "foundry_tick.py"), "--repo", str(REPO)],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode:
        print(proc.stdout, end="")
        return proc.returncode
    efficiency_output = STATE / "foundry_efficiency_latest.json"
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    metrics = subprocess.run(
        [
            sys.executable,
            str(REPO / "tools" / "foundry_efficiency.py"),
            str(AGENT_LOG),
            "--since", since,
            "--output", str(efficiency_output),
        ],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if metrics.returncode:
        print(metrics.stdout, end="")
        return metrics.returncode
    efficiency_output.chmod(0o600)
    # Successful routine ticks stay silent; cron emits only failures.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

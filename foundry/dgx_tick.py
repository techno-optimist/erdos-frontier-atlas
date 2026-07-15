#!/usr/bin/env python3
"""DGX no-agent cron entrypoint for the Foundry publication membrane."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path.home() / "erdos-frontier-atlas"


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
    # Successful routine ticks stay silent; cron emits only failures.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


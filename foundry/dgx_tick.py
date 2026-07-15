#!/usr/bin/env python3
"""DGX no-agent cron entrypoint for the Foundry publication membrane."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path.home() / "erdos-frontier-atlas"
STATE = Path.home() / ".hermes" / "chronos_state"
AGENT_LOG = Path.home() / ".hermes" / "logs" / "agent.log"
REVIEWED_SKILL = REPO / "foundry" / "SKILL.md"
INSTALLED_SKILL = Path.home() / ".hermes" / "skills" / "foundry" / "SKILL.md"


def restore_reviewed_skill() -> str:
    """Discard unreviewed background mutations after each publisher tick."""
    data = REVIEWED_SKILL.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    INSTALLED_SKILL.parent.mkdir(parents=True, exist_ok=True)
    tmp = INSTALLED_SKILL.with_suffix(INSTALLED_SKILL.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.chmod(0o644)
    os.replace(tmp, INSTALLED_SKILL)
    if hashlib.sha256(INSTALLED_SKILL.read_bytes()).hexdigest() != digest:
        raise RuntimeError("installed Foundry skill digest mismatch")
    return digest


def agent_log_paths() -> list[Path]:
    """Return rotated Hermes logs oldest-first so split turns reconstruct."""
    paths = {path for path in AGENT_LOG.parent.glob(AGENT_LOG.name + "*") if path.is_file()}
    return sorted(paths, key=lambda path: (path.stat().st_mtime_ns, path.name))


def main() -> int:
    try:
        efficiency_output = STATE / "foundry_efficiency_latest.json"
        pending_output = efficiency_output.with_suffix(".json.pending")
        pending_output.unlink(missing_ok=True)
        since = (datetime.now(timezone.utc) - timedelta(hours=24)).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z")
        metrics = subprocess.run(
            [
                sys.executable,
                str(REPO / "tools" / "foundry_efficiency.py"),
                *[str(path) for path in agent_log_paths()],
                "--since", since,
                "--output", str(pending_output),
            ],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if metrics.returncode:
            pending_output.unlink(missing_ok=True)
            print(metrics.stdout, end="")
            return metrics.returncode
        # Ingest consumes the just-generated private report. A post-hoc metric
        # refresh cannot protect a receipt that has already crossed the
        # membrane, so runtime telemetry must exist before publication.
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO / "tools" / "foundry_tick.py"),
                "--repo", str(REPO),
                "--efficiency-report", str(pending_output),
            ],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if proc.returncode:
            pending_output.unlink(missing_ok=True)
            print(proc.stdout, end="")
            return proc.returncode
        os.replace(pending_output, efficiency_output)
        efficiency_output.chmod(0o600)
        # Successful routine ticks stay silent; cron emits only failures.
        return 0
    finally:
        restore_reviewed_skill()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Install the narrow per-job turn-cap hook required by the Foundry.

Hermes currently exposes only a process-wide ``agent.max_turns`` setting.
Foundry shares that gateway with unrelated research jobs, so lowering the
global setting would silently change their authority. This exact-source patch
adds an opt-in ``job['max_turns']`` cap while leaving every other job on the
existing global default. Unknown scheduler source fails closed.
"""
from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

MARKER = "FOUNDRY_JOB_MAX_TURNS_V1"
OLD = """        # Max iterations
        max_iterations = _cfg.get("agent", {}).get("max_turns") or _cfg.get("max_turns") or 90
"""
NEW = """        # Max iterations
        # FOUNDRY_JOB_MAX_TURNS_V1: operator-owned cron jobs may lower, never
        # raise, the process-wide turn budget. Jobs without the field retain
        # the exact upstream behavior.
        _global_max_iterations = int(
            _cfg.get("agent", {}).get("max_turns") or _cfg.get("max_turns") or 90
        )
        _job_max_iterations = job.get("max_turns")
        max_iterations = (
            min(_global_max_iterations, max(1, int(_job_max_iterations)))
            if _job_max_iterations is not None
            else _global_max_iterations
        )
"""


def patch_text(text: str) -> tuple[str, bool]:
    if MARKER in text:
        return text, False
    if text.count(OLD) != 1:
        raise RuntimeError(
            "Hermes scheduler source drifted; refusing unreviewed turn-cap patch"
        )
    return text.replace(OLD, NEW), True


def patch_file(path: Path) -> dict:
    original = path.read_text()
    patched, changed = patch_text(original)
    compile(patched, str(path), "exec")
    backup = path.with_name(path.name + ".pre-foundry-job-max-turns")
    if changed:
        if not backup.exists():
            shutil.copy2(path, backup)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(patched)
        tmp.chmod(path.stat().st_mode & 0o777)
        os.replace(tmp, path)
    installed = path.read_text()
    compile(installed, str(path), "exec")
    if MARKER not in installed:
        raise RuntimeError("Hermes per-job turn-cap marker missing after patch")
    return {
        "path": str(path),
        "changed": changed,
        "sha256": hashlib.sha256(installed.encode()).hexdigest(),
        "backup": str(backup),
    }


def main() -> int:
    path = Path.home() / ".hermes" / "hermes-agent" / "cron" / "scheduler.py"
    print(patch_file(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

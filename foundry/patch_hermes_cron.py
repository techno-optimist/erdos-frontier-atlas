#!/usr/bin/env python3
"""Install narrow per-job runtime caps required by the Foundry.

Hermes currently exposes only a process-wide ``agent.max_turns`` setting.
Foundry shares that gateway with unrelated research jobs, so lowering the
global setting would silently change their authority. This exact-source patch
adds opt-in ``job['max_turns']`` and ``job['max_wall_seconds']`` caps while
adding an opt-in finalization-only phase through ``job['finalize_no_tools_after']``
and leaving every other job on the existing global behavior. Unknown scheduler
source fails closed.
"""
from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

MARKER = "FOUNDRY_JOB_MAX_TURNS_V1"
WALL_MARKER = "FOUNDRY_JOB_MAX_WALL_SECONDS_V1"
FINALIZE_MARKER = "FOUNDRY_JOB_FINALIZE_NO_TOOLS_V1"
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
WALL_SETUP_OLD = """        _cron_inactivity_limit = _cron_timeout if _cron_timeout > 0 else None
"""
WALL_SETUP_NEW = """        _cron_inactivity_limit = _cron_timeout if _cron_timeout > 0 else None
        # FOUNDRY_JOB_MAX_WALL_SECONDS_V1: an operator-owned cron job may opt
        # into a finite wall-clock cap. Jobs without the field retain the
        # exact upstream inactivity-only behavior.
        _raw_job_wall_seconds = job.get("max_wall_seconds")
        if _raw_job_wall_seconds is None:
            _job_wall_limit = None
        else:
            try:
                _job_wall_limit = float(_raw_job_wall_seconds)
            except (TypeError, ValueError) as _wall_exc:
                raise RuntimeError(
                    f"Cron job '{job_name}' has invalid max_wall_seconds="
                    f"{_raw_job_wall_seconds!r}"
                ) from _wall_exc
            if not (0 < _job_wall_limit < float("inf")):
                raise RuntimeError(
                    f"Cron job '{job_name}' requires finite positive "
                    f"max_wall_seconds, got {_raw_job_wall_seconds!r}"
                )
        import time as _foundry_time
        _job_wall_started = _foundry_time.monotonic()
"""
WALL_LOOP_OLD = """                    if done:
                        result = _cron_future.result()
                        break
                    # Agent still running — check inactivity.
"""
WALL_LOOP_NEW = """                    if (
                        _job_wall_limit is not None
                        and _foundry_time.monotonic() - _job_wall_started
                        >= _job_wall_limit
                    ):
                        _wall_elapsed = _foundry_time.monotonic() - _job_wall_started
                        logger.error(
                            "Job '%s' exceeded wall limit %.0fs after %.0fs",
                            job_name, _job_wall_limit, _wall_elapsed,
                        )
                        if hasattr(agent, "interrupt"):
                            agent.interrupt("Cron job timed out (wall limit)")
                        raise TimeoutError(
                            f"Cron job '{job_name}' exceeded wall limit "
                            f"{int(_job_wall_limit)}s"
                        )
                    if done:
                        result = _cron_future.result()
                        break
                    # Agent still running — check inactivity.
"""
FINALIZE_OLD = """            session_db=_session_db,
        )
""" + "        \n" + """        # Run the agent with an *inactivity*-based timeout: the job can run
"""
FINALIZE_NEW = """            session_db=_session_db,
        )

        # FOUNDRY_JOB_FINALIZE_NO_TOOLS_V1: an operator-owned job may reserve
        # its last calls for a direct response. At the first call strictly
        # after the configured threshold, remove tool schemas and inject one
        # finalization steer. Jobs without the field retain upstream behavior.
        _raw_finalize_after = job.get("finalize_no_tools_after")
        if _raw_finalize_after is None:
            _job_finalize_after = None
        else:
            try:
                _job_finalize_after = int(_raw_finalize_after)
            except (TypeError, ValueError) as _finalize_exc:
                raise RuntimeError(
                    f"Cron job '{job_name}' has invalid finalize_no_tools_after="
                    f"{_raw_finalize_after!r}"
                ) from _finalize_exc
            if not (0 < _job_finalize_after < max_iterations):
                raise RuntimeError(
                    f"Cron job '{job_name}' requires 0 < "
                    f"finalize_no_tools_after < max_turns, got "
                    f"{_raw_finalize_after!r} and {max_iterations}"
                )
        if _job_finalize_after is not None:
            _prior_step_callback = agent.step_callback
            _finalization_injected = False

            def _foundry_finalize_step(iteration, previous_tools):
                nonlocal _finalization_injected
                if _prior_step_callback is not None:
                    _prior_step_callback(iteration, previous_tools)
                if iteration <= _job_finalize_after:
                    return
                agent.tools = []
                agent.valid_tool_names = set()
                agent._skill_nudge_interval = 0
                if _finalization_injected:
                    return
                instruction = (
                    "Operator finalization gate: tool access is now disabled. "
                    "Reply directly with exactly these six markdown labels and "
                    "their public-safe contents: Frontier, Action, Verified, "
                    "Result, Next gate, Boundary held. Copy the hash-bound "
                    "milestone Action prefix from the prep contract. Do not "
                    "describe a tool call or write another file."
                )
                lock = getattr(agent, "_pending_steer_lock", None)
                if lock is not None:
                    with lock:
                        pending = getattr(agent, "_pending_steer", None)
                        agent._pending_steer = (
                            pending + "\\n" + instruction if pending else instruction
                        )
                else:
                    pending = getattr(agent, "_pending_steer", None)
                    agent._pending_steer = (
                        pending + "\\n" + instruction if pending else instruction
                    )
                _finalization_injected = True
                logger.info(
                    "Job '%s' entered no-tools finalization at call %s after %s",
                    job_name, iteration, _job_finalize_after,
                )

            agent.step_callback = _foundry_finalize_step
""" + "        \n" + """        # Run the agent with an *inactivity*-based timeout: the job can run
"""


def patch_text(text: str) -> tuple[str, bool]:
    changed = False
    if MARKER not in text:
        if text.count(OLD) != 1:
            raise RuntimeError(
                "Hermes scheduler source drifted; refusing unreviewed turn-cap patch"
            )
        text = text.replace(OLD, NEW)
        changed = True
    if WALL_MARKER not in text:
        if text.count(WALL_SETUP_OLD) != 1 or text.count(WALL_LOOP_OLD) != 1:
            raise RuntimeError(
                "Hermes scheduler source drifted; refusing unreviewed wall-cap patch"
            )
        text = text.replace(WALL_SETUP_OLD, WALL_SETUP_NEW)
        text = text.replace(WALL_LOOP_OLD, WALL_LOOP_NEW)
        changed = True
    if FINALIZE_MARKER not in text:
        if text.count(FINALIZE_OLD) != 1:
            raise RuntimeError(
                "Hermes scheduler source drifted; refusing unreviewed finalization patch"
            )
        text = text.replace(FINALIZE_OLD, FINALIZE_NEW)
        changed = True
    return text, changed


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
    if (
        MARKER not in installed
        or WALL_MARKER not in installed
        or FINALIZE_MARKER not in installed
    ):
        raise RuntimeError("Hermes per-job runtime-cap markers missing after patch")
    return {
        "path": str(path),
        "changed": changed,
        "sha256": hashlib.sha256(installed.encode()).hexdigest(),
        "backup": str(backup),
        "markers": [MARKER, WALL_MARKER, FINALIZE_MARKER],
    }


def main() -> int:
    path = Path.home() / ".hermes" / "hermes-agent" / "cron" / "scheduler.py"
    print(patch_file(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

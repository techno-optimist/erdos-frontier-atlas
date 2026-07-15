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
LEGACY_FINALIZE_MARKER = "FOUNDRY_JOB_FINALIZE_NO_TOOLS_V1"
FINALIZE_MARKER = "FOUNDRY_JOB_FINALIZE_NO_TOOLS_V2"
FINALIZE_WALL_MARKER = "FOUNDRY_JOB_FINALIZE_WALL_SECONDS_V1"
LOOP_MARKER = "FOUNDRY_REQUIRED_RECEIPT_RETRY_V1"
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
# The wall-finalization anchor is the tail of WALL_SETUP_NEW, so this hunk can
# install on a scheduler that is already wall-capped (WALL_MARKER present).
FINALIZE_WALL_OLD = """        import time as _foundry_time
        _job_wall_started = _foundry_time.monotonic()
"""
FINALIZE_WALL_NEW = """        import time as _foundry_time
        _job_wall_started = _foundry_time.monotonic()
        # FOUNDRY_JOB_FINALIZE_WALL_SECONDS_V1: a job that reserves its last
        # calls for a receipt (finalize_no_tools_after) and carries a wall cap
        # (max_wall_seconds) may also finalize on *elapsed wall time*. Under
        # inference contention a slow-but-active run can exhaust the wall budget
        # while still below the call threshold; without this it is hard-killed
        # as a failed cron envelope and publishes nothing. At the first step
        # boundary past finalize_wall_seconds this removes tool schemas and
        # injects one finalization steer, so the worker still emits its six
        # labelled receipt before the hard wall kill. The hard cap remains the
        # backstop for a genuinely wedged single call. Jobs without the field
        # retain the exact prior behavior.
        _raw_finalize_wall = job.get("finalize_wall_seconds")
        if _raw_finalize_wall is None:
            _job_finalize_wall = None
        else:
            try:
                _job_finalize_wall = float(_raw_finalize_wall)
            except (TypeError, ValueError) as _finalize_wall_exc:
                raise RuntimeError(
                    f"Cron job '{job_name}' has invalid finalize_wall_seconds="
                    f"{_raw_finalize_wall!r}"
                ) from _finalize_wall_exc
            if _job_finalize_after is None:
                raise RuntimeError(
                    f"Cron job '{job_name}' finalize_wall_seconds requires "
                    f"finalize_no_tools_after"
                )
            if _job_wall_limit is None or not (
                0 < _job_finalize_wall < _job_wall_limit
            ):
                raise RuntimeError(
                    f"Cron job '{job_name}' requires 0 < finalize_wall_seconds "
                    f"< max_wall_seconds, got {_raw_finalize_wall!r}"
                )
            _prior_wall_finalize_callback = agent.step_callback
            agent._foundry_wall_finalize_started = _job_wall_started
            agent._foundry_wall_finalize_deadline = _job_finalize_wall
            agent._foundry_wall_finalize_triggered = False

            def _foundry_wall_finalize_step(iteration, previous_tools):
                if _prior_wall_finalize_callback is not None:
                    _prior_wall_finalize_callback(iteration, previous_tools)
                _wall_elapsed = (
                    _foundry_time.monotonic()
                    - agent._foundry_wall_finalize_started
                )
                if _wall_elapsed < agent._foundry_wall_finalize_deadline:
                    return
                agent.tools = []
                agent.valid_tool_names = set()
                agent._skill_nudge_interval = 0
                if agent._foundry_wall_finalize_triggered:
                    return
                instruction = (
                    "Operator wall-clock finalization gate: this job is nearly "
                    "out of wall-clock budget and tool access is now disabled. "
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
                agent._foundry_wall_finalize_triggered = True
                logger.info(
                    "Job '%s' entered no-tools finalization at %.0fs wall "
                    "(finalize_wall_seconds=%.0f, call %s)",
                    job_name, _wall_elapsed,
                    agent._foundry_wall_finalize_deadline, iteration,
                )

            agent.step_callback = _foundry_wall_finalize_step
"""
FINALIZE_OLD = """            session_db=_session_db,
        )
""" + "        \n" + """        # Run the agent with an *inactivity*-based timeout: the job can run
"""
FINALIZE_STATE_V1 = """            _prior_step_callback = agent.step_callback
            _finalization_injected = False

            def _foundry_finalize_step(iteration, previous_tools):
"""
FINALIZE_STATE_V2 = """            _prior_step_callback = agent.step_callback
            _finalization_injected = False
            agent._foundry_finalize_after = _job_finalize_after
            agent._foundry_required_final_labels = (
                "Frontier", "Action", "Verified", "Result", "Next gate",
                "Boundary held",
            )
            agent._foundry_finalization_retry_limit = max(
                0, max_iterations - _job_finalize_after - 1
            )
            agent._foundry_finalization_retries = 0

            def _foundry_finalize_step(iteration, previous_tools):
"""
FINALIZE_NEW = """            session_db=_session_db,
        )

        # FOUNDRY_JOB_FINALIZE_NO_TOOLS_V2: an operator-owned job may reserve
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
            agent._foundry_finalize_after = _job_finalize_after
            agent._foundry_required_final_labels = (
                "Frontier", "Action", "Verified", "Result", "Next gate",
                "Boundary held",
            )
            agent._foundry_finalization_retry_limit = max(
                0, max_iterations - _job_finalize_after - 1
            )
            agent._foundry_finalization_retries = 0

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
LOOP_OLD = """                final_response = agent._strip_think_blocks(final_response).strip()
""" + "                \n" + """                final_msg = agent._build_assistant_message(assistant_message, finish_reason)
"""
LOOP_NEW = """                final_response = agent._strip_think_blocks(final_response).strip()

                # FOUNDRY_REQUIRED_RECEIPT_RETRY_V1: exact opt-in jobs can
                # reject an intermediate tool-free answer and spend their
                # reserved calls on the required public receipt. Other agents
                # do not have these attributes and retain upstream behavior.
                _foundry_labels = getattr(
                    agent, "_foundry_required_final_labels", ()
                )
                _foundry_finalize_after = getattr(
                    agent, "_foundry_finalize_after", None
                )
                if (
                    _foundry_labels
                    and _foundry_finalize_after is not None
                    and api_call_count > _foundry_finalize_after
                ):
                    _missing_foundry_labels = [
                        label for label in _foundry_labels
                        if f"**{label}**" not in final_response
                    ]
                    _foundry_retries = int(getattr(
                        agent, "_foundry_finalization_retries", 0
                    ))
                    _foundry_retry_limit = int(getattr(
                        agent, "_foundry_finalization_retry_limit", 0
                    ))
                    if (
                        _missing_foundry_labels
                        and _foundry_retries < _foundry_retry_limit
                        and api_call_count < agent.max_iterations
                    ):
                        agent._foundry_finalization_retries = _foundry_retries + 1
                        interim_msg = agent._build_assistant_message(
                            assistant_message, "receipt_labels_required"
                        )
                        interim_msg["_foundry_finalization_synthetic"] = True
                        messages.append(interim_msg)
                        messages.append({
                            "role": "user",
                            "content": (
                                "Operator receipt gate: the prior response is "
                                "not publishable. Reply now with all six required "
                                "markdown labels and no preamble: "
                                + ", ".join(_foundry_labels)
                                + ". Missing from the prior response: "
                                + ", ".join(_missing_foundry_labels)
                                + ". Copy the hash-bound milestone Action prefix. "
                                "Tool access remains disabled."
                            ),
                            "_foundry_finalization_synthetic": True,
                        })
                        agent._session_messages = messages
                        logger.info(
                            "Foundry receipt retry %s/%s at call %s; missing=%s",
                            _foundry_retries + 1, _foundry_retry_limit,
                            api_call_count, ",".join(_missing_foundry_labels),
                        )
                        continue

                final_msg = agent._build_assistant_message(assistant_message, finish_reason)
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
    if FINALIZE_WALL_MARKER not in text:
        # Anchor is created by the wall-cap hunk above, so this applies to a
        # freshly patched source and to one that was already wall-capped.
        if text.count(FINALIZE_WALL_OLD) != 1:
            raise RuntimeError(
                "Hermes scheduler source drifted; refusing unreviewed "
                "wall-finalization patch"
            )
        text = text.replace(FINALIZE_WALL_OLD, FINALIZE_WALL_NEW)
        changed = True
    if FINALIZE_MARKER not in text:
        if LEGACY_FINALIZE_MARKER in text:
            if (
                text.count(LEGACY_FINALIZE_MARKER) != 1
                or text.count(FINALIZE_STATE_V1) != 1
            ):
                raise RuntimeError(
                    "Hermes legacy finalization state drifted; refusing unreviewed V2 upgrade"
                )
            text = text.replace(
                LEGACY_FINALIZE_MARKER, FINALIZE_MARKER, 1
            ).replace(FINALIZE_STATE_V1, FINALIZE_STATE_V2, 1)
        else:
            if text.count(FINALIZE_OLD) != 1:
                raise RuntimeError(
                    "Hermes scheduler source drifted; refusing unreviewed finalization patch"
                )
            text = text.replace(FINALIZE_OLD, FINALIZE_NEW)
        changed = True
    return text, changed


def patch_loop_text(text: str) -> tuple[str, bool]:
    if LOOP_MARKER in text:
        return text, False
    if text.count(LOOP_OLD) != 1:
        raise RuntimeError(
            "Hermes conversation loop source drifted; refusing unreviewed receipt-retry patch"
        )
    return text.replace(LOOP_OLD, LOOP_NEW), True


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
        or FINALIZE_WALL_MARKER not in installed
    ):
        raise RuntimeError("Hermes per-job runtime-cap markers missing after patch")
    return {
        "path": str(path),
        "changed": changed,
        "sha256": hashlib.sha256(installed.encode()).hexdigest(),
        "backup": str(backup),
        "markers": [MARKER, WALL_MARKER, FINALIZE_MARKER, FINALIZE_WALL_MARKER],
    }


def patch_loop_file(path: Path) -> dict:
    original = path.read_text()
    patched, changed = patch_loop_text(original)
    compile(patched, str(path), "exec")
    backup = path.with_name(path.name + ".pre-foundry-receipt-retry")
    if changed:
        if not backup.exists():
            shutil.copy2(path, backup)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(patched)
        tmp.chmod(path.stat().st_mode & 0o777)
        os.replace(tmp, path)
    installed = path.read_text()
    compile(installed, str(path), "exec")
    if LOOP_MARKER not in installed:
        raise RuntimeError("Hermes Foundry receipt-retry marker missing after patch")
    return {
        "path": str(path),
        "changed": changed,
        "sha256": hashlib.sha256(installed.encode()).hexdigest(),
        "backup": str(backup),
        "markers": [LOOP_MARKER],
    }


def main() -> int:
    root = Path.home() / ".hermes" / "hermes-agent"
    print({
        "scheduler": patch_file(root / "cron" / "scheduler.py"),
        "conversation_loop": patch_loop_file(root / "agent" / "conversation_loop.py"),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

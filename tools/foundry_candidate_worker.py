#!/usr/bin/env python3
"""Minimal verifier-first worker for an isolated Foundry evaluation container.

The worker has no TCP transport. It can reach the evaluator's local model only
through an explicitly mounted Unix-domain socket. All filesystem helpers are
confined to the read-only candidate workspace, the single task packet, and the
candidate output directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import time
from pathlib import Path

WORKSPACE = Path("/workspace")
TASK_PATH = Path("/task/task.json")
OUTPUT = Path("/output")
MODEL_SOCKET = Path(os.environ.get("FOUNDRY_MODEL_SOCKET", "/model/model.sock"))
MODEL = os.environ.get("FOUNDRY_MODEL", "evaluator-forced-local-model")
MAX_TOOL_OUTPUT = 24_000
SUBMISSION_RESERVE_CALLS = 2
MAX_SUBMISSION_REPLAYS = 8
MAX_REPLAY_PATH_BYTES = 240
MAX_CORRECTION_MESSAGE = 4_000
MAX_PREFLIGHT_TOTAL_SECONDS = 120


class ReplayPreflightError(ValueError):
    """Bounded candidate-visible correction data, never evaluator authority."""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_text",
            "description": "Read a bounded UTF-8 text file from the candidate workspace or task packet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "max_chars": {"type": "integer", "minimum": 1, "maximum": 24000},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List bounded paths beneath the read-only candidate workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 200},
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run an argv command inside the no-network container; workspace is read-only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "argv": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 180},
                },
                "required": ["argv"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_artifact",
            "description": "Write a bounded candidate artifact beneath /output/artifacts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_result",
            "description": "Submit the final typed result. This is a claim for independent replay, not acceptance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "classification": {"enum": ["progress", "negative_result", "blocked"]},
                    "hypothesis": {"type": "string"},
                    "falsifier": {"type": "string"},
                    "claim": {"type": "string"},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "artifacts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Final evidence artifacts only; unlisted scratch files are deleted. "
                            "Every final Python artifact needs its own replay step."
                        ),
                    },
                    "replay": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "argv": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 2,
                                },
                                "timeout_seconds": {
                                    "type": "integer", "minimum": 1, "maximum": 180,
                                },
                                "expected_exit": {"const": 0},
                            },
                            "required": ["argv"],
                            "additionalProperties": False,
                        },
                    },
                    "theorem_status": {
                        "enum": [
                            "witness_only", "local_result_only",
                            "certificate_pending", "theorem_unchanged",
                        ]
                    },
                },
                "required": [
                    "classification", "hypothesis", "falsifier", "claim",
                    "evidence", "artifacts", "replay", "theorem_status",
                ],
                "additionalProperties": False,
            },
        },
    },
]


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _workspace_path(raw: str) -> Path:
    if raw == "/task/task.json":
        return TASK_PATH
    path = Path(raw)
    if not path.is_absolute():
        path = WORKSPACE / path
    if not _inside(path, WORKSPACE):
        raise ValueError("path escapes candidate workspace")
    return path


def _artifact_path(raw: str) -> Path:
    root = OUTPUT / "artifacts"
    value = str(raw)
    if value.startswith("/output/artifacts/"):
        value = value.removeprefix("/output/artifacts/")
    elif value.startswith("artifacts/"):
        value = value.removeprefix("artifacts/")
    relative = Path(value)
    path = root / relative
    if (
        not value
        or relative.is_absolute()
        or ".." in relative.parts
        or (relative.parts and relative.parts[0] == "artifacts")
        or not _inside(path, root)
    ):
        raise ValueError("artifact path escapes output directory")
    return path


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()


def _artifact_inventory() -> list[dict]:
    root = OUTPUT / "artifacts"
    rows = []
    if not root.exists():
        return rows
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or (path.exists() and not _inside(path, root)):
            raise ValueError("artifact tree contains an unsafe path")
        if not path.is_file():
            continue
        data = path.read_bytes()
        if len(data) > 1_000_000:
            raise ValueError("artifact exceeds one megabyte")
        rows.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        })
    return rows


def _finalize_artifacts(claimed: object) -> list[str]:
    """Keep only the candidate-declared final artifact set, using canonical paths."""
    if not isinstance(claimed, list) or not all(isinstance(row, str) for row in claimed):
        raise ValueError("final artifacts must be a string array")
    root = OUTPUT / "artifacts"
    keep = set()
    for raw in claimed:
        path = _artifact_path(raw)
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"final artifact is absent or unsafe: {raw}")
        keep.add(path.relative_to(root).as_posix())
    if root.exists():
        for path in sorted(root.rglob("*"), reverse=True):
            if path.is_symlink():
                raise ValueError("artifact tree contains an unsafe path")
            if path.is_file() and path.relative_to(root).as_posix() not in keep:
                path.unlink()
            elif path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass
    return sorted(keep)


def _preflight_replays(replay: object, final_paths: list[str]) -> None:
    """Give the candidate correction feedback before evaluator-owned replay."""
    if not isinstance(replay, list) or len(replay) > MAX_SUBMISSION_REPLAYS:
        raise ValueError("replay must be an array of at most eight steps")
    python_paths = {path for path in final_paths if Path(path).suffix == ".py"}
    replayed = set()
    normalized = []
    for step in replay:
        if not isinstance(step, dict):
            raise ValueError("each replay step must be an argv object")
        argv = step.get("argv")
        if not isinstance(argv, list) or len(argv) < 2 or not all(
            isinstance(value, str) and value for value in argv
        ):
            raise ValueError("replay argv must contain an executable and artifact")
        if argv[0] not in {"python", "python3", "/usr/local/bin/python3"}:
            raise ValueError("replay executable must be the frozen Python runtime")
        script = argv[1]
        script = script.removeprefix("/output/artifacts/").removeprefix("/artifacts/")
        script = script.removeprefix("artifacts/")
        script_path = Path(script)
        if (
            script_path.is_absolute()
            or ".." in script_path.parts
            or script_path.suffix != ".py"
            or len(script_path.as_posix().encode()) > MAX_REPLAY_PATH_BYTES
            or script_path.as_posix() not in python_paths
        ):
            raise ValueError(f"replay script is not a final Python artifact: {argv[1]}")
        try:
            timeout = int(step.get("timeout_seconds", 180))
            expected = int(step.get("expected_exit", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError("replay timeout/exit must be integers") from exc
        if timeout < 1 or timeout > 180 or expected != 0:
            raise ValueError("replay requires timeout 1..180 and expected exit zero")
        replayed.add(script_path.as_posix())
        normalized.append((script_path, argv[2:], timeout))
    missing = sorted(python_paths - replayed)
    if missing:
        raise ValueError(
            "every final Python artifact requires replay: " + ", ".join(missing)
        )
    work = OUTPUT / "work"
    work.mkdir(parents=True, exist_ok=True)
    failures = []
    deadline = time.monotonic() + MAX_PREFLIGHT_TOTAL_SECONDS
    for script_path, args, timeout in normalized:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            failures.append(f"{script_path}: skipped after preflight time limit")
            continue
        effective_timeout = min(timeout, max(1, int(remaining)))
        try:
            proc = subprocess.run(
                ["python3", str(OUTPUT / "artifacts" / script_path), *args],
                cwd=work,
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "HOME": "/tmp",
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=effective_timeout,
            )
        except subprocess.TimeoutExpired:
            failures.append(
                f"{script_path}: timed out after {effective_timeout}s preflight limit"
            )
            continue
        if proc.returncode != 0:
            output_tail = " ".join(proc.stdout[-160:].split())
            failures.append(
                f"{script_path}: exit {proc.returncode}: {output_tail}"
            )
    if failures:
        raise ReplayPreflightError(
            "candidate replay preflight failed: " + " | ".join(failures)
        )


def unix_chat(payload: dict, socket_path: Path = MODEL_SOCKET) -> dict:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    request = (
        b"POST /v1/chat/completions HTTP/1.1\r\n"
        b"Host: foundry-model\r\n"
        b"Content-Type: application/json\r\n"
        + f"Content-Length: {len(body)}\r\n".encode()
        + b"Connection: close\r\n\r\n"
        + body
    )
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(600)
        sock.connect(str(socket_path))
        sock.sendall(request)
        chunks = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
    raw = b"".join(chunks)
    head, separator, response_body = raw.partition(b"\r\n\r\n")
    if not separator:
        raise RuntimeError("model proxy returned an invalid HTTP response")
    status_line = head.splitlines()[0].decode("ascii", errors="replace")
    try:
        status = int(status_line.split()[1])
    except (IndexError, ValueError) as exc:
        raise RuntimeError("model proxy returned an invalid HTTP status") from exc
    value = json.loads(response_body)
    if status >= 300:
        raise RuntimeError(f"model proxy HTTP {status}: {value}")
    return value


def execute_tool(name: str, args: dict) -> str:
    try:
        if name == "read_text":
            path = _workspace_path(str(args["path"]))
            limit = min(int(args.get("max_chars", MAX_TOOL_OUTPUT)), MAX_TOOL_OUTPUT)
            return path.read_text(errors="replace")[:limit]
        if name == "list_files":
            path = _workspace_path(str(args.get("path", ".")))
            limit = min(int(args.get("limit", 100)), 200)
            rows = []
            for item in sorted(path.rglob("*")):
                if len(rows) >= limit:
                    break
                if item.is_file() and _inside(item, WORKSPACE):
                    rows.append(str(item.relative_to(WORKSPACE)))
            return json.dumps(rows)
        if name == "run_command":
            argv = args["argv"]
            if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
                raise ValueError("argv must be a non-empty string array")
            work = OUTPUT / "work"
            work.mkdir(parents=True, exist_ok=True)
            proc = subprocess.run(
                argv,
                cwd=work,
                env={"PATH": os.environ.get("PATH", ""), "HOME": "/tmp", "PYTHONDONTWRITEBYTECODE": "1"},
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=min(int(args.get("timeout_seconds", 60)), 180),
            )
            return json.dumps({"returncode": proc.returncode, "output": proc.stdout[-MAX_TOOL_OUTPUT:]})
        if name == "write_artifact":
            content = str(args["content"])
            if len(content.encode()) > 1_000_000:
                raise ValueError("artifact exceeds one megabyte")
            path = _artifact_path(str(args["path"]))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return json.dumps({"written": str(path.relative_to(OUTPUT)), "bytes": len(content.encode())})
        if name == "submit_result":
            result = dict(args)
            task = json.loads(TASK_PATH.read_text())
            result["schema"] = "p42-foundry-candidate-result-v2"
            result["evaluation_id"] = task.get("evaluation_id")
            result["seed"] = task.get("seed")
            result["task_packet_sha256"] = (
                "sha256:" + hashlib.sha256(_canonical_bytes(task)).hexdigest()
            )
            result["artifacts_claimed"] = _finalize_artifacts(
                result.pop("artifacts")
            )
            _preflight_replays(
                result.get("replay"), result["artifacts_claimed"]
            )
            result["artifacts"] = _artifact_inventory()
            result["independent_replay_status"] = "pending"
            (OUTPUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
            return json.dumps({"submitted": True, "authority": "none_pending_independent_replay"})
        raise ValueError(f"unknown tool: {name}")
    except Exception as exc:  # An error is data for the agent, not a sandbox escape.
        correction = isinstance(exc, ReplayPreflightError)
        return json.dumps({
            "error": "ValueError" if correction else type(exc).__name__,
            "message": str(exc)[: MAX_CORRECTION_MESSAGE if correction else 500],
        })


def run_smoke() -> int:
    response = unix_chat({
        "model": MODEL,
        "messages": [{"role": "user", "content": "Reply with exactly FOUNDRY_MODEL_OK"}],
        "temperature": 0,
        "max_tokens": 32,
        "stream": False,
    })
    content = str(response["choices"][0]["message"].get("content", ""))
    if "FOUNDRY_MODEL_OK" not in content:
        raise SystemExit("model-only transport response did not contain the smoke token")
    (OUTPUT / "model-transport-smoke.ok").write_text("model-only-ok")
    return 0


def run_task(task_path: Path) -> int:
    task = json.loads(task_path.read_text())
    max_calls = int(task["budget"]["max_api_calls"])
    system = (
        "You are the isolated Foundry math worker. Work verifier-first on the single task packet. "
        "Register one bounded hypothesis and executable falsifier before exploration. Use tools to "
        "inspect candidate code and run local checks. Separate witness/local evidence/certificate/theorem "
        "status. Put every final file under artifacts/, and give replay as argv objects of the form "
        "{\"argv\":[\"python3\",\"artifacts/check.py\"],\"timeout_seconds\":180,"
        "\"expected_exit\":0}; shell strings, inline Python, and nonzero expected exits are forbidden. "
        "Use only the bounded theorem_status classes exposed by submit_result. Never infer acceptance "
        "from your own classification. If canonical_artifact_contract is present, write exactly its "
        "artifact_path and satisfy its public schema; only the evaluator-owned verifier can score it. "
        "Pass artifact paths relative to the artifact root (for example check.py, not "
        "artifacts/check.py); the worker also normalizes one accidental artifacts/ prefix. "
        "A negative_result must say only what its bounded replay establishes: use language such "
        "as 'no witness found within this bounded search; theorem and bracket unchanged.' Never "
        "turn a timeout, heuristic search, or finite sample into nonexistence or an exact value. "
        "A successfully completed bounded negative search must exit zero on replay and print its "
        "bounded outcome; reserve nonzero exit status for an execution or verifier-invariant failure. "
        "Negative-search artifact output must not say that failure suggests, supports, or implies a "
        "Ramsey bound. For the C4/S17 task, a 22-vertex witness implies R(C4,S17)>=23. "
        "Submit only final evidence artifacts; scratch files are deleted at submission. Every final "
        "Python artifact must have its own zero-exit replay step, including verifier self-tests. "
        "Finish with submit_result. The evaluator reserves the final two API calls for typed "
        "submission; when that gate appears, stop exploring and submit the strongest bounded "
        "result supported by the artifacts, including negative_result or blocked when appropriate."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(task, ensure_ascii=False)},
    ]
    submission_start = max(0, max_calls - SUBMISSION_RESERVE_CALLS)
    for call_index in range(max_calls):
        submission_phase = call_index >= submission_start
        if call_index == submission_start:
            messages.append({
                "role": "user",
                "content": (
                    "SUBMISSION GATE: exploration is over. Use submit_result now. Report a "
                    "bounded negative_result or blocked outcome if no strict frontier improvement "
                    "was established; do not spend another call exploring. A failed search means "
                    "only no witness found within the stated budget, never nonexistence, an upper "
                    "bound, or an exact Ramsey value without a replayable proof certificate. Ensure "
                    "the submitted replay exits zero when that bounded negative experiment succeeds."
                ),
            })
        response = unix_chat({
            "model": MODEL,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": (
                {"type": "function", "function": {"name": "submit_result"}}
                if submission_phase else "auto"
            ),
            "temperature": 0.1,
            "seed": int(task["seed"]),
            "max_tokens": 4096,
            "stream": False,
        })
        message = response["choices"][0]["message"]
        messages.append({
            key: message.get(key)
            for key in ("role", "content", "tool_calls")
            if message.get(key) is not None
        })
        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            if not (OUTPUT / "result.json").exists():
                fallback = {
                    "schema": "p42-foundry-candidate-result-v1",
                    "classification": "blocked",
                    "claim": str(message.get("content", "")),
                    "independent_replay_status": "pending",
                    "contract_status": "unstructured_final_without_submit_result",
                }
                (OUTPUT / "result.json").write_text(json.dumps(fallback, indent=2) + "\n")
            return 0
        for call in tool_calls:
            function = call.get("function", {})
            try:
                arguments = json.loads(function.get("arguments") or "{}")
            except json.JSONDecodeError as exc:
                arguments = {"_parse_error": str(exc)}
            result = execute_tool(str(function.get("name", "")), arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": call.get("id", "missing"),
                "name": function.get("name", "unknown"),
                "content": result,
            })
            if function.get("name") == "submit_result" and (OUTPUT / "result.json").exists():
                return 0
    raise SystemExit("candidate exhausted API-call budget without submitting a result")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, default=TASK_PATH)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    return run_smoke() if args.smoke else run_task(args.task)


if __name__ == "__main__":
    raise SystemExit(main())

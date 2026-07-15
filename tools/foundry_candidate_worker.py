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
from pathlib import Path

WORKSPACE = Path("/workspace")
TASK_PATH = Path("/task/task.json")
OUTPUT = Path("/output")
MODEL_SOCKET = Path(os.environ.get("FOUNDRY_MODEL_SOCKET", "/model/model.sock"))
MODEL = os.environ.get("FOUNDRY_MODEL", "evaluator-forced-local-model")
MAX_TOOL_OUTPUT = 24_000


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
                    "artifacts": {"type": "array", "items": {"type": "string"}},
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
    path = root / raw
    if Path(raw).is_absolute() or not _inside(path, root):
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
            result["artifacts_claimed"] = result.pop("artifacts")
            result["artifacts"] = _artifact_inventory()
            result["independent_replay_status"] = "pending"
            (OUTPUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
            return json.dumps({"submitted": True, "authority": "none_pending_independent_replay"})
        raise ValueError(f"unknown tool: {name}")
    except Exception as exc:  # An error is data for the agent, not a sandbox escape.
        return json.dumps({"error": type(exc).__name__, "message": str(exc)[:500]})


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
        "Finish with submit_result."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(task, ensure_ascii=False)},
    ]
    for _ in range(max_calls):
        response = unix_chat({
            "model": MODEL,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
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

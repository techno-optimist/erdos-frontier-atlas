#!/usr/bin/env python3
"""Frozen-suite and Docker-isolation controller for Foundry outer-loop evals.

The controller runs on the evaluator host. A candidate receives one task packet
at a time; the private suite manifest is never mounted into its container.
This module does not grant promotion authority or score mathematical claims.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import http.client
import http.server
import json
import os
import secrets
import socketserver
import subprocess
import tempfile
import threading
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "atlas" / "problems.json"
PROTOCOL = ROOT / "foundry" / "rsi_protocol.json"
PUBLIC_SUITE = ROOT / "foundry" / "eval" / "public_suite.json"
CANONICAL_CONTRACTS = ROOT / "foundry" / "eval" / "canonical_contracts.json"
PRIVATE_ROOT = Path.home() / ".hermes" / "chronos_state" / "foundry_eval"
PRIVATE_MANIFEST = PRIVATE_ROOT / "private_suite.json"
PRIVATE_COMMITMENT = PRIVATE_ROOT / "private_suite.commitment.json"
DEFAULT_EVAL_IMAGE = "p42-verifier-v2:hadamard-mini"
MODEL_HOST = "127.0.0.1"
MODEL_PORT = 30000

FAMILY_LANES = {
    "exact_witness_or_backtracking": {"exact-backtracking"},
    "nonexistence_or_certificate": {"SAT+DRAT-nonexistence", "LP/SDP-certificate"},
    "constructive_or_local_search": {"witness-local-search"},
}


def canonical_bytes(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_json(path: Path, value: dict, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.chmod(mode)
    tmp.replace(path)


def family_for(problem: dict) -> str | None:
    lane = problem.get("lane")
    return next((family for family, lanes in FAMILY_LANES.items() if lane in lanes), None)


def build_private_manifest(
    atlas: dict,
    public_suite: dict,
    protocol: dict,
    salt_hex: str,
    created_at: str,
) -> dict:
    salt = bytes.fromhex(salt_hex)
    if len(salt) < 32:
        raise ValueError("private split salt must contain at least 32 bytes")
    public_ids = {int(row["problem_id"]) for row in public_suite["tasks"]}
    per_family = int(protocol["evaluation"]["private_holdout_tasks"]) // len(FAMILY_LANES)
    if per_family * len(FAMILY_LANES) != int(protocol["evaluation"]["private_holdout_tasks"]):
        raise ValueError("private holdout task count must divide evenly across families")
    grouped: dict[str, list[tuple[str, dict]]] = {family: [] for family in FAMILY_LANES}
    for problem in atlas["problems"]:
        problem_id = int(problem["id"])
        family = family_for(problem)
        if not family or problem_id in public_ids or problem.get("board_class") == "NONE":
            continue
        rank = hmac.new(salt, f"select:{family}:{problem_id}".encode(), hashlib.sha256).hexdigest()
        grouped[family].append((rank, problem))
    tasks = []
    for family in FAMILY_LANES:
        candidates = sorted(grouped[family], key=lambda row: row[0])
        if len(candidates) < per_family:
            raise ValueError(f"not enough eligible private tasks for {family}")
        for _, problem in candidates[:per_family]:
            problem_id = int(problem["id"])
            opaque = hmac.new(salt, f"task:{problem_id}".encode(), hashlib.sha256).hexdigest()[:20]
            tasks.append({
                "task_id": "holdout_" + opaque,
                "problem_id": problem_id,
                "family": family,
            })
    return {
        "schema": "p42-foundry-private-eval-suite-v1",
        "suite_version": protocol["protocol_version"],
        "created_at": created_at,
        "atlas_version": atlas["atlas_version"],
        "public_suite_version": public_suite["suite_version"],
        "split_salt_hex": salt_hex,
        "tasks": tasks,
    }


def build_commitment(manifest: dict) -> dict:
    counts = Counter(row["family"] for row in manifest["tasks"])
    return {
        "schema": "p42-foundry-private-suite-commitment-v1",
        "suite_version": manifest["suite_version"],
        "created_at": manifest["created_at"],
        "atlas_version": manifest["atlas_version"],
        "public_suite_version": manifest["public_suite_version"],
        "manifest_sha256": "sha256:" + sha256(canonical_bytes(manifest)),
        "task_count": len(manifest["tasks"]),
        "family_counts": dict(sorted(counts.items())),
        "task_ids_or_problem_ids_disclosed": False,
    }


def validate_private(manifest: dict, commitment: dict, protocol: dict) -> list[str]:
    errors = []
    if manifest.get("schema") != "p42-foundry-private-eval-suite-v1":
        errors.append("bad private manifest schema")
    if commitment.get("schema") != "p42-foundry-private-suite-commitment-v1":
        errors.append("bad private commitment schema")
    tasks = manifest.get("tasks", [])
    expected = int(protocol["evaluation"]["private_holdout_tasks"])
    if len(tasks) != expected:
        errors.append(f"expected {expected} private tasks, found {len(tasks)}")
    if len({row.get("task_id") for row in tasks}) != len(tasks):
        errors.append("duplicate private task_id")
    if len({row.get("problem_id") for row in tasks}) != len(tasks):
        errors.append("duplicate private problem_id")
    expected_per_family = expected // len(FAMILY_LANES)
    counts = Counter(row.get("family") for row in tasks)
    if counts != Counter({family: expected_per_family for family in FAMILY_LANES}):
        errors.append("private family balance mismatch")
    expected_digest = "sha256:" + sha256(canonical_bytes(manifest))
    if commitment.get("manifest_sha256") != expected_digest:
        errors.append("private commitment digest mismatch")
    if commitment.get("task_count") != len(tasks):
        errors.append("private commitment task count mismatch")
    if commitment.get("family_counts") != dict(sorted(counts.items())):
        errors.append("private commitment family counts mismatch")
    for key in ("suite_version", "atlas_version", "public_suite_version"):
        if commitment.get(key) != manifest.get(key):
            errors.append(f"private commitment {key} mismatch")
    if commitment.get("task_ids_or_problem_ids_disclosed") is not False:
        errors.append("private commitment disclosure flag missing")
    try:
        if len(bytes.fromhex(str(manifest.get("split_salt_hex", "")))) < 32:
            errors.append("private split salt is too short")
    except ValueError:
        errors.append("private split salt is not hexadecimal")
    return errors


def make_task_packet(
    task: dict, atlas: dict, protocol: dict, seed: int
) -> dict:
    by_id = {int(row["id"]): row for row in atlas["problems"]}
    problem = by_id[int(task["problem_id"])]
    budget = dict(protocol["evaluation"]["budget_per_task_run"])
    contracts = load(CANONICAL_CONTRACTS).get("contracts", {})
    value = {
        "schema": "p42-foundry-eval-task-v1",
        "protocol_version": protocol["protocol_version"],
        "evaluation_id": task.get("task_id") or task.get("frontier_id"),
        "family": task["family"],
        "seed": int(seed),
        "budget": budget,
        "target": {
            key: problem.get(key)
            for key in (
                "id", "title", "statement", "finite_object", "current_record",
                "verifier", "attack", "verdict", "lane", "erdos_url",
            )
        },
        "required_result": {
            "hypothesis": "one explicit bounded hypothesis",
            "falsifier": "one executable falsifier registered before work",
            "artifacts": "content-addressed final artifacts with replay commands",
            "claim_boundary": "witness, local result, certificate, and theorem status separated",
        },
        "authority": {
            "promotion": "none",
            "atlas_writes": False,
            "external_submission": False,
            "frontier_calls": False,
        },
        "split_disclosure": "undisclosed_to_candidate",
    }
    contract = contracts.get(str(problem["id"]))
    if contract:
        value["canonical_artifact_contract"] = contract
    return value


def docker_sandbox_command(
    image: str, workspace: Path, task_packet: Path, output_dir: Path
) -> list[str]:
    workspace = workspace.resolve()
    task_packet = task_packet.resolve()
    output_dir = output_dir.resolve()
    return [
        "docker", "run", "--rm",
        "--network", "none",
        "--read-only",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--pids-limit", "64",
        "--memory", "256m",
        "--cpus", "1",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "--tmpfs", "/tmp:rw,nosuid,nodev,size=64m",
        "--mount", f"type=bind,src={workspace},dst=/workspace,readonly",
        "--mount", f"type=bind,src={task_packet},dst=/task/task.json,readonly",
        "--mount", f"type=bind,src={output_dir},dst=/output",
        "--workdir", "/workspace",
        image,
        "/bin/sh", "-ec",
        "test -r /task/task.json; "
        "test ! -e /home/chronos/.hermes/chronos_state; "
        "test ! -e /var/run/docker.sock; "
        "test \"$(ls /sys/class/net | tr -d '\\n')\" = lo; "
        "printf sandbox-ok > /output/sandbox-smoke.ok",
    ]


def run_sandbox_smoke(
    image: str,
    workspace: Path,
    task_packet: Path,
    output_dir: Path,
    private_manifest: Path,
) -> dict:
    private_resolved = private_manifest.resolve()
    command = docker_sandbox_command(image, workspace, task_packet, output_dir)
    if str(private_resolved) in " ".join(command):
        raise ValueError("private manifest must never be mounted into candidate sandbox")
    output_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    marker = output_dir / "sandbox-smoke.ok"
    ok = bool(marker.exists() and proc.returncode == 0 and marker.read_text() == "sandbox-ok")
    return {
        "schema": "p42-foundry-sandbox-smoke-v1",
        "ok": ok,
        "image": image,
        "network_mode": "none",
        "root_filesystem": "read_only",
        "capabilities": "all_dropped",
        "private_manifest_mounted": False,
        "docker_socket_mounted": False,
        "workspace_mode": "read_only",
        "task_packet_mode": "read_only",
        "output_mode": "read_write",
        "returncode": proc.returncode,
        "output_tail": proc.stdout[-500:],
    }


class BudgetRejected(ValueError):
    """The evaluator refused a model request before it reached the endpoint."""


class ModelProxyState:
    """Thread-safe, evaluator-owned accounting for the Unix-only model proxy."""

    def __init__(self, budget: dict, model: str):
        self.budget = {
            "max_api_calls": int(budget["max_api_calls"]),
            "max_input_tokens": int(budget["max_input_tokens"]),
            "max_output_tokens": int(budget["max_output_tokens"]),
        }
        self.model = model
        self.api_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.reserved_input_tokens = 0
        self.reserved_output_tokens = 0
        self.denied_requests = 0
        self.upstream_errors = 0
        self.missing_usage = 0
        self.lock = threading.Lock()

    def prepare(self, payload: dict, request_bytes: int) -> tuple[dict, tuple[int, int]]:
        if not isinstance(payload, dict) or not isinstance(payload.get("messages"), list):
            raise BudgetRejected("chat payload must contain a messages array")
        with self.lock:
            if self.api_calls >= self.budget["max_api_calls"]:
                self.denied_requests += 1
                raise BudgetRejected("API-call budget exhausted")
            # Byte length is a conservative upper bound for byte-fallback BPE
            # prompt tokens. The reserve covers chat-template control tokens.
            input_reservation = request_bytes + 4096
            if (
                self.input_tokens + self.reserved_input_tokens + input_reservation
                > self.budget["max_input_tokens"]
            ):
                self.denied_requests += 1
                raise BudgetRejected("input-token budget cannot admit this request")
            remaining_output = (
                self.budget["max_output_tokens"]
                - self.output_tokens
                - self.reserved_output_tokens
            )
            if remaining_output <= 0:
                self.denied_requests += 1
                raise BudgetRejected("output-token budget exhausted")
            try:
                requested_output = int(payload.get("max_tokens", min(4096, remaining_output)))
            except (TypeError, ValueError) as exc:
                raise BudgetRejected("max_tokens must be an integer") from exc
            if requested_output <= 0:
                raise BudgetRejected("max_tokens must be positive")
            self.api_calls += 1
            sanitized = dict(payload)
            sanitized["model"] = self.model
            sanitized["stream"] = False
            sanitized["max_tokens"] = min(requested_output, remaining_output)
            sanitized["n"] = 1
            sanitized["chat_template_kwargs"] = {"enable_thinking": False}
            sanitized.pop("max_completion_tokens", None)
            output_reservation = int(sanitized["max_tokens"])
            self.reserved_input_tokens += input_reservation
            self.reserved_output_tokens += output_reservation
            return sanitized, (input_reservation, output_reservation)

    def record(self, response: dict, reservation: tuple[int, int]) -> None:
        usage = response.get("usage") if isinstance(response, dict) else None
        try:
            prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
            completion_tokens = int(usage.get("completion_tokens", 0) or 0)
            usage_valid = isinstance(usage, dict)
        except (AttributeError, TypeError, ValueError):
            prompt_tokens = completion_tokens = 0
            usage_valid = False
        with self.lock:
            self.reserved_input_tokens -= reservation[0]
            self.reserved_output_tokens -= reservation[1]
            if not usage_valid:
                self.missing_usage += 1
                return
            self.input_tokens += prompt_tokens
            self.output_tokens += completion_tokens

    def record_upstream_error(self, reservation: tuple[int, int]) -> None:
        with self.lock:
            self.reserved_input_tokens -= reservation[0]
            self.reserved_output_tokens -= reservation[1]
            self.upstream_errors += 1

    def report(self) -> dict:
        with self.lock:
            budget_ok = bool(
                self.api_calls <= self.budget["max_api_calls"]
                and self.input_tokens <= self.budget["max_input_tokens"]
                and self.output_tokens <= self.budget["max_output_tokens"]
                and self.reserved_input_tokens == 0
                and self.reserved_output_tokens == 0
                and self.missing_usage == 0
                and self.upstream_errors == 0
            )
            return {
                "api_calls": self.api_calls,
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "in_flight_input_reservation": self.reserved_input_tokens,
                "in_flight_output_reservation": self.reserved_output_tokens,
                "denied_requests": self.denied_requests,
                "upstream_errors": self.upstream_errors,
                "missing_usage_responses": self.missing_usage,
                "limits": dict(self.budget),
                "budget_ok": budget_ok,
            }


class UnixModelProxy(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


class ModelProxyHandler(http.server.BaseHTTPRequestHandler):
    server_version = "FoundryModelMembrane/1"

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _send_json(self, status: int, value: dict) -> None:
        body = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self._send_json(403, {"error": "model membrane permits only chat completions"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "invalid content length"})
            return
        if length <= 0 or length > 16_000_000:
            self._send_json(413, {"error": "request body outside model membrane limit"})
            return
        raw = self.rfile.read(length)
        reservation = None
        try:
            payload = json.loads(raw)
            payload, reservation = self.server.proxy_state.prepare(payload, len(raw))  # type: ignore[attr-defined]
        except (json.JSONDecodeError, BudgetRejected) as exc:
            self._send_json(429 if isinstance(exc, BudgetRejected) else 400, {"error": str(exc)})
            return
        connection = http.client.HTTPConnection(
                self.server.model_host,  # type: ignore[attr-defined]
                self.server.model_port,  # type: ignore[attr-defined]
                timeout=self.server.model_timeout,  # type: ignore[attr-defined]
        )
        try:
            encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
            connection.request(
                "POST", "/v1/chat/completions", body=encoded,
                headers={"Content-Type": "application/json", "Authorization": "Bearer local"},
            )
            upstream = connection.getresponse()
            body = upstream.read()
            parsed = json.loads(body)
            if upstream.status < 300:
                self.server.proxy_state.record(parsed, reservation)  # type: ignore[attr-defined]
            else:
                self.server.proxy_state.record_upstream_error(reservation)  # type: ignore[attr-defined]
        except Exception as exc:
            self.server.proxy_state.record_upstream_error(reservation)  # type: ignore[attr-defined]
            self._send_json(502, {"error": type(exc).__name__ + ": " + str(exc)[:300]})
            return
        finally:
            connection.close()
        self.send_response(upstream.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)


@contextmanager
def model_only_proxy(
    socket_path: Path,
    state: ModelProxyState,
    model_host: str = MODEL_HOST,
    model_port: int = MODEL_PORT,
    timeout: int = 600,
):
    if model_host != MODEL_HOST or int(model_port) != MODEL_PORT:
        raise ValueError(f"model proxy upstream is frozen at {MODEL_HOST}:{MODEL_PORT}")
    socket_path.parent.mkdir(parents=True, exist_ok=True)
    socket_path.parent.chmod(0o700)
    socket_path.unlink(missing_ok=True)
    server = UnixModelProxy(str(socket_path), ModelProxyHandler)
    server.proxy_state = state
    server.model_host = model_host
    server.model_port = int(model_port)
    server.model_timeout = int(timeout)
    socket_path.chmod(0o600)
    thread = threading.Thread(target=server.serve_forever, name="foundry-model-proxy", daemon=True)
    thread.start()
    try:
        yield
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        socket_path.unlink(missing_ok=True)


def candidate_sandbox_command(
    image: str,
    workspace: Path,
    task_packet: Path,
    output_dir: Path,
    model_socket_dir: Path,
    model: str,
    smoke: bool = False,
) -> list[str]:
    command = [
        "docker", "run", "--rm",
        "--network", "none",
        "--read-only",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--pids-limit", "256",
        "--memory", "4g",
        "--cpus", "4",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "--tmpfs", "/tmp:rw,nosuid,nodev,size=1g",
        "--mount", f"type=bind,src={workspace.resolve()},dst=/workspace,readonly",
        "--mount", f"type=bind,src={task_packet.resolve()},dst=/task/task.json,readonly",
        "--mount", f"type=bind,src={output_dir.resolve()},dst=/output",
        "--mount", f"type=bind,src={model_socket_dir.resolve()},dst=/model,readonly",
        "--env", "FOUNDRY_MODEL_SOCKET=/model/model.sock",
        "--env", f"FOUNDRY_MODEL={model}",
        "--workdir", "/workspace",
        "--entrypoint", "/usr/local/bin/python3",
        image,
        "/workspace/tools/foundry_candidate_worker.py",
        "--task", "/task/task.json",
    ]
    if smoke:
        command.append("--smoke")
    return command


def resolve_image_id(image: str) -> str:
    proc = subprocess.run(
        ["docker", "image", "inspect", "--format", "{{.Id}}", image],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    image_id = proc.stdout.strip()
    if proc.returncode != 0 or not image_id.startswith("sha256:"):
        raise RuntimeError(f"evaluation image is unavailable: {image}: {proc.stderr[-300:]}")
    return image_id


def run_model_sandbox(
    image: str,
    workspace: Path,
    task_packet: Path,
    output_dir: Path,
    private_manifest: Path,
    model_host: str = MODEL_HOST,
    model_port: int = MODEL_PORT,
    smoke: bool = False,
) -> dict:
    packet = load(task_packet)
    if packet.get("schema") != "p42-foundry-eval-task-v1":
        raise ValueError("model sandbox requires exactly one generated evaluation task packet")
    frozen_budget = load(PROTOCOL)["evaluation"]["budget_per_task_run"]
    if packet.get("budget") != frozen_budget:
        raise ValueError("task packet does not carry the frozen evaluation budget")
    if packet.get("authority") != {
        "promotion": "none",
        "atlas_writes": False,
        "external_submission": False,
        "frontier_calls": False,
    }:
        raise ValueError("task packet authority boundary is missing or modified")
    if packet.get("split_disclosure") != "undisclosed_to_candidate":
        raise ValueError("task packet split-disclosure boundary is missing or modified")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("candidate output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    budget = dict(packet["budget"])
    if smoke:
        budget.update({
            "max_api_calls": 1,
            "max_input_tokens": min(int(budget["max_input_tokens"]), 20_000),
            "max_output_tokens": min(int(budget["max_output_tokens"]), 256),
            "max_wall_seconds": min(int(budget["max_wall_seconds"]), 120),
        })
    image_id = resolve_image_id(image)
    model = str(packet["budget"]["model"])
    state = ModelProxyState(budget, model)
    timed_out = False
    with tempfile.TemporaryDirectory(prefix="fmeval-", dir="/tmp") as proxy_tmp:
        socket_dir = Path(proxy_tmp)
        socket_path = socket_dir / "model.sock"
        command = candidate_sandbox_command(
            image_id, workspace, task_packet, output_dir, socket_dir, model, smoke=smoke
        )
        if str(private_manifest.resolve()) in " ".join(command):
            raise ValueError("private manifest must never be mounted into candidate sandbox")
        with model_only_proxy(socket_path, state, model_host, model_port):
            try:
                proc = subprocess.run(
                    command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    timeout=int(budget["max_wall_seconds"]),
                )
            except subprocess.TimeoutExpired as exc:
                timed_out = True
                partial = "".join(
                    value.decode(errors="replace") if isinstance(value, bytes) else str(value or "")
                    for value in (exc.stdout, exc.stderr)
                )
                proc = subprocess.CompletedProcess(command, 124, partial)
    model_report = state.report()
    marker = output_dir / "model-transport-smoke.ok"
    result = output_dir / "result.json"
    artifact = marker if smoke else result
    ok = bool(
        proc.returncode == 0 and not timed_out and model_report["budget_ok"]
        and artifact.exists()
        and (not smoke or marker.read_text() == "model-only-ok")
    )
    return {
        "schema": "p42-foundry-model-transport-v1",
        "created_at": iso_now(),
        "ok": ok,
        "mode": "smoke" if smoke else "candidate_run",
        "image": image,
        "image_id": image_id,
        "candidate_network": "none",
        "model_transport": "mounted_unix_socket_only",
        "model_upstream": "evaluator_loopback_only",
        "model_upstream_host": model_host,
        "model_upstream_port": int(model_port),
        "root_filesystem": "read_only",
        "capabilities": "all_dropped",
        "private_manifest_mounted": False,
        "docker_socket_mounted": False,
        "workspace_mode": "read_only",
        "task_packet_count": 1,
        "output_mode": "read_write",
        "budget": model_report,
        "timed_out": timed_out,
        "returncode": proc.returncode,
        "artifact_sha256": "sha256:" + sha256(artifact.read_bytes()) if artifact.exists() else None,
        "output_tail": str(proc.stdout)[-1000:],
        "promotion_authority": "none_pending_independent_replay",
    }


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init-private")
    init.add_argument("--manifest", type=Path, default=PRIVATE_MANIFEST)
    init.add_argument("--commitment", type=Path, default=PRIVATE_COMMITMENT)
    init.add_argument("--salt-hex")

    validate = sub.add_parser("validate-private")
    validate.add_argument("--manifest", type=Path, default=PRIVATE_MANIFEST)
    validate.add_argument("--commitment", type=Path, default=PRIVATE_COMMITMENT)

    packet = sub.add_parser("packet")
    packet.add_argument("--split", choices=("public", "private"), required=True)
    packet.add_argument("--task", required=True, help="frontier_id/task_id or zero-based index")
    packet.add_argument("--seed", type=int, required=True)
    packet.add_argument("--manifest", type=Path, default=PRIVATE_MANIFEST)
    packet.add_argument("--output", type=Path, required=True)

    smoke = sub.add_parser("sandbox-smoke")
    smoke.add_argument("--image", default="alpine:3.22")
    smoke.add_argument("--workspace", type=Path, default=ROOT)
    smoke.add_argument("--task-packet", type=Path, default=PUBLIC_SUITE)
    smoke.add_argument("--output-dir", type=Path)
    smoke.add_argument("--private-manifest", type=Path, default=PRIVATE_MANIFEST)

    model_smoke = sub.add_parser("model-transport-smoke")
    model_smoke.add_argument("--image", default=DEFAULT_EVAL_IMAGE)
    model_smoke.add_argument("--workspace", type=Path, default=ROOT)
    model_smoke.add_argument("--task-packet", type=Path, required=True)
    model_smoke.add_argument("--output-dir", type=Path)
    model_smoke.add_argument("--private-manifest", type=Path, default=PRIVATE_MANIFEST)
    model_smoke.add_argument("--model-host", default=MODEL_HOST)
    model_smoke.add_argument("--model-port", type=int, default=MODEL_PORT)
    model_smoke.add_argument("--report", type=Path)

    candidate = sub.add_parser("candidate-run")
    candidate.add_argument("--image", default=DEFAULT_EVAL_IMAGE)
    candidate.add_argument("--workspace", type=Path, default=ROOT)
    candidate.add_argument("--task-packet", type=Path, required=True)
    candidate.add_argument("--output-dir", type=Path, required=True)
    candidate.add_argument("--private-manifest", type=Path, default=PRIVATE_MANIFEST)
    candidate.add_argument("--model-host", default=MODEL_HOST)
    candidate.add_argument("--model-port", type=int, default=MODEL_PORT)
    candidate.add_argument("--report", type=Path)

    args = parser.parse_args()
    protocol, atlas, public = load(PROTOCOL), load(ATLAS), load(PUBLIC_SUITE)

    if args.command == "init-private":
        if args.manifest.exists() or args.commitment.exists():
            raise SystemExit("refusing to reroll an existing private suite")
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.parent.chmod(0o700)
        manifest = build_private_manifest(
            atlas, public, protocol, args.salt_hex or secrets.token_hex(32), iso_now()
        )
        commitment = build_commitment(manifest)
        atomic_json(args.manifest, manifest, 0o600)
        atomic_json(args.commitment, commitment, 0o644)
        print(json.dumps(commitment, indent=2))
        return 0

    if args.command == "validate-private":
        manifest, commitment = load(args.manifest), load(args.commitment)
        errors = validate_private(manifest, commitment, protocol)
        if args.manifest.stat().st_mode & 0o777 != 0o600:
            errors.append("private manifest mode is not 0600")
        print(json.dumps({"valid": not errors, "errors": errors, "commitment": commitment}, indent=2))
        return 0 if not errors else 1

    if args.command == "packet":
        tasks = public["tasks"] if args.split == "public" else load(args.manifest)["tasks"]
        if args.task.isdigit():
            task = tasks[int(args.task)]
        else:
            task = next(row for row in tasks if args.task in {row.get("task_id"), row.get("frontier_id")})
        value = make_task_packet(task, atlas, protocol, args.seed)
        atomic_json(args.output, value, 0o400)
        print(json.dumps({"output": str(args.output), "sha256": sha256(canonical_bytes(value))}, indent=2))
        return 0

    if args.command == "sandbox-smoke":
        if not args.private_manifest.exists():
            raise SystemExit("private manifest is absent; initialize and commit it before isolation smoke")
        if args.output_dir:
            report = run_sandbox_smoke(
                args.image, args.workspace, args.task_packet, args.output_dir, args.private_manifest
            )
        else:
            with tempfile.TemporaryDirectory() as tmp:
                report = run_sandbox_smoke(
                    args.image, args.workspace, args.task_packet, Path(tmp), args.private_manifest
                )
        print(json.dumps(report, indent=2))
        return 0 if report["ok"] else 1

    if args.command == "model-transport-smoke":
        if not args.private_manifest.exists():
            raise SystemExit("private manifest is absent; initialize it before model isolation smoke")
        if args.output_dir:
            report = run_model_sandbox(
                args.image, args.workspace, args.task_packet, args.output_dir,
                args.private_manifest, args.model_host, args.model_port, smoke=True,
            )
        else:
            with tempfile.TemporaryDirectory() as tmp:
                report = run_model_sandbox(
                    args.image, args.workspace, args.task_packet, Path(tmp),
                    args.private_manifest, args.model_host, args.model_port, smoke=True,
                )
        if args.report:
            atomic_json(args.report, report, 0o600)
        print(json.dumps(report, indent=2))
        return 0 if report["ok"] else 1

    if args.command == "candidate-run":
        if not args.private_manifest.exists():
            raise SystemExit("private manifest is absent; initialize it before candidate evaluation")
        report = run_model_sandbox(
            args.image, args.workspace, args.task_packet, args.output_dir,
            args.private_manifest, args.model_host, args.model_port, smoke=False,
        )
        if args.report:
            atomic_json(args.report, report, 0o600)
        print(json.dumps(report, indent=2))
        return 0 if report["ok"] else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

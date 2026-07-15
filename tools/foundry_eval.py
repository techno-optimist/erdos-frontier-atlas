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
import json
import os
import secrets
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "atlas" / "problems.json"
PROTOCOL = ROOT / "foundry" / "rsi_protocol.json"
PUBLIC_SUITE = ROOT / "foundry" / "eval" / "public_suite.json"
PRIVATE_ROOT = Path.home() / ".hermes" / "chronos_state" / "foundry_eval"
PRIVATE_MANIFEST = PRIVATE_ROOT / "private_suite.json"
PRIVATE_COMMITMENT = PRIVATE_ROOT / "private_suite.commitment.json"

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
    return {
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

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

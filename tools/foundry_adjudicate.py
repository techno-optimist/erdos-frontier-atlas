#!/usr/bin/env python3
"""Independent replay and paired comparison for Foundry candidate artifacts.

This program is evaluator-owned.  It never imports code from a candidate
workspace, never exposes the model transport, and never grants promotion
authority.  Candidate artifacts are replayed in a fresh no-network container.
Candidate-authored replay proves reproducibility only and earns zero utility;
promotion-bearing units require a separately registered evaluator-owned
canonical verdict bound to the task and candidate-result hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shlex
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "foundry" / "rsi_protocol.json"
DEFAULT_EVAL_IMAGE = "p42-verifier-v2:hadamard-mini"
CANONICAL_VERDICT_ROOT = (
    Path.home() / ".hermes" / "chronos_state" / "foundry_eval" / "canonical_verdicts"
)
CANONICAL_VERIFIER_SOURCES = {
    verifier_id: ROOT / "tools" / "foundry_canonical_verify.py"
    for verifier_id in (
        "erdos-1-distinct-subset-sums-v1",
        "erdos-21-q6-v1",
        "erdos-138-van-der-waerden-v1",
        "erdos-552-c4-star-v1",
    )
}
MAX_ARTIFACT_BYTES = 1_000_000
MAX_TOTAL_ARTIFACT_BYTES = 16_000_000
MAX_ARTIFACT_FILES = 128
MAX_REPLAY_STEPS = 8
ALLOWED_THEOREM_STATUS = {
    "witness_only",
    "local_result_only",
    "certificate_pending",
    "theorem_unchanged",
}


class AdjudicationError(ValueError):
    """The candidate output is structurally unsafe or not replayable."""


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise AdjudicationError(f"expected JSON object: {path}")
    return value


def atomic_json(path: Path, value: dict, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.chmod(mode)
    tmp.replace(path)


def resolve_image_id(image: str) -> str:
    proc = subprocess.run(
        ["docker", "image", "inspect", "--format", "{{.Id}}", image],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    image_id = proc.stdout.strip()
    if proc.returncode != 0 or not image_id.startswith("sha256:"):
        raise AdjudicationError(
            f"evaluation image is unavailable: {image}: {proc.stderr[-300:]}"
        )
    return image_id


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def artifact_inventory(root: Path) -> list[dict]:
    """Content-address every bounded regular file beneath ``root``."""
    if not root.is_dir():
        return []
    rows: list[dict] = []
    total = 0
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise AdjudicationError("artifact tree contains a symlink")
        if not path.is_file():
            continue
        if len(rows) >= MAX_ARTIFACT_FILES:
            raise AdjudicationError("artifact set exceeds file-count limit")
        if not _inside(path, root):
            raise AdjudicationError("artifact path escapes artifact root")
        if len(path.relative_to(root).as_posix()) > 240:
            raise AdjudicationError("artifact path exceeds length limit")
        size = path.stat().st_size
        if size > MAX_ARTIFACT_BYTES:
            raise AdjudicationError("artifact exceeds one-megabyte limit")
        total += size
        if total > MAX_TOTAL_ARTIFACT_BYTES:
            raise AdjudicationError("artifact set exceeds total byte limit")
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256_file(path),
                "bytes": size,
            }
        )
    return rows


def _claimed_artifact_paths(result: dict) -> set[str]:
    claimed = result.get("artifacts", [])
    if not isinstance(claimed, list):
        raise AdjudicationError("artifacts must be an array")
    paths: set[str] = set()
    for row in claimed:
        if isinstance(row, dict):
            path = row.get("path")
            evaluator_relative = True
        elif isinstance(row, str):
            # Legacy v1 workers described artifacts as strings.  Accept only
            # an unambiguous path token; the evaluator supplies the digest.
            tokens = shlex.split(row)
            path = next(
                (
                    token
                    for token in tokens
                    if token.startswith("artifacts/")
                    or token.startswith("/output/artifacts/")
                ),
                tokens[0] if len(tokens) == 1 else None,
            )
            evaluator_relative = False
        else:
            path = None
            evaluator_relative = False
        if not isinstance(path, str) or not path:
            raise AdjudicationError("artifact claim lacks a bounded path")
        if not evaluator_relative:
            path = path.removeprefix("/output/artifacts/").removeprefix("artifacts/")
        candidate = Path(path)
        if candidate.is_absolute() or ".." in candidate.parts or path in {"", "."}:
            raise AdjudicationError("artifact claim escapes artifact root")
        paths.add(candidate.as_posix())
    return paths


def semantic_contract_violations(result: dict, packet: dict) -> list[str]:
    """Reject theorem inflation that a replayable bounded search cannot establish."""
    violations = []
    claim = " ".join(
        str(result.get(key, "")) for key in ("hypothesis", "claim")
    ).lower()
    if result.get("classification") == "negative_result":
        observation_markers = (
            "bounded", "no witness found", "did not find", "inconclusive",
            "failed to find", "local exhaustion", "route closed",
        )
        boundary_markers = (
            "theorem unchanged", "bracket unchanged", "does not prove",
            "not a proof", "cannot conclude", "local result only",
        )
        if not any(marker in claim for marker in observation_markers) or not any(
            marker in claim for marker in boundary_markers
        ):
            violations.append("negative_result_lacks_bounded_claim_boundary")
    if int((packet.get("target") or {}).get("id", -1)) == 552:
        normalized = re.sub(r"[\s_{}\\]", "", claim)
        unsupported_nonexistence = bool(
            re.search(r"no\s+c4[- ]free\s+graph.{0,100}\b(?:exists|exist)\b", claim)
            or re.search(r"r\(c4,s17\)(?:=|<=)22", normalized)
            or re.search(r"r\(c4,k1,?17\)(?:=|<=)22", normalized)
            or (
                ("prove" in claim or "therefore" in claim)
                and (
                    "upper bound" in claim
                    or "nonexistence" in claim
                    or "no c4-free" in claim
                )
            )
        )
        explicit_boundary = any(
            marker in claim
            for marker in (
                "does not prove", "not a proof", "cannot conclude", "theorem unchanged"
            )
        )
        if unsupported_nonexistence and not explicit_boundary:
            violations.append(
                "erdos_552_nonexistence_claim_without_replayable_proof"
            )
    return violations


def _normalized_replay_step(step: object, inventory: list[dict]) -> dict:
    if isinstance(step, str):
        argv = shlex.split(step)
        timeout_seconds = 180
        expected_exit = 0
    elif isinstance(step, dict):
        argv = step.get("argv")
        timeout_seconds = step.get("timeout_seconds", 180)
        expected_exit = step.get("expected_exit", 0)
    else:
        raise AdjudicationError("replay step must be an argv object")
    if not isinstance(argv, list) or len(argv) < 2 or not all(
        isinstance(value, str) and value for value in argv
    ):
        raise AdjudicationError("replay argv must contain an executable and artifact")
    if argv[0] not in {"python", "python3", "/usr/local/bin/python3"}:
        raise AdjudicationError("replay executable must be the frozen Python runtime")
    script = argv[1]
    if script in {"-c", "-m", "-"}:
        raise AdjudicationError("inline or module replay is forbidden")
    script = script.removeprefix("/output/artifacts/").removeprefix("/artifacts/")
    script = script.removeprefix("artifacts/")
    script_path = Path(script)
    if (
        script_path.is_absolute()
        or ".." in script_path.parts
        or script_path.suffix != ".py"
    ):
        raise AdjudicationError("replay script must be a Python artifact path")
    known = {row["path"] for row in inventory}
    if script_path.as_posix() not in known:
        raise AdjudicationError("replay script is absent from content-addressed artifacts")
    try:
        timeout = int(timeout_seconds)
        expected = int(expected_exit)
    except (TypeError, ValueError) as exc:
        raise AdjudicationError("replay timeout/exit must be integers") from exc
    if timeout < 1 or timeout > 180:
        raise AdjudicationError("replay timeout is outside 1..180 seconds")
    if expected != 0:
        raise AdjudicationError("independent replay must expect exit status zero")
    if any("\x00" in arg or len(arg) > 4096 for arg in argv[2:]):
        raise AdjudicationError("replay argument is invalid")
    return {
        "argv": ["python3", "/artifacts/" + script_path.as_posix(), *argv[2:]],
        "timeout_seconds": timeout,
        "expected_exit": expected,
    }


def normalize_replay(result: dict, inventory: list[dict]) -> list[dict]:
    steps = result.get("replay", [])
    if not isinstance(steps, list):
        raise AdjudicationError("replay must be an array")
    if len(steps) > MAX_REPLAY_STEPS:
        raise AdjudicationError("too many replay steps")
    return [_normalized_replay_step(step, inventory) for step in steps]


def replay_sandbox_command(
    image_id: str,
    artifacts_root: Path,
    task_packet: Path,
    step: dict,
) -> list[str]:
    argv = step["argv"]
    return [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "64",
        "--memory",
        "512m",
        "--cpus",
        "1",
        "--user",
        f"{os.getuid()}:{os.getgid()}",
        "--tmpfs",
        "/tmp:rw,nosuid,nodev,size=128m",
        "--mount",
        f"type=bind,src={artifacts_root.resolve()},dst=/artifacts,readonly",
        "--mount",
        f"type=bind,src={task_packet.resolve()},dst=/task/task.json,readonly",
        "--workdir",
        "/tmp",
        "--entrypoint",
        "/usr/local/bin/python3",
        image_id,
        argv[1],
        *argv[2:],
    ]


def run_replays(
    image_id: str,
    artifacts_root: Path,
    task_packet: Path,
    steps: list[dict],
) -> list[dict]:
    rows = []
    for index, step in enumerate(steps):
        command = replay_sandbox_command(image_id, artifacts_root, task_packet, step)
        timed_out = False
        try:
            proc = subprocess.run(
                command,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=step["timeout_seconds"],
            )
            output = proc.stdout
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            output = str(exc.stdout or "")
            proc = subprocess.CompletedProcess(command, 124, output)
        rows.append(
            {
                "index": index,
                "argv": step["argv"],
                "timeout_seconds": step["timeout_seconds"],
                "returncode": proc.returncode,
                "timed_out": timed_out,
                "output_sha256": sha256_bytes(output.encode()),
                "output_tail": output[-1000:],
                "ok": bool(not timed_out and proc.returncode == step["expected_exit"]),
            }
        )
    return rows


def _required_result_errors(result: dict) -> list[str]:
    errors = []
    if result.get("schema") not in {
        "p42-foundry-candidate-result-v1",
        "p42-foundry-candidate-result-v2",
    }:
        errors.append("unsupported candidate result schema")
    if result.get("classification") not in {"progress", "negative_result", "blocked"}:
        errors.append("invalid candidate classification")
    for key in ("hypothesis", "falsifier", "claim"):
        if not isinstance(result.get(key), str) or not result[key].strip():
            errors.append(f"missing {key}")
    if not isinstance(result.get("evidence"), list):
        errors.append("evidence must be an array")
    if result.get("theorem_status") not in ALLOWED_THEOREM_STATUS:
        errors.append("theorem_status is not a bounded epistemic class")
    return errors


def validate_canonical_verdict(
    path: Path, task_sha: str, result_sha: str
) -> tuple[dict | None, list[str]]:
    """Validate a verdict emitted outside the candidate/replay sandboxes."""
    errors = []
    try:
        verdict = load(path)
        private_mode = (
            path.stat().st_mode & 0o777 == 0o600
            and path.stat().st_uid == os.getuid()
            and CANONICAL_VERDICT_ROOT.stat().st_mode & 0o777 == 0o700
            and _inside(path, CANONICAL_VERDICT_ROOT)
        )
    except (OSError, ValueError, AdjudicationError) as exc:
        return None, ["canonical verdict unreadable: " + str(exc)]
    if verdict.get("schema") != "p42-foundry-canonical-verdict-v1":
        errors.append("canonical verdict schema mismatch")
    if verdict.get("task_packet_sha256") != task_sha:
        errors.append("canonical verdict task binding mismatch")
    if verdict.get("candidate_result_sha256") != result_sha:
        errors.append("canonical verdict result binding mismatch")
    if verdict.get("verdict") != "accepted":
        errors.append("canonical verifier did not accept the artifact")
    if verdict.get("utility_units") not in {1, 2, 4, 8}:
        errors.append("canonical verdict utility is outside the frozen rubric")
    if verdict.get("independent_from_candidate") is not True:
        errors.append("canonical verifier independence flag is absent")
    if verdict.get("hard_constraints_ok") is not True:
        errors.append("canonical verifier reports a hard-constraint failure")
    for key in ("verifier_source_sha256", "evidence_sha256"):
        if not str(verdict.get(key, "")).startswith("sha256:"):
            errors.append(f"canonical verdict lacks {key}")
    if not verdict.get("verifier_id") or not verdict.get("verifier_revision"):
        errors.append("canonical verifier identity/revision is absent")
    source = CANONICAL_VERIFIER_SOURCES.get(str(verdict.get("verifier_id")))
    if not source or not source.is_file():
        errors.append("canonical verifier is absent from the trusted registry")
    elif verdict.get("verifier_source_sha256") != sha256_file(source):
        errors.append("canonical verifier source digest mismatch")
    if verdict.get("verifier_revision") != _git_revision() or not _git_tree_clean():
        errors.append("canonical verifier revision is not the clean evaluator revision")
    if not private_mode:
        errors.append("canonical verdict is not private mode 0600")
    if errors:
        return None, errors
    return {
        "schema": verdict["schema"],
        "verdict": verdict["verdict"],
        "utility_units": verdict["utility_units"],
        "verifier_id": verdict["verifier_id"],
        "verifier_revision": verdict["verifier_revision"],
        "verifier_source_sha256": verdict["verifier_source_sha256"],
        "evidence_sha256": verdict["evidence_sha256"],
        "independent_from_candidate": True,
        "hard_constraints_ok": True,
        "verdict_sha256": sha256_file(path),
    }, []


def adjudicate(
    candidate_output: Path,
    task_packet: Path,
    candidate_run_report: Path,
    image: str,
    scope: str,
    canonical_verdict_path: Path | None = None,
    run_replay: bool = True,
) -> dict:
    """Replay one candidate output; only a canonical verdict may award utility."""
    result_path = candidate_output / "result.json"
    if not result_path.is_file():
        raise AdjudicationError("candidate result.json is absent")
    result, packet, run_report = load(result_path), load(task_packet), load(candidate_run_report)
    if packet.get("schema") != "p42-foundry-eval-task-v1":
        raise AdjudicationError("adjudicator requires one frozen task packet")
    errors = _required_result_errors(result)
    hard_violations: list[str] = semantic_contract_violations(result, packet)
    evaluator_revision = _git_revision()
    evaluator_tree_clean = _git_tree_clean()
    if not evaluator_revision or not evaluator_tree_clean:
        hard_violations.append("evaluator_revision_not_clean")
    if result.get("schema") != "p42-foundry-candidate-result-v2":
        errors.append("legacy candidate result is not task/content bound")
    if result.get("theorem_status") not in ALLOWED_THEOREM_STATUS:
        hard_violations.append("semantic_contract_violation")
    if run_report.get("schema") != "p42-foundry-model-transport-v1":
        errors.append("candidate run report schema mismatch")
    if not run_report.get("ok") or run_report.get("mode") != "candidate_run":
        errors.append("candidate run did not complete under the model membrane")
    if not (run_report.get("budget") or {}).get("budget_ok"):
        hard_violations.append("fixed_budget_not_held")
    expected_result_sha = sha256_file(result_path)
    if run_report.get("artifact_sha256") != expected_result_sha:
        hard_violations.append("candidate_result_hash_mismatch")
    task_sha = sha256_bytes(canonical_bytes(packet))
    if result.get("schema") == "p42-foundry-candidate-result-v2":
        if result.get("task_packet_sha256") != task_sha:
            hard_violations.append("candidate_task_binding_mismatch")
        if result.get("evaluation_id") != packet.get("evaluation_id"):
            hard_violations.append("candidate_evaluation_binding_mismatch")
        if result.get("seed") != packet.get("seed"):
            hard_violations.append("candidate_seed_binding_mismatch")
    try:
        inventory = artifact_inventory(candidate_output / "artifacts")
        claimed_paths = _claimed_artifact_paths(result)
        inventory_paths = {row["path"] for row in inventory}
        if claimed_paths != inventory_paths:
            errors.append("artifact claims do not exactly match content-addressed files")
        if result.get("schema") == "p42-foundry-candidate-result-v2":
            if result.get("artifacts") != inventory:
                hard_violations.append("candidate_artifact_digest_mismatch")
        steps = normalize_replay(result, inventory)
    except AdjudicationError as exc:
        inventory, steps = [], []
        errors.append(str(exc))
    if bool(inventory) != bool(steps):
        errors.append("replay must cover a non-empty artifact set")
    image_id = resolve_image_id(image) if run_replay and steps and not errors else None
    replay_rows = (
        run_replays(image_id, candidate_output / "artifacts", task_packet, steps)
        if image_id
        else []
    )
    replay_ok = bool(replay_rows and all(row["ok"] for row in replay_rows))
    canonical_verifier = None
    if canonical_verdict_path and not errors and not hard_violations and replay_ok:
        if _inside(canonical_verdict_path, candidate_output):
            errors.append("canonical verdict cannot originate in candidate output")
        else:
            canonical_verifier, canonical_errors = validate_canonical_verdict(
                canonical_verdict_path, task_sha, expected_result_sha
            )
            errors.extend(canonical_errors)
    utility = int(canonical_verifier["utility_units"]) if canonical_verifier else 0
    report = {
        "schema": "p42-foundry-independent-replay-v1",
        "created_at": iso_now(),
        "scope": scope,
        "evaluation_id": packet.get("evaluation_id"),
        "seed": packet.get("seed"),
        "task_packet_sha256": task_sha,
        "candidate_result_sha256": expected_result_sha,
        "candidate_run_report_sha256": sha256_file(candidate_run_report),
        "evaluator_revision": evaluator_revision,
        "evaluator_tree_clean": evaluator_tree_clean,
        "image": image,
        "image_id": image_id,
        "replay_boundary": {
            "candidate_network": "none",
            "root_filesystem": "read_only",
            "artifacts": "read_only_content_addressed",
            "task_packet": "read_only",
            "candidate_workspace_mounted": False,
            "model_transport_mounted": False,
            "private_manifest_mounted": False,
            "docker_socket_mounted": False,
        },
        "artifact_inventory": inventory,
        "replays": replay_rows,
        "structural_errors": errors,
        "hard_constraint_violations": hard_violations,
        "artifact_replay_ok": replay_ok,
        "canonical_math_verdict": (
            "accepted_by_evaluator_owned_verifier"
            if canonical_verifier
            else "pending_evaluator_owned_verifier"
        ),
        "canonical_verifier": canonical_verifier,
        "fixed_budget": {
            "model": (packet.get("budget") or {}).get("model"),
            "limits": (run_report.get("budget") or {}).get("limits"),
            "budget_ok": bool((run_report.get("budget") or {}).get("budget_ok")),
        },
        "verified_utility_units": utility,
        "utility_rationale": (
            "evaluator-owned canonical verdict accepted the independently replayed artifact"
            if canonical_verifier
            else "candidate-authored replay is reproducibility evidence only; canonical verifier required"
        ),
        "promotion_authority": "none_human_review_required",
        "ok": bool(not errors and not hard_violations and replay_ok),
    }
    report["adjudication_id"] = sha256_bytes(canonical_bytes(report))
    return report


def _git_revision() -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def _git_tree_clean() -> bool:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return bool(proc.returncode == 0 and not proc.stdout.strip())


def _report_key(report: dict) -> tuple[str, str, int]:
    return (
        str(report.get("scope")),
        str(report.get("evaluation_id")),
        int(report.get("seed")),
    )


def _index_reports(reports: list[dict], label: str) -> dict[tuple[str, str, int], dict]:
    indexed = {}
    for report in reports:
        if report.get("schema") != "p42-foundry-independent-replay-v1":
            raise AdjudicationError(f"{label} contains a non-adjudication report")
        if int(report.get("verified_utility_units", 0)) > 0:
            canonical = report.get("canonical_verifier") or {}
            if not (
                canonical.get("verdict") == "accepted"
                and canonical.get("independent_from_candidate") is True
                and canonical.get("hard_constraints_ok") is True
            ):
                raise AdjudicationError(
                    f"{label} contains utility without an independent canonical verdict"
                )
        key = _report_key(report)
        if key in indexed:
            raise AdjudicationError(f"duplicate {label} paired key")
        indexed[key] = report
    return indexed


def bootstrap_lower_bound(
    deltas: list[int], confidence: float = 0.95, iterations: int = 10_000, seed: int = 42
) -> float | None:
    if not deltas:
        return None
    rng = random.Random(seed)
    means = []
    size = len(deltas)
    for _ in range(iterations):
        means.append(sum(deltas[rng.randrange(size)] for _ in range(size)) / size)
    means.sort()
    alpha = (1.0 - confidence) / 2.0
    return means[max(0, min(iterations - 1, int(alpha * iterations)))]


def compare_paired(
    baseline_reports: list[dict],
    candidate_reports: list[dict],
    protocol: dict,
    baseline_id: str,
    candidate_id: str,
) -> dict:
    baseline = _index_reports(baseline_reports, "baseline")
    candidate = _index_reports(candidate_reports, "candidate")
    if set(baseline) != set(candidate):
        raise AdjudicationError("paired report matrices are incomplete or mismatched")
    pairs = []
    for key in sorted(baseline):
        left, right = baseline[key], candidate[key]
        if left.get("task_packet_sha256") != right.get("task_packet_sha256"):
            raise AdjudicationError("paired task packet hashes differ")
        if left.get("fixed_budget") != right.get("fixed_budget"):
            raise AdjudicationError("paired fixed model/budget evidence differs")
        pairs.append(
            {
                "scope": key[0],
                "evaluation_id": key[1],
                "seed": key[2],
                "task_packet_sha256": left.get("task_packet_sha256"),
                "baseline_utility": int(left.get("verified_utility_units", 0)),
                "candidate_utility": int(right.get("verified_utility_units", 0)),
                "delta": int(right.get("verified_utility_units", 0))
                - int(left.get("verified_utility_units", 0)),
                "baseline_hard_constraints_ok": not bool(
                    left.get("hard_constraint_violations")
                ),
                "candidate_hard_constraints_ok": not bool(
                    right.get("hard_constraint_violations")
                ),
                "baseline_replay_operational": bool(
                    left.get("ok") is True and left.get("artifact_replay_ok") is True
                ),
                "candidate_replay_operational": bool(
                    right.get("ok") is True and right.get("artifact_replay_ok") is True
                ),
            }
        )
    private = [row for row in pairs if row["scope"] == "private"]
    public = [row for row in pairs if row["scope"] == "public"]
    deltas = [row["delta"] for row in private]
    confidence = float(protocol["promotion_gate"]["bootstrap_confidence"])
    lower = bootstrap_lower_bound(deltas, confidence=confidence)
    wins = sum(row["delta"] > 0 for row in private)
    public_regression = any(row["delta"] < 0 for row in public)
    hard_constraints_ok = all(row["candidate_hard_constraints_ok"] for row in pairs)
    all_replays_operational = all(
        row["baseline_replay_operational"] and row["candidate_replay_operational"]
        for row in pairs
    )
    gate = protocol["promotion_gate"]
    promotion_eligible = bool(
        len(private) >= int(gate["minimum_paired_holdout_runs"])
        and wins >= int(gate["minimum_holdout_wins"])
        and lower is not None
        and lower > float(gate["required_lower_bound_on_mean_utility_delta"])
        and not public_regression
        and hard_constraints_ok
        and all_replays_operational
    )
    report = {
        "schema": "p42-foundry-paired-evaluation-v1",
        "created_at": iso_now(),
        "protocol_version": protocol.get("protocol_version"),
        "baseline_id": baseline_id,
        "candidate_id": candidate_id,
        "paired_runs": len(pairs),
        "private_paired_runs": len(private),
        "public_paired_runs": len(public),
        "private_wins": wins,
        "private_losses": sum(row["delta"] < 0 for row in private),
        "private_ties": sum(row["delta"] == 0 for row in private),
        "private_mean_utility_delta": (
            sum(deltas) / len(deltas) if deltas else None
        ),
        "bootstrap_confidence": confidence,
        "bootstrap_lower_bound": lower,
        "fixed_budget_evidence_matched": True,
        "public_regression": public_regression,
        "hard_constraints_ok": hard_constraints_ok,
        "all_replays_operational": all_replays_operational,
        "pairs": pairs,
        "promotion_eligible": promotion_eligible,
        "claim_status": (
            "promotion_candidate_human_review_required"
            if promotion_eligible
            else "development_evidence_only"
        ),
        "automatic_production_promotion": False,
        "promotion_authority": "none_human_review_required",
    }
    report["comparison_id"] = sha256_bytes(canonical_bytes(report))
    return report


def replay_contract_smoke(task_packet: Path, image: str) -> dict:
    packet = load(task_packet)
    with tempfile.TemporaryDirectory(prefix="foundry-replay-smoke-") as tmp:
        root = Path(tmp)
        output = root / "candidate"
        artifacts = output / "artifacts"
        artifacts.mkdir(parents=True)
        script = artifacts / "probe.py"
        script.write_text(
            "import json\n"
            "from pathlib import Path\n"
            "task=json.loads(Path('/task/task.json').read_text())\n"
            "assert task['schema']=='p42-foundry-eval-task-v1'\n"
            "print('FOUNDRY_REPLAY_OK')\n"
        )
        inventory = artifact_inventory(artifacts)
        result = {
            "schema": "p42-foundry-candidate-result-v2",
            "evaluation_id": packet.get("evaluation_id"),
            "seed": packet.get("seed"),
            "task_packet_sha256": sha256_bytes(canonical_bytes(packet)),
            "classification": "progress",
            "hypothesis": "fresh replay container can read only the task and artifact",
            "falsifier": "nonzero replay exit or missing smoke token",
            "claim": "independent replay boundary smoke only",
            "evidence": ["probe exits zero after checking the task schema"],
            "artifacts": inventory,
            "artifacts_claimed": ["probe.py"],
            "replay": [
                {
                    "argv": ["python3", "artifacts/probe.py"],
                    "timeout_seconds": 30,
                    "expected_exit": 0,
                }
            ],
            "theorem_status": "theorem_unchanged",
            "independent_replay_status": "pending",
        }
        result_path = output / "result.json"
        result_path.write_text(json.dumps(result, indent=2) + "\n")
        run_report = {
            "schema": "p42-foundry-model-transport-v1",
            "ok": True,
            "mode": "candidate_run",
            "budget": {"budget_ok": True, "limits": packet.get("budget")},
            "artifact_sha256": sha256_file(result_path),
        }
        run_path = root / "candidate-run.json"
        run_path.write_text(json.dumps(run_report, indent=2) + "\n")
        report = adjudicate(output, task_packet, run_path, image, "contract_smoke")
        report["mode"] = "synthetic_boundary_smoke_no_rsi_claim"
        report["promotion_authority"] = "none_smoke_only"
        report["ok"] = bool(
            report["ok"]
            and report["verified_utility_units"] == 0
            and report["artifact_replay_ok"] is True
            and "FOUNDRY_REPLAY_OK" in report["replays"][0]["output_tail"]
        )
        report["adjudication_id"] = sha256_bytes(
            canonical_bytes({key: value for key, value in report.items() if key != "adjudication_id"})
        )
        return report


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    replay = sub.add_parser("replay")
    replay.add_argument("--candidate-output", type=Path, required=True)
    replay.add_argument("--task-packet", type=Path, required=True)
    replay.add_argument("--candidate-run-report", type=Path, required=True)
    replay.add_argument("--scope", choices=("public", "private"), required=True)
    replay.add_argument("--image", default=DEFAULT_EVAL_IMAGE)
    replay.add_argument("--canonical-verdict", type=Path)
    replay.add_argument("--output", type=Path, required=True)

    compare = sub.add_parser("compare")
    compare.add_argument("--baseline-report", action="append", type=Path, required=True)
    compare.add_argument("--candidate-report", action="append", type=Path, required=True)
    compare.add_argument("--baseline-id", required=True)
    compare.add_argument("--candidate-id", required=True)
    compare.add_argument("--output", type=Path, required=True)

    smoke = sub.add_parser("smoke")
    smoke.add_argument("--task-packet", type=Path, required=True)
    smoke.add_argument("--image", default=DEFAULT_EVAL_IMAGE)
    smoke.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    try:
        if args.command == "replay":
            report = adjudicate(
                args.candidate_output,
                args.task_packet,
                args.candidate_run_report,
                args.image,
                args.scope,
                args.canonical_verdict,
            )
        elif args.command == "compare":
            report = compare_paired(
                [load(path) for path in args.baseline_report],
                [load(path) for path in args.candidate_report],
                load(PROTOCOL),
                args.baseline_id,
                args.candidate_id,
            )
        else:
            report = replay_contract_smoke(args.task_packet, args.image)
    except AdjudicationError as exc:
        raise SystemExit(str(exc)) from exc
    atomic_json(args.output, report, 0o600)
    print(json.dumps(report, indent=2))
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())

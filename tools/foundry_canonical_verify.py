#!/usr/bin/env python3
"""Evaluator-owned canonical verifiers for replay-ready Foundry frontiers.

Only simple, exact witness classes live here.  Candidate code is never
imported or executed.  A successful run emits a private, hash-bound verdict
that ``foundry_adjudicate.py`` can consume after independent artifact replay.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from functools import lru_cache
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "foundry" / "eval" / "canonical_contracts.json"
VERIFIER_ID_BY_PROBLEM = {
    1: "erdos-1-distinct-subset-sums-v1",
    21: "erdos-21-q6-v1",
    138: "erdos-138-van-der-waerden-v1",
    552: "erdos-552-c4-star-v1",
}
DISTINCT_SUBSET_SUMS_FROZEN_UPPER = 594
Q6_FROZEN_UPPER = 18
VAN_DER_WAERDEN_FROZEN_WITNESS_LENGTH = {
    7: 3702,
    8: 11494,
    9: 41264,
    10: 103473,
}


class CanonicalVerificationError(ValueError):
    """The candidate artifact does not establish the registered claim."""


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise CanonicalVerificationError(f"expected JSON object: {path}")
    return value


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.chmod(0o600)
    tmp.replace(path)


def git_revision() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    revision = proc.stdout.strip()
    if proc.returncode or not revision:
        raise CanonicalVerificationError("canonical verifier revision is unavailable")
    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if dirty.returncode or dirty.stdout.strip():
        raise CanonicalVerificationError("canonical verifier revision is not clean")
    return revision


def verify_distinct_subset_sums(document: dict) -> dict:
    values = document.get("set")
    if not isinstance(values, list) or len(values) != 11:
        raise CanonicalVerificationError("witness must contain exactly 11 elements")
    if any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in values):
        raise CanonicalVerificationError("witness elements must be positive integers")
    if values != sorted(set(values)):
        raise CanonicalVerificationError("witness must be strictly increasing")
    sums = {0}
    for value in values:
        shifted = {old + value for old in sums}
        if sums & shifted:
            raise CanonicalVerificationError("two subsets have the same sum")
        sums |= shifted
    if len(sums) != 2048:
        raise CanonicalVerificationError("not all 2048 subset sums are distinct")
    if values[-1] >= DISTINCT_SUBSET_SUMS_FROZEN_UPPER:
        raise CanonicalVerificationError("valid witness does not improve the frozen upper bound")
    return {
        "problem_id": 1,
        "witness_size": 11,
        "subset_sums": len(sums),
        "largest_element": values[-1],
        "strict_upper_bound_improvement": True,
    }


def _has_hitting_set(edges: tuple[frozenset[int], ...], budget: int) -> bool:
    @lru_cache(maxsize=None)
    def search(remaining: tuple[frozenset[int], ...], left: int) -> bool:
        if not remaining:
            return True
        if left == 0:
            return False
        pivot = min(remaining, key=len)
        for vertex in sorted(pivot):
            next_edges = tuple(edge for edge in remaining if vertex not in edge)
            if search(next_edges, left - 1):
                return True
        return False

    return search(edges, budget)


def verify_q6(document: dict) -> dict:
    raw_edges = document.get("edges")
    if not isinstance(raw_edges, list) or not raw_edges:
        raise CanonicalVerificationError("edges must be a non-empty array")
    if len(raw_edges) >= Q6_FROZEN_UPPER:
        raise CanonicalVerificationError("valid witness does not improve the frozen edge bound")
    edges = []
    for index, raw in enumerate(raw_edges):
        if not isinstance(raw, list) or len(raw) != 6:
            raise CanonicalVerificationError(f"edge {index} is not six-uniform")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in raw):
            raise CanonicalVerificationError(f"edge {index} has an invalid vertex")
        edge = frozenset(raw)
        if len(edge) != 6:
            raise CanonicalVerificationError(f"edge {index} repeats a vertex")
        edges.append(edge)
    if len(set(edges)) != len(edges):
        raise CanonicalVerificationError("duplicate hyperedge")
    for left, right in combinations(edges, 2):
        if left.isdisjoint(right):
            raise CanonicalVerificationError("hypergraph is not pairwise intersecting")
    frozen = tuple(sorted(edges, key=lambda edge: tuple(sorted(edge))))
    if _has_hitting_set(frozen, 5):
        raise CanonicalVerificationError("hypergraph admits a hitting set of size at most five")
    vertices = set().union(*edges)
    return {
        "problem_id": 21,
        "edges": len(edges),
        "vertices": len(vertices),
        "pairwise_intersecting": True,
        "cover_number": 6,
        "strict_upper_bound_improvement": True,
    }


def verify_van_der_waerden(document: dict) -> dict:
    k, coloring = document.get("k"), document.get("coloring")
    if k not in VAN_DER_WAERDEN_FROZEN_WITNESS_LENGTH:
        raise CanonicalVerificationError("k is outside the registered frontier cells")
    if not isinstance(coloring, list) or not coloring:
        raise CanonicalVerificationError("coloring must be a non-empty array")
    if len(coloring) > 200_000 or any(
        isinstance(value, bool) or value not in {0, 1} for value in coloring
    ):
        raise CanonicalVerificationError("coloring must be a bounded zero/one array")
    length = len(coloring)
    if length <= VAN_DER_WAERDEN_FROZEN_WITNESS_LENGTH[k]:
        raise CanonicalVerificationError("valid coloring would not improve the frozen lower bound")
    bits = [0, 0]
    for index, color in enumerate(coloring):
        bits[color] |= 1 << index
    for difference in range(1, (length - 1) // (k - 1) + 1):
        for color_bits in bits:
            starts = color_bits
            for offset in range(1, k):
                starts &= color_bits >> (offset * difference)
                if not starts:
                    break
            if starts:
                raise CanonicalVerificationError("coloring contains a monochromatic progression")
    return {
        "problem_id": 138,
        "k": k,
        "length": length,
        "certified_lower_bound": length + 1,
        "strict_lower_bound_improvement": True,
    }


def _load_erdos_552_verifier():
    path = ROOT / "certificates" / "erdos-552" / "verify.py"
    spec = importlib.util.spec_from_file_location("foundry_erdos_552_verifier", path)
    if not spec or not spec.loader:
        raise CanonicalVerificationError("trusted Erdős 552 verifier is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_c4_star(document: dict) -> dict:
    if document.get("n") != 17 or document.get("vertices") != 22:
        raise CanonicalVerificationError("registered frontier requires n=17 on 22 vertices")
    verifier = _load_erdos_552_verifier()
    result = verifier.verify_witness(document, expected_vertices=22, exact=True)
    if result.get("value") != 23 or result.get("status") != "EXACT":
        raise CanonicalVerificationError("witness did not close the 22..23 bracket")
    return {
        "problem_id": 552,
        **result,
        "strict_frontier_closure": True,
    }


VERIFY = {
    1: verify_distinct_subset_sums,
    21: verify_q6,
    138: verify_van_der_waerden,
    552: verify_c4_star,
}


def verify_candidate(candidate_output: Path, task_packet: Path) -> dict:
    packet = load(task_packet)
    result_path = candidate_output / "result.json"
    result = load(result_path)
    if packet.get("schema") != "p42-foundry-eval-task-v1":
        raise CanonicalVerificationError("canonical verifier requires one task packet")
    if result.get("schema") != "p42-foundry-candidate-result-v2":
        raise CanonicalVerificationError("canonical verifier requires a v2 bound result")
    task_sha = sha256_bytes(canonical_bytes(packet))
    result_sha = sha256_file(result_path)
    if result.get("task_packet_sha256") != task_sha:
        raise CanonicalVerificationError("candidate task binding mismatch")
    if result.get("evaluation_id") != packet.get("evaluation_id"):
        raise CanonicalVerificationError("candidate evaluation binding mismatch")
    if result.get("seed") != packet.get("seed"):
        raise CanonicalVerificationError("candidate seed binding mismatch")
    target = packet.get("target") or {}
    problem_id = target.get("id")
    if problem_id not in VERIFY:
        raise CanonicalVerificationError("task has no registered canonical verifier")
    contracts = load(CONTRACTS).get("contracts", {})
    contract = packet.get("canonical_artifact_contract")
    expected = contracts.get(str(problem_id))
    if contract != expected:
        raise CanonicalVerificationError("task canonical contract is absent or modified")
    if contract.get("verifier_id") != VERIFIER_ID_BY_PROBLEM[problem_id]:
        raise CanonicalVerificationError("canonical verifier identity mismatch")
    artifact_path = candidate_output / "artifacts" / contract["artifact_path"]
    if artifact_path.is_symlink() or not artifact_path.is_file():
        raise CanonicalVerificationError("canonical witness artifact is absent or unsafe")
    descriptor = next(
        (
            row for row in result.get("artifacts", [])
            if isinstance(row, dict) and row.get("path") == contract["artifact_path"]
        ),
        None,
    )
    if not descriptor or descriptor.get("sha256") != sha256_file(artifact_path):
        raise CanonicalVerificationError("canonical witness content address mismatch")
    document = load(artifact_path)
    evidence = VERIFY[problem_id](document)
    return {
        "task_packet_sha256": task_sha,
        "candidate_result_sha256": result_sha,
        "verifier_id": contract["verifier_id"],
        "evidence": evidence,
        "utility_units": 8,
    }


def build_verdict(verified: dict, revision: str) -> dict:
    evidence_sha = sha256_bytes(canonical_bytes(verified["evidence"]))
    return {
        "schema": "p42-foundry-canonical-verdict-v1",
        "task_packet_sha256": verified["task_packet_sha256"],
        "candidate_result_sha256": verified["candidate_result_sha256"],
        "verdict": "accepted",
        "utility_units": verified["utility_units"],
        "independent_from_candidate": True,
        "hard_constraints_ok": True,
        "verifier_id": verified["verifier_id"],
        "verifier_revision": revision,
        "verifier_source_sha256": sha256_file(Path(__file__)),
        "evidence_sha256": evidence_sha,
        "evidence": verified["evidence"],
        "promotion_authority": "none_input_to_independent_adjudicator",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-output", type=Path, required=True)
    parser.add_argument("--task-packet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        verdict = build_verdict(
            verify_candidate(args.candidate_output, args.task_packet), git_revision()
        )
    except (OSError, ValueError, CanonicalVerificationError) as exc:
        raise SystemExit(str(exc)) from exc
    atomic_json(args.output, verdict)
    print(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

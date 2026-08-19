#!/usr/bin/env python3
"""Pure-stdlib hostile replay for the q=6, 117-cell deletion-wall CEGAR.

This script deliberately does not import the producer's module.  It rebuilds
the 117 cells, evaluates the continuous closure rows with Fraction arithmetic,
checks every claimed Farkas ray, and can make/check an exhaustive hypergraph
proof that the ray supports have no transversal of cardinality at most six.

The hypergraph proof is a hash-consed branching certificate.  A leaf contains
a pairwise-disjoint packing of still-unhit ray supports.  Such a packing is a
direct lower bound on the number of additional deleted cells required.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path


Q = 6
S0 = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
      (5, 0), (5, 1), (5, 2))
D = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
     (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
EXPECTED_CELL_COUNT = 117
EXPECTED_LEDGER_COUNT = 98167
TERMINAL_VERDICT = "EXACT_NO_HITTING_SET_WITH_AT_MOST_SIX_DELETIONS"


class VerificationError(ValueError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def bundle() -> tuple[tuple[int, int, int, int], ...]:
    cells = tuple((a, b, (a + da) % Q, (b + db) % Q)
                  for a, b in S0 for da, db in D)
    if len(cells) != EXPECTED_CELL_COUNT or len(set(cells)) != len(cells):
        fail("the independently reconstructed bundle is not 117 distinct cells")
    return cells


U = bundle()


def coordinate_requirement(a: int, b: int, c: int) -> Fraction | None:
    """Closure supremum for one coordinate, evaluated from its three cases.

    The scaled row condition is q*carry-(a+c-2b) in {-1,0,1}.  For each
    allowed carry, the offset interval is closed at exactly the endpoint that
    maximizes -2*q*carry*(...).  We enumerate all carries, so this is both an
    exact implementation of the continuous semantics and avoids LP arithmetic.
    """
    defect = a + c - 2 * b
    candidates: list[Fraction] = []
    for carry in (-1, 0, 1):
        ell = Q * carry - defect
        if ell not in (-1, 0, 1):
            continue
        # closure of the valid offset cell: ell=-1 has [1/2,1], ell=0
        # has [0,1], and ell=1 has [0,1/2].
        low = {-1: Fraction(1, 2), 0: Fraction(0), 1: Fraction(0)}[ell]
        high = {-1: Fraction(1), 0: Fraction(1), 1: Fraction(1, 2)}[ell]
        t = low if carry > 0 else high
        candidates.append(-2 * Q * carry * (
            Fraction(a + c, 2) + b + 2 * t + Fraction(ell, 2)))
    return max(candidates) if candidates else None


# There are only 6^3 digit triples.  Materializing this independently computed
# exact table keeps the full 117^3 ledger audit inexpensive without relaxing
# any arithmetic to floats.
COORD_REQUIREMENTS = tuple(
    tuple(tuple(coordinate_requirement(a, b, c) for c in range(Q))
                for b in range(Q))
    for a in range(Q))


def row_rhs(x: int, y: int, z: int) -> int | None:
    values = [COORD_REQUIREMENTS[U[x][j]][U[y][j]][U[z][j]]
              for j in range(4)]
    if any(value is None for value in values):
        return None
    total = sum(values, Fraction(0))
    if total.denominator != 1:
        fail(f"nonintegral exact RHS for row {(x, y, z)}: {total}")
    return int(total)


def independently_count_legal_rows() -> int:
    return sum(row_rhs(x, y, z) is not None
               for x, y, z in product(range(len(U)), repeat=3))


def canonical_sha256(path: Path) -> str:
    # Proof certificates bind to the bytes that were replayed, not merely to
    # an informally similar checkpoint.
    return hashlib.sha256(path.read_bytes()).hexdigest()


def support_digest(supports: tuple[frozenset[int], ...]) -> str:
    canonical = json.dumps([sorted(edge) for edge in supports],
                           separators=(",", ":")).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def verify_exact_gate() -> Fraction:
    gate = Fraction(111, Q ** 4) - Fraction(7, 24) ** 2
    if gate != Fraction(1, 1728):
        fail(f"after-six density gate is {gate}, not 1/1728")
    return gate


def normalize_ray(record: dict, ray_index: int) -> tuple[tuple[int, int, int, int, int], ...]:
    rows = record.get("rows")
    if not isinstance(rows, list) or not rows:
        fail(f"ray {ray_index}: rows must be a nonempty list")
    answer = []
    for row_index, row in enumerate(rows):
        if (not isinstance(row, list)) or len(row) != 5 or any(
                not isinstance(v, int) or isinstance(v, bool) for v in row):
            fail(f"ray {ray_index}, row {row_index}: expected five integer fields")
        weight, x, y, z, rhs = row
        if weight <= 0:
            fail(f"ray {ray_index}, row {row_index}: nonpositive Farkas weight")
        if not all(0 <= index < len(U) for index in (x, y, z)):
            fail(f"ray {ray_index}, row {row_index}: cell index out of range")
        answer.append((weight, x, y, z, rhs))
    return tuple(answer)


def replay_ray(record: dict, ray_index: int) -> frozenset[int]:
    ray = normalize_ray(record, ray_index)
    incidence = [0] * len(U)
    weighted_rhs = 0
    support: set[int] = set()
    for row_index, (weight, x, y, z, rhs) in enumerate(ray):
        actual_rhs = row_rhs(x, y, z)
        if actual_rhs is None:
            fail(f"ray {ray_index}, row {row_index}: illegal continuous row")
        if rhs != actual_rhs:
            fail(f"ray {ray_index}, row {row_index}: RHS {rhs} != exact {actual_rhs}")
        incidence[x] += weight
        incidence[y] -= 2 * weight
        incidence[z] += weight
        weighted_rhs += weight * rhs
        support.update((x, y, z))
    bad = [(index, value) for index, value in enumerate(incidence) if value]
    if bad:
        fail(f"ray {ray_index}: nonzero potential incidence {bad[:6]}")
    if weighted_rhs <= 0:
        fail(f"ray {ray_index}: nonpositive weighted RHS {weighted_rhs}")
    listed_support = record.get("support")
    if listed_support != sorted(support):
        fail(f"ray {ray_index}: listed support disagrees with its rows")
    if record.get("weighted_rhs") != weighted_rhs:
        fail(f"ray {ray_index}: listed weighted RHS disagrees with its rows")
    deleted = record.get("deleted", [])
    if not isinstance(deleted, list) or any(not isinstance(v, int) for v in deleted):
        fail(f"ray {ray_index}: malformed deleted list")
    if set(deleted) & support:
        fail(f"ray {ray_index}: ray uses a cell that its discovery deletion removed")
    return frozenset(support)


def replay_checkpoint(payload: dict) -> tuple[frozenset[int], ...]:
    if payload.get("max_deletions") != 6:
        fail("checkpoint is not a six-deletion claim")
    rays = payload.get("rays")
    if not isinstance(rays, list) or not rays:
        fail("checkpoint has no rays")
    if payload.get("ray_count") != len(rays):
        fail("declared ray_count disagrees with rays list")
    supports = tuple(replay_ray(record, index) for index, record in enumerate(rays))
    if len(set(supports)) != len(supports):
        fail("duplicate supports make the source's newly-learned-cut invariant false")
    return supports


def remaining_edges(edges: tuple[frozenset[int], ...], chosen: frozenset[int]) -> list[int]:
    return [index for index, edge in enumerate(edges) if edge.isdisjoint(chosen)]


def pick_branch(edges: tuple[frozenset[int], ...], unhit: list[int]) -> int:
    return min(unhit, key=lambda index: (len(edges[index]), tuple(sorted(edges[index])), index))


def greedy_packing(edges: tuple[frozenset[int], ...], unhit: list[int], needed: int) -> list[int] | None:
    """Find a deterministic disjoint packing, stopping as soon as it suffices."""
    used: set[int] = set()
    packing: list[int] = []
    for index in sorted(unhit, key=lambda i: (len(edges[i]), tuple(sorted(edges[i])), i)):
        if edges[index].isdisjoint(used):
            packing.append(index)
            used.update(edges[index])
            if len(packing) >= needed:
                return packing
    return None


def find_transversal(edges: tuple[frozenset[int], ...], budget: int) -> tuple[int, ...] | None:
    """Exact bounded-depth witness search; used only to diagnose a non-wall."""
    failed: set[tuple[int, ...]] = set()

    def visit(chosen: frozenset[int]) -> tuple[int, ...] | None:
        key = tuple(sorted(chosen))
        if key in failed:
            return None
        unhit = remaining_edges(edges, chosen)
        if not unhit:
            return key
        if len(chosen) == budget:
            failed.add(key)
            return None
        edge_index = pick_branch(edges, unhit)
        for cell in sorted(edges[edge_index]):
            answer = visit(chosen | {cell})
            if answer is not None:
                return answer
        failed.add(key)
        return None

    return visit(frozenset())


def make_certificate(edges: tuple[frozenset[int], ...], budget: int) -> dict:
    """Build a complete, independently checkable no-transversal certificate.

    Nodes are keyed by the chosen-cell set.  The branch rule is exhaustive:
    every hitting set extending the chosen cells must choose a member of the
    selected unhit edge.  Packing leaves are elementary lower-bound proofs.
    """
    nodes: list[dict] = []
    by_state: dict[tuple[int, ...], int] = {}

    def visit(chosen: frozenset[int]) -> int | None:
        key = tuple(sorted(chosen))
        known = by_state.get(key)
        if known is not None:
            return known
        unhit = remaining_edges(edges, chosen)
        if not unhit:
            return None  # This is a genuine <=budget transversal.
        needed = budget - len(chosen) + 1
        packing = greedy_packing(edges, unhit, needed)
        node_id = len(nodes)
        by_state[key] = node_id
        if packing is not None:
            nodes.append({"kind": "packing", "chosen": list(key), "packing": packing})
            return node_id
        if len(chosen) == budget:
            # An unhit edge itself is a packing of size one, since needed=1.
            # Reaching here means an implementation error, not a normal leaf.
            fail("packing lower bound failed at the deletion budget")
        edge_index = pick_branch(edges, unhit)
        children: list[list[int]] = []
        nodes.append({})  # reserve before recursive calls for hash-consing
        for cell in sorted(edges[edge_index]):
            child = visit(chosen | {cell})
            if child is None:
                return None
            children.append([cell, child])
        nodes[node_id] = {"kind": "branch", "chosen": list(key),
                          "edge": edge_index, "children": children}
        return node_id

    root = visit(frozenset())
    if root is None:
        fail("the ray-support hypergraph HAS a hitting set of size at most budget")
    return {"schema": "terra-sixdelete-hypergraph-proof-v1", "budget": budget,
            "node_count": len(nodes), "root": root, "nodes": nodes}


def verify_certificate(cert: dict, edges: tuple[frozenset[int], ...], expected_sha: str) -> None:
    if cert.get("schema") != "terra-sixdelete-hypergraph-proof-v1":
        fail("unrecognized proof schema")
    if cert.get("source_sha256") != expected_sha:
        fail("certificate is not bound to these checkpoint bytes")
    if cert.get("ray_supports_sha256") != support_digest(edges):
        fail("certificate ray-support digest does not match the replayed rays")
    if cert.get("cells") != EXPECTED_CELL_COUNT or cert.get("legal_rows") != EXPECTED_LEDGER_COUNT:
        fail("certificate bundle/ledger metadata is not the exact q=6 model")
    if cert.get("after_six_gate") != "1/1728":
        fail("certificate does not state the exact after-six gate")
    if cert.get("source_verdict") != TERMINAL_VERDICT:
        fail("certificate is not marked as replayed from a terminal checkpoint")
    budget = cert.get("budget")
    if not isinstance(budget, int) or budget != 6:
        fail("certificate budget is not six")
    nodes = cert.get("nodes")
    if not isinstance(nodes, list) or cert.get("node_count") != len(nodes):
        fail("malformed node array")
    root = cert.get("root")
    if not isinstance(root, int) or not 0 <= root < len(nodes):
        fail("invalid root node")
    active: set[int] = set()
    checked: dict[int, tuple[int, ...]] = {}

    def check(node_id: int, expected: tuple[int, ...]) -> None:
        if node_id in checked:
            if checked[node_id] != expected:
                fail(f"node {node_id} reused with a different chosen set")
            return
        if node_id in active:
            fail("certificate graph has a cycle")
        if not 0 <= node_id < len(nodes):
            fail("child node out of range")
        node = nodes[node_id]
        if node.get("chosen") != list(expected):
            fail(f"node {node_id}: chosen set does not match its parent")
        if len(expected) > budget:
            fail(f"node {node_id}: exceeds budget")
        unhit = remaining_edges(edges, frozenset(expected))
        if not unhit:
            fail(f"node {node_id}: claims impossibility after already hitting every edge")
        active.add(node_id)
        if node.get("kind") == "packing":
            packing = node.get("packing")
            if not isinstance(packing, list) or not packing:
                fail(f"node {node_id}: malformed packing")
            used: set[int] = set()
            for edge_index in packing:
                if not isinstance(edge_index, int) or edge_index not in unhit:
                    fail(f"node {node_id}: packing uses a hit/nonexistent edge")
                if not edges[edge_index].isdisjoint(used):
                    fail(f"node {node_id}: packing edges are not disjoint")
                used.update(edges[edge_index])
            if len(expected) + len(packing) <= budget:
                fail(f"node {node_id}: packing does not exceed deletion budget")
        elif node.get("kind") == "branch":
            edge_index = node.get("edge")
            if edge_index != pick_branch(edges, unhit):
                fail(f"node {node_id}: noncanonical or invalid branch edge")
            children = node.get("children")
            want = sorted(edges[edge_index])
            if not isinstance(children, list) or [child[0] if isinstance(child, list) and len(child) == 2 else None for child in children] != want:
                fail(f"node {node_id}: children do not exhaust the branch edge")
            for cell, child_id in children:
                if not isinstance(child_id, int):
                    fail(f"node {node_id}: child id is not an integer")
                check(child_id, tuple(sorted((*expected, cell))))
        else:
            fail(f"node {node_id}: unknown kind")
        active.remove(node_id)
        checked[node_id] = expected

    check(root, ())
    if len(checked) != len(nodes):
        fail("certificate contains unreachable nodes")


def run_self_test() -> None:
    # A seven-singleton hypergraph needs seven deletions.  The generated tree
    # must prove that fact, while six singletons must be recognized as feasible.
    seven = tuple(frozenset({i}) for i in range(7))
    cert = make_certificate(seven, 6)
    cert["source_sha256"] = "self-test"
    cert["ray_supports_sha256"] = support_digest(seven)
    cert["cells"] = EXPECTED_CELL_COUNT
    cert["legal_rows"] = EXPECTED_LEDGER_COUNT
    cert["after_six_gate"] = "1/1728"
    cert["source_verdict"] = TERMINAL_VERDICT
    verify_certificate(cert, seven, "self-test")
    try:
        make_certificate(tuple(frozenset({i}) for i in range(6)), 6)
    except VerificationError:
        pass
    else:
        fail("self-test: feasible six-singleton instance was accepted as a wall")
    damaged = copy.deepcopy(cert)
    packing_node = next(i for i, node in enumerate(damaged["nodes"])
                        if node["kind"] == "packing")
    damaged["nodes"][packing_node]["packing"] = [0]
    try:
        verify_certificate(damaged, seven, "self-test")
    except VerificationError:
        pass
    else:
        fail("self-test: undersized planted packing was accepted")
    print("SELF_TEST_OK")


def run_checkpoint_negative_tests(payload: dict) -> None:
    """Make sure the ray replay rejects two realistic producer corruptions."""
    for label, mutate in (
        ("rhs", lambda row: row.__setitem__(4, row[4] + 1)),
        ("incidence", lambda row: row.__setitem__(0, row[0] + 1)),
    ):
        damaged = copy.deepcopy(payload)
        mutate(damaged["rays"][0]["rows"][0])
        try:
            replay_checkpoint(damaged)
        except VerificationError:
            continue
        fail(f"self-test: planted {label} corruption was accepted")
    print("PLANTED_RAY_FAILURES_REJECTED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path, help="root CEGAR checkpoint JSON")
    parser.add_argument("--certificate", type=Path, help="write no-hit certificate if a wall exists")
    parser.add_argument("--verify-certificate", type=Path, help="verify an existing certificate")
    parser.add_argument("--find-hit", action="store_true", help="report an exact <=6 transversal if one exists")
    parser.add_argument("--freeze-checkpoint", type=Path,
                        help="write the exact terminal checkpoint bytes beside the proof artifacts")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            run_self_test()
        # Read once: source hash and decoded evidence always refer to identical
        # bytes even while the live CEGAR writer is updating a later checkpoint.
        source_bytes = args.checkpoint.read_bytes()
        source_sha = hashlib.sha256(source_bytes).hexdigest()
        payload = json.loads(source_bytes.decode("utf-8"))
        supports = replay_checkpoint(payload)
        if args.self_test:
            run_checkpoint_negative_tests(payload)
        legal_rows = independently_count_legal_rows()
        if legal_rows != EXPECTED_LEDGER_COUNT:
            fail(f"legal continuous row count {legal_rows} != {EXPECTED_LEDGER_COUNT}")
        gate = verify_exact_gate()
        print(f"RAYS_OK rays={len(supports)} cells={len(U)} legal_rows={legal_rows}")
        print(f"GATE_OK after_six=111/1296-(7/24)^2={gate}")
        if args.find_hit:
            witness = find_transversal(supports, 6)
            print("HYPERGRAPH_HIT=" + (str(witness) if witness is not None else "NONE"))
        if args.verify_certificate:
            cert = json.loads(args.verify_certificate.read_text(encoding="utf-8"))
            verify_certificate(cert, supports, source_sha)
            print(f"HYPERGRAPH_PROOF_OK nodes={cert['node_count']} budget=6")
        if args.certificate:
            if payload.get("verdict") != TERMINAL_VERDICT:
                fail("refusing terminal artifact: source checkpoint verdict is not terminal")
            cert = make_certificate(supports, 6)
            cert["source_sha256"] = source_sha
            cert["ray_supports_sha256"] = support_digest(supports)
            cert["cells"] = len(U)
            cert["legal_rows"] = legal_rows
            cert["after_six_gate"] = str(gate)
            cert["source_verdict"] = payload["verdict"]
            cert["ray_count"] = len(supports)
            args.certificate.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
            if args.freeze_checkpoint:
                args.freeze_checkpoint.write_bytes(source_bytes)
                frozen_sha = hashlib.sha256(args.freeze_checkpoint.read_bytes()).hexdigest()
                if frozen_sha != source_sha:
                    fail("frozen checkpoint bytes did not retain the replayed hash")
                print(f"CHECKPOINT_FROZEN path={args.freeze_checkpoint} sha256={frozen_sha}")
            print(f"WALL_PROVED certificate={args.certificate} nodes={cert['node_count']} budget=6")
    except (OSError, json.JSONDecodeError, VerificationError) as error:
        print(f"VERIFY_FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

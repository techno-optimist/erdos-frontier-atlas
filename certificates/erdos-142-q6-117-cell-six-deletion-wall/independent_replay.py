#!/usr/bin/env python3
"""Independent, stdlib-only replay of the Erdos142 six-deletion wall.

This is a fresh implementation.  Cells are represented by one base-six
integer rather than coordinate tuples; the continuous closure table is built
from scaled integer endpoint values; and the terminal hypergraph is checked by
an independent bit-mask DFS in addition to checking the supplied proof DAG.
The two input JSON files are read-only evidence.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


ORDER = 6
CELL_TOTAL = 117
ROW_TOTAL = 98167
BUDGET = 6
VERDICT = "EXACT_NO_HITTING_SET_WITH_AT_MOST_SIX_DELETIONS"

# The nine seed pairs and thirteen allowed offset pairs define U_D.  The
# representation below is deliberately a packed base-six integer, not the
# producer's four-tuple cell representation.
SEEDS = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
         (5, 0), (5, 1), (5, 2))
OFFSETS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
           (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))


class ReplayError(ValueError):
    pass


def packed(a: int, b: int, c: int, d: int) -> int:
    return (((a * ORDER + b) * ORDER + c) * ORDER + d)


def unpack(code: int) -> tuple[int, int, int, int]:
    return ((code // (ORDER ** 3)) % ORDER,
            (code // (ORDER ** 2)) % ORDER,
            (code // ORDER) % ORDER,
            code % ORDER)


def build_integer_bundle() -> tuple[int, ...]:
    answer = tuple(packed(a, b, (a + da) % ORDER, (b + db) % ORDER)
                   for a, b in SEEDS for da, db in OFFSETS)
    if len(answer) != CELL_TOTAL or len(set(answer)) != CELL_TOTAL:
        raise ReplayError("integer U_D reconstruction is not 117 distinct cells")
    if any(unpack(v)[0:2] not in SEEDS for v in answer):
        raise ReplayError("packed cell has an invalid seed pair")
    return answer


CELLS = build_integer_bundle()
COORDS = tuple(unpack(v) for v in CELLS)


def closure_entry(a: int, b: int, c: int) -> int | None:
    """Return the exact coordinate closure contribution, or None.

    We enumerate the three possible carries.  All endpoint arithmetic is
    integer arithmetic after doubling the half-unit coordinates.  This is
    equivalent to evaluating the continuous cell closure, without borrowing
    the producer's Fraction/table code.
    """
    defect = a + c - 2 * b
    best: int | None = None
    for carry in (-1, 0, 1):
        residual = ORDER * carry - defect
        if residual not in (-1, 0, 1):
            continue
        # t endpoints in half-unit coordinates: r=-1 -> [1/2,1],
        # r=0 -> [0,1], r=1 -> [0,1/2].
        endpoints = { -1: (1, 2), 0: (0, 2), 1: (0, 1) }[residual]
        for t_half in endpoints:
            # -2Q*k*((a+c)/2+b+2t+r/2), with 2t=t_half.
            # The expression in parentheses is represented by its doubled
            # numerator, hence this is integral in the present model.
            doubled = a + c + 2 * b + 2 * t_half + residual
            candidate = -ORDER * carry * doubled
            best = candidate if best is None else max(best, candidate)
    return best


TABLE = tuple(tuple(tuple(closure_entry(a, b, c) for c in range(ORDER))
                   for b in range(ORDER)) for a in range(ORDER))


def row_value(x: int, y: int, z: int) -> int | None:
    xx, yy, zz = COORDS[x], COORDS[y], COORDS[z]
    total = 0
    for j in range(4):
        term = TABLE[xx[j]][yy[j]][zz[j]]
        if term is None:
            return None
        total += term
    return total


def count_rows() -> int:
    total = 0
    for x in range(CELL_TOTAL):
        for y in range(CELL_TOTAL):
            for z in range(CELL_TOTAL):
                total += row_value(x, y, z) is not None
    return total


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def support_hash(edges: tuple[frozenset[int], ...]) -> str:
    serial = json.dumps([sorted(edge) for edge in edges],
                        separators=(",", ":")).encode("ascii")
    return sha256_bytes(serial)


def replay_rays(doc: dict) -> tuple[frozenset[int], ...]:
    rays = doc.get("rays")
    if not isinstance(rays, list) or doc.get("ray_count") != len(rays):
        raise ReplayError("ray list/count mismatch")
    edges: list[frozenset[int]] = []
    for ri, ray in enumerate(rays):
        rows = ray.get("rows") if isinstance(ray, dict) else None
        if not isinstance(rows, list) or not rows:
            raise ReplayError(f"ray {ri}: missing rows")
        incidence = [0] * CELL_TOTAL
        actual_support: set[int] = set()
        weighted = 0
        for rj, rec in enumerate(rows):
            if (not isinstance(rec, list) or len(rec) != 5 or
                    any(type(v) is not int for v in rec)):
                raise ReplayError(f"ray {ri} row {rj}: not five plain integers")
            weight, x, y, z, claimed = rec
            if weight <= 0 or not all(0 <= q < CELL_TOTAL for q in (x, y, z)):
                raise ReplayError(f"ray {ri} row {rj}: invalid index/weight")
            exact = row_value(x, y, z)
            if exact is None or exact != claimed:
                raise ReplayError(f"ray {ri} row {rj}: closure RHS mismatch")
            incidence[x] += weight
            incidence[y] -= 2 * weight
            incidence[z] += weight
            weighted += weight * exact
            actual_support.update((x, y, z))
        if any(incidence):
            raise ReplayError(f"ray {ri}: nonzero integer potential incidence")
        if weighted <= 0:
            raise ReplayError(f"ray {ri}: nonpositive weighted RHS")
        if ray.get("support") != sorted(actual_support):
            raise ReplayError(f"ray {ri}: support mismatch")
        if ray.get("weighted_rhs") != weighted:
            raise ReplayError(f"ray {ri}: weighted RHS mismatch")
        deleted = ray.get("deleted")
        if (not isinstance(deleted, list) or any(type(v) is not int for v in deleted)
                or set(deleted) & actual_support):
            raise ReplayError(f"ray {ri}: deletion compatibility failure")
        edges.append(frozenset(actual_support))
    if len(set(edges)) != len(edges):
        raise ReplayError("ray supports are not pairwise distinct")
    return tuple(edges)


def check_gate() -> Fraction:
    gate = Fraction(111, ORDER ** 4) - Fraction(7 * 7, 24 * 24)
    if gate != Fraction(1, 1728):
        raise ReplayError(f"gate is {gate}, not 1/1728")
    return gate


def unhit_masks(edge_masks: tuple[int, ...], hit: int) -> list[int]:
    return [m for m in edge_masks if not (m & hit)]


def independent_search(edges: tuple[frozenset[int], ...], budget: int) -> tuple[tuple[int, ...] | None, int]:
    """Exact DFS over bit masks, with dynamic pivot and coverage ordering.

    This search is intentionally separate from the certificate's node graph.
    It explores the dual recurrence directly and reports a witness if one is
    found.  A complete return of None is an exact no-transversal result.
    """
    masks = tuple(sum(1 << cell for cell in edge) for edge in edges)
    states = 0
    dead: set[tuple[int, int]] = set()

    def visit(hit: int, depth: int) -> tuple[int, ...] | None:
        nonlocal states
        states += 1
        key = (hit, depth)
        if key in dead:
            return None
        open_edges = unhit_masks(masks, hit)
        if not open_edges:
            return tuple(i for i in range(CELL_TOTAL) if hit & (1 << i))
        if depth >= budget:
            dead.add(key)
            return None
        # Dynamic pivot: smallest currently available edge, tie-broken by
        # highest total overlap with the other open constraints.
        def pivot_key(mask: int) -> tuple[int, int]:
            overlap = sum((mask & other).bit_count() for other in open_edges)
            return (mask.bit_count(), -overlap)
        pivot = min(open_edges, key=pivot_key)
        choices = [i for i in range(CELL_TOTAL) if pivot & (1 << i) and not (hit & (1 << i))]
        frequency = {i: sum(bool(m & (1 << i)) for m in open_edges) for i in choices}
        for cell in sorted(choices, key=lambda i: (-frequency[i], i)):
            found = visit(hit | (1 << cell), depth + 1)
            if found is not None:
                return found
        dead.add(key)
        return None

    return visit(0, 0), states


def verify_certificate(cert: dict, edges: tuple[frozenset[int], ...], source_sha: str) -> int:
    if cert.get("schema") != "terra-sixdelete-hypergraph-proof-v1":
        raise ReplayError("proof schema mismatch")
    if cert.get("source_sha256") != source_sha or cert.get("ray_supports_sha256") != support_hash(edges):
        raise ReplayError("proof hash binding mismatch")
    if (cert.get("cells"), cert.get("legal_rows"), cert.get("after_six_gate"),
            cert.get("source_verdict"), cert.get("ray_count")) != (
                CELL_TOTAL, ROW_TOTAL, "1/1728", VERDICT, len(edges)):
        raise ReplayError("proof metadata mismatch")
    nodes = cert.get("nodes")
    if not isinstance(nodes, list) or cert.get("node_count") != len(nodes):
        raise ReplayError("proof node array mismatch")
    root = cert.get("root")
    if type(root) is not int or not 0 <= root < len(nodes) or cert.get("budget") != BUDGET:
        raise ReplayError("proof root/budget mismatch")
    masks = tuple(sum(1 << c for c in e) for e in edges)
    seen: dict[int, tuple[int, ...]] = {}
    active: set[int] = set()

    def walk(node_id: int, chosen: tuple[int, ...]) -> None:
        if node_id in seen:
            if seen[node_id] != chosen:
                raise ReplayError("proof node reused under another state")
            return
        if node_id in active or not 0 <= node_id < len(nodes):
            raise ReplayError("proof graph cycle/range error")
        node = nodes[node_id]
        if node.get("chosen") != list(chosen) or len(chosen) > BUDGET:
            raise ReplayError("proof chosen-set mismatch")
        hit = sum(1 << c for c in chosen)
        open_indices = [i for i, m in enumerate(masks) if not (m & hit)]
        if not open_indices:
            raise ReplayError("proof node already hits all constraints")
        active.add(node_id)
        if node.get("kind") == "packing":
            packing = node.get("packing")
            if not isinstance(packing, list) or not packing:
                raise ReplayError("malformed packing leaf")
            used = 0
            for ei in packing:
                if type(ei) is not int or ei not in open_indices or masks[ei] & used:
                    raise ReplayError("invalid disjoint packing")
                used |= masks[ei]
            if len(chosen) + len(packing) <= BUDGET:
                raise ReplayError("packing does not exceed remaining budget")
        elif node.get("kind") == "branch":
            candidates = [i for i in open_indices]
            # The certificate commits to the source's canonical edge order;
            # use the explicit cell-list tie break rather than relying on the
            # integer value of a bit mask (which is representation-specific).
            pivot = min(candidates, key=lambda i: (len(edges[i]), tuple(sorted(edges[i])), i))
            if node.get("edge") != pivot:
                raise ReplayError("noncanonical proof pivot")
            children = node.get("children")
            want = sorted(edges[pivot])
            if (not isinstance(children, list) or
                    [x[0] if isinstance(x, list) and len(x) == 2 else None for x in children] != want):
                raise ReplayError("proof branch does not exhaust pivot")
            for cell, child in children:
                if type(cell) is not int or type(child) is not int:
                    raise ReplayError("malformed proof child")
                walk(child, tuple(sorted(chosen + (cell,))))
        else:
            raise ReplayError("unknown proof node kind")
        active.remove(node_id)
        seen[node_id] = chosen

    walk(root, ())
    if len(seen) != len(nodes):
        raise ReplayError("proof has unreachable nodes")
    return len(seen)


def expect_rejection(fn, label: str) -> None:
    try:
        fn()
    except ReplayError:
        return
    raise ReplayError(f"planted failure was accepted: {label}")


def self_tests(doc: dict, cert: dict, edges: tuple[frozenset[int], ...], source_sha: str) -> None:
    damaged = copy.deepcopy(doc)
    damaged["rays"][0]["rows"][0][4] += 1
    expect_rejection(lambda: replay_rays(damaged), "ray RHS mutation")
    damaged = copy.deepcopy(doc)
    damaged["rays"][0]["rows"][0][0] += 1
    expect_rejection(lambda: replay_rays(damaged), "ray incidence mutation")
    badproof = copy.deepcopy(cert)
    leaf = next(n for n in badproof["nodes"] if n.get("kind") == "packing")
    leaf["packing"] = []
    expect_rejection(lambda: verify_certificate(badproof, edges, source_sha), "proof packing mutation")
    feasible = tuple(frozenset({i}) for i in range(BUDGET))
    witness, _ = independent_search(feasible, BUDGET)
    if witness is None:
        raise ReplayError("six-singleton planted feasible instance rejected")
    impossible = tuple(frozenset({i}) for i in range(BUDGET + 1))
    witness, _ = independent_search(impossible, BUDGET)
    if witness is not None:
        raise ReplayError("seven-singleton planted impossible instance accepted")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("checkpoint", type=Path)
    ap.add_argument("proof", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    try:
        source = args.checkpoint.read_bytes()
        proof_source = args.proof.read_bytes()
        source_sha = sha256_bytes(source)
        before = (source_sha, sha256_bytes(proof_source))
        doc = json.loads(source.decode("utf-8"))
        cert = json.loads(proof_source.decode("utf-8"))
        if doc.get("max_deletions") != BUDGET or doc.get("verdict") != VERDICT:
            raise ReplayError("checkpoint is not the terminal six-deletion claim")
        edges = replay_rays(doc)
        if len(edges) != 943:
            raise ReplayError(f"expected 943 exact rays, got {len(edges)}")
        rows = count_rows()
        if rows != ROW_TOTAL:
            raise ReplayError(f"legal continuous closure count {rows} != {ROW_TOTAL}")
        gate = check_gate()
        proof_nodes = verify_certificate(cert, edges, source_sha)
        witness, search_states = independent_search(edges, BUDGET)
        if witness is not None:
            raise ReplayError(f"independent search found <=6 hitting set {witness}")
        if args.self_test:
            self_tests(doc, cert, edges, source_sha)
        after = (sha256_bytes(args.checkpoint.read_bytes()), sha256_bytes(args.proof.read_bytes()))
        if before != after:
            raise ReplayError("input bytes changed during replay")
        print("LUNA_REPLAY_OK")
        print(f"cells={len(CELLS)} legal_rows={rows} rays={len(edges)}")
        print(f"gate={gate} support_sha256={support_hash(edges)}")
        print(f"checkpoint_sha256={source_sha} proof_nodes={proof_nodes}")
        print(f"independent_exact_search=NONE states={search_states}")
        if args.self_test:
            print("PLANTED_FAILURES_AND_NONMUTATION_OK")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ReplayError) as exc:
        print(f"LUNA_REPLAY_FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

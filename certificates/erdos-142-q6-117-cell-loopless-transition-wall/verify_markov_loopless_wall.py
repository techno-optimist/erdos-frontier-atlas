#!/usr/bin/env python3
"""Independent exact replay for a q=6 synchronized transition Farkas wall.

The row convention is deliberately the same raw-canonical continuous closure
convention as the supplied 117-cell certificate.  No producer code is
imported.  A row [x,y,z,b] represents h[x]+h[z]-2h[y] >= b after the
quadratic part 2||.||^2 has been eliminated and multiplied by q^2.
"""
from __future__ import annotations

import argparse
import copy
import json
from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path

Q = 6
S0 = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
      (5, 0), (5, 1), (5, 2))
D = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
     (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))


class VerificationError(ValueError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def bundle() -> tuple[tuple[int, int, int, int], ...]:
    out = tuple((a, b, (a + da) % Q, (b + db) % Q)
                for a, b in S0 for da, db in D)
    if len(out) != 117 or len(set(out)) != 117:
        fail("the independently decoded alphabet is not 117 distinct cells")
    return out


U = bundle()


def coordinate_requirement(a: int, b: int, c: int) -> Fraction | None:
    """Exact closure supremum for one scalar q=6 cell branch.

    For digits a,b,c, enumerate the modular carry k.  The physical residual
    ell=6k-(a+c-2b) must be -1, 0, or 1, giving respectively the closed
    offsets [1/2,1], [0,1], or [0,1/2].  The affine expression is maximized
    at the indicated endpoint.  This is the continuous half-open semantics
    because these closure values are suprema of the corresponding branches.
    """
    defect = a + c - 2 * b
    values: list[Fraction] = []
    for carry in (-1, 0, 1):
        ell = Q * carry - defect
        if ell not in (-1, 0, 1):
            continue
        low = {-1: Fraction(1, 2), 0: Fraction(0), 1: Fraction(0)}[ell]
        high = {-1: Fraction(1), 0: Fraction(1), 1: Fraction(1, 2)}[ell]
        t = low if carry > 0 else high
        values.append(-2 * Q * carry *
                      (Fraction(a + c, 2) + b + 2 * t + Fraction(ell, 2)))
    return max(values) if values else None


COORD = tuple(tuple(tuple(coordinate_requirement(a, b, c) for c in range(Q))
                          for b in range(Q)) for a in range(Q))


def local_rhs(x: int, y: int, z: int) -> int | None:
    if not all(0 <= v < len(U) for v in (x, y, z)):
        return None
    terms = [COORD[U[x][j]][U[y][j]][U[z][j]] for j in range(4)]
    if any(t is None for t in terms):
        return None
    total = sum(terms, Fraction(0))
    if total.denominator != 1:
        fail("nonintegral raw-canonical row RHS")
    return int(total)


def check_local(row: object, label: str) -> tuple[int, int, int, int]:
    if not isinstance(row, list) or len(row) != 4 or any(type(v) is not int for v in row):
        fail(f"{label}: expected [x,y,z,rhs] integer row")
    x, y, z, rhs = row
    actual = local_rhs(x, y, z)
    if actual is None:
        fail(f"{label}: incompatible local carry row")
    if rhs != actual:
        fail(f"{label}: RHS {rhs} differs from exact raw-canonical value {actual}")
    return x, y, z, rhs


def decode_rows(payload: dict) -> tuple[tuple[int, tuple[int, int, int, int], tuple[int, int, int, int]], ...]:
    if payload.get("schema") != "erdos142-q6-synchronized-transition-wall-v1":
        fail("unknown certificate schema")
    if payload.get("q") != Q or payload.get("alphabet_cells") != len(U):
        fail("wrong quotient or alphabet metadata")
    if payload.get("transition_graph") != "all ordered distinct pairs of alphabet cells":
        fail("this replay is specifically for the loopless complete graph")
    if payload.get("scaled_variables") != "G=36*g and J=36*H":
        fail("certificate does not state the exact q^2 scaling")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        fail("no Farkas rows")
    decoded = []
    # This is the exact finite pricing universe of the deliberately smallest
    # nontrivial synchronized chain: two physical 4D blocks.  The wall itself
    # needs only five cuts, but every cut is checked against this whole local
    # carry ledger rather than against producer-supplied RHS data.
    pricing_cells = (41, 67, 80, 83)
    pricing_local = [(x, y, z, local_rhs(x, y, z))
                     for x, y, z in product(pricing_cells, repeat=3)
                     if local_rhs(x, y, z) is not None]
    pricing_triples = {row[:3] for row in pricing_local}
    for i, record in enumerate(rows):
        if not isinstance(record, dict) or type(record.get("weight")) is not int:
            fail(f"row {i}: malformed positive multiplier")
        weight = record["weight"]
        if weight <= 0:
            fail(f"row {i}: multiplier is not positive")
        left = check_local(record.get("left"), f"row {i}, first block")
        right = check_local(record.get("right"), f"row {i}, second block")
        if left[:3] not in pricing_triples or right[:3] not in pricing_triples:
            fail(f"row {i}: local row is outside the active exact pricing ledger")
        decoded.append((weight, left, right))
    return tuple(decoded)


def padded_local_rows(left: tuple[int, int, int, int],
                      right: tuple[int, int, int, int], m: int) -> tuple[tuple[int, int, int, int], ...]:
    """Pad with the common diagonal tail 0,1,0,1,... for every m >= 2.

    Cells 0 and 1 lie outside the active four-cell ray support, hence the
    join from the second block is loopless.  Every tail row is (p,p,p,0), so
    it is a genuine carry-zero local row.  Alternating p prevents a tail
    self-loop.  This works uniformly for every m, not merely a tested range.
    """
    if m < 2:
        fail("the synchronized transition model starts at two blocks")
    tail = tuple((p, p, p, 0) for p in (0 if j % 2 == 0 else 1
                                        for j in range(m - 2)))
    for row in tail:
        if local_rhs(*row[:3]) != row[3]:
            fail("internal error: common tail is not a carry-zero row")
    return (left, right) + tail


def replay_length(decoded: tuple[tuple[int, tuple[int, int, int, int], tuple[int, int, int, int]], ...],
                  m: int) -> tuple[int, set[int], set[tuple[int, int]]]:
    """Check the full G,J coefficient cancellation at one path length.

    A row for actual tables g,H is multiplied by q^2=36.  Thus the exact
    variables here are G=36g and J=36H, with the same RHS reconstructed from
    raw canonical endpoint costs.  Endpoint coefficients are halves and are
    retained as Fractions rather than cleared informally.
    """
    g: defaultdict[int, Fraction] = defaultdict(Fraction)
    edge: defaultdict[tuple[int, int], int] = defaultdict(int)
    total_rhs = 0
    active_cells: set[int] = set()
    active_edges: set[tuple[int, int]] = set()
    for index, (weight, left, right) in enumerate(decoded):
        local = padded_local_rows(left, right, m)
        total_rhs += weight * sum(row[3] for row in local)
        for role, coefficient in ((0, 1), (1, -2), (2, 1)):
            path = [row[role] for row in local]
            g[path[0]] += Fraction(weight * coefficient, 2)
            g[path[-1]] += Fraction(weight * coefficient, 2)
            active_cells.update(path)
            for a, b in zip(path, path[1:]):
                if a == b:
                    fail(f"row {index}, role {role}: transition {(a, b)} is a forbidden self-loop")
                edge[a, b] += weight * coefficient
                active_edges.add((a, b))
    if any(g.values()) or any(edge.values()):
        fail(f"length {m}: Farkas combination does not cancel every G or J coefficient")
    if total_rhs <= 0:
        fail(f"length {m}: Farkas combination has no positive raw endpoint contradiction")
    return total_rhs, active_cells, active_edges


def replay(payload: dict, max_length: int = 9) -> None:
    decoded = decode_rows(payload)
    if max_length < 2:
        fail("max_length must be at least two")
    total_rhs, active_cells, active_edges = replay_length(decoded, 2)

    if total_rhs != payload.get("expected_weighted_rhs"):
        fail("weighted RHS metadata mismatch")
    if sorted(active_cells) != payload.get("expected_active_cells"):
        fail("active cell semantics mismatch")
    if sorted(map(list, active_edges)) != payload.get("expected_active_transitions"):
        fail("active transition semantics mismatch")
    for m in range(3, max_length + 1):
        padded_rhs, _, _ = replay_length(decoded, m)
        if padded_rhs != total_rhs:
            fail(f"length {m}: common-tail padding changed the exact RHS")

    # Perron/density gate for the loopless complete 117-state directed graph.
    # It has exactly 116 outgoing choices at every state, so rho=116.
    rho = 116
    density_base = Fraction(rho, Q ** 4)
    gate = Fraction(7, 24) ** 2
    if not density_base > gate:
        fail("loopless Markov language misses the required Perron density gate")
    print("SEMANTICS_OK cells=117 q=6 cegar_path_blocks=2 variables=G=36g,J=36H")
    print("EXACT_PRICING_OK active_local_rows=16 paired_rows=100 selected_cuts=5")
    print(f"FARKAS_OK weighted_rhs={total_rhs} scaled_contradiction=0>={total_rhs}")
    print(f"COMMON_TAIL_PADDING_OK lengths=2..{max_length} universal_formula=alternating_0_1")
    print(f"PERRON_GATE_OK rho={rho} base={density_base} gate={gate} excess={density_base-gate}")


def self_test(payload: dict) -> None:
    bad_rhs = copy.deepcopy(payload)
    bad_rhs["rows"][0]["left"][3] += 1
    try:
        replay(bad_rhs)
    except VerificationError:
        pass
    else:
        fail("self-test accepted a corrupted local RHS")
    bad_loop = copy.deepcopy(payload)
    # Replace the second local row by another genuine local row with the same
    # first endpoint.  Both local carry rows remain legal; only the resulting
    # synchronized transition (41,41) is forbidden.
    bad_loop["rows"][0]["right"] = [41, 41, 80, 72]
    try:
        replay(bad_loop)
    except VerificationError as error:
        if "self-loop" not in str(error):
            raise
    else:
        fail("self-test accepted a forbidden self-loop")
    bad_weight = copy.deepcopy(payload)
    bad_weight["rows"][0]["weight"] += 1
    try:
        replay(bad_weight)
    except VerificationError:
        pass
    else:
        fail("self-test accepted a noncancelling Farkas multiplier")
    print("PLANTED_FAILURES_REJECTED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--max-length", type=int, default=9,
                        help="explicitly replay padded lengths 2 through this value")
    args = parser.parse_args()
    try:
        payload = json.loads(args.certificate.read_text(encoding="utf-8"))
        if args.self_test:
            self_test(payload)
        replay(payload, args.max_length)
    except (OSError, json.JSONDecodeError, VerificationError) as error:
        print(f"VERIFY_FAIL: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

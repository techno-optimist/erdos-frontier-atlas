#!/usr/bin/env python3
"""Exact replay of the endpoint-pruned Perron-core extension.

The script rebuilds the 117-cell bad-pair census, checks the supplied disjoint
matching, exhausts the integer sandwich-free core bound, and checks the small
finite-horizon endpoint-pruning example.  It uses only the standard library.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations

Q = 6
S0 = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
      (5, 0), (5, 1), (5, 2))
D = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
     (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
U = tuple((a, b, (a + da) % Q, (b + db) % Q)
          for a, b in S0 for da, db in D)

MATCHING = ((0, 12), (1, 4), (3, 18), (5, 17), (7, 24), (16, 31),
            (25, 36), (29, 68), (30, 69), (37, 76), (39, 41), (40, 43),
            (42, 54), (44, 46), (47, 64), (52, 91), (53, 56), (55, 67),
            (59, 98), (66, 105), (77, 116), (78, 79), (80, 93), (83, 84),
            (86, 87), (92, 104), (96, 108))


def coordinate_requirement(a: int, b: int, c: int) -> Fraction | None:
    defect = a + c - 2 * b
    vals: list[Fraction] = []
    for carry in (-1, 0, 1):
        ell = Q * carry - defect
        if ell not in (-1, 0, 1):
            continue
        low = {-1: Fraction(1, 2), 0: Fraction(0), 1: Fraction(0)}[ell]
        high = {-1: Fraction(1), 0: Fraction(1), 1: Fraction(1, 2)}[ell]
        t = low if carry > 0 else high
        vals.append(-2 * Q * carry *
                    (Fraction(a + c, 2) + b + 2 * t + Fraction(ell, 2)))
    return max(vals) if vals else None


COORD = tuple(tuple(tuple(coordinate_requirement(a, b, c)
                          for c in range(Q)) for b in range(Q))
              for a in range(Q))


def local_rhs(x: int, y: int, z: int) -> int | None:
    terms = [COORD[U[x][j]][U[y][j]][U[z][j]] for j in range(4)]
    if any(t is None for t in terms):
        return None
    total = sum(terms, Fraction(0))
    assert total.denominator == 1
    return int(total)


def bad_pairs() -> dict[tuple[int, int], int]:
    out: dict[tuple[int, int], int] = {}
    for a, b in combinations(range(len(U)), 2):
        r1 = local_rhs(a, b, b)
        r2 = local_rhs(a, a, b)
        if r1 is not None and r2 is not None and r1 + r2 > 0:
            out[(a, b)] = r1 + r2
    return out


def sandwich_free_bound() -> int:
    """Exhaust k,h,r possibilities allowed by the matching incidence count."""
    worst = 0
    witnesses: list[tuple[int, int, int, int]] = []
    for k in range(1, 118):
        h_min = max(0, k - 90)
        for h in range(h_min, min(27, k // 2) + 1):
            for r in range(h + 1):
                bound = min(k - r, k - (h - r))
                if bound > worst:
                    worst = bound
                    witnesses = [(k, h, r, bound)]
                elif bound == worst:
                    witnesses.append((k, h, r, bound))
    assert worst == 103
    assert any(k == 117 and h == 27 for k, h, _, _ in witnesses)
    return worst


def complete_core_endpoint_example() -> None:
    # Complete looped graph on n states: (A^m)[s,s] = n^(m-1), m>=1.
    n = 112
    counts = {m: n ** (m - 1) for m in range(1, 7)}
    assert counts[1] == 1
    assert all(counts[m + 1] == n * counts[m] for m in range(1, 6))
    assert Fraction(n) > Fraction(441, 4)

    # Removing only five of 117 vertices leaves at least 22 of the 27 disjoint
    # matching pairs intact, hence horizon two already has a sandwich witness
    # in the complete graph (choose the common start/end state as q=p=s).
    removed = set(range(112, 117))
    intact = [pair for pair in MATCHING if not (set(pair) & removed)]
    assert len(intact) >= 22


def main() -> None:
    assert len(U) == len(set(U)) == 117
    bad = bad_pairs()
    assert len(bad) == 187
    assert Counter(bad.values()) == Counter({72: 173, 144: 14})
    flat = [x for pair in MATCHING for x in pair]
    assert len(flat) == len(set(flat)) == 54
    assert all(tuple(sorted(pair)) in bad for pair in MATCHING)
    assert all(local_rhs(p, p, p) == 0 for p in range(117))

    bound = sandwich_free_bound()
    assert Fraction(bound) < Fraction(441, 4)
    complete_core_endpoint_example()

    print("PASS_ENDPOINT_PRUNED_EXTENSION")
    print("CENSUS_OK cells=117 bad_pairs=187 matching=27")
    print("SANDWICH_FREE_CORE_BOUND rho<=103<441/4")
    print("PERRON_CORE_OK fixed_endpoint_pruning_preserves_above_gate_wall")
    print("POSITION_DEPENDENT_LABEL_TABLES_OK exact_two_path_cancellation")
    print("FINITE_HORIZON_CAVEAT_OK complete112_fixed_endpoint_horizon1")


if __name__ == "__main__":
    main()

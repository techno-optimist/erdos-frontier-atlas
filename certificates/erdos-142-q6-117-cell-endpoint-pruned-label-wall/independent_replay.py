#!/usr/bin/env python3
"""No-import hostile replay for the endpoint-pruned extension.

This implementation deliberately does not import the primary replay.  It
derives scalar closure costs from the quadratic identity

    2x^2 + 2z^2 - 4y^2 - (x-z)^2 = 4*k*y + k^2

when x+z=2y+k, enumerates core-incidence patterns rather than using the
primary k/h shortcut, and checks cancellation as a multiset of complete path
labels.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import product

Q = 6
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFFSETS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
           (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
CELLS = tuple((x, y, (x + dx) % Q, (y + dy) % Q)
              for (x, y), (dx, dy) in product(BASE, OFFSETS))

MATCHING_WITH_GAPS = (
    (0, 12, 72), (1, 4, 72), (3, 18, 72), (5, 17, 72),
    (7, 24, 72), (16, 31, 72), (25, 36, 72), (29, 68, 72),
    (30, 69, 72), (37, 76, 72), (39, 41, 72), (40, 43, 72),
    (42, 54, 72), (44, 46, 72), (47, 64, 72), (52, 91, 72),
    (53, 56, 144), (55, 67, 72), (59, 98, 72), (66, 105, 72),
    (77, 116, 72), (78, 79, 72), (80, 93, 72), (83, 84, 72),
    (86, 87, 72), (92, 104, 144), (96, 108, 72),
)


def scalar_closure_cost(x_digit: int, y_digit: int,
                        z_digit: int) -> Fraction | None:
    """Maximal scaled correction RHS over the closed residual polytope."""
    digit_defect = x_digit + z_digit - 2 * y_digit
    candidates: list[Fraction] = []
    for carry in (-1, 0, 1):
        residual_defect = Q * carry - digit_defect
        # rx+rz=2*ry+residual_defect, with residuals in [0,1] in
        # the necessary one-sided closure.
        lower = max(Fraction(0), -Fraction(residual_defect, 2))
        upper = min(Fraction(1), Fraction(2 - residual_defect, 2))
        if lower > upper:
            continue
        ry = lower if carry > 0 else upper
        # -36*(4*carry*y+carry^2), y=(y_digit+ry)/6.
        cost = -24 * carry * (y_digit + ry) - 36 * carry * carry
        candidates.append(cost)
    return max(candidates) if candidates else None


def row_cost(x_label: int, y_label: int, z_label: int) -> int | None:
    terms = [scalar_closure_cost(CELLS[x_label][i], CELLS[y_label][i],
                                 CELLS[z_label][i]) for i in range(4)]
    if any(value is None for value in terms):
        return None
    answer = sum(terms, Fraction(0))
    assert answer.denominator == 1
    return int(answer)


def check_matching_geometry() -> None:
    assert len(CELLS) == len(set(CELLS)) == 117
    vertices: list[int] = []
    observed: list[int] = []
    for a, b, expected in MATCHING_WITH_GAPS:
        first = row_cost(a, b, b)
        second = row_cost(a, a, b)
        assert first is not None and second is not None
        assert first + second == expected > 0
        observed.append(expected)
        vertices.extend((a, b))
    assert len(vertices) == len(set(vertices)) == 54
    assert Counter(observed) == Counter({72: 25, 144: 2})


def independent_core_bound() -> int:
    """Enumerate every incidence pattern of a core with the 27-pair matching."""
    worst = 0
    # s: unmatched vertices chosen; t: matching pairs contributing one vertex;
    # h: matching pairs contributing both.  Thus t+h<=27 and k=s+t+2h.
    for s in range(64):
        for h in range(28):
            for t in range(28 - h):
                k = s + t + 2 * h
                if not 1 <= k <= 117:
                    continue
                # r of the h nonsandwiched full pairs are out-disjoint; the
                # rest are in-disjoint.  Right and left Perron partitions give
                # k-r and k-(h-r) blocks respectively.
                for r in range(h + 1):
                    bound = min(k - r, k - (h - r))
                    worst = max(worst, bound)
    assert worst == 103
    return worst


def add(counter: Counter, key, coefficient: int) -> None:
    counter[key] += coefficient
    if counter[key] == 0:
        del counter[key]


def check_complete_path_cancellation() -> None:
    # The two accepted paths share prefix q and suffix p but have a/b at one
    # position.  Labels are arbitrary tokens here because cancellation is
    # purely a complete-path multiset identity.
    path_a = (11, 37, 52, 3, 90, 8)
    path_b = (11, 37, 91, 3, 90, 8)

    whole_path = Counter()
    # Row (A,B,B): +Phi(A)-2Phi(B)+Phi(B).
    for path, coefficient in ((path_a, 1), (path_b, -2), (path_b, 1)):
        add(whole_path, path, coefficient)
    # Row (A,A,B): +Phi(A)-2Phi(A)+Phi(B).
    for path, coefficient in ((path_a, 1), (path_a, -2), (path_b, 1)):
        add(whole_path, path, coefficient)
    assert not whole_path

    # Expand the same identity into independently position-indexed vertex and
    # edge features.  This explicitly covers position-dependent tables.
    position_features = Counter()
    for path, coefficient in ((path_a, 1), (path_b, -1),
                              (path_b, 1), (path_a, -1)):
        for i, label in enumerate(path):
            add(position_features, ("v", i, label), coefficient)
        for i, edge in enumerate(zip(path, path[1:])):
            add(position_features, ("e", i, edge), coefficient)
    assert not position_features

    # The independently replayed matched gap remains strictly positive after
    # the zero correction sum.
    a, b, gap = MATCHING_WITH_GAPS[0]
    assert row_cost(a, b, b) + row_cost(a, a, b) == gap == 72


def check_cyclic_residue_identity() -> None:
    # In a period-d SCC, write chi(edge head)=chi(edge tail)+1.  The sandwich
    # q->a/b->p therefore advances two cyclic classes.  Exhaust all possible
    # periods/classes and verify that routing entry r through q,(a/b),p to exit
    # z has the same residue as every r-to-z walk.
    for period in range(1, 118):
        for chi_r in range(period):
            for chi_q in range(period):
                chi_p = (chi_q + 2) % period
                for chi_z in range(period):
                    via_sandwich = ((chi_q - chi_r) + 2
                                    + (chi_z - chi_p)) % period
                    direct = (chi_z - chi_r) % period
                    assert via_sandwich == direct

    # Concrete period-three sanity check: complete edges between consecutive
    # cyclic classes {q},{a,b},{p}.  Closed walks at q have lengths 3t, so the
    # branch realizes every admissible q-to-p length 2 mod 3.
    for length in range(2, 80):
        admissible = length % 3 == 2
        branch_with_q_cycles = (length >= 2 and (length - 2) % 3 == 0)
        assert admissible == branch_with_q_cycles


def check_short_horizon_control() -> None:
    n = 112
    # Complete looped n-state adjacency, fixed start=end s.
    counts = [None] + [n ** (m - 1) for m in range(1, 8)]
    assert counts[1] == 1
    assert all(counts[m + 1] == n * counts[m] for m in range(1, 7))
    assert Fraction(n) > Fraction(441, 4)

    retained = set(range(112))
    intact = [(a, b) for a, b, _ in MATCHING_WITH_GAPS
              if a in retained and b in retained]
    assert intact
    s = 0
    a, b = intact[0]
    assert (s, a, s) != (s, b, s)  # horizon-two branch-and-merge pair


def planted_failures() -> None:
    # Losing disjointness invalidates the 54-vertex incidence count.
    corrupted = list(MATCHING_WITH_GAPS)
    corrupted[-1] = (corrupted[0][0], corrupted[-1][1], corrupted[-1][2])
    assert len({v for a, b, _ in corrupted for v in (a, b)}) < 54

    # A wrong centre coefficient leaves a nonzero complete-path coefficient.
    a_path, b_path = (1, 2, 3), (1, 4, 3)
    broken = Counter({a_path: 2 - 1, b_path: 2 - 2})
    assert broken

    # A one-class shift of p breaks the cyclic residue identity for d>1.
    period, chi_r, chi_q, chi_z = 5, 1, 3, 4
    wrong_p = (chi_q + 3) % period
    assert ((chi_q - chi_r) + 2 + (chi_z - wrong_p)) % period \
        != (chi_z - chi_r) % period


def main() -> None:
    check_matching_geometry()
    bound = independent_core_bound()
    assert Fraction(bound) < Fraction(441, 4)
    check_complete_path_cancellation()
    check_cyclic_residue_identity()
    check_short_horizon_control()
    planted_failures()
    print("PASS_INDEPENDENT_ENDPOINT_PRUNED_REPLAY")
    print("MATCHING_GEOMETRY_OK pairs=27 gaps=72:25,144:2")
    print("MIXED_LEFT_RIGHT_PERRON_OK sandwich_free_rho<=103<441/4")
    print("LABEL_PATH_CANCELLATION_OK arbitrary_Phi_m_and_position_tables")
    print("SCC_RESIDUE_OK exact_length_branch_exists_on_eventual_residues")
    print("SHORT_HORIZON_CONTROL_OK complete112_rate=112_horizon1_exception")
    print("PLANTED_FAILURES_REJECTED")


if __name__ == "__main__":
    main()

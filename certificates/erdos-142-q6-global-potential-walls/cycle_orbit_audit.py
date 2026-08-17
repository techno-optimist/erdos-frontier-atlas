#!/usr/bin/env python3
"""Exact scope audit for the three-row q=6 global-potential cycle.

Enumerate all 8^5 D4 assignments, retain every maximum-union assignment,
and test every global D4 transport of the three-row packet. This is a finite
combinatorial scope screen, not an LP or continuum claim.
"""

from __future__ import annotations

import itertools
import json

Q = 6
ROLES = ("P1", "P2", "P3", "B", "K")
WORDS = (
    ("P1", "K", "B"),
    ("B", "K", "P1"),
    ("P2", "B", "P2"),
    ("P3", "B", "B"),
    ("B", "B", "P3"),
)
EXPECTED_COVERED = 32
EXPECTED_MAXIMIZERS = 256
EXPECTED_MASS = 3645


def base_support() -> frozenset[tuple[int, int]]:
    """Exact q=6 specialization of the three half-open EHPS pieces."""
    return frozenset(
        (x, y)
        for x in range(Q)
        for y in range(Q)
        if (x >= 3 and 5 <= x + y <= 7)
        or (x >= 3 and y < 3 and x + y == 8)
        or (x < 3 and y >= 3 and x + y == 8 and 2 * x + y >= 10)
    )


def d4(point: tuple[int, int], index: int) -> tuple[int, int]:
    x, y = point
    if index & 1:
        x = Q - 1 - x
    if index & 2:
        y = Q - 1 - y
    if index & 4:
        x, y = y, x
    return x, y


BASE = base_support()
IMAGES = tuple(frozenset(d4(point, index) for point in BASE) for index in range(8))


def union_mass(assignment: tuple[int, ...]) -> int:
    union = set()
    for word in WORDS:
        union.update(
            itertools.product(*(IMAGES[assignment[ROLES.index(role)]] for role in word))
        )
    return len(union)


def cycle_transports(assignment: tuple[int, ...]) -> tuple[int, ...]:
    supports = {role: IMAGES[assignment[i]] for i, role in enumerate(ROLES)}
    hits = []
    # Packet vertices are (A,B,C), (A,B,B), and (A,B,D).
    for index in range(8):
        a, b, c, d = (
            d4(point, index) for point in ((4, 0), (1, 3), (3, 1), (5, 5))
        )
        if (
            a in supports["P2"]
            and c in supports["P2"]
            and a in supports["P3"]
            and b in supports["B"]
            and d in supports["B"]
        ):
            hits.append(index)
    return tuple(hits)


def main() -> None:
    assert len(BASE) == 9
    assert len(set(IMAGES)) == 8
    masses = {
        assignment: union_mass(assignment)
        for assignment in itertools.product(range(8), repeat=5)
    }
    maximum = max(masses.values())
    maximizers = tuple(sorted(a for a, mass in masses.items() if mass == maximum))
    covered = {assignment: cycle_transports(assignment) for assignment in maximizers}
    covered = {assignment: hits for assignment, hits in covered.items() if hits}

    assert maximum == EXPECTED_MASS
    assert len(maximizers) == EXPECTED_MAXIMIZERS
    assert len(covered) == EXPECTED_COVERED
    assert (7, 7, 7, 6, 7) in covered
    # The B representative needs its separate 646-row ray; this tiny cycle
    # does not certify it.
    assert (7, 6, 7, 6, 7) not in covered
    assert all(0 <= index < 8 for hits in covered.values() for index in hits)

    print("PASS_Q6_GLOBAL_THREE_ROW_CYCLE_SCOPE_AUDIT")
    print(
        json.dumps(
            {
                "assignment_count": 8**5,
                "maximum_union_mass": maximum,
                "maximizer_count": len(maximizers),
                "three_row_cycle_covered": len(covered),
                "three_row_cycle_uncovered": len(maximizers) - len(covered),
                "cycle_positive_contradiction_raw": 48,
                "finite_q_only": True,
                "continuum_claim": False,
                "global_impossibility_claim_for_uncovered": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

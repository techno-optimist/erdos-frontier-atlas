#!/usr/bin/env python3
"""Independent stdlib replay of the 117-cell full-word dilation quotient.

No code or data are imported from the other dilation, transition, or word
quotient packets.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import product

Q = 6
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFFSETS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
           (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
CELLS = tuple((a, b, (a + da) % Q, (b + db) % Q)
              for a, b in BASE for da, db in OFFSETS)

PAIR_DIGEST = "0cdd8ee497e047ec11f50ff248c2a7163b4f2d4abbd39d41d6eb4cf9698ebe8b"
SIMPLE7 = ((25, 24), (37, 36), (41, 40), (47, 46),
           (77, 76), (79, 78), (84, 86))
MAXIMUM21 = ((55, 3), (17, 4), (59, 12), (68, 16), (25, 24),
             (37, 36), (52, 39), (53, 40), (105, 41), (96, 46),
             (106, 54), (69, 56), (111, 64), (77, 76), (79, 78),
             (93, 80), (84, 83), (87, 86), (92, 91), (99, 98),
             (104, 116))
BARRIER = {12, 46}


def enumerate_pairs() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    digest_rows: list[list[object]] = []
    for ia, a in enumerate(CELLS):
        for ib, b in enumerate(CELLS):
            active = [i for i, (x, y) in enumerate(zip(a, b))
                      if y == (x - 1) % Q]
            wraps = [i for i in active if a[i] == 0 and b[i] == 5]
            if wraps and all(x == y or y == (x - 1) % Q
                             for x, y in zip(a, b)):
                rows.append({"a": ia, "b": ib,
                             "active": tuple(active), "wraps": tuple(wraps)})
                digest_rows.append([ia, ib, active, wraps])
    encoded = (json.dumps(digest_rows, separators=(",", ":")) + "\n").encode()
    assert hashlib.sha256(encoded).hexdigest() == PAIR_DIGEST
    assert len(rows) == 66
    assert Counter(len(r["active"]) for r in rows) == Counter(
        {1: 11, 2: 38, 3: 10, 4: 7})
    assert Counter(len(r["wraps"]) for r in rows) == Counter({1: 61, 2: 5})
    return rows


def scalar_requirement(x_digit: int, y_digit: int, z_digit: int,
                       rx: Fraction, ry: Fraction, rz: Fraction) -> Fraction:
    numerator = ((x_digit + rx) + (z_digit + rz)
                 - 2 * (y_digit + ry))
    assert numerator.denominator == 1
    carry = int(numerator / Q)
    assert numerator == Q * carry
    y = Fraction(y_digit + ry, Q)
    return -36 * (4 * carry * y + carry * carry)


def oriented_pair_rows(row: dict[str, object], t: Fraction,
                       reverse: bool) -> tuple[Fraction, Fraction]:
    assert 0 < t < Fraction(1, 3)
    a_index, b_index = int(row["a"]), int(row["b"])
    a, b = CELLS[a_index], CELLS[b_index]
    active = set(row["active"])
    first = Fraction(0)
    second = Fraction(0)
    for i in range(4):
        if i not in active:
            s = Fraction(i + 2, 10)
            p_t = p_3 = q_t = q_3 = s
        elif not reverse:
            p_t, p_3, q_t, q_3 = t, 3 * t, 1 - t, 1 - 3 * t
        else:
            p_t, p_3, q_t, q_3 = 1 - t, 1 - 3 * t, t, 3 * t
        assert all(0 < r < 1 for r in (p_t, p_3, q_t, q_3))

        p_digit, q_digit = (b[i], a[i]) if reverse else (a[i], b[i])
        # Global rows (P(t),Q(t),Q(3t)) and (P(3t),P(t),Q(t)).
        first += scalar_requirement(p_digit, q_digit, q_digit,
                                    p_t, q_t, q_3)
        second += scalar_requirement(p_digit, p_digit, q_digit,
                                     p_3, p_t, q_t)
    expected = len(row["wraps"]) * (72 - 48 * t)
    assert first + second == expected > 0
    if reverse:
        assert first == len(row["wraps"]) * (-36 - 24 * t)
        assert second == len(row["wraps"]) * (108 - 24 * t)
    else:
        assert first == len(row["wraps"]) * (108 - 24 * t)
        assert second == len(row["wraps"]) * (-36 - 24 * t)
    return first, second


def check_orientations(rows: list[dict[str, object]]) -> None:
    for row in rows:
        for t in (Fraction(1, 12), Fraction(2, 15), Fraction(7, 24)):
            oriented_pair_rows(row, t, reverse=False)
            oriented_pair_rows(row, t, reverse=True)


def edge_lookup(rows: list[dict[str, object]]) -> dict[tuple[int, int], dict[str, object]]:
    return {(int(r["a"]), int(r["b"])): r for r in rows}


def check_matching(matching: tuple[tuple[int, int], ...],
                   edges: dict[tuple[int, int], dict[str, object]]) -> None:
    flat = [v for edge in matching for v in edge]
    assert len(flat) == len(set(flat))
    assert all(edge in edges for edge in matching)


def components(adjacency: dict[int, set[int]], removed=frozenset()) -> list[set[int]]:
    seen = set(removed)
    answer: list[set[int]] = []
    for start in range(117):
        if start in seen:
            continue
        comp = {start}
        seen.add(start)
        stack = [start]
        while stack:
            x = stack.pop()
            for y in adjacency[x]:
                if y not in seen:
                    seen.add(y)
                    comp.add(y)
                    stack.append(y)
        answer.append(comp)
    return answer


def maximum_matching_audit(rows: list[dict[str, object]],
                           edges: dict[tuple[int, int], dict[str, object]]) -> None:
    check_matching(MAXIMUM21, edges)
    adjacency = {i: set() for i in range(117)}
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    original_sizes = Counter(map(len, components(adjacency)))
    assert original_sizes == Counter({1: 73, 4: 1, 40: 1})
    after = components(adjacency, BARRIER)
    after_sizes = Counter(map(len, after))
    assert after_sizes == Counter({1: 76, 4: 1, 35: 1})
    odd_components = sum(len(c) % 2 for c in after)
    forced_unmatched = odd_components - len(BARRIER)
    upper = (117 - forced_unmatched) // 2
    assert odd_components == 77
    assert forced_unmatched == 75
    assert upper == len(MAXIMUM21) == 21


def quotient(matching: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    answer = [-1] * 117
    group = 0
    for a, b in matching:
        assert answer[a] == answer[b] == -1
        answer[a] = answer[b] = group
        group += 1
    for label in range(117):
        if answer[label] == -1:
            answer[label] = group
            group += 1
    assert group == 117 - len(matching)
    return tuple(answer)


def word_telescope_audit(edges: dict[tuple[int, int], dict[str, object]]) -> None:
    # Exhaust every equal/forward/reverse pattern across the seven simple word
    # positions.  This explicitly checks multiple differing blocks and mixed
    # orientations.  State 0 is equal, 1 forward, 2 reverse.
    t = Fraction(1, 7)
    for pattern in product(range(3), repeat=7):
        if not any(pattern):
            continue
        first = Fraction(0)
        second = Fraction(0)
        wrap_total = 0
        for state, edge in zip(pattern, SIMPLE7):
            if state == 0:
                continue
            row = edges[edge]
            r1, r2 = oriented_pair_rows(row, t, reverse=(state == 2))
            first += r1
            second += r2
            wrap_total += len(row["wraps"])
        assert wrap_total == sum(state != 0 for state in pattern)
        assert first + second == wrap_total * (72 - 48 * t) > 0

    # Abstract H coefficient identity for arbitrary full-word physical points.
    coefficients = Counter()
    for key, value in (("P(t)", 1), ("Q(3t)", 1), ("Q(t)", -2),
                       ("P(3t)", 1), ("P(t)", -2), ("Q(t)", 1)):
        coefficients[key] += value
    assert coefficients == Counter({"P(3t)": 1, "Q(3t)": 1,
                                    "P(t)": -1, "Q(t)": -1})

    # Finite telescope, including the exact floor choice in the theorem.
    for M, wraps in ((0, 1), (72, 1), (10_000, 7), (10**9, 21)):
        N = (4 * M + 6 * wraps) // (72 * wraps) + 1
        lower = 72 * wraps * N - 6 * wraps * (1 - Fraction(1, 3**N))
        assert lower > 4 * M


def quotient_and_gate_audit() -> None:
    q7 = quotient(SIMPLE7)
    q21 = quotient(MAXIMUM21)
    assert len(set(q7)) == 110
    assert len(set(q21)) == 96
    gate = Fraction(441, 4)
    assert Fraction(110) < gate
    assert Fraction(96) < gate
    assert Fraction(111) > gate  # six doubleton merges do not suffice by count.
    for m in range(1, 9):
        assert Fraction(110**m) < gate**m
        assert Fraction(96**m) < gate**m
        assert Fraction(110**m, 1296**m) < Fraction(49, 576)**m


def planted_failures(rows: list[dict[str, object]],
                     edges: dict[tuple[int, int], dict[str, object]]) -> None:
    overlapping = SIMPLE7[:-1] + ((SIMPLE7[0][0], SIMPLE7[-1][1]),)
    try:
        check_matching(overlapping, edges)
    except AssertionError:
        pass
    else:
        raise AssertionError("overlapping matching passed")

    wrong_barrier = {12}
    adjacency = {i: set() for i in range(117)}
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    odd = sum(len(c) % 2 for c in components(adjacency, wrong_barrier))
    try:
        assert odd - len(wrong_barrier) == 75
    except AssertionError:
        pass
    else:
        raise AssertionError("incomplete Tutte barrier passed")

    # Replacing 72-48t by its sign-reversed mutation must be caught.
    t = Fraction(1, 7)
    correct = oriented_pair_rows(rows[0], t, False)
    assert sum(correct) > 0
    try:
        assert sum(correct) == -(len(rows[0]["wraps"]) * (72 - 48 * t))
    except AssertionError:
        pass
    else:
        raise AssertionError("sign-reversed gap passed")


def main() -> None:
    assert len(CELLS) == len(set(CELLS)) == 117
    rows = enumerate_pairs()
    edges = edge_lookup(rows)
    check_orientations(rows)
    check_matching(SIMPLE7, edges)
    assert all(len(edges[e]["active"]) == len(edges[e]["wraps"]) == 1
               for e in SIMPLE7)
    maximum_matching_audit(rows, edges)
    word_telescope_audit(edges)
    quotient_and_gate_audit()
    planted_failures(rows, edges)
    print("PASS_FULLWORD_DILATION_QUOTIENT_AUDIT")
    print("PAIR_CENSUS_OK directed=66 digest=" + PAIR_DIGEST)
    print("SIMPLE7_OK disjoint=true classes=110 both_orientations=strict")
    print("MAXIMUM_MATCHING_OK size=21 classes=96 barrier={12,46}")
    print("TUTTE_BOUND_OK odd_components=77 forced_unmatched=75")
    print("MULTIBLOCK_TELESCOPE_OK arbitrary_bounded_residual_H")
    print("FINITE_N_OK D(T)-D(T/3^N)>=72WN-6W(1-3^-N)>4M")
    print("WORD_BOUND_OK seven:|L_m|<=110^m; maximum:|L_m|<=96^m<(441/4)^m")
    print("PLANTED_FAILURES_REJECTED")


if __name__ == "__main__":
    main()

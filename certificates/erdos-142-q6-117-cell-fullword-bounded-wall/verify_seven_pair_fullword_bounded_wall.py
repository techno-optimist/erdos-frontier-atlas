#!/usr/bin/env python3
"""Standalone no-import replay of the seven-pair full-word bounded wall.

It independently reconstructs the 117 q=6 cells, seven 0/5-wrap pairs,
both strict midpoint orientations, direct raw-norm RHS values, mixed
full-word rows, whole-word h cancellation, and the finite telescope.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as F
from itertools import product

Q = 6
N = 117
GATE = F(441, 4)
S = F(1, 2)

SEED = (
    (3, 2), (3, 3), (3, 4),
    (4, 1), (4, 2), (4, 3),
    (5, 0), (5, 1), (5, 2),
)
OFFSETS = (
    (0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
    (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3),
)
CELLS = tuple(
    (a, b, (a + da) % Q, (b + db) % Q)
    for a, b in SEED
    for da, db in OFFSETS
)

# Ordered as (low, high).  At the sole differing coordinate, low has digit 0
# and high has digit 5.
PAIRS = (
    (25, 24), (37, 36), (41, 40), (47, 46),
    (77, 76), (79, 78), (84, 86),
)


def norm2(x: tuple[F, ...]) -> F:
    return sum((v * v for v in x), F(0))


def raw_cost(x: tuple[F, ...], z: tuple[F, ...]) -> F:
    """The required canonical-representative cost, not geodesic torus cost."""
    return sum(((a - b) ** 2 for a, b in zip(x, z)), F(0))


def geodesic_cost(x: tuple[F, ...], z: tuple[F, ...]) -> F:
    """Deliberately wrong metric used only for a planted semantic mutation."""
    return sum((min(abs(a - b), 1 - abs(a - b)) ** 2 for a, b in zip(x, z)), F(0))


def rhs(x: tuple[F, ...], y: tuple[F, ...], z: tuple[F, ...]) -> F:
    """RHS for h(x)+h(z)-2h(y), h=q^2(F-2||.||^2), directly from norms."""
    return Q ** 2 * (raw_cost(x, z) - 2 * (norm2(x) + norm2(z) - 2 * norm2(y)))


def carry(x: tuple[F, ...], y: tuple[F, ...], z: tuple[F, ...]) -> tuple[F, ...]:
    return tuple(a + c - 2 * b for a, b, c in zip(x, y, z))


def special(low: int, high: int) -> int:
    differing = [i for i, pair in enumerate(zip(CELLS[low], CELLS[high])) if pair[0] != pair[1]]
    assert len(differing) == 1
    j = differing[0]
    assert (CELLS[low][j], CELLS[high][j]) == (0, 5)
    return j


def residuals(j: int, value: F) -> tuple[F, ...]:
    out = [S] * 4
    out[j] = value
    assert all(F(0) < v < F(1) for v in out)
    return tuple(out)


def point(label: int, r: tuple[F, ...]) -> tuple[F, ...]:
    return tuple((F(digit) + residual) / Q for digit, residual in zip(CELLS[label], r))


def unit_carry(j: int, sign: int) -> tuple[F, ...]:
    out = [F(0)] * 4
    out[j] = F(sign)
    return tuple(out)


def rows(low: int, high: int, reverse: bool, t: F):
    """Return (A,B,B), (A,A,B), then expected (carry,rhs) for each.

    All residuals are strict interior for 0<t<1/3.  reverse=True means A is
    the high endpoint and B is the low endpoint.
    """
    assert F(0) < t < F(1, 3)
    j = special(low, high)
    r = lambda u: residuals(j, u)
    if not reverse:
        first = (point(low, r(t)), point(high, r(1 - t)), point(high, r(1 - 3 * t)))
        second = (point(low, r(3 * t)), point(low, r(t)), point(high, r(1 - t)))
        expected = ((unit_carry(j, -1), 108 - 24 * t),
                    (unit_carry(j, +1), -36 - 24 * t))
    else:
        first = (point(high, r(1 - t)), point(low, r(t)), point(low, r(3 * t)))
        second = (point(high, r(1 - 3 * t)), point(high, r(1 - t)), point(low, r(t)))
        expected = ((unit_carry(j, +1), -36 - 24 * t),
                    (unit_carry(j, -1), 108 - 24 * t))
    return first, second, expected


def test_geometry_and_orientations() -> None:
    assert len(CELLS) == len(set(CELLS)) == N
    assert len({v for pair in PAIRS for v in pair}) == 14
    for t in (F(1, 10), F(1, 4)):
        for low, high in PAIRS:
            for reverse in (False, True):
                first, second, expected = rows(low, high, reverse, t)
                for row, (wanted_carry, wanted_rhs) in zip((first, second), expected):
                    x, y, z = row
                    assert carry(x, y, z) == wanted_carry
                    assert rhs(x, y, z) == wanted_rhs
                assert expected[0][1] + expected[1][1] == 72 - 48 * t > 0


def cat(parts: list[tuple[F, ...]]) -> tuple[F, ...]:
    return tuple(v for part in parts for v in part)


def test_mixed_full_word_rows() -> None:
    """Tensor actual 4D witnesses into direct raw-norm word-level witnesses."""
    t = F(1, 10)
    for r in range(1, len(PAIRS) + 1):
        for orientation in product((False, True), repeat=r):
            blocks = [rows(PAIRS[i][0], PAIRS[i][1], orientation[i], t) for i in range(r)]
            for row_number in (0, 1):
                x = cat([block[row_number][0] for block in blocks])
                y = cat([block[row_number][1] for block in blocks])
                z = cat([block[row_number][2] for block in blocks])
                wanted_carry = cat([block[2][row_number][0] for block in blocks])
                wanted_rhs = sum((block[2][row_number][1] for block in blocks), F(0))
                assert carry(x, y, z) == wanted_carry
                assert rhs(x, y, z) == wanted_rhs
            total = sum((block[2][0][1] + block[2][1][1] for block in blocks), F(0))
            assert total == r * (72 - 48 * t) > 0

    # This algebra covers arbitrary word Hamming distance r and any mixture.
    for r in range(1, 41):
        for low_to_high in range(r + 1):
            high_to_low = r - low_to_high
            first = low_to_high * (108 - 24 * t) + high_to_low * (-36 - 24 * t)
            second = low_to_high * (-36 - 24 * t) + high_to_low * (108 - 24 * t)
            assert first + second == r * (72 - 48 * t) > 0


def test_whole_word_cancellation() -> None:
    """No additive/coordinate/edge form of h is assumed in this identity."""
    c: Counter[str] = Counter()
    # Row (A(t),B(t),B(3t)).
    c.update({"A_t": 1, "B_t": -2, "B_3t": 1})
    # Row (A(3t),A(t),B(t)).
    c.update({"A_3t": 1, "A_t": -2, "B_t": 1})
    assert c == Counter({"A_3t": 1, "B_3t": 1, "A_t": -1, "B_t": -1})
    # This is D(3t)-D(t), D(u)=h(A(u))+h(B(u)).


def telescope_rhs(steps: int, r: int, T: F = F(1, 4)) -> F:
    assert steps >= 1 and r >= 1 and F(0) < T < F(1, 3)
    direct = sum((r * (72 - 48 * T / (3 ** n)) for n in range(1, steps + 1)), F(0))
    closed = r * (72 * steps - 24 * T * (1 - F(1, 3 ** steps)))
    assert direct == closed
    return direct


def test_finite_telescope() -> None:
    for r in (1, 2, 7, 23):
        for steps in (1, 2, 9):
            assert telescope_rhs(steps, r) > 0
        for M in (F(0), F(1), F(1000)):
            # For T=1/4, r(72N-6)>4M is sufficient.
            steps = int((F(4) * M / r + 6) // 72 + 1)
            assert telescope_rhs(steps, r) > 4 * M
    # If |h|<=M along both full word boxes, the left telescope side is <=4M.


def quotient() -> tuple[int, ...]:
    kappa = [-1] * N
    for class_id, (low, high) in enumerate(PAIRS):
        kappa[low] = kappa[high] = class_id
    next_class = len(PAIRS)
    for label in range(N):
        if kappa[label] == -1:
            kappa[label] = next_class
            next_class += 1
    assert next_class == 110
    assert all(kappa[low] == kappa[high] for low, high in PAIRS)
    return tuple(kappa)


def test_gate() -> None:
    assert len(set(quotient())) == 110
    assert F(110) < GATE < F(111)
    for m in (1, 2, 5, 11):
        assert F(110 ** m) < GATE ** m


def expect_assertion(action) -> None:
    try:
        action()
    except AssertionError:
        return
    raise AssertionError("planted corruption was accepted")


def test_planted_failures() -> None:
    low, high = PAIRS[0]
    j = special(low, high)
    t = F(1, 10)

    def wrong_residual() -> None:
        x = point(low, residuals(j, t))
        y = point(high, residuals(j, t))  # Must be 1-t.
        z = point(high, residuals(j, 1 - 3 * t))
        assert carry(x, y, z) == unit_carry(j, -1)

    def wrong_row_order() -> None:
        first, _second, expected = rows(low, high, False, t)
        x, y, z = first
        assert carry(y, x, z) == expected[0][0]

    def geodesic_mutation() -> None:
        first, _second, expected = rows(low, high, False, t)
        x, y, z = first
        wrong = Q ** 2 * (geodesic_cost(x, z) - 2 * (norm2(x) + norm2(z) - 2 * norm2(y)))
        assert wrong == expected[0][1]

    def duplicate_pair() -> None:
        corrupt = PAIRS[:-1] + ((PAIRS[0][0], PAIRS[-1][1]),)
        assert len({v for pair in corrupt for v in pair}) == 14

    def wrong_gate() -> None:
        assert F(111) < GATE

    for action in (wrong_residual, wrong_row_order, geodesic_mutation, duplicate_pair, wrong_gate):
        expect_assertion(action)


def main() -> None:
    test_geometry_and_orientations()
    test_mixed_full_word_rows()
    test_whole_word_cancellation()
    test_finite_telescope()
    test_gate()
    test_planted_failures()
    print("PASS_SEVEN_PAIR_FULLWORD_BOUNDED_WALL")
    print("GEOMETRY_OK cells=117 pairs=7 classes=110 low_digit=0 high_digit=5")
    print("STRICT_ROWS_OK both_orientations R1/R2=(108-24t,-36-24t) sum=72-48t")
    print("FULLWORD_TENSOR_OK mixed_orientations direct_raw_norm_and_whole_h_cancellation")
    print("FINITE_TELESCOPE_OK D(T)-D(T/3^N)>=r[72N-24T(1-3^-N)]")
    print("GATE_OK 110<441/4<111")
    print("PLANTED_FAILURES_REJECTED")


if __name__ == "__main__":
    main()

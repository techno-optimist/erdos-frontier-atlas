#!/usr/bin/env python3
"""Independent seven-pair strict-dilation wall for full-cell word languages.

Seven disjoint q=6 cell pairs differ only by a 0/5 digit in one coordinate.
For any two decoded words in the same 110-class quotient fibre, strict
interior midpoint rows give

    D(3t)-D(t) >= k*(72-48t),  0<t<1/3,

where k is the number of differing blocks.  A finite telescope contradicts
boundedness of an arbitrary residual-dependent physical potential.
"""
from __future__ import annotations

from fractions import Fraction as F
import sys

Q = 6
N = 117
GATE = F(441, 4)
S0 = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
      (5, 0), (5, 1), (5, 2))
OFFSETS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
           (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
CELLS = tuple((a, b, (a + x) % Q, (b + y) % Q)
              for a, b in S0 for x, y in OFFSETS)

# In each ordered pair the first cell has active digit 0 and the second 5.
PAIRS = ((25, 24), (37, 36), (41, 40), (47, 46),
         (77, 76), (79, 78), (84, 86))

# Polynomials a+b*t+c*t^2 with exact rational coefficients.
Poly = tuple[F, F, F]


def poly(a=0, b=0, c=0) -> Poly:
    return F(a), F(b), F(c)


def add(x: Poly, y: Poly) -> Poly:
    return tuple(a + b for a, b in zip(x, y))  # type: ignore[return-value]


def neg(x: Poly) -> Poly:
    return tuple(-a for a in x)  # type: ignore[return-value]


def sub(x: Poly, y: Poly) -> Poly:
    return add(x, neg(y))


def scale(c: F | int, x: Poly) -> Poly:
    return tuple(F(c) * a for a in x)  # type: ignore[return-value]


def mul(x: Poly, y: Poly) -> Poly:
    out = [F(0), F(0), F(0), F(0), F(0)]
    for i, a in enumerate(x):
        for j, b in enumerate(y):
            out[i + j] += a * b
    assert out[3:] == [0, 0]
    return tuple(out[:3])  # type: ignore[return-value]


def substitute_scale(x: Poly, factor: int) -> Poly:
    return x[0], factor * x[1], factor * factor * x[2]


def evaluate(x: Poly, t: F) -> F:
    return x[0] + x[1] * t + x[2] * t * t


def midpoint_defect(x: Poly, y: Poly, z: Poly) -> Poly:
    return sub(add(x, z), scale(2, y))


def correction_rhs(x: Poly, y: Poly, z: Poly) -> Poly:
    # q^2-scaled RHS after F=2||.||^2+h/36 is substituted:
    # 36*((x-z)^2 - 2*x^2 - 2*z^2 + 4*y^2).
    value = add(mul(sub(x, z), sub(x, z)),
                add(scale(-2, mul(x, x)),
                    add(scale(-2, mul(z, z)), scale(4, mul(y, y)))))
    return scale(36, value)


LOW_T = poly(0, F(1, 6))
LOW_3T = poly(0, F(1, 2))
HIGH_1_T = poly(1, F(-1, 6))
HIGH_1_3T = poly(1, F(-1, 2))


def check_scalar_templates() -> None:
    # Forward rows: (low,high,high) and (low,low,high).
    assert midpoint_defect(LOW_T, HIGH_1_T, HIGH_1_3T) == poly(-1)
    assert correction_rhs(LOW_T, HIGH_1_T, HIGH_1_3T) == poly(108, -24)
    assert midpoint_defect(LOW_3T, LOW_T, HIGH_1_T) == poly(1)
    assert correction_rhs(LOW_3T, LOW_T, HIGH_1_T) == poly(-36, -24)

    # Reversing word orientation swaps endpoints and preserves the RHS.
    assert midpoint_defect(HIGH_1_T, LOW_T, LOW_3T) == poly(1)
    assert correction_rhs(HIGH_1_T, LOW_T, LOW_3T) == poly(-36, -24)
    assert midpoint_defect(HIGH_1_3T, HIGH_1_T, LOW_T) == poly(-1)
    assert correction_rhs(HIGH_1_3T, HIGH_1_T, LOW_T) == poly(108, -24)

    assert add(poly(108, -24), poly(-36, -24)) == poly(72, -48)
    for t in (F(1, 100), F(1, 12), F(1, 4), F(99, 300)):
        assert 0 < t < F(1, 3)
        residuals = (t, 3 * t, 1 - t, 1 - 3 * t)
        assert all(0 < r < 1 for r in residuals)


def active_coordinate(low: int, high: int) -> int:
    differences = [j for j in range(4) if CELLS[low][j] != CELLS[high][j]]
    assert len(differences) == 1
    j = differences[0]
    assert CELLS[low][j] == 0 and CELLS[high][j] == 5
    assert all(CELLS[low][i] == CELLS[high][i] for i in range(4) if i != j)
    return j


def build_quotient() -> tuple[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    flat = [u for pair in PAIRS for u in pair]
    assert len(flat) == len(set(flat)) == 14
    groups: list[tuple[int, ...]] = list(PAIRS)
    used = set(flat)
    groups.extend((u,) for u in range(N) if u not in used)
    assert len(groups) == 110
    quotient = [-1] * N
    for group_id, group in enumerate(groups):
        for u in group:
            assert quotient[u] == -1
            quotient[u] = group_id
    assert all(x >= 0 for x in quotient)
    return tuple(quotient), tuple(groups)


def actual_coordinate(digit: int, residual: Poly) -> Poly:
    return add(poly(F(digit, Q)), scale(F(1, Q), residual))


def word_point(word: tuple[int, ...], parameter_scale: int,
               low_by_pair: dict[int, tuple[int, int, int]],
               fixed_residual: F = F(1, 2)) -> tuple[Poly, ...]:
    """Build X(t) or Y(t): active residual is t for low, 1-t for high."""
    coordinates: list[Poly] = []
    for cell in word:
        pair_info = low_by_pair.get(cell)
        for j, digit in enumerate(CELLS[cell]):
            if pair_info is None or j != pair_info[2]:
                residual = poly(fixed_residual)
            elif cell == pair_info[0]:
                residual = poly(0, parameter_scale)
            else:
                residual = poly(1, -parameter_scale)
            coordinates.append(actual_coordinate(digit, residual))
    return tuple(coordinates)


def vector_rhs(x: tuple[Poly, ...], y: tuple[Poly, ...],
               z: tuple[Poly, ...]) -> Poly:
    assert len(x) == len(y) == len(z)
    total = poly()
    for a, b, c in zip(x, y, z):
        defect = midpoint_defect(a, b, c)
        assert defect[1:] == (0, 0) and defect[0].denominator == 1
        total = add(total, correction_rhs(a, b, c))
    return total


def check_multi_block_template() -> None:
    pair_info: dict[int, tuple[int, int, int]] = {}
    for low, high in PAIRS:
        j = active_coordinate(low, high)
        pair_info[low] = pair_info[high] = (low, high, j)

    # Seven differing blocks, alternating word orientation, plus two equal
    # blocks.  This exercises simultaneous rows rather than adding unrelated
    # one-block inequalities.
    left = tuple(low if i % 2 == 0 else high
                 for i, (low, high) in enumerate(PAIRS)) + (0, 116)
    right = tuple(high if i % 2 == 0 else low
                  for i, (low, high) in enumerate(PAIRS)) + (0, 116)
    X_t = word_point(left, 1, pair_info)
    X_3t = word_point(left, 3, pair_info)
    Y_t = word_point(right, 1, pair_info)
    Y_3t = word_point(right, 3, pair_info)

    row_one = vector_rhs(X_t, Y_t, Y_3t)       # labels (left,right,right)
    row_two = vector_rhs(X_3t, X_t, Y_t)       # labels (left,left,right)
    assert row_one == poly(324, -168)           # 4*108 + 3*(-36), -7*24
    assert row_two == poly(180, -168)           # 4*(-36) + 3*108, -7*24
    assert add(row_one, row_two) == poly(7 * 72, -7 * 48)


def telescope_rhs(k: int, N_steps: int) -> F:
    return 72 * k * N_steps - 6 * k * (1 - F(1, 3 ** N_steps))


def check_telescope() -> None:
    for k in (1, 3, 7):
        for steps in (1, 2, 9):
            exact = telescope_rhs(k, steps)
            direct = sum((k * (72 - 12 / F(3 ** j))
                          for j in range(1, steps + 1)), F(0))
            assert exact == direct
        for M in (F(0), F(1), F(10**4), F(17, 3)):
            steps = (int((4 * M + 6 * k) // (72 * k)) + 1)
            assert telescope_rhs(k, steps) > 4 * M


def planted_failures(quotient: tuple[int, ...]) -> None:
    split = list(quotient)
    split[PAIRS[0][1]] = 110
    try:
        assert len(set(split)) == 110
    except AssertionError:
        pass
    else:
        raise AssertionError("split strict pair was accepted")

    duplicate = PAIRS[:-1] + ((PAIRS[0][0], PAIRS[-1][1]),)
    flat = [u for pair in duplicate for u in pair]
    try:
        assert len(flat) == len(set(flat))
    except AssertionError:
        pass
    else:
        raise AssertionError("overlapping pair family was accepted")

    wrong_high = poly(F(5, 6), F(-1, 6))  # digit 4 with residual 1-t
    try:
        assert midpoint_defect(LOW_T, wrong_high, substitute_scale(wrong_high, 3)) == poly(-1)
    except AssertionError:
        pass
    else:
        raise AssertionError("wrong 0/4 digit pair was accepted")


def main() -> None:
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ["--self-test"]
    assert len(CELLS) == len(set(CELLS)) == N
    coordinates = [active_coordinate(*pair) for pair in PAIRS]
    assert coordinates == [3, 3, 3, 3, 3, 2, 3]
    check_scalar_templates()
    quotient, groups = build_quotient()
    check_multi_block_template()
    check_telescope()
    assert len(groups) == 110 and F(110) < GATE < F(117)
    planted_failures(quotient)
    print("PASS_INDEPENDENT_SEVEN_PAIR_DILATION_WORD_WALL")
    print(f"PAIR_GEOMETRY_OK pairs={len(PAIRS)} active_coordinates={coordinates}")
    print("STRICT_ROWS_OK forward_reverse sums=72-48t for 0<t<1/3")
    print("MULTIBLOCK_OK D(3t)-D(t)>=k*(72-48t) orientations=mixed")
    print("FINITE_TELESCOPE_OK rhs=72*k*N-6*k*(1-3^-N) bounded_h=impossible")
    print("QUOTIENT_GATE_OK classes=110<441/4 full_word_bound=|L_m|<=110^m")
    print("PLANTED_FAILURES_REJECTED")


if __name__ == "__main__":
    main()

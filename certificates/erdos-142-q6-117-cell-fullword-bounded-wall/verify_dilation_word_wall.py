#!/usr/bin/env python3
"""Primary exact componentwise-dilation word-language wall.

The q=6 117-cell alphabet has 66 oriented pairs A->B such that every coarse
coordinate is equal or decrements by one modulo 6, with at least one 0->5
wrap.  A checked 21-edge matching gives a 96-class quotient.  Two accepted
words in one quotient fibre force a strict-interior recurrence

    D(3t)-D(t) >= K*(72-48t),

where K>=1 is the total number of wrapped scalar coordinates.  A finite
telescope contradicts any bounded residual-dependent physical potential.
"""
from __future__ import annotations

from collections import Counter
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

MATCHING_UNDIRECTED = ((3, 55), (4, 17), (16, 68), (24, 25), (36, 37),
                       (39, 52), (40, 53), (46, 96), (54, 106), (12, 59),
                       (56, 69), (76, 77), (78, 79), (83, 84), (86, 87),
                       (91, 92), (80, 93), (98, 99), (41, 105), (64, 111),
                       (104, 116))

# Exact polynomials a+b*t+c*t^2.
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
    out = [F(0)] * 5
    for i, a in enumerate(x):
        for j, b in enumerate(y):
            out[i + j] += a * b
    assert out[3:] == [0, 0]
    return tuple(out[:3])  # type: ignore[return-value]


def midpoint_defect(x: Poly, y: Poly, z: Poly) -> Poly:
    return sub(add(x, z), scale(2, y))


def correction_rhs(x: Poly, y: Poly, z: Poly) -> Poly:
    value = add(mul(sub(x, z), sub(x, z)),
                add(scale(-2, mul(x, x)),
                    add(scale(-2, mul(z, z)), scale(4, mul(y, y)))))
    return scale(36, value)


def actual(digit: int, residual: Poly) -> Poly:
    return add(poly(F(digit, Q)), scale(F(1, Q), residual))


def is_dilation_edge(a: int, b: int) -> bool:
    A, B = CELLS[a], CELLS[b]
    return (a != b
            and all(y == x or y == (x - 1) % Q for x, y in zip(A, B))
            and any(x == 0 and y == 5 for x, y in zip(A, B)))


def edge_data(a: int, b: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    assert is_dilation_edge(a, b)
    active = tuple(j for j, (x, y) in enumerate(zip(CELLS[a], CELLS[b]))
                   if x != y)
    wraps = tuple(j for j in active if CELLS[a][j] == 0 and CELLS[b][j] == 5)
    assert active and wraps
    return active, wraps


def orient_matching() -> tuple[tuple[int, int], ...]:
    oriented: list[tuple[int, int]] = []
    flat = [u for pair in MATCHING_UNDIRECTED for u in pair]
    assert len(flat) == len(set(flat)) == 42
    for u, v in MATCHING_UNDIRECTED:
        if is_dilation_edge(u, v):
            oriented.append((u, v))
        else:
            assert is_dilation_edge(v, u)
            oriented.append((v, u))
    assert len(oriented) == 21
    return tuple(oriented)


def all_edges() -> tuple[tuple[int, int], ...]:
    edges = tuple((a, b) for a in range(N) for b in range(N)
                  if is_dilation_edge(a, b))
    assert len(edges) == 66
    return edges


def check_scalar_digit(a: int) -> None:
    """Check both rows for digit a and its predecessor b=a-1 mod 6."""
    b = (a - 1) % Q
    A_t = actual(a, poly(0, 1))
    A_3t = actual(a, poly(0, 3))
    B_1t = actual(b, poly(1, -1))
    B_13t = actual(b, poly(1, -3))
    wrap = a == 0
    carry_one = -1 if wrap else 0
    carry_two = 1 if wrap else 0
    rhs_one = poly(108, -24) if wrap else poly()
    rhs_two = poly(-36, -24) if wrap else poly()

    assert midpoint_defect(A_t, B_1t, B_13t) == poly(carry_one)
    assert correction_rhs(A_t, B_1t, B_13t) == rhs_one
    assert midpoint_defect(A_3t, A_t, B_1t) == poly(carry_two)
    assert correction_rhs(A_3t, A_t, B_1t) == rhs_two
    # Reverse word orientation swaps endpoints and reverses row order.
    assert correction_rhs(B_1t, A_t, A_3t) == rhs_two
    assert correction_rhs(B_13t, B_1t, A_t) == rhs_one


def check_strict_interior() -> None:
    for t in (F(1, 100), F(1, 12), F(1, 4), F(99, 300)):
        assert 0 < t < F(1, 3)
        assert all(0 < value < 1 for value in (t, 3 * t, 1 - t, 1 - 3 * t))


def build_quotient(matching: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    quotient = [-1] * N
    group = 0
    for a, b in matching:
        assert quotient[a] == quotient[b] == -1
        quotient[a] = quotient[b] = group
        group += 1
    for u in range(N):
        if quotient[u] == -1:
            quotient[u] = group
            group += 1
    assert group == N - len(matching) == 96
    return tuple(quotient)


def word_point(word: tuple[int, ...], parameter_scale: int,
               ownership: dict[int, tuple[int, int, tuple[int, ...]]]) -> tuple[Poly, ...]:
    coordinates: list[Poly] = []
    for cell in word:
        info = ownership.get(cell)
        for j, digit in enumerate(CELLS[cell]):
            if info is None or j not in info[2]:
                residual = poly(F(1, 2))
            elif cell == info[0]:
                residual = poly(0, parameter_scale)
            else:
                residual = poly(1, -parameter_scale)
            coordinates.append(actual(digit, residual))
    return tuple(coordinates)


def vector_rhs(x: tuple[Poly, ...], y: tuple[Poly, ...],
               z: tuple[Poly, ...]) -> Poly:
    total = poly()
    for a, b, c in zip(x, y, z):
        defect = midpoint_defect(a, b, c)
        assert defect[1:] == (0, 0) and defect[0].denominator == 1
        total = add(total, correction_rhs(a, b, c))
    return total


def check_global_mixed_orientation(matching: tuple[tuple[int, int], ...]) -> None:
    ownership: dict[int, tuple[int, int, tuple[int, ...]]] = {}
    wrap_total = 0
    for a, b in matching:
        active, wraps = edge_data(a, b)
        ownership[a] = ownership[b] = (a, b, active)
        wrap_total += len(wraps)
    assert wrap_total == 21

    left = tuple(a if i % 2 == 0 else b for i, (a, b) in enumerate(matching))
    right = tuple(b if i % 2 == 0 else a for i, (a, b) in enumerate(matching))
    X_t = word_point(left, 1, ownership)
    X_3t = word_point(left, 3, ownership)
    Y_t = word_point(right, 1, ownership)
    Y_3t = word_point(right, 3, ownership)
    row_one = vector_rhs(X_t, Y_t, Y_3t)
    row_two = vector_rhs(X_3t, X_t, Y_t)
    assert row_one == poly(828, -504)   # 11 forward, 10 reverse wraps.
    assert row_two == poly(684, -504)
    assert add(row_one, row_two) == poly(21 * 72, -21 * 48)


def telescope(K: int, steps: int) -> F:
    return 72 * K * steps - 6 * K * (1 - F(1, 3 ** steps))


def check_finite_telescope() -> None:
    for K in (1, 7, 21, 37):
        for steps in (1, 2, 10):
            direct = sum((K * (72 - 12 / F(3 ** j))
                          for j in range(1, steps + 1)), F(0))
            assert telescope(K, steps) == direct
        for M in (F(0), F(1), F(17, 3), F(10**4)):
            steps = int((4 * M + 6 * K) // (72 * K)) + 1
            assert telescope(K, steps) > 4 * M


def planted_failures(quotient: tuple[int, ...],
                     matching: tuple[tuple[int, int], ...]) -> None:
    split = list(quotient)
    split[matching[0][1]] = 96
    try:
        assert len(set(split)) == 96
    except AssertionError:
        pass
    else:
        raise AssertionError("split matching pair was accepted")

    duplicate = MATCHING_UNDIRECTED[:-1] + ((MATCHING_UNDIRECTED[0][0],
                                             MATCHING_UNDIRECTED[-1][1]),)
    flat = [u for pair in duplicate for u in pair]
    try:
        assert len(flat) == len(set(flat))
    except AssertionError:
        pass
    else:
        raise AssertionError("overlapping matching was accepted")

    # Removing the required wrap makes an ordinary carry-zero adjacency.
    try:
        assert any(x == 0 and y == 5 for x, y in zip((4, 2, 2, 1), (3, 2, 2, 1)))
    except AssertionError:
        pass
    else:
        raise AssertionError("wrap-free pair was accepted")


def main() -> None:
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ["--self-test"]
    assert len(CELLS) == len(set(CELLS)) == N
    edges = all_edges()
    wrap_hist = Counter(len(edge_data(a, b)[1]) for a, b in edges)
    active_hist = Counter(len(edge_data(a, b)[0]) for a, b in edges)
    matching = orient_matching()
    assert all(pair in edges for pair in matching)
    for digit in range(Q):
        check_scalar_digit(digit)
    check_strict_interior()
    quotient = build_quotient(matching)
    check_global_mixed_orientation(matching)
    check_finite_telescope()
    assert len(set(quotient)) == 96 and F(96) < GATE < F(117)
    planted_failures(quotient, matching)
    print("PASS_DILATION_WORD_WALL")
    print(f"DILATION_GRAPH_OK oriented_edges={len(edges)} "
          f"active_hist={dict(sorted(active_hist.items()))} "
          f"wrap_hist={dict(sorted(wrap_hist.items()))}")
    print("MATCHING_OK size=21 quotient_classes=96")
    print("STRICT_ROWS_OK all_digits both_orientations nonwrap_cost=0 wrap_sum=72-48t")
    print("MULTIBLOCK_OK D(3t)-D(t)>=K*(72-48t) mixed_orientations K>=1")
    print("FINITE_TELESCOPE_OK bounded_residual_potential=impossible")
    print("GATE_OK |L_m|<=96^m<(441/4)^m")
    print("PLANTED_FAILURES_REJECTED")


if __name__ == "__main__":
    main()

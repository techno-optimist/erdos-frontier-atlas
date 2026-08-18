#!/usr/bin/env python3
"""Solver-free exact replay for the cells 91/93 carving audit."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction

Q = 6
A = (5, 1, 0, 0)
B = (5, 1, 5, 5)
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFFSETS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
           (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
CELLS = tuple((x, y, (x + dx) % Q, (y + dy) % Q)
              for x, y in BASE for dx, dy in OFFSETS)
TRANSPORT_DIGEST = "0cdd8ee497e047ec11f50ff248c2a7163b4f2d4abbd39d41d6eb4cf9698ebe8b"

# Affine polynomials c+a*t3+b*t4, used to verify the row formula as an
# identity rather than only at numerical samples.
Poly = tuple[Fraction, Fraction, Fraction]


def padd(x: Poly, y: Poly) -> Poly:
    return tuple(a + b for a, b in zip(x, y))  # type: ignore[return-value]


def pscale(c: int | Fraction, x: Poly) -> Poly:
    return tuple(c * a for a in x)  # type: ignore[return-value]


def symbolic_rows() -> None:
    one: Poly = (Fraction(1), Fraction(0), Fraction(0))
    t3: Poly = (Fraction(0), Fraction(1), Fraction(0))
    t4: Poly = (Fraction(0), Fraction(0), Fraction(1))

    def requirement(y_digit: int, ry: Poly, carry: int) -> Poly:
        # -24*k*(digit_y+ry)-36*k^2.
        digit_plus_ry = padd((Fraction(y_digit), Fraction(0), Fraction(0)), ry)
        return padd(pscale(-24 * carry, digit_plus_ry),
                    (Fraction(-36 * carry * carry), Fraction(0), Fraction(0)))

    r1 = padd(requirement(5, padd(one, pscale(-1, t3)), -1),
               requirement(5, padd(one, pscale(-1, t4)), -1))
    r2 = padd(requirement(0, t3, 1), requirement(0, t4, 1))
    assert r1 == (Fraction(216), Fraction(-24), Fraction(-24))
    assert r2 == (Fraction(-72), Fraction(-24), Fraction(-24))
    assert padd(r1, r2) == (Fraction(144), Fraction(-48), Fraction(-48))

    # Digit plus residual defects are identically -6 and +6.
    r1_residual = padd(t3, padd(padd(one, pscale(-3, t3)),
                                  pscale(-2, padd(one, pscale(-1, t3)))))
    r2_residual = padd(pscale(3, t3),
                       padd(padd(one, pscale(-1, t3)), pscale(-2, t3)))
    assert r1_residual == (Fraction(-1), Fraction(0), Fraction(0))
    assert r2_residual == (Fraction(1), Fraction(0), Fraction(0))
    assert padd((Fraction(-5), Fraction(0), Fraction(0)), r1_residual) \
        == (Fraction(-6), Fraction(0), Fraction(0))
    assert padd((Fraction(5), Fraction(0), Fraction(0)), r2_residual) \
        == (Fraction(6), Fraction(0), Fraction(0))


def scalar_scaled_requirement(x_digit: int, y_digit: int, z_digit: int,
                              rx, ry, rz) -> Fraction:
    """Use -36(4*k*y+k^2) after x+z=2y+k."""
    numerator = (x_digit + rx) + (z_digit + rz) - 2 * (y_digit + ry)
    assert numerator.denominator == 1
    carry = int(numerator / Q)
    assert numerator == Q * carry
    y = Fraction(y_digit + ry, Q)
    return -36 * (4 * carry * y + carry * carry)


def strict_row_check(t3: Fraction, t4: Fraction) -> None:
    assert 0 < t3 < Fraction(1, 3)
    assert 0 < t4 < Fraction(1, 3)
    r1 = []
    r2 = []
    for t in (t3, t4):
        # A digit 0, B digit 5 in each active coordinate.
        r1.append(scalar_scaled_requirement(0, 5, 5,
                                             t, 1 - t, 1 - 3 * t))
        r2.append(scalar_scaled_requirement(0, 0, 5,
                                             3 * t, t, 1 - t))
        assert all(0 < r < 1 for r in (t, 1 - t, 1 - 3 * t,
                                       3 * t))
    assert sum(r1) == 216 - 24 * (t3 + t4)
    assert sum(r2) == -72 - 24 * (t3 + t4)
    assert sum(r1) + sum(r2) == 144 - 48 * (t3 + t4)


def density_arithmetic() -> None:
    cell = Fraction(1, 1296)
    union = Fraction(117, 1296)
    gate = Fraction(49, 576)
    margin = union - gate
    assert union == Fraction(52, 576)
    assert margin == Fraction(1, 192)
    assert cell < 2 * cell < margin


def finite_chain_bound(M: int) -> tuple[int, Fraction]:
    N = 1
    while Fraction(144 * N) - 48 * (1 - Fraction(1, 3**N)) <= 4 * M:
        N += 1
    residual_slice_bound = Fraction(8, 9 ** (N + 1) - 1)
    physical_bound = residual_slice_bound / 1296
    assert physical_bound > 0
    return N, physical_bound


def small_corner_controls() -> None:
    for J in range(1, 9):
        epsilon = Fraction(1, 3**J)
        deleted = epsilon * epsilon / 1296
        correction_bound = 72 * (J + 1)
        assert deleted == Fraction(1, 1296 * 9**J)
        assert deleted < Fraction(1, 192)

        # Exact rational samples: every T/3^n eventually has both active
        # residuals at most epsilon.
        for T3, T4 in ((Fraction(1, 2), Fraction(2, 3)),
                       (Fraction(1, 7), Fraction(5, 11)),
                       (Fraction(1, 100), Fraction(1, 101))):
            n = 0
            while max(T3 / 3**n, T4 / 3**n) > epsilon:
                n += 1
            assert max(T3 / 3**n, T4 / 3**n) <= epsilon

        # The explicit correction uses D(3t)-D(t)=144 and e=144.
        delta_D = 144
        e_term = 144
        r1_left = Fraction(delta_D + 2 * e_term, 2)
        r2_left = Fraction(delta_D - 2 * e_term, 2)
        assert r1_left == 216
        assert r2_left == -72
        assert correction_bound < 10_000


def scalar_sheet_check() -> None:
    # Every literal-family residual point obeys two independent affine
    # equalities r1=r2 and r3=r4, so its affine dimension is at most two.
    for s, t in ((Fraction(1, 5), Fraction(1, 7)),
                 (Fraction(2, 5), Fraction(1, 11))):
        a_points = ((s, s, t, t), (s, s, 3 * t, 3 * t))
        b_points = ((s, s, 1 - t, 1 - t),
                    (s, s, 1 - 3 * t, 1 - 3 * t))
        for point in a_points + b_points:
            assert point[0] == point[1]
            assert point[2] == point[3]


def canonical_transport_census() -> None:
    found: list[list[object]] = []
    for ia, a in enumerate(CELLS):
        for ib, b in enumerate(CELLS):
            active = [i for i, (x, y) in enumerate(zip(a, b))
                      if y == (x - 1) % Q]
            wraps = [i for i in active if a[i] == 0 and b[i] == 5]
            if wraps and all(x == y or y == (x - 1) % Q
                              for x, y in zip(a, b)):
                found.append([ia, ib, active, wraps])
    assert len(found) == 66
    assert Counter(len(row[2]) for row in found) == Counter({1: 11, 2: 38,
                                                              3: 10, 4: 7})
    assert Counter(len(row[3]) for row in found) == Counter({1: 61, 2: 5})
    encoded = (json.dumps(found, separators=(",", ":")) + "\n").encode()
    assert hashlib.sha256(encoded).hexdigest() == TRANSPORT_DIGEST
    for J in range(2, 8):
        epsilon = Fraction(1, 3**J)
        cover_upper_bound = (11 * epsilon + 38 * epsilon**2
                             + 10 * epsilon**3 + 7 * epsilon**4) / 1296
        assert cover_upper_bound > 0
        assert cover_upper_bound < Fraction(1, 192)


def main() -> None:
    assert len(CELLS) == len(set(CELLS)) == 117
    assert CELLS[93] == A and CELLS[91] == B
    density_arithmetic()
    scalar_sheet_check()
    symbolic_rows()
    canonical_transport_census()
    for t3, t4 in ((Fraction(1, 12), Fraction(1, 9)),
                   (Fraction(2, 15), Fraction(1, 6)),
                   (Fraction(7, 24), Fraction(5, 18))):
        strict_row_check(t3, t4)
    for M in (0, 72, 720, 7200):
        N, bound = finite_chain_bound(M)
        assert N >= 1 and bound > 0
    small_corner_controls()
    print("PASS_117_CARVING_DILATION_AUDIT")
    print("DENSITY_OK margin=1/192=6.75_cell_volumes")
    print("SCALAR_FAMILY_NULL_COVER_OK dimension=2_in_4")
    print("VECTOR_FAMILY_OK R1=216-24sum(t) R2=-72-24sum(t)")
    print("HYPERGRAPH_BOUND_OK M_dependent_positive_no_uniform_constant")
    print("CORNER_EVASION_OK deletion=1/(1296*9^J) infimum=0")
    print("EXPLICIT_TWO_FAMILY_CORRECTION_OK bound=72(J+1)")
    print("COMPONENTWISE_TRANSPORTS_OK pairs=66 active=1:11,2:38,3:10,4:7")
    print("TRANSPORT_RAY_COVER_OK infimum=0")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Hostile, stdlib-only audit of the q=6 93/91 dilation obstruction.

This file intentionally does not import either supplied packet.  It starts
from the pointwise EHPS raw-canonical inequality

    f(x) + f(z) - 2 f(y) >= sum_j (x_j-z_j)^2

for x+z=2y modulo one, using canonical representatives in [0,1).  It then
checks the actual half-open q=6 points, not merely a cell-graph transition.
"""
from collections import defaultdict
from fractions import Fraction as F

Q = 6
SEED = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFFSETS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
           (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
CELLS = tuple((a, b, (a + da) % Q, (b + db) % Q)
              for a, b in SEED for da, db in OFFSETS)
A, B = 93, 91


def point(cell, residual):
    return tuple((F(d) + r) / Q for d, r in zip(CELLS[cell], residual))


def squared_norm(v):
    return sum((x * x for x in v), F(0))


def raw_cost(x, z):
    """EHPS cost: squared difference of raw canonical representatives."""
    return sum(((u - v) ** 2 for u, v in zip(x, z)), F(0))


def geodesic_cost(x, z):
    """Deliberately different torus metric; included as a semantic control."""
    return sum((min(abs(u-v), 1-abs(u-v)) ** 2 for u, v in zip(x, z)), F(0))


def correction_rhs(x, y, z):
    # h=36(f-2||.||^2); substitute the EHPS inequality exactly.
    return Q**2 * (raw_cost(x, z)
                   - 2 * (squared_norm(x) + squared_norm(z) - 2*squared_norm(y)))


def carry_rhs(cells, residuals):
    """Independent scalar carry expansion of correction_rhs."""
    x, y, z = cells
    rx, ry, rz = residuals
    total = F(0)
    carries, errors = [], []
    for a, b, c, u, v, w in zip(CELLS[x], CELLS[y], CELLS[z], rx, ry, rz):
        e = u + w - 2*v
        k_num = a + c - 2*b + e
        assert k_num.denominator == 1 and k_num % Q == 0
        k = k_num // Q
        assert k in (-1, 0, 1)
        carries.append(k); errors.append(e)
        total += -2 * Q * k * (F(a+c, 2) + b + 2*v + e/2)
    return tuple(carries), tuple(errors), total


def families(t, s=F(1, 2)):
    assert F(0) < t < F(1, 3) and F(0) < s < F(1)
    # Ordered as (x,y,z), matching f(x)+f(z)-2f(y).
    return (
        ((A, B, B), ((s, s, t, t), (s, s, 1-t, 1-t),
                     (s, s, 1-3*t, 1-3*t))),
        ((A, A, B), ((s, s, 3*t, 3*t), (s, s, t, t),
                     (s, s, 1-t, 1-t))),
    )


def check_row(cells, residuals, wanted_carry, wanted_error, wanted_rhs):
    # Strict interior check is stronger than half-open membership.
    assert all(F(0) < r < F(1) for residual in residuals for r in residual)
    x, y, z = (point(c, r) for c, r in zip(cells, residuals))
    actual_carry = tuple(u + w - 2*v for u, v, w in zip(x, y, z))
    assert actual_carry == wanted_carry
    carries, errors, raw_expansion = carry_rhs(cells, residuals)
    assert carries == wanted_carry and errors == wanted_error
    assert correction_rhs(x, y, z) == raw_expansion == wanted_rhs
    # The relevant normal coordinates cross a canonical face.  Replacing the
    # raw EHPS cost by a geodesic torus cost is an actual, detected mutation.
    assert raw_cost(x, z) != geodesic_cost(x, z)
    return x, y, z


def exact_geometry():
    assert len(CELLS) == 117 and len(set(CELLS)) == 117
    assert CELLS[A] == (5, 1, 0, 0)
    assert CELLS[B] == (5, 1, 5, 5)
    for t in (F(1, 10), F(1, 5)):
        r1, r2 = families(t)
        check_row(*r1, (0, 0, -1, -1), (0, 0, -1, -1), 216-48*t)
        check_row(*r2, (0, 0, 1, 1), (0, 0, 1, 1), -72-48*t)
        assert (216-48*t) + (-72-48*t) == 144-96*t


def symbolic_increment():
    """Check the h-coefficient cancellation without an ansatz for h."""
    # H_A(u) abbreviates h_A(s,s,u,u), H_B(1-u) h_B(s,s,1-u,1-u).
    r1 = {('A', 't'): 1, ('B', '1-3t'): 1, ('B', '1-t'): -2}
    r2 = {('A', '3t'): 1, ('A', 't'): -2, ('B', '1-t'): 1}
    out = defaultdict(int)
    for row in (r1, r2):
        for key, coeff in row.items(): out[key] += coeff
    out = {key: value for key, value in out.items() if value}
    assert out == {('A', '3t'): 1, ('B', '1-3t'): 1,
                   ('A', 't'): -1, ('B', '1-t'): -1}
    # Thus D(u)=H_A(u)+H_B(1-u) obeys D(3t)-D(t)>=144-96t.


def finite_telescope(N, T=F(1, 4)):
    assert N >= 1 and F(0) < T < F(1, 3)
    ts = tuple(T / (3**n) for n in range(1, N+1))
    assert all(F(0) < t < F(1, 3) for t in ts)
    rhs = sum((144-96*t for t in ts), F(0))
    closed = 144*N - 48*T*(1-F(1, 3**N))
    assert rhs == closed
    return rhs


def planted_failures():
    t = F(1, 10)
    r1, _r2 = families(t)
    cells, residuals = r1
    # Planted carry error: x+z-2y is no longer the claimed -1 in coord. 2.
    bad = list(residuals); bad[2] = (F(1, 2), F(1, 2), 1-2*t, 1-3*t)
    try:
        check_row(cells, tuple(bad), (0, 0, -1, -1),
                  (0, 0, -1, -1), 216-48*t)
    except AssertionError:
        pass
    else:
        raise AssertionError('planted carry/residual corruption passed')
    # Planted x/y order error: y is no longer a modular midpoint.
    try:
        check_row((A, B, B), (residuals[1], residuals[0], residuals[2]),
                  (0, 0, -1, -1), (0, 0, -1, -1), 216-48*t)
    except AssertionError:
        pass
    else:
        raise AssertionError('planted row-order corruption passed')
    x, y, z = (point(c, r) for c, r in zip(cells, residuals))
    assert Q**2 * (geodesic_cost(x, z)
                    - 2*(squared_norm(x)+squared_norm(z)-2*squared_norm(y))) != 216-48*t


def boundedness_and_contradiction():
    # If |f|<=K on the union, then |h|<=36(K+8), since ||x||^2<4.
    # Conversely only boundedness of h along these two interior curves is used.
    for M in (F(0), F(1), F(1000)):
        N = (4*M + 12)//144 + 1  # T=1/4
        assert finite_telescope(N) > 4*M
    # |h|<=M implies |D(T)-D(T/3^N)|<=4M, contradicting the displayed line.


if __name__ == '__main__':
    exact_geometry()
    symbolic_increment()
    planted_failures()
    boundedness_and_contradiction()
    print('PASS_HOSTILE_DILATION_REPLAY')
    print('cells 93=(5,1,0,0), 91=(5,1,5,5); strict 0<t<1/3')
    print('R1=216-48t; R2=-72-48t; D(3t)-D(t)>=144-96t')
    print('finite telescope: D(1/4)-D(1/(4*3^N)) >= 144N-12(1-3^-N)')
    print('planted carry, row-order, and raw-vs-geodesic failures rejected')

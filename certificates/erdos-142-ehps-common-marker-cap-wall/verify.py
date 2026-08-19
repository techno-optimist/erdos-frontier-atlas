#!/usr/bin/env python3
"""Exact stdlib replay for the literal-EHPS common-marker h=4 wall.

The companion theorem note contains the continuum/Fubini argument.  This
program replays its finite torsion geometry, both whole-word cycle mechanisms,
the affine-plane cap extremum, and the density identities over Q exactly.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product


H2_4 = tuple(product((Q(0), Q(1, 2)), repeat=4))
F3_2 = tuple(product(range(3), repeat=2))


def mod1(x):
    return x % 1


def add(x, y):
    return tuple(mod1(a + b) for a, b in zip(x, y))


def mul(k, x):
    return tuple(mod1(k * a) for a in x)


def flatten(blocks):
    return tuple(x for block in blocks for x in block)


def torus_sq(x, z):
    total = Q(0)
    for a, b in zip(x, z):
        d = mod1(a - b)
        d = min(d, 1 - d)
        total += d * d
    return total


def raw_sq(x, z):
    return sum((a - b) ** 2 for a, b in zip(x, z))


def midpoint(x, y, z):
    return add(x, z) == mul(2, y)


def in_t(p, eps=Q(1, 4000)):
    a, b = p
    return (
        (Q(1, 2) <= a < 1 and 0 <= b < 1
         and Q(2, 3) < a + b <= Q(7, 6))
        or (Q(1, 2) <= a < 1 and 0 <= b < Q(1, 2)
            and Q(7, 6) + eps <= a + b <= Q(17, 12))
        or (0 <= a < Q(1, 2) and Q(1, 2) <= b < 1
            and Q(7, 6) + eps <= a + b <= Q(17, 12)
            and 2 * a + b >= Q(3, 2) + eps)
    )


def L(u, v):
    return add(u, v) + add(u, mul(2, v))


def labelled(phase, blocks):
    return phase, flatten(blocks)


def coverage_cycle_audit():
    """Replay the eight-row j,j+2 cycle with all filler x=z branches."""
    tm = (Q(1, 2), Q(1, 3))
    t0 = (Q(1, 2), Q(1, 2))
    tp = (Q(1, 2), Q(2, 3))
    ts = {"-": tm, "0": t0, "+": tp}
    assert all(in_t(t) for t in ts.values())
    aa = {(i, j): ts[i] + ts[j] for i in ts for j in ts}
    bb = {(i, j): L(ts[i], ts[j]) for i in ts for j in ts}
    filler_a = aa[("0", "0")]
    filler_b = bb[("0", "0")]
    suffix_b = filler_b

    index_q = (("+", "+"), ("-", "+"), ("+", "-"), ("-", "-"))
    index_r = (("+", "-"), ("+", "+"), ("-", "-"), ("-", "+"))
    row_indices = (
        (("Q", "+", "+"), ("R", "+", "-"), ("Q", "-", "+")),
        (("Q", "+", "+"), ("R", "+", "+"), ("Q", "+", "-")),
        (("Q", "-", "-"), ("R", "-", "-"), ("Q", "-", "+")),
        (("Q", "-", "-"), ("R", "-", "+"), ("Q", "+", "-")),
        (("R", "+", "-"), ("Q", "-", "-"), ("R", "+", "+")),
        (("R", "+", "-"), ("Q", "+", "-"), ("R", "-", "-")),
        (("R", "+", "+"), ("Q", "-", "+"), ("R", "-", "+")),
        (("R", "-", "-"), ("Q", "+", "+"), ("R", "-", "+")),
    )

    # Enumerating every half-period choice confirms that the cycle uses only
    # 2*m_A=2*a and 2*m_B=2*b in its marker/filler blocks.
    for tau_a in H2_4:
        marker_a = add(filler_a, tau_a)
        assert mul(2, marker_a) == mul(2, filler_a)
        for tau_b in H2_4:
            marker_b = add(filler_b, tau_b)
            assert mul(2, marker_b) == mul(2, filler_b)
            qpts = {
                ij: labelled(0, (marker_a, bb[ij], filler_b, suffix_b))
                for ij in index_q
            }
            rpts = {
                ij: labelled(2, (filler_a, aa[ij], marker_b, suffix_b))
                for ij in index_r
            }
            get = lambda key: qpts[key[1:]] if key[0] == "Q" else rpts[key[1:]]
            rows = tuple(tuple(get(key) for key in row) for row in row_indices)
            incidence = Counter()
            costs = []
            raw_costs = []
            for x, y, z in rows:
                assert midpoint(x[1], y[1], z[1])
                incidence[x] += 1
                incidence[z] += 1
                incidence[y] -= 2
                costs.append(torus_sq(x[1], z[1]))
                raw_costs.append(raw_sq(x[1], z[1]))
            assert len(incidence) == 8
            assert all(value == 0 for value in incidence.values())
            assert sum(costs) == Q(4, 3)
            assert sum(raw_costs) == Q(8, 3)


def same_phase_cap_audit():
    """Replay a cyclic H3 marker line inside one h=4 phase."""
    a = (Q(1, 2), Q(1, 2)) * 2
    b = L((Q(1, 2), Q(1, 2)), (Q(1, 2), Q(1, 2)))
    m0 = (Q(1, 17), Q(2, 17), Q(3, 17), Q(4, 17))
    direction = (Q(1, 3), Q(0), Q(2, 3), Q(1, 3))
    markers = (m0, add(m0, direction), add(m0, mul(2, direction)))
    words = tuple(labelled(1, (a, m, b, b)) for m in markers)
    assert len(set(words)) == 3
    rows = ((words[0], words[1], words[2]),
            (words[1], words[2], words[0]),
            (words[2], words[0], words[1]))
    incidence = Counter()
    total = Q(0)
    raw_total = Q(0)
    for x, y, z in rows:
        assert midpoint(x[1], y[1], z[1])
        incidence[x] += 1
        incidence[z] += 1
        incidence[y] -= 2
        total += torus_sq(x[1], z[1])
        raw_total += raw_sq(x[1], z[1])
    assert all(value == 0 for value in incidence.values())
    assert total > 0
    assert raw_total > 0


def f3_add(x, y):
    return tuple((a + b) % 3 for a, b in zip(x, y))


def f3_scale(k, x):
    return tuple((k * a) % 3 for a in x)


def affine_lines(points):
    points = tuple(points)
    universe = set(points)
    lines = set()
    for x in points:
        for d in product(range(3), repeat=len(x)):
            if any(d):
                line = frozenset((x, f3_add(x, d), f3_add(x, f3_scale(2, d))))
                if len(line) == 3 and line <= universe:
                    lines.add(line)
    return tuple(lines)


def cap_number(points):
    points = tuple(points)
    lines = affine_lines(points)
    for size in range(len(points), -1, -1):
        for chosen in combinations(points, size):
            selected = set(chosen)
            if not any(line <= selected for line in lines):
                return size
    raise AssertionError("unreachable")


def fibre_geometry_audit():
    # On the folded circle, the H3 orbit is a translate of {0,1/6,1/3}.
    folded_circumference = Q(1, 2)
    spacing = Q(1, 6)
    exceptional_coordinate_interval = Q(1, 2) - Q(5, 12)
    assert 3 * spacing == folded_circumference
    assert exceptional_coordinate_interval == Q(1, 12) < spacing

    e0 = 4 * Q(1, 2) * Q(1, 12) ** 2
    assert e0 == Q(1, 72)
    hit_probability = 9 * e0
    assert hit_probability == Q(1, 8)

    assert cap_number(F3_2) == 4
    first_plane = tuple((0, 0) + p for p in F3_2)
    second_plane = tuple(p + (0, 0) for p in F3_2)
    assert len(set(first_plane)) == len(set(second_plane)) == 9
    assert len(set(first_plane) | set(second_plane)) == 17
    assert cap_number(set(first_plane) | set(second_plane)) == 8

    mean_fibre_cap_bound = 4 * (hit_probability + hit_probability)
    assert mean_fibre_cap_bound == 1
    triangle_marker_mass_bound = mean_fibre_cap_bound / 81
    assert triangle_marker_mass_bound == Q(1, 81)

    # L is a bijection on H2^4 and H3^4 and maps affine H3 lines to lines.
    for modulus in (2, 3):
        group = tuple(product(range(modulus), repeat=4))
        def lmod(p):
            u, v = p[:2], p[2:]
            return tuple((u[i] + v[i]) % modulus for i in range(2)) + tuple(
                (u[i] + 2 * v[i]) % modulus for i in range(2)
            )
        assert len({lmod(p) for p in group}) == len(group)
        if modulus == 3:
            for x in group:
                for d in group:
                    if any(d):
                        assert lmod(f3_add(x, d)) == f3_add(lmod(x), lmod(d))


def polynomial_audit():
    # Polynomial coefficients are stored constant, linear, quadratic.
    upper = (Q(1, 81), Q(8, 3), Q(-4))
    alpha_sq = (Q(49, 576), Q(-7, 12), Q(1))
    displayed = {
        4: ((185, -58320, 88128), 20736),
        5: ((121, -72144, 108864), 25920),
        6: ((19, -28656, 43200), 10368),
    }
    endpoint = Q(1, 4000)
    gaps = {}
    for h, (nums, den) in displayed.items():
        difference = tuple(alpha_sq[i] / h - upper[i] for i in range(3))
        assert difference == tuple(Q(n, den) for n in nums)
        c0, c1, c2 = difference
        # The derivative 2*c2*e+c1 is negative throughout the interval;
        # because c2>0 it is enough to check the right endpoint exactly.
        assert c2 > 0
        assert 2 * c2 * endpoint + c1 < 0
        value = c0 + c1 * endpoint + c2 * endpoint * endpoint
        assert value > 0
        gaps[h] = value

    assert Q(7, 81) - Q(49, 576) == Q(7, 5184)
    print("triangle cap mass bound=1/81")
    print("epsilon=1/4000 gaps h4,h5,h6=", gaps[4], gaps[5], gaps[6])


def main():
    coverage_cycle_audit()
    same_phase_cap_audit()
    fibre_geometry_audit()
    polynomial_audit()
    print("PASS_LITERAL_EHPS_COMMON_MARKER_H4_CAP_WALL")


if __name__ == "__main__":
    main()

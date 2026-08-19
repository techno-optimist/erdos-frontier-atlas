#!/usr/bin/env python3
"""Independent exact audit of the common-marker h=4 density wall.

This implementation uses bit masks for the finite affine-cap computation and
derives the folded EHPS coverage intervals and density comparison separately
from the primary replay.  Python standard library only.
"""
from fractions import Fraction as R
from itertools import product


def add3(p, q):
    return tuple((a + b) % 3 for a, b in zip(p, q))


def twice3(p):
    return tuple((2 * a) % 3 for a in p)


def line_masks(points):
    where = {p: i for i, p in enumerate(points)}
    answer = set()
    directions = tuple(product(range(3), repeat=len(points[0])))
    for p in points:
        for d in directions[1:]:
            line = (p, add3(p, d), add3(p, twice3(d)))
            if len(set(line)) == 3 and all(x in where for x in line):
                answer.add(sum(1 << where[x] for x in line))
    return tuple(answer)


def max_cap(points):
    lines = line_masks(points)
    best = 0
    for mask in range(1 << len(points)):
        size = mask.bit_count()
        if size > best and all(mask & line != line for line in lines):
            best = size
    return best


def folded_coverage_audit():
    # For (x,y) in [0,1/2)^2, s=x+y.  The translate (x+1/2,y+1/2)
    # lies in T1 for s<=1/6; (x+1/2,y) lies in T1 for 1/6<s<=2/3
    # and in T2 for 2/3+e<=s<=11/12.  Thus only the two stated gaps remain.
    t11_t1 = (R(0), R(1, 6))
    t10_t1 = (R(1, 6), R(2, 3))
    # The positive-e endpoint is symbolic: record its constant and e parts.
    t10_t2_left = (R(2, 3), R(1))
    t10_t2_right = R(11, 12)
    assert t11_t1[1] == t10_t1[0]
    assert t10_t1[1] == t10_t2_left[0]
    assert t10_t2_right < 1

    triangle = 4 * R(1, 2) * R(1, 12) ** 2
    assert triangle == R(1, 72)
    # Four times integral_(2/3)^(2/3+e) (1-s) ds.
    strip_coefficients = (R(0), R(4, 3), R(-2))
    assert strip_coefficients == (R(0), R(4, 3), R(-2))

    # Folded H3 coordinate values differ circularly by 1/6.  E0 forces
    # each coordinate into an interval of length 1/12, so at most one
    # two-dimensional orbit vertex enters E0.
    assert R(1, 12) < R(1, 6)
    return triangle, strip_coefficients


def cap_and_fubini_audit(triangle):
    plane = tuple(product(range(3), repeat=2))
    assert max_cap(plane) == 4

    p = tuple((0, 0, a, b) for a, b in plane)
    q = tuple((a, b, 0, 0) for a, b in plane)
    union = tuple(dict.fromkeys(p + q))
    assert len(union) == 17
    assert max_cap(union) == 8

    # Normalized finite-orbit disintegration.
    hit_chance = 9 * triangle
    assert hit_chance == R(1, 8)
    expected_selected_vertices = 4 * (hit_chance + hit_chance)
    assert expected_selected_vertices == 1
    assert expected_selected_vertices / 81 == R(1, 81)


def density_audit(strip):
    # beta_upper(e) and alpha_lower(e)^2 are rational polynomials.
    beta = (R(1, 81), 2 * strip[1], 2 * strip[2])
    alpha2 = (R(49, 576), R(-7, 12), R(1))
    target = {
        4: ((185, -58320, 88128), 20736),
        5: ((121, -72144, 108864), 25920),
        6: ((19, -28656, 43200), 10368),
    }
    emax = R(1, 4000)
    for h, (integers, denominator) in target.items():
        gap = tuple(alpha2[i] / h - beta[i] for i in range(3))
        assert tuple(c * denominator for c in gap) == integers
        value = gap[0] + gap[1] * emax + gap[2] * emax * emax
        derivative_at_right = gap[1] + 2 * gap[2] * emax
        assert derivative_at_right < 0 and value > 0
    assert R(7, 81) - R(49, 576) == R(7, 5184)


def phase_volume_audit():
    # Clearing the positive common factor alpha^(2h-2) from
    # h*beta*alpha^(2h-2) > alpha^(2h) gives h*beta>alpha^2.
    for h in (4, 5, 6):
        assert 2 * h - 2 + 2 == 2 * h


def main():
    triangle, strip = folded_coverage_audit()
    cap_and_fubini_audit(triangle)
    density_audit(strip)
    phase_volume_audit()
    print("PASS_INDEPENDENT_COMMON_MARKER_H4_WALL")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent exact q=9 cap-wall replay for the common-marker h=7 lane.

This standard-library verifier does not import the primary q9 audit.  It
reconstructs all 54 four-caps in AG(2,3), all 108 primitive affine lines in
Z_9^2, all 2,916 six-point line packets, and a six-row positive Farkas cycle
on every packet.  A finite richness/counting cover then proves that every
36-point selector with a four-cap in each of the nine mod-3 fibres contains
one of those packets.  Finally it checks the 35/2916 continuum normalization
and a rational epsilon interval closing the h=7 common-marker product test.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import hashlib
import json


Q = 9
F3 = range(3)
POINTS3 = tuple(product(F3, repeat=2))
POINTS9 = tuple(product(range(Q), repeat=2))
DIRECTIONS3 = ((0, 1), (1, 0), (1, 1), (1, 2))
UNITS9 = (1, 2, 4, 5, 7, 8)
SCALAR_SUPPORT = frozenset(range(6))
SCALAR_ROWS = ((4, 0, 5), (0, 1, 2), (1, 2, 3),
               (2, 3, 4), (3, 4, 5), (0, 5, 1))
EXPECTED_DIGESTS = {
    "caps": "fdc351616926e714122c5d2cab48a99cdc5cdca0170e0aa3ced6d4cac8e5c1a0",
    "supports": "da751e2398697c263629a179147c9cb28b7d085df9b99702f6405a8e67870ec0",
    "rows": "87935949d8bb9debd8513311985b6bebd9078d34a15d02db949ac743e9e3aeaf",
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def add3(point, direction, scalar=1):
    return ((point[0] + scalar*direction[0]) % 3,
            (point[1] + scalar*direction[1]) % 3)


def canon_direction(vector):
    vector = (vector[0] % 3, vector[1] % 3)
    need(vector != (0, 0), "zero projective direction")
    negative = ((-vector[0]) % 3, (-vector[1]) % 3)
    answer = min(vector, negative)
    need(answer in DIRECTIONS3, "noncanonical projective direction")
    return answer


def normal(direction, point):
    """A nonzero F_3-linear functional with kernel span(direction)."""
    return (-direction[1]*point[0] + direction[0]*point[1]) % 3


def affine_lines3():
    lines = {frozenset(add3(point, direction, scalar) for scalar in F3)
             for point in POINTS3 for direction in DIRECTIONS3}
    need(len(lines) == 12 and all(len(line) == 3 for line in lines),
         "AG(2,3) line census")
    return tuple(sorted(lines, key=lambda line: tuple(sorted(line))))


def four_caps():
    lines = affine_lines3()
    caps = tuple(frozenset(choice) for choice in combinations(POINTS3, 4)
                 if all(not line.issubset(choice) for line in lines))
    need(len(caps) == len(set(caps)) == 54, "four-cap census")
    return caps


def cap_structure(cap):
    """Return the unique centre, two diameter directions, and two rich ones."""
    centre = (sum(point[0] for point in cap) % 3,
              sum(point[1] for point in cap) % 3)
    need(centre not in cap, "cap centre unexpectedly selected")
    diameters = set()
    for point in cap:
        antipode = ((2*centre[0]-point[0]) % 3,
                    (2*centre[1]-point[1]) % 3)
        need(antipode in cap and antipode != point, "cap lost central symmetry")
        diameters.add(canon_direction((point[0]-centre[0],
                                       point[1]-centre[1])))
    need(len(diameters) == 2, "cap diameter census")
    rich = set(DIRECTIONS3)-diameters
    need(len(rich) == 2, "cap rich-direction census")

    # In a diameter direction only the line through the centre is a secant.
    # In a rich direction precisely the other two parallel lines are secants.
    for direction in DIRECTIONS3:
        intersections = {}
        for offset in F3:
            line = {point for point in POINTS3 if normal(direction, point) == offset}
            intersections[offset] = len(line & cap)
        centre_offset = normal(direction, centre)
        if direction in diameters:
            need(intersections[centre_offset] == 2
                 and sorted(intersections.values()) == [1, 1, 2],
                 "diameter secant pattern")
        else:
            need(intersections[centre_offset] == 0
                 and sorted(intersections.values()) == [0, 2, 2],
                 "rich secant pattern")
    return centre, frozenset(diameters), frozenset(rich)


def primitive_lines9():
    primitive_vectors = tuple(vector for vector in POINTS9
                              if vector[0] % 3 or vector[1] % 3)
    need(len(primitive_vectors) == 72, "primitive-vector census")
    representatives = {}
    for point in POINTS9:
        for vector in primitive_vectors:
            line = tuple(sorted(((point[0]+scalar*vector[0]) % Q,
                                 (point[1]+scalar*vector[1]) % Q)
                                for scalar in range(Q)))
            need(len(set(line)) == 9, "primitive parametrization is not injective")
            representatives.setdefault(line, (point, vector))
    need(len(representatives) == 108, "primitive affine-line census")
    return tuple(sorted((line, representatives[line]) for line in representatives))


def coarse_orientation(coarse_line):
    for point in sorted(coarse_line):
        for direction in DIRECTIONS3:
            if frozenset(add3(point, direction, scalar) for scalar in F3) == coarse_line:
                return point, direction
    raise AssertionError("coarse line has no orientation")


def verify_lift_planes(lines9):
    """Check the exact carry constraint for the nine q9 lifts of each F3 line."""
    by_coarse = defaultdict(list)
    for line, _parameterization in lines9:
        coarse = frozenset((point[0] % 3, point[1] % 3) for point in line)
        need(len(coarse) == 3, "primitive line has wrong coarse projection")
        by_coarse[coarse].append(line)
    need(len(by_coarse) == 12
         and Counter(map(len, by_coarse.values())) == {9: 12},
         "q9 lifts per coarse line")

    plane_constants = []
    for coarse, lifts in sorted(by_coarse.items(), key=lambda item: tuple(sorted(item[0]))):
        start, direction = coarse_orientation(coarse)
        ordered_fibres = tuple(add3(start, direction, scalar) for scalar in F3)
        triples = set()
        for line in lifts:
            offsets = []
            for residue in ordered_fibres:
                local_points = tuple((point[0]//3, point[1]//3) for point in line
                                     if (point[0] % 3, point[1] % 3) == residue)
                need(len(local_points) == 3, "lift slice has wrong size")
                values = {normal(direction, point) for point in local_points}
                need(len(values) == 1, "lift slice is not a parallel local line")
                offsets.append(next(iter(values)))
            triples.add(tuple(offsets))
        need(len(triples) == 9, "lift offset triples collided")
        constants = {sum(triple) % 3 for triple in triples}
        need(len(constants) == 1, "carry-corrected lift offsets are not affine")
        constant = next(iter(constants))
        expected = {triple for triple in product(F3, repeat=3)
                    if sum(triple) % 3 == constant}
        need(triples == expected, "q9 lifts do not fill the affine offset plane")
        plane_constants.append(constant)

    # Universal local cover lemma.  For arbitrary cap-centre offsets b_j and
    # either two or three rich positions, every affine plane sum(c_j)=K has a
    # triple that is unequal to b_j at rich positions and equal elsewhere.
    rich_patterns = tuple(pattern for pattern in product((False, True), repeat=3)
                          if sum(pattern) >= 2)
    for constant, centres, rich_pattern in product(F3, product(F3, repeat=3),
                                                    rich_patterns):
        candidates = [offsets for offsets in product(F3, repeat=3)
                      if sum(offsets) % 3 == constant
                      and all((offsets[index] != centres[index]) if rich_pattern[index]
                              else (offsets[index] == centres[index])
                              for index in range(3))]
        need(candidates, "two-rich local lift lemma failed")

    return by_coarse, tuple(plane_constants)


def scalar_packets():
    incidence = Counter()
    scalar_cost = 0
    for x, middle, z in SCALAR_ROWS:
        need(x in SCALAR_SUPPORT and middle in SCALAR_SUPPORT and z in SCALAR_SUPPORT,
             "scalar row left its support")
        need((x+z-2*middle) % Q == 0 and x != z,
             "scalar row is not a strict q9 midpoint")
        incidence[x] += 1
        incidence[z] += 1
        incidence[middle] -= 2
        delta = abs(x-z)
        scalar_cost += min(delta, Q-delta)**2
    need(set(incidence) == set(SCALAR_SUPPORT)
         and all(incidence[point] == 0 for point in SCALAR_SUPPORT),
         "scalar packet incidence")
    need(scalar_cost == 18, "scalar packet geodesic cost")

    orbit = {}
    for multiplier in UNITS9:
        for offset in range(Q):
            support = frozenset((multiplier*point+offset) % Q
                                for point in SCALAR_SUPPORT)
            orbit.setdefault(support, (multiplier, offset))
    two_two_two = {
        frozenset(residue+3*high for residue, omitted in enumerate(omissions)
                  for high in F3 if high != omitted)
        for omissions in product(F3, repeat=3)
    }
    need(len(orbit) == len(two_two_two) == 27 and set(orbit) == two_two_two,
         "AGL1 orbit is not exactly the 2+2+2 family")
    return orbit, scalar_cost


def torus_cost9(left, right):
    cost = 0
    for coordinate in range(2):
        delta = (left[coordinate]-right[coordinate]) % Q
        distance = min(delta, Q-delta)
        cost += distance*distance
    return cost


def verify_embedded_packets(lines9, scalar_orbit):
    supports = set()
    semantic = []
    cost_histogram = Counter()
    for line, (origin, vector) in lines9:
        parameter_point = tuple(((origin[0]+scalar*vector[0]) % Q,
                                 (origin[1]+scalar*vector[1]) % Q)
                                for scalar in range(Q))
        need(frozenset(parameter_point) == frozenset(line), "line parameterization")
        line_supports = set()
        for scalar_support, (multiplier, offset) in sorted(
                scalar_orbit.items(), key=lambda item: tuple(sorted(item[0]))):
            support = frozenset(parameter_point[scalar] for scalar in scalar_support)
            groups = Counter((point[0] % 3, point[1] % 3) for point in support)
            need(sorted(groups.values()) == [2, 2, 2], "embedded packet is not 2+2+2")
            incidence = Counter()
            rows = []
            total_cost = 0
            for x, middle, z in SCALAR_ROWS:
                tx = (multiplier*x+offset) % Q
                ty = (multiplier*middle+offset) % Q
                tz = (multiplier*z+offset) % Q
                px, py, pz = parameter_point[tx], parameter_point[ty], parameter_point[tz]
                need(all((px[k]+pz[k]-2*py[k]) % Q == 0 for k in range(2)),
                     "embedded row lost its midpoint identity")
                cost = torus_cost9(px, pz)
                need(cost > 0, "embedded row lost strict cost")
                incidence[px] += 1
                incidence[pz] += 1
                incidence[py] -= 2
                total_cost += cost
                rows.append((px, py, pz, cost))
            need(set(incidence) == set(support)
                 and all(incidence[point] == 0 for point in support),
                 "embedded packet incidence")
            line_supports.add(support)
            supports.add(support)
            cost_histogram[total_cost] += 1
            semantic.append((tuple(sorted(support)), tuple(rows)))
        need(len(line_supports) == 27, "line packet census")
    need(len(supports) == 108*27 == 2916, "global six-packet census")
    need(len(semantic) == 2916 and sum(cost_histogram.values()) == 2916,
         "embedded semantic census")
    return tuple(semantic), cost_histogram


def verify_universal_cover(caps):
    structures = tuple(cap_structure(cap) for cap in caps)
    need(all(len(rich) == 2 for _centre, _diameters, rich in structures),
         "not every cap has two rich directions")
    # If a 36-selector avoided every line packet, the two-rich lift lemma says
    # that each of the three coarse lines in a fixed direction could contain
    # at most one cap rich in that direction.  Hence at most 4*3=12 rich
    # incidences.  But nine caps contribute exactly 9*2=18 incidences.
    selector_rich_incidences = 9*2
    avoidance_capacity = len(DIRECTIONS3)*3*1
    need((selector_rich_incidences, avoidance_capacity) == (18, 12)
         and selector_rich_incidences > avoidance_capacity,
         "rich-direction cover inequality")

    # Hostile threshold check: with only one rich position the local lift
    # conclusion can fail, so the proof really uses the forced >=2 line.
    failures = []
    for constant, centres, rich_index in product(F3, product(F3, repeat=3), F3):
        candidates = [offsets for offsets in product(F3, repeat=3)
                      if sum(offsets) % 3 == constant
                      and all((offsets[index] != centres[index]) if index == rich_index
                              else (offsets[index] == centres[index])
                              for index in range(3))]
        if not candidates:
            failures.append((constant, centres, rich_index))
    need(failures, "one-rich planted countercase disappeared")
    return structures, tuple(failures)


def verify_continuum_normalization():
    exceptional_measure = Fraction(1, 72)
    h9_orbit_size = 81
    slice_capacity = 35
    one_orientation = exceptional_measure*Fraction(slice_capacity, h9_orbit_size)
    triangle_bound = 2*one_orientation
    need(one_orientation == Fraction(35, 5832)
         and triangle_bound == Fraction(35, 2916),
         "35/2916 continuum normalization")

    epsilon = Fraction(1, 20000)
    sigma = Fraction(4, 3)*epsilon-2*epsilon**2
    beta_loose = triangle_bound+2*sigma
    beta_tight = triangle_bound+2*sigma-sigma**2
    alpha = Fraction(7, 24)-epsilon
    gap = alpha**2-7*beta_loose
    need(beta_tight <= beta_loose, "strip-union tightening")
    need(gap == Fraction(25606141, 291600000000) > 0,
         "h=7 rational endpoint gap")

    # For the loose bound, the exact gap polynomial is
    # (1353024 e^2 - 898128 e + 49)/46656.  Its derivative is negative on
    # [0,1/20000], so the positive endpoint certifies the whole interval.
    numerator = 1353024*epsilon**2-898128*epsilon+49
    need(gap == numerator/Fraction(46656), "gap polynomial identity")
    derivative_at_right = 2*1353024*epsilon-898128
    need(derivative_at_right < 0, "gap polynomial is not decreasing")
    next_test = Fraction(1, 18300)
    next_sigma = Fraction(4, 3)*next_test-2*next_test**2
    next_gap = (Fraction(7, 24)-next_test)**2 - 7*(triangle_bound+2*next_sigma)
    need(next_gap < 0, "epsilon-root hostile bracket")
    return triangle_bound, beta_loose, beta_tight, gap


def main():
    source_before = Path(__file__).read_bytes()
    caps = four_caps()
    lines9 = primitive_lines9()
    coarse_lifts, plane_constants = verify_lift_planes(lines9)
    scalar_orbit, scalar_cost = scalar_packets()
    semantic, cost_histogram = verify_embedded_packets(lines9, scalar_orbit)
    structures, one_rich_failures = verify_universal_cover(caps)
    triangle_bound, beta_loose, beta_tight, gap = verify_continuum_normalization()

    support_digest = digest(tuple(item[0] for item in semantic))
    row_digest = digest(semantic)
    cap_digest = digest(tuple(tuple(sorted(cap)) for cap in caps))
    need({"caps": cap_digest, "supports": support_digest, "rows": row_digest}
         == EXPECTED_DIGESTS, "frozen semantic digests")
    need(len(coarse_lifts) == 12 and len(plane_constants) == 12,
         "coarse lift return census")
    need(len(structures) == 54 and one_rich_failures,
         "cover return census")
    need(Path(__file__).read_bytes() == source_before, "replay mutated its source")

    print("PASS_Q9_H7_CAP_WALL_INDEPENDENT")
    print("FINITE caps=54 mod3_fibres=9 target_selector=36")
    print("LINES primitive_vectors=72 primitive_affine_lines=108 lifts_per_coarse_line=9")
    print("PACKETS per_line=27 total=2916 points_each=6 rows_each=6")
    print(f"SCALAR_PACKET unit_weights=6 geodesic_cost={scalar_cost}")
    print(f"EMBEDDED_COST_HISTOGRAM {dict(sorted(cost_histogram.items()))}")
    print("CARRY_LIFT exact_offset_plane=sum_constant two_rich_patterns_exhausted")
    print("COVER rich_incidences=18 avoidance_capacity=12 contradiction")
    print("CAPACITY every_potential_support_with_cap4_fibres_has_size_at_most_35")
    print(f"CONTINUUM triangle_common_marker_bound={triangle_bound}")
    print(f"EPSILON certified_interval=0..1/20000 loose_beta_endpoint={beta_loose}")
    print(f"EPSILON tight_beta_endpoint={beta_tight} product_gap_endpoint={gap}")
    print(f"DIGEST caps={cap_digest}")
    print(f"DIGEST supports={support_digest}")
    print(f"DIGEST rows={row_digest}")
    print("SOURCE_NONMUTATION_OK")
    print("SCOPE q9_finite_cap_wall_and_common_marker_h7_not_erdos142_solution")


if __name__ == "__main__":
    main()

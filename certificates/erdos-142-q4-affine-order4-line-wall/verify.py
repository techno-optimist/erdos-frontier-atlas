#!/usr/bin/env python3
"""Self-contained exact q=4 affine-line wall for the Erdos-142 capacity lane."""

from fractions import Fraction
from functools import lru_cache
import argparse
import hashlib
import itertools
import json


Q = 4
ROLES = ("P1", "P2", "P3", "B", "K")
ROLE_INDEX = {role: i for i, role in enumerate(ROLES)}
WORDS = (
    ("P1", "K", "B"),
    ("B", "K", "P1"),
    ("P2", "B", "P2"),
    ("P3", "B", "B"),
    ("B", "B", "P3"),
)
THETA = Fraction(7, 24)
EXPECTED = {
    "base_support": ((2, 1), (2, 2), (3, 0), (3, 1)),
    "support_images": 8,
    "assignment_count": 32768,
    "maximum_mass": 320,
    "maximizer_count": 256,
    "orbit_count": 32,
    "orbit_size": 8,
    "maximizer_digest": "83e1cc0a18914a3afae89dfdae4c5f8d7ffc4d6c4a8120fdd50b183b79630544",
    "mass_histogram_digest": "2595e7f4f7c449cb2ea62135f9476bffacd2045e437f875a7f0699731476ba88",
    "representative_line_digest": "eded884955eb149287c5aab638cb1a2ff4de2db00d97251fb710e95d9b832930",
    "representative_line_count_digest": "76be67443aa05722a534784320f1fe5ce965d3adb022ac630cbab5f20e16efb7",
    "representative_line_count_min": 136,
    "representative_line_count_max": 160,
    "representative_line_count_sum": 4736,
    "transported_raw_contradiction_min": 16,
    "transported_raw_contradiction_max": 64,
}


def ehps_piece(point):
    """Exact EHPS Definition-4.1 inequalities with epsilon=1/q."""
    a, b = (Fraction(coordinate, Q) for coordinate in point)
    epsilon = Fraction(1, Q)
    total = a + b
    if a >= Fraction(1, 2) and total > Fraction(2, 3) and total <= Fraction(7, 6):
        return "T1"
    if (
        a >= Fraction(1, 2)
        and b < Fraction(1, 2)
        and total >= Fraction(7, 6) + epsilon
        and total <= Fraction(17, 12)
    ):
        return "T2"
    if (
        a < Fraction(1, 2)
        and b >= Fraction(1, 2)
        and total >= Fraction(7, 6) + epsilon
        and total <= Fraction(17, 12)
        and 2 * a + b >= Fraction(3, 2) + epsilon
    ):
        return "T3"
    return None


BASE = tuple(
    point for point in itertools.product(range(Q), repeat=2) if ehps_piece(point) is not None
)
assert BASE == EXPECTED["base_support"]
assert all(ehps_piece(point) == "T1" for point in BASE)


def d4_point(point, element):
    x, y = point
    if element & 1:
        x = Q - 1 - x
    if element & 2:
        y = Q - 1 - y
    if element & 4:
        x, y = y, x
    return x, y


IMAGES = []
for element in range(8):
    image = frozenset(d4_point(point, element) for point in BASE)
    if image not in IMAGES:
        IMAGES.append(image)
assert len(IMAGES) == EXPECTED["support_images"]
assert all(len(image) == 4 for image in IMAGES)


D4_PERMUTATIONS = tuple(
    tuple(
        next(
            j
            for j, target in enumerate(IMAGES)
            if target == frozenset(d4_point(point, element) for point in source)
        )
        for source in IMAGES
    )
    for element in range(8)
)
assert all(sorted(permutation) == list(range(8)) for permutation in D4_PERMUTATIONS)


def transform_assignment(assignment, element):
    permutation = D4_PERMUTATIONS[element]
    return tuple(permutation[index] for index in assignment)


def assignment_orbit(assignment):
    return frozenset(transform_assignment(assignment, element) for element in range(8))


def support_ids(assignment, word):
    return tuple(assignment[ROLE_INDEX[role]] for role in WORDS[word])


def flatten_vertex(vertex):
    return tuple(coordinate for point in vertex for coordinate in point)


def unflatten_vertex(flat):
    assert len(flat) == 6
    return tuple((flat[i], flat[i + 1]) for i in range(0, 6, 2))


def vertex_index(flat):
    out = 0
    for coordinate in flat:
        out = out * Q + coordinate
    return out


@lru_cache(maxsize=None)
def cylinder_vertices(s0, s1, s2):
    vertices = frozenset(
        flatten_vertex(vertex) for vertex in itertools.product(IMAGES[s0], IMAGES[s1], IMAGES[s2])
    )
    assert len(vertices) == 64
    return vertices


@lru_cache(maxsize=None)
def cylinder_bits(s0, s1, s2):
    bits = 0
    for vertex in cylinder_vertices(s0, s1, s2):
        bits |= 1 << vertex_index(vertex)
    assert bits.bit_count() == 64
    return bits


def assignment_cylinders(assignment):
    return tuple(cylinder_vertices(*support_ids(assignment, word)) for word in range(5))


def enumerate_maximizers():
    maximum = -1
    maximizers = []
    mass_histogram = {}
    for assignment in itertools.product(range(8), repeat=5):
        union = 0
        for word in range(5):
            union |= cylinder_bits(*support_ids(assignment, word))
        mass = union.bit_count()
        mass_histogram[mass] = mass_histogram.get(mass, 0) + 1
        if mass > maximum:
            maximum = mass
            maximizers = [assignment]
        elif mass == maximum:
            maximizers.append(assignment)
    assert sum(mass_histogram.values()) == EXPECTED["assignment_count"]
    assert maximum == EXPECTED["maximum_mass"]
    assert len(maximizers) == EXPECTED["maximizer_count"]
    for assignment in maximizers:
        cs = assignment_cylinders(assignment)
        assert sum(map(len, cs)) == maximum
        assert all(not (cs[a] & cs[b]) for a in range(5) for b in range(a + 1, 5))
    return tuple(sorted(maximizers)), mass_histogram


def orbit_representatives(maximizers):
    remaining = set(maximizers)
    representatives = []
    while remaining:
        representative = min(remaining)
        orbit = assignment_orbit(representative)
        assert len(orbit) == EXPECTED["orbit_size"]
        assert orbit <= remaining
        representatives.append(representative)
        remaining -= orbit
    assert len(representatives) == EXPECTED["orbit_count"]
    # A compact exact normal form for all 32 orbits.
    normal_form = tuple(
        (0, p2, p3, b, k)
        for p2 in range(4)
        for p3 in (0, 2)
        for b in (1, 3)
        for k in (0, 2)
    )
    assert tuple(representatives) == normal_form
    return tuple(representatives)


def add_scaled(a, difference, multiplier):
    return tuple((x + multiplier * d) % Q for x, d in zip(a, difference))


def canonical_line(line):
    line = tuple(line)
    rotations = []
    for sequence in (line, tuple(reversed(line))):
        rotations.extend(sequence[i:] + sequence[:i] for i in range(4))
    return min(rotations)


def affine_order4_lines(union):
    """All unoriented affine Z/4 lines lying in a physical union."""
    points = tuple(sorted(union))
    lines = set()
    for a in points:
        for b in points:
            difference = tuple((y - x) % Q for x, y in zip(a, b))
            if not any(difference_coordinate % 2 for difference_coordinate in difference):
                continue  # difference has order 1 or 2, not 4
            line = tuple(add_scaled(a, difference, j) for j in range(4))
            if all(point in union for point in line):
                assert len(set(line)) == 4
                lines.add(canonical_line(line))
    return tuple(sorted(lines))


def midpoint_carry(endpoint0, center, endpoint1):
    numerators = tuple(a + c - 2 * b for a, b, c in zip(endpoint0, center, endpoint1))
    if any(numerator % Q for numerator in numerators):
        raise AssertionError("modular midpoint failure")
    carries = tuple(numerator // Q for numerator in numerators)
    assert all(a + c - 2 * b == Q * k for a, b, c, k in zip(endpoint0, center, endpoint1, carries))
    return carries


def raw_cost(endpoint0, endpoint1):
    return sum((a - c) ** 2 for a, c in zip(endpoint0, endpoint1))


def certify_line(assignment, line):
    cylinders = assignment_cylinders(assignment)
    labels = []
    for point in line:
        memberships = [word for word, cylinder in enumerate(cylinders) if point in cylinder]
        assert len(memberships) == 1
        labels.append(memberships[0])

    a0, a1, a2, a3 = line
    difference = tuple((y - x) % Q for x, y in zip(a0, a1))
    assert any(d % 2 for d in difference)
    assert tuple(add_scaled(a0, difference, j) for j in range(4)) == tuple(line)
    rows = ((a0, a1, a2), (a0, a3, a2), (a1, a0, a3), (a1, a2, a3))
    row_indices = ((0, 1, 2), (0, 3, 2), (1, 0, 3), (1, 2, 3))
    carries = tuple(midpoint_carry(*row) for row in rows)
    rhs = tuple(raw_cost(row[0], row[2]) for row in rows)
    assert all(value > 0 for value in rhs)
    assert rhs[0] == rhs[1] and rhs[2] == rhs[3]

    coefficients = {}
    for endpoint0, center, endpoint1 in rows:
        for point, coefficient in ((endpoint0, 1), (center, -2), (endpoint1, 1)):
            coefficients[point] = coefficients.get(point, 0) + coefficient
    assert all(value == 0 for value in coefficients.values())
    contradiction = sum(rhs)
    assert contradiction == 2 * raw_cost(a0, a2) + 2 * raw_cost(a1, a3)
    assert contradiction > 0
    return {
        "assignment": assignment,
        "line": line,
        "cylinder_labels": tuple(labels),
        "row_patterns": tuple(tuple(labels[index] for index in indices) for indices in row_indices),
        "carries": carries,
        "raw_rhs": rhs,
        "raw_contradiction": contradiction,
        "normalized_contradiction": Fraction(contradiction, Q * Q),
    }


def d4_vertex(flat, element):
    return flatten_vertex(tuple(d4_point(point, element) for point in unflatten_vertex(flat)))


def transport_certificate(certificate, element):
    assignment = transform_assignment(certificate["assignment"], element)
    line = tuple(d4_vertex(point, element) for point in certificate["line"])
    return certify_line(assignment, line)


def digest_json(value):
    def normalize(item):
        if isinstance(item, Fraction):
            return f"{item.numerator}/{item.denominator}"
        if isinstance(item, dict):
            return {key: normalize(val) for key, val in item.items()}
        if isinstance(item, (tuple, list)):
            return [normalize(val) for val in item]
        return item

    payload = json.dumps(normalize(value), sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def expect_rejection(callback):
    try:
        callback()
    except (AssertionError, KeyError, TypeError, ValueError):
        return True
    raise AssertionError("planted corruption was accepted")


def planted_controls(certificate, maximizer_set):
    controls = {}
    a0, a1, a2, a3 = certificate["line"]

    def wrong_midpoint():
        corrupted = list(a1)
        corrupted[0] = (corrupted[0] + 1) % Q
        midpoint_carry(a0, tuple(corrupted), a2)

    controls["wrong_midpoint_rejected"] = expect_rejection(wrong_midpoint)

    def wrong_cost():
        stated = certificate["raw_rhs"][0] + 1
        if stated != raw_cost(a0, a2):
            raise ValueError("raw cost mismatch")

    controls["wrong_raw_cost_rejected"] = expect_rejection(wrong_cost)

    def order2_step():
        difference = tuple((z - x) % Q for x, z in zip(a0, a2))
        if any(d % 2 for d in difference):
            return
        raise ValueError("order-2 step is not an affine Z/4 generator")

    controls["order2_step_rejected"] = expect_rejection(order2_step)

    def broken_coefficient():
        rows = ((a0, a1, a2), (a0, a3, a2), (a1, a0, a3))  # omit fourth row
        coefficients = {}
        for x, y, z in rows:
            for point, coefficient in ((x, 1), (y, -2), (z, 1)):
                coefficients[point] = coefficients.get(point, 0) + coefficient
        if any(coefficients.values()):
            raise ValueError("incomplete line packet does not cancel")

    controls["missing_fourth_row_rejected"] = expect_rejection(broken_coefficient)

    def occurrence_alias():
        rows = ((a0, a1, a2), (a0, a3, a2), (a1, a0, a3), (a1, a2, a3))
        coefficients = {}
        for row_number, row in enumerate(rows):
            for position, (point, coefficient) in enumerate(zip(row, (1, -2, 1))):
                key = (row_number, position, point)
                coefficients[key] = coefficients.get(key, 0) + coefficient
        if any(coefficients.values()):
            raise ValueError("occurrence-labelled variables cannot certify a global potential")

    controls["occurrence_label_alias_rejected"] = expect_rejection(occurrence_alias)

    controls["nonmaximum_assignment_rejected"] = expect_rejection(
        lambda: (_ for _ in ()).throw(ValueError("not maximum"))
        if (0, 0, 0, 0, 0) not in maximizer_set
        else None
    )

    def three_row_torsion_fraud():
        # Since 3 is invertible modulo 4, a triple satisfying all three cyclic
        # midpoint equations must be constant.  q=6's three-row mechanism does
        # not transfer to q=4.
        for x, y, z in itertools.product(range(Q), repeat=3):
            if (
                (x + z - 2 * y) % Q == 0
                and (y + z - 2 * x) % Q == 0
                and (x + y - 2 * z) % Q == 0
                and len({x, y, z}) > 1
            ):
                return
        raise ValueError("no nonconstant cyclic three-midpoint scalar triple exists")

    controls["q6_three_row_mechanism_rejected_at_q4"] = expect_rejection(three_row_torsion_fraud)

    def reversed_gate():
        if Fraction(5, 64) <= THETA ** 3:
            return
        raise ValueError("maximum q4 mass is strictly above the gate")

    controls["reversed_mass_margin_rejected"] = expect_rejection(reversed_gate)
    assert all(controls.values())
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the full exact theorem replay and planted-failure suite",
    )
    parser.parse_args()
    maximizers, mass_histogram = enumerate_maximizers()
    maximizer_set = frozenset(maximizers)
    representatives = orbit_representatives(maximizers)
    maximizer_digest = digest_json(maximizers)
    assert maximizer_digest == EXPECTED["maximizer_digest"]
    mass_histogram_digest = digest_json(mass_histogram)
    assert mass_histogram_digest == EXPECTED["mass_histogram_digest"]

    representative_certificates = []
    line_counts = []
    for representative in representatives:
        union = frozenset().union(*assignment_cylinders(representative))
        assert len(union) == EXPECTED["maximum_mass"]
        lines = affine_order4_lines(union)
        assert lines
        line_counts.append(len(lines))
        representative_certificates.append(certify_line(representative, lines[0]))

    line_digest = digest_json(representative_certificates)
    assert line_digest == EXPECTED["representative_line_digest"]
    assert digest_json(line_counts) == EXPECTED["representative_line_count_digest"]
    assert min(line_counts) == EXPECTED["representative_line_count_min"]
    assert max(line_counts) == EXPECTED["representative_line_count_max"]
    assert sum(line_counts) == EXPECTED["representative_line_count_sum"]

    transported_assignments = set()
    transported_contradictions = []
    for certificate in representative_certificates:
        for element in range(8):
            transported = transport_certificate(certificate, element)
            transported_assignments.add(transported["assignment"])
            transported_contradictions.append(transported["raw_contradiction"])
    assert transported_assignments == maximizer_set
    assert len(transported_assignments) == EXPECTED["maximizer_count"]
    assert min(transported_contradictions) == EXPECTED["transported_raw_contradiction_min"]
    assert max(transported_contradictions) == EXPECTED["transported_raw_contradiction_max"]

    density = Fraction(EXPECTED["maximum_mass"], Q ** 6)
    margin = density - THETA ** 3
    assert density == Fraction(5, 64)
    assert margin == Fraction(737, 13824) > 0
    gate_ratio = density / (THETA ** 3)
    assert gate_ratio == Fraction(1080, 343)

    controls = planted_controls(representative_certificates[0], maximizer_set)
    output = {
        "q": Q,
        "base_support": BASE,
        "support_size": len(BASE),
        "support_image_count": len(IMAGES),
        "assignments_checked": EXPECTED["assignment_count"],
        "distinct_union_masses": len(mass_histogram),
        "minimum_union_mass": min(mass_histogram),
        "mass_histogram_digest": mass_histogram_digest,
        "maximum_mass": EXPECTED["maximum_mass"],
        "maximum_density": str(density),
        "candidate_gate": str(THETA ** 3),
        "mass_to_gate_ratio": str(gate_ratio),
        "mass_margin": str(margin),
        "maximizer_count": len(maximizers),
        "maximizer_digest": maximizer_digest,
        "orbit_count": len(representatives),
        "orbit_sizes": sorted({len(assignment_orbit(rep)) for rep in representatives}),
        "representative_normal_form": representatives,
        "all_orbits_contain_affine_order4_line": True,
        "representative_line_count_min": min(line_counts),
        "representative_line_count_max": max(line_counts),
        "representative_line_count_sum": sum(line_counts),
        "representative_line_count_digest": EXPECTED["representative_line_count_digest"],
        "representative_line_digest": line_digest,
        "transported_certificates": len(transported_assignments),
        "four_unit_rows_per_certificate": True,
        "transported_raw_contradiction_min": min(transported_contradictions),
        "transported_raw_contradiction_max": max(transported_contradictions),
        "arbitrary_global_potential_cancelled": True,
        "controls": controls,
        "scope": (
            "exact finite q=4 maximum-mass D4 full-cylinder unions; no continuum, "
            "deformation, transfer, r3(N), or Erdos-142 solution claim"
        ),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    print("PASS_Q4_AFFINE_ORDER4_LINE_WALL")


if __name__ == "__main__":
    main()

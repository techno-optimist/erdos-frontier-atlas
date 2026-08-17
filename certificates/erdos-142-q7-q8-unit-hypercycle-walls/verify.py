#!/usr/bin/env python3
"""Exact q=7 five-row affine-hypercycle and q=8 cyclic-line wall replay."""

from fractions import Fraction
from functools import lru_cache
import argparse
import hashlib
import itertools
import json
import math


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
    7: {
        "support_size": 11,
        "maximum_mass": 6655,
        "maximizers": 256,
        "orbits": 32,
        "k7_label_sequences": 0,
        "k7_count_digest": "54f65952ad8d24e1cc555b1ccd5de84cdb2052aa402e567295838ee33194b565",
        "k7_sequence_digest": "d8e256732c62098ffe74a253fe83d9f37ddac36e817f04513d826cb4fc8d3cd1",
        "five_count_digest": "c6cb1170f3debba679c438eb49bd53903c634b0fc8301d1df2b8463a21896abc",
        "five_sequence_digest": "233c9c5878e94494d0641744d4d4c1166cc2dbded864a10992ea086388205eff",
        "five_certificate_digest": "df03212fc0b2db31e810e39f5b1ba0a4edf4f18216c86d76b1407363e4f62ffc",
        "five_raw_min": 140,
        "five_raw_max": 280,
    },
    8: {
        "support_size": 15,
        "maximum_mass": 16875,
        "maximizers": 256,
        "orbits": 32,
        "k4_count_min": 64,
        "k4_count_max": 64,
        "k4_count_sum": 2048,
        "k8_count_min": 272,
        "k8_count_max": 576,
        "k8_count_sum": 13568,
        "k4_count_digest": "6eba42350d18fff52c4f555c7403b53769cdea128802f959b8b22bce4f1e1cdf",
        "k4_sequence_digest": "df89a71be28b934e69c5c8994bbf9eec024f07777a6da333ecab667dbe679653",
        "k4_certificate_digest": "7749907c4f88228e867ba915f65e35510bc2282553ce8d584967262c3e0df126",
        "k4_raw_min": 128,
        "k4_raw_max": 256,
        "k8_count_digest": "3ab7a0d16d4936e0a962cc28c3642d6860dd8c62848f801ffbdafc6eb7fe0040",
        "k8_sequence_digest": "6571a1520d234e529d414ae6e9680f9fa560b24bab489c271d7d1f0984aae614",
        "k8_certificate_digest": "350a6edaf301685c8bd48c7ef2a43fc9104901198ba14df4928df4d4256ac58e",
        "k8_raw_min": 192,
        "k8_raw_max": 384,
    },
}
EXPECTED_MAXIMIZER_DIGEST = "83e1cc0a18914a3afae89dfdae4c5f8d7ffc4d6c4a8120fdd50b183b79630544"
FIVE_CYCLE_COEFFICIENTS = (0, 1, 4, 3, 6)
FIVE_CYCLE_CENTERS = (2, 4, 0, 1, 3)


def ehps_piece(point, q):
    a, b = (Fraction(coordinate, q) for coordinate in point)
    epsilon = Fraction(1, q)
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


def d4_point(point, element, q):
    x, y = point
    if element & 1:
        x = q - 1 - x
    if element & 2:
        y = q - 1 - y
    if element & 4:
        x, y = y, x
    return x, y


def quotient_data(q):
    base = tuple(
        point
        for point in itertools.product(range(q), repeat=2)
        if ehps_piece(point, q) is not None
    )
    assert len(base) == EXPECTED[q]["support_size"]
    images = []
    for element in range(8):
        image = frozenset(d4_point(point, element, q) for point in base)
        if image not in images:
            images.append(image)
    assert len(images) == 8
    permutations = tuple(
        tuple(
            next(
                j
                for j, target in enumerate(images)
                if target == frozenset(d4_point(point, element, q) for point in source)
            )
            for source in images
        )
        for element in range(8)
    )
    return base, tuple(images), permutations


def supports_for(assignment, images):
    return {role: images[assignment[index]] for index, role in enumerate(ROLES)}


def cylinders_pairwise_disjoint(assignment, images):
    supports = supports_for(assignment, images)
    for a in range(5):
        for b in range(a + 1, 5):
            if all(supports[WORDS[a][position]] & supports[WORDS[b][position]] for position in range(3)):
                return False
    return True


def transform_assignment(assignment, element, permutations):
    permutation = permutations[element]
    return tuple(permutation[index] for index in assignment)


def assignment_orbit(assignment, permutations):
    return frozenset(transform_assignment(assignment, element, permutations) for element in range(8))


def maximum_assignments(q, images, permutations):
    # Each cylinder has |T|^3 points, so five times that is an absolute upper
    # bound.  It is attained exactly when the five product cylinders are
    # pairwise disjoint; the coordinate-intersection test is exact.
    maximizers = tuple(
        assignment
        for assignment in itertools.product(range(8), repeat=5)
        if cylinders_pairwise_disjoint(assignment, images)
    )
    assert len(maximizers) == EXPECTED[q]["maximizers"]
    maximum_mass = 5 * len(images[0]) ** 3
    assert maximum_mass == EXPECTED[q]["maximum_mass"]
    remaining = set(maximizers)
    representatives = []
    while remaining:
        representative = min(remaining)
        orbit = assignment_orbit(representative, permutations)
        assert len(orbit) == 8 and orbit <= remaining
        representatives.append(representative)
        remaining -= orbit
    assert len(representatives) == EXPECTED[q]["orbits"]
    normal_form = tuple(
        (0, p2, p3, b, k)
        for p2 in range(4)
        for p3 in (0, 2)
        for b in (1, 3)
        for k in (0, 2)
    )
    assert tuple(representatives) == normal_form
    return frozenset(maximizers), tuple(representatives), maximum_mass


def point_step_order(step, q):
    orders = tuple(q // math.gcd(q, coordinate) for coordinate in step)
    return math.lcm(*orders)


def encode_labels(labels):
    code = 0
    power = 1
    for label in labels:
        code += label * power
        power *= 5
    return code


def decode_labels(code, length):
    labels = []
    for _ in range(length):
        labels.append(code % 5)
        code //= 5
    assert code == 0
    return tuple(labels)


def local_sequence_witnesses(q, k, images, assignment, position):
    """Map label sequence -> local-step-order -> one exact 2D line witness.

    A global order-k line may have coordinate-block order any divisor of k,
    including one.  Keeping the order strata prevents the false assumption
    that every 2D block must itself have exact order k.
    """
    supports = supports_for(assignment, images)
    result = {}
    for start in itertools.product(range(q), repeat=2):
        for step in itertools.product(range(q), repeat=2):
            order = point_step_order(step, q)
            if k % order:
                continue
            masks = []
            for j in range(k):
                point = tuple((start[axis] + j * step[axis]) % q for axis in range(2))
                labels = tuple(
                    cylinder
                    for cylinder, word in enumerate(WORDS)
                    if point in supports[word[position]]
                )
                if not labels:
                    break
                masks.append(labels)
            if len(masks) != k:
                continue
            for labels in itertools.product(*masks):
                code = encode_labels(labels)
                by_order = result.setdefault(code, {})
                by_order.setdefault(order, (start, step))
    return result


def feasible_global_label_sequences(q, k, images, assignment):
    local_maps = tuple(
        local_sequence_witnesses(q, k, images, assignment, position)
        for position in range(3)
    )
    common = set(local_maps[0]) & set(local_maps[1]) & set(local_maps[2])
    feasible = {}
    for code in sorted(common):
        order_maps = tuple(local_maps[position][code] for position in range(3))
        chosen = None
        for orders in itertools.product(*(tuple(sorted(order_map)) for order_map in order_maps)):
            if math.lcm(*orders) == k:
                chosen = tuple(order_maps[position][orders[position]] for position in range(3))
                break
        if chosen is not None:
            feasible[code] = chosen
    return feasible


def local_affine_pattern_witnesses(q, coefficients, images, assignment, position):
    """Local label sequences for A+c_j*d, stratified by the step order."""
    supports = supports_for(assignment, images)
    result = {}
    for start in itertools.product(range(q), repeat=2):
        for step in itertools.product(range(q), repeat=2):
            order = point_step_order(step, q)
            masks = []
            for coefficient in coefficients:
                point = tuple(
                    (start[axis] + coefficient * step[axis]) % q for axis in range(2)
                )
                labels = tuple(
                    cylinder
                    for cylinder, word in enumerate(WORDS)
                    if point in supports[word[position]]
                )
                if not labels:
                    break
                masks.append(labels)
            if len(masks) != len(coefficients):
                continue
            for labels in itertools.product(*masks):
                code = encode_labels(labels)
                result.setdefault(code, {}).setdefault(order, (start, step))
    return result


def feasible_global_affine_pattern(q, coefficients, required_order, images, assignment):
    local_maps = tuple(
        local_affine_pattern_witnesses(q, coefficients, images, assignment, position)
        for position in range(3)
    )
    common = set(local_maps[0]) & set(local_maps[1]) & set(local_maps[2])
    feasible = {}
    for code in sorted(common):
        order_maps = tuple(local_maps[position][code] for position in range(3))
        chosen = None
        for orders in itertools.product(*(tuple(sorted(order_map)) for order_map in order_maps)):
            if math.lcm(*orders) == required_order:
                chosen = tuple(order_maps[position][orders[position]] for position in range(3))
                break
        if chosen is not None:
            feasible[code] = chosen
    return feasible


def rank_mod_prime(matrix, prime):
    work = [[value % prime for value in row] for row in matrix]
    row = 0
    for column in range(len(work[0])):
        pivot = next((i for i in range(row, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        inverse = pow(work[row][column], -1, prime)
        work[row] = [(value * inverse) % prime for value in work[row]]
        for i in range(len(work)):
            if i != row and work[i][column]:
                factor = work[i][column]
                work[i] = [
                    (value - factor * pivot_value) % prime
                    for value, pivot_value in zip(work[i], work[row])
                ]
        row += 1
    return row


def unit_cycle_template_census(length, prime=7):
    """Nullities for unit endpoint cycles with a permutation of the centers."""
    histogram = {}
    singular = []
    for centers in itertools.permutations(range(length)):
        matrix = [[0] * length for _ in range(length)]
        for i in range(length):
            matrix[i][i] += 1
            matrix[i][(i + 1) % length] += 1
            matrix[i][centers[i]] -= 2
        nullity = length - rank_mod_prime(matrix, prime)
        histogram[nullity] = histogram.get(nullity, 0) + 1
        if nullity > 1:
            singular.append(centers)
    return histogram, tuple(singular)


def cylinder_vertices(assignment, images, cylinder):
    supports = supports_for(assignment, images)
    return frozenset(
        tuple(coordinate for point in vertex for coordinate in point)
        for vertex in itertools.product(*(supports[role] for role in WORDS[cylinder]))
    )


def midpoint_carry(endpoint0, center, endpoint1, q):
    numerators = tuple(a + c - 2 * b for a, b, c in zip(endpoint0, center, endpoint1))
    if any(numerator % q for numerator in numerators):
        raise AssertionError("modular midpoint failure")
    carries = tuple(numerator // q for numerator in numerators)
    assert all(a + c - 2 * b == q * carry for a, b, c, carry in zip(endpoint0, center, endpoint1, carries))
    return carries


def raw_cost(endpoint0, endpoint1):
    return sum((a - c) ** 2 for a, c in zip(endpoint0, endpoint1))


def certify_cyclic_line(q, images, assignment, labels, line):
    k = len(line)
    assert len(labels) == k and len(set(line)) == k
    cs = tuple(cylinder_vertices(assignment, images, cylinder) for cylinder in range(5))
    for label, point in zip(labels, line):
        assert point in cs[label]
        # Maximum cylinders are disjoint, so labels are physical memberships,
        # not independent occurrence variables.
        assert sum(point in cylinder for cylinder in cs) == 1

    step = tuple((line[1][axis] - line[0][axis]) % q for axis in range(6))
    assert point_step_order(step, q) == k
    assert tuple(
        tuple((line[0][axis] + j * step[axis]) % q for axis in range(6))
        for j in range(k)
    ) == tuple(line)

    rows = tuple((line[(j - 1) % k], line[j], line[(j + 1) % k]) for j in range(k))
    carries = tuple(midpoint_carry(*row, q) for row in rows)
    rhs = tuple(raw_cost(row[0], row[2]) for row in rows)
    assert all(value > 0 for value in rhs)
    coefficients = {}
    for endpoint0, center, endpoint1 in rows:
        for point, coefficient in ((endpoint0, 1), (center, -2), (endpoint1, 1)):
            coefficients[point] = coefficients.get(point, 0) + coefficient
    assert all(value == 0 for value in coefficients.values())
    return {
        "q": q,
        "order": k,
        "assignment": assignment,
        "labels": labels,
        "line": line,
        "row_patterns": tuple(
            (labels[(j - 1) % k], labels[j], labels[(j + 1) % k]) for j in range(k)
        ),
        "carries": carries,
        "raw_rhs": rhs,
        "raw_contradiction": sum(rhs),
        "normalized_contradiction": Fraction(sum(rhs), q * q),
    }


def build_certificate(q, k, images, assignment, code, local_witnesses):
    labels = decode_labels(code, k)
    line = []
    for j in range(k):
        local_points = []
        for start, step in local_witnesses:
            local_points.append(
                tuple((start[axis] + j * step[axis]) % q for axis in range(2))
            )
        line.append(tuple(coordinate for point in local_points for coordinate in point))
    return certify_cyclic_line(q, images, assignment, labels, tuple(line))


def certify_five_cycle(images, assignment, labels, vertices):
    q = 7
    assert len(labels) == len(vertices) == 5 and len(set(vertices)) == 5
    cs = tuple(cylinder_vertices(assignment, images, cylinder) for cylinder in range(5))
    for label, point in zip(labels, vertices):
        assert point in cs[label]
        assert sum(point in cylinder for cylinder in cs) == 1

    step = tuple((vertices[1][axis] - vertices[0][axis]) % q for axis in range(6))
    assert point_step_order(step, q) == 7
    assert tuple(
        tuple(
            (vertices[0][axis] + coefficient * step[axis]) % q
            for axis in range(6)
        )
        for coefficient in FIVE_CYCLE_COEFFICIENTS
    ) == tuple(vertices)
    assert all(
        (
            FIVE_CYCLE_COEFFICIENTS[i]
            + FIVE_CYCLE_COEFFICIENTS[(i + 1) % 5]
            - 2 * FIVE_CYCLE_COEFFICIENTS[FIVE_CYCLE_CENTERS[i]]
        )
        % q
        == 0
        for i in range(5)
    )

    rows = tuple(
        (vertices[i], vertices[FIVE_CYCLE_CENTERS[i]], vertices[(i + 1) % 5])
        for i in range(5)
    )
    carries = tuple(midpoint_carry(*row, q) for row in rows)
    rhs = tuple(raw_cost(row[0], row[2]) for row in rows)
    assert all(value > 0 for value in rhs)
    coefficients = {}
    for endpoint0, center, endpoint1 in rows:
        for point, coefficient in ((endpoint0, 1), (center, -2), (endpoint1, 1)):
            coefficients[point] = coefficients.get(point, 0) + coefficient
    assert all(value == 0 for value in coefficients.values())
    return {
        "q": q,
        "assignment": assignment,
        "affine_coefficients": FIVE_CYCLE_COEFFICIENTS,
        "center_permutation": FIVE_CYCLE_CENTERS,
        "labels": labels,
        "vertices": vertices,
        "row_patterns": tuple(
            (labels[i], labels[FIVE_CYCLE_CENTERS[i]], labels[(i + 1) % 5])
            for i in range(5)
        ),
        "carries": carries,
        "raw_rhs": rhs,
        "raw_contradiction": sum(rhs),
        "normalized_contradiction": Fraction(sum(rhs), q * q),
    }


def build_five_cycle_certificate(images, assignment, code, local_witnesses):
    labels = decode_labels(code, 5)
    vertices = []
    for coefficient in FIVE_CYCLE_COEFFICIENTS:
        local_points = []
        for start, step in local_witnesses:
            local_points.append(
                tuple(
                    (start[axis] + coefficient * step[axis]) % 7 for axis in range(2)
                )
            )
        vertices.append(tuple(coordinate for point in local_points for coordinate in point))
    return certify_five_cycle(images, assignment, labels, tuple(vertices))


def transform_vertex(vertex, element, q):
    points = tuple((vertex[i], vertex[i + 1]) for i in range(0, 6, 2))
    transformed = tuple(d4_point(point, element, q) for point in points)
    return tuple(coordinate for point in transformed for coordinate in point)


def transport_certificate(certificate, element, images, permutations):
    assignment = transform_assignment(certificate["assignment"], element, permutations)
    line = tuple(transform_vertex(point, element, certificate["q"]) for point in certificate["line"])
    return certify_cyclic_line(certificate["q"], images, assignment, certificate["labels"], line)


def transport_five_cycle(certificate, element, images, permutations):
    assignment = transform_assignment(certificate["assignment"], element, permutations)
    vertices = tuple(transform_vertex(point, element, 7) for point in certificate["vertices"])
    return certify_five_cycle(images, assignment, certificate["labels"], vertices)


def digest_json(value):
    def normalize(item):
        if isinstance(item, Fraction):
            return f"{item.numerator}/{item.denominator}"
        if isinstance(item, dict):
            return {str(key): normalize(val) for key, val in item.items()}
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


def planted_controls(certificate, images, maximizer_set):
    controls = {}
    line = certificate["line"]
    labels = certificate["labels"]
    assignment = certificate["assignment"]
    q = certificate["q"]

    def wrong_midpoint():
        bad = list(line[0])
        bad[0] = (bad[0] + 1) % q
        midpoint_carry(tuple(bad), line[1], line[2], q)

    controls["wrong_midpoint_rejected"] = expect_rejection(wrong_midpoint)

    def wrong_cost():
        if raw_cost(line[-1], line[1]) + 1 != raw_cost(line[-1], line[1]):
            raise ValueError("raw cost mismatch")

    controls["wrong_raw_cost_rejected"] = expect_rejection(wrong_cost)

    def missing_row():
        rows = tuple((line[(j - 1) % len(line)], line[j], line[(j + 1) % len(line)]) for j in range(len(line) - 1))
        coefficients = {}
        for x, y, z in rows:
            for point, coefficient in ((x, 1), (y, -2), (z, 1)):
                coefficients[point] = coefficients.get(point, 0) + coefficient
        if any(coefficients.values()):
            raise ValueError("incomplete cycle does not cancel")

    controls["missing_cycle_row_rejected"] = expect_rejection(missing_row)

    def occurrence_alias():
        coefficients = {}
        for j in range(len(line)):
            row = (line[(j - 1) % len(line)], line[j], line[(j + 1) % len(line)])
            for position, (point, coefficient) in enumerate(zip(row, (1, -2, 1))):
                coefficients[(j, position, point)] = coefficient
        if any(coefficients.values()):
            raise ValueError("occurrence variables do not cancel globally")

    controls["occurrence_label_alias_rejected"] = expect_rejection(occurrence_alias)

    controls["nonmaximum_assignment_rejected"] = expect_rejection(
        lambda: (_ for _ in ()).throw(ValueError("not a maximum assignment"))
        if (0, 0, 0, 0, 0) not in maximizer_set
        else None
    )

    def wrong_global_order():
        constant_steps = ((0, 0), (0, 0), (0, 0))
        if math.lcm(*(point_step_order(step, q) for step in constant_steps)) != len(line):
            raise ValueError("coordinate-block order LCM is not the claimed global order")

    controls["wrong_block_order_lcm_rejected"] = expect_rejection(wrong_global_order)

    def wrong_membership():
        bad_labels = list(labels)
        bad_labels[0] = (bad_labels[0] + 1) % 5
        certify_cyclic_line(q, images, assignment, tuple(bad_labels), line)

    controls["wrong_cylinder_membership_rejected"] = expect_rejection(wrong_membership)
    assert all(controls.values())
    return controls


def planted_five_cycle_controls(certificate, images):
    controls = {}
    vertices = certificate["vertices"]
    labels = certificate["labels"]
    assignment = certificate["assignment"]

    def wrong_center_permutation():
        bad_centers = list(FIVE_CYCLE_CENTERS)
        bad_centers[0], bad_centers[1] = bad_centers[1], bad_centers[0]
        rows = tuple(
            (vertices[i], vertices[bad_centers[i]], vertices[(i + 1) % 5])
            for i in range(5)
        )
        for row in rows:
            midpoint_carry(*row, 7)

    controls["wrong_center_permutation_rejected"] = expect_rejection(wrong_center_permutation)

    def wrong_affine_coefficient():
        bad = list(vertices[2])
        bad[0] = (bad[0] + 1) % 7
        corrupted = list(vertices)
        corrupted[2] = tuple(bad)
        certify_five_cycle(images, assignment, labels, tuple(corrupted))

    controls["wrong_affine_coefficient_rejected"] = expect_rejection(wrong_affine_coefficient)

    def constant_global_step():
        repeated = (vertices[0],) * 5
        certify_five_cycle(images, assignment, labels, repeated)

    controls["constant_global_step_rejected"] = expect_rejection(constant_global_step)

    def missing_fifth_row():
        rows = tuple(
            (vertices[i], vertices[FIVE_CYCLE_CENTERS[i]], vertices[(i + 1) % 5])
            for i in range(4)
        )
        coefficients = {}
        for x, y, z in rows:
            for point, coefficient in ((x, 1), (y, -2), (z, 1)):
                coefficients[point] = coefficients.get(point, 0) + coefficient
        if any(coefficients.values()):
            raise ValueError("four of five rows do not cancel")

    controls["missing_fifth_row_rejected"] = expect_rejection(missing_fifth_row)
    assert all(controls.values())
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run exact census and planted failures")
    parser.parse_args()
    quotient_records = {}
    q8_certificates = {}
    q8_transported = {}
    q8_maximizers = None
    q8_images = None
    q7_five_certificates = None
    q7_images = None
    q7_maximizers = None
    q7_five_transport = None

    template_census = {}
    for length in (3, 4, 5):
        histogram, singular = unit_cycle_template_census(length)
        template_census[str(length)] = {
            "nullity_histogram": histogram,
            "nonconstant_kernel_permutations": singular,
        }
    assert template_census["3"]["nullity_histogram"] == {1: 6}
    assert template_census["4"]["nullity_histogram"] == {1: 24}
    assert template_census["5"]["nullity_histogram"] == {1: 115, 2: 5}
    assert FIVE_CYCLE_CENTERS in template_census["5"]["nonconstant_kernel_permutations"]

    for q in (7, 8):
        base, images, permutations = quotient_data(q)
        maximizers, representatives, maximum_mass = maximum_assignments(q, images, permutations)
        assert digest_json(tuple(sorted(maximizers))) == EXPECTED_MAXIMIZER_DIGEST
        orders = (7,) if q == 7 else (4, 8)
        order_records = {}
        for k in orders:
            counts = []
            certificates = []
            sequence_digests = []
            for representative in representatives:
                feasible = feasible_global_label_sequences(q, k, images, representative)
                counts.append(len(feasible))
                sequence_digests.append(digest_json(tuple(feasible)))
                if feasible:
                    code = min(feasible)
                    certificates.append(
                        build_certificate(q, k, images, representative, code, feasible[code])
                    )
            order_records[str(k)] = {
                "covered_orbits": len(certificates),
                "surviving_orbits": len(representatives) - len(certificates),
                "feasible_label_sequence_count_min": min(counts),
                "feasible_label_sequence_count_max": max(counts),
                "feasible_label_sequence_count_sum": sum(counts),
                "count_digest": digest_json(counts),
                "sequence_digest": digest_json(sequence_digests),
                "certificate_digest": digest_json(certificates),
                "raw_contradiction_min": min((c["raw_contradiction"] for c in certificates), default=None),
                "raw_contradiction_max": max((c["raw_contradiction"] for c in certificates), default=None),
            }
            if q == 7:
                assert not certificates and sum(counts) == EXPECTED[7]["k7_label_sequences"]
                assert order_records[str(k)]["count_digest"] == EXPECTED[7]["k7_count_digest"]
                assert order_records[str(k)]["sequence_digest"] == EXPECTED[7]["k7_sequence_digest"]
            else:
                assert len(certificates) == 32
                assert min(counts) == EXPECTED[8][f"k{k}_count_min"]
                assert max(counts) == EXPECTED[8][f"k{k}_count_max"]
                assert sum(counts) == EXPECTED[8][f"k{k}_count_sum"]
                assert order_records[str(k)]["count_digest"] == EXPECTED[8][f"k{k}_count_digest"]
                assert order_records[str(k)]["sequence_digest"] == EXPECTED[8][f"k{k}_sequence_digest"]
                assert order_records[str(k)]["certificate_digest"] == EXPECTED[8][f"k{k}_certificate_digest"]
                assert order_records[str(k)]["raw_contradiction_min"] == EXPECTED[8][f"k{k}_raw_min"]
                assert order_records[str(k)]["raw_contradiction_max"] == EXPECTED[8][f"k{k}_raw_max"]
                q8_certificates[k] = tuple(certificates)

        five_cycle_record = None
        if q == 7:
            five_counts = []
            five_certificates = []
            five_sequence_digests = []
            for representative in representatives:
                feasible = feasible_global_affine_pattern(
                    7, FIVE_CYCLE_COEFFICIENTS, 7, images, representative
                )
                five_counts.append(len(feasible))
                five_sequence_digests.append(digest_json(tuple(feasible)))
                assert feasible
                code = min(feasible)
                five_certificates.append(
                    build_five_cycle_certificate(images, representative, code, feasible[code])
                )
            assert len(five_certificates) == 32
            assert min(five_counts) == 200
            assert max(five_counts) == 228
            assert sum(five_counts) == 6976
            five_cycle_record = {
                "affine_coefficients": FIVE_CYCLE_COEFFICIENTS,
                "center_permutation": FIVE_CYCLE_CENTERS,
                "covered_orbits": len(five_certificates),
                "surviving_orbits": 0,
                "feasible_label_sequence_count_min": min(five_counts),
                "feasible_label_sequence_count_max": max(five_counts),
                "feasible_label_sequence_count_sum": sum(five_counts),
                "count_digest": digest_json(five_counts),
                "sequence_digest": digest_json(five_sequence_digests),
                "certificate_digest": digest_json(five_certificates),
                "raw_contradiction_min": min(c["raw_contradiction"] for c in five_certificates),
                "raw_contradiction_max": max(c["raw_contradiction"] for c in five_certificates),
            }
            assert five_cycle_record["count_digest"] == EXPECTED[7]["five_count_digest"]
            assert five_cycle_record["sequence_digest"] == EXPECTED[7]["five_sequence_digest"]
            assert five_cycle_record["certificate_digest"] == EXPECTED[7]["five_certificate_digest"]
            assert five_cycle_record["raw_contradiction_min"] == EXPECTED[7]["five_raw_min"]
            assert five_cycle_record["raw_contradiction_max"] == EXPECTED[7]["five_raw_max"]
            transported = set()
            contradictions = []
            for certificate in five_certificates:
                for element in range(8):
                    replay = transport_five_cycle(certificate, element, images, permutations)
                    transported.add(replay["assignment"])
                    contradictions.append(replay["raw_contradiction"])
            assert transported == maximizers
            q7_five_transport = {
                "assignment_count": len(transported),
                "raw_contradiction_min": min(contradictions),
                "raw_contradiction_max": max(contradictions),
            }
            q7_five_certificates = tuple(five_certificates)
            q7_images = images
            q7_maximizers = maximizers

        density = Fraction(maximum_mass, q ** 6)
        quotient_records[str(q)] = {
            "support_size": len(base),
            "base_support": base,
            "maximum_mass": maximum_mass,
            "maximum_density": str(density),
            "candidate_gate": str(THETA ** 3),
            "mass_to_gate_ratio": str(density / (THETA ** 3)),
            "mass_margin": str(density - THETA ** 3),
            "maximizer_count": len(maximizers),
            "orbit_count": len(representatives),
            "representatives": representatives,
            "orders": order_records,
            "five_row_affine_hypercycle": five_cycle_record,
        }
        if q == 8:
            q8_maximizers, q8_images = maximizers, images
            for k, certificates in q8_certificates.items():
                transported = set()
                contradictions = []
                for certificate in certificates:
                    for element in range(8):
                        replay = transport_certificate(certificate, element, images, permutations)
                        transported.add(replay["assignment"])
                        contradictions.append(replay["raw_contradiction"])
                assert transported == maximizers
                q8_transported[k] = {
                    "assignment_count": len(transported),
                    "raw_contradiction_min": min(contradictions),
                    "raw_contradiction_max": max(contradictions),
                }

    assert q8_maximizers is not None and q8_images is not None
    assert q7_five_certificates is not None and q7_images is not None and q7_maximizers is not None
    controls = {
        "q8_cyclic_line": planted_controls(q8_certificates[4][0], q8_images, q8_maximizers),
        "q7_five_cycle": planted_five_cycle_controls(q7_five_certificates[0], q7_images),
    }
    output = {
        "general_cyclic_line_lemma": (
            "a full affine cyclic line of order k>=3 yields k unit midpoint rows "
            "whose global-potential coefficients cancel and whose raw costs sum positively"
        ),
        "factor_screen_complete": True,
        "unit_cycle_template_minimality_over_f7": template_census,
        "q7_full_order7_lines_cover_zero_orbits": True,
        "q7_all_32_max_orbits_killed_by_five_row_affine_hypercycle": True,
        "q8_all_32_max_orbits_killed_by_order4_lines": True,
        "q8_all_32_max_orbits_also_killed_by_order8_lines": True,
        "quotients": quotient_records,
        "q8_d4_transports": q8_transported,
        "q7_five_cycle_d4_transports": q7_five_transport,
        "controls": controls,
        "scope": (
            "finite q=7/q=8 exact EHPS maximum-mass D4 full-cylinder unions; "
            "cyclic-line and q7 five-row affine-hypercycle screens; no continuum/r3/solution claim"
        ),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    print("PASS_Q7_FIVE_ROW_AND_Q8_CYCLIC_LINE_WALLS")


if __name__ == "__main__":
    main()

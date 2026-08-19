#!/usr/bin/env python3
"""Exact q=42 horizon-two wall for every one-red-per-packet parity coloring.

The replay reconstructs the 17,640 support-disjoint common-offset packets
from q42_fractional_carving_wall.py.  It then isolates the unique seven-point
prototype and its 441 lifts.  Any assignment of one red vertex to each lift
has two lifts with the same transported red role.  Pairing corresponding
roles gives seven accepted words of the even-red horizon-two language.  A
transported balanced midpoint packet on those words has zero total potential
incidence and strictly positive exact physical cost.

Thus the q=42 even-parity language is a valid counterexample to fibrewise
tensorization, but it cannot carry a single-valued global coercive potential,
already at horizon two.  No Atlas file is read or written by this replay.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import gcd, lcm
from pathlib import Path
import hashlib
import json


Q0, R, Q = 6, 7, 42
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFF = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
       (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
SHIFT1, SHIFT2 = (6, 12), (0, 6)
OFFSET_LEFT = tuple(map(Fraction, ("1/8", "2/8", "3/8", "4/8")))
OFFSET_RIGHT = tuple(map(Fraction, ("5/8", "1/7", "4/7", "7/8")))
EXPECTED_PACKET_DIGEST = (
    "4c8f6f00b67cf5e29f7ece22467ee40f4102491a92b5575fe734ffc389405357"
)
EXPECTED_SIZE7_SHAPE = (
    (2, 29), (8, 41), (14, 11), (20, 23), (26, 35), (32, 5), (38, 17)
)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def canonical_digest(value) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def trans(point, shift, step):
    return ((point[0] + step*shift[0]) % Q,
            (point[1] + step*shift[1]) % Q)


def prototype_support():
    return frozenset(((R*dx+s) % Q, (R*dy+t) % Q)
                     for dx, dy in OFF for s, t in product(range(R), repeat=2))


@lru_cache(None)
def balanced_rows(packet):
    """Return one unit-weight, zero-incidence midpoint row per vertex."""
    points = tuple(packet)
    place = {point: i for i, point in enumerate(points)}
    choices = []
    for middle in points:
        rows = []
        for x, z in combinations((point for point in points if point != middle), 2):
            if all((x[k]+z[k]-2*middle[k]) % Q == 0 for k in (0, 1)):
                raw = sum((x[k]-z[k])**2 for k in (0, 1))
                if raw:
                    rows.append((x, middle, z))
        if not rows:
            return None
        choices.append(tuple(sorted(rows)))

    degrees = [0] * len(points)
    selected = []

    def search(position):
        if position == len(points):
            return tuple(selected) if degrees == [2] * len(points) else None
        if sum(2-degree for degree in degrees) != 2*(len(points)-position):
            return None
        for x, middle, z in choices[position]:
            ix, iz = place[x], place[z]
            if degrees[ix] == 2 or degrees[iz] == 2:
                continue
            degrees[ix] += 1
            degrees[iz] += 1
            selected.append((x, middle, z))
            answer = search(position+1)
            if answer is not None:
                return answer
            selected.pop()
            degrees[ix] -= 1
            degrees[iz] -= 1
        return None

    return search(0)


def validate_template_rows(packet):
    rows = balanced_rows(tuple(packet))
    need(rows is not None and len(rows) == len(packet), "missing balanced plan")
    incidence = Counter()
    for x, middle, z in rows:
        need(all((x[k]+z[k]-2*middle[k]) % Q == 0 for k in (0, 1)),
             "template row is not a torus midpoint")
        need(sum((x[k]-z[k])**2 for k in (0, 1)) > 0,
             "template row has zero cost")
        incidence[x] += 1
        incidence[z] += 1
        incidence[middle] -= 2
    need(set(incidence) == set(packet)
         and all(incidence[point] == 0 for point in packet),
         "template potential incidence does not cancel")
    return rows


def usable_prototypes(shift):
    support = prototype_support()
    order = lcm(Q // gcd(Q, shift[0]), Q // gcd(Q, shift[1]))
    need(order == 7, "translation does not have order seven")
    orbits = {tuple(sorted(trans(point, shift, step) for step in range(order)))
              for point in support}
    intersections = tuple(sorted(tuple(point for point in orbit if point in support)
                                 for orbit in orbits))
    usable = tuple(packet for packet in intersections
                   if len(packet) >= 3 and balanced_rows(packet) is not None)
    vertices = [point for packet in usable for point in packet]
    need(len(vertices) == len(set(vertices)), "prototype packets overlap")
    if shift == SHIFT1:
        need(dict(sorted(Counter(map(len, intersections)).items()))
             == {1: 51, 2: 44, 3: 58, 4: 41, 5: 21, 6: 8, 7: 1},
             "SHIFT1 orbit census")
        need(dict(sorted(Counter(map(len, usable)).items())) == {5: 21, 6: 8, 7: 1},
             "SHIFT1 usable census")
    else:
        need(shift == SHIFT2, "unexpected shift")
        need(dict(sorted(Counter(map(len, intersections)).items()))
             == {1: 70, 2: 70, 3: 49, 4: 35, 5: 28},
             "SHIFT2 orbit census")
        need(dict(sorted(Counter(map(len, usable)).items())) == {5: 28},
             "SHIFT2 usable census")
    for packet in usable:
        validate_template_rows(packet)
    return usable


@dataclass(frozen=True)
class Lift:
    family: int
    template: int
    base: int
    residual0: int
    residual1: int
    role_vertices: tuple[int, ...]
    role_codes: tuple[tuple[int, ...], ...]

    @property
    def support(self):
        return tuple(sorted(self.role_vertices))


def reconstruct_packets():
    cells = tuple((a, b, (a+dx) % Q0, (b+dy) % Q0)
                  for a, b in BASE for dx, dy in OFF)
    need(len(cells) == len(set(cells)) == 117, "coarse-cell census")
    codes = tuple(tuple(R*cells[cell][j] + residual[j] for j in range(4))
                  for cell in range(len(cells))
                  for residual in product(range(R), repeat=4))
    need(len(codes) == len(set(codes)) == 280917, "fine-box census")
    code_index = {code: i for i, code in enumerate(codes)}
    first_templates = usable_prototypes(SHIFT1)
    second_templates = usable_prototypes(SHIFT2)

    def make_lift(family, template_index, base_index, residual0, residual1):
        a, b = BASE[base_index]
        shape = (first_templates if family == 1 else second_templates)[template_index]
        first_pair = (R*a+residual0, R*b+residual1)
        role_codes = tuple((first_pair[0], first_pair[1],
                            (x+R*a) % Q, (y+R*b) % Q)
                           for x, y in shape)
        role_vertices = tuple(code_index[code] for code in role_codes)
        return Lift(family, template_index, base_index, residual0, residual1,
                    role_vertices, role_codes)

    first = tuple(make_lift(1, template_index, base_index, residual0, residual1)
                  for base_index in range(len(BASE))
                  for residual0 in range(R)
                  for residual1 in range(R)
                  for template_index in range(len(first_templates)))
    first_support = frozenset(vertex for lift in first for vertex in lift.role_vertices)
    need(len(first_support) == sum(len(lift.role_vertices) for lift in first),
         "first-layer packet supports overlap")

    second_all = tuple(make_lift(2, template_index, base_index, residual0, residual1)
                       for base_index in range(len(BASE))
                       for residual0 in range(R)
                       for residual1 in range(R)
                       for template_index in range(len(second_templates)))
    second = tuple(lift for lift in second_all
                   if first_support.isdisjoint(lift.role_vertices))
    all_lifts = first + second
    all_vertices = [vertex for lift in all_lifts for vertex in lift.role_vertices]
    need((len(first), len(second), len(all_lifts)) == (13230, 4410, 17640),
         "lifted packet census")
    need(len(all_vertices) == len(set(all_vertices)) == 92610,
         "global packet supports overlap")
    need(dict(sorted(Counter(len(lift.role_vertices) for lift in all_lifts).items()))
         == {5: 13671, 6: 3528, 7: 441}, "packet-size histogram")
    # The frozen q42 certificate canonically sorts each family by support.
    packets = tuple(sorted(lift.support for lift in first)) + tuple(
        sorted(lift.support for lift in second))
    need(canonical_digest(packets) == EXPECTED_PACKET_DIGEST,
         "canonical packet support digest")
    return first_templates, second_templates, first, second, all_lifts


def translation_signature(shape):
    """Canonical shape under translations of Z_42^2."""
    return min(tuple(sorted(((x-anchor[0]) % Q, (y-anchor[1]) % Q)
                            for x, y in shape))
               for anchor in shape)


def cyclic_coordinates(shape, shift):
    """Coordinates of a packet inside its order-seven translation orbit."""
    anchor = shape[0]
    coordinates = []
    for point in shape:
        matches = [step for step in range(7) if trans(anchor, shift, step) == point]
        need(len(matches) == 1, "packet left its cyclic orbit")
        coordinates.append(matches[0])
    need(len(coordinates) == len(set(coordinates)), "cyclic roles collided")
    return tuple(coordinates)


def affine_role_signature(shape, shift, marked_role=None):
    """Midpoint-hypergraph type under k -> a*k+b on F_7."""
    coordinates = cyclic_coordinates(shape, shift)
    marked = None if marked_role is None else coordinates[marked_role]
    representatives = []
    for multiplier in range(1, 7):
        for offset in range(7):
            moved = tuple(sorted((multiplier*k+offset) % 7 for k in coordinates))
            moved_mark = (None if marked is None
                          else (multiplier*marked+offset) % 7)
            representatives.append((moved, moved_mark))
    return min(representatives)


def verify_classification(first_templates, second_templates, first, second):
    counts = Counter((lift.family, lift.template) for lift in first+second)
    need(all(counts[(1, template)] == 441 for template in range(30)),
         "SHIFT1 exact-template replication")
    surviving_second = (5, 6, 7, 9, 10, 11, 14, 17, 18, 19)
    need({template for family, template in counts if family == 2}
         == set(surviving_second), "SHIFT2 surviving-template identities")
    need(all(counts[(2, template)] == 441 for template in surviving_second),
         "SHIFT2 exact-template replication")
    need(len(counts) == 40, "used exact-template census")

    first_translation = Counter(translation_signature(shape)
                                for shape in first_templates)
    second_translation = Counter(translation_signature(second_templates[index])
                                 for index in surviving_second)
    first_class_census = Counter((len(signature), multiplicity)
                                 for signature, multiplicity in first_translation.items())
    need(first_class_census == Counter({(5, 4): 1, (5, 5): 1, (5, 12): 1,
                                       (6, 8): 1, (7, 1): 1}),
         "SHIFT1 translation-isomorphism census")
    need(len(second_translation) == 1
         and next(iter(second_translation.values())) == 10,
         "SHIFT2 translation-isomorphism census")

    used = (tuple((shape, SHIFT1) for shape in first_templates)
            + tuple((second_templates[index], SHIFT2) for index in surviving_second))
    unpointed = Counter((len(shape), affine_role_signature(shape, shift))
                        for shape, shift in used)
    need(unpointed == Counter({
        (5, ((0, 1, 2, 3, 4), None)): 31,
        (6, ((0, 1, 2, 3, 4, 5), None)): 8,
        (7, ((0, 1, 2, 3, 4, 5, 6), None)): 1,
    }), "affine packet-isomorphism census")

    pointed = Counter()
    for shape, shift in used:
        for role in range(len(shape)):
            pointed[(len(shape), affine_role_signature(shape, shift, role))] += 1
    need(pointed == Counter({
        (5, ((0, 1, 2, 3, 4), 0)): 62,
        (5, ((0, 1, 2, 3, 4), 1)): 62,
        (5, ((0, 1, 2, 3, 4), 2)): 31,
        (6, ((0, 1, 2, 3, 4, 5), 0)): 48,
        (7, ((0, 1, 2, 3, 4, 5, 6), 0)): 7,
    }), "pointed red-role isomorphism census")
    exact_role_buckets = sum(len(shape) for shape, _shift in used)
    need(exact_role_buckets == 210, "exact-template red-role bucket census")
    return surviving_second, first_class_census, unpointed, pointed


def cyclic_role_permutation(shape, shift, step):
    """Permutation induced by translating a full cyclic packet by `step`."""
    place = {point: role for role, point in enumerate(shape)}
    permutation = tuple(place[trans(point, shift, step)] for point in shape)
    need(tuple(sorted(permutation)) == tuple(range(len(shape))),
         "cyclic role map is not a permutation")
    return permutation


def transported_rows(shape, lift, role_permutation=None):
    need(len(shape) == len(lift.role_codes), "shape/lift role mismatch")
    role = {point: index for index, point in enumerate(shape)}
    if role_permutation is None:
        role_permutation = tuple(range(len(shape)))
    need(tuple(sorted(role_permutation)) == tuple(range(len(shape))),
         "invalid transported role permutation")
    plan = validate_template_rows(shape)
    incidence = Counter()
    rows = []
    for x, middle, z in plan:
        ix, iy, iz = (role_permutation[role[x]],
                      role_permutation[role[middle]],
                      role_permutation[role[z]])
        dx, dy, dz = (lift.role_codes[ix], lift.role_codes[iy], lift.role_codes[iz])
        delta = tuple(dx[k]+dz[k]-2*dy[k] for k in range(4))
        need(all(value % Q == 0 for value in delta),
             "transported row lost midpoint congruence")
        carry = tuple(value // Q for value in delta)
        raw = sum((dx[k]-dz[k])**2 for k in range(4))
        need(raw > 0, "transported row has zero cost")
        incidence[ix] += 1
        incidence[iz] += 1
        incidence[iy] -= 2
        rows.append((ix, iy, iz, carry, raw))
    need(set(incidence) == set(range(len(shape)))
         and all(incidence[index] == 0 for index in range(len(shape))),
         "transported potential incidence does not cancel")
    need(sum(row[-1] for row in rows) > 0, "transported aggregate cost vanished")
    return tuple(rows)


def physical_point(code, offset):
    need(len(code) == len(offset) == 4, "physical point dimension")
    need(all(0 < value < 1 for value in offset), "offset reached a box boundary")
    point = tuple((Fraction(code[index]) + offset[index]) / Q for index in range(4))
    need(all(0 <= value < 1 for value in point), "physical point left the torus chart")
    return point


def verify_paired_cycle(shape, left, right, left_red_role, right_red_role,
                        right_permutation=None):
    """Check one exact seven-row horizon-two Farkas cycle."""
    need(left.family == right.family == 1
         and left.template == right.template, "paired lifts use different templates")
    need(left.support != right.support
         and set(left.support).isdisjoint(right.support), "paired lifts are not distinct")
    need(0 <= left_red_role < len(shape)
         and 0 <= right_red_role < len(shape), "invalid red role")
    if right_permutation is None:
        right_permutation = tuple(range(len(shape)))
    need(right_permutation[left_red_role] == right_red_role,
         "right role map does not align the red vertices")
    left_rows = transported_rows(shape, left)
    right_rows = transported_rows(shape, right, right_permutation)

    words = tuple(physical_point(left.role_codes[role], OFFSET_LEFT)
                  + physical_point(right.role_codes[right_permutation[role]],
                                   OFFSET_RIGHT)
                  for role in range(len(shape)))
    symbol_pairs = tuple((left.role_vertices[role],
                          right.role_vertices[right_permutation[role]])
                         for role in range(len(shape)))
    need(len(words) == len(set(words)) == 7, "paired global words collided")
    # The common role is red in both packets; all other roles are blue in both.
    parities = tuple(((role == left_red_role)
                      + (right_permutation[role] == right_red_role)) % 2
                     for role in range(len(shape)))
    need(parities == (0,)*len(shape), "paired word left the even-red language")

    incidence = Counter()
    total_cost = Fraction(0)
    semantic_rows = []
    for left_row, right_row in zip(left_rows, right_rows):
        ix, iy, iz = left_row[:3]
        need(tuple(right_permutation[role] for role in (ix, iy, iz))
             == right_row[:3], "coordinatewise row mismatch")
        x, middle, z = words[ix], words[iy], words[iz]
        delta = tuple(x[k]+z[k]-2*middle[k] for k in range(8))
        need(all(value.denominator == 1 for value in delta),
             "physical row is not a torus midpoint")
        expected_carry = left_row[3] + right_row[3]
        need(tuple(int(value) for value in delta) == expected_carry,
             "physical row carry mismatch")
        cost = sum((x[k]-z[k])**2 for k in range(8))
        expected_cost = Fraction(left_row[4]+right_row[4], Q**2)
        need(cost == expected_cost > 0, "physical squared cost mismatch")
        incidence[symbol_pairs[ix]] += 1
        incidence[symbol_pairs[iz]] += 1
        incidence[symbol_pairs[iy]] -= 2
        total_cost += cost
        semantic_rows.append((ix, iy, iz, expected_carry, str(cost)))
    need(set(incidence) == set(symbol_pairs)
         and all(incidence[word] == 0 for word in symbol_pairs),
         "global potential incidence does not cancel")
    need(total_cost > 0, "global Farkas cost is not strict")
    return total_cost, tuple(semantic_rows), symbol_pairs


def duplicate_role_pair(red_roles, role_count):
    """Return a duplicate role bucket, if one exists."""
    buckets = [[] for _ in range(role_count)]
    for lift_index, role in enumerate(red_roles):
        need(0 <= role < role_count, "red selection left its packet")
        buckets[role].append(lift_index)
    best = max(buckets, key=len)
    return (len(best), tuple(best[:2]) if len(best) >= 2 else None)


def planted_failures(shape, left, right):
    # Different red roles make two mixed-color words; the paired seven-word
    # support is then not contained in the even-parity language.
    left_red, right_red = 0, 1
    bad = tuple(((role == left_red)+(role == right_red)) % 2
                for role in range(len(shape)))
    need(sum(bad) == 2, "mismatched-red-role mutation escaped")
    # A non-common fine offset destroys the exact midpoint equation in a
    # coordinate where a transported row has nonzero incidence.
    rows = transported_rows(shape, left)
    ix, iy, iz = rows[0][:3]
    offsets = [OFFSET_LEFT, OFFSET_LEFT, OFFSET_LEFT]
    offsets[1] = tuple(value+Fraction(1, 1000) for value in OFFSET_LEFT)
    points = [physical_point(left.role_codes[role], offsets[position])
              for position, role in enumerate((ix, iy, iz))]
    delta = tuple(points[0][k]+points[2][k]-2*points[1][k] for k in range(4))
    need(any(value.denominator != 1 for value in delta),
         "non-common-offset mutation escaped")
    # Seven copies can use all seven roles without repetition.  The actual
    # theorem needs 441 copies (indeed, any eight would already suffice).
    multiplicity, pair = duplicate_role_pair(tuple(range(7)), 7)
    need((multiplicity, pair) == (1, None), "sub-pigeonhole mutation escaped")
    need(set(left.support).isdisjoint(right.support), "ownership overlap mutation escaped")


def main():
    source_before = Path(__file__).read_bytes()
    first_templates, second_templates, first, second, all_lifts = reconstruct_packets()
    surviving_second, translation_classes, unpointed, pointed = verify_classification(
        first_templates, second_templates, first, second)

    size7_templates = [(index, shape) for index, shape in enumerate(first_templates)
                       if len(shape) == 7]
    need(size7_templates == [(6, EXPECTED_SIZE7_SHAPE)],
         "unique size-seven prototype identity")
    template_index, shape = size7_templates[0]
    size7_lifts = tuple(lift for lift in first if lift.template == template_index)
    need(len(size7_lifts) == 9*R**2 == 441, "size-seven lift census")
    need(len({lift.support for lift in size7_lifts}) == 441,
         "size-seven lifts are not distinct")

    # Check that the same exact row plan transports to every possible lift.
    cyclic_permutations = tuple(cyclic_role_permutation(shape, SHIFT1, step)
                                for step in range(7))
    need(len(set(cyclic_permutations)) == 7, "cyclic automorphisms collapsed")
    # Every cyclic red-role alignment transports the packet on every lift.
    lift_costs = tuple(sum(row[-1] for row in transported_rows(shape, lift, permutation))
                       for lift in size7_lifts
                       for permutation in cyclic_permutations)
    need(all(cost > 0 for cost in lift_costs), "a size-seven lift lost strictness")

    # Universal pigeonhole step.  For every map from 441 lifts to seven red
    # roles, some role class has size at least ceil(441/7)=63, hence supplies
    # two distinct same-role lifts.  Round-robin realizes the sharp 63 bound.
    forced_multiplicity = (len(size7_lifts)+len(shape)-1)//len(shape)
    need(forced_multiplicity == 63 >= 2, "pigeonhole lower bound")
    adversarial_roles = tuple(index % len(shape) for index in range(len(size7_lifts)))
    multiplicity, pair_indices = duplicate_role_pair(adversarial_roles, len(shape))
    need((multiplicity, pair_indices) == (63, (0, 7)),
         "sharp round-robin pigeonhole control")
    left, right = size7_lifts[pair_indices[0]], size7_lifts[pair_indices[1]]

    # The geometry is independent of which common role is red.  Check every
    # one of the seven possible pointed cases on an exact physical packet.
    cycles = tuple(verify_paired_cycle(shape, left, right, red_role, red_role)
                   for red_role in range(len(shape)))
    total_costs = {cycle[0] for cycle in cycles}
    row_digests = {canonical_digest(cycle[1]) for cycle in cycles}
    word_digests = {canonical_digest(cycle[2]) for cycle in cycles}
    need(len(total_costs) == len(row_digests) == len(word_digests) == 1,
         "red role changed the physical Farkas packet")
    total_cost = next(iter(total_costs))
    need(total_cost > 0, "representative paired packet is not strict")

    # Stronger than the literal-role pigeonhole: the full size-seven orbit has
    # a transitive cyclic automorphism group.  Hence any two lifts can align
    # any ordered pair of red roles.  Check all 7^2 pointed cases exactly.
    pointed_cycles = []
    for left_red in range(7):
        for right_red in range(7):
            alignments = [permutation for permutation in cyclic_permutations
                          if permutation[left_red] == right_red]
            need(len(alignments) == 1, "red-role alignment is not unique")
            pointed_cycles.append(verify_paired_cycle(
                shape, left, right, left_red, right_red, alignments[0]))
    need(len(pointed_cycles) == 49
         and all(cycle[0] > 0 for cycle in pointed_cycles),
         "an arbitrary pointed size-seven pair escaped")
    pointed_costs = {cycle[0] for cycle in pointed_cycles}
    planted_failures(shape, left, right)
    need(Path(__file__).read_bytes() == source_before, "replay mutated its source")

    print("PASS_Q42_HORIZON2_PARITY_WALL")
    print("PACKETS first=13230 second=4410 total=17640 support=92610")
    print("TEMPLATES exact_used=40 each_lifts=441 exact_pointed_buckets=210")
    print(f"SECOND_SURVIVORS indices={surviving_second}")
    print("TRANSLATION_CLASSES first=5 second=1")
    print("AFFINE_TYPES unpointed=3 pointed_red_roles=5")
    print(f"SIZE7 prototype_index={template_index} lifts={len(size7_lifts)} roles=7")
    print(f"PIGEONHOLE forced_same_role_multiplicity={forced_multiplicity}")
    print("AUTOMORPHISMS cyclic=7 arbitrary_red_role_pairs_checked=49")
    print(f"GLOBAL_PACKET words=7 rows=7 exact_total_cost={total_cost}")
    print(f"GLOBAL_COST_RANGE arbitrary_roles={min(pointed_costs)}..{max(pointed_costs)}")
    print(f"GLOBAL_ROW_DIGEST {next(iter(row_digests))}")
    print(f"GLOBAL_WORD_DIGEST {next(iter(word_digests))}")
    print("OWNERSHIP distinct_half_open_fine_boxes offsets_strictly_interior")
    print("CONCLUSION no_single_valued_global_coercive_potential_at_horizon_2")
    print("PLANTED_FAILURES_REJECTED")
    print("SOURCE_NONMUTATION_OK")


if __name__ == "__main__":
    main()

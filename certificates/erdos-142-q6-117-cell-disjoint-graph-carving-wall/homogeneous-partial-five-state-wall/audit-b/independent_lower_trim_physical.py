#!/usr/bin/env python3
"""Hash-bound hostile replay of lower SCCs, trim scope, and q42 geometry."""

from __future__ import annotations

import argparse
import hashlib
from collections import Counter, deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations, product
from math import gcd, lcm
from pathlib import Path


B, R, TOTAL = 263_277, 17_640, 280_917
GATE = Fraction(1_058_841, 4)
Q = 42
Q0, SUBQ = 6, 7
UNDEFINED = -1
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFF = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
       (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
SHIFT1, SHIFT2 = (6, 12), (0, 6)
SIZE7 = ((2, 29), (8, 41), (14, 11), (20, 23),
         (26, 35), (32, 5), (38, 17))
ROLES = (
    (21, 14, 23, 1), (21, 14, 29, 13), (21, 14, 35, 25),
    (21, 14, 41, 37), (21, 14, 5, 7), (21, 14, 11, 19),
    (21, 14, 17, 31),
)
PLAN = ((1, 0, 6), (0, 1, 2), (0, 2, 4), (1, 3, 5),
        (3, 4, 5), (4, 5, 6), (2, 6, 3))

SOURCE_HASHES = {
    "AT_MOST_FIVE_STATE_SUNFLOWER_WALL.md":
        "6fa6b6b2fb2a113f837e37960a63edb17c759691af982fa24e3a6ab3c575eb72",
    "exhaust_five_state_orbits.cpp":
        "2f311d5aa389cca75ba75c1d21a6fc13d8612ba013a952704a8163103e00c6cb",
    "verify_lower_state_live_sccs.py":
        "b59ac9c7da552ff520755a43ebd317c51b0d5ebdfd41ae835a90515e9d9b1139",
    "run.ps1":
        "302a244d71a4f5668239c388cc4ba6237ea44a54a3b9a4999ccdd1bd87038631",
    "run.sh":
        "853d765139a5839ae4f90fe357abf13a1f96115ce6389f499195cd229d947c74",
}

EXPECTED_LOWER = {
    1: (4, 4, 1, 1, Counter({1: 1}), 2),
    2: (81, 25, 17, 15, Counter({1: 8, 2: 32, 3: 22, 4: 6}), 10),
    3: (4096, 828, 644, 566,
        Counter({1: 288, 2: 1386, 3: 2148, 4: 1254,
                 5: 390, 6: 162, 7: 108, 8: 42, 9: 18}), 39),
    4: (390625, 60654, 49662, 44370,
        Counter({1: 23112, 2: 119040, 3: 245520, 4: 228000,
                 5: 115800, 6: 40320, 7: 13152, 8: 5304,
                 9: 2232, 10: 720, 11: 216, 12: 312,
                 13: 360, 14: 264, 15: 168, 16: 72}), 124),
}


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def bind_source(source: Path):
    actual = {
        name: hashlib.sha256((source / name).read_bytes()).hexdigest()
        for name in SOURCE_HASHES
    }
    check(actual == SOURCE_HASHES, "frozen source hashes")
    manifest = {}
    for line in (source / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        manifest[name] = digest
    check(manifest == SOURCE_HASHES, "frozen source manifest")
    check(hashlib.sha256((source / "SHA256SUMS").read_bytes()).hexdigest()
          == "2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71",
          "source manifest hash")
    theorem = (source / "AT_MOST_FIVE_STATE_SUNFLOWER_WALL.md").read_text(
        encoding="utf-8")
    for phrase in (
            "accepted-language rate", "live trim", "lambda=rho(W)",
            "ambient unreachable or\nnoncoaccessible sink is deliberately irrelevant",
            "choose exactly one red box in each of its 17,640 packets",
            "color every other\nq42 box blue",
            "not an arbitrary coloring having the same global counts",
            "any one actual size-seven packet from the\nfrozen packing",
            "without one red role in\nevery packed packet",
            "Not proved: a wall for six or more states",
            "avoidance remains only a necessary escape"):
        check(phrase in theorem, f"scope phrase: {phrase}")


def translate(point, shift, step):
    return ((point[0] + step * shift[0]) % Q,
            (point[1] + step * shift[1]) % Q)


def prototype_support():
    return frozenset(((SUBQ * dx + s) % Q, (SUBQ * dy + t) % Q)
                     for dx, dy in OFF
                     for s, t in product(range(SUBQ), repeat=2))


@lru_cache(None)
def balanced_rows(packet):
    points = tuple(packet)
    place = {point: index for index, point in enumerate(points)}
    choices = []
    for middle in points:
        rows = []
        for left, right in combinations((point for point in points
                                         if point != middle), 2):
            if all((left[j] + right[j] - 2 * middle[j]) % Q == 0
                   for j in range(2)):
                rows.append((left, middle, right))
        if not rows:
            return None
        choices.append(tuple(rows))
    degrees = [0] * len(points)

    def select(index):
        if index == len(points):
            return degrees == [2] * len(points)
        for left, _, right in choices[index]:
            il, ir = place[left], place[right]
            if degrees[il] >= 2 or degrees[ir] >= 2:
                continue
            degrees[il] += 1
            degrees[ir] += 1
            if select(index + 1):
                return True
            degrees[il] -= 1
            degrees[ir] -= 1
        return False

    return True if select(0) else None


def usable_prototypes(shift):
    support = prototype_support()
    order = lcm(Q // gcd(Q, shift[0]), Q // gcd(Q, shift[1]))
    check(order == 7, "prototype translation order")
    orbits = {tuple(sorted(translate(point, shift, step) for step in range(7)))
              for point in support}
    intersections = tuple(sorted(tuple(point for point in orbit if point in support)
                                 for orbit in orbits))
    usable = tuple(shape for shape in intersections
                   if len(shape) >= 3 and balanced_rows(shape) is not None)
    flat = tuple(point for shape in usable for point in shape)
    check(len(flat) == len(set(flat)), "prototype support disjointness")
    if shift == SHIFT1:
        check(Counter(map(len, intersections)) ==
              Counter({1: 51, 2: 44, 3: 58, 4: 41,
                       5: 21, 6: 8, 7: 1}), "first prototype orbit census")
        check(Counter(map(len, usable)) == Counter({5: 21, 6: 8, 7: 1}),
              "first usable prototype census")
    else:
        check(shift == SHIFT2, "second prototype shift")
        check(Counter(map(len, intersections)) ==
              Counter({1: 70, 2: 70, 3: 49, 4: 35, 5: 28}),
              "second prototype orbit census")
        check(Counter(map(len, usable)) == Counter({5: 28}),
              "second usable prototype census")
    return usable


def packet_coloring_scope():
    coarse = tuple((a, b, (a + dx) % Q0, (b + dy) % Q0)
                   for a, b in BASE for dx, dy in OFF)
    check(len(coarse) == len(set(coarse)) == 117, "coarse q42 geometry")
    codes = tuple(tuple(SUBQ * coarse[index][coordinate] + residual[coordinate]
                        for coordinate in range(4))
                  for index in range(len(coarse))
                  for residual in product(range(SUBQ), repeat=4))
    check(len(codes) == len(set(codes)) == TOTAL, "fine q42 alphabet")
    code_id = {code: index for index, code in enumerate(codes)}

    def lift(templates, forbidden=frozenset()):
        packets = []
        for (a, b), r0, r1, shape in product(
                BASE, range(SUBQ), range(SUBQ), templates):
            first = (SUBQ * a + r0, SUBQ * b + r1)
            packet = tuple(sorted(code_id[(first[0], first[1],
                                           (x + SUBQ * a) % Q,
                                           (y + SUBQ * b) % Q)]
                                  for x, y in shape))
            if forbidden.isdisjoint(packet):
                packets.append(packet)
        flat = tuple(vertex for packet in packets for vertex in packet)
        check(len(flat) == len(set(flat)), "within-layer packet disjointness")
        return tuple(sorted(packets))

    first_templates = usable_prototypes(SHIFT1)
    second_templates = usable_prototypes(SHIFT2)
    first = lift(first_templates)
    first_vertices = frozenset(vertex for packet in first for vertex in packet)
    second = lift(second_templates, first_vertices)
    packets = first + second
    vertices = tuple(vertex for packet in packets for vertex in packet)
    check((len(first), len(second), len(packets)) == (13230, 4410, R),
          "packet layer census")
    check(len(vertices) == len(set(vertices)) == 92610,
          "global support disjointness")
    check(Counter(map(len, packets)) == Counter({5: 13671, 6: 3528, 7: 441}),
          "packet size histogram")
    check(tuple(shape for shape in first_templates if len(shape) == 7) == (SIZE7,),
          "unique cyclic size-seven prototype")

    # Vary the selected index with the packet number.  Disjoint support proves
    # the same count and one-red property for every independent choice.
    red = frozenset(packet[index % len(packet)]
                    for index, packet in enumerate(packets))
    check(len(red) == R, "one distinct red per packet")
    check(all(sum(vertex in red for vertex in packet) == 1 for packet in packets),
          "exactly one red role in every packet")
    blue = frozenset(range(TOTAL)) - red
    check(len(blue) == B and red.isdisjoint(blue), "every other q42 box blue")
    return len(packets), Counter(map(len, packets)), len(vertices)


def strongly_connected(delta, states):
    reach = [(1 << source) for source in range(states)]
    for source in range(states):
        for target in delta[2 * source:2 * source + 2]:
            if target >= 0:
                reach[source] |= 1 << target
    for middle in range(states):
        for source in range(states):
            if reach[source] >> middle & 1:
                reach[source] |= reach[middle]
    return all(mask == (1 << states) - 1 for mask in reach)


def weighted_matrix(delta, states):
    matrix = [[0] * states for _ in range(states)]
    for source in range(states):
        for bit, weight in ((0, B), (1, R)):
            target = delta[2 * source + bit]
            if target >= 0:
                matrix[source][target] += weight
    return tuple(tuple(row) for row in matrix)


def determinant(matrix):
    size = len(matrix)
    answer = 0
    for permutation in permutations(range(size)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(size) for j in range(i + 1, size))
        term = 1
        for row in range(size):
            term *= matrix[row][permutation[row]]
        answer += -term if inversions & 1 else term
    return answer


def rate_above(matrix, scalar):
    numerator, denominator = scalar.numerator, scalar.denominator
    states = len(matrix)
    for size in range(1, states + 1):
        for subset in combinations(range(states), size):
            minor = tuple(
                tuple((numerator if i == j else 0)
                      - denominator * matrix[subset[i]][subset[j]]
                      for j in range(size))
                for i in range(size))
            check(all(minor[i][j] <= 0 for i in range(size)
                      for j in range(size) if i != j), "Z-matrix signs")
            if determinant(minor) < 0:
                return True
    return False


def successor_counts(delta, counts, column):
    states = len(counts)
    output = [0] * states
    if column in (0, 1):
        for source, count in enumerate(counts):
            if not count:
                continue
            target = delta[2 * source + column]
            if target < 0:
                return None
            output[target] += count
        return tuple(output)

    selected = column - 2
    if not counts[selected]:
        return None
    red_target = delta[2 * selected + 1]
    if red_target < 0:
        return None
    output[red_target] += 1
    for source, count in enumerate(counts):
        blue_count = count - int(source == selected)
        if not blue_count:
            continue
        blue_target = delta[2 * source]
        if blue_target < 0:
            return None
        output[blue_target] += blue_count
    return tuple(output)


def singleton_horizons(delta, states, start, keep_words=False):
    initial = (tuple(7 if q == start else 0 for q in range(states)), False)
    queue = deque([initial])
    distance = {initial: 0}
    previous = {} if keep_words else None
    targets = {}
    while queue:
        counts, active = node = queue.popleft()
        if active and max(counts) == 7:
            target = counts.index(7)
            targets.setdefault(target, distance[node])
        for column in range(2 + states):
            image = successor_counts(delta, counts, column)
            if image is None:
                continue
            nxt = (image, active or column >= 2)
            if nxt in distance:
                continue
            distance[nxt] = distance[node] + 1
            if previous is not None:
                previous[nxt] = (node, column)
            queue.append(nxt)
    return targets, len(distance), previous


def lower_census():
    results = {}
    for states in range(1, 5):
        tables = strong = above_blue = above_gate = 0
        horizons = Counter()
        maximum_reached = 0
        for delta in product(range(-1, states), repeat=2 * states):
            tables += 1
            if not strongly_connected(delta, states):
                continue
            strong += 1
            matrix = weighted_matrix(delta, states)
            high_blue = rate_above(matrix, Fraction(B))
            high_gate = rate_above(matrix, GATE)
            above_gate += high_gate
            check(not high_gate or high_blue, "gate implies above blue")
            if not high_blue:
                continue
            above_blue += 1
            for start in range(states):
                found, reached, _ = singleton_horizons(delta, states, start)
                check(len(found) == states, f"missing lower witness n={states}")
                horizons.update(found.values())
                maximum_reached = max(maximum_reached, reached)
        result = (tables, strong, above_blue, above_gate, horizons, maximum_reached)
        check(result == EXPECTED_LOWER[states], f"lower census n={states}")
        results[states] = (tables, strong, above_blue, above_gate,
                           sum(horizons.values()), tuple(sorted(horizons.items())),
                           maximum_reached)
    return results


def accepted(delta, start, accepts, word):
    state = start
    for bit in word:
        state = delta[2 * state + bit]
        if state < 0:
            return False
    return state in accepts


def trim_and_dead_sink_control():
    delta = (0, 1, 1, 1)
    accepts = frozenset({0})
    for length in range(10):
        words = tuple(word for word in product((0, 1), repeat=length)
                      if accepted(delta, 0, accepts, word))
        check(words == ((0,) * length,), "dead-sink accepted language")
    ambient = weighted_matrix(delta, 2)
    check(ambient == ((B, R), (0, TOTAL)), "dead-sink ambient matrix")
    check(rate_above(ambient, Fraction(B)), "dead-sink ambient rho")
    trim = weighted_matrix((0, UNDEFINED), 1)
    check(trim == ((B,),) and not rate_above(trim, Fraction(B)),
          "dead-sink live trim")
    check(B**8 == sum(B ** (8 - sum(word)) * R ** sum(word)
                          for word in product((0, 1), repeat=8)
                          if accepted(delta, 0, accepts, word)),
          "dead-sink accepted physical mass")


def validate_multisunflower(delta, start, target, words):
    check(len(words) == 7 and len({len(word) for word in words}) == 1,
          "witness shape")
    active = False
    for column in zip(*words):
        weight = sum(column)
        check(weight in (0, 1, 7), "witness column")
        active |= weight == 1
    check(active, "witness activity")
    for word in words:
        check(accepted(delta, start, frozenset({target}), word),
              "witness accepted path")


def reconstruct_words(delta, states, start, target):
    found, _, previous = singleton_horizons(delta, states, start, keep_words=True)
    check(target in found, "planted target")
    goal = (tuple(7 if q == target else 0 for q in range(states)), True)
    labels = []
    while goal in previous:
        parent, label = previous[goal]
        labels.append(label)
        goal = parent
    labels.reverse()
    roles = [start] * 7
    words = [[] for _ in range(7)]
    for label in labels:
        column = [0] * 7
        if label < 2:
            column = [label] * 7
        else:
            selected = label - 2
            role = roles.index(selected)
            column[role] = 1
        for i, bit in enumerate(column):
            words[i].append(bit)
            roles[i] = delta[2 * roles[i] + bit]
    output = tuple(tuple(word) for word in words)
    validate_multisunflower(delta, start, target, output)
    return output


def reducible_singleton_exit_control():
    # Common blue prefix enters SCC {1,2}; one common red suffix exits state 2.
    full = (1, UNDEFINED, 1, 2, 1, 3, 3, UNDEFINED)
    block = (0, 1, 0, UNDEFINED)
    check(rate_above(weighted_matrix(block, 2), Fraction(B)),
          "planted SCC rate")
    internal = reconstruct_words(block, 2, 0, 1)
    lifted = tuple((0,) + word + (1,) for word in internal)
    validate_multisunflower(full, 0, 3, lifted)
    return internal, lifted


def circle_square(left, right):
    difference = abs(left - right)
    return min(difference, Q - difference) ** 2


def physical_geometry():
    incidence = Counter()
    for left, middle, right in PLAN:
        incidence[left] += 1
        incidence[right] += 1
        incidence[middle] -= 2
    check(all(incidence[role] == 0 for role in range(7)), "balanced incidence")

    raw_costs, wrapped_costs, ledgers = [], [], []
    for shift in range(7):
        shifted = tuple(ROLES[(role + shift) % 7] for role in range(7))
        raw = wrapped = 0
        ledger = []
        for left, middle, right in PLAN:
            x, y, z = shifted[left], shifted[middle], shifted[right]
            residual = tuple(x[j] + z[j] - 2 * y[j] for j in range(4))
            check(all(value % Q == 0 for value in residual), "plan midpoint row")
            ledger.append(tuple(value // Q for value in residual))
            raw += sum((x[j] - z[j]) ** 2 for j in range(4))
            wrapped += sum(circle_square(x[j], z[j]) for j in range(4))

        modular_rows = tuple(
            (x, y, z) for x, y, z in product(shifted, repeat=3)
            if all((x[j] + z[j] - 2 * y[j]) % Q == 0 for j in range(4)))
        check(len(modular_rows) == 49, "all modular midpoint rows")
        diagonal = tuple(row for row in modular_rows if row[0] == row[2])
        check(len(diagonal) == 7 and all(x == y == z for x, y, z in diagonal),
              "same-endpoint seam")
        raw_costs.append(Fraction(raw, Q**2))
        wrapped_costs.append(Fraction(wrapped, Q**2))
        ledgers.append(tuple(ledger))

    check(tuple(raw_costs) == (
        Fraction(16, 7), Fraction(22, 7), Fraction(20, 7), Fraction(24, 7),
        Fraction(22, 7), Fraction(18, 7), Fraction(18, 7)), "raw costs")
    check(tuple(wrapped_costs) == (Fraction(11, 7),) * 7, "wrapped costs")
    return tuple(raw_costs), tuple(wrapped_costs), tuple(ledgers)


_PHYSICAL = None


def physical_lift(words, red_role):
    global _PHYSICAL
    if _PHYSICAL is None:
        _PHYSICAL = physical_geometry()
    raw_costs, wrapped_costs, _ = _PHYSICAL
    physical_words = [[] for _ in range(7)]
    unit_shifts = []
    total_raw = total_wrapped = Fraction(0)
    for column in zip(*words):
        weight = sum(column)
        if weight == 0:
            symbols = (ROLES[(red_role + 1) % 7],) * 7
        elif weight == 7:
            symbols = (ROLES[red_role],) * 7
        else:
            check(weight == 1, "lift column weight")
            unique = column.index(1)
            shift = (red_role - unique) % 7
            unit_shifts.append(shift)
            symbols = tuple(ROLES[(role + shift) % 7] for role in range(7))
            total_raw += raw_costs[shift]
            total_wrapped += wrapped_costs[shift]
        for role, symbol in enumerate(symbols):
            check((symbol == ROLES[red_role]) == bool(column[role]), "lift color")
            physical_words[role].append(symbol)
    check(len({tuple(word) for word in physical_words}) == 7,
          "seven physically distinct words")
    check(total_raw == sum((raw_costs[s] for s in unit_shifts), Fraction()),
          "lift raw cost")
    check(total_wrapped == len(unit_shifts) * Fraction(11, 7),
          "lift wrapped cost")


def maximum_witness():
    exceptional = tuple(map(int, "1000110001100011000110001"))
    repeated = tuple(map(int, "1000000000000000000000001"))
    words = (exceptional,) + (repeated,) * 6
    delta = (UNDEFINED, 1, 2, UNDEFINED, 3, UNDEFINED,
             4, UNDEFINED, 1, 0)
    validate_multisunflower(delta, 0, 0, words)
    for red_role in range(7):
        physical_lift(words, red_role)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    bind_source(args.source)
    print("PASS_FROZEN_FIVE_STATE_HASH_SCOPE_CONTRACT")
    trim_and_dead_sink_control()
    print("PASS_ACCEPTED_RATE_LIVE_TRIM_DEAD_SINK_CONTROL")
    lower = lower_census()
    print("PASS_INDEPENDENT_LOWER_ONE_THROUGH_FOUR_CENSUS")
    internal, lifted = reducible_singleton_exit_control()
    print("PASS_REDUCIBLE_PREFIX_SINGLETON_TARGET_SUFFIX_CONTROL")
    packing = packet_coloring_scope()
    print("PASS_Q42_DISJOINT_ONE_RED_PER_PACKET_COLORING_SCOPE")
    raw, wrapped, carries = physical_geometry()
    maximum_witness()
    print("PASS_Q42_ALL_ROWS_CARRIES_COSTS_AND_PHYSICAL_LIFT")
    print(f"LOWER={lower}")
    print(f"PLANTED_LENGTHS={len(internal[0])},{len(lifted[0])}")
    print(f"PACKING={packing}")
    print(f"RAW={raw} WRAPPED={wrapped}")
    for shift, ledger in enumerate(carries):
        print(f"CARRIES shift={shift} ledger={ledger}")
    print("NONCLAIM=no_six_state_wall_no_box_sensitive_wall_no_potential_from_avoidance")
    print("VERDICT_APPROVE")


if __name__ == "__main__":
    main()

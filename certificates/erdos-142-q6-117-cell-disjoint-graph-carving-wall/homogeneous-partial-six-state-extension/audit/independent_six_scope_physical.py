#!/usr/bin/env python3
"""Independent hash, live-trim, SCC-lift, packing, and q42 replay for n<=6."""

from __future__ import annotations

import argparse
import hashlib
from collections import Counter, deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import gcd, lcm
from pathlib import Path


B, R, TOTAL = 263_277, 17_640, 280_917
GATE = Fraction(1_058_841, 4)
Q, Q0, SUBQ = 42, 6, 7
U = -1

SOURCE_PAYLOADS = {
    "AT_MOST_SIX_STATE_SUNFLOWER_WALL.md":
        "4e0059d11babefbfe6a19853b2d0b1b1d464879727d99ea49d5c5e26e3fa1bbc",
    "exhaust_six_state_orbits_cegar.cpp":
        "6f59fb09b6568f2bcb1a98d6045db1e42fbb99179263c913e97e92f77d17ce88",
    "verify_six_state_burnside.cpp":
        "50e81a587d7b67a4137031f740ffbc8d74217218d0a0569f2aacb1fc19c5b442",
    "verify_six_boundary.py":
        "7a362535f2afb528e9646540281eade02e4f03201c31daf422cad61359bee3bf",
    "verify_six_scope_physical.py":
        "607060c1d94551778db723f420db55c74d296d7b60eff5a7f60e75ab5dd241a6",
    "run.ps1":
        "cb28712f45c531afa60233a98bb728a53782db06d877045ca309dd3a09f61a7b",
    "run.sh":
        "fe83fa43245bd9ed9a90cc1257c255108c56adad95660b59864fef732a616cff",
}
SOURCE_MANIFEST = "a62da6552877464d13c45f615f1d61e9b05cee7c52e81b472db3f6a77dc97d01"

FIVE_PAYLOADS = {
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
FIVE_MANIFEST = "2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71"

BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFF = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
       (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
SHIFT1, SHIFT2 = (6, 12), (0, 6)
SIZE7 = ((2, 29), (8, 41), (14, 11), (20, 23),
         (26, 35), (32, 5), (38, 17))
ROLES = ((21, 14, 23, 1), (21, 14, 29, 13), (21, 14, 35, 25),
         (21, 14, 41, 37), (21, 14, 5, 7), (21, 14, 11, 19),
         (21, 14, 17, 31))
PLAN = ((1, 0, 6), (0, 1, 2), (0, 2, 4), (1, 3, 5),
        (3, 4, 5), (4, 5, 6), (2, 6, 3))

MAX_TABLE = (U, 1, U, 2, 3, 4, 0, U, 1, 5, 4, U)
MAX_START, MAX_TARGET = 3, 0
MAX_WORDS = tuple(tuple(map(int, word)) for word in (
    "01110111010011101001110100111010011101001110100100",
    "01100111011011101001110100111010011101001110100100",
    "01100111010011101101110100111010011101001110100100",
    "01100111010011101001110110111010011101001110100100",
    "01100111010011101001110100111011011101001110100100",
    "01100111010011101001110100111010011101101110100100",
    "01100111010011101001110100111010011101001110110100",
))


def need(condition, note):
    if not condition:
        raise AssertionError(note)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest(path):
    result = {}
    for line in path.read_text(encoding="ascii").splitlines():
        value, name = line.split("  ", 1)
        need(len(value) == 64 and name not in result, "manifest syntax")
        result[name] = value
    return result


def bind_package(path, payloads, manifest_digest, label):
    actual = {name: digest(path / name) for name in payloads}
    need(actual == payloads, f"{label} payload hashes")
    need(parse_manifest(path / "SHA256SUMS") == payloads,
         f"{label} manifest contents")
    need(digest(path / "SHA256SUMS") == manifest_digest,
         f"{label} manifest hash")


def bind_scope(source, five):
    bind_package(source, SOURCE_PAYLOADS, SOURCE_MANIFEST, "six-state")
    bind_package(five, FIVE_PAYLOADS, FIVE_MANIFEST, "five-state")
    theorem = (source / "AT_MOST_SIX_STATE_SUNFLOWER_WALL.md").read_text(
        encoding="utf-8")
    for phrase in (
            "Choose exactly one red box in\neach of its 17,640 packets",
            "not an\narbitrary coloring with the same global counts",
            "accepted-language rate",
            "Delete unreachable and noncoaccessible states",
            "Perron root of an ambient dead or unreachable component",
            "from every start to every singleton target",
            "location carries no trust",
            "pinned hashes above, never the path",
            "Not proved: seven or more states",
            "existence of a physical potential from packet\navoidance"):
        need(phrase in theorem, f"scope phrase {phrase!r}")
    joined = "\n".join((theorem,
                         (source / "run.ps1").read_text(encoding="utf-8"),
                         (source / "run.sh").read_text(encoding="utf-8")))
    need("D:\\p42_scratch" not in joined and "/mnt/d/p42_scratch" not in joined,
         "machine-local path removed")


def accepted(delta, start, targets, word):
    state = start
    for bit in word:
        state = delta[2 * state + bit]
        if state < 0:
            return False
    return state in targets


def validate_witness(delta, start, target, words):
    need(len(words) == 7 and len({len(word) for word in words}) == 1,
         "seven equal-length words")
    unit = 0
    for column in zip(*words):
        weight = sum(column)
        need(weight in (0, 1, 7), "column weight")
        unit += weight == 1
    need(unit > 0, "nondegenerate witness")
    need(all(accepted(delta, start, {target}, word) for word in words),
         "fixed-start singleton-target acceptance")
    return unit


def live_trim_and_scc_controls():
    # Reachable state 1 is a noncoaccessible high-rate sink and must be deleted.
    dead = (0, 1, 1, 1)
    for length in range(10):
        words = tuple(word for word in product((0, 1), repeat=length)
                      if accepted(dead, 0, {0}, word))
        need(words == ((0,) * length,), "dead-sink accepted language")
        weighted = sum(B ** (length - sum(word)) * R ** sum(word)
                       for word in words)
        need(weighted == B ** length, "accepted physical mass")
    need(B + R > GATE > B, "ambient/live threshold separation")

    # A common blue prefix enters a two-state SCC; a common red singleton exit
    # leaves q=2 for the accepting state 3.  This tests that no synchronized
    # multi-exit suffix is required.
    full = (1, U, 1, 2, 1, 3, 3, U)
    block = (0, 1, 0, U)
    internal = shortest_singleton_witness(block, 2, 0, 1)
    lifted = tuple((0,) + word + (1,) for word in internal)
    validate_witness(block, 0, 1, internal)
    validate_witness(full, 0, 3, lifted)
    return len(internal[0]), len(lifted[0])


def step_counts(delta, counts, label):
    states = len(counts)
    out = [0] * states
    if label < 2:
        for source, count in enumerate(counts):
            if count:
                target = delta[2 * source + label]
                if target < 0:
                    return None
                out[target] += count
    else:
        selected = label - 2
        if not counts[selected]:
            return None
        red = delta[2 * selected + 1]
        if red < 0:
            return None
        out[red] += 1
        for source, count in enumerate(counts):
            amount = count - (source == selected)
            if amount:
                blue = delta[2 * source]
                if blue < 0:
                    return None
                out[blue] += amount
    return tuple(out)


def shortest_singleton_witness(delta, states, start, target):
    initial = (tuple(7 if q == start else 0 for q in range(states)), False)
    goal = (tuple(7 if q == target else 0 for q in range(states)), True)
    queue, previous = deque([initial]), {initial: None}
    while queue and goal not in previous:
        node = queue.popleft()
        counts, active = node
        for label in range(2 + states):
            image = step_counts(delta, counts, label)
            if image is None:
                continue
            nxt = (image, active or label >= 2)
            if nxt not in previous:
                previous[nxt] = (node, label)
                queue.append(nxt)
    need(goal in previous, "planted singleton goal")
    labels = []
    node = goal
    while previous[node] is not None:
        node, label = previous[node]
        labels.append(label)
    labels.reverse()
    roles = [start] * 7
    words = [[] for _ in range(7)]
    for label in labels:
        column = [label] * 7 if label < 2 else [0] * 7
        if label >= 2:
            column[roles.index(label - 2)] = 1
        for role, bit in enumerate(column):
            words[role].append(bit)
            roles[role] = delta[2 * roles[role] + bit]
    return tuple(tuple(word) for word in words)


def translate(point, shift, count):
    return ((point[0] + count * shift[0]) % Q,
            (point[1] + count * shift[1]) % Q)


def prototype_support():
    return frozenset(((SUBQ * dx + s) % Q, (SUBQ * dy + t) % Q)
                     for dx, dy in OFF
                     for s, t in product(range(SUBQ), repeat=2))


@lru_cache(None)
def has_balanced_rows(packet):
    points = tuple(packet)
    position = {point: index for index, point in enumerate(points)}
    choices = []
    for middle in points:
        rows = tuple((left, right) for left, right in combinations(
            (point for point in points if point != middle), 2)
            if all((left[j] + right[j] - 2 * middle[j]) % Q == 0
                   for j in range(2)))
        if not rows:
            return False
        choices.append(rows)
    degrees = [0] * len(points)

    def choose(index):
        if index == len(points):
            return degrees == [2] * len(points)
        for left, right in choices[index]:
            il, ir = position[left], position[right]
            if degrees[il] == 2 or degrees[ir] == 2:
                continue
            degrees[il] += 1
            degrees[ir] += 1
            if choose(index + 1):
                return True
            degrees[il] -= 1
            degrees[ir] -= 1
        return False

    return choose(0)


def usable_prototypes(shift):
    support = prototype_support()
    order = lcm(Q // gcd(Q, shift[0]), Q // gcd(Q, shift[1]))
    need(order == 7, "translation order")
    orbits = {tuple(sorted(translate(point, shift, step)
                           for step in range(7))) for point in support}
    intersections = tuple(sorted(tuple(point for point in orbit
                                       if point in support) for orbit in orbits))
    usable = tuple(shape for shape in intersections
                   if len(shape) >= 3 and has_balanced_rows(shape))
    flat = tuple(point for shape in usable for point in shape)
    need(len(flat) == len(set(flat)), "prototype disjointness")
    expected_all = (Counter({1: 51, 2: 44, 3: 58, 4: 41,
                             5: 21, 6: 8, 7: 1}) if shift == SHIFT1 else
                    Counter({1: 70, 2: 70, 3: 49, 4: 35, 5: 28}))
    expected_usable = (Counter({5: 21, 6: 8, 7: 1}) if shift == SHIFT1 else
                       Counter({5: 28}))
    need(Counter(map(len, intersections)) == expected_all,
         "prototype orbit histogram")
    need(Counter(map(len, usable)) == expected_usable,
         "usable prototype histogram")
    return usable


def build_packing():
    coarse = tuple((a, b, (a + dx) % Q0, (b + dy) % Q0)
                   for a, b in BASE for dx, dy in OFF)
    need(len(coarse) == len(set(coarse)) == 117, "coarse alphabet")
    codes = tuple(tuple(SUBQ * coarse[index][coordinate] + residual[coordinate]
                        for coordinate in range(4))
                  for index in range(117)
                  for residual in product(range(SUBQ), repeat=4))
    need(len(codes) == len(set(codes)) == TOTAL, "q42 alphabet")
    code_id = {code: index for index, code in enumerate(codes)}

    def lift(templates, forbidden=frozenset()):
        packets = []
        for (a, b), r0, r1, shape in product(
                BASE, range(SUBQ), range(SUBQ), templates):
            first = (SUBQ * a + r0, SUBQ * b + r1)
            packet = tuple(code_id[(first[0], first[1],
                                    (x + SUBQ * a) % Q,
                                    (y + SUBQ * b) % Q)] for x, y in shape)
            if forbidden.isdisjoint(packet):
                packets.append(packet)
        flat = tuple(vertex for packet in packets for vertex in packet)
        need(len(flat) == len(set(flat)), "within-layer packet disjointness")
        return tuple(packets)

    first_templates = usable_prototypes(SHIFT1)
    second_templates = usable_prototypes(SHIFT2)
    need(tuple(shape for shape in first_templates if len(shape) == 7) == (SIZE7,),
         "unique size-seven prototype")
    first = lift(first_templates)
    first_vertices = frozenset(v for packet in first for v in packet)
    second = lift(second_templates, first_vertices)
    packets = first + second
    vertices = tuple(v for packet in packets for v in packet)
    need((len(first), len(second), len(packets)) == (13_230, 4_410, R),
         "packet layer counts")
    need(len(vertices) == len(set(vertices)) == 92_610,
         "global packet support disjointness")
    histogram = Counter(map(len, packets))
    need(histogram == Counter({5: 13_671, 6: 3_528, 7: 441}),
         "packet size histogram")

    # Varying the chosen index demonstrates arbitrary independent red choices.
    red = frozenset(packet[index % len(packet)]
                    for index, packet in enumerate(packets))
    need(len(red) == R and all(sum(v in red for v in packet) == 1
                               for packet in packets), "one red per packet")
    need(TOTAL - len(red) == B, "all other boxes blue")
    size_seven = tuple(tuple(codes[v] for v in packet)
                       for packet in packets if len(packet) == 7)
    need(len(size_seven) == 441 and ROLES in size_seven,
         "explicit actual size-seven packet")
    return packets, size_seven, histogram, len(vertices)


def packet_geometry(roles):
    raw, wrapped, ledgers = [], [], []
    for shift in range(7):
        shifted = tuple(roles[(role + shift) % 7] for role in range(7))
        raw_sum = wrapped_sum = 0
        ledger = []
        for left, middle, right in PLAN:
            x, y, z = shifted[left], shifted[middle], shifted[right]
            residue = tuple(x[j] + z[j] - 2 * y[j] for j in range(4))
            need(all(value % Q == 0 for value in residue), "midpoint row")
            ledger.append(tuple(value // Q for value in residue))
            for coordinate in range(4):
                difference = abs(x[coordinate] - z[coordinate])
                raw_sum += difference * difference
                wrapped_sum += min(difference, Q - difference) ** 2
        rows = tuple((x, y, z) for x, y, z in product(shifted, repeat=3)
                     if all((x[j] + z[j] - 2 * y[j]) % Q == 0
                            for j in range(4)))
        diagonal = tuple(row for row in rows if row[0] == row[2])
        need(len(rows) == 49, "all ordered modular rows")
        need(len(diagonal) == 7 and all(x == y == z for x, y, z in diagonal),
             "same-endpoint seam")
        raw.append(Fraction(raw_sum, Q * Q))
        wrapped.append(Fraction(wrapped_sum, Q * Q))
        ledgers.append(tuple(ledger))
    return tuple(raw), tuple(wrapped), tuple(ledgers)


def all_packet_geometry(size_seven):
    incidence = Counter()
    for left, middle, right in PLAN:
        incidence[left] += 1
        incidence[right] += 1
        incidence[middle] -= 2
    need(not any(incidence.values()), "role incidence cancellation")
    explicit = packet_geometry(ROLES)
    need(explicit[0] == tuple(map(Fraction, (Fraction(16, 7), Fraction(22, 7),
                                             Fraction(20, 7), Fraction(24, 7),
                                             Fraction(22, 7), Fraction(18, 7),
                                             Fraction(18, 7)))), "explicit raw costs")
    need(explicit[1] == (Fraction(11, 7),) * 7, "explicit wrapped costs")
    raw_histogram = Counter()
    for roles in size_seven:
        raw, wrapped, _ = packet_geometry(roles)
        need(wrapped == (Fraction(11, 7),) * 7, "all-packet wrapped costs")
        need(all(value > 0 for value in raw), "all-packet positive raw cost")
        raw_histogram.update(raw)
    need(sum(raw_histogram.values()) == 441 * 7, "all size-seven alignments")
    return explicit, raw_histogram


def physical_lift(words, red_role):
    geometry = packet_geometry(ROLES)
    physical = [[] for _ in range(7)]
    units = 0
    for column in zip(*words):
        weight = sum(column)
        if weight == 0:
            symbols = (ROLES[(red_role + 1) % 7],) * 7
        elif weight == 7:
            symbols = (ROLES[red_role],) * 7
        else:
            need(weight == 1, "lift unit column")
            unique = column.index(1)
            shift = (red_role - unique) % 7
            symbols = tuple(ROLES[(role + shift) % 7] for role in range(7))
            need(geometry[0][shift] > 0, "positive raw unit cost")
            units += 1
        for role, symbol in enumerate(symbols):
            need((symbol == ROLES[red_role]) == bool(column[role]),
                 "physical color lift")
            physical[role].append(symbol)
        for left, middle, right in PLAN:
            need(all((symbols[left][j] + symbols[right][j]
                      - 2 * symbols[middle][j]) % Q == 0 for j in range(4)),
                 "whole-word physical row")
    need(units > 0 and len({tuple(word) for word in physical}) == 7,
         "seven physically distinct lifted words")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--five", required=True, type=Path)
    args = parser.parse_args()
    bind_scope(args.source, args.five)
    print("PASS_FROZEN_SIX_AND_FIVE_HASH_SCOPE_CONTRACT")
    planted_lengths = live_trim_and_scc_controls()
    print("PASS_ACCEPTED_RATE_LIVE_TRIM_AND_SINGLETON_EXIT_CONTROL")
    packets, size_seven, histogram, support = build_packing()
    print("PASS_FULL_Q42_DISJOINT_ONE_RED_PER_PACKET_PACKING_REPLAY")
    explicit, raw_histogram = all_packet_geometry(size_seven)
    print("PASS_ALL_441_SIZE7_PACKETS_ROWS_AND_POSITIVE_RAW_COST")
    units = validate_witness(MAX_TABLE, MAX_START, MAX_TARGET, MAX_WORDS)
    need(len(MAX_WORDS[0]) == 50, "maximum horizon witness")
    for red_role in range(7):
        physical_lift(MAX_WORDS, red_role)
    print("PASS_LENGTH50_WITNESS_AND_ALL_SEVEN_RED_ROLE_PHYSICAL_LIFTS")
    print(f"PACKETS={len(packets)} HIST={histogram} SUPPORT={support}")
    print(f"PLANTED_LENGTHS={planted_lengths} MAX_UNITS={units}")
    print(f"EXPLICIT_RAW={explicit[0]} WRAPPED={explicit[1]}")
    print(f"ALL_PACKET_RAW_HIST={sorted(raw_histogram.items())}")
    print("NONCLAIM=no_n_ge_7_no_arbitrary_same_count_coloring_no_box_sensitive_transitions_no_potential_from_avoidance")
    print("PASS_INDEPENDENT_SIX_SCOPE_AND_PHYSICAL_HOSTILE_REPLAY")


if __name__ == "__main__":
    main()

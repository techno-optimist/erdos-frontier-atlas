#!/usr/bin/env python3
"""Standalone exact replay of the q=30 four-of-five one-block packing wall.

Only the Python standard library is used.  The theorem concerns one retained
union of complete globally aligned r=5 microboxes; it makes no word-language
capacity claim.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from fractions import Fraction as F
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

Q0 = 6
R = 5
Q = Q0 * R
BASE = (
    (3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
    (5, 0), (5, 1), (5, 2),
)
OFFSETS = (
    (0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
    (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3),
)
CELLS = tuple(
    (a, b, (a + dx) % Q0, (b + dy) % Q0)
    for a, b in BASE for dx, dy in OFFSETS
)
SUBS = tuple(product(range(R), repeat=4))
LABELS = tuple((cell, sub) for cell in range(len(CELLS)) for sub in SUBS)
CODES = tuple(
    tuple(R * CELLS[cell][j] + sub[j] for j in range(4))
    for cell, sub in LABELS
)
LABEL_POS = {label: i for i, label in enumerate(LABELS)}
CODE_POS = {code: i for i, code in enumerate(CODES)}
SHIFT2 = (6, 12)
CERTIFICATE = Path(__file__).with_name("independent_semantic_certificate.json")

MATCHING_DIGEST = "b4822c187ed2c8a9950d6d13eede60f6ef92b7c1635863e407d1cfc45b864298"
PACKET_SUPPORT_DIGEST = "c770ed776221672eb6ac435b46859967717ef34434b9faa63528096064b89e13"
PACKET_EXPANDED_DIGEST = "6b040b0c9975cc78386ceadadb1e34486fd66827cc46304f374e0eeb6b0fa3a7"
PAYLOAD_SEMANTIC_DIGEST = "ee456fb4a80360a39860409e261ff08879843ec0e76e124cd933d9d22058c5d2"


class ReplayError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayError(message)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def dilation_edges():
    edges = set()
    for ia, a in enumerate(CELLS):
        for ib, b in enumerate(CELLS):
            active = tuple(j for j in range(4) if a[j] != b[j])
            if not active:
                continue
            if not all(b[j] == a[j] or b[j] == (a[j] - 1) % Q0
                       for j in range(4)):
                continue
            if not any(a[j] == 0 and b[j] == Q0 - 1 for j in active):
                continue
            inactive = tuple(j for j in range(4) if j not in active)
            for values in product(range(R), repeat=len(inactive)):
                low = [0] * 4
                high = [R - 1] * 4
                for j, value in zip(inactive, values):
                    low[j] = high[j] = value
                edges.add(tuple(sorted(((ia, tuple(low)),
                                        (ib, tuple(high))))))
    return tuple(sorted(edges))


def connected_components(edges):
    adjacency = defaultdict(set)
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    todo = set(adjacency)
    answer = []
    while todo:
        root = min(todo)
        todo.remove(root)
        found = {root}
        queue = deque([root])
        while queue:
            a = queue.popleft()
            for b in adjacency[a]:
                if b in todo:
                    todo.remove(b)
                    found.add(b)
                    queue.append(b)
        answer.append(tuple(sorted(found)))
    return tuple(sorted(answer))


def canonical_matching(edges):
    """Lexicographically first exact maximum matching in each component."""
    answer = []
    for component in connected_components(edges):
        vertices = set(component)
        local = tuple(edge for edge in edges
                      if edge[0] in vertices and edge[1] in vertices)
        found = None
        for size in range(min(len(component) // 2, len(local)), -1, -1):
            for chosen in combinations(local, size):
                flat = tuple(v for edge in chosen for v in edge)
                if len(flat) == len(set(flat)):
                    found = chosen
                    break
            if found is not None:
                answer.extend(found)
                break
        require(found is not None, "component matching search failed")
    return tuple(sorted(answer))


def orient_edge(edge):
    def attempt(source, target):
        ia, low = source
        ib, high = target
        a, b = CELLS[ia], CELLS[ib]
        active = tuple(j for j in range(4) if a[j] != b[j])
        wraps = tuple(j for j in active if a[j] == 0 and b[j] == Q0 - 1)
        if not wraps:
            return None
        if not all(b[j] == a[j] or b[j] == (a[j] - 1) % Q0
                   for j in range(4)):
            return None
        if not all(low[j] == 0 and high[j] == R - 1 for j in active):
            return None
        if not all(low[j] == high[j] for j in range(4) if j not in active):
            return None
        return source, target, active, wraps

    record = attempt(*edge)
    if record is None:
        record = attempt(edge[1], edge[0])
    require(record is not None, "edge lacks strict-dilation orientation")
    return record


def scalar_row_identity(a: int, t: F):
    b = (a - 1) % Q0
    a_t = F(a + t, Q0)
    a_3t = F(a + 3*t, Q0)
    b_1t = F(b + 1 - t, Q0)
    b_13t = F(b + 1 - 3*t, Q0)

    def correction(x, y, z):
        defect = x + z - 2*y
        require(defect.denominator == 1, "nonintegral dilation carry")
        return Q0**2 * ((x-z)**2 - 2*x*x - 2*z*z + 4*y*y)

    one = correction(a_t, b_1t, b_13t)
    two = correction(a_3t, a_t, b_1t)
    if a == 0:
        require(one == 108 - 24*t and two == -36 - 24*t,
                "wrap correction identity failed")
    else:
        require(one == two == 0, "nonwrap correction is nonzero")
    return one, two


def dilation_semantics():
    edges = dilation_edges()
    components = connected_components(edges)
    matching = canonical_matching(edges)
    require(len(edges) == 2382, "wrong dilation edge census")
    require(len(components) == 1632 and max(map(len, components)) == 9,
            "wrong dilation component census")
    require(len(matching) == 1789, "wrong dilation matching count")
    endpoints = tuple(LABEL_POS[v] for edge in matching for v in edge)
    require(len(endpoints) == len(set(endpoints)) == 3578,
            "dilation matching overlaps")
    records = []
    wrap_hist = Counter()
    for edge in matching:
        source, target, active, wraps = orient_edge(edge)
        wrap_hist[len(wraps)] += 1
        records.append((LABEL_POS[source], LABEL_POS[target],
                        sum(1 << j for j in active),
                        sum(1 << j for j in wraps)))
        cell = CELLS[source[0]]
        for t in (F(1, 100), F(1, 30), F(1, 17)):
            require(0 < t < 3*t < F(1, R),
                    "dilation sample exits low microinterval")
            total = sum(sum(scalar_row_identity(cell[j], t)) for j in active)
            require(total == len(wraps) * (72 - 48*t) > 0,
                    "dilation recurrence mismatch")
    require(set(wrap_hist) <= {1, 2}, "unexpected wrap multiplicity")

    # A finite telescope beats each displayed candidate bound.  Since the
    # bound was arbitrary, the recurrence contradicts bounded correction.
    T = F(1, 2*R)
    for bound in (0, 1, 10**3, 10**9):
        steps = int((4*bound + 24*T) // 72) + 1
        coarse_lower = 72*steps - 24*T
        exact_lower = 72*steps - 24*T*(1 - F(1, 3**steps))
        require(exact_lower > coarse_lower > 4*bound,
                "finite telescope does not beat bound")
    for j in range(1, 8):
        t = T / 3**j
        require(0 < t < 3*t <= T < F(1, R),
                "low residual leaves microbox")
        require(F(R-1, R) < 1-3*t < 1-t < 1,
                "high residual leaves microbox")
    return frozenset(endpoints), tuple(records), wrap_hist


def prototype_support():
    return frozenset(
        ((R*dx+s) % Q, (R*dy+t) % Q)
        for dx, dy in OFFSETS for s, t in product(range(R), repeat=2)
    )


def add2(point, k):
    return ((point[0] + k*SHIFT2[0]) % Q,
            (point[1] + k*SHIFT2[1]) % Q)


def prototype_four_packets():
    support = prototype_support()
    ambient = {
        tuple(sorted(add2(point, k) for k in range(5)))
        for point in support
    }
    intersections = tuple(sorted(
        tuple(point for point in orbit if point in support)
        for orbit in ambient
    ))
    hist = Counter(map(len, intersections))
    require(hist == Counter({1: 48, 2: 48, 3: 39, 4: 16}),
            "wrong order-five intersection census")
    packets = tuple(packet for packet in intersections if len(packet) == 4)
    flat = tuple(point for packet in packets for point in packet)
    require(len(flat) == len(set(flat)) == 64,
            "prototype four-packets overlap")
    return packets, hist


def relative_last_pair(vertex):
    cell, sub = LABELS[vertex]
    base = cell // len(OFFSETS)
    a, b = BASE[base]
    return base, sub[0], sub[1], (
        (CODES[vertex][2] - R*a) % Q,
        (CODES[vertex][3] - R*b) % Q,
    )


def global_four_packets(blocked):
    prototypes, intersection_hist = prototype_four_packets()
    packets = []
    for base, s0, s1, prototype in product(
            range(len(BASE)), range(R), range(R), prototypes):
        a, b = BASE[base]
        first = (R*a + s0, R*b + s1)
        support = tuple(sorted(CODE_POS[
            (first[0], first[1],
             (relative[0] + R*a) % Q,
             (relative[1] + R*b) % Q)
        ] for relative in prototype))
        if blocked.isdisjoint(support):
            packets.append(support)
    packets = tuple(sorted(packets))
    flat = tuple(v for packet in packets for v in packet)
    require(len(packets) == 2852, "wrong unblocked four-packet count")
    require(len(flat) == len(set(flat)) == 11408,
            "global four-packet supports overlap")
    require(blocked.isdisjoint(flat), "packet touches dilation endpoint")
    return packets, intersection_hist


def expand_packet(packet):
    support = set(packet)
    incidence = Counter()
    rows = []
    u = (F(1, 7), F(2, 7), F(3, 7), F(4, 7))
    for y in packet:
        options = []
        others = tuple(v for v in packet if v != y)
        for x, z in combinations(others, 2):
            defect = tuple(CODES[x][j] + CODES[z][j] - 2*CODES[y][j]
                           for j in range(4))
            if all(value % Q == 0 for value in defect):
                raw = sum((CODES[x][j] - CODES[z][j])**2
                          for j in range(4))
                if raw > 0:
                    options.append((x, z, *(value // Q for value in defect), raw))
        require(len(options) == 1, "four-packet centre lacks unique row")
        row = options[0]
        x, z = row[:2]
        carries = row[2:6]
        raw = row[6]
        incidence[x] += 1
        incidence[z] += 1
        incidence[y] -= 2
        xp = tuple(F(CODES[x][j], Q) + u[j]/Q for j in range(4))
        yp = tuple(F(CODES[y][j], Q) + u[j]/Q for j in range(4))
        zp = tuple(F(CODES[z][j], Q) + u[j]/Q for j in range(4))
        require(all(xp[j] + zp[j] - 2*yp[j] == carries[j]
                    for j in range(4)), "physical midpoint sample failed")
        require(sum((xp[j]-zp[j])**2 for j in range(4)) == F(raw, Q**2),
                "physical raw cost sample failed")
        rows.append((x, y, z, *carries, raw))
    require(set(incidence) == support and all(v == 0 for v in incidence.values()),
            "packet potential incidence does not cancel")
    require(sum(row[-1] for row in rows) > 0,
            "packet aggregate raw RHS is not positive")
    return tuple(rows)


def packet_semantics(blocked):
    packets, intersection_hist = global_four_packets(blocked)
    records = tuple((packet, expand_packet(packet)) for packet in packets)
    raw_hist = Counter(row[-1] for _, rows in records for row in rows)
    carry_hist = Counter(row[3:7] for _, rows in records for row in rows)
    require(sum(raw*count for raw, count in raw_hist.items()) > 0,
            "global packet RHS is not positive")
    return packets, records, intersection_hist, raw_hist, carry_hist


def density_audit(matching_count, packet_count):
    total = len(LABELS)
    gate = F(49, 576) * Q**4
    forced = matching_count + packet_count
    require(total == 73125, "wrong microbox total")
    require(gate == F(275625, 4), "wrong gate count")
    require(total - 68907 == 4218,
            "wrong strict-above-gate deletion budget")
    require(forced == 4641 and total-forced == 68484 < gate,
            "packing does not cross gate")
    return total, gate, forced


def certificate_audit(matching_records, packets, packet_records):
    before = CERTIFICATE.read_bytes()
    payload = json.loads(before)
    require(payload["schema"] == "erdos142-q6-r5-four-of-five-one-block-wall-v1",
            "wrong certificate schema")
    require(payload["geometry"] == {
        "coarse_q": 6, "residual_subdivision": 5, "fine_q": 30,
        "coarse_cells": 117, "microboxes": 73125,
    }, "wrong certificate geometry")
    require(payload["dilation"] == {
        "edge_count": 2382, "component_count": 1632,
        "maximum_component_size": 9, "matching_count": 1789,
        "endpoint_count": 3578,
        "algorithm": "lex-first maximum matching in each sorted component",
    }, "wrong certificate dilation record")
    require(payload["four_of_five"] == {
        "shift_last_pair": [6, 12],
        "prototype_intersection_histogram": {"1": 48, "2": 48, "3": 39, "4": 16},
        "full_four_packets": 3600, "blocked_packets": 748,
        "retained_packets": 2852, "packet_size": 4,
        "row_weight": 1,
    }, "wrong certificate packet record")
    require(payload["gate"] == {
        "numerator": 49, "denominator": 576,
        "gate_count_numerator": 275625, "gate_count_denominator": 4,
        "allowed_deletions_strictly_above": 4218,
        "forced_deletions_one_block": 4641,
        "max_retained_one_block": 68484,
    }, "wrong certificate gate record")
    require(payload["scope"] == {
        "one_block_complete_aligned_microbox_union": True,
        "arbitrary_word_language_capacity": False,
        "proper_submicrobox_carving": False,
    }, "wrong scope record")
    require(payload["digests"] == {
        "dilation_semantic": MATCHING_DIGEST,
        "packet_support": PACKET_SUPPORT_DIGEST,
        "packet_expanded_semantic": PACKET_EXPANDED_DIGEST,
        "payload_semantic": PAYLOAD_SEMANTIC_DIGEST,
    }, "wrong digest header")
    require(digest(matching_records) == MATCHING_DIGEST,
            "matching semantic digest mismatch")
    require(digest(packets) == PACKET_SUPPORT_DIGEST,
            "packet support digest mismatch")
    require(digest(packet_records) == PACKET_EXPANDED_DIGEST,
            "expanded packet semantic digest mismatch")
    semantic = dict(payload)
    semantic.pop("digests")
    require(digest(semantic) == PAYLOAD_SEMANTIC_DIGEST,
            "payload semantic digest mismatch")
    require(CERTIFICATE.read_bytes() == before,
            "verifier mutated frozen certificate")
    return hashlib.sha256(before).hexdigest()


def planted_failures(blocked, packets):
    bad = list(packets[0])
    bad[-1] = packets[1][0]
    try:
        expand_packet(tuple(sorted(bad)))
    except ReplayError:
        pass
    else:
        raise ReplayError("corrupted packet passed")

    try:
        density_audit(1788, len(packets))
    except ReplayError:
        pass
    else:
        raise ReplayError("corrupted obstruction count passed")

    try:
        duplicate = tuple(sorted((packets[0], packets[0])))
        flat = tuple(v for packet in duplicate for v in packet)
        require(len(flat) == len(set(flat)), "duplicate packet passed")
    except ReplayError:
        pass
    else:
        raise ReplayError("duplicate packet was accepted")
    require(blocked.isdisjoint(packets[0]), "packet/dilation overlap")


def main():
    require(len(CELLS) == len(set(CELLS)) == 117,
            "coarse-cell collision")
    require(len(LABELS) == len(set(LABELS)) == 73125,
            "microbox label collision")
    require(len(CODES) == len(set(CODES)) == 73125,
            "physical code collision")
    blocked, matching_records, wrap_hist = dilation_semantics()
    packets, packet_records, intersection_hist, raw_hist, carry_hist = (
        packet_semantics(blocked)
    )
    total, gate, forced = density_audit(len(matching_records), len(packets))

    got = {
        "matching": digest(matching_records),
        "support": digest(packets),
        "expanded": digest(packet_records),
    }
    certificate_sha = certificate_audit(matching_records, packets,
                                        packet_records)
    planted_failures(blocked, packets)

    print("PASS_R5_FOUR_OF_FIVE_ONE_BLOCK_PACKING_WALL")
    print(f"GEOMETRY_OK coarse=117 q30_microboxes={total}")
    print(f"DILATION_OK edges=2382 components=1632 matching=1789 "
          f"endpoints=3578 wrap_hist={dict(sorted(wrap_hist.items()))}")
    print("FOUR_OF_FIVE_OK shift=(0,0,6,12) prototype=16 "
          f"full=3600 blocked=748 retained={len(packets)} incidence=0")
    print(f"INTERSECTION_HIST {dict(sorted(intersection_hist.items()))}")
    print(f"PACKET_RAW_TYPES {len(raw_hist)} CARRY_TYPES {len(carry_hist)}")
    print(f"DISJOINT_PACKING_OK forced={forced} required=4219 margin={forced-4219}")
    print(f"GATE_OK allowed_deletions=4218 max_retained={total-forced} "
          f"gate_count={gate}")
    print(f"MATCHING_DIGEST {got['matching']}")
    print(f"PACKET_SUPPORT_DIGEST {got['support']}")
    print(f"PACKET_EXPANDED_DIGEST {got['expanded']}")
    print(f"CERTIFICATE_SHA256 {certificate_sha}")
    print("SCOPE_ONE_BLOCK_ONLY no_arbitrary_word_language_capacity_claim")
    print("PLANTED_FAILURES_REJECTED")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        require(sys.argv[1:] == ["--self-test"], "unexpected arguments")
    main()

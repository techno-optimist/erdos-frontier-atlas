#!/usr/bin/env python3
"""Standalone exact replay of the q=42 two-layer one-block packing wall.

Only the Python standard library is used.  The theorem concerns one retained
union of complete globally aligned r=7 microboxes; it makes no word-language
capacity claim.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from fractions import Fraction as F
from functools import lru_cache
import hashlib
from itertools import combinations, product
import json
from math import gcd, lcm
from pathlib import Path
import sys

Q0 = 6
R = 7
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
FIRST_SHIFT = (6, 12)
SECOND_SHIFT = (0, 6)
CERTIFICATE = Path(__file__).with_name("frozen_semantic_certificate.json")

MATCHING_DIGEST = "0730b2e7730bd144b86b3299311a530ab3608f4777e9e3b257e7a4eddd2412a5"
PACKET_SUPPORT_DIGEST = "96dc66ed94ae58bc485cc35169da46361b71aa226e4bb2173b8266ecd9a2f3af"
PACKET_EXPANDED_DIGEST = "fd74a90da1a372c482c8a82acfbeed94765cff659b708ed30db1c8ed9284af6c"
PAYLOAD_SEMANTIC_DIGEST = "cee9ba92386faac163476dd41c7aee1d5776a149eeb9bf5ebf1b8348bd6b10bd"


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
        vertices = tuple(component)
        pos = {v: i for i, v in enumerate(vertices)}
        adjacency = [[] for _ in vertices]
        for a, b in edges:
            if a in pos and b in pos:
                adjacency[pos[a]].append(pos[b])
                adjacency[pos[b]].append(pos[a])
        for row in adjacency:
            row.sort()

        @lru_cache(None)
        def best(mask):
            if not mask:
                return ()
            i = (mask & -mask).bit_length() - 1
            candidates = [best(mask ^ (1 << i))]
            for j in adjacency[i]:
                if mask & (1 << j):
                    tail = best(mask ^ (1 << i) ^ (1 << j))
                    candidates.append(((min(i, j), max(i, j)),) + tail)
            return min(candidates, key=lambda value: (-len(value), value))

        local = best((1 << len(vertices)) - 1)
        answer.extend(tuple(sorted((vertices[i], vertices[j])))
                      for i, j in local)
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
    require(len(edges) == 5712, "wrong dilation edge census")
    require(len(components) == 4368 and max(map(len, components)) == 9,
            "wrong dilation component census")
    require(len(matching) == 4617, "wrong dilation matching count")
    endpoints = tuple(LABEL_POS[v] for edge in matching for v in edge)
    require(len(endpoints) == len(set(endpoints)) == 9234,
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
        for t in (F(1, 100), F(1, 42), F(1, 29)):
            require(0 < t < 3*t < F(1, R),
                    "dilation sample exits low microinterval")
            total = sum(sum(scalar_row_identity(cell[j], t)) for j in active)
            require(total == len(wraps) * (72 - 48*t) > 0,
                    "dilation recurrence mismatch")
    require(wrap_hist == Counter({1: 4617}),
            "wrong matching wrap histogram")

    # A finite telescope beats each displayed candidate bound.  Since the
    # bound was arbitrary, the recurrence contradicts bounded correction.
    T = F(1, 2*R)
    for bound in (0, 1, 10**3, 10**9):
        steps = int((4*bound + 24*T) // 72) + 1
        coarse_lower = 72*steps - 24*T
        require(coarse_lower > 4*bound,
                "finite telescope does not beat bound")
        if steps <= 100:
            exact_lower = 72*steps - 24*T*(1 - F(1, 3**steps))
            require(exact_lower > coarse_lower,
                    "telescope correction has wrong sign")
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


def add2(point, shift, k):
    return ((point[0] + k*shift[0]) % Q,
            (point[1] + k*shift[1]) % Q)


@lru_cache(None)
def unit_balanced_rows(support):
    """Find canonical unit-weight rows with zero potential incidence."""
    support = tuple(support)
    pos = {point: i for i, point in enumerate(support)}
    options = []
    for y in support:
        choices = []
        for x, z in combinations((p for p in support if p != y), 2):
            if all((x[j] + z[j] - 2*y[j]) % Q == 0 for j in range(2)):
                raw = sum((x[j] - z[j])**2 for j in range(2))
                if raw > 0:
                    choices.append((x, y, z, raw))
        if not choices:
            return None
        options.append(tuple(sorted(choices)))
    degrees = [0] * len(support)
    chosen = []

    def visit(i):
        if i == len(support):
            return tuple(chosen) if all(d == 2 for d in degrees) else None
        require(sum(2-d for d in degrees) == 2*(len(support)-i),
                "balanced-row endpoint accounting failed")
        for row in options[i]:
            x, _, z, _ = row
            ix, iz = pos[x], pos[z]
            if degrees[ix] >= 2 or degrees[iz] >= 2:
                continue
            degrees[ix] += 1
            degrees[iz] += 1
            chosen.append(row)
            result = visit(i+1)
            if result is not None:
                return result
            chosen.pop()
            degrees[ix] -= 1
            degrees[iz] -= 1
        return None

    return visit(0)


def prototype_packets(shift):
    support = prototype_support()
    order = lcm(Q // gcd(Q, shift[0]), Q // gcd(Q, shift[1]))
    require(order == 7, "wrong translation order")
    ambient = {
        tuple(sorted(add2(point, shift, k) for k in range(order)))
        for point in support
    }
    intersections = tuple(sorted(
        tuple(point for point in orbit if point in support)
        for orbit in ambient
    ))
    hist = Counter(map(len, intersections))
    packets = tuple(packet for packet in intersections
                    if 3 <= len(packet) <= 10
                    and unit_balanced_rows(packet) is not None)
    flat = tuple(point for packet in packets for point in packet)
    require(len(flat) == len(set(flat)), "prototype packets overlap")
    if shift == FIRST_SHIFT:
        require(hist == Counter({1: 51, 2: 44, 3: 58, 4: 41,
                                 5: 21, 6: 8, 7: 1}),
                "wrong first-layer intersection census")
        require(Counter(map(len, packets)) == Counter({5: 21, 6: 8, 7: 1}),
                "wrong first-layer prototype packet census")
        require(len(flat) == 160, "wrong first-layer prototype support")
    elif shift == SECOND_SHIFT:
        require(hist == Counter({1: 70, 2: 70, 3: 49, 4: 35, 5: 28}),
                "wrong second-layer intersection census")
        require(Counter(map(len, packets)) == Counter({5: 28}),
                "wrong second-layer prototype packet census")
        require(len(flat) == 140, "wrong second-layer prototype support")
    else:
        raise ReplayError("unrecognized packet shift")
    return packets, hist


def global_packet_layer(shift, blocked):
    prototypes, intersection_hist = prototype_packets(shift)
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
    full = len(BASE) * R**2 * len(prototypes)
    require(len(flat) == len(set(flat)), "global packet layer overlaps")
    require(blocked.isdisjoint(flat), "packet layer touches blocked vertex")
    if shift == FIRST_SHIFT:
        require(full == 13230 and len(packets) == 11534,
                "wrong first-layer packet count")
        require(full-len(packets) == 1696 and len(flat) == 61452,
                "wrong first-layer blocked/support count")
    elif shift == SECOND_SHIFT:
        require(full == 12348 and len(packets) == 3413,
                "wrong second-layer packet count")
        require(full-len(packets) == 8935 and len(flat) == 17065,
                "wrong second-layer blocked/support count")
    return packets, intersection_hist


def expand_packet(packet):
    fine = tuple(CODES[v] for v in packet)
    require(len({code[:2] for code in fine}) == 1,
            "packet does not fix its first pair")
    last = tuple(sorted(code[2:] for code in fine))
    rows2 = unit_balanced_rows(last)
    require(rows2 is not None and len(rows2) == len(packet),
            "packet lacks balanced midpoint rows")
    point_pos = {CODES[v][2:]: v for v in packet}
    incidence = Counter()
    rows = []
    u = (F(1, 8), F(2, 8), F(3, 8), F(4, 8))
    for x2, y2, z2, raw2 in rows2:
        x, y, z = point_pos[x2], point_pos[y2], point_pos[z2]
        defect = tuple(CODES[x][j] + CODES[z][j] - 2*CODES[y][j]
                       for j in range(4))
        require(all(value % Q == 0 for value in defect),
                "packet row is not a modular midpoint")
        carries = tuple(value // Q for value in defect)
        raw = sum((CODES[x][j] - CODES[z][j])**2 for j in range(4))
        require(raw == raw2 > 0, "packet raw endpoint cost mismatch")
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
    require(set(incidence) == set(packet) and
            all(value == 0 for value in incidence.values()),
            "packet potential incidence does not cancel")
    require(sum(row[-1] for row in rows) > 0,
            "aggregate packet raw RHS is not positive")
    return tuple(rows)


def packet_semantics(blocked):
    first, first_hist = global_packet_layer(FIRST_SHIFT, blocked)
    first_vertices = frozenset(v for packet in first for v in packet)
    second, second_hist = global_packet_layer(
        SECOND_SHIFT, blocked | first_vertices)
    second_vertices = frozenset(v for packet in second for v in packet)
    require(first_vertices.isdisjoint(second_vertices),
            "packet layers overlap")
    layers = (first, second)
    records = tuple(
        tuple((packet, expand_packet(packet)) for packet in layer)
        for layer in layers
    )
    raw_hist = Counter(row[-1] for layer in records
                       for _, rows in layer for row in rows)
    carry_hist = Counter(row[3:7] for layer in records
                         for _, rows in layer for row in rows)
    size_hists = tuple(Counter(map(len, layer)) for layer in layers)
    require(size_hists == (Counter({5: 8151, 6: 2984, 7: 399}),
                           Counter({5: 3413})),
            "wrong retained packet-size histograms")
    require(raw_hist == Counter({
        36: 6456, 144: 9575, 180: 14661, 360: 11143,
        468: 8353, 612: 8010, 720: 6225, 900: 664,
        936: 4512, 1224: 1219, 1296: 370, 1440: 3103,
        1476: 1352, 1620: 1835, 1872: 772, 2196: 267,
    }), "wrong packet raw-cost histogram")
    require(carry_hist == Counter({
        (0, 0, -1, -1): 5266, (0, 0, -1, 0): 7828,
        (0, 0, -1, 1): 4267, (0, 0, 0, -1): 11215,
        (0, 0, 0, 0): 20045, (0, 0, 0, 1): 12535,
        (0, 0, 1, -1): 3831, (0, 0, 1, 0): 10020,
        (0, 0, 1, 1): 3510,
    }), "wrong packet carry histogram")
    require(sum(raw*count for raw, count in raw_hist.items()) == 39815496,
            "wrong aggregate packet RHS")
    return (layers, records, (first_hist, second_hist), size_hists,
            raw_hist, carry_hist)


def density_audit(matching_count, packet_count):
    total = len(LABELS)
    gate = F(49, 576) * Q**4
    forced = matching_count + packet_count
    require(total == 280917, "wrong microbox total")
    require(gate == F(1058841, 4), "wrong gate count")
    require(total - 264711 == 16206,
            "wrong strict-above-gate deletion budget")
    require(forced == 19564 and total-forced == 261353 < gate,
            "packing does not cross gate")
    return total, gate, forced


def certificate_audit(matching_records, packets, packet_records):
    before = CERTIFICATE.read_bytes()
    payload = json.loads(before)
    require(payload["schema"] == "erdos142-q6-r7-two-layer-one-block-wall-v1",
            "wrong certificate schema")
    require(payload["geometry"] == {
        "coarse_q": 6, "residual_subdivision": 7, "fine_q": 42,
        "coarse_cells": 117, "microboxes": 280917,
    }, "wrong certificate geometry")
    require(payload["dilation"] == {
        "edge_count": 5712, "component_count": 4368,
        "maximum_component_size": 9, "matching_count": 4617,
        "endpoint_count": 9234,
        "algorithm": "lex-first maximum matching in each sorted component",
    }, "wrong certificate dilation record")
    require(payload["packet_layers"] == [
        {
            "name": "first", "shift_last_pair": [6, 12],
            "translation_order": 7,
            "prototype_intersection_histogram": {
                "1": 51, "2": 44, "3": 58, "4": 41,
                "5": 21, "6": 8, "7": 1,
            },
            "prototype_packet_size_histogram": {"5": 21, "6": 8, "7": 1},
            "full_packets": 13230, "blocked_packets": 1696,
            "retained_packets": 11534,
            "retained_packet_size_histogram": {
                "5": 8151, "6": 2984, "7": 399,
            },
            "retained_vertices": 61452, "rows": 61452,
        },
        {
            "name": "second", "shift_last_pair": [0, 6],
            "translation_order": 7,
            "prototype_intersection_histogram": {
                "1": 70, "2": 70, "3": 49, "4": 35, "5": 28,
            },
            "prototype_packet_size_histogram": {"5": 28},
            "full_packets": 12348,
            "blocked_by_dilation_or_first_layer": 8935,
            "retained_packets": 3413,
            "retained_packet_size_histogram": {"5": 3413},
            "retained_vertices": 17065, "rows": 17065,
        },
    ], "wrong certificate packet-layer record")
    require(payload["gate"] == {
        "density_numerator": 49, "density_denominator": 576,
        "gate_count_numerator": 1058841, "gate_count_denominator": 4,
        "allowed_deletions_strictly_above": 16206,
        "forced_deletions_one_block": 19564,
        "max_retained_one_block": 261353,
        "margin_below_gate_in_deletions": 3357,
    }, "wrong certificate gate record")
    require(payload["packet_semantics"] == {
        "expanded_rows": 78517,
        "potential_incidence_per_vertex": 0,
        "common_strict_interior_offset": ["1/8", "2/8", "3/8", "4/8"],
        "aggregate_raw_fine_digit_square_cost": 39815496,
        "raw_fine_digit_square_histogram": {
            "36": 6456, "144": 9575, "180": 14661,
            "360": 11143, "468": 8353, "612": 8010,
            "720": 6225, "900": 664, "936": 4512,
            "1224": 1219, "1296": 370, "1440": 3103,
            "1476": 1352, "1620": 1835, "1872": 772,
            "2196": 267,
        },
        "carry_histogram": {
            "0,0,-1,-1": 5266, "0,0,-1,0": 7828,
            "0,0,-1,1": 4267, "0,0,0,-1": 11215,
            "0,0,0,0": 20045, "0,0,0,1": 12535,
            "0,0,1,-1": 3831, "0,0,1,0": 10020,
            "0,0,1,1": 3510,
        },
        "aggregate_raw_cost_strictly_positive": True,
    }, "wrong certificate packet-semantics record")
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


def planted_failures(blocked, layers):
    packets = layers[0]
    bad = list(packets[0])
    bad[-1] = packets[1][0]
    try:
        expand_packet(tuple(sorted(bad)))
    except ReplayError:
        pass
    else:
        raise ReplayError("corrupted packet passed")

    try:
        density_audit(4616, sum(map(len, layers)))
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
    certificate_before = CERTIFICATE.read_bytes()
    require(len(CELLS) == len(set(CELLS)) == 117,
            "coarse-cell collision")
    require(len(LABELS) == len(set(LABELS)) == 280917,
            "microbox label collision")
    require(len(CODES) == len(set(CODES)) == 280917,
            "physical code collision")
    blocked, matching_records, wrap_hist = dilation_semantics()
    (layers, packet_records, intersection_hists, size_hists,
     raw_hist, carry_hist) = packet_semantics(blocked)
    packet_count = sum(map(len, layers))
    total, gate, forced = density_audit(len(matching_records), packet_count)

    got = {
        "matching": digest(matching_records),
        "support": digest(layers),
        "expanded": digest(packet_records),
    }
    if MATCHING_DIGEST != "TO_BE_FROZEN":
        certificate_sha = certificate_audit(matching_records, layers,
                                            packet_records)
    else:
        certificate_sha = "NOT_YET_FROZEN"
    planted_failures(blocked, layers)
    require(CERTIFICATE.read_bytes() == certificate_before,
            "self-test mutated frozen certificate")

    print("PASS_R7_TWO_LAYER_ONE_BLOCK_PACKING_WALL")
    print(f"GEOMETRY_OK coarse=117 q42_microboxes={total}")
    print(f"DILATION_OK edges=5712 components=4368 matching=4617 "
          f"endpoints=9234 wrap_hist={dict(sorted(wrap_hist.items()))}")
    print("FIRST_LAYER_OK shift=(0,0,6,12) order=7 prototype=30 "
          f"full=13230 blocked=1696 retained={len(layers[0])} incidence=0")
    print("SECOND_LAYER_OK shift=(0,0,0,6) order=7 prototype=28 "
          f"full=12348 blocked=8935 retained={len(layers[1])} incidence=0")
    print(f"INTERSECTION_HISTS {[dict(sorted(h.items())) for h in intersection_hists]}")
    print(f"PACKET_SIZE_HISTS {[dict(sorted(h.items())) for h in size_hists]}")
    print(f"PACKET_RAW_HIST {dict(sorted(raw_hist.items()))} "
          f"CARRY_TYPES {len(carry_hist)}")
    print(f"PACKET_CARRY_HIST {dict(sorted(carry_hist.items()))}")
    print(f"DISJOINT_PACKING_OK forced={forced} required=16207 "
          f"margin={forced-16207}")
    print(f"GATE_OK allowed_deletions=16206 max_retained={total-forced} "
          f"gate_count={gate}")
    print(f"MATCHING_DIGEST {got['matching']}")
    print(f"PACKET_SUPPORT_DIGEST {got['support']}")
    print(f"PACKET_EXPANDED_DIGEST {got['expanded']}")
    print(f"CERTIFICATE_SHA256 {certificate_sha}")
    print("FROZEN_CERTIFICATE_NONMUTATION_OK")
    print("SCOPE_ONE_BLOCK_ONLY no_arbitrary_word_language_capacity_claim")
    print("PLANTED_FAILURES_REJECTED")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        require(sys.argv[1:] == ["--self-test"], "unexpected arguments")
    main()

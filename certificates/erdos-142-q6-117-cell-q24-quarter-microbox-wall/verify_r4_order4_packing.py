#!/usr/bin/env python3
"""Standalone exact replay of the q=24 one-block microbox packing wall.

The theorem certified here concerns one retained union of complete aligned
microboxes.  It deliberately does *not* turn the four-point packets into a
per-coordinate quotient for arbitrary word languages; the final audit records
an exact obstruction to that naive transfer.
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
R = 4
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
SHIFT = (0, 0, 6, 12)

# Filled from this verifier's canonical JSON encoding after independent
# reconstruction.  These constants make accidental enumeration drift loud.
MATCHING_DIGEST = "b76a136b58f6adcbebb9f0d34447bda10b99070c5339b6df5afd87989d9ab803"
PACKET_DIGEST = "061eba59ea9fd5e529b9c161b8d90d2c538df38067c5d485f3ae90dbf4736037"
PACKET_SUPPORT_DIGEST = "f7e337056bde4b79568b97ff156e9bd6f03abc513da7d3fffedaae494d813db1"
PAYLOAD_SEMANTIC_DIGEST = "8e54dab21a04d4a9f78631eb2c74e800597a78942080a417a3a4b7c493e25e65"
CERTIFICATE = Path(__file__).with_name("frozen_semantic_certificate.json")


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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
    """Maximum component matching by exhaustive search (components <= 9)."""
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


def oriented_edge(edge):
    def try_orientation(source, target):
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

    record = try_orientation(*edge)
    if record is None:
        record = try_orientation(edge[1], edge[0])
    require(record is not None, "matching edge lacks dilation orientation")
    return record


def scalar_row_identity(a: int, t: F):
    """Return the two exact q0^2-scaled raw-canonical corrections."""
    b = (a - 1) % Q0
    a_t = F(a + t, Q0)
    a_3t = F(a + 3 * t, Q0)
    b_1t = F(b + 1 - t, Q0)
    b_13t = F(b + 1 - 3 * t, Q0)

    def correction(x: F, y: F, z: F):
        defect = x + z - 2 * y
        require(defect.denominator == 1, "nonintegral dilation carry")
        return Q0**2 * ((x - z)**2 - 2*x*x - 2*z*z + 4*y*y)

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
    require(len(edges) == 1359, "wrong dilation edge census")
    require(len(components) == 843 and max(map(len, components)) == 9,
            "wrong dilation component census")
    require(len(matching) == 960, "wrong matching count")
    endpoints = tuple(LABEL_POS[v] for edge in matching for v in edge)
    require(len(endpoints) == len(set(endpoints)) == 1920,
            "dilation matching overlaps")
    wrap_hist = Counter()
    records = []
    for edge in matching:
        source, target, active, wraps = oriented_edge(edge)
        wrap_hist[len(wraps)] += 1
        records.append((LABEL_POS[source], LABEL_POS[target],
                        sum(1 << j for j in active),
                        sum(1 << j for j in wraps)))
        source_cell = CELLS[source[0]]
        # These are actual strict-interior residual samples in the low/high
        # microintervals.  Summing the two physical row corrections leaves
        # exactly one 72-48t contribution per wrap coordinate.
        for t in (F(1, 100), F(1, 24), F(1, 17)):
            require(0 < t < 3*t < F(1, R),
                    "dilation sample leaves low microinterval")
            total = sum(sum(scalar_row_identity(source_cell[j], t))
                        for j in active)
            require(total == len(wraps) * (72 - 48*t) > 0,
                    "physical dilation recurrence mismatch")
    require(set(wrap_hist) <= {1, 2}, "unexpected wrap multiplicity")

    # Exact finite telescope: every wrap contributes 72-48t in q0^2 units.
    T = F(1, 2 * R)
    for bound in (0, 1, 10**3, 10**9):
        steps = int((4 * bound + 24 * T) // 72) + 1
        lower = 72 * steps - 24 * T
        require(lower > 4 * bound, "telescope does not beat bound")
        if steps <= 100:
            exact = 72 * steps - 24 * T * (1 - F(1, 3**steps))
            require(exact > lower, "telescope correction has wrong sign")
    for j in range(1, 8):
        t = T / 3**j
        require(0 < t < 3 * t <= T < F(1, R),
                "low residual exits microbox")
        require(F(R - 1, R) < 1 - 3 * t < 1 - t < 1,
                "high residual exits microbox")
    return matching, frozenset(endpoints), tuple(records), wrap_hist


def add_shift(code, multiple):
    return tuple((code[j] + multiple * SHIFT[j]) % Q for j in range(4))


def all_order_four_packets():
    packets = set()
    for code in CODES:
        orbit = tuple(sorted(CODE_POS.get(add_shift(code, k), -1)
                             for k in range(4)))
        if -1 not in orbit and len(set(orbit)) == 4:
            packets.add(orbit)
    packets = tuple(sorted(packets))
    flat = tuple(v for packet in packets for v in packet)
    require(len(packets) == 1152, "wrong full order-four orbit count")
    require(len(flat) == len(set(flat)) == 4608,
            "full translation orbits do not partition their support")
    return packets


def packet_semantics(blocked):
    packets = tuple(packet for packet in all_order_four_packets()
                    if blocked.isdisjoint(packet))
    require(len(packets) == 833, "wrong unblocked packet count")
    flat = tuple(v for packet in packets for v in packet)
    require(len(flat) == len(set(flat)) == 3332,
            "unblocked packet supports overlap")
    incidence = Counter()
    raw_hist = Counter()
    carry_hist = Counter()
    u = (F(1, 5), F(2, 5), F(3, 5), F(4, 5))
    records = []
    for packet in packets:
        support = set(packet)
        rows = []
        for y in packet:
            cy = CODES[y]
            x = CODE_POS[add_shift(cy, 1)]
            z = CODE_POS[add_shift(cy, -1)]
            require(x in support and z in support and x != z,
                    "translation row escapes packet or degenerates")
            defect = tuple(CODES[x][j] + CODES[z][j] - 2 * cy[j]
                           for j in range(4))
            require(all(value % Q == 0 for value in defect),
                    "packet row is not a torus midpoint")
            carries = tuple(value // Q for value in defect)
            raw = sum((CODES[x][j] - CODES[z][j]) ** 2
                      for j in range(4))
            require(raw > 0, "packet row has zero raw endpoint cost")
            incidence[x] += 1
            incidence[z] += 1
            incidence[y] -= 2
            raw_hist[raw] += 1
            carry_hist[carries] += 1
            rows.append((x, y, z, *carries, raw))

            # One exact strict-interior physical sample.  The same common
            # offset cancels symbolically in every midpoint and endpoint gap.
            xp = tuple(F(CODES[x][j], Q) + u[j] / Q for j in range(4))
            yp = tuple(F(CODES[y][j], Q) + u[j] / Q for j in range(4))
            zp = tuple(F(CODES[z][j], Q) + u[j] / Q for j in range(4))
            require(all(xp[j] + zp[j] - 2 * yp[j] == carries[j]
                        for j in range(4)), "physical midpoint sample failed")
            require(sum((xp[j] - zp[j]) ** 2 for j in range(4))
                    == F(raw, Q**2), "physical raw cost sample failed")
        records.append((packet, tuple(rows)))
    require(all(value == 0 for value in incidence.values()),
            "aggregate packet potential incidence does not cancel")
    require(sum(raw * count for raw, count in raw_hist.items()) > 0,
            "aggregate packet RHS is not positive")
    return packets, tuple(records), raw_hist, carry_hist


def density_audit(matching_count, packet_count):
    total = len(LABELS)
    gate = F(49, 576) * Q**4
    obstructions = matching_count + packet_count
    require(total == 117 * R**4 == 29952, "wrong total microbox count")
    require(gate == 28224, "wrong q24 gate count")
    require(total - int(gate) - 1 == 1727,
            "wrong strict-above-gate deletion budget")
    require(obstructions == 1793, "wrong obstruction count")
    require(total - obstructions == 28159 < gate,
            "packing does not cross gate")
    return total, gate, obstructions


def language_transfer_warning():
    """Exact counterexample to naive four-cycle quotient injectivity."""
    phases = tuple(product(range(4), repeat=2))
    ten = frozenset({
        (0, 0), (0, 1), (0, 2), (1, 0), (1, 1),
        (1, 2), (2, 0), (2, 2), (2, 3), (3, 1),
    })
    lines = set()
    for start in phases:
        for direction in product((0, 1, 3), repeat=2):
            if direction == (0, 0):
                continue
            line = frozenset(
                tuple((start[j] + k * direction[j]) % 4 for j in range(2))
                for k in range(4)
            )
            require(len(line) == 4, "non-generator direction entered audit")
            lines.add(line)
    require(len(lines) == 16, "wrong Z4^2 affine-line census")
    require(len(ten) == 10 > 3**2, "warning-set size drift")
    require(not any(line <= ten for line in lines),
            "warning set contains a direct four-word orbit")
    return ten, lines


def certificate_audit(matching_records, packets, packet_records):
    before = CERTIFICATE.read_bytes()
    payload = json.loads(before)
    require(payload["schema"] == "erdos142-q6-r4-order4-one-block-wall-v1",
            "wrong certificate schema")
    require(payload["coarse_q"] == Q0 and
            payload["residual_subdivision"] == R and
            payload["fine_q"] == Q and
            payload["coarse_cells"] == 117 and
            payload["microboxes"] == 29952,
            "wrong certificate geometry header")
    require(tuple(tuple(row) for row in payload["dilation"])
            == matching_records, "frozen dilation ledger mismatch")
    require(tuple(tuple(packet) for packet in payload["order4_packets"])
            == packets, "frozen packet ledger mismatch")
    require(tuple(payload["order4_shift"]) == SHIFT,
            "frozen translation shift mismatch")
    require(payload["gate"] == {
        "numerator": 49,
        "denominator": 576,
        "gate_count": 28224,
        "allowed_deletions_strictly_above": 1727,
        "forced_deletions_one_block": 1793,
        "max_retained_one_block": 28159,
    }, "frozen gate record mismatch")
    require(payload["scope"] == {
        "one_block_complete_aligned_microbox_union": True,
        "arbitrary_word_language_capacity": False,
    }, "frozen scope record mismatch")
    digests = payload["digests"]
    require(digests == {
        "dilation_semantic": MATCHING_DIGEST,
        "packet_support": PACKET_SUPPORT_DIGEST,
        "packet_expanded_semantic": PACKET_DIGEST,
        "payload_semantic": PAYLOAD_SEMANTIC_DIGEST,
    }, "frozen digest header mismatch")
    require(digest(matching_records) == digests["dilation_semantic"],
            "dilation semantic digest mismatch")
    require(digest(packets) == digests["packet_support"],
            "packet support digest mismatch")
    require(digest(packet_records) == digests["packet_expanded_semantic"],
            "expanded packet semantic digest mismatch")
    semantic = dict(payload)
    semantic.pop("digests")
    require(digest(semantic) == digests["payload_semantic"],
            "payload semantic digest mismatch")
    require(CERTIFICATE.read_bytes() == before,
            "verifier mutated the frozen certificate")
    return hashlib.sha256(before).hexdigest()


def planted_failures(packets, blocked):
    corrupted = list(packets[0])
    corrupted[-1] = packets[1][0]
    require(len(set(corrupted)) == 4, "planted packet collision malformed")
    try:
        support = set(corrupted)
        for y in corrupted:
            require(CODE_POS[add_shift(CODES[y], 1)] in support,
                    "corrupted packet rejected")
    except AssertionError:
        pass
    else:
        raise AssertionError("corrupted translation packet was accepted")

    try:
        density_audit(959, len(packets))
    except AssertionError:
        pass
    else:
        raise AssertionError("corrupted obstruction count was accepted")

    require(blocked.isdisjoint(packets[0]), "frozen packet overlaps matching")


def main():
    require(len(CELLS) == len(set(CELLS)) == 117,
            "coarse-cell geometry collision")
    require(len(LABELS) == len(set(LABELS)) == 29952,
            "microbox label collision")
    require(len(CODES) == len(set(CODES)) == 29952,
            "physical microbox collision")
    matching, blocked, matching_records, wrap_hist = dilation_semantics()
    packets, packet_records, raw_hist, carry_hist = packet_semantics(blocked)
    total, gate, obstructions = density_audit(len(matching), len(packets))
    language_transfer_warning()
    certificate_sha = certificate_audit(matching_records, packets,
                                        packet_records)

    got_matching_digest = digest(matching_records)
    got_packet_digest = digest(packet_records)
    if MATCHING_DIGEST != "TO_BE_FROZEN":
        require(got_matching_digest == MATCHING_DIGEST,
                "matching semantic digest mismatch")
    if PACKET_DIGEST != "TO_BE_FROZEN":
        require(got_packet_digest == PACKET_DIGEST,
                "packet semantic digest mismatch")
    planted_failures(packets, blocked)

    print("PASS_R4_ORDER4_ONE_BLOCK_PACKING_WALL")
    print(f"GEOMETRY_OK coarse=117 q24_microboxes={total}")
    print(f"DILATION_OK edges=1359 matching={len(matching)} "
          f"endpoints={len(blocked)} wrap_hist={dict(sorted(wrap_hist.items()))}")
    print(f"ORDER4_PACKETS_OK full=1152 unblocked={len(packets)} "
          "size=4 shift=(0,0,6,12) incidence=0 raw_rhs_positive")
    print(f"PACKET_RAW_HIST {dict(sorted(raw_hist.items()))}")
    print(f"PACKET_CARRY_TYPES {len(carry_hist)}")
    print(f"DISJOINT_PACKING_OK obstructions={obstructions} margin={obstructions-1728}")
    print(f"GATE_OK allowed_deletions=1727 max_retained={total-obstructions} "
          f"gate_count={gate}")
    print(f"MATCHING_DIGEST {got_matching_digest}")
    print(f"PACKET_DIGEST {got_packet_digest}")
    print(f"CERTIFICATE_SHA256 {certificate_sha}")
    print("LANGUAGE_WARNING_OK Z4^2_direct_line_free_size=10 product_baseline=9")
    print("SCOPE_ONE_BLOCK_ONLY no_arbitrary_word_language_capacity_claim")
    print("PLANTED_FAILURES_REJECTED")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        require(sys.argv[1:] == ["--self-test"], "unexpected arguments")
    main()

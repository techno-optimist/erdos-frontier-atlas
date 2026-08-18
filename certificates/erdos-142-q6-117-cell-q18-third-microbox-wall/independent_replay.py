#!/usr/bin/env python3
"""Independent stdlib replay for the frozen q=18 microbox packing wall.

This file imports no producer or discovery module.  It reconstructs the fixed
117-cell geometry, validates every semantic dilation/packet row, verifies
physical-point incidence and raw costs, checks cross-support disjointness, and
does the exact density arithmetic.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

Q = 6
R = 3
QF = Q * R
BASE = (
    (3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
    (5, 0), (5, 1), (5, 2),
)
OFFSETS = (
    (0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
    (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3),
)
COARSE = tuple(
    (a, b, (a + dx) % Q, (b + dy) % Q)
    for a, b in BASE
    for dx, dy in OFFSETS
)
MICRO_SUBS = tuple(product(range(R), repeat=4))
LABELS = tuple(
    (coarse_index, subs)
    for coarse_index in range(len(COARSE))
    for subs in MICRO_SUBS
)
CODES = tuple(
    tuple(R * COARSE[coarse_index][j] + subs[j] for j in range(4))
    for coarse_index, subs in LABELS
)


class ReplayError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayError(message)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def exact_top_level(payload: dict) -> None:
    require(payload.get("schema") == "erdos142-q6-r3-explicit-microbox-wall-v1",
            "wrong schema")
    require(payload.get("q") == Q, "wrong coarse q")
    require(payload.get("residual_subdivision") == R, "wrong subdivision")
    require(payload.get("fine_q") == QF, "wrong fine q")
    require(payload.get("coarse_cells") == 117, "wrong coarse count")
    require(payload.get("microboxes") == 9477, "wrong microbox count")
    require(len(COARSE) == len(set(COARSE)) == 117, "coarse geometry collision")
    require(len(LABELS) == len(set(LABELS)) == 9477, "label collision")
    require(len(CODES) == len(set(CODES)) == 9477, "physical code collision")

    digests = payload.get("digests")
    require(isinstance(digests, dict), "missing digests")
    require(digests.get("dilation") == digest(payload.get("dilation")),
            "dilation digest mismatch")
    require(digests.get("packets") == digest(payload.get("packets")),
            "packet digest mismatch")
    semantic = dict(payload)
    semantic.pop("digests")
    require(digests.get("semantic") == digest(semantic),
            "semantic digest mismatch")


def mask(indices: tuple[int, ...]) -> int:
    return sum(1 << index for index in indices)


def check_dilation_record(record: object) -> tuple[int, int]:
    require(isinstance(record, list) and len(record) == 4,
            "malformed dilation record")
    source, target, active_mask, wrap_mask = record
    require(all(isinstance(x, int) and not isinstance(x, bool)
                for x in record), "noninteger dilation field")
    require(0 <= source < len(LABELS) and 0 <= target < len(LABELS),
            "dilation endpoint out of range")
    require(source != target, "dilation loop")
    source_cell, source_sub = LABELS[source]
    target_cell, target_sub = LABELS[target]
    A = COARSE[source_cell]
    B = COARSE[target_cell]
    active = tuple(j for j, (a, b) in enumerate(zip(A, B)) if a != b)
    wraps = tuple(j for j in active if A[j] == 0 and B[j] == Q - 1)
    require(bool(active) and bool(wraps), "dilation lacks active wrap")
    require(all(b == a or b == (a - 1) % Q for a, b in zip(A, B)),
            "invalid coarse predecessor geometry")
    require(active_mask == mask(active), "active mask mismatch")
    require(wrap_mask == mask(wraps), "wrap mask mismatch")
    require(all(source_sub[j] == 0 and target_sub[j] == R - 1
                for j in active), "active microinterval mismatch")
    require(all(source_sub[j] == target_sub[j]
                for j in range(4) if j not in active),
            "inactive microinterval mismatch")
    return source, target


def scalar_row_identity(a: int, t: F) -> tuple[F, F]:
    """Return the two exact q^2-scaled correction costs."""
    b = (a - 1) % Q
    A_t = F(a + t, Q)
    A_3t = F(a + 3 * t, Q)
    B_1t = F(b + 1 - t, Q)
    B_13t = F(b + 1 - 3 * t, Q)

    def midpoint_cost(x: F, y: F, z: F) -> F:
        defect = x + z - 2 * y
        require(defect.denominator == 1, "nonintegral torus carry")
        return Q * Q * ((x - z)**2 - 2*x*x - 2*z*z + 4*y*y)

    one = midpoint_cost(A_t, B_1t, B_13t)
    two = midpoint_cost(A_3t, A_t, B_1t)
    if a == 0:
        require(one == 108 - 24*t and two == -36 - 24*t,
                "wrap correction identity failed")
    else:
        require(one == two == 0, "nonwrap correction is nonzero")
    return one, two


def dilation_semantics(dilation: list) -> set[int]:
    require(len(dilation) == 433, "wrong dilation matching size")
    endpoints = []
    wrap_hist = Counter()
    for record in dilation:
        source, target = check_dilation_record(record)
        endpoints.extend((source, target))
        wrap_hist[record[3].bit_count()] += 1
    require(len(endpoints) == len(set(endpoints)) == 866,
            "dilation records are not a matching")
    require(all(count in (1, 2) for count in wrap_hist),
            "unexpected wrap multiplicity")

    for digit in range(Q):
        for t in (F(1, 100), F(1, 12), F(1, 7)):
            one, two = scalar_row_identity(digit, t)
            if digit == 0:
                require(one + two == 72 - 48*t > 0,
                        "positive wrap recurrence failed")

    T = F(1, 2 * R)
    for bound in (0, 1, 10**3, 10**9):
        steps = int((4 * bound + 24 * T) // 72) + 1
        coarse_lower = 72 * steps - 24 * T
        require(coarse_lower > 4 * bound,
                "finite telescope does not beat bound")
        if steps <= 100:
            exact_lower = 72 * steps - 24 * T * (1 - F(1, 3**steps))
            require(exact_lower > coarse_lower,
                    "exact telescope correction has wrong sign")
    for j in range(1, 8):
        t = T / 3**j
        require(0 < t < 3*t <= T < F(1, R),
                "low residual leaves microbox")
        require(F(R - 1, R) < 1 - 3*t < 1 - t < 1,
                "high residual leaves microbox")
    return set(endpoints)


def packet_digest(packet: dict) -> None:
    listed = packet.get("digest")
    body = dict(packet)
    body.pop("digest", None)
    require(listed == digest(body), "individual packet digest mismatch")


def check_packet(packet: object) -> tuple[set[int], int, int]:
    require(isinstance(packet, dict), "packet is not an object")
    packet_digest(packet)
    support = packet.get("support")
    rows = packet.get("rows")
    weighted_rhs = packet.get("weighted_rhs")
    require(isinstance(support, list) and support, "empty packet support")
    require(all(isinstance(v, int) and not isinstance(v, bool)
                and 0 <= v < len(CODES) for v in support),
            "bad packet support vertex")
    require(len(support) == len(set(support)), "duplicate packet support")
    support_set = set(support)
    require(isinstance(rows, list) and len(rows) == len(support),
            "packet must have one row per support centre")
    require(isinstance(weighted_rhs, int) and weighted_rhs > 0,
            "bad listed packet RHS")

    incidence = Counter()
    actual_rhs = 0
    centers = []
    for row in rows:
        require(isinstance(row, list) and len(row) == 9,
                "malformed packet row")
        x, y, z, weight, c0, c1, c2, c3, cost = row
        require(all(isinstance(v, int) and not isinstance(v, bool)
                    for v in row), "noninteger packet field")
        require(x in support_set and y in support_set and z in support_set,
                "packet row escapes semantic support")
        require(weight > 0, "nonpositive row weight")
        carries = (c0, c1, c2, c3)
        defect = tuple(CODES[x][j] + CODES[z][j] - 2*CODES[y][j]
                       for j in range(4))
        require(defect == tuple(QF * carry for carry in carries),
                "modular defect/carry mismatch")
        raw = sum((CODES[x][j] - CODES[z][j])**2 for j in range(4))
        require(raw == cost > 0, "raw canonical cost mismatch")
        incidence[x] += weight
        incidence[y] -= 2 * weight
        incidence[z] += weight
        actual_rhs += weight * raw
        centers.append(y)

        # One exact common-offset sample also checks canonical strict interior
        # and the unscaled physical midpoint/cost identity directly.
        u = (F(1, 7), F(2, 7), F(3, 7), F(4, 7))
        xp = tuple(F(CODES[x][j] + u[j], QF) for j in range(4))
        yp = tuple(F(CODES[y][j] + u[j], QF) for j in range(4))
        zp = tuple(F(CODES[z][j] + u[j], QF) for j in range(4))
        require(all(0 < u[j] < 1 for j in range(4)),
                "sample offset is not strict interior")
        require(all(xp[j] + zp[j] - 2*yp[j] == carries[j]
                    for j in range(4)), "physical midpoint row failed")
        require(sum((xp[j]-zp[j])**2 for j in range(4))
                == F(raw, QF**2), "physical raw cost failed")

    require(set(centers) == support_set and len(centers) == len(set(centers)),
            "support vertices are not exactly the row centres")
    require(all(value == 0 for value in incidence.values()),
            "physical potential incidence does not cancel")
    require(actual_rhs == weighted_rhs > 0,
            "weighted packet RHS mismatch")
    return support_set, actual_rhs, max(row[3] for row in rows)


def packet_semantics(packets: list, forbidden: set[int]) -> set[int]:
    require(len(packets) == 114, "wrong packet count")
    used = set(forbidden)
    packet_vertices = set()
    sizes = Counter()
    for index, packet in enumerate(packets):
        support, _, _ = check_packet(packet)
        require(used.isdisjoint(support),
                f"packet {index} overlaps a prior obstruction")
        used.update(support)
        packet_vertices.update(support)
        sizes[len(support)] += 1
    require(len(packet_vertices) == sum(
        len(packet["support"]) for packet in packets
    ), "packet supports are not mutually disjoint")
    require(min(sizes) >= 1, "empty packet size histogram")
    return packet_vertices


def gate_audit(payload: dict, dilation_vertices: set[int],
               packet_vertices: set[int]) -> None:
    gate = payload.get("gate")
    require(isinstance(gate, dict), "missing gate record")
    require(gate == {
        "numerator": 49,
        "denominator": 576,
        "forced_deletions": 547,
        "allowed_deletions": 546,
        "max_retained": 8930,
        "gate_count_numerator": 35721,
        "gate_count_denominator": 4,
    }, "gate record mismatch")
    require(dilation_vertices.isdisjoint(packet_vertices),
            "dilation and packet supports overlap")
    obstruction_count = 433 + 114
    require(obstruction_count == 547, "wrong obstruction count")
    total = 117 * R**4
    gate_count = F(49, 576) * QF**4
    require(total == 9477, "wrong total box count")
    require(gate_count == F(35721, 4), "wrong gate count")
    require(total - obstruction_count == 8930 < gate_count,
            "deletion packing does not cross gate")
    require(total - 546 == 8931 > gate_count,
            "strict-above-gate integer budget is wrong")


def planted_failures(payload: dict) -> None:
    mutated = json.loads(json.dumps(payload))
    mutated["packets"][0]["rows"][0][8] += 1
    try:
        check_packet(mutated["packets"][0])
    except ReplayError:
        pass
    else:
        raise ReplayError("corrupted raw cost passed")

    mutated = json.loads(json.dumps(payload))
    mutated["dilation"][1][0] = mutated["dilation"][0][0]
    try:
        dilation_semantics(mutated["dilation"])
    except ReplayError:
        pass
    else:
        raise ReplayError("overlapping dilation matching passed")

    mutated = json.loads(json.dumps(payload))
    mutated["gate"]["forced_deletions"] = 546
    try:
        gate_audit(mutated, set(), set())
    except ReplayError:
        pass
    else:
        raise ReplayError("corrupted gate passed")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: independent_replay.py frozen_semantic_certificate.json")
    path = Path(sys.argv[1])
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), "top level is not an object")
    exact_top_level(payload)
    dilation = payload.get("dilation")
    packets = payload.get("packets")
    require(isinstance(dilation, list), "dilation is not a list")
    require(isinstance(packets, list), "packets is not a list")
    dilation_vertices = dilation_semantics(dilation)
    packet_vertices = packet_semantics(packets, dilation_vertices)
    gate_audit(payload, dilation_vertices, packet_vertices)
    planted_failures(payload)
    print("PASS_INDEPENDENT_Q18_MICROBOX_PACKING_WALL")
    print("GEOMETRY_OK coarse=117 microboxes=9477 physical_codes_unique")
    print("DILATION_OK matching=433 endpoints=866 strict_telescope")
    print("PACKETS_OK count=114 physical_incidence=0 raw_rhs_positive common_offset")
    print("DISJOINTNESS_OK obstruction_supports=547 mutually_disjoint")
    print("GATE_OK forced=547 allowed=546 retained=8930<35721/4")
    print("DEPENDENCIES_OK verifier=stdlib_only frozen_semantic_input")
    print("PLANTED_FAILURES_REJECTED")


if __name__ == "__main__":
    main()

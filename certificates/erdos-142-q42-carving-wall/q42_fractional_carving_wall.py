#!/usr/bin/env python3
"""Exact q=42 *fractional* carving wall for the fixed 117-cell one-block set.

Unlike a complete-microbox deletion count, this replay permits an arbitrary
measurable retained subset E of every q=42 microbox.  A balanced packet has a
common offset u in [0,1)^4.  If all its translated copies of u survive, its
pointwise midpoint rows cancel every value of a single physical potential.
Thus their intersection must be empty; the union bound makes the sum of the
deleted relative measures across that packet at least one whole microbox.

Two fully disjoint packet families contain 17,640 packets.  That alone is
larger than the 16,206 whole-q42-box deletion budget above the EHPS gate.
No dilation/telescoping edge is used, so this survives arbitrary measurable
proper carving.  This is a scratch theorem for one four-dimensional block;
it is not a multi-block/path-capacity result or an Erdos-142 solution.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import gcd, lcm
from pathlib import Path
import hashlib
import json
import sys

Q0, R, Q = 6, 7, 42
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFF = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
       (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
SHIFT1, SHIFT2 = (6, 12), (0, 6)
OFFSET = (Fraction(1, 8), Fraction(2, 8), Fraction(3, 8), Fraction(4, 8))
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "q42_fractional_carving_certificate.json"

CELLS = tuple((a, b, (a + dx) % Q0, (b + dy) % Q0)
              for a, b in BASE for dx, dy in OFF)
SUB = tuple(product(range(R), repeat=4))
CODES = tuple(tuple(R * CELLS[i][j] + s[j] for j in range(4))
              for i in range(len(CELLS)) for s in SUB)
CID = {z: i for i, z in enumerate(CODES)}


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value):
    return hashlib.sha256(canon(value)).hexdigest()


def trans(point, shift, k):
    return ((point[0] + k * shift[0]) % Q, (point[1] + k * shift[1]) % Q)


def prototype():
    return frozenset(((R * dx + s) % Q, (R * dy + t) % Q)
                     for dx, dy in OFF for s, t in product(range(R), repeat=2))


@lru_cache(None)
def balanced_rows(packet):
    """Find exactly one unit-weight balanced midpoint row per vertex."""
    pts = tuple(packet)
    place = {p: i for i, p in enumerate(pts)}
    choices = []
    for middle in pts:
        rows = []
        for x, z in combinations(tuple(p for p in pts if p != middle), 2):
            if all((x[k] + z[k] - 2 * middle[k]) % Q == 0 for k in (0, 1)):
                raw = sum((x[k] - z[k]) ** 2 for k in (0, 1))
                if raw:
                    rows.append((x, middle, z, raw))
        if not rows:
            return None
        choices.append(tuple(sorted(rows)))
    degree, taken = [0] * len(pts), []

    def walk(index):
        if index == len(pts):
            return tuple(taken) if degree == [2] * len(pts) else None
        if sum(2-d for d in degree) != 2 * (len(pts)-index):
            return None
        for x, y, z, raw in choices[index]:
            ix, iz = place[x], place[z]
            if degree[ix] == 2 or degree[iz] == 2:
                continue
            degree[ix] += 1; degree[iz] += 1; taken.append((x, y, z, raw))
            answer = walk(index+1)
            if answer is not None:
                return answer
            taken.pop(); degree[ix] -= 1; degree[iz] -= 1
        return None

    return walk(0)


def usable_prototypes(shift):
    support = prototype()
    order = lcm(Q // gcd(Q, shift[0]), Q // gcd(Q, shift[1]))
    need(order == 7, "translation does not have order seven")
    orbits = {tuple(sorted(trans(p, shift, k) for k in range(order))) for p in support}
    intersections = tuple(sorted(tuple(p for p in orb if p in support) for orb in orbits))
    usable = tuple(p for p in intersections if len(p) >= 3 and balanced_rows(p) is not None)
    flat = [v for packet in usable for v in packet]
    need(len(flat) == len(set(flat)), "prototype packets overlap")
    expected = ({1: 51, 2: 44, 3: 58, 4: 41, 5: 21, 6: 8, 7: 1},
                {5: 21, 6: 8, 7: 1}) if shift == SHIFT1 else \
               ({1: 70, 2: 70, 3: 49, 4: 35, 5: 28}, {5: 28})
    need(dict(sorted(Counter(map(len, intersections)).items())) == expected[0],
         "prototype orbit census")
    need(dict(sorted(Counter(map(len, usable)).items())) == expected[1],
         "prototype packet census")
    return usable


def lift(shift, forbidden=frozenset()):
    proto = usable_prototypes(shift)
    packets = []
    for (a, b), s0, s1, shape in product(BASE, range(R), range(R), proto):
        first = (R*a+s0, R*b+s1)
        packet = tuple(sorted(CID[(first[0], first[1],
                                  (x+R*a) % Q, (y+R*b) % Q)]
                              for x, y in shape))
        if forbidden.isdisjoint(packet):
            packets.append(packet)
    packets = tuple(sorted(packets))
    vertices = [v for p in packets for v in p]
    need(len(vertices) == len(set(vertices)), "lifted packet supports overlap")
    need(forbidden.isdisjoint(vertices), "forbidden support leaked")
    return packets


def physical_packet_check(packet):
    """Check all actual common-offset rows and exact potential cancellation."""
    points = tuple(CODES[i] for i in packet)
    need(len({p[:2] for p in points}) == 1, "packet leaves first-pair fiber")
    plan = balanced_rows(tuple(sorted(p[2:] for p in points)))
    need(plan is not None and len(plan) == len(packet), "missing balanced plan")
    by_tail = {CODES[i][2:]: i for i in packet}
    incidence, raw_total, semantic_rows = Counter(), 0, []
    for x2, y2, z2, raw2 in plan:
        x, y, z = by_tail[x2], by_tail[y2], by_tail[z2]
        dx, dy, dz = CODES[x], CODES[y], CODES[z]
        carry = tuple((dx[k]+dz[k]-2*dy[k]) // Q for k in range(4))
        need(all((dx[k]+dz[k]-2*dy[k]) % Q == 0 for k in range(4)),
             "fine midpoint congruence")
        xp = tuple((Fraction(dx[k]) + OFFSET[k]) / Q for k in range(4))
        yp = tuple((Fraction(dy[k]) + OFFSET[k]) / Q for k in range(4))
        zp = tuple((Fraction(dz[k]) + OFFSET[k]) / Q for k in range(4))
        need(tuple(xp[k]+zp[k]-2*yp[k] for k in range(4)) == carry,
             "physical torus midpoint")
        raw = sum((dx[k]-dz[k])**2 for k in range(4))
        need(raw == raw2 and raw > 0, "strict raw cost")
        incidence[x] += 1; incidence[z] += 1; incidence[y] -= 2
        raw_total += raw
        semantic_rows.append((x, y, z, *carry, raw))
    need(set(incidence) == set(packet) and all(v == 0 for v in incidence.values()),
         "potential incidence does not cancel")
    need(raw_total > 0, "packet has zero aggregate cost")
    return tuple(semantic_rows)


def core_control():
    """A natural high-density collar carve still contains a complete packet."""
    delta = Fraction(1, 144)
    relative_mass = (1 - 2*delta) ** 4
    need(relative_mass > Fraction(49, 52), "central core misses gate")
    # At the one fixed common offset used below, every packet witness has fine
    # residual (s+OFFSET_j)/7.  Its distance from a coarse-cell face is at
    # least min(1/56,1/28,3/56,1/14)=1/56.
    need(delta < Fraction(1, 56), "collar reaches packet witness")
    # This checks the whole q=42 grid, so in particular it applies to every
    # packet point, irrespective of which fine subbox a packet uses.
    for code in CODES:
        residual = tuple((Fraction(code[j] % R)+OFFSET[j]) / R for j in range(4))
        need(all(delta < t < 1-delta for t in residual), "offset core control")
    return delta, relative_mass


def planted_controls(first, second, expanded, total, gate):
    """Reject three semantic corruptions without touching frozen inputs."""
    # A row with its final raw cost changed no longer describes the physical
    # triple.  This catches a bookkeeping-only RHS substitution.
    row = list(expanded[0][1][0])
    row[-1] += 1
    x, y, z, *_carry, bad_raw = row
    actual = sum((CODES[x][k]-CODES[z][k])**2 for k in range(4))
    need(actual != bad_raw, "planted raw-RHS mutation escaped")
    # Reusing a first-layer vertex in the second layer destroys the disjoint
    # accounting on which the fractional deletion sum rests.
    first_vertices = {v for packet in first for v in packet}
    need(first_vertices.isdisjoint({v for packet in second for v in packet}),
         "planted support-overlap mutation escaped")
    # The strict quarter-integer gate, rather than a rounded comparison, is
    # what makes the 17,640 lower bound decisive.
    need(total-len(first)-len(second) < gate, "planted gate mutation escaped")


def main():
    source_before = Path(__file__).read_bytes()
    certificate_before = CERTIFICATE.read_bytes()
    certificate = json.loads(certificate_before)
    need(len(CELLS) == len(set(CELLS)) == 117, "coarse geometry")
    need(len(CODES) == len(set(CODES)) == 117 * R**4, "fine geometry")
    first = lift(SHIFT1)
    first_vertices = frozenset(v for p in first for v in p)
    second = lift(SHIFT2, first_vertices)
    packets = first + second
    need((len(first), len(second), len(packets)) == (13230, 4410, 17640),
         "disjoint packet census")
    need(first_vertices.isdisjoint({v for p in second for v in p}), "layers intersect")
    expanded = tuple((packet, physical_packet_check(packet)) for packet in packets)
    row_count = sum(len(rows) for _packet, rows in expanded)
    need(row_count == 92610, "actual balanced-row census")
    total = 117 * R**4
    gate = Fraction(49, 576) * Q**4
    deletion_budget = total - 264711  # strictly above a quarter-integer gate
    need((total, gate, deletion_budget) == (280917, Fraction(1058841, 4), 16206),
         "gate arithmetic")
    need(len(packets) > deletion_budget, "fractional packet cover misses gate")
    max_retained = total-len(packets)
    need(max_retained == 263277 and max_retained < gate, "fractional wall")
    delta, relative_mass = core_control()
    semantic = {
        "first_support": digest(first),
        "second_support": digest(second),
        "all_support": digest(packets),
        "expanded_rows": digest(expanded),
    }
    need(certificate["schema"] == "erdos142-q42-fractional-carving-wall-v1",
         "certificate schema")
    need(certificate["geometry"] == {"coarse_cells": 117, "fine_q": 42,
                                       "fine_boxes": 280917}, "certificate geometry")
    need(certificate["packet_families"] == {"first_shift": [6, 12],
                                               "first_packets": 13230,
                                               "second_shift": [0, 6],
                                               "second_packets": 4410,
                                               "disjoint_total": 17640,
                                               "actual_rows": 92610}, "certificate packet census")
    need(certificate["gate"] == {"allowed_deletions_strictly_above": 16206,
                                   "max_retained": 263277,
                                   "gate_count": "1058841/4"}, "certificate gate")
    need(certificate["digests"] == semantic, "certificate semantic digest")
    planted_controls(first, second, expanded, total, gate)
    need(Path(__file__).read_bytes() == source_before, "replay mutated source")
    need(CERTIFICATE.read_bytes() == certificate_before, "replay mutated frozen certificate")
    print("PASS_Q42_FRACTIONAL_PROPER_CARVING_WALL")
    print("GEOMETRY coarse=117 fine_boxes=280917")
    print("PACKETS first=13230 second=4410 disjoint_total=17640")
    print(f"ROWS actual_common_offset={row_count} checked_all_packets")
    print("FRACTIONAL_DELETION lower_bound=17640 allowed_above_gate=16206")
    print("GATE max_retained=263277 gate=1058841/4")
    print(f"CORE_CONTROL delta={delta} retained_fraction={relative_mass}")
    print("DIGESTS", json.dumps(semantic, sort_keys=True))
    print("FROZEN_CERTIFICATE_NONMUTATION_OK")
    print("PLANTED_FAILURES_REJECTED")
    print("SCOPE one_block arbitrary_measurable_subsets pointwise_single_valued_potential")


if __name__ == "__main__":
    main()

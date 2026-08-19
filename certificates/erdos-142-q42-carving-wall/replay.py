#!/usr/bin/env python3
"""Independent hostile replay of the q=42 arbitrary-measurable carving wall.

This script does not import the proposed replay.  It regenerates the 117-cell
geometry, finds balanced midpoint plans from their defining congruences, lifts
two disjoint translation-packet layers, and checks the physical (rather than
box-label) midpoint equations at a common offset.  It also states and checks
the exact finite-measure bookkeeping used for arbitrary measurable carving.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from functools import lru_cache
from math import gcd, lcm
import argparse
import hashlib
import json
import sys

Q0, R, Q = 6, 7, 42
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFFSETS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
           (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
SHIFT_A, SHIFT_B = (6, 12), (0, 6)
COMMON_U = (Fraction(1, 8), Fraction(1, 4), Fraction(3, 8), Fraction(1, 2))
EXPECTED = {
    "first_support": "e91b67988985df24a69f9c7350df564fa1abf6e1ae308c71aaeb7761e9a089ec",
    "second_support": "d59a81e0494937b1483952f49f1fbd099b4298f5d0b7fa6d2cc4a85ef456ca66",
    "all_support": "4c8f6f00b67cf5e29f7ece22467ee40f4102491a92b5575fe734ffc389405357",
    "expanded_rows": "2b83d3841ded7fd9329b625e493c1bae93145423f430da359fb3035ad4f61835",
}


def need(statement, message):
    if not statement:
        raise AssertionError(message)


def frozen_json_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


# The explicit q=6 cells and q=42 digit encoding.  This intentionally does
# not use the candidate module or any of its functions.
CELLS = tuple((a, b, (a + dx) % Q0, (b + dy) % Q0)
              for a, b in BASE for dx, dy in OFFSETS)
SUBDIGITS = tuple(product(range(R), repeat=4))
CODES = tuple(tuple(R * cell[j] + sub[j] for j in range(4))
              for cell in CELLS for sub in SUBDIGITS)
CODE_ID = {code: n for n, code in enumerate(CODES)}


def translate(point, shift, power):
    return ((point[0] + power * shift[0]) % Q,
            (point[1] + power * shift[1]) % Q)


def tail_prototype():
    return frozenset(((R * dx + sx) % Q, (R * dy + sy) % Q)
                     for dx, dy in OFFSETS for sx, sy in product(range(R), repeat=2))


def midpoint_choices(points, middle):
    """All unordered nondegenerate endpoint pairs centered at ``middle``."""
    others = [p for p in points if p != middle]
    answer = []
    for left, right in combinations(others, 2):
        if all((left[j] + right[j] - 2 * middle[j]) % Q == 0 for j in range(2)):
            answer.append((left, right))
    return tuple(answer)


@lru_cache(None)
def canonical_balance(shape):
    """Self-contained exact degree-2 search; one midpoint row per vertex."""
    pts = tuple(sorted(shape))
    place = {p: n for n, p in enumerate(pts)}
    choices = {middle: midpoint_choices(pts, middle) for middle in pts}
    need(all(choices[p] for p in pts), "a packet center lacks a midpoint row")
    degree = [0] * len(pts)
    chosen = []

    def visit(index):
        if index == len(pts):
            return tuple(chosen) if all(d == 2 for d in degree) else None
        middle = pts[index]
        for left, right in choices[middle]:
            il, ir = place[left], place[right]
            if degree[il] == 2 or degree[ir] == 2:
                continue
            degree[il] += 1
            degree[ir] += 1
            chosen.append((left, middle, right))
            found = visit(index + 1)
            if found is not None:
                return found
            chosen.pop()
            degree[il] -= 1
            degree[ir] -= 1
        return None

    result = visit(0)
    need(result is not None, "no balanced unit-weight midpoint plan")
    return result


@lru_cache(None)
def mrv_balance(shape):
    """A second, variable-order solver used only as an independent witness."""
    pts = tuple(sorted(shape))
    position = {p: n for n, p in enumerate(pts)}
    options = {p: midpoint_choices(pts, p) for p in pts}
    degree = [0] * len(pts)
    selected = []

    def visit(remaining):
        if not remaining:
            return tuple(selected) if all(d == 2 for d in degree) else None
        viable = {}
        for middle in remaining:
            candidates = []
            for left, right in options[middle]:
                if degree[position[left]] < 2 and degree[position[right]] < 2:
                    candidates.append((left, right))
            if not candidates:
                return None
            viable[middle] = candidates
        middle = min(remaining, key=lambda p: (len(viable[p]), p))
        later = tuple(p for p in remaining if p != middle)
        for left, right in viable[middle]:
            il, ir = position[left], position[right]
            degree[il] += 1
            degree[ir] += 1
            selected.append((left, middle, right))
            found = visit(later)
            if found is not None:
                return found
            selected.pop()
            degree[il] -= 1
            degree[ir] -= 1
        return None

    result = visit(pts)
    need(result is not None, "MRV solver found no balanced plan")
    return result


def prototype_packets(shift):
    """Intersect all length-seven translation orbits with the 13-offset tile."""
    support = tail_prototype()
    order = lcm(Q // gcd(Q, shift[0]), Q // gcd(Q, shift[1]))
    need(order == 7, "last-pair translation does not have order seven")
    orbits = {tuple(sorted(translate(point, shift, k) for k in range(order)))
              for point in support}
    intersections = tuple(sorted(tuple(point for point in orbit if point in support)
                                 for orbit in orbits))
    candidates = []
    for piece in intersections:
        if len(piece) < 3:
            continue
        try:
            canonical_balance(piece)
        except AssertionError:
            continue
        candidates.append(piece)
    candidates = tuple(candidates)
    seen = [point for piece in candidates for point in piece]
    need(len(seen) == len(set(seen)), "prototype packet supports overlap")
    census = dict(sorted(Counter(map(len, intersections)).items()))
    usable = dict(sorted(Counter(map(len, candidates)).items()))
    if shift == SHIFT_A:
        need(census == {1: 51, 2: 44, 3: 58, 4: 41, 5: 21, 6: 8, 7: 1}, "first orbit census")
        need(usable == {5: 21, 6: 8, 7: 1}, "first usable census")
    elif shift == SHIFT_B:
        need(census == {1: 70, 2: 70, 3: 49, 4: 35, 5: 28}, "second orbit census")
        need(usable == {5: 28}, "second usable census")
    else:
        raise AssertionError("unexpected shift")
    for piece in candidates:
        # The variable-order search independently finds a valid cancellation
        # plan for the same packet; it is not used to reproduce a checksum.
        check_balance(piece, mrv_balance(piece))
    return candidates


def check_balance(shape, plan):
    incidence = Counter()
    points = set(shape)
    need(len(plan) == len(points), "not one row per vertex")
    for left, middle, right in plan:
        need({left, middle, right} <= points and len({left, middle, right}) == 3,
             "row has repeated or outside vertex")
        need(all((left[j] + right[j] - 2 * middle[j]) % Q == 0 for j in range(2)),
             "tail row is not a torus midpoint")
        incidence[left] += 1
        incidence[right] += 1
        incidence[middle] -= 2
    need(set(incidence) == points and all(v == 0 for v in incidence.values()),
         "tail-plan potential coefficients do not cancel")


def lift_layer(shift, forbidden):
    shapes = prototype_packets(shift)
    out = []
    for (a, b), sx, sy, shape in product(BASE, range(R), range(R), shapes):
        first = (R * a + sx, R * b + sy)
        packet = tuple(sorted(CODE_ID[(first[0], first[1],
                                      (tail[0] + R * a) % Q,
                                      (tail[1] + R * b) % Q)]
                              for tail in shape))
        if not (set(packet) & forbidden):
            out.append(packet)
    out = tuple(sorted(out))
    flat = [vertex for packet in out for vertex in packet]
    need(len(flat) == len(set(flat)), "layer contains intersecting supports")
    need(not (set(flat) & forbidden), "forbidden first-layer support leaked")
    return out


def physical_rows(packet):
    """Lift the canonical tail rows and inspect actual q=42 torus triples."""
    points = [CODES[vertex] for vertex in packet]
    need(len({point[:2] for point in points}) == 1, "packet crosses first-pair fiber")
    tail_to_vertex = {CODES[vertex][2:]: vertex for vertex in packet}
    shape = tuple(sorted(tail_to_vertex))
    plan = canonical_balance(shape)
    check_balance(shape, plan)
    incidence, rows = Counter(), []
    for xt, yt, zt in plan:
        x, y, z = tail_to_vertex[xt], tail_to_vertex[yt], tail_to_vertex[zt]
        dx, dy, dz = CODES[x], CODES[y], CODES[z]
        carry = tuple((dx[j] + dz[j] - 2 * dy[j]) // Q for j in range(4))
        need(all((dx[j] + dz[j] - 2 * dy[j]) % Q == 0 for j in range(4)),
             "full q=42 digit midpoint congruence failed")
        px = tuple((Fraction(dx[j]) + COMMON_U[j]) / Q for j in range(4))
        py = tuple((Fraction(dy[j]) + COMMON_U[j]) / Q for j in range(4))
        pz = tuple((Fraction(dz[j]) + COMMON_U[j]) / Q for j in range(4))
        need(tuple(px[j] + pz[j] - 2 * py[j] for j in range(4)) == carry,
             "common-offset physical torus equation failed")
        raw = sum((dx[j] - dz[j]) ** 2 for j in range(4))
        need(raw > 0, "zero endpoint cost")
        incidence[x] += 1
        incidence[z] += 1
        incidence[y] -= 2
        rows.append((x, y, z, *carry, raw))
    need(set(incidence) == set(packet) and all(value == 0 for value in incidence.values()),
         "physical potential coefficients do not cancel")
    return tuple(rows)


def measure_theorem_checks():
    """Exact arithmetic for the Fubini/union-bound implication.

    For a packet P define A_v={u in [0,1)^4:(d_v+u)/42 in E}.  These are
    measurable whenever E is.  Pointwise coercivity and one packet's zero
    incidence give intersection_v A_v=empty; no a.e. inference is used.
    Union-bound: 1 <= sum_v measure([0,1)^4 minus A_v).  Since the affine
    maps have Jacobian 42^-4 and distinct packet vertices are disjoint
    half-open fine boxes, that packet deletes at least one q=42 box volume.
    """
    total = 117 * R**4
    gate = Fraction(49, 576) * Q**4
    forced_packets = 17640
    retained = total - forced_packets
    strict_whole_box_budget = total - (gate.numerator // gate.denominator + 1)
    need((total, gate, forced_packets, retained, strict_whole_box_budget) ==
         (280917, Fraction(1058841, 4), 17640, 263277, 16206),
         "exact q=42 gate bookkeeping")
    need(retained < gate and forced_packets > strict_whole_box_budget,
         "fractional packing does not cross the strict gate")
    # The map uses [0,1)^4, so every fine box is half-open and the images of
    # distinct digit vectors are truly disjoint, not merely a.e. disjoint.
    for digit in CODES:
        for j in range(4):
            low = Fraction(digit[j], Q)
            high = Fraction(digit[j] + 1, Q)
            need(0 <= low < high <= 1, "fine box leaves fundamental domain")
    return total, gate, retained, strict_whole_box_budget


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True,
                        help="candidate q42 scratch directory; read-only")
    args = parser.parse_args()
    target = Path(args.target)
    source = target / "q42_fractional_carving_wall.py"
    cert_path = target / "q42_fractional_carving_certificate.json"
    source_before, cert_before = source.read_bytes(), cert_path.read_bytes()
    frozen = json.loads(cert_before)

    need(len(CELLS) == 117 and len(set(CELLS)) == 117, "117-cell coarse geometry")
    need(len(CODES) == 280917 and len(CODES) == len(set(CODES)), "q42 digit geometry")
    first = lift_layer(SHIFT_A, set())
    first_support = {vertex for packet in first for vertex in packet}
    second = lift_layer(SHIFT_B, first_support)
    packets = first + second
    all_support = [vertex for packet in packets for vertex in packet]
    need((len(first), len(second), len(packets), len(all_support)) ==
         (13230, 4410, 17640, 92610), "packet/support census")
    need(len(all_support) == len(set(all_support)), "layers are not mutually disjoint")

    expanded = tuple((packet, physical_rows(packet)) for packet in packets)
    rows = [row for _packet, group in expanded for row in group]
    need(len(rows) == 92610, "physical row census")
    carries = Counter(tuple(row[3:7]) for row in rows)
    raw_costs = Counter(row[7] for row in rows)
    need(all(cost > 0 for cost in raw_costs), "some physical row has nonpositive raw cost")
    total, gate, retained, budget = measure_theorem_checks()

    semantic = {
        "first_support": frozen_json_digest(first),
        "second_support": frozen_json_digest(second),
        "all_support": frozen_json_digest(packets),
        "expanded_rows": frozen_json_digest(expanded),
    }
    need(semantic == EXPECTED, "rebuilt data disagree with frozen public digests")
    need(frozen.get("digests") == semantic, "certificate digests disagree with independent replay")
    need(frozen.get("geometry") == {"coarse_cells": 117, "fine_q": 42, "fine_boxes": 280917},
         "certificate geometry fields")
    need(frozen.get("packet_families") == {
        "first_shift": [6, 12], "first_packets": 13230,
        "second_shift": [0, 6], "second_packets": 4410,
        "disjoint_total": 17640, "actual_rows": 92610}, "certificate packet fields")
    need(frozen.get("gate") == {
        "allowed_deletions_strictly_above": 16206,
        "max_retained": 263277, "gate_count": "1058841/4"}, "certificate gate fields")
    need(source.read_bytes() == source_before and cert_path.read_bytes() == cert_before,
         "read-only audit mutated candidate files")

    print("PASS_INDEPENDENT_Q42_FRACTIONAL_CARVING_AUDIT")
    print("GEOMETRY coarse=117 q=42 fine_boxes=280917 half_open=[d/42,(d+1)/42)")
    print("PACKING first_packets=13230 second_packets=4410 disjoint_packets=17640 supports=92610")
    print("PHYSICAL_ROWS count=92610 zero_incidence=all strict_raw=all")
    print("CARRIES", json.dumps({str(key): value for key, value in sorted(carries.items())}, sort_keys=True))
    print("RAW_COSTS", json.dumps(dict(sorted(raw_costs.items())), sort_keys=True))
    print(f"FUBINI_POINTWISE forced_deletion={len(packets)}/42^4 retained={retained}/42^4")
    print(f"GATE retained_boxes={retained} gate_boxes={gate} strict_budget={budget} margin={gate-retained}")
    print("DIGESTS", json.dumps(semantic, sort_keys=True))
    print("SOURCE_SHA256", hashlib.sha256(source_before).hexdigest())
    print("CERTIFICATE_SHA256", hashlib.sha256(cert_before).hexdigest())
    print("SCOPE one_block arbitrary_measurable_subtiles pointwise_single_valued_physical_potential")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL_INDEPENDENT_Q42_FRACTIONAL_CARVING_AUDIT: {exc}", file=sys.stderr)
        raise

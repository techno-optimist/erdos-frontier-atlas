#!/usr/bin/env python3
"""Exact solver-free replay of a q=30 one-block four-point packet packing.

This is scratch research, not an Atlas certificate.  It proves only a
one-block deletion wall for unions of complete aligned q=30 microboxes.
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

# The four prototype points and their row pattern.  A row is (x,y,z), with y
# the midpoint.  Coordinates here are the last-pair q=30 residues relative to
# the corresponding BASE anchor.
A = (5, 23)
B = (11, 5)
C = (23, 29)
D = (29, 11)
PROTOTYPE = (A, B, C, D)
ROW_PATTERN = ((B, A, D), (C, B, D), (A, C, B), (A, D, C))

EXPECTED_TRANSLATIONS = (
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
    (15, 27), (15, 28),
    (20, 16), (20, 17), (20, 18),
    (21, 16), (21, 17), (21, 18), (21, 19),
    (29, 0), (29, 1),
)

CERTIFICATE = Path(__file__).with_name("frozen_semantic_certificate.json")
MATCHING_DIGEST = "24a1632cda94383627b7031650143df7f35f3b37172afe5e32aad2f4ea5d5bf5"
TEMPLATE_DIGEST = "13b8cf19649e810e9ed1c154bf46661c1b36c4bd259fb0c043a05a1b73c5bdb7"
SUPPORT_DIGEST = "e3bc26d8cdc88ce5f7d50eb59b5309a00d3e55863af94190476f3221e0be0ee2"
PACKET_DIGEST = "b320d6105ffd7b61be58ef3433792cd1fd55876584dcc215636390593a1f338d"
PAYLOAD_SEMANTIC_DIGEST = "806d3de8a1196121215cfb48610ad6630252b1f06eef87adc50b221bb7c567c7"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


def json_value(value: object):
    """Return the canonical JSON-shaped (list/dict/scalar) form of value."""
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":")))


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
    result = []
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
        result.append(tuple(sorted(found)))
    return tuple(sorted(result))


def canonical_matching(edges):
    """Lexicographically first maximum matching in every component."""
    answer = []
    for component in connected_components(edges):
        vertices = set(component)
        local = tuple(edge for edge in edges
                      if edge[0] in vertices and edge[1] in vertices)
        found = None
        for size in range(min(len(component) // 2, len(local)), -1, -1):
            for chosen in combinations(local, size):
                flat = tuple(vertex for edge in chosen for vertex in edge)
                if len(flat) == len(set(flat)):
                    found = chosen
                    break
            if found is not None:
                answer.extend(found)
                break
        require(found is not None, "matching search failed")
    return tuple(sorted(answer))


def prototype_points():
    return frozenset(
        ((R * dx + s) % Q, (R * dy + t) % Q)
        for dx, dy in OFFSETS for s, t in product(range(R), repeat=2)
    )


def translate(point, shift):
    return tuple((point[j] + shift[j]) % Q for j in range(2))


def admissible_templates(points):
    templates = []
    for shift in product(range(Q), repeat=2):
        support = tuple(sorted(translate(p, shift) for p in PROTOTYPE))
        if all(p in points for p in support):
            rows = tuple(
                (translate(x, shift), translate(y, shift),
                 translate(z, shift))
                for x, y, z in ROW_PATTERN
            )
            templates.append((shift, support, rows))
    require(tuple(row[0] for row in templates) == EXPECTED_TRANSLATIONS,
            "admissible translation list drift")
    require(len({row[1] for row in templates}) == len(templates) == 16,
            "template support collision")
    return tuple(templates)


def fiber_of(index):
    cell, sub = LABELS[index]
    base = cell // len(OFFSETS)
    return base, sub[0], sub[1]


def relative_point(index):
    cell, _ = LABELS[index]
    base = cell // len(OFFSETS)
    a, b = BASE[base]
    code = CODES[index]
    return ((code[2] - R * a) % Q, (code[3] - R * b) % Q)


def vertex_lookup():
    result = {}
    for index in range(len(LABELS)):
        key = (*fiber_of(index), relative_point(index))
        require(key not in result, "fiber coordinate collision")
        result[key] = index
    return result


def packet_semantics(rows, lookup, fiber):
    incidence = Counter()
    expanded = []
    for x2, y2, z2 in rows:
        x = lookup[(*fiber, x2)]
        y = lookup[(*fiber, y2)]
        z = lookup[(*fiber, z2)]
        cx, cy, cz = CODES[x], CODES[y], CODES[z]
        defect = tuple(cx[j] + cz[j] - 2 * cy[j] for j in range(4))
        require(all(value % Q == 0 for value in defect),
                "row is not a torus midpoint")
        carries = tuple(value // Q for value in defect)
        raw = sum((cx[j] - cz[j]) ** 2 for j in range(4))
        require(raw > 0, "row has zero endpoint cost")
        incidence[x] += 1
        incidence[z] += 1
        incidence[y] -= 2

        # Common strict-interior offset: it cancels from both the modular
        # midpoint identity and the physical squared distance.
        u = (F(1, 6), F(1, 3), F(1, 2), F(2, 3))
        xp = tuple(F(cx[j], Q) + u[j] / Q for j in range(4))
        yp = tuple(F(cy[j], Q) + u[j] / Q for j in range(4))
        zp = tuple(F(cz[j], Q) + u[j] / Q for j in range(4))
        require(all(xp[j] + zp[j] - 2 * yp[j] == carries[j]
                    for j in range(4)), "physical midpoint failure")
        require(sum((xp[j] - zp[j]) ** 2 for j in range(4))
                == F(raw, Q**2), "physical raw cost failure")
        expanded.append((x, y, z, *carries, raw))
    support = set(v for row in expanded for v in row[:3])
    require(len(support) == 4, "packet does not use four vertices")
    require(all(incidence[v] == 0 for v in support),
            "physical-potential coefficients do not cancel")
    return tuple(sorted(support)), tuple(expanded)


def deterministic_packing(blocked, templates, lookup):
    points = prototype_points()
    packet_records = []
    support_records = []
    count_by_fiber = Counter()
    for fiber in product(range(len(BASE)), range(R), range(R)):
        available = {
            point for point in points
            if lookup[(*fiber, point)] not in blocked
        }
        used = set()
        for shift, support2, rows in sorted(templates, key=lambda row: row[1]):
            support2_set = set(support2)
            if support2_set <= available and used.isdisjoint(support2_set):
                support, expanded = packet_semantics(rows, lookup, fiber)
                require(set(support) == {
                    lookup[(*fiber, point)] for point in support2
                }, "support lift mismatch")
                used.update(support2_set)
                support_records.append(support)
                packet_records.append((fiber, shift, expanded))
                count_by_fiber[fiber] += 1
    flat = tuple(v for support in support_records for v in support)
    require(len(flat) == len(set(flat)), "packet supports overlap")
    require(blocked.isdisjoint(flat), "packet touches dilation endpoint")
    return tuple(support_records), tuple(packet_records), count_by_fiber


def density_audit(matching_count, packet_count):
    total = len(LABELS)
    gate = F(49, 576) * Q**4
    forced = matching_count + packet_count
    require(gate == F(275625, 4), "gate drift")
    require(total - (gate.numerator // gate.denominator) - 1 == 4218,
            "strict-above-gate deletion budget drift")
    require(total == 73125, "total microbox count drift")
    require(forced == 4641 and total - forced == 68484 < gate,
            "packing does not cross the gate")
    return total, gate, forced


def semantic_payload(matching_records, templates, supports, records):
    return {
        "schema": "erdos142-q6-r5-fourpoint-one-block-wall-v1",
        "coarse_q": Q0,
        "residual_subdivision": R,
        "fine_q": Q,
        "coarse_cells": len(CELLS),
        "microboxes": len(LABELS),
        "prototype": PROTOTYPE,
        "row_pattern": ROW_PATTERN,
        "admissible_translations": EXPECTED_TRANSLATIONS,
        "dilation": matching_records,
        "packet_supports": supports,
        "packet_ledger": records,
        "gate": {
            "numerator": 275625,
            "denominator": 4,
            "allowed_deletions_strictly_above": 4218,
            "forced_deletions_one_block": 4641,
            "max_retained_one_block": 68484,
        },
        "scope": {
            "one_block_complete_aligned_microbox_union": True,
            "arbitrary_word_language_capacity": False,
        },
    }


def certificate_audit(matching_records, templates, supports, records):
    before = CERTIFICATE.read_bytes()
    payload = json.loads(before)
    require(payload["schema"] ==
            "erdos142-q6-r5-fourpoint-one-block-wall-v1",
            "wrong certificate schema")
    require(payload["dilation"] == json_value(matching_records),
            "frozen dilation ledger mismatch")
    require(payload["packet_supports"] == json_value(supports),
            "frozen packet-support ledger mismatch")
    require(payload["packet_ledger"] == json_value(records),
            "frozen expanded packet ledger mismatch")
    expected = semantic_payload(matching_records, templates, supports, records)
    frozen_semantic = dict(payload)
    digests = frozen_semantic.pop("digests")
    require(frozen_semantic == json_value(expected),
            "frozen semantic header or payload mismatch")
    require(digests == {
        "dilation_semantic": MATCHING_DIGEST,
        "packet_templates": TEMPLATE_DIGEST,
        "packet_supports": SUPPORT_DIGEST,
        "packet_expanded_semantic": PACKET_DIGEST,
        "payload_semantic": PAYLOAD_SEMANTIC_DIGEST,
    }, "frozen digest header mismatch")
    require(digest(matching_records) == MATCHING_DIGEST,
            "matching semantic digest mismatch")
    require(digest(templates) == TEMPLATE_DIGEST,
            "template semantic digest mismatch")
    require(digest(supports) == SUPPORT_DIGEST,
            "support semantic digest mismatch")
    require(digest(records) == PACKET_DIGEST,
            "expanded packet semantic digest mismatch")
    require(digest(expected) == PAYLOAD_SEMANTIC_DIGEST,
            "payload semantic digest mismatch")
    require(CERTIFICATE.read_bytes() == before,
            "verifier mutated the frozen certificate")
    return hashlib.sha256(before).hexdigest()


def expanded_row_is_valid(row):
    if len(row) != 8:
        return False
    x, y, z, *tail = row
    if not all(isinstance(v, int) for v in row):
        return False
    if not all(0 <= v < len(CODES) for v in (x, y, z)):
        return False
    carries, raw = tuple(tail[:4]), tail[4]
    cx, cy, cz = CODES[x], CODES[y], CODES[z]
    defect = tuple(cx[j] + cz[j] - 2 * cy[j] for j in range(4))
    return (all(value % Q == 0 for value in defect) and
            tuple(value // Q for value in defect) == carries and
            sum((cx[j] - cz[j]) ** 2 for j in range(4)) == raw and
            raw > 0)


def planted_failures(matching, blocked, supports, records):
    bad_row = list(records[0][2][0])
    bad_row[-1] += 1
    require(not expanded_row_is_valid(tuple(bad_row)),
            "corrupted raw cost was accepted")

    bad_carry = list(records[0][2][0])
    bad_carry[3] += 1
    require(not expanded_row_is_valid(tuple(bad_carry)),
            "corrupted carry was accepted")

    collided = list(supports[:2])
    collided[1] = collided[0]
    flat = tuple(v for support in collided for v in support)
    require(len(flat) != len(set(flat)),
            "planted support collision was accepted")

    require(blocked.isdisjoint(supports[0]),
            "first valid packet unexpectedly touches matching")
    try:
        density_audit(len(matching), len(supports) - 500)
    except AssertionError:
        pass
    else:
        raise AssertionError("insufficient obstruction count was accepted")


def main():
    require(len(CELLS) == len(set(CELLS)) == 117,
            "coarse geometry collision")
    require(len(LABELS) == len(set(LABELS)) == 73125,
            "microbox label collision")
    require(len(CODES) == len(set(CODES)) == 73125,
            "physical-code collision")
    points = prototype_points()
    require(len(points) == 325, "prototype point census drift")

    # Check the untranslated abstract packet directly before lifting it.
    abstract_incidence = Counter()
    for x, y, z in ROW_PATTERN:
        defect = tuple(x[j] + z[j] - 2 * y[j] for j in range(2))
        require(all(value % Q == 0 for value in defect),
                "prototype row midpoint failure")
        require(sum((x[j] - z[j])**2 for j in range(2)) > 0,
                "prototype row has zero cost")
        abstract_incidence[x] += 1
        abstract_incidence[z] += 1
        abstract_incidence[y] -= 2
    require(dict(abstract_incidence) == {p: 0 for p in PROTOTYPE},
            "prototype incidence does not cancel")

    edges = dilation_edges()
    components = connected_components(edges)
    matching = canonical_matching(edges)
    blocked = frozenset(LABEL_POS[v] for edge in matching for v in edge)
    require(len(edges) == 2382, "dilation edge census drift")
    require(len(components) == 1632 and max(map(len, components)) == 9,
            "dilation component census drift")
    require(len(matching) == 1789 and len(blocked) == 3578,
            "dilation matching census drift")

    templates = admissible_templates(points)
    lookup = vertex_lookup()
    supports, records, count_by_fiber = deterministic_packing(
        blocked, templates, lookup
    )
    require(len(supports) == len(records) == 2852,
            "packet packing count drift")
    hist = Counter(count_by_fiber.values())
    require(hist == Counter({12: 74, 14: 52, 16: 40, 10: 31,
                             11: 11, 8: 6, 13: 5, 9: 5, 7: 1}),
            "per-fiber packet histogram drift")

    raw_hist = Counter()
    carry_hist = Counter()
    for _, _, rows in records:
        for row in rows:
            carry_hist[row[3:7]] += 1
            raw_hist[row[7]] += 1
    require(sum(raw * count for raw, count in raw_hist.items()) > 0,
            "aggregate raw cost is not positive")

    total, gate, forced = density_audit(len(matching), len(supports))
    matching_records = tuple(
        tuple(LABEL_POS[vertex] for vertex in edge) for edge in matching
    )
    certificate_sha = certificate_audit(
        matching_records, templates, supports, records
    )
    planted_failures(matching, blocked, supports, records)

    print("PASS_Q30_FOURPOINT_ONE_BLOCK_PACKING")
    print(f"GEOMETRY coarse=117 microboxes={total} prototype_points={len(points)}")
    print(f"DILATION edges={len(edges)} components={len(components)} "
          f"matching={len(matching)} endpoints={len(blocked)}")
    print(f"FOURPOINT templates={len(templates)} packets={len(supports)} "
          f"vertices={4*len(supports)} rows={4*len(supports)}")
    print(f"FIBER_HIST {dict(sorted(hist.items()))}")
    print(f"RAW_HIST {dict(sorted(raw_hist.items()))}")
    print(f"CARRY_TYPES {len(carry_hist)}")
    print(f"DISJOINT obstructions={forced} required=4219 margin={forced-4219}")
    print(f"GATE allowed_deletions=4218 max_retained={total-forced} gate={gate}")
    print(f"MATCHING_DIGEST {digest(matching_records)}")
    print(f"TEMPLATE_DIGEST {digest(templates)}")
    print(f"SUPPORT_DIGEST {digest(supports)}")
    print(f"PACKET_DIGEST {digest(records)}")
    print(f"CERTIFICATE_SHA256 {certificate_sha}")
    print("SCOPE one_block_complete_aligned_q30_microbox_unions_only")
    print("PLANTED_FAILURES_REJECTED")


if __name__ == "__main__":
    require(sys.argv[1:] in ([], ["--self-test"]), "unexpected arguments")
    main()

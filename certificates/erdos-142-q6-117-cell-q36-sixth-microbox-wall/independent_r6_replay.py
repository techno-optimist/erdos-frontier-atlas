#!/usr/bin/env python3
"""Independent stdlib hostile replay for the q=36 one-block wall.

This script deliberately does not import the producer or primary verifier.  It
uses a bitmask dynamic program for component matchings and directly checks the
physical midpoint rows at exact rational interior points.
"""
from collections import Counter, defaultdict, deque
from fractions import Fraction
from functools import lru_cache
from itertools import product
import hashlib
import json
from math import gcd, lcm
from pathlib import Path
import sys


Q0, R, Q = 6, 6, 36
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFFSETS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
           (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
EXPECTED = {
    "matching": "d520ceaf418068665a166617e747da23b970d701c71de1cf13b5eac8d368bff1",
    "support": "36c478be01b818a32980563b193ae2290e9db41048f6a2e757d77609cb0dd243",
    "expanded": "e8ae9b924fa16076ecf9a117f8a210c665bca1bc1c01d7490f3c7f97a90b5bfc",
    "payload": "9aa110472ac2da97d919e30fea2cfdee1b308c2f743bca4b70d67781f819f544",
    "certificate_bytes": "318bb7ac5cb3bac2dba1b10815c47d0997bf95c8b88f8dfd5d2da1f7a6720d5d",
    "primary_verifier_bytes": "f7a0b693220cf4891c954f8675ce78bcd6c40a68ec3ce59889ab1b22739576d9",
    "readme_bytes": "b507cc836a0d8b399479b99bb44f77bfb8550a2ddbceaf811669607c368bba88",
}


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def canonical_hash(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_geometry():
    cells = tuple((a, b, (a + dx) % Q0, (b + dy) % Q0)
                  for a, b in BASE for dx, dy in OFFSETS)
    check(len(cells) == len(set(cells)) == 117, "coarse-cell census")
    labels = tuple((ci, sub) for ci in range(117)
                   for sub in product(range(R), repeat=4))
    codes = tuple(tuple(R*cells[ci][j] + sub[j] for j in range(4))
                  for ci, sub in labels)
    check(len(labels) == len(set(labels)) == 151632, "label census")
    check(len(codes) == len(set(codes)) == 151632, "physical-code census")
    return cells, labels, codes, {v: i for i, v in enumerate(labels)}, {
        v: i for i, v in enumerate(codes)}


def build_dilation(cells, label_index):
    edges = set()
    for source, a in enumerate(cells):
        for target, b in enumerate(cells):
            active = tuple(j for j in range(4) if a[j] != b[j])
            if not active:
                continue
            if any(b[j] not in (a[j], (a[j] - 1) % Q0) for j in range(4)):
                continue
            if not any(a[j] == 0 and b[j] == Q0-1 for j in active):
                continue
            inactive = tuple(j for j in range(4) if j not in active)
            for vals in product(range(R), repeat=len(inactive)):
                lo, hi = [0]*4, [R-1]*4
                for j, val in zip(inactive, vals):
                    lo[j] = hi[j] = val
                edge = tuple(sorted((label_index[(source, tuple(lo))],
                                     label_index[(target, tuple(hi))])))
                edges.add(edge)
    edges = tuple(sorted(edges))
    check(len(edges) == 3811, "dilation edge count")
    return edges


def components_and_matching(edges, labels, cells):
    adjacency = defaultdict(set)
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    unseen, components = set(adjacency), []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        comp, queue = {start}, deque([start])
        while queue:
            a = queue.popleft()
            for b in adjacency[a]:
                if b in unseen:
                    unseen.remove(b)
                    comp.add(b)
                    queue.append(b)
        components.append(tuple(sorted(comp)))
    components.sort()
    check(len(components) == 2785 and max(map(len, components)) == 9,
          "component census")

    matching = []
    for comp in components:
        pos = {v: i for i, v in enumerate(comp)}
        neighbors = [0]*len(comp)
        for v in comp:
            for w in adjacency[v]:
                if w in pos:
                    neighbors[pos[v]] |= 1 << pos[w]

        @lru_cache(None)
        def solve(mask):
            if not mask:
                return 0, ()
            lowbit = mask & -mask
            i = lowbit.bit_length()-1
            best_n, best_edges = solve(mask ^ lowbit)
            choices = neighbors[i] & mask
            while choices:
                wbit = choices & -choices
                choices ^= wbit
                j = wbit.bit_length()-1
                n, chosen = solve(mask ^ lowbit ^ wbit)
                edge = tuple(sorted((comp[i], comp[j])))
                candidate = tuple(sorted((edge,) + chosen))
                n += 1
                if n > best_n or (n == best_n and candidate < best_edges):
                    best_n, best_edges = n, candidate
            return best_n, best_edges

        _, chosen = solve((1 << len(comp))-1)
        matching.extend(chosen)
    matching = tuple(sorted(matching))
    check(len(matching) == 2986, "maximum matching count")
    flat = tuple(v for e in matching for v in e)
    check(len(flat) == len(set(flat)) == 5972, "matching disjointness")

    records, wraps_hist = [], Counter()
    for edge in matching:
        oriented = None
        for source, target in (edge, edge[::-1]):
            ca, sa = labels[source]
            cb, sb = labels[target]
            a, b = cells[ca], cells[cb]
            active = tuple(j for j in range(4) if a[j] != b[j])
            wraps = tuple(j for j in active if a[j] == 0 and b[j] == Q0-1)
            if (wraps and
                all(b[j] in (a[j], (a[j]-1) % Q0) for j in range(4)) and
                all(sa[j] == 0 and sb[j] == R-1 for j in active) and
                all(sa[j] == sb[j] for j in range(4) if j not in active)):
                oriented = source, target, active, wraps
                break
        check(oriented is not None, "dilation orientation")
        source, target, active, wraps = oriented
        records.append((source, target, sum(1 << j for j in active),
                        sum(1 << j for j in wraps)))
        wraps_hist[len(wraps)] += 1

        # Directly check the two physical rows and their telescoping RHS.
        ca, source_sub = labels[source]
        _, target_sub = labels[target]
        a = cells[ca]
        for t in (Fraction(1, 100), Fraction(1, 36), Fraction(1, 19)):
            low_t = [Fraction(R*a[j] + source_sub[j], Q) + Fraction(1, 2*Q)
                     for j in range(4)]
            low_3t = list(low_t)
            high_t = list(low_t)
            high_3t = list(low_t)
            for j in active:
                b = (a[j]-1) % Q0
                low_t[j] = Fraction(a[j], Q0) + t/Q0
                low_3t[j] = Fraction(a[j], Q0) + 3*t/Q0
                high_t[j] = Fraction(b+1, Q0) - t/Q0
                high_3t[j] = Fraction(b+1, Q0) - 3*t/Q0
            source_code = tuple(R*a[j] + source_sub[j] for j in range(4))
            target_cell = cells[labels[target][0]]
            target_code = tuple(R*target_cell[j] + target_sub[j] for j in range(4))
            for point in (low_t, low_3t):
                check(all(Fraction(source_code[j], Q) < point[j] <
                          Fraction(source_code[j]+1, Q) for j in range(4)),
                      "source point leaves its open microbox")
            for point in (high_t, high_3t):
                check(all(Fraction(target_code[j], Q) < point[j] <
                          Fraction(target_code[j]+1, Q) for j in range(4)),
                      "target point leaves its open microbox")
            rows = ((low_t, high_t, high_3t),
                    (low_3t, low_t, high_t))
            direct_rhs = Fraction(0)
            for x, y, z in rows:
                defects = tuple(x[j]+z[j]-2*y[j] for j in range(4))
                check(all(d.denominator == 1 for d in defects),
                      "nonintegral torus defect")
                direct_rhs += sum((x[j]-z[j])**2 for j in range(4))
            formula = (sum(Fraction(8)*t*t/9 for j in active if j not in wraps)
                       + sum(2*(1-Fraction(2)*t/3)**2 for _ in wraps))
            check(direct_rhs == formula > 0, "direct dilation RHS")
    check(wraps_hist == Counter({1: 2986}), "matching wrap census")
    check(canonical_hash(tuple(records)) == EXPECTED["matching"],
          "matching semantic digest")
    return frozenset(flat), tuple(records), components


def packet_prototypes():
    support = {(R*dx+s) % Q for dx, _ in OFFSETS for s in range(R)}
    # Rebuild the correlated two-coordinate support, not its projections.
    support = {((R*dx+s) % Q, (R*dy+t) % Q)
               for dx, dy in OFFSETS for s, t in product(range(R), repeat=2)}
    shift = (0, 4)
    order = lcm(Q//gcd(Q, shift[0]), Q//gcd(Q, shift[1]))
    check(order == 9, "translation order")
    unseen = set(product(range(Q), repeat=2))
    intersections = []
    while unseen:
        start = min(unseen)
        orbit = {(start[0], (start[1]+4*k) % Q) for k in range(order)}
        unseen -= orbit
        hit = tuple(sorted(orbit & support))
        if hit:
            intersections.append(hit)
    intersections.sort()
    hist = Counter(map(len, intersections))
    check(hist == Counter({1: 24, 2: 36, 3: 24, 4: 24, 5: 12, 6: 24}),
          "prototype intersection histogram")
    packets = tuple(p for p in intersections if len(p) == 6)
    check(len(packets) == 24 and len(set().union(*map(set, packets))) == 144,
          "prototype six-packets")
    for packet in packets:
        check(len({p[0] for p in packet}) == 1, "prototype first digit")
    return packets, hist


def expand_packet(packet, codes, code_index):
    support = set(packet)
    starts = [v for v in packet
              if code_index.get((*codes[v][:3], (codes[v][3]-4) % Q))
              not in support]
    check(len(starts) == 1, "unique packet start")
    ordered = tuple(code_index[(*codes[starts[0]][:3],
                                (codes[starts[0]][3]+4*k) % Q)]
                    for k in range(6))
    check(set(ordered) == support, "packet order")
    endpoint_pairs = ((4, 5), (0, 2), (1, 3), (2, 4), (3, 5), (0, 1))
    offset = tuple(Fraction(k, 7) for k in range(1, 5))
    incidence, rows = Counter(), []
    for centre, (li, ri) in enumerate(endpoint_pairs):
        x, y, z = ordered[li], ordered[centre], ordered[ri]
        defect = tuple(codes[x][j]+codes[z][j]-2*codes[y][j]
                       for j in range(4))
        check(all(d % Q == 0 for d in defect), "digit midpoint")
        carries = tuple(d//Q for d in defect)
        raw = sum((codes[x][j]-codes[z][j])**2 for j in range(4))
        check(raw > 0 and len({x, y, z}) == 3, "nondegenerate row")
        incidence[x] += 1
        incidence[z] += 1
        incidence[y] -= 2
        xp = tuple(Fraction(codes[x][j], Q)+offset[j]/Q for j in range(4))
        yp = tuple(Fraction(codes[y][j], Q)+offset[j]/Q for j in range(4))
        zp = tuple(Fraction(codes[z][j], Q)+offset[j]/Q for j in range(4))
        check(all(xp[j]+zp[j]-2*yp[j] == carries[j] for j in range(4)),
              "physical torus midpoint")
        check(sum((xp[j]-zp[j])**2 for j in range(4)) == Fraction(raw, Q*Q),
              "physical raw cost")
        rows.append((x, y, z, *carries, raw))
    check(set(incidence) == support and all(v == 0 for v in incidence.values()),
          "potential incidence cancellation")
    check(sum(row[-1] for row in rows) > 0, "positive packet RHS")
    return tuple(rows)


def packets(blocked, cells, codes, code_index):
    prototypes, hist = packet_prototypes()
    all_packets, kept = [], []
    for bi, (a, b) in enumerate(BASE):
        for s0, s1 in product(range(R), repeat=2):
            first = (R*a+s0, R*b+s1)
            for proto in prototypes:
                packet = tuple(sorted(code_index[(first[0], first[1],
                                                  (u+R*a) % Q,
                                                  (v+R*b) % Q)]
                                      for u, v in proto))
                all_packets.append(packet)
                if blocked.isdisjoint(packet):
                    kept.append(packet)
    all_packets, kept = tuple(sorted(all_packets)), tuple(sorted(kept))
    check(len(all_packets) == 7776 and len(kept) == 6323,
          "lifted and blocked packet count")
    check(len(all_packets)-len(kept) == 1453, "blocked packet count")
    flat = tuple(v for p in kept for v in p)
    check(len(flat) == len(set(flat)) == 37938, "packet disjointness")
    check(blocked.isdisjoint(flat), "cross-family disjointness")
    records = tuple((packet, expand_packet(packet, codes, code_index))
                    for packet in kept)
    raw_hist = Counter(row[-1] for _, rows in records for row in rows)
    carry_hist = Counter(row[3:7] for _, rows in records for row in rows)
    check(raw_hist == Counter({16: 12164, 64: 23082, 784: 2210, 1024: 482}),
          "raw histogram")
    check(carry_hist == Counter({(0, 0, 0, -1): 7187,
                                 (0, 0, 0, 0): 23564,
                                 (0, 0, 0, 1): 7187}), "carry histogram")
    check(canonical_hash(kept) == EXPECTED["support"], "support digest")
    check(canonical_hash(records) == EXPECTED["expanded"], "expanded digest")
    return kept, records, hist, raw_hist, carry_hist


def audit_certificate(target):
    cert = target / "frozen_semantic_certificate.json"
    primary = target / "verify_r6_six_of_nine_packing.py"
    readme = target / "README.md"
    check(file_hash(cert) == EXPECTED["certificate_bytes"], "certificate bytes")
    check(file_hash(primary) == EXPECTED["primary_verifier_bytes"], "primary bytes")
    check(file_hash(readme) == EXPECTED["readme_bytes"], "README bytes")
    payload = json.loads(cert.read_text(encoding="utf-8"))
    semantic = dict(payload)
    digests = semantic.pop("digests")
    check(canonical_hash(semantic) == EXPECTED["payload"], "payload digest")
    check(digests == {"dilation_semantic": EXPECTED["matching"],
                      "packet_support": EXPECTED["support"],
                      "packet_expanded_semantic": EXPECTED["expanded"],
                      "payload_semantic": EXPECTED["payload"]}, "digest binding")
    check(payload["scope"] == {
        "one_block_complete_aligned_microbox_union": True,
        "arbitrary_word_language_capacity": False,
        "proper_submicrobox_carving": False}, "scope binding")


def main(target):
    cells, labels, codes, label_index, code_index = build_geometry()
    edges = build_dilation(cells, label_index)
    blocked, matching_records, components = components_and_matching(
        edges, labels, cells)
    kept, records, hist, raw_hist, carry_hist = packets(
        blocked, cells, codes, code_index)
    total = len(codes)
    gate = Fraction(49, 576)*Q**4
    forced = len(matching_records)+len(kept)
    check(gate == 142884 and total-gate == 8748, "gate arithmetic")
    check(forced == 9309 and total-forced == 142323 and forced-8748 == 561,
          "obstruction arithmetic")
    audit_certificate(target)
    print("PASS_INDEPENDENT_R6_Q36_ONE_BLOCK_WALL")
    print(f"GEOMETRY_OK coarse={len(cells)} microboxes={total} codes_unique")
    print(f"DILATION_OK edges={len(edges)} components={len(components)} "
          f"max_component={max(map(len, components))} matching={len(matching_records)}")
    print(f"PACKETS_OK full=7776 blocked=1453 retained={len(kept)} "
          f"rows={sum(len(x) for _, x in records)}")
    print(f"INTERSECTION_HIST {dict(sorted(hist.items()))}")
    print(f"RAW_HIST {dict(sorted(raw_hist.items()))}")
    print(f"CARRY_HIST {dict(sorted(carry_hist.items()))}")
    print(f"DISJOINT_OK obstructions={forced} margin={forced-8748}")
    print(f"GATE_OK total={total} allowed_deletions=8747 "
          f"max_retained={total-forced} gate={gate}")
    print("DEPENDENCIES_OK stdlib_only no_import no_solver")
    print("SCOPE one_block_complete_aligned_q36_microbox_unions_only")


if __name__ == "__main__":
    check(len(sys.argv) == 3 and sys.argv[1] == "--target",
          "usage: independent_r6_replay.py --target PACKET_DIR")
    main(Path(sys.argv[2]).resolve())

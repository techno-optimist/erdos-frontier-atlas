#!/usr/bin/env python3
"""Independent stdlib audit of the frozen q=42/r=7 one-block certificate.

This file deliberately rebuilds the geometry, matching and both packet
layers from the public constants; it neither imports nor executes the
discovery program or the supplied replay.  The JSON is read only after the
calculation, as a frozen claim to compare against.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import gcd, lcm
from pathlib import Path
import hashlib
import json
import sys


HERE = Path(__file__).resolve().parent
TARGET = HERE
FROZEN = TARGET / "frozen_semantic_certificate.json"

Q0, R, Q = 6, 7, 42
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFF = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
       (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
SHIFT1, SHIFT2 = (6, 12), (0, 6)


def fail(msg):
    raise AssertionError(msg)


def need(ok, msg):
    if not ok:
        fail(msg)


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode("ascii")


def sha(x):
    return hashlib.sha256(canon(x)).hexdigest()


# Physical q=42 boxes are built without referencing the supplied verifier.
CELLS = tuple((a, b, (a + dx) % Q0, (b + dy) % Q0)
              for a, b in BASE for dx, dy in OFF)
SUB = tuple(product(range(R), repeat=4))
LABELS = tuple((i, s) for i in range(len(CELLS)) for s in SUB)
CODES = tuple(tuple(R * CELLS[i][j] + s[j] for j in range(4))
              for i, s in LABELS)
LID = {z: i for i, z in enumerate(LABELS)}
CID = {z: i for i, z in enumerate(CODES)}


def build_dilation_graph():
    """Strict residual low/high edges induced by a coarse wrap decrement."""
    edges = set()
    for i, p in enumerate(CELLS):
        for j, q in enumerate(CELLS):
            live = [k for k in range(4) if p[k] != q[k]]
            if not live:
                continue
            if not all(q[k] == p[k] or q[k] == (p[k] - 1) % Q0 for k in range(4)):
                continue
            if not any(p[k] == 0 and q[k] == Q0 - 1 for k in live):
                continue
            still = [k for k in range(4) if k not in live]
            for digits in product(range(R), repeat=len(still)):
                lo, hi = [0] * 4, [R - 1] * 4
                for k, digit in zip(still, digits):
                    lo[k] = hi[k] = digit
                edges.add(tuple(sorted(((i, tuple(lo)), (j, tuple(hi))))))
    return tuple(sorted(edges))


def components(edges):
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    unseen, ans = set(adj), []
    while unseen:
        seed = min(unseen)
        q, piece = deque([seed]), {seed}
        unseen.remove(seed)
        while q:
            a = q.popleft()
            for b in adj[a]:
                if b in unseen:
                    unseen.remove(b)
                    piece.add(b)
                    q.append(b)
        ans.append(tuple(sorted(piece)))
    return tuple(sorted(ans))


def maximum_lex_matching(edges):
    """A fresh exhaustive matching implementation; pieces have <=9 vertices."""
    edge_set = frozenset(edges)
    chosen = []
    for comp in components(edges):
        comp_set = frozenset(comp)
        nbr = {v: tuple(sorted(w for w in comp if tuple(sorted((v, w))) in edge_set))
               for v in comp}

        @lru_cache(None)
        def search(available):
            left = tuple(v for v in comp if v in available)
            if not left:
                return ()
            v = left[0]
            best = search(frozenset(available - {v}))
            for w in nbr[v]:
                if w not in available:
                    continue
                trial = (tuple(sorted((v, w))),) + search(frozenset(available - {v, w}))
                trial = tuple(sorted(trial))
                if len(trial) > len(best) or (len(trial) == len(best) and trial < best):
                    best = trial
            return best

        chosen.extend(search(comp_set))
    return tuple(sorted(chosen))


def edge_orientation(edge):
    def valid(lo_side, hi_side):
        i, low = lo_side
        j, high = hi_side
        a, b = CELLS[i], CELLS[j]
        live = tuple(k for k in range(4) if a[k] != b[k])
        wraps = tuple(k for k in live if a[k] == 0 and b[k] == Q0 - 1)
        if (not wraps or
            not all(b[k] == a[k] or b[k] == (a[k] - 1) % Q0 for k in range(4)) or
            not all(low[k] == 0 and high[k] == R - 1 for k in live) or
            not all(low[k] == high[k] for k in range(4) if k not in live)):
            return None
        return lo_side, hi_side, live, wraps
    return valid(*edge) or valid(edge[1], edge[0])


def validate_dilation_recurrence(matching):
    """Verify the two actual torus triples behind the boundedness recurrence."""
    wrap_hist, records = Counter(), []
    for e in matching:
        oriented = edge_orientation(e)
        need(oriented is not None, "unorientable strict-dilation edge")
        source, target, live, wraps = oriented
        wrap_hist[len(wraps)] += 1
        records.append((LID[source], LID[target], sum(1 << k for k in live),
                        sum(1 << k for k in wraps)))
        a = CELLS[source[0]]
        for t in (Fraction(1, 100), Fraction(1, 42), Fraction(1, 29)):
            # Coordinates below are in units of a coarse 1/6 interval.
            correction = Fraction(0)
            for k in live:
                A_t, A_3t = Fraction(a[k]) + t, Fraction(a[k]) + 3*t
                B_t, B_3t = Fraction((a[k] - 1) % Q0 + 1) - t, Fraction((a[k] - 1) % Q0 + 1) - 3*t
                # (A_t,B_3t; B_t) and (A_3t,B_t; A_t) are torus midpoints.
                need((A_t + B_3t - 2 * B_t).denominator == 1,
                     "first dilation triple lacks integral carry")
                need((A_3t + B_t - 2 * A_t).denominator == 1,
                     "second dilation triple lacks integral carry")
                c1 = (A_t - B_3t) ** 2 - 2 * A_t ** 2 - 2 * B_3t ** 2 + 4 * B_t ** 2
                c2 = (A_3t - B_t) ** 2 - 2 * A_3t ** 2 - 2 * B_t ** 2 + 4 * A_t ** 2
                correction += c1 + c2
            need(correction == len(wraps) * (72 - 48 * t),
                 "G recurrence correction mismatch")
        # The infinite telescope uses 0<t<3t<1/7 in the low box and the
        # corresponding residual offsets 1-t,1-3t in the high box.
        for n in range(1, 12):
            t = Fraction(1, 14 * 3 ** n)
            need(0 < t < 3*t < Fraction(1, R), "low-box telescope exits")
            need(Fraction(R-1, R) < 1-3*t < 1-t < 1, "high-box telescope exits")
    need(wrap_hist == Counter({1: 4617}), "matching must have one wrap each")
    return tuple(records), wrap_hist


def trans(point, shift, k):
    return ((point[0] + k * shift[0]) % Q, (point[1] + k * shift[1]) % Q)


def prototype():
    return frozenset(((R * dx + s) % Q, (R * dy + t) % Q)
                     for dx, dy in OFF for s, t in product(range(R), repeat=2))


@lru_cache(None)
def balanced_rows(packet):
    """Solve the finite unit-incidence condition independently by DFS."""
    pts = tuple(packet)
    place = {p: i for i, p in enumerate(pts)}
    choices = []
    for middle in pts:
        rows = []
        others = tuple(p for p in pts if p != middle)
        for x, z in combinations(others, 2):
            if all((x[k] + z[k] - 2 * middle[k]) % Q == 0 for k in (0, 1)):
                raw = (x[0] - z[0]) ** 2 + (x[1] - z[1]) ** 2
                if raw:
                    rows.append((x, middle, z, raw))
        if not rows:
            return None
        choices.append(tuple(sorted(rows)))

    degree = [0] * len(pts)
    taken = []
    def recurse(idx):
        if idx == len(pts):
            return tuple(taken) if degree == [2] * len(pts) else None
        # Every remaining row has two endpoints, so this is a cheap exact
        # capacity pruning condition rather than a copy of producer logic.
        if sum(2-d for d in degree) != 2 * (len(pts) - idx):
            return None
        for x, y, z, raw in choices[idx]:
            ix, iz = place[x], place[z]
            if degree[ix] == 2 or degree[iz] == 2:
                continue
            degree[ix] += 1
            degree[iz] += 1
            taken.append((x, y, z, raw))
            out = recurse(idx + 1)
            if out is not None:
                return out
            taken.pop()
            degree[ix] -= 1
            degree[iz] -= 1
        return None
    return recurse(0)


def prototypes_for(shift):
    support = prototype()
    order = lcm(Q // gcd(Q, shift[0]), Q // gcd(Q, shift[1]))
    need(order == 7, "not order seven")
    orbit_set = {tuple(sorted(trans(p, shift, k) for k in range(order))) for p in support}
    inter = tuple(sorted(tuple(p for p in orbit if p in support) for orbit in orbit_set))
    hist = Counter(map(len, inter))
    usable = tuple(p for p in inter if len(p) >= 3 and balanced_rows(p) is not None)
    occupied = tuple(x for p in usable for x in p)
    need(len(occupied) == len(set(occupied)), "prototype packets overlap")
    wanted = ({1:51,2:44,3:58,4:41,5:21,6:8,7:1}, {5:21,6:8,7:1}, 160) if shift == SHIFT1 else \
             ({1:70,2:70,3:49,4:35,5:28}, {5:28}, 140)
    need(dict(sorted(hist.items())) == wanted[0], "prototype orbit histogram")
    need(dict(sorted(Counter(map(len, usable)).items())) == wanted[1], "usable packet census")
    need(len(occupied) == wanted[2], "prototype vertex census")
    return usable, hist


def lift_layer(shift, prohibited):
    proto, inter_hist = prototypes_for(shift)
    ans = []
    for bi, s0, s1, shape in product(range(len(BASE)), range(R), range(R), proto):
        a, b = BASE[bi]
        first = (R*a + s0, R*b + s1)
        packet = tuple(sorted(CID[(first[0], first[1], (x + R*a) % Q, (y + R*b) % Q)]
                              for x, y in shape))
        if prohibited.isdisjoint(packet):
            ans.append(packet)
    ans = tuple(sorted(ans))
    flat = tuple(x for p in ans for x in p)
    need(len(flat) == len(set(flat)), "lifted packets overlap within layer")
    need(prohibited.isdisjoint(flat), "lifted packet hits prohibited support")
    full = len(BASE) * R * R * len(proto)
    expected = (13230, 11534, 61452) if shift == SHIFT1 else (12348, 3413, 17065)
    need((full, len(ans), len(flat)) == expected, "lifted layer count mismatch")
    return ans, inter_hist


def physical_rows(packet):
    fine = tuple(CODES[i] for i in packet)
    need(len({p[:2] for p in fine}) == 1, "packet leaks first pair")
    last = tuple(sorted(p[2:] for p in fine))
    plan = balanced_rows(last)
    need(plan is not None and len(plan) == len(packet), "no balanced physical row plan")
    lookup = {CODES[i][2:]: i for i in packet}
    incidence, out = Counter(), []
    offset = (Fraction(1,8), Fraction(2,8), Fraction(3,8), Fraction(4,8))
    for x2, y2, z2, raw2 in plan:
        x, y, z = lookup[x2], lookup[y2], lookup[z2]
        defect = tuple(CODES[x][k] + CODES[z][k] - 2*CODES[y][k] for k in range(4))
        need(all(v % Q == 0 for v in defect), "fine digits fail torus midpoint")
        carry = tuple(v // Q for v in defect)
        raw = sum((CODES[x][k] - CODES[z][k]) ** 2 for k in range(4))
        need(raw == raw2 and raw > 0, "raw endpoint cost corrupt")
        # Exact physical representative at common strict-interior offset.
        xp = tuple((Fraction(CODES[x][k]) + offset[k]) / Q for k in range(4))
        yp = tuple((Fraction(CODES[y][k]) + offset[k]) / Q for k in range(4))
        zp = tuple((Fraction(CODES[z][k]) + offset[k]) / Q for k in range(4))
        need(all(xp[k] + zp[k] - 2*yp[k] == carry[k] for k in range(4)),
             "actual physical midpoint/carry failure")
        need(sum((xp[k]-zp[k])**2 for k in range(4)) == Fraction(raw, Q*Q),
             "actual physical raw RHS failure")
        incidence[x] += 1
        incidence[z] += 1
        incidence[y] -= 2
        out.append((x, y, z, *carry, raw))
    need(set(incidence) == set(packet) and all(v == 0 for v in incidence.values()),
         "packet potential incidence does not cancel")
    need(sum(r[-1] for r in out) > 0, "packet has no positive aggregate RHS")
    return tuple(out)


def check_packets(blocked):
    one, h1 = lift_layer(SHIFT1, blocked)
    one_vertices = frozenset(v for p in one for v in p)
    two, h2 = lift_layer(SHIFT2, blocked | one_vertices)
    two_vertices = frozenset(v for p in two for v in p)
    need(one_vertices.isdisjoint(two_vertices), "two packet layers intersect")
    expanded = tuple(tuple((p, physical_rows(p)) for p in layer) for layer in (one, two))
    raw = Counter(row[-1] for layer in expanded for _, rs in layer for row in rs)
    carry = Counter(row[3:7] for layer in expanded for _, rs in layer for row in rs)
    need(Counter(map(len, one)) == Counter({5:8151, 6:2984, 7:399}), "layer 1 packet sizes")
    need(Counter(map(len, two)) == Counter({5:3413}), "layer 2 packet sizes")
    expected_raw = {36:6456,144:9575,180:14661,360:11143,468:8353,612:8010,
                    720:6225,900:664,936:4512,1224:1219,1296:370,1440:3103,
                    1476:1352,1620:1835,1872:772,2196:267}
    expected_carry = {(0,0,-1,-1):5266,(0,0,-1,0):7828,(0,0,-1,1):4267,
                      (0,0,0,-1):11215,(0,0,0,0):20045,(0,0,0,1):12535,
                      (0,0,1,-1):3831,(0,0,1,0):10020,(0,0,1,1):3510}
    need(dict(sorted(raw.items())) == expected_raw, "raw-cost histogram")
    need(dict(sorted(carry.items())) == expected_carry, "physical carry histogram")
    need(sum(raw.values()) == 78517, "expanded-row count")
    need(sum(k*v for k, v in raw.items()) == 39815496, "aggregate raw cost")
    return (one, two), expanded, (h1, h2), raw, carry


def compare_frozen(records, layers, expanded, raw, carry):
    before = FROZEN.read_bytes()
    payload = json.loads(before)
    need(hashlib.sha256(before).hexdigest() == "3eb6de036e2f8294f49f282e5f98769351ffe55fe25155a2dbf3077e14bbafa3",
         "frozen source bytes changed")
    need(payload["geometry"]["microboxes"] == len(CODES) == 280917, "frozen geometry")
    need(payload["dilation"]["matching_count"] == len(records) == 4617, "frozen matching")
    need(payload["packet_layers"][0]["retained_packets"] == len(layers[0]) == 11534, "frozen first layer")
    need(payload["packet_layers"][1]["retained_packets"] == len(layers[1]) == 3413, "frozen second layer")
    need(payload["packet_semantics"]["raw_fine_digit_square_histogram"] == {str(k):v for k,v in raw.items()}, "frozen raw histogram")
    need(payload["packet_semantics"]["carry_histogram"] == {','.join(map(str,k)):v for k,v in carry.items()}, "frozen carries")
    need(sha(records) == payload["digests"]["dilation_semantic"], "dilation semantic digest")
    need(sha(layers) == payload["digests"]["packet_support"], "support semantic digest")
    need(sha(expanded) == payload["digests"]["packet_expanded_semantic"], "expanded semantic digest")
    return hashlib.sha256(before).hexdigest()


def main():
    need(len(CELLS) == len(set(CELLS)) == 117, "coarse cell geometry")
    need(len(CODES) == len(set(CODES)) == 117 * R**4, "q42 physical geometry")
    edges = build_dilation_graph()
    comps = components(edges)
    need(len(edges) == 5712 and len(comps) == 4368 and max(map(len, comps)) == 9,
         "dilation graph census")
    matching = maximum_lex_matching(edges)
    need(len(matching) == 4617, "maximum matching census")
    endpoints = frozenset(LID[p] for e in matching for p in e)
    need(len(endpoints) == 9234, "matching endpoint collision")
    records, wraps = validate_dilation_recurrence(matching)
    layers, expanded, hists, raw, carry = check_packets(endpoints)
    packet_count = sum(map(len, layers))
    total, forced, gate = len(CODES), len(matching) + packet_count, Fraction(49,576) * Q**4
    need((total, packet_count, forced, gate) == (280917, 14947, 19564, Fraction(1058841,4)),
         "packing arithmetic")
    need(total - forced == 261353 < gate, "one-block gate not crossed")
    need(total - 264711 == 16206 and forced - 16207 == 3357, "strict gate margin")
    cert_sha = compare_frozen(records, layers, expanded, raw, carry)
    # Scope is checked textually too: no unsupported word-capacity theorem is
    # silently advertised in the frozen README.
    readme = (TARGET / "README.md").read_text(encoding="utf-8")
    need("not a word-language capacity theorem" in readme and "Not proved:" in readme,
         "scope disclaimer absent")
    print("PASS_INDEPENDENT_R7_Q42_TWO_LAYER_ONE_BLOCK_AUDIT")
    print("GEOMETRY_OK coarse=117 microboxes=280917")
    print("DILATION_OK edges=5712 components=4368 max_component=9 matching=4617 wraps={1: 4617}")
    print("PACKETS_OK first=11534 second=3413 supports=61452+17065 rows=78517")
    print("PHYSICAL_OK carries=9 raw_total=39815496 incidence=zero common_offset=(1/8,2/8,3/8,4/8)")
    print("DISJOINT_OK forced=19564 required=16207 margin=3357")
    print("GATE_OK total=280917 allowed_deletions=16206 max_retained=261353 gate=1058841/4")
    print("DIGESTS_OK matching={} support={} expanded={}".format(sha(records), sha(layers), sha(expanded)))
    print("CERTIFICATE_SHA256", cert_sha)
    print("SCOPE one_block_complete_aligned_q42_microbox_unions_only")


if __name__ == "__main__":
    need(sys.argv[1:] in ([], ["--self-test"]), "unexpected arguments")
    main()

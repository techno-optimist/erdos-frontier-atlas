#!/usr/bin/env python3
"""Independent hostile replay of the q=12 half-cell dilation wall.

This file imports no Atlas or sibling-scratch code.  It reconstructs the
117-cell q=6 alphabet, its 1,872 physical q=12 half-microboxes, all strict
dilation edges, the claimed lifted 109-edge matching, and a stronger
deterministic 148-edge greedy matching.  It also checks the two scalar rows,
both word orientations, a mixed global row, and the finite telescope.
"""
from __future__ import annotations

from fractions import Fraction as F
from itertools import product
import hashlib
import json

Q0 = 6
Q = 12
N0 = 117
N = 1872
GATE = 1764
EDGE_DIGEST = "fe25fe2b765bef0f573ad96997e2fe007fa99e81726caf7bf34ace943e895434"
CLAIMED_MATCHING_DIGEST = "335bc10a35a0a15fd31c0ce58a3dbb159708fa90628d903512f08240a8b333e7"
GREEDY_MATCHING_DIGEST = "e49c28c5dd8e750ee1bfe71579e13d5dc38ef36545e7fc94424c3fee7cb7f521"

S0 = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
      (5, 0), (5, 1), (5, 2))
OFFSETS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
           (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))

# This is the already public coarse matching, used only to audit the claimed
# 106 canonical lifts.  The independent 148-edge matching below does not use
# this list.
COARSE_MATCHING = (
    (3, 55), (4, 17), (16, 68), (24, 25), (36, 37), (39, 52),
    (40, 53), (46, 96), (54, 106), (12, 59), (56, 69), (76, 77),
    (78, 79), (83, 84), (86, 87), (91, 92), (80, 93), (98, 99),
    (41, 105), (64, 111), (104, 116),
)
EXTRA = ((0, 195), (4, 199), (656, 627))

Poly = tuple[F, F, F]  # c + a*t + b*t^2


def poly(c=0, a=0, b=0) -> Poly:
    return F(c), F(a), F(b)


def add(x: Poly, y: Poly) -> Poly:
    return tuple(a + b for a, b in zip(x, y))  # type: ignore[return-value]


def scale(a: F | int, x: Poly) -> Poly:
    return tuple(F(a) * b for b in x)  # type: ignore[return-value]


def sub(x: Poly, y: Poly) -> Poly:
    return add(x, scale(-1, y))


def mul(x: Poly, y: Poly) -> Poly:
    out = [F(0)] * 5
    for i, a in enumerate(x):
        for j, b in enumerate(y):
            out[i + j] += a * b
    assert out[3:] == [0, 0]
    return tuple(out[:3])  # type: ignore[return-value]


def coarse_cells() -> tuple[tuple[int, ...], ...]:
    cells = tuple((a, b, (a + dx) % Q0, (b + dy) % Q0)
                  for a, b in S0 for dx, dy in OFFSETS)
    assert len(cells) == len(set(cells)) == N0
    return cells


def fine_cells(coarse: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    # product() is lexicographic: the last bit changes fastest.  Thus the
    # exact integer decoder is id = 16*coarse_id + bit_code.
    cells = tuple(tuple(2 * digit + bit for digit, bit in zip(cell, bits))
                  for cell in coarse for bits in product((0, 1), repeat=4))
    assert len(cells) == len(set(cells)) == N
    for i, point in enumerate(cells):
        coarse_id, bit_code = divmod(i, 16)
        bits = tuple((bit_code >> shift) & 1 for shift in (3, 2, 1, 0))
        assert point == tuple(2 * coarse[coarse_id][j] + bits[j]
                              for j in range(4))
    return cells


def is_edge(a: tuple[int, ...], b: tuple[int, ...], q=Q) -> bool:
    return (a != b
            and all(y == x or y == (x - 1) % q for x, y in zip(a, b))
            and any(x == 0 and y == q - 1 for x, y in zip(a, b)))


def enumerate_edges(cells: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, int], ...]:
    decoder = {cell: i for i, cell in enumerate(cells)}
    edges = []
    # A strict dilation successor differs on a nonempty coordinate mask, so
    # only 15 candidates per vertex are needed; this is not an O(N^2) oracle.
    for ia, a in enumerate(cells):
        for mask in range(1, 16):
            b = tuple((x - 1) % Q if (mask >> j) & 1 else x
                      for j, x in enumerate(a))
            ib = decoder.get(b)
            if ib is not None and any(x == 0 and y == Q - 1
                                      for x, y in zip(a, b)):
                assert is_edge(a, b)
                edges.append((ia, ib))
    edges = sorted(edges)
    assert len(edges) == len(set(edges)) == 676
    # Orientation cannot be reversed because every edge contains 0 -> 11.
    assert all((b, a) not in set(edges) for a, b in edges)
    digest = hashlib.sha256(
        (json.dumps(edges, separators=(",", ":")) + "\n").encode("ascii")
    ).hexdigest()
    assert digest == EDGE_DIGEST
    return tuple(edges), digest


def digest_rows(rows) -> str:
    return hashlib.sha256(
        (json.dumps(rows, separators=(",", ":")) + "\n").encode("ascii")
    ).hexdigest()


def orient_coarse(coarse, u: int, v: int) -> tuple[int, int]:
    if is_edge(coarse[u], coarse[v], Q0):
        return u, v
    assert is_edge(coarse[v], coarse[u], Q0)
    return v, u


def claimed_matching(coarse, fine, edge_set) -> tuple[tuple[int, int], ...]:
    lifted = []
    for u, v in COARSE_MATCHING:
        a, b = orient_coarse(coarse, u, v)
        active = tuple(j for j, (x, y) in enumerate(zip(coarse[a], coarse[b]))
                       if x != y)
        inactive = tuple(j for j in range(4) if j not in active)
        # Active fine bits must be A=0, B=1.  On inactive coordinates choose
        # equal bits.  These 2^(4-|active|) edges match every participating
        # A-side vertex to a distinct B-side vertex.
        for free in product((0, 1), repeat=len(inactive)):
            abit = [0] * 4
            bbit = [1 if j in active else 0 for j in range(4)]
            for j, bit in zip(inactive, free):
                abit[j] = bbit[j] = bit
            ia = 16 * a + sum(bit << shift for bit, shift in zip(abit, (3, 2, 1, 0)))
            ib = 16 * b + sum(bit << shift for bit, shift in zip(bbit, (3, 2, 1, 0)))
            assert fine[ia] == tuple(2 * coarse[a][j] + abit[j] for j in range(4))
            assert fine[ib] == tuple(2 * coarse[b][j] + bbit[j] for j in range(4))
            assert (ia, ib) in edge_set
            lifted.append((ia, ib))
    assert len(lifted) == 106
    matching = lifted + list(EXTRA)
    assert all(edge in edge_set for edge in matching)
    flat = [v for edge in matching for v in edge]
    assert len(matching) == 109 and len(flat) == len(set(flat)) == 218
    assert digest_rows(matching) == CLAIMED_MATCHING_DIGEST
    assert all(sum(x == 0 and y == Q - 1 for x, y in zip(fine[a], fine[b])) == 1
               for a, b in matching)
    assert fine[0] == (6, 4, 6, 0) and fine[195] == (6, 4, 5, 11)
    assert fine[4] == (6, 5, 6, 0) and fine[199] == (6, 5, 5, 11)
    assert fine[656] == (8, 2, 10, 0) and fine[627] == (8, 2, 9, 11)
    assert N - len(matching) == 1763 < GATE
    return tuple(matching)


def independent_greedy(edges) -> tuple[tuple[int, int], ...]:
    # This reconstruction uses neither the public coarse matching nor EXTRA.
    used = set()
    matching = []
    for edge in sorted(edges):
        if edge[0] not in used and edge[1] not in used:
            matching.append(edge)
            used.update(edge)
    assert len(matching) == 148
    assert len(used) == 296
    assert N - len(matching) == 1724 < GATE
    assert digest_rows(matching) == GREEDY_MATCHING_DIGEST
    return tuple(matching)


def actual(digit: int, residual: Poly) -> Poly:
    return add(poly(F(digit, Q)), scale(F(1, Q), residual))


def defect(x: Poly, y: Poly, z: Poly) -> Poly:
    return sub(add(x, z), scale(2, y))


def correction(x: Poly, y: Poly, z: Poly) -> Poly:
    # q^2 times [(x-z)^2 - 2x^2 - 2z^2 + 4y^2].
    return scale(Q * Q,
                 add(mul(sub(x, z), sub(x, z)),
                     add(scale(-2, mul(x, x)),
                         add(scale(-2, mul(z, z)), scale(4, mul(y, y))))))


def scalar_rows() -> None:
    for a in range(Q):
        b = (a - 1) % Q
        at = actual(a, poly(0, 1))
        a3t = actual(a, poly(0, 3))
        b1t = actual(b, poly(1, -1))
        b13t = actual(b, poly(1, -3))
        wrap = a == 0
        r1 = poly(432, -48) if wrap else poly()
        r2 = poly(-144, -48) if wrap else poly()
        assert defect(at, b1t, b13t) == poly(-1 if wrap else 0)
        assert defect(a3t, at, b1t) == poly(1 if wrap else 0)
        assert correction(at, b1t, b13t) == r1
        assert correction(a3t, at, b1t) == r2
        # Reverse endpoint ownership swaps the order of the two rows.
        assert correction(b1t, at, a3t) == r2
        assert correction(b13t, b1t, at) == r1
    for t in (F(1, 100), F(1, 12), F(1, 4), F(99, 300)):
        assert 0 < t < F(1, 3)
        assert all(0 < x < 1 for x in (t, 3*t, 1-t, 1-3*t))


def point(cell, scale_t: int, side: int, active: tuple[int, ...]) -> tuple[Poly, ...]:
    ans = []
    for j, digit in enumerate(cell):
        if j not in active:
            residual = poly(F(1, 2))
        elif side == 0:
            residual = poly(0, scale_t)
        else:
            residual = poly(1, -scale_t)
        ans.append(actual(digit, residual))
    return tuple(ans)


def vec_correction(x, y, z) -> Poly:
    total = poly()
    for a, b, c in zip(x, y, z):
        d = defect(a, b, c)
        assert d[1:] == (0, 0) and d[0].denominator == 1
        total = add(total, correction(a, b, c))
    return total


def mixed_global_rows(fine, matching) -> None:
    # Use 17 independent blocks, alternating which physical word owns the
    # oriented A side.  This catches a silent one-orientation proof.
    chosen = matching[:17]
    row1 = poly()
    row2 = poly()
    wraps = 0
    for block, (ia, ib) in enumerate(chosen):
        a, b = fine[ia], fine[ib]
        active = tuple(j for j, (x, y) in enumerate(zip(a, b)) if x != y)
        k = sum(x == 0 and y == Q - 1 for x, y in zip(a, b))
        assert k >= 1
        wraps += k
        if block % 2 == 0:
            xt = point(a, 1, 0, active); x3 = point(a, 3, 0, active)
            yt = point(b, 1, 1, active); y3 = point(b, 3, 1, active)
            row1 = add(row1, vec_correction(xt, yt, y3))
            row2 = add(row2, vec_correction(x3, xt, yt))
        else:
            # The left accepted word is B and the right accepted word is A.
            xt = point(b, 1, 1, active); x3 = point(b, 3, 1, active)
            yt = point(a, 1, 0, active); y3 = point(a, 3, 0, active)
            row1 = add(row1, vec_correction(xt, yt, y3))
            row2 = add(row2, vec_correction(x3, xt, yt))
    assert add(row1, row2) == poly(288 * wraps, -96 * wraps)


def telescope() -> None:
    for k in (1, 2, 17, 103):
        for n in (1, 2, 7, 50):
            exact = k * (288*n - 12*(1 - F(1, 3**n)))
            direct = sum((k * (288 - F(24, 3**j))
                          for j in range(1, n + 1)), F(0))
            assert exact == direct
        for bound in (F(0), F(1), F(10**3), F(10**9)):
            n = int((4*bound + 12*k) // (288*k)) + 1
            assert k * (288*n - 12*(1 - F(1, 3**n))) > 4*bound


def physical_deduplication() -> None:
    # Two abstract paths may emit the same word.  Half-open q=12 boxes are
    # pairwise disjoint, so physical volume counts the decoded word once.
    paths = ((0, 1), (0, 1), (0, 2), (0, 1))
    language = set(paths)
    assert len(paths) == 4 and len(language) == 2
    assert F(len(language), Q**(4*2)) == F(2, Q**8)
    # A full horizon-m language has exact volume |L|/12^(4m).
    for m, count in ((1, 1724), (2, 1724**2), (3, 109)):
        assert F(count, Q**(4*m)) * Q**(4*m) == count


def planted_controls(fine, edges, claimed) -> None:
    edge_set = set(edges)
    a, b = claimed[0]
    assert (a, b) in edge_set
    # Remove the wrap: a pure ordinary predecessor is not a certified edge.
    ordinary_a = (6, 5, 6, 1)
    ordinary_b = (6, 5, 6, 0)
    assert all(y == x or y == x - 1 for x, y in zip(ordinary_a, ordinary_b))
    assert not any(x == 0 and y == Q - 1 for x, y in zip(ordinary_a, ordinary_b))
    assert not is_edge(ordinary_a, ordinary_b)
    # Duplicate one endpoint and ensure disjointness detects it.
    bad = list(claimed)
    bad[-1] = (bad[0][0], bad[-1][1])
    flat = [v for edge in bad for v in edge]
    assert len(flat) != len(set(flat))
    # The physical decoder is injective, not merely the abstract ID list.
    assert len(fine) == len(set(fine))


def main() -> None:
    coarse = coarse_cells()
    fine = fine_cells(coarse)
    edges, digest = enumerate_edges(fine)
    edge_set = set(edges)
    claimed = claimed_matching(coarse, fine, edge_set)
    greedy = independent_greedy(edges)
    greedy_wraps = tuple(sum(x == 0 and y == Q - 1
                             for x, y in zip(fine[a], fine[b]))
                         for a, b in greedy)
    assert greedy_wraps.count(1) == 147 and greedy_wraps.count(2) == 1
    assert all(k >= 1 for k in greedy_wraps)
    scalar_rows()
    mixed_global_rows(fine, claimed)
    mixed_global_rows(fine, greedy)
    telescope()
    physical_deduplication()
    planted_controls(fine, edges, claimed)
    assert F(1724, Q**4) < F(GATE, Q**4) == F(49, 576)
    print("PASS_INDEPENDENT_Q12_HALFCELL_WALL")
    print(f"PHYSICAL_DECODER_OK coarse={len(coarse)} halfcells={len(fine)}")
    print(f"DILATION_GRAPH_OK directed_edges={len(edges)} sha256={digest}")
    print("CLAIMED_MATCHING_OK lifted=106 extras=3 total=109 quotient=1763")
    print("STRONGER_GREEDY_MATCHING_OK total=148 quotient=1724<1764")
    print("GREEDY_WRAPS_OK one_wrap=147 two_wraps=1 zero_wraps=0")
    print("BOTH_ORIENTATIONS_OK scalar_and_mixed_global")
    print("FINITE_TELESCOPE_OK recurrence=K*(288-96t)")
    print("PHYSICAL_DEDUP_OK repeated_abstract_paths_count_once")
    print("SCOPE full_q12_microboxes_only; proper_submicrobox_carving_open")


if __name__ == "__main__":
    main()

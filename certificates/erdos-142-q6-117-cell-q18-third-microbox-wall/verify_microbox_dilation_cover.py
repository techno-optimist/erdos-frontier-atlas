#!/usr/bin/env python3
"""Exact q-adic microbox cover for all 66 componentwise dilation walls.

This is deliberately solver-free.  Every connected conflict component has at
most nine vertices for the tested subdivisions, so its minimum vertex cover is
proved by exhaustive enumeration.  A retained pair across a conflict edge
supports the full strict-interior dilation telescope for an arbitrary bounded
physical potential.
"""
from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction as F
import hashlib
from itertools import combinations, product
import json

Q = 6
S0 = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
      (5, 0), (5, 1), (5, 2))
OFFSETS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
           (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
CELLS = tuple((a, b, (a + x) % Q, (b + y) % Q)
              for a, b in S0 for x, y in OFFSETS)

Vertex = tuple[int, tuple[int, int, int, int]]
Edge = tuple[Vertex, Vertex]


def dilation_edges() -> tuple[tuple[int, int, tuple[int, ...], tuple[int, ...]], ...]:
    answer = []
    for ia, a in enumerate(CELLS):
        for ib, b in enumerate(CELLS):
            active = tuple(i for i, (x, y) in enumerate(zip(a, b)) if x != y)
            wraps = tuple(i for i in active if a[i] == 0 and b[i] == 5)
            if wraps and all(x == y or y == (x - 1) % Q
                             for x, y in zip(a, b)):
                answer.append((ia, ib, active, wraps))
    return tuple(answer)


def microbox_edges(r: int) -> tuple[Edge, ...]:
    edges: set[Edge] = set()
    for ia, ib, active, _ in dilation_edges():
        inactive = tuple(i for i in range(4) if i not in active)
        for values in product(range(r), repeat=len(inactive)):
            low = [0] * 4
            high = [r - 1] * 4
            for coordinate, value in zip(inactive, values):
                low[coordinate] = high[coordinate] = value
            x = (ia, tuple(low))
            y = (ib, tuple(high))
            edges.add(tuple(sorted((x, y))))  # type: ignore[arg-type]
    return tuple(sorted(edges))


def connected_components(edges: tuple[Edge, ...]) -> tuple[tuple[Vertex, ...], ...]:
    adjacency: dict[Vertex, set[Vertex]] = {}
    for x, y in edges:
        adjacency.setdefault(x, set()).add(y)
        adjacency.setdefault(y, set()).add(x)
    remaining = set(adjacency)
    components = []
    while remaining:
        start = min(remaining)
        queue = deque([start])
        found = {start}
        remaining.remove(start)
        while queue:
            x = queue.popleft()
            for y in adjacency[x]:
                if y in remaining:
                    remaining.remove(y)
                    found.add(y)
                    queue.append(y)
        components.append(tuple(sorted(found)))
    return tuple(sorted(components))


def exact_component_cover(component: tuple[Vertex, ...],
                          all_edges: tuple[Edge, ...]) -> tuple[Vertex, ...]:
    vertices = set(component)
    edges = tuple((x, y) for x, y in all_edges if x in vertices and y in vertices)
    for size in range(len(component) + 1):
        for chosen_tuple in combinations(component, size):
            chosen = set(chosen_tuple)
            if all(x in chosen or y in chosen for x, y in edges):
                # Exhaustion of every smaller subset is an exact lower-bound
                # proof; the first witness is the canonical minimum cover.
                return chosen_tuple
    raise AssertionError("a finite graph has no vertex cover")


def exact_cover(r: int) -> tuple[tuple[Vertex, ...], tuple[tuple[int, int, int], ...]]:
    edges = microbox_edges(r)
    cover: list[Vertex] = []
    signature = []
    for component in connected_components(edges):
        local = exact_component_cover(component, edges)
        vertex_set = set(component)
        local_edge_count = sum(x in vertex_set and y in vertex_set for x, y in edges)
        signature.append((len(component), local_edge_count, len(local)))
        cover.extend(local)
    assert all(x in cover or y in cover for x, y in edges)
    return tuple(sorted(cover)), tuple(sorted(signature))


def recurrence_semantics() -> None:
    """Check the exact scalar rows behind every graph edge."""
    edges = dilation_edges()
    assert len(CELLS) == len(set(CELLS)) == 117
    assert len(edges) == 66
    assert Counter(len(active) for _, _, active, _ in edges) == Counter(
        {1: 11, 2: 38, 3: 10, 4: 7})
    assert Counter(len(wraps) for _, _, _, wraps in edges) == Counter({1: 61, 2: 5})

    for ia, ib, active, wraps in edges:
        a, b = CELLS[ia], CELLS[ib]
        for j in range(4):
            if j not in active:
                assert a[j] == b[j]
                continue
            assert b[j] == (a[j] - 1) % Q
            # Digit-plus-residual midpoint numerators, before division by q.
            row_one_defect = a[j] + b[j] - 2 * b[j] - 1
            row_two_defect = a[j] + b[j] - 2 * a[j] + 1
            if j in wraps:
                assert (a[j], b[j]) == (0, 5)
                assert (row_one_defect, row_two_defect) == (-Q, Q)
            else:
                assert (row_one_defect, row_two_defect) == (0, 0)

        # Each wrap contributes (108-24t)+(-36-24t)=72-48t.
        for t in (F(1, 100), F(1, 12), F(1, 7)):
            assert 0 < t < F(1, 3)
            total = len(wraps) * ((108 - 24 * t) + (-36 - 24 * t))
            assert total == len(wraps) * (72 - 48 * t) > 0


def strict_microbox_telescope(r: int) -> None:
    """Verify that every graph edge carries an infinite strict-interior wall."""
    T = F(1, 2 * r)
    for N in (1, 2, 10, 100):
        levels = [T / 3**j for j in range(1, N + 1)]
        assert all(0 < t < 3 * t <= T < F(1, r) for t in levels)
        assert all(F(r - 1, r) < 1 - 3 * t < 1 - t < 1 for t in levels)
        summed = 72 * N - 24 * T * (1 - F(1, 3**N))
        direct = sum((72 - 48 * t for t in levels), F(0))
        assert summed == direct
        assert summed > 0
    # The right side grows linearly and hence beats the four-value bound 4M
    # for every finite bound M on h.
    for M in (0, 1, 10**3, 10**9):
        N = int((4 * M + 24 * T) // 72) + 1
        # Dropping the positive 24*T*3^-N term gives this exact lower bound.
        assert 72 * N - 24 * T > 4 * M


def digest(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def audit(r: int, expected_vertices: int, expected_edges: int,
          expected_components: int, expected_cover: int) -> tuple[Vertex, ...]:
    edges = microbox_edges(r)
    vertices = {x for edge in edges for x in edge}
    components = connected_components(edges)
    cover, signature = exact_cover(r)
    assert len(vertices) == expected_vertices
    assert len(edges) == expected_edges
    assert len(components) == expected_components
    assert max(map(len, components)) <= 9
    assert len(cover) == expected_cover
    assert all(x in cover or y in cover for x, y in edges)
    strict_microbox_telescope(r)
    total = 117 * r**4
    gate = F(49, 576) * (6 * r)**4
    retained = total - len(cover)
    print(f"R={r} GRAPH vertices={len(vertices)} edges={len(edges)} "
          f"components={len(components)} max_component={max(map(len, components))}")
    print(f"R={r} EXACT_MIN_COVER={len(cover)} retained={retained} "
          f"gate_count={gate} cover_digest={digest(cover)}")
    print(f"R={r} COMPONENT_SIGNATURE={Counter(signature)}")
    return cover


def main() -> None:
    recurrence_semantics()
    cover2 = audit(2, 327, 267, 93, 143)
    cover3 = audit(3, 983, 676, 352, 438)
    cover4 = audit(4, 2143, 1359, 843, 971)
    assert len(cover2) > F(27, 4) * 2**4
    assert len(cover3) < F(27, 4) * 3**4
    assert len(cover4) < F(27, 4) * 4**4

    # r=2 theorem: strict-above-gate means at most 107 deletions, but every
    # bounded pointwise candidate must delete at least 143 conflict vertices.
    total2 = 117 * 2**4
    gate2 = F(49, 576) * 12**4
    assert gate2 == 1764
    assert total2 - int(gate2) - 1 == 107
    assert total2 - len(cover2) == 1729 < gate2

    # r=3 survivor: this exact cover kills every displayed dilation edge and
    # still retains strictly more full microboxes than the EHPS gate.
    total3 = 117 * 3**4
    gate3 = F(49, 576) * 18**4
    assert gate3 == F(35721, 4)
    assert total3 - len(cover3) == 9039 > gate3
    assert F(total3 - len(cover3), 18**4) - F(49, 576) == F(145, 139968)

    print("PASS_MICROBOX_DILATION_COVER")
    print("HALF_GRID_WALL exact_min_deletions=143 budget=107 deficit_boxes=35")
    print("THIRD_GRID_DILATION_SURVIVOR retained=9039 gate=8930.25 "
          "density_margin=145/139968")
    print("SCOPE only_complete_aligned_microboxes_and_66_dilation_families")


if __name__ == "__main__":
    main()

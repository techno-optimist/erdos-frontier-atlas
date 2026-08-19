#!/usr/bin/env python3
"""Deterministically regenerate the normalized four-cap rank CNF.

The exact irredundant sequential counter is implemented below using only the
Python standard library. All geometry, blockers, counts, and bytes are checked.
"""

from __future__ import annotations

import argparse
from collections import deque
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
POINTS = tuple(product(range(9), repeat=2))
INDEX = {point: i for i, point in enumerate(POINTS)}
MID = tuple(tuple(INDEX[((5 * (POINTS[a][0] + POINTS[b][0])) % 9,
                         (5 * (POINTS[a][1] + POINTS[b][1])) % 9)]
                  for b in range(81)) for a in range(81))
LEVELS = 31
SATURATED = {(1, 0), (2, 0), (0, 1), (0, 2)}
EXPECTED = "3d490be403585b03ddc30b7aff7445b4c4e9d3b7550e2e97077964b627a88108"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


class IDPool:
    """The occupied-interval-free subset of python-sat's IDPool."""

    def __init__(self):
        self.top = 0
        self.ids = {}

    def id(self, key):
        if key not in self.ids:
            self.top += 1
            self.ids[key] = self.top
        return self.ids[key]


def encode_atmost(literals, bound, pool):
    """Knuth/Healy irredundant sequential counter used by python-sat."""
    literals = list(literals)
    if bound >= len(literals):
        return []
    if bound == len(literals) - 1:
        return [[-literal for literal in literals]]
    if bound == 0:
        return [[-literal] for literal in literals]
    need(0 < bound < len(literals) - 1, "atmost bound")
    auxiliary = {}

    def yvar(k, j):
        key = (k, j)
        if key not in auxiliary:
            pool.top += 1
            auxiliary[key] = pool.top
        return auxiliary[key]

    clauses = []
    for j in range(len(literals) - bound):
        s0j = yvar(0, j)
        clauses.append([-literals[j], s0j])
        for k in range(bound - 1):
            skj = yvar(k, j)
            if j < len(literals) - bound - 1:
                clauses.append([-skj, yvar(k, j + 1)])
            clauses.append([-literals[j + k + 1], -skj, yvar(k + 1, j)])
        stj = yvar(bound - 1, j)
        if j < len(literals) - bound - 1:
            clauses.append([-stj, yvar(bound - 1, j + 1)])
        clauses.append([-literals[j + bound], -stj])
    return clauses


def encode_atleast(literals, bound, pool):
    literals = list(literals)
    if bound <= 0:
        return []
    if bound == 1:
        return [literals]
    if bound == len(literals):
        return [[literal] for literal in literals]
    return encode_atmost([-literal for literal in literals],
                         len(literals) - bound, pool)


def encode_equals(literals, bound, pool):
    # python-sat CardEnc.equals emits AtLeast first, then AtMost.
    return (encode_atleast(literals, bound, pool) +
            encode_atmost(literals, bound, pool))


def midpoint_core(support):
    members = tuple(support)
    alive = set(members)
    incoming = {v: 0 for v in members}
    for a, b in combinations(members, 2):
        midpoint = MID[a][b]
        if midpoint in incoming:
            incoming[midpoint] += 1
    queue = deque(v for v in members if incoming[v] == 0)
    while queue:
        vertex = queue.popleft()
        if vertex not in alive:
            continue
        alive.remove(vertex)
        for other in tuple(alive):
            midpoint = MID[vertex][other]
            if midpoint in alive:
                incoming[midpoint] -= 1
                if incoming[midpoint] == 0:
                    queue.append(midpoint)
    return frozenset(alive)


def primitive_core6():
    subgroups = set()
    for vector in POINTS:
        subgroup = frozenset(((k * vector[0]) % 9,
                              (k * vector[1]) % 9) for k in range(9))
        if len(subgroup) == 9:
            subgroups.add(subgroup)
    need(len(subgroups) == 12, "primitive subgroup census")
    lines = set()
    for subgroup in subgroups:
        for translation in POINTS:
            lines.add(frozenset(((x + translation[0]) % 9,
                                 (y + translation[1]) % 9)
                                for x, y in subgroup))
    need(len(lines) == 108, "primitive line census")
    edges = set()
    for line in lines:
        groups = {}
        for point in line:
            groups.setdefault((point[0] % 3, point[1] % 3), []).append(point)
        need(len(groups) == 3 and set(map(len, groups.values())) == {3},
             "primitive line residue groups")
        grouped = tuple(tuple(sorted(INDEX[p] for p in group))
                        for _, group in sorted(groups.items()))
        for omitted in product(range(3), repeat=3):
            edges.add(tuple(sorted(vertex
                                   for at, group in enumerate(grouped)
                                   for j, vertex in enumerate(group)
                                   if j != omitted[at])))
    need(len(edges) == 2916, "minimal core6 census")
    for edge in edges:
        need(midpoint_core(edge) == frozenset(edge), "core6 self-core")
        need(all(not midpoint_core(v for v in edge if v != dropped)
                 for dropped in edge), "core6 deletion minimality")
    return tuple(sorted(edges))


def read_core5(path):
    need(path.is_file(), "missing minimal_core5.txt")
    rows = []
    for line_no, raw in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        row = tuple(map(int, raw.split()))
        need(len(row) == 5 and tuple(sorted(set(row))) == row and
             all(0 <= v < 81 for v in row), "malformed core5 line %d" % line_no)
        need(midpoint_core(row) == frozenset(row),
             "core5 line %d is not a self-core" % line_no)
        rows.append(row)
    need(len(rows) == len(set(rows)) == 3402, "minimal core5 census")
    return tuple(rows)


def build(core5_path):
    pool = IDPool()
    q = [[pool.id((v, t)) for t in range(LEVELS + 1)] for v in range(81)]
    selected = [q[v][LEVELS] for v in range(81)]
    clauses = []

    def card(literals, bound, kind="equals"):
        encoded = (encode_equals(literals, bound, pool) if kind == "equals"
                   else encode_atmost(literals, bound, pool))
        clauses.extend(encoded)

    # q[v,t] means that v has entered strictly before boundary t.
    for v in range(81):
        clauses.append((-q[v][0],))
        for t in range(LEVELS):
            clauses.append((-q[v][t], q[v][t + 1]))
    clauses.append(tuple(q[v][1] for v in range(81)))
    card(selected, 31)

    # Exactly one false-to-true transition at each of the 31 ranks.
    for t in range(LEVELS):
        transitions = []
        for v in range(81):
            transition = pool.id(("transition", v, t))
            transitions.append(transition)
            clauses.append((-transition, -q[v][t]))
            clauses.append((-transition, q[v][t + 1]))
            clauses.append((q[v][t], -q[v][t + 1], transition))
        card(transitions, 1)

    # If midpoint m enters at t, its two selected endpoints cannot both have
    # entered by t+1.  This is exactly the strict reverse-add constraint.
    for a, b in combinations(range(81), 2):
        midpoint = MID[a][b]
        for t in range(LEVELS):
            clauses.append((q[midpoint][t], -q[midpoint][t + 1],
                            -q[a][t + 1], -q[b][t + 1]))

    # Universal fibre cap, followed below by the exact four-cap profile.
    for rx, ry in product(range(3), repeat=2):
        card([selected[v] for v, (x, y) in enumerate(POINTS)
              if x % 3 == rx and y % 3 == ry], 4, "atmost")

    # Redundant but sound local order-three line blockers.
    local_lines = set()
    for a, b in combinations(range(81), 2):
        midpoint = MID[a][b]
        if (midpoint != a and midpoint != b and MID[a][midpoint] == b and
                MID[b][midpoint] == a):
            local_lines.add(tuple(sorted((a, b, midpoint))))
    need(len(local_lines) == 108, "local line census")
    for line in sorted(local_lines):
        clauses.append(tuple(-selected[v] for v in line))

    core5 = read_core5(core5_path)
    for edge in core5:
        clauses.append(tuple(-selected[v] for v in edge))

    for rx, ry in product(range(3), repeat=2):
        literals = [selected[v] for v, (x, y) in enumerate(POINTS)
                    if x % 3 == rx and y % 3 == ry]
        card(literals, 4 if (rx, ry) in SATURATED else 3)

    need(pool.top == 11203 and len(clauses) == 128765,
         "core5 CNF census")

    core6 = primitive_core6()
    for edge in core6:
        clauses.append(tuple(-selected[v] for v in edge))
    need(pool.top == 11203 and len(clauses) == 131681,
         "core6 CNF census")

    chunks = [b"p cnf 11203 131681\n"]
    chunks.extend((" ".join(map(str, clause)) + " 0\n").encode("ascii")
                  for clause in clauses)
    return b"".join(chunks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--core5", type=Path,
                        default=HERE / "minimal_core5.txt")
    parser.add_argument("--check", type=Path,
                        default=HERE / "case2_unique_core6.cnf")
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    output = build(args.core5)
    digest = sha256(output).hexdigest()
    need(len(output) == 2915646 and digest == EXPECTED,
         "regenerated base bytes")
    if args.check:
        need(args.check.read_bytes() == output, "frozen base byte mismatch")
    if args.write:
        args.write.write_bytes(output)
    print("PASS_CASE2_CORE6_CNF_REGEN")
    print("CNF vars=11203 clauses=131681 bytes=%d sha256=%s" %
          (len(output), digest))
    print("REDUNDANT_BLOCKERS core3=108 core5=3402 core6=2916")


if __name__ == "__main__":
    main()

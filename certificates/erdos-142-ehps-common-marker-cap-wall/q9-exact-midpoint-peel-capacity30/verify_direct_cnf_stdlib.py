#!/usr/bin/env python3
"""Byte-regenerate both direct slab CNFs with only the Python stdlib."""

from hashlib import sha256
from itertools import combinations, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
DIRECT = HERE / "certificates" / "direct_slab31" / "cnf"
POINTS = tuple(product(range(9), repeat=2))
INDEX = {point: i for i, point in enumerate(POINTS)}
MID = tuple(tuple(INDEX[((5*(POINTS[a][0]+POINTS[b][0])) % 9,
                         (5*(POINTS[a][1]+POINTS[b][1])) % 9)]
                  for b in range(81)) for a in range(81))
TEMPLATES = (
    ((0,3),(0,6),(1,3),(1,6),(2,0),(2,3),
     (3,0),(4,0),(4,3),(5,0),(5,3),(6,0)),
    ((0,0),(0,3),(1,0),(1,6),(2,3),(2,6),
     (3,3),(4,0),(4,3),(5,0),(5,3),(6,0)),
)
EXPECTED = (
    (2473044, "5f5b635ac07727751368bb766b91bacc9524f4c4818b95254e53bb62e03b0c15"),
    (2473043, "54f931b253189be9b921fb83c1c1bdefffe425c1f340ff73fd2dcda8e2a3d8e8"),
)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


class IDPool:
    """Occupied-interval-free part of python-sat's IDPool."""

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
    if bound == len(literals)-1:
        return [[-literal for literal in literals]]
    if bound == 0:
        return [[-literal] for literal in literals]
    need(0 < bound < len(literals)-1, "atmost bound")
    auxiliary = {}

    def yvar(k, j):
        key = (k, j)
        if key not in auxiliary:
            pool.top += 1
            auxiliary[key] = pool.top
        return auxiliary[key]

    clauses = []
    for j in range(len(literals)-bound):
        s0j = yvar(0, j)
        clauses.append([-literals[j], s0j])
        for k in range(bound-1):
            skj = yvar(k, j)
            if j < len(literals)-bound-1:
                clauses.append([-skj, yvar(k, j+1)])
            clauses.append([-literals[j+k+1], -skj, yvar(k+1, j)])
        stj = yvar(bound-1, j)
        if j < len(literals)-bound-1:
            clauses.append([-stj, yvar(bound-1, j+1)])
        clauses.append([-literals[j+bound], -stj])
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
                         len(literals)-bound, pool)


def encode_equals(literals, bound, pool):
    # python-sat CardEnc.equals emits AtLeast first and then AtMost.
    return (encode_atleast(literals, bound, pool)+
            encode_atmost(literals, bound, pool))


def build(case):
    pool = IDPool()
    q = [[pool.id((v, t)) for t in range(32)] for v in range(81)]
    selected = [q[v][31] for v in range(81)]
    clauses = []

    for v in range(81):
        clauses.append((-q[v][0],))
        for t in range(31):
            clauses.append((-q[v][t], q[v][t+1]))
    clauses.append(tuple(q[v][1] for v in range(81)))
    clauses.extend(encode_equals(selected, 31, pool))
    need(pool.top == 5692 and len(clauses) == 8793,
         "exact-size block census")

    for a, b in combinations(range(81), 2):
        midpoint = MID[a][b]
        for t in range(31):
            clauses.append((q[midpoint][t], -q[midpoint][t+1],
                            -q[a][t+1], -q[b][t+1]))
    need(len(clauses) == 109233, "midpoint block census")

    for rx, ry in product(range(3), repeat=2):
        literals = [selected[v] for v, (x, y) in enumerate(POINTS)
                    if x % 3 == rx and y % 3 == ry]
        clauses.extend(encode_atmost(literals, 4, pool))
    need(pool.top == 5872 and len(clauses) == 109602,
         "fibre-cap block census")

    for point in TEMPLATES[case]:
        clauses.append((selected[INDEX[point]],))
    need(len(clauses) == 109614, "template unit census")

    chunks = [b"p cnf 5872 109614\n"]
    chunks.extend((" ".join(map(str, clause))+" 0\n").encode("ascii")
                  for clause in clauses)
    return b"".join(chunks)


def main():
    source = Path(__file__).read_bytes()
    for case, (expected_bytes, expected_hash) in enumerate(EXPECTED):
        output = build(case)
        actual = DIRECT / ("case%d_direct_unary31.cnf" % case)
        need(len(output) == expected_bytes, "CNF byte census case%d" % case)
        need(sha256(output).hexdigest() == expected_hash,
             "CNF hash case%d" % case)
        need(actual.read_bytes() == output, "frozen CNF bytes case%d" % case)
        print("PASS_STDLIB_DIRECT_CNF_REGEN case=%d vars=5872 "
              "clauses=109614 bytes=%d sha256=%s" %
              (case, len(output), expected_hash))
    need(Path(__file__).read_bytes() == source, "source mutation")
    print("PASS_STDLIB_DIRECT_CNF_REGEN_ALL cases=2")


if __name__ == "__main__":
    main()

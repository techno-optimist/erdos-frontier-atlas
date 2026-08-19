#!/usr/bin/env python3
"""Independent deterministic replay of the two direct slab order CNFs."""

from __future__ import annotations

import argparse
from collections import deque
from itertools import combinations, product
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


PTS = tuple(product(range(9), repeat=2))
INDEX = {p:i for i,p in enumerate(PTS)}
MID = tuple(tuple(INDEX[((5*(PTS[a][0]+PTS[b][0])) % 9,
                         (5*(PTS[a][1]+PTS[b][1])) % 9)]
                  for b in range(81)) for a in range(81))
TEMPLATES = (
    ((0,3),(0,6),(1,3),(1,6),(2,0),(2,3),
     (3,0),(4,0),(4,3),(5,0),(5,3),(6,0)),
    ((0,0),(0,3),(1,0),(1,6),(2,3),(2,6),
     (3,3),(4,0),(4,3),(5,0),(5,3),(6,0)),
)


def need(c, m):
    if not c:
        raise AssertionError(m)


def peelable(vertices):
    alive = set(vertices)
    while alive:
        choice = next((m for m in sorted(alive)
                       if not any(MID[a][b] == m
                                  for a,b in combinations(sorted(alive),2))), None)
        if choice is None:
            return False
        alive.remove(choice)
    return True


def fibre_capacity_replay():
    fibre = [INDEX[(3*x,3*y)] for x,y in product(range(3), repeat=2)]
    best = 0
    count4 = 0
    for mask in range(1 << 9):
        chosen = [fibre[i] for i in range(9) if mask >> i & 1]
        if peelable(chosen):
            best = max(best,len(chosen))
            if len(chosen) == 4:
                count4 += 1
    need(best == 4 and count4 == 54, (best,count4))
    print("PASS_FIBRE_CAPACITY best=4 size4=54")


def expected(case):
    pool = IDPool()
    q = [[pool.id((v,t)) for t in range(32)] for v in range(81)]
    selected = [q[v][31] for v in range(81)]
    clauses = []

    def card(lits, bound, equality=False):
        enc = (CardEnc.equals if equality else CardEnc.atmost)(
            lits=lits, bound=bound, vpool=pool, encoding=EncType.seqcounter)
        clauses.extend(enc.clauses)

    for v in range(81):
        clauses.append((-q[v][0],))
        for t in range(31):
            clauses.append((-q[v][t],q[v][t+1]))
    clauses.append(tuple(q[v][1] for v in range(81)))
    card(selected,31,True)

    row_count = 0
    for a,b in combinations(range(81),2):
        m = MID[a][b]
        for t in range(31):
            clauses.append((q[m][t],-q[m][t+1],-q[a][t+1],-q[b][t+1]))
            row_count += 1
    need(row_count == 3240*31, row_count)

    for rx,ry in product(range(3),repeat=2):
        card([selected[v] for v,(x,y) in enumerate(PTS)
              if x%3==rx and y%3==ry],4)
    for p in TEMPLATES[case]:
        clauses.append((selected[INDEX[p]],))
    need(pool.top == 5872 and len(clauses) == 109614,
         (pool.top,len(clauses)))
    return pool.top,clauses


def cnf_bytes(nvars, clauses):
    text = f"p cnf {nvars} {len(clauses)}\n"
    text += "".join(" ".join(map(str,c))+" 0\n" for c in clauses)
    return text.encode("ascii")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case0", type=Path, default=Path("cnf/case0_direct_unary31.cnf"))
    ap.add_argument("--case1", type=Path, default=Path("cnf/case1_direct_unary31.cnf"))
    args = ap.parse_args()
    fibre_capacity_replay()
    for case,path in enumerate((args.case0,args.case1)):
        nvars,clauses = expected(case)
        actual = path.read_bytes()
        wanted = cnf_bytes(nvars,clauses)
        need(actual == wanted, f"CNF mismatch case {case}: {path}")
        print(f"PASS_DIRECT_CNF case={case} vars={nvars} clauses={len(clauses)} "
              f"ordered_rows={3240*31}")
    print("PASS_DIRECT_SLAB_CNF_REPLAY")


if __name__ == "__main__":
    main()

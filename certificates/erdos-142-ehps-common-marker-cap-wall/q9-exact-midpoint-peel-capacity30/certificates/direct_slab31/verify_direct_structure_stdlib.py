#!/usr/bin/env python3
"""Standard-library structural audit of the direct slab CNFs."""

from itertools import combinations, product
from pathlib import Path

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

def need(c,m):
    if not c:
        raise AssertionError(m)

def q(v,t):
    return 32*v+t+1

def peelable(vertices):
    alive=set(vertices)
    while alive:
        m=next((m for m in sorted(alive)
                if not any(MID[a][b] == m for a,b in combinations(sorted(alive),2))),None)
        if m is None:
            return False
        alive.remove(m)
    return True

def read_cnf(path):
    clauses=[]
    nvars=nclauses=None
    for raw in path.read_text(encoding="ascii").splitlines():
        if not raw or raw.startswith("c"):
            continue
        if raw.startswith("p "):
            _,kind,vs,cs=raw.split()
            need(kind == "cnf", "header kind")
            nvars,nclauses=int(vs),int(cs)
            continue
        row=tuple(map(int,raw.split()))
        need(row and row[-1] == 0, "clause terminator")
        clauses.append(row[:-1])
    need((nvars,nclauses,len(clauses)) == (5872,109614,109614), "header census")
    need(max(abs(x) for c in clauses for x in c) == 5872, "variable census")
    return clauses

def audit(case,path):
    c=read_cnf(path)
    base=[]
    for v in range(81):
        base.append((-q(v,0),))
        for t in range(31):
            base.append((-q(v,t),q(v,t+1)))
    base.append(tuple(q(v,1) for v in range(81)))
    need(c[:2593] == base, "base rank clauses")

    exact=c[2593:8793]
    need(len(exact) == 6200, "exact counter clauses")
    selected={q(v,31) for v in range(81)}
    need(all(abs(x) in selected or 2593 <= abs(x) <= 5692
             for row in exact for x in row), "exact counter variable scope")
    need(set(abs(x) for row in exact for x in row if abs(x) <= 2592) == selected,
         "exact counter inputs")

    rows=[]
    for a,b in combinations(range(81),2):
        m=MID[a][b]
        for t in range(31):
            rows.append((q(m,t),-q(m,t+1),-q(a,t+1),-q(b,t+1)))
    need(len(rows) == 100440 and c[8793:109233] == rows, "all midpoint rows")

    fibre=c[109233:109602]
    need(len(fibre) == 9*41, "fibre counter census")
    for i,(rx,ry) in enumerate(product(range(3),repeat=2)):
        block=fibre[41*i:41*(i+1)]
        inputs={q(v,31) for v,(x,y) in enumerate(PTS) if x%3==rx and y%3==ry}
        auxlo,auxhi=5693+20*i,5692+20*(i+1)
        need(all(abs(x) in inputs or auxlo <= abs(x) <= auxhi
                 for row in block for x in row), f"fibre {rx,ry} scope")
        need(set(abs(x) for row in block for x in row if abs(x) <= 2592) == inputs,
             f"fibre {rx,ry} inputs")

    units=tuple((q(INDEX[p],31),) for p in TEMPLATES[case])
    need(tuple(c[109602:]) == units, "template units")
    print(f"PASS_STDLIB_DIRECT_CNF case={case} vars=5872 clauses=109614 "
          "symmetric_rows=100440 ordered_endpoint_directions=200880")

def main():
    fibre=[INDEX[(3*x,3*y)] for x,y in product(range(3),repeat=2)]
    good=[mask for mask in range(512)
          if peelable([fibre[i] for i in range(9) if mask>>i&1])]
    need(max(mask.bit_count() for mask in good) == 4, "fibre capacity")
    need(sum(mask.bit_count() == 4 for mask in good) == 54, "four-cap census")
    print("PASS_STDLIB_FIBRE_CAPACITY best=4 size4=54")
    audit(0,Path("cnf/case0_direct_unary31.cnf"))
    audit(1,Path("cnf/case1_direct_unary31.cnf"))
    print("PASS_STDLIB_DIRECT_SLAB_STRUCTURE")

if __name__ == "__main__":
    main()

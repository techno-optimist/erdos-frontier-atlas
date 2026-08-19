#!/usr/bin/env python3
"""Independent semantic and affine-orbit replay of minimal_core6.txt."""

from collections import deque
from itertools import combinations, product
from pathlib import Path

PTS=tuple(product(range(9),repeat=2))
INDEX={p:i for i,p in enumerate(PTS)}
MID=tuple(tuple(INDEX[((5*(PTS[a][0]+PTS[b][0]))%9,
                       (5*(PTS[a][1]+PTS[b][1]))%9)]
                for b in range(81)) for a in range(81))


def core(vertices):
    members=tuple(vertices)
    alive=set(members)
    incoming={v:0 for v in members}
    for a,b in combinations(members,2):
        m=MID[a][b]
        if m in incoming:
            incoming[m]+=1
    queue=deque(v for v in members if incoming[v]==0)
    while queue:
        v=queue.popleft()
        if v not in alive:
            continue
        alive.remove(v)
        for u in tuple(alive):
            m=MID[u][v]
            if m in alive:
                incoming[m]-=1
                if incoming[m]==0:
                    queue.append(m)
    return tuple(sorted(alive))


def main():
    path=Path(__file__).with_name("minimal_core6.txt")
    rows=[]
    for raw in path.read_text(encoding="ascii").splitlines():
        row=tuple(map(int,raw.split()))
        assert len(row)==6 and tuple(sorted(set(row)))==row
        rows.append(row)
    assert len(rows)==len(set(rows))==2916
    for row in rows:
        assert core(row)==row
        for v in row:
            assert not core(x for x in row if x!=v)

    rep=rows[0]
    orbit=set()
    matrices=0
    for a,b,c,d in product(range(9),repeat=4):
        if (a*d-b*c)%3==0:
            continue
        matrices+=1
        for tx,ty in product(range(9),repeat=2):
            orbit.add(tuple(sorted(INDEX[((a*PTS[v][0]+b*PTS[v][1]+tx)%9,
                                          (c*PTS[v][0]+d*PTS[v][1]+ty)%9)]
                                   for v in rep)))
    assert matrices==3888
    assert orbit==set(rows)
    print("PASS_CORE6_SEMANTICS rows=2916 all_deletions_peelable=true")
    print("PASS_CORE6_SINGLE_AFFINE_ORBIT matrices=3888 affine_maps=314928 orbit=2916")


if __name__=="__main__":
    main()

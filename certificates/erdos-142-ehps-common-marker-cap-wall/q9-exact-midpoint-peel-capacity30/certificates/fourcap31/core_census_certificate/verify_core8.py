#!/usr/bin/env python3
"""Independent semantic replay and affine-orbit census for core8 ledger."""

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


def affine_orbit(rep):
    result=set()
    matrices=0
    for a,b,c,d in product(range(9),repeat=4):
        if (a*d-b*c)%3==0:
            continue
        matrices+=1
        linear=tuple(((a*PTS[v][0]+b*PTS[v][1])%9,
                      (c*PTS[v][0]+d*PTS[v][1])%9) for v in rep)
        for tx,ty in product(range(9),repeat=2):
            result.add(tuple(sorted(INDEX[((x+tx)%9,(y+ty)%9)]
                                    for x,y in linear)))
    assert matrices==3888
    return result


def main():
    path=Path(__file__).with_name("minimal_core8.txt")
    rows=[]
    for raw in path.read_text(encoding="ascii").splitlines():
        row=tuple(map(int,raw.split()))
        assert len(row)==8 and tuple(sorted(set(row)))==row
        rows.append(row)
    ledger=set(rows)
    assert len(rows)==len(ledger)==17496
    deletion_checks=0
    for row in rows:
        assert core(row)==row
        for v in row:
            assert not core(x for x in row if x!=v)
            deletion_checks+=1
    print(f"PASS_CORE8_SEMANTICS rows={len(rows)} deletion_checks={deletion_checks}",flush=True)

    unseen=set(ledger)
    records=[]
    while unseen:
        rep=min(unseen)
        orbit=affine_orbit(rep)
        assert orbit<=ledger
        records.append((rep,len(orbit)))
        unseen-=orbit
        print("ORBIT",len(records)-1,"SIZE",len(orbit),"REP"," ".join(map(str,rep)),flush=True)
    assert sum(size for _,size in records)==len(ledger)
    print("PASS_CORE8_AFFINE_PARTITION",
          f"orbits={len(records)} sizes={tuple(size for _,size in records)}")


if __name__=="__main__":
    main()

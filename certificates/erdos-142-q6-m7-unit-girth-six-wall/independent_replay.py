#!/usr/bin/env python3
"""Separately written direct replay of the q=6/M7 girth-six wall."""

from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path


ROOT=Path(__file__).resolve().parent
Q=6
S0={(3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2)}
S1={(5-x,y) for x,y in S0}
EXPECTED_COUNTS={2:3,3:21,4:282,5:6210}
EXPECTED_POSITIVE={2:0,3:1,4:40,5:1470}
TDIG="bf2f1d9ef4b5a5ad400a4c5f43a5a694c3fb0002a1c24323c9b70258a1c24075"
WDIG="01dc21dddf141769893a25d33a5e9646e8e8139ee8bdb1b2994353481e71462c"


def selector():
    cells=[]
    for line in (ROOT/"selector.cells").read_text(encoding="ascii").splitlines():
        if line.strip():
            cells.append(tuple(map(int,line.split(":"))))
    assert len(cells)==len(set(cells))==28
    return tuple(cells)


def support_bit(point):
    flags=(point in S0,point in S1)
    assert sum(flags)==1
    return 0 if flags[0] else 1


def point_cell(vertex):
    word=0; residue=0
    for j,(x,y) in enumerate(vertex):
        word|=support_bit((x,y))<<j
        residue+=(x+y)&1
    return word,residue


def selector_mass(cells):
    total=0
    parity_counts=[]
    for support in (S0,S1):
        parity_counts.append((sum((x+y)%2==0 for x,y in support),sum((x+y)%2==1 for x,y in support)))
    assert parity_counts==[(3,6),(6,3)]
    for word,residue in cells:
        poly=[1]
        for j in range(6):
            even,odd=parity_counts[(word>>j)&1]
            new=[0]*(len(poly)+1)
            for r,n in enumerate(poly):
                new[r]+=n*even; new[r+1]+=n*odd
            poly=new
        total+=poly[residue]
    assert total==1_405_512
    mass=Fraction(total,6**12)
    assert mass==Fraction(241,373248) and mass-Fraction(7,24)**6==Fraction(5743,191102976)>0
    return total,mass


def no_order3_orbit(cells):
    # Direct local-channel DP; no use of the primary replay's closed formula.
    channels={bits:set() for bits in itertools.product((0,1),repeat=3)}
    for dx,dy in itertools.product((0,2,4),repeat=2):
        for p in S0|S1:
            orbit=tuple(((p[0]+t*dx)%6,(p[1]+t*dy)%6) for t in range(3))
            if all(x in S0 or x in S1 for x in orbit):
                channels[tuple(support_bit(x) for x in orbit)].add((((p[0]+p[1])&1),(dx,dy)!=(0,0)))
    assert sum(len(v) for v in channels.values())==10
    by_r={r:[] for r in range(7)}
    for w,r in cells:
        by_r[r].append(w)
    checked=0
    for r,words in by_r.items():
        for wa,wb,wc in itertools.product(words,repeat=3):
            states={(0,False)}
            for j in range(6):
                bits=((wa>>j)&1,(wb>>j)&1,(wc>>j)&1)
                states={(s+p,nz or active) for s,active in states for p,nz in channels[bits]}
            assert (r,True) not in states
            checked+=1
    assert checked==1102
    return checked


def wall_replay(cells):
    data=json.loads((ROOT/"witness.json").read_text(encoding="utf-8"))
    vertices=tuple(tuple(tuple(map(int,p)) for p in v) for v in data["vertices"])
    assert len(vertices)==len(set(vertices))==6
    got_cells=tuple(point_cell(v) for v in vertices)
    assert got_cells==((49,0),(21,0),(45,0),(35,0),(7,0),(45,0))
    assert set(got_cells)<=set(cells)
    balance={v:0 for v in vertices}
    costs=[]
    carry_digest=[]
    for record in data["rows"]:
        a,b=map(int,record["endpoints"]); c=int(record["center"])
        left,right,center=vertices[a],vertices[b],vertices[c]
        carries=[]
        for x,z,y in zip(left,right,center):
            delta=(x[0]+z[0]-2*y[0],x[1]+z[1]-2*y[1])
            assert delta[0]%6==delta[1]%6==0
            carries.append((delta[0]//6,delta[1]//6))
        assert carries==[tuple(map(int,p)) for p in record["carry"]]
        cost=sum((x[d]-z[d])**2 for x,z in zip(left,right) for d in (0,1))
        assert cost==int(record["raw_rhs"])>0
        balance[left]+=1; balance[right]+=1; balance[center]-=2
        costs.append(cost); carry_digest.extend(carries)
    assert all(value==0 for value in balance.values())
    assert costs==[68,56,32,32,56,68] and sum(costs)==312
    assert Fraction(sum(costs),36)==Fraction(26,3)
    assert all(any(pair!=(0,0) for pair in carry_digest[6*i:6*i+6]) for i in range(6))

    # Independent symbolic common-offset check at delta=1/18.
    delta=Fraction(1,18)
    lifted=tuple(tuple(tuple(Fraction(d,6)+delta for d in p) for p in v) for v in vertices)
    for original,new in zip(vertices,lifted):
        for p,np in zip(original,new):
            assert all(Fraction(d,6)<x<Fraction(d+1,6) for d,x in zip(p,np))
    for record in data["rows"]:
        a,b=map(int,record["endpoints"]); c=int(record["center"])
        for j,(x,z,y) in enumerate(zip(lifted[a],lifted[b],lifted[c])):
            k=tuple(Fraction(v,1) for v in record["carry"][j])
            assert tuple(x[d]+z[d]-2*y[d] for d in (0,1))==k
    return costs


def edge_product_templates(k):
    edges=tuple((a,b) for a in range(k) for b in range(a,k))
    for rows in itertools.product(edges,repeat=k):
        degrees=[0]*k
        for a,b in rows:
            degrees[a]+=1; degrees[b]+=1
        if degrees==[2]*k:
            yield rows


def scalar_solutions(k,rows):
    for x in itertools.product(range(6),repeat=k):
        if all((x[a]+x[b]-2*x[c])%6==0 for c,(a,b) in enumerate(rows)):
            yield x


def row_text(rows):
    return ",".join(f"{a}{b}" for a,b in rows)


def digest(lines):
    return hashlib.sha256(("\n".join(lines)+"\n").encode("ascii")).hexdigest()


def girth_lower_replay():
    counts={}; positive_counts={}; all_lines=[]; witness_lines=[]
    for k in range(2,6):
        count=0; positive_count=0
        for rows in edge_product_templates(k):
            count+=1
            all_lines.append(f"{k}:{row_text(rows)}")
            solutions=list(scalar_solutions(k,rows))
            positive=[x for x in solutions if any(x[a]!=x[b] for a,b in rows)]
            if not positive:
                continue
            positive_count+=1
            found=None
            for triple in itertools.combinations(range(k),3):
                def kind(x):
                    values={x[i] for i in triple}
                    return 0 if len(values)==1 else (1 if len(values)==3 and len({v&1 for v in values})==1 else -1)
                if all(kind(x)>=0 for x in solutions) and all(kind(x)==1 for x in positive):
                    found=triple; break
            assert found is not None
            witness_lines.append(f"{k}:{row_text(rows)}:{''.join(map(str,found))}")
        counts[k]=count; positive_counts[k]=positive_count
    assert counts==EXPECTED_COUNTS and positive_counts==EXPECTED_POSITIVE
    assert digest(all_lines)==TDIG and digest(witness_lines)==WDIG
    return counts,positive_counts


def main():
    cells=selector()
    boxes,mass=selector_mass(cells)
    checked=no_order3_orbit(cells)
    costs=wall_replay(cells)
    counts,positive=girth_lower_replay()
    print("PASS_INDEPENDENT_Q6_M7_UNIT_GIRTH_SIX_WALL")
    print(json.dumps({"mass_boxes":boxes,"mass":str(mass),"order3_triples_checked":checked,
                      "row_costs":costs,"normalized_contradiction":"0 >= 26/3",
                      "template_counts":counts,"positive_template_counts":positive,
                      "unit_girth_rows":6,"ordinary_euclidean_claim":False,
                      "erdos142_solved":False,"new_r3_bound":False},sort_keys=True))


if __name__=="__main__":
    main()

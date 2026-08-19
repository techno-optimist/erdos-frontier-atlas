#!/usr/bin/env python3
"""Exact replay of the q=6/M7 unit-girth-six physical Farkas wall."""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
Q = 6
BASE = frozenset({(3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2)})
REFLECTED = frozenset((5-x,y) for x,y in BASE)
SUPPORTS = (BASE,REFLECTED)
EXPECTED_SELECTOR = (
    (7,0),(11,0),(21,0),(25,0),(35,0),(45,0),(49,0),(62,0),
    (27,1),(45,1),(54,1),(7,2),(56,2),(30,3),(33,3),
    (21,4),(42,4),(9,5),(20,5),(34,5),
    (4,6),(19,6),(25,6),(26,6),(35,6),(41,6),(42,6),(48,6),
)
EXPECTED_TEMPLATE_COUNTS = {2:3,3:21,4:282,5:6210}
EXPECTED_POSITIVE_COUNTS = {2:0,3:1,4:40,5:1470}
EXPECTED_TEMPLATE_DIGEST = "bf2f1d9ef4b5a5ad400a4c5f43a5a694c3fb0002a1c24323c9b70258a1c24075"
EXPECTED_WITNESS_DIGEST = "01dc21dddf141769893a25d33a5e9646e8e8139ee8bdb1b2994353481e71462c"


def parity(point):
    return (point[0]+point[1])&1


def orientation(point):
    if point in BASE:
        return 0
    if point in REFLECTED:
        return 1
    raise AssertionError("point outside both local supports")


def translate(point,step,times):
    return ((point[0]+times*step[0])%Q,(point[1]+times*step[1])%Q)


def local_order3_table():
    table={bits:set() for bits in itertools.product((0,1),repeat=3)}
    rows=0
    for step in itertools.product((0,2,4),repeat=2):
        for start in BASE|REFLECTED:
            triple=tuple(translate(start,step,k) for k in range(3))
            if not all(p in BASE or p in REFLECTED for p in triple):
                continue
            table[tuple(orientation(p) for p in triple)].add((parity(start),step!=(0,0)))
            rows+=1
    assert rows==42
    assert table[(0,0,0)]==table[(1,1,1)]=={(0,False),(1,False)}
    for bits in itertools.product((0,1),repeat=3):
        if len(set(bits))==1:
            continue
        assert table[bits]=={(1 if sum(bits)==1 else 0,True)}
    return table


def order3_criterion(a,b,c,residue):
    columns=[((a>>i)&1,(b>>i)&1,(c>>i)&1) for i in range(6)]
    changing=[column for column in columns if len(set(column))>1]
    v=len(changing)
    t=sum(sum(column)==1 for column in changing)
    return v>0 and t<=residue<=t+6-v


def direct_order3_exists(a,b,c,residue,table):
    states={(0,False)}
    for i in range(6):
        bits=((a>>i)&1,(b>>i)&1,(c>>i)&1)
        states={(total+p,active or nonzero) for total,active in states for p,nonzero in table[bits]}
    return (residue,True) in states


def cell_mass(word,residue):
    poly=[1]
    for i in range(6):
        support=SUPPORTS[(word>>i)&1]
        even=sum(parity(p)==0 for p in support)
        odd=sum(parity(p)==1 for p in support)
        nxt=[0]*(len(poly)+1)
        for j,value in enumerate(poly):
            nxt[j]+=even*value
            nxt[j+1]+=odd*value
        poly=nxt
    return poly[residue]


def parse_selector():
    cells=tuple(tuple(map(int,line.split(":"))) for line in
                (HERE/"selector.cells").read_text(encoding="ascii").splitlines() if line.strip())
    assert cells==EXPECTED_SELECTOR and len(set(cells))==28
    return cells


def selector_audit(cells=EXPECTED_SELECTOR,expected_edges=0):
    assert BASE.isdisjoint(REFLECTED) and len(BASE)==len(REFLECTED)==9
    assert tuple((sum(parity(p)==0 for p in s),sum(parity(p)==1 for p in s)) for s in SUPPORTS)==((3,6),(6,3))
    table=local_order3_table()
    by_residue={r:tuple(w for w,rr in cells if rr==r) for r in range(7)}
    checked=0
    edges=[]
    for residue,words in by_residue.items():
        for a,b,c in itertools.product(words,repeat=3):
            closed=order3_criterion(a,b,c,residue)
            direct=direct_order3_exists(a,b,c,residue,table)
            assert closed==direct
            checked+=1
            if direct:
                edges.append((a,b,c,residue))
    assert len(edges)==expected_edges
    total=sum(cell_mass(w,r) for w,r in cells)
    assert total==1_405_512
    mass=Fraction(total,Q**12)
    gate=Fraction(7,24)**6
    assert mass==Fraction(241,373248)
    assert mass-gate==Fraction(5743,191102976)>0
    return {"cells":len(cells),"ordered_word_triples":checked,"order3_edges":len(edges),
            "mass_boxes":total,"mass":str(mass),"gate_excess":str(mass-gate)}


def physical_cell(vertex):
    word=sum(orientation(point)<<i for i,point in enumerate(vertex))
    return (word,sum(parity(point) for point in vertex))


def midpoint_carry(left,right,center):
    out=[]
    for x,z,y in zip(left,right,center):
        delta=(x[0]+z[0]-2*y[0],x[1]+z[1]-2*y[1])
        assert delta[0]%Q==delta[1]%Q==0
        out.append((delta[0]//Q,delta[1]//Q))
    return tuple(out)


def raw_cost(left,right):
    return sum((x[d]-z[d])**2 for x,z in zip(left,right) for d in range(2))


def load_packet():
    return json.loads((HERE/"witness.json").read_text(encoding="utf-8"))


def wall_audit(packet,selector=EXPECTED_SELECTOR):
    assert int(packet["q"])==Q
    vertices=tuple(tuple(tuple(map(int,p)) for p in vertex) for vertex in packet["vertices"])
    assert len(vertices)==6 and len(set(vertices))==6 and all(len(v)==6 for v in vertices)
    cells=tuple(physical_cell(v) for v in vertices)
    assert cells==tuple(map(tuple,packet["expected_cells"]))
    assert all(cell in set(selector) for cell in cells)

    coefficients=[0]*6
    costs=[]
    carries=[]
    for row in packet["rows"]:
        a,b=map(int,row["endpoints"])
        c=int(row["center"])
        assert len({a,b,c})==3
        actual_carry=midpoint_carry(vertices[a],vertices[b],vertices[c])
        declared_carry=tuple(tuple(map(int,p)) for p in row["carry"])
        assert actual_carry==declared_carry
        actual_cost=raw_cost(vertices[a],vertices[b])
        assert actual_cost==int(row["raw_rhs"]) and actual_cost>0
        coefficients[a]+=1; coefficients[b]+=1; coefficients[c]-=2
        costs.append(actual_cost); carries.append(actual_carry)
    assert coefficients==[0]*6
    total=sum(costs)
    assert costs==[68,56,32,32,56,68]
    assert total==int(packet["expected_raw_total"])==312
    assert Fraction(total,Q*Q)==Fraction(packet["expected_normalized_total"])==Fraction(26,3)>0
    assert all(any(pair!=(0,0) for pair in carry) for carry in carries)

    # Strict common-offset lift: digit/q + delta stays in the same open box;
    # delta cancels from every midpoint row and endpoint difference.
    delta=Fraction(1,12)
    lifted=tuple(tuple(tuple(Fraction(d,Q)+delta for d in p) for p in v) for v in vertices)
    for v,lv in zip(vertices,lifted):
        for p,lp in zip(v,lv):
            for d,x in zip(p,lp):
                assert Fraction(d,Q)<x<Fraction(d+1,Q)
    for row,declared in zip(packet["rows"],carries):
        a,b=map(int,row["endpoints"]); c=int(row["center"])
        for x,z,y,kappa in zip(lifted[a],lifted[b],lifted[c],declared):
            assert tuple(x[d]+z[d]-2*y[d] for d in range(2))==tuple(Fraction(k,1) for k in kappa)
        assert sum((x[d]-z[d])**2 for x,z in zip(lifted[a],lifted[b]) for d in range(2))==Fraction(int(row["raw_rhs"]),Q*Q)
    return {"physical_vertices":6,"cells":[list(c) for c in cells],"rows":6,
            "row_costs":costs,"coefficient_vector":coefficients,"raw_contradiction":f"0 >= {total}",
            "normalized_contradiction":f"0 >= {Fraction(total,Q*Q)}",
            "open_offset_domain":"delta in (0,1/6)^12"}


def generate_templates(k):
    remaining=[2]*k
    rows=[]
    def visit(row):
        if row==k:
            if not any(remaining):
                yield tuple(rows)
            return
        for a in range(k):
            if remaining[a]==0:
                continue
            remaining[a]-=1
            for b in range(a,k):
                if remaining[b]==0:
                    continue
                remaining[b]-=1; rows.append((a,b))
                yield from visit(row+1)
                rows.pop(); remaining[b]+=1
            remaining[a]+=1
    yield from visit(0)


def hash_lines(lines):
    return hashlib.sha256(("\n".join(lines)+"\n").encode("ascii")).hexdigest()


def row_text(rows):
    return ",".join(f"{a}{b}" for a,b in rows)


def build_masks(k,equation_shift=0):
    assignments=tuple(itertools.product(range(Q),repeat=k))
    pairs=tuple((a,b) for a in range(k) for b in range(a,k))
    row_ok=[[0 for _ in pairs] for _ in range(k)]
    different=[[0 for _ in range(k)] for _ in range(k)]
    triples=tuple(itertools.combinations(range(k),3))
    triple_good={triple:0 for triple in triples}
    triple_orbit={triple:0 for triple in triples}
    for bit,x in enumerate(assignments):
        flag=1<<bit
        for center in range(k):
            for pi,(a,b) in enumerate(pairs):
                if (x[a]+x[b]-2*x[center]-equation_shift)%Q==0:
                    row_ok[center][pi]|=flag
        for a in range(k):
            for b in range(k):
                if x[a]!=x[b]:
                    different[a][b]|=flag
        for triple in triples:
            values={x[label] for label in triple}
            constant=len(values)==1
            orbit=len(values)==3 and len({value%2 for value in values})==1
            if constant or orbit:
                triple_good[triple]|=flag
            if orbit:
                triple_orbit[triple]|=flag
    return pairs,row_ok,different,triples,triple_good,triple_orbit


def unit_girth_lower_audit(equation_shift=0,expected_positive=EXPECTED_POSITIVE_COUNTS):
    template_counts={}; positive_counts={}; template_lines=[]; witness_lines=[]
    for k in range(2,6):
        pairs,row_ok,different,triples,triple_good,triple_orbit=build_masks(k,equation_shift)
        pair_index={pair:i for i,pair in enumerate(pairs)}
        templates=tuple(generate_templates(k))
        template_counts[k]=len(templates)
        positive_count=0
        for rows in templates:
            kernel=-1
            for center,pair in enumerate(rows):
                kernel&=row_ok[center][pair_index[pair]]
            template_lines.append(f"{k}:{row_text(rows)}")
            endpoint_different=0
            for a,b in rows:
                endpoint_different|=different[a][b]
            positive_kernel=kernel&endpoint_different
            if not positive_kernel:
                continue
            positive_count+=1
            witness=None
            for triple in triples:
                if kernel&~triple_good[triple]:
                    continue
                if positive_kernel&~triple_orbit[triple]:
                    continue
                witness=triple; break
            assert witness is not None
            witness_lines.append(f"{k}:{row_text(rows)}:{''.join(map(str,witness))}")
        positive_counts[k]=positive_count
    assert template_counts==EXPECTED_TEMPLATE_COUNTS
    assert positive_counts==expected_positive
    td=hash_lines(template_lines); wd=hash_lines(witness_lines)
    if equation_shift==0:
        assert td==EXPECTED_TEMPLATE_DIGEST and wd==EXPECTED_WITNESS_DIGEST
    return {"template_counts":template_counts,"positive_template_counts":positive_counts,
            "template_digest":td,"fixed_witness_digest":wd,
            "positive_templates_total":sum(positive_counts.values())}


def check_hashes():
    constants=json.loads((HERE/"constants.json").read_text(encoding="utf-8"))
    assert constants["scope"]=={"erdos142_solved":False,"new_r3_bound":False,
                                "ordinary_euclidean_claim":False,"unit_girth_rows":6}
    for name,expected in constants["sha256"].items():
        actual=hashlib.sha256((HERE/name).read_bytes()).hexdigest().upper()
        assert actual==expected,(name,actual,expected)


def expect_rejected(label,action):
    try:
        action()
    except AssertionError:
        return label
    raise AssertionError("planted corruption accepted: "+label)


def self_test(packet):
    failures=[]
    bad=copy.deepcopy(packet); bad["vertices"][0][0]=[3,2]
    failures.append(expect_rejected("physical-vertex",lambda:wall_audit(bad)))
    bad=copy.deepcopy(packet); bad["rows"][0]["carry"][2]=[0,1]
    failures.append(expect_rejected("carry",lambda:wall_audit(bad)))
    bad=copy.deepcopy(packet); bad["rows"][3]["raw_rhs"]=31
    failures.append(expect_rejected("raw-rhs",lambda:wall_audit(bad)))
    bad=copy.deepcopy(packet); bad["rows"][5]["center"]=4
    failures.append(expect_rejected("physical-cancellation",lambda:wall_audit(bad)))
    planted=((0,0),)+EXPECTED_SELECTOR
    failures.append(expect_rejected("order3-edge",lambda:selector_audit(planted,expected_edges=0)))
    wrong=dict(EXPECTED_POSITIVE_COUNTS); wrong[5]-=1
    failures.append(expect_rejected("unit-template-count",lambda:unit_girth_lower_audit(expected_positive=wrong)))
    failures.append(expect_rejected("shifted-equation",lambda:unit_girth_lower_audit(equation_shift=1)))
    return failures


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    check_hashes()
    cells=parse_selector()
    selector=selector_audit(cells)
    packet=load_packet()
    wall=wall_audit(packet,cells)
    lower=unit_girth_lower_audit()
    result={"machine_verdict":"PASS_Q6_M7_UNIT_GIRTH_SIX_WALL","selector":selector,
            "wall":wall,"unit_girth":{"lower_bound":6,"upper_bound":6,**lower},
            "scope":{"finite_q":6,"arbitrary_physical_potential":True,
                     "strict_common_offset_torus":True,"ordinary_euclidean":False,
                     "erdos142_solved":False,"new_r3_bound":False}}
    if args.self_test:
        result["planted_failures"]={label:"rejected" for label in self_test(packet)}
    print("PASS_Q6_M7_UNIT_GIRTH_SIX_WALL")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()

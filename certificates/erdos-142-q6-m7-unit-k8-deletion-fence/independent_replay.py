#!/usr/bin/env python3
"""Independent stdlib replay of the three k8 deletion-fence witnesses.

The 12D vertices are transcribed independently rather than loaded from the
primary packet.  This file imports no discovery or primary-verifier module.
"""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import copy
import json


Q=6
BASE=frozenset({(3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2)})
REF=frozenset((5-x,y) for x,y in BASE)
U=BASE|REF
ROWS=((2,3),(5,6),(5,7),(6,7),(0,1),(2,4),(3,4),(0,1))
CELLS=frozenset({(7,0),(25,0),(45,0),(49,0),(62,0),(27,1),(45,1),(54,1),
 (7,2),(56,2),(30,3),(33,3),(21,4),(42,4),(9,5),(20,5),(34,5),
 (4,6),(19,6),(26,6),(41,6),(48,6)})
WITNESSES={
"w1":(
 ((2,2),(3,3),(3,2),(3,2),(3,4),(2,2)), ((2,2),(3,3),(3,4),(3,4),(3,2),(2,2)),
 ((2,2),(3,3),(4,2),(4,2),(1,1),(2,2)), ((2,2),(3,3),(2,2),(2,2),(5,1),(2,2)),
 ((2,2),(3,3),(0,0),(0,0),(3,3),(2,2)), ((2,2),(3,3),(5,1),(5,1),(2,2),(2,2)),
 ((2,2),(3,3),(1,1),(1,1),(4,2),(2,2)), ((2,2),(3,3),(3,3),(3,3),(0,0),(2,2))),
"w2":(
 ((2,4),(4,2),(2,2),(2,2),(4,2),(2,3)), ((2,2),(4,2),(2,2),(2,4),(4,2),(2,3)),
 ((0,1),(1,2),(5,2),(3,2),(1,2),(5,0)), ((4,1),(1,2),(5,2),(1,2),(1,2),(5,0)),
 ((2,3),(1,2),(5,2),(5,0),(1,2),(5,0)), ((1,2),(1,2),(5,2),(4,1),(1,2),(5,0)),
 ((3,2),(1,2),(5,2),(0,1),(1,2),(5,0)), ((5,0),(1,2),(5,2),(2,3),(1,2),(5,0))),
"w3":(
 ((3,2),(2,4),(2,2),(2,3),(2,2),(3,2)), ((3,2),(2,2),(2,4),(2,3),(2,4),(3,4)),
 ((3,2),(0,1),(3,2),(5,0),(3,2),(2,2)), ((3,2),(4,1),(1,2),(5,0),(1,2),(4,2)),
 ((3,2),(2,3),(5,0),(5,0),(5,0),(0,0)), ((3,2),(1,2),(4,1),(5,0),(4,1),(1,1)),
 ((3,2),(3,2),(0,1),(5,0),(0,1),(5,1)), ((3,2),(5,0),(2,3),(5,0),(2,3),(3,3))),
}
EXPECTED_CELLS={
"w1":((33,3),(33,3),(49,0),(45,0),(45,0),(49,0),(45,0),(49,0)),
"w2":((45,1),(45,1),(19,6),(26,6),(19,6),(19,6),(26,6),(26,6)),
"w3":((30,3),(30,3),(34,5),(20,5),(34,5),(34,5),(20,5),(20,5)),}
EXPECTED_RAW={"w1":216,"w2":144,"w3":288}
CUTS=(frozenset({(33,3),(45,0),(49,0)}),frozenset({(45,1),(19,6),(26,6)}),frozenset({(30,3),(20,5),(34,5)}))
GATE_NUM=85_766_121


def cell(vertex):
    return (sum((point in REF)<<i for i,point in enumerate(vertex)),sum((a+b)&1 for a,b in vertex))


def weight(word,residue):
    total=0
    for bits in product((0,1),repeat=6):
        if sum(bits)!=residue:
            continue
        value=1
        for i,parity in enumerate(bits):
            value *= 3 if ((word>>i)&1)==parity else 6
        total += value
    return total


WEIGHTS={candidate:weight(*candidate) for candidate in CELLS}


def canonical_text():
    lines=[''.join(f'{a}{b}' for a,b in ROWS)]
    for name in ('w1','w2','w3'):
        lines.append(name+':'+';'.join(','.join(f'{a}{b}' for a,b in point) for point in WITNESSES[name]))
    return '\n'.join(lines)+'\n'


def check(witnesses=WITNESSES,cells=CELLS,cuts=CUTS,gate=GATE_NUM):
    assert len(U)==18 and BASE.isdisjoint(REF)
    assert Counter(label for row in ROWS for label in row)==Counter({i:2 for i in range(8)})
    assert all(len(witnesses[name])==8 and len(set(witnesses[name]))==8 for name in ('w1','w2','w3'))
    results={}
    for name,vertices in witnesses.items():
        assert all(point in U for vertex in vertices for point in vertex)
        physical_cells=tuple(cell(vertex) for vertex in vertices)
        assert physical_cells==EXPECTED_CELLS[name]
        assert all(candidate in cells for candidate in physical_cells)
        balance=[0]*8
        carries=[]
        row_costs=[]
        for center,(left,right) in enumerate(ROWS):
            balance[left]+=1;balance[right]+=1;balance[center]-=2
            row_carries=[]
            row_cost=0
            for position in range(6):
                x=vertices[left][position];z=vertices[right][position];y=vertices[center][position]
                dx=x[0]+z[0]-2*y[0];dy=x[1]+z[1]-2*y[1]
                assert dx%Q==dy%Q==0
                row_carries.append((dx//Q,dy//Q))
                row_cost+=(x[0]-z[0])**2+(x[1]-z[1])**2
            carries.append(tuple(row_carries))
            row_costs.append(row_cost)
        assert balance==[0]*8
        assert all(cost>0 for cost in row_costs)
        assert sum(row_costs)==EXPECTED_RAW[name]

        delta=Fraction(1,12)
        lifted=tuple(tuple((Fraction(a,Q)+delta,Fraction(b,Q)+delta) for a,b in vertex) for vertex in vertices)
        for vertex,lifted_vertex in zip(vertices,lifted):
            for point,lifted_point in zip(vertex,lifted_vertex):
                for digit,value in zip(point,lifted_point):
                    assert Fraction(digit,Q)<value<Fraction(digit+1,Q)
        for center,(left,right) in enumerate(ROWS):
            for position in range(6):
                for coordinate in range(2):
                    assert lifted[left][position][coordinate]+lifted[right][position][coordinate]-2*lifted[center][position][coordinate]==Fraction(carries[center][position][coordinate])
            lifted_cost=sum((lifted[left][position][coordinate]-lifted[right][position][coordinate])**2 for position in range(6) for coordinate in range(2))
            assert lifted_cost==Fraction(row_costs[center],Q*Q)
        results[name]={"cells":physical_cells,"raw":sum(row_costs),"carries":carries,"balance":balance}

    cut_sets=[set(cut) for cut in cuts]
    assert all(len(cut)==3 for cut in cut_sets) and len(set().union(*cut_sets))==9
    assert all(set(EXPECTED_CELLS[name])>=cut_sets[i] for i,name in enumerate(('w1','w2','w3')))
    assert all(not cut_sets[i]&cut_sets[j] for i in range(3) for j in range(i))
    minimum_deleted=sum(min(WEIGHTS[candidate] for candidate in cut) for cut in cut_sets)
    full_mass=sum(WEIGHTS.values())
    excess=Fraction(full_mass*64-gate,64)
    assert full_mass==1_370_520 and excess==Fraction(1_947_159,64) and minimum_deleted==81_648
    remaining=full_mass-minimum_deleted
    assert remaining==1_288_872 and remaining*64-gate==-3_278_313<0
    results['arithmetic']={
        'weights':{f'{word}:{residue}':value for (word,residue),value in WEIGHTS.items()},
        'full_mass':full_mass,
        'gate':f'{gate}/64',
        'excess':str(excess),
        'min_deletion':minimum_deleted,
        'remaining_mass':remaining,
        'remaining_excess_numerator':remaining*64-gate,
    }
    return results


def rejected(label,callback):
    try:
        callback()
    except AssertionError:
        return label
    raise AssertionError(label+' mutation accepted')


def controls():
    bad=copy.deepcopy(WITNESSES)
    changed=[list(vertex) for vertex in bad['w2']]
    changed[0][0]=(0,0)
    bad['w2']=tuple(tuple(vertex) for vertex in changed)
    point=rejected('point',lambda:check(bad))
    badcuts=(CUTS[0],CUTS[1],CUTS[2]|{(7,0)})
    cut=rejected('cut',lambda:check(cuts=badcuts))
    gate=rejected('gate',lambda:check(gate=GATE_NUM+1))
    return {label:'rejected' for label in (point,cut,gate)}


if __name__=='__main__':
    report=check()
    planted=controls()
    payload={
        'verdict':'PASS_INDEPENDENT_Q6_M7_UNIT_K8_DELETION_FENCE',
        'canonical_sha256':sha256(canonical_text().encode('ascii')).hexdigest(),
        'result':report,
        'planted_failures':planted,
    }
    print('PASS_INDEPENDENT_Q6_M7_UNIT_K8_DELETION_FENCE')
    print(json.dumps(payload,sort_keys=True))

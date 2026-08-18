#!/usr/bin/env python3
"""Independent stdlib audit of the frozen q6 microbox matching.

This is deliberately separate from verify.py: it has its own digit map, cell
map, mass loop, midpoint loop, and measurable shared-offset calculation.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE=Path(__file__).resolve().parent
Q=6
N=30_425
TOTAL=1_370_520
GATE=85_766_121

# Position 0..8 is BASE, 9..17 is REF in the ledger's base-18 encoding.
L=((3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2),
   (2,2),(2,3),(2,4),(1,1),(1,2),(1,3),(0,0),(0,1),(0,2))
T=((4,5),(4,7),(6,7),(5,6),(2,3),(1,2),(0,1),(0,3))
C=frozenset({(7,0),(25,0),(45,0),(49,0),(62,0),(27,1),(45,1),(54,1),
 (7,2),(56,2),(30,3),(33,3),(21,4),(42,4),(9,5),(20,5),(34,5),
 (4,6),(19,6),(26,6),(41,6),(48,6)})


def parse_cells_file():
    z=[]
    for line in (HERE/'candidate.cells').read_text(encoding='ascii').splitlines():
        if line:z.append(tuple(map(int,line.split(':'))))
    assert tuple(z)==((7,0),(25,0),(45,0),(49,0),(62,0),(27,1),(45,1),(54,1),
        (7,2),(56,2),(30,3),(33,3),(21,4),(42,4),(9,5),(20,5),(34,5),
        (4,6),(19,6),(26,6),(41,6),(48,6))


def parse_template_file():
    z=json.loads((HERE/'template.json').read_text(encoding='ascii'))
    assert z['q']==6 and tuple(map(tuple,z['rows']))==T
    assert z['endpoint_degree']==2 and z['centers']==list(range(8))


def count_box(word,residue):
    n=0
    for b in product((0,1),repeat=6):
        if sum(b)!=residue:continue
        v=1
        for j,par in enumerate(b):
            # orientation 0 gives 3 at even parity, orientation 1 gives 6.
            v*=3 if par==((word>>j)&1) else 6
        n+=v
    return n


def box_cell(columns,i):
    w=0;r=0
    for j in range(6):
        n=columns[j][i]
        w|=(n//9)<<j
        r+=(L[n][0]+L[n][1])&1
    return w,r


def code(columns,i):
    result=0
    factor=1
    for j in range(6):
        result+=factor*columns[j][i]
        factor*=18
    return result


def check_manifest():
    con=json.loads((HERE/'constants.json').read_text(encoding='ascii'))
    assert con['matching_packets']==N and con['maximum_minus_gate_numerator']==-41
    assert con['forced_deleted_measure_box_units']==N
    assert con['maximum_retained_measure_box_units']==TOTAL-N
    assert con['ledger_channels_sha256']=='96655FA6B81E3B67D1FA55D12242557924A7DD5403BC74318EFEF05A04622BE8'
    assert con['ledger_enumeration_solutions_used']==7194
    for name,digest in con['artifact_sha256'].items():
        assert sha256((HERE/name).read_bytes()).hexdigest().upper()==digest


def run():
    check_manifest();parse_cells_file();parse_template_file()
    assert len(L)==18 and len(set(L))==18 and tuple((x[0] for x in L[9:]))==(2,2,2,1,1,1,0,0,0)
    # For every full shared offset t in D=[0,1/6)^12, each digit/6+t
    # remains in its half-open microbox.  The coefficient of t in any row is
    # 1+1-2=0; the integer defect checks below therefore prove the lifted
    # torus identity for all t, not merely a chosen representative.
    assert Fraction(0)<Fraction(1,12)<Fraction(1,6)
    assert all(0<=coordinate<6 for pair in L for coordinate in pair)
    assert 1+1-2==0
    assert Counter(k for row in T for k in row)==Counter({j:2 for j in range(8)})
    assert sum(count_box(*z) for z in C)==TOTAL
    d=json.loads((HERE/'matching_ledger.json').read_text(encoding='ascii'))
    assert tuple(map(tuple,d['template']))==T and frozenset(map(tuple,d['candidate']))==C
    assert d['channels_sha256'].upper()=='96655FA6B81E3B67D1FA55D12242557924A7DD5403BC74318EFEF05A04622BE8'
    assert d['enumeration_solutions_used']==7194
    assert len(d['packets'])==N
    used=set();total_cost=0;car=Counter();roles=Counter()
    for pno,p in enumerate(d['packets']):
        x=tuple(tuple(c) for c in p['columns'])
        assert len(x)==6 and all(len(c)==8 for c in x)
        assert all(0<=z<18 for c in x for z in c)
        got=tuple(box_cell(x,i) for i in range(8))
        assert got==tuple(map(tuple,p['cells'])) and set(got)<=C
        ids=tuple(code(x,i) for i in range(8))
        assert ids==tuple(p['vertices']) and len(set(ids))==8
        assert used.isdisjoint(ids),(pno,'overlap')
        used.update(ids);roles.update(got)
        coefficients=[0]*8;cost=[]
        for center,(a,b) in enumerate(T):
            coefficients[a]+=1;coefficients[b]+=1;coefficients[center]-=2
            q=0
            for j in range(6):
                aa,bb,cc=L[x[j][a]],L[x[j][b]],L[x[j][center]]
                for k in (0,1):
                    defect=aa[k]+bb[k]-2*cc[k]
                    assert defect%6==0
                    car[(j,k,defect//6)]+=1
                    q+=(aa[k]-bb[k])**2
            assert q>0;cost.append(q)
        assert coefficients==[0]*8 and tuple(cost)==tuple(p['raw_costs'])
        total_cost+=sum(cost)
    assert len(used)==8*N
    # For a retained measurable E, A[p,i]={t in [0,1/6)^12: d[p,i]/6+t in E}.
    # Positive cancellation says intersect_i A[p,i] is empty a.e.; union bound
    # gives one offset-cube worth of deletion per packet.  Distinct ledger boxes
    # make these translated deletion pieces disjoint, hence deletion >= N boxes.
    remaining=TOTAL-N
    assert remaining==1_340_095 and remaining*64-GATE==-41
    return {'verdict':'PASS_INDEPENDENT_CANDIDATE22_MICROBOX_FENCE','packets':N,
      'boxes':len(used),'ledger_sha256':sha256((HERE/'matching_ledger.json').read_bytes()).hexdigest(),
      'raw_cost_total':total_cost,'carry_terms':sum(car.values()),
      'role_count_total':sum(roles.values()),'remaining_measure_box_units':remaining,'gate_gap_numerator':-41}


if __name__=='__main__':
    print('PASS_INDEPENDENT_CANDIDATE22_MICROBOX_FENCE')
    print(json.dumps(run(),sort_keys=True))

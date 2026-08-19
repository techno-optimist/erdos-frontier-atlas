"""Stdlib-only semantic replay for the q=24 role-distinct Farkas packet."""
from __future__ import annotations
import copy, hashlib, json, sys
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

HERE=Path(__file__).resolve().parent
PACKET=HERE/'certificate.json'
Q=24; ROLES=('P1','P2','P3','B','K')
WORDS=(('P1','K','B'),('B','K','P1'),('P2','B','P2'),('P3','B','B'),('B','B','P3'))
EXPECTED_HASH='45B29FD55F923626354885825ED57E8DB47E5C40BDE6AF8D8B1E203C3B3F68A1'

def tile():
    out=[]
    for x,y in product(range(Q),repeat=2):
        s=x+y
        t1=2*x>=Q and 6*s>4*Q and 6*s<=7*Q
        t2=2*x>=Q and 2*y<Q and 12*s>=14*Q+12 and 12*s<=17*Q
        t3=2*x<Q and 2*y>=Q and 12*s>=14*Q+12 and 12*s<=17*Q and 2*(2*x+y)>=3*Q+2
        if t1 or t2 or t3: out.append((x,y))
    assert len(out)==163
    return tuple(out)

def image(base,k):
    out=[]
    for x,y in base:
        if k&1: x=Q-1-x
        if k&2: y=Q-1-y
        if k&4: x,y=y,x
        out.append((x,y))
    return tuple(sorted(out))

def union_count(supports):
    ss={r:set(supports[r]) for r in ROLES}; total=0
    for size in range(1,6):
        for chosen in combinations(WORDS,size):
            term=1
            for c in range(3):
                common=set(ss[chosen[0][c]])
                for word in chosen[1:]: common.intersection_update(ss[word[c]])
                term*=len(common)
            total+=term if size&1 else -term
    return total

def verify(d, *, check_hash=True):
    assert d['packet']=='q24 role-distinct semantic Farkas replay'
    assert d['q']==Q and tuple(d['roles'])==ROLES and tuple(map(tuple,d['codewords']))==WORDS
    assert d['assignment']==[7,7,7,6,7] and d['share_overlaps'] is False
    assert d['source_frozen_sha256']==EXPECTED_HASH
    frozen_rows=None
    if check_hash:
        frozen=HERE/'role_distinct_ipm_rows.json'
        assert frozen.exists() and hashlib.sha256(frozen.read_bytes()).hexdigest().upper()==EXPECTED_HASH
        frozen_rows=json.loads(frozen.read_text())['rows']
    base=tile(); images=[]
    for k in range(8):
        im=image(base,k)
        if im not in images: images.append(im)
    assert len(images)==8
    supports={r:images[d['assignment'][i]] for i,r in enumerate(ROLES)}
    assert union_count(supports)==d['union_mass_count']==21653735
    assert d['union_mass_count']>d['threshold_count']==4741632
    # Role-distinct indexer: role order, then sorted support order.
    labels=[]; index={}
    for role in ROLES:
        for point in supports[role]:
            index[(role,point)]=len(labels); labels.append([role,list(point)])
    assert labels==d['variable_labels'] and len(labels)==815
    aggregate={}; rhs=0
    assert len(d['selected_rows'])==d['selected_row_count']==622
    seen=set()
    for row in d['selected_rows']:
        frozen_index=row['frozen_row_index']; assert isinstance(frozen_index,int) and 0<=frozen_index<d['frozen_row_count']
        assert frozen_index not in seen; seen.add(frozen_index)
        m=int(row['multiplier']); assert m>0
        a,b,c=row['word_indices']; assert all(0<=t<5 for t in (a,b,c))
        u,v,w=WORDS[a],WORDS[b],WORDS[c]
        assert len(row['witnesses'])==3
        coeff={}; row_rhs=0
        for coordinate,rec in enumerate(row['witnesses']):
            roles=(u[coordinate],v[coordinate],w[coordinate])
            assert tuple(rec['role_triple'])==roles
            x,y,z=map(tuple,(rec['x'],rec['y'],rec['z']))
            assert x in supports[roles[0]] and y in supports[roles[1]] and z in supports[roles[2]]
            assert all((2*y[j]-x[j]-z[j])%Q==0 for j in (0,1))
            carry=tuple((x[j]+z[j]-2*y[j])//Q for j in (0,1))
            assert list(carry)==rec['carry'] and all(t in (-1,0,1) for t in carry)
            cost=(x[0]-z[0])**2+(x[1]-z[1])**2
            assert cost==rec['raw_cost_numerator']
            row_rhs+=cost
            for role,point,coef in ((roles[0],x,1),(roles[1],y,-2),(roles[2],z,1)):
                k=index[(role,point)]; coeff[k]=coeff.get(k,0)+coef
        if frozen_rows is not None:
            saved=frozen_rows[frozen_index]
            expected=[[k,v] for k,v in sorted(coeff.items()) if v]
            assert saved['coefficients']==expected and saved['rhs_num']==row_rhs
        rhs+=m*row_rhs
        for k,val in coeff.items(): aggregate[k]=aggregate.get(k,0)+m*val
    assert not any(aggregate.values())
    assert rhs==int(d['positive_rhs_num']) and rhs>0
    return rhs

def expect_failure(d):
    try: verify(d,check_hash=False)
    except (AssertionError,KeyError,TypeError,ValueError): return
    raise AssertionError('planted corruption was accepted')

def self_test(d):
    # multiplier; midpoint carry; raw cost; role; missing row; mass/D4 assignment.
    x=copy.deepcopy(d); x['selected_rows'][0]['multiplier']=str(int(x['selected_rows'][0]['multiplier'])+1); expect_failure(x)
    x=copy.deepcopy(d); x['selected_rows'][0]['witnesses'][0]['carry'][0]+=1; expect_failure(x)
    x=copy.deepcopy(d); x['selected_rows'][0]['witnesses'][0]['raw_cost_numerator']+=1; expect_failure(x)
    x=copy.deepcopy(d); x['selected_rows'][0]['witnesses'][0]['role_triple'][0]='B'; expect_failure(x)
    x=copy.deepcopy(d); x['selected_rows'].pop(); expect_failure(x)
    x=copy.deepcopy(d); x['assignment'][3]=7; expect_failure(x)

if __name__=='__main__':
    data=json.loads(PACKET.read_text()); value=verify(data)
    planted='--self-test' in sys.argv
    if planted: self_test(data)
    print('PASS_Q24_D4_ROLE_DISTINCT_ADDITIVE_WALL')
    print(f'verified semantic q=24 role-distinct Farkas packet: 0 >= {value}')
    if planted:
        print('planted_failures multiplier,carry,raw-cost,role,missing-row,d4-assignment-mass')

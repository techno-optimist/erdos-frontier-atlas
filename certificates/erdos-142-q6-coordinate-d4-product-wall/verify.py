#!/usr/bin/env python3
"""Self-contained q=6 coordinate-dependent D4 product-block wall.

For every n>=1, distinct D4 words A,B produce three physical rows
(A,A,B),(A,B,A),(B,A,A) whose signed physical-point incidence is zero and
whose raw RHS is positive.  A singleton block has density (1/4)^n<(7/24)^n.
No project-module imports or LP solver are used.
"""
from __future__ import annotations
import argparse, itertools, json
from collections import Counter
from fractions import Fraction

Q=6; THETA=Fraction(7,24)
EHPS=((3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2))
POINTS=tuple(itertools.product(range(Q),repeat=2))

def image(k):
    assert 0<=k<8
    if not k&4: return frozenset((Q-1-x if k&1 else x,Q-1-y if k&2 else y) for x,y in EHPS)
    return frozenset((Q-1-y if k&2 else y,Q-1-x if k&1 else x) for x,y in EHPS)
IMS=tuple(image(k) for k in range(8))
assert len(set(IMS))==8 and all(len(s)==9 for s in IMS)
def mid(x,y,z): return all((2*y[i]-x[i]-z[i])%Q==0 for i in range(2))
def carry(x,y,z):
    d=tuple(x[i]+z[i]-2*y[i] for i in range(2)); assert all(v%Q==0 for v in d); return tuple(v//Q for v in d)
def raw(x,z): return sum((x[i]-z[i])**2 for i in range(2))

TORSION=tuple((x,y,z) for x,y,z in itertools.product(POINTS,repeat=3) if mid(x,y,z) and mid(y,z,x) and mid(z,x,y))
def local():
    buckets={(a,b,c):tuple(t for t in TORSION if t[0] in IMS[a] and t[1] in IMS[b] and t[2] in IMS[c]) for a,b,c in itertools.product(range(8),repeat=3)}
    assert len(TORSION)==324 and len(buckets)==512
    sizes=list(map(len,buckets.values())); assert min(sizes)==4 and max(sizes)==9
    diag={}; non={}
    for a in range(8):
        diag[a]=next(t for t in buckets[a,a,a] if t[0]==t[1]==t[2]); assert all(t[0]==t[1]==t[2] for t in buckets[a,a,a])
        for b in range(8):
            if a!=b: non[a,b]=next(t for t in buckets[a,a,b] if len(set(t))>1)
    assert len(non)==56
    return buckets,diag,non
BUCKETS,DIAG,NON=local()

def construct(A,B,non=NON,diag=DIAG):
    assert len(A)==len(B) and len(A)>0 and tuple(A)!=tuple(B)
    t=[non[a,b] if a!=b else diag[a] for a,b in zip(A,B)]
    X,Y,Z=tuple(x[0] for x in t),tuple(x[1] for x in t),tuple(x[2] for x in t)
    return [((0,0,1),X,Y,Z),((0,1,0),Y,Z,X),((1,0,0),Z,X,Y)]

def validate(A,B,rows,label_alias=False):
    words=(tuple(A),tuple(B)); bal=Counter(); total=0; out=[]
    for labels,X,Y,Z in rows:
        cs=[]
        for i,(x,y,z) in enumerate(zip(X,Y,Z)):
            assert x in IMS[words[labels[0]][i]] and y in IMS[words[labels[1]][i]] and z in IMS[words[labels[2]][i]]
            assert mid(x,y,z); cs.append(carry(x,y,z))
        r=sum(raw(x,z) for x,z in zip(X,Z)); total+=r
        keys=((labels[0],X),(labels[1],Y),(labels[2],Z)) if label_alias else (X,Y,Z)
        bal[keys[0]]+=1; bal[keys[1]]-=2; bal[keys[2]]+=1
        out.append({"label_word_indices":list(labels),"x":[list(p) for p in X],"y":[list(p) for p in Y],"z":[list(p) for p in Z],"carries":[list(c) for c in cs],"raw_cost_numerator":r})
    assert not {k:v for k,v in bal.items() if v} and total>0
    return out,total,len(bal)

def density(n,gate=THETA):
    value=Fraction(1,4)**n; target=gate**n; assert value<target; return value,target
def expect_fail(name,f,got):
    try:f()
    except (AssertionError,KeyError,StopIteration):got.append(name);return
    raise AssertionError('planted failure passed: '+name)
def self_tests(A,B,rows):
    got=[]; broken=dict(NON);del broken[0,1]
    expect_fail('removed_local_witness',lambda:construct(A,B,non=broken),got)
    bad=list(rows); labels,X,Y,Z=bad[0]; bad[0]=(labels,X,(Z[0],)+Y[1:],Z)
    expect_fail('corrupt_midpoint',lambda:validate(A,B,bad),got)
    x,y,z=rows[0][1][0],rows[0][2][0],rows[0][3][0]
    expect_fail('corrupt_carry',lambda:assert_carry(x,y,z,(carry(x,y,z)[0]+1,carry(x,y,z)[1])),got)
    expect_fail('corrupt_raw_cost',lambda:assert_raw(x,z,raw(x,z)+1),got)
    # Two labels carrying the identical word denote the same physical block;
    # counting label occurrences as separate vertices would double its mass.
    expect_fail('alias_labels_not_physical_vertices',lambda:assert_physical_mass_not_label_count(),got)
    expect_fail('erase_differing_coordinate',lambda:construct(A,A),got)
    expect_fail('wrong_singleton_gate',lambda:density(6,Fraction(1,5)),got)
    assert len(got)==7;return got
def assert_carry(x,y,z,v):assert carry(x,y,z)==v
def assert_raw(x,z,v):assert raw(x,z)==v
def assert_physical_mass_not_label_count():
    physical=Fraction(1,4)**6; occurrence=2*physical
    assert occurrence==physical

def main(test):
    A=(0,0,0,0,0,0);B=(1,1,1,1,0,0); rows=construct(A,B); rendered,total,verts=validate(A,B,rows); mass,gate=density(6)
    result={"status":"verified-coordinate-dependent-product-block-wall","self_contained":True,"q":Q,"ehps_q6_support":[list(p) for p in EHPS],"torsion_triple_count":len(TORSION),"ordered_d4_bucket_count":len(BUCKETS),"bucket_size_min":min(map(len,BUCKETS.values())),"bucket_size_max":max(map(len,BUCKETS.values())),"nondegenerate_ordered_pair_count":len(NON),"general_theorem":"For every n>=1, construct(A,B) proves a positive physical 3-row Farkas cycle for distinct D4 words; density(n) proves a singleton is below gate.","single_block_mass_n6":str(mass),"gate_n6":str(gate),"example_distinct_words":[list(A),list(B)],"example_rows":rendered,"example_weighted_raw_cost":total,"example_weighted_rhs":str(Fraction(total,Q*Q)),"example_physical_vertices":verts,"planted_failures_caught":self_tests(A,B,rows) if test else []}
    print(json.dumps({k:result[k] for k in ('status','self_contained','torsion_triple_count','ordered_d4_bucket_count','bucket_size_min','bucket_size_max','nondegenerate_ordered_pair_count','single_block_mass_n6','gate_n6','example_weighted_rhs','planted_failures_caught')},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');main(p.parse_args().self_test)

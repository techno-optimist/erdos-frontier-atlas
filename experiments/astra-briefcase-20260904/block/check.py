#!/usr/bin/env python3
"""Independent exact integer probe of three-hub Laurent block."""
from collections import defaultdict
from itertools import product
from math import comb
import json, argparse

def add(*ps):
    o=defaultdict(int)
    for p in ps:
        for k,v in p.items(): o[k]+=v
    return {k:v for k,v in o.items() if v}
def scale(p,a): return {k:a*v for k,v in p.items() if a*v}
def mul(*ps):
    o={0:1}
    for p in ps:
        d=defaultdict(int)
        for i,a in o.items():
            for j,b in p.items(): d[i+j]+=a*b
        o=dict(d)
    return o
def P(r): return add({r:1},{-r:1})
def W(r): return {r-2*j:comb(r,j) for j in range(r+1)}
def B(r,s,t,c=1,d=1,e=1):
    return add(P(r-s+t),scale(mul(W(r),P(s-t)),c),scale(mul(W(s),P(r),P(t)),d),scale(mul(W(t),P(r-s)),e),scale(mul(W(r+s),P(t)),c*d),scale(mul(W(r+t),P(s)),c*e),scale(mul(W(s+t),P(r)),d*e),scale(W(r+s+t),c*d*e))
def states(rs,cs):
    o={}
    for active in product((0,1),repeat=3):
        factors=[]; i=0
        while i<3:
            if not active[i]: factors.append(scale(W(rs[i]),cs[i])); i+=1
            else:
                v=0; sign=1
                while i<3 and active[i]: v+=sign*rs[i]; sign=-sign; i+=1
                factors.append(P(v))
        o=add(o,mul(*factors))
    return o
def failures(p):
    assert all(p.get(-k,0)==v for k,v in p.items())
    top=max(p)
    return [(k,p.get(k,0),p.get(k+2,0)) for k in range(top%2,top,2) if p.get(k,0)<p.get(k+2,0)]
def Q(r): return add(W(r),P(r))
def H(r,s): return add(mul(Q(r),Q(s)),scale(P(r+s),-1))
def shifted_expansion(r,s,t,c,d,e):
    C,D,E=c-1,d-1,e-1
    return add(B(r,s,t),scale(mul(W(r),H(s,t)),C),
      scale(mul(W(s),Q(r),Q(t)),D),scale(mul(W(t),H(r,s)),E),
      scale(mul(W(r+s),Q(t)),C*D),scale(mul(W(r+t),Q(s)),C*E),
      scale(mul(W(s+t),Q(r)),D*E),scale(W(r+s+t),C*D*E))
def inward(p,n): return [p.get(n-2*j,0) for j in range(n//2+1)]
def differences(p,n):
    v=inward(p,n)
    return [b-a for a,b in zip(v,v[1:])]
def proof_boundaries():
    single=[]; double=[]; small=[]
    for a in range(1,8):
        for b in range(8-a):
            if (7-a-b)%2: continue
            p=add(W(7),scale(mul(W(a),P(b)),7))
            assert not failures(p)
            single.append({'a':a,'b':b,'differences':differences(p,7)})
    for r in range(1,6):
        for t in range(1,7-r):
            s=7-r-t
            p=add(W(7),scale(mul(W(s),P(r),P(t)),7))
            assert not failures(p)
            double.append({'r':r,'s':s,'t':t,'differences':differences(p,7)})
    for n in range(3,7):
        for r in range(1,n-1):
            for s in range(1,n-r):
                t=n-r-s; p=B(r,s,t)
                assert p==states((r,s,t),(1,1,1))
                assert not failures(p)
                small.append({'r':r,'s':s,'t':t,'differences':differences(p,n)})
    # Independent finite guards for unbounded algebraic proof identities.
    auxiliary=0
    for r,s,t in product(range(1,7),repeat=3):
        assert shifted_expansion(r,s,t,2,4,8)==states((r,s,t),(2,4,8))
        auxiliary+=1
    return {'single_boundary':single,'double_boundary':double,'small_blocks':small,
            'boundary_counts':[len(single),len(double),len(small)],
            'shifted_scalar_identity_checks':auxiliary}
def main():
    a=argparse.ArgumentParser(); a.add_argument('--bound',type=int,default=12); args=a.parse_args()
    if args.bound<1: a.error('--bound must be at least 1')
    count=0; bad=[]; tight=[]
    for rs in product(range(1,args.bound+1),repeat=3):
        p=B(*rs); f=failures(p); count+=1
        if f: bad.append({'rs':rs,'failures':f}); break
        if any(p.get(k,0)==p.get(k+2,0) for k in range(sum(rs)%2,sum(rs),2)): tight.append(rs)
    identities=0
    for rs in product(range(1,5),repeat=3):
        for cs in ((1,1,1),(2,4,8),(0,1,0)):
            assert B(*rs,*cs)==states(rs,cs); identities+=1
    neg=B(1,4,1,1,0,1); assert failures(neg)
    proof=proof_boundaries()
    assert not bad
    print(json.dumps({'status':'PASS','checked':count,'bound':args.bound,'counterexamples':bad,'tight':tight,'independent_state_identities':identities,'negative_control':failures(neg),'proof':proof},indent=2))
if __name__=='__main__': main()

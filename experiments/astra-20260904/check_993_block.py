#!/usr/bin/env python3
"""Exact checks supporting an algebraic lemma, not a tree enumeration."""
from collections import defaultdict
from fractions import Fraction
from itertools import product
from math import comb
import json


def add(*ps):
    out = defaultdict(Fraction)
    for p in ps:
        for k, v in p.items():
            out[k] += v
    return {k: v for k, v in out.items() if v}


def mul(*ps):
    out = {0: Fraction(1)}
    for p in ps:
        tmp = defaultdict(Fraction)
        for i, a in out.items():
            for j, b in p.items():
                tmp[i + j] += a * b
        out = {k: v for k, v in tmp.items() if v}
    return out


def scale(p, a):
    return {k: Fraction(a) * v for k, v in p.items() if a * v}


def P(r):
    return add({r: Fraction(1)}, {-r: Fraction(1)})


def W(r):
    return {2*j-r: Fraction(comb(r,j)) for j in range(r+1)}


def states_block(rs, cs):
    """Independent derivation from active-site runs on a 3-vertex path."""
    out = {}
    for active in product((False, True), repeat=3):
        term = {0: Fraction(1)}
        i = 0
        while i < 3:
            if not active[i]:
                term = mul(term, scale(W(rs[i]), cs[i]))
                i += 1
            else:
                imbalance, sign = 0, 1
                while i < 3 and active[i]:
                    imbalance += sign * rs[i]
                    sign *= -1
                    i += 1
                term = mul(term, P(imbalance))
        out = add(out, term)
    return out


def expanded_block(r,s,t,c,d,e):
    R,S,T = scale(W(r),c),scale(W(s),d),scale(W(t),e)
    return add(P(r-s+t), mul(R,P(s-t)), mul(S,P(r),P(t)),
               mul(T,P(r-s)), mul(R,S,P(t)), mul(R,T,P(s)),
               mul(S,T,P(r)), mul(R,S,T))


def compact_block(s,c,d,e):
    n = s + 2
    u = (1+c)*(1+e)
    return add(scale(W(n),d*u), scale(P(n),c*e),
               scale(P(n-2),c+e+2*c*e), scale(P(n-4),u))


def failures(p):
    if not p:
        return []
    assert all(p.get(-k,0) == a for k,a in p.items())
    top = max(p)
    return [(k,p.get(k,0),p.get(k+2,0))
            for k in range(top % 2, top, 2)
            if p.get(k,0) < p.get(k+2,0)]


def main():
    cases = [(0,1,0),(1,1,1),(2,4,8),(Fraction(1,3),1,Fraction(7,2))]
    checked = 0
    for s in range(1,65):
        for c,d,e in cases:
            p = states_block((1,s,1),(c,d,e))
            assert p == expanded_block(1,s,1,c,d,e)
            assert p == compact_block(s,c,d,e)
            assert not failures(p)
            checked += 1
    general_identities = 0
    for r,s,t in product((1,2,5),repeat=3):
        assert states_block((r,s,t),(2,4,8)) == expanded_block(r,s,t,2,4,8)
        general_identities += 1
    bad = compact_block(4,1,0,1)
    assert failures(bad), 'The deliberately inadmissible d=0 must fail'
    assert bad.get(0,0)==0 and bad[2]==4
    result = {'status':'PASS', 'lemma_test_cases':checked,
              'general_block_identity_cases':general_identities,
              'range_s':[1,64], 'all_arithmetic':'exact rational',
              'negative_control':{'s':4,'c':1,'d':0,'e':1,
                                  'coefficient_z0':int(bad.get(0,0)),
                                  'coefficient_z2':int(bad.get(2,0))},
              'scope':'Checks identities and examples; unbounded proof is in 993-block.md.'}
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()

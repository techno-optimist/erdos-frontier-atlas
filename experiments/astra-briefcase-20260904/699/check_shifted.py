#!/usr/bin/env python3
"""Exact small lemma probes; no frontier or all-n computational claim."""
from math import comb, gcd, isqrt
from pathlib import Path
import json
import sys

PRIMES = [p for p in range(2, 1500) if all(p % q for q in range(2, isqrt(p)+1))]
EXCEPTIONS = {(8,3):7, (9,4):None, (10,5):None, (12,5):11,
              (21,7):19, (21,8):19, (30,7):29, (33,13):31,
              (33,14):31, (36,13):31, (36,17):31, (56,13):53}

def valuation(x,p):
    a=0
    while x%p==0:
        x//=p
        a+=1
    return a

def inspect(i,j,d):
    n=2*j+d
    X,Y=comb(n,i),comb(n,j)
    h=(i-d+1)//2
    B=comb(j,h)
    W=1
    wraps=[]
    for p in PRIMES:
        if p>n: break
        if p<i or X%p or Y%p==0: continue
        a=valuation(X,p)
        M=p**(a+int(p==i))
        r,s=j%M,(j+d)%M
        assert r+s<i
        W*=p**a
        if d+r-s:
            wraps.append((p,a,r,s))
        else:
            assert 0<=r<h and B%(p**a)==0
    if not wraps:
        assert B%W==0
        assert W*W<X
    else:
        assert len(wraps)==1 and i%2==0
        p,a,r,s=wraps[0]
        assert p==i+1 and a==1 and r==p-d and s==0
        A=i//2
        C=comb(j+1,A)
        k=(j+d)//p
        assert j==k*p-d and k>=2
        U=W//p
        g=gcd(A,j+1)
        assert B%U==0 and C%U==0
        assert gcd(B,C)==B*g//A
        assert g==gcd(A,k+1-d)
        if d==2 or k>=3:
            assert p*g<j+1
            assert W<=p*gcd(B,C)<C
            assert C*C<X
        else:
            assert d==3 and k==2 and j==2*i-1
    # Independently check the resulting theorem in its stated domain.
    theorem_applies = d==2 or (d==3 and i%2==0 and j!=2*i-1)
    if theorem_applies:
        assert any(p>=i and X%p==0 and Y%p==0 for p in PRIMES if p<=n)
    return dict(wrap=bool(wraps), theorem=theorem_applies)

# A tempting stronger divisibility is false on an actual wrap instance.
i,j,n,p=4,8,18,5
assert comb(n,i)%p==0 and comb(n,j)%p!=0
assert comb(j+1,i//2)%p!=0
if '--negative-control' in sys.argv:
    assert comb(j+1,i//2)%p==0, 'FALSE shifted integrality: 5 does not divide C(9,2)=36'

counts=dict(d2_triples=0,d2_wraps=0,d3_even_triples=0,d3_even_wraps=0,
            d3_theorem_triples=0,d3_diagonal_wraps=0,exception_triples=0,
            symbolic_inequality_samples=0)
for i in range(2,61):
    for j in range(i+1,361):
        z=inspect(i,j,2)
        counts['d2_triples']+=1
        counts['d2_wraps']+=z['wrap']
        if i>=4 and i%2==0:
            z=inspect(i,j,3)
            counts['d3_even_triples']+=1
            counts['d3_even_wraps']+=z['wrap']
            counts['d3_theorem_triples']+=z['theorem']
            counts['d3_diagonal_wraps']+=z['wrap'] and not z['theorem']

# Large j, small degree: check exact symbolic inequalities, not giant C(n,j).
for p in [3,5,7,11,13,17,31,101,499]:
    A=(p-1)//2
    for k in [2,3,7,p,10**3,10**6]:
        j=k*p-2
        B,C=comb(j,A-1),comb(j+1,A)
        g=gcd(A,k-1)
        assert gcd(B,C)==B*g//A
        assert p*g<j+1
        assert p*gcd(B,C)<C
        assert C*C<comb(2*j+2,2*A)
        counts['symbolic_inequality_samples']+=1

for (n,i),p in EXCEPTIONS.items():
    for j in range(i+1,n//2+1):
        if n!=2*j+2 and not(n==2*j+3 and i>=4 and i%2==0 and j!=2*i-1): continue
        assert p is not None and p>=i and comb(n,i)%p==0 and comb(n,j)%p==0
        counts['exception_triples']+=1

obstruction=dict(n=42,i=10,j=20,p=11,N=comb(42,10),B=comb(20,4),C=comb(21,5))
obstruction['crude_bound_squared']=(11*obstruction['B'])**2
obstruction['corrected_bound']=11*gcd(obstruction['B'],obstruction['C'])
assert obstruction['crude_bound_squared']>obstruction['N']
assert obstruction['corrected_bound']**2<obstruction['N']
report=dict(verified=True,counts=counts,crude_bound_counterexample=obstruction,
            integrality_counterexample=dict(n=18,i=4,j=8,absent_prime=5,shifted_binomial=36),
            scope='Exact bounded lemma checks plus sampled symbolic inequalities; all-parameter proofs are in result.md; no novelty, formalization, or publication claim.')
text=json.dumps(report,indent=2)+'\n'
path=Path(__file__).with_name('receipt.json')
if '--emit' in sys.argv:
    with path.open('x') as f: f.write(text)
else:
    assert path.read_text()==text, 'receipt differs from recomputation'
print(text)

#!/usr/bin/env python3
"""Bounded exact tests of lifted localization, not a frontier sweep.
All binomial divisibility/valuations use direct math.comb arithmetic.
--negative-control deliberately over-lifts by one and must exit nonzero.
"""
from math import comb, isqrt, prod
import json
import sys
from pathlib import Path

NEGATIVE = '--negative-control' in sys.argv
LIMIT = 240
primes = [p for p in range(2, 2 * LIMIT + 1)
          if all(p % q for q in range(2, isqrt(p) + 1))]
EXCEPTIONS = {(8,3):7, (9,4):None, (10,5):None, (12,5):11,
              (21,7):19, (21,8):19, (30,7):29, (33,13):31,
              (33,14):31, (36,13):31, (36,17):31, (56,13):53}

# First tracer bullet: prime i loses exactly one p in i!, not two.
# This is a real non-common candidate, so the test is nonvacuous.
n, i, j, p = 18, 3, 9, 3
assert comb(n, i) % p == 0 and comb(n, j) % p != 0
x, a = comb(n, i), 0
while x % p == 0:
    x //= p
    a += 1
M = p ** (a + 1 + int(NEGATIVE))
r, s = j % M, (n-j) % M
assert r+s < i, ('planted over-lift', n, i, j, p, a, M, r, s)

counts = dict(localized_prime_powers=0, boundary_prime_lifts=0,
              refined_euclidean_products=0, strip_products=0,
              strip_gcd_checks=0, exception_triples=0,
              inequality_checks=0)
examples = []

for n in range(4, LIMIT+1):
    half = n // 2
    C = [comb(n, k) for k in range(half+1)]
    for i in range(2, half):
        candidates = []
        for p in primes:
            if p > n:
                break
            if p < i or C[i] % p:
                continue
            x, a = C[i], 0
            while x % p == 0:
                x //= p
                a += 1
            candidates.append((p,a))
        pnext = next(p for p in primes if p > i)
        for j in range(i+1, half+1):
            W = 1
            Q, R = divmod(n,j)
            T = R+(Q-1)*(i-1)
            hE = max(0, (i-R+Q-1)//Q)
            LE = 1
            for q in primes:
                if q > T:
                    break
                if q < i:
                    continue
                power, exponent = q, 0
                while power <= T:
                    exponent += 1
                    power *= q
                exponent = max(0, exponent-int(q==i))
                LE *= q**exponent
            for p,a in candidates:
                if C[j] % p == 0:
                    continue
                M = p ** (a+int(p==i))
                r,s = j%M, (n-j)%M
                assert r+s < i, (n,i,j,p,a,M,r,s)
                assert (n-r-s) % M == 0
                assert (j-r) % M == 0 and (n-j-s) % M == 0
                W *= p**a
                counts['localized_prime_powers'] += 1
                if p == i:
                    counts['boundary_prime_lifts'] += 1
                    if len(examples) < 8:
                        examples.append(dict(n=n,i=i,j=j,p=p,a=a,M=M,r=r,s=s))
            assert (LE*comb(j,hE)) % W == 0, (n,i,j,W,T,hE,LE)
            counts['refined_euclidean_products'] += 1
            d = n-2*j
            if 1 <= d <= pnext-i:
                h = (i-d+1)//2
                assert 0 <= h <= i//2
                assert comb(j,h) % W == 0, (n,i,j,d,h,W)
                counts['strip_products'] += 1
                # Direct check of the theorem, independent of the size proof.
                assert any(C[j] % p == 0 for p,a in candidates), (n,i,j)
                counts['strip_gcd_checks'] += 1

for (n,i),q in EXCEPTIONS.items():
    for j in range(i+1,n//2+1):
        assert q is not None and q in primes and q >= i
        assert n-i < q <= n and q > n/2
        assert comb(n,i)%q == 0 and comb(n,j)%q == 0
        counts['exception_triples'] += 1

for i in range(2,301):
    pnext = next(p for p in primes if p > i)
    for d in range(1,pnext-i+1):
        h=(i-d+1)//2
        for j in sorted({i+1,2*i,10*i,100*i}):
            assert comb(2*j+d,i) > comb(j,h)**2
            counts['inequality_checks'] += 1

assert counts['boundary_prime_lifts'] > 0
summary = dict(verified=True, n_bound=LIMIT, counts=counts,
               boundary_lift_examples=examples,
               scope='bounded lemma tests; no all-n computational claim')
target = Path(__file__).with_name('lemma-checks.json')
payload = json.dumps(summary, indent=2) + '\n'
if '--emit' in sys.argv:
    with target.open('x') as f:
        f.write(payload)
elif not target.exists() or target.read_text() != payload:
    raise SystemExit('FAIL: lemma receipt differs from complete recomputation')
print(payload)

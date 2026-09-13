#!/usr/bin/env python3
"""Independent direct-binomial audit; bounded checks are not the proof."""
from math import comb, gcd, isqrt
from pathlib import Path
from collections import Counter
import hashlib
import json
import random
import sys

ROOT = Path(__file__).parent
rng = random.Random(699)
cases = {(i, j, 2) for j in range(3, 421) for i in range(2, j)}
cases |= {(i, j, 3) for j in range(5, 421) for i in range(4, j, 2)}
for _ in range(1500):
    j = rng.randrange(421, 1601)
    i = rng.randrange(2, min(j, 701))
    d = rng.choice([2, 3]) if i >= 4 and i % 2 == 0 else 2
    cases.add((i, j, d))
limit = max(2*j+d for i, j, d in cases)
sieve = bytearray(b'\1') * (limit+1)
sieve[:2] = b'\0\0'
for p in range(2, isqrt(limit)+1):
    if sieve[p]:
        sieve[p*p::p] = b'\0' * (((limit-p*p)//p)+1)
primes = [p for p in range(2, limit+1) if sieve[p]]

def factorial_v(n, p):
    a = 0
    while n:
        n //= p
        a += n
    return a

def binomial_v(n, k, p):
    return factorial_v(n, p)-factorial_v(k, p)-factorial_v(n-k, p)

def absent(n, i, j):
    X, Y = comb(n, i), comb(n, j)
    out = []
    for p in primes:
        if p > n:
            break
        if p < i or X % p or Y % p == 0:
            continue
        a, v = 0, X
        while v % p == 0:
            a += 1
            v //= p
        assert a == binomial_v(n, i, p)
        assert binomial_v(n, j, p) == 0
        M = p ** (a + int(p == i))
        r, s = j % M, (n-j) % M
        assert r+s < i, (n, i, j, p, a, M, r, s)
        out.append((p, a, M, r, s))
    return X, Y, out

counts = Counter()
digest = hashlib.sha256()
# An independent general-n check of the inherited lifted lemma.
for n in range(6, 121):
    for i in range(2, n//2):
        for j in range(i+1, n//2+1):
            _, _, contributions = absent(n, i, j)
            counts['general_localization_triples'] += 1
            counts['general_absent_prime_powers'] += len(contributions)
            counts['general_boundary_prime_powers'] += sum(p == i for p, *_ in contributions)

for i, j, d in sorted(cases):
    n = 2*j+d
    X, Y, contributions = absent(n, i, j)
    W = 1
    wraps = []
    h = (i-d+1)//2
    B = comb(j, h)
    for p, a, M, r, s in contributions:
        W *= p**a
        E = d+r-s
        assert E % M == 0
        assert d-i+1 <= E <= d+i-1
        if E:
            wraps.append((p, a, r, s))
        else:
            assert 2*r+d < i and 0 <= r < h
            assert B % (p**a) == 0
        counts['line_absent_prime_powers'] += 1
        counts['line_boundary_prime_powers'] += p == i
        counts['line_higher_exponents'] += a >= 2
    counts[f'd{d}_triples'] += 1
    theorem = d == 2 or j != 2*i-1
    if not wraps:
        assert B % W == 0
        assert W*W <= B*B <= comb(2*j, 2*h) <= X
        counts[f'd{d}_nonwrap'] += 1
    else:
        assert len(wraps) == 1
        p, a, r, s = wraps[0]
        assert i % 2 == 0 and p == i+1 and a == 1
        assert (r, s) == (p-d, 0)
        A = i//2
        k = (j+d)//p
        assert j == k*p-d and k >= 2
        C = comb(j+1, A)
        U = W//p
        g = gcd(A, j+1)
        assert gcd(U, A) == 1
        assert B % U == C % U == 0
        assert A*gcd(B, C) == B*g
        assert g == gcd(A, k+1-d)
        if d == 2 or k >= 3:
            assert p*g < j+1
            assert W <= p*gcd(B, C) < C
            assert C*C < comb(2*j+2, i) <= X
        else:
            assert d == 3 and k == 2 and j == 2*i-1
            counts['excluded_diagonal_wraps'] += 1
        counts[f'd{d}_wrap'] += 1
    G = gcd(X, Y)
    common = next((p for p in primes if i <= p <= n and G % p == 0), None)
    if theorem:
        assert common is not None, (n, i, j)
        counts['claimed_theorem_triples'] += 1
    else:
        counts['excluded_diagonal_triples'] += 1
        counts['excluded_diagonal_with_common_prime'] += common is not None
    digest.update(json.dumps([i, j, d, W, wraps, common], separators=(',', ':')).encode()+b'\n')

expected = {(8,3), (9,4), (10,5), (12,5), (21,7), (21,8),
            (30,7), (33,13), (33,14), (36,13), (36,17), (56,13)}
found = set()
for n in range(4, 121):
    for i in range(2, n//2+1):
        X = comb(n, i)
        V = 1
        for p in primes:
            if p > n:
                break
            if p >= i:
                V *= p ** binomial_v(n, i, p)
        if X >= V*V:
            found.add((n, i))
assert found == expected, (found, expected)
exceptions = []
for n, i in sorted(expected):
    for d in (2, 3):
        if (n-d) % 2:
            continue
        j = (n-d)//2
        if not 2 <= i < j:
            continue
        if d == 3 and not(i >= 4 and i % 2 == 0 and j != 2*i-1):
            continue
        p = next(p for p in primes if i <= p <= n and comb(n, i) % p == comb(n, j) % p == 0)
        exceptions.append({'n': n, 'i': i, 'j': j, 'd': d, 'common_prime': p})
assert len(exceptions) == 5
report = {
    'passed': True,
    'counts': dict(sorted(counts.items())),
    'domain': {'exhaustive_j_max': 420, 'exhaustive_i': '2<=i<j; d=3 only even i>=4',
               'extra_draws': 1500, 'seed': 699, 'extra_j': [421,1600], 'extra_i_max': 700,
               'unique_line_triples': len(cases), 'general_localization_n_max': 120,
               'EEES_exception_check_n_max': 120},
    'line_records_sha256': digest.hexdigest(),
    'EEES_admissible_exceptions': exceptions,
    'scope': 'Independent exact finite checks; does not establish infinite claims or novelty.'
}
print(json.dumps(report, indent=2))
if '--emit' in sys.argv:
    with (ROOT/'independent-receipt.json').open('x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')

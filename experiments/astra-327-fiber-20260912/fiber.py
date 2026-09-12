"""Multiplier-sensitive density transfer for P327 (exact integers)."""
from fractions import Fraction
from functools import lru_cache
from math import gcd, isqrt, prod


def _integer(value, minimum=1):
    if type(value) is not int or value < minimum:
        raise ValueError('expected an integer >= %d' % minimum)


def _parameters(P, L, d=None):
    _integer(L)
    if not isinstance(P, (list, tuple)):
        raise ValueError('P must be a sorted list/tuple of distinct primes')
    for p in P:
        _integer(p, 2)
        if any(p % q == 0 for q in range(2, isqrt(p) + 1)):
            raise ValueError('P contains a non-prime')
    if list(P) != sorted(set(P)) or gcd(prod(P), L) != 1:
        raise ValueError('P must be sorted and distinct; L must be coprime to P')
    if d is not None:
        _integer(d)
        if L % d:
            raise ValueError('state d must divide L')


def activation_modulus(a, b, k=1):
    """ma+mb divides k*(ma)*(mb) iff the returned modulus divides m."""
    for v in (a,b,k):
        _integer(v)
    if a == b:
        raise ValueError('pair entries must be distinct')
    return (a + b) // gcd(a + b, k * a * b)


def _prime_divisors(n):
    factors = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            factors.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        factors.append(n)
    return factors


def state_count(N, P, L, d):
    """Count m<=N coprime to P with gcd(m,L)=d, by inclusion-exclusion."""
    _integer(N, 0)
    _parameters(P,L,d)
    terms = [(1, 1)]
    for p in _prime_divisors(prod(P) * (L // d)):
        terms += [(divisor * p, -sign) for divisor, sign in terms]
    return sum(sign * (N // (d * divisor)) for divisor, sign in terms)


def _smooth_numbers(P, cutoff):
    values = {1}
    for p in P:
        old = sorted(values)
        for a in old:
            b = a * p
            while b <= cutoff:
                values.add(b)
                b *= p
    return sorted(values)


def _prefix_independent_sets(S, edges):
    """Exact include/exclude recurrence; a witness for every prefix."""
    positions = {v: i for i, v in enumerate(S)}
    adjacent = [0] * len(S)
    for a, b in edges:
        i, j = positions[a], positions[b]
        adjacent[i] |= 1 << j
        adjacent[j] |= 1 << i

    @lru_cache(None)
    def solve(mask):
        if not mask:
            return ()
        bit = mask & -mask
        i = bit.bit_length() - 1
        rest = mask ^ bit
        no = solve(rest)
        yes = (S[i],) + solve(rest & ~adjacent[i])
        return max((no, yes), key=lambda t: (len(t), t))

    return [list(solve((1 << i) - 1)) for i in range(1, len(S) + 1)]


def finite_bound(N, result):
    """All-N upper bound; callers obtain result from analyze()."""
    _integer(N, 0)
    S = result['smooth']
    return N - sum(e * state_count(N // c, result['P'], result['L'], row['d'])
                   for row in result['states'] for e,c in zip(row['delta'],S))


def analyze(P, L, cutoff, k=1):
    _parameters(P,L)
    _integer(cutoff)
    _integer(k)
    if cutoff > 10000 or L > 10000:
        raise ValueError('demo cap: cutoff and L must be <= 10000')
    S = _smooth_numbers(P, cutoff)
    if len(S) > 18:
        raise ValueError('demo cap: at most 18 smooth vertices')
    rows = []
    coefficient = Fraction(1)
    for d in range(1, L + 1):
        if L % d:
            continue
        edges = [[a,b] for i,a in enumerate(S) for b in S[i+1:]
                 if d % activation_modulus(a,b,k) == 0]
        witnesses = _prefix_independent_sets(S, edges)
        alpha = [len(w) for w in witnesses]
        deficits = [0] + [i-b for i,b in enumerate(alpha,1)]
        delta = [b-a for a,b in zip(deficits,deficits[1:])]
        weight = state_weight(P,L,d)
        coefficient -= weight * sum(Fraction(e,c) for e,c in zip(delta,S))
        rows.append({'d': d, 'weight': weight, 'edges': edges,
                     'alpha': alpha, 'delta': delta, 'witnesses': witnesses})
    return {'P': list(P), 'L': L, 'cutoff': cutoff, 'k': k,
            'smooth': S, 'states': rows, 'coefficient': coefficient}


def state_weight(P, L, d):
    """Natural density of this state among all positive integers."""
    _parameters(P,L,d)
    return Fraction(1, d) * prod(Fraction(p - 1, p)
                                for p in _prime_divisors(prod(P) * (L // d)))

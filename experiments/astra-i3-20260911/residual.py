#!/usr/bin/env python3
"""i=3 residual: coprime-to-j! cancellation and the o|P list."""
import math


def odd_part(x):
    x = abs(int(x))
    while x % 2 == 0 and x:
        x //= 2
    return x


def cancel(d, n, j):
    """True iff d|C(n,3), gcd(d, j!)=1, j>=3, which implies d|C(n,j)."""
    if j < 3 or j > n or d <= 0:
        return False
    if math.comb(n, 3) % d != 0:
        return False
    if math.gcd(d, math.factorial(j)) != 1:
        return False
    return math.comb(n, j) % d == 0


def op_divides_P(n_min, n_max):
    hits = []
    for n in range(n_min, n_max):
        o = odd_part(math.comb(n, 3))
        if o <= 1:
            continue
        for j in range(4, n // 2 + 1):
            if j * (j - 1) * (j - 2) % o == 0:
                hits.append((n, j))
    return hits


def _is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def twice_prime_hits(p_min, p_max):
    """o|P pairs among n=2p, p prime in [p_min, p_max)."""
    hits = []
    for p in range(p_min, p_max):
        if not _is_prime(p):
            continue
        n = 2 * p
        if n < 8:
            continue
        o = odd_part(math.comb(n, 3))
        m = n // 2
        for j in range(4, m + 1):
            if j * (j - 1) * (j - 2) % o == 0:
                hits.append((n, j))
    return hits

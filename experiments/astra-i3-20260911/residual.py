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

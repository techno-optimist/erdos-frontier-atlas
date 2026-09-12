#!/usr/bin/env python3
"""Type B2b leftover is structural, not another p-band scan.

Even n, 3 doesn't divide n-1 ⇒ n-1 divides C(n,3). Then o|P forces n-1|P.
Not a solution of #699.
"""
import math


def n_minus_1_divides_binom3(n):
    n = int(n)
    if n < 6 or n % 2 or (n - 1) % 3 == 0:
        return False
    return math.comb(n, 3) % (n - 1) == 0


def leftover_class(n):
    n = int(n)
    if n % 2 == 0 and (n - 1) % 3 == 0:
        return 'three_divides_n_minus_1'
    if n % 2 == 0:
        return 'n_minus_1_divides_C'
    return 'odd_n'


def is_prime_power(m):
    m = int(m)
    if m < 2:
        return False
    # strip one prime
    x = m
    p = 2
    while p * p <= x:
        if x % p == 0:
            while x % p == 0:
                x //= p
            return x == 1
        p += 1 if p == 2 else 2
    return True  # remaining x is prime


def oP_hits(n):
    from typeA import odd_part_binom3
    n = int(n)
    o = odd_part_binom3(n)
    hits = []
    m = n // 2
    for j in range(4, m + 1):
        if j * (j - 1) * (j - 2) % o == 0:
            hits.append(j)
    return hits

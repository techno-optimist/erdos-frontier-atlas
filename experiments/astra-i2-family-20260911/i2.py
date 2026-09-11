#!/usr/bin/env python3
"""Exact arithmetic for the P699 i=2, n=2j+3 family."""
import math


def min_prime_divisor(n):
    if n < 2:
        raise ValueError('no prime divisor')
    if n % 2 == 0:
        return 2
    f = 3
    while f * f <= n:
        if n % f == 0:
            return f
        f += 2
    return n


def modulus(n, k, p):
    return math.comb(n, k) % p


def erdos699_i2_witness(j):
    if j < 3:
        raise ValueError('need j >= 3 so that 2 < j <= n/2')
    n = 2 * j + 3
    g = math.gcd(n, j)
    m = n // g
    p = min_prime_divisor(m)
    return {'j': j, 'n': n, 'g': g, 'm': m, 'prime': p}

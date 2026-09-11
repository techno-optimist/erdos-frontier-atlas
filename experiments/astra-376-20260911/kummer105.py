#!/usr/bin/env python3
"""Kummer form of Erdős #376: gcd(C(2n,n), 105)=1 iff restricted digits in bases 3,5,7.

Not a solution of #376 (infinitude remains open).
"""
import math


def digits_base(n, b):
    n = int(n)
    if n == 0:
        return [0]
    out = []
    while n:
        out.append(n % b)
        n //= b
    return out


def digits_ok(n):
    """No carry when adding n+n in bases 3,5,7: digits < p/2."""
    n = int(n)
    if n < 0:
        return False
    return (
        all(d <= 1 for d in digits_base(n, 3))
        and all(d <= 2 for d in digits_base(n, 5))
        and all(d <= 3 for d in digits_base(n, 7))
    )


def coprime_105(n):
    n = int(n)
    if n < 0:
        return False
    return math.gcd(math.comb(2 * n, n), 105) == 1


def enumerate_below(limit):
    return [n for n in range(int(limit)) if digits_ok(n)]

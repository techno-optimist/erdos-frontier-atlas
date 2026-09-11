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


def search_base3(max_digits):
    """All n whose base-3 digits are in {0,1} with at most max_digits, and digits_ok.

    Completeness: every such n < 3**max_digits is visited exactly once.
    """
    max_digits = int(max_digits)
    if max_digits < 0:
        return []
    pow3 = [3 ** i for i in range(max_digits)]
    hits = []
    limit = 1 << max_digits
    for mask in range(limit):
        n = 0
        m = mask
        i = 0
        while m:
            if m & 1:
                n += pow3[i]
            m >>= 1
            i += 1
        if digits_ok(n):
            hits.append(n)
    hits.sort()
    return hits

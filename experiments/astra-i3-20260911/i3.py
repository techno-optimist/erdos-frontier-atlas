#!/usr/bin/env python3
"""Exact arithmetic for the i=3 slice of P699."""
import math


def identity(n, j):
    """Return 0 iff j(j-1)(j-2)C(n,j) = n(n-1)(n-2)C(n-3,j-3)."""
    return (
        j * (j - 1) * (j - 2) * math.comb(n, j)
        - n * (n - 1) * (n - 2) * math.comb(n - 3, j - 3)
    )


def binom3_gt(n, j):
    return math.comb(n, 3) > j * (j - 1) * (j - 2)


def gcd_both(n, j):
    return math.gcd(math.comb(n, 3), math.comb(n, j))


def binom3_odd(n):
    return math.comb(n, 3) % 2 == 1

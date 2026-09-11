#!/usr/bin/env python3
"""Exact arithmetic for the complete i=2 case of P699."""
import math


def identity(n, j):
    """Return 0 iff j(j-1)C(n,j) = n(n-1)C(n-2,j-2)."""
    return j * (j - 1) * math.comb(n, j) - n * (n - 1) * math.comb(n - 2, j - 2)


def binom2_gt(n, j):
    return math.comb(n, 2) > j * (j - 1)


def gcd_both(n, j):
    return math.gcd(math.comb(n, 2), math.comb(n, j))

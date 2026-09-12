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

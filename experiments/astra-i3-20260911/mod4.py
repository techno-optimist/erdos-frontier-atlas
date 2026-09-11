#!/usr/bin/env python3
"""n ≡ 3 (mod 4): C(n,3) is odd and exceeds falling_max, so o never divides P."""
import math

from typeA import odd_part_binom3


def falling_max(n):
    m = n // 2
    return m * (m - 1) * (m - 2)


def size_gap_poly(t):
    """4t^2 + 22t + 3. Positive for t ≥ 1, hence C(4t+3,3) > falling_max(4t+3)."""
    return 4 * t * t + 22 * t + 3


def o_divides_P_hits_mod4(n_min, n_max):
    hits = []
    n = n_min if n_min % 4 == 3 else n_min + (3 - n_min % 4)
    if n % 4 != 3:
        n += 4
    while n < n_max:
        o = odd_part_binom3(n)
        m = n // 2
        for j in range(4, m + 1):
            if j * (j - 1) * (j - 2) % o == 0:
                hits.append((n, j))
        n += 4
    return hits

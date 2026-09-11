#!/usr/bin/env python3
"""Type B1: n/6 < P+(o) <= n/4, so 4p <= n < 6p and j near p or 2p."""
from typeA import (
    all_composite_triple,
    odd_part_binom3,
    primes,
    pstar,
)


def typeB1_hits(n_min, n_max):
    hits = []
    for n in range(n_min, n_max):
        if n < 8 or not all_composite_triple(n):
            continue
        o = odd_part_binom3(n)
        p = pstar(n)
        if not (n / 6 < p <= n / 4):
            continue
        m = n // 2
        for j in (p, p + 1, p + 2, 2 * p, 2 * p + 1, 2 * p + 2):
            if 4 <= j <= m and j * (j - 1) * (j - 2) % o == 0:
                hits.append((n, j))
    return hits


_FAMILIES = {
    '4p': lambda p: 4 * p,
    '4p+1': lambda p: 4 * p + 1,
    '4p+2': lambda p: 4 * p + 2,
    '5p': lambda p: 5 * p,
    '5p+1': lambda p: 5 * p + 1,
    '5p+2': lambda p: 5 * p + 2,
}


def family_hits(name, p_min, p_max):
    fn = _FAMILIES[name]
    hits = []
    for p in primes(p_max):
        if p < p_min:
            continue
        n = fn(p)
        if n < 8 or not all_composite_triple(n):
            continue
        o = odd_part_binom3(n)
        m = n // 2
        for j in range(4, m + 1):
            if j * (j - 1) * (j - 2) % o == 0:
                hits.append((n, j))
    return hits

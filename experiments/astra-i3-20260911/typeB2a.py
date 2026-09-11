#!/usr/bin/env python3
"""Type B2a: n/8 < P+(o) <= n/6, so 6p <= n < 8p and j near p, 2p, or 3p."""
from typeA import all_composite_triple, odd_part_binom3, primes, pstar


def typeB2a_hits(n_min, n_max):
    hits = []
    for n in range(n_min, n_max):
        if n < 8 or not all_composite_triple(n):
            continue
        o = odd_part_binom3(n)
        p = pstar(n)
        if not (n / 8 < p <= n / 6):
            continue
        m = n // 2
        for k in (1, 2, 3):
            for r in (0, 1, 2):
                j = k * p + r
                if 4 <= j <= m and j * (j - 1) * (j - 2) % o == 0:
                    hits.append((n, j))
    return hits


_FAMILIES = {
    '6p': lambda p: 6 * p,
    '6p+1': lambda p: 6 * p + 1,
    '6p+2': lambda p: 6 * p + 2,
    '7p': lambda p: 7 * p,
    '7p+1': lambda p: 7 * p + 1,
    '7p+2': lambda p: 7 * p + 2,
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

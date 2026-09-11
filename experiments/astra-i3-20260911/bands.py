#!/usr/bin/env python3
"""p-bands: n = m p, m p+1, m p+2 with p = P+(odd_part(C(n,3)))."""
from typeA import all_composite_triple, odd_part_binom3, primes, pstar


def family_m_hits(m, p_min, p_max):
    hits = []
    for p in primes(p_max):
        if p < p_min:
            continue
        for r in (0, 1, 2):
            n = m * p + r
            if n < 8 or not all_composite_triple(n):
                continue
            o = odd_part_binom3(n)
            half = n // 2
            for j in range(4, half + 1):
                if j * (j - 1) * (j - 2) % o == 0:
                    hits.append((n, j))
    return hits


def band_hits(m_lo, m_hi, n_min, n_max):
    """Hits with m_lo * p <= n < m_hi * p, i.e. n/m_hi < p <= n/m_lo."""
    hits = []
    for n in range(n_min, n_max):
        if n < 8 or not all_composite_triple(n):
            continue
        o = odd_part_binom3(n)
        p = pstar(n)
        if p <= 0:
            continue
        if not (m_lo * p <= n < m_hi * p):
            continue
        half = n // 2
        tmax = half // p
        for t in range(1, tmax + 1):
            for r in (0, 1, 2):
                j = t * p + r
                if 4 <= j <= half and j * (j - 1) * (j - 2) % o == 0:
                    hits.append((n, j))
    return hits

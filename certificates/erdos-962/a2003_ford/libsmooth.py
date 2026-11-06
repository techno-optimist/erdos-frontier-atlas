"""Clean-room 2003-smooth helpers for A327909 a(2003). No atlas search code."""
from __future__ import annotations

def primes_upto(n: int) -> list[int]:
    s = bytearray(b"\x01") * (n + 1)
    s[0:2] = b"\x00\x00"
    r = int(n ** 0.5)
    for i in range(2, r + 1):
        if s[i]:
            s[i * i :: i] = bytearray(len(s[i * i :: i]))
    return [i for i in range(n + 1) if s[i]]

def is_m_smooth(k: int, primes: list[int], m: int) -> bool:
    """True iff k is m-smooth (all prime factors <= m). primes must include all p<=m."""
    if k == 0:
        return False
    k = abs(k)
    if k == 1:
        return True
    for p in primes:
        if p > m:
            break
        while k % p == 0:
            k //= p
        if k == 1:
            return True
        if p * p > k:
            break
    return k == 1 or k <= m

def gpf_trial(k: int, primes: list[int]) -> int:
    """Greatest prime factor via trial division; primes should cover sqrt(k) or we handle cofactor."""
    if k <= 1:
        return k
    g = 1
    n = k
    for p in primes:
        if p * p > n:
            break
        if n % p == 0:
            g = p
            while n % p == 0:
                n //= p
    if n > 1:
        g = n  # n prime or prime > primes[-1]
    return g

def mark_smooth_segment(L: int, R: int, primes: list[int], m: int) -> bytearray:
    """Return bytearray smooth[0:R-L] where smooth[i]=1 iff L+i is m-smooth.
    Uses divide-out against a mutable copy of each value (segmented)."""
    N = R - L
    # val[i] starts as L+i; divide out p<=m; smooth iff ends at 1
    val = [L + i for i in range(N)]
    for p in primes:
        if p > m:
            break
        # first multiple of p in [L,R)
        r = L % p
        start = 0 if r == 0 else p - r
        for i in range(start, N, p):
            while val[i] % p == 0:
                val[i] //= p
    out = bytearray(N)
    for i, v in enumerate(val):
        out[i] = 1 if v == 1 else 0
    return out

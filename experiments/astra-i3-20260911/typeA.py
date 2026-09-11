#!/usr/bin/env python3
"""Type A: P+(odd_part(C(n,3))) > n/4, so j in {p,p+1,p+2}."""
import math


def odd_part(x):
    x = abs(int(x))
    while x % 2 == 0 and x:
        x //= 2
    return x


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def primes(limit):
    if limit < 3:
        return []
    s = bytearray(b'\x01') * limit
    s[0:2] = b'\x00\x00'
    for i in range(2, int(limit ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = b'\x00' * ((limit - 1 - i * i) // i + 1)
    return [i for i in range(2, limit) if s[i]]


def pmax_odd(n):
    x = odd_part(n)
    last = 1
    p = 3
    while p * p <= x:
        while x % p == 0:
            last = p
            x //= p
        p += 2
    if x > 1:
        last = x
    return last


def odd_part_binom3(n):
    return odd_part(math.comb(n, 3))


def pstar(n):
    return max(pmax_odd(n), pmax_odd(n - 1), pmax_odd(n - 2))


def all_composite_triple(n):
    return not any(is_prime(x) and x > 3 for x in (n - 2, n - 1, n))


def typeA_hits(n_min, n_max):
    hits = []
    for n in range(n_min, n_max):
        if n < 8 or not all_composite_triple(n):
            continue
        o = odd_part_binom3(n)
        p = pstar(n)
        if p <= n / 4:
            continue
        m = n // 2
        for j in (p, p + 1, p + 2):
            if 4 <= j <= m and j * (j - 1) * (j - 2) % o == 0:
                hits.append((n, j))
    return hits


_FAMILIES = {
    '2p': lambda p: 2 * p,
    '2p+1': lambda p: 2 * p + 1,
    '2p+2': lambda p: 2 * p + 2,
    '3p': lambda p: 3 * p,
    '3p+1': lambda p: 3 * p + 1,
    '3p+2': lambda p: 3 * p + 2,
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

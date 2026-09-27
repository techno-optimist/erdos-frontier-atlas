"""Gaps between consecutive integers coprime to a primorial -- reference implementation.

For P = p_1 p_2 ... p_n, an even gap t = 2m OCCURS iff some x has x and x + t
coprime to P and every x + j (0 < j < t) sharing a prime with P.  Write c_p for
the residue with x = -c_p (mod p); then p divides x + j iff j = c_p (mod p), so
t occurs iff residues with c_p != 0 and c_p != t (mod p) cover 1..t-1.  By CRT
every residue choice is realised by some x.

The prime 2 must take the odd positions (c_2 = 1), so what remains is to cover
the even positions j = 2k, k = 1..m-1, by the odd primes: p covers 2k iff
k = d_p (mod p), d_p = c_p / 2 (mod p), with d_p != 0 and d_p != m (mod p).
The search branches on the uncovered k with the fewest candidate primes, and
prunes when the best-case coverage of the unassigned primes is too small.
"""
from math import gcd, prod


def primes(n):
    out, k = [], 2
    while len(out) < n:
        if all(k % p for p in out if p * p <= k):
            out.append(k)
        k += 1
    return out


class Cover:
    """Exhaustive covering search for one (n, t); mirrors gapsc2.c node for node."""

    def __init__(self, n, t):
        assert t % 2 == 0 and t >= 4
        self.qs = primes(n)[1:]            # odd primes
        self.m = t // 2
        self.full = sum(1 << k for k in range(1, self.m))
        self.cl = [[sum(1 << k for k in range(d, self.m, q) if k >= 1) for d in range(q)]
                   for q in self.qs]
        self.used = [False] * len(self.qs)
        self.asg = [None] * len(self.qs)
        self.nodes = 0

    def run(self):
        return self._dfs(0)

    def _dfs(self, cov):
        self.nodes += 1
        m, qs = self.m, self.qs
        unc = self.full & ~cov
        if not unc:
            return True
        need = bin(unc).count("1")
        capsum = 0
        for i, q in enumerate(qs):
            if self.used[i]:
                continue
            best = 0
            for d in range(1, q):
                if d == m % q:
                    continue
                c = bin(self.cl[i][d] & unc).count("1")
                if c > best:
                    best = c
            capsum += best
        if capsum < need:
            return False
        bestk, bestc = -1, None
        for k in range(1, m):
            if not (unc >> k) & 1:
                continue
            c = sum(1 for i, q in enumerate(qs)
                    if not self.used[i] and k % q != 0 and k % q != m % q)
            if bestc is None or c < bestc:
                bestc, bestk = c, k
                if c == 0:
                    return False
        k = bestk
        for i, q in enumerate(qs):
            if self.used[i]:
                continue
            d = k % q
            if d == 0 or d == m % q:
                continue
            self.used[i], self.asg[i] = True, d
            if self._dfs(cov | self.cl[i][d]):
                return True
            self.used[i] = False
        return False

    def residues(self):
        """{p: c_p} for the covering found; primes the search left free are absent."""
        out = {2: 1}
        for q, u, d in zip(self.qs, self.used, self.asg):
            if u:
                out[q] = (2 * d) % q
        return out


def realise(n, t, residues):
    """An explicit x for a covering: CRT over the first n primes, with x = -c_p
    (mod p); primes the covering leaves free take the least allowed c_p.
    Returns x with 0 < x < P."""
    ps = primes(n)
    P = prod(ps)
    x = 0
    for p in ps:
        c = residues.get(p)
        if c is None:
            c = next(c for c in range(1, p) if c != t % p)
        r = (-c) % p
        mp = P // p
        x = (x + r * mp * pow(mp, -1, p)) % P
    return x


def is_gap(n, x, t):
    """Direct check, independent of any search: x and x + t are coprime to P and
    every integer strictly between them shares a prime with P."""
    P = prod(primes(n))
    return (gcd(x, P) == 1 and gcd(x + t, P) == 1
            and all(gcd(x + j, P) > 1 for j in range(1, t)))

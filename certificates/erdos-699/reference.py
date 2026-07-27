#!/usr/bin/env python3
"""Erdős #699 — reference implementation and proof-checking of the pruning.

Question: for every 1 <= i < j <= n/2, is there a prime p >= i with
p | gcd(C(n,i), C(n,j))?

This file is the slow, obviously-correct oracle: it decides the property by
direct big-integer gcd and factorisation, with no number theory at all. The
fast sweep uses Kummer's theorem plus a prime-gap pruning; this file exists to
prove those are the same predicate on every n it can reach.

  python3 -I reference.py 200        # decide n = 3..200 by brute force
  python3 -I reference.py --prove    # check the pruning lemma computationally
"""
import sys
from math import comb, gcd


def factorize(m):
    f, d = {}, 2
    while d * d <= m:
        while m % d == 0:
            f[d] = f.get(d, 0) + 1
            m //= d
        d += 1 if d == 2 else 2
    if m > 1:
        f[m] = f.get(m, 0) + 1
    return f


def holds_bruteforce(n):
    """Decide the property for n, by gcd and factorisation. Returns None if it
    holds, else the first counterexample triple (n, i, j)."""
    half = n // 2
    for i in range(1, half + 1):
        ci = comb(n, i)
        for j in range(i + 1, half + 1):
            g = gcd(ci, comb(n, j))
            if not any(p >= i for p in factorize(g)):
                return (n, i, j)
    return None


# --------------------------------------------------------------- Kummer -----
def divides_binom(p, n, k):
    """Kummer: p | C(n,k) iff adding k and n-k in base p produces a carry."""
    a, b, carry = k, n - k, 0
    while a or b:
        if a % p + b % p + carry >= p:
            return True
        carry = 1 if (a % p + b % p + carry) >= p else 0
        a //= p
        b //= p
    return False


def prevprime(n):
    def isp(m):
        if m < 2:
            return False
        if m % 2 == 0:
            return m == 2
        d = 3
        while d * d <= m:
            if m % d == 0:
                return False
            d += 2
        return True
    m = n
    while m > 1:
        if isp(m):
            return m
        m -= 1
    return 1


def prove_pruning(nmax=400):
    """THE LOAD-BEARING LEMMA.

    Claim: if some prime p satisfies n-i < p <= n, then p divides both C(n,i)
    and C(n,j) for every j with i < j <= n/2, and p >= i — so the triple is
    satisfied and nothing about (n,i) needs checking.

    Why: p > n-i >= n/2 (as i <= n/2), so p > n/2 >= j > i, giving p >= i.
    Also j < p and n-j < n-i < p, so adding j and (n-j) in base p is a
    one-digit addition whose sum is n >= p — a carry. Same for i. Kummer then
    gives p | C(n,i) and p | C(n,j).

    Consequence: a counterexample needs NO prime in (n-i, n], i.e.
    i <= n - prevprime(n) — the prime gap below n, which is tiny.

    This function checks the claim exhaustively rather than trusting the prose.
    """
    bad = 0
    for n in range(4, nmax + 1):
        half = n // 2
        for i in range(1, half + 1):
            # is there a prime in (n-i, n]?
            pp = prevprime(n)
            if pp <= n - i:
                continue                     # no such prime; lemma says nothing
            p = pp
            if p < i:
                print(f"LEMMA FAILS (p<i): n={n} i={i} p={p}")
                bad += 1
                continue
            if not divides_binom(p, n, i):
                print(f"LEMMA FAILS (p does not divide C(n,i)): n={n} i={i} p={p}")
                bad += 1
                continue
            for j in range(i + 1, half + 1):
                if not divides_binom(p, n, j):
                    print(f"LEMMA FAILS (C(n,j)): n={n} i={i} j={j} p={p}")
                    bad += 1
                    break
    return bad


def main():
    if "--prove" in sys.argv[1:]:
        nmax = 400
        print(f"checking the prime-gap lemma exhaustively for n <= {nmax}")
        bad = prove_pruning(nmax)
        print("LEMMA HOLDS on every (n,i) checked" if bad == 0
              else f"LEMMA BROKEN in {bad} cases")
        # and Kummer against direct factorisation
        mism = 0
        for n in range(2, 60):
            for k in range(n + 1):
                fs = factorize(comb(n, k)) if comb(n, k) > 1 else {}
                for p in (2, 3, 5, 7, 11, 13):
                    if divides_binom(p, n, k) != (p in fs):
                        mism += 1
        print(f"Kummer vs direct factorisation: {mism} mismatches")
        raise SystemExit(0 if bad == 0 and mism == 0 else 1)

    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    ce = []
    for n in range(4, nmax + 1):
        r = holds_bruteforce(n)
        if r:
            ce.append(r)
            print(f"COUNTEREXAMPLE {r}")
    print(f"# brute-forced n=4..{nmax}: {len(ce)} counterexamples")


if __name__ == "__main__":
    main()

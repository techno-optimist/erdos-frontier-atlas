#!/usr/bin/env python3
"""Structured search for i = 3 near-counterexamples of Erdős #699 beyond brute force.

  python3 -I structured.py [NMAX] [--jobs J]   # default NMAX 1e12 (seconds); the result does not depend on J

By the reduction (README), a pair (n, j) that satisfies (*) for every odd prime of C(n,3) has
4 | n, n = 2KA with K = 2^(a-1) * 3^eps, (2KA-1)(2KA-2) <= (4/sqrt 3) K^3, j = A*m with
1 <= m < K, and with B = (n-1)/3^[3||n-1], C = (n-2)/(2*3^[3||n-2]):
    every prime power of B divides m or 2K - m,
    every prime power of C divides m, K - m or 2K - m.
For every such "special" n <= NMAX this enumerates the 2^w(B) splits of B by the Chinese
remainder theorem, keeps each m in [1, K), and tests C.  It first validates that enumeration
against direct enumeration of every m on all special n <= 2e5.  Exit 0 iff no pair with j > 3
passes; the only passes are the trivial j = 1 at n = 2^a and 3 * 2^a.
"""
import math
import pathlib
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import product

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import position as P  # noqa: E402

SMALL = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)


def is_prime(n):
    """Deterministic Miller-Rabin for n < 3.3e24."""
    if n < 2:
        return False
    for p in SMALL:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def rho(n, rng):
    while True:
        c = rng.randrange(1, n)
        x = y = rng.randrange(2, n)
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d


def factor(n, rng=random.Random(699)):
    out = {}
    for p in SMALL:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
    stack = [n] if n > 1 else []
    while stack:
        x = stack.pop()
        if is_prime(x):
            out[x] = out.get(x, 0) + 1
        else:
            d = rho(x, rng)
            stack += [d, x // d]
    return out


def prime_powers(x):
    """Odd prime powers exactly dividing x, dropping a lone factor 3."""
    return [q ** e for q, e in factor(x).items() if q != 2 and not (q == 3 and e == 1)]


def crt(pairs):
    r0, m0 = 0, 1
    for r, m in pairs:
        t = ((r - r0) * pow(m0, -1, m)) % m
        r0, m0 = r0 + m0 * t, m0 * m
    return r0 % m0, m0


def within(K, A):
    """(2KA-1)(2KA-2) <= (4/sqrt 3) K^3, in exact integers: 3 L^2 <= 16 K^6."""
    L = (2 * K * A - 1) * (2 * K * A - 2)
    return 3 * L * L <= 16 * K ** 6


def special(nmax):
    """All n = 2KA <= nmax with 4 | n and (2KA-1)(2KA-2) <= (4/sqrt3) K^3."""
    a = 2
    while 2 ** a <= nmax:
        for eps in (0, 1):
            K = 2 ** (a - 1) * 3 ** eps
            A = 1
            while 2 * K * A <= nmax and within(K, A):
                if not (A % 3 == 0 and (eps == 1 or A % 9 != 0)) and 2 * K * A >= 8:
                    yield 2 * K * A, K, A
                A += 2
        a += 1


def candidates(n, K, A):
    """All m in [1, K) passing the B- and C-conditions, via CRT over the splits of B."""
    Bq = prime_powers(n - 1)
    Cq = prime_powers((n - 2) // 2)
    out = []
    for choice in product((0, 1), repeat=len(Bq)):
        m0, Mb = crt([(0 if c == 0 else (2 * K) % M, M) for c, M in zip(choice, Bq)])
        m = m0 if m0 > 0 else Mb
        while m < K:
            if all(m % M == 0 or (K - m) % M == 0 or (2 * K - m) % M == 0 for M in Cq):
                out.append(m)
            m += Mb
    return sorted(set(out)), Bq, Cq


def passes_on(chunk):
    """[(n, j)] for the special n in chunk; module level so it runs in a worker process."""
    return [(n, A * m) for n, K, A in chunk for m in candidates(n, K, A)[0]]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--jobs")]
    jobs = next((int(a.split("=", 1)[1]) for a in sys.argv[1:] if a.startswith("--jobs=")), 1)
    nmax = int(float(args[0])) if args else 10 ** 12
    # validation: CRT enumeration == direct enumeration on every special n <= 2e5
    checked = 0
    for n, K, A in special(200000):
        ms, Bq, Cq = candidates(n, K, A)
        direct = [m for m in range(1, K)
                  if all(m % M == 0 or (2 * K - m) % M == 0 for M in Bq)
                  and all(m % M == 0 or (K - m) % M == 0 or (2 * K - m) % M == 0 for M in Cq)]
        assert ms == direct, (n, ms, direct)
        assert all(P.passes(n, A * m) for m in ms), n   # agrees with the definition of (*)
        checked += 1
    print(f"CRT enumeration equals direct enumeration on all {checked} special n <= 2e5")
    todo = list(special(nmax))
    count = len(todo)
    chunks = [todo[i:i + 2000] for i in range(0, count, 2000)]
    if jobs > 1:
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            results = list(ex.map(passes_on, chunks))
    else:
        results = [passes_on(c) for c in chunks]
    trivial, found = [], []
    for res in results:
        for n, j in res:
            (trivial if j <= 3 else found).append((n, j))
    assert all(j == 1 and n in (2 ** ((n & -n).bit_length() - 1), 3 * 2 ** ((n & -n).bit_length() - 1))
               for n, j in trivial), trivial[:5]
    print(f"special n <= {nmax:.3g}: {count}; pairs with j > 3 passing (*): {len(found)}; "
          f"trivial j = 1 passes: {len(trivial)}")
    assert found == [], found[:10]
    print("all checks passed")


if __name__ == "__main__":
    main()

"""Exact number theory for the briefcase: primality, factoring, CRT, Kummer carries.

Everything here is integer arithmetic; there are no floats anywhere.
- `is_prime` is proven correct for n < 3.3e24: Miller-Rabin with the first 13 prime bases is
  deterministic there (Sorenson-Webster).
- Above that, `is_prime` is the Baillie-PSW test. BPSW has no known counterexample, but it is
  not a proof. `PROVEN_PRIME_BOUND` marks the line, and callers that need a proof must stay
  below it.
"""
import math
import random

PROVEN_PRIME_BOUND = 3317044064679887385961981
_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)


def primes_upto(n):
    """All primes <= n (sieve of Eratosthenes)."""
    if n < 2:
        return []
    sieve = bytearray([1]) * (n + 1)
    sieve[0] = sieve[1] = 0
    for p in range(2, math.isqrt(n) + 1):
        if sieve[p]:
            sieve[p * p::p] = bytearray(len(range(p * p, n + 1, p)))
    return [p for p in range(n + 1) if sieve[p]]


SMALL_PRIMES = tuple(primes_upto(1000))
_SMALL_SET = frozenset(SMALL_PRIMES)


def _strong_probable_prime(n, a):
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    x = pow(a, d, n)
    if x in (1, n - 1):
        return True
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1:
            return True
    return False


def _jacobi(a, n):
    a %= n
    result = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    return result if n == 1 else 0


def _strong_lucas_probable_prime(n):
    """Strong Lucas test with Selfridge's parameters (method A)."""
    if math.isqrt(n) ** 2 == n:
        return False
    D = 5
    while _jacobi(D, n) != -1:
        D = -D - 2 if D > 0 else -D + 2
    P, Q = 1, (1 - D) // 4
    d, s = n + 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    # binary Lucas chain for U_d, V_d
    U, V, Qk = 0, 2, 1
    inv2 = (n + 1) // 2
    for bit in bin(d)[2:]:
        U, V, Qk = U * V % n, (V * V - 2 * Qk) % n, Qk * Qk % n
        if bit == "1":
            U, V = (P * U + V) * inv2 % n, (D * U + P * V) * inv2 % n
            Qk = Qk * Q % n
    if U == 0 or V == 0:
        return True
    for _ in range(s - 1):
        V = (V * V - 2 * Qk) % n
        Qk = Qk * Qk % n
        if V == 0:
            return True
    return False


def is_prime(n):
    """Primality: a proof below PROVEN_PRIME_BOUND, Baillie-PSW above it."""
    if n < 2:
        return False
    if n in _SMALL_SET:
        return True
    for p in SMALL_PRIMES[:25]:
        if n % p == 0:
            return False
    if n < PROVEN_PRIME_BOUND:
        return all(_strong_probable_prime(n, a) for a in _MR_BASES)
    return _strong_probable_prime(n, 2) and _strong_lucas_probable_prime(n)


def _brent(n, rng):
    """A nontrivial factor of the odd composite n (Brent's variant of Pollard rho)."""
    while True:
        y, c, m = rng.randrange(1, n), rng.randrange(1, n), 128
        g = r = q = 1
        x = ys = y
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = math.gcd(q, n)
                k += m
            r *= 2
        if g == n:
            g = 1
            while g == 1:
                ys = (ys * ys + c) % n
                g = math.gcd(abs(x - ys), n)
        if g != n:
            return g


def factor(n, rng=None):
    """{prime: exponent} for n >= 1. Exact whenever every prime found is < PROVEN_PRIME_BOUND."""
    if n < 1:
        raise ValueError("factor() needs n >= 1")
    rng = rng or random.Random(699)
    out = {}
    for p in SMALL_PRIMES:
        if p * p > n:
            break
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
    stack = [n] if n > 1 else []
    while stack:
        x = stack.pop()
        if is_prime(x):
            out[x] = out.get(x, 0) + 1
            continue
        r = math.isqrt(x)
        if r * r == x:
            stack += [r, r]
            continue
        d = _brent(x, rng)
        stack += [d, x // d]
    return dict(sorted(out.items()))


def valuation(x, p):
    """v_p(x) for x != 0."""
    if x == 0:
        raise ValueError("valuation of 0")
    v = 0
    while x % p == 0:
        x //= p
        v += 1
    return v


def crt(pairs):
    """(r, M) with r = r_k mod m_k for pairwise coprime moduli; r in [0, M)."""
    r0, m0 = 0, 1
    for r, m in pairs:
        t = ((r - r0) * pow(m0, -1, m)) % m
        r0, m0 = r0 + m0 * t, m0 * m
    return r0 % m0, m0


def carries(a, b, p):
    """Number of carries when adding a and b in base p. By Kummer this is v_p(C(a+b, a))."""
    c = count = 0
    while a or b or c:
        s = a % p + b % p + c
        c = 1 if s >= p else 0
        count += c
        a //= p
        b //= p
    return count


def v_binom(n, k, p):
    """v_p(C(n, k)) for 0 <= k <= n, by Kummer's theorem."""
    if not 0 <= k <= n:
        raise ValueError("need 0 <= k <= n")
    return carries(k, n - k, p)


def smooth_rough(x, i, fac=None):
    """Split x >= 1 as S * R for the prime threshold i >= 2.

    R collects the prime powers q^e || x that can divide C(n, i) when x = n - t with t < i:
    q > i, or q = i with e >= 2 (C(n, i) loses one factor i to i!). S is the rest: primes
    below i, and a lone factor i.
    """
    fac = factor(x) if fac is None else fac
    R = 1
    for q, e in fac.items():
        if q > i or (q == i and e >= 2):
            R *= q ** e
    return x // R, R


def is_smooth(x, i):
    """True when x >= 1 has no prime factor above i and at most a lone factor i (x = S, R = 1)."""
    if x < 1:
        raise ValueError("is_smooth needs x >= 1")
    for p in primes_upto(i):
        e = 0
        while x % p == 0:
            x //= p
            e += 1
        if p == i and e >= 2:
            return False
    return x == 1


def smooth_numbers(i, limit):
    """Sorted list of all S <= limit with R = 1 in `smooth_rough(S, i)`."""
    ps = primes_upto(i)
    out = [1]
    for p in ps:
        cap = 1 if p == i else None
        new = []
        for s in out:
            x, e = s * p, 1
            while x <= limit and (cap is None or e <= cap):
                new.append(x)
                x *= p
                e += 1
        out += new
    return sorted(out)

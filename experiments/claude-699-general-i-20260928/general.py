"""Positional localization for Erdős #699 at every i >= 3: the reference search.

A triple (n, i, j) with i < j <= n/2 is a counterexample when no prime p >= i divides both
C(n, i) and C(n, j). Notation (README): n - t = S_t * R_t for 0 <= t < i, where R_t holds the
prime powers q^e || n - t with q > i, or q = i and e >= 2, and S_t is the rest.

For a counterexample with j < n/2:
  (a) R_0 | j; write j = R_0 * m with 1 <= m < S_0 / 2.
  (b) R_t | P_t(m) := prod_{r=0..t} (t*m - r*S_0) for 1 <= t < i.
  (c) 4 (n - 1) <= S_0^2 S_1.
  (d) 108 ((n-1)(n-2))^2 <= (S_0^3 S_1 S_2)^2.
For j = n/2 (central): n - 1 is smooth (R_1 = 1).

`search(i, X)` visits every "special" n <= X, meaning (c) and (d) hold, and every central
candidate n (n - 1 smooth, n even). For each special n it finds all m in [1, S_0/2) with
R_1 | P_1(m) and R_2 | P_2(m), then keeps those that also satisfy R_t | P_t(m) for
3 <= t < i. Every survivor j = R_0 m is finally tested exactly for a common prime (Kummer).
"""
import math
from itertools import product

import nt


def smooth_primes(i):
    return nt.primes_upto(i)


def smooth_part(x, i, primes):
    """S in x = S * R (see module docstring), by trial division by the primes <= i."""
    s = 1
    for p in primes:
        if x % p == 0:
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            if not (p == i and e >= 2):
                s *= p ** e
    return s


def blocks(n, i):
    """[(M, t, p)]: every prime p >= i dividing C(n, i), its position t and M = p^v_p(n-t)."""
    out = []
    for t in range(i):
        for p, e in nt.factor(n - t).items():
            if p > i or (p == i and e >= 2):
                out.append((p ** e, t, p))
    return out


def passes(n, j, blk):
    """(*) for every block: j mod M <= t."""
    return all(j % M <= t for M, t, _ in blk)


def common_prime(n, j, blk):
    """Least prime p >= i dividing both C(n, i) and C(n, j), or None (exact, Kummer)."""
    for p in sorted(p for _, _, p in blk):
        if nt.carries(j, n - j, p):
            return p
    return None


def cond_c(n, S0, S1):
    return 4 * (n - 1) <= S0 * S0 * S1


def cond_d(n, S0, S1, S2):
    L = (n - 1) * (n - 2)
    return 108 * L * L <= (S0 ** 3 * S1 * S2) ** 2


def P(t, m, S0):
    out = 1
    for r in range(t + 1):
        out *= t * m - r * S0
    return out


def special_numbers(i, X):
    """Every n in [2i+2, X] with S_0 >= 2, (c) and (d): an (S_0, S_1)-progression scan."""
    primes = smooth_primes(i)
    SM = nt.smooth_numbers(i, X)
    for S0 in SM:
        if S0 < 2:
            continue
        for S1 in SM:
            if S1 > X:
                break
            if math.gcd(S0, S1) != 1:
                continue
            top = min(X, S0 * S0 * S1 // 4 + 1)
            r, L = nt.crt([(0, S0), (1, S1)])
            n = r if r > 0 else L
            while n <= top:
                if (n >= 2 * i + 2 and smooth_part(n, i, primes) == S0
                        and smooth_part(n - 1, i, primes) == S1):
                    S2 = smooth_part(n - 2, i, primes)
                    if cond_d(n, S0, S1, S2):
                        yield n, S0, S1, S2
                n += L


def central_numbers(i, X):
    """Every even n in [2i+2, X] with n - 1 smooth: the only n that can fail at j = n/2."""
    for s in nt.smooth_numbers(i, X - 1):
        n = s + 1
        if n % 2 == 0 and n >= 2 * i + 2:
            yield n


def residue_options(M, t, S0):
    """m mod M allowed by one block at position t >= 1: t*m = r*S_0 (mod M) for some r <= t."""
    inv = pow(t, -1, M)
    return sorted({(r * S0 * inv) % M for r in range(t + 1)})


def prime_powers(x):
    return [p ** e for p, e in nt.factor(x).items()]


def m_candidates(S0, blocks12):
    """All m in [1, S0/2) meeting the (M, t) blocks, via CRT; blocks in descending M."""
    hi = (S0 - 1) // 2
    use = sorted(blocks12, reverse=True)
    k, W = 0, 1
    while k < len(use) and W <= hi:
        W *= use[k][0]
        k += 1
    head, tail = use[:k], use[k:]
    out = set()
    opts = [residue_options(M, t, S0) for M, t in head]
    mods = [M for M, _ in head]
    tail_ok = [(M, t, set(residue_options(M, t, S0))) for M, t in tail]
    for choice in product(*opts):
        r, W = nt.crt(list(zip(choice, mods)))
        m = r if r > 0 else W
        while m <= hi:
            if all(m % M in ok for M, t, ok in tail_ok):
                out.add(m)
            m += W
    return sorted(out)


def examine_special(n, i, S0, S1, S2, primes, tmax):
    """(number of m passing t = 1, 2; survivors [(j, common prime or None)]).

    Positions 3..tmax are then required by divisibility (tmax = i - 1 is the real condition)."""
    R0 = n // S0
    R1, R2 = (n - 1) // S1, (n - 2) // S2
    blk = [(M, 1) for M in prime_powers(R1)] + [(M, 2) for M in prime_powers(R2)]
    ms = m_candidates(S0, blk)
    surv = []
    for m in ms:
        ok = True
        for t in range(3, tmax + 1):
            Rt = (n - t) // smooth_part(n - t, i, primes)
            if P(t, m, S0) % Rt:
                ok = False
                break
        if ok:
            j = R0 * m
            if j > i:
                full = blocks(n, i)
                assert passes(n, j, [b for b in full if b[1] <= tmax]), (n, j)
                surv.append((j, common_prime(n, j, full)))
    return len(ms), surv


MASK = (1 << 64) - 1


def splitmix64(x):
    z = (x + 0x9E3779B97F4A7C15) & MASK
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return z ^ (z >> 31)


def search(i, X, tmax=None):
    """Stats and survivors for the i-slice up to X (see module docstring).

    tmax < i - 1 relaxes (*) to the positions t <= tmax: a negative control."""
    tmax = i - 1 if tmax is None else tmax
    primes = smooth_primes(i)
    count = cand12 = checksum = 0
    survivors = []
    for n, S0, S1, S2 in special_numbers(i, X):
        count += 1
        checksum = (checksum + splitmix64(n)) & MASK
        c, s = examine_special(n, i, S0, S1, S2, primes, tmax)
        cand12 += c
        survivors += [(n, j, p) for j, p in s]
    central = 0
    for n in central_numbers(i, X):
        central += 1
        full = blocks(n, i)
        j = n // 2
        if passes(n, j, [b for b in full if b[1] <= tmax]):
            survivors.append((n, j, common_prime(n, j, full)))
    return {"i": i, "X": X, "special": count, "checksum": checksum,
            "cand12": cand12, "central": central, "survivors": sorted(survivors)}

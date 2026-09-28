"""Positional localization for the i = 3 slice of Erdős #699 (shared helpers).

For an odd prime q dividing C(n,3), let t in {0,1,2} be the position with q | n - t and
M = q^{v_q(n-t)}.  (q = 3 divides C(n,3) only when v_3(n-t) >= 2.)  If q does not divide
C(n,j), Kummer's theorem gives no carry out of the low block, so
    (j mod M) + ((n - j) mod M) = t.                                   (*)
A pair (n, j) with 3 < j <= n/2 and no odd prime dividing both C(n,3) and C(n,j) must satisfy
(*) for EVERY odd prime q | C(n,3).  `passes` tests exactly that necessary condition.
"""
import math


def factor(x):
    """Prime factorization of x >= 1 (trial division; for the small ranges used here)."""
    f, d = {}, 2
    while d * d <= x:
        while x % d == 0:
            f[d] = f.get(d, 0) + 1
            x //= d
        d += 1 if d == 2 else 2
    if x > 1:
        f[x] = f.get(x, 0) + 1
    return f


def blocks(n, factorize=factor):
    """[(M, t)]: M = q^{v_q(n-t)} for every odd prime q | C(n,3), t its position."""
    out = []
    for t in range(3):
        for q, e in factorize(n - t).items():
            if q == 2 or (q == 3 and e == 1):
                continue
            out.append((q ** e, t))
    return out


def passes(n, j, blk=None):
    """The positional necessary condition (*) for every odd prime of C(n,3)."""
    blk = blocks(n) if blk is None else blk
    return all((j % M) + ((n - j) % M) == t for M, t in blk)


def passes_position_blind(n, j):
    """The weaker condition used before: odd_part(C(n,3)) divides j(j-1)(j-2)."""
    c = math.comb(n, 3)
    while c % 2 == 0:
        c //= 2
    return (j * (j - 1) * (j - 2)) % c == 0


def shape(n):
    """(a, eps, A, K) with n = 2^a * 3^eps * A, eps = [3 || n], K = 2^(a-1) * 3^eps."""
    a = (n & -n).bit_length() - 1
    odd = n >> a
    eps = 1 if odd % 3 == 0 and odd % 9 != 0 else 0
    A = odd // 3 ** eps
    return a, eps, A, (2 ** (a - 1) * 3 ** eps if a >= 1 else None)


def in_reduction(n):
    """The reduction's conclusion: 4 | n and (2KA-1)(2KA-2) <= (4/sqrt 3) K^3."""
    a, eps, A, K = shape(n)
    L = (2 * K * A - 1) * (2 * K * A - 2) if a >= 1 else 0
    return a >= 2 and 3 * L * L <= 16 * K ** 6

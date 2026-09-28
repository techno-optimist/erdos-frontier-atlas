#!/usr/bin/env python3
"""Exact small-n checks for the general-i positional reduction of Erdős #699 (README).

  python3 -I check_small.py        # about 30 s

1. The lemma, straight from binomial coefficients (i = 3..8, n < 400).
2. Theorem 2 on every pair that passes (*) at positions t <= 1 or t <= 2 (i = 3..10, n <= 2500).
3. The CRT candidates equal direct enumeration on every special n <= 2e5 (i = 3..10).
4. (b) is (*) itself: R_t | P_t(m) exactly when j = R_0 m passes (*) at every block of position
   t, for every m < S_0/2 and every position, on every special n <= 12000 (i = 4..10).
5. No pair with n <= 3000 and 3 <= i <= 10 passes (*) at every position.
6. Negative control: at positions t <= 2 only, pairs do pass, and the search reproduces the
   brute-force list exactly.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import general as G  # noqa: E402
import nt  # noqa: E402


def lemma():
    inst = 0
    for i in range(3, 9):
        for n in range(2 * i + 2, 400):
            blk = G.blocks(n, i)
            ps = sorted(p for p in nt.factor(math.comb(n, i)) if p >= i)
            assert ps == sorted(p for _, _, p in blk), (n, i)
            for j in range(i + 1, n // 2 + 1):
                cj = math.comb(n, j)
                for M, t, p in blk:
                    if cj % p:
                        inst += 1
                        assert (j % M) + ((n - j) % M) == t, (n, i, j, M, t)
    print(f"1. lemma: {inst} instances (p >= i dividing C(n,i) but not C(n,j)), all satisfy (*)")


def theorem2():
    tot1 = tot2 = cen = 0
    for i in range(3, 11):
        primes = G.smooth_primes(i)
        special = {n: s for n, *s in G.special_numbers(i, 2500)}
        for n in range(2 * i + 2, 2501):
            blk = G.blocks(n, i)
            S = [G.smooth_part(n - t, i, primes) for t in range(i)]
            R = [(n - t) // S[t] for t in range(i)]
            for j in range(i + 1, n // 2 + 1):
                if not G.passes(n, j, [b for b in blk if b[1] <= 1]):
                    continue
                tot1 += 1
                assert j % R[0] == 0 and 1 <= j // R[0] <= S[0] // 2           # (a)
                m = j // R[0]
                assert G.P(1, m, S[0]) % R[1] == 0                                # (b), t = 1
                assert G.cond_c(n, S[0], S[1])                                    # (c)
                if 2 * j == n:
                    cen += 1
                    assert R[1] == 1                                              # (e), t = 1
                    odd = [t for t in range(3, i, 2) if G.passes(n, j, [b for b in blk if b[1] == t])]
                    assert all(R[t] == 1 for t in odd)                            # (e)
                    continue
                if not G.passes(n, j, [b for b in blk if b[1] <= 2]):
                    continue
                tot2 += 1
                assert G.P(2, m, S[0]) % R[2] == 0                                # (b), t = 2
                assert G.cond_d(n, S[0], S[1], S[2]) and n in special             # (d)
    print(f"2. theorem 2: {tot1} pairs pass (*) at t <= 1 ({cen} central), {tot2} non-central pass "
          f"t <= 2; (a)-(e) hold for all")


def candidates():
    checked = 0
    for i in range(3, 11):
        for n, S0, S1, S2 in G.special_numbers(i, 200000):
            R1, R2 = (n - 1) // S1, (n - 2) // S2
            blk = [(M, 1) for M in G.prime_powers(R1)] + [(M, 2) for M in G.prime_powers(R2)]
            direct = [m for m in range(1, (S0 + 1) // 2)
                      if G.P(1, m, S0) % R1 == 0 and G.P(2, m, S0) % R2 == 0]
            assert G.m_candidates(S0, blk) == direct, (i, n)
            checked += 1
    print(f"3. CRT candidates equal direct enumeration on all {checked} (i, special n <= 2e5)")


def divisibility_is_position():
    cases = 0
    for i in range(4, 11):
        primes = G.smooth_primes(i)
        for n, S0, S1, S2 in G.special_numbers(i, 12000):
            blk = G.blocks(n, i)
            R0 = n // S0
            Rt = [(n - t) // G.smooth_part(n - t, i, primes) for t in range(i)]
            for m in range(1, (S0 + 1) // 2):
                j = R0 * m
                for t in range(1, i):
                    a = G.P(t, m, S0) % Rt[t] == 0
                    b = G.passes(n, j, [x for x in blk if x[1] == t])
                    assert a == b, (i, n, m, t)
                    cases += 1
    print(f"4. (b) agrees with (*) position by position in {cases} cases")


def no_pass():
    for i in range(3, 11):
        for n in range(2 * i + 2, 3001):
            blk = G.blocks(n, i)
            assert not any(G.passes(n, j, blk) for j in range(i + 1, n // 2 + 1)), (i, n)
    print("5. no pair with n <= 3000, 3 <= i <= 10 passes (*) at every position")


def negative_control():
    rows = []
    for i in range(4, 11):
        brute = []
        for n in range(2 * i + 2, 3001):
            blk = G.blocks(n, i)
            low = [b for b in blk if b[1] <= 2]
            brute += [(n, j, G.common_prime(n, j, blk)) for j in range(i + 1, n // 2 + 1) if G.passes(n, j, low)]
        got = G.search(i, 3000, tmax=2)["survivors"]
        assert sorted(brute) == got, i
        assert all(p is not None for _, _, p in got)
        rows.append(len(got))
    assert all(r > 0 for r in rows)
    print(f"6. negative control: at positions t <= 2 only, {sum(rows)} pairs pass for i = 4..10 "
          f"(each has a common prime); the search reproduces the brute-force list exactly")


if __name__ == "__main__":
    lemma()
    theorem2()
    candidates()
    divisibility_is_position()
    no_pass()
    negative_control()
    print("all checks passed")

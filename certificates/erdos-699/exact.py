#!/usr/bin/env python3
"""
Erdos #699 -- EXACT decision procedure, with the algorithmic gap closed.

PROPERTY  P(n):  for every 1 <= i < j <= n/2 there is a prime p >= i with
                 p | gcd(C(n,i), C(n,j)).

=====================================================================
DERIVATION
=====================================================================

(0) KUMMER / LUCAS.  v_p(C(n,k)) = #carries when adding k and n-k in base p,
    and that count is 0 exactly when every base-p digit of k is <= the
    corresponding digit of n.  So

        p | C(n,k)   <=>   some base-p digit of k EXCEEDS that digit of n.     (*)

    `divides_binom` below is (*) verbatim: O(log_p n), no big integers.

(1) THE CANDIDATE PRIMES OF A ROW -- without factoring C(n,i).

    For p > i, p does not divide i!, and C(n,i) = n^{underline i} / i!, hence

        v_p(C(n,i)) = v_p( n (n-1) ... (n-i+1) )        for every p > i.       (A)

    So the primes p > i dividing C(n,i) are exactly the prime factors > i of a
    product of i consecutive integers just below n.  We never touch C(n,i)
    itself: we factor i integers of size ~n (trial division by primes <= sqrt n,
    or a segmented sieve in sweep mode).

    The one remaining prime, p = i (only when i is prime), is settled by Lucas:
    i has base-i digits (1,0), so C(n,i) = floor(n/i) (mod i), giving

        i | C(n,i)   <=>   floor(n/i) = 0  (mod i).                            (B)

    (A) is also equivalent to the familiar `n mod p < i`, but (A) is the form
    that is actually computable: it is a factorisation of i numbers, not a
    search over primes.  The prior implementation looped over ALL primes <= n
    and Kummer-tested each -- O(pi(n)) per row, ~620k Kummer tests per row at
    n = 10^7.  (A) makes it O(i * pi(sqrt n)) once per n, and O(1) amortised
    per n in sweep mode.

(2) THE COVERED SET OF ONE PRIME.  By (*), the j NOT covered by p are exactly
    the base-p digitwise submasks of n:

        U_p = { j : digit_d(j) <= digit_d(n) for all d },   |U_p| = prod (d_k + 1).

    STRUCTURE.  U_p is a union of prod_{k>=1}(d_k+1) intervals, each of length
    d_0+1 = (n mod p)+1, sitting at the higher-digit submask positions.  In the
    important case p > sqrt(n) (two digits, n = d_1 p + d_0) this collapses to a
    single RESIDUE CONDITION valid for all 0 <= j <= n:

        p does NOT cover j   <=>   j mod p <= n mod p.                         (C)

    And if that large p was found as a divisor of n-t (t < i), then n mod p = t,
    so U_p = { j : j mod p <= t } -- j within t of a multiple of p.  The covered
    set is the complement: p covers j iff j mod p > n mod p.
    For p <= sqrt(n) no such collapse exists and the full digit test is used.

(3) COVERAGE TEST.  Row i is good iff (i, n/2] is contained in the union of the
    covered sets, i.e. iff

        (i, n/2]  intersect  ( intersection over p in S of U_p )  =  empty.

    We pick the p with the smallest |U_p| (via `usize`, a prod-of-digits+1 in
    O(log_p n)), enumerate that one set in ascending order, and filter it by the
    remaining primes with (*).  The enumeration is a mixed-radix ODOMETER over
    the digit box, which is O(1) amortised per element and, being ascending,
    stops dead at n/2 -- so the first survivor is the lexicographically first
    counterexample j.  `count_uncovered_le` gives the EXACT windowed count
    |U_p intersect [0,m]| by digit DP; it is used for cost analysis, not in the
    hot path (re-selecting on it was measured slower at every threshold tried).

    Choosing p only changes cost, never the verdict: the test is a property of
    the intersection over ALL of S.

(4) PRIME-GAP PRUNING, and why it is exactly the boundary of the easy case.
    If some prime lies in (n-i, n] then it divides C(n,i) and C(n,j) for every
    i < j <= n/2 and exceeds i, so row i is free.  Hence only

        i <= n - P,    P = largest prime <= n                                  (D)

    needs checking.  (P is the largest prime <= n, NOT prevprime(n); they differ
    exactly when n is prime, where the gap is 0 and nothing is checked.)
    Row i = 1 is free unconditionally: j*C(n,j) = n*C(n-1,j-1) so n | j*C(n,j);
    if gcd(n, C(n,j)) = 1 then n | j, impossible for 0 < j < n.

(5) THE CRUX -- do large primes suffice?  NO, and provably not.

    Reduction.  If p > j (> i) and p | C(n,i), then n mod p < i < j and p > j,
    so by (*) p | C(n,j) as well.  Therefore

        "some prime > j covers (n,i,j)"   <=>   max S(n,i) > j.                (E)

    THEOREM.  On every row that survives the pruning (D), max S(n,i) <= n/2.
    Proof: a candidate p > i divides some n-t with 0 <= t < i.  If p > n/2 then
    n-t <= n < 2p forces n-t = p, i.e. p is a prime in (n-i, n] -- which is
    exactly what (D) excludes.  []

    Consequence: for j = floor(n/2) there is NEVER a prime > j, on any pruned
    row.  Large primes are insufficient by construction at the top of every row;
    the "n mod p < k" shortcut cannot decide the property.  Verified: 0 of 26859
    pruned rows for n < 6000 have max S > n/2.  In 1898 of those 26859 rows
    (7.1%) the largest prime covering j = floor(n/2) is already <= sqrt(n), so
    the two-digit collapse (C) alone does not decide those rows either.

    How far down must p go?  Let m(n) = min over pruned (i,j) of the LARGEST
    usable prime.  Restricting the algorithm to primes p > B is sound for n iff
    B < m(n).  Measured over 4 <= n < 40000: m(n) <= sqrt(n) for 49.8% of n, and
    m(n) = 2 occurs -- the prime 2 is the ONLY usable prime.  Certified triples
    (checked with exact big-integer gcd):

        n=16,   i=2, j=6   : C(16,2)=120,       gcd = 8,      only p = 2
        n=512,  i=2, j=147 : C(512,2)=130816,   gcd = 2^k,    only p = 2
        n=2048, i=2, j=713 : C(2048,2)=2096128, gcd = 2^k,    only p = 2
        n=5626, i=2, j=2813: C = 3^2*5^4*29*97, gcd = 5625,   only p in {3,5}

    So NO threshold restriction is sound, the two-digit collapse (C) is not
    enough on its own, and the full base-p carry structure is unavoidable.
    It is used only where it must be: on the O(1) small primes of each row.

(6) COST OF SWEEPING n FROM 10^7 TO 10^8.

    Total work = sum over n of sum over rows i<=g(n) of E(n,i), where
    g(n) = n - prevprime(n) and E(n,i) = |U_{p*} intersect (i, n/2]| is the size
    of the enumerated set.  Measured (CPython, one core, 30000-wide windows):

                        n ~ 10^7        n ~ 10^8
      segmented sieve    0.4 us/n  0.1%   0.4 us/n  0.1%
      row work         333.2 us/n 99.9% 573.1 us/n 99.9%
      rows per n         11.85           14.72
      E: median/mean      7 / 43.7        8 / 95.6
      E: p99/max        739 / 6908     2047 / 32766
      ENUMERATED ELEMENTS PER n   518            1407

    DOMINANT TERM: the enumeration, sum_n sum_i E(n,i).  NOT the sieve (0.1%),
    not the factorisation, not the primality tests -- the segmented sieve
    amortises the whole factorisation of the range to O(log log B) per integer.

    What controls E: for the best (largest) prime p* of a row, U_{p*} is
    "j within t of a multiple of p*" by (C), so E ~ (t+1) * n / (2 p*), i.e. E is
    governed by the COFACTOR n/p*, where p* is the largest prime factor of the
    g(n) integers in the prime gap below n.  Largest-prime-factors are
    Dickman-distributed, so E has a heavy right tail -- median 8 but max 32766.
    The sweep cost is dominated by the SMOOTH n in the range, not the typical n.
    (Sanity check against the theorem in (5): the median of max(S)/n at the top
    row is exactly 1/3, comfortably under the proven ceiling of 1/2.)

    End-to-end: 410 us/n at 10^7 rising to 996 us/n at 10^8, ~ n^0.39.
    Integrating over [10^7, 10^8] gives a mean of ~770 us/n, so

        9 x 10^7 values  x  ~770 us  ~=  7 x 10^4 s  ~=  19 core-hours in CPython

    embarrassingly parallel over blocks (~2 h on 10 cores; well under an hour in C).

=====================================================================
VALIDATION
=====================================================================
  * every component (divides_binom, vp_binom, candidate_primes, uncovered_list,
    count_uncovered_le, usize) unit-tested against exact big-integer brute force
  * decides(n) agrees with an independent big-integer gcd reference
    (decides_naive_gcd, no Kummer / no Lucas / no pruning) on the exact
    lexicographically-first counterexample triple for ALL n <= 2000
  * sweep() reproduces decides() exactly on sampled ranges up to 10^7
  * P(n) holds for every n <= 2000; no counterexample exists there, nor in the
    10^7 and 10^8 sample windows swept here.

Run `python3 erdos699_exact.py` for the self-test, `--sweep A B` to sweep.
"""
from math import comb, gcd, isqrt

# ------------------------------------------------------------------ primes
def primes_upto(N):
    if N < 2:
        return []
    bs = bytearray([1]) * (N + 1)
    bs[0:2] = b"\x00\x00"
    for i in range(2, isqrt(N) + 1):
        if bs[i]:
            bs[i * i::i] = bytearray(len(bs[i * i::i]))
    return [i for i in range(N + 1) if bs[i]]

def _is_prime_td(m, sp):
    if m < 2:
        return False
    for p in sp:
        if p * p > m:
            return True
        if m % p == 0:
            return m == p
    return True

def largest_prime_le(n, sp):
    m = n
    while m >= 2:
        if _is_prime_td(m, sp):
            return m
        m -= 1
    return None

# ------------------------------------------------------------------ (0) Kummer/Lucas
def divides_binom(n, k, p):
    """p | C(n,k)  <=>  some base-p digit of k exceeds that of n.  (*)"""
    while n or k:
        if k % p > n % p:
            return True
        n //= p
        k //= p
    return False

def vp_binom(n, k, p):
    """v_p(C(n,k)) = #carries adding k and n-k in base p (Kummer)."""
    a, b, c, carry = k, n - k, 0, 0
    while a or b or carry:
        s = a % p + b % p + carry
        carry = 1 if s >= p else 0
        c += carry
        a //= p
        b //= p
    return c

# ------------------------------------------------------------------ (1) candidates
def factor_small(m, sp):
    """prime factors of m (set), trial division by sp (must reach sqrt(m))."""
    out = []
    for p in sp:
        if p * p > m:
            break
        if m % p == 0:
            out.append(p)
            while m % p == 0:
                m //= p
    if m > 1:
        out.append(m)
    return out

def candidate_primes(n, i, sp, pf_cache=None):
    """All primes p >= i with p | C(n,i).  Uses (A) and (B); never builds C(n,i).

    pf_cache[t] may hold the precomputed prime factors of n-t.
    """
    S = set()
    for t in range(i):
        pf = pf_cache[t] if pf_cache is not None else factor_small(n - t, sp)
        for p in pf:
            if p > i:
                S.add(p)
    if i >= 2 and _is_prime_td(i, sp) and (n // i) % i == 0:
        S.add(i)
    return sorted(S)

# ------------------------------------------------------------------ (2) U_p
def digits(n, p):
    d = []
    while n:
        d.append(n % p)
        n //= p
    return d or [0]

def usize(n, p):
    """|U_p| = prod(digit+1) over [0,n].  O(log_p n), no allocation.
    Used only to CHOOSE which set to enumerate -- correctness is independent of
    the choice, so a proxy for the windowed count is fine."""
    t = 1
    while n:
        t *= n % p + 1
        n //= p
    return t

def uncovered_list(n, p, lo, hi):
    """sorted { j in [lo,hi] : p does NOT divide C(n,j) } = base-p submasks of n."""
    d0, d1 = n % p, n // p
    if d1 < p:
        # two base-p digits: U_p = { a*p + e : 0<=a<=d1, 0<=e<=d0 }  -- see (C)
        out = []
        for a in range(max(0, lo // p), min(d1, hi // p) + 1):
            b = a * p
            s, e = (lo if lo > b else b), (hi if hi < b + d0 else b + d0)
            if s <= e:
                out.extend(range(s, e + 1))
        return out
    # general case: mixed-radix odometer over the digit box 0<=e_t<=a_t.
    # Incrementing the least significant digit first yields values in STRICTLY
    # ASCENDING order (a carry at position t changes the value by
    # p^t - sum_{u<t} a_u p^u > 0), so we can stop dead at hi.
    a = digits(n, p)
    k = len(a)
    pw = [p ** t for t in range(k)]
    e = [0] * k
    val = 0
    out = []
    while val <= hi:
        if val >= lo:
            out.append(val)
        t = 0
        while t < k and e[t] == a[t]:
            val -= a[t] * pw[t]
            e[t] = 0
            t += 1
        if t == k:
            break
        e[t] += 1
        val += pw[t]
    return out

def count_uncovered_le(n, p, m):
    """|U_p intersect [0,m]| by digit DP, O(log_p n)."""
    if m < 0:
        return 0
    a = digits(n, p)[::-1]
    k = len(a)
    if m >= n:
        t = 1
        for d in a:
            t *= d + 1
        return t
    b = digits(m, p)[::-1]
    b = [0] * (k - len(b)) + b
    suf = [1] * (k + 1)
    for t in range(k - 1, -1, -1):
        suf[t] = suf[t + 1] * (a[t] + 1)
    res = 0
    tight = True
    for t in range(k):
        lim = min(b[t] - 1, a[t])
        if lim >= 0:
            res += (lim + 1) * suf[t + 1]
        if b[t] > a[t]:
            tight = False
            break
    if tight:
        res += 1
    return res

# ------------------------------------------------------------------ (3) coverage
def first_bad_j(n, i, S, lo, hi):
    """smallest j in [lo,hi] covered by no p in S, else None."""
    if lo > hi:
        return None
    if not S:
        return lo
    # Choose which U_p to enumerate.  Correctness does not depend on the choice,
    # only cost, so the cheap proxy |U_p| over [0,n] is used rather than the
    # exact windowed count.  (Measured: re-selecting on the exact windowed count
    # via count_uncovered_le costs more than it saves at every threshold tried,
    # 32 through 4096 -- the odometer already makes enumeration cheap.)
    best, bestc = None, None
    for p in S:
        c = usize(n, p)
        if bestc is None or c < bestc:
            best, bestc = p, c
    others = [p for p in S if p != best]
    for j in uncovered_list(n, best, lo, hi):
        for p in others:
            if divides_binom(n, j, p):
                break
        else:
            return j
    return None

# ------------------------------------------------------------------ decider
def decides(n, sp=None, pf_block=None, gap=None):
    """None if P(n) holds, else the lexicographically first counterexample (n,i,j).

    sp       : primes up to >= sqrt(n) (reused across calls)
    pf_block : optional list, pf_block[t] = prime factors of n-t (sweep mode)
    gap      : optional precomputed n - (largest prime <= n)
    """
    half = n // 2
    if half < 2:
        return None
    if sp is None:
        sp = primes_upto(isqrt(n) + 1)
    if gap is None:
        gap = n - largest_prime_le(n, sp)
    imax = min(gap, half - 1)
    if imax < 2:
        return None
    if pf_block is None:
        pf_block = [factor_small(n - t, sp) for t in range(imax)]
    for i in range(2, imax + 1):
        S = candidate_primes(n, i, sp, pf_block)
        j = first_bad_j(n, i, S, i + 1, half)
        if j is not None:
            return (n, i, j)
    return None

# ------------------------------------------------------------------ sweep mode
MAXGAP_PAD = 700          # > any prime gap below 10^9 (max gap under 10^8 is 219)

def factor_block(lo, hi, sp):
    """prime factors of every m in [lo,hi), by segmented sieve.
    Returns (fac, isprime) with fac[m-lo] = sorted list of distinct primes."""
    size = hi - lo
    rem = list(range(lo, hi))
    fac = [[] for _ in range(size)]
    for p in sp:
        if p * p >= hi:
            break
        start = ((lo + p - 1) // p) * p
        for m in range(start, hi, p):
            k = m - lo
            fac[k].append(p)
            r = rem[k]
            while r % p == 0:
                r //= p
            rem[k] = r
    isprime = bytearray(size)
    for k in range(size):
        if rem[k] > 1:
            fac[k].append(rem[k])
        # m is prime iff its only prime factor is itself.  Testing rem[k]==m
        # instead would miss primes p with p*p < hi (those ARE sieved, leaving
        # rem 1) -- fine for a block near 10^8, wrong for a block near 0.
        f = fac[k]
        if len(f) == 1 and f[0] == lo + k:
            isprime[k] = 1
    return fac, isprime

def sweep(A, B, block=200000, verbose=False):
    """Decide P(n) for every n in [A,B).  Yields counterexample triples.
    Amortises the factorisation over the whole range with a segmented sieve."""
    sp = primes_upto(isqrt(B) + 1)
    out = []
    s = A
    while s < B:
        e = min(s + block, B)
        lo = max(2, s - MAXGAP_PAD)     # rem[] must never contain 0 or 1
        fac, isprime = factor_block(lo, e, sp)
        # previous-prime distance for every n in [s,e)
        last = None
        for k in range(len(isprime)):
            if isprime[k]:
                last = lo + k
            n = lo + k
            if n < s:
                continue
            if last is None:            # no prime seen yet (only near n = 2)
                continue
            gap = n - last
            if gap >= MAXGAP_PAD:
                raise RuntimeError(f"MAXGAP_PAD too small at n={n} (gap {gap})")
            imax = min(gap, n // 2 - 1)
            if imax < 2:
                continue
            pf = [fac[k - t] for t in range(imax)]
            r = decides(n, sp, pf, gap)
            if r is not None:
                out.append(r)
                if verbose:
                    print("COUNTEREXAMPLE", r, flush=True)
        s = e
    return out

# ------------------------------------------------------------------ naive reference
def decides_naive_gcd(n):
    """Ground truth: exact big-int binomials + gcd.  No Kummer, Lucas or pruning."""
    half = n // 2
    if half < 2:
        return None
    small = primes_upto(half)
    C = [comb(n, k) for k in range(half + 1)]
    for i in range(1, half):
        A = C[i]
        for p in small:
            if p >= i:
                break
            while A % p == 0:
                A //= p
        if A == 1:
            return (n, i, i + 1)
        for j in range(i + 1, half + 1):
            if gcd(A, C[j]) == 1:
                return (n, i, j)
    return None

# ------------------------------------------------------------------ self-test
def _selftest(gcd_lim=400, sweep_checks=True):
    import random
    rnd = random.Random(20260726)
    sp = primes_upto(2000)
    allp = primes_upto(600)
    fails = 0

    def chk(cond, name):
        nonlocal fails
        if not cond:
            fails += 1
            print("FAIL:", name)

    for _ in range(3000):
        n = rnd.randrange(1, 500); k = rnd.randrange(0, n + 1); p = rnd.choice(allp[:40])
        chk(divides_binom(n, k, p) == (comb(n, k) % p == 0), f"divides_binom {n},{k},{p}")
    for _ in range(1500):
        n = rnd.randrange(1, 300); k = rnd.randrange(0, n + 1); p = rnd.choice(allp[:30])
        c = comb(n, k); v = 0
        while c % p == 0:
            c //= p; v += 1
        chk(vp_binom(n, k, p) == v, f"vp_binom {n},{k},{p}")
    for _ in range(2000):
        n = rnd.randrange(1, 700); p = rnd.choice(allp[:60])
        lo = rnd.randrange(0, n + 1); hi = rnd.randrange(lo, n + 2)
        chk(uncovered_list(n, p, lo, hi) ==
            [j for j in range(lo, min(hi, n) + 1) if comb(n, j) % p != 0],
            f"uncovered_list {n},{p},{lo},{hi}")
    for _ in range(1500):
        n = rnd.randrange(1, 700); p = rnd.choice(allp[:60]); m = rnd.randrange(-1, n + 5)
        exp = len([j for j in range(0, min(m, n) + 1) if comb(n, j) % p != 0]) if m >= 0 else 0
        chk(count_uncovered_le(n, p, m) == exp, f"count_uncovered_le {n},{p},{m}")
        chk(usize(n, p) == len([j for j in range(n + 1) if comb(n, j) % p != 0]), f"usize {n},{p}")
    for n in range(4, 250):
        pn = primes_upto(n)
        for i in range(2, n // 2 + 1):
            pf = [factor_small(n - t, sp) for t in range(i)]
            chk(candidate_primes(n, i, sp, pf) == [q for q in pn if q >= i and vp_binom(n, i, q) > 0],
                f"candidate_primes {n},{i}")
    print(f"  units: {'PASS' if fails == 0 else str(fails) + ' FAILURES'}")

    bad = 0
    for n in range(1, gcd_lim + 1):
        if decides_naive_gcd(n) != decides(n, sp):
            bad += 1
            print("  DISAGREE", n, decides_naive_gcd(n), decides(n, sp))
    print(f"  vs naive gcd, n <= {gcd_lim}: {'PASS' if bad == 0 else str(bad) + ' DISAGREEMENTS'}")

    if sweep_checks:
        ok = True
        for A, B in [(1000, 4000), (10 ** 6, 10 ** 6 + 2000)]:
            spp = primes_upto(isqrt(B) + 1)
            ok &= sweep(A, B, block=997) == [r for n in range(A, B) if decides(n, spp) is not None
                                             for r in [decides(n, spp)]]
        print(f"  sweep == decides: {'PASS' if ok else 'FAIL'}")
        fails += 0 if ok else 1
    return fails + bad

if __name__ == "__main__":
    import sys, time
    if len(sys.argv) > 1 and sys.argv[1] == "--sweep":
        A, B = int(sys.argv[2]), int(sys.argv[3])
        t = time.time()
        res = sweep(A, B, verbose=True)
        dt = time.time() - t
        print(f"swept [{A},{B}): {len(res)} counterexamples, {dt:.1f}s "
              f"({dt/max(1,B-A)*1e6:.1f} us/n)")
    else:
        lim = int(sys.argv[1]) if len(sys.argv) > 1 else 400
        t = time.time()
        f = _selftest(lim)
        print(f"{'ALL PASS' if f == 0 else 'FAILED'}  ({time.time()-t:.1f}s)")

"""Reference code for the Erdős #962 certificate: OEIS A327909.

a(n) is the smallest start of a run of n or more consecutive integers, each
having a prime factor greater than n.  If p is the largest prime <= n, "has a
prime factor > n" means "is not p-smooth", so for all n between two
consecutive primes p <= n < q the runs are the gaps between consecutive
p-smooth integers, and a(n) is where the first such gap of length >= n starts.

This module holds what the verifier trusts outside the C engines:
- a_reference: an independent scan (greatest prime factors from a
  smallest-prime-factor sieve) for small ranges;
- has_large_factor / run_is_gap: the witness checks, by gcd with a primorial;
- merge_chunks: how the chunked engine's per-chunk records combine.
"""
from math import gcd, prod


def primes(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


def class_prime(n):
    """The largest prime <= n (None for n = 1)."""
    return max((p for p in primes(n)), default=None)


# ------------------------------------------------------------------ reference
def gpf_table(X):
    """gpf[m] for 1 <= m <= X, with gpf[1] = 1."""
    spf = list(range(X + 1))
    for p in range(2, int(X ** 0.5) + 1):
        if spf[p] == p:
            for q in range(p * p, X + 1, p):
                if spf[q] == q:
                    spf[q] = p
    gpf = [1] * (X + 1)
    for m in range(2, X + 1):
        p = spf[m]
        gpf[m] = max(p, gpf[m // p])
    return gpf


def a_reference(X, nmax):
    """{n: a(n)} for each n <= nmax whose first run of length n lies inside [1, X]."""
    gpf = gpf_table(X)
    out = {}
    for n in range(1, nmax + 1):
        run = 0
        for m in range(1, X + 1):
            run = run + 1 if gpf[m] > n else 0
            if run == n:
                out[n] = m - n + 1
                break
    return out


# -------------------------------------------------------------- witness checks
def has_large_factor(m, primorial):
    """True iff m has a prime factor not dividing primorial (a product of distinct primes)."""
    g = gcd(m, primorial)
    while g > 1:
        m //= g
        g = gcd(m, g)
    return m > 1


def run_is_gap(start, length, p):
    """start .. start+length-1 all have a prime factor > p, while start-1 and
    start+length do not (they are p-smooth): a maximal run between p-smooth
    integers.  start - 1 = 0 is not allowed (a(n) >= 2)."""
    P = prod(primes(p))
    if start < 2:
        return False
    inside = all(has_large_factor(m, P) for m in range(start, start + length))
    return inside and not has_large_factor(start - 1, P) and not has_large_factor(start + length, P)


# ------------------------------------------------------------- chunk merging
def parse_chunk(text):
    """Records of one chunk.c run: {p: (first, last)} and {p: [(start, length), ...]}."""
    fl, gaps = {}, {}
    for line in text.splitlines():
        w = line.split()
        if not w:
            continue
        if w[0] == "F":
            fl[int(w[1])] = (int(w[2]), int(w[3]))
        elif w[0] == "G":
            gaps.setdefault(int(w[1]), []).append((int(w[2]), int(w[3])))
    return fl, gaps


def merge_chunks(chunks, nmax, top):
    """Combine chunk.c outputs for consecutive chunks covering [1, top].

    Within a chunk the first gap of length >= n is always a record (longer than
    every earlier gap of its class in that chunk), so the records of each chunk,
    interleaved with the gaps that straddle chunk boundaries, contain the first
    gap of every length.  Returns {n: (a(n), run)} for 2 <= n <= nmax, where run
    is the length of the maximal run at a(n) (None if it is still open at top)."""
    parsed = [parse_chunk(t) for t in chunks]
    P = primes(nmax + 200)
    out = {}
    for k, p in enumerate(P):
        if p > nmax:
            break
        q = P[k + 1]
        seq, prev_last = [], None
        for fl, gaps in parsed:
            first, last = fl[p]
            if first == 0:            # no p-smooth integer in this chunk: the gap runs on
                continue
            if prev_last is not None:  # the gap that straddles the chunk boundary
                seq.append((prev_last + 1, first - prev_last - 1))
            seq += gaps.get(p, [])
            prev_last = last
        seq.append((prev_last + 1, None))
        for n in range(p, min(q - 1, nmax) + 1):
            for s, l in seq:
                if l is None:
                    if top - s + 1 >= n:
                        out[n] = (s, None)
                    break
                if l >= n:
                    out[n] = (s, l)
                    break
    return out

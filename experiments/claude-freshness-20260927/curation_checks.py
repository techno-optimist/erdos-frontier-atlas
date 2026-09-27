#!/usr/bin/env python3
"""Offline re-checks behind the 2026-09-27 gap-map curation (atlas/gap_map.json).

  python3 -I experiments/claude-freshness-20260927/curation_checks.py          # ~10 s
  python3 -I experiments/claude-freshness-20260927/curation_checks.py --census # + #376 to 10^100 (~30 s)

Each check recomputes, from the definition and with standard-library code only,
a fact that a curated gap-map row now relies on.  Values quoted from outside
sources are embedded below next to their source; nothing is fetched.  What a
check does NOT establish is stated beside it: the minimality claims of the
external computations (#1057, #1095) are cited, not replayed, and #156's lower
bound is F. Huber's theorem i(8) = 144, not re-proved here.
"""
import argparse
import itertools
import sys
from math import prod

FAILURES = []


def check(ok, label):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}", flush=True)
    if not ok:
        FAILURES.append(label)


# ---------------------------------------------------------------- #376 --
# A030979 (numbers k with binomial(2k,k) coprime to 105), OEIS data a(1..23);
# the b-file (C. E. Thompson) is complete to 10^70 with 1374 terms.
A030979_DATA = [0, 1, 10, 756, 757, 3160, 3186, 3187, 3250, 7560, 7561, 7651, 20007,
                59548377, 59548401, 45773612811, 45775397187, 237617431723407,
                24991943420078301, 24991943420078302, 24991943420078307,
                24991943715007536, 24991943715007537]
A030979_1375 = 41793835224715561827991803724419285037533255120531924813793252461031887


def succ(x, b, d):
    """Least m >= x whose base-b digits are all <= d."""
    while True:
        y, pos, i = x, -1, 0
        while y:
            if y % b > d:
                pos = i
            y //= b
            i += 1
        if pos < 0:
            return x
        q = b ** (pos + 1)
        x = (x // q + 1) * q


def next_term(x):
    """Least k >= x with base-3 digits <= 1, base-5 digits <= 2, base-7 digits <= 3.

    Each succ() never passes the least common member y >= x (y lies in every
    digit set and is >= the current point), so the iterates stay <= y and the
    fixed point, which lies in all three sets, is y itself."""
    while True:
        y = succ(succ(succ(x, 3, 1), 5, 2), 7, 3)
        if y == x:
            return x
        x = y


def census(limit):
    terms, x = [0], 1
    while True:
        x = next_term(x)
        if x > limit:
            return terms, x
        terms.append(x)
        x += 1


def check_376(full):
    print("#376  A030979: successor census (Kummer: no carry in k + k in bases 3, 5, 7)")
    terms, nxt = census(10 ** 70)
    check(terms[:len(A030979_DATA)] == A030979_DATA, "reproduces the OEIS data a(1..23)")
    check(len(terms) == 1374, "exactly 1374 terms <= 10^70, the size of Thompson's b-file")
    check(nxt == A030979_1375, "a(1375), the least term > 10^70, is the 71-digit value in the row")
    if full:
        terms, nxt = census(10 ** 100)
        check(len(terms) - 1 == 14273, "14,273 positive terms <= 10^100 (the count reported "
                                       "with jaredwilder/erdos376-successor-frontier)")


# --------------------------------------------------------------- #1005 --
# A386893(n), n = 4..100 (OEIS data): largest m such that Farey fractions of
# order n at index distance <= m are similarly ordered.
A386893_DATA = [2, 3, 3, 4, 3, 3, 4, 5, 4, 5, 5, 5, 5, 6, 6, 7, 6, 7, 7, 8, 7, 7, 8, 8, 8, 9,
                9, 10, 9, 10, 10, 11, 10, 11, 11, 12, 11, 12, 12, 14, 12, 13, 13, 15, 13, 13,
                14, 15, 14, 15, 15, 17, 15, 16, 16, 18, 16, 17, 17, 18, 17, 18, 18, 20, 18,
                19, 19, 21, 19, 20, 20, 22, 20, 21, 21, 23, 21, 22, 22, 24, 22, 23, 23, 25,
                23, 24, 24, 25, 24, 25, 25, 27, 25, 26, 26, 28, 26]


def farey(n):
    a, b, c, d = 0, 1, 1, n
    out = [(0, 1)]
    while c <= n:
        k = (n + b) // d
        a, b, c, d = c, d, k * c - a, k * d - b
        out.append((a, b))
    return out


def mayer_erdos(n):
    F = farey(n)
    best = len(F)          # least index distance of a pair that is NOT similarly ordered
    for i, (p, q) in enumerate(F):
        for j in range(i + 1, min(len(F), i + best)):
            r, s = F[j]
            if (p - r) * (q - s) < 0:
                best = j - i
                break
    return best - 1


def check_1005():
    print("#1005 A386893: Farey scan from the definition")
    check([mayer_erdos(n) for n in range(4, 101)] == A386893_DATA,
          "reproduces the 97 OEIS terms a(4..100)")
    vals = [mayer_erdos(n) for n in range(101, 109)]
    check(vals[0] == 27, "a(101) = 27")
    check(vals == [n // 4 + (1, 2, 2, 4)[n % 4] for n in range(101, 109)],
          "a(101..108) follow floor(n/4) + (1, 2, 2, 4)[n mod 4] (van Doorn's conjectured form)")


# ---------------------------------------------------------------- #302 --
def harmonic_triples(N):
    """All {a < b < c <= N} with 1/a = 1/b + 1/c (then a < b < 2a, c = ab/(b - a))."""
    out = set()
    for a in range(1, N + 1):
        for b in range(a + 1, 2 * a):
            if (a * b) % (b - a) == 0 and a * b // (b - a) <= N:
                out.add((a, b, a * b // (b - a)))
    return out


def check_302():
    print("#302  A390395: local arguments past the b-file (a(731) = 606)")
    T = harmonic_triples(735)
    comp = {122, 183, 244, 366, 732}
    touch = sorted(t for t in T if set(t) & comp and t[2] <= 732)
    check(touch == [(122, 183, 366), (183, 244, 732), (244, 366, 732)],
          "in {1..732}, 122, 183, 244, 366, 732 meet exactly three triples, all inside the set")
    best = lambda S, ts: max(len(X) for r in range(len(S) + 1)
                             for X in itertools.combinations(sorted(S), r)
                             if not any(set(t) <= set(X) for t in ts))
    before = best(comp - {732}, [t for t in touch if 732 not in t])
    check(before == 3 and best(comp, touch) == 3,
          "the component's best choice is 3 before and after 732, so a(732) = a(731)")
    for n in (733, 734):
        check(not any(n in t for t in T if t[2] <= n), f"{n} lies in no triple inside {{1..{n}}}, "
                                                        "so a(n) = a(n-1) + 1")
    check(sorted(t for t in T if 735 in t) == [(210, 294, 735), (294, 490, 735)],
          "735 is the first such n whose triples tie it to the rest: (210,294,735), (294,490,735)")


# --------------------------------------------------------------- #1095 --
# g(k) = A003458(k): g(376), g(377) from Sorenson-Sorenson-Webster (arXiv:1907.08559v3);
# g(378..400) from A. Eastwood (github.com/AlexanderEastwood/erdos-selfridge, 2026).
G = {376: 7778804220120654420924631668091, 377: 5973303871796437264595936954237,
     378: 11243132307156301763663607287294, 379: 161870983573549868804425756301179,
     380: 10462825184429793014317942235516, 381: 12870452058086999925869938534781,
     382: 33595253716498387794413412981758, 383: 540148968489634107903617360993663,
     384: 347602760349418009297709548536219, 385: 327295190388354179623724094491095,
     386: 13244365243698813468350652166046, 387: 17088927744279024569389598842319,
     388: 1379978640683593021393172825519, 389: 4171959526360182919803787001674199,
     390: 1967924476778959819324408694516718, 391: 1407678907549820296859900034849791,
     392: 2149910863290282683111595748554173, 393: 8221905832123087594889003885519,
     394: 26940132483154282770968897574794, 395: 70422314661266035686410669061023,
     396: 7350984493848874781629926017999, 397: 7282852096749166908452220090055597,
     398: 358644756463853013270803607289823, 399: 1463367633345557449307696345739199,
     400: 58305842808280308870124770403739}


def primes_upto(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


def carry(a, b, p):
    """Kummer: p divides binomial(a + b, a) iff adding a and b in base p carries."""
    c = 0
    while a or b or c:
        if a % p + b % p + c >= p:
            return True
        a, b, c = a // p, b // p, 0
    return False


def check_1095():
    print("#1095 A003458: admissibility of g(376..400) by Kummer's theorem")
    ok = all(g > k + 1 and not any(carry(k, g - k, p) for p in primes_upto(k))
             for k, g in G.items())
    check(ok, "no prime <= k divides binomial(g(k), k), for all 25 values (minimality not replayed)")
    # the defining property really needs the exact value: g - 1 fails for k = 378
    check(any(carry(378, G[378] - 1 - 378, p) for p in primes_upto(378)),
          "negative control: g(378) - 1 is not admissible")


# --------------------------------------------------------------- #1057 --
# A006931(40), with its factorization (Butler University table,
# github.com/jewebste/small-carmichael-numbers, k = 40 row).
C40 = 336344101674863882264460997162737741032660590208112263486472947389502099210991168001
C40_PRIMES = [17, 19, 23, 29, 31, 37, 41, 43, 53, 61, 67, 71, 73, 79, 89, 97, 101, 109, 113,
              127, 131, 151, 157, 163, 181, 193, 197, 199, 211, 241, 251, 271, 313, 337, 353,
              379, 401, 541, 617, 1409]


def check_1057():
    print("#1057 A006931: Korselt's criterion for the 40-factor value")
    P = set(primes_upto(1500))
    check(len(set(C40_PRIMES)) == 40 and all(p in P for p in C40_PRIMES)
          and prod(C40_PRIMES) == C40, "40 distinct primes whose product is the 84-digit value")
    check(all((C40 - 1) % (p - 1) == 0 for p in C40_PRIMES),
          "(p - 1) | (N - 1) for every prime factor, so N is a Carmichael number "
          "(minimality is the table's claim)")


# ----------------------------------------------------------------- #20 --
def f39():
    """Theorem 5.1 of arXiv:2609.06175, rebuilt from its description: groups V1, V2, V3,
    apex a, and a link point l_ij for each pair of groups; 3 + 9 + 27 = 39 triples."""
    V = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    a, link = 9, {(0, 1): 10, (0, 2): 11, (1, 2): 12}
    F = [frozenset(v) for v in V]
    F += [frozenset((a,) + pr) for v in V for pr in itertools.combinations(v, 2)]
    F += [frozenset((link[i, j], x, y)) for (i, j) in link for x in V[i] for y in V[j]]
    return F


def check_20():
    print("#20   Sun(3,4): the 39-triple family has no 4-sunflower")
    F = f39()
    check(len(set(F)) == 39 and all(len(A) == 3 for A in F), "39 distinct triples on 13 points")
    bad = 0
    for Q in itertools.combinations(F, 4):
        K = Q[0] & Q[1]
        bad += all(Q[i] & Q[j] == K for i in range(4) for j in range(i + 1, 4))
    check(bad == 0, "no 4 of them pairwise meet in a common kernel, so Sun(3,4) >= 40")
    F2 = F + [frozenset((13, 14, 15))]
    bad2 = sum(all(Q[i] & Q[j] == Q[0] & Q[1] for i in range(4) for j in range(i + 1, 4))
               for Q in itertools.combinations(F2, 4))
    check(bad2 > 0, "negative control: adding a disjoint triple creates a 4-sunflower")


# ---------------------------------------------------------------- #156 --
# Maximal Sidon sets, found by a local search for this curation, with the range
# of n for which each is maximal in {1..n} (it is not maximal at the next n).
SIDON_WITNESSES = [((31, 46, 87, 90, 91, 96, 98, 118, 175), 175, 186),
                   ((12, 62, 72, 74, 80, 113, 116, 117, 141), 141, 186),
                   ((10, 67, 87, 89, 94, 95, 98, 139, 154), 154, 186),
                   ((39, 43, 72, 78, 99, 100, 112, 119, 143), 143, 188),
                   ((3, 19, 49, 64, 91, 92, 102, 123, 128, 141), 141, 187)]


def is_sidon(S):
    sums = [a + b for i, a in enumerate(S) for b in S[i:]]
    return len(sums) == len(set(sums))


def is_maximal_sidon(S, n):
    return (is_sidon(S) and all(1 <= s <= n for s in S)
            and all(not is_sidon(tuple(S) + (x,)) for x in range(1, n + 1) if x not in S))


def check_156():
    print("#156  A382397 past n = 183: maximal Sidon sets of size 9")
    for S, lo, hi in SIDON_WITNESSES:
        check(all(is_maximal_sidon(S, n) for n in range(lo, hi + 1))
              and not is_maximal_sidon(S, hi + 1),
              f"a {len(S)}-set is maximal in {{1..n}} exactly for n = {lo}..{hi}")
    top9 = max(hi for S, lo, hi in SIDON_WITNESSES if len(S) == 9)
    check(top9 >= 184, f"so a(n) <= 9 for 184 <= n <= {top9}, and i(9) >= {top9}")
    check((7 ** 3 + 7) // 2 < 184, "sizes <= 7 are impossible at n >= 176: a k-set blocks at most "
                                   "(k^3 - k)/2 points, and (7^3 + 7)/2 = 175")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", action="store_true", help="also count #376 terms to 10^100")
    args = ap.parse_args()
    check_376(args.census)
    check_1005()
    check_302()
    check_1095()
    check_1057()
    check_20()
    check_156()
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s)")
        sys.exit(1)
    print("\nall curation checks passed")


if __name__ == "__main__":
    main()

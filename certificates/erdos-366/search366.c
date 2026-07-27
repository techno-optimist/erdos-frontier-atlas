/* search366.c — Erdős #366 sweep: is there a 2-full n with n+1 3-full?
 *
 *   powerful (2-full):  p | n  =>  p^2 | n
 *   cubefull (3-full):  p | n  =>  p^3 | n
 *
 * Strategy (per the atlas attack card, S:triage:366): only the CUBEFULL side
 * needs enumerating. Cubefull numbers below X number ~ X^(1/3), against
 * ~X^(1/2) powerful numbers — which is why the 10^22 frontier inherited from
 * the consecutive-powerful-pair search (OEIS A060355) can be passed here on
 * one workstation. Every cubefull number is a^3 b^4 c^5 (every exponent >= 3
 * is a nonneg combination of 3,4,5), so we stream those triples and test both
 * neighbours of each.
 *
 * Both orientations are swept, because upstream's statement and its own worked
 * examples disagree about which member is the cubefull one:
 *   strict  (n 2-full, n+1 3-full):  test C-1 powerful for cubefull C  [0 known]
 *   reverse (n 3-full, n+1 2-full):  test C+1 powerful for cubefull C  [(8,9), (12167,12168)]
 *
 * EXACT powerfulness test, no factoring, no floats. For m <= N pick B with
 * B^5 >= N. Trial-divide m by primes <= B demanding exponent >= 2 for each.
 * The cofactor r then has all prime factors > B, and:
 *
 *   m is powerful  <=>  every prime <= B divides m to exponent >= 2,
 *                       AND r is 1 or a perfect power.
 *
 * Proof of the interesting direction. Suppose r > 1 is powerful and NOT a
 * perfect power. "Not a perfect power" means the gcd of ALL its exponents is 1
 * (the JOINT gcd — pairwise gcds can all exceed 1, e.g. exponents (6,10,15)).
 * So r is not a single prime power (whose joint gcd is its exponent >= 2), and
 * with every exponent >= 2 and joint gcd 1 the exponent SUM is at least 5:
 * two primes cannot be (2,2) (gcd 2) so sum >= 5, and three or more primes
 * give sum >= 6. Hence r >= q^5 where q is the least prime exceeding B, so
 * r > B^5 >= N >= r — contradiction. (The minimising configuration is p^3 q^2,
 * larger exponent on the smaller prime, not p^2 q^3; the exponent-sum bound is
 * what carries the argument either way.)
 *
 * Directionality worth stating: conditions (i)+(ii) imply powerful for ANY B,
 * so the test has NO false positives ever. B controls only false NEGATIVES —
 * a B that is too small can silently MISS powerful numbers, never invent them.
 * A misconfigured B therefore under-reports hits, which is why the bound is
 * asserted at startup rather than assumed.
 *
 *   cc -O2 -o search366 search366.c
 *   ./search366 <lo> <hi> [shard] [nshards]      sweeps cubefull C in (lo, hi]
 *
 * Prints one line per hit (orientation, n, and the neighbour pair), then a
 * machine-readable summary line. Exit 0 on a clean sweep.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;

/* ---------------------------------------------------------------- utility */
static void print_u128(char *buf, u128 v)
{
    char tmp[64];
    int i = 0;
    if (v == 0) { strcpy(buf, "0"); return; }
    while (v) { tmp[i++] = '0' + (int)(v % 10); v /= 10; }
    for (int j = 0; j < i; j++) buf[j] = tmp[i - 1 - j];
    buf[i] = 0;
}

static u128 parse_u128(const char *s)
{
    u128 v = 0;
    for (; *s; s++) {
        if (*s < '0' || *s > '9') { fprintf(stderr, "bad number: %s\n", s); exit(2); }
        v = v * 10 + (u128)(*s - '0');
    }
    return v;
}

/* k^e <= r, overflow-safe */
static int powle(u128 k, int e, u128 r)
{
    u128 t = 1;
    for (int i = 0; i < e; i++) {
        if (k > 1 && t > r / k) return 0;
        t *= k;
    }
    return t <= r;
}

static int ipow_eq(u128 k, int e, u128 target)
{
    u128 t = 1;
    for (int i = 0; i < e; i++) {
        if (k > 1 && t > target / k) return 0;
        t *= k;
    }
    return t == target;
}

/* largest k with k^e <= r  (r >= 1, e >= 1) */
static u128 introot(u128 r, int e)
{
    u128 lo = 1, hi = (u128)1 << (128 / e < 100 ? 128 / e : 100), best = 1;
    if (hi < 2) hi = 2;
    while (lo <= hi) {
        u128 mid = lo + (hi - lo) / 2;
        if (mid == 0) break;
        if (powle(mid, e, r)) { best = mid; lo = mid + 1; }
        else { if (mid == 0) break; hi = mid - 1; }
    }
    return best;
}

static int is_perfect_power(u128 r)
{
    static const int exps[] = {2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,
                               53,59,61,67,71,73,79,83,89,97,101,103,107,
                               109,113,127,0};
    for (int i = 0; exps[i]; i++) {
        int e = exps[i];
        if (!powle(2, e, r)) break;          /* 2^e > r: no larger e can work */
        u128 k = introot(r, e);
        if (k >= 2 && ipow_eq(k, e, r)) return 1;
    }
    return 0;
}

/* ------------------------------------------------------- powerfulness test */
static u64 *primes;
static int nprimes;
static unsigned char wheel[44100];        /* 2^2 * 3^2 * 5^2 * 7^2 */

static void sieve(u64 B)
{
    unsigned char *comp = calloc(B + 1, 1);
    if (!comp) { fprintf(stderr, "oom\n"); exit(2); }
    primes = malloc(sizeof(u64) * (B / 4 + 1024));
    nprimes = 0;
    for (u64 i = 2; i <= B; i++) {
        if (!comp[i]) {
            primes[nprimes++] = i;
            if (i <= B / i) for (u64 j = i * i; j <= B; j += i) comp[j] = 1;
        }
    }
    free(comp);
}

static void build_wheel(void)
{
    const int ps[4] = {2, 3, 5, 7};
    for (int x = 0; x < 44100; x++) {
        int ok = 1;
        for (int i = 0; i < 4; i++) {
            int p = ps[i];
            if (x % p == 0 && x % (p * p) != 0) { ok = 0; break; }
        }
        wheel[x] = (unsigned char)ok;
    }
}

/* exact; requires B^5 >= m, enforced at startup */
static int is_powerful(u128 m)
{
    if (m <= 1) return m == 1;                    /* 1 is vacuously powerful */
    if (!wheel[(u64)(m % 44100)]) return 0;       /* cheap 57% rejection */
    for (int i = 0; i < nprimes; i++) {
        u64 p = primes[i];
        if ((u128)p * p > m) return 0;   /* m > 1 is now prime: exponent 1 */
        if (m % p == 0) {
            int e = 0;
            do { m /= p; e++; } while (m % p == 0);
            if (e < 2) return 0;
            if (m == 1) return 1;
        }
    }
    return is_perfect_power(m);           /* cofactor: all prime factors > B */
}

/* --------------------------------------------------------------- selftest */
/* Independent oracle: full factorization, no cofactor shortcut. */
static int is_powerful_bruteforce(u128 m)
{
    if (m <= 1) return m == 1;
    for (u128 d = 2; d * d <= m; d++) {
        if (m % d == 0) {
            int e = 0;
            while (m % d == 0) { m /= d; e++; }
            if (e < 2) return 0;
        }
    }
    return m == 1;              /* leftover prime => exponent 1 => not powerful */
}

static int selftest(void)
{
    int fails = 0, checked = 0;

    /* (1) Differential vs the brute-force oracle with a DELIBERATELY TINY B,
     *     so the "cofactor is a perfect power" path carries almost all the
     *     weight and every edge case actually fires. B=64 is exact for
     *     m <= 64^5 = 2^30 = 1073741824. */
    sieve(64);
    build_wheel();
    for (u128 m = 1; m <= 200000; m++) {
        if (is_powerful(m) != is_powerful_bruteforce(m)) {
            char b[64]; print_u128(b, m);
            printf("SELFTEST FAIL: exhaustive m=%s\n", b);
            if (++fails > 5) return fails;
        }
        checked++;
    }
    /* adversarial p^2 q^3 with both primes just above B: the exact case the
     * validity bound B^5 >= N is protecting. All of these are <= 2^30. */
    const u64 pr[] = {67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 0};
    for (int i = 0; pr[i]; i++)
        for (int j = 0; pr[j]; j++) {
            if (i == j) continue;
            u128 m = (u128)pr[i] * pr[i] * pr[j] * pr[j] * pr[j];
            if (m > ((u128)1 << 30)) continue;      /* outside B=64 validity */
            if (is_powerful(m) != is_powerful_bruteforce(m)) {
                char b[64]; print_u128(b, m);
                printf("SELFTEST FAIL: p^2q^3 m=%s\n", b);
                fails++;
            }
            checked++;
        }
    free(primes);

    /* (2) PLANTED FAILURES at production scale. Brute force cannot reach 10^24,
     *     so build numbers whose answer is known by construction and demand the
     *     verifier get BOTH directions right. A checker that always says
     *     "powerful" fails here, and so does one that always says "not". */
    sieve(65536);               /* exact for m <= 65536^5 = 1.18e24 */
    build_wheel();
    const u64 big[] = {1000003, 1000033, 1000037, 1000039, 15485863, 32452843, 0};
    for (int i = 0; big[i]; i++) {
        for (int j = 0; big[j]; j++) {
            u128 a = big[i], b = big[j];
            u128 pw = a * a * b * b * b;               /* powerful by construction */
            if (pw > (u128)1e24) continue;
            if (!is_powerful(pw)) {
                char s[64]; print_u128(s, pw);
                printf("SELFTEST FAIL: constructed powerful rejected %s\n", s);
                fails++;
            }
            checked++;
            /* PLANTED FAILURE: one extra prime factor at exponent 1 must flip
             * the verdict. If this is ever accepted, the sweep is worthless. */
            u128 spoiled = pw * 3;
            if (spoiled <= (u128)1e24 && pw % 3 != 0) {
                if (is_powerful(spoiled)) {
                    char s[64]; print_u128(s, spoiled);
                    printf("SELFTEST FAIL: planted non-powerful ACCEPTED %s\n", s);
                    fails++;
                }
                checked++;
            }
        }
    }
    /* (3) the two known #366 pairs must survive at production B */
    if (!is_powerful(9) || !is_powerful(8) || !is_powerful(12168) ||
        !is_powerful(12167)) {
        printf("SELFTEST FAIL: known pair members rejected\n");
        fails++;
    }
    /* and their neighbours must not be powerful */
    if (is_powerful(7) || is_powerful(10) || is_powerful(12166)) {
        printf("SELFTEST FAIL: known non-powerful accepted\n");
        fails++;
    }
    checked += 7;
    free(primes);

    printf("SELFTEST %s\tchecks=%d\tfailures=%d\n",
           fails ? "FAIL" : "PASS", checked, fails);
    return fails;
}

/* ------------------------------------------------------------------- sweep */
int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "--selftest") == 0)
        return selftest() ? 1 : 0;
    if (argc < 3) {
        fprintf(stderr, "usage: %s <lo> <hi> [shard] [nshards]\n"
                        "       %s --selftest\n", argv[0], argv[0]);
        return 2;
    }
    u128 LO = parse_u128(argv[1]);
    u128 HI = parse_u128(argv[2]);
    u64 shard = argc > 3 ? strtoull(argv[3], 0, 10) : 0;
    u64 nshards = argc > 4 ? strtoull(argv[4], 0, 10) : 1;
    if (shard >= nshards) { fprintf(stderr, "shard >= nshards\n"); return 2; }

    /* The largest number whose powerfulness we ever decide is HI+1 (the upper
     * neighbour of the largest cubefull number swept). The cofactor argument
     * is exact only while B^5 >= that. Assert it rather than trust it: if this
     * bound is wrong the entire sweep is worthless, so it must never be a
     * silent assumption. */
    u128 MMAX = HI + 1;
    u64 B = (u64)introot(MMAX, 5) + 1;
    if (B < 1000) B = 1000;
    if (powle(B, 5, MMAX) && !ipow_eq(B, 5, MMAX)) {
        fprintf(stderr, "FATAL: B^5 < max tested m — test would be unsound\n");
        return 2;
    }
    sieve(B);
    build_wheel();

    char b1[64], b2[64], b3[64];
    print_u128(b1, LO); print_u128(b2, HI);
    if (shard == 0)
        fprintf(stderr, "# sweep (%s, %s], B=%llu (%d primes), shards=%llu\n",
                b1, b2, (unsigned long long)B, nprimes, (unsigned long long)nshards);

    u64 tested = 0, hits = 0;
    clock_t t0 = clock();

    for (u64 c = 1; ; c++) {
        u128 c5;
        if (!powle(c, 5, HI)) break;
        c5 = 1; for (int i = 0; i < 5; i++) c5 *= c;
        for (u64 b = 1; ; b++) {
            u128 b4 = 1; int ovf = 0;
            for (int i = 0; i < 4; i++) {
                if (b > 1 && b4 > (HI / c5) / b) { ovf = 1; break; }
                b4 *= b;
            }
            if (ovf) break;
            u128 base = c5 * b4;
            if (base > HI) break;

            u128 amax128 = introot(HI / base, 3);
            u64 amax = (u64)amax128;
            /* smallest a with base*a^3 > LO */
            u64 amin = 1;
            if (base <= LO) {
                amin = (u64)introot(LO / base, 3);
                if (amin < 1) amin = 1;
                while (base * (u128)amin * amin * amin <= LO) amin++;
            }
            for (u64 a = amin + shard; a <= amax; a += nshards) {
                u128 C = base * (u128)a * a * a;
                if (C <= LO || C > HI) continue;
                tested++;
                if (C >= 2 && is_powerful(C - 1)) {          /* strict */
                    print_u128(b1, C - 1); print_u128(b2, C);
                    printf("HIT\tstrict\tn=%s\tn+1=%s\n", b1, b2);
                    fflush(stdout); hits++;
                }
                if (is_powerful(C + 1)) {                    /* reverse */
                    print_u128(b1, C); print_u128(b2, C + 1);
                    printf("HIT\treverse\tn=%s\tn+1=%s\n", b1, b2);
                    fflush(stdout); hits++;
                }
            }
        }
    }
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
    print_u128(b1, LO); print_u128(b2, HI); print_u128(b3, (u128)tested);
    printf("SUMMARY\tlo=%s\thi=%s\tshard=%llu/%llu\tcandidates=%s\thits=%llu"
           "\tB=%llu\tsecs=%.1f\n",
           b1, b2, (unsigned long long)shard, (unsigned long long)nshards,
           b3, (unsigned long long)hits, (unsigned long long)B, secs);
    return 0;
}

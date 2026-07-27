/* unimodal.c — Erdős #993: is every tree's independence sequence unimodal?
 *
 * i_k(T) = number of independent vertex sets of size k. The conjecture
 * (Alavi–Malde–Schwenk–Erdős 1987) is that for every tree the sequence
 * i_0, i_1, ..., is unimodal. It is FALSE for general graphs.
 *
 * This program enumerates every free (unlabeled, unrooted) tree on n vertices
 * and tests its independence sequence. Frontier: Reynolds 2026 verified all
 * 8,691,747,673 trees on n <= 29 (Zenodo DOI 10.5281/zenodo.19100781) — a
 * single-author preprint that nobody has independently replayed.
 *
 * GENERATION — WROM (Wright, Richmond, Odlyzko & McKay 1986), the algorithm
 * behind nauty's gentreeg: constant amortised time per free tree, via canonic
 * rooted level sequences filtered to WROM-"primary" ones. Roots at the
 * ECCENTRICITY CENTER, not the centroid. The three traps, all guarded below:
 *   (a) center vs centroid — different representatives, same count;
 *   (b) dropping the size tie-break emits bicentral trees TWICE;
 *   (c) reversing the lexicographic tie-break duplicates and omits at once.
 * Counts are pinned to OEIS A000055 in --selftest, so any of these fails loud.
 *
 * INDEPENDENCE POLYNOMIAL — exact integer DP over the rooted tree:
 *   A_v = prod_c (A_c + B_c)      (v excluded)
 *   B_v = x * prod_c A_c          (v included)
 * with I(T,x) = A_root + B_root. Theta(n^2) coefficient operations, not
 * linear. Every coefficient fits: the maximum i_k over all trees on 30
 * vertices is C(29,14) = 77,558,760, attained by the star — so uint64 has
 * room to spare and no overflow check can trigger below n = 40.
 *
 * UNIMODALITY — find the first strict descent, then require no later strict
 * ascent. Plateaus are fine (a plateau is not a violation).
 * NOT log-concavity: that is FALSE for trees from n = 26 onward, so testing
 * it as a proxy would report counterexamples that are not counterexamples.
 *
 *   cc -O2 -o unimodal unimodal.c
 *   ./unimodal <n> [shard] [nshards]
 *   ./unimodal --selftest
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXN 40
typedef uint64_t u64;

/* OEIS A000055, free trees on n nodes, n = 0..30 */
static const u64 A000055[] = {
    1ULL, 1ULL, 1ULL, 1ULL, 2ULL, 3ULL, 6ULL, 11ULL, 23ULL, 47ULL, 106ULL,
    235ULL, 551ULL, 1301ULL, 3159ULL, 7741ULL, 19320ULL, 48629ULL, 123867ULL,
    317955ULL, 823065ULL, 2144505ULL, 5623756ULL, 14828074ULL, 39299897ULL,
    104636890ULL, 279793450ULL, 751065460ULL, 2023443032ULL, 5469566585ULL,
    14830871802ULL};

/* ---------------------------------------------------------------- WROM ---- */
static int N;                       /* tree order */
static int L[MAXN];                 /* current canonic rooted level sequence */

static void wrom_start(void)
{
    int i, k = 0;
    for (i = 0; i <= N / 2; i++) L[k++] = i;
    for (i = 1; i < (N + 1) / 2; i++) L[k++] = i;
}

/* split at the root's first (tallest) branch; fills left/rest, returns |left| */
static int split_tree(int *left, int *nleft, int *rest, int *nrest)
{
    int m = -1, one_found = 0;
    for (int i = 0; i < N; i++) {
        if (L[i] == 1) {
            if (one_found) { m = i; break; }
            one_found = 1;
        }
    }
    if (m < 0) m = N;
    *nleft = 0;
    for (int i = 1; i < m; i++) left[(*nleft)++] = L[i] - 1;
    *nrest = 0;
    rest[(*nrest)++] = 0;
    for (int i = m; i < N; i++) rest[(*nrest)++] = L[i];
    return *nleft;
}

static int maxarr(const int *a, int n)
{
    int m = 0;
    for (int i = 0; i < n; i++) if (a[i] > m) m = a[i];
    return m;
}

/* lexicographic compare */
static int lexcmp(const int *a, int na, const int *b, int nb)
{
    int m = na < nb ? na : nb;
    for (int i = 0; i < m; i++) if (a[i] != b[i]) return a[i] < b[i] ? -1 : 1;
    return na == nb ? 0 : (na < nb ? -1 : 1);
}

static int is_primary(void)
{
    if (N <= 2) return 1;
    int left[MAXN], rest[MAXN + 1], nl, nr;
    split_tree(left, &nl, rest, &nr);
    if (nl == 0) return 0;                       /* root has < 2 branches */
    int h1 = maxarr(left, nl), h2 = maxarr(rest, nr);
    if (h2 < h1) return 0;                       /* (C1) root not a center */
    if (h2 == h1) {
        if (nl > nr) return 0;                   /* (C2) size tie-break */
        if (nl == nr && lexcmp(left, nl, rest, nr) > 0) return 0;   /* (C3) */
    }
    return 1;
}

/* Beyer-Hedetniemi successor over canonic ROOTED level sequences.
 * Returns 0 when exhausted. If p >= 0, restart the copy at position p. */
static int bh_next_from(int p)
{
    if (p < 0) {
        p = -1;
        for (int i = N - 1; i > 0; i--) if (L[i] > 1) { p = i; break; }
        if (p < 0) return 0;
    }
    if (p == 0) return 0;
    int target = L[p] - 1, q = -1;
    for (int j = p - 1; j >= 0; j--) if (L[j] == target) { q = j; break; }
    if (q < 0) return 0;
    int d = p - q;
    for (int i = p; i < N; i++) L[i] = L[i - d];
    return 1;
}

/* advance L to the next PRIMARY sequence; returns 0 when exhausted */
static int wrom_advance(void)
{
    for (;;) {
        if (!bh_next_from(-1)) return 0;
        while (!is_primary()) {
            int left[MAXN], rest[MAXN + 1], nl, nr;
            split_tree(left, &nl, rest, &nr);
            int p = nl;                       /* == len(left) */
            int old = (p < N) ? L[p] : 0;
            if (!bh_next_from(p)) return 0;
            if (old > 2) {
                split_tree(left, &nl, rest, &nr);
                int h = nl ? maxarr(left, nl) : 0;
                int len = h + 1;              /* ramp 1..h+1 */
                for (int i = 0; i < len; i++) L[N - len + i] = i + 1;
            }
        }
        return 1;
    }
}

/* ------------------------------------------------ independence polynomial -- */
/* Level sequence -> parent array (parents precede children). */
static int par[MAXN];
static void parents_from_levels(void)
{
    int at[MAXN];
    par[0] = -1;
    for (int i = 0; i < N; i++) {
        at[L[i]] = i;
        if (L[i] > 0) par[i] = at[L[i] - 1];
    }
}

static u64 A[MAXN][MAXN + 1], B[MAXN][MAXN + 1];   /* coefficients */
static int dA[MAXN], dB[MAXN];                     /* degrees */

/* I(T,x) into out[0..*deg]; vertices are in level order so children have
 * larger index than parents — a reverse sweep is a valid post-order. */
static int independence_poly(u64 *out)
{
    for (int v = 0; v < N; v++) {
        A[v][0] = 1; dA[v] = 0;
        B[v][0] = 0; B[v][1] = 1; dB[v] = 1;
    }
    for (int v = N - 1; v >= 1; v--) {
        int p = par[v];
        /* A_p *= (A_v + B_v) */
        u64 s[MAXN + 1];
        int ds = dA[v] > dB[v] ? dA[v] : dB[v];
        for (int i = 0; i <= ds; i++)
            s[i] = (i <= dA[v] ? A[v][i] : 0) + (i <= dB[v] ? B[v][i] : 0);
        u64 t[MAXN + 1];
        int dt = dA[p] + ds;
        for (int i = 0; i <= dt; i++) t[i] = 0;
        for (int i = 0; i <= dA[p]; i++)
            if (A[p][i])
                for (int j = 0; j <= ds; j++) t[i + j] += A[p][i] * s[j];
        for (int i = 0; i <= dt; i++) A[p][i] = t[i];
        dA[p] = dt;
        /* B_p *= A_v */
        int du = dB[p] + dA[v];
        for (int i = 0; i <= du; i++) t[i] = 0;
        for (int i = 0; i <= dB[p]; i++)
            if (B[p][i])
                for (int j = 0; j <= dA[v]; j++) t[i + j] += B[p][i] * A[v][j];
        for (int i = 0; i <= du; i++) B[p][i] = t[i];
        dB[p] = du;
    }
    int d = dA[0] > dB[0] ? dA[0] : dB[0];
    for (int i = 0; i <= d; i++)
        out[i] = (i <= dA[0] ? A[0][i] : 0) + (i <= dB[0] ? B[0][i] : 0);
    while (d > 0 && out[d] == 0) d--;
    return d;
}

/* first strict descent, then no later strict ascent. Plateaus are legal. */
static int is_unimodal(const u64 *c, int d)
{
    int i = 0;
    while (i < d && c[i] <= c[i + 1]) i++;
    while (i < d && c[i] >= c[i + 1]) i++;
    return i == d;
}

/* --------------------------------------------------------------- selftest -- */
static int selftest(void)
{
    int fails = 0;
    for (int n = 1; n <= 18; n++) {
        N = n;
        u64 cnt = 0;
        if (N <= 2) cnt = 1;
        else {
            wrom_start();
            do { if (is_primary()) cnt++; } while (wrom_advance());
        }
        if (cnt != A000055[n]) {
            printf("SELFTEST FAIL: n=%d generated %llu != A000055 %llu\n",
                   n, (unsigned long long)cnt, (unsigned long long)A000055[n]);
            fails++;
        }
    }
    /* known independence sequences */
    u64 c[MAXN + 1];
    N = 5; L[0]=0; L[1]=1; L[2]=1; L[3]=1; L[4]=1;       /* star K_{1,4} */
    parents_from_levels();
    int d = independence_poly(c);
    /* star K_{1,m}: i_0=1, i_1=m+1, i_k=C(m,k) for k>=2 */
    if (!(c[0] == 1 && c[1] == 5 && c[2] == 6 && c[3] == 4 && c[4] == 1)) {
        printf("SELFTEST FAIL: star K_{1,4} sequence wrong\n"); fails++;
    }
    if (!is_unimodal(c, d)) { printf("SELFTEST FAIL: star must be unimodal\n"); fails++; }

    N = 5; for (int i = 0; i < 5; i++) L[i] = i;          /* path P_5 */
    parents_from_levels();
    d = independence_poly(c);
    /* i_k(P_n) = C(n-k+1, k): 1,5,6,1 */
    if (!(c[0] == 1 && c[1] == 5 && c[2] == 6 && c[3] == 1)) {
        printf("SELFTEST FAIL: path P_5 sequence wrong\n"); fails++;
    }

    /* PLANTED FAILURES: the unimodality test must REJECT non-unimodal input
     * and ACCEPT plateaus. A test that always passes proves nothing. */
    u64 bad[] = {1, 5, 2, 7, 1};
    if (is_unimodal(bad, 4)) {
        printf("SELFTEST FAIL: non-unimodal sequence ACCEPTED\n"); fails++;
    }
    u64 plateau[] = {1, 4, 4, 4, 2};
    if (!is_unimodal(plateau, 4)) {
        printf("SELFTEST FAIL: plateau rejected (plateaus are unimodal)\n");
        fails++;
    }
    u64 rising[] = {1, 2, 3, 4};
    if (!is_unimodal(rising, 3)) {
        printf("SELFTEST FAIL: monotone sequence rejected\n"); fails++;
    }
    printf("SELFTEST %s\tfailures=%d\n", fails ? "FAIL" : "PASS", fails);
    return fails;
}

int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "--selftest") == 0)
        return selftest() ? 1 : 0;
    if (argc < 2) {
        fprintf(stderr, "usage: %s <n> [shard] [nshards]\n"
                        "       %s --selftest\n", argv[0], argv[0]);
        return 2;
    }
    N = atoi(argv[1]);
    long long shard = argc > 2 ? atoll(argv[2]) : 0;
    long long nshards = argc > 3 ? atoll(argv[3]) : 1;
    if (N < 1 || N >= MAXN) { fprintf(stderr, "n out of range\n"); return 2; }

    u64 trees = 0, violations = 0;
    long long which = 0;
    u64 c[MAXN + 1];
    clock_t t0 = clock();

    if (N <= 2) {
        /* The single tree on 1 or 2 vertices is generated by no loop, so it
         * must be attributed to exactly ONE shard — otherwise every shard
         * claims it and the cumulative count is inflated by (nshards-1) per
         * such n. This is why the totals are checked against A000055 per n
         * AND cumulatively: the per-n selftest is unsharded and cannot see it. */
        trees = (shard == 0) ? 1 : 0;
    } else {
        wrom_start();
        do {
            if (!is_primary()) continue;
            if (which++ % nshards != shard) continue;
            trees++;
            parents_from_levels();
            int d = independence_poly(c);
            if (!is_unimodal(c, d)) {
                violations++;
                printf("VIOLATION\tn=%d\tlevels=", N);
                for (int i = 0; i < N; i++) printf("%d%s", L[i],
                                                   i == N - 1 ? "\t" : ",");
                printf("seq=");
                for (int i = 0; i <= d; i++)
                    printf("%llu%s", (unsigned long long)c[i],
                           i == d ? "\n" : ",");
                fflush(stdout);
            }
        } while (wrom_advance());
    }
    printf("SUMMARY\tn=%d\tshard=%lld/%lld\ttrees=%llu\tviolations=%llu"
           "\tsecs=%.1f\n", N, shard, nshards, (unsigned long long)trees,
           (unsigned long long)violations,
           (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 0;
}

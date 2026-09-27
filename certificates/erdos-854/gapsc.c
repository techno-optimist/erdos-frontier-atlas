/*
 * gapsc.c -- which even gaps occur between consecutive integers coprime to
 * the primorial p_n#?  C port of coprime_gaps.Cover (node for node).
 *
 * Gap t = 2m occurs iff there are residues c_p (x = -c_p mod p) with c_p != 0,
 * c_p != t (mod p), covering every j in 1..t-1 (p divides x + j iff
 * j = c_p mod p); CRT realises any choice.  Prime 2 must take the odd
 * positions, so the odd primes cover k = j/2 in 1..m-1 with classes d_p,
 * d_p != 0 and d_p != m (mod p).  Exhaustive DFS: branch on the uncovered k
 * with the fewest candidate primes; prune when the best-case coverage of the
 * unassigned primes is short.
 *
 * usage: gapsc n [t]
 *   gapsc n     try t = 4, 6, ... until the first absent gap:
 *               "GAP n t occurs nodes [res p:c ...]" per t, then "TERM n a"
 *   gapsc n t   decide the single gap t
 * Positions k < 128 (t <= 256).
 */
#include <stdio.h>
#include <stdlib.h>

typedef unsigned __int128 u128;
static int nq, qs[64], M;
static u128 CL[64][512];        /* CL[i][d] = {k in 1..M-1 : k = d mod qs[i]} */
static int used[64], asg[64];
static long long nodes;
static u128 FULL;

static int popc(u128 x) { return __builtin_popcountll((unsigned long long)x) + __builtin_popcountll((unsigned long long)(x >> 64)); }

static int dfs(u128 cov) {
    nodes++;
    u128 unc = FULL & ~cov;
    if (!unc) return 1;
    int need = popc(unc), capsum = 0;
    for (int i = 0; i < nq; i++) if (!used[i]) {
        int q = qs[i], best = 0;
        for (int d = 1; d < q; d++) {
            if (d == M % q) continue;
            int c = popc(CL[i][d] & unc);
            if (c > best) best = c;
        }
        capsum += best;
    }
    if (capsum < need) return 0;
    int bestk = -1, bestc = 1 << 30;
    for (int k = 1; k < M; k++) {
        if (!((unc >> k) & 1)) continue;
        int c = 0;
        for (int i = 0; i < nq; i++) if (!used[i]) {
            int q = qs[i], d = k % q;
            if (d != 0 && d != M % q) c++;
        }
        if (c < bestc) { bestc = c; bestk = k; if (c == 0) return 0; }
    }
    int k = bestk;
    for (int i = 0; i < nq; i++) {
        if (used[i]) continue;
        int q = qs[i], d = k % q;
        if (d == 0 || d == M % q) continue;
        used[i] = 1; asg[i] = d;
        if (dfs(cov | CL[i][d])) return 1;
        used[i] = 0;
    }
    return 0;
}

static int occurs(int t) {
    M = t / 2;
    FULL = 0;
    for (int k = 1; k < M; k++) FULL |= (u128)1 << k;
    for (int i = 0; i < nq; i++) {
        int q = qs[i];
        for (int d = 0; d < q; d++) {
            u128 m = 0;
            for (int k = d; k < M; k += q) if (k >= 1) m |= (u128)1 << k;
            CL[i][d] = m;
        }
        used[i] = 0;
    }
    nodes = 0;
    return dfs(0);
}

static void report(int n, int t, int r) {
    printf("GAP %d %d %d %lld", n, t, r, nodes);
    if (r) {
        printf(" res 2:1");
        for (int i = 0; i < nq; i++)
            if (used[i]) printf(" %d:%d", qs[i], (2 * asg[i]) % qs[i]);   /* c_p = 2 d_p */
    }
    printf("\n");
    fflush(stdout);
}

int main(int argc, char **argv) {
    if (argc != 2 && argc != 3) { fprintf(stderr, "usage: %s n [t]\n", argv[0]); return 1; }
    int n = atoi(argv[1]);
    if (n < 2 || n > 60) { fprintf(stderr, "need 2 <= n <= 60\n"); return 1; }
    int all[64], cnt = 0;
    for (int q = 2; cnt < 64; q++) {
        int ok = 1;
        for (int i = 0; i < cnt && all[i] * all[i] <= q; i++) if (q % all[i] == 0) ok = 0;
        if (ok) all[cnt++] = q;
    }
    nq = n - 1;
    for (int i = 0; i < nq; i++) qs[i] = all[i + 1];               /* the odd primes */
    if (argc == 3) {
        int t = atoi(argv[2]);
        if (t < 4 || t % 2 || t > 256) { fprintf(stderr, "need even 4 <= t <= 256\n"); return 1; }
        report(n, t, occurs(t));
        return 0;
    }
    for (int t = 4; t <= 256; t += 2) {                            /* gap 2: x = p_n# - 1 */
        int r = occurs(t);
        report(n, t, r);
        if (!r) { printf("TERM %d %d\n", n, t); return 0; }
    }
    fprintf(stderr, "no absent gap up to 256\n");
    return 2;
}

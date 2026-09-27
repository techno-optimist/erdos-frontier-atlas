/*
 * xcheck.c -- independent cross-check for k-chord pancyclic systems C_n + k chords.
 *
 * Deliberately different from pancyclic.py at every layer:
 *   - NO symmetry reduction: every labeled skeleton (k distinct chords on t
 *     cyclically ordered endpoints, every endpoint used) is searched;
 *   - cycles of the skeleton multigraph are enumerated by DFS (rooted at the
 *     least vertex), not by the parity recurrence;
 *   - branching always targets the SMALLEST uncovered length.
 * Shared (mathematically justified) rules: domain and capacity exclusion.
 *
 * usage: xcheck k nlo nhi   -> one summary line per n, witnesses on "SAT" lines
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXT 16
#define MAXK 8
#define MAXF 1024
#define MAXN 400

static int K, T, N;
static int ca[MAXK], cb[MAXK];
static int nf, fcnt[MAXF];
static uint32_t fmask[MAXF];
static int lb[MAXT];
static long long nodes;

/* ---------- cycle enumeration on the skeleton multigraph ---------- */
static int eu[MAXT + MAXK], ev[MAXT + MAXK], ne;
static int adjn[MAXT], adje[MAXT][MAXT + MAXK];

static void add_form(int c, uint32_t m) {
    for (int i = 0; i < nf; i++)
        if (fcnt[i] == c && fmask[i] == m) return;
    if (nf >= MAXF) { fprintf(stderr, "MAXF\n"); exit(2); }
    fcnt[nf] = c; fmask[nf] = m; nf++;
}

static int st_s, st_first;
static void dfs_cycles(int v, uint32_t vis, int len, int c, uint32_t m) {
    for (int j = 0; j < adjn[v]; j++) {
        int e = adje[v][j];
        int w = (eu[e] == v) ? ev[e] : eu[e];
        int ec = (e >= T), em = (e < T);
        if (w == st_s) {
            if (len >= 2 || (len == 1 && e != st_first))
                add_form(c + ec, m | (em ? (1u << e) : 0));
        } else if (w > st_s && !(vis >> w & 1)) {
            if (len == 0) st_first = e;
            dfs_cycles(w, vis | (1u << w), len + 1, c + ec, m | (em ? (1u << e) : 0));
        }
    }
}

static void build_forms(void) {
    ne = 0;
    for (int i = 0; i < T; i++) { eu[ne] = i; ev[ne] = (i + 1) % T; ne++; }      /* arcs */
    for (int j = 0; j < K; j++) { eu[ne] = ca[j]; ev[ne] = cb[j]; ne++; }        /* chords */
    for (int v = 0; v < T; v++) adjn[v] = 0;
    for (int e = 0; e < ne; e++) {
        adje[eu[e]][adjn[eu[e]]++] = e;
        if (ev[e] != eu[e]) adje[ev[e]][adjn[ev[e]]++] = e;
    }
    nf = 0;
    for (int s = 0; s < T; s++) { st_s = s; dfs_cycles(s, 1u << s, 0, 0, 0); }
    for (int i = 0; i < T; i++) lb[i] = 1;
    for (int j = 0; j < K; j++)
        for (int i = 0; i < T; i++) {
            int a = i, b = (i + 1) % T;
            if ((ca[j] == a && cb[j] == b) || (ca[j] == b && cb[j] == a)) lb[i] = 2;
        }
}

/* ---------------------------- search ------------------------------- */
static int wit[MAXT];

static int covers(const int *x) {
    static unsigned char hit[MAXN + 2];
    memset(hit, 0, N + 2);
    for (int f = 0; f < nf; f++) {
        int s = fcnt[f];
        for (int i = 0; i < T; i++) if (fmask[f] >> i & 1) s += x[i];
        if (s >= 3 && s <= N) hit[s] = 1;
    }
    for (int l = 3; l <= N; l++) if (!hit[l]) return 0;
    return 1;
}

static long long ncomp(int s, int m) {             /* weak compositions, capped */
    if (m == 0) return s == 0;
    long long r = 1;
    for (int i = 1; i < m; i++) { r = r * (s + i) / i; if (r > (1LL << 40)) return 1LL << 40; }
    return r;
}

static int search(int *x);

static int enum_side(int *x, const int *idx, int cnt, int pos, int left) {
    if (pos == cnt - 1) {
        x[idx[pos]] = lb[idx[pos]] + left;
        int r = search(x);
        x[idx[pos]] = 0;
        return r;
    }
    for (int y = 0; y <= left; y++) {
        x[idx[pos]] = lb[idx[pos]] + y;
        if (enum_side(x, idx, cnt, pos + 1, left - y)) { x[idx[pos]] = 0; return 1; }
    }
    x[idx[pos]] = 0;
    return 0;
}

static int search(int *x) {
    nodes++;
    int nfree = 0, fixed = 0, lbfree = 0, freei[MAXT];
    uint32_t freem = 0;
    for (int i = 0; i < T; i++) {
        if (x[i]) fixed += x[i];
        else { freei[nfree++] = i; freem |= 1u << i; lbfree += lb[i]; }
    }
    int R = N - fixed - lbfree;
    if (R < 0) return 0;
    if (nfree <= 1) {
        int y[MAXT];
        memcpy(y, x, sizeof(int) * T);
        if (nfree == 1) y[freei[0]] = lb[freei[0]] + R;
        if (covers(y)) { memcpy(wit, y, sizeof(int) * T); return 1; }
        return 0;
    }
    unsigned char cov[MAXN + 2];
    memset(cov, 0, N + 2);
    int ra[MAXF]; uint32_t rm[MAXF]; int nr = 0;
    for (int f = 0; f < nf; f++) {
        int a = fcnt[f];
        for (int i = 0; i < T; i++)
            if (fmask[f] >> i & 1) a += x[i] ? x[i] : lb[i];
        uint32_t mf = fmask[f] & freem;
        if (mf == 0) { if (a >= 3 && a <= N) cov[a] = 1; }
        else if (mf == freem) { if (a + R >= 3 && a + R <= N) cov[a + R] = 1; }
        else {
            int dup = 0;
            for (int r = 0; r < nr; r++) if (ra[r] == a && rm[r] == mf) { dup = 1; break; }
            if (!dup) { ra[nr] = a; rm[nr] = mf; nr++; }
        }
    }
    int need = 0, lo = -1, hi = -1;
    for (int l = 3; l <= N; l++) if (!cov[l]) { need++; if (lo < 0) lo = l; hi = l; }
    if (!need) {
        int y[MAXT];
        memcpy(y, x, sizeof(int) * T);
        for (int j = 0; j < nfree; j++) y[freei[j]] = lb[freei[j]];
        y[freei[0]] += R;
        if (!covers(y)) { fprintf(stderr, "internal: constant cover failed\n"); exit(3); }
        memcpy(wit, y, sizeof(int) * T);
        return 1;
    }
    int useful = 0;
    for (int r = 0; r < nr; r++) if (ra[r] <= hi && ra[r] + R >= lo) useful++;
    if (useful < need) return 0;                                   /* capacity */
    for (int l = lo; l <= hi; l++) {                               /* domain */
        if (cov[l]) continue;
        int ok = 0;
        for (int r = 0; r < nr; r++) if (ra[r] <= l && l <= ra[r] + R) { ok = 1; break; }
        if (!ok) return 0;
    }
    int l = lo;                                                    /* smallest uncovered */
    for (int r = 0; r < nr; r++) {
        if (!(ra[r] <= l && l <= ra[r] + R)) continue;
        int q = l - ra[r];
        int k1 = __builtin_popcount(rm[r]);
        int idx[MAXT], cnt = 0, total;
        if (ncomp(q, k1) <= ncomp(R - q, nfree - k1)) {
            for (int j = 0; j < nfree; j++) if (rm[r] >> freei[j] & 1) idx[cnt++] = freei[j];
            total = q;
        } else {
            for (int j = 0; j < nfree; j++) if (!(rm[r] >> freei[j] & 1)) idx[cnt++] = freei[j];
            total = R - q;
        }
        if (enum_side(x, idx, cnt, 0, total)) return 1;
    }
    return 0;
}

/* ------------------------- enumeration ----------------------------- */
static int P, pa[MAXT * MAXT], pb[MAXT * MAXT];
static long long elig[MAXN + 1], satc[MAXN + 1], labeled[MAXT + 1];
static long long nodesum[MAXN + 1];
static int nlo, nhi;
static int printed[MAXN + 1];

static void process(void) {
    build_forms();
    labeled[T]++;
    int sumlb = 0;
    for (int i = 0; i < T; i++) sumlb += lb[i];
    for (N = nlo; N <= nhi; N++) {
        if (nf < N - 2 || sumlb > N) continue;
        elig[N]++;
        int x[MAXT] = {0};
        long long before = nodes;
        int r = search(x);
        nodesum[N] += nodes - before;
        if (r) {
            satc[N]++;
            if (printed[N] < 3) {
                printed[N]++;
                int pos[MAXT]; pos[0] = 0;
                for (int i = 1; i < T; i++) pos[i] = pos[i - 1] + wit[i - 1];
                printf("SAT n=%d chords", N);
                for (int j = 0; j < K; j++) {
                    int u = pos[ca[j]], v = pos[cb[j]];
                    printf(" %d-%d", u < v ? u : v, u < v ? v : u);
                }
                printf("\n");
            }
        }
    }
}

static void rec(int start, int depth, uint32_t used) {
    if (depth == K) { if (used == (1u << T) - 1) process(); return; }
    int unc = T - __builtin_popcount(used);
    if (unc > 2 * (K - depth)) return;
    for (int p = start; p < P; p++) {
        ca[depth] = pa[p]; cb[depth] = pb[p];
        rec(p + 1, depth + 1, used | (1u << pa[p]) | (1u << pb[p]));
    }
}

int main(int argc, char **argv) {
    if (argc != 4) { fprintf(stderr, "usage: %s k nlo nhi\n", argv[0]); return 1; }
    K = atoi(argv[1]); nlo = atoi(argv[2]); nhi = atoi(argv[3]);
    if (K < 1 || K > MAXK || nlo < 3 || nhi > MAXN || nlo > nhi) return 1;
    for (T = 2; T <= 2 * K && T <= MAXT; T++) {
        P = 0;
        for (int a = 0; a < T; a++) for (int b = a + 1; b < T; b++) { pa[P] = a; pb[P] = b; P++; }
        rec(0, 0, 0);
    }
    for (int t = 2; t <= 2 * K; t++) if (labeled[t]) printf("LABELED t=%d %lld\n", t, labeled[t]);
    for (int n = nlo; n <= nhi; n++)
        printf("SUMMARY k=%d n=%d eligible_labeled=%lld sat_labeled=%lld nodes=%lld\n",
               K, n, elig[n], satc[n], nodesum[n]);
    return 0;
}

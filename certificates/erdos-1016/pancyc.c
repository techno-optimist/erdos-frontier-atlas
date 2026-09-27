/*
 * pancyc.c -- C port of pancyclic.Search, one skeleton per dihedral class,
 * for k-chord systems C_n + k chords.  It carries the k = 7 exhaustion of
 * verify_k7.py, where the Python reference would take about 12 CPU-hours.
 *
 * Mirrors pancyclic.py step for step (class order, parity cycle forms, state
 * memo, target shortlist, candidate order, composition order), so on k <= 6
 * its per-class verdicts AND node counts must equal the Python reference;
 * verify_k7.py checks this against RESULT.json at all 45 k = 6 levels.
 *
 * usage: pancyc k nlo nhi [mode [shard nshards]]
 *   mode "census" (default): search every eligible class at every n
 *   mode "first":            stop each n at the first pancyclic class, trying
 *                            classes in descending distinct-form order
 *   mode "classes":          as census, plus one CLASS line per eligible class
 *                            (verdict and node count) for per-class comparison
 *   shard/nshards (census only): search only classes with index % nshards ==
 *                            shard; per-class memos make LEVEL counts additive
 * output: CLASSES / ORBITSUM / MAXFORMS header, then per n a LEVEL line; SAT
 *         lines carry the class index, skeleton and arc lengths.  ORBITSUM is
 *         the sum over classes of 2t/|stabiliser|, which must equal the number
 *         of labeled skeletons (pancyclic.labeled_count_formula); a LEVEL's
 *         eligible_labeled is the same orbit sum over its eligible classes,
 *         comparable with the labeled counts of xcheck.c.
 * Arc lengths are packed into 8-bit memo keys, hence n <= 255.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXT 16
#define MAXK 8
#define MAXF 520
#define MAXN 255

/* a class's nf distinct cycle forms (c chords, arc mask m) live in the pools
   FC/FM at offset off; orb is its orbit size, the number of labeled skeletons
   it stands for */
typedef struct { int t; unsigned char a[MAXK], b[MAXK]; int nf, orb; long off; } Class;

static int K;
static Class *cls; static long ncls, capcls;
static unsigned short *FC; static uint32_t *FM; static long fpool, fcap;
static long long orbitsum;

/* ------------------------- class enumeration ----------------------- */
static int T, P, pa[MAXT * MAXT], pb[MAXT * MAXT];
static int cha[MAXK], chb[MAXK];

static int cmp_pairs(const int *xa, const int *xb, const int *ya, const int *yb, int k) {
    for (int i = 0; i < k; i++) {
        if (xa[i] != ya[i]) return xa[i] < ya[i] ? -1 : 1;
        if (xb[i] != yb[i]) return xb[i] < yb[i] ? -1 : 1;
    }
    return 0;
}

static void sort_pairs(int *xa, int *xb, int k) {
    for (int i = 1; i < k; i++) {
        int a = xa[i], b = xb[i], j = i - 1;
        while (j >= 0 && (xa[j] > a || (xa[j] == a && xb[j] > b))) { xa[j + 1] = xa[j]; xb[j + 1] = xb[j]; j--; }
        xa[j + 1] = a; xb[j + 1] = b;
    }
}

/* 0 if some dihedral image is lexicographically smaller, else the number of
   the 2T group elements (s, sg) fixing the chord set (its stabiliser order) */
static int is_canonical(void) {
    int ia[MAXK], ib[MAXK], stab = 0;
    for (int s = 0; s < T; s++)
        for (int sg = 0; sg < 2; sg++) {
            for (int i = 0; i < K; i++) {
                int a = sg ? ((-cha[i] + s) % T + T) % T : (cha[i] + s) % T;
                int b = sg ? ((-chb[i] + s) % T + T) % T : (chb[i] + s) % T;
                if (a < b) { ia[i] = a; ib[i] = b; } else { ia[i] = b; ib[i] = a; }
            }
            sort_pairs(ia, ib, K);
            int c = cmp_pairs(ia, ib, cha, chb, K);
            if (c < 0) return 0;
            if (c == 0) stab++;
        }
    return stab;
}

static int connected(int t, const int *ca, const int *cb, int k, int sub, uint32_t mask) {
    int parent[MAXT];
    for (int i = 0; i < t; i++) parent[i] = i;
    uint32_t touched = 0;
#define FIND(u) ({ int _u = (u); while (parent[_u] != _u) { parent[_u] = parent[parent[_u]]; _u = parent[_u]; } _u; })
    for (int j = 0; j < k; j++) if (sub >> j & 1) {
        int ra = FIND(ca[j]), rb = FIND(cb[j]); parent[ra] = rb;
        touched |= (1u << ca[j]) | (1u << cb[j]);
    }
    for (int i = 0; i < t; i++) if (mask >> i & 1) {
        int j = (i + 1) % t; int ra = FIND(i), rb = FIND(j); parent[ra] = rb;
        touched |= (1u << i) | (1u << j);
    }
    if (!touched) return 0;
    int root = -1;
    for (int u = 0; u < t; u++) if (touched >> u & 1) {
        int r = FIND(u);
        if (root < 0) root = r; else if (r != root) return 0;
    }
    return 1;
#undef FIND
}

static int form_cmp(const void *x, const void *y) {
    const uint64_t *a = x, *b = y;
    return (*a > *b) - (*a < *b);
}

static void add_class(int stab) {
    if (ncls == capcls) { capcls = capcls ? capcls * 2 : 4096; cls = realloc(cls, capcls * sizeof(Class)); }
    if (!cls) { fprintf(stderr, "out of memory\n"); exit(2); }
    Class *C = &cls[ncls++];
    C->t = T;
    if ((2 * T) % stab) { fprintf(stderr, "stabiliser order does not divide 2t\n"); exit(3); }
    C->orb = (2 * T) / stab;
    orbitsum += C->orb;
    for (int i = 0; i < K; i++) { C->a[i] = cha[i]; C->b[i] = chb[i]; }
    /* cycle forms by the parity recurrence, as in pancyclic.cycle_forms */
    uint64_t keys[MAXF]; int nk = 0;
    uint32_t full = (T == 32) ? 0xffffffffu : ((1u << T) - 1);
    keys[nk++] = ((uint64_t)0 << 32) | full;
    for (int sub = 1; sub < (1 << K); sub++) {
        int deg[MAXT] = {0};
        for (int j = 0; j < K; j++) if (sub >> j & 1) { deg[cha[j]]++; deg[chb[j]]++; }
        int ok = 1;
        for (int i = 0; i < T; i++) if (deg[i] > 2) ok = 0;
        if (!ok) continue;
        uint32_t mask = 0; int r = 0;
        for (int i = 0; i < T; i++) { r ^= deg[i] & 1; if (r) mask |= 1u << i; }
        if (mask >> (T - 1) & 1) { fprintf(stderr, "parity inconsistent\n"); exit(3); }
        for (int w = 0; w < 2; w++) {
            uint32_t m = w ? (full ^ mask) : mask;
            int good = 1;
            for (int i = 0; i < T && good; i++) {
                int d = deg[i] + (int)(m >> ((i - 1 + T) % T) & 1) + (int)(m >> i & 1);
                if (d != 0 && d != 2) good = 0;
            }
            if (good && connected(T, cha, chb, K, sub, m))
                keys[nk++] = ((uint64_t)__builtin_popcount(sub) << 32) | m;
        }
    }
    qsort(keys, nk, sizeof(uint64_t), form_cmp);
    if (fpool + nk > fcap) {
        fcap = fcap ? 2 * fcap : 1 << 20;
        FC = realloc(FC, fcap * sizeof(unsigned short)); FM = realloc(FM, fcap * sizeof(uint32_t));
        if (!FC || !FM) { fprintf(stderr, "out of memory\n"); exit(2); }
    }
    int nf = 0;
    C->off = fpool;
    for (int i = 0; i < nk; i++) if (i == 0 || keys[i] != keys[i - 1]) {
        FC[fpool + nf] = (unsigned short)(keys[i] >> 32); FM[fpool + nf] = (uint32_t)keys[i]; nf++;
    }
    C->nf = nf;
    fpool += nf;
}

static void rec(int start, int depth, uint32_t used) {
    if (depth == K) {
        if (used == (T == 32 ? 0xffffffffu : (1u << T) - 1)) { int st = is_canonical(); if (st) add_class(st); }
        return;
    }
    if (T - __builtin_popcount(used) > 2 * (K - depth)) return;
    int u = 0; while (u < T && (used >> u & 1)) u++;
    for (int p = start; p < P; p++) {
        if (u < T && pa[p] > u) break;
        cha[depth] = pa[p]; chb[depth] = pb[p];
        rec(p + 1, depth + 1, used | (1u << pa[p]) | (1u << pb[p]));
    }
}

/* ------------------------------ search ------------------------------ */
static const Class *C;
static int N, t_, lb[MAXT];
static long long nodes;
static int wit[MAXT];
typedef unsigned __int128 u128;
static u128 W[MAXT + 1][MAXN + 1];

/* dead-state memo: open addressing on 128-bit keys (t <= 16 bytes) */
typedef struct { uint64_t lo, hi; } Key;
static Key *tab; static unsigned char *used_; static size_t tabsz, tabn;
static Key keyof(const int *x) {
    Key k = {0, 0};
    for (int i = 0; i < t_; i++) { if (i < 8) k.lo |= (uint64_t)x[i] << (8 * i); else k.hi |= (uint64_t)x[i] << (8 * (i - 8)); }
    return k;
}
static size_t hk(Key k) { uint64_t h = k.lo * 0x9E3779B97F4A7C15ULL ^ (k.hi + 0x632BE59BD9B4E019ULL) * 0xC2B2AE3D27D4EB4FULL; h ^= h >> 29; return (size_t)h; }
static void tab_reset(void) { if (!tab) { tabsz = 1 << 16; tab = malloc(tabsz * sizeof(Key)); used_ = calloc(tabsz, 1); } else memset(used_, 0, tabsz); tabn = 0; }
static int tab_has(Key k) { size_t i = hk(k) & (tabsz - 1); while (used_[i]) { if (tab[i].lo == k.lo && tab[i].hi == k.hi) return 1; i = (i + 1) & (tabsz - 1); } return 0; }
static void tab_add(Key k);
static void tab_grow(void) {
    Key *ot = tab; unsigned char *ou = used_; size_t os = tabsz;
    tabsz *= 2; tab = malloc(tabsz * sizeof(Key)); used_ = calloc(tabsz, 1); tabn = 0;
    for (size_t i = 0; i < os; i++) if (ou[i]) tab_add(ot[i]);
    free(ot); free(ou);
}
static void tab_add(Key k) {
    if (2 * (tabn + 1) > tabsz) tab_grow();
    size_t i = hk(k) & (tabsz - 1);
    while (used_[i]) { if (tab[i].lo == k.lo && tab[i].hi == k.hi) return; i = (i + 1) & (tabsz - 1); }
    used_[i] = 1; tab[i] = k; tabn++;
}

static int covers(const int *x) {
    unsigned char hit[MAXN + 2]; memset(hit, 0, N + 2);
    const unsigned short *cc = FC + C->off; const uint32_t *cm = FM + C->off;
    for (int f = 0; f < C->nf; f++) {
        int s = cc[f]; uint32_t m = cm[f];
        for (int i = 0; m; i++, m >>= 1) if (m & 1) s += x[i];
        if (s >= 3 && s <= N) hit[s] = 1;
    }
    for (int l = 3; l <= N; l++) if (!hit[l]) return 0;
    return 1;
}

static int dfs(int *x);

static int enum_side(int *x, const int *idx, int cnt, int pos, int left) {
    if (pos == cnt - 1) {
        x[idx[pos]] = lb[idx[pos]] + left;
        int r = dfs(x);
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

typedef struct { int a; uint32_t mf; } Res;
static int res_cmp(const void *x, const void *y) {
    const Res *p = x, *q = y;
    if (p->a != q->a) return p->a < q->a ? -1 : 1;
    return (p->mf > q->mf) - (p->mf < q->mf);
}
static int *g_ncand;
static int need_cmp(const void *x, const void *y) {
    int l1 = *(const int *)x, l2 = *(const int *)y;
    if (g_ncand[l1] != g_ncand[l2]) return g_ncand[l1] < g_ncand[l2] ? -1 : 1;
    return (l1 > l2) - (l1 < l2);
}

static int dfs(int *x) {
    Key key = keyof(x);
    if (tab_has(key)) return 0;
    nodes++;
    int nfree = 0, freei[MAXT], fixed = 0, lbfree = 0; uint32_t freem = 0;
    for (int i = 0; i < t_; i++) {
        if (x[i]) fixed += x[i];
        else { freei[nfree++] = i; freem |= 1u << i; lbfree += lb[i]; }
    }
    int R = N - fixed - lbfree;
    if (R < 0) { tab_add(key); return 0; }
    if (nfree <= 1) {
        int y[MAXT]; memcpy(y, x, sizeof(int) * t_);
        if (nfree) y[freei[0]] = lb[freei[0]] + R;
        if (covers(y)) { memcpy(wit, y, sizeof(int) * t_); return 1; }
        tab_add(key); return 0;
    }
    int base[MAXT];
    for (int i = 0; i < t_; i++) base[i] = x[i] ? x[i] : lb[i];
    unsigned char cov[MAXN + 2]; memset(cov, 0, N + 2);
    Res res[MAXF]; int nr = 0;
    const unsigned short *cc = FC + C->off; const uint32_t *cm = FM + C->off;
    for (int f = 0; f < C->nf; f++) {
        int a = cc[f]; uint32_t m = cm[f];
        for (int i = 0; m; i++, m >>= 1) if (m & 1) a += base[i];
        uint32_t mf = cm[f] & freem;
        if (mf == 0) { if (a <= N) cov[a] = 1; }
        else if (mf == freem) { if (a + R <= N) cov[a + R] = 1; }
        else { res[nr].a = a; res[nr].mf = mf; nr++; }
    }
    qsort(res, nr, sizeof(Res), res_cmp);
    { int w = 0; for (int r = 0; r < nr; r++) if (r == 0 || res[r].a != res[w - 1].a || res[r].mf != res[w - 1].mf) res[w++] = res[r]; nr = w; }
    int need[MAXN + 2], nn = 0;
    for (int l = 3; l <= N; l++) if (!cov[l]) need[nn++] = l;
    if (!nn) {
        int y[MAXT]; memcpy(y, base, sizeof(int) * t_);
        y[freei[0]] += R;
        if (!covers(y)) { fprintf(stderr, "internal: constant cover\n"); exit(3); }
        memcpy(wit, y, sizeof(int) * t_);
        return 1;
    }
    int lo = need[0], hi = need[nn - 1];
    Res use[MAXF]; int nu = 0;
    for (int r = 0; r < nr; r++) if (res[r].a <= hi && res[r].a + R >= lo) use[nu++] = res[r];
    if (nu < nn) { tab_add(key); return 0; }                         /* capacity */
    int diff[MAXN + 3]; memset(diff, 0, sizeof(int) * (N + 3));
    for (int r = 0; r < nu; r++) {
        int s = use[r].a > 3 ? use[r].a : 3, e = use[r].a + R < N ? use[r].a + R : N;
        if (s <= e) { diff[s]++; diff[e + 1]--; }
    }
    int ncand[MAXN + 1], run = 0;
    for (int l = 0; l <= N; l++) { run += diff[l]; ncand[l] = run; }
    for (int j = 0; j < nn; j++) if (ncand[need[j]] == 0) { tab_add(key); return 0; }   /* domain */
    int srt[MAXN + 2]; for (int j = 0; j < nn; j++) srt[j] = need[j];
    g_ncand = ncand; qsort(srt, nn, sizeof(int), need_cmp);
    int shortl[8], ns = 0;
    for (int j = 0; j < nn && j < 4; j++) shortl[ns++] = srt[j];
    int ext[2] = {need[0], need[nn - 1]};
    for (int e = 0; e < 2; e++) { int in = 0; for (int j = 0; j < ns; j++) if (shortl[j] == ext[e]) in = 1; if (!in) shortl[ns++] = ext[e]; }
    u128 bestc = 0; int bestl = -1;
    for (int j = 0; j < ns; j++) {
        int l = shortl[j]; u128 cost = 0;
        for (int r = 0; r < nu; r++) if (use[r].a <= l && l <= use[r].a + R) {
            int k1 = __builtin_popcount(use[r].mf), q = l - use[r].a;
            u128 c1 = W[k1][q], c2 = W[nfree - k1][R - q];
            cost += c1 < c2 ? c1 : c2;
        }
        if (bestl < 0 || cost < bestc) { bestc = cost; bestl = l; }
    }
    int l = bestl;
    for (int r = 0; r < nu; r++) {
        if (!(use[r].a <= l && l <= use[r].a + R)) continue;
        int k1 = __builtin_popcount(use[r].mf), q = l - use[r].a;
        uint32_t side; int total;
        if (W[k1][q] <= W[nfree - k1][R - q]) { side = use[r].mf; total = q; }
        else { side = freem ^ use[r].mf; total = R - q; }
        int idx[MAXT], cnt = 0;
        for (int j = 0; j < nfree; j++) if (side >> freei[j] & 1) idx[cnt++] = freei[j];
        if (enum_side(x, idx, cnt, 0, total)) return 1;
    }
    tab_add(key);
    return 0;
}

static int decide(const Class *cl, int n, long long *nd) {
    C = cl; N = n; t_ = cl->t;
    for (int i = 0; i < t_; i++) lb[i] = 1;
    for (int j = 0; j < K; j++) for (int i = 0; i < t_; i++) {
        int a = i, b = (i + 1) % t_;
        if ((cl->a[j] == a && cl->b[j] == b) || (cl->a[j] == b && cl->b[j] == a)) lb[i] = 2;
    }
    int s = 0; for (int i = 0; i < t_; i++) s += lb[i];
    *nd = 0;
    if (s > n) return 0;
    tab_reset(); nodes = 0;
    int x[MAXT] = {0};
    int r = dfs(x);
    *nd = nodes;
    return r;
}

static int ord_cmp(const void *x, const void *y) {
    long i = *(const long *)x, j = *(const long *)y;
    if (cls[i].nf != cls[j].nf) return cls[i].nf > cls[j].nf ? -1 : 1;
    return (i > j) - (i < j);
}

int main(int argc, char **argv) {
    if (argc != 4 && argc != 5 && argc != 7) { fprintf(stderr, "usage: %s k nlo nhi [census|first [shard nshards]]\n", argv[0]); return 1; }
    K = atoi(argv[1]); int nlo = atoi(argv[2]), nhi = atoi(argv[3]);
    int first = argc > 4 && !strcmp(argv[4], "first");
    int perclass = argc > 4 && !strcmp(argv[4], "classes");
    if (argc > 4 && !first && !perclass && strcmp(argv[4], "census")) { fprintf(stderr, "unknown mode %s\n", argv[4]); return 1; }
    long shard = 0, nshards = 1;
    if (argc == 7) { shard = atol(argv[5]); nshards = atol(argv[6]); }
    if (K < 1 || K > MAXK || nlo < 3 || nlo > nhi || nhi > MAXN) { fprintf(stderr, "bad k or range (need 3 <= nlo <= nhi <= %d)\n", MAXN); return 1; }
    if (nshards < 1 || shard < 0 || shard >= nshards || (first && nshards > 1)) { fprintf(stderr, "bad shard\n"); return 1; }
    for (int m = 0; m <= MAXT; m++) for (int s = 0; s <= MAXN; s++) {
        if (m == 0) { W[m][s] = s == 0; continue; }
        /* C(s+m-1, m-1) exactly: C(s+i, i) = C(s+i-1, i-1) * (s+i) / i */
        u128 v = 1; for (int i = 1; i < m; i++) v = v * (u128)(s + i) / (u128)i;
        W[m][s] = v;
    }
    for (T = 2; T <= 2 * K && T <= MAXT; T++) {
        P = 0;
        for (int a = 0; a < T; a++) for (int b = a + 1; b < T; b++) { pa[P] = a; pb[P] = b; P++; }
        rec(0, 0, 0);
    }
    int maxf = 0; for (long i = 0; i < ncls; i++) if (cls[i].nf > maxf) maxf = cls[i].nf;
    printf("CLASSES k=%d %ld\nORBITSUM k=%d %lld\nMAXFORMS %d\n", K, ncls, K, orbitsum, maxf);
    fflush(stdout);
    long *ord = malloc(ncls * sizeof(long));
    for (long i = 0; i < ncls; i++) ord[i] = i;
    if (first) qsort(ord, ncls, sizeof(long), ord_cmp);
    for (int n = nlo; n <= nhi; n++) {
        long elig = 0, sat = 0; long long nd, tot = 0, elab = 0;
        for (long oi = 0; oi < ncls; oi++) {
            long i = ord[oi];
            if (i % nshards != shard) continue;
            if (cls[i].nf < n - 2) continue;
            elig++; elab += cls[i].orb;
            int r = decide(&cls[i], n, &nd);
            tot += nd;
            if (perclass) {
                printf("CLASS n=%d class=%ld sat=%d nodes=%lld t=%d skel", n, i, r, nd, cls[i].t);
                for (int j = 0; j < K; j++) printf(" %d-%d", cls[i].a[j], cls[i].b[j]);
                printf("\n");
            }
            if (r) {
                sat++;
                printf("SAT n=%d class=%ld t=%d skel", n, i, cls[i].t);
                for (int j = 0; j < K; j++) printf(" %d-%d", cls[i].a[j], cls[i].b[j]);
                printf(" arcs");
                for (int j = 0; j < cls[i].t; j++) printf(" %d", wit[j]);
                printf("\n"); fflush(stdout);
                if (first) break;
            }
        }
        printf("LEVEL k=%d n=%d eligible=%ld eligible_labeled=%lld sat=%ld nodes=%lld%s\n", K, n, elig, elab, sat, tot, first ? " (first-mode)" : nshards > 1 ? " (shard)" : "");
        fflush(stdout);
    }
    return 0;
}

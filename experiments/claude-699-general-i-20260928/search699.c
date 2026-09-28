/* search699.c -- structured search for the i-slices (i >= 3) of Erdos #699.
 *
 *   search699 I X [--plain] [--shard K/J] [--tmax T] [--from LO] [--list]
 *
 * Visits every "special" n <= X (conditions (c) and (d) of the README) and every central
 * candidate (n even, n - 1 smooth), and reports every pair (n, j) with i < j <= n/2 that
 * passes the positional condition (*) at every prime p >= i of C(n, i), together with its
 * exact verdict. Output (one line of stats, then one line per survivor):
 *   stats I X special SUM cand12 central survivors
 *   survivor n j p        (p = least common prime >= i, or 0 for a counterexample)
 * SUM is the sum mod 2^64 of splitmix64(n) over the special n (order independent).
 *
 * The special set is enumerated over (S0, S1) progressions. By default the tail of each
 * progression, where (d) needs S2 >= 2, is walked through sub-progressions n = 2 mod d for the
 * smooth d in (2^k, P 2^k] (P = largest prime <= i): a smooth S2 > 2^k has its least divisor
 * above 2^k in that window. --plain walks every element instead. Both must give the same set.
 * --from LO restricts everything to n > LO, to extend a finished search or sample a window.
 * --list also prints "special n S0 S1 S2 c" for every special n (c = its m passing t <= 2).
 * --tmax T (2 <= T < I) requires (*) only at positions t <= T: a negative control, since the
 * relaxed condition does admit pairs. Requires X < 2^62.
 */
#include <inttypes.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef uint64_t u64;
typedef unsigned __int128 u128;
typedef __int128 i128;

static int I;
static u64 X;
static int NP;
static u64 SP[32];
static u64 PMAX;
static int PLAIN = 0, SHK = 0, SHJ = 1, TMAX = -1;
static u64 FROM = 0;  /* only n > FROM are considered */
static int LIST = 0;  /* print every special n */

static u64 *SM;
static size_t NSM;

static u64 n_special = 0, sum_special = 0, n_cand12 = 0, n_central = 0, n_surv = 0;

static u64 splitmix64(u64 x) {
    u64 z = x + 0x9e3779b97f4a7c15ULL;
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

/* ---------- smooth parts ---------- */
static u64 SPINV[32], SPLIM[32];  /* p * SPINV = 1 mod 2^64; x divisible by p iff x * SPINV <= SPLIM */

static void init_inverses(void) {
    for (int k = 0; k < NP; k++) {
        u64 p = SP[k];
        if (p == 2) continue;
        u64 inv = p;  /* Newton: inv = inv * (2 - p * inv) */
        for (int it = 0; it < 6; it++) inv *= 2 - p * inv;
        SPINV[k] = inv;
        SPLIM[k] = UINT64_MAX / p;
    }
}

static u64 smooth_part(u64 x) {
    u64 s = 1;
    int k = 0;
    if (NP && SP[0] == 2) {
        int e = __builtin_ctzll(x);
        x >>= e;
        s <<= e;
        if (I == 2 && e >= 2) s = 1;
        k = 1;
    }
    for (; k < NP; k++) {
        u64 y = x * SPINV[k];
        if (y > SPLIM[k]) continue;
        u64 p = SP[k], pe = 1;
        int e = 0;
        while (y <= SPLIM[k]) { x = y; pe *= p; e++; y = x * SPINV[k]; }
        if (!(p == (u64)I && e >= 2)) s *= pe;
    }
    return s;
}

static int cmp_u64(const void *a, const void *b) {
    u64 x = *(const u64 *)a, y = *(const u64 *)b;
    return x < y ? -1 : x > y;
}

static void gen_smooth(void) {
    size_t cap = 1 << 16;
    SM = malloc(cap * sizeof(u64));
    NSM = 0;
    SM[NSM++] = 1;
    for (int k = 0; k < NP; k++) {
        u64 p = SP[k];
        int maxe = (p == (u64)I) ? 1 : 64;
        size_t cur = NSM;
        for (size_t a = 0; a < cur; a++) {
            u64 x = SM[a];
            for (int e = 1; e <= maxe; e++) {
                if (x > X / p) break;
                x *= p;
                if (NSM == cap) { cap *= 2; SM = realloc(SM, cap * sizeof(u64)); }
                SM[NSM++] = x;
            }
        }
    }
    qsort(SM, NSM, sizeof(u64), cmp_u64);
}

/* ---------- arithmetic ---------- */
static u64 gcd64(u64 a, u64 b) { while (b) { u64 t = a % b; a = b; b = t; } return a; }

static u64 mulmod(u64 a, u64 b, u64 m) { return (u64)((u128)a * b % m); }

static u64 powmod(u64 a, u64 e, u64 m) {
    u64 r = 1 % m;
    a %= m;
    while (e) { if (e & 1) r = mulmod(r, a, m); a = mulmod(a, a, m); e >>= 1; }
    return r;
}

/* inverse of a mod m (gcd must be 1), m >= 1 */
static u128 invmod128(u128 a, u128 m) {
    if (m == 1) return 0;
    i128 t = 0, nt = 1;
    u128 r = m, nr = a % m;
    while (nr) {
        u128 q = r / nr, tmp = r - q * nr;
        i128 tt = t - (i128)q * nt;
        t = nt; nt = tt; r = nr; nr = tmp;
    }
    if (t < 0) t += (i128)m;
    return (u128)t;
}

static u64 invmod64(u64 a, u64 m) {
    if (m == 1) return 0;
    int64_t t = 0, nt = 1;
    u64 r = m, nr = a % m;
    while (nr) {
        u64 q = r / nr, tmp = r - q * nr;
        int64_t tt = t - (int64_t)q * nt;
        t = nt; nt = tt; r = nr; nr = tmp;
    }
    if (t < 0) t += (int64_t)m;
    return (u64)t;
}

static u128 mulmod128(u128 a, u128 b, u128 m) {
    /* a, b < m < 2^126: double-and-add */
    u128 r = 0;
    a %= m;
    while (b) {
        if (b & 1) { r += a; if (r >= m) r -= m; }
        a <<= 1; if (a >= m) a -= m;
        b >>= 1;
    }
    return r;
}

/* (r1 mod m1) with (r2 mod m2), coprime, m1*m2 < 2^126 */
static void crt2(u128 r1, u128 m1, u128 r2, u128 m2, u128 *r, u128 *m) {
    u128 inv = invmod128(m1 % m2, m2);
    u128 diff = (r2 % m2 + m2 - r1 % m2) % m2;
    u128 t = (m2 < ((u128)1 << 63) && inv < ((u128)1 << 63)) ? (diff * inv) % m2 : mulmod128(diff, inv, m2);
    *m = m1 * m2;
    *r = r1 + m1 * t;
}

static int is_prime64(u64 n) {
    static const u64 sp[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    if (n < 2) return 0;
    for (int k = 0; k < 12; k++) {
        if (n % sp[k] == 0) return n == sp[k];
    }
    u64 d = n - 1;
    int s = 0;
    while (!(d & 1)) { d >>= 1; s++; }
    for (int k = 0; k < 12; k++) {
        u64 x = powmod(sp[k], d, n);
        if (x == 1 || x == n - 1) continue;
        int ok = 0;
        for (int r = 1; r < s; r++) {
            x = mulmod(x, x, n);
            if (x == n - 1) { ok = 1; break; }
        }
        if (!ok) return 0;
    }
    return 1;
}

static u64 rng_state = 699;
static u64 rnd(void) { rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL; return rng_state >> 11; }

static u64 brent(u64 n) {
    for (;;) {
        u64 y = rnd() % n, c = rnd() % (n - 1) + 1, m = 128, g = 1, r = 1, q = 1, x = 0, ys = 0;
        while (g == 1) {
            x = y;
            for (u64 k = 0; k < r; k++) y = (mulmod(y, y, n) + c) % n;
            u64 k = 0;
            while (k < r && g == 1) {
                ys = y;
                u64 lim = (m < r - k) ? m : r - k;
                for (u64 z = 0; z < lim; z++) {
                    y = (mulmod(y, y, n) + c) % n;
                    q = mulmod(q, x > y ? x - y : y - x, n);
                }
                g = gcd64(q, n);
                k += m;
            }
            r <<= 1;
        }
        if (g == n) {
            g = 1;
            while (g == 1) {
                ys = (mulmod(ys, ys, n) + c) % n;
                g = gcd64(x > ys ? x - ys : ys - x, n);
            }
        }
        if (g != n) return g;
    }
}

static const u64 TD[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
                         73, 79, 83, 89, 97};

/* distinct prime powers of n (n >= 1); returns count */
static int prime_powers(u64 n, u64 *pp, u64 *pr) {
    int c = 0;
    for (size_t k = 0; k < sizeof TD / sizeof TD[0]; k++) {
        u64 p = TD[k];
        if (n % p == 0) {
            u64 q = 1;
            while (n % p == 0) { n /= p; q *= p; }
            pr[c] = p; pp[c++] = q;
        }
    }
    u64 stack[64];
    int sp = 0;
    if (n > 1) stack[sp++] = n;
    u64 fp[64];
    int nf = 0;
    while (sp) {
        u64 x = stack[--sp];
        if (x == 1) continue;
        if (is_prime64(x)) { fp[nf++] = x; continue; }
        u64 r = (u64)sqrtl((long double)x);
        while (r * r > x) r--;
        while ((r + 1) * (r + 1) <= x) r++;
        if (r * r == x) { stack[sp++] = r; stack[sp++] = r; continue; }
        u64 d = brent(x);
        stack[sp++] = d;
        stack[sp++] = x / d;
    }
    /* group equal primes */
    for (int a = 0; a < nf; a++) {
        if (fp[a] == 0) continue;
        u64 p = fp[a], q = p;
        for (int b = a + 1; b < nf; b++)
            if (fp[b] == p) { q *= p; fp[b] = 0; }
        pr[c] = p; pp[c++] = q;
    }
    return c;
}

/* ---------- conditions ---------- */
/* 108 L^2 <= W^2 with L = (n-1)(n-2), W = S0^3 S1 S2, exact */
static void mul128(u128 a, u128 b, u128 *hi, u128 *lo) {
    u64 a0 = (u64)a, a1 = (u64)(a >> 64), b0 = (u64)b, b1 = (u64)(b >> 64);
    u128 p00 = (u128)a0 * b0, p01 = (u128)a0 * b1, p10 = (u128)a1 * b0, p11 = (u128)a1 * b1;
    u128 mid = (p00 >> 64) + (u64)p01 + (u64)p10;
    *lo = (mid << 64) | (u64)p00;
    *hi = p11 + (p01 >> 64) + (p10 >> 64) + (mid >> 64);
}

static int cond_d(u64 n, u64 S0, u64 S1, u64 S2) {
    u128 L = (u128)(n - 1) * (n - 2);
    long double W = (long double)S0 * S0 * S0 * S1 * S2;
    long double q = W / (long double)L;
    if (q > 10.3923049L) return 1;
    if (q < 10.3923048L) return 0;
    /* here W < 11 L < 2^128: exact */
    u128 Wx = (u128)S0 * S0 * S0 * S1 * S2;
    u128 h1, l1, h2, l2;
    mul128(L, L, &h1, &l1);  /* L^2 */
    /* 108 L^2 as (h1,l1)*108 */
    u128 lo108_lo = (u128)(u64)l1 * 108, lo108_hi = (u128)(u64)(l1 >> 64) * 108 + (lo108_lo >> 64);
    u128 L108_lo = ((lo108_hi << 64) | (u64)lo108_lo);
    u128 L108_hi = h1 * 108 + (lo108_hi >> 64);
    mul128(Wx, Wx, &h2, &l2);
    if (L108_hi != h2) return L108_hi < h2;
    return L108_lo <= l2;
}

/* largest n with cond_d(n, S0, S1, s) (n >= 3), capped at cap */
static u64 nd_max(u64 S0, u64 S1, u64 s, u64 cap) {
    long double W = (long double)S0 * S0 * S0 * S1 * s;
    long double est = sqrtl(W / 10.392304845413264L) + 2;
    if (est >= (long double)cap) {
        if (cond_d(cap, S0, S1, s)) return cap;
        est = (long double)cap;
    }
    u64 n = (u64)est;
    if (n < 3) n = 3;
    while (n > 3 && !cond_d(n, S0, S1, s)) n--;
    while (n < cap && cond_d(n + 1, S0, S1, s)) n++;
    return n;
}

/* ---------- examination of one special n ---------- */
typedef struct { u64 M; int t; } blk_t;

static int blk_desc(const void *a, const void *b) {
    u64 x = ((const blk_t *)a)->M, y = ((const blk_t *)b)->M;
    return x > y ? -1 : x < y;
}

static void report_survivor(u64 n, u64 j) {
    u64 best = 0;
    for (int t = 0; t < I; t++) {
        u64 pp[64], pr[64];
        int c = prime_powers(n - t, pp, pr);
        for (int k = 0; k < c; k++) {
            u64 p = pr[k], q = pp[k];
            int e = 0;
            while (q > 1) { q /= p; e++; }
            if (!(p > (u64)I || (p == (u64)I && e >= 2))) continue;
            if (t <= TMAX && j % pp[k] > (u64)t) { fprintf(stderr, "internal: survivor fails (*) n=%" PRIu64 "\n", n); exit(3); }
            u64 a = j, b = n - j, carry = 0;
            int any = 0;
            while (a || b || carry) {
                u64 s = a % p + b % p + carry;
                carry = s >= p;
                if (carry) any = 1;
                a /= p; b /= p;
            }
            if (any && (best == 0 || p < best)) best = p;
        }
    }
    n_surv++;
    printf("survivor %" PRIu64 " %" PRIu64 " %" PRIu64 "\n", n, j, best);
    fflush(stdout);
}

/* R_t | prod_{r=0..t} (t m - r S0) ? */
static int passes_t(u64 m, u64 S0, int t, u64 Rt) {
    if (Rt == 1) return 1;
    u64 prod = 1 % Rt;
    for (int r = 0; r <= t; r++) {
        i128 v = (i128)t * m - (i128)r * S0;
        i128 w = v % (i128)Rt;
        if (w < 0) w += Rt;
        prod = mulmod(prod, (u64)w, Rt);
        if (prod == 0) return 1;
    }
    return prod == 0;
}

static void examine(u64 n, u64 S0, u64 S1, u64 S2) {
    u64 R1 = (n - 1) / S1, R2 = (n - 2) / S2;
    blk_t B[160];
    int nb = 0;
    u64 pp[64], pr[64];
    int c = prime_powers(R1, pp, pr);
    for (int k = 0; k < c; k++) { B[nb].M = pp[k]; B[nb++].t = 1; }
    c = prime_powers(R2, pp, pr);
    for (int k = 0; k < c; k++) { B[nb].M = pp[k]; B[nb++].t = 2; }
    qsort(B, nb, sizeof(blk_t), blk_desc);
    u64 hi = (S0 - 1) / 2;
    int h = 0;
    u128 W = 1;
    while (h < nb && W <= hi) { W *= B[h].M; h++; }
    /* residue options per head block */
    u64 opt[160][3];
    int nopt[160];
    for (int k = 0; k < nb; k++) {
        u64 M = B[k].M;
        u64 s0 = S0 % M;
        if (B[k].t == 1) {
            opt[k][0] = 0; opt[k][1] = s0; nopt[k] = (s0 == 0) ? 1 : 2;
        } else {
            u64 inv2 = (M + 1) / 2;  /* M odd */
            u64 half = mulmod(s0, inv2, M);
            u64 v[3] = {0, half, s0};
            int q = 0;
            for (int a = 0; a < 3; a++) {
                int dup = 0;
                for (int b = 0; b < q; b++) if (opt[k][b] == v[a]) dup = 1;
                if (!dup) opt[k][q++] = v[a];
            }
            nopt[k] = q;
        }
    }
    /* odometer over the head */
    int idx[160];
    memset(idx, 0, sizeof idx);
    u64 found_local = 0;
    u64 Rt[64];
    int have_Rt = 0;
    for (;;) {
        u128 r = 0, mod = 1;
        for (int k = 0; k < h; k++) crt2(r, mod, opt[k][idx[k]], B[k].M, &r, &mod);
        r %= mod;
        u128 m = r ? r : mod;
        for (; m <= hi; m += mod) {
            int ok = 1;
            for (int k = h; k < nb && ok; k++) {
                u64 v = (u64)(m % B[k].M);
                int hit = 0;
                for (int a = 0; a < nopt[k]; a++) if (opt[k][a] == v) hit = 1;
                ok = hit;
            }
            if (!ok) continue;
            found_local++;
            /* positions 3 .. I-1 by divisibility */
            if (!have_Rt) {
                for (int t = 3; t <= TMAX; t++) Rt[t] = (n - t) / smooth_part(n - t);
                have_Rt = 1;
            }
            int all = 1;
            for (int t = 3; t <= TMAX && all; t++) all = passes_t((u64)m, S0, t, Rt[t]);
            if (all) {
                u64 j = (n / S0) * (u64)m;
                if (j > (u64)I) report_survivor(n, j);
            }
        }
        int k = 0;
        while (k < h) {
            if (++idx[k] < nopt[k]) break;
            idx[k] = 0;
            k++;
        }
        if (k == h) break;
    }
    n_cand12 += found_local;
    if (LIST) printf("special %" PRIu64 " %" PRIu64 " %" PRIu64 " %" PRIu64 " %" PRIu64 "\n", n, S0, S1, S2, found_local);
}

static void consider(u64 n, u64 S0, u64 S1) {
    if (n < (u64)(2 * I + 2)) return;
    if (smooth_part(n) != S0 || smooth_part(n - 1) != S1) return;
    u64 S2 = smooth_part(n - 2);
    if (!cond_d(n, S0, S1, S2)) return;
    n_special++;
    sum_special += splitmix64(n);
    examine(n, S0, S1, S2);
}

/* least divisor of the smooth s exceeding b, or 0 */
static u64 ld_best;
static void ld_dfs(int k, u64 cur, const u64 *pk, const int *ek, int np, u64 b) {
    if (cur > b) { if (ld_best == 0 || cur < ld_best) ld_best = cur; return; }
    if (k == np) return;
    u64 x = cur;
    for (int f = 0; f <= ek[k]; f++) {
        if (ld_best && x >= ld_best) break;
        ld_dfs(k + 1, x, pk, ek, np, b);
        if (f < ek[k]) x *= pk[k];
    }
}

static u64 least_div_above(u64 s, u64 b) {
    u64 pk[32];
    int ek[32], np = 0;
    for (int k = 0; k < NP; k++) {
        int e = 0;
        while (s % SP[k] == 0) { s /= SP[k]; e++; }
        if (e) { pk[np] = SP[k]; ek[np++] = e; }
    }
    ld_best = 0;
    ld_dfs(0, 1, pk, ek, np, b);
    return ld_best;
}

static void scan_pair(u64 S0, u64 S1) {
    /* top = min(X, S0^2 S1 / 4 + 1) */
    u128 sq = (u128)S0 * S0;
    u64 top;
    if (sq >= (u128)4 * X) top = X;
    else {
        u128 v = sq * S1 / 4 + 1;
        top = v > X ? X : (u64)v;
    }
    if (top < S0 || top <= FROM) return;
    /* n = 0 mod S0, n = 1 mod S1 */
    u128 L = (u128)S0 * S1;
    u64 n0;
    if (S1 == 1) n0 = S0;
    else {
        u64 inv = invmod64(S0 % S1, S1);
        n0 = (u64)((u128)S0 * inv);  /* < L */
        if (n0 == 0) n0 = (u64)L;
    }
    if (n0 > top) return;
    if (L > X) { if (n0 > FROM) consider(n0, S0, S1); return; }
    u64 step = (u64)L;
    u64 start = n0 > FROM ? n0 : n0 + ((FROM - n0) / step + 1) * step;
    if (PLAIN) {
        for (u64 n = start; n <= top; n += step) { consider(n, S0, S1); if (n > top - step) break; }
        return;
    }
    u64 nd1 = nd_max(S0, S1, 1, top);
    u64 n = start;
    for (; n <= nd1; n += step) { consider(n, S0, S1); if (n > top - step) return; }
    /* tail (nd1, top]: pieces (nu_k, nu_{k+1}] with S2 > 2^k */
    u64 lo = nd1;
    for (int k = 0; lo < top && k < 63; k++) {
        u64 bk = (u64)1 << k;
        if (bk >= X) break;
        u64 hiK = (k + 1 < 63 && ((u64)1 << (k + 1)) < X) ? nd_max(S0, S1, (u64)1 << (k + 1), top) : top;
        if (hiK <= lo) continue;
        if (hiK <= FROM) { lo = hiK; continue; }
        u64 lo2 = lo > FROM ? lo : FROM;  /* the piece is (lo, hiK]; only n > FROM count */
        /* elements of the progression in (lo2, hiK] */
        u64 first = (lo2 < n0) ? n0 : n0 + ((lo2 - n0) / step + 1) * step;
        if (first > hiK) { lo = hiK; continue; }
        u64 count = (hiK - first) / step + 1;
        /* window of d */
        size_t a = 0, b = NSM;
        { size_t L2 = 0, R2 = NSM; while (L2 < R2) { size_t mid = (L2 + R2) / 2; if (SM[mid] <= bk) L2 = mid + 1; else R2 = mid; } a = L2; }
        u128 wtop = (u128)PMAX * bk;
        { size_t L2 = a, R2 = NSM; while (L2 < R2) { size_t mid = (L2 + R2) / 2; if ((u128)SM[mid] <= wtop) L2 = mid + 1; else R2 = mid; } b = L2; }
        if (count <= 4 * (u64)(b - a) + 16) {
            for (u64 m = first; m <= hiK; m += step) { consider(m, S0, S1); if (m > hiK - step) break; }
        } else {
            for (size_t w = a; w < b; w++) {
                u64 d = SM[w];
                if (gcd64(d, S1) != 1) continue;
                u64 g = gcd64(d, S0);
                if (g != 1 && g != 2) continue;
                /* n = n0 (mod step), n = 2 (mod d): solvable iff n0 = 2 (mod g2) */
                u64 g2 = gcd64(step, d);
                if ((n0 % g2) != (2 % g2)) continue;
                u64 dg = d / g2, sg = step / g2;
                u128 r, M;
                {
                    /* n = n0 + step * t with sg * t = (2 - n0) / g2 (mod dg) */
                    u64 rhs;
                    if (dg == 1) rhs = 0;
                    else {
                        i128 diff = ((i128)2 - (i128)n0) / (i128)g2;
                        i128 w = diff % (i128)dg;
                        if (w < 0) w += dg;
                        rhs = (u64)w;
                    }
                    u64 t = dg == 1 ? 0 : (u64)(((u128)rhs * invmod128(sg % dg, dg)) % dg);
                    M = (u128)step * dg;
                    r = (u128)n0 + (u128)step * t;
                    r %= M;
                }
                if (M > (u128)X) {
                    u64 m = (u64)r;
                    if (m <= lo2) continue;
                    if (m <= hiK && (m - 2) % d == 0) {
                        u64 S2 = smooth_part(m - 2);
                        if (least_div_above(S2, bk) == d) consider(m, S0, S1);
                    }
                    continue;
                }
                u64 MM = (u64)M;
                u64 m = (u64)r;
                if (m <= lo2) m += ((lo2 - m) / MM + 1) * MM;
                for (; m <= hiK; m += MM) {
                    if ((m - 2) % d == 0) {
                        u64 S2 = smooth_part(m - 2);
                        if (least_div_above(S2, bk) == d) consider(m, S0, S1);
                    }
                    if (m > hiK - MM) break;
                }
            }
        }
        lo = hiK;
    }
}

static void central(void) {
    for (size_t a = 0; a < NSM; a++) {
        u64 s = SM[a];
        if (s > X - 1) break;
        u64 n = s + 1;
        if (n % 2 || n < (u64)(2 * I + 2) || n <= FROM) continue;
        if ((u64)(a % SHJ) != (u64)SHK) continue;
        n_central++;
        u64 j = n / 2;
        /* (*) at every block, then exact */
        int ok = 1;
        for (int t = 0; t <= TMAX && ok; t++) {
            u64 pp[64], pr[64];
            int c = prime_powers(n - t, pp, pr);
            for (int k = 0; k < c && ok; k++) {
                u64 p = pr[k], q = pp[k];
                int e = 0;
                while (q > 1) { q /= p; e++; }
                if (!(p > (u64)I || (p == (u64)I && e >= 2))) continue;
                if (j % pp[k] > (u64)t) ok = 0;
            }
        }
        if (ok) report_survivor(n, j);
    }
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: search699 I X [--plain] [--shard K/J] [--tmax T] [--from LO] [--list]\n"); return 2; }
    I = atoi(argv[1]);
    long double xl = strtold(argv[2], NULL);
    if (!(xl >= 1 && xl < 4611686018427387904.0L)) { fprintf(stderr, "need 1 <= X < 2^62\n"); return 2; }
    X = (u64)xl;
    for (int a = 3; a < argc; a++) {
        if (!strcmp(argv[a], "--plain")) PLAIN = 1;
        else if (!strncmp(argv[a], "--shard", 7) && a + 1 < argc) { sscanf(argv[++a], "%d/%d", &SHK, &SHJ); }
        else if (!strcmp(argv[a], "--tmax") && a + 1 < argc) TMAX = atoi(argv[++a]);
        else if (!strcmp(argv[a], "--from") && a + 1 < argc) {
            long double fl = strtold(argv[++a], NULL);
            if (!(fl >= 0 && fl < 4611686018427387904.0L)) { fprintf(stderr, "need 0 <= LO < 2^62\n"); return 2; }
            FROM = (u64)fl;
        }
        else if (!strcmp(argv[a], "--list")) LIST = 1;
        else { fprintf(stderr, "bad arg %s\n", argv[a]); return 2; }
    }
    if (TMAX < 0) TMAX = I - 1;
    if (I < 3 || X >= ((u64)1 << 62) || SHJ < 1 || SHK < 0 || SHK >= SHJ || TMAX < 2 || TMAX > I - 1) {
        fprintf(stderr, "bad parameters\n");
        return 2;
    }
    NP = 0;
    for (u64 p = 2; p <= (u64)I; p++) {
        int pr = 1;
        for (u64 d = 2; d * d <= p; d++) if (p % d == 0) pr = 0;
        if (pr) { SP[NP++] = p; PMAX = p; }
    }
    init_inverses();
    gen_smooth();
    for (size_t a = 0; a < NSM; a++) {
        u64 S0 = SM[a];
        if (S0 < 2) continue;
        if ((u64)(a % SHJ) != (u64)SHK) continue;
        for (size_t b = 0; b < NSM; b++) {
            u64 S1 = SM[b];
            if (gcd64(S0, S1) != 1) continue;
            if ((S0 & 1) && (S1 & 1)) continue;  /* n(n-1) is even */
            scan_pair(S0, S1);
        }
    }
    central();
    printf("stats %d %" PRIu64 " %" PRIu64 " %" PRIu64 " %" PRIu64 " %" PRIu64 " %" PRIu64 "\n", I, X, n_special,
           sum_special, n_cand12, n_central, n_surv);
    return 0;
}

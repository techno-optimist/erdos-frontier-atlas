/* Sequential engine for OEIS A327909 (Erdős #962), all n <= NMAX in one pass over [1, X].

   a(n) = smallest start of a run of n or more consecutive integers each having a
   prime factor > n.  With p the largest prime <= n, the integers that break a run
   are exactly the p-smooth ones, so for each prime p <= NMAX (a "class", covering
   p <= n < next prime) the engine follows the gaps between consecutive p-smooth
   integers.  Smoothness is exact integer arithmetic: acc[m] is the product of the
   prime powers p^k dividing m with p <= NMAX, so m is NMAX-smooth iff acc[m] == m,
   and gp[m] is the largest such prime (the last one to hit m).

   Usage: runs NMAX X
   Prints "A n a(n) run" for every n whose run is found in [1, X] ("run" is the
   length of the maximal run at a(n), or "open" if it is still running at X), and
   "NOTFOUND n" otherwise. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#define W (1 << 18)
static uint64_t acc[W];
static uint16_t gp[W];

int main(int argc, char **argv){
    if (argc != 3){ fprintf(stderr, "usage: runs NMAX X\n"); return 2; }
    int NMAX = atoi(argv[1]); uint64_t X = strtoull(argv[2], 0, 10);
    if (NMAX < 2 || NMAX > 3000){ fprintf(stderr, "NMAX out of range\n"); return 2; }
    int lim = NMAX + 400, np = 0;
    char *comp = calloc(lim + 1, 1); int *pr = malloc(sizeof(int) * (lim + 1));
    for (int i = 2; i <= lim; i++) if (!comp[i]){ for (int j = 2 * i; j <= lim; j += i) comp[j] = 1; }
    for (int i = 2; i <= lim; i++) if (!comp[i]){ pr[np++] = i; if (i > NMAX) break; }
    /* class 0: n = 1 (the only 1-smooth integer is 1); class c >= 1: prime pr[c-1],
       thresholds pr[c-1] .. min(pr[c]-1, NMAX); pr[np-1] > NMAX only closes the last class */
    int nc = np;
    uint64_t *last = calloc(nc, sizeof(uint64_t));
    int *nxt = calloc(nc, sizeof(int)), *hi = calloc(nc, sizeof(int));
    uint64_t *ans = calloc(NMAX + 1, sizeof(uint64_t)), *run = calloc(NMAX + 1, sizeof(uint64_t));
    char *open = calloc(NMAX + 1, 1);
    nxt[0] = 1; hi[0] = 1;
    for (int c = 1; c < nc; c++){ nxt[c] = pr[c - 1]; hi[c] = pr[c] - 1 < NMAX ? pr[c] - 1 : NMAX; }
    int pending = nc;
    uint64_t L, top = 0;
    for (L = 1; L <= X && pending > 0; L += W){
        uint64_t R = L + W - 1; if (R > X) R = X; int len = (int)(R - L + 1);
        for (int i = 0; i < len; i++){ acc[i] = 1; gp[i] = 1; }
        for (int k = 0; k < np - 1; k++){
            uint64_t p = pr[k], s = ((L + p - 1) / p) * p;
            for (uint64_t m = s; m <= R; m += p){ acc[m - L] *= p; gp[m - L] = (uint16_t)p; }
            for (uint64_t q = p * p; q <= R; ){
                uint64_t t = ((L + q - 1) / q) * q;
                for (uint64_t m = t; m <= R; m += q) acc[m - L] *= p;
                if (q > R / p) break;
                q *= p;
            }
        }
        for (int i = 0; i < len; i++){
            uint64_t m = L + i;
            if (acc[i] != m) continue;                 /* has a prime factor > NMAX: breaks nothing */
            int g = gp[i];                             /* largest prime factor; 1 for m = 1 */
            for (int c = (g == 1 ? 0 : 1); c < nc; c++){
                if (c >= 1 && pr[c - 1] < g) continue;  /* m is not pr[c-1]-smooth */
                if (nxt[c] <= hi[c]){
                    uint64_t gap = m - last[c] - 1;
                    while (nxt[c] <= hi[c] && gap >= (uint64_t)nxt[c]){
                        ans[nxt[c]] = last[c] + 1; run[nxt[c]] = gap; nxt[c]++;
                    }
                    if (nxt[c] > hi[c]) pending--;
                }
                last[c] = m;
            }
        }
        top = R;
    }
    for (int c = 0; c < nc; c++)                        /* runs still open at the end of the scan */
        while (nxt[c] <= hi[c] && top - last[c] >= (uint64_t)nxt[c]){
            ans[nxt[c]] = last[c] + 1; open[nxt[c]] = 1; nxt[c]++;
        }
    for (int n = 1; n <= NMAX; n++){
        if (!ans[n]) printf("NOTFOUND %d\n", n);
        else if (open[n]) printf("A %d %llu open\n", n, (unsigned long long)ans[n]);
        else printf("A %d %llu %llu\n", n, (unsigned long long)ans[n], (unsigned long long)run[n]);
    }
    return 0;
}

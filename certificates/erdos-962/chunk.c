/* Chunked engine for OEIS A327909 (Erdős #962): one chunk [L, R] of the scan.

   Same exact smoothness sieve as runs.c.  For every prime p <= NMAX it prints the
   first and last p-smooth integers of the chunk ("F p first last") and every gap
   between consecutive p-smooth integers inside the chunk that is longer than all
   earlier gaps of that class in the chunk ("G p start length", start = first
   integer of the run).  The first gap of length >= n is always such a record, so
   smooth_runs.merge_chunks can combine consecutive chunks exactly; chunks can run
   in parallel.

   Usage: chunk L R NMAX */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#define W (1 << 18)
static uint64_t acc[W];
static uint16_t gp[W];

int main(int argc, char **argv){
    if (argc != 4){ fprintf(stderr, "usage: chunk L R NMAX\n"); return 2; }
    uint64_t L0 = strtoull(argv[1], 0, 10), R0 = strtoull(argv[2], 0, 10);
    int NMAX = atoi(argv[3]);
    if (L0 < 1 || R0 < L0 || NMAX < 2 || NMAX > 3000){ fprintf(stderr, "bad arguments\n"); return 2; }
    char *comp = calloc(NMAX + 1, 1); int *pr = malloc(sizeof(int) * (NMAX + 1)), np = 0;
    for (int i = 2; i <= NMAX; i++) if (!comp[i]){ pr[np++] = i; for (int j = 2 * i; j <= NMAX; j += i) comp[j] = 1; }
    uint64_t *first = calloc(np, sizeof(uint64_t)), *last = calloc(np, sizeof(uint64_t)),
             *best = calloc(np, sizeof(uint64_t));
    for (uint64_t L = L0; L <= R0; L += W){
        uint64_t R = L + W - 1; if (R > R0) R = R0; int len = (int)(R - L + 1);
        for (int i = 0; i < len; i++){ acc[i] = 1; gp[i] = 1; }
        for (int k = 0; k < np; k++){
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
            if (acc[i] != m) continue;
            int g = gp[i];
            for (int c = 0; c < np; c++){
                if (pr[c] < g) continue;
                if (first[c] == 0) first[c] = m;
                else {
                    uint64_t gap = m - last[c] - 1;
                    if (gap > best[c]){
                        best[c] = gap;
                        printf("G %d %llu %llu\n", pr[c], (unsigned long long)(last[c] + 1), (unsigned long long)gap);
                    }
                }
                last[c] = m;
            }
        }
    }
    for (int c = 0; c < np; c++)
        printf("F %d %llu %llu\n", pr[c], (unsigned long long)first[c], (unsigned long long)last[c]);
    return 0;
}

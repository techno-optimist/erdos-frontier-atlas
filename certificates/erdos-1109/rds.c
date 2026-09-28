/* Independent cross-check for the Erdős #1109 certificate: the exact clique number of G_N by
   Östergård's Russian-doll search (the basic algorithm of cliquer), with no colouring bound.

   G_N has vertices V_N = { a < N : 2a and a + N squarefree } and edges a ~ b iff a + b is
   squarefree; the largest valid S with maximum N has omega(G_N) + 1 elements, so
   f(N) = max(f(N-1), omega(G_N) + 1).  Vertices are taken in increasing order of degree
   (ties by value); c[i] is the clique number of the graph on the i-th and later vertices.

   Usage: rds N0 N1 F0      (F0 = f(N0 - 1))
   Prints "N omega f nodes" for every N in [N0, N1] with 2N squarefree, "RECORD" when f grows. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXV 2048
#define WORDS (MAXV / 64)
typedef struct { uint64_t w[WORDS]; } bs;
static int nw, nv, V[MAXV], deg[MAXV], c[MAXV + 1], best, found;
static bs adj[MAXV];
static unsigned char *sqf;
static long long nodes;

static inline int popc(const bs *b){ int s = 0; for (int i = 0; i < nw; i++) s += __builtin_popcountll(b->w[i]); return s; }
static inline int lowest(const bs *b){ for (int i = 0; i < nw; i++) if (b->w[i]) return i * 64 + __builtin_ctzll(b->w[i]); return -1; }

static void clique(bs U, int size){
    nodes++;
    if (popc(&U) == 0){ if (size > best){ best = size; found = 1; } return; }
    while (popc(&U)){
        if (size + popc(&U) <= best) return;
        int i = lowest(&U);
        if (size + c[i] <= best) return;
        U.w[i >> 6] &= ~(1ULL << (i & 63));
        bs NU; for (int k = 0; k < nw; k++) NU.w[k] = U.w[k] & adj[i].w[k];
        clique(NU, size + 1);
        if (found) return;
    }
}

int main(int argc, char **argv){
    if (argc != 4){ fprintf(stderr, "usage: rds N0 N1 F0\n"); return 2; }
    int N0 = atoi(argv[1]), N1 = atoi(argv[2]), f = atoi(argv[3]);
    if (N0 < 1 || N1 < N0 || N1 > 12000){ fprintf(stderr, "bad range\n"); return 2; }
    sqf = calloc(2 * N1 + 2, 1);
    for (int m = 1; m <= 2 * N1 + 1; m++) sqf[m] = 1;
    for (long p = 2; p * p <= 2 * N1 + 1; p++) for (long m = p * p; m <= 2 * N1 + 1; m += p * p) sqf[m] = 0;
    for (int N = N0; N <= N1; N++){
        if (!sqf[2 * N]) continue;
        nv = 0;
        for (int a = 1; a < N; a++) if (sqf[2 * a] && sqf[a + N]) V[nv++] = a;
        if (nv >= MAXV){ fprintf(stderr, "too many vertices at N = %d\n", N); return 1; }
        for (int i = 0; i < nv; i++){ deg[i] = 0; for (int j = 0; j < nv; j++) if (i != j && sqf[V[i] + V[j]]) deg[i]++; }
        for (int i = 1; i < nv; i++){                     /* stable insertion sort by degree */
            int x = V[i], d = deg[i], j = i - 1;
            while (j >= 0 && deg[j] > d){ V[j + 1] = V[j]; deg[j + 1] = deg[j]; j--; }
            V[j + 1] = x; deg[j + 1] = d;
        }
        nw = nv ? (nv + 63) / 64 : 1;
        for (int i = 0; i < nv; i++){
            memset(&adj[i], 0, sizeof(bs));
            for (int j = 0; j < nv; j++) if (i != j && sqf[V[i] + V[j]]) adj[i].w[j >> 6] |= 1ULL << (j & 63);
        }
        best = 0; nodes = 0;
        for (int i = nv - 1; i >= 0; i--){
            found = 0;
            bs U; memset(&U, 0, sizeof U);
            for (int j = i + 1; j < nv; j++) if ((adj[i].w[j >> 6] >> (j & 63)) & 1) U.w[j >> 6] |= 1ULL << (j & 63);
            clique(U, 1);
            c[i] = best;
        }
        int nf = best + 1 > f ? best + 1 : f;
        printf("%d %d %d %lld%s\n", N, best, nf, nodes, nf > f ? " RECORD" : "");
        fflush(stdout);
        f = nf;
    }
    return 0;
}

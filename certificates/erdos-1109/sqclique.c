/* Records of OEIS A392164 (Erdős #1109), C port of sqfree_sums.Clique, node for node.

   f(N) = largest S in {1..N} with every element of S + S squarefree (a + a included).
   A record at N forces N into S, so N is odd and squarefree, and f(N) = f(N-1) + 1 exactly
   when the graph on V_N = { a < N : 2a and a + N squarefree }, a ~ b iff a + b squarefree,
   has a clique of size f(N-1).  Decision search with a greedy-colouring bound: colour the
   candidates lowest vertex first, branch from the last colour class, prune when
   |R| + colour < target.

   Usage: sqclique NMAX [N0 F0]      (start at N0 with f(N0 - 1) = F0; default N0 = 1, F0 = 0,
                                     so a verifier can replay disjoint ranges in parallel)
   For every N0 <= N <= NMAX with 2N squarefree it prints
     "R k N |V_N| nodes s_1 ... s_k"   when N is the k-th record (s_i = the record set), or
     "C k N |V_N| nodes"               when no set of size k has maximum N. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXV 2048
#define WORDS (MAXV / 64)
typedef struct { uint64_t w[WORDS]; } bs;
static int nw, V[MAXV], nv, R[256], nr, target, found[256];
static bs adj[MAXV];
static unsigned char *sqf;
static long long nodes;

static inline int popc(const bs *b){ int c = 0; for (int i = 0; i < nw; i++) c += __builtin_popcountll(b->w[i]); return c; }

static int expand(bs P){
    nodes++;
    int order[MAXV], color[MAXV], cnt = 0, col = 0;
    bs U = P;
    while (popc(&U)){                                   /* greedy colouring, lowest vertex first */
        col++;
        bs Q = U;
        for (int i = 0; i < nw; i++){
            while (Q.w[i]){
                int b = __builtin_ctzll(Q.w[i]), v = i * 64 + b;
                Q.w[i] &= Q.w[i] - 1;
                U.w[i] &= ~(1ULL << b);
                for (int j = 0; j < nw; j++) Q.w[j] &= ~adj[v].w[j];
                order[cnt] = v; color[cnt] = col; cnt++;
            }
        }
    }
    for (int k = cnt - 1; k >= 0; k--){
        if (nr + color[k] < target) return 0;
        int v = order[k];
        R[nr++] = v;
        if (nr == target){ memcpy(found, R, sizeof(int) * nr); return 1; }
        bs NP; int any = 0;
        for (int i = 0; i < nw; i++){ NP.w[i] = P.w[i] & adj[v].w[i]; any |= NP.w[i] != 0; }
        if (any && expand(NP)) return 1;
        nr--;
        P.w[v >> 6] &= ~(1ULL << (v & 63));
    }
    return 0;
}

int main(int argc, char **argv){
    if (argc != 2 && argc != 4){ fprintf(stderr, "usage: sqclique NMAX [N0 F0]\n"); return 2; }
    int NMAX = atoi(argv[1]), N0 = argc == 4 ? atoi(argv[2]) : 1, f = argc == 4 ? atoi(argv[3]) : 0;
    if (NMAX < 1 || NMAX > 12000 || N0 < 1 || f < 0){ fprintf(stderr, "argument out of range\n"); return 2; }
    sqf = calloc(2 * NMAX + 2, 1);
    for (int m = 1; m <= 2 * NMAX + 1; m++) sqf[m] = 1;
    for (long p = 2; p * p <= 2 * NMAX + 1; p++) for (long m = p * p; m <= 2 * NMAX + 1; m += p * p) sqf[m] = 0;
    for (int N = N0; N <= NMAX; N++){
        if (!sqf[2 * N]) continue;
        nv = 0;
        for (int a = 1; a < N; a++) if (sqf[2 * a] && sqf[a + N]) V[nv++] = a;
        if (nv >= MAXV){ fprintf(stderr, "too many vertices at N = %d\n", N); return 1; }
        nw = nv ? (nv + 63) / 64 : 1;
        for (int i = 0; i < nv; i++){
            memset(&adj[i], 0, sizeof(bs));
            for (int j = 0; j < nv; j++) if (i != j && sqf[V[i] + V[j]]) adj[i].w[j >> 6] |= 1ULL << (j & 63);
        }
        bs P; memset(&P, 0, sizeof P);
        for (int i = 0; i < nv; i++) P.w[i >> 6] |= 1ULL << (i & 63);
        nodes = 0; nr = 0; target = f;
        int ok = target == 0 ? 1 : expand(P);
        if (ok){
            f++;
            printf("R %d %d %d %lld", f, N, nv, nodes);
            for (int i = 0; i < target; i++) printf(" %d", V[found[i]]);
            printf(" %d\n", N);
        } else printf("C %d %d %d %lld\n", f + 1, N, nv, nodes);
        fflush(stdout);
    }
    return 0;
}

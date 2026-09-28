/* Thresholds of OEIS A068063 (Erdős #131), C port of nondividing.Search, node for node.

   A set is nondividing if no element divides the sum of any nonempty subset of the others;
   T_k is the least N such that {1..N} has a nondividing k-set.  A k-set with maximum N is
   built in decreasing order; subsets of nondividing sets are nondividing, so after choosing x
   the remaining k-d-1 smaller elements force x > T_{k-d-1}.  A new smaller x is admissible iff
   (a) x divides no nonempty subset sum of the chosen set, and (b) for every chosen e, no subset
   sum of the others (the empty one included) is congruent to -x mod e.

   Usage: nondiv KMAX NMAX
   For k = 1..KMAX and N = T_{k-1}+1, ... it prints "C k N nodes" for every N with no
   nondividing k-set of maximum N, then "T k N nodes s_1 ... s_k" for the first N with one
   (or "NONE k above NMAX"). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXK 16
#define MAXE 1024                    /* elements <= MAXE */
#define SW ((MAXK * MAXE) / 64 + 2)  /* subset-sum bitset words */
#define RW (MAXE / 64 + 1)
static int K, T[MAXK + 2], S[MAXK + 2], d;
static uint64_t SS[MAXK + 2][SW];            /* subset sums of the first d elements, per depth */
static uint64_t R[MAXK + 2][MAXK + 2][RW];   /* R[d][i]: residues mod S[i] of sums of others */
static int maxsum[MAXK + 2], hw[MAXK + 2];
static long long nodes;
static inline int bit(const uint64_t *b, int i){ return (b[i >> 6] >> (i & 63)) & 1; }
static inline void setb(uint64_t *b, int i){ b[i >> 6] |= 1ULL << (i & 63); }
static int ok_add(int x){
    /* (a) multiples of x among nonempty subset sums */
    for (int m = x; m <= maxsum[d]; m += x) if (bit(SS[d], m)) return 0;
    /* (b) */
    for (int i = 0; i < d; i++){ int e = S[i]; int r = (e - x % e) % e; if (bit(R[d][i], r)) return 0; }
    return 1;
}
static void push(int x){
    int nd = d + 1;
    /* new subset sums */
    maxsum[nd] = maxsum[d] + x;
    {   /* SS[nd] = SS[d] | (SS[d] << x); SS[d] is zero from word hw[d] on */
        int ws = x >> 6, sh = x & 63, top = (maxsum[nd] >> 6) + 1;
        for (int w = 0; w < top; w++){
            uint64_t v = w < hw[d] ? SS[d][w] : 0;
            int a = w - ws;
            if (a >= 0 && a < hw[d]) v |= SS[d][a] << sh;
            if (sh && a - 1 >= 0 && a - 1 < hw[d]) v |= SS[d][a - 1] >> (64 - sh);
            SS[nd][w] = v;
        }
        for (int w = top; w < hw[nd]; w++) SS[nd][w] = 0;
        hw[nd] = top;
    }
    /* residues for old elements: R <- R U (R + x) mod e */
    for (int i = 0; i < d; i++){                 /* R <- R | rotate_e(R, x mod e), word by word */
        int e = S[i], s = x % e, nwd = (e + 63) >> 6;
        const uint64_t *A = R[d][i]; uint64_t *B = R[nd][i];
        for (int w = 0; w < RW; w++) B[w] = 0;
        for (int w = 0; w < nwd; w++) B[w] = A[w];
        if (s){
            /* left shift by s (bits that pass e are wrapped by the right shift below) */
            int ws = s >> 6, sh = s & 63;
            for (int w = nwd - 1; w >= 0; w--){
                int a = w - ws; uint64_t v = 0;
                if (a >= 0) v |= A[a] << sh;
                if (sh && a - 1 >= 0) v |= A[a - 1] >> (64 - sh);
                B[w] |= v;
            }
            /* right shift by e - s */
            int t = e - s, wt = t >> 6, st = t & 63;
            for (int w = 0; w < nwd; w++){
                int a = w + wt; uint64_t v = 0;
                if (a < nwd) v |= A[a] >> st;
                if (st && a + 1 < nwd) v |= A[a + 1] << (64 - st);
                B[w] |= v;
            }
            /* keep only bits 0..e-1 */
            if (e & 63) B[nwd - 1] &= (1ULL << (e & 63)) - 1;
        }
    }
    /* residues for x: all subset sums of the old set mod x */
    memset(R[nd][d], 0, sizeof(R[nd][d]));
    for (int w = 0; w < hw[d]; w++)
        for (uint64_t b = SS[d][w]; b; b &= b - 1) setb(R[nd][d], (w * 64 + __builtin_ctzll(b)) % x);
    S[d] = x; d = nd;
}
static int dfs(int prev){
    nodes++;
    if (d == K) return 1;
    int need = K - d - 1;                       /* elements still to place below x */
    int lo = T[need] + 1;
    for (int x = prev - 1; x >= lo; x--){
        if (!ok_add(x)) continue;
        push(x);
        if (dfs(x)) return 1;
        d--;
    }
    return 0;
}
int main(int argc, char **argv){
    int KMAX = atoi(argv[1]), NMAX = atoi(argv[2]);
    T[0] = 0;
    for (K = 1; K <= KMAX; K++){
        int found = 0;
        for (int N = T[K - 1] + 1; N <= NMAX && !found; N++){
            d = 0; maxsum[0] = 0; memset(SS, 0, sizeof(SS)); memset(hw, 0, sizeof(hw)); setb(SS[0], 0); hw[0] = 1;
            nodes = 0;
            /* place N first: no condition */
            push(N);
            if (dfs(N)){
                T[K] = N; found = 1;
                printf("T %d %d %lld", K, N, nodes); for (int i = 0; i < K; i++) printf(" %d", S[i]); printf("\n");
            } else printf("C %d %d %lld\n", K, N, nodes);
            fflush(stdout);
        }
        if (!found){ printf("NONE %d above %d\n", K, NMAX); return 0; }
    }
    return 0;
}

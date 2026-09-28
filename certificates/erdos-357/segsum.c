/* Erdős #357: sequences all of whose segment sums are distinct.  C port of
   segment_sums.Search, node for node.

   A segment of (s_1, ..., s_n) is a run s_i + s_{i+1} + ... + s_j of consecutive terms.
     mode m: increasing n-sequences from {1..N}               (OEIS A364132)
     mode a: n-sequences of distinct values from {1..N}, any order  (OEIS A364153)
   a(n) is the least N for which such a sequence exists.

   The sequence is built left to right.  With T = the sums of the segments that end at the
   last term, 0 included, and D = every segment sum so far, a next term x is admissible iff
   (T + x) and D are disjoint; then T <- (T + x) | {0} and D <- D | (T + x).  Both sets are
   bitsets.  Pruning, both modes: the n - j terms still to come are distinct values of
   [lo, N] outside D, since each is itself a segment sum, where lo = s_j + 1 in mode m and 1
   in mode a.  Mode m caps the next term at N - (n - j - 1).  Mode a keeps only sequences
   with s_1 < s_n: the reversal of a valid sequence is valid.

   Usage: segsum MODE n N
   Prints "none MODE n N nodes", or "found MODE n N nodes : s_1 ... s_n" for the first
   sequence in search order.  nodes counts every call of the search, root included. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXN 60
#define W 64                                /* bitset words: sums below 64 * W = 4096 */
typedef uint64_t u64;
static int mode, n, N, s[MAXN + 1], found;
static long long nodes;
static u64 T[MAXN + 1][W], D[MAXN + 1][W];
static int top[MAXN + 1];                   /* words in use at each depth; the rest are 0 */

static inline int bit(const u64 *b, int i) { return (b[i >> 6] >> (i & 63)) & 1; }

/* word w of (b << x), for a bitset b whose words from `used` on are zero */
static inline u64 shl_word(const u64 *b, int used, int x, int w) {
    int a = w - (x >> 6), sh = x & 63;
    u64 v = 0;
    if (a >= 0 && a < used) v = b[a] << sh;
    if (sh && a - 1 >= 0 && a - 1 < used) v |= b[a - 1] >> (64 - sh);
    return v;
}

static void dfs(int j, int total) {
    nodes++;
    if (j == n) { found = 1; return; }
    int lo = (mode == 'm' && j) ? s[j - 1] + 1 : 1;
    int hi = mode == 'm' ? N - (n - j - 1) : N;
    int avail = 0;
    for (int x = lo; x <= N; x++) if (!bit(D[j], x)) avail++;
    if (avail < n - j) return;
    int used = top[j];
    for (int x = lo; x <= hi; x++) {
        if (bit(D[j], x)) continue;
        if (mode == 'a' && j == n - 1 && n > 1 && x < s[0]) continue;
        int nw = ((total + x) >> 6) + 1, clash = 0;
        for (int w = x >> 6; w < nw; w++)
            if (shl_word(T[j], used, x, w) & D[j][w]) { clash = 1; break; }
        if (clash) continue;
        s[j] = x;
        for (int w = 0; w < nw; w++) {
            u64 v = shl_word(T[j], used, x, w);
            T[j + 1][w] = v;
            D[j + 1][w] = (w < used ? D[j][w] : 0) | v;
        }
        for (int w = nw; w < top[j + 1]; w++) T[j + 1][w] = D[j + 1][w] = 0;  /* stale */
        T[j + 1][0] |= 1;
        top[j + 1] = nw;
        dfs(j + 1, total + x);
        if (found) return;
    }
}

int main(int argc, char **argv) {
    if (argc != 4 || (argv[1][0] != 'm' && argv[1][0] != 'a') || argv[1][1]) {
        fprintf(stderr, "usage: segsum m|a n N\n");
        return 2;
    }
    mode = argv[1][0]; n = atoi(argv[2]); N = atoi(argv[3]);
    if (n < 1 || n > MAXN || N < 1 || (long long)n * N >= 64LL * W) {
        fprintf(stderr, "need 1 <= n <= %d and n * N < %d\n", MAXN, 64 * W);
        return 2;
    }
    memset(T, 0, sizeof T); memset(D, 0, sizeof D);
    T[0][0] = 1; top[0] = 1;
    dfs(0, 0);
    printf("%s %c %d %d %lld", found ? "found" : "none", mode, n, N, nodes);
    if (found) { printf(" :"); for (int i = 0; i < n; i++) printf(" %d", s[i]); }
    printf("\n");
    return 0;
}

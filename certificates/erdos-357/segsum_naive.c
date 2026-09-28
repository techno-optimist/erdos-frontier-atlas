/* Erdős #357: a second, deliberately different search, used only to cross-check verdicts
   of segsum.c.  It shares no code with segsum.c and prunes nothing beyond the definitions.

     mode m: the increasing sequence is built from its LARGEST term down.  Prepending y to
             the block s_{j+1} < ... < s_n adds the segment sums y + (sums of the block's
             initial runs, the empty run included).
     mode a: the sequence is built left to right, trying values from N down, with no
             symmetry breaking (both orientations are searched).
   Segment sums in use are marked in a byte array and unmarked on backtracking.

   Usage: segsum_naive MODE n N
   Prints "none MODE n N nodes", or "found MODE n N nodes : s_1 ... s_n". */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 60
#define MAXS 4096
static int mode, n, N, found;
static long long nodes;
static unsigned char in_use[MAXS + 1];
static int run[MAXN + 2][MAXN + 2];   /* run[d][0..d]: the sums of the partial runs at depth d */
static int seq[MAXN + 2];             /* mode m: seq[n-d..n-1]; mode a: seq[0..d-1] */

/* try to extend depth d by the value v; on success mark the new sums and fill run[d+1] */
static int extend(int d, int v) {
    for (int i = 0; i <= d; i++) if (in_use[v + run[d][i]]) return 0;
    for (int i = 0; i <= d; i++) in_use[v + run[d][i]] = 1;
    run[d + 1][0] = 0;
    for (int i = 0; i <= d; i++) run[d + 1][i + 1] = v + run[d][i];
    return 1;
}
static void retract(int d, int v) {
    for (int i = 0; i <= d; i++) in_use[v + run[d][i]] = 0;
}

static void search(int d) {
    nodes++;
    if (d == n) { found = 1; return; }
    if (mode == 'm') {
        int below = n - d - 1;                     /* terms still to come under this one */
        int hi = d ? seq[n - d] - 1 : N;
        for (int y = hi; y >= below + 1; y--) {
            if (!extend(d, y)) continue;
            seq[n - d - 1] = y;
            search(d + 1);
            if (found) return;
            retract(d, y);
        }
    } else {
        for (int x = N; x >= 1; x--) {
            if (!extend(d, x)) continue;
            seq[d] = x;
            search(d + 1);
            if (found) return;
            retract(d, x);
        }
    }
}

int main(int argc, char **argv) {
    if (argc != 4 || (argv[1][0] != 'm' && argv[1][0] != 'a') || argv[1][1]) {
        fprintf(stderr, "usage: segsum_naive m|a n N\n");
        return 2;
    }
    mode = argv[1][0]; n = atoi(argv[2]); N = atoi(argv[3]);
    if (n < 1 || n > MAXN || N < 1 || (long long)n * N > MAXS) {
        fprintf(stderr, "need 1 <= n <= %d and n * N <= %d\n", MAXN, MAXS);
        return 2;
    }
    run[0][0] = 0;
    search(0);
    printf("%s %c %d %d %lld", found ? "found" : "none", mode, n, N, nodes);
    if (found) { printf(" :"); for (int i = 0; i < n; i++) printf(" %d", seq[i]); }
    printf("\n");
    return 0;
}

/* Erdős #864: a second, deliberately different search, used only to cross-check verdicts of
   onesum.c.  It shares no code with onesum.c: the inner elements are added in DECREASING order,
   every candidate is tested from scratch against a table of sum counts, there are no candidate
   lists and no symmetry breaking, and a node is dropped only when fewer values below it than
   elements still to place fit on their own.

   Usage: onesum_naive N K
   Prints "none N K nodes" or "found N K nodes : a_1 ... a_K" (increasing): is there a K-set
   in {1..N} containing 1 and N in which at most one sum a + b (a <= b) occurs more than once? */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 400
#define MAXK 64
static int N, K, found, S[MAXK + 1], reps[2 * MAXN + 2], repeated;
static long long nodes;

/* reps[s] = representations of s; repeated = number of values s with reps[s] > 1 */
static void bump(int s, int sign) {
    if (sign > 0 && ++reps[s] == 2) repeated++;
    if (sign < 0 && reps[s]-- == 2) repeated--;
}
static void put(int k, int x, int sign) {       /* S[0..k-1] present, x joins or leaves */
    for (int i = 0; i < k; i++) bump(S[i] + x, sign);
    bump(2 * x, sign);
}

static void search(int k, int below) {          /* S[0..k-1] chosen; next element < below */
    nodes++;
    if (k == K) { found = 1; return; }
    int left = K - k;                           /* inner elements still to place */
    int room = 0;                               /* values below that fit on their own */
    for (int x = below - 1; x >= 2 && room < left; x--) {
        put(k, x, 1);
        room += repeated <= 1;
        put(k, x, -1);
    }
    if (room < left) return;
    for (int x = below - 1; x >= 2 && x - 1 >= left; x--) {
        put(k, x, 1);
        if (repeated <= 1) {
            S[k] = x;
            search(k + 1, x);
        }
        put(k, x, -1);
        if (found) return;
    }
}

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: onesum_naive N K\n"); return 2; }
    N = atoi(argv[1]); K = atoi(argv[2]);
    if (N < 1 || N > MAXN || K < 1 || K > MAXK) {
        fprintf(stderr, "need 1 <= N <= %d and 1 <= K <= %d\n", MAXN, MAXK);
        return 2;
    }
    memset(reps, 0, sizeof reps);
    int k = 0;
    S[k] = 1; put(k, 1, 1); k++;
    if (K >= 2 && N > 1) { S[k] = N; put(k, N, 1); k++; }
    if (K <= k) { nodes = 1; found = K == k; }
    else if (N > 1) search(k, N);
    else nodes = 1;
    printf("%s %d %d %lld", found ? "found" : "none", N, K, nodes);
    if (found) {
        for (int i = 1; i < K; i++) for (int j = i; j > 0 && S[j - 1] > S[j]; j--) {
            int t = S[j]; S[j] = S[j - 1]; S[j - 1] = t;
        }
        printf(" :");
        for (int i = 0; i < K; i++) printf(" %d", S[i]);
    }
    printf("\n");
    return 0;
}

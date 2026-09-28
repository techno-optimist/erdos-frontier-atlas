/* Erdős #864: sets whose pairwise sums are distinct except for at most one value.
   C port of one_exception.Search, node for node.

   A389182(N) is the largest A in {1..N} such that among the sums a + b (a <= b in A) at most one
   value occurs more than once.  The property survives translation and the reflection
   x -> N + 1 - x.  So if a(N - 1) = K - 1, a K-set in {1..N} contains 1 and N, else a translate
   would lie in {1..N-1}.  The search decides whether such a K-set exists.

   1 and N are placed first; the inner elements are added in increasing order.  cnt[s] counts the
   representations of s so far and exc is the repeated value, or -1 while every sum is distinct.
   A new x is admissible iff each new sum x + a (a in A, and 2x) is either unused, or equal to
   exc, or, while exc = -1, the first used one, which becomes exc.  Admissibility only shrinks as
   A grows, so each node keeps the candidates admissible so far and re-tests only those.
   Symmetry: of a set and its reflection, only the one whose first inner element s has
   s - 1 <= N - t, t the last inner element, is searched, so every later inner element is at most
   N + 1 - s.  A node is dropped when fewer candidates remain than elements still to place.

   Usage: onesum N K
   Prints "none N K nodes" or "found N K nodes : a_1 ... a_K" (increasing).  nodes counts every
   call of the search, root included. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 400
#define MAXK 64
static int N, K, A[MAXK + 1], cnt[2 * MAXN + 2], exc, found;
static long long nodes;
static int cand[MAXK + 1][MAXN], ncand[MAXK + 1];

/* the exception after adding x to A[0..d-1], or -2 if x is not admissible */
static int admit(int d, int x) {
    int e = exc;
    for (int i = 0; i <= d; i++) {
        int s = x + (i < d ? A[i] : x);
        if (cnt[s] && s != e) {
            if (e != -1) return -2;
            e = s;
        }
    }
    return e;
}
static void place(int d, int x, int sign) {
    for (int i = 0; i < d; i++) cnt[x + A[i]] += sign;
    cnt[2 * x] += sign;
}

static void dfs(int d) {
    nodes++;
    if (d == K) { found = 1; return; }
    int need = K - d;
    if (ncand[d] < need) return;
    for (int i = 0; i + need <= ncand[d]; i++) {
        int x = cand[d][i], e = admit(d, x), save = exc;
        place(d, x, 1); A[d] = x; exc = e;
        int hi = d == 2 ? N + 1 - x : N, m = 0;
        for (int j = i + 1; j < ncand[d]; j++) {
            int y = cand[d][j];
            if (y <= hi && admit(d + 1, y) != -2) cand[d + 1][m++] = y;
        }
        ncand[d + 1] = m;
        dfs(d + 1);
        place(d, x, -1); exc = save;
        if (found) return;
    }
}

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: onesum N K\n"); return 2; }
    N = atoi(argv[1]); K = atoi(argv[2]);
    if (N < 1 || N > MAXN || K < 1 || K > MAXK) {
        fprintf(stderr, "need 1 <= N <= %d and 1 <= K <= %d\n", MAXN, MAXK);
        return 2;
    }
    memset(cnt, 0, sizeof cnt);
    exc = -1;
    int d = 0;
    A[d] = 1; place(d, 1, 1); d++;
    if (K >= 2 && N > 1) {                       /* N itself: 1 + N and 2N are new sums */
        A[d] = N; place(d, N, 1); d++;
    }
    if (K <= d) {
        nodes = 1; found = K == d;
    } else if (N > 1) {
        int m = 0;
        for (int y = 2; y < N; y++) if (admit(d, y) != -2) cand[d][m++] = y;
        ncand[d] = m;
        dfs(d);
    } else {
        nodes = 1;
    }
    printf("%s %d %d %lld", found ? "found" : "none", N, K, nodes);
    if (found) {
        int B[MAXK + 1];
        for (int i = 0; i < K; i++) B[i] = A[i];
        for (int i = 1; i < K; i++) for (int j = i; j > 0 && B[j - 1] > B[j]; j--) {
            int t = B[j]; B[j] = B[j - 1]; B[j - 1] = t;
        }
        printf(" :");
        for (int i = 0; i < K; i++) printf(" %d", B[i]);
    }
    printf("\n");
    return 0;
}

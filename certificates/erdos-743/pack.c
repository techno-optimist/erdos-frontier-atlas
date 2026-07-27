/* pack.c — Erdős #743 (Gyárfás tree packing) exhaustive test at K_n.
 *
 * Conjecture: for any trees T_2,...,T_n with |V(T_k)| = k, K_n is the
 * edge-disjoint union of the T_k. The edge count is exact —
 * sum_{k=2}^{n} (k-1) = C(n,2) — so this is a PERFECT decomposition with no
 * slack: every edge of K_n is used exactly once.
 *
 * Frontier: Fishburn 1983 verified n <= 9. This program tests every tuple at
 * a given n; n = 9 is therefore a positive control (all tuples must pack) and
 * n = 10 is the open case.
 *
 * WLOG on T_n. T_n is spanning (n vertices, n-1 edges). Any packing maps to
 * one with T_n at a fixed embedding by permuting V(K_n), and permutations are
 * automorphisms of K_n, so fixing ONE embedding of T_n loses nothing. Nothing
 * analogous is done for T_{n-1} — that would be unsound, since after T_n is
 * pinned the remaining symmetry is only the stabiliser of T_n, not S_n.
 *
 * No other reduction is assumed. In particular Bollobás's greedy result for
 * the smallest floor(n/sqrt 2) trees is NOT used to skip work: the search
 * places every tree itself, so a misreading of the literature cannot silently
 * shrink the sweep.
 *
 *   cc -O2 -o pack pack.c
 *   ./pack trees.txt <n> [shard] [nshards]
 *   ./pack --selftest trees.txt
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXN 12
#define MAXTREES 512

typedef uint64_t u64;

static int NV;                       /* n, the order of K_n */
static int eidx[MAXN][MAXN];         /* edge index of {u,v} */
static int NE;                       /* C(n,2) */

typedef struct {
    int k;                           /* vertices */
    int parent[MAXN];                /* parent[i] for i>=1, parents precede */
    int prev_leaf_sib[MAXN];         /* symmetry break: see below, or -1 */
} Tree;

static Tree trees[MAXTREES];
static int ntrees;
static int byk_start[MAXN + 1], byk_count[MAXN + 1];

static void build_edge_index(int n)
{
    NV = n;
    NE = 0;
    for (int u = 0; u < n; u++)
        for (int v = u + 1; v < n; v++) {
            eidx[u][v] = eidx[v][u] = NE++;
        }
}

static int load_trees(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "cannot open %s\n", path); return 0; }
    char line[512];
    ntrees = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == '#' || line[0] == '\n') continue;
        char *p = line;
        int k = (int)strtol(p, &p, 10);
        if (k < 2 || k > MAXN) continue;
        Tree *t = &trees[ntrees++];
        t->k = k;
        t->parent[0] = -1;
        for (int i = 1; i < k; i++) t->parent[i] = (int)strtol(p, &p, 10);
        /* SYMMETRY BREAK. Swapping two leaf children of the same parent is an
         * automorphism of the tree, so a packing exists iff one exists with
         * those leaves mapped in increasing order. Without this the search
         * explores all m! orderings of a star's leaves; the hardest tuples at
         * n=10 are exactly the ones where T_4..T_7 are all stars, so the
         * factorial blow-up lands precisely where the conjecture is least
         * covered by theory. Sound: it prunes only images of automorphic
         * configurations, never a distinct packing. */
        int isleaf[MAXN];
        for (int i = 0; i < k; i++) isleaf[i] = 1;
        for (int i = 1; i < k; i++) isleaf[t->parent[i]] = 0;
        for (int i = 1; i < k; i++) {
            t->prev_leaf_sib[i] = -1;
            if (!isleaf[i]) continue;
            for (int j = i - 1; j >= 1; j--)
                if (t->parent[j] == t->parent[i] && isleaf[j]) {
                    t->prev_leaf_sib[i] = j;
                    break;
                }
        }
    }
    fclose(f);
    for (int k = 0; k <= MAXN; k++) { byk_start[k] = -1; byk_count[k] = 0; }
    for (int i = 0; i < ntrees; i++) {
        int k = trees[i].k;
        if (byk_start[k] < 0) byk_start[k] = i;
        byk_count[k]++;
    }
    return ntrees;
}

/* ---- embedding search -------------------------------------------------- */
/* Map tree vertices 0..k-1 to distinct K_n vertices so every tree edge lands
 * on a currently-unused K_n edge. Tree vertices are visited in index order,
 * and parents precede children, so each new vertex has exactly one constraint:
 * the edge to its already-placed parent must be free. */

static u64 g_used;                   /* bitmask of consumed K_n edges */
static int g_img[MAXN];              /* tree vertex -> K_n vertex */
static int g_taken[MAXN];            /* K_n vertex in use by this tree */
static const Tree *g_t;

/* Per-tuple search budget. Cost is wildly uneven: nearly every tuple packs in
 * a handful of nodes, but a thin tail needs far more, and a genuinely
 * unpackable tuple needs the WHOLE tree exhausted. Capping keeps one hard
 * tuple from blocking a shard; capped tuples are reported as HARD (never as
 * unpackable) and re-run uncapped. Conflating "gave up" with "no packing
 * exists" would be the single worst bug this program could have. */
static long long g_budget = 0;       /* 0 = unlimited */
static long long g_tuple_nodes;
static int g_exhausted;              /* set when the budget aborted a tuple */

static int embed_from(const Tree *t, int i, int (*cont)(void))
{
    if (g_exhausted) return 0;
    if (++g_tuple_nodes > g_budget && g_budget) { g_exhausted = 1; return 0; }
    if (i == t->k) return cont();
    int par = t->parent[i];
    int sib = t->prev_leaf_sib[i];
    int lo = (sib >= 0) ? g_img[sib] + 1 : 0;     /* symmetry break */
    for (int v = lo; v < NV; v++) {
        if (g_taken[v]) continue;
        int e = eidx[g_img[par]][v];
        if (g_used >> e & 1ULL) continue;
        g_taken[v] = 1;
        g_img[i] = v;
        g_used |= 1ULL << e;
        if (embed_from(t, i + 1, cont)) return 1;
        g_used &= ~(1ULL << e);
        g_taken[v] = 0;
    }
    return 0;
}

/* The tuple currently being tested: shape index chosen for each k. */
static int g_shape[MAXN + 1];
static int g_level;                  /* current k being placed */
static long long g_nodes;

static int cont_next(void);

static int place_tree_k(int k)
{
    if (k < 2) return 1;                         /* everything placed */
    const Tree *t = &trees[byk_start[k] + g_shape[k]];
    g_nodes++;
    /* root of this tree may go anywhere unused */
    for (int r = 0; r < NV; r++) {
        memset(g_taken, 0, sizeof g_taken);
        g_taken[r] = 1;
        g_img[0] = r;
        g_t = t;
        g_level = k;
        u64 save = g_used;
        if (embed_from(t, 1, cont_next)) return 1;
        g_used = save;
    }
    return 0;
}

static int cont_next(void)
{
    int k = g_level;
    /* save/restore the per-tree scratch across the recursive descent */
    int save_img[MAXN], save_taken[MAXN], save_level = g_level;
    memcpy(save_img, g_img, sizeof g_img);
    memcpy(save_taken, g_taken, sizeof g_taken);
    const Tree *save_t = g_t;
    int ok = place_tree_k(k - 1);
    memcpy(g_img, save_img, sizeof g_img);
    memcpy(g_taken, save_taken, sizeof g_taken);
    g_t = save_t;
    g_level = save_level;
    return ok;
}

/* Fix one embedding of the spanning tree T_n: vertex i of the tree -> vertex i
 * of K_n. Sound because vertex permutations are automorphisms of K_n. */
static u64 fixed_spanning_mask(const Tree *t)
{
    u64 m = 0;
    for (int i = 1; i < t->k; i++) m |= 1ULL << eidx[i][t->parent[i]];
    return m;
}

static int tuple_packs(int n)
{
    const Tree *top = &trees[byk_start[n] + g_shape[n]];
    g_used = fixed_spanning_mask(top);
    return place_tree_k(n - 1);
}

/* ---- selftest ---------------------------------------------------------- */
static int selftest(void)
{
    int fails = 0;
    /* K_3 = T_2 (one edge) + T_3 (path, 2 edges): 1+2 = 3 = C(3,2). Packs. */
    build_edge_index(3);
    g_shape[2] = 0; g_shape[3] = 0;
    if (!tuple_packs(3)) { printf("SELFTEST FAIL: K_3 must pack\n"); fails++; }

    /* PLANTED FAILURE: demand one edge too many. Replace T_2 by a second copy
     * of T_3 (3 edges total needed beyond T_3's 2 = 4 > 3 available). The
     * search MUST refuse. A packer that always says yes dies here. */
    build_edge_index(3);
    {
        u64 save = g_used;
        const Tree *t3 = &trees[byk_start[3]];
        g_used = fixed_spanning_mask(t3);          /* 2 edges used */
        /* now try to place ANOTHER 3-vertex tree (2 more edges) in 1 free edge */
        g_shape[3] = 0;
        int ok = place_tree_k(3);
        if (ok) { printf("SELFTEST FAIL: over-full packing ACCEPTED\n"); fails++; }
        g_used = save;
    }

    /* K_4: T_2+T_3+T_4 = 1+2+3 = 6 = C(4,2). Both shapes of T_4 must pack. */
    build_edge_index(4);
    for (int s = 0; s < byk_count[4]; s++) {
        g_shape[2] = g_shape[3] = 0; g_shape[4] = s;
        if (!tuple_packs(4)) {
            printf("SELFTEST FAIL: K_4 tuple shape %d must pack\n", s);
            fails++;
        }
    }
    printf("SELFTEST %s\tfailures=%d\n", fails ? "FAIL" : "PASS", fails);
    return fails;
}

int main(int argc, char **argv)
{
    if (argc >= 3 && strcmp(argv[1], "--selftest") == 0) {
        if (!load_trees(argv[2])) return 2;
        return selftest() ? 1 : 0;
    }
    if (argc >= 5 && strcmp(argv[1], "--tuples") == 0) {
        /* Re-run a named list of tuple indices, by default UNCAPPED. This is
         * how budget-aborted (HARD) tuples get their real answer: a capped
         * abort is never reported as unpackable. */
        if (!load_trees(argv[2])) return 2;
        int n = atoi(argv[3]);
        build_edge_index(n);
        g_budget = argc > 5 ? atoll(argv[5]) : 0;
        FILE *f = fopen(argv[4], "r");
        if (!f) { fprintf(stderr, "cannot open %s\n", argv[4]); return 2; }
        long long idx, tested = 0, unpackable = 0, hard = 0;
        clock_t t0 = clock();
        while (fscanf(f, "%lld", &idx) == 1) {
            long long r = idx;
            for (int k = 2; k <= n; k++) {
                g_shape[k] = (int)(r % byk_count[k]);
                r /= byk_count[k];
            }
            tested++;
            g_tuple_nodes = 0;
            g_exhausted = 0;
            int ok = tuple_packs(n);
            if (!ok && g_exhausted) {
                hard++;
                printf("HARD\ttuple=%lld\n", idx);
                fflush(stdout);
            } else if (!ok) {
                unpackable++;
                printf("UNPACKABLE\ttuple=%lld\tshapes=", idx);
                for (int k = 2; k <= n; k++) printf("%d%s", g_shape[k],
                                                    k == n ? "\n" : ",");
                fflush(stdout);
            }
        }
        fclose(f);
        printf("SUMMARY\tn=%d\tlist=%s\ttuples=%lld\tunpackable=%lld"
               "\thard=%lld\tbudget=%lld\tsecs=%.1f\n",
               n, argv[4], tested, unpackable, hard, g_budget,
               (double)(clock() - t0) / CLOCKS_PER_SEC);
        return 0;
    }
    if (argc < 3) {
        fprintf(stderr, "usage: %s <trees.txt> <n> [shard] [nshards] [node_budget]\n"
                        "       %s --tuples <trees.txt> <n> <list> [budget]\n"
                        "       %s --selftest <trees.txt>\n",
                argv[0], argv[0], argv[0]);
        return 2;
    }
    if (!load_trees(argv[1])) return 2;
    int n = atoi(argv[2]);
    long long shard = argc > 3 ? atoll(argv[3]) : 0;
    long long nshards = argc > 4 ? atoll(argv[4]) : 1;
    g_budget = argc > 5 ? atoll(argv[5]) : 0;
    if (n < 3 || n > MAXN) { fprintf(stderr, "n out of range\n"); return 2; }
    build_edge_index(n);

    long long total = 1;
    for (int k = 2; k <= n; k++) total *= byk_count[k];
    if (shard == 0)
        fprintf(stderr, "# n=%d, %lld tuples, %d edges, shards=%lld\n",
                n, total, NE, nshards);

    long long tested = 0, unpackable = 0, hard = 0;
    clock_t t0 = clock();
    for (long long idx = shard; idx < total; idx += nshards) {
        long long r = idx;
        for (int k = 2; k <= n; k++) {
            g_shape[k] = (int)(r % byk_count[k]);
            r /= byk_count[k];
        }
        tested++;
        g_tuple_nodes = 0;
        g_exhausted = 0;
        int ok = tuple_packs(n);
        if (!ok && g_exhausted) {
            hard++;
            printf("HARD\ttuple=%lld\tshapes=", idx);
            for (int k = 2; k <= n; k++) printf("%d%s", g_shape[k],
                                                k == n ? "\n" : ",");
            fflush(stdout);
        } else if (!ok) {
            unpackable++;
            printf("UNPACKABLE\ttuple=%lld\tshapes=", idx);
            for (int k = 2; k <= n; k++) printf("%d%s", g_shape[k],
                                                k == n ? "\n" : ",");
            fflush(stdout);
        }
    }
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("SUMMARY\tn=%d\tshard=%lld/%lld\ttuples=%lld\tunpackable=%lld"
           "\thard=%lld\tbudget=%lld\tnodes=%lld\tsecs=%.1f\n",
           n, shard, nshards, tested, unpackable, hard, g_budget, g_nodes, secs);
    return 0;
}

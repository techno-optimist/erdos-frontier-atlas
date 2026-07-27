#!/usr/bin/env python3
"""Free (unlabeled, unrooted) tree generation — reference implementation.

WROM: Wright, Richmond, Odlyzko & McKay, "Constant time generation of free
trees", SIAM J. Comput. 15 (1986) 540-548 — the algorithm behind nauty's
gentreeg. A tree on n vertices is represented by its canonical LEVEL SEQUENCE
L[0..n-1]: root the tree at the centroid, and L[i] is the depth of vertex i in
a depth-first order that visits subtrees in non-increasing lexicographic order.
Each free tree has exactly one such canonical sequence, so successive
generation of canonical sequences enumerates free trees without duplication.

This file is the slow, obviously-correct oracle. The sweep uses a C port; the
verifier cross-checks the two, and both are pinned to OEIS A000055.

  python3 -I freetrees.py 12        # count free trees on 1..12 vertices
"""
import sys

# OEIS A000055, number of free trees on n nodes, n = 0..24.
A000055 = [1, 1, 1, 1, 2, 3, 6, 11, 23, 47, 106, 235, 551, 1301, 3159, 7741,
           19320, 48629, 123867, 317955, 823065, 2144505, 5623756, 14828074,
           39299897]


def rooted_trees(n):
    """Yield the level sequence of every ROOTED tree on n vertices, once each
    (Beyer-Hedetniemi successor). Counts give OEIS A000081."""
    if n < 1:
        return
    if n == 1:
        yield [0]
        return
    L = list(range(n))
    while True:
        yield list(L)
        p = n - 1
        while p > 0 and L[p] == 1:
            p -= 1
        if p == 0:
            return
        q = p - 1
        while L[q] != L[p] - 1:
            q -= 1
        L[p] -= 1
        for i in range(p + 1, n):
            L[i] = L[i - p + q]


def free_trees(n):
    """Yield one parent array per FREE tree on n vertices.

    Deliberately the slow, obviously-correct construction: enumerate every
    ROOTED tree and keep one representative per isomorphism class of the
    underlying free tree. Counts give OEIS A000055. This is the oracle — the
    sweep uses a fast generator that this file exists to check.
    """
    seen = set()
    for L in rooted_trees(n):
        par = parents_from_levels(L)
        key = canonical_form(n, edges_from_parents(par))
        if key not in seen:
            seen.add(key)
            yield par


def parents_from_levels(L):
    """Parent array from a level sequence (vertex 0 is the root)."""
    n = len(L)
    parent = [-1] * n
    stack = {}
    for i, d in enumerate(L):
        stack[d] = i
        if d > 0:
            parent[i] = stack[d - 1]
    return parent


def edges_from_parents(parent):
    return [(i, parent[i]) for i in range(1, len(parent)) if parent[i] >= 0]


def _adj(n, edges):
    a = [[] for _ in range(n)]
    for u, v in edges:
        a[u].append(v)
        a[v].append(u)
    return a


def centroids(n, edges):
    """The 1 or 2 centroid vertices of a tree."""
    a = _adj(n, edges)
    size = [1] * n
    order, seen, stack = [], [False] * n, [0]
    par = [-1] * n
    seen[0] = True
    while stack:
        v = stack.pop()
        order.append(v)
        for w in a[v]:
            if not seen[w]:
                seen[w] = True
                par[w] = v
                stack.append(w)
    for v in reversed(order):
        if par[v] >= 0:
            size[par[v]] += size[v]
    best, res = n + 1, []
    for v in range(n):
        m = max([size[w] for w in a[v] if w != par[v]] + [n - size[v]])
        if m < best:
            best, res = m, [v]
        elif m == best:
            res.append(v)
    return res


def _rooted_canon(v, parent, a):
    """Canonical string of the subtree rooted at v (AHU-style)."""
    subs = sorted(_rooted_canon(w, v, a) for w in a[v] if w != parent)
    return "(" + "".join(subs) + ")"


def canonical_level_sequence(parent):
    """The canonical (lexicographically greatest) centroid-rooted level
    sequence of the tree given by a parent array."""
    n = len(parent)
    edges = edges_from_parents(parent)
    a = _adj(n, edges)
    best = None
    for c in centroids(n, edges):
        seq = []

        def walk(v, p, depth):
            seq.append(depth)
            kids = sorted((w for w in a[v] if w != p),
                          key=lambda w: _rooted_canon(w, v, a), reverse=True)
            for w in kids:
                walk(w, v, depth + 1)
        walk(c, -1, 0)
        if best is None or seq > best:
            best = seq
    return best


def canonical_form(n, edges):
    """Isomorphism-invariant key for a tree given as an edge list."""
    a = _adj(n, edges)
    best = None
    for c in centroids(n, edges):
        s = _rooted_canon(c, -1, a)
        if best is None or s < best:
            best = s
    return best


def all_free_trees_bruteforce(n):
    """Independent oracle: every labeled tree via Prüfer, deduped by canonical
    form. Exponential, only for small n — this is the cross-check."""
    import itertools
    if n == 1:
        return {"()"}
    if n == 2:
        return {canonical_form(2, [(0, 1)])}
    seen = set()
    for seq in itertools.product(range(n), repeat=n - 2):
        deg = [1] * n
        for x in seq:
            deg[x] += 1
        s = list(seq)
        edges, d = [], deg[:]
        used = [False] * n
        for x in s:
            for v in range(n):
                if d[v] == 1 and not used[v]:
                    edges.append((v, x))
                    d[v] -= 1
                    d[x] -= 1
                    used[v] = True
                    break
        rest = [v for v in range(n) if d[v] == 1 and not used[v]]
        edges.append((rest[0], rest[1]))
        seen.add(canonical_form(n, edges))
    return seen


def main():
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    ok = True
    for n in range(1, nmax + 1):
        c = sum(1 for _ in free_trees(n))
        want = A000055[n]
        flag = "OK " if c == want else "BAD"
        if c != want:
            ok = False
        print(f"  n={n:3d}  generated={c:8d}  A000055={want:8d}  {flag}")
    print("A000055 match" if ok else "MISMATCH")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()

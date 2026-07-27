#!/usr/bin/env python3
"""Emit every free tree on 2..N vertices, as parent arrays, for the packer.

Self-contained by design: a certificate must not depend on another
certificate's files. Counts are pinned to OEIS A000055, so a generation bug
cannot pass silently.

  python3 -I gen_trees.py 10 > trees.txt

Format: one tree per line, "<k> <p_1> <p_2> ... <p_{k-1}>" where p_i is the
parent of vertex i (vertex 0 is the root, parents precede children).
"""
import sys

A000055 = [1, 1, 1, 1, 2, 3, 6, 11, 23, 47, 106, 235, 551, 1301, 3159]


def rooted_level_sequences(n):
    """Beyer-Hedetniemi successor over rooted trees (counts = A000081)."""
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


def parents_from_levels(L):
    parent, at = [-1] * len(L), {}
    for i, d in enumerate(L):
        at[d] = i
        if d > 0:
            parent[i] = at[d - 1]
    return parent


def adj(n, parent):
    a = [[] for _ in range(n)]
    for i in range(1, n):
        a[i].append(parent[i])
        a[parent[i]].append(i)
    return a


def centroids(n, a):
    if n == 1:
        return [0]
    size, par, order, seen, stack = [1] * n, [-1] * n, [], [False] * n, [0]
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


def rooted_canon(v, p, a):
    return "(" + "".join(sorted(rooted_canon(w, v, a)
                                for w in a[v] if w != p)) + ")"


def canonical_form(n, parent):
    a = adj(n, parent)
    return min(rooted_canon(c, -1, a) for c in centroids(n, a))


def free_trees(n):
    """One parent array per free tree on n vertices (counts = A000055)."""
    if n == 1:
        return [[-1]]
    out, seen = [], set()
    for L in rooted_level_sequences(n):
        par = parents_from_levels(L)
        key = canonical_form(n, par)
        if key not in seen:
            seen.add(key)
            out.append(par)
    return out


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    lines, bad = [], False
    for k in range(2, N + 1):
        ts = free_trees(k)
        if len(ts) != A000055[k]:
            print(f"# FATAL k={k}: generated {len(ts)} != A000055 {A000055[k]}",
                  file=sys.stderr)
            bad = True
        for par in ts:
            lines.append(f"{k} " + " ".join(str(par[i]) for i in range(1, k)))
    if bad:
        raise SystemExit(1)
    print("\n".join(lines))
    print(f"# emitted {len(lines)} trees for k=2..{N}, counts match A000055",
          file=sys.stderr)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Erdős #617 at r=5: is there a balanced 5-colouring of K_26?

The conjecture (Erdős–Gyárfás): for r >= 3, every r-colouring of K_{r^2+1}
contains r+1 vertices whose induced K_{r+1} misses a colour. For r = 5 that is
K_26 with 5 colours and 6-subsets. A COUNTEREXAMPLE is a "balanced" colouring:
every 6-subset sees all 5 colours.

Equivalently, per colour c let G_c be the graph of c-coloured edges. A 6-set
missing colour c is an independent 6-set of G_c, so balanced means
alpha(G_c) <= 5 for every c.

  python3 -I build_cnf.py 26 > k26.cnf      # the open case
  python3 -I build_cnf.py 25 > k25.cnf      # known SAT (lower bound witness)
  python3 -I build_cnf.py --extend > ext.cnf  # does the known K_25 colouring
                                              # extend to K_26 by one vertex?

Encoding: x[e][c] for each of the C(n,2) edges and 5 colours; exactly-one per
edge; and for every 6-subset S and colour c, a clause saying c occurs among the
15 edges induced by S.
"""
import sys
from itertools import combinations

R = 5
COLOURS = range(R)


def edge_index(n):
    idx, k = {}, 0
    for u, v in combinations(range(n), 2):
        idx[(u, v)] = k
        k += 1
    return idx


def var(e, c):
    return e * R + c + 1


# --------------------------------------------------------------- AG(2,5) ----
def affine_plane_colouring():
    """A balanced 5-colouring of K_25 from AG(2,5).

    AG(2,5) has q+1 = 6 parallel classes, one more than we have colours. Each
    class is a partition of the 25 points into 5 lines of 5, so as a graph it
    is 5 disjoint K_5's with independence number exactly 5 — precisely the
    bound we need. Colours 0..4 take classes 0..4; the SIXTH class is then
    distributed arbitrarily among the five colours, which is safe because
    ADDING edges to G_c can only DECREASE alpha(G_c). Without that step only
    250 of the 300 edges would be coloured.
    """
    pts = [(x, y) for x in range(5) for y in range(5)]
    pos = {p: i for i, p in enumerate(pts)}

    def direction(p, q):
        dx, dy = (q[0] - p[0]) % 5, (q[1] - p[1]) % 5
        if dx == 0:
            return 5                       # the vertical class
        return (dy * pow(dx, -1, 5)) % 5   # slope classes 0..4

    col = {}
    for p, q in combinations(pts, 2):
        d = direction(p, q)
        u, v = sorted((pos[p], pos[q]))
        col[(u, v)] = d if d < 5 else 0    # class 5 folded into colour 0
    return col


def is_balanced(n, col):
    """Every 6-subset sees all 5 colours. Exact, exhaustive."""
    bad = []
    for S in combinations(range(n), 6):
        seen = {col[(u, v)] for u, v in combinations(sorted(S), 2)}
        if len(seen) < R:
            bad.append((S, sorted(seen)))
            if len(bad) > 5:
                break
    return bad


# ------------------------------------------------------------------ CNF -----
def emit_full(n, out):
    idx = edge_index(n)
    clauses = []
    for e in idx.values():
        clauses.append([var(e, c) for c in COLOURS])
        for a, b in combinations(COLOURS, 2):
            clauses.append([-var(e, a), -var(e, b)])
    for S in combinations(range(n), 6):
        es = [idx[(u, v)] for u, v in combinations(S, 2)]
        for c in COLOURS:
            clauses.append([var(e, c) for e in es])
    out.write(f"p cnf {len(idx) * R} {len(clauses)}\n")
    for cl in clauses:
        out.write(" ".join(map(str, cl)) + " 0\n")
    return len(idx) * R, len(clauses)


def emit_extension(out):
    """Fix the AG(2,5) colouring on K_25 and ask whether one new vertex (25 new
    edges) can be coloured so every 6-set through it still sees all 5 colours.

    NOTE ON SCOPE: a NEGATIVE here refutes only THIS K_25 colouring, not the
    conjecture — many balanced colourings of K_25 exist. It is a cheap probe,
    not a proof. (The converse direction IS sound: every balanced colouring of
    K_26 restricts to a balanced colouring of K_25 on any 25 vertices, since a
    6-subset of those 25 is still a 6-subset of the 26.)
    """
    col = affine_plane_colouring()
    n = 26
    new = 25                                  # the added vertex
    clauses = []
    # variables: only the 25 new edges (new, t) for t in 0..24
    def nvar(t, c):
        return t * R + c + 1
    for t in range(25):
        clauses.append([nvar(t, c) for c in COLOURS])
        for a, b in combinations(COLOURS, 2):
            clauses.append([-nvar(t, a), -nvar(t, b)])
    for T in combinations(range(25), 5):
        have = {col[(u, v)] for u, v in combinations(T, 2)}
        for c in COLOURS:
            if c in have:
                continue                      # already satisfied by old edges
            clauses.append([nvar(t, c) for t in T])
    out.write(f"p cnf {25 * R} {len(clauses)}\n")
    for cl in clauses:
        out.write(" ".join(map(str, cl)) + " 0\n")
    return 25 * R, len(clauses)


def main():
    args = sys.argv[1:]
    if "--check-ap" in args:
        col = affine_plane_colouring()
        bad = is_balanced(25, col)
        used = sorted({c for c in col.values()})
        print(f"AG(2,5) colouring of K_25: colours used {used}, "
              f"edges {len(col)} (expect 300)", file=sys.stderr)
        if bad:
            print(f"NOT BALANCED: {len(bad)} bad 6-sets, e.g. {bad[0]}",
                  file=sys.stderr)
            raise SystemExit(1)
        print("BALANCED: all C(25,6)=177100 six-subsets see all 5 colours",
              file=sys.stderr)
        return
    if "--extend" in args:
        v, c = emit_extension(sys.stdout)
        print(f"extension CNF: {v} vars, {c} clauses", file=sys.stderr)
        return
    n = int(args[0]) if args else 26
    v, c = emit_full(n, sys.stdout)
    print(f"K_{n} balanced-5-colouring CNF: {v} vars, {c} clauses",
          file=sys.stderr)


if __name__ == "__main__":
    main()

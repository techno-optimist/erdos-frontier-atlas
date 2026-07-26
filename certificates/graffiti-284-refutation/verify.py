#!/usr/bin/env python3
"""Independent replay of an EXTERNAL refutation of Graffiti conjecture 284.

WHOSE RESULT THIS IS
--------------------
The counterexample is NOT ours. Nathan Wilbanks and "Annie" (AGNT Labs,
"Graffiti 284 Refuted by Hoffman-Singleton -- AGNT Labs Verification Note",
2026-07-23) identified the Hoffman-Singleton graph as a counterexample to
Graffiti 284. This directory contributes the independent, dependency-free,
exactly-arithmetic verification only. Nothing here is claimed as a discovery
of this repository.

WHAT IS CHECKED (all exact; no float anywhere in the trust path)
---------------------------------------------------------------
Graffiti 284 (Fajtlowicz), as stated by the authors:
    if girth(G) >= 5 then  min_v d*(v)  <=  -lambda_min(D(G)),
    where d*(v) = (1/deg v) * sum_{u ~ v} deg(u) is the dual degree
    (mean degree of the neighbours of v) and D(G) is the distance matrix.

Legs:
  1. BUILD the Hoffman-Singleton graph from Robertson's pentagon/pentagram
     definition -- not from a library constant. 5 pentagons P_h (j ~ j+-1),
     5 pentagrams Q_i (j ~ j+-2), and P_h[j] ~ Q_i[(h*i + j) mod 5].
  2. IDENTIFY it: n=50, m=175, 7-regular, connected, every adjacent pair has
     0 common neighbours and every non-adjacent pair exactly 1 (srg(50,7,0,1)),
     and girth exactly 5 computed by BFS (not assumed from the parameters).
  3. DISTANCE MATRIX by BFS, integer entries; diameter 2; symmetric; zero
     diagonal; and the integer identity D = 2(J - I) - A.
  4. lambda_min(D) = -4 EXACTLY, by two independent integer arguments plus a
     rational multiplicity count:
       (a) (D - 91I)(D - I)(D + 4I) = 0 as an integer matrix.  An annihilating
           polynomial confines the spectrum to its roots, so every eigenvalue
           of D lies in {91, 1, -4} and lambda_min >= -4.
       (b) an exhibited nonzero INTEGER vector v with D v = -4 v, so -4 really
           is attained and lambda_min <= -4.  (a)+(b) give lambda_min = -4.
       (c) exact rational rank/nullity: dim ker(D - 91I) = 1,
           dim ker(D + 4I) = 28, dim ker(D - I) = 21, summing to 50 -- so the
           spectrum is exactly {91^1, (-4)^28, 1^21} with nothing else.
       (d) trace identities tr(D^k) for k=1,2,3 against that spectrum.
  5. MINIMUM DUAL DEGREE COMPUTED from the graph with Fraction arithmetic --
     never asserted.  See the README: the authors' own shipped verifier
     hardcodes `min_dual = 7` and `rhs = 4` as literals; those two numbers are
     the entire refutation, and they are the two this script refuses to assume.
  6. VERDICT: girth 5 >= 5, computed min dual degree 7, computed
     -lambda_min(D) = 4, and 7 <= 4 is false.

PLANTED-FAILURE CONTROLS (the point of the lane)
------------------------------------------------
Six, each of which MUST be rejected, printing as `[ok] rejected: ...`.
A checker that cannot fail certifies nothing -- and neither does a CONTROL
that cannot fail, which is why the count here is six rather than the nine
this lane once advertised. See the note above control C5.

THE QUOTED EXTERNAL ARTIFACT
----------------------------
The `min_dual = 7` / `rhs = 4` lines this lane quotes and re-creates as
control C4 come from the authors' shipped verifier, which is a SEPARATE
artifact from the prose note -- the note does not serve that code:
    https://agnt.gg/whitepapers/graffiti-284-artifacts/verify_284_hoffman_singleton_exact.py
    sha256 7d58813fa2b9f151eb4ac39dc342244503772702fc75c24f4052eed7653c97f2
    3380 bytes, read 2026-07-25, quoted lines 69-70.
That digest also matches the authors' own published SHA256SUMS.txt. We are
publishing criticism of named third parties: the reader must be able to fetch
the exact bytes we read, and a silent edit must be detectable.

WHAT IS NOT CERTIFIED
---------------------
See README.md `not_certified_here`: novelty, priority, the authors' own
artifacts, Graffiti's provenance, and everything about 284 other than the
falsity of its universally-quantified statement.

Replay (from the repository root):
    python3 -I certificates/graffiti-284-refutation/verify.py
Emit the receipt instead of checking it (deliberate, never on a normal run):
    python3 -I certificates/graffiti-284-refutation/verify.py --emit
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "receipt.json"

FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> bool:
    tag = "[ok]" if ok else "[FAIL]"
    print(f"  {tag} {label}" + (f"  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)
    return ok


def rejected(label: str, was_rejected: bool, detail: str = "") -> bool:
    """A planted failure: `was_rejected` must be True or the checker is blind."""
    if was_rejected:
        print(f"  [ok] rejected: {label}" + (f"  --  {detail}" if detail else ""))
    else:
        print(f"  [FAIL] NOT rejected: {label}" + (f"  --  {detail}" if detail else ""))
        FAILURES.append(f"control not rejected: {label}")
    return was_rejected


# --------------------------------------------------------------------------
# Graphs.  A graph is (n, adj) with adj a list of frozensets of neighbours.
# --------------------------------------------------------------------------

def graph_from_edges(n: int, edges) -> tuple[int, list[frozenset]]:
    nbrs = [set() for _ in range(n)]
    for u, v in edges:
        if u == v:
            raise ValueError("loop")
        nbrs[u].add(v)
        nbrs[v].add(u)
    return n, [frozenset(s) for s in nbrs]


def hoffman_singleton():
    """Robertson's pentagon/pentagram construction, built here from scratch.

    Vertices: P_{h,j} -> index 5h + j (h,j in 0..4);  Q_{i,j} -> 25 + 5i + j.
    Edges:   pentagon  P_h[j] ~ P_h[j+1 mod 5]
             pentagram Q_i[j] ~ Q_i[j+2 mod 5]
             cross     P_h[j] ~ Q_i[(h*i + j) mod 5]
    """
    def P(h, j):
        return 5 * h + (j % 5)

    def Q(i, j):
        return 25 + 5 * i + (j % 5)

    edges = []
    for h in range(5):
        for j in range(5):
            edges.append((P(h, j), P(h, j + 1)))
    for i in range(5):
        for j in range(5):
            edges.append((Q(i, j), Q(i, j + 2)))
    for h in range(5):
        for i in range(5):
            for j in range(5):
                edges.append((P(h, j), Q(i, (h * i + j) % 5)))
    return graph_from_edges(50, edges)


def petersen():
    """Outer 5-cycle 0..4, inner pentagram 5..9, spokes i ~ i+5."""
    edges = []
    for j in range(5):
        edges.append((j, (j + 1) % 5))
        edges.append((5 + j, 5 + (j + 2) % 5))
        edges.append((j, 5 + j))
    return graph_from_edges(10, edges)


def k33():
    return graph_from_edges(6, [(a, b) for a in range(3) for b in range(3, 6)])


def hs_rewired():
    """Hoffman-Singleton with one 2-swap: a corrupted 7-regular impostor."""
    n, adj = hoffman_singleton()
    edges = sorted({(min(u, v), max(u, v)) for u in range(n) for v in adj[u]})
    eset = set(edges)
    # Search for two vertex-disjoint edges whose cross-connections are non-edges,
    # so the swap preserves 7-regularity and m=175 and can only be caught by the
    # srg identity -- not by a degree count. Deterministic: first pair in order.
    for a in edges:
        for b in edges:
            if b <= a or set(a) & set(b):
                continue
            new = [(min(a[0], b[0]), max(a[0], b[0])), (min(a[1], b[1]), max(a[1], b[1]))]
            if any(e in eset for e in new):
                continue
            return graph_from_edges(n, sorted((eset - {a, b}) | set(new)))
    raise AssertionError("no admissible 2-swap found")


# --------------------------------------------------------------------------
# Exact graph invariants -- all integer / Fraction.
# --------------------------------------------------------------------------

def degrees(g):
    _, adj = g
    return [len(s) for s in adj]


def edge_count(g):
    return sum(degrees(g)) // 2


def bfs_levels(g, src):
    n, adj = g
    dist = [-1] * n
    dist[src] = 0
    frontier = [src]
    while frontier:
        nxt = []
        for u in frontier:
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    nxt.append(v)
        frontier = nxt
    return dist


def is_connected(g):
    n, _ = g
    return all(d >= 0 for d in bfs_levels(g, 0)) if n else True


def distance_matrix(g):
    """Exact integer distance matrix by BFS. Returns None if disconnected."""
    n, _ = g
    D = []
    for s in range(n):
        row = bfs_levels(g, s)
        if any(d < 0 for d in row):
            return None
        D.append(row)
    return D


def girth(g):
    """Exact girth by BFS from every vertex (inf -> None for a forest).

    For each root the BFS finds, for every non-tree edge (x,y), a closed walk of
    length dist[x]+dist[y]+1; minimising over ALL roots yields the true girth.
    """
    n, adj = g
    best = None
    for root in range(n):
        dist = [-1] * n
        parent = [-1] * n
        dist[root] = 0
        frontier = [root]
        while frontier:
            nxt = []
            for u in frontier:
                for v in adj[u]:
                    if dist[v] < 0:
                        dist[v] = dist[u] + 1
                        parent[v] = u
                        nxt.append(v)
                    elif v != parent[u]:
                        cyc = dist[u] + dist[v] + 1
                        if best is None or cyc < best:
                            best = cyc
            frontier = nxt
    return best


def common_neighbour_profile(g):
    """(set of |N(u) & N(v)| over adjacent pairs, same over non-adjacent pairs)."""
    n, adj = g
    lam, mu = set(), set()
    for u in range(n):
        for v in range(u + 1, n):
            c = len(adj[u] & adj[v])
            (lam if v in adj[u] else mu).add(c)
    return lam, mu


def min_dual_degree(g):
    """COMPUTED, never assumed: min over v of the mean degree of N(v).

    Exact Fraction so a non-regular graph gives an honest rational, not a
    rounded integer. Isolated vertices have no dual degree and are skipped.
    """
    n, adj = g
    deg = degrees(g)
    best = None
    argmin = None
    for v in range(n):
        if deg[v] == 0:
            continue
        d_star = Fraction(sum(deg[u] for u in adj[v]), deg[v])
        if best is None or d_star < best:
            best, argmin = d_star, v
    return best, argmin


# --------------------------------------------------------------------------
# Exact linear algebra over Z and Q. No float, no eigensolver.
# --------------------------------------------------------------------------

def mat_sub_scalar(M, lam):
    """M - lam*I over the integers."""
    return [[M[i][j] - (lam if i == j else 0) for j in range(len(M))] for i in range(len(M))]


def mat_mul(A, B):
    n, k, m = len(A), len(B), len(B[0])
    Bt = list(zip(*B))
    return [[sum(A[i][t] * Bt[j][t] for t in range(k)) for j in range(m)] for i in range(n)]


def is_zero(M):
    return all(all(x == 0 for x in row) for row in M)


def trace_powers(M, kmax):
    """[tr(M), tr(M^2), ..., tr(M^kmax)] over the integers."""
    n = len(M)
    out = []
    P = [row[:] for row in M]
    for _ in range(kmax):
        out.append(sum(P[i][i] for i in range(n)))
        P = mat_mul(P, M)
    return out


def rank_exact(M):
    """Exact rank over Q by fraction-free (Bareiss) elimination -- integers only.

    Every division is asserted exact; Bareiss guarantees it (Sylvester's
    identity), so a nonzero remainder means the implementation drifted and the
    run must abort rather than report a rank it cannot justify.
    """
    A = [row[:] for row in M]
    n, m = len(A), len(A[0])
    rank = 0
    prev = 1
    row = 0
    for col in range(m):
        piv = None
        for r in range(row, n):
            if A[r][col] != 0:
                piv = r
                break
        if piv is None:
            continue
        A[row], A[piv] = A[piv], A[row]
        pivot = A[row][col]
        for r in range(row + 1, n):
            factor = A[r][col]
            for c in range(col + 1, m):
                num = A[r][c] * pivot - A[row][c] * factor
                q, rem = divmod(num, prev)
                if rem:
                    raise ArithmeticError("Bareiss division was not exact")
                A[r][c] = q
            A[r][col] = 0
        prev = pivot
        row += 1
        rank += 1
        if row == n:
            break
    return rank


def integer_kernel_vector(M):
    """One nonzero INTEGER vector in ker(M), or None. Exact Fraction elimination.

    Denominators are cleared at the end so the returned witness can be checked
    against M with pure integer arithmetic.
    """
    n, m = len(M), len(M[0])
    A = [[Fraction(x) for x in row] for row in M]
    pivots = []
    row = 0
    for col in range(m):
        piv = None
        for r in range(row, n):
            if A[r][col] != 0:
                piv = r
                break
        if piv is None:
            continue
        A[row], A[piv] = A[piv], A[row]
        inv = A[row][col]
        A[row] = [x / inv for x in A[row]]
        for r in range(n):
            if r != row and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * b for a, b in zip(A[r], A[row])]
        pivots.append(col)
        row += 1
        if row == n:
            break
    free = [c for c in range(m) if c not in pivots]
    if not free:
        return None
    f0 = free[0]
    v = [Fraction(0)] * m
    v[f0] = Fraction(1)
    for r, c in enumerate(pivots):
        v[c] = -A[r][f0]
    den = 1
    for x in v:
        d = x.denominator
        g = den
        b = d
        while b:
            g, b = b, g % b
        den = den * d // g
    iv = [int(x * den) for x in v]
    g = 0
    for x in iv:
        a, b = abs(x), g
        while a:
            a, b = b % a, a
        g = b
    if g > 1:
        iv = [x // g for x in iv]
    return iv


def mat_vec(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]


# --------------------------------------------------------------------------
# The pipeline: everything a Graffiti-284 counterexample claim needs.
# --------------------------------------------------------------------------

def spectrum_of_distance_matrix(D, candidates):
    """Exact spectrum of the integer symmetric matrix D, given candidate roots.

    Returns (eigenvalues_with_multiplicity, annihilator_is_zero, witness) where
    the multiplicity of lam is dim ker(D - lam I) computed by exact rank, and
    annihilator_is_zero says whether prod_lam (D - lam I) is the zero matrix.
    The two together pin the spectrum: the annihilator confines it to the
    candidate set, the nullities show the candidates exhaust dimension n.
    """
    n = len(D)
    mults = {}
    for lam in candidates:
        mults[lam] = n - rank_exact(mat_sub_scalar(D, lam))
    prod = None
    for lam in candidates:
        blk = mat_sub_scalar(D, lam)
        prod = blk if prod is None else mat_mul(prod, blk)
    lam_min = min(candidates)
    witness = integer_kernel_vector(mat_sub_scalar(D, lam_min))
    return mults, is_zero(prod), witness


def graffiti_284_report(g, name, candidates):
    """Everything COMPUTED from the graph. No number here is a literal."""
    n, _ = g
    D = distance_matrix(g)
    if D is None:
        return {"name": name, "connected": False}
    mults, annihilated, witness = spectrum_of_distance_matrix(D, candidates)
    md, argmin = min_dual_degree(g)
    spectrum_complete = sum(mults.values()) == n and annihilated
    lam_min = min(l for l, m in mults.items() if m > 0)
    return {
        "name": name,
        "connected": True,
        "n": n,
        "m": edge_count(g),
        "degrees": sorted(set(degrees(g))),
        "girth": girth(g),
        "diameter": max(max(row) for row in D),
        "multiplicities": mults,
        "spectrum_complete": spectrum_complete,
        "lambda_min_D": lam_min,
        "min_dual_degree": md,
        "min_dual_degree_vertex": argmin,
        "hypothesis_girth_ge_5": girth(g) is not None and girth(g) >= 5,
        "conjecture_284_holds": md <= -lam_min,
        "refutes_284": (girth(g) is not None and girth(g) >= 5) and not (md <= -lam_min),
        "_D": D,
        "_witness": witness,
    }


def paper_style_hardcoded_verdict(_g):
    """A faithful re-creation of the DEFECT, used only as a planted control.

    The authors' shipped verify_284_hoffman_singleton_exact.py (sha256
    7d58813f..., 3380 bytes; see the module docstring for the URL) sets at
    lines 69-70, verbatim:
        min_dual = 7  # every neighbor of every vertex has degree 7
        rhs = 4       # -lambda_min(D)
    Both decisive numbers are literals: the graph argument is never read. This
    function reproduces that logic so the control below can show it returning
    "REFUTED" for a graph that in fact satisfies Graffiti 284.
    """
    min_dual = 7
    rhs = 4
    return min_dual > rhs


# --------------------------------------------------------------------------

def main() -> int:
    emit = "--emit" in sys.argv[1:]
    for arg in sys.argv[1:]:
        if arg != "--emit":
            print(f"unknown argument: {arg}", file=sys.stderr)
            return 2

    print("Graffiti 284 -- independent replay of an EXTERNAL refutation")
    print("external result: Nathan Wilbanks & \"Annie\" (AGNT Labs, 2026-07-23);")
    print("this directory contributes the independent verification only.")
    print()

    # ---- Leg 1-2: build and identify the graph -----------------------------
    print("[1] Hoffman-Singleton, built from Robertson's pentagon/pentagram definition")
    HS = hoffman_singleton()
    n, adj = HS
    check("n = 50", n == 50, f"n={n}")
    check("m = 175", edge_count(HS) == 175, f"m={edge_count(HS)}")
    check("7-regular", sorted(set(degrees(HS))) == [7], f"degrees={sorted(set(degrees(HS)))}")
    check("connected", is_connected(HS))
    lam_set, mu_set = common_neighbour_profile(HS)
    check("adjacent pairs share 0 common neighbours (lambda=0)", lam_set == {0}, f"observed={sorted(lam_set)}")
    check("non-adjacent pairs share exactly 1 (mu=1)", mu_set == {1}, f"observed={sorted(mu_set)}")
    g_hs = girth(HS)
    check("girth = 5 (computed by BFS, not inferred)", g_hs == 5, f"girth={g_hs}")
    print("      => the constructed object is srg(50,7,0,1) of girth 5: the Hoffman-Singleton graph")
    print()

    # ---- Leg 3: distance matrix -------------------------------------------
    print("[2] distance matrix by BFS -- exact integers")
    D = distance_matrix(HS)
    check("D is symmetric with zero diagonal",
          all(D[i][j] == D[j][i] for i in range(n) for j in range(n))
          and all(D[i][i] == 0 for i in range(n)))
    offdiag = {D[i][j] for i in range(n) for j in range(n) if i != j}
    check("diameter 2 (every off-diagonal entry is 1 or 2)", offdiag == {1, 2}, f"entries={sorted(offdiag)}")
    A = [[1 if j in adj[i] else 0 for j in range(n)] for i in range(n)]
    # J[i][j] = 1 for all i,j;  I[i][j] = 1 iff i == j.
    ident = all(D[i][j] == 2 * (1 - (1 if i == j else 0)) - A[i][j]
                for i in range(n) for j in range(n))
    check("integer identity D = 2(J - I) - A", ident)
    print()

    # ---- Leg 4: exact smallest eigenvalue ----------------------------------
    print("[3] lambda_min(D) = -4, exactly -- no eigensolver, no float")
    CAND = (91, 1, -4)
    mults, annihilated, witness = spectrum_of_distance_matrix(D, CAND)
    check("(D - 91I)(D - I)(D + 4I) = 0 over Z  =>  spec(D) subset {91, 1, -4}", annihilated)
    check("dim ker(D - 91I) = 1", mults[91] == 1, f"got {mults[91]}")
    check("dim ker(D + 4I) = 28", mults[-4] == 28, f"got {mults[-4]}")
    check("dim ker(D - I) = 21", mults[1] == 21, f"got {mults[1]}")
    check("multiplicities exhaust dimension 50  =>  nothing else is an eigenvalue",
          sum(mults.values()) == 50, f"sum={sum(mults.values())}")
    ok_wit = witness is not None and any(x != 0 for x in witness) \
        and mat_vec(D, witness) == [-4 * x for x in witness]
    check("exhibited integer v != 0 with D v = -4 v  =>  -4 is attained", ok_wit,
          f"||v||_inf={max(abs(x) for x in witness) if witness else 0}")
    tr = trace_powers(D, 3)
    expect = [sum(m * lam ** k for lam, m in mults.items()) for k in (1, 2, 3)]
    check("tr(D), tr(D^2), tr(D^3) agree with that spectrum", tr == expect,
          f"tr={tr} expected={expect}")
    print("      => lambda_min(D) = -4 exactly;  -lambda_min(D) = 4")
    print()

    # ---- Leg 5: the number the authors' script does not compute -----------
    print("[4] minimum dual degree -- COMPUTED from the graph, not asserted")
    md, argmin = min_dual_degree(HS)
    check("min dual degree is an exact rational", isinstance(md, Fraction))
    check("min_v d*(v) = 7", md == 7, f"d*_min = {md} attained at vertex {argmin}")
    print("      (the authors' shipped verifier sets `min_dual = 7` as a literal;")
    print("       this line is the reason the lane exists -- see README.md)")
    print()

    # ---- Leg 6: the verdict ------------------------------------------------
    print("[5] verdict")
    rep = graffiti_284_report(HS, "hoffman-singleton", CAND)
    check("hypothesis holds: girth >= 5", rep["hypothesis_girth_ge_5"])
    check("conclusion fails: min dual degree > -lambda_min(D)", not rep["conjecture_284_holds"],
          f"{rep['min_dual_degree']} <= {-rep['lambda_min_D']} is false")
    check("margin = 3 (exact integer)", rep["min_dual_degree"] - (-rep["lambda_min_D"]) == 3)
    check("this constitutes a counterexample to Graffiti 284", rep["refutes_284"])
    print()

    # ---- Planted-failure controls -----------------------------------------
    print("[6] planted-failure controls -- each MUST be rejected")

    # C1: the girth hypothesis is load-bearing. K_{3,3} has min dual degree 3
    #     and -lambda_min(D) = 2, so 3 <= 2 fails -- but its girth is 4, so it
    #     is NOT a counterexample. A checker that skipped the hypothesis would
    #     accept it.
    K = k33()
    rk = graffiti_284_report(K, "k33", (7, 1, -2))
    rejected("girth-4 graph K_{3,3} offered as a 284 counterexample",
             (rk["girth"] == 4) and (not rk["hypothesis_girth_ge_5"]) and (not rk["refutes_284"]),
             f"girth={rk['girth']}, min d*={rk['min_dual_degree']}, "
             f"-lambda_min={-rk['lambda_min_D']} (conclusion fails but hypothesis does not hold)")

    # C2: wrong eigenvalue -- claim lambda_min = -3 (too big) or -5 (too small).
    for bad in (-3, -5):
        bad_mults = {bad: len(D) - rank_exact(mat_sub_scalar(D, bad))}
        blk = mat_sub_scalar(D, bad)
        prod = mat_mul(mat_mul(mat_sub_scalar(D, 91), mat_sub_scalar(D, 1)), blk)
        rejected(f"claimed lambda_min(D) = {bad}",
                 bad_mults[bad] == 0 and not is_zero(prod),
                 f"dim ker(D - ({bad})I) = {bad_mults[bad]}; annihilator with root {bad} is nonzero")

    # C3: corrupted graph -- a 2-swap keeps it 7-regular on 50 vertices but
    #     destroys srg(50,7,0,1); the identification gate must not pass it.
    BAD = hs_rewired()
    bl, bm = common_neighbour_profile(BAD)
    rejected("Hoffman-Singleton with one 2-swap presented as HS",
             sorted(set(degrees(BAD))) == [7] and edge_count(BAD) == 175
             and not (bl == {0} and bm == {1}),
             f"still 7-regular with m=175, but lambda-values={sorted(bl)}, mu-values={sorted(bm)}")

    # C4: THE HEADLINE. Hardcoded-vs-computed. The paper-style checker asserts
    #     min_dual = 7 and rhs = 4 as literals, so it returns "REFUTED" for ANY
    #     input -- including the Petersen graph, which satisfies Graffiti 284.
    PET = petersen()
    rp = graffiti_284_report(PET, "petersen", (15, 0, -3))
    hardcoded_says_refuted = paper_style_hardcoded_verdict(PET)
    rejected("hardcoded (min_dual=7, rhs=4) verdict applied to the Petersen graph",
             hardcoded_says_refuted and rp["hypothesis_girth_ge_5"] and rp["conjecture_284_holds"]
             and not rp["refutes_284"],
             f"hardcoded verdict says REFUTED; computed: girth={rp['girth']}, "
             f"min d*={rp['min_dual_degree']}, -lambda_min={-rp['lambda_min_D']}, "
             f"so {rp['min_dual_degree']} <= {-rp['lambda_min_D']} HOLDS")

    # (An earlier revision of this lane also "rejected" the assertions
    #  min d* in {6, 8, 3} on Hoffman-Singleton. Those were removed, not
    #  renamed: each merely evaluated `Fraction(literal) != md` against the
    #  already-computed `md`, so each still printed `[ok] rejected` under the
    #  one defect this lane exists to catch -- min_dual_degree() stubbed to
    #  return the literal 7 -- while only C4 below actually fired. A control
    #  that survives the mutation it is supposed to detect is not a control,
    #  and counting it inflates the score. See README, "Planted-failure
    #  controls".)

    # C5: the checker must reject a claimed integer eigenvector that is not one.
    fake = list(witness)
    fake[0] += 1
    rejected("perturbed eigenvector witness for -4",
             mat_vec(D, fake) != [-4 * x for x in fake])
    print()

    # ---- Receipt: CHECK by default, --emit only ---------------------------
    computed = {
        "schema": "efa-graffiti-284-v1",
        "external_result": {
            "claim": "Graffiti conjecture 284 is false",
            "counterexample": "Hoffman-Singleton graph",
            "authors": ["Nathan Wilbanks", "Annie"],
            "affiliation": "AGNT Labs",
            "source": "https://agnt.gg/whitepapers/graffiti-284-refutation.html",
            # The note above is prose and does NOT serve the code this lane
            # quotes and rebuilds as control C4. The quoted file is a separate
            # artifact; it is pinned by digest so a reader can locate the exact
            # bytes we read and detect a silent edit.
            "quoted_artifact": {
                "url": "https://agnt.gg/whitepapers/graffiti-284-artifacts/"
                       "verify_284_hoffman_singleton_exact.py",
                "sha256": "7d58813fa2b9f151eb4ac39dc342244503772702fc75c24f4052eed7653c97f2",
                "bytes": 3380,
                "read_date": "2026-07-25",
                "digest_agrees_with_authors_sha256sums": True,
                "quoted_lines": [69, 70],
            },
            "our_contribution": "independent exact replay only; not a discovery of this repository",
        },
        "graph": {
            "construction": "Robertson pentagon/pentagram, built in this script",
            "n": rep["n"], "m": rep["m"], "regular_degree": 7,
            "srg_parameters": [50, 7, 0, 1],
            "girth_computed": rep["girth"],
            "diameter": rep["diameter"],
        },
        "distance_spectrum": {
            "eigenvalues": {"91": mults[91], "1": mults[1], "-4": mults[-4]},
            "annihilating_polynomial_vanishes": annihilated,
            "multiplicities_sum": sum(mults.values()),
            "lambda_min": rep["lambda_min_D"],
            "method": "integer annihilating polynomial + exact Bareiss rank + integer eigenvector",
        },
        "min_dual_degree": {
            "computed": str(rep["min_dual_degree"]),
            "attained_at_vertex": rep["min_dual_degree_vertex"],
            "hardcoded_in_external_verifier": 7,
            "agrees": Fraction(7) == rep["min_dual_degree"],
        },
        "verdict": {
            "hypothesis_girth_ge_5": rep["hypothesis_girth_ge_5"],
            "conjecture_284_holds": rep["conjecture_284_holds"],
            "margin": int(rep["min_dual_degree"] - (-rep["lambda_min_D"])),
            "refutes_284": rep["refutes_284"],
        },
        # Six, and every one of them load-bearing: each dies under at least one
        # source mutation. Deliberately NOT the count of `[ok] rejected` lines
        # a reader could tally -- a control that cannot fail must not be scored.
        "controls_rejected": 6,
    }

    if emit:
        RECEIPT.write_text(json.dumps(computed, indent=2, sort_keys=True) + "\n")
        print(f"receipt-emitted: {RECEIPT.name}")
    else:
        if not RECEIPT.is_file():
            check(f"receipt {RECEIPT.name} exists", False)
        else:
            stored = json.loads(RECEIPT.read_text())
            drift = sorted(k for k in set(stored) | set(computed)
                           if stored.get(k) != computed.get(k))
            check("committed receipt matches this run (no drift)", not drift,
                  f"drifting fields: {drift}" if drift else "")
            # Flush-left and exactly this spelling: tools/check_receipt_drift.py
            # scores a check-only verifier's coverage off `line.startswith(...)`.
            print(f"receipt-checked: {RECEIPT.name}")
    print()

    if FAILURES:
        print(f"FAIL -- {len(FAILURES)} check(s) failed:")
        for f in FAILURES:
            print(f"  - {f}")
        return 1

    # The claim string is the most-copied artifact this lane produces, so the
    # transcription caveat has to travel inside it -- "the statement as given",
    # plus an explicit not_checked field. What is certified is that a specific
    # sentence is false, not that the sentence is Fajtlowicz's conjecture 284.
    print('{"claim":"The Graffiti 284 statement as given -- if girth(G) >= 5 then '
          'min dual degree <= -lambda_min(D(G)) -- is FALSE: the Hoffman-Singleton graph '
          'has girth 5, computed minimum dual degree 7, and distance-matrix smallest '
          'eigenvalue exactly -4",'
          '"not_checked":"that this statement is conjecture 284 of Fajtlowicz\'s Graffiti '
          'list; the statement is taken as transcribed by the authors cited below",'
          '"attribution":"external (Wilbanks & Annie, AGNT Labs); this repository verified only",'
          '"valid":true}')
    print("PASS -- external refutation independently verified; all planted controls rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

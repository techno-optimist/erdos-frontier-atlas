#!/usr/bin/env python3
"""Independent replay of an EXTERNAL refutation of Graffiti conjecture 284.

WHOSE RESULT THIS IS
--------------------
The counterexample is NOT ours. Nathan Wilbanks and Annie (AGNT Labs,
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
     Every value of lambda_min that this script goes on to USE passes
     lambda_min_is_derived() first: that gate re-derives the minimum from the
     multiplicity table and then demands an integer eigenvector for the value
     actually offered, so a lambda_min that was typed rather than computed is
     rejected on the verdict path itself (control C5 exercises exactly that).
  5. MINIMUM DUAL DEGREE COMPUTED from the graph with Fraction arithmetic --
     never asserted.  See the README: the authors' own shipped verifier
     never asserts lambda_min(D) at all and hand-types both sides of its final
     comparison (`min_dual = 7`, `rhs = 4`); those two numbers are the entire
     refutation, and they are the two this script refuses to assume.
  6. VERDICT: girth 5 >= 5, computed min dual degree 7, computed
     -lambda_min(D) = 4, and 7 <= 4 is false.

PLANTED-FAILURE CONTROLS (the point of the lane)
------------------------------------------------
Eight, each of which MUST be rejected, printing as `[ok] rejected: ...`.
A checker that cannot fail certifies nothing -- and neither does a CONTROL
that cannot fail, which is why three earlier "controls" were deleted rather
than renamed. See the note after control C4.

The count is measured, not asserted: the exit gate compares the number of
controls that actually EXECUTED against EXPECTED_CONTROLS, and the receipt
publishes the measured number, so deleting a control block fails the run.

WHAT THIS VERIFIER CANNOT DEFEND AGAINST
----------------------------------------
It defends against corrupted DATA: a wrong graph, a wrong distance matrix, a
wrong eigenvalue, a wrong dual degree, a poisoned receipt field.  Every one of
those is caught by a check or a control here.

It does NOT defend against a corrupted VERIFIER -- against edits to THIS FILE.
No script can. Stub a function, no-op an accumulator, hardcode a constant in
the verdict path, and the surviving code is simply a different program that
prints PASS.  The exit gate below is made tamper-EVIDENT (it recomputes the
verdict from the per-check and per-control results recorded at call time
instead of trusting the FAILURES side effect, and cross-checks the two
accountings), which raises the number of edits an attacker needs -- it does not
reduce it to infinity.

The real defenses against that threat are outside this file:
  * certificates/contracts.json pins the sha256 of this file AND of
    receipt.json, and tools/check_certificate_contracts.py fails if either
    byte-string moves;
  * that contract also pins the decisive stdout lines and forbids "[FAIL]"
    anywhere in the output;
  * git history and review make the edit itself visible.
Read this file's diff, not only its output.

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

# The numbers this lane PUBLISHES about the Hoffman-Singleton graph. Each one is
# compared against a value computed from the graph; none of them is ever used to
# produce one. They exist so that a check reads "computed == claimed" rather than
# comparing a value to itself.
CLAIM_MIN_DUAL = Fraction(7)
CLAIM_LAMBDA_MIN = -4
CLAIM_MARGIN = 3

# How many planted controls this file is supposed to contain. Compared against
# the number that actually executed -- see the exit gate.
EXPECTED_CONTROLS = 8

# Per-result ledgers. These are what the exit gate recomputes from; FAILURES is
# a convenience list for the human-readable summary and is NOT trusted alone.
CHECKS: list[tuple[str, bool]] = []
CONTROLS: list[tuple[str, bool]] = []
FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> bool:
    ok = bool(ok)
    CHECKS.append((label, ok))
    tag = "[ok]" if ok else "[FAIL]"
    print(f"  {tag} {label}" + (f"  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)
    return ok


def rejected(label: str, was_rejected: bool, detail: str = "") -> bool:
    """A planted failure: `was_rejected` must be True or the checker is blind."""
    was_rejected = bool(was_rejected)
    CONTROLS.append((label, was_rejected))
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


def c7_with_pendant():
    """7-cycle 0..6 plus a pendant vertex 7 hung off vertex 0.

    girth 7 (so the >= 5 hypothesis holds) and deliberately NOT regular: the
    degrees are 3 at vertex 0, 2 around the rest of the cycle, 1 at the pendant.
    Its minimum dual degree is d*(0) = (2 + 2 + 1)/3 = 5/3.

    Every other graph in this lane -- Hoffman-Singleton, Petersen, K_{3,3}, the
    2-swapped impostor -- is regular, so every dual degree there has denominator
    1 and exact rational division is indistinguishable from integer truncation.
    This graph is the only input that can tell them apart, which is why control
    C7 exists and why the README's "an honest fraction, not a rounded integer"
    claim is testable rather than decorative.
    """
    edges = [(j, (j + 1) % 7) for j in range(7)]
    edges.append((0, 7))
    return graph_from_edges(8, edges)


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


def lambda_min_is_derived(D, mults, annihilated, lam_min):
    """Gate: on THIS evidence, is `lam_min` really the least eigenvalue of D?

    Returns (ok, why). This is what stands between a lambda_min that was
    computed and one that was typed, and it is on the verdict path -- every
    lambda_min this script publishes or compares has passed through here.

      * the annihilating polynomial over the candidate set must vanish and the
        multiplicities must exhaust dimension n, or `mults` is not known to be
        the whole spectrum and nothing can be minimal over it;
      * `lam_min` must equal the least candidate with nonzero nullity -- a
        hand-typed value that is not the true minimum dies here;
      * ker(D - lam_min I) must contain a nonzero INTEGER vector v with
        D v = lam_min v, checked in integer arithmetic -- a hand-typed value
        that is not an eigenvalue of D at all dies here.

    Note what this does and does not buy: it makes a literal lambda_min WRONG
    rather than merely unjustified, so the failure is mechanical. It cannot stop
    someone from editing this function. See the module docstring.
    """
    n = len(D)
    if not annihilated:
        return False, "annihilating polynomial does not vanish: the spectrum is not confined"
    if sum(mults.values()) != n:
        return False, f"multiplicities sum to {sum(mults.values())}, not n={n}"
    attained = sorted(l for l, m in mults.items() if m > 0)
    if not attained:
        return False, "no candidate eigenvalue has nonzero nullity"
    if lam_min != attained[0]:
        return False, (f"offered lambda_min={lam_min}, but the least eigenvalue with nonzero "
                       f"multiplicity is {attained[0]} (attained: {attained})")
    v = integer_kernel_vector(mat_sub_scalar(D, lam_min))
    if v is None or all(x == 0 for x in v):
        return False, f"ker(D - ({lam_min})I) is trivial: {lam_min} is not an eigenvalue of D"
    if mat_vec(D, v) != [lam_min * x for x in v]:
        return False, f"the exhibited kernel vector does not satisfy D v = {lam_min} v"
    return True, (f"least attained eigenvalue of a spectrum that exhausts dim {n}, "
                  f"with an integer eigenvector (||v||_inf={max(abs(x) for x in v)})")


def graffiti_284_report(g, name, candidates):
    """Everything COMPUTED from the graph. No number here is a literal.

    lambda_min is derived from the multiplicity table and then put through
    lambda_min_is_derived() before anything downstream may use it. If that gate
    says no, this function records a failed check and publishes NO verdict for
    the graph -- no lambda_min, no margin, no refutes_284 -- because printing a
    verdict about a named third party's graph on an underived number is the
    exact defect this lane criticises.
    """
    n, _ = g
    D = distance_matrix(g)
    if D is None:
        return {"name": name, "connected": False}
    mults, annihilated, witness = spectrum_of_distance_matrix(D, candidates)
    md, argmin = min_dual_degree(g)
    spectrum_complete = sum(mults.values()) == n and annihilated
    lam_min = min(l for l, m in mults.items() if m > 0)
    lam_ok, lam_why = lambda_min_is_derived(D, mults, annihilated, lam_min)
    check(f"lambda_min({name}) = {lam_min} is DERIVED from the checked spectrum, not asserted",
          lam_ok, lam_why)
    hypothesis = girth(g) is not None and girth(g) >= 5
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
        "lambda_min_derived_ok": lam_ok,
        "lambda_min_derivation": lam_why,
        "lambda_min_D": lam_min if lam_ok else None,
        "min_dual_degree": md,
        "min_dual_degree_vertex": argmin,
        "hypothesis_girth_ge_5": hypothesis,
        "conjecture_284_holds": (md <= -lam_min) if lam_ok else None,
        "refutes_284": (hypothesis and not (md <= -lam_min)) if lam_ok else None,
        "_D": D,
        "_witness": witness,
    }


def report_line(rep):
    """One honest sentence about a graph -- or a refusal to produce one."""
    if not rep.get("lambda_min_derived_ok"):
        return ("no verdict printed: lambda_min was not derived -- "
                + rep.get("lambda_min_derivation", "?"))
    lhs, rhs = rep["min_dual_degree"], -rep["lambda_min_D"]
    return (f"girth={rep['girth']}, min d*={lhs}, -lambda_min={rhs}, "
            f"so {lhs} <= {rhs} {'HOLDS' if rep['conjecture_284_holds'] else 'FAILS'}")


def paper_style_hardcoded_verdict(_g):
    """A faithful re-creation of the DEFECT, used only as a planted control.

    To be fair to the authors: their shipped verify_284_hoffman_singleton_exact.py
    (sha256 7d58813f..., 3380 bytes; see the module docstring for the URL)
    genuinely checks a great deal in exact integer arithmetic -- the strongly
    regular identity A@A + A - 6I == J (L38-39), tr(A) = 0 and tr(A^2) = 2m = 350
    (L43-44), the eigenvalue-multiplicity system at L48, and the distance facts
    that the off-diagonal entries are {1, 2} and D == 2(J - I) - A (L57-59). Its
    one floating-point eigensolver call is explicitly fenced in the source as a
    "float sanity cross-check only (not part of the proof)", which is honest.

    The defect is narrow and total: lambda_min(D) = -4 is never ASSERTED
    anywhere -- L61-62 are print statements -- and the final comparison is
    between two hand-typed literals, at L69-70 verbatim:
        min_dual = 7  # every neighbor of every vertex has degree 7
        rhs = 4       # -lambda_min(D)
    The graph argument is never read on that path, so the script certifies
    everything except the inequality it exists to refute. This function
    reproduces that logic so the control below can show it returning "REFUTED"
    for a graph that in fact satisfies Graffiti 284.
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
    print("external result: Nathan Wilbanks & Annie (AGNT Labs, 2026-07-23);")
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
    check(f"computed min_v d*(v) equals the published claim {CLAIM_MIN_DUAL}",
          md == CLAIM_MIN_DUAL, f"computed d*_min = {md} attained at vertex {argmin}")
    print("      (the authors' shipped verifier sets `min_dual = 7` as a literal;")
    print("       this line is the reason the lane exists -- see README.md)")
    print()

    # ---- Leg 6: the verdict ------------------------------------------------
    print("[5] verdict")
    rep = graffiti_284_report(HS, "hoffman-singleton", CAND)
    check("lambda_min for the verdict graph passed the derivation gate",
          rep["lambda_min_derived_ok"], rep["lambda_min_derivation"])
    check("hypothesis holds: girth >= 5", rep["hypothesis_girth_ge_5"])
    check(f"computed lambda_min(D) equals the published claim {CLAIM_LAMBDA_MIN}",
          rep["lambda_min_D"] == CLAIM_LAMBDA_MIN, f"computed lambda_min = {rep['lambda_min_D']}")
    check("conclusion fails: min dual degree > -lambda_min(D)",
          rep["conjecture_284_holds"] is False, report_line(rep))
    margin = rep["min_dual_degree"] - (-rep["lambda_min_D"])
    check(f"computed margin min d* - (-lambda_min) equals the published claim {CLAIM_MARGIN}",
          margin == CLAIM_MARGIN and margin.denominator == 1, f"computed margin = {margin}")
    check("this constitutes a counterexample to Graffiti 284", rep["refutes_284"] is True)
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
             rk["lambda_min_derived_ok"] and (rk["girth"] == 4)
             and (not rk["hypothesis_girth_ge_5"]) and rk["refutes_284"] is False,
             f"{report_line(rk)} -- conclusion fails, but the hypothesis does not hold")

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
             hardcoded_says_refuted and rp["lambda_min_derived_ok"]
             and rp["hypothesis_girth_ge_5"] and rp["conjecture_284_holds"] is True
             and rp["refutes_284"] is False,
             f"hardcoded verdict says REFUTED; computed: {report_line(rp)}")

    # C5: THE SAME DEFECT, AIMED AT US. This lane's public thesis is "their
    #     verifier hardcodes the decisive number, ours computes it" -- so the
    #     derivation gate that carries our lambda_min has to reject a literal.
    #     The Petersen distance spectrum is {15, (-3)^5, 0^4}: -4 is not an
    #     eigenvalue of it at all, so a typed `lam_min = -4` -- exactly the
    #     source mutation this control exists to catch -- must die here while
    #     the genuinely derived -3 passes.
    D_pet = distance_matrix(PET)
    m_pet, ann_pet, _ = spectrum_of_distance_matrix(D_pet, (15, 0, -3))
    literal_ok, literal_why = lambda_min_is_derived(D_pet, m_pet, ann_pet, -4)
    derived_ok, _ = lambda_min_is_derived(D_pet, m_pet, ann_pet, -3)
    rejected("lambda_min asserted as the literal -4 on the Petersen graph",
             (not literal_ok) and derived_ok,
             f"gate says: {literal_why}; the derived value -3 passes the same gate")

    # (An earlier revision of this lane also "rejected" the assertions
    #  min d* in {6, 8, 3} on Hoffman-Singleton. Those were removed, not
    #  renamed: each merely evaluated `Fraction(literal) != md` against the
    #  already-computed `md`, so each still printed `[ok] rejected` under the
    #  one defect this lane exists to catch -- min_dual_degree() stubbed to
    #  return the literal 7 -- while only C4 above actually fired. A control
    #  that survives the mutation it is supposed to detect is not a control,
    #  and counting it inflates the score. See README, "Planted-failure
    #  controls".)

    # C6: the checker must reject a claimed integer eigenvector that is not one.
    fake = list(witness)
    fake[0] += 1
    rejected("perturbed eigenvector witness for -4",
             mat_vec(D, fake) != [-4 * x for x in fake])

    # C7: exact rational vs integer truncation. Every graph above is REGULAR, so
    #     every dual degree has denominator 1 and `Fraction(a, b)` is
    #     indistinguishable from `Fraction(a // b)`. C_7 plus a pendant vertex
    #     has girth 7 and min d* = 5/3, so it is the input that makes the
    #     Fraction in min_dual_degree() load-bearing rather than decorative.
    NR = c7_with_pendant()
    g_nr = girth(NR)
    md_nr, v_nr = min_dual_degree(NR)
    rejected("integer-truncated dual degree on a non-regular girth-7 graph",
             g_nr is not None and g_nr >= 5 and sorted(set(degrees(NR))) == [1, 2, 3]
             and md_nr == Fraction(5, 3) and md_nr.denominator == 3,
             f"girth={g_nr}, degrees={sorted(set(degrees(NR)))}, min d* = {md_nr} at "
             f"vertex {v_nr}; a truncating `//` would report 1 and hide the denominator")
    print()

    # ---- Control accounting: MEASURED, not asserted ------------------------
    controls_run = len(CONTROLS)
    controls_rejected = sum(1 for _, ok in CONTROLS if ok)
    check(f"planted controls: {EXPECTED_CONTROLS} expected, all rejected",
          controls_run == EXPECTED_CONTROLS and controls_rejected == controls_run,
          f"executed={controls_run}, rejected={controls_rejected}")
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
            "lambda_min_derived_ok": rep["lambda_min_derived_ok"],
            "margin": int(margin),
            "refutes_284": rep["refutes_284"],
        },
        # MEASURED, not typed: the number of rejected() calls that actually ran
        # in this process, and how many of them rejected. Deleting a control
        # block changes these numbers, so it drifts the receipt and fails the
        # count check above instead of silently publishing a stale total.
        "controls_run": controls_run,
        "controls_rejected": controls_rejected,
        "controls_expected": EXPECTED_CONTROLS,
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

    # ---- Tamper-evident exit gate -----------------------------------------
    # Do NOT trust FAILURES. It is an append side effect, and a single edit
    # (`FAILURES.append(...)` -> `pass` inside rejected()) would disarm every
    # control at once while the per-control results stayed correct. So the exit
    # verdict is recomputed here from the results recorded at call time, the
    # control count is compared against EXPECTED_CONTROLS, and the two
    # accountings are cross-checked against each other -- a disagreement
    # between them is itself a failure and names the tampering.
    # This raises the cost of a verifier edit. It does not make one impossible;
    # see "What this verifier cannot defend against" in the module docstring.
    failed_checks = [label for label, ok in CHECKS if not ok]
    unrejected = [label for label, ok in CONTROLS if not ok]
    problems = failed_checks + [f"control not rejected: {label}" for label in unrejected]
    if len(CONTROLS) != EXPECTED_CONTROLS:
        problems.append(
            f"planted-control count: {len(CONTROLS)} executed, {EXPECTED_CONTROLS} expected "
            "-- a control block was deleted, duplicated or skipped")
    if len(FAILURES) != len(failed_checks) + len(unrejected):
        problems.append(
            f"failure accumulator disagrees with the recorded results "
            f"(FAILURES={len(FAILURES)}, recorded={len(failed_checks) + len(unrejected)}) "
            "-- the accumulator has been tampered with")
    if problems:
        print(f"FAIL -- {len(problems)} problem(s), recomputed from "
              f"{len(CHECKS)} recorded checks and {len(CONTROLS)} recorded controls:")
        for f in problems:
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
    print(f"PASS -- external refutation independently verified; "
          f"{controls_rejected}/{controls_run} planted controls rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

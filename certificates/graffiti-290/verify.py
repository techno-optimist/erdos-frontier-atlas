#!/usr/bin/env python3
"""Independent, dependency-free replay of the inequality asserted by Graffiti 290.

WHOSE RESULT IS THIS.  The conjecture is Graffiti's (Fajtlowicz), conjecture 290,
"Written on the Wall" p. 79.  The *proof* replayed against here is by Nathan
Wilbanks and Annie (AGNT Labs), "A Proof of Graffiti 290".  Neither the
conjecture nor the proof is ours.  This file is ONLY an independent finite
verification of the inequality they claim, plus an explicit statement of what
that verification does and does not settle.  Nothing here is a discovery of this
repository.

WHICH CONVENTION.  The truth value of Graffiti 290 is convention-dependent.  We
verify it under the "Written on the Wall" / Brewster et al. gravity convention,
which Roucairol-Cazenave (arXiv:2409.18626v1, Sec. 5.2 "Erratum") transcribe from
"Written on the Wall" p. 52 and Brewster-Dinneen-Faber as: the gravity matrix
entry Gr(u,v) is 0 if u = v or if no path joins u to v, and otherwise

        Gr(u,v) = (1/(n-1)) * d(u) * d(v) / d(u,v).

`gravity_matrix` below implements exactly that, and check 1b verifies it entry by
entry against hand-computed connected AND disconnected cases rather than assuming
the transcription was implemented correctly.

The same section reports that under the gravity definition in Aouchiche and
Hansen's survey (Linear Algebra Appl. 432(9):2293-2322, 2010) the conjecture "was
solved instantly" -- i.e. REFUTED -- while refutation was "seemingly impossible"
under the Brewster et al. definition.  Roucairol-Cazenave call the latter "the
correct definition", i.e. the authors who found the refutation identify the survey
definition as the misstatement.  Both halves are load-bearing and neither may be
reported alone: a live refutation exists under the survey definition, AND its own
discoverers disavow that definition.  We do not have the Aouchiche-Hansen
definition and do NOT replay that refutation; this certificate is scoped to the
Written-on-the-Wall / Brewster reading, which is the one the theorem is stated
over.

WHAT IS CHECKED (all exact -- Fraction/integer arithmetic only; no float ever
enters a decision):

  1  the exact-arithmetic engine is calibrated against four graphs with
     closed-form spectra, and mis-stated spectra are rejected;
  1b the gravity matrix is checked ENTRY BY ENTRY against the transcription
     quoted above -- including Gr(u,u) = 0 and Gr(u,v) = 0 when no path joins u
     to v -- on hand-computed connected and disconnected cases;
  2  every graph of girth >= 5 on n <= 10 vertices, up to isomorphism, is
     generated (connected AND disconnected), and the generator is cross-checked
     by orbit counting against an independent labelled-graph enumeration;
  3  on every one of those graphs the inequality is verified in BOTH readings
     (the paper's -lambda_{n-1} <= m/Gr_bar, and the literal Written-on-the-Wall
     lambda_{n-1} <= m/Gr_bar) and under BOTH mean conventions (mean over all
     n^2 entries -- the paper's -- and mean over the n(n-1) off-diagonal ones);
  4  a battery of larger named/constructed graphs of girth >= 5, up to the
     Hoffman-Singleton graph on 50 vertices, is checked the same way, with each
     graph's structure (order, size, girth, regularity) re-derived, not asserted;
  5  the paper's two worked examples are reproduced exactly as rationals;
  6  PLANTED-FAILURE CONTROLS: EXPECTED_CONTROLS (= 19) deliberately corrupted
     inputs, each of which MUST be rejected, printed as `[ok] rejected:` lines.
     The run ASSERTS that exactly that many were rejected and records the number
     in the receipt, so deleting or short-circuiting a control block fails the
     run instead of silently shrinking the battery.

WHAT PINS THE VERDICT.  A verifier whose central check can be stubbed without any
shipped artifact changing is not a verifier.  So `holds_paper` and `holds_literal`
do not return bare booleans: each returns a VERDICT RECORD
(holds, exact_count, m/Gr_bar, spectral_index) and the receipt pins a sha256
VERDICT DIGEST over a canonical, sorted text stream of what those two functions
ACTUALLY RETURNED on every corpus graph under both mean conventions.

The fourth field is there because of a mutant that got through the previous
round.  `mutD` replaced both verdict bodies with `return (True, 0, rhs(...))`:
real m/Gr_bar (rhs() needs no spectral work), fabricated count 0 (the honest
count on every graph of this corpus), no eigenvalue computed anywhere.  It passed
all sixteen controls with a byte-identical transcript and a byte-identical
certificate.json -- and it had no input on which it could answer False, so a real
counterexample would have been reported as a pass.  The digest now includes the
inertia of the adjacency matrix, which varies graph to graph and cannot be
produced without the exact congruence, and check 6f plants mutD itself, a
sharpened mutD with a fabricated inertia index, and a genuinely FAILING instance
on which the verdict path is required to return False.

WHAT THIS FILE CANNOT DEFEND AGAINST.  Every control above is a corrupted INPUT.
None of them, and no control that could be written here, defends against a
corrupted VERIFIER -- someone editing verify.py to stub a function, no-op the
`FAILURES` accumulator, or hardcode a constant in the verdict path.  A program
cannot certify its own source.  What defends that boundary is outside this file:
the sha256 of verify.py and of certificate.json pinned in
certificates/contracts.json, the git history of both, and review.  Said here so a
reader does not have to infer it.

Eigenvalues are never computed numerically.  "How many eigenvalues of A lie below
a rational t" is decided by the inertia of the INTEGER matrix q*A - p*I (where
t = p/q in lowest terms, q > 0) via exact symmetric congruence -- Sylvester's law
of inertia.  Decimal renderings of rationals appear in the printout for reading
only, and in no comparison.

Replay:   python3 -I verify.py
Emit  :   python3 -I verify.py --emit     (rewrites certificate.json; not default)
"""

import hashlib
import json
import sys
from collections import deque
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "certificate.json"

# The order up to which the girth->=5 family is enumerated exhaustively.  This is
# a compute cutoff, not a mathematical one -- see README.
NMAX = 10

# How many planted-failure controls MUST be rejected in a complete run.  This is
# asserted in main() and recorded in the receipt: a deleted or skipped control
# block makes the run fail loudly instead of quietly certifying less.
#   6a: 2   6b: 5   6c: 3   6d: 3   6e: 3   6f: 3
EXPECTED_CONTROLS = 19

FAILURES = []
CONTROLS_PASSED = 0


def bad(msg):
    FAILURES.append(msg)
    print("[FAIL] " + msg)


def ok(msg):
    print("[ok] " + msg)


def rejected(msg):
    global CONTROLS_PASSED
    CONTROLS_PASSED += 1
    print("[ok] rejected: " + msg)


def dec(fr, places=4):
    """Decimal rendering of an exact Fraction -- for the printout only."""
    fr = Fraction(fr)
    sign = "-" if fr < 0 else ""
    fr = abs(fr)
    scaled = (fr.numerator * 10 ** places) // fr.denominator
    s = str(scaled).rjust(places + 1, "0")
    return "%s%s.%s" % (sign, s[:-places], s[-places:])


# ---------------------------------------------------------------------------
# graphs: adjacency as a list of bitmasks
# ---------------------------------------------------------------------------

def validate(n, adj):
    """Reject anything that is not a simple undirected graph on n vertices."""
    if n != len(adj):
        return "order %d does not match adjacency length %d" % (n, len(adj))
    full = (1 << n) - 1
    for v in range(n):
        if adj[v] & ~full:
            return "vertex %d has a neighbour outside 0..%d" % (v, n - 1)
        if (adj[v] >> v) & 1:
            return "vertex %d carries a self-loop" % v
    for u in range(n):
        for v in range(n):
            if ((adj[u] >> v) & 1) != ((adj[v] >> u) & 1):
                return "adjacency is not symmetric at (%d,%d)" % (u, v)
    return None


def mk(n, edges):
    adj = [0] * n
    for a, b in edges:
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    return n, adj


def size(n, adj):
    return sum(bin(a).count("1") for a in adj) // 2


def degrees(n, adj):
    return [bin(adj[v]).count("1") for v in range(n)]


def distances(n, adj):
    """All-pairs BFS distance; -1 means "no path joining u to v"."""
    out = []
    for s in range(n):
        d = [-1] * n
        d[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            m = adj[u]
            while m:
                b = m & -m
                v = b.bit_length() - 1
                m ^= b
                if d[v] < 0:
                    d[v] = d[u] + 1
                    q.append(v)
        out.append(d)
    return out


def girth(n, adj):
    """Exact girth; INF for a forest.  BFS from every vertex."""
    best = None
    for s in range(n):
        d = [-1] * n
        par = [-1] * n
        d[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            m = adj[u]
            while m:
                b = m & -m
                v = b.bit_length() - 1
                m ^= b
                if d[v] < 0:
                    d[v] = d[u] + 1
                    par[v] = u
                    q.append(v)
                elif v != par[u]:
                    c = d[u] + d[v] + 1
                    if best is None or c < best:
                        best = c
    return best  # None == acyclic == girth infinite


def girth_at_least_5(n, adj):
    g = girth(n, adj)
    return g is None or g >= 5


def is_connected(n, adj):
    return all(x >= 0 for x in distances(n, adj)[0])


# ---------------------------------------------------------------------------
# gravity (Written-on-the-Wall / Brewster convention)
# ---------------------------------------------------------------------------

def gravity_matrix(n, adj):
    """Gr(u,v) = 0 if u==v or no u-v path; else d(u)d(v)/((n-1) d(u,v))."""
    if n < 2:
        return None
    d = degrees(n, adj)
    D = distances(n, adj)
    G = [[Fraction(0)] * n for _ in range(n)]
    for u in range(n):
        for v in range(n):
            if u == v or D[u][v] < 0:
                continue
            G[u][v] = Fraction(d[u] * d[v], (n - 1) * D[u][v])
    return G


def mean_gravity(n, adj, over="n2"):
    """`over="n2"`  : mean over all n^2 entries        (the paper's reading)
       `over="offd"`: mean over the n(n-1) off-diagonal entries (alternative)."""
    G = gravity_matrix(n, adj)
    total = sum(sum(row) for row in G)
    return total / (n * n if over == "n2" else n * (n - 1))


# ---------------------------------------------------------------------------
# exact spectral counting -- Sylvester inertia, integer matrices, no floats
# ---------------------------------------------------------------------------

def inertia(mat):
    """(#negative, #zero, #positive) eigenvalues of a symmetric rational matrix,
    with multiplicity, by exact symmetric congruence (Sylvester's law)."""
    M = [[Fraction(x) for x in row] for row in mat]
    k = len(M)
    neg = pos = 0
    while k > 0:
        piv = -1
        for i in range(k):
            if M[i][i] != 0:
                piv = i
                break
        if piv < 0:
            spot = None
            for i in range(k):
                for j in range(k):
                    if i != j and M[i][j] != 0:
                        spot = (i, j)
                        break
                if spot:
                    break
            if spot is None:
                break  # remaining block is the zero matrix
            i, j = spot
            # congruence  M <- E M E^T  with E = I + e_i e_j^T; makes M[i][i]=2*M[i][j]
            for c in range(k):
                M[i][c] += M[j][c]
            for r in range(k):
                M[r][i] += M[r][j]
            continue
        if piv != 0:
            M[0], M[piv] = M[piv], M[0]
            for r in range(k):
                M[r][0], M[r][piv] = M[r][piv], M[r][0]
        p = M[0][0]
        if p < 0:
            neg += 1
        else:
            pos += 1
        M = [[M[i][j] - M[i][0] * M[0][j] / p for j in range(1, k)] for i in range(1, k)]
        k -= 1
    return neg, len(mat) - neg - pos, pos


def _shifted_integer_matrix(n, adj, t):
    """q*(A - t I) as an INTEGER matrix, with q > 0 (inertia is scale-invariant)."""
    t = Fraction(t)
    q, p = t.denominator, t.numerator  # t = p/q, q > 0 by Fraction's normal form
    return [[(q if (adj[i] >> j) & 1 else 0) - (p if i == j else 0) for j in range(n)]
            for i in range(n)]


def count_below(n, adj, t):
    """#{i : lambda_i(A) < t}, with multiplicity.  Exact."""
    return inertia(_shifted_integer_matrix(n, adj, t))[0]


def count_above(n, adj, t):
    """#{i : lambda_i(A) > t}, with multiplicity.  Exact."""
    return inertia(_shifted_integer_matrix(n, adj, t))[2]


def count_equal(n, adj, t):
    """multiplicity of t as an eigenvalue of A.  Exact."""
    return inertia(_shifted_integer_matrix(n, adj, t))[1]


def spectral_index(n, adj):
    """The inertia of the ADJACENCY MATRIX ITSELF: (#eigenvalues < 0, mult of 0).

    This exists for one reason.  Every other field of a verdict record can be
    produced WITHOUT computing an eigenvalue: `rhs` is a gravity/degree/distance
    computation, and on this corpus the honest eigenvalue count is 0 on every
    graph, so a fabricated 0 is indistinguishable from the truth.  A verdict
    function that never touches the spectrum could therefore emit a complete,
    correct-looking record -- and one did: mutant `mutD` (control 6f(i)) replaced
    both verdict bodies with `return (True, 0, rhs(...))` and produced a
    byte-identical transcript AND a byte-identical certificate.json.

    The inertia index is not reachable that way.  It varies graph to graph (on
    the n <= 10 corpus it takes the values 1..5 with multiplicities
    45/140/346/600/229), it is a function of nothing but the spectrum, and the
    only way to produce it is to run the exact congruence.  Putting it in the
    record puts it in the digest, so a spectrum-free stub can no longer
    reproduce the committed receipt.

    It is NOT part of the inequality.  It is the entropy the inequality's own
    verdict does not carry on this corpus, carried alongside it.
    """
    neg, zero, _ = inertia(_shifted_integer_matrix(n, adj, 0))
    return (neg, zero)


def lambda2_bracket(n, adj, eps=Fraction(1, 4096)):
    """Certified rational bracket lo <= lambda_{n-1}(A) <= hi, width <= eps.
    lambda_{n-1} >= t  <=>  at most one eigenvalue lies strictly below t."""
    lo, hi = Fraction(-n), Fraction(n)
    while hi - lo > eps:
        mid = (lo + hi) / 2
        if count_below(n, adj, mid) <= 1:
            lo = mid
        else:
            hi = mid
    return lo, hi


# ---------------------------------------------------------------------------
# the two readings of the conjecture
# ---------------------------------------------------------------------------

def rhs(n, adj, over="n2", gravity=mean_gravity):
    """size / mean gravity, exactly.  None when mean gravity is 0 (edgeless).

    `gravity` is a seam, defaulting to the certified convention.  It exists so a
    control can feed the verdict path a DELIBERATELY WRONG convention and watch
    it answer False -- see check_falsifiability (6f(iii)).  Nothing on the
    default path ever passes it.
    """
    gbar = gravity(n, adj, over)
    if gbar == 0:
        return None
    return Fraction(size(n, adj)) / gbar


VERDICT_SHAPE = ("(holds: bool, exact_count: int >= 0, rhs: Fraction > 0, "
                 "spectrum: (negative_eigenvalues: int >= 0, nullity: int >= 0))")


def holds_paper(n, adj, over="n2", gravity=mean_gravity):
    """The paper's reading: -lambda_{n-1}(A) <= m / Gr_bar.

    Returns a VERDICT RECORD (holds, count, r, spectrum), NOT a bare boolean:

      holds     the answer;
      count     the exact number of adjacency eigenvalues lying strictly below
                -m/Gr_bar -- the quantity the answer is decided on, `holds` being
                exactly `count <= 1`;
      r         the exact m/Gr_bar the answer was decided against;
      spectrum  `spectral_index(n, adj)` -- the inertia of A itself.

    WHY THE FOURTH FIELD.  The first three can all be produced without computing
    an eigenvalue.  `r` is a gravity computation and `rhs()` is callable by
    anyone; and on this corpus the honest `count` is 0 on every single graph
    (the bound is loose by a factor of 5 or more), so a fabricated 0 is exactly
    right.  Mutant `mutD` exploited precisely that: `return (True, 0, rhs(...))`
    passed every control and reproduced the receipt byte for byte.  `spectrum`
    is the field with per-graph entropy that only the exact congruence can
    produce, so the digest now depends on spectral work having been done.

    None when m/Gr_bar is undefined (edgeless graph, mean gravity 0).
    """
    r = rhs(n, adj, over, gravity)
    if r is None:
        return None
    c = count_below(n, adj, -r)
    return (c <= 1, c, r, spectral_index(n, adj))


def holds_literal(n, adj, over="n2", gravity=mean_gravity):
    """The literal Written-on-the-Wall reading: lambda_{n-1}(A) <= m / Gr_bar.

    Returns a VERDICT RECORD (holds, count, r, spectrum) as `holds_paper` does;
    here `count` is the exact number of eigenvalues lying strictly above
    m/Gr_bar.
    """
    r = rhs(n, adj, over, gravity)
    if r is None:
        return None
    c = count_above(n, adj, r)
    return (c <= 1, c, r, spectral_index(n, adj))


def verdict_error(v):
    """None if `v` is a well-formed verdict record, else why it is not.

    This is where a verdict function that has been stubbed out -- `return True`,
    say, or `return (True, 0, rhs(...))` with the spectral field dropped -- is
    caught, BEFORE its non-answer can reach the receipt.  `bool` is a subclass of
    `int`, so the integer fields are explicitly required not to be bools.
    """
    if not (isinstance(v, tuple) and len(v) == 4
            and isinstance(v[0], bool)
            and isinstance(v[1], int) and not isinstance(v[1], bool) and v[1] >= 0
            and isinstance(v[2], Fraction) and v[2] > 0
            and isinstance(v[3], tuple) and len(v[3]) == 2
            and all(isinstance(x, int) and not isinstance(x, bool) and x >= 0
                    for x in v[3])):
        return "expected a verdict record %s, got %r" % (VERDICT_SHAPE, v)
    if v[0] != (v[1] <= 1):
        return ("verdict %r is internally inconsistent: holds=%r but the exact count is %d"
                % (v, v[0], v[1]))
    return None


def graph_key(n, adj):
    """Stable, platform-independent label for a graph: its order and the exact
    adjacency bitmasks, in hex.  This identifies the LABELLED graph, so the
    digest pins which graphs got which verdict, not merely how many.

    It is deliberately not a canonical (isomorphism-invariant) form: canonical
    labelling is brute-force here and would be hopeless on the 50-vertex
    Hoffman-Singleton graph.  Nothing is lost -- every producer of graphs in this
    file (the canonical-augmentation generator, the named constructions, the
    fixed-LCG pseudo-random ones) is fully deterministic, so these labels are
    reproducible run to run and machine to machine.  Should a future edit change
    which representatives the generator emits, the digest changes and the
    committed receipt stops matching: visibly, which is the point.
    """
    return "%d:%s" % (n, ",".join("%x" % a for a in adj))


def verdict_stream(items, fp=None, fl=None):
    """The canonical text stream of the verdicts ACTUALLY RETURNED by the two
    verdict functions on `items` (a list of (n, adj) with at least one edge).

    One line per (graph, mean convention), carrying the boolean, the exact
    eigenvalue count behind it, the exact m/Gr_bar it was decided against, and
    the inertia of the adjacency matrix -- the last being the field that cannot
    be produced without running the exact congruence.  Lines are sorted before
    hashing, so the digest is a function of the multiset of verdicts and not of
    enumeration order.

    Returns a dict:
      error    None, or why a verdict function failed to answer properly
      digest   sha256 of the stream
      pairs    sorted multiset of the exact (count_below, count_above) pairs
               under the paper's n^2 mean, as [count_below, count_above, times]
      records  number of verdict lines hashed
      refuted  (n, adj, over, which) for every graph whose verdict was False
      detail   per (graph, convention): {"n", "over", "paper", "literal"}, so a
               caller can report the exact counts without asking again
    """
    fp = holds_paper if fp is None else fp
    fl = holds_literal if fl is None else fl
    lines = []
    detail = []
    pairs = {}
    refuted = []
    for n, adj in items:
        key = graph_key(n, adj)
        for over in ("n2", "offd"):
            vp = fp(n, adj, over)
            vl = fl(n, adj, over)
            for which, v in (("holds_paper", vp), ("holds_literal", vl)):
                err = verdict_error(v)
                if err is not None:
                    return {"error": "%s(n=%d, over=%s): %s" % (which, n, over, err)}
                if not v[0]:
                    refuted.append((n, tuple(adj), over, which))
            if vp[2] != vl[2]:
                return {"error": "n=%d over=%s: the two readings were decided against "
                                 "different values of m/Gr_bar, %s and %s"
                                 % (n, over, vp[2], vl[2])}
            if vp[3] != vl[3]:
                return {"error": "n=%d over=%s: the two readings report different spectra "
                                 "for the same graph, %r and %r -- at most one of them "
                                 "computed it" % (n, over, vp[3], vl[3])}
            # Every graph in this stream has at least one edge, and a graph with
            # an edge has a negative adjacency eigenvalue (trace 0, not the zero
            # matrix).  So a reported inertia index of 0 is not a near miss, it
            # is proof that no congruence was run.
            if vp[3][0] < 1:
                return {"error": "n=%d over=%s: reported inertia index %d on a graph with "
                                 "%d edges -- a graph with an edge has a negative "
                                 "eigenvalue, so no spectrum was computed"
                                 % (n, over, vp[3][0], size(n, adj))}
            lines.append("%s over=%s rhs=%s spec=%d,%d paper=%s,%d literal=%s,%d"
                         % (key, over, vp[2], vp[3][0], vp[3][1],
                            "T" if vp[0] else "F", vp[1],
                            "T" if vl[0] else "F", vl[1]))
            detail.append({"n": n, "adj": adj, "over": over, "paper": vp, "literal": vl})
            if over == "n2":
                pairs[(vp[1], vl[1])] = pairs.get((vp[1], vl[1]), 0) + 1
    stream = "\n".join(sorted(lines)) + "\n"
    return {
        "error": None,
        "digest": hashlib.sha256(stream.encode("ascii")).hexdigest(),
        "pairs": [[cb, ca, k] for (cb, ca), k in sorted(pairs.items())],
        "records": len(lines),
        "refuted": refuted,
        "detail": detail,
    }


# ---------------------------------------------------------------------------
# generation of every girth->=5 graph up to isomorphism
# ---------------------------------------------------------------------------

def canonical(n, adj):
    """Canonical form: the lexicographically greatest column-wise adjacency
    string over all vertex orderings, found by branch-and-bound."""
    best = [None]
    perm = []
    used = [0]

    def rec(prefix):
        if len(perm) == n:
            if best[0] is None or prefix > best[0]:
                best[0] = prefix
            return
        scored = []
        for v in range(n):
            if (used[0] >> v) & 1:
                continue
            s = 0
            for u in perm:
                s = (s << 1) | ((adj[u] >> v) & 1)
            scored.append((s, v))
        scored.sort(reverse=True)
        top = scored[0][0]
        for s, v in scored:
            if s != top:
                break
            new = prefix + tuple((adj[u] >> v) & 1 for u in perm)
            if best[0] is not None and best[0][:len(new)] > new:
                continue
            perm.append(v)
            used[0] |= 1 << v
            rec(new)
            used[0] &= ~(1 << v)
            perm.pop()

    rec(())
    return best[0]


def _extensions(n, adj, enforce_girth=True):
    """Neighbourhoods S for a new vertex that keep girth >= 5: S independent and
    no two members of S share a neighbour."""
    out = []

    def rec(start, S, chosen):
        out.append(S)
        for v in range(start, n):
            if enforce_girth:
                blocked = False
                for u in chosen:
                    if (adj[u] >> v) & 1 or (adj[u] & adj[v]):
                        blocked = True
                        break
                if blocked:
                    continue
            rec(v + 1, S | (1 << v), chosen + [v])

    rec(0, 0, [])
    return out


def generate(nmax, enforce_girth=True):
    """All girth->=5 graphs on 1..nmax vertices, up to isomorphism, by canonical
    augmentation.  Includes disconnected graphs."""
    levels = {1: [[0]]}
    for n in range(2, nmax + 1):
        seen = {}
        for adj in levels[n - 1]:
            for S in _extensions(n - 1, adj, enforce_girth):
                new = list(adj) + [S]
                for v in range(n - 1):
                    if (S >> v) & 1:
                        new[v] |= 1 << (n - 1)
                c = canonical(n, new)
                if c not in seen:
                    seen[c] = new
        levels[n] = list(seen.values())
    return levels


def labelled_count(n):
    """Independent count of LABELLED graphs of girth >= 5 on n vertices, by DFS
    over the C(n,2) edge slots.  Shares no code with `generate`."""
    slots = [(i, j) for i in range(n) for j in range(i + 1, n)]
    total = 0

    def rec(k, adj):
        nonlocal total
        if k == len(slots):
            total += 1
            return
        rec(k + 1, adj)  # slot omitted
        i, j = slots[k]
        if (adj[i] & adj[j]) == 0 and not (adj[i] >> j) & 1:
            nxt = list(adj)
            nxt[i] |= 1 << j
            nxt[j] |= 1 << i
            if girth_at_least_5(n, nxt):
                rec(k + 1, nxt)

    rec(0, [0] * n)
    return total


def automorphism_count(n, adj):
    """|Aut(G)| by brute force over all n! vertex permutations."""
    c = 0
    for p in permutations(range(n)):
        good = True
        for u in range(n):
            for v in range(u + 1, n):
                if ((adj[u] >> v) & 1) != ((adj[p[u]] >> p[v]) & 1):
                    good = False
                    break
            if not good:
                break
        if good:
            c += 1
    return c


def factorial(k):
    f = 1
    for i in range(2, k + 1):
        f *= i
    return f


# ---------------------------------------------------------------------------
# named / constructed graphs
# ---------------------------------------------------------------------------

def petersen():
    """Kneser graph K(5,2): the 2-subsets of {0..4}, adjacent iff disjoint."""
    S = list(combinations(range(5), 2))
    idx = {s: i for i, s in enumerate(S)}
    E = [(idx[a], idx[b]) for a, b in combinations(S, 2) if not set(a) & set(b)]
    return mk(len(S), E)


def hoffman_singleton():
    """Standard pentagon/pentagram construction: P_h vertex j joined to Q_i
    vertex (h*i + j) mod 5."""
    idx = {}
    for t in ("P", "Q"):
        for h in range(5):
            for j in range(5):
                idx[(t, h, j)] = len(idx)
    E = set()
    for h in range(5):
        for j in range(5):
            E.add(tuple(sorted((idx[("P", h, j)], idx[("P", h, (j + 1) % 5)]))))
            E.add(tuple(sorted((idx[("Q", h, j)], idx[("Q", h, (j + 2) % 5)]))))
    for h in range(5):
        for i in range(5):
            for j in range(5):
                E.add(tuple(sorted((idx[("P", h, j)], idx[("Q", i, (h * i + j) % 5)]))))
    return mk(50, sorted(E))


def heawood():
    """Incidence graph of the Fano plane: lines {i, i+1, i+3} mod 7."""
    return mk(14, [(i, 7 + ((i + d) % 7)) for i in range(7) for d in (0, 1, 3)])


def pg23_incidence():
    """Incidence graph of PG(2,3) from the perfect difference set {0,1,3,9} mod 13."""
    return mk(26, [(i, 13 + ((i + d) % 13)) for i in range(13) for d in (0, 1, 3, 9)])


def odd_graph_4():
    """Kneser graph K(7,3), the odd graph O_4."""
    S = list(combinations(range(7), 3))
    idx = {s: i for i, s in enumerate(S)}
    E = [(idx[a], idx[b]) for a, b in combinations(S, 2) if not set(a) & set(b)]
    return mk(len(S), E)


def cycle(k):
    return mk(k, [(i, (i + 1) % k) for i in range(k)])


def complete_bipartite(a, b):
    return mk(a + b, [(i, a + j) for i in range(a) for j in range(b)])


def cube_q3():
    return mk(8, [(u, u ^ (1 << b)) for u in range(8) for b in range(3) if u < (u ^ (1 << b))])


def deterministic_girth5(n, seed):
    """A reproducible pseudo-random maximal girth->=5 graph.  The generator is a
    fixed integer LCG so the graph is a deterministic function of (n, seed) --
    no dependence on `random`, hashing, or platform."""
    slots = [(i, j) for i in range(n) for j in range(i + 1, n)]
    state = (seed * 6364136223846793005 + 1442695040888963407) % (1 << 64)
    order = []
    pool = list(slots)
    while pool:
        state = (state * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        order.append(pool.pop((state >> 33) % len(pool)))
    adj = [0] * n
    for i, j in order:
        if (adj[i] >> j) & 1:
            continue
        if adj[i] & adj[j]:
            continue
        blocked = False
        m = adj[i]
        while m:
            b = m & -m
            u = b.bit_length() - 1
            m ^= b
            if adj[u] & adj[j]:
                blocked = True
                break
        if blocked:
            continue
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    return n, adj


def battery():
    out = [
        ("Petersen = Kneser K(5,2)", petersen()),
        ("Heawood = Fano incidence", heawood()),
        ("PG(2,3) incidence", pg23_incidence()),
        ("Odd graph O_4 = Kneser K(7,3)", odd_graph_4()),
        ("Hoffman-Singleton", hoffman_singleton()),
    ]
    for k in (5, 7, 11, 13, 17, 23, 31, 40):
        out.append(("cycle C_%d" % k, cycle(k)))
    for n in (16, 25, 33, 40):
        for s in (1, 2):
            out.append(("pseudo-random girth-5 n=%d seed=%d" % (n, s), deterministic_girth5(n, s)))
    return out


# ---------------------------------------------------------------------------
# check 1 -- calibrate the exact spectral engine
# ---------------------------------------------------------------------------

def check_engine():
    print("\n== 1. exact spectral engine, calibrated against closed-form spectra ==")
    # K_2: spectrum {-1, 1}
    n, adj = mk(2, [(0, 1)])
    cases = [
        ("K_2", (n, adj), {-1: 1, 1: 1}),
        ("C_5", cycle(5), None),
        ("Petersen", petersen(), {3: 1, 1: 5, -2: 4}),
        ("Hoffman-Singleton", hoffman_singleton(), {7: 1, 2: 28, -3: 21}),
    ]
    for name, (n, adj), spec in cases:
        if spec is None:
            continue
        recovered = {}
        for lam in sorted(spec, reverse=True):
            recovered[lam] = count_equal(n, adj, Fraction(lam))
        if recovered != spec:
            bad("spectrum of %s came out as %s, expected %s" % (name, recovered, spec))
        elif sum(recovered.values()) != n:
            bad("multiplicities of %s sum to %d, not %d" % (name, sum(recovered.values()), n))
        else:
            ok("%s spectrum recovered exactly: %s" %
               (name, " ".join("%d^%d" % (k, v) for k, v in sorted(spec.items(), reverse=True))))
    # C_5: eigenvalues 2, (sqrt5-1)/2 twice, -(sqrt5+1)/2 twice.  The second
    # smallest is irrational, so it is certified by an exact rational bracket
    # whose endpoints straddle the root of x^2 + x - 1 -- no decimal is compared.
    n, adj = cycle(5)
    lo, hi = lambda2_bracket(n, adj, Fraction(1, 1 << 20))
    f = lambda x: x * x + x - 1
    if not (f(lo) > 0 > f(hi)):
        bad("C_5 bracket [%s,%s] does not straddle the root of x^2+x-1" % (lo, hi))
    else:
        ok("C_5 lambda_{n-1} bracketed to width 2^-20; endpoints straddle the root of "
           "x^2+x-1, i.e. -(1+sqrt5)/2 ~ %s" % dec(lo, 6))
    return True


def check_engine_controls():
    print("\n== 6a. controls on the spectral engine ==")
    n, adj = petersen()
    # Petersen really has 4 eigenvalues below -1.9.
    c = count_below(n, adj, Fraction(-19, 10))
    if c <= 1:
        bad("planted false spectral claim about Petersen was NOT caught (count=%d)" % c)
    else:
        rejected("planted claim 'Petersen has at most one eigenvalue < -19/10' "
                 "-- the exact counter finds %d" % c)
    # A mis-stated Hoffman-Singleton multiplicity must not validate.
    n, adj = hoffman_singleton()
    mult = count_equal(n, adj, Fraction(-3))
    if mult == 22:
        bad("planted false multiplicity for Hoffman-Singleton eigenvalue -3 was accepted")
    else:
        rejected("planted claim 'Hoffman-Singleton has (-3)^22' -- exact multiplicity is %d" % mult)


# ---------------------------------------------------------------------------
# check 1b -- the gravity matrix, against the transcribed definition
# ---------------------------------------------------------------------------

def check_gravity_convention():
    """Check `gravity_matrix` ENTRY BY ENTRY against the definition as
    transcribed in Roucairol-Cazenave arXiv:2409.18626v1 Sec. 5.2 from "Written
    on the Wall" p. 52 and Brewster-Dinneen-Faber:

        Gr(u,v) = 0                               if u = v, or no u-v path
        Gr(u,v) = (1/(n-1)) * d(u) * d(v) / d(u,v)  otherwise

    The expected entries below are computed by hand from that formula, not by
    calling the implementation, so this check tests the transcription rather than
    assuming it.  The disconnected case is included deliberately: the
    zero-for-no-path clause is exactly the clause a connected-only reading would
    quietly drop.
    """
    print("\n== 1b. gravity matrix vs the transcribed Written-on-the-Wall / Brewster definition ==")
    F = Fraction
    cases = [
        # P_3 = 0-1-2.  n=3, degrees (1,2,1), d(0,2)=2.
        # Gr(0,1) = (1/2)(1*2)/1 = 1 ; Gr(0,2) = (1/2)(1*1)/2 = 1/4 ; Gr(1,2) = 1
        ("path P_3", mk(3, [(0, 1), (1, 2)]),
         [[F(0), F(1), F(1, 4)],
          [F(1), F(0), F(1)],
          [F(1, 4), F(1), F(0)]]),
        # K_2 + isolated vertex.  n=3, degrees (1,1,0); vertex 2 joins nothing,
        # so its whole row and column are 0 by the no-path clause.
        # Gr(0,1) = (1/2)(1*1)/1 = 1/2
        ("K_2 disjoint union K_1 (DISCONNECTED)", mk(3, [(0, 1)]),
         [[F(0), F(1, 2), F(0)],
          [F(1, 2), F(0), F(0)],
          [F(0), F(0), F(0)]]),
        # two disjoint edges.  n=4, all degrees 1; only the two matched pairs
        # have a path.  Gr = (1/3)(1*1)/1 = 1/3 on those.
        ("2 K_2 (DISCONNECTED)", mk(4, [(0, 1), (2, 3)]),
         [[F(0), F(1, 3), F(0), F(0)],
          [F(1, 3), F(0), F(0), F(0)],
          [F(0), F(0), F(0), F(1, 3)],
          [F(0), F(0), F(1, 3), F(0)]]),
    ]
    for name, (n, adj), want in cases:
        got = gravity_matrix(n, adj)
        if got != want:
            bad("gravity matrix of %s is %s, but the transcribed definition gives %s"
                % (name, got, want))
            continue
        if any(got[u][u] != 0 for u in range(n)):
            bad("gravity matrix of %s has a nonzero diagonal" % name)
            continue
        D = distances(n, adj)
        stray = [(u, v) for u in range(n) for v in range(n) if D[u][v] < 0 and got[u][v] != 0]
        if stray:
            bad("gravity matrix of %s is nonzero at no-path pairs %s" % (name, stray))
            continue
        ok("%s: every entry matches the hand-computed definition (diagonal 0; "
           "no-path pairs 0)" % name)
    # the 1/(n-1) factor is not decorative: it must scale with the order
    n, adj = petersen()
    G = gravity_matrix(n, adj)
    want01 = Fraction(3 * 3, (10 - 1) * distances(n, adj)[0][1])
    if G[0][1] != want01:
        bad("Petersen Gr(0,1) is %s, expected d(0)d(1)/((n-1)d(0,1)) = %s" % (G[0][1], want01))
    else:
        ok("Petersen Gr(0,1) = %s = 3*3/(9*%d), so the 1/(n-1) factor is present and exact"
           % (want01, distances(n, adj)[0][1]))


# ---------------------------------------------------------------------------
# check 2 -- the girth->=5 family, generated and cross-checked
# ---------------------------------------------------------------------------

def check_family(levels):
    print("\n== 2. the girth->=5 family up to n = %d, generated and cross-checked ==" % NMAX)
    counts = {n: len(levels[n]) for n in range(1, NMAX + 1)}
    print("     classes up to isomorphism, n = 1..%d:  %s" %
          (NMAX, ", ".join(str(counts[n]) for n in range(1, NMAX + 1))))
    for n in range(1, NMAX + 1):
        for adj in levels[n]:
            err = validate(n, adj)
            if err:
                bad("generated graph on %d vertices is malformed: %s" % (n, err))
                return counts
            if not girth_at_least_5(n, adj):
                bad("generated graph on %d vertices has girth %s" % (n, girth(n, adj)))
                return counts
    ok("every generated graph re-validated: simple, symmetric, loop-free, girth >= 5")

    # Orbit counting: sum over isomorphism classes of n!/|Aut| must equal the
    # labelled count produced by a completely separate DFS enumeration.
    xmax = 7
    before = len(FAILURES)
    for n in range(1, xmax + 1):
        orbit = sum(Fraction(factorial(n), automorphism_count(n, adj)) for adj in levels[n])
        direct = labelled_count(n)
        if orbit != direct:
            bad("orbit count %s != independent labelled count %d at n=%d" % (orbit, direct, n))
        elif orbit.denominator != 1:
            bad("orbit count at n=%d is not an integer: %s" % (n, orbit))
    if len(FAILURES) == before:
        ok("orbit counting agrees with an independent labelled enumeration for n <= %d "
           "(so the generator neither misses nor duplicates a class)" % xmax)
    return counts


def check_family_controls(levels):
    print("\n== 6b. control on the girth filter ==")
    for name, (n, adj) in (("C_4", cycle(4)), ("K_{3,3}", complete_bipartite(3, 3)),
                           ("3-cube Q_3", cube_q3()), ("K_4", mk(4, list(combinations(range(4), 2))))):
        g = girth(n, adj)
        if girth_at_least_5(n, adj):
            bad("girth filter accepted %s, which has girth %s" % (name, g))
        else:
            rejected("%s offered as a girth->=5 instance -- measured girth is %d" % (name, g))
    # Turning the girth filter off must visibly change the enumeration.
    loose = generate(6, enforce_girth=False)
    tight = {n: len(levels[n]) for n in range(1, 7)}
    got = {n: len(loose[n]) for n in range(1, 7)}
    if got == tight:
        bad("disabling the girth filter did not change the enumeration -- the filter is inert")
    else:
        rejected("enumeration with the girth filter disabled: %s vs the certified %s" %
                 (", ".join(str(got[n]) for n in range(1, 7)),
                  ", ".join(str(tight[n]) for n in range(1, 7))))


# ---------------------------------------------------------------------------
# check 3 -- the inequality on the whole family
# ---------------------------------------------------------------------------

def check_inequality(levels):
    print("\n== 3. the inequality on every girth->=5 graph, n <= %d ==" % NMAX)
    items = []
    edgeless = 0
    disconnected = 0
    tight_ratio = None
    tight_margin = None
    for n in range(2, NMAX + 1):
        for adj in levels[n]:
            if size(n, adj) == 0:
                edgeless += 1
                continue
            items.append((n, adj))
            if not is_connected(n, adj):
                disconnected += 1
    checked = len(items)

    # THE ONLY PLACE THE VERDICT IS DECIDED.  Everything the receipt says about
    # the corpus verdicts comes out of this call, so no shipped artifact can be
    # independent of what holds_paper / holds_literal returned.
    vs = verdict_stream(items)
    if vs["error"] is not None:
        bad("the verdict path did not answer: %s" % vs["error"])
        return None
    if vs["refuted"]:
        n, adj, over, which = vs["refuted"][0]
        bad("%s fails, over=%s, n=%d, adj=%s (%d refutation(s) in all)"
            % (which, over, n, list(adj), len(vs["refuted"])))
        return None

    # Tightness is measured against the SAME m/Gr_bar the verdicts were decided
    # on -- taken out of the verdict records, not recomputed beside them.  The
    # earlier version called rhs() again here, which is how the receipt ended up
    # independent of the verdict path in the first place.
    for d in vs["detail"]:
        if d["over"] != "n2":
            continue
        n, adj, r = d["n"], d["adj"], d["paper"][2]
        lo, hi = lambda2_bracket(n, adj)
        lhs_ub = -lo              # certified upper bound on -lambda_{n-1}
        if lhs_ub <= 0:
            continue              # -lambda_{n-1} <= 0 <= m/Gr_bar: nothing to be tight about
        ratio = r / lhs_ub
        if tight_ratio is None or ratio < tight_ratio[0]:
            tight_ratio = (ratio, n, tuple(adj), r, lhs_ub)
        margin = r - lhs_ub
        if tight_margin is None or margin < tight_margin[0]:
            tight_margin = (margin, n, tuple(adj), r, lhs_ub)
    ok("%d graphs checked (%d of them disconnected); %d edgeless graphs excluded, "
       "mean gravity being 0 there" % (checked, disconnected, edgeless))
    ok("both readings hold, under both the n^2 and the n(n-1) mean convention, on all of them")
    ok("connectivity is NOT needed in this range: the %d disconnected instances hold too"
       % disconnected)
    ok("verdict digest over the %d verdict records actually returned: %s"
       % (vs["records"], vs["digest"]))
    print("     exact (count_below, count_above) pairs, with multiplicity: %s"
          % ", ".join("(%d,%d)x%d" % (a, b, k) for a, b, k in vs["pairs"]))
    # lambda2_bracket returns lo <= lambda_{n-1}, so -lo is an UPPER bound on the
    # left-hand side; both figures below are therefore certified LOWER bounds on
    # the true tightness, restricted to instances where -lambda_{n-1} > 0.
    print("     tightest ratio  m/Gr_bar : -lambda_{n-1}  >= %s  (~%s) at n=%d"
          % (tight_ratio[0], dec(tight_ratio[0]), tight_ratio[1]))
    print("     smallest margin m/Gr_bar - (-lambda_{n-1}) >= %s (~%s) at n=%d"
          % (tight_margin[0], dec(tight_margin[0]), tight_margin[1]))
    print("     so the bound is nowhere tight in this range -- it is loose by a factor of 5 or more")
    return {
        "graphs_checked": checked,
        "disconnected_checked": disconnected,
        "edgeless_excluded": edgeless,
        "tightest_ratio_lower_bound": str(tight_ratio[0]),
        "tightest_ratio_order": tight_ratio[1],
        "smallest_margin_lower_bound": str(tight_margin[0]),
        "smallest_margin_order": tight_margin[1],
        # Verdict-derived, and derived from NOTHING ELSE: these two fields are
        # functions of what holds_paper / holds_literal returned.  Stub either
        # and the committed receipt stops matching.
        "verdict_digest_sha256": vs["digest"],
        "verdict_records": vs["records"],
        "verdict_count_pairs": vs["pairs"],
    }


# ---------------------------------------------------------------------------
# check 3b -- is the girth hypothesis visibly necessary?
# ---------------------------------------------------------------------------

def check_girth_necessity(nmax=6):
    """Sweep ALL labelled graphs on n <= nmax with girth < 5 and count how many
    violate the inequality.  This is a disclosure, not a certification: finding
    none is a fact about this range, not evidence the hypothesis can be dropped.

    HOW THE TWO READINGS ARE CONSULTED, AND HOW THEY ARE NOT.  This sweep used to
    end in `if not (vp[0] and vl[0]): violations += 1`.  Because the sweep finds
    zero violations, that conjunction is inert: mutating it to `vp[0] and vp[0]`
    -- deleting the literal reading from the test outright -- left the transcript
    and certificate.json byte-identical (mutant `mutK`).  A violation counter on
    a corpus with no violations carries no entropy, and no amount of rephrasing
    the boolean changes that.

    So the counters are now kept SEPARATELY per reading (no compound boolean is
    left to make inert), and -- this is the part that actually bites -- the sweep
    ships a DIGEST over both readings' returned records, including the inertia
    index.  Dropping, stubbing, or short-circuiting either reading moves that
    digest and the committed receipt stops matching.  The counters are reported
    because a reader wants the number; the digest is what makes them load-bearing.
    """
    print("\n== 3b. is the girth >= 5 hypothesis visibly necessary in this range? ==")
    swept = 0
    violations_paper = 0
    violations_literal = 0
    lines = []
    for n in range(3, nmax + 1):
        slots = [(i, j) for i in range(n) for j in range(i + 1, n)]
        for mask in range(1 << len(slots)):
            adj = [0] * n
            for k, (i, j) in enumerate(slots):
                if (mask >> k) & 1:
                    adj[i] |= 1 << j
                    adj[j] |= 1 << i
            if girth_at_least_5(n, adj):
                continue
            # Routed through the verdict functions, not around them: this sweep
            # used to call count_below/count_above directly, which made it one
            # more place where the shipped numbers did not depend on the verdict
            # path at all.
            vp = holds_paper(n, adj, "n2")
            if vp is None:
                continue
            vl = holds_literal(n, adj, "n2")
            for which, v in (("holds_paper", vp), ("holds_literal", vl)):
                err = verdict_error(v)
                if err is not None:
                    bad("the verdict path did not answer in the girth<5 sweep: %s: %s"
                        % (which, err))
                    return None
            if vp[3] != vl[3]:
                bad("the two readings reported different spectra for the same girth<5 "
                    "graph, %r and %r" % (vp[3], vl[3]))
                return None
            swept += 1
            # Counted separately: no compound boolean is left for a mutation to
            # make inert.  Both counters are 0 across this range, so neither
            # carries entropy -- the digest below is what consults the readings.
            if not vp[0]:
                violations_paper += 1
            if not vl[0]:
                violations_literal += 1
            lines.append("%s paper=%s,%d literal=%s,%d rhs=%s spec=%d,%d"
                         % (graph_key(n, adj), "T" if vp[0] else "F", vp[1],
                            "T" if vl[0] else "F", vl[1], vp[2], vp[3][0], vp[3][1]))
    digest = hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode("ascii")).hexdigest()
    print("     %d labelled graphs of girth < 5 on n <= %d swept; %d violate the paper's "
          "reading, %d the literal one" % (swept, nmax, violations_paper, violations_literal))
    print("     sweep digest over both readings' returned records: %s" % digest)
    ok("no girth < 5 counterexample in this range -- so the hypothesis is not visibly "
       "necessary HERE. That is a fact about the range, not a theorem, and not a reason "
       "to drop it: the paper's proof uses girth >= 5 essentially.")
    return {"girth_lt5_labelled_swept": swept,
            "girth_lt5_violations_paper": violations_paper,
            "girth_lt5_violations_literal": violations_literal,
            "girth_lt5_sweep_digest_sha256": digest,
            "girth_lt5_sweep_up_to_order": nmax}


# ---------------------------------------------------------------------------
# check 4 -- the larger battery
# ---------------------------------------------------------------------------

def check_battery():
    print("\n== 4. larger named and constructed graphs ==")
    rows = []
    for name, (n, adj) in battery():
        err = validate(n, adj)
        if err:
            bad("%s is malformed: %s" % (name, err))
            continue
        if not girth_at_least_5(n, adj):
            bad("%s has girth %s, so it does not belong in this battery" % (name, girth(n, adj)))
            continue
        m = size(n, adj)
        g = girth(n, adj)
        degs = sorted(set(degrees(n, adj)))
        vs = verdict_stream([(n, adj)])
        if vs["error"] is not None:
            bad("%s: the verdict path did not answer: %s" % (name, vs["error"]))
            continue
        if vs["refuted"]:
            bad("%s violates the inequality: %s" % (name, vs["refuted"]))
            continue
        n2 = [d for d in vs["detail"] if d["over"] == "n2"][0]
        r = n2["paper"][2]        # the m/Gr_bar the verdict was actually decided on
        lo, hi = lambda2_bracket(n, adj)
        print("     %-38s n=%-3d m=%-4d girth=%-3s deg=%-14s  -lam_{n-1} <= %-9s <= %s = m/Gr_bar"
              % (name, n, m, g, degs, dec(-lo, 3), dec(r, 3)))
        # The two counts below come straight out of the verdict records, so each
        # battery row in the receipt is itself verdict-derived.
        rows.append({"name": name, "n": n, "m": m, "girth": g,
                     "rhs": str(r), "lhs_upper_bound": str(-lo),
                     "count_below_minus_rhs": n2["paper"][1],
                     "count_above_rhs": n2["literal"][1],
                     # The spectral field of the verdict record: the inertia of
                     # A, which no gravity computation can produce.
                     "adjacency_inertia_neg_zero": list(n2["paper"][3]),
                     "verdict_digest_sha256": vs["digest"]})
    ok("%d larger instances, up to n = 50, satisfy both readings under both mean conventions"
       % len(rows))
    return rows


def check_battery_controls():
    print("\n== 6c. controls on the battery constructions ==")
    n, adj = hoffman_singleton()
    v = (adj[0] & -adj[0]).bit_length() - 1
    broken = list(adj)
    broken[0] &= ~(1 << v)
    broken[v] &= ~(1 << 0)
    degs = sorted(set(degrees(n, broken)))
    if degs == [7]:
        bad("deleting an edge from Hoffman-Singleton left it 7-regular -- the structure check is inert")
    else:
        rejected("Hoffman-Singleton with edge (0,%d) deleted -- degree set is %s, not [7]" % (v, degs))
    # add an edge: girth must drop below 5
    aug = list(adj)
    u, w = None, None
    for a in range(n):
        for b in range(a + 1, n):
            if not (adj[a] >> b) & 1 and (adj[a] & adj[b]):
                u, w = a, b
                break
        if u is not None:
            break
    aug[u] |= 1 << w
    aug[w] |= 1 << u
    g = girth(n, aug)
    if girth_at_least_5(n, aug):
        bad("adding edge (%d,%d) to Hoffman-Singleton left girth >= 5 -- impossible" % (u, w))
    else:
        rejected("Hoffman-Singleton plus edge (%d,%d) -- girth drops to %d" % (u, w, g))
    # malformed input
    err = validate(3, [0b010, 0b000, 0b000])
    if err is None:
        bad("an asymmetric adjacency list was accepted as a graph")
    else:
        rejected("asymmetric adjacency list -- %s" % err)


# ---------------------------------------------------------------------------
# check 5 -- the paper's own worked examples
# ---------------------------------------------------------------------------

def check_worked_examples():
    print("\n== 5. the paper's two worked examples, reproduced as exact rationals ==")
    out = {}
    for name, (n, adj), lam2, want_rhs in (
        ("Petersen", petersen(), Fraction(-2), Fraction(25)),
        ("Hoffman-Singleton", hoffman_singleton(), Fraction(-3), Fraction(625, 2)),
    ):
        r = rhs(n, adj, "n2")
        mult_below = count_below(n, adj, lam2)
        mult_at = count_equal(n, adj, lam2)
        if r != want_rhs:
            bad("%s: m/Gr_bar came out %s, expected %s" % (name, r, want_rhs))
            continue
        if mult_below != 0 or mult_at < 2:
            bad("%s: lambda_{n-1} is not %s (below=%d, at=%d)" % (name, lam2, mult_below, mult_at))
            continue
        margin = r - (-lam2)
        ok("%s: -lambda_{n-1} = %s <= %s = m/Gr_bar, margin %s (~%s), loose by a factor ~%s"
           % (name, -lam2, r, margin, dec(margin, 1), dec(r / (-lam2), 2)))
        out[name] = {"lhs": str(-lam2), "rhs": str(r), "margin": str(margin)}
    return out


# ---------------------------------------------------------------------------
# check 6d -- the convention control
# ---------------------------------------------------------------------------

def mutated_mean_gravity(n, adj):
    """A DELIBERATELY WRONG convention, ours, planted so that the checker has
    something it must reject: gravity averaged over EDGES only and with the
    1/(n-1) factor dropped.  This is NOT Aouchiche and Hansen's definition --
    we do not have that definition and make no claim about it."""
    d = degrees(n, adj)
    total = Fraction(0)
    m = 0
    for u in range(n):
        for v in range(u + 1, n):
            if (adj[u] >> v) & 1:
                total += d[u] * d[v]
                m += 1
    return total / m


def check_convention_controls():
    print("\n== 6d. controls on the gravity convention ==")
    n, adj = petersen()
    r_true = rhs(n, adj, "n2")
    r_mut = Fraction(size(n, adj)) / mutated_mean_gravity(n, adj)
    if count_below(n, adj, -r_mut) <= 1:
        bad("the mutated gravity convention still satisfied the inequality on Petersen")
    else:
        rejected("mutated convention (edge-mean, 1/(n-1) dropped) on Petersen: "
                 "m/Gr_bar = %s (~%s) < 2 = -lambda_{n-1}; certified convention gives %s"
                 % (r_mut, dec(r_mut), r_true))
    # inflating mean gravity by a factor of 20 must break the certified instance
    r_scaled = r_true / 20
    if count_below(n, adj, -r_scaled) <= 1:
        bad("inflating mean gravity 20x on Petersen did not break the inequality")
    else:
        rejected("mean gravity inflated 20x on Petersen: m/Gr_bar = %s < 2" % r_scaled)
    # the flipped inequality must fail.  The baseline goes through holds_paper
    # rather than around it, so this block cannot pass while the verdict path is
    # broken.
    base = holds_paper(n, adj, "n2")
    base_err = verdict_error(base)
    if base_err is not None:
        bad("the verdict path did not answer on Petersen: %s" % base_err)
    elif not base[0]:
        bad("Petersen unexpectedly violates the certified inequality (count_below = %d)"
            % base[1])
    else:
        flipped_holds = r_true <= 2
        if flipped_holds:
            bad("the flipped inequality m/Gr_bar <= -lambda_{n-1} was satisfied on Petersen")
        else:
            rejected("flipped inequality m/Gr_bar <= -lambda_{n-1} on Petersen: %s <= 2 is false"
                     % r_true)


# ---------------------------------------------------------------------------
# check 6e -- controls on the verdict path itself
# ---------------------------------------------------------------------------

def _stubbed_holds_paper(n, adj, over="n2"):
    """A DELIBERATELY STUBBED verdict function: it answers "the inequality holds"
    without ever looking at the graph.  This is the exact mutation that a
    verifier must not survive -- and, before this control existed, this one did:
    replacing the body of `holds_paper` with `return True` left the transcript
    and certificate.json byte-identical.  Planted here so the property is
    demonstrated on every run instead of assumed."""
    return True


def _fabricated_count_holds_paper(n, adj, over="n2", gravity=mean_gravity):
    """Harder than the stub: correct RECORD SHAPE and correct m/Gr_bar, but a
    fabricated eigenvalue count.  It reports one eigenvalue below -m/Gr_bar on
    every graph.  The boolean verdict is unchanged and the record type-checks, so
    only the digest can catch this."""
    r = rhs(n, adj, over, gravity)
    if r is None:
        return None
    return (True, 1, r, spectral_index(n, adj))


def _fabricated_rhs_holds_paper(n, adj, over="n2", gravity=mean_gravity):
    """Correct shape, correct boolean, correct eigenvalue count -- and a
    fabricated m/Gr_bar.  On this corpus every honest count is 0, so the count
    carries no entropy and cannot catch anything; if the digest is to mean
    anything it has to include the fields that do the work."""
    r = rhs(n, adj, over, gravity)
    if r is None:
        return None
    return (True, count_below(n, adj, -r), r + 1, spectral_index(n, adj))


def _spectrum_free_holds_paper(n, adj, over="n2", gravity=mean_gravity):
    """MUTANT mutD, verbatim -- the one that got through.

    Real m/Gr_bar (rhs() is reachable by anyone without touching the spectrum),
    fabricated count 0 (which is the honest value on every graph of this corpus),
    no spectral work at all.  Against the OLD three-field verdict record this
    passed all sixteen controls, exited 0, and produced a transcript AND a
    certificate.json byte-identical to the clean run -- while being a verdict
    function with NO INPUT ON WHICH IT CAN ANSWER FALSE.

    It is planted here so that property is demonstrated on every run.
    """
    r = rhs(n, adj, over, gravity)
    if r is None:
        return None
    return (True, 0, r)


def _fabricated_spectrum_holds_paper(n, adj, over="n2", gravity=mean_gravity):
    """The sharpened mutD: everything mutD had, PLUS a shape-valid spectral field
    that was invented rather than computed -- inertia index 1, nullity 0, which is
    the honest answer for 45 of the 1360 corpus graphs and wrong for the other
    1315.  It is applied to BOTH readings (see `_fabricated_spectrum_holds_literal`)
    so that the two-readings-agree cross-check and the "index >= 1" invariant both
    pass.  Nothing structural can reject it.  Only the digest can -- which is the
    whole point of putting a spectral quantity in the record."""
    r = rhs(n, adj, over, gravity)
    if r is None:
        return None
    return (True, count_below(n, adj, -r), r, (1, 0))


def _fabricated_spectrum_holds_literal(n, adj, over="n2", gravity=mean_gravity):
    """The literal-reading half of the fabricated-spectrum mutant, so the fake is
    internally consistent and the digest is the only thing left to catch it."""
    r = rhs(n, adj, over, gravity)
    if r is None:
        return None
    return (True, count_above(n, adj, r), r, (1, 0))


def check_verdict_controls(levels):
    print("\n== 6e. controls on the verdict path itself ==")
    n, adj = petersen()

    # (i) a constant-True stub must not pass for a verdict record
    v = _stubbed_holds_paper(n, adj, "n2")
    err = verdict_error(v)
    if err is None:
        bad("a verdict function stubbed to `return True` was accepted as a verdict record")
    else:
        rejected("verdict function stubbed to `return True` on Petersen -- %s" % err)

    # (ii), (iii) shape-correct verdicts with fabricated content must move the
    # digest.  Same sub-corpus, same everything, only the verdict function
    # swapped: if the digest does not move, the digest is not a function of the
    # verdicts and pinning it proves nothing.
    sub = [(k, a) for k in range(2, 7) for a in levels[k] if size(k, a) > 0]
    real = verdict_stream(sub)
    if real["error"] is not None:
        bad("the honest sub-corpus stream did not build: %s" % real["error"])
        return
    for label, fake_fn in (("a fabricated eigenvalue count", _fabricated_count_holds_paper),
                           ("a fabricated m/Gr_bar", _fabricated_rhs_holds_paper)):
        fake = verdict_stream(sub, fp=fake_fn)
        # Either rejection counts: the stream may refuse to build at all (the two
        # readings then disagree about which m/Gr_bar they were decided on), or
        # it builds and the digest moves.  What must NOT happen is a matching
        # digest.
        if fake["error"] is not None:
            rejected("verdict with %s over %d records -- stream refused to build: %s"
                     % (label, real["records"], fake["error"]))
        elif real["digest"] == fake["digest"]:
            bad("%s left the verdict digest unchanged -- the digest is not a function of "
                "the verdicts, so pinning it certifies nothing" % label)
        else:
            rejected("verdict with %s over %d records -- digest moves %s... -> %s..."
                     % (label, real["records"], real["digest"][:16], fake["digest"][:16]))


# ---------------------------------------------------------------------------
# check 6f -- the mutant that got through, and the question it exposed
# ---------------------------------------------------------------------------

def check_spectrum_free_controls(levels):
    """The three controls added after mutant `mutD` was found.

    mutD replaced BOTH verdict bodies with `return (True, 0, rhs(...))`.  It kept
    the record shape, produced the REAL m/Gr_bar (rhs() needs no spectral work),
    and fabricated a count of 0 -- which is the honest count on every graph of
    this corpus.  It passed all sixteen controls of the previous round with a
    transcript and a certificate.json byte-identical to the clean run.

    Two things were wrong and both are controlled here:
      (i)  the digest had ZERO entropy from the eigenvalue engine, so a verdict
           function that never computed a spectrum could reproduce the receipt;
      (iii) mutD had NO INPUT ON WHICH IT COULD ANSWER FALSE, so a real
           counterexample anywhere in the corpus would have been reported as a
           pass.  A certificate that cannot fail certifies nothing.
    """
    print("\n== 6f. the spectrum-free mutant, and whether this path can answer False ==")
    n, adj = petersen()
    sub = [(k, a) for k in range(2, 7) for a in levels[k] if size(k, a) > 0]
    real = verdict_stream(sub)
    if real["error"] is not None:
        bad("the honest sub-corpus stream did not build: %s" % real["error"])
        return

    # (i) mutD itself.
    for label, fp, fl in (
            ("mutD: (True, 0, rhs(...)) -- no spectral work at all",
             _spectrum_free_holds_paper, _spectrum_free_holds_paper),
            ("mutD sharpened: shape-valid but FABRICATED inertia index",
             _fabricated_spectrum_holds_paper, _fabricated_spectrum_holds_literal)):
        fake = verdict_stream(sub, fp=fp, fl=fl)
        if fake["error"] is not None:
            rejected("%s -- stream refused to build: %s" % (label, fake["error"]))
        elif real["digest"] == fake["digest"]:
            bad("%s left the verdict digest unchanged -- the digest still carries no "
                "entropy from the eigenvalue engine" % label)
        else:
            rejected("%s -- digest moves %s... -> %s..."
                     % (label, real["digest"][:16], fake["digest"][:16]))

    # (iii) THE DECISIVE ONE.  Feed the real verdict function a graph on which
    # the inequality genuinely FAILS -- Petersen under this file's own planted
    # mutated_mean_gravity, which control 6d independently certifies as a
    # violation -- and require it to say so.  A verdict function that cannot
    # produce False here is not deciding anything.
    fail_gravity = lambda k, a, over="n2": mutated_mean_gravity(k, a)
    v = holds_paper(n, adj, "n2", gravity=fail_gravity)
    err = verdict_error(v)
    if err is not None:
        bad("on a planted FAILING instance the verdict path did not answer: %s" % err)
    elif v[0] or v[1] < 2:
        bad("holds_paper returned %r on Petersen under the planted-wrong gravity "
            "convention, where the inequality genuinely fails (m/Gr_bar = %s < 2 = "
            "-lambda_{n-1}) -- this verdict path has no input on which it answers False"
            % (v, v[2]))
    else:
        rejected("planted FAILING instance -- Petersen under the mutated gravity "
                 "convention: holds_paper returns %r, i.e. False with %d eigenvalues "
                 "below -%s. The verdict path can answer False." % (v, v[1], v[2]))


# ---------------------------------------------------------------------------
# receipt
# ---------------------------------------------------------------------------

def build_receipt(counts, corpus, battery_rows, worked, controls_passed):
    return {
        "planted_failure_controls": {
            "expected": EXPECTED_CONTROLS,
            "rejected": controls_passed,
            "note": "Every control block must run and be rejected. The count is asserted "
                    "against EXPECTED_CONTROLS before this receipt is built, so removing a "
                    "control block fails the run rather than quietly shrinking the battery.",
        },
        "verdict_binding": "corpus.verdict_digest_sha256 is a sha256 over the canonical sorted "
                           "stream of the verdict records RETURNED by holds_paper and "
                           "holds_literal on every corpus graph under both mean conventions. "
                           "Each record is (holds, exact_count, m/Gr_bar, spectral_index), the "
                           "last being the inertia of the adjacency matrix -- the field with "
                           "per-graph entropy that cannot be produced without running the exact "
                           "congruence. It was added after mutant mutD, which returned "
                           "(True, 0, rhs(...)) with no spectral work at all, reproduced the "
                           "previous receipt byte for byte. No shipped field in this receipt is "
                           "computed around the verdict path. Controls 6e and 6f plant a stubbed "
                           "verdict function, a fabricated count, a fabricated m/Gr_bar, mutD "
                           "itself, a fabricated inertia index, and a genuinely FAILING instance "
                           "on which the verdict path must return False.",
        "not_defended_against": "A corrupted VERIFIER. Every control in this run is a corrupted "
                                "INPUT; nothing in verify.py can detect an edit to verify.py "
                                "(a stubbed function, a no-oped failure accumulator, a hardcoded "
                                "verdict). That boundary is held outside the file: the sha256 of "
                                "verify.py and of this receipt pinned in "
                                "certificates/contracts.json, the git history of both, and "
                                "review.",
        "claim_owner": "Graffiti (S. Fajtlowicz), conjecture 290, 'Written on the Wall' p.79; "
                       "proof by Nathan Wilbanks and 'Annie' (AGNT Labs), "
                       "'A Proof of Graffiti 290'",
        "our_contribution": "independent finite verification only -- no part of the conjecture "
                            "or of the proof is a result of this repository",
        "convention": {
            "gravity_matrix": "Written-on-the-Wall / Brewster et al.: Gr(u,v) = 0 if u == v or "
                              "if no path joins u to v, else d(u)d(v)/((n-1) d(u,v)); checked "
                              "entry by entry against that transcription in check 1b, on "
                              "connected and disconnected hand-computed cases, rather than "
                              "assumed",
            "convention_dependence": "The truth value of Graffiti 290 depends on which gravity "
                                     "definition is used, and BOTH halves of the situation must "
                                     "be reported. (a) A live refutation exists under the "
                                     "gravity definition in Aouchiche and Hansen's survey "
                                     "(Linear Algebra Appl. 432(9):2293-2322, 2010): "
                                     "Roucairol-Cazenave (arXiv:2409.18626v1, Sec. 5.2 "
                                     "'Erratum') report 290 there 'was solved instantly'. "
                                     "(b) Those same authors disavow that definition: they call "
                                     "the Written-on-the-Wall / Brewster-Dinneen-Faber "
                                     "definition 'the correct definition' and report that "
                                     "refutation was 'seemingly impossible' under it. This "
                                     "certificate is scoped to the Brewster reading -- the one "
                                     "the theorem is stated over -- and does NOT replay the "
                                     "refutation.",
            "mean_gravity": "not defined in Written on the Wall; the paper fixes it as the mean "
                            "over all n^2 entries of the gravity matrix. Verified here under "
                            "that convention AND under the mean over the n(n-1) off-diagonal "
                            "entries.",
            "readings": "verified in both the paper's reading (-lambda_{n-1} <= m/Gr_bar) and "
                        "the literal Written-on-the-Wall reading (lambda_{n-1} <= m/Gr_bar); "
                        "the paper's is the stronger of the two",
            "connectivity": "the paper adds a connectivity hypothesis that Written on the Wall "
                            "p.79 does not state; not needed in the verified range",
        },
        "exhaustive_enumeration": {
            "up_to_order": NMAX,
            "isomorphism_classes_by_order": [counts[n] for n in range(1, NMAX + 1)],
            "includes_disconnected": True,
            "cutoff_reason": "compute, not mathematics -- see README",
        },
        "corpus": corpus,
        "larger_instances": battery_rows,
        "worked_examples_from_the_paper": worked,
        "not_certified_here": [
            "novelty and priority of the proof -- not assessed",
            "the paper's own proof, its lemmas, its quartic-positivity step, and its n >= 7 "
            "argument -- NOT replayed; only the inequality's truth on a finite family is checked",
            "the conjecture for n > 10 outside the explicitly listed larger instances",
            "the Aouchiche-Hansen gravity definition and the refutation reported under it -- "
            "we did not obtain that definition and did not replay that refutation; we also do "
            "not adjudicate Roucairol-Cazenave's own judgement that it is a misstatement",
            "the text of Written on the Wall p.79 and p.52 -- quoted here at second hand via "
            "Roucairol-Cazenave, not read in the original by this certificate",
            "whether the girth >= 5 hypothesis is necessary -- see README; our search found no "
            "girth < 5 counterexample either, which is a fact about our range, not a theorem",
        ],
    }


def compare(computed, stored, path=""):
    diffs = []
    if type(computed) is not type(stored) and not (
            isinstance(computed, (int, float)) and isinstance(stored, (int, float))):
        return ["%s: type %s vs %s" % (path or "<root>", type(computed).__name__,
                                       type(stored).__name__)]
    if isinstance(computed, dict):
        for k in sorted(set(computed) | set(stored)):
            if k not in computed:
                diffs.append("%s.%s: missing from the recomputation" % (path, k))
            elif k not in stored:
                diffs.append("%s.%s: missing from the stored receipt" % (path, k))
            else:
                diffs += compare(computed[k], stored[k], "%s.%s" % (path, k))
    elif isinstance(computed, list):
        if len(computed) != len(stored):
            diffs.append("%s: length %d vs stored %d" % (path, len(computed), len(stored)))
        else:
            for i, (a, b) in enumerate(zip(computed, stored)):
                diffs += compare(a, b, "%s[%d]" % (path, i))
    elif computed != stored:
        diffs.append("%s: %r vs stored %r" % (path, computed, stored))
    return diffs


# ---------------------------------------------------------------------------

def main():
    emit = "--emit" in sys.argv[1:]

    print("Graffiti 290 -- independent replay of an EXTERNAL result.")
    print("Conjecture: Graffiti / S. Fajtlowicz. Proof: N. Wilbanks and 'Annie' (AGNT Labs).")
    print("Ours: the verification below, and the scope statement, and nothing else.")
    print("Convention: Written-on-the-Wall / Brewster gravity matrix. Under the gravity")
    print("definition in Aouchiche and Hansen's survey the conjecture is reported REFUTED")
    print("(Roucairol-Cazenave, arXiv:2409.18626v1 Sec. 5.2) -- not replayed here. Those same")
    print("authors call the Brewster definition 'the correct definition'; both halves stand.")

    check_engine()
    check_engine_controls()
    check_gravity_convention()

    levels = generate(NMAX)
    counts = check_family(levels)
    check_family_controls(levels)

    corpus = check_inequality(levels)
    if corpus is not None:
        girth_facts = check_girth_necessity()
        if girth_facts is None:
            corpus = None
        else:
            corpus.update(girth_facts)
    battery_rows = check_battery()
    check_battery_controls()
    worked = check_worked_examples()
    check_convention_controls()
    check_verdict_controls(levels)
    check_spectrum_free_controls(levels)

    # A control battery that is never counted is a control battery that can be
    # deleted in silence.  Commenting out a control block used to leave this run
    # at exit 0; it now fails here.
    if CONTROLS_PASSED != EXPECTED_CONTROLS:
        bad("%d planted-failure controls were rejected, but exactly %d must run -- a control "
            "block has been removed, skipped, or short-circuited"
            % (CONTROLS_PASSED, EXPECTED_CONTROLS))

    if FAILURES or corpus is None:
        print("\nFAIL -- %d check(s) failed:" % len(FAILURES))
        for f in FAILURES:
            print("  - " + f)
        return 1

    receipt = build_receipt(counts, corpus, battery_rows, worked, CONTROLS_PASSED)

    print("\n== 7. receipt ==")
    if emit:
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print("     receipt-emitted: %s  (--emit was passed; this is NOT the default path)"
              % RECEIPT.name)
    else:
        if not RECEIPT.exists():
            print("[FAIL] %s is missing; run with --emit to create it" % RECEIPT.name)
            return 1
        stored = json.loads(RECEIPT.read_text())
        diffs = compare(receipt, stored)
        if diffs:
            print("[FAIL] recomputation does not match the committed receipt:")
            for d in diffs[:40]:
                print("  - " + d)
            return 1
        # Unindented on purpose: tools/check_receipt_drift.py matches this line
        # with str.startswith("receipt-checked:"), and that is how a CHECK-ONLY
        # verifier declares it re-derived its receipt without rewriting it.
        # Indented, the gate cannot see it and reports the receipt as never
        # checked -- a false "unchecked" on a receipt that is compared field by
        # field on every run.
        print("receipt-checked: %s" % RECEIPT.name)

    print("\n%d of %d planted-failure controls rejected as required (count asserted, not just "
          "printed)." % (CONTROLS_PASSED, EXPECTED_CONTROLS))
    print("verdict digest over %d verdict records: %s"
          % (corpus["verdict_records"], corpus["verdict_digest_sha256"]))
    print("PASS -- Graffiti 290 holds, under the Written-on-the-Wall / Brewster gravity")
    print("convention, on every girth->=5 graph of order <= %d (all %d of them, connected and"
          % (NMAX, corpus["graphs_checked"]))
    print("not) and on %d larger instances up to Hoffman-Singleton. Under the Aouchiche-Hansen"
          % len(battery_rows))
    print("convention it is reported refuted; that reading is NOT certified here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

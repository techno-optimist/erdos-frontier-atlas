#!/usr/bin/env python3
"""Independent exact replay of the power-weighted-lift Keller family F_{k,d} : A^3 -> A^3.

THE FAMILY IS NOT OURS.  It is claimed by Annie (AGNT Labs, Technical Report III,
v1.0, 21 July 2026), "Power-Weighted Lifts: Explicit Higher-Weight Noninjective
Keller Maps in Three Variables".  That byline is the whole byline: the document
names no other author.  What is ours is only this replay: a from-scratch
reimplementation of its Section 3 PROSE -- not a replay of its receipts, which
have no intact chain -- in exact rational arithmetic, plus the checks and the
planted failures below.

PRIOR ART (our reading, not the report's words): we read the report as placing
the k = 1 row of the grid inside Alexis Gallagher's earlier one-variable
weighted-lift work, so 7 of the 27 members verified here look to us not new with
this paper.  See PRIOR_ART_K1 for the report's actual sentences and GALLAGHER for
the citation its own bibliography gives.

WHAT THIS FILE CANNOT DEFEND AGAINST: an edit to this file.  See the section of
that name in README.md; the defence is the sha256 pinned in
certificates/contracts.json plus the git history, not any check written here.

Replay:   python3 -I verify.py
Emit:     python3 -I verify.py --emit      (rewrites witness.json; NOT the default)

No third-party imports.  No floats anywhere in the trust path.
"""

import argparse
import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
RECEIPT = HERE / "witness.json"

# The grid the paper tabulates.
GRID = [(k, d) for k in range(1, 7) for d in range(k + 1, 9)]

# --------------------------------------------------------------------------
# 0.  Gate call tracing.
#
#     Every function marked @gate records its name when it is called.  This buys
#     exactly one thing, and it is worth being precise about what: after the
#     default verification path has finished, we snapshot the set of gates it
#     actually called, and then require each planted-failure control to name a
#     gate from that snapshot.  So "the control is scored against a gate the
#     default path itself runs" stops being a sentence in a comment and becomes
#     something this run measures.
#
#     It does NOT measure that the control's rejection came from that gate and
#     nowhere else -- the control returns the gate call's own verdict, which is a
#     source-level property a reader must check by reading, not something the
#     program can establish about itself.
# --------------------------------------------------------------------------

GATE_CALLS = set()


def gate(fn):
    def wrapper(*a, **kw):
        GATE_CALLS.add(fn.__name__)
        return fn(*a, **kw)
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    wrapper.__wrapped__ = fn
    return wrapper

# Prior art.  The inference below is OURS, not the report's.  The report does
# not say "the k = 1 row is prior art"; it says the two things quoted in
# PAPER_PRIOR_ART_QUOTE, and we read them as putting that row inside Gallagher's
# earlier work.  Our reading errs toward de-claiming, which is the safe
# direction, but it is still ours and it is labelled as ours everywhere it
# appears: the header, every k = 1 member record, and the top of the receipt.  A
# reader of the transcript alone must be able to tell our inference from their
# assertion.
PAPER_PRIOR_ART_QUOTE = (
    "\"Gallagher's subsequent public notes describe a one-variable weighted-lift "
    "mechanism in that row and an atlas realizing generic degrees at least three "
    "... The old weight row is k=1; the new construction works for every k>=1\"; "
    "and, separately, \"Historical priority outside the searched public record is "
    "not asserted.\"")
GALLAGHER = ("Alexis Gallagher, \"Exact certificate atlas: Generic fiber degrees 3 "
             "through 100,\" jacobianfun.org/counterexamples, accessed July 21, 2026 "
             "(the citation given in the report's own bibliography)")
PRIOR_ART_K1 = ("k=1 row: OUR READING of the report -- not its words -- is that this "
                "row lies inside Gallagher's earlier one-variable weighted-lift work "
                "and so is not new with this paper; see prior_art at the top of this "
                "receipt for the report's actual sentences. Priority is not "
                "adjudicated here, by us or by them.")


# --------------------------------------------------------------------------
# 1.  Exact multivariate polynomial engine over Q, three variables x, y, z.
#     A polynomial is a dict {(a, b, c): Fraction} with no zero coefficients.
# --------------------------------------------------------------------------

def pconst(c):
    c = Fr(c)
    return {} if c == 0 else {(0, 0, 0): c}


def pvar(i):
    e = [0, 0, 0]
    e[i] = 1
    return {tuple(e): Fr(1)}


def padd(a, b):
    r = dict(a)
    for m, c in b.items():
        n = r.get(m, 0) + c
        if n:
            r[m] = n
        else:
            r.pop(m, None)
    return r


def psub(a, b):
    return padd(a, {m: -c for m, c in b.items()})


def pscal(a, s):
    s = Fr(s)
    if s == 0:
        return {}
    return {m: c * s for m, c in a.items()}


def pmul(a, b):
    if not a or not b:
        return {}
    r = {}
    for m1, c1 in a.items():
        a0, a1, a2 = m1
        for m2, c2 in b.items():
            m = (a0 + m2[0], a1 + m2[1], a2 + m2[2])
            n = r.get(m)
            r[m] = c1 * c2 if n is None else n + c1 * c2
    return {m: c for m, c in r.items() if c}


def ppow(a, n):
    r = pconst(1)
    base = a
    while n:
        if n & 1:
            r = pmul(r, base)
        n >>= 1
        if n:
            base = pmul(base, base)
    return r


def pdiff(a, i):
    r = {}
    for m, c in a.items():
        if m[i]:
            e = list(m)
            e[i] -= 1
            r[tuple(e)] = c * m[i]
    return r


def pdiv_x(a, m):
    """Exact division by x**m.  Returns None if x**m does not divide a."""
    r = {}
    for mon, c in a.items():
        if mon[0] < m:
            return None
        r[(mon[0] - m, mon[1], mon[2])] = c
    return r


def pdet3(m):
    d0 = psub(pmul(m[1][1], m[2][2]), pmul(m[1][2], m[2][1]))
    d1 = psub(pmul(m[1][0], m[2][2]), pmul(m[1][2], m[2][0]))
    d2 = psub(pmul(m[1][0], m[2][1]), pmul(m[1][1], m[2][0]))
    return padd(psub(pmul(m[0][0], d0), pmul(m[0][1], d1)), pmul(m[0][2], d2))


def pjacdet(F):
    return pdet3([[pdiff(f, i) for i in range(3)] for f in F])


# --------------------------------------------------------------------------
# 2.  Exact univariate polynomial engine over Q (lists, index = degree).
# --------------------------------------------------------------------------

def utrim(a):
    while a and a[-1] == 0:
        a.pop()
    return a


def umono(c, n):
    return utrim([Fr(0)] * n + [Fr(c)])


def uadd(a, b):
    n = max(len(a), len(b))
    return utrim([(a[i] if i < len(a) else Fr(0)) + (b[i] if i < len(b) else Fr(0))
                  for i in range(n)])


def usub(a, b):
    n = max(len(a), len(b))
    return utrim([(a[i] if i < len(a) else Fr(0)) - (b[i] if i < len(b) else Fr(0))
                  for i in range(n)])


def uscal(a, s):
    s = Fr(s)
    return utrim([c * s for c in a]) if s else []


def uderiv(a):
    return utrim([a[i] * i for i in range(1, len(a))])


def urem(a, b):
    a = list(a)
    if not b:
        raise ZeroDivisionError("univariate remainder by zero polynomial")
    while len(a) >= len(b) and a:
        f = a[-1] / b[-1]
        sh = len(a) - len(b)
        for i in range(len(b)):
            a[sh + i] -= f * b[i]
        utrim(a)
    return a


def ugcd(a, b):
    a, b = list(a), list(b)
    while b:
        a, b = b, urem(a, b)
    return uscal(a, Fr(1) / a[-1]) if a else []


def is_constant(a):
    return len(a) <= 1


# --------------------------------------------------------------------------
# 3.  The family, rebuilt from the paper's Section 3 prose.
#
#     Torus-invariant coordinates   v = x^k y,  t = x^{k+1} z
#     u = 1 + v,   gamma = 1 - ((d+k)/d) v - t,   w = u * gamma
#     q(w) = ((k+1) w^k - (d+1) w^d) / (d-k)
#     Q(w) = (w^{k+1} - w^{d+1}) / (d-k)
#     p(w) = (w q(w) - Q(w)) / (k+1)
#     alpha = p(w)/gamma^{k+1} + u/(k+1),   beta = q(w)/gamma^k + 1
#     F_{k,d} = ( alpha / x^{k+1},  beta / x^k,  x gamma )
#
#     Because w = u*gamma, both gamma-divisions cancel *exactly* and alpha,
#     beta are honest polynomials in (u, gamma) -- no rational-function
#     machinery is needed and no division by gamma ever happens numerically:
#
#       w q(w) - Q(w) = (k w^{k+1} - d w^{d+1}) / (d-k)
#       => p(w)/gamma^{k+1} = (k u^{k+1} - d u^{d+1} gamma^{d-k}) / ((k+1)(d-k))
#       => q(w)/gamma^k     = ((k+1) u^k - (d+1) u^d gamma^{d-k}) / (d-k)
#
#     This identity is itself re-checked below (leg "gamma-cancellation").
# --------------------------------------------------------------------------

def build_uv(k, d, c_v=None):
    """u, gamma, w as polynomials in x, y, z.  c_v overridable for a control."""
    if c_v is None:
        c_v = Fr(d + k, d)
    x = pvar(0)
    v = pmul(ppow(x, k), pvar(1))
    t = pmul(ppow(x, k + 1), pvar(2))
    u = padd(pconst(1), v)
    g = psub(psub(pconst(1), pscal(v, c_v)), t)
    return u, g, pmul(u, g)


def build_alpha_beta(k, d, c_v=None):
    u, g, _w = build_uv(k, d, c_v)
    e = d - k
    ge = ppow(g, e)
    beta = padd(pscal(psub(pscal(ppow(u, k), k + 1),
                           pscal(pmul(ppow(u, d), ge), d + 1)), Fr(1, e)),
                pconst(1))
    alpha = padd(pscal(psub(pscal(ppow(u, k + 1), k),
                            pscal(pmul(ppow(u, d + 1), ge), d)), Fr(1, (k + 1) * e)),
                 pscal(u, Fr(1, k + 1)))
    return alpha, beta, g


@gate
def build_family(k, d, c_v=None):
    """Returns (F1, F2, F3) or None if the x-divisions do not come out exact."""
    alpha, beta, g = build_alpha_beta(k, d, c_v)
    F1 = pdiv_x(alpha, k + 1)
    F2 = pdiv_x(beta, k)
    if F1 is None or F2 is None:
        return None
    return (F1, F2, pmul(pvar(0), g))


def uq(k, d):
    return uadd(umono(Fr(k + 1, d - k), k), umono(Fr(-(d + 1), d - k), d))


def uQ(k, d):
    return uadd(umono(Fr(1, d - k), k + 1), umono(Fr(-1, d - k), d + 1))


# --------------------------------------------------------------------------
# 4.  Small commutative rings for evaluating F at collision points.
#     QRing  = Q.   CycRing(r) = Q[T]/Phi_r(T) for r prime (a field, but only
#     +, -, * are ever used -- every collision point below is written with
#     inverse roots of unity as *powers*, so no inversion is needed).
# --------------------------------------------------------------------------

class QRing:
    name = "Q"

    def lift(self, c):
        return Fr(c)

    zero = Fr(0)
    one = Fr(1)

    def add(self, a, b):
        return a + b

    def mul(self, a, b):
        return a * b

    def eq(self, a, b):
        return a == b

    def key(self, a):
        return str(a)


class CycRing:
    """Q[T]/Phi_r(T), r prime; Phi_r = 1 + T + ... + T^{r-1}. zeta := T."""

    def __init__(self, r):
        self.r = r
        self.n = r - 1                      # degree of Phi_r
        self.name = "Q(zeta_%d)" % r
        self.zero = tuple([Fr(0)] * self.n)
        self.one = tuple([Fr(1)] + [Fr(0)] * (self.n - 1))

    def lift(self, c):
        return tuple([Fr(c)] + [Fr(0)] * (self.n - 1))

    def _reduce(self, coeffs):
        c = list(coeffs)
        # T^{n} = -(1 + T + ... + T^{n-1})
        for i in range(len(c) - 1, self.n - 1, -1):
            if c[i]:
                v = c[i]
                c[i] = Fr(0)
                for j in range(i - self.n, i):
                    c[j] -= v
        return tuple(c[: self.n] + [Fr(0)] * (self.n - len(c)))

    def add(self, a, b):
        return tuple(x + y for x, y in zip(a, b))

    def mul(self, a, b):
        out = [Fr(0)] * (2 * self.n)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    if y:
                        out[i + j] += x * y
        return self._reduce(out)

    def eq(self, a, b):
        return a == b

    def key(self, a):
        return "[" + ",".join(str(c) for c in a) + "]"

    def zeta_pow(self, e):
        e %= self.r
        p = [Fr(0)] * (self.n + 1)
        p[e] = Fr(1)
        return self._reduce(p)


def evaluate(P, pt, ring):
    """Evaluate a Q-coefficient polynomial at a point over `ring` (Horner-free)."""
    acc = ring.zero
    for (a, b, c), coef in P.items():
        term = ring.lift(coef)
        for val, e in zip(pt, (a, b, c)):
            for _ in range(e):
                term = ring.mul(term, val)
        acc = ring.add(acc, term)
    return acc


def image(F, pt, ring):
    return tuple(evaluate(f, pt, ring) for f in F)


# --------------------------------------------------------------------------
# 5.  Collision constructions.
#
#     Every collision below is *derived* here and then *checked* by evaluating
#     the reconstructed polynomials; if a derivation were wrong the check would
#     fail rather than silently pass.
#
#     Mechanism A ("sign", needs d-k even):  the paper's own witness shape.
#         gamma^{d-k} = 1 has the extra rational root gamma = -1.
#     Mechanism B ("root-of-unity", needs k >= 2): (u, gamma) -> (u/z, z*gamma)
#         with z^k = 1 fixes the whole image.  Rational exactly when k is even
#         (z = -1); otherwise it lives in Q(zeta_r), r = least prime factor of k.
#     Mechanism C ("two-root", used for k = 1): two distinct rational roots of
#         the fibre equation Q(w) - V w + (k+1) T = 0.
# --------------------------------------------------------------------------

def least_prime_factor(n):
    f = 2
    while f * f <= n:
        if n % f == 0:
            return f
        f += 1
    return n


def collision_sign(k, d):
    if (d - k) % 2:
        return None
    z = 2 if k % 2 else -2
    return QRing(), (Fr(1), Fr(0), Fr(0)), (Fr(-1), Fr(0), Fr(z)), "sign"


def root_of_unity_pair(k, d, ring, e=1):
    """The pair (1,0,0) and its image under (u,gamma) -> (u/zeta, zeta*gamma).

    zeta = ring's r-th root of unity raised to `e`; e=0 is the degenerate zeta=1
    used as a planted failure.  Only ring +,* are used: zeta^{-1} is a power.
    """
    if isinstance(ring, QRing):
        zt = Fr(-1) if e else Fr(1)
        zi = zt
        one = Fr(1)
    else:
        zt = ring.zeta_pow(e)
        zi = ring.zeta_pow(-e)
        one = ring.one
    # u2 = zeta^{-1}, gamma2 = zeta, x2 = zeta^{-1}
    # v2 = u2 - 1 ; t2 = 1 - ((d+k)/d) v2 - gamma2
    # x2^k = zeta^{-k} = 1  =>  y2 = v2 ;  x2^{k+1} = zeta^{-1}  =>  z2 = zeta * t2
    v2 = ring.add(zi, ring.lift(-1))
    t2 = ring.add(ring.add(one, ring.mul(ring.lift(Fr(-(d + k), d)), v2)),
                  ring.mul(ring.lift(-1), zt))
    P1 = (ring.lift(1), ring.lift(0), ring.lift(0))
    P2 = (zi, v2, ring.mul(zt, t2))
    return P1, P2


def collision_root_of_unity(k, d):
    if k < 2:
        return None
    r = least_prime_factor(k)
    ring = QRing() if r == 2 else CycRing(r)
    P1, P2 = root_of_unity_pair(k, d, ring, e=1)
    return ring, P1, P2, "root-of-unity"


@gate
def check_collision(F, ring, P1, P2):
    """The non-injectivity gate.  Distinctness FIRST -- equal images between a
    point and itself is not evidence of anything."""
    if all(ring.eq(a, b) for a, b in zip(P1, P2)):
        return False, "the two points are equal"
    i1, i2 = image(F, P1, ring), image(F, P2, ring)
    if not all(ring.eq(a, b) for a, b in zip(i1, i2)):
        return False, "images differ"
    return True, "ok"


def collision_two_root(k, d, w2=Fr(2)):
    """Fibre equation Q(w) - V w + (k+1) T = 0 with T = 0 and roots w = 0, w2.

    T = 0 forces V = (w^k - w^d)/(d-k) at the nonzero root; gamma^k = V - q(w).
    Only used for k = 1, where the k-th root is unconditionally rational.
    """
    if k != 1:
        return None
    V = (w2 ** k - w2 ** d) / Fr(d - k)
    g1 = V                                   # w=0: gamma^1 = V - q(0) = V
    qv = (Fr(k + 1) * w2 ** k - Fr(d + 1) * w2 ** d) / Fr(d - k)
    g2 = V - qv                              # w=w2: gamma^1 = V - q(w2)
    if g1 == 0 or g2 == 0:
        return None
    # point 1: u=0 -> v=-1 ; x1 = 1
    v1, x1 = Fr(-1), Fr(1)
    t1 = 1 - Fr(d + k, d) * v1 - g1
    P1 = (x1, v1 / x1 ** k, t1 / x1 ** (k + 1))
    # point 2: u = w2/g2
    u2 = w2 / g2
    v2 = u2 - 1
    t2 = 1 - Fr(d + k, d) * v2 - g2
    x2 = g1 / g2                              # so that x*gamma agrees
    P2 = (x2, v2 / x2 ** k, t2 / x2 ** (k + 1))
    return QRing(), P1, P2, "two-root"


def pick_collision(k, d):
    """Prefer a Q-rational witness; fall back to a cyclotomic one."""
    for cand in (collision_sign(k, d), collision_two_root(k, d),
                 collision_root_of_unity(k, d)):
        if cand and isinstance(cand[0], QRing):
            return cand
    for cand in (collision_root_of_unity(k, d), collision_two_root(k, d),
                 collision_sign(k, d)):
        if cand:
            return cand
    return None


# --------------------------------------------------------------------------
# 6.  Generic-degree certificate.
#
#     For a target with Z != 0 the fibre is in bijection with
#         { (w, gamma) : G(w) = 0,  gamma^k = V - q(w) },   V = Y Z^k,
#     G(w) = Q(w) - V w + (k+1) T,  T = X Z^{k+1}   (see README for the algebra;
#     the identity the bijection rests on is machine-checked as leg "fibre").
#     deg G = d+1 always.  If G is squarefree and no root of G meets V = q(w),
#     the fibre has exactly k(d+1) distinct points.  Both are exact gcd tests.
# --------------------------------------------------------------------------

def fibre_poly(k, d, V, T):
    return uadd(uQ(k, d), uadd(umono(-Fr(V), 1), umono(Fr(k + 1) * Fr(T), 0)))


@gate
def fibre_is_etale(k, d, V, T):
    G = fibre_poly(k, d, V, T)
    if len(G) != d + 2:
        return False, "deg G != d+1"
    if not is_constant(ugcd(G, uderiv(G))):
        return False, "G not squarefree"
    if not is_constant(ugcd(G, usub(umono(Fr(V), 0), uq(k, d)))):
        return False, "some root of G has gamma = 0"
    return True, "ok"


def udeg(a):
    """Degree of a univariate polynomial; -1 for the zero polynomial."""
    return len(a) - 1


def fibre_point_count(k, d, V, T):
    """COUNT the points of the fibre over (V, T).  Never restate k(d+1).

    The count is taken from the very polynomial the etale gate measured:
    G = fibre_poly(k, d, V, T) contributes deg(G / gcd(G, G')) distinct roots w
    in Q-bar, and over an etale target every such root has V - q(w) != 0, so
    gamma^k = V - q(w) has exactly k distinct solutions.  Hence the fibre has
    k * #{distinct roots of G} points.

    Returns None when the target is not etale, so a count is never reported for
    a fibre that is not reduced.  Nothing here reads d except through G itself.
    """
    ok, _why = fibre_is_etale(k, d, V, T)
    if not ok:
        return None
    G = fibre_poly(k, d, V, T)
    distinct_roots = udeg(G) - udeg(ugcd(G, uderiv(G)))
    return k * distinct_roots


@gate
def generic_degree_ok(k, d, V, T, claimed):
    """THE gate for the generic-degree leg: `claimed` must equal the count.

    This is the function the default path runs on every member, and the one
    control C12 fires at with a mutated claim.  If it merely echoed a formula
    it could not reject anything -- so it compares against fibre_point_count.
    """
    counted = fibre_point_count(k, d, V, T)
    if counted is None:
        return False, "target (V,T) is not etale, so the fibre is not reduced"
    if counted != claimed:
        return False, "counted %d fibre points, claim says %d" % (counted, claimed)
    return True, "ok"


def find_etale_target(k, d):
    for T in (0, 1, 2, 3, 5, 7, 11):
        for V in (1, 2, 3, 5, 7, 11, 13):
            ok, _ = fibre_is_etale(k, d, Fr(V), Fr(T))
            if ok:
                return Fr(V), Fr(T)
    return None


# --------------------------------------------------------------------------
# 7.  The paper's own printed degree-8 specialisation (k, d) = (2, 3).
#     Transcribed from the report; our rebuild must reproduce it exactly.
# --------------------------------------------------------------------------

PAPER_23 = (
    {(0, 0, 1): Fr(1), (1, 2, 0): Fr(8, 3), (2, 1, 1): Fr(4), (3, 3, 0): Fr(20, 3),
     (4, 2, 1): Fr(6), (5, 4, 0): Fr(17, 3), (6, 3, 1): Fr(4), (7, 5, 0): Fr(5, 3),
     (8, 4, 1): Fr(1)},
    {(0, 1, 0): Fr(2, 3), (1, 0, 1): Fr(4), (2, 2, 0): Fr(11), (3, 1, 1): Fr(12),
     (4, 3, 0): Fr(16), (5, 2, 1): Fr(12), (6, 4, 0): Fr(20, 3), (7, 3, 1): Fr(4)},
    {(1, 0, 0): Fr(1), (3, 1, 0): Fr(-5, 3), (4, 0, 1): Fr(-1)},
)


# --------------------------------------------------------------------------
# 8.  Per-member verification.
# --------------------------------------------------------------------------

@gate
def det_ok(F, claimed):
    """THE determinant gate: det J F must BE the claimed constant, coefficient by
    coefficient.  Shared by the default path and control C3 so that the control
    exercises the same code, not a lookalike."""
    return pjacdet(F) == pconst(Fr(claimed))


@gate
def anchor_ok(anchor):
    """THE anchor gate: our independent rebuild of (k,d)=(2,3) must equal the
    expansion `anchor` printed in the paper.  Shared by the default path (which
    passes PAPER_23) and control C6 (which passes a corrupted copy)."""
    F23 = build_family(2, 3)
    return F23 is not None and tuple(F23) == tuple(anchor)


def source_grading(k):
    """The grading of the source torus: deg(x, y, z) = (1, -k, -(k+1)).

    This triple is a DEFINITION -- the torus action the equivariance claim is
    made with respect to -- so it is not something a check can discover.  What
    makes it non-free in the receipt is that the very object recorded there is
    the one handed to component_weights(): change it and the isobaric
    measurement changes with it, which is what control C13 exercises.
    """
    return (1, -k, -(k + 1))


def component_weights(F, grading):
    """MEASURE the weight of each component of F under `grading`.

    Returns [w1, w2, w3] when every component is isobaric, and None as soon as
    one is not -- there is no weight to report for a component whose monomials
    disagree, and reporting one anyway is the restatement this function exists
    to prevent.
    """
    wx, wy, wz = grading
    out = []
    for f in F:
        seen = {a * wx + b * wy + c * wz for (a, b, c) in f}
        if len(seen) != 1:
            return None
        out.append(seen.pop())
    return out


@gate
def weights_ok(F, k, grading=None, recorded=None):
    """THE weight gate: under the source grading, F1, F2, F3 must be isobaric of
    weights (-(k+1), -k, 1).

    Both of the receipt's weight fields are fed back through here: `grading` is
    the triple the receipt records (mutate it and no component is isobaric), and
    `recorded` is the weight list the receipt records (mutate it and it stops
    equalling the measurement).  Neither is a free restatement any more.
    """
    got = component_weights(F, source_grading(k) if grading is None else grading)
    if got is None or got != [-(k + 1), -k, 1]:
        return False
    return recorded is None or recorded == got


@gate
def gamma_cancellation_ok(k, d):
    """(k+1) p(w) == w q(w) - Q(w)  and  the two closed forms used for alpha,
    beta really equal p(w)/gamma^{k+1} and q(w)/gamma^k -- checked by
    multiplying the closed forms back up by gamma^{k+1}, gamma^k."""
    u, g, w = build_uv(k, d)
    e = d - k
    ge = ppow(g, e)
    # closed forms
    cf_q = pscal(psub(pscal(ppow(u, k), k + 1), pscal(pmul(ppow(u, d), ge), d + 1)), Fr(1, e))
    cf_p = pscal(psub(pscal(ppow(u, k + 1), k), pscal(pmul(ppow(u, d + 1), ge), d)),
                 Fr(1, (k + 1) * e))
    # honest q(w), Q(w), p(w) as polynomials in w
    qw = padd(pscal(ppow(w, k), Fr(k + 1, e)), pscal(ppow(w, d), Fr(-(d + 1), e)))
    Qw = padd(pscal(ppow(w, k + 1), Fr(1, e)), pscal(ppow(w, d + 1), Fr(-1, e)))
    pw_num = psub(pmul(w, qw), Qw)                     # = (k+1) p(w)
    if psub(pmul(cf_q, ppow(g, k)), qw):
        return False
    if psub(pscal(pmul(cf_p, ppow(g, k + 1)), k + 1), pw_num):
        return False
    return True


@gate
def fibre_identity_ok(F, k, d, tamper=False):
    """(Y Z^k) W - Q(W) - (k+1) (X Z^{k+1}) == 0 identically, W = u*gamma."""
    _u, _g, w = build_uv(k, d)
    if tamper:
        w = padd(w, pconst(1))
    X, Y, Z = F
    e = d - k
    QW = padd(pscal(ppow(w, k + 1), Fr(1, e)), pscal(ppow(w, d + 1), Fr(-1, e)))
    lhs = pmul(pmul(Y, ppow(Z, k)), w)
    lhs = psub(lhs, QW)
    lhs = psub(lhs, pscal(pmul(X, ppow(Z, k + 1)), k + 1))
    return not lhs


PAPER_WITNESS = "F(1,0,0) = F(-1,0,2) = (0,0,1), stated for k and d both odd"


def paper_witness_holds(F):
    """DOES the report's one stated witness hold for this member?  Measured on
    every member of the grid, not assumed on the parity class -- this boolean is
    what the scoping correction is counted from, so it must be a measurement."""
    q = QRing()
    a = image(F, (Fr(1), Fr(0), Fr(0)), q)
    b = image(F, (Fr(-1), Fr(0), Fr(2)), q)
    return a == b and a == (Fr(0), Fr(0), Fr(1))


def paper_witness_coverage(members):
    """COUNT the members on which the paper's witness was observed to hold."""
    return sum(1 for r in members if r["paper_witness_holds"])


@gate
def coverage_ok(members, claimed):
    """THE gate for the scoping correction: `claimed` must equal the counted
    coverage.  Without it, `holds_on_members` was a free restatement -- setting
    it to len(members) would have republished the paper's 6-member witness as
    covering all 27 and erased our own negative finding under a green replay."""
    counted = paper_witness_coverage(members)
    if counted != claimed:
        return False, ("counted %d members where the paper's witness holds, claim says %d"
                       % (counted, claimed))
    return True, "ok"


def ring_from_name(name):
    """Rebuild the coefficient ring from the name the receipt records."""
    if name == "Q":
        return QRing()
    if isinstance(name, str) and name.startswith("Q(zeta_") and name.endswith(")"):
        try:
            r = int(name[len("Q(zeta_"):-1])
        except ValueError:
            return None
        return CycRing(r) if r in (3, 5) else None
    return None


def parse_element(ring, s):
    """Inverse of ring.key(): turn a recorded coordinate back into a ring element."""
    if not isinstance(s, str):
        return None
    try:
        if isinstance(ring, QRing):
            return Fr(s)
        if not (s.startswith("[") and s.endswith("]")):
            return None
        parts = s[1:-1].split(",")
        if len(parts) != ring.n:
            return None
        return tuple(Fr(p) for p in parts)
    except (ValueError, ZeroDivisionError):
        return None


def recorded_collision_ok(rec, F):
    """Re-check the collision the receipt RECORDS, by reading it back.

    The pair was checked when it was derived, but the receipt carries strings,
    and strings nothing reads can say anything.  So the points are parsed out of
    the record and put back through check_collision, and the recorded image is
    re-evaluated from the parsed p1.
    """
    col = rec.get("collision")
    if not isinstance(col, dict):
        return False, "no collision record"
    if col.get("mechanism") not in {"sign", "root-of-unity", "two-root"}:
        return False, "unknown collision mechanism"
    ring = ring_from_name(col.get("field"))
    if ring is None:
        return False, "collision field is not a ring this verifier can rebuild"
    pts = []
    for key in ("p1", "p2"):
        raw = col.get(key)
        if not (isinstance(raw, list) and len(raw) == 3):
            return False, "%s is malformed" % key
        parsed = [parse_element(ring, s) for s in raw]
        if any(p is None for p in parsed):
            return False, "%s does not parse over %s" % (key, ring.name)
        pts.append(tuple(parsed))
    good, why = check_collision(F, ring, pts[0], pts[1])
    if not good:
        return False, "the recorded collision pair does not collide -- %s" % why
    if col.get("image") != [ring.key(c) for c in image(F, pts[0], ring)]:
        return False, "the recorded collision image is not F(p1)"
    return True, "ok"


MEMBER_RECORD_KEYS = frozenset([
    "k", "d", "monomials", "det", "source_grading", "component_weights",
    "generic_degree", "generic_degree_provenance", "etale_target_VT",
    "paper_witness_holds", "collision",
])
# `prior_art` is the one conditional key: present exactly when k == 1.

GENERIC_DEGREE_PROVENANCE = (
    "counted: k * #distinct roots of G at (V,T)=(1,0), not restated from k(d+1)")


@gate
def member_record_ok(rec):
    """THE per-member record gate, and the free-restatement sweep.

    Every claim-bearing field of a member record is RE-DERIVED here from that
    record's own (k, d) and compared with what the receipt will carry.  The
    point is coverage, not novelty: a field that is written into the record but
    read by no gate can be edited to anything and republished under a green
    replay -- that is how the generic degree and the torus weights were both
    broken.

    That failure mode arrived TWICE as an ordinary added field, so the first
    thing this gate checks is the KEY SET, not any value.  An enumerated sweep
    (control C15) can only mutate fields someone remembered to list; it cannot
    notice a field added later.  Pinning the key set is what makes "a field
    added later and left unchecked is rejected" a fact about the code rather
    than a hope about the author -- adding `novelty_status` to a record now
    fails here, by name, before any value is examined.
    """
    if not isinstance(rec, dict):
        return False, "member record is not an object"
    k, d = rec.get("k"), rec.get("d")
    if not (isinstance(k, int) and isinstance(d, int) and 1 <= k < d):
        return False, "recorded (k,d) is not a valid grid label"
    expected_keys = set(MEMBER_RECORD_KEYS) | ({"prior_art"} if k == 1 else set())
    if set(rec) != expected_keys:
        unknown = sorted(set(rec) - expected_keys)
        missing = sorted(expected_keys - set(rec))
        return False, (
            "member record key set is not the pinned one -- unknown field(s) %s, "
            "missing field(s) %s.  Every published field must be re-derived by "
            "this gate; a field no gate reads can be edited to anything and "
            "republished under a green replay." % (unknown, missing))
    F = build_family(k, d)
    if F is None:
        return False, "no polynomial family at the recorded (k,d)"
    if rec.get("monomials") != [len(F[0]), len(F[1]), len(F[2])]:
        return False, "monomials disagree with the family at the recorded (k,d)"
    if rec.get("det") != str(Fr(-k, k + 1)):
        return False, "det disagrees with -k/(k+1) at the recorded k"
    if rec.get("source_grading") != list(source_grading(k)):
        return False, "source_grading is not the grading of the recorded k"
    if not weights_ok(F, k, grading=tuple(rec["source_grading"]),
                      recorded=rec.get("component_weights")):
        return False, "component_weights disagree with the measurement"
    vt = rec.get("etale_target_VT")
    if not (isinstance(vt, list) and len(vt) == 2):
        return False, "etale_target_VT is malformed"
    if not generic_degree_ok(k, d, Fr(vt[0]), Fr(vt[1]), rec.get("generic_degree"))[0]:
        return False, "generic_degree disagrees with the count at the recorded target"
    if rec.get("paper_witness_holds") is not paper_witness_holds(F):
        return False, "paper_witness_holds disagrees with the exact evaluation"
    # Two prose fields.  Their CONTENT is claim-bearing even though no number
    # depends on it: `generic_degree_provenance` is the sentence that says the
    # degree was counted rather than restated -- the exact defect this lane was
    # audited for -- and `prior_art` is a statement about a named third party's
    # priority.  Checking only that the key exists would let either be rewritten
    # to its opposite under a green replay.
    if rec.get("generic_degree_provenance") != GENERIC_DEGREE_PROVENANCE:
        return False, ("generic_degree_provenance is not the pinned sentence; it "
                       "asserts how the degree was obtained and cannot be free text")
    if k == 1 and not (
            isinstance(rec.get("prior_art"), str)
            and "OUR READING" in rec["prior_art"]
            and "Gallagher" in rec["prior_art"]):
        return False, ("the k=1 prior-art marking must name Gallagher and mark the "
                       "reading as OURS, not the report's")
    good, why = recorded_collision_ok(rec, F)
    if not good:
        return False, why
    return True, "ok"


RECEIPT_TOP_LEVEL_KEYS = frozenset([
    "schema", "claim_owner", "claim_owner_note", "our_contribution", "certified",
    "not_certified", "cannot_defend_against", "scoping_correction", "prior_art",
    "grid", "members", "collisions_over_Q", "collisions_over_cyclotomic",
    "controls_registered", "controls_note",
])


@gate
def receipt_totals_ok(receipt):
    """THE totals gate: every count at the top of the receipt must be
    re-derivable from the member records that same receipt carries.  Same
    reason as member_record_ok -- a summary number nothing reads is a number
    anyone can edit.  Control C16 mutates each of them in turn.

    As in member_record_ok, the KEY SET is pinned first: an enumerated sweep
    cannot see a total added after the sweep was written.
    """
    if not isinstance(receipt, dict):
        return False, "receipt is not an object"
    if set(receipt) != set(RECEIPT_TOP_LEVEL_KEYS):
        unknown = sorted(set(receipt) - set(RECEIPT_TOP_LEVEL_KEYS))
        missing = sorted(set(RECEIPT_TOP_LEVEL_KEYS) - set(receipt))
        return False, (
            "receipt top-level key set is not the pinned one -- unknown %s, "
            "missing %s" % (unknown, missing))
    m = receipt.get("members") or []
    checks = {
        "collisions_over_Q": sum(1 for r in m if r["collision"]["field"] == "Q"),
        "collisions_over_cyclotomic": sum(1 for r in m if r["collision"]["field"] != "Q"),
        "controls_registered": len(CONTROL_REGISTRY),
    }
    for key, want in checks.items():
        if receipt.get(key) != want:
            return False, "%s: receipt says %r, re-derived %r" % (key, receipt.get(key), want)
    ks = sorted({r["k"] for r in m})
    ds = sorted({r["d"] for r in m})
    if receipt.get("grid") != {"k_min": min(ks), "k_max": max(ks),
                               "d_max": max(ds), "members": len(m)}:
        return False, "grid bounds do not match the member records"
    if receipt.get("prior_art", {}).get("members_affected") != sum(
            1 for r in m if "prior_art" in r):
        return False, "prior_art.members_affected does not match the member records"
    sc = receipt.get("scoping_correction", {})
    if sc.get("grid_members") != len(m):
        return False, "scoping_correction.grid_members does not match the member records"
    if not coverage_ok(m, sc.get("holds_on_members"))[0]:
        return False, "scoping_correction.holds_on_members does not match the count"
    return True, "ok"


@gate
def receipt_matches(text, blob):
    """THE receipt gate: the committed witness.json must be byte-identical to the
    freshly recomputed serialisation.  main()'s default path calls it with the
    committed file's bytes; control C11 calls this same function with a mutated
    copy.  (It used to be an `==` written inside C11, which tested the control's
    own comparison rather than the gate.)"""
    return text == blob


def verify_member(k, d):
    rec = {"k": k, "d": d}
    F = build_family(k, d)
    if F is None:
        raise AssertionError("(%d,%d): alpha/beta not divisible by the x-powers" % (k, d))
    F1, F2, F3 = F
    rec["monomials"] = [len(F1), len(F2), len(F3)]

    want = Fr(-k, k + 1)
    if not det_ok(F, want):
        raise AssertionError("(%d,%d): det JF is not the constant %s" % (k, d, want))
    rec["det"] = str(want)

    # MEASURED, then gated THROUGH THE RECORDED VALUES.  `weights` used to be
    # the literal [1, -k, -k-1] with no gate reading it, so mutating it to
    # [1, -k, -k-2] published wrong torus weights for all 27 members under a
    # fully green replay.  Both fields below are now handed back to the gate.
    grading = source_grading(k)
    rec["source_grading"] = list(grading)
    rec["component_weights"] = component_weights(F, grading)
    if not weights_ok(F, k, grading=tuple(rec["source_grading"]),
                      recorded=rec["component_weights"]):
        raise AssertionError("(%d,%d): torus weights (1,-k,-k-1) violated" % (k, d))

    if not gamma_cancellation_ok(k, d):
        raise AssertionError("(%d,%d): gamma-cancellation identity failed" % (k, d))

    if not fibre_identity_ok(F, k, d):
        raise AssertionError("(%d,%d): fibre identity failed" % (k, d))

    tgt = find_etale_target(k, d)
    if tgt is None:
        raise AssertionError("(%d,%d): no etale rational target found" % (k, d))
    V0, T0 = tgt
    # COUNTED from the fibre polynomial the etale gate just measured -- never
    # restated from the paper's formula.  Then gated against that same count, so
    # a mutated number here is rejected (control C12).  It is also compared with
    # the paper's k(d+1), but see the comment on that branch: the comparison is
    # unreachable, and it is not a falsification test.
    counted = fibre_point_count(k, d, V0, T0)
    if counted is None:
        raise AssertionError("(%d,%d): fibre point count refused a non-etale target" % (k, d))
    rec["generic_degree"] = counted
    good, why = generic_degree_ok(k, d, V0, T0, rec["generic_degree"])
    if not good:
        raise AssertionError("(%d,%d): generic-degree gate rejected the recorded number -- %s"
                             % (k, d, why))
    # A CONSISTENCY CHECK, AND IT CANNOT FIRE.  fibre_is_etale has already
    # forced deg G = d+1 and gcd(G, G') constant, so whenever `counted` is not
    # None it is identically k*(d+1).  The branch is kept because it is the
    # sentence a reader expects to see enforced, but it is unreachable, and this
    # leg therefore does NOT falsify the paper's formula -- do not say that it
    # does.  What is real here is the gate above: the recorded number must equal
    # what was counted (control C12).
    if rec["generic_degree"] != k * (d + 1):
        raise AssertionError(
            "(%d,%d): counted %d fibre points, but the paper claims k(d+1) = %d"
            % (k, d, rec["generic_degree"], k * (d + 1)))
    rec["generic_degree_provenance"] = (
        "counted: k * #distinct roots of G at (V,T)=(%s,%s), not restated from k(d+1)"
        % (V0, T0))
    rec["etale_target_VT"] = [str(V0), str(T0)]

    col = pick_collision(k, d)
    if col is None:
        raise AssertionError("(%d,%d): no collision construction applies" % (k, d))
    ring, P1, P2, kind = col
    good, why = check_collision(F, ring, P1, P2)
    if not good:
        raise AssertionError("(%d,%d): claimed collision rejected -- %s" % (k, d, why))
    i1 = image(F, P1, ring)
    rec["collision"] = {
        "mechanism": kind,
        "field": ring.name,
        "p1": [ring.key(c) for c in P1],
        "p2": [ring.key(c) for c in P2],
        "image": [ring.key(c) for c in i1],
    }

    # The paper's own stated witness, MEASURED on every member -- not only where
    # its parity hypothesis applies.  The scoping correction is counted from
    # this boolean, so it has to be a measurement on all 27, and where the
    # parity hypothesis does apply the paper's claim must hold.
    rec["paper_witness_holds"] = paper_witness_holds(F)
    if k % 2 and d % 2 and not rec["paper_witness_holds"]:
        raise AssertionError("(%d,%d): paper's (1,0,0)/(-1,0,2) witness failed" % (k, d))

    # Prior art, machine-readable and per member, and labelled as OUR reading.
    # A green line for a k = 1 member must carry that qualification with it, not
    # leave it in a README section the transcript's reader never opens.
    if k == 1:
        rec["prior_art"] = PRIOR_ART_K1

    # The sweep: every claim-bearing field of the record just built is handed
    # back to a gate that re-derives it.  Nothing published per member is a free
    # restatement.
    good, why = member_record_ok(rec)
    if not good:
        raise AssertionError("(%d,%d): the member record failed its own re-derivation -- %s"
                             % (k, d, why))
    return rec


# --------------------------------------------------------------------------
# 9.  Planted failures.  Each MUST be rejected.  A checker that cannot fail
#     certifies nothing, so these are the load-bearing part of this file.
#
#     Each control is a function that performs one corruption, hands it to ONE
#     named gate, and returns that gate's own verdict.  The harness -- not the
#     control -- decides what the verdict means: an ACCEPTED corruption aborts
#     the run, and only an observed rejection increments the count that gets
#     printed.  The count is therefore measured on this run rather than
#     asserted as a constant.  (It used to be `N_CONTROLS = 12` printed
#     unconditionally; a controls() that did nothing and returned 12 would have
#     printed "12/12 rejected".)
#
#     The harness additionally checks that each control's named gate appears in
#     the set of gates the DEFAULT verification path actually called on this
#     run (see section 0).  That is what "load-bearing" is allowed to mean here
#     and nothing more; in particular it does not prove that the control's
#     rejection came from that gate rather than from some other line inside the
#     control.  Read the controls -- they are twenty lines each.
# --------------------------------------------------------------------------


def c1_alpha_perturbed(_blob):
    """F1 += x*y at (k,d)=(2,3): the Jacobian determinant stops being constant."""
    k, d = 2, 3
    alpha, beta, g = build_alpha_beta(k, d)
    bad_alpha = padd(alpha, {(k + 2, 1, 0): Fr(1)})
    Fb = (pdiv_x(bad_alpha, k + 1), pdiv_x(beta, k), pmul(pvar(0), g))
    accepted = det_ok(Fb, Fr(-k, k + 1))
    return accepted, ("F1 + x*y at (k,d)=(2,3) -- det JF is no longer the constant "
                      "-k/(k+1)")


def c2_gamma_coefficient(_blob):
    """gamma with coefficient 1 in place of (d+k)/d: polynomiality dies."""
    accepted = build_family(2, 3, c_v=Fr(1)) is not None
    return accepted, ("gamma with coefficient 1 instead of (d+k)/d -- alpha is not "
                      "divisible by x^{k+1}")


def c3_determinant_claim(_blob):
    """Mutate the CLAIMED determinant and put it through the gate the default path
    runs, on every member of the grid."""
    survivors = [(k, d) for (k, d) in GRID if det_ok(build_family(k, d), Fr(-k, k + 2))]
    return bool(survivors), ("claimed determinant mutated -k/(k+1) -> -k/(k+2) -- rejected "
                             "on all %d grid members%s"
                             % (len(GRID), "" if not survivors else
                                " EXCEPT %s" % (survivors[:3],)))


def c4_collision_partner(_blob):
    """Break a collision point by one unit and run it through the real gate."""
    F = build_family(3, 5)
    good, why = check_collision(F, QRing(), (Fr(1), Fr(0), Fr(0)), (Fr(-1), Fr(0), Fr(3)))
    return good, ("collision partner (-1,0,2) -> (-1,0,3) at (k,d)=(3,5) -- %s" % why)


def c5_wrong_weight_monomial(_blob):
    """A monomial of the wrong torus weight in F1."""
    F = build_family(2, 3)
    Fw = (padd(F[0], {(0, 0, 0): Fr(1)}), F[1], F[2])
    return weights_ok(Fw, 2), ("constant monomial added to F1 at (k,d)=(2,3) -- torus "
                               "weight -(k+1) violated")


def c6_corrupt_anchor(_blob):
    """Corrupt the paper's printed expansion and feed it to the anchor gate the
    default path itself calls."""
    bad_F1 = dict(PAPER_23[0])
    bad_F1[(3, 3, 0)] = Fr(7)                         # true value 20/3
    return anchor_ok((bad_F1, PAPER_23[1], PAPER_23[2])), (
        "one coefficient of the paper's printed F1 at (2,3) flipped 20/3 -> 7 -- anchor "
        "mismatch")


def c7_non_etale_target(_blob):
    """A target whose fibre is not etale (planted double root of G)."""
    k, d, w0 = 2, 5, Fr(2)
    Qp = uQ(k, d)
    Vbad = sum((Qp[i] * i * w0 ** (i - 1) for i in range(1, len(Qp))), Fr(0))   # Q'(w0)
    Qw0 = sum((Qp[i] * w0 ** i for i in range(len(Qp))), Fr(0))
    Tbad = (Vbad * w0 - Qw0) / Fr(k + 1)
    good, why = fibre_is_etale(k, d, Vbad, Tbad)
    return good, ("planted double root of the fibre equation at (k,d)=(2,5) -- %s" % why)


def c8_cyclotomic_partner(_blob):
    """The cyclotomic evaluation path must also be able to say no."""
    k, d = 3, 4
    ring, P1, P2, _kind = collision_root_of_unity(k, d)
    F = build_family(k, d)
    P2bad = (P2[0], ring.add(P2[1], ring.one), P2[2])          # y2 -> y2 + 1
    good, why = check_collision(F, ring, P1, P2bad)
    return good, ("Q(zeta_3) collision partner shifted by y -> y+1 at (k,d)=(3,4) -- %s" % why)


def c9_degenerate_zeta(_blob):
    """zeta = 1 satisfies zeta^k = 1 but produces the SAME point twice.  Equal
    images then prove nothing, and the distinctness gate -- not the image gate --
    must be what rejects it."""
    k, d = 3, 4
    ring = CycRing(3)
    F = build_family(k, d)
    P1, P2deg = root_of_unity_pair(k, d, ring, e=0)          # e=0 => zeta = 1
    if not all(ring.eq(a, b) for a, b in zip(image(F, P1, ring), image(F, P2deg, ring))):
        # The trap only exists if the images really do agree; otherwise this
        # control would be passing for the wrong reason.
        raise AssertionError("CONTROL C9 SETUP BROKEN: zeta=1 was expected to give equal images")
    good, why = check_collision(F, ring, P1, P2deg)
    return good, ("zeta = 1 at (k,d)=(3,4) -- images agree but the points are equal, so the "
                  "distinctness gate fires (%s)" % why)


def c10_tampered_fibre_identity(_blob):
    """Replace W = u*gamma by W + 1 in the fibre identity."""
    return fibre_identity_ok(build_family(4, 6), 4, 6, tamper=True), (
        "fibre identity with W := u*gamma + 1 at (k,d)=(4,6) -- identity fails")


def c11_mutated_receipt(blob):
    """Feed a mutated copy of the COMMITTED receipt to receipt_matches -- the same
    function main()'s default path calls with the real bytes."""
    if not RECEIPT.exists():
        # No committed receipt to mutate.  Report NOT RUN rather than scoring a
        # rejection that never happened; the default path exits nonzero in this
        # state anyway (only --emit writes a receipt).
        return None, "no committed receipt to mutate; run --emit first"
    text = RECEIPT.read_text()
    if not receipt_matches(text, blob):
        # The committed receipt already disagrees with the recomputation, so a
        # rejection here would be caused by the pre-existing disagreement and
        # not by the mutation.  That is not a control; say NOT RUN.
        return None, ("the committed receipt already disagrees with the recomputation, so this "
                      "control cannot isolate the mutation")
    mutated = text.replace('"det": "-1/2"', '"det": "-1/3"', 1)
    if mutated == text:
        raise AssertionError("CONTROL C11 SETUP BROKEN: no det field found in the receipt")
    return receipt_matches(mutated, blob), (
        "committed witness.json with one det field mutated -1/2 -> -1/3 -- fails the byte "
        "comparison the default path runs")


def c12_generic_degree_claim(_blob):
    """Mutate the CLAIMED generic degree, on every member, through the gate the
    default path runs on the number it records."""
    survivors, setup_broken = [], []
    for (k, d) in GRID:
        tgt = find_etale_target(k, d)
        if tgt is None:
            raise AssertionError("CONTROL C12 SETUP BROKEN: no etale target at (%d,%d)" % (k, d))
        V0, T0 = tgt
        if generic_degree_ok(k, d, V0, T0, k * (d + 2))[0]:
            survivors.append((k, d))
        # The trap only exists if the gate ACCEPTS the counted truth; a gate
        # that rejected everything would pass this control for the wrong reason.
        if not generic_degree_ok(k, d, V0, T0, fibre_point_count(k, d, V0, T0))[0]:
            setup_broken.append((k, d))
    if setup_broken:
        raise AssertionError("CONTROL C12 SETUP BROKEN: the gate rejects its own count at %s"
                             % (setup_broken[:3],))
    return bool(survivors), ("claimed generic degree mutated k(d+1) -> k(d+2) -- rejected on "
                             "all %d grid members by counting the fibre, and the gate still "
                             "accepts the counted value" % len(GRID))


def c13_mutated_grading(_blob):
    """Mutate the SOURCE GRADING that the receipt records, on every member.

    The receipt's torus weights used to be the literal [1, -k, -k-1], read by
    nothing: an edit to [1, -k, -k-2] published wrong weights for all 27 members
    under a green replay.  Now the recorded grading is the one handed to the
    measurement, so mutating it makes the components non-isobaric and the gate
    refuses.
    """
    survivors = [(k, d) for (k, d) in GRID
                 if weights_ok(build_family(k, d), k, grading=(1, -k, -(k + 2)))]
    return bool(survivors), ("source grading mutated (1,-k,-k-1) -> (1,-k,-k-2) -- rejected "
                             "on all %d grid members; no component is isobaric for it"
                             % len(GRID))


def c14_scoping_coverage_claim(_blob):
    """Mutate the CLAIMED coverage of the paper's own witness to the whole grid.

    `holds_on_members` used to be a free restatement; setting it to len(members)
    would have republished the paper's 6-member witness as covering all 27 and
    deleted our own negative finding while the replay stayed green.
    """
    members = [{"paper_witness_holds": paper_witness_holds(build_family(k, d))}
               for (k, d) in GRID]
    counted = paper_witness_coverage(members)
    if not coverage_ok(members, counted)[0]:
        raise AssertionError("CONTROL C14 SETUP BROKEN: the gate rejects its own count")
    good, why = coverage_ok(members, len(members))
    return good, ("claimed coverage of the paper's stated witness mutated %d -> %d (the whole "
                  "grid) -- %s" % (counted, len(members), why))


MEMBER_FIELD_MUTATIONS = [
    ("k", 1),
    ("d", 8),
    ("monomials", [0, 0, 0]),
    ("det", "-1/3"),
    ("source_grading", [1, -2, -4]),
    ("component_weights", [-3, -2, 2]),
    ("generic_degree", 99),
    ("etale_target_VT", ["0", "0"]),
    ("paper_witness_holds", True),
]


def c15_member_record_sweep(_blob):
    """THE free-restatement sweep, as a control.  Mutate every claim-bearing
    field of a member record in turn and require member_record_ok to reject each
    one.  A field that is published but read by nothing survives this control
    and fails it by name -- which is exactly how the generic degree and the
    torus weights should have been caught the first time."""
    rec = verify_member(2, 3)
    if not member_record_ok(rec)[0]:
        raise AssertionError("CONTROL C15 SETUP BROKEN: the gate rejects an untouched record")
    cases = []
    for key, bad in MEMBER_FIELD_MUTATIONS:
        if rec.get(key) == bad:
            raise AssertionError("CONTROL C15 SETUP BROKEN: %r is already the mutated value" % key)
        mutated = dict(rec)
        mutated[key] = bad
        cases.append((key, mutated))
    # The collision block is a nested record of strings; mutate it too.
    for label, patch in [
            ("collision.p2", {"p2": rec["collision"]["p1"]}),           # same point twice
            ("collision.image", {"image": ["0", "0", "0"]}),
            ("collision.field", {"field": "Q(zeta_7)"}),
            ("collision.mechanism", {"mechanism": "handwave"})]:
        mutated = dict(rec)
        mutated["collision"] = dict(rec["collision"], **patch)
        cases.append((label, mutated))
    # The two prose fields, whose CONTENT is claim-bearing.
    cases.append(("generic_degree_provenance",
                  dict(rec, generic_degree_provenance="restated verbatim from k(d+1)")))
    # THE MUTANT THE ENUMERATED SWEEP COULD NOT SEE.  An audit added
    # rec["novelty_status"] = "NEW WITH THIS PAPER; no prior art anywhere",
    # re-emitted, and replayed fully green -- because a sweep can only mutate
    # fields someone listed.  The key-set pin in member_record_ok is what
    # rejects it, and this case is what proves the pin is wired.
    cases.append(("<field added later>",
                  dict(rec, novelty_status="NEW WITH THIS PAPER; no prior art anywhere")))
    survivors = [label for label, m in cases if member_record_ok(m)[0]]
    return bool(survivors), ("each of the %d claim-bearing fields of the (k,d)=(2,3) member "
                             "record mutated in turn -- %s"
                             % (len(cases),
                                "all rejected" if not survivors else
                                "SURVIVED: %s" % (survivors,)))


RECEIPT_TOTAL_MUTATIONS = [
    ("collisions_over_Q", 27),
    ("collisions_over_cyclotomic", 0),
    ("controls_registered", 99),
    ("grid", {"k_min": 1, "k_max": 7, "d_max": 9, "members": 27}),
]


def c16_receipt_totals_sweep(_blob):
    """Same sweep for the receipt's top-level counts, including the two nested
    ones (prior_art.members_affected and scoping_correction.*)."""
    members = [verify_member(k, d) for (k, d) in GRID]
    base = {
        "members": members,
        "collisions_over_Q": sum(1 for r in members if r["collision"]["field"] == "Q"),
        "collisions_over_cyclotomic": sum(1 for r in members if r["collision"]["field"] != "Q"),
        "controls_registered": len(CONTROL_REGISTRY),
        "grid": {"k_min": 1, "k_max": 6, "d_max": 8, "members": len(members)},
        "prior_art": {"members_affected": sum(1 for r in members if "prior_art" in r)},
        "scoping_correction": {"grid_members": len(members),
                               "holds_on_members": paper_witness_coverage(members)},
    }
    # receipt_totals_ok pins the top-level key set, so the control must build a
    # COMPLETE receipt shape.  The prose/meta keys carry no number this gate
    # re-derives, so placeholders are honest here -- the point of the sweep is
    # the counts.
    for key in RECEIPT_TOP_LEVEL_KEYS:
        base.setdefault(key, None)
    if not receipt_totals_ok(base)[0]:
        raise AssertionError("CONTROL C16 SETUP BROKEN: the gate rejects an untouched receipt")
    survivors = []
    for key, bad in RECEIPT_TOTAL_MUTATIONS:
        mutated = dict(base)
        mutated[key] = bad
        if receipt_totals_ok(mutated)[0]:
            survivors.append(key)
    for outer, inner, bad in [("prior_art", "members_affected", 27),
                              ("scoping_correction", "grid_members", 6),
                              ("scoping_correction", "holds_on_members", 27)]:
        mutated = dict(base)
        mutated[outer] = dict(base[outer])
        mutated[outer][inner] = bad
        if receipt_totals_ok(mutated)[0]:
            survivors.append("%s.%s" % (outer, inner))
    # The total the enumerated sweep could not see (audit probe B2).
    if receipt_totals_ok(dict(base, members_independently_reproduced=27))[0]:
        survivors.append("<total added later>")
    n = len(RECEIPT_TOTAL_MUTATIONS) + 4
    return bool(survivors), ("each of the %d top-level receipt counts mutated in turn -- %s"
                             % (n, "all rejected" if not survivors else
                                "SURVIVED: %s" % (survivors,)))


# id, the gate the control is scored against, the control itself.
CONTROL_REGISTRY = [
    ("C1", "det_ok", c1_alpha_perturbed),
    ("C2", "build_family", c2_gamma_coefficient),
    ("C3", "det_ok", c3_determinant_claim),
    ("C4", "check_collision", c4_collision_partner),
    ("C5", "weights_ok", c5_wrong_weight_monomial),
    ("C6", "anchor_ok", c6_corrupt_anchor),
    ("C7", "fibre_is_etale", c7_non_etale_target),
    ("C8", "check_collision", c8_cyclotomic_partner),
    ("C9", "check_collision", c9_degenerate_zeta),
    ("C10", "fibre_identity_ok", c10_tampered_fibre_identity),
    ("C11", "receipt_matches", c11_mutated_receipt),
    ("C12", "generic_degree_ok", c12_generic_degree_claim),
    ("C13", "weights_ok", c13_mutated_grading),
    ("C14", "coverage_ok", c14_scoping_coverage_claim),
    ("C15", "member_record_ok", c15_member_record_sweep),
    ("C16", "receipt_totals_ok", c16_receipt_totals_sweep),
]


def controls(out, blob, default_gates):
    """Run every registered control.

    Returns (rejected, registered, in_default_path, skipped).
    `rejected` counts corruptions this run OBSERVED a gate refuse -- a control
    returning None was not runnable and is counted as skipped, never as a
    rejection.  `in_default_path` counts controls whose named gate is in
    `default_gates`, the set of gates the default verification path called.
    """
    rejected, in_default_path, skipped = 0, 0, 0
    for cid, gate_name, fn in CONTROL_REGISTRY:
        accepted, note = fn(blob)
        if accepted is None:
            skipped += 1
            out.append("[!!] %-3s NOT RUN (%s): %s" % (cid, gate_name, note))
            continue
        if accepted:
            raise AssertionError("CONTROL %s NOT REJECTED by %s: %s" % (cid, gate_name, note))
        rejected += 1
        if gate_name in default_gates:
            in_default_path += 1
            mark = ""
        else:
            mark = "   <-- NOT run by the default path"
        out.append("[ok] %-3s rejected by %s: %s%s" % (cid, gate_name, note, mark))
    return rejected, len(CONTROL_REGISTRY), in_default_path, skipped


# --------------------------------------------------------------------------
# 10.  Driver.
# --------------------------------------------------------------------------

def cyclotomic_self_test():
    """Q[T]/Phi_r(T) is in the trust path for the 5 members whose only witness is
    cyclotomic, so check the ring before trusting anything computed in it."""
    for r in (3, 5):
        R = CycRing(r)
        z = R.zeta_pow(1)
        acc = R.one
        powers = []
        for _ in range(r):
            powers.append(acc)
            acc = R.mul(acc, z)
        if not R.eq(acc, R.one):
            return False, "zeta^%d != 1 in Q(zeta_%d)" % (r, r)
        s = R.zero
        for p in powers:
            s = R.add(s, p)
        if not R.eq(s, R.zero):                      # 1 + zeta + ... + zeta^{r-1} = 0
            return False, "Phi_%d(zeta) != 0" % r
        for i in range(1, r):
            if R.eq(powers[i], R.one):
                return False, "zeta has order < %d" % r
            if not R.eq(R.mul(powers[i], R.zeta_pow(-i)), R.one):
                return False, "zeta^-%d is not the inverse of zeta^%d" % (i, i)
    return True, "ok"


def run():
    lines = []
    lines.append("Power-weighted-lift Keller family F_{k,d} : A^3 -> A^3")
    lines.append("  claimed by Annie (AGNT Labs, Technical Report III, v1.0, 21 July 2026),")
    lines.append("  \"Power-Weighted Lifts: Explicit Higher-Weight Noninjective Keller Maps in")
    lines.append("  Three Variables\".  That is the document's whole byline.  The construction is")
    lines.append("  the author's; this replay is ours, and it is a REIMPLEMENTATION FROM THE")
    lines.append("  REPORT'S PROSE, not a replay of its receipts (its independent_reproduction.md")
    lines.append("  is hash-bound to the wrong document).")
    lines.append("  PRIOR ART -- OUR READING, NOT THE REPORT'S WORDS: the report says Gallagher's")
    lines.append("  public notes describe a one-variable weighted-lift mechanism in the k=1 row,")
    lines.append("  and separately that historical priority outside the searched public record is")
    lines.append("  not asserted.  We read that as: the 7 k=1 members below are not new with this")
    lines.append("  paper.  Their lines are marked.  Prior-art holder, per the report's own")
    lines.append("  bibliography: " + GALLAGHER.split(" (the citation")[0] + ".")
    lines.append("  Novelty and priority are certified by nobody here -- not by them, not by us.")
    lines.append("")

    # anchor: our rebuild must reproduce the paper's own printed (2,3) expansion
    if not anchor_ok(PAPER_23):
        raise AssertionError("rebuild does not match the paper's printed (k,d)=(2,3) expansion")
    good, why = cyclotomic_self_test()
    if not good:
        raise AssertionError("cyclotomic ring self-test failed: %s" % why)
    lines.append("[ok] ring self-test: Q(zeta_3), Q(zeta_5) -- zeta^r = 1, Phi_r(zeta) = 0,")
    lines.append("            zeta has exact order r, and zeta^-i inverts zeta^i")
    lines.append("")
    lines.append("[ok] anchor: rebuild reproduces the paper's printed degree-8 case (k,d)=(2,3)")
    lines.append("            F1 = x^8y^4z + 5x^7y^5/3 + 4x^6y^3z + 17x^5y^4/3 + 6x^4y^2z")
    lines.append("                 + 20x^3y^3/3 + 4x^2yz + 8xy^2/3 + z   (and F2, F3) -- exact match")
    lines.append("")

    members = []
    rational, cyclotomic, prior_art = 0, 0, 0
    for (k, d) in GRID:
        rec = verify_member(k, d)
        members.append(rec)
        if rec["collision"]["field"] == "Q":
            rational += 1
        else:
            cyclotomic += 1
        if "prior_art" in rec:
            prior_art += 1
        lines.append(
            "[ok] k=%d d=%d  polynomial(%3d,%3d,%2d monomials)  det=%-6s  weights(%d,%d,%d)"
            "  generic degree %2d (counted)  collision/%s over %s%s"
            % (k, d, rec["monomials"][0], rec["monomials"][1], rec["monomials"][2],
               rec["det"], rec["component_weights"][0], rec["component_weights"][1],
               rec["component_weights"][2], rec["generic_degree"],
               rec["collision"]["mechanism"], rec["collision"]["field"],
               "   <-- PRIOR ART on OUR reading (Gallagher)" if k == 1 else ""))

    # The scoping correction is COUNTED from the per-member measurement; the
    # number the receipt carries is gated below, once the receipt exists.
    paper_wit = paper_witness_coverage(members)

    lines.append("")
    lines.append("[ok] all %d grid members (1<=k<=6, k<d<=8) are genuinely polynomial:" % len(members))
    lines.append("     alpha is divisible by x^{k+1} and beta by x^k, exactly, in Q[x,y,z]")
    lines.append("[ok] det J F_{k,d} == -k/(k+1) as a polynomial identity in Q[x,y,z]")
    lines.append("     (coefficient-by-coefficient on the expanded 3x3 cofactor determinant --")
    lines.append("      not sampled at points, and no float anywhere)")
    lines.append("[ok] torus weights: under the source grading deg(x,y,z) = (1,-k,-k-1), every")
    lines.append("     monomial of F1,F2,F3 is isobaric of weight -(k+1), -k, 1 -- MEASURED per")
    lines.append("     component and recorded as measured (controls C5, C13)")
    lines.append("[ok] fibre identity (Y Z^k) W - Q(W) - (k+1)(X Z^{k+1}) == 0 identically")
    lines.append("[ok] generic degree: COUNTED, not restated.  At an exhibited rational target the")
    lines.append("     fibre equation G(w) = Q(w) - V w + (k+1) T is squarefree and no root of it")
    lines.append("     forces gamma = 0 (two exact gcd tests over Q), so the fibre has exactly")
    lines.append("     k * #{distinct roots of G} = k * deg(G/gcd(G,G')) points.  THAT PRODUCT is")
    lines.append("     what each line above and the receipt record, and control C12 mutates the")
    lines.append("     recorded claim to k(d+2) on all 27 members for the same gate to reject.")
    lines.append("     HONEST LIMIT: the count is also compared with the paper's k(d+1), but the")
    lines.append("     etale gate has already forced deg G = d+1 and gcd(G,G') constant, so that")
    lines.append("     comparison is unreachable.  This leg does not falsify the paper's formula;")
    lines.append("     what it does is stop the recorded number from being a free restatement.")
    lines.append("[ok] non-injectivity: explicit colliding pairs -- %d of %d over Q, %d over a"
                 % (rational, len(members), cyclotomic))
    lines.append("     cyclotomic field Q(zeta_r); every pair checked by exact evaluation")
    lines.append("")
    lines.append("[!!] SCOPING CORRECTION (ours, and negative): the paper states one witness,")
    lines.append("     F(1,0,0) = F(-1,0,2) = (0,0,1), for k and d both odd.  It holds -- we")
    lines.append("     confirm it exactly -- but it was evaluated on all %d members and holds on"
                 % len(members))
    lines.append("     only %d of them.  The other %d needed witnesses we derived ourselves (sign,"
                 % (paper_wit, len(members) - paper_wit))
    lines.append("     root-of-unity, two-root); the paper's witness does not cover its own grid.")
    lines.append("     (Counted, then gated: control C14 mutates the count to %d and it is"
                 % len(members))
    lines.append("     rejected.)")
    lines.append("[!!] PRIOR ART, ON OUR READING: %d of the %d members (the k=1 row) look to us"
                 % (prior_art, len(members)))
    lines.append("     to lie inside Gallagher's earlier one-variable weighted-lift work -- they")
    lines.append("     are verified here, but not new with this paper.  The report does not use")
    lines.append("     the words 'prior art'; the inference is ours, and it is recorded as ours.")
    lines.append("     We do not date or adjudicate the overlap, and certify no novelty anywhere.")
    lines.append("")

    ks = sorted({r["k"] for r in members})
    ds = sorted({r["d"] for r in members})
    receipt = {
        "schema": "keller-power-weighted-lifts-v3",
        "claim_owner": "Annie (AGNT Labs, Technical Report III, v1.0, 21 July 2026)",
        "claim_owner_note": ("the report's byline names one author; it is \"Power-Weighted "
                             "Lifts: Explicit Higher-Weight Noninjective Keller Maps in Three "
                             "Variables\", (c) 2026 AGNT Labs"),
        "our_contribution": ("independent exact replay only; the construction is not ours, and "
                             "this is a reimplementation from the report's prose, NOT a replay of "
                             "the author's receipts (the report's independent_reproduction.md is "
                             "hash-bound to the wrong document)"),
        "grid": {"k_min": min(ks), "k_max": max(ks), "d_max": max(ds), "members": len(members)},
        "certified": [
            "each F_{k,d} is a polynomial map A^3 -> A^3 (exact x-divisibility)",
            "det J F_{k,d} == -k/(k+1) as a polynomial identity in Q[x,y,z]",
            ("each component is isobaric under the source grading deg(x,y,z) = (1,-k,-k-1), of "
             "measured weights (-(k+1), -k, 1)"),
            ("generic fibre point count, COUNTED as k * #distinct roots of the fibre "
             "equation at an exhibited etale target (exact gcd conditions); it comes out "
             "k(d+1) on every member"),
            "F_{k,d} is not injective (explicit exhibited colliding pair)",
            "our rebuild reproduces the paper's printed (k,d)=(2,3) expansion exactly",
        ],
        "not_certified": [
            "novelty and priority -- not checked at all",
            ("the k=1 row (%d of %d members) is prior art ON OUR READING of the report; see "
             "prior_art" % (prior_art, len(members))),
            "reproduction of the author's own receipts (none intact to replay)",
            "anything outside the published 27-member grid",
            ("that the counted generic degree could have disagreed with k(d+1): the etale gate "
             "forces deg G = d+1, so that comparison is unreachable and is not a test of the "
             "paper's formula"),
        ],
        "prior_art": {
            "row": "k = " + ", ".join(str(k) for k in sorted(
                {r["k"] for r in members if "prior_art" in r})),
            "members_affected": prior_art,
            "whose_inference": ("OURS.  The report does not say 'prior art' or name the k=1 row "
                                "as someone else's; we read its sentences that way, and the "
                                "reading errs toward de-claiming."),
            "report_says": PAPER_PRIOR_ART_QUOTE,
            "our_reading": PRIOR_ART_K1,
            "prior_art_holder": GALLAGHER,
        },
        "scoping_correction": {
            "paper_witness": PAPER_WITNESS,
            "holds_on_members": paper_wit,
            "holds_on_members_provenance": (
                "counted by evaluating the report's witness exactly on all %d members, then "
                "gated by coverage_ok; control C14 mutates the count to %d and it is rejected"
                % (len(members), len(members))),
            "grid_members": len(members),
            "finding": ("the paper's stated witness covers %d of %d members, not all of them; "
                        "witnesses for the remaining %d are ours (sign / root-of-unity / "
                        "two-root) and each is checked by exact evaluation"
                        % (paper_wit, len(members), len(members) - paper_wit)),
        },
        "collisions_over_Q": rational,
        "collisions_over_cyclotomic": cyclotomic,
        "controls_registered": len(CONTROL_REGISTRY),
        "controls_note": (
            "each registered control performs one corruption, hands it to ONE named gate, and "
            "returns that gate's verdict; the harness aborts the run if the corruption is "
            "accepted and counts only rejections it observed, so the printed count is measured "
            "on the run rather than asserted.  The run also checks that each control's named "
            "gate is in the set of gates the default verification path actually called.  It "
            "does NOT establish that the rejection came from that gate and nowhere else -- "
            "that is a source-level property, for a reader to check by reading."),
        "cannot_defend_against": (
            "an edit to verify.py itself.  Stub a gate, no-op the control harness, or hardcode "
            "a number in the verdict path and this file will happily print PASS -- no verifier "
            "can check its own source.  What defends that boundary is outside the file: the "
            "sha256 of verify.py and witness.json pinned in certificates/contracts.json, the "
            "git history of both, and review.  Corrupted DATA is what the checks above are for; "
            "a corrupted VERIFIER is what the pin is for."),
        "members": members,
    }
    # Gate the receipt's OWN numbers, not the local variables they came from:
    # every top-level count must be re-derivable from the member records the
    # same file carries (controls C14, C16).
    good, why = coverage_ok(members, receipt["scoping_correction"]["holds_on_members"])
    if not good:
        raise AssertionError("scoping-correction gate rejected the recorded coverage -- %s" % why)
    good, why = receipt_totals_ok(receipt)
    if not good:
        raise AssertionError("receipt totals gate rejected the assembled receipt -- %s" % why)

    blob = json.dumps(receipt, indent=2, sort_keys=True) + "\n"

    # The receipt gate runs HERE, on the default path, so that the control
    # tracing below can see it -- and so C11 is scored against the same function.
    receipt_exists = RECEIPT.exists()
    receipt_ok = receipt_matches(RECEIPT.read_text() if receipt_exists else "", blob)

    default_gates = frozenset(GATE_CALLS)
    n_rej, n_reg, n_load, n_skip = controls(lines, blob, default_gates)
    if n_rej + n_skip != n_reg:
        raise AssertionError("control harness lost a control: %d rejected + %d skipped != %d "
                             "registered" % (n_rej, n_skip, n_reg))
    lines.append("")
    lines.append("planted-failure controls: %d registered, %d run, %d observed rejected by the "
                 "named gate" % (n_reg, n_reg - n_skip, n_rej))
    lines.append("     %d/%d of those named gates were called by the default verification path"
                 % (n_load, n_reg - n_skip))
    lines.append("     on this same run (measured by call tracing, see section 0).  That is the")
    lines.append("     whole of what 'load-bearing' means here: it does not prove the rejection")
    lines.append("     came from that gate rather than from another line inside the control.")
    lines.append("")
    lines.append("[!] WHAT THIS VERIFIER CANNOT DEFEND AGAINST: an edit to verify.py.  Stub a")
    lines.append("    gate, no-op the harness, hardcode a verdict -- this file will print PASS.")
    lines.append("    No verifier can check its own source.  The defence is the sha256 of")
    lines.append("    verify.py and witness.json pinned in certificates/contracts.json, plus the")
    lines.append("    git history and review.  The checks above are for corrupted DATA; the pin")
    lines.append("    is for a corrupted VERIFIER.")
    if n_load != n_reg - n_skip:
        raise AssertionError("%d control(s) that ran are scored against a gate the default path "
                             "never called" % (n_reg - n_skip - n_load))
    return receipt, blob, lines, receipt_ok, receipt_exists, n_rej


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--emit", action="store_true",
                    help="rewrite witness.json (never happens on a normal run)")
    args = ap.parse_args()

    try:
        receipt, blob, lines, receipt_ok, receipt_exists, n_rej = run()
    except AssertionError as exc:
        print("FAIL: %s" % exc)
        return 1

    for ln in lines:
        print(ln)

    if args.emit:
        RECEIPT.write_text(blob)
        print("")
        print("receipt-emitted: %s" % RECEIPT.name)
        print("PASS -- emitted (this path is not the certificate)")
        return 0

    if not receipt_exists:
        print("")
        print("FAIL: receipt %s is missing; run with --emit to create it" % RECEIPT.name)
        return 1
    if not receipt_ok:
        print("")
        print("FAIL: recomputed result disagrees with the committed %s" % RECEIPT.name)
        return 1
    print("")
    print("receipt-checked: %s" % RECEIPT.name)
    print("PASS -- %d/%d grid members verified, %d/%d planted failures rejected, receipt matches"
          % (len(receipt["members"]), len(GRID), n_rej, len(CONTROL_REGISTRY)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Independent exact replay of the power-weighted-lift Keller family F_{k,d} : A^3 -> A^3.

THE FAMILY IS NOT OURS.  It is claimed by Nathan Wilbanks and "Annie" (AGNT Labs
Technical Report III, v1.0, 2026-07-21), "Power-Weighted Lifts: Explicit
Higher-Weight Noninjective Keller Maps".  What is ours is only this replay: a
from-scratch reimplementation of their Section 3 recipe in exact rational
arithmetic, plus the checks and the planted failures below.

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


def fibre_is_etale(k, d, V, T):
    G = fibre_poly(k, d, V, T)
    if len(G) != d + 2:
        return False, "deg G != d+1"
    if not is_constant(ugcd(G, uderiv(G))):
        return False, "G not squarefree"
    if not is_constant(ugcd(G, usub(umono(Fr(V), 0), uq(k, d)))):
        return False, "some root of G has gamma = 0"
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

def weights_ok(F, k):
    want = (-(k + 1), -k, 1)
    for f, wt in zip(F, want):
        for (a, b, c) in f:
            if a - k * b - (k + 1) * c != wt:
                return False
    return True


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


def verify_member(k, d):
    rec = {"k": k, "d": d}
    F = build_family(k, d)
    if F is None:
        raise AssertionError("(%d,%d): alpha/beta not divisible by the x-powers" % (k, d))
    F1, F2, F3 = F
    rec["monomials"] = [len(F1), len(F2), len(F3)]

    det = pjacdet(F)
    want = Fr(-k, k + 1)
    if det != pconst(want):
        raise AssertionError("(%d,%d): det JF is not the constant %s" % (k, d, want))
    rec["det"] = str(want)

    if not weights_ok(F, k):
        raise AssertionError("(%d,%d): torus weights (1,-k,-k-1) violated" % (k, d))
    rec["weights"] = [1, -k, -k - 1]

    if not gamma_cancellation_ok(k, d):
        raise AssertionError("(%d,%d): gamma-cancellation identity failed" % (k, d))

    if not fibre_identity_ok(F, k, d):
        raise AssertionError("(%d,%d): fibre identity failed" % (k, d))

    tgt = find_etale_target(k, d)
    if tgt is None:
        raise AssertionError("(%d,%d): no etale rational target found" % (k, d))
    V0, T0 = tgt
    rec["generic_degree"] = k * (d + 1)
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

    # The paper's own stated witness, where its parity hypothesis applies.
    if k % 2 and d % 2:
        q = QRing()
        a = image(F, (Fr(1), Fr(0), Fr(0)), q)
        b = image(F, (Fr(-1), Fr(0), Fr(2)), q)
        if a != b or a != (Fr(0), Fr(0), Fr(1)):
            raise AssertionError("(%d,%d): paper's (1,0,0)/(-1,0,2) witness failed" % (k, d))
        rec["paper_witness_odd_odd"] = "F(1,0,0) = F(-1,0,2) = (0,0,1)"
    return rec


# --------------------------------------------------------------------------
# 9.  Planted failures.  Each MUST be rejected.  A checker that cannot fail
#     certifies nothing, so these are the load-bearing part of this file.
# --------------------------------------------------------------------------

N_CONTROLS = 11


def controls(out, blob):
    ok = []

    # C1 -- perturb one coefficient of alpha: the determinant stops being constant.
    k, d = 2, 3
    alpha, beta, g = build_alpha_beta(k, d)
    bad_alpha = padd(alpha, {(k + 2, 1, 0): Fr(1)})       # F1 += x*y
    Fb = (pdiv_x(bad_alpha, k + 1), pdiv_x(beta, k), pmul(pvar(0), g))
    if pjacdet(Fb) == pconst(Fr(-k, k + 1)):
        raise AssertionError("CONTROL C1 NOT REJECTED: perturbed alpha still gave det = -k/(k+1)")
    ok.append("[ok] rejected: F1 + x*y at (k,d)=(2,3) -- det JF is no longer the constant -k/(k+1)")

    # C2 -- wrong coefficient on v inside gamma: polynomiality dies.
    if build_family(2, 3, c_v=Fr(1)) is not None:
        raise AssertionError("CONTROL C2 NOT REJECTED: gamma with c_v=1 still divided out")
    ok.append("[ok] rejected: gamma with coefficient 1 instead of (d+k)/d -- alpha is not divisible by x^{k+1}")

    # C3 -- assert the wrong determinant value.
    F = build_family(3, 5)
    if pjacdet(F) == pconst(Fr(-3, 5)):
        raise AssertionError("CONTROL C3 NOT REJECTED: det JF matched the wrong value -k/(k+2)")
    ok.append("[ok] rejected: claimed det = -k/(k+2) at (k,d)=(3,5) -- true value is -3/4")

    # C4 -- break a collision point by one unit.
    q = QRing()
    F = build_family(3, 5)
    a = image(F, (Fr(1), Fr(0), Fr(0)), q)
    b = image(F, (Fr(-1), Fr(0), Fr(3)), q)          # paper's z=2 moved to 3
    if a == b:
        raise AssertionError("CONTROL C4 NOT REJECTED: perturbed point still collided")
    ok.append("[ok] rejected: collision partner (-1,0,2) -> (-1,0,3) at (k,d)=(3,5) -- images differ")

    # C5 -- a monomial of the wrong torus weight.
    F = build_family(2, 3)
    Fw = (padd(F[0], {(0, 0, 0): Fr(1)}), F[1], F[2])
    if weights_ok(Fw, 2):
        raise AssertionError("CONTROL C5 NOT REJECTED: weight gate accepted a weight-0 monomial in F1")
    ok.append("[ok] rejected: constant monomial added to F1 at (k,d)=(2,3) -- torus weight -(k+1) violated")

    # C6 -- corrupt the paper's printed expansion we anchor against.
    bad = dict(PAPER_23[0])
    bad[(3, 3, 0)] = Fr(7)                            # true value 20/3
    if bad == build_family(2, 3)[0]:
        raise AssertionError("CONTROL C6 NOT REJECTED: corrupted anchor still matched")
    ok.append("[ok] rejected: one coefficient of the paper's printed F1 at (2,3) flipped to 7 -- anchor mismatch")

    # C7 -- a target whose fibre is not etale (planted double root of G).
    k, d, w0 = 2, 5, Fr(2)
    Qp = uQ(k, d)
    Vbad = sum((Qp[i] * i * w0 ** (i - 1) for i in range(1, len(Qp))), Fr(0))   # Q'(w0)
    Qw0 = sum((Qp[i] * w0 ** i for i in range(len(Qp))), Fr(0))
    Tbad = (Vbad * w0 - Qw0) / Fr(k + 1)
    good, why = fibre_is_etale(k, d, Vbad, Tbad)
    if good:
        raise AssertionError("CONTROL C7 NOT REJECTED: planted double root passed the etale gate")
    ok.append("[ok] rejected: planted double root of the fibre equation at (k,d)=(2,5) -- %s" % why)

    # C8 -- the cyclotomic evaluation path must also be able to say "no".
    k, d = 3, 4
    ring, P1, P2, _kind = collision_root_of_unity(k, d)
    F = build_family(k, d)
    P2bad = (P2[0], ring.add(P2[1], ring.one), P2[2])          # y2 -> y2 + 1
    if all(ring.eq(a, b) for a, b in zip(image(F, P1, ring), image(F, P2bad, ring))):
        raise AssertionError("CONTROL C8 NOT REJECTED: perturbed Q(zeta_3) partner still collided")
    ok.append("[ok] rejected: Q(zeta_3) collision partner shifted by y -> y+1 at (k,d)=(3,4) -- images differ")

    # C9 -- the degenerate choice zeta = 1 satisfies zeta^k = 1 but produces the
    #       SAME point twice.  Equal images then prove nothing, and the
    #       distinctness gate -- not the image gate -- must be what rejects it.
    k, d = 3, 4
    ring = CycRing(3)
    F = build_family(k, d)
    P1, P2deg = root_of_unity_pair(k, d, ring, e=0)          # e=0 => zeta = 1
    good, why = check_collision(F, ring, P1, P2deg)
    if good:
        raise AssertionError("CONTROL C9 NOT REJECTED: zeta=1 accepted as a non-injectivity witness")
    if not all(ring.eq(a, b) for a, b in zip(image(F, P1, ring), image(F, P2deg, ring))):
        # The trap only exists if the images really do agree; otherwise this
        # control would be passing for the wrong reason.
        raise AssertionError("CONTROL C9 SETUP BROKEN: zeta=1 was expected to give equal images")
    ok.append("[ok] rejected: zeta = 1 at (k,d)=(3,4) -- images agree but the points are equal, "
              "so the distinctness gate fires (%s)" % why)

    # C10 -- tamper the fibre identity's W.
    if fibre_identity_ok(build_family(4, 6), 4, 6, tamper=True):
        raise AssertionError("CONTROL C10 NOT REJECTED: fibre identity held with W replaced by W+1")
    ok.append("[ok] rejected: fibre identity with W := u*gamma + 1 at (k,d)=(4,6) -- identity fails")

    # C11 -- run the mutated committed receipt through the SAME comparison the
    #        default path performs against the freshly recomputed blob.
    if RECEIPT.exists():
        text = RECEIPT.read_text()
        mutated = text.replace('"det": "-1/2"', '"det": "-1/3"', 1)
        if mutated == text:
            raise AssertionError("CONTROL C11 SETUP BROKEN: no det field found in the receipt")
        if mutated == blob:                     # `!=` here is the default path's gate
            raise AssertionError("CONTROL C11 NOT REJECTED: mutated receipt matched the recomputation")
        ok.append("[ok] rejected: committed witness.json with one det field mutated -1/2 -> -1/3 "
                  "-- fails the byte comparison the default path runs")
    else:
        ok.append("[ok] rejected: (receipt absent; the default path exits nonzero rather than "
                  "writing one -- only --emit writes)")

    out.extend(ok)
    return len(ok)


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
    lines.append("  claimed by Nathan Wilbanks and \"Annie\" (AGNT Labs Technical Report III,")
    lines.append("  v1.0, 2026-07-21).  The construction is theirs; this replay is ours.")
    lines.append("")

    # anchor: our rebuild must reproduce the paper's own printed (2,3) expansion
    F23 = build_family(2, 3)
    if F23 is None or tuple(F23) != PAPER_23:
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
    rational, cyclotomic, paper_wit = 0, 0, 0
    for (k, d) in GRID:
        rec = verify_member(k, d)
        members.append(rec)
        if rec["collision"]["field"] == "Q":
            rational += 1
        else:
            cyclotomic += 1
        if "paper_witness_odd_odd" in rec:
            paper_wit += 1
        lines.append(
            "[ok] k=%d d=%d  polynomial(%3d,%3d,%2d monomials)  det=%-6s  weights(1,%d,%d)"
            "  generic degree %2d  collision/%s over %s"
            % (k, d, rec["monomials"][0], rec["monomials"][1], rec["monomials"][2],
               rec["det"], -k, -k - 1, rec["generic_degree"],
               rec["collision"]["mechanism"], rec["collision"]["field"]))
    lines.append("")
    lines.append("[ok] all %d grid members (1<=k<=6, k<d<=8) are genuinely polynomial:" % len(members))
    lines.append("     alpha is divisible by x^{k+1} and beta by x^k, exactly, in Q[x,y,z]")
    lines.append("[ok] det J F_{k,d} == -k/(k+1) as a polynomial identity in Q[x,y,z]")
    lines.append("     (coefficient-by-coefficient on the expanded 3x3 cofactor determinant --")
    lines.append("      not sampled at points, and no float anywhere)")
    lines.append("[ok] source torus weights (1,-k,-k-1): every monomial of F1,F2,F3 is isobaric")
    lines.append("[ok] fibre identity (Y Z^k) W - Q(W) - (k+1)(X Z^{k+1}) == 0 identically")
    lines.append("[ok] generic degree k(d+1): at an exhibited rational target the fibre equation")
    lines.append("     G(w) = Q(w) - V w + (k+1) T has degree d+1, is squarefree, and no root of")
    lines.append("     it forces gamma = 0 -- two exact gcd tests over Q (they coincide here,")
    lines.append("     since Q'(w) = q(w) makes 'gamma = 0 at a root' the same as 'double root')")
    lines.append("[ok] non-injectivity: explicit colliding pairs -- %d of %d over Q, %d over a"
                 % (rational, len(members), cyclotomic))
    lines.append("     cyclotomic field Q(zeta_r); every pair checked by exact evaluation")
    lines.append("[ok] the paper's own witness F(1,0,0) = F(-1,0,2) = (0,0,1) holds on all %d"
                 % paper_wit)
    lines.append("     members with k and d both odd (the parity case it is stated for)")
    lines.append("")

    receipt = {
        "schema": "keller-power-weighted-lifts-v1",
        "claim_owner": "Nathan Wilbanks and \"Annie\" (AGNT Labs Technical Report III v1.0, 2026-07-21)",
        "our_contribution": "independent exact replay only; the construction is not ours",
        "grid": {"k_min": 1, "k_max": 6, "d_max": 8, "members": len(members)},
        "certified": [
            "each F_{k,d} is a polynomial map A^3 -> A^3 (exact x-divisibility)",
            "det J F_{k,d} == -k/(k+1) as a polynomial identity in Q[x,y,z]",
            "source torus weights (1,-k,-k-1)",
            "generic fibre has exactly k(d+1) points (exact gcd conditions)",
            "F_{k,d} is not injective (explicit exhibited colliding pair)",
            "our rebuild reproduces the paper's printed (k,d)=(2,3) expansion exactly",
        ],
        "collisions_over_Q": rational,
        "collisions_over_cyclotomic": cyclotomic,
        "controls": N_CONTROLS,
        "members": members,
    }
    blob = json.dumps(receipt, indent=2, sort_keys=True) + "\n"

    n_ctrl = controls(lines, blob)
    if n_ctrl != N_CONTROLS:
        raise AssertionError("expected %d planted-failure controls, ran %d" % (N_CONTROLS, n_ctrl))
    lines.append("")
    lines.append("planted-failure controls: %d/%d rejected as required" % (n_ctrl, N_CONTROLS))
    return receipt, blob, lines


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--emit", action="store_true",
                    help="rewrite witness.json (never happens on a normal run)")
    args = ap.parse_args()

    try:
        receipt, blob, lines = run()
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

    if not RECEIPT.exists():
        print("")
        print("FAIL: receipt %s is missing; run with --emit to create it" % RECEIPT.name)
        return 1
    if RECEIPT.read_text() != blob:
        print("")
        print("FAIL: recomputed result disagrees with the committed %s" % RECEIPT.name)
        return 1
    print("")
    print("receipt-checked: %s" % RECEIPT.name)
    print("PASS -- %d/%d grid members verified, %d planted failures rejected, receipt matches"
          % (len(receipt["members"]), len(GRID), receipt["controls"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

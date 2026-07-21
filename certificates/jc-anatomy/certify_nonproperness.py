#!/usr/bin/env python3
"""Certify the JELONEK NON-PROPERNESS SET of Alpoge's dim-3 Keller counterexample.

CLAIM TYPING. The map F is ALPOGE's (with Claude Fable assistance); we verify
and derive, we do not discover the root. Everything below is CONDITIONAL on
the certified root claim (certificates/jacobian-conjecture/verify.py: det JF
== -2 identically, F non-injective; atlas/jc-crater/geometric_degree.py:
[C(x,y,z) : C(f1,f2,f3)] = 3). The non-properness computation itself is new
(round 3); its machine content is this script.

THE MAP  F : C^3 -> C^3

  f1 = (1+xy)^3 z + y^2 (1+xy)(4+3xy)
  f2 = y + 3x(1+xy)^2 z + 3xy^2 (4+3xy)
  f3 = 2x - 3x^2 y - x^3 z

THE RESULT.  Let t1,t2,t3 be target coordinates and set

  E(t) := 27 t1^2 t3^2 - 18 t1 t2 t3 + 16 t1 + t2^3 t3 - t2^2.

Then the Jelonek set (asymptotic set / set of points at which F is not proper)

  S_F  =  V(E),

a quartic hypersurface. Equivalently: F is a proper
(hence, being etale, an unbranched 3-sheeted covering) map exactly over the
complement of V(E); over V(E) at least one of the three preimages has escaped
to infinity. Only the x-coordinate can escape: y and z satisfy monic-up-to-
constant equations over C[t] (leading coefficients 2 and 8), while AN
ANNIHILATOR of x has leading coefficient E(t).

NOT CLAIMED (and not needed): that E is irreducible over Q, and that Phi_x is
the MINIMAL annihilator of x. Both were only PROBED with a CAS during
discovery; neither has a stdlib replay path here, so both are demoted to
CAS-level discovery notes. Irreducibility is dodged on purpose -- the density
step (I5) is stated per irreducible component precisely so that it never needs
to know what the components are. Minimality is likewise unnecessary: every
argument below uses only that Phi_x ANNIHILATES x, which (I2) certifies as an
identity in Q[x,y,z].

DIVISION OF LABOR -- what the machine checks vs. what is standard prose.

Machine-checked below, in exact rational arithmetic (Fraction), stdlib only:

  (I1)  G1(F(p), y) == 0 identically in Q[x,y,z], where
        G1(t,Y) = 2Y^3 - 3t2 Y^2 + 18t1 Y + (27t1^2 t3 - 18t1 t2 + t2^3).
        => on EVERY fiber F^-1(t), the y-coordinate is a root of the cubic
        G1(t, .), whose leading coefficient is the constant 2.
  (I2)  Phi_x(F(p), x) == 0 identically, where
        Phi_x(t,X) = E(t) X^3 + (4 - 3 t2 t3) X - 2 t3.
        => on every fiber, x is a root of Phi_x(t, .); leading coeff E(t).
  (I3)  Phi_z(F(p), z) == 0 identically, where Phi_z(t,Z) = 8 Z^3 + c2(t) Z^2
        + c1(t) Z + c0(t) (coefficients in the code below).
        => on every fiber, z is a root of a cubic with leading coeff 8.
  (I4)  disc_Y(G1)  ==  -2916 t1^2 E(t)   identically in Q[t].
        => on V(E) the fiber cubic for y has a multiple root, i.e. at most 2
        distinct y-values occur on any fiber over V(E).
  (I5)  E|_{t3=0} = 16 t1 - t2^2 != 0  and  16A + 12 t2 B + 9 t2^2 C != 0
        (where E = A t3^2 + B t3 + C as a polynomial in t3, recomposition
        machine-checked) => t3 does not divide E and (4 - 3 t2 t3) does not
        divide E => no irreducible component of V(E) lies inside {t3 = 0} or
        {4 - 3 t2 t3 = 0}: the "good" locus used in (W1) is dense in V(E).
  (W1)  Witness fibers ON V(E):  t* = (-16/27, 0, 1),  t** = (-4/27, 0, 2),
        and (off the t2 = 0 slice)  t*** = (-1, 2, -2).
        At t*: E(t*) = 0; Phi_x(t*, X) == 4X - 2 exactly (the cubic term dies
        with E, so every fiber point has x = 1/2); G1(t*, Y) ==
        2(Y + 8/3)(Y - 4/3)^2 exactly (so y in {-8/3, 4/3}); z is then forced
        by f3 = t3 (x != 0): both candidate points are evaluated exactly, ONE
        hits, one misses:
             F(1/2, -8/3, 16) = t*   and   F(1/2, 4/3, -8) != t*.
        => #F^-1(t*) = 1 < 3.  Same structure at t** (fiber = {(1, -4/3, 4)})
        and at t*** (Phi_x == 16X + 4, x = -1/4; G1 == 2(Y-5)(Y+1)^2;
        fiber = {(-1/4, 5, -36)}).
  (W2)  Witness fiber OFF V(E): the collision target (-1/4, 0, 0) has
        E = -4 != 0 and its three certified rational preimages are re-checked:
        the fiber jump 3 -> 1 across V(E) is exhibited by exact points.
  (I6)  THE OMITTED CURVE (F is NOT surjective). On the punctured rational
        curve  gamma(s) = (s^2/12, s, 4/(3s)), s != 0,  BOTH non-leading
        structural coefficients of Phi_x vanish identically:
            E(gamma(s)) == 0   and   (4 - 3 t2 t3)(gamma(s)) == 0,
        (checked as exact Laurent-polynomial identities in s), while
        t3(gamma(s)) = 4/(3s) != 0. So for any p with F(p) = gamma(s),
        identity (I2) reads 0 = Phi_x(gamma(s), x(p)) = -8/(3s) != 0 --
        contradiction. Hence gamma(s) has NO preimage: im(F) misses the whole
        curve. (Together with (L3), C^3 minus V(E) is inside im(F); and gamma
        is precisely V(E) intersect {4 - 3 t2 t3 = 0}, since
        16A + 12t2B + 9t2^2C = 3(t2^2 - 12t1)^2 -- see (I6b). Observation,
        CAS-level, not needed for any claim: gamma is exactly the SINGULAR
        LOCUS of the quartic V(E).)
  (NC)  Negative controls: a perturbed Phi_x, a perturbed disc identity, a
        perturbed witness point, and a wrong cubic factorization must all FAIL.

Standard prose (the human steps, stated so nobody mistakes where the machine
stops; each is classical):

  (L1)  Root bound: if a_0 x^d + ... + a_d = 0 and |a_0| >= eps > 0 with all
        |a_j| <= M, then |x| <= 1 + M/eps. Hence if E(t*) != 0, then along any
        sequence p_k with F(p_k) -> t*, (I1)+(I2)+(I3) bound |y_k|, |x_k|,
        |z_k|; no sequence escapes; t* not in S_F.   =>   S_F is contained in V(E).
  (L2)  S_F := { t : exists p_k, |p_k| -> infinity, F(p_k) -> t } (Jelonek's
        asymptotic set) equals the set of points at which F is not proper
        (over no neighborhood of which F is proper) -- elementary compactness.
  (L3)  Etale covering count: det JF = -2 (certified) makes F an everywhere-
        local biholomorphism; a proper local homeomorphism onto an open ball
        is a covering map; the sheet number is constant and equals the generic
        fiber count 3 (certified field degree, char 0, etale => honest
        points). Hence if F were proper over a neighborhood of t, EVERY fiber
        near t would have exactly 3 points. Contrapositive: #F^-1(t*) <= 2
        => t* in S_F. (W1) exhibits fibers of size 1 on V(E); the generic-
        on-V(E) argument is (I2)+(I4): for t in V(E) with t3 != 0 and
        4 - 3 t2 t3 != 0, x is unique (Phi_x is linear: E = 0), y takes <= 2
        values (disc = 0 by (I4)), z is determined by f3 = t3 since
        x = 2t3/(4 - 3 t2 t3) != 0; so #fiber <= 2 and t is in S_F.
  (L4)  S_F is closed (diagonal argument on escaping sequences), and by (I5)
        no component of V(E) hides inside the two removed sets, so the locus
        covered by (L3) is dense in V(E) and its closure is all of V(E).
        =>   V(E) is contained in S_F.
  (L5)  disc = 0 with leading coeff != 0 => a multiple root, so <= 2 distinct
        roots (standard discriminant fact, used in (L3)).

(L1)-(L5) + (I1)-(I5) + (W1) give S_F = V(E). Context: this is exactly
Jelonek's leading-coefficient method (Z. Jelonek, "The set of points at which
a polynomial map is not proper", Ann. Polon. Math. 58 (1993) 259-266), but the
proof above is self-contained modulo classical facts -- the annihilators are
certified as identities, not imported from a CAS.

GEOMETRIC READING. For a PROPER 3:1 map the discriminant locus of the fiber
cubic would be the branch locus. Alpoge's map is etale -- branching is
forbidden -- so where the discriminant -2916 t1^2 E degenerates, the colliding
preimages must instead vanish to infinity (the E factor: true escape, 1 or 2
preimages left) or separate in a coordinate the cubic cannot see (the t1^2
factor: two fiber points share y but differ in x -- a false alarm, F stays
proper there; sample fiber over (0,1,2) in the round-3 findings). The
non-properness escape hatch predicted by keller_properness_universal
(BCW 1982: proper Keller => invertible) is here made exact: THE escape
hypersurface is the quartic V(E).

CHECK COUNT. This script runs exactly 18 machine checks:
  (I1,I2,I3) 3 + (I4) 1 + (I5a,I5b,I5c) 3 + (W1a,W1b,W1c) 3 + (I6a,I6b) 2
  + (W2) 1 + (NCa..NCe) 5  =  18.
The count is not prose: main() tallies every check() call and asserts the
total is EXPECTED_CHECKS, so the figure cannot drift from the code again.
(An earlier round-3 draft advertised "19 checks"; that was an off-by-one in
the write-up, never in the arithmetic.)

META-CONTROL (the constant 16 t1 in E, mutated to 17 t1). E appears in the
source TWICE and independently: in the definition of E, and again inside the
(I5a) recomposition E == A t3^2 + B t3 + C. All three mutations exit 1;
the failure profiles, MEASURED on this file (2026-07-20), are:

  mutation site                       #FAIL   which checks fail
  ---------------------------------   -----   -----------------------------
  BOTH (E definition + I5a copy)        8     I2 I4 W1a W1b W1c I6a I6b W2
  E definition only                     8     I2 I4 I5a W1a W1b W1c I6a W2
  I5a recomposition copy only           2     I5a I6b

Read it this way: mutating the definition breaks the annihilator identity
(I2), the discriminant identity (I4), all three witness fibers, the omitted
curve (I6a) and the off-V(E) fiber (W2) -- E is load-bearing everywhere.
Mutating only ONE of the two copies is caught by (I5a), which exists exactly
to pin the two transcriptions of E against each other. So no single-site edit
of E can slip through: either the identities catch it or (I5a) does.
(These are the numbers this file produces; an earlier round-3 draft reported
"10 legs fail", which does not reproduce -- the measured figure is 8.)

Exit 0 iff every machine check above holds.
"""
from fractions import Fraction as Q
import sys

# ---------------------------------------------------------------- poly engine
# Polynomials in Q[x, y, z, t1, t2, t3] as dicts {exponent 6-tuple: coeff},
# zero coefficients never stored -- the same monomial-dict convention as
# certificates/jacobian-conjecture/verify.py and atlas/jc-crater/
# geometric_degree.py, so all agree on what "exact" means.

NV = 6
VARNAMES = ("x", "y", "z", "t1", "t2", "t3")


def var(i):
    e = [0] * NV
    e[i] = 1
    return {tuple(e): Q(1)}


X, Y, Z, T1, T2, T3 = (var(i) for i in range(NV))


def const(c):
    c = Q(c)
    return {(0,) * NV: c} if c else {}


def add(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            s = out.get(m, Q(0)) + c
            if s:
                out[m] = s
            else:
                out.pop(m, None)
    return out


def smul(c, p):
    c = Q(c)
    return {m: c * v for m, v in p.items()} if c else {}


def mul(*ps):
    out = const(1)
    for p in ps:
        acc = {}
        for m1, c1 in out.items():
            for m2, c2 in p.items():
                m = tuple(a + b for a, b in zip(m1, m2))
                s = acc.get(m, Q(0)) + c1 * c2
                if s:
                    acc[m] = s
                else:
                    acc.pop(m, None)
        out = acc
    return out


def power(p, n):
    out = const(1)
    for _ in range(n):
        out = mul(out, p)
    return out


def subst(p, images):
    """Substitute images[i] for variable i, with cached powers (the identity
    checks raise images to exponents up to 9; recomputing powers per-term is
    the difference between seconds and minutes)."""
    cache = [{0: const(1)} for _ in range(NV)]

    def pw(i, e):
        c = cache[i]
        if e not in c:
            c[e] = mul(pw(i, e - 1), images[i])
        return c[e]

    out = {}
    for m, c in p.items():
        term = const(c)
        for i, e in enumerate(m):
            if e:
                term = mul(term, pw(i, e))
        out = add(out, term)
    return out


def peval(p, vals):
    """Exact evaluation at a rational 6-tuple."""
    tot = Q(0)
    for m, c in p.items():
        v = c
        for i, e in enumerate(m):
            if e:
                v *= vals[i] ** e
        tot += v
    return tot


# ------------------------------------------------------- the counterexample
ONE_PLUS_XY = add(const(1), mul(X, Y))
W4 = add(const(4), smul(3, mul(X, Y)))

F1 = add(mul(power(ONE_PLUS_XY, 3), Z), mul(power(Y, 2), ONE_PLUS_XY, W4))
F2 = add(Y, smul(3, mul(X, power(ONE_PLUS_XY, 2), Z)),
         smul(3, mul(X, power(Y, 2), W4)))
F3 = add(smul(2, X), smul(-3, mul(power(X, 2), Y)), smul(-1, mul(power(X, 3), Z)))

AT_F = [X, Y, Z, F1, F2, F3]  # t_i := f_i(x,y,z)


def F_direct(x, y, z):
    """Independent nested-expression evaluation path (never touches the
    polynomial engine), mirroring verify.py."""
    u = 1 + x * y
    return ((u ** 3) * z + y ** 2 * u * (4 + 3 * x * y),
            y + 3 * x * u ** 2 * z + 3 * x * y ** 2 * (4 + 3 * x * y),
            2 * x - 3 * x ** 2 * y - x ** 3 * z)


# ------------------------------------------------------------- the objects
# E(t): the non-properness hypersurface.
E = add(smul(27, mul(power(T1, 2), power(T3, 2))),
        smul(-18, mul(T1, T2, T3)),
        smul(16, T1),
        mul(power(T2, 3), T3),
        smul(-1, power(T2, 2)))

# G1: the fiber cubic for y (as certified in geometric_degree.py).
G1 = add(smul(2, power(Y, 3)),
         smul(-3, mul(T2, power(Y, 2))),
         smul(18, mul(T1, Y)),
         smul(27, mul(power(T1, 2), T3)),
         smul(-18, mul(T1, T2)),
         power(T2, 3))

# Phi_x: the annihilator of x. Leading coefficient E(t) -- the whole theorem
# hangs on this shape: the X^3 term dies exactly on V(E).
PHIX = add(mul(E, power(X, 3)),
           mul(add(const(4), smul(-3, mul(T2, T3))), X),
           smul(-2, T3))

# Phi_z: the annihilator of z. Leading coefficient 8, CONSTANT -- z never
# escapes. (Discovered as the primitive part of Res_y(G1, D*G3 - A*G2); the
# identity check (I3) below is what makes it trustworthy, not the CAS run.)
PHIZ_C2 = add(smul(324, mul(power(T1, 2), power(T3, 2))),
              smul(-216, mul(T1, T2, T3)),
              smul(408, T1),
              smul(-15, mul(power(T2, 3), T3)),
              smul(6, power(T2, 2)))
PHIZ_C1 = add(
    smul(4374, mul(power(T1, 4), power(T3, 4))),
    smul(-5832, mul(power(T1, 3), T2, power(T3, 3))),
    smul(11016, mul(power(T1, 3), power(T3, 2))),
    smul(324, mul(power(T1, 2), power(T2, 3), power(T3, 3))),
    smul(4050, mul(power(T1, 2), power(T2, 2), power(T3, 2))),
    smul(-7344, mul(power(T1, 2), T2, T3)),
    smul(4992, power(T1, 2)),
    smul(-216, mul(T1, power(T2, 4), power(T3, 2))),
    smul(-996, mul(T1, power(T2, 3), T3)),
    smul(1032, mul(T1, power(T2, 2))),
    smul(6, mul(power(T2, 6), power(T3, 2))),
    smul(78, mul(power(T2, 5), T3)),
    smul(-84, power(T2, 4)))
PHIZ_C0 = add(
    smul(19683, mul(power(T1, 6), power(T3, 6))),
    smul(-39366, mul(power(T1, 5), T2, power(T3, 5))),
    smul(74358, mul(power(T1, 5), power(T3, 4))),
    smul(2187, mul(power(T1, 4), power(T2, 3), power(T3, 5))),
    smul(24057, mul(power(T1, 4), power(T2, 2), power(T3, 4))),
    smul(-158193, mul(power(T1, 4), T2, power(T3, 3))),
    smul(28026, mul(power(T1, 4), power(T3, 2))),
    smul(-2916, mul(power(T1, 3), power(T2, 4), power(T3, 4))),
    smul(2592, mul(power(T1, 3), power(T2, 3), power(T3, 3))),
    smul(106272, mul(power(T1, 3), power(T2, 2), power(T3, 2))),
    smul(-53676, mul(power(T1, 3), T2, T3)),
    smul(-5408, power(T1, 3)),
    smul(81, mul(power(T1, 2), power(T2, 6), power(T3, 4))),
    smul(810, mul(power(T1, 2), power(T2, 5), power(T3, 3))),
    smul(-8937, mul(power(T1, 2), power(T2, 4), power(T3, 2))),
    smul(-19347, mul(power(T1, 2), power(T2, 3), T3)),
    smul(22290, mul(power(T1, 2), power(T2, 2))),
    smul(-54, mul(T1, power(T2, 7), power(T3, 3))),
    smul(210, mul(T1, power(T2, 6), power(T3, 2))),
    smul(2658, mul(T1, power(T2, 5), T3)),
    smul(-2652, mul(T1, power(T2, 4))),
    mul(power(T2, 9), power(T3, 3)),
    smul(-3, mul(power(T2, 8), power(T3, 2))),
    smul(-78, mul(power(T2, 7), T3)),
    smul(80, power(T2, 6)))
PHIZ = add(smul(8, power(Z, 3)), mul(PHIZ_C2, power(Z, 2)), mul(PHIZ_C1, Z),
           PHIZ_C0)


EXPECTED_CHECKS = 18  # see "CHECK COUNT" in the module docstring
_N_CHECKS = 0


def check(name, ok, note, detail=""):
    global _N_CHECKS
    _N_CHECKS += 1
    print(f"  [{'OK' if ok else 'FAIL'}] {name}: {note}")
    if not ok and detail:
        print(f"         {detail}")
    return ok


def main() -> int:
    print("Non-properness (Jelonek) set of Alpoge's dim-3 Keller counterexample")
    print("Claim: S_F = V(E),  E = 27t1^2t3^2 - 18t1t2t3 + 16t1 + t2^3t3 - t2^2\n")
    ok = True

    # ---- (I1)-(I3): annihilator identities ------------------------------
    for name, rel, note in (
        ("I1", G1, "y on any fiber satisfies the cubic G1(t,.)   [lc 2]"),
        ("I2", PHIX, "x on any fiber satisfies Phi_x(t,.)         [lc E(t)]"),
        ("I3", PHIZ, "z on any fiber satisfies Phi_z(t,.)         [lc 8]"),
    ):
        res = subst(rel, AT_F)
        ok &= check(name, not res, note,
                    f"residual has {len(res)} nonzero term(s); "
                    f"sample: {sorted(res.items())[:2]}")

    # ---- (I4): discriminant identity ------------------------------------
    a, b = const(2), smul(-3, T2)
    c, d = smul(18, T1), add(smul(27, mul(power(T1, 2), T3)),
                             smul(-18, mul(T1, T2)), power(T2, 3))
    disc = add(smul(18, mul(a, b, c, d)),
               smul(-4, mul(power(b, 3), d)),
               mul(power(b, 2), power(c, 2)),
               smul(-4, mul(a, power(c, 3))),
               smul(-27, mul(power(a, 2), power(d, 2))))
    ok &= check("I4", not add(disc, smul(2916, mul(power(T1, 2), E))),
                "disc_Y(G1) == -2916 t1^2 E  (multiple y-root exactly on "
                "V(t1) u V(E))")

    # ---- (I5): no component of V(E) inside the removed sets -------------
    A_ = smul(27, power(T1, 2))
    B_ = add(smul(-18, mul(T1, T2)), power(T2, 3))
    C_ = add(smul(16, T1), smul(-1, power(T2, 2)))
    recomp = add(mul(A_, power(T3, 2)), mul(B_, T3), C_)
    ok &= check("I5a", not add(recomp, smul(-1, E)),
                "E == A t3^2 + B t3 + C recomposition")
    e_t30 = subst(E, [X, Y, Z, T1, T2, const(0)])
    ok &= check("I5b", bool(e_t30),
                "E|_{t3=0} = 16t1 - t2^2 != 0   => t3 does not divide E")
    wit = add(smul(16, A_), smul(12, mul(T2, B_)), smul(9, mul(power(T2, 2), C_)))
    ok &= check("I5c", bool(wit),
                "16A + 12t2B + 9t2^2C = 432t1^2 - 72t1t2^2 + 3t2^4 != 0  "
                "=> (4 - 3t2t3) does not divide E")

    # ---- (W1): witness fibers ON V(E): fiber collapses to ONE point -----
    for tag, tstar, xstar, ylift, zlift, ydead, zdead, cubic_factored in (
        ("W1a", (Q(-16, 27), Q(0), Q(1)), Q(1, 2),
         Q(-8, 3), Q(16), Q(4, 3), Q(-8),
         smul(2, mul(add(Y, const(Q(8, 3))),
                     power(add(Y, const(Q(-4, 3))), 2)))),
        ("W1b", (Q(-4, 27), Q(0), Q(2)), Q(1),
         Q(-4, 3), Q(4), Q(2, 3), Q(-2),
         smul(2, mul(add(Y, const(Q(4, 3))),
                     power(add(Y, const(Q(-2, 3))), 2)))),
        ("W1c", (Q(-1), Q(2), Q(-2)), Q(-1, 4),
         Q(5), Q(-36), Q(-1), Q(-108),
         smul(2, mul(add(Y, const(Q(-5))),
                     power(add(Y, const(Q(1))), 2)))),
    ):
        t_imgs = [X, Y, Z, const(tstar[0]), const(tstar[1]), const(tstar[2])]
        vals6 = (Q(0), Q(0), Q(0)) + tstar  # for evaluating pure-t polys
        on_E = (peval(E, vals6) == 0)
        # Phi_x at t*: cubic term dies with E; must be exactly linear with
        # root xstar.
        phix_t = subst(PHIX, t_imgs)
        lin = add(smul(4 - 3 * tstar[1] * tstar[2], X),
                  const(-2 * tstar[2]))
        phix_lin = (not add(phix_t, smul(-1, lin))) and \
                   (peval(lin, (xstar, Q(0), Q(0), Q(0), Q(0), Q(0))) == 0)
        # G1 at t*: exactly the claimed factored cubic (double root ydead,
        # simple root ylift).
        g1_t = subst(G1, t_imgs)
        g1_fact = not add(g1_t, smul(-1, cubic_factored))
        # z forced by f3 = t3 at x = xstar (x != 0): z = (2x - 3x^2 y - t3)/x^3
        z_of = lambda yv: (2 * xstar - 3 * xstar ** 2 * yv - tstar[2]) / xstar ** 3
        z_forced = (z_of(ylift) == zlift) and (z_of(ydead) == zdead) and xstar != 0
        # the two candidate points: one hits t*, one misses -- both paths.
        p_hit = (xstar, ylift, zlift)
        p_dead = (xstar, ydead, zdead)
        img_hit_a = tuple(peval(f, p_hit + (Q(0),) * 3) for f in (F1, F2, F3))
        img_hit_b = F_direct(*p_hit)
        img_dead_a = tuple(peval(f, p_dead + (Q(0),) * 3) for f in (F1, F2, F3))
        img_dead_b = F_direct(*p_dead)
        hit = (img_hit_a == img_hit_b == tstar)
        dead = (img_dead_a == img_dead_b) and (img_dead_a != tstar)
        ok &= check(tag, on_E and phix_lin and g1_fact and z_forced and hit
                    and dead,
                    f"t*={tuple(map(str, tstar))} in V(E): x forced = {xstar}, "
                    f"y in {{{ydead}, {ylift}}}, z forced; fiber = "
                    f"{{{tuple(map(str, p_hit))}}} EXACTLY (size 1 < 3)",
                    f"on_E={on_E} phix_lin={phix_lin} g1_fact={g1_fact} "
                    f"z_forced={z_forced} hit={hit} dead={dead}")

    # ---- (I6): the omitted curve gamma(s) = (s^2/12, s, 4/(3s)) ---------
    def on_curve(p):
        """Exact Laurent evaluation of a pure-t polynomial along gamma(s):
        returns dict {s-exponent: coeff}. t1 -> s^2/12, t2 -> s, t3 -> 4/(3s)."""
        out = {}
        for m, cf in p.items():
            assert m[0] == m[1] == m[2] == 0, "not a pure-t polynomial"
            a, b, c = m[3], m[4], m[5]
            e = 2 * a + b - c
            v = cf * Q(1, 12) ** a * Q(4, 3) ** c
            sacc = out.get(e, Q(0)) + v
            if sacc:
                out[e] = sacc
            else:
                out.pop(e, None)
        return out

    FOURM = add(const(4), smul(-3, mul(T2, T3)))
    ok &= check("I6a", not on_curve(E) and not on_curve(FOURM),
                "E(gamma(s)) == 0 and (4-3t2t3)(gamma(s)) == 0 identically; "
                "with t3(gamma) = 4/(3s) != 0 and (I2): gamma has NO preimage "
                "=> F is NOT surjective")
    # gamma is exactly V(E) & {4-3t2t3=0}: the elimination witness is a square.
    sq = smul(3, power(add(power(T2, 2), smul(-12, T1)), 2))
    ok &= check("I6b", not add(wit, smul(-1, sq)),
                "16A + 12t2B + 9t2^2C == 3(t2^2 - 12t1)^2  (so V(E) & "
                "{4-3t2t3=0} = {t2^2 = 12t1, t3 = 4/(3t2)} = gamma)")

    # ---- (W2): witness fiber OFF V(E): full 3-point fiber ---------------
    target = (Q(-1, 4), Q(0), Q(0))
    e_at = peval(E, (Q(0), Q(0), Q(0)) + target)
    pts = [(Q(0), Q(0), Q(-1, 4)), (Q(1), Q(-3, 2), Q(13, 2)),
           (Q(-1), Q(3, 2), Q(13, 2))]
    full = (e_at == Q(-4)) and len(set(pts)) == 3 and all(
        tuple(peval(f, p + (Q(0),) * 3) for f in (F1, F2, F3)) == target
        and F_direct(*p) == target for p in pts)
    ok &= check("W2", full,
                "collision target (-1/4,0,0): E = -4 != 0, three exact "
                "preimages re-verified (proper side; fiber jump 3 -> 1)")

    # ---- (NC): negative controls ----------------------------------------
    bad_phix = add(PHIX, mul(T1, power(X, 2)))
    ok &= check("NCa", bool(subst(bad_phix, AT_F)),
                "perturbed Phi_x (+ t1 x^2) is NOT an annihilator")
    ok &= check("NCb", bool(add(disc, smul(2915, mul(power(T1, 2), E)))),
                "perturbed disc identity (-2915 t1^2 E) FAILS")
    bad_pt = (Q(1, 2), Q(-8, 3), Q(16) + Q(1, 100))
    ok &= check("NCc", F_direct(*bad_pt) != (Q(-16, 27), Q(0), Q(1)),
                "perturbed witness point misses t*")
    wrong_fact = smul(2, mul(power(add(Y, const(Q(8, 3))), 2),
                             add(Y, const(Q(-4, 3)))))
    g1_at_t = subst(G1, [X, Y, Z, const(Q(-16, 27)), const(0), const(1)])
    ok &= check("NCd", bool(add(g1_at_t, smul(-1, wrong_fact))),
                "wrong cubic factorization (double root swapped) FAILS")
    # perturbed curve parametrization (t1 = s^2/11) must NOT kill E.
    bad_curve = {}
    for m, cf in E.items():
        a, b, c = m[3], m[4], m[5]
        e = 2 * a + b - c
        v = cf * Q(1, 11) ** a * Q(4, 3) ** c
        sacc = bad_curve.get(e, Q(0)) + v
        if sacc:
            bad_curve[e] = sacc
        else:
            bad_curve.pop(e, None)
    ok &= check("NCe", bool(bad_curve),
                "perturbed curve (t1 = s^2/11) does NOT annihilate E")

    print()
    if _N_CHECKS != EXPECTED_CHECKS:
        print(f"HARNESS ERROR: ran {_N_CHECKS} checks, docstring advertises "
              f"{EXPECTED_CHECKS}. Fix the count before trusting the run.")
        return 1
    print(f"({_N_CHECKS} machine checks run, matching the advertised count.)")
    if ok:
        print("CERTIFIED (machine part): the annihilator identities, the")
        print("discriminant identity, the density facts, and the witness fibers.")
        print("With the classical lemmas (L1)-(L5) in the docstring these give")
        print("  S_F = V(27t1^2t3^2 - 18t1t2t3 + 16t1 + t2^3t3 - t2^2):")
        print("F is an unbranched 3-sheeted covering over the complement of this")
        print("quartic; over it, preimages escape to infinity (x-coordinate only).")
        print("BONUS (I6): F is NOT surjective -- the punctured curve")
        print("gamma(s) = (s^2/12, s, 4/(3s)) inside V(E) has empty fibers.")
        print("CONDITIONAL on the root claim (Alpoge 2026); claim-typed as")
        print("VERIFICATION+DERIVATION, not discovery of the map.")
        return 0
    print("FAILED: a check did not pass -- do not trust the S_F claim.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

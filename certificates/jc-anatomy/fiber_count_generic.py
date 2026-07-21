#!/usr/bin/env python3
"""Certify: over EVERY base point t with D(t) != 0, Alpoge's map has EXACTLY
3 preimages — and D factors as 9 * t1 * t2 * Q, with Q the same degree-4
polynomial that carries the discriminant.

CONDITIONAL on the root claim (Alpoge's counterexample; verification, not
discovery). Style contract: certificates/jacobian-conjecture/verify.py.

Round 2 certified [C(x,y,z) : C(f1,f2,f3)] = 3 — the map is GENERICALLY
3-to-1. This certificate upgrades "generically" to an EXPLICIT dense open
set: writing t = (t1,t2,t3) for the target coordinates and

  Q(t) = 27t1^2t3^2 - 18t1t2t3 + 16t1 + t2^3t3 - t2^2
  D(t) = 9 * t1 * t2 * Q(t)          (leading x-coefficient of relation G2)

              D(t) != 0   ==>   #F^{-1}(t) = 3   (exactly).

Consequently every fiber-degeneracy (count < 3, including empty fibers) is
confined to the hypersurface {t1 * t2 * Q = 0}; companion anchor
certificates (fiber_anchors.py) show counts 3 / 1 / 0 actually occur on its
strata, with count 3 on {t1=0, Q != 0} — so the t1, t2 factors are artifacts
of the y-elimination, while {Q = 0} carries the true degeneracy.

PROOF SHAPE (machine part = five exact polynomial identities):

  Leg 1  G1(F;y) == 0, G2(F;x,y) == 0, G3(F;x,y,z) == 0 in Q[x,y,z]
         (the three certified elimination relations, re-verified here):
         over any t, every fiber point's y is a root of the cubic G1(t;y);
         if D(t) != 0, x is then determined by y (G2 is linear in x with
         leading coefficient D), and z is determined by (x,y) (G3 is linear
         in z with leading coefficient 2). So distinct fiber points have
         distinct y, and #fiber <= #roots of the cubic.

  Leg 2  D == 9 * t1 * t2 * Q  identically.

  Leg 3  LIFTING. Let x(y,t) = XN/D and z(y,t) = ZN2/(2D) be the rational
         solutions read off G2 and G3 (XN := -(G2 - D x); ZN2 defined by
         clearing x in G3). Then for i = 1,2,3:

             (2D)^ez * D^ex * ( f_i(x(y,t), y, z(y,t)) - t_i )

         expanded as a POLYNOMIAL in Q[y,t] (ex, ez = the x-, z-degrees of
         f_i) is DIVISIBLE by G1: the division remainder w.r.t. y is exactly
         0. Hence for every t with D(t) != 0 and every root y0 of the cubic
         G1(t; -), the candidate point (x(y0,t), y0, z(y0,t)) is finite and
         maps to t on the nose: EVERY root lifts.

  Leg 4  disc(G1) = -2916 t1^2 Q  and  det Sylvester(G1, G1') = -2 disc
         (both identities; leading coefficient of G1 is the constant 2), so
         D(t) != 0 => t1 != 0 and Q(t) != 0 => disc(t) != 0 => the cubic
         has 3 DISTINCT roots.

  READING (the human step): fix t with D(t) != 0. By Leg 4 the cubic has 3
  distinct roots; by Leg 3 each lifts to a fiber point; the 3 points are
  distinct (distinct y); by Leg 1 there are no others (any fiber point sits
  over a root, and its x, z are forced). Exactly 3.

NEGATIVE CONTROLS: planted perturbations of the lifting identity, of the
D-factorization, and of the map itself must each FAIL.

Exit 0 iff all identities hold and all controls fail as planted.
"""
from fractions import Fraction as Fr
import sys

NV = 6  # x y z t1 t2 t3
X, Y, Z, T1, T2, T3 = range(NV)


def var(i):
    e = [0] * NV
    e[i] = 1
    return {tuple(e): Fr(1)}


def const(c):
    c = Fr(c)
    return {(0,) * NV: c} if c else {}


def add(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            s = out.get(m, Fr(0)) + c
            if s:
                out[m] = s
            else:
                out.pop(m, None)
    return out


def neg(p):
    return {m: -c for m, c in p.items()}


def smul(c, p):
    c = Fr(c)
    return {m: c * v for m, v in p.items()} if c else {}


def mul(*ps):
    out = const(1)
    for p in ps:
        acc = {}
        for m1, c1 in out.items():
            for m2, c2 in p.items():
                m = tuple(a + b for a, b in zip(m1, m2))
                s = acc.get(m, Fr(0)) + c1 * c2
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
    out = {}
    for m, c in p.items():
        term = const(c)
        for i, e in enumerate(m):
            if e:
                term = mul(term, power(images[i], e))
        out = add(out, term)
    return out


def deg_in(p, vidx):
    return max((m[vidx] for m in p), default=0)


x, y, z, t1, t2, t3 = (var(i) for i in range(NV))

# ------------------------------------------------------- the map (root claim)
ONE_PLUS_XY = add(const(1), mul(x, y))
F1 = add(mul(power(ONE_PLUS_XY, 3), z),
         mul(power(y, 2), ONE_PLUS_XY, add(const(4), smul(3, mul(x, y)))))
F2 = add(y,
         smul(3, mul(x, power(ONE_PLUS_XY, 2), z)),
         smul(3, mul(x, power(y, 2), add(const(4), smul(3, mul(x, y))))))
F3 = add(smul(2, x), smul(-3, mul(power(x, 2), y)), smul(-1, mul(power(x, 3), z)))

# ------------------------- the relations G1, G2, G3 (crater-certified, verbatim
# coefficients from atlas/jc-crater/geometric_degree.py) -----------------------
G1 = add(smul(2, power(y, 3)),
         smul(-3, mul(t2, power(y, 2))),
         smul(18, mul(t1, y)),
         smul(27, mul(power(t1, 2), t3)),
         smul(-18, mul(t1, t2)),
         power(t2, 3))

D = add(smul(243, mul(power(t1, 3), t2, power(t3, 2))),
        smul(-162, mul(power(t1, 2), power(t2, 2), t3)),
        smul(144, mul(power(t1, 2), t2)),
        smul(9, mul(t1, power(t2, 4), t3)),
        smul(-9, mul(t1, power(t2, 3))))

G2REST = add(mul(add(smul(-18, mul(t1, t3)), smul(2, t2)), power(y, 3)),
             mul(add(smul(9, mul(t1, t2, t3)), smul(-1, power(t2, 2))), power(y, 2)),
             mul(add(smul(-162, mul(power(t1, 2), t3)),
                     smul(27, mul(t1, power(t2, 2), t3)),
                     smul(-6, mul(t1, t2)),
                     smul(-1, power(t2, 3))), y),
             smul(-243, mul(power(t1, 3), power(t3, 2))),
             smul(81, mul(power(t1, 2), t2, t3)),
             smul(-9, mul(t1, power(t2, 3), t3)),
             smul(6, mul(t1, power(t2, 2))))
G2 = add(mul(D, x), G2REST)

G3REST = add(smul(-6, mul(t3, x, power(y, 4))),
             smul(9, mul(x, power(y, 3))),
             smul(-3, mul(t2, x, power(y, 2))),
             smul(3, mul(t1, x, y)),
             smul(-8, mul(t3, power(y, 3))),
             smul(7, power(y, 2)),
             mul(t2, y),
             smul(-2, t1))
G3 = add(smul(2, z), G3REST)

QPOLY = add(smul(27, mul(power(t1, 2), power(t3, 2))),
            smul(-18, mul(t1, t2, t3)),
            smul(16, t1),
            mul(power(t2, 3), t3),
            smul(-1, power(t2, 2)))

# ----------------------------------------- rational solutions read off G2, G3
# x = XN / D           with XN = -G2REST                       (from G2 = 0)
# z = ZN2 / (2D)       with ZN2 = -(XN*c1 + D*c0)              (from G3 = 0)
#   where G3REST = c1(y,t)*x + c0(y,t).
XN = neg(G2REST)
C1 = {m[:X] + (0,) + m[X + 1:]: c for m, c in G3REST.items() if m[X] == 1}
C0 = {m: c for m, c in G3REST.items() if m[X] == 0}
assert not any(m[X] > 1 for m in G3REST), "G3REST must be linear in x"
ZN2 = neg(add(mul(XN, C1), mul(D, C0)))


def subst_xz_rational(p):
    """p(XN/D, y, ZN2/(2D)) * D^degx(p) * (2D)^degz(p), exactly, as a polynomial.

    Substitutes monomial by monomial, multiplying each term by the deficit
    powers of the denominators so everything stays polynomial.
    """
    ex, ez = deg_in(p, X), deg_in(p, Z)
    out = {}
    for m, c in p.items():
        term = const(c)
        term = mul(term, power(XN, m[X]), power(D, ex - m[X]))
        term = mul(term, power(ZN2, m[Z]), power(smul(2, D), ez - m[Z]))
        rest = list(m)
        rest[X] = 0
        rest[Z] = 0
        term = mul(term, {tuple(rest): Fr(1)})
        out = add(out, term)
    return out, ex, ez


def reduce_mod_G1(p):
    """Division remainder of p by G1 w.r.t. y (leading y-coeff of G1 is 2)."""
    tail = neg(add(G1, smul(-2, power(y, 3))))  # 2y^3 = tail
    r = dict(p)
    while True:
        d = deg_in(r, Y)
        if d < 3:
            return r
        lead = {m: c for m, c in r.items() if m[Y] == d}
        # r -= (lead / (2 y^3)) * (2y^3 - tail)  ==  r - lead + (lead/2y^3)*tail
        shift = {}
        for m, c in lead.items():
            mm = list(m)
            mm[Y] = d - 3
            shift[tuple(mm)] = c / 2
        r = add(r, neg(lead), mul(shift, tail))


def check(name, ok, note, detail=""):
    print(f"  [{'OK' if ok else 'FAIL'}] {name}: {note}")
    if not ok and detail:
        print(f"         {detail}")
    return ok


def lifting_residual(fi, ti_var):
    """(2D)^ez D^ex (f_i(x(y),y,z(y)) - t_i) reduced mod G1; {} iff divisible."""
    num, ex, ez = subst_xz_rational(fi)
    full = add(num, neg(mul(ti_var, power(D, ex), power(smul(2, D), ez))))
    return reduce_mod_G1(full)


def main():
    ok = True
    print("Exact fiber count on {D != 0} for Alpoge's map "
          "(conditional on the root claim)\n")

    at_f = [x, y, z, F1, F2, F3]
    for name, rel in (("G1", G1), ("G2", G2), ("G3", G3)):
        res = subst(rel, at_f)
        ok &= check(f"leg1 {name}(F) == 0", not res,
                    "elimination relation holds along the map",
                    f"residual {len(res)} term(s)")

    ok &= check("leg2 D == 9*t1*t2*Q", not add(D, neg(smul(9, mul(t1, t2, QPOLY)))),
                "the x-leading coefficient factors through Q")

    for i, fi in enumerate((F1, F2, F3), 1):
        r = lifting_residual(fi, var(T1 + i - 1))
        ok &= check(f"leg3 lift f{i}", not r,
                    f"(2D)^1 D^3 (f{i}(x(y),y,z(y)) - t{i}) is divisible by G1",
                    f"remainder has {len(r)} term(s)")

    # Leg 4: disc identities (shared with galois_group_s3.py).
    A, B, C = const(2), smul(-3, t2), smul(18, t1)
    Dc = add(smul(27, mul(power(t1, 2), t3)), smul(-18, mul(t1, t2)), power(t2, 3))
    DELTA = add(smul(18, mul(A, B, C, Dc)),
                smul(-4, mul(power(B, 3), Dc)),
                mul(power(B, 2), power(C, 2)),
                smul(-4, mul(A, power(C, 3))),
                smul(-27, mul(power(A, 2), power(Dc, 2))))
    ok &= check("leg4 disc == -2916*t1^2*Q",
                not add(DELTA, smul(2916, mul(power(t1, 2), QPOLY))),
                "so D != 0 => t1,Q != 0 => disc != 0 => 3 distinct roots")

    print("\nNegative controls (each must FAIL as planted):")
    r = lifting_residual(add(F1, mul(x, y)), var(T1))
    ok &= check("ctrl A", bool(r),
                f"perturbed f1 + xy leaves a nonzero remainder ({len(r)} term(s))")
    Dbad = add(D, power(t2, 2))
    ok &= check("ctrl B", bool(add(Dbad, neg(smul(9, mul(t1, t2, QPOLY))))),
                "perturbed D + t2^2 no longer factors as 9*t1*t2*Q")
    res = subst(G2, [x, y, z, F1, F2, add(F3, mul(x, y))])
    ok &= check("ctrl C", bool(res),
                f"perturbed map (f3 + xy) breaks G2's pullback identity "
                f"({len(res)} residual term(s))")

    print()
    if ok:
        print("CERTIFIED (conditional on the root claim):")
        print("  For every t = (t1,t2,t3) with 9*t1*t2*Q(t) != 0, the fiber")
        print("  F^{-1}(t) has EXACTLY 3 points. All fiber degeneracy of the")
        print("  3:1 etale counterexample lives on the hypersurface t1*t2*Q = 0;")
        print("  anchor certificates locate the true degeneracy on {Q = 0}.")
        return 0
    print("FAILED — do not trust the fiber-count claim.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

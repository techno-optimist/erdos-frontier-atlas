#!/usr/bin/env python3
"""Certify: the image of Alpoge's dim-3 Keller counterexample omits the ENTIRE
punctured rational curve

    t(s) = ( s^2/12 ,  s ,  4/(3s) ),      s in C, s != 0.

Every fiber over t(s) is EMPTY — the etale, generically 3-to-1 counterexample
map is not surjective, and the complement of its image contains a whole
rational curve (the "cusp curve" of the fiber cubic, where all three sheets
escape to infinity simultaneously). Companion certificates:
fiber_count_generic.py (exactly 3 preimages off {t1 t2 Q = 0}) and
fiber_anchors.py (counts 3/1/0 at ten rational anchors, including t(6) and
t(2) — the two cusp anchors this certificate upgrades to the whole curve).

CONDITIONAL on the root claim (Alpoge's counterexample; verification, not
discovery). Style contract: certificates/jacobian-conjecture/verify.py —
exact rational arithmetic, stdlib only, identity-shaped checks,
planted-failure negative controls.

STRUCTURE (machine part = five exact polynomial identities in Q[x,y,s,T]):

  Leg 0  G1(F(x,y,z); y) == 0 identically in Q[x,y,z]: over ANY target point
         t, the y-coordinate of every fiber point is a root of the cubic
         G1(t; y)  (the crater's certified elimination relation, re-verified
         here so this file stands alone).

  Leg 1  CUBIC COLLAPSE.  With t1 = s^2/12, t2 = s and t3 = T abstract:

           G1(s^2/12, s, T; y)  ==  (1/4)(2y - s)^3  +  (1/16) s^3 (3sT - 4).

         At T = 4/(3s) the second summand vanishes: on the curve the fiber
         cubic is (1/4)(2y - s)^3, whose ONLY root is y = s/2. So any fiber
         point over t(s) has y = s/2 exactly.

  Leg 2  SLICE RESULTANTS.  Substituting y = s/2, each equation
         f_i = t_i(s) is linear in z:  p_i = a_i(x,s) z + b_i(x,s), where
         p3 is first scaled by 6s (harmless: s != 0) to clear its
         denominator. The certificate verifies the two resultant identities

           R12 := a1 b2 - a2 b1  ==  -(1/8) s (sx + 2)^2
           R13 := a1 b3 - a3 b1  ==  3 s^2 x^2 - 8
                                 ==  3 (sx + 2)(sx - 2) + 4.

  Leg 3  READING (the human step, elementary). Fix s != 0 and suppose
         (x0, z0) were a fiber point over t(s); by Legs 0-1 its y is s/2.
         At a common zero of p1, p2, p3:
           R12(x0) = a1 p2 - a2 p1 = 0   and   R13(x0) = a1 p3 - a3 p1 = 0.
         But R12(x0) = 0 with s != 0 forces (s x0 + 2)^2 = 0, i.e.
         s x0 = -2, and then the third identity gives
         R13(x0) = 3*0*(sx0-2) + 4 = 4 != 0.  Contradiction: NO fiber point
         exists. Hence F^{-1}(t(s)) is empty for every complex s != 0.
         (s = 0 is not a point of the curve: t3 = 4/(3s) is undefined.)

CONSEQUENCE.  C^3 \\ image(F) contains the rational curve {t(s) : s != 0}.
Consistency: an etale map omitting a point is non-proper (the crater's
non-properness note); Keller-ness never implied surjectivity. Together with
fiber_count_generic.py this pins the fiber-count stratification:
3 off {t1 t2 Q = 0}; 1 at every certified anchor on {Q = 0} off the cusp
curve; 0 on the cusp curve.

NEGATIVE CONTROLS (each must FAIL as planted): perturbations of the cubic
collapse, of R12's closed form, and of the R13 rewrite.

Exit 0 iff every identity holds and every control fails as planted.
"""
from fractions import Fraction as Fr
import sys

# ------------------------------------------------------------------ engine
# Q[x, y, z, s, T] as {exponent 5-tuple: nonzero Fraction}.
NV = 5
X, Y, Z, S, T = range(NV)


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
            v = out.get(m, Fr(0)) + c
            if v:
                out[m] = v
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
                v = acc.get(m, Fr(0)) + c1 * c2
                if v:
                    acc[m] = v
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


x, y, z, s, Tv = (var(i) for i in range(NV))


def check(name, ok, note, detail=""):
    print(f"  [{'OK' if ok else 'FAIL'}] {name}: {note}")
    if not ok and detail:
        print(f"         {detail}")
    return ok


# --------------------------------------------- the map and the fiber cubic
ONE_PLUS_XY = add(const(1), mul(x, y))
F1 = add(mul(power(ONE_PLUS_XY, 3), z),
         mul(power(y, 2), ONE_PLUS_XY, add(const(4), smul(3, mul(x, y)))))
F2 = add(y,
         smul(3, mul(x, power(ONE_PLUS_XY, 2), z)),
         smul(3, mul(x, power(y, 2), add(const(4), smul(3, mul(x, y))))))
F3 = add(smul(2, x), smul(-3, mul(power(x, 2), y)), smul(-1, mul(power(x, 3), z)))


def G1_of(T1p, T2p, T3p):
    """G1(t1,t2,t3;y) with polynomial images for the t_i (y stays y)."""
    return add(smul(2, power(y, 3)),
               smul(-3, mul(T2p, power(y, 2))),
               smul(18, mul(T1p, y)),
               smul(27, mul(power(T1p, 2), T3p)),
               smul(-18, mul(T1p, T2p)),
               power(T2p, 3))


def main():
    ok = True
    print("Empty fibers over the whole cusp curve t(s) = (s^2/12, s, 4/(3s))")
    print("(conditional on the root claim; see module docstring)\n")

    # Leg 0: the elimination cubic annihilates y along the map (composed
    # directly: G1 is a fixed polynomial combination of its arguments).
    G1F = add(smul(2, power(y, 3)),
              smul(-3, mul(F2, power(y, 2))),
              smul(18, mul(F1, y)),
              smul(27, mul(power(F1, 2), F3)),
              smul(-18, mul(F1, F2)),
              power(F2, 3))
    ok &= check("leg0 G1(F;y) == 0", not G1F,
                "every fiber point's y is a root of the fiber cubic",
                f"residual {len(G1F)} term(s)")

    # Leg 1: cubic collapse on the curve (t3 abstract as T).
    T1p = smul(Fr(1, 12), power(s, 2))
    T2p = s
    lhs = G1_of(T1p, T2p, Tv)
    two_y_minus_s = add(smul(2, y), neg(s))
    rhs = add(smul(Fr(1, 4), power(two_y_minus_s, 3)),
              smul(Fr(1, 16), mul(power(s, 3),
                                  add(smul(3, mul(s, Tv)), const(-4)))))
    ok &= check("leg1 cubic collapse", not add(lhs, neg(rhs)),
                "G1(s^2/12, s, T; y) == (1/4)(2y-s)^3 + (1/16)s^3(3sT-4); "
                "at T = 4/(3s) only root is y = s/2")

    # Leg 2: slice system at y = s/2 and the two resultant identities.
    half_sx = smul(Fr(1, 2), mul(s, x))
    lin = add(const(1), half_sx)                       # 1 + (s/2) x
    four3 = add(const(4), smul(Fr(3, 2), mul(s, x)))   # 4 + 3(s/2)x
    a1 = power(lin, 3)
    b1 = add(mul(smul(Fr(1, 4), power(s, 2)), lin, four3),
             smul(Fr(-1, 12), power(s, 2)))
    a2 = smul(3, mul(x, power(lin, 2)))
    b2 = add(smul(Fr(1, 2), s),
             mul(smul(Fr(3, 4), power(s, 2)), x, four3),
             neg(s))
    a3 = smul(-6, mul(s, power(x, 3)))                 # p3 scaled by 6s
    b3 = add(smul(12, mul(s, x)),
             smul(-9, mul(power(s, 2), power(x, 2))),
             const(-8))

    R12 = add(mul(a1, b2), neg(mul(a2, b1)))
    R13 = add(mul(a1, b3), neg(mul(a3, b1)))
    sx2 = add(mul(s, x), const(2))
    ok &= check("leg2a R12 closed form",
                not add(R12, smul(Fr(1, 8), mul(s, power(sx2, 2)))),
                "a1*b2 - a2*b1 == -(1/8) s (sx+2)^2")
    ok &= check("leg2b R13 closed form",
                not add(R13, neg(add(smul(3, mul(power(s, 2), power(x, 2))),
                                     const(-8)))),
                "a1*b3 - a3*b1 == 3 s^2 x^2 - 8")
    rewrite = add(smul(3, mul(sx2, add(mul(s, x), const(-2)))), const(4))
    ok &= check("leg2c R13 rewrite", not add(R13, neg(rewrite)),
                "3s^2x^2 - 8 == 3(sx+2)(sx-2) + 4: at sx = -2 it equals 4 != 0")

    print("\nNegative controls (each must FAIL as planted):")
    bad = add(rhs, mul(s, y))
    ok &= check("ctrl A", bool(add(lhs, neg(bad))),
                "perturbed collapse identity (+ s*y) no longer matches")
    ok &= check("ctrl B",
                bool(add(R12, smul(Fr(1, 8), mul(s, power(add(mul(s, x),
                                                              const(3)), 2))))),
                "R12 != -(1/8) s (sx+3)^2 — the closed form is sharp")
    bad = add(smul(3, mul(sx2, add(mul(s, x), const(-2)))), const(5))
    ok &= check("ctrl C", bool(add(R13, neg(bad))),
                "R13 != 3(sx+2)(sx-2) + 5 — the constant 4 is exact")

    print()
    if ok:
        print("CERTIFIED (conditional on the root claim):")
        print("  For EVERY complex s != 0 the fiber of F over")
        print("  (s^2/12, s, 4/(3s)) is EMPTY. The image of Alpoge's etale")
        print("  3:1 Keller counterexample omits an entire rational curve —")
        print("  the map is not surjective.")
        return 0
    print("FAILED — do not trust the emptiness claim.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

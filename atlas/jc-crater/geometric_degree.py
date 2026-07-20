#!/usr/bin/env python3
"""Certify the exact GEOMETRIC DEGREE of Alpoge's dim-3 Keller counterexample.

Backs the quantity 'jc-min-geometric-degree-noninjective' in quantities.json,
whose upper bound previously rested on a CAS session-log observation (a sympy
fiber count over two sample targets -- explicitly NOT a certified computation,
confidence C3). This script replaces that observation with an exact,
replayable certificate that the map is generically 3-to-1:

    [ C(x,y,z) : C(f1,f2,f3) ] = 3

The geometric degree (generic fiber size) equals that field-extension degree
because char 0 makes the extension separable; and because det(JF) = -2 is a
nonzero CONSTANT the map is etale everywhere, so fibers are never fattened by
multiplicity -- points are counted honestly.

WHAT IS CERTIFIED HERE, AND HOW

Write t1, t2, t3 for the coordinates on the target. A Groebner computation
(Singular, char 0, lex, on the DGX) produced three relations generating the
ideal (f1-t1, f2-t2, f3-t3). This script does NOT trust that computation: it
carries the three relations as abstract polynomials in Q[x,y,z,t1,t2,t3] and
verifies each one directly by substituting t_i := f_i(x,y,z) and expanding in
exact rational arithmetic. Each must collapse to the zero polynomial:

  (G1)  2y^3 - 3t2*y^2 + 18t1*y + (27t1^2t3 - 18t1t2 + t2^3)  =  0
  (G2)  D(t)*x + (a cubic in y over Q[t])                     =  0
  (G3)  2z - (a polynomial in x, y over Q[t])                 =  0

A transcription error in any coefficient makes the identity FAIL -- it cannot
produce a false PASS. That is the reason the check is shaped as an identity
rather than as an assertion that Singular's answer was right.

  UPPER BOUND (degree <= 3).  G1 says y is a root of a degree-3 polynomial
  over C(t) = C(f1,f2,f3), so [C(t)(y) : C(t)] <= 3. G2 is LINEAR in x with
  leading coefficient D(t), a nonzero element of C(t), so x lies in C(t)(y).
  G3 is linear in z with constant leading coefficient 2, so z lies in
  C(t)(x,y) = C(t)(y). Hence C(x,y,z) = C(t)(y), of degree <= 3.

  LOWER BOUND (degree >= 3).  It suffices that G1 is irreducible over C(t).
  Specialize t1 = 1, t2 = 0 -- this script performs that substitution on the
  same G1 object and checks the result equals

      2y^3 + 18y + 27t3.

  As an element of C[y, t3] this has degree 1 in t3, hence is irreducible in
  C(y)[t3]; it is primitive in C[y][t3] (its coefficients 2y^3 + 18y and 27
  share no common factor), so by Gauss's lemma it is irreducible in C[y, t3],
  hence in C(t3)[y]. A specialization that preserves the y-degree can only be
  reducible if the generic polynomial is, so generic G1 is irreducible over
  C(t) and the degree is exactly 3.

  Only that last sentence-and-a-half is human reasoning: the script checks the
  substitution arithmetic and the y-degree, and leaves Gauss's lemma to the
  reader. Stated plainly so nobody mistakes where the machine stops.

CONSEQUENCE FOR THE ATLAS.  The bracket for the minimal geometric degree of a
non-injective Keller map stays [2, 3] and stays OPEN -- this map realizes 3,
and whether a generically 2-to-1 Keller map exists is untouched. What changes
is only that the upper bound is certified rather than observed.

Exit 0 iff every identity above holds exactly.
"""
from fractions import Fraction as Q
import sys

# --------------------------------------------------------------- poly engine
# Polynomials in Q[x, y, z, t1, t2, t3] as dicts {exponent 6-tuple: coeff},
# zero coefficients never stored -- the same monomial-dict convention as
# map_degree.py and certificates/jacobian-conjecture/verify.py, so all three
# agree on what "exact" means. Substitution maps a polynomial into this same
# ring, which is all we need: t_i := f_i(x,y,z) and t_i := rational constants
# are both just substitutions.

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
    """Substitute images[i] (a polynomial) for variable i, in this same ring."""
    out = {}
    for m, c in p.items():
        term = const(c)
        for i, e in enumerate(m):
            if e:
                term = mul(term, power(images[i], e))
        out = add(out, term)
    return out


def show(p):
    """Human-readable, deterministic rendering (for the specialization check)."""
    if not p:
        return "0"
    parts = []
    for m in sorted(p, reverse=True):
        c = p[m]
        body = "*".join(f"{VARNAMES[i]}^{e}" if e > 1 else VARNAMES[i]
                        for i, e in enumerate(m) if e)
        parts.append(f"{c}" if not body else f"{c}*{body}")
    return " + ".join(parts)


# ------------------------------------------------------- the counterexample
# Alpoge's map, transcribed from certificates/jacobian-conjecture/witness.json.
# That certificate proves it IS a Keller counterexample (det(JF) == -2
# identically; three distinct points sharing the image (-1/4, 0, 0)). This
# script only measures how many-to-one it is.

ONE_PLUS_XY = add(const(1), mul(X, Y))

F1 = add(mul(power(ONE_PLUS_XY, 3), Z),
         mul(power(Y, 2), ONE_PLUS_XY, add(const(4), smul(3, mul(X, Y)))))
F2 = add(Y,
         smul(3, mul(X, power(ONE_PLUS_XY, 2), Z)),
         smul(3, mul(X, power(Y, 2), add(const(4), smul(3, mul(X, Y))))))
F3 = add(smul(2, X), smul(-3, mul(power(X, 2), Y)), smul(-1, mul(power(X, 3), Z)))

# ----------------------------------------------------------- the relations
# Abstract in Q[x,y,z,t1,t2,t3]; nothing below is specialized yet.

G1 = add(smul(2, power(Y, 3)),
         smul(-3, mul(T2, power(Y, 2))),
         smul(18, mul(T1, Y)),
         smul(27, mul(power(T1, 2), T3)),
         smul(-18, mul(T1, T2)),
         power(T2, 3))

D = add(smul(243, mul(power(T1, 3), T2, power(T3, 2))),
        smul(-162, mul(power(T1, 2), power(T2, 2), T3)),
        smul(144, mul(power(T1, 2), T2)),
        smul(9, mul(T1, power(T2, 4), T3)),
        smul(-9, mul(T1, power(T2, 3))))

G2 = add(mul(D, X),
         mul(add(smul(-18, mul(T1, T3)), smul(2, T2)), power(Y, 3)),
         mul(add(smul(9, mul(T1, T2, T3)), smul(-1, power(T2, 2))), power(Y, 2)),
         mul(add(smul(-162, mul(power(T1, 2), T3)),
                 smul(27, mul(T1, power(T2, 2), T3)),
                 smul(-6, mul(T1, T2)),
                 smul(-1, power(T2, 3))), Y),
         smul(-243, mul(power(T1, 3), power(T3, 2))),
         smul(81, mul(power(T1, 2), T2, T3)),
         smul(-9, mul(T1, power(T2, 3), T3)),
         smul(6, mul(T1, power(T2, 2))))

G3 = add(smul(2, Z),
         smul(-6, mul(T3, X, power(Y, 4))),
         smul(9, mul(X, power(Y, 3))),
         smul(-3, mul(T2, X, power(Y, 2))),
         smul(3, mul(T1, X, Y)),
         smul(-8, mul(T3, power(Y, 3))),
         smul(7, power(Y, 2)),
         mul(T2, Y),
         smul(-2, T1))

# t_i := f_i(x,y,z); x, y, z left alone.
AT_F = [X, Y, Z, F1, F2, F3]
# t1 := 1, t2 := 0; y and t3 left alone (G1 involves neither x nor z).
SPECIALIZE = [X, Y, Z, const(1), const(0), T3]


def check(name, ok, note, detail=""):
    print(f"  [{'OK' if ok else 'FAIL'}] {name}: {note}")
    if not ok and detail:
        print(f"         {detail}")
    return ok


def main() -> int:
    print("Geometric degree of Alpoge's dim-3 Keller counterexample")
    print("Substituting t_i := f_i(x,y,z); every relation must vanish "
          "identically in Q[x,y,z].\n")
    ok = True

    for name, rel, note in (
        ("G1", G1, "y satisfies a cubic over C(f)        =>  [C(f)(y):C(f)] <= 3"),
        ("G2", G2, "x is C(f)-rational in y              =>  x in C(f)(y)"),
        ("G3", G3, "z is C(f)-rational in x, y           =>  z in C(f)(y)"),
    ):
        res = subst(rel, AT_F)
        ok &= check(name, not res, note,
                    f"residual has {len(res)} nonzero term(s); "
                    f"sample: {sorted(res.items())[:2]}")

    ok &= check("D != 0", bool(D),
                "leading coefficient of x in G2 is a nonzero element of C(f)")

    # Lower bound: specialize G1 at t1 = 1, t2 = 0 and compare with the target.
    spec = subst(G1, SPECIALIZE)
    target = add(smul(2, power(Y, 3)), smul(18, Y), smul(27, T3))
    ok &= check("G1|(t1=1,t2=0)", not add(spec, smul(-1, target)),
                f"specializes to {show(target)}",
                f"got {show(spec)}")
    deg_y = max((m[1] for m in spec), default=0)
    deg_t3 = max((m[5] for m in spec), default=0)
    ok &= check("degrees", deg_y == 3 and deg_t3 == 1,
                f"specialization has deg_y = {deg_y} (y-degree preserved) and "
                f"deg_t3 = {deg_t3} (linear in t3)  =>  irreducible, by Gauss")

    print()
    if ok:
        print("CERTIFIED: [C(x,y,z) : C(f1,f2,f3)] = 3 -- the map is "
              "generically 3-to-1.")
        print("The atlas bracket for the MINIMAL geometric degree of a "
              "non-injective Keller map")
        print("remains [2, 3] and remains OPEN: this certifies the upper "
              "bound only.")
        return 0
    print("FAILED: a relation did not vanish -- do not trust the degree claim.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

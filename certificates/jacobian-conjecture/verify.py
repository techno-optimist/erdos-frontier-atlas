#!/usr/bin/env python3
"""Replayable certificate: the 2026 Jacobian Conjecture counterexample map.

Verifies, in exact rational arithmetic with no dependencies beyond the CPython
standard library, that the polynomial map F : C^3 -> C^3

  f1 = (1+xy)^3 z + y^2 (1+xy)(4+3xy)
  f2 = y + 3x(1+xy)^2 z + 3xy^2 (4+3xy)
  f3 = 2x - 3x^2 y - x^3 z

satisfies BOTH:

  (1) det JF == -2, IDENTICALLY -- proved symbolically: the determinant is
      computed as a polynomial in Q[x,y,z] via an exact monomial-dict engine
      (build -> differentiate -> 3x3 cofactor expansion) and asserted equal,
      coefficient by coefficient, to the constant polynomial -2. This is a
      proof of constancy, not a sample of evaluations.

  (2) F is NOT injective -- the three distinct rational points
        (0, 0, -1/4), (1, -3/2, 13/2), (-1, 3/2, 13/2)
      all map exactly to (-1/4, 0, 0). Images are computed by two independent
      paths (direct nested-expression evaluation, and evaluation of the
      expanded polynomials from leg 1) which must agree.

(1) + (2) contradict the Jacobian Conjecture (Keller 1939; see van den Essen,
"Polynomial Automorphisms and the Jacobian Conjecture", 2000): a polynomial
self-map of C^n with nonzero constant Jacobian determinant would be injective.

Negative controls: a perturbed map must FAIL leg 1 and a perturbed point must
FAIL leg 2 -- demonstrating the checker can reject.

Run:  python3 verify.py        (exit 0 = certificate verified)
"""
from fractions import Fraction as Q
import json
import os
import sys

# ---------------------------------------------------------------- poly engine
# A polynomial in Q[x,y,z] is a dict {(i,j,k): coeff} with nonzero Fraction
# coefficients; (i,j,k) are the exponents of x,y,z.

def pconst(c):
    c = Q(c)
    return {(0, 0, 0): c} if c else {}

X, Y, Z = {(1, 0, 0): Q(1)}, {(0, 1, 0): Q(1)}, {(0, 0, 1): Q(1)}

def padd(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            s = out.get(m, Q(0)) + c
            if s: out[m] = s
            elif m in out: del out[m]
    return out

def pmul(a, b):
    out = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            m = (ma[0] + mb[0], ma[1] + mb[1], ma[2] + mb[2])
            s = out.get(m, Q(0)) + ca * cb
            if s: out[m] = s
            elif m in out: del out[m]
    return out

def pscale(a, c):
    c = Q(c)
    return {m: v * c for m, v in a.items()} if c else {}

def ppow(a, n):
    out = pconst(1)
    for _ in range(n): out = pmul(out, a)
    return out

def pdiff(a, axis):
    out = {}
    for m, c in a.items():
        e = m[axis]
        if e:
            dm = tuple(v - (1 if i == axis else 0) for i, v in enumerate(m))
            out[dm] = out.get(dm, Q(0)) + c * e
    return {m: c for m, c in out.items() if c}

def peval(a, pt):
    x, y, z = pt
    return sum((c * x**m[0] * y**m[1] * z**m[2] for m, c in a.items()), Q(0))

# ---------------------------------------------------------------- the map F
def build_map():
    u = padd(pconst(1), pmul(X, Y))                     # 1 + xy
    w = padd(pconst(4), pscale(pmul(X, Y), 3))          # 4 + 3xy
    f1 = padd(pmul(ppow(u, 3), Z), pmul(pmul(ppow(Y, 2), u), w))
    f2 = padd(Y, pscale(pmul(pmul(X, ppow(u, 2)), Z), 3),
              pscale(pmul(pmul(X, ppow(Y, 2)), w), 3))
    f3 = padd(pscale(X, 2), pscale(pmul(ppow(X, 2), Y), -3),
              pscale(pmul(ppow(X, 3), Z), -1))
    return f1, f2, f3

def det3(rows):
    (a, b, c), (d, e, f), (g, h, i) = rows
    return padd(pmul(a, padd(pmul(e, i), pscale(pmul(f, h), -1))),
                pscale(pmul(b, padd(pmul(d, i), pscale(pmul(f, g), -1))), -1),
                pmul(c, padd(pmul(d, h), pscale(pmul(e, g), -1))))

def jac_det(fs):
    return det3([[pdiff(f, ax) for ax in (0, 1, 2)] for f in fs])

# Second, independent evaluation path for leg 2: nested expressions, never
# touching the polynomial engine.
def F_direct(x, y, z):
    u = 1 + x * y
    return ((u**3) * z + y**2 * u * (4 + 3 * x * y),
            y + 3 * x * u**2 * z + 3 * x * y**2 * (4 + 3 * x * y),
            2 * x - 3 * x**2 * y - x**3 * z)

# ---------------------------------------------------------------- the checks
POINTS = [(Q(0), Q(0), Q(-1, 4)),
          (Q(1), Q(-3, 2), Q(13, 2)),
          (Q(-1), Q(3, 2), Q(13, 2))]
TARGET = (Q(-1, 4), Q(0), Q(0))

def _q(s):
    return Q(str(s))

def witness_matches_code():
    """Guard against witness.json drifting from the object the code verifies:
    the machine-readable constants (colliding points, common image, Jacobian
    value) must equal what this script hardcodes. (The map *expressions* in
    witness.json are human-readable documentation; build_map() is authoritative.)"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "witness.json")
    if not os.path.exists(path):
        return None
    w = json.load(open(path))
    pts_w = [tuple(_q(c) for c in p) for p in w["colliding_points"]]
    img_w = tuple(_q(c) for c in w["common_image"])
    det_w = _q(w["jacobian_determinant"])
    return (set(pts_w) == set(POINTS) and img_w == TARGET and det_w == Q(-2))

def main():
    ok = True
    fs = build_map()

    # Leg 0 -- the machine-readable witness matches the object under test.
    w = witness_matches_code()
    if w is not None:
        print(f"leg 0  witness.json constants match verified object: "
              f"{'PASS' if w else 'FAIL'}")
        ok &= w

    # Leg 1 -- det JF is identically -2 (symbolic polynomial identity).
    # The dict-equality below is sound because every polynomial op maintains the
    # canonical-form invariant "no stored zero coefficients" (padd/pmul/pscale/
    # pdiff prune, and Q is a field so nonzero*nonzero != 0) -- assert it holds.
    d = jac_det(fs)
    assert all(c != 0 for c in d.values()), "non-canonical polynomial (stored zero coeff)"
    leg1 = (d == pconst(-2))
    print(f"leg 1  det(JF) as a polynomial == -2 identically: "
          f"{'PASS' if leg1 else 'FAIL  (got ' + repr(d) + ')'}")
    ok &= leg1

    # Leg 2 -- three distinct points, one image, two evaluation paths.
    leg2 = len(set(POINTS)) == 3
    for p in POINTS:
        img_a = tuple(peval(f, p) for f in fs)
        img_b = F_direct(*p)
        hit = (img_a == img_b == TARGET)
        leg2 &= hit
        print(f"leg 2  F{tuple(map(str, p))} = {tuple(map(str, img_a))}  "
              f"[paths agree: {img_a == img_b}]  hits target: {hit}")
    print(f"leg 2  three distinct preimages of (-1/4, 0, 0): "
          f"{'PASS' if leg2 else 'FAIL'}")
    ok &= leg2

    # Negative control A -- perturb the map (add xy to f3): det must leave -2.
    f3_bad = padd(fs[2], pmul(X, Y))
    ctrl_a = (jac_det((fs[0], fs[1], f3_bad)) != pconst(-2))
    print(f"ctrl A perturbed map (f3 + xy) rejected by leg 1: "
          f"{'PASS' if ctrl_a else 'FAIL'}")
    ok &= ctrl_a

    # Negative control B -- perturb a point: it must miss the target under
    # BOTH evaluation paths used by leg 2.
    bad = (Q(1), Q(-3, 2), Q(13, 2) + Q(1, 100))
    ctrl_b = (F_direct(*bad) != TARGET
              and tuple(peval(f, bad) for f in fs) != TARGET)
    print(f"ctrl B perturbed point rejected by leg 2: "
          f"{'PASS' if ctrl_b else 'FAIL'}")
    ok &= ctrl_b

    print("\nCERTIFICATE " + ("VERIFIED: constant Jacobian -2 + non-injective "
          "=> counterexample to the Jacobian Conjecture (n = 3)" if ok
          else "FAILED -- see legs above"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())

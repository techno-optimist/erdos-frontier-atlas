#!/usr/bin/env python3
"""Exact fiber cardinalities of Alpoge's dim-3 Keller counterexample at ten
rational base points — one anchor per stratum of the degeneracy hypersurface
{t1 * t2 * Q = 0} — including an EMPTY fiber: the etale 3:1 map is NOT
surjective.

CONDITIONAL on the root claim (Alpoge's counterexample; we verify and derive,
we do not discover the root). Style contract:
certificates/jacobian-conjecture/verify.py — exact rationals, stdlib only,
identity-shaped checks, planted-failure negative controls.

Q(t) = 27t1^2t3^2 - 18t1t2t3 + 16t1 + t2^3t3 - t2^2   (deg 4)

NOT CLAIMED: irreducibility of Q over Q. An earlier draft of this header said
"irreducible"; that was a CAS-level discovery probe with no stdlib replay path
here, and no check below uses it. Demoted to a discovery note.

The companion certificate fiber_count_generic.py proves #F^{-1}(t) = 3
whenever t1*t2*Q(t) != 0. This one measures the strata:

  anchor (t1,t2,t3)     stratum                              #fiber
  (-1/4, 0,   0  )   t2=0, Q=-4       (generic thm n/a)        3
  ( 0,   2,   3  )   t1=0, Q=20, disc=0(!)                     3
  ( 1,   4,   0  )   Q=0 (smooth pt)                           1
  ( 2,   5,  1/4 )   Q=0                                       1
  ( 2,   5,  7/27)   Q=0                                       1
  (-16/27, 0, 1  )   Q=0 and t2=0                              1
  ( 0,   1,   1  )   Q=0 and t1=0  (t2*t3=1)                   1
  ( 0,   0,   5  )   t1=t2=0 (subset of Q=0)                   1
  ( 3,   6,  2/9 )   cusp curve (s^2/12, s, 4/(3s)), s=6       0   <- EMPTY
  ( 1/3, 2,  2/3 )   cusp curve, s=2                           0   <- EMPTY

Readings. (0,2,3): the fiber cubic has a DOUBLE root yet the fiber has 3
honest points (two share the same y) — the t1^2 factor of the discriminant is
an artifact of eliminating to the y-coordinate, not fiber degeneracy. On
{Q=0}: exactly the SIMPLE root of the cubic lifts; the two sheets merging in
y escape to infinity (the etale map is non-proper there). On the cusp curve
the cubic degenerates to 2(y - s/2)^3 and ALL THREE sheets escape: the fiber
is empty, so the image of F omits the rational curve points (3,6,2/9) and
(1/3,2,2/3) — a certified NON-SURJECTIVITY witness. Observed fiber-count
spectrum: {3, 1, 0}.

METHOD (exact, per anchor t and per root y0 of the fiber cubic):

  Leg 0   G1(F(x,y,z); y) == 0 identically in Q[x,y,z] (6-variable exact
          expansion): every fiber point over t has its y among the roots of
          the cubic G1(t; y).
  Leg 1   The claimed factorization  G1(t; y) = 2 * prod (y - y0)^m  is
          verified by expansion, with multiplicities summing to 3 — so the
          listed y0 exhaust ALL complex roots.
  Leg 2   For fixed y0 the system f_i(x, y0, z) = t_i (i=1,2,3) is LINEAR in
          z:  p_i = a_i(x) z + b_i(x)  with
             a1 = (1+y0 x)^3,  a2 = 3x(1+y0 x)^2,  a3 = -x^3.
          Set R_ij = a_i b_j - a_j b_i and g = gcd(R12, R13, R23) in Q[x].

          LEMMA (the one human step, elementary): the solutions with y = y0
          are exactly the complex roots of g.
            Necessity: at a solution (x0,z0), R_ij(x0) =
            a_i(x0)p_j(x0,z0) - a_j(x0)p_i(x0,z0) = 0.
            Sufficiency: let g(x0)=0. Note a1, a3 cannot both vanish
            (a1(x0)=0 forces 1+y0x0=0, so x0 != 0, so a3(x0) != 0).
              - If a1(x0) != 0: z0 := -b1/a1 kills p1, and then
                p2 = -R12/a1 = 0, p3 = -R13/a1 = 0.
              - If a1(x0) = 0: R13 = -a3 b1 = 0 gives b1(x0) = 0, so p1
                vanishes for every z; z0 := -b3/a3 kills p3, and
                p2 = -R23/a3 = 0.
            Either way z0 is unique (some a_i != 0), so
            #solutions(y0) = #distinct complex roots of g
                           = deg( g / gcd(g, g') )   [squarefree part],
            provided g != 0 (checked; g == 0 would be a documented boundary).
  Leg 3   The claimed squarefree part is verified by exact expansion
          (monic normalization), and every claimed rational fiber point is
          verified to map to t by DIRECT nested evaluation of the original
          F (the same two-path discipline as verify.py), plus distinctness.
          For the one quadratic factor with no rational roots
          (10x^2+10x+3 at anchor (0,2,3), y0=2) the certificate checks
          gcd with a1 is constant — its 2 complex roots are genuine points.

  #F^{-1}(t) = sum over y0 of the counts. Matches the claimed totals above.

NEGATIVE CONTROLS (must FAIL as planted):
  A  claiming count 3 at (1,4,0) is detected as wrong (machinery totals 1);
  B  a perturbed point (1,-3/2,13/2 + 1/100) does not map to (-1/4,0,0);
  C  a wrong cubic factorization claim at (3,6,2/9) fails the expansion check;
  D  perturbed map (f3 + xy) breaks Leg 0.

Exit 0 iff every leg holds at every anchor and every control fails as planted.
"""
from fractions import Fraction as Fr
import sys

# ---------------------------------------------------------------- 6-var engine
NV = 6
X, Y, Z, T1, T2, T3 = range(NV)


def var(i):
    e = [0] * NV
    e[i] = 1
    return {tuple(e): Fr(1)}


def const(c):
    c = Fr(c)
    return {(0,) * NV: c} if c else {}


def add6(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            s = out.get(m, Fr(0)) + c
            if s:
                out[m] = s
            else:
                out.pop(m, None)
    return out


def smul6(c, p):
    c = Fr(c)
    return {m: c * v for m, v in p.items()} if c else {}


def mul6(*ps):
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


def pow6(p, n):
    out = const(1)
    for _ in range(n):
        out = mul6(out, p)
    return out


def subst6(p, images):
    out = {}
    for m, c in p.items():
        term = const(c)
        for i, e in enumerate(m):
            if e:
                term = mul6(term, pow6(images[i], e))
        out = add6(out, term)
    return out


xv, yv, zv, t1v, t2v, t3v = (var(i) for i in range(NV))
ONE_PLUS_XY = add6(const(1), mul6(xv, yv))
F1 = add6(mul6(pow6(ONE_PLUS_XY, 3), zv),
          mul6(pow6(yv, 2), ONE_PLUS_XY, add6(const(4), smul6(3, mul6(xv, yv)))))
F2 = add6(yv,
          smul6(3, mul6(xv, pow6(ONE_PLUS_XY, 2), zv)),
          smul6(3, mul6(xv, pow6(yv, 2), add6(const(4), smul6(3, mul6(xv, yv))))))
F3 = add6(smul6(2, xv), smul6(-3, mul6(pow6(xv, 2), yv)),
          smul6(-1, mul6(pow6(xv, 3), zv)))
G1 = add6(smul6(2, pow6(yv, 3)),
          smul6(-3, mul6(t2v, pow6(yv, 2))),
          smul6(18, mul6(t1v, yv)),
          smul6(27, mul6(pow6(t1v, 2), t3v)),
          smul6(-18, mul6(t1v, t2v)),
          pow6(t2v, 3))


def F_direct(x, y, z):
    """Nested exact evaluation of the map — independent of the engine."""
    p = 1 + x * y
    return (p**3 * z + y**2 * p * (4 + 3 * x * y),
            y + 3 * x * p**2 * z + 3 * x * y**2 * (4 + 3 * x * y),
            2 * x - 3 * x**2 * y - x**3 * z)


# ------------------------------------------------- univariate polys over Q
def ut(u):
    u = list(u)
    while len(u) > 1 and u[-1] == 0:
        u.pop()
    return u


def udeg(u):
    return len(u) - 1 if any(c != 0 for c in u) else -1


def uadd(a, b):
    n = max(len(a), len(b))
    return ut([(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
               for i in range(n)])


def usmul(c, a):
    return ut([c * v for v in a])


def umul(a, b):
    out = [Fr(0)] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            out[i + j] += ca * cb
    return ut(out)


def usub(a, b):
    return uadd(a, usmul(Fr(-1), b))


def uderiv(a):
    return ut([i * c for i, c in enumerate(a)][1:] or [Fr(0)])


def udivmod(f, g):
    f = ut(f)
    g = ut(g)
    assert udeg(g) >= 0
    q = [Fr(0)] * max(1, len(f) - len(g) + 1)
    r = f[:]
    while udeg(r) >= udeg(g):
        k = udeg(r) - udeg(g)
        c = r[-1] / g[-1]
        q[k] += c
        r = ut([rc - c * g[i - k] if 0 <= i - k <= udeg(g) else rc
                for i, rc in enumerate(r)])
        if udeg(r) < 0:
            break
    return ut(q), r


def ugcd(f, g):
    f, g = ut(f), ut(g)
    if udeg(f) < 0:
        f, g = g, f
    while udeg(g) >= 0:
        f, g = g, udivmod(f, g)[1]
    if udeg(f) >= 0 and f[-1] != 1:
        f = usmul(1 / f[-1], f)  # monic
    return f


def usqfree(g):
    """g / gcd(g, g'), monic."""
    d = ugcd(g, uderiv(g))
    q, r = udivmod(g, d)
    assert udeg(r) < 0
    if udeg(q) >= 0 and q[-1] != 1:
        q = usmul(1 / q[-1], q)
    return q


def ueval(u, x0):
    acc = Fr(0)
    for c in reversed(u):
        acc = acc * x0 + c
    return acc


def check(name, ok, note, detail=""):
    print(f"  [{'OK' if ok else 'FAIL'}] {name}: {note}")
    if not ok and detail:
        print(f"         {detail}")
    return ok


# --------------------------------------------------------------- anchor data
# (t, [(y0, mult)...], per-root claims, exhibited rational points, total)
# per-root claim: (y0, [rational roots of sqfree part], [residual factor
#                  coefficients, low->high] or None)
F = Fr
ANCHORS = [
    ("t2=0, Q=-4 (certified collision target)",
     (F(-1, 4), F(0), F(0)),
     [(F(0), 1), (F(3, 2), 1), (F(-3, 2), 1)],
     {F(0): ([F(0)], None), F(3, 2): ([F(-1)], None), F(-3, 2): ([F(1)], None)},
     [(F(0), F(0), F(-1, 4)), (F(-1), F(3, 2), F(13, 2)),
      (F(1), F(-3, 2), F(13, 2))],
     3),
    ("t1=0, Q=20: disc=0 yet 3 points (t1^2 factor = elimination artifact)",
     (F(0), F(2), F(3)),
     [(F(2), 2), (F(-1), 1)],
     {F(2): ([], [F(3, 10), F(1), F(1)]),   # x^2 + x + 3/10 (monic of 10x^2+10x+3)
      F(-1): ([F(1)], None)},
     [(F(1), F(-1), F(2))],
     3),
    ("Q=0: only the simple root lifts",
     (F(1), F(4), F(0)),
     [(F(4), 1), (F(1), 2)],
     {F(4): ([F(0)], None), F(1): ([], None)},
     [(F(0), F(4), F(-63))],
     1),
    ("Q=0",
     (F(2), F(5), F(1, 4)),
     [(F(2), 2), (F(7, 2), 1)],
     {F(2): ([], None), F(7, 2): ([F(2)], None)},
     [(F(2), F(7, 2), F(-153, 32))],
     1),
    ("Q=0",
     (F(2), F(5), F(7, 27)),
     [(F(3), 2), (F(3, 2), 1)],
     {F(3): ([], None), F(3, 2): ([F(14, 3)], None)},
     [(F(14, 3), F(3, 2), F(-7, 8))],
     1),
    ("Q=0 and t2=0",
     (F(-16, 27), F(0), F(1)),
     [(F(4, 3), 2), (F(-8, 3), 1)],
     {F(4, 3): ([], None), F(-8, 3): ([F(1, 2)], None)},
     [(F(1, 2), F(-8, 3), F(16))],
     1),
    ("Q=0 and t1=0 (t2*t3=1)",
     (F(0), F(1), F(1)),
     [(F(1), 2), (F(-1, 2), 1)],
     {F(1): ([], None), F(-1, 2): ([F(2)], None)},
     [(F(2), F(-1, 2), F(9, 8))],
     1),
    ("t1=t2=0 (triple root, NOT on the cusp curve)",
     (F(0), F(0), F(5)),
     [(F(0), 3)],
     {F(0): ([F(5, 2)], None)},
     [(F(5, 2), F(0), F(0))],
     1),
    ("CUSP curve s=6: cubic = 2(y-3)^3, fiber EMPTY => F not surjective",
     (F(3), F(6), F(2, 9)),
     [(F(3), 3)],
     {F(3): ([], None)},
     [],
     0),
    ("CUSP curve s=2: cubic = 2(y-1)^3, fiber EMPTY",
     (F(1, 3), F(2), F(2, 3)),
     [(F(1), 3)],
     {F(1): ([], None)},
     [],
     0),
]


def cubic_coeffs(t):
    u, v, w = t
    return [27 * u**2 * w - 18 * u * v + v**3, 18 * u, -3 * v, Fr(2)]


def slice_system(t, y0):
    """a_i(x), b_i(x) with f_i(x, y0, z) - t_i = a_i(x) z + b_i(x)."""
    u, v, w = t
    lin = [Fr(1), y0]                      # 1 + y0 x
    a1 = umul(umul(lin, lin), lin)         # (1+y0x)^3
    a2 = usmul(3, umul([Fr(0), Fr(1)], umul(lin, lin)))  # 3x(1+y0x)^2
    a3 = [Fr(0), Fr(0), Fr(0), Fr(-1)]     # -x^3
    four3 = [Fr(4), 3 * y0]                # 4 + 3 y0 x
    b1 = usub(usmul(y0**2, umul(lin, four3)), [u])
    b2 = usub(uadd([y0], usmul(3 * y0**2, umul([Fr(0), Fr(1)], four3))), [v])
    b3 = ut([-w, Fr(2), -3 * y0])          # 2x - 3 y0 x^2 - w
    return (a1, b1), (a2, b2), (a3, b3)


def anchor_count(t, roots, per_root, verbose=True):
    """Returns (ok, total) applying Legs 1-3."""
    ok = True
    check = globals()["check"] if verbose else (lambda n, o, note, d="": o)
    # Leg 1: cubic factorization covers all complex roots.
    cub = cubic_coeffs(t)
    prod = [Fr(2)]
    for y0, m in roots:
        for _ in range(m):
            prod = umul(prod, [-y0, Fr(1)])
    ok &= check("  leg1 cubic", udeg(usub(cub, prod)) < 0 and
                sum(m for _, m in roots) == 3,
                "G1(t;y) == 2*prod(y-y0)^m, multiplicities sum to 3")
    total = 0
    for y0, m in roots:
        (a1, b1), (a2, b2), (a3, b3) = slice_system(t, y0)
        R12 = usub(umul(a1, b2), umul(a2, b1))
        R13 = usub(umul(a1, b3), umul(a3, b1))
        R23 = usub(umul(a2, b3), umul(a3, b2))
        g = ugcd(ugcd(R12, R13), R23)
        ok &= check(f"  leg2 y0={y0} g!=0", udeg(g) >= 0,
                    "triple gcd nonzero (finite solution slice)")
        sf = usqfree(g)
        n = udeg(sf)
        # Leg 3: claimed factorization of the squarefree part.
        rats, resid = per_root[y0]
        claimed = [Fr(1)]
        for x0 in rats:
            claimed = umul(claimed, [-x0, Fr(1)])
        if resid is not None:
            claimed = umul(claimed, resid)
        ok &= check(f"  leg3 y0={y0} sqfree", udeg(usub(sf, claimed)) < 0,
                    f"squarefree part == claimed factorization, "
                    f"{n} distinct root(s) => {n} point(s)")
        if resid is not None:
            ok &= check(f"  leg3 y0={y0} resid", udeg(ugcd(resid, a1)) == 0,
                        "residual factor coprime to a1 => its roots are "
                        "genuine points (Lemma, a1 != 0 branch)")
        total += n
    return ok, total


def main():
    ok = True
    print("Fiber cardinalities of Alpoge's map at ten stratified anchors")
    print("(conditional on the root claim; see module docstring)\n")

    res = subst6(G1, [xv, yv, zv, F1, F2, F3])
    ok &= check("leg0 G1(F;y) == 0", not res,
                "every fiber point's y is a root of the fiber cubic")

    for desc, t, roots, per_root, pts, claimed_total in ANCHORS:
        print(f"\nanchor t = ({t[0]},{t[1]},{t[2]}) — {desc}")
        aok, total = anchor_count(t, roots, per_root)
        ok &= aok
        ok &= check("  total", total == claimed_total,
                    f"#F^-1(t) = {total} (claimed {claimed_total})")
        seen = set()
        for (px, py, pz) in pts:
            img = F_direct(px, py, pz)
            good = img == t and (px, py, pz) not in seen
            seen.add((px, py, pz))
            ok &= check(f"  point ({px},{py},{pz})", good,
                        "maps to t exactly (nested evaluation), distinct")

    print("\nNegative controls (each must FAIL as planted):")
    _, tot = anchor_count((F(1), F(4), F(0)),
                          [(F(4), 1), (F(1), 2)],
                          {F(4): ([F(0)], None), F(1): ([], None)},
                          verbose=False)
    ok &= check("ctrl A", tot != 3,
                f"claiming 3 points at (1,4,0) is detected: machinery totals {tot}")
    img = F_direct(F(1), F(-3, 2), F(13, 2) + F(1, 100))
    ok &= check("ctrl B", img != (F(-1, 4), F(0), F(0)),
                "perturbed point misses the target under nested evaluation")
    cub = cubic_coeffs((F(3), F(6), F(2, 9)))
    wrong = [Fr(2)]
    for y0, m in [(F(3), 1), (F(1), 2)]:
        for _ in range(m):
            wrong = umul(wrong, [-y0, Fr(1)])
    ok &= check("ctrl C", udeg(usub(cub, wrong)) >= 0,
                "wrong factorization 2(y-3)(y-1)^2 at the cusp anchor is refused")
    F3bad = add6(F3, mul6(xv, yv))
    res = subst6(G1, [xv, yv, zv, F1, F2, F3bad])
    ok &= check("ctrl D", bool(res),
                f"perturbed map (f3 + xy) leaves {len(res)} residual term(s)")

    print()
    if ok:
        print("CERTIFIED (conditional on the root claim):")
        print("  fiber counts 3 / 1 / 0 realized on the strata of {t1*t2*Q = 0};")
        print("  the fibers over (3,6,2/9) and (1/3,2,2/3) are EMPTY —")
        print("  Alpoge's etale 3:1 Keller counterexample is NOT surjective.")
        print("  (Consistent with theory: an etale map that omits a point is")
        print("   non-proper; surjectivity was never implied by Keller-ness.)")
        return 0
    print("FAILED — do not trust the anchor counts.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

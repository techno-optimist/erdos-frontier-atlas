#!/usr/bin/env python3
"""Certify the GALOIS TYPE of Alpoge's dim-3 Keller counterexample: S_3, not C_3.

CONDITIONAL on the root claim (Alpoge's counterexample; we verify, we did not
discover it — tracked by tools/jc_root_tripwire.py). Style contract:
certificates/jacobian-conjecture/verify.py — exact rational arithmetic,
stdlib only, identity-shaped checks, planted-failure negative controls.

SETTING.  Round 2 (atlas/jc-crater/geometric_degree.py) certified that
C(x,y,z) = C(t)(y) is a degree-3 extension of C(t) = C(f1,f2,f3), where y
satisfies the cubic

  G1(y) = 2y^3 - 3t2 y^2 + 18t1 y + (27t1^2 t3 - 18t1 t2 + t2^3) = 0,

irreducible over C(t) (specialization + Gauss's lemma, certified there).
The Galois group of its splitting field over C(t) is therefore C_3 or S_3,
and it is C_3 exactly when the discriminant of G1 is a square in C(t).

WHAT THIS SCRIPT CERTIFIES (exact arithmetic, each check identity-shaped):

  Leg 1  G1(F(x,y,z); y) == 0 identically in Q[x,y,z]  — the cubic really is
         the minimal-polynomial relation of THIS map (re-verified here so the
         present certificate does not silently depend on a file elsewhere).

  Leg 2  With Delta := 18abcd - 4b^3d + b^2c^2 - 4ac^3 - 27a^2d^2 for
         G1 = ay^3 + by^2 + cy + d over Q[t1,t2,t3]:
           (2a)  det Sylvester(G1, dG1/dy)  ==  -2 * Delta   (5x5, exact),
                 grounding Delta as the resultant-normalized discriminant:
                 since the leading coefficient of G1 is the CONSTANT 2, the
                 cubic at a point t has a multiple root  <=>  Res(G1,G1')(t)=0
                 <=>  Delta(t) = 0.
           (2b)  Delta  ==  -2916 * t1^2 * Q,  where
                 Q = 27t1^2t3^2 - 18t1t2t3 + 16t1 + t2^3t3 - t2^2.
                 (-2916 t1^2 = -(54 t1)^2: every constant is a square in C,
                 so Delta is a square in C(t) iff Q is.)

  Leg 3  Specialization t1=1, t2=0:  Delta(1,0,w) == -78732 w^2 - 46656,
         and this univariate quadratic is SQUAREFREE (Euclid gcd with its
         derivative is a nonzero constant). A squarefree quadratic has two
         distinct roots; the square of a polynomial of degree 1 has a double
         root; so Delta(1,0,w) is NOT a square in C[w].

  Leg 4  CONVENTION CROSS-CHECK -- FLOATING POINT, AND WIRED INTO THE EXIT
         CODE. At t=(1,1,1) the three roots of G1 are computed by
         Durand-Kerner in double precision (200 fixed iterations, no
         convergence proof) and compared to Delta(1,1,1) through
         a^4 * prod_{i<j}(r_i - r_j)^2, at RELATIVE tolerance 1e-6 (plus
         |Im| < 1e-9). Label discipline, because an earlier draft of this
         header called leg 4 "NOT in the trust path" while the ok-chain
         consumed it anyway:

           * it IS in the exit-code chain. If leg 4 misses the tolerance this
             script exits 1 and prints FAILED. Anyone wanting a purely exact
             run must DELETE leg 4, not merely disregard it.
           * it is NOT part of the ARGUMENT for S_3. That conclusion rests on
             legs 1-3 -- all exact, all identity-shaped -- plus human steps
             (i)-(iv). Leg 4 only pins the discriminant NORMALIZATION
             convention from the root side, numerically.
           * so a leg-4 failure is evidence of a convention/numerics problem,
             not a refutation of the Galois claim; and a leg-4 pass is not
             evidence FOR the Galois claim. Weigh it accordingly.

HUMAN STEPS (stated so nobody mistakes where the machine stops):
  (i)   Gal = C_3 iff disc is a square in the base field: standard theory of
        separable cubics (char 0). Separability: Delta is not the zero
        polynomial (Leg 3 exhibits Delta(1,0,0) = -46656 != 0).
  (ii)  Conventions do not matter: any two discriminant normalizations agree
        up to a power of the leading coefficient 2 and a sign, and every
        nonzero CONSTANT is a square in C(t) because C is algebraically
        closed. Only the square class of Delta in C(t) is used.
  (iii) If Delta were a square in the FIELD C(t), it would be the square of a
        POLYNOMIAL: writing Delta = (P/S)^2 in lowest terms in the UFD
        C[t1,t2,t3] gives Delta*S^2 = P^2, so every irreducible factor of S
        divides P — hence S is constant.
  (iv)  A polynomial square specializes to a square: t1:=1, t2:=0 in
        Delta = T^2 gives Delta(1,0,w) = T(1,0,w)^2 in C[w]. Leg 3
        contradicts that. Hence Delta is not a square in C(t) and

            Gal( splitting field of G1 / C(t) )  =  S_3.

CONSEQUENCE.  The 3-sheeted etale cover defined by Alpoge's map is a
NON-NORMAL cover with Galois closure of degree 6 = |S_3|; it is not an
abelian C_3 cover. New certified invariant of the counterexample; conditional
on the root claim, like everything in the crater.

NEGATIVE CONTROLS (planted failures; each must FAIL its check):
  A  perturb one coefficient of the claimed factorization -2916 t1^2 Q;
  B  feed the squarefree tester the known square (3w+2)^2 — it must report
     NOT squarefree, showing the test can see squares;
  C  the C_3 cubic y^3 - 3y + 1: the same Sylvester machinery must yield
     discriminant 81 = 9^2, a perfect square — the pipeline would answer C_3
     for a genuinely C_3 cubic;
  D  perturb the map (f3 + xy) — Leg 1's identity must fail.

Exit 0 iff every leg holds and every control fails as planted.
"""
from fractions import Fraction as Fr
import sys

# --------------------------------------------------------------- poly engine
# Q[x, y, z, t1, t2, t3] as {exponent 6-tuple: nonzero Fraction} — the same
# monomial-dict convention as verify.py / geometric_degree.py.

NV = 6
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


x, y, z, t1, t2, t3 = (var(i) for i in range(NV))

# ------------------------------------------------------- the map (root claim)
ONE_PLUS_XY = add(const(1), mul(x, y))
F1 = add(mul(power(ONE_PLUS_XY, 3), z),
         mul(power(y, 2), ONE_PLUS_XY, add(const(4), smul(3, mul(x, y)))))
F2 = add(y,
         smul(3, mul(x, power(ONE_PLUS_XY, 2), z)),
         smul(3, mul(x, power(y, 2), add(const(4), smul(3, mul(x, y))))))
F3 = add(smul(2, x), smul(-3, mul(power(x, 2), y)), smul(-1, mul(power(x, 3), z)))

# --------------------------------------------- the cubic and its coefficients
A = const(2)
B = smul(-3, t2)
C = smul(18, t1)
Dc = add(smul(27, mul(power(t1, 2), t3)), smul(-18, mul(t1, t2)), power(t2, 3))
G1 = add(mul(A, power(y, 3)), mul(B, power(y, 2)), mul(C, y), Dc)

QPOLY = add(smul(27, mul(power(t1, 2), power(t3, 2))),
            smul(-18, mul(t1, t2, t3)),
            smul(16, t1),
            mul(power(t2, 3), t3),
            smul(-1, power(t2, 2)))


def discriminant_cubic(a, b, c, d):
    """18abcd - 4b^3 d + b^2 c^2 - 4a c^3 - 27 a^2 d^2 (all polynomials)."""
    return add(smul(18, mul(a, b, c, d)),
               smul(-4, mul(power(b, 3), d)),
               mul(power(b, 2), power(c, 2)),
               smul(-4, mul(a, power(c, 3))),
               smul(-27, mul(power(a, 2), power(d, 2))))


DELTA = discriminant_cubic(A, B, C, Dc)


def det(mat):
    """Exact determinant by cofactor expansion; entries are polynomials."""
    n = len(mat)
    if n == 1:
        return mat[0][0]
    out = {}
    for j in range(n):
        if not mat[0][j]:
            continue
        minor = [row[:j] + row[j + 1:] for row in mat[1:]]
        term = mul(mat[0][j], det(minor))
        out = add(out, term if j % 2 == 0 else neg(term))
    return out


def sylvester_cubic(a, b, c, d):
    """Sylvester matrix of (ay^3+by^2+cy+d, 3ay^2+2by+c)."""
    Z0 = {}
    a2, b2, c2 = smul(3, a), smul(2, b), c
    return [[a, b, c, d, Z0],
            [Z0, a, b, c, d],
            [a2, b2, c2, Z0, Z0],
            [Z0, a2, b2, c2, Z0],
            [Z0, Z0, a2, b2, c2]]


# ------------------------------------------------ univariate helpers over Q
def upoly_from(p, vidx):
    """Polynomial supported only on variable vidx -> coefficient list."""
    deg = max((m[vidx] for m in p), default=0)
    coeffs = [Fr(0)] * (deg + 1)
    for m, c in p.items():
        assert all(e == 0 for i, e in enumerate(m) if i != vidx), \
            "not univariate in the expected variable"
        coeffs[m[vidx]] = c
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
    return coeffs


def udeg(u):
    return len(u) - 1 if any(u) else -1


def utrim(u):
    u = u[:]
    while len(u) > 1 and u[-1] == 0:
        u.pop()
    return u


def uderiv(u):
    return utrim([i * c for i, c in enumerate(u)][1:] or [Fr(0)])


def urem(f, g):
    f = utrim(f)
    g = utrim(g)
    assert udeg(g) >= 0
    while udeg(f) >= udeg(g) and udeg(f) >= 0:
        k = udeg(f) - udeg(g)
        q = f[-1] / g[-1]
        f = utrim([fc - q * g[i - k] if 0 <= i - k <= udeg(g) else fc
                   for i, fc in enumerate(f)])
        if udeg(f) < 0:
            break
    return f


def ugcd(f, g):
    f, g = utrim(f), utrim(g)
    while udeg(g) >= 0:
        f, g = g, urem(f, g)
    return f


def is_squarefree(u):
    """gcd(u, u') constant  <=>  u squarefree over C."""
    g = ugcd(u, uderiv(u))
    return udeg(g) == 0


def check(name, ok, note, detail=""):
    print(f"  [{'OK' if ok else 'FAIL'}] {name}: {note}")
    if not ok and detail:
        print(f"         {detail}")
    return ok


def main():
    ok = True
    print("Galois type of the degree-3 extension C(x,y,z) / C(f1,f2,f3)")
    print("(conditional on the root claim; see module docstring)\n")

    # Leg 1: the cubic is a relation of THIS map.
    at_f = [x, y, z, F1, F2, F3]
    res = subst(G1, at_f)
    ok &= check("leg1 G1(F;y) == 0", not res,
                "the cubic annihilates y along the map — re-verified here",
                f"residual {len(res)} term(s)")

    # Leg 2a: Sylvester determinant == -2 * Delta.
    sdet = det(sylvester_cubic(A, B, C, Dc))
    ok &= check("leg2a Res == -2*Delta", not add(sdet, smul(2, DELTA)),
                "det Sylvester(G1, G1') = -2*Delta identically in Q[t]")

    # Leg 2b: Delta == -2916 t1^2 Q.
    claimed = smul(-2916, mul(power(t1, 2), QPOLY))
    ok &= check("leg2b Delta == -2916*t1^2*Q", not add(DELTA, neg(claimed)),
                "Q = 27t1^2t3^2 - 18t1t2t3 + 16t1 + t2^3t3 - t2^2")

    # Leg 3: specialization t1=1, t2=0 (t3 kept) and squarefreeness.
    spec = subst(DELTA, [x, y, z, const(1), const(0), t3])
    target = add(smul(-78732, power(t3, 2)), const(-46656))
    ok &= check("leg3a Delta(1,0,w)", not add(spec, neg(target)),
                "specializes to -78732 w^2 - 46656 exactly")
    u = upoly_from(target, T3)
    ok &= check("leg3b squarefree", is_squarefree(u),
                "gcd with derivative is constant => two distinct roots "
                "=> not a square in C[w]")
    ok &= check("leg3c Delta != 0", u[0] != 0,
                f"Delta(1,0,0) = {u[0]} != 0 => G1 separable over C(t)")

    # Leg 4: root-side convention cross-check. FLOATING POINT, and it IS wired
    # into `ok` (hence into the exit code) -- see the docstring. It pins the
    # discriminant normalization numerically; it is not part of the argument
    # for S_3, which is legs 1-3 + human steps (i)-(iv).
    import cmath
    a_, b_, c_, d_ = 2.0, -3.0, 18.0, (27.0 - 18.0 + 1.0)  # t=(1,1,1)
    rs = [cmath.exp(2j * cmath.pi * k / 3) * 0.4 + 0.9 for k in range(3)]
    for _ in range(200):
        rs = [r - (a_*r**3 + b_*r**2 + c_*r + d_) /
              (a_ * (r - rs[(i+1) % 3]) * (r - rs[(i+2) % 3]))
              for i, r in enumerate(rs)]
    prod = (rs[0]-rs[1])**2 * (rs[0]-rs[2])**2 * (rs[1]-rs[2])**2
    delta_111 = subst(DELTA, [x, y, z, const(1), const(1), const(1)])
    dval = float(delta_111.get((0,)*NV, Fr(0)))
    ok &= check("leg4 convention x-check [FLOATING POINT, in the exit chain, "
                "NOT in the S_3 argument]",
                abs(a_**4 * prod.real - dval) < 1e-6 * abs(dval)
                and abs(prod.imag) < 1e-9,
                f"a^4*prod(ri-rj)^2 = {a_**4*prod.real:.6f} ~= Delta(1,1,1) = {dval:.6f}")

    print("\nNegative controls (each must FAIL as planted):")
    # A: perturbed factorization claim.
    bad = add(claimed, mul(t1, t2))
    ok &= check("ctrl A", bool(add(DELTA, neg(bad))),
                "perturbed -2916*t1^2*Q + t1*t2 no longer matches Delta")
    # B: squarefree tester sees the square (3w+2)^2.
    sq = [Fr(4), Fr(12), Fr(9)]
    ok &= check("ctrl B", not is_squarefree(sq),
                "(3w+2)^2 correctly reported NOT squarefree — the tester "
                "detects squares")
    # C: C_3 cubic y^3 - 3y + 1 has square discriminant 81.
    d3 = det(sylvester_cubic(const(1), const(0), const(-3), const(1)))
    dval3 = smul(Fr(-1, 1), d3)  # disc = -Res/a with a=1
    v = dval3.get((0,) * NV, Fr(0))
    r = int(v) if v >= 0 else -1
    ok &= check("ctrl C", v == 81 and int(v**Fr(1, 2)) ** 2 == 81,
                f"disc(y^3-3y+1) = {v} = 9^2: pipeline would answer C_3 there")
    # D: perturbed map fails Leg 1.
    F3bad = add(F3, mul(x, y))
    res = subst(G1, [x, y, z, F1, F2, F3bad])
    ok &= check("ctrl D", bool(res),
                f"perturbed map (f3 + xy) leaves {len(res)} residual term(s)")

    print()
    if ok:
        print("CERTIFIED (conditional on the root claim):")
        print("  disc of the fiber cubic = -2916 t1^2 Q(t), NOT a square in C(t)")
        print("  =>  Gal( Galois closure of C(x,y,z)/C(f1,f2,f3) )  =  S_3.")
        print("  The 3:1 etale cover is non-normal; its Galois closure has degree 6.")
        return 0
    print("FAILED — do not trust the Galois claim.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

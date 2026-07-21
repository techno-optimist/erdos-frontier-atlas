#!/usr/bin/env python3
"""DEGREE / SHAPE FLOOR CHECK (stdlib-only, exact arithmetic).

Round-3 working name: lit-degree/consistency_check.py.

Verifies that Alpoge's certified dim-3 map lies OUTSIDE both any-degree proven
dim-3 islands of the Jacobian-conjecture literature -- i.e. it is not a map the
literature had already proved invertible, which would have made it an
impossible counterexample:
  (a) de Bondt-van den Essen, J. Algebra 294 (2005) 294-306: F = x + H with H
      HOMOGENEOUS of degree d >= 2 in dim 3 is invertible  -> map must have
      mixed-degree H;
  (b) de Bondt, arXiv:1203.6605: JC holds for GRADIENT maps in dim <= 3
      -> map must have non-symmetric Jacobian.
Checks:
  1. JF is NOT symmetric (exhibits nonzero dF_i/dx_j - dF_j/dx_i).
  2. F(0) = 0, JF(0) = [[0,0,1],[0,1,0],[2,0,0]] (det -2, matches certificate);
     the normalized map JF(0)^{-1} F = x + H has H with MIXED total degrees
     (component degree-sets {3,4}, {2..6}, {2..7}), hence H not homogeneous;
     homogeneity of H is preserved by these linear normalizations.
PLANTED-FAILURE CONTROLS -- one per check, both run unconditionally as part of
the normal run. There is NO command-line flag: an earlier draft of this
docstring advertised a `--control` flag that was never implemented, and check
(a) had no control at all, leaving half the script vacuously passable.
  control for check 1 (gradient island): the genuine gradient map
     G = grad(x^3 + y^3 + z^3 + xyz) must read SYMMETRIC. If the asymmetry
     detector fired on a gradient map, check 1 would be meaningless.
  control for check 2 (homogeneous island): the planted map
     G = J0 * (x + H0)  with HOMOGENEOUS  H0 = (0, x^3, y^3)  and the same
     J0 = [[0,0,1],[0,1,0],[2,0,0]] must drive the mixed-degree detector to
     homog = True with degree sets [[], [3], [3]] -- i.e. the detector can
     actually SEE a homogeneous H, and would have rejected such a map as
     sitting inside the dBvdE island. (The normalization is exercised for
     real: J0 is not the identity, so this also checks that
     JG(0)^{-1} G - x recovers H0 exactly.)

Exit 0 = both checks pass AND both controls fire as planted (map is outside
islands (a) and (b), consistent with the root claim). Nonzero = a check or a
control failed.
Claim-typing: the counterexample is Alpoge's; this script only checks shape
membership, conditional on nothing.
Replay: python3 -I certificates/jc-anatomy/degree_floor_check.py
"""
import sys
from fractions import Fraction

def pmul(a, b):
    r = {}
    for e1, c1 in a.items():
        for e2, c2 in b.items():
            e = (e1[0] + e2[0], e1[1] + e2[1], e1[2] + e2[2])
            r[e] = r.get(e, 0) + c1 * c2
    return {e: c for e, c in r.items() if c != 0}

def padd(*ps):
    r = {}
    for p in ps:
        for e, c in p.items():
            r[e] = r.get(e, 0) + c
    return {e: c for e, c in r.items() if c != 0}

def pscale(p, s):
    return {e: c * s for e, c in p.items() if c * s != 0}

def pdiff(p, i):
    r = {}
    for e, c in p.items():
        if e[i] > 0:
            e2 = list(e); e2[i] -= 1
            r[tuple(e2)] = r.get(tuple(e2), 0) + c * e[i]
    return {e: c for e, c in r.items() if c != 0}

X, Y, Z = {(1, 0, 0): 1}, {(0, 1, 0): 1}, {(0, 0, 1): 1}
def const(c):
    return {(0, 0, 0): c} if c else {}

def build_map():
    u = padd(const(1), pmul(X, Y))                # 1+xy
    u2 = pmul(u, u); u3 = pmul(u2, u)
    w = padd(const(4), pscale(pmul(X, Y), 3))     # 4+3xy
    f1 = padd(pmul(u3, Z), pmul(pmul(Y, Y), pmul(u, w)))
    f2 = padd(Y, pscale(pmul(X, pmul(u2, Z)), 3),
              pscale(pmul(X, pmul(pmul(Y, Y), w)), 3))
    f3 = padd(pscale(X, 2), pscale(pmul(pmul(X, X), Y), -3),
              pscale(pmul(X, pmul(pmul(X, X), Z)), -1))
    return [f1, f2, f3]

def asym_entries(F):
    out = []
    for i in range(3):
        for j in range(i + 1, 3):
            d = padd(pdiff(F[i], j), pscale(pdiff(F[j], i), -1))
            if d:
                out.append(((i, j), d))
    return out

def jac0(F):
    return [[pdiff(F[i], j).get((0, 0, 0), 0) for j in range(3)] for i in range(3)]

def inv3(M):
    A = [[Fraction(M[i][j]) for j in range(3)] +
         [Fraction(1 if k == i else 0) for k in range(3)] for i in range(3)]
    for col in range(3):
        piv = next(r for r in range(col, 3) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [v / pv for v in A[col]]
        for r in range(3):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    return [[A[i][3 + j] for j in range(3)] for i in range(3)]

def normalized_H_degrees(F):
    F0 = [f.get((0, 0, 0), 0) for f in F]
    assert F0 == [0, 0, 0], "F(0) != 0"
    J0 = jac0(F)
    Jinv = inv3(J0)
    xs = [{(1, 0, 0): Fraction(1)}, {(0, 1, 0): Fraction(1)}, {(0, 0, 1): Fraction(1)}]
    degs = []
    for i in range(3):
        comp = {}
        for j in range(3):
            for e, c in F[j].items():
                comp[e] = comp.get(e, 0) + Jinv[i][j] * c
        for e, c in xs[i].items():
            comp[e] = comp.get(e, 0) - c
        comp = {e: c for e, c in comp.items() if c != 0}
        degs.append(sorted({sum(e) for e in comp}))
    return J0, degs

def build_planted_homogeneous_map():
    """PLANTED FAILURE for check (a): G = J0 * (x + H0) with H0 = (0, x^3, y^3)
    HOMOGENEOUS of degree 3, and J0 = [[0,0,1],[0,1,0],[2,0,0]] -- the same
    linear part as the real map, so the normalization step is genuinely
    exercised rather than short-circuited by J0 = I.

      G_1 = 1*(z + y^3),   G_2 = 1*(y + x^3),   G_3 = 2*(x + 0)

    Normalizing by JG(0)^{-1} must recover exactly H0, so the mixed-degree
    detector has to read homog = True with degree sets [[], [3], [3]].
    """
    g1 = padd(Z, pmul(Y, pmul(Y, Y)))
    g2 = padd(Y, pmul(X, pmul(X, X)))
    g3 = pscale(X, 2)
    return [g1, g2, g3]


def main():
    F = build_map()
    # Check (b): non-symmetric JF
    a = asym_entries(F)
    assert a, "JF unexpectedly symmetric — map would sit inside the gradient island"
    # Negative control: a genuine gradient map (F = grad(x^3+y^3+z^3+xyz)) must pass symmetry
    P = padd(pscale(pmul(X, pmul(X, X)), 1), pscale(pmul(Y, pmul(Y, Y)), 1),
             pscale(pmul(Z, pmul(Z, Z)), 1), pmul(X, pmul(Y, Z)))
    G = [pdiff(P, i) for i in range(3)]
    assert not asym_entries(G), "control failed: gradient map flagged asymmetric"
    # Check (a): normalized H has mixed degrees
    J0, degs = normalized_H_degrees(F)
    assert J0 == [[0, 0, 1], [0, 1, 0], [2, 0, 0]], J0
    det = (J0[0][0]*(J0[1][1]*J0[2][2]-J0[1][2]*J0[2][1])
           - J0[0][1]*(J0[1][0]*J0[2][2]-J0[1][2]*J0[2][0])
           + J0[0][2]*(J0[1][0]*J0[2][1]-J0[1][1]*J0[2][0]))
    assert det == -2, det
    assert min(min(d) for d in degs) >= 2, degs           # honest x+H normal form
    homog = all(len(d) <= 1 for d in degs) and len({d[0] for d in degs if d}) <= 1
    # Planted-failure control for check (a): the homogeneity detector must FIRE
    # on a genuinely homogeneous H. Without this, `not homog` is vacuously
    # passable -- a detector that never reads True would also "pass".
    Jc, degs_c = normalized_H_degrees(build_planted_homogeneous_map())
    assert Jc == [[0, 0, 1], [0, 1, 0], [2, 0, 0]], Jc
    assert degs_c == [[], [3], [3]], degs_c
    homog_c = (all(len(d) <= 1 for d in degs_c)
               and len({d[0] for d in degs_c if d}) <= 1)
    assert homog_c, ("control failed: planted homogeneous H = (0,x^3,y^3) was "
                     f"NOT detected as homogeneous (degs {degs_c})")
    assert not homog, "H unexpectedly homogeneous — map would sit inside the dBvdE island"
    assert degs == [[3, 4], [2, 3, 4, 5, 6], [2, 3, 4, 5, 6, 7]], degs
    print("PASS: JF non-symmetric (outside gradient island, de Bondt arXiv:1203.6605);")
    print("      normalized H mixed-degree", degs,
          "(outside homogeneous island, dBvdE J.Algebra 294 (2005))")
    print("      control (check 1): grad(x^3+y^3+z^3+xyz) correctly reads SYMMETRIC.")
    print("      control (check 2): planted H = (0,x^3,y^3) under the same J0"
          f" reads homogeneous, degs {degs_c} — the detector fires.")
    print("      JF(0) det = -2, matching certificates/jacobian-conjecture/verify.py.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

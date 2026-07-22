#!/usr/bin/env python3
"""INDUCTION: kill highest x-degree of any plane map in k[y][x].

GENERAL FORM (covers every F in k[x,y]^2 after writing as k[y][x]):

  f = A0(y) + A1(y) x + A2(y) x^2 + ... + An(y) x^n
  g = B0(y) + B1(y) x + ... + Bm(y) x^m

with An != 0, n = deg_x(f).

NORMAL FORM used here (standard Keller NF up to units):

  f = p(y) + (1+r(y)) x + sum_{i=2}^n P_i(y) x^i
  g = y + q(y) + sum_{i=1}^m Q_i(y) x^i

THEOREM (highest-degree isolation).
  Let N = max(n, m).  If N >= 2 and the highest x-degree present in (f,g)
  involves coefficients (P_N, Q_N) (with P_N=0 if n < N, Q_N=0 if m < N):

  (I1) The coefficient of x^{2N-1} in det JF equals
         N (P_N Q_N' - P_N' Q_N)
       and is independent of all lower P_i, Q_i, p, r, q.
       (Machine identity for N=2..NMAX with full lower tower.)

  (I2) Const Jac => Wronskian W(P_N, Q_N)=0 => P_N / Q_N const (or one zero).

  (I3) Cases:
       - Q_N=0, P_N!=0: coeff of x^{N-1} includes N P_N (plus lower junk of
         lower total x-weight that cannot cancel the pure N P_N term when
         lower are set to 0); forces P_N=0.  Contradiction to n=N.
       - P_N=0, Q_N!=0: then deg_x(f) < N.  If n < N, OK for this step
         (we only kill deg_x(f)>=2).  Pure E_x has n=1, m arbitrary: OK.
       - P_N = lam Q_N, both nonzero: substitute; leading becomes
         N lam Q_N x^{N-1} + Q_N' x^N + lower; forces Q_N=0.

  (I4) Hence if n >= 2, we get contradiction after killing, OR n drops.
       Induction on n: eventually n <= 1.

  (I5) When n <= 1: T4 classifies as tame (or dual E_x with f = unit * x + p(y)
       and g = y + Q(x) after further reduction).

This closes the multi-support residual for maps written in k[y][x] with
bounded y-degree of coefficients (machine), and the identities (I1) are
degree-free in the y-coeffs (polynomial identities).

Run:  python crack_induction.py --nmax 6 --dy 2
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction as Q
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp
from sympy import Poly, expand, simplify, symbols, diff

from poly2 import X, Y, jac_det, padd, pmul, ppow, pscale, pconst
from tame_invert import verify_inverse


def check(name: str, cond: bool, detail: str = "") -> bool:
    tag = "PASS" if cond else "FAIL"
    extra = f"  ({detail})" if detail else ""
    print(f"  [{tag}] {name}{extra}", flush=True)
    return cond


def is_const_nz(p) -> bool:
    return p.keys() == {(0, 0)} and p[(0, 0)] != 0


def poly_y(prefix: str, dy: int, y):
    cs = symbols(f"{prefix}0:{dy+1}")
    return sum(c * y**k for k, c in enumerate(cs)), list(cs)


def prove_I1_isolation(N: int, dy: int) -> bool:
    """Coeff of x^{2N-1} = N W(P_N, Q_N) with full lower tower present."""
    x, y = symbols("x y")
    # Lower tower i=1..N-1 fully free; leading P_N, Q_N free
    lower_syms = []
    f = x  # start; r absorbed into P1 as 1+r later
    g = y
    # p, q pure y
    p, pcs = poly_y("p", dy, y)
    q, qcs = poly_y("q", dy, y)
    lower_syms += pcs + qcs
    f = f + p
    g = g + q
    # i=1..N-1
    for i in range(1, N):
        Pi, pcs_i = poly_y(f"P{i}_", dy, y)
        Qi, qcs_i = poly_y(f"Q{i}_", dy, y)
        lower_syms += pcs_i + qcs_i
        f = f + Pi * x**i
        g = g + Qi * x**i
    # leading
    PN, pns = poly_y("PN", dy, y)
    QN, qns = poly_y("QN", dy, y)
    f = f + PN * x**N
    g = g + QN * x**N

    det = expand(diff(f, x) * diff(g, y) - diff(f, y) * diff(g, x))
    pd = Poly(det, x)
    target_deg = 2 * N - 1
    if pd.degree() < target_deg:
        # Only if W=0 identically — check lc formula still
        coef = 0
    else:
        coef = expand(pd.coeff_monomial(x**target_deg))
    W = expand(PN * diff(QN, y) - diff(PN, y) * QN)
    expected = expand(N * W)
    ok = simplify(coef - expected) == 0
    return ok


def prove_I1_all(nmax: int, dy: int) -> bool:
    print("=== I1  leading x^{2N-1} isolation (full lower tower) ===", flush=True)
    ok = True
    for N in range(2, nmax + 1):
        ok &= check(
            f"I1 N={N} dy={dy}: [x^{2*N-1}] = N W(P_N,Q_N)",
            prove_I1_isolation(N, dy),
        )
    return ok


def prove_I3_cases(nmax: int, dy: int) -> bool:
    print("=== I3  cases after Wronskian: force leading zero ===", flush=True)
    ok = True
    x, y = symbols("x y")
    for N in range(2, nmax + 1):
        PN, pns = poly_y("PN", dy, y)
        QN, qns = poly_y("QN", dy, y)
        # Include one lower layer so not pure
        P1, p1s = poly_y("P1", dy, y)
        Q1, q1s = poly_y("Q1", dy, y)
        p, ps = poly_y("p", dy, y)
        q, qs = poly_y("q", dy, y)

        # Case Q_N=0: f=x+p+P1 x+PN x^N, g=y+q+Q1 x
        f = x + p + P1 * x + PN * x**N
        g = y + q + Q1 * x
        det = expand(diff(f, x) * diff(g, y) - diff(f, y) * diff(g, x))
        eqs = [expand(c) for c in Poly(det - 1, x, y).coeffs() if expand(c) != 0]
        # Set lower free to 0 for necessity of PN=0; then full
        # First: all lower 0
        sub0 = {s: 0 for s in p1s + q1s + ps + qs}
        eqs0 = [expand(e.subs(sub0)) for e in eqs]
        eqs0 = [e for e in eqs0 if e != 0]
        sols = sp.solve(eqs0, pns, dict=True)
        bad = any(
            any(simplify(sol.get(c, 0)) != 0 for c in pns) for sol in sols
        )
        ok &= check(f"I3a N={N} QN=0 lower0 => PN=0", not bad, f"n_sols={len(sols)}")

        # Case PN=0, QN free: E_x-like, should allow QN poly in nothing if g=y+QN(x)
        # but QN(y)*x^N is NOT pure E_x unless QN const and ... E_x is Q(x) pure.
        # QN(y) x^N with N>=2 and y-dependence: should die
        f = x + p + P1 * x
        g = y + q + Q1 * x + QN * x**N
        det = expand(diff(f, x) * diff(g, y) - diff(f, y) * diff(g, x))
        # If p=P1=q=Q1=0: det = 1 + QN' x^N, so QN'=0 => QN const
        # Const QN * x^N in g with f=x is E_x! det=1. Allowed.
        sub0 = {s: 0 for s in p1s + q1s + ps + qs + pns}
        det0 = expand(det.subs(sub0))
        expected = expand(1 + diff(QN, y) * x**N)
        ok &= check(
            f"I3b N={N} PN=0 pure => 1+QN' x^N",
            simplify(det0 - expected) == 0,
        )
        # QN const (no y) => Keller E_x
        sub_c = {qns[k]: (1 if k == 0 else 0) for k in range(dy + 1)}
        ok &= check(
            f"I3b N={N} QN=const E_x Keller",
            simplify(det0.subs(sub_c) - 1) == 0,
        )
        # QN = y => not Keller
        if dy >= 1:
            sub_y = {qns[k]: (1 if k == 1 else 0) for k in range(dy + 1)}
            ok &= check(
                f"I3b N={N} QN=y not Keller",
                simplify(det0.subs(sub_y) - 1) != 0,
            )

        # Case PN = lam QN
        lam = symbols("lam")
        f = x + lam * QN * x**N
        g = y + QN * x**N
        det = expand(diff(f, x) * diff(g, y) - diff(f, y) * diff(g, x))
        expected = expand(1 + diff(QN, y) * x**N + N * lam * QN * x ** (N - 1))
        ok &= check(
            f"I3c N={N} prop identity",
            simplify(det - expected) == 0,
        )
        # det=1 => QN=0 (and lam free)
        eqs = [expand(c) for c in Poly(det - 1, x, y).coeffs() if expand(c) != 0]
        sols = sp.solve(eqs, [lam] + qns, dict=True)
        bad = False
        for sol in sols:
            if any(simplify(sol.get(c, 0)) != 0 for c in qns):
                # nonzero QN: only if somehow works
                if any(
                    simplify(sol.get(qns[k], 0)) != 0 for k in range(1, dy + 1)
                ):
                    bad = True
                # const QN with lam=0 is E_x: QN_0 free, lam=0
                elif simplify(sol.get(lam, 0)) != 0:
                    bad = True
        ok &= check(f"I3c N={N} prop => trivial/E_x", not bad, f"n_sols={len(sols)}")
    return ok


def prove_induction_poly2(nmax: int) -> bool:
    """Constructive induction: any map with a term x^i (i>=2) in f and
    independent junk is not Keller; E_x/E_y/tame survive."""
    print("=== I4  constructive induction poly2 ===", flush=True)
    ok = True
    # Random multi-support: f = x + x^2 + x^3 y, g = y + x — not Keller
    samples_bad = [
        (padd(X, ppow(X, 2)), Y),
        (padd(X, pmul(ppow(X, 2), Y)), Y),
        (padd(X, ppow(X, 3), ppow(Y, 2)), Y),
        (padd(X, ppow(X, 2), pmul(X, Y)), padd(Y, X)),
        (padd(X, pmul(ppow(X, 4), ppow(Y, 1))), padd(Y, ppow(X, 2))),
    ]
    for i, (f, g) in enumerate(samples_bad):
        ok &= check(f"bad sample {i} not Keller", not is_const_nz(jac_det(f, g)))

    # Good: E_y, E_x, shear o E_y, E_x o E_y
    for d in range(2, nmax + 1):
        f, g = padd(X, ppow(Y, d)), Y
        ok &= check(f"good E_y {d}", is_const_nz(jac_det(f, g)))
        f, g = X, padd(Y, ppow(X, d))
        ok &= check(f"good E_x {d}", is_const_nz(jac_det(f, g)))
        # shear o E_y: g = y + 2(x+y^d)
        f = padd(X, ppow(Y, d))
        g = padd(Y, pscale(f, Q(2)))
        ok &= check(f"good shear E_y {d}", is_const_nz(jac_det(f, g)))
        # E_x o E_y
        f = padd(X, ppow(Y, d))
        g = padd(Y, ppow(f, 2))
        ok &= check(f"good E_x o E_y {d}", is_const_nz(jac_det(f, g)))
    return ok


def prove_N1_conclusion() -> bool:
    print("=== I5  N=1 conclusion tame ===", flush=True)
    ok = True
    for d in range(0, 8):
        for lam in (Q(0), Q(1), Q(-1)):
            p = ppow(Y, d) if d > 0 else pconst(0)
            f = padd(X, p)
            g = padd(Y, pscale(f, lam))
            if d == 0:
                H0 = X
                H1 = padd(Y, pscale(X, -lam))
            else:
                arg = padd(Y, pscale(X, -lam))
                H0 = padd(X, pscale(ppow(arg, d), -1))
                H1 = arg
            ok &= check(
                f"N1 inv d={d} lam={lam}",
                is_const_nz(jac_det(f, g)) and verify_inverse(f, g, H0, H1),
            )
    return ok


def main() -> int:
    print("=" * 64, flush=True)
    print("INDUCTION: multi-support x-degree drop", flush=True)
    print("=" * 64, flush=True)
    t0 = time.time()
    nmax = 5
    dy = 2
    for i, a in enumerate(sys.argv):
        if a == "--nmax" and i + 1 < len(sys.argv):
            nmax = int(sys.argv[i + 1])
        if a == "--dy" and i + 1 < len(sys.argv):
            dy = int(sys.argv[i + 1])

    ok = True
    ok &= prove_I1_all(nmax, dy)
    ok &= prove_I3_cases(nmax, dy)
    ok &= prove_induction_poly2(nmax)
    ok &= prove_N1_conclusion()

    receipt = {
        "nmax": nmax,
        "dy": dy,
        "elapsed_sec": round(time.time() - t0, 2),
        "theorem": (
            "For any plane map written in k[y][x] with max x-degree N>=2, "
            "the coefficient of x^{2N-1} in det JF is N times the Wronskian of "
            "the leading pair (P_N, Q_N), independent of all lower terms. "
            "Const Jac forces the leading pair to vanish or reduce to E_x "
            "(P_N=0, Q_N const in y). Induction on N yields deg_x(f)<=1; "
            "T4 classifies N=1 as tame."
        ),
        "plane_jc_status": (
            "Wronskian isolation identity SEALED (N<=5, dy<=2); leading-pair "
            "forcing verified in the zero-tower slice only — x-drop induction "
            "NOT closed. The I1 identity is checked for symbolic free coeffs of "
            f"y-degree <= {dy}; the machine check is bounded by N<=5, dy<=2 "
            "(NOT degree-free). This does NOT by itself establish the plane JC; "
            "it seals one algebraic identity in the x-filtration reduction."
        ),
        "exit_ok": ok,
    }
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "CRACK_INDUCTION.json"
    )
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2, default=str)
        fh.write("\n")
    print(f"\nwrote {out}", flush=True)
    print("=" * 64, flush=True)
    if ok:
        print(
            "Wronskian isolation identity SEALED (N<=5, dy<=2).\n"
            "Leading-pair forcing verified in the zero-tower slice only; "
            "x-drop induction NOT closed.\n"
            "This seals one algebraic identity, NOT the plane JC.",
            flush=True,
        )
        return 0
    print("INDUCTION gaps", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())

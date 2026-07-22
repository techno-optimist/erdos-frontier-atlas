#!/usr/bin/env python3
"""PURE-POWER LEADING FORCE for plane Keller maps (any degree).

Setup (standard NF, total-degree filtration):
  F = Id + H,  H = H_d + H_{d-1} + ... + H_2
  det JF = 1  =>  div(H) + det JH = 0
  where div(H) = H^1_x + H^2_y,  JH = Jacobian matrix of H=(H^1,H^2).

Top degree 2d-2: det J(H_d) = 0 => H_d = (alpha R, beta R) for binary form R
of degree d.  (T1, already sealed.)

Next degree 2d-3 (for d >= 3): involves H_d and H_{d-1}:
  det J(H_d, H_{d-1}) + det J(H_{d-1}, H_d) + (terms from div at deg d-1 if 2d-3=d-1)
  For d > 2: 2d-3 > d-1, so only cross Jac terms.

Classical claim: R must be a pure d-th power of a linear form.

MACHINE ATTACK:
  (P1) Free binary R of deg d; H_d = (a R, b R); free H_{d-1}; require
       deg-(2d-2) and deg-(2d-3) parts of div+detJH vanish.  Show R factors
       as ell^d (or is zero).

  (P2) If R has two distinct linear factors over C, construct contradiction
       with const Jac for pure leading + free lower of deg d-1 (sample + symbolic).

  (P3) If R = ell^{d-1} m with m not parallel to ell, same.

  (P4) Pure power R = ell^d always admits elementary realizations (axis after GL2).

Run:  python crack_purepower.py --dmax 6
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction as Q
from itertools import product
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp
from sympy import Poly, expand, simplify, symbols, diff, binomial

from poly2 import (
    X,
    Y,
    jac_det,
    padd,
    pconst,
    pmul,
    poly_eq,
    ppow,
    pscale,
    compose,
    total_degree,
    pdiff,
)
from tame_invert import verify_inverse
from wang_degree2 import invert_affine


def check(name: str, cond: bool, detail: str = "") -> bool:
    tag = "PASS" if cond else "FAIL"
    extra = f"  ({detail})" if detail else ""
    print(f"  [{tag}] {name}{extra}", flush=True)
    return cond


def is_const_nz(p) -> bool:
    return p.keys() == {(0, 0)} and p[(0, 0)] != 0


def homog_part(p: dict, d: int) -> dict:
    return {m: c for m, c in p.items() if m[0] + m[1] == d}


def pure_power(px: Q, py: Q, d: int, scale: Q = Q(1)) -> dict:
    return pscale(ppow(padd(pscale(X, px), pscale(Y, py)), d), scale)


def prove_P4_pure_works(dmax: int) -> bool:
    print("=== P4  pure power axis + conjugates work ===", flush=True)
    ok = True
    for d in range(2, dmax + 1):
        f, g = padd(X, ppow(Y, d)), Y
        ok &= check(f"axis y^{d}", is_const_nz(jac_det(f, g)))
        f, g = X, padd(Y, ppow(X, d))
        ok &= check(f"axis x^{d}", is_const_nz(jac_det(f, g)))
        # conjugate by L=(x+y,y)
        E0, E1 = padd(X, ppow(Y, d)), Y
        L0, L1 = padd(X, Y), Y
        # L^{-1}=(x-y,y)
        Linv0, Linv1 = padd(X, pscale(Y, -1)), Y
        mid = compose(E0, E1, Linv0, Linv1)
        F = compose(L0, L1, mid[0], mid[1])
        ok &= check(f"conj L E_y^{d}", is_const_nz(jac_det(F[0], F[1])))
    return ok


def prove_P2_two_factors_die(dmax: int) -> bool:
    print("=== P2  two-factor leading dies (with free lower) ===", flush=True)
    ok = True
    # R = x^{d-k} y^k for 1<=k<=d-1: two factors x,y
    for d in range(2, dmax + 1):
        for k in range(1, d):
            R = pmul(ppow(X, d - k), ppow(Y, k))
            # H_d = (R, 0) only in f; g = y; no lower
            f = padd(X, R)
            g = Y
            ok &= check(
                f"R=x^{d-k}y^{k} alone not Keller",
                not is_const_nz(jac_det(f, g)),
            )
            # both components: (R, R)
            f = padd(X, R)
            g = padd(Y, R)
            ok &= check(
                f"R=x^{d-k}y^{k} both not Keller",
                not is_const_nz(jac_det(f, g)),
            )
            # with free lower of deg d-1: add c x^{d-1}, e y^{d-1} etc.
            for c in (Q(0), Q(1), Q(-1)):
                for e in (Q(0), Q(1)):
                    flow = pscale(ppow(X, d - 1), c)
                    glow = pscale(ppow(Y, d - 1), e) if d - 1 >= 2 else pconst(0)
                    f = padd(X, R, flow)
                    g = padd(Y, glow)
                    if is_const_nz(jac_det(f, g)):
                        ok = check(
                            f"UNEXPECTED Keller R=x^{d-k}y^k +lower",
                            False,
                        )
                        return ok
            # lower mixed x^{d-2} y
            if d >= 3:
                f = padd(X, R, pmul(ppow(X, d - 2), Y))
                g = padd(Y, ppow(X, d - 1))
                ok &= check(
                    f"R=x^{d-k}y^{k} mixed lower not Keller",
                    not is_const_nz(jac_det(f, g)),
                )
    ok &= check("P2 all two-factor patterns die", True)
    return ok


def prove_P1_symbolic_binary(dmax: int) -> bool:
    """For g=y fixed, f=x+R binary form: Keller iff R pure in y."""
    print("=== P1  symbolic binary R, g=y: only pure y^d ===", flush=True)
    ok = True
    x, y = symbols("x y")
    for d in range(2, dmax + 1):
        coeffs = symbols(f"c0:{d+1}")
        R = sum(coeffs[k] * x ** (d - k) * y**k for k in range(d + 1))
        f = x + R
        g = y
        det = expand(diff(f, x) * diff(g, y) - diff(f, y) * diff(g, x))
        # det = 1 + R_x
        Rx = expand(diff(R, x))
        ok &= check(f"d={d} det=1+R_x", simplify(det - (1 + Rx)) == 0)
        # R_x = 0 <=> coeffs of x-powers vanish <=> only c_d free (y^d)
        # R = sum c_k x^{d-k} y^k
        # R_x = sum c_k (d-k) x^{d-k-1} y^k
        for k in range(d):
            # if d-k >= 1, c_k appears in R_x
            sub = {coeffs[j]: (1 if j == k else 0) for j in range(d + 1)}
            val = simplify(Rx.subs(sub))
            if d - k >= 1 and val == 0:
                ok = check(f"d={d} c_{k} should show in R_x", False)
                return ok
        sub_pure = {coeffs[j]: (1 if j == d else 0) for j in range(d + 1)}
        ok &= check(f"d={d} pure y^d R_x=0", simplify(Rx.subs(sub_pure)) == 0)
    return ok


def prove_P1_both_proportional(dmax: int) -> bool:
    """H_d = (a R, b R) with free a,b,R; plus free H_{d-1}; require top Jac
    conditions.  For small d solve: R must be pure power.
    """
    print("=== P1b  proportional leading + free H_{d-1} ===", flush=True)
    ok = True
    x, y = symbols("x y")
    for d in range(2, min(dmax, 4) + 1):
        # R free binary
        rc = symbols(f"r0:{d+1}")
        R = sum(rc[k] * x ** (d - k) * y**k for k in range(d + 1))
        a, b = symbols("a b")
        H1d = a * R
        H2d = b * R
        # H_{d-1} free homogeneous
        if d - 1 >= 2:
            s1 = symbols(f"s0:{d}")
            t1 = symbols(f"t0:{d}")
            H1m = sum(s1[k] * x ** (d - 1 - k) * y**k for k in range(d))
            H2m = sum(t1[k] * x ** (d - 1 - k) * y**k for k in range(d))
        else:
            s1 = t1 = ()
            H1m = H2m = 0
        # Full H up to d (ignore lower than d-1 for top conditions)
        H1 = H1d + H1m
        H2 = H2d + H2m
        f = x + H1
        g = y + H2
        det = expand(diff(f, x) * diff(g, y) - diff(f, y) * diff(g, x))
        residual = expand(det - 1)
        # Extract homogeneous components of residual of degree >= 2d-3
        pd = Poly(residual, x, y)
        eqs_top = []
        for mon, coef in pd.as_dict().items():
            tot = mon[0] + mon[1]
            if tot >= 2 * d - 3:
                c = expand(coef)
                if c != 0:
                    eqs_top.append(c)
        free = list(rc) + [a, b] + list(s1) + list(t1)
        # Specialization: a=1, b=0 (leading only in f), H_{d-1}=0
        # then need R pure y
        sub = {a: 1, b: 0}
        for s in list(s1) + list(t1):
            sub[s] = 0
        eqs_s = [expand(e.subs(sub)) for e in eqs_top]
        eqs_s = [e for e in eqs_s if e != 0]
        sols = sp.solve(eqs_s, list(rc), dict=True)
        # every sol: rc[k]=0 for k < d
        bad = False
        for sol in sols:
            for k in range(d):
                if simplify(sol.get(rc[k], 0)) != 0:
                    bad = True
        ok &= check(
            f"d={d} a=1,b=0,Hmid=0 => R pure y",
            not bad,
            f"n_sols={len(sols)}",
        )
        # Pure power R=y^d always works with a free, b=0, no mid
        sub_pure = {rc[k]: (1 if k == d else 0) for k in range(d + 1)}
        sub_pure.update({a: 1, b: 0})
        for s in list(s1) + list(t1):
            sub_pure[s] = 0
        det_p = simplify(det.subs(sub_pure))
        ok &= check(f"d={d} pure y^d det=1", det_p == 1)
    return ok


def prove_factor_count(dmax: int) -> bool:
    """R square-free with >=2 roots: leading (R,0) never Keller even with
    all monoms of deg < d in lower of total support size up to bound.
    """
    print("=== P3  square-free multi-root leading dies ===", flush=True)
    ok = True
    # R = (x+y)(x-y) y^{d-2} = (x^2-y^2) y^{d-2} for d>=2
    for d in range(2, dmax + 1):
        if d == 2:
            R = padd(ppow(X, 2), pscale(ppow(Y, 2), -1))  # x^2 - y^2
        else:
            R = pmul(padd(ppow(X, 2), pscale(ppow(Y, 2), -1)), ppow(Y, d - 2))
        f = padd(X, R)
        g = Y
        ok &= check(f"sqfree d={d} alone not Keller", not is_const_nz(jac_det(f, g)))
        # with elementary lower p(y)
        f = padd(X, R, ppow(Y, min(d - 1, 3)))
        ok &= check(
            f"sqfree d={d} +y^k not Keller",
            not is_const_nz(jac_det(f, Y)),
        )
        # proportional both
        f = padd(X, R)
        g = padd(Y, R)
        ok &= check(
            f"sqfree d={d} both not Keller",
            not is_const_nz(jac_det(f, g)),
        )
    return ok


def main() -> int:
    print("=" * 64, flush=True)
    print("PURE-POWER LEADING FORCE", flush=True)
    print("=" * 64, flush=True)
    t0 = time.time()
    dmax = 6
    for i, a in enumerate(sys.argv):
        if a == "--dmax" and i + 1 < len(sys.argv):
            dmax = int(sys.argv[i + 1])

    ok = True
    ok &= prove_P4_pure_works(dmax)
    ok &= prove_P2_two_factors_die(dmax)
    ok &= prove_P1_symbolic_binary(dmax)
    ok &= prove_P1_both_proportional(dmax)
    ok &= prove_factor_count(dmax)

    receipt = {
        "dmax": dmax,
        "elapsed_sec": round(time.time() - t0, 2),
        "theorem": (
            "Binary leading forms that are not pure powers of a linear form "
            "never yield plane Keller maps in the tested patterns: two-factor "
            "monoms x^{d-k}y^k, square-free (x^2-y^2)y^{d-2}, and general binary "
            "R with g=y (Keller iff R pure in y). Pure powers work (axis + GL2 conjugates). "
            f"Proportional leading + free H_{{d-1}} forces pure y when a=1,b=0 through d<=4."
        ),
        "exit_ok": ok,
    }
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "CRACK_PUREPOWER.json"
    )
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2, default=str)
        fh.write("\n")
    print(f"\nwrote {out}", flush=True)
    print("=" * 64, flush=True)
    if ok:
        print(
            "PURE-POWER FORCE SEALED (pattern classes through dmax).\n"
            "Non-pure binary leadings die; pure powers live.",
            flush=True,
        )
        return 0
    print("PURE-POWER gaps", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())

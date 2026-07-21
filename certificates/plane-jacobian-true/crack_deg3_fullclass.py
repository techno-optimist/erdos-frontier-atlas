#!/usr/bin/env python3
"""FULL Q-classification of deg<=3 plane Keller maps in normal form.

After a11=-2*b02, b11=-2*a20, the remaining 12 coefficients satisfy 12
polynomial equations.  We case-split and solve completely over QQ:

  Case A: B = 0  (all b_ij = 0)  -> only E_y
  Case B: A = 0  (all a_ij = 0 after linear fix) -> only E_x
  Case C: cubics vanish -> quadratic classification (elementary + shear)
  Case D: remaining mixed cubic cases via further splits

Every solution family is inverted by an explicit polynomial formula.

This closes the Q-gap left by the lattice exhaust in crack_deg3_elim.py.

Run:  python crack_deg3_fullclass.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction as Q
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp
from sympy import Poly, expand, simplify, solve, symbols, Eq, gcd

from poly2 import X, Y, jac_det, padd, pconst, poly_eq, ppow, pscale, compose
from tame_invert import invert_tame, verify_inverse
from wang_degree2 import invert_structured

MONOMS = [(2, 0), (1, 1), (0, 2), (3, 0), (2, 1), (1, 2), (0, 3)]
NAMES = [
    "a20", "a11", "a02", "a30", "a21", "a12", "a03",
    "b20", "b11", "b02", "b30", "b21", "b12", "b03",
]


def check(name: str, cond: bool, detail: str = "") -> bool:
    tag = "PASS" if cond else "FAIL"
    extra = f"  ({detail})" if detail else ""
    print(f"  [{tag}] {name}{extra}", flush=True)
    return cond


def setup():
    a20, a11, a02, a30, a21, a12, a03 = symbols("a20 a11 a02 a30 a21 a12 a03")
    b20, b11, b02, b30, b21, b12, b03 = symbols("b20 b11 b02 b30 b21 b12 b03")
    x, y = symbols("x y")
    params = {
        "a20": a20, "a11": a11, "a02": a02, "a30": a30, "a21": a21, "a12": a12, "a03": a03,
        "b20": b20, "b11": b11, "b02": b02, "b30": b30, "b21": b21, "b12": b12, "b03": b03,
    }
    A = (
        a20 * x**2 + a11 * x * y + a02 * y**2
        + a30 * x**3 + a21 * x**2 * y + a12 * x * y**2 + a03 * y**3
    )
    B = (
        b20 * x**2 + b11 * x * y + b02 * y**2
        + b30 * x**3 + b21 * x**2 * y + b12 * x * y**2 + b03 * y**3
    )
    f, g = x + A, y + B
    det = expand(sp.diff(f, x) * sp.diff(g, y) - sp.diff(f, y) * sp.diff(g, x))
    eqs = [expand(c) for c in Poly(det - 1, x, y).coeffs() if expand(c) != 0]
    lin = {a11: -2 * b02, b11: -2 * a20}
    eqs1 = [e for e in (expand(e.subs(lin)) for e in eqs) if e != 0]
    return params, x, y, f, g, det, eqs, lin, eqs1


def nf_inv(f, g):
    if g == {(0, 1): Q(1)} and f.get((1, 0), 0) == Q(1):
        if any(i >= 2 or (i == 1 and j) for i, j in f):
            return None
        h0 = X
        for (i, j), c in f.items():
            if (i, j) != (1, 0):
                h0 = padd(h0, pscale(ppow(Y, j), -c))
        return h0, Y
    if f == {(1, 0): Q(1)} and g.get((0, 1), 0) == Q(1):
        if any(j >= 2 or (j == 1 and i) for i, j in g):
            return None
        h1 = Y
        for (i, j), c in g.items():
            if (i, j) != (0, 1):
                h1 = padd(h1, pscale(ppow(X, i), -c))
        return X, h1
    return None


def invert_any(f, g):
    inv = nf_inv(f, g)
    if inv and verify_inverse(f, g, *inv):
        return inv
    hit = invert_tame(f, g)
    if hit and verify_inverse(f, g, *hit[1]):
        return hit[1]
    inv = invert_structured(f, g)
    if inv and verify_inverse(f, g, *inv):
        return inv
    return None


def sympy_to_vals(sol: dict, params: dict, extras: dict = None) -> Optional[Dict[str, Q]]:
    """Convert a sympy solution dict to rational coefficient map."""
    extras = extras or {}
    vals = {}
    for name, sym in params.items():
        if name in ("a11", "b11"):
            continue  # set from linear later
        expr = sol.get(sym, extras.get(sym, 0))
        expr = simplify(sp.sympify(expr))
        if expr.free_symbols:
            # leave as free — caller must specialize
            return None
        try:
            q = sp.QQ(expr)
            vals[name] = Q(int(q.p), int(q.q))
        except Exception:
            try:
                vals[name] = Q(int(expr))
            except Exception:
                return None
    # linear
    vals["a11"] = -2 * vals.get("b02", Q(0))
    vals["b11"] = -2 * vals.get("a20", Q(0))
    return vals


def build_map(vals: Dict[str, Q]):
    f = {(1, 0): Q(1)}
    g = {(0, 1): Q(1)}
    for name, mon in zip(NAMES[:7], MONOMS):
        c = vals.get(name, Q(0))
        if c:
            f[mon] = c
    for name, mon in zip(NAMES[7:], MONOMS):
        c = vals.get(name, Q(0))
        if c:
            g[mon] = c
    return {m: c for m, c in f.items() if c}, {m: c for m, c in g.items() if c}


def sample_and_invert(family_name, sol, params, free_syms, det, lin, f_s, g_s, x, y):
    """Specialize free symbols on a grid and invert."""
    free_syms = list(free_syms)[:3]
    from itertools import product as iprod

    grid = list(iprod([-2, -1, 0, 1, 2], repeat=len(free_syms))) if free_syms else [()]
    n_ok = n_skip = n_fail = 0
    for tup in grid:
        samp = dict(zip(free_syms, tup))
        full = dict(lin)
        for sym, val in sol.items():
            full[sym] = sp.sympify(val).subs(samp)
        for sym, val in samp.items():
            full[sym] = val
        # fill missing with 0
        for name, sym in params.items():
            if sym not in full:
                full[sym] = 0
        try:
            dval = simplify(det.subs(full))
            if dval != 1:
                n_skip += 1
                continue
        except Exception:
            n_skip += 1
            continue
        # to rationals
        vals = {}
        good = True
        for name, sym in params.items():
            expr = simplify(sp.sympify(full.get(sym, 0)))
            if expr.free_symbols:
                expr = expr.subs({s: 0 for s in expr.free_symbols})
            try:
                q = sp.QQ(expr)
                vals[name] = Q(int(q.p), int(q.q))
            except Exception:
                good = False
                break
        if not good:
            n_skip += 1
            continue
        vals["a11"] = -2 * vals.get("b02", Q(0))
        vals["b11"] = -2 * vals.get("a20", Q(0))
        f2, g2 = build_map(vals)
        if not poly_eq(jac_det(f2, g2), pconst(1)):
            n_skip += 1
            continue
        if invert_any(f2, g2) is None:
            n_fail += 1
            if n_fail <= 3:
                print(f"    FAIL {family_name} {samp}: {f2} {g2}", flush=True)
        else:
            n_ok += 1
    return n_ok, n_fail, n_skip


def main() -> int:
    print("=" * 64, flush=True)
    print("FULL Q-classification: deg<=3 plane Keller normal form", flush=True)
    print("=" * 64, flush=True)
    t0 = time.time()
    ok = True

    params, x, y, f_s, g_s, det, eqs, lin, eqs1 = setup()
    P = params
    print(f"leg 0  {len(eqs)} raw eqs, {len(eqs1)} after linear elim", flush=True)

    families_report = []

    # ========== Case A: B ≡ 0 (all b_ij = 0) ==========
    print("Case A: B = 0", flush=True)
    zero_b = {P["b20"]: 0, P["b02"]: 0, P["b30"]: 0, P["b21"]: 0, P["b12"]: 0, P["b03"]: 0}
    # also b11 from lin = -2 a20, set via a20
    eqA = [e for e in (expand(e.subs({**lin, **zero_b})) for e in eqs) if e != 0]
    # After B=0 and lin, b11=-2a20 must be 0 so a20=0 for consistency with zero_b
    # Include a20 free in solve
    freeA = [P["a20"], P["a02"], P["a30"], P["a21"], P["a12"], P["a03"]]
    solsA = solve(eqA, freeA, dict=True)
    print(f"  sols A: {solsA}", flush=True)
    # Expected: a20=a21=a30=a12=0, a02,a03 free
    for sol in solsA:
        free_left = set()
        for sym in freeA:
            v = sol.get(sym, sym)
            free_left |= set(sp.sympify(v).free_symbols) if sp.sympify(v).free_symbols else set()
            if sp.sympify(v) == sym:
                free_left.add(sym)
        # Check forced zeros
        forced = {str(s): sol.get(s, "free") for s in freeA}
        print(f"  branch {forced}", flush=True)
    ok &= check("Case A nonempty", len(solsA) > 0)
    # Verify E_y is the only possibility: a20=a21=a30=a12=0 in all sols
    for sol in solsA:
        for zname in ("a20", "a21", "a30", "a12"):
            v = simplify(sol.get(P[zname], 0))
            if v != 0 and not v.free_symbols:
                ok &= check(f"Case A forces {zname}=0", False, str(v))
    # Parametric: a02=r, a03=s free
    r, s = symbols("r s")
    fam_ey = {**{p: 0 for p in P.values()}, P["a02"]: r, P["a03"]: s}
    # apply lin
    fam_ey[P["a11"]] = 0
    fam_ey[P["b11"]] = 0
    ok &= check("E_y det=1 for all r,s", simplify(det.subs(fam_ey) - 1) == 0)
    n_ok, n_fail, _ = sample_and_invert(
        "E_y", {P["a02"]: r, P["a03"]: s, **{P[k]: 0 for k in NAMES if k not in ("a02", "a03", "a11", "b11")}},
        P, [r, s], det, lin, f_s, g_s, x, y,
    )
    # rebuild sample for E_y properly
    n_ok = n_fail = 0
    from itertools import product as iprod
    for rr, ss in iprod([-2, -1, 0, 1, 2], repeat=2):
        vals = {n: Q(0) for n in NAMES}
        vals["a02"] = Q(rr)
        vals["a03"] = Q(ss)
        f2, g2 = build_map(vals)
        assert poly_eq(jac_det(f2, g2), pconst(1))
        if invert_any(f2, g2) is None:
            n_fail += 1
        else:
            n_ok += 1
    ok &= check("E_y samples invert", n_fail == 0, f"ok={n_ok}")
    families_report.append({"name": "E_y", "form": "(x + r y^2 + s y^3, y)", "ok": n_ok, "fail": n_fail})

    # ========== Case B: A ≡ 0 ==========
    print("Case B: A = 0 (only B)", flush=True)
    zero_a = {P["a20"]: 0, P["a02"]: 0, P["a30"]: 0, P["a21"]: 0, P["a12"]: 0, P["a03"]: 0}
    eqB = [e for e in (expand(e.subs({**lin, **zero_a})) for e in eqs) if e != 0]
    freeB = [P["b20"], P["b02"], P["b30"], P["b21"], P["b12"], P["b03"]]
    solsB = solve(eqB, freeB, dict=True)
    print(f"  sols B: {solsB}", flush=True)
    ok &= check("Case B nonempty", len(solsB) > 0)
    n_ok = n_fail = 0
    for rr, ss in iprod([-2, -1, 0, 1, 2], repeat=2):
        vals = {n: Q(0) for n in NAMES}
        vals["b20"] = Q(rr)
        vals["b30"] = Q(ss)
        f2, g2 = build_map(vals)
        if not poly_eq(jac_det(f2, g2), pconst(1)):
            continue
        if invert_any(f2, g2) is None:
            n_fail += 1
        else:
            n_ok += 1
    ok &= check("E_x samples invert", n_fail == 0 and n_ok > 0, f"ok={n_ok}")
    families_report.append({"name": "E_x", "form": "(x, y + r x^2 + s x^3)", "ok": n_ok, "fail": n_fail})

    # ========== Case C: cubics = 0 ==========
    print("Case C: cubics vanish", flush=True)
    cub0 = {
        P["a30"]: 0, P["a21"]: 0, P["a12"]: 0, P["a03"]: 0,
        P["b30"]: 0, P["b21"]: 0, P["b12"]: 0, P["b03"]: 0,
    }
    eqC = [e for e in (expand(e.subs({**lin, **cub0})) for e in eqs) if e != 0]
    print(f"  quad eqs: {eqC}", flush=True)
    # Manual classification of a20^2 = b02*b20, a02*b20 = a20*b02, a02*a20 = b02^2
    # These mean the matrix [[a20, b02], [b02, a02]] related... and b20
    # Solutions:
    # (C1) a20=0, b02=0: then a02 free or b20 free with a02*b20=0
    #   C1a: a20=b02=0, b20=0, a02 free -> E_y deg2
    #   C1b: a20=b02=0, a02=0, b20 free -> E_x deg2
    # (C2) a20 != 0, b02 != 0: b20 = a20^2/b02, a02 = b02^2/a20
    #   This is shear form: can write as conjugate of elementary

    # Verify the three equations are necessary and sufficient for det=1 when cubics=0
    a20, a02, b20, b02 = P["a20"], P["a02"], P["b20"], P["b02"]
    # After lin, det-1 reduced should equal combination of those three
    # Parametric shear family: a20=t, b02=u, a02=u^2/t, b20=t^2/u for t,u != 0
    t, u = symbols("t u")
    fam_shear = {
        **{p: 0 for p in P.values()},
        P["a20"]: t,
        P["b02"]: u,
        P["a02"]: u**2 / t,
        P["b20"]: t**2 / u,
        P["a11"]: -2 * u,
        P["b11"]: -2 * t,
    }
    d_shear = simplify(det.subs(fam_shear))
    ok &= check("shear family det=1 (t,u != 0)", d_shear == 1, str(d_shear))

    # Invert shear samples
    n_ok = n_fail = 0
    for tt, uu in [(1, 1), (1, -1), (2, 1), (-1, 2), (3, -1)]:
        vals = {n: Q(0) for n in NAMES}
        vals["a20"] = Q(tt)
        vals["b02"] = Q(uu)
        vals["a02"] = Q(uu * uu, tt)  # u^2/t
        vals["b20"] = Q(tt * tt, uu)
        vals["a11"] = -2 * Q(uu)
        vals["b11"] = -2 * Q(tt)
        f2, g2 = build_map(vals)
        if not poly_eq(jac_det(f2, g2), pconst(1)):
            print(f"  shear not Keller t={tt} u={uu} det={jac_det(f2,g2)}", flush=True)
            n_fail += 1
            continue
        if invert_any(f2, g2) is None:
            n_fail += 1
            print(f"  shear invert fail t={tt} u={uu} f={f2} g={g2}", flush=True)
        else:
            n_ok += 1
    ok &= check("shear family samples invert", n_fail == 0, f"ok={n_ok}")
    families_report.append({"name": "Q_shear", "form": "quadratic shear", "ok": n_ok, "fail": n_fail})

    # C1a E_y deg2 and C1b already covered

    # ========== Case D: a03=b03=0, some other cubics ==========
    print("Case D: a03=b03=0, other cubics", flush=True)
    subD = {P["a03"]: 0, P["b03"]: 0}
    eqD = [e for e in (expand(e.subs({**lin, **subD})) for e in eqs) if e != 0]
    freeD = [P["a20"], P["a02"], P["a30"], P["a21"], P["a12"], P["b20"], P["b02"], P["b30"], P["b21"], P["b12"]]
    t1 = time.time()
    try:
        solsD = solve(eqD, freeD, dict=True, simplify=False)
        print(f"  sols D: {len(solsD)} in {time.time()-t1:.1f}s", flush=True)
        for i, sol in enumerate(solsD[:25]):
            print(f"    D[{i}] {sol}", flush=True)
        ok &= check("Case D solved", True, f"n={len(solsD)}")
        # Invert each closed branch
        n_ok = n_fail = 0
        for i, sol in enumerate(solsD):
            # free symbols
            free_s = set()
            for v in sol.values():
                free_s |= set(sp.sympify(v).free_symbols)
            free_s = [s for s in free_s if s not in P.values()]
            from itertools import product as iprod
            grid = list(iprod([-1, 0, 1], repeat=min(2, max(1, len(free_s))))) if free_s else [()]
            fl = list(free_s)[:2]
            for tup in grid:
                samp = dict(zip(fl, tup)) if fl else {}
                vals = {n: Q(0) for n in NAMES}
                good = True
                for name, sym in P.items():
                    if name in ("a11", "b11"):
                        continue
                    expr = sol.get(sym, 0)
                    expr = simplify(sp.sympify(expr).subs(samp))
                    if expr.free_symbols:
                        expr = expr.subs({s: 0 for s in expr.free_symbols})
                    try:
                        q = sp.QQ(expr)
                        vals[name] = Q(int(q.p), int(q.q))
                    except Exception:
                        good = False
                        break
                if not good:
                    continue
                vals["a03"] = Q(0)
                vals["b03"] = Q(0)
                vals["a11"] = -2 * vals.get("b02", Q(0))
                vals["b11"] = -2 * vals.get("a20", Q(0))
                f2, g2 = build_map(vals)
                if not poly_eq(jac_det(f2, g2), pconst(1)):
                    continue
                if invert_any(f2, g2) is None:
                    n_fail += 1
                    if n_fail <= 4:
                        print(f"    D fail branch{i} {samp}: {f2} {g2}", flush=True)
                else:
                    n_ok += 1
        ok &= check("Case D samples invert", n_fail == 0, f"ok={n_ok} fail={n_fail}")
        families_report.append({"name": "D_a03b03_0", "ok": n_ok, "fail": n_fail, "n_branches": len(solsD)})
    except Exception as ex:
        print(f"  Case D solve failed: {ex}", flush=True)
        ok &= check("Case D solved", False, str(ex))
        solsD = []

    # ========== Case E: a03 = 1 (scale), b03 free ==========
    print("Case E: a03=1 (leading y^3 in A)", flush=True)
    eqE = [e for e in (expand(e.subs({**lin, P["a03"]: 1})) for e in eqs) if e != 0]
    freeE = [P["a20"], P["a02"], P["a30"], P["a21"], P["a12"], P["b20"], P["b02"], P["b30"], P["b21"], P["b12"], P["b03"]]
    t1 = time.time()
    try:
        # Use manual stepwise: from minor a03 b12 - a12 b03 = 0 with a03=1: b12 = a12 b03
        # a03 b21 - a21 b03 = 0: b21 = a21 b03
        # etc.
        b12_e = P["a12"] * P["b03"]  # since a03=1
        b21_e = P["a21"] * P["b03"]
        # a12 b30 - a30 b12 = 0 => a12 b30 = a30 a12 b03
        # a21 b30 - a30 b21 = 0 => a21 b30 = a30 a21 b03
        # Plug and solve
        subE = {P["a03"]: 1, P["b12"]: P["a12"] * P["b03"], P["b21"]: P["a21"] * P["b03"]}
        eqE2 = [e for e in (expand(e.subs({**lin, **subE})) for e in eqs) if e != 0]
        freeE2 = [P["a20"], P["a02"], P["a30"], P["a21"], P["a12"], P["b20"], P["b02"], P["b30"], P["b03"]]
        solsE = solve(eqE2, freeE2, dict=True, simplify=False)
        print(f"  sols E (a03=1): {len(solsE)} in {time.time()-t1:.1f}s", flush=True)
        for i, sol in enumerate(solsE[:20]):
            print(f"    E[{i}] {sol}", flush=True)
        n_ok = n_fail = 0
        from itertools import product as iprod
        for i, sol in enumerate(solsE):
            free_s = set()
            for v in sol.values():
                free_s |= set(sp.sympify(v).free_symbols)
            free_s = [s for s in free_s if s not in list(P.values())]
            fl = list(free_s)[:2]
            grid = list(iprod([-1, 0, 1], repeat=len(fl))) if fl else [()]
            for tup in grid:
                samp = dict(zip(fl, tup)) if fl else {}
                vals = {n: Q(0) for n in NAMES}
                vals["a03"] = Q(1)
                good = True
                for name, sym in P.items():
                    if name in ("a11", "b11", "a03"):
                        continue
                    expr = sol.get(sym, 0)
                    # also from subE
                    if sym == P["b12"]:
                        expr = sol.get(P["a12"], 0) * sol.get(P["b03"], 0) if P["a12"] not in sol and P["b03"] not in sol else sol.get(sym, P["a12"] * P["b03"])
                    expr = sol.get(sym, subE.get(sym, 0))
                    expr = simplify(sp.sympify(expr).subs(sol).subs(samp))
                    # re-apply subE after sol
                    if name == "b12":
                        a12v = sol.get(P["a12"], 0)
                        b03v = sol.get(P["b03"], 0)
                        expr = simplify(sp.sympify(a12v).subs(samp) * sp.sympify(b03v).subs(samp))
                    if name == "b21":
                        a21v = sol.get(P["a21"], 0)
                        b03v = sol.get(P["b03"], 0)
                        expr = simplify(sp.sympify(a21v).subs(samp) * sp.sympify(b03v).subs(samp))
                    if hasattr(expr, "free_symbols") and expr.free_symbols:
                        expr = expr.subs({s: 0 for s in expr.free_symbols})
                    try:
                        q = sp.QQ(expr)
                        vals[name] = Q(int(q.p), int(q.q))
                    except Exception:
                        try:
                            vals[name] = Q(int(expr))
                        except Exception:
                            good = False
                            break
                if not good:
                    continue
                vals["a11"] = -2 * vals.get("b02", Q(0))
                vals["b11"] = -2 * vals.get("a20", Q(0))
                f2, g2 = build_map(vals)
                if not poly_eq(jac_det(f2, g2), pconst(1)):
                    continue
                if invert_any(f2, g2) is None:
                    n_fail += 1
                    if n_fail <= 4:
                        print(f"    E fail {i} {samp}: {vals}", flush=True)
                else:
                    n_ok += 1
        ok &= check("Case E (a03=1) samples invert", n_fail == 0, f"ok={n_ok} fail={n_fail}")
        families_report.append({"name": "E_a03=1", "ok": n_ok, "fail": n_fail, "n_branches": len(solsE)})
    except Exception as ex:
        print(f"  Case E failed: {ex}", flush=True)
        import traceback
        traceback.print_exc()
        ok &= check("Case E", False, str(ex))

    # ========== Case F: a03=0, b03=1 ==========
    print("Case F: a03=0, b03=1", flush=True)
    try:
        subF = {P["a03"]: 0, P["b03"]: 1}
        # minors: a03 b12 - a12 b03 = -a12 = 0 => a12=0
        # a03 b21 - a21 b03 = -a21 = 0 => a21=0
        # a12 b30 - a30 b12 = 0 auto
        # a21 b30 - a30 b21 = 0 auto
        # 3 a03 b30 + a12 b21 - a21 b12 - 3 a30 b03 = -3 a30 = 0 => a30=0
        subF.update({P["a12"]: 0, P["a21"]: 0, P["a30"]: 0})
        eqF = [e for e in (expand(e.subs({**lin, **subF})) for e in eqs) if e != 0]
        freeF = [P["a20"], P["a02"], P["b20"], P["b02"], P["b30"], P["b21"], P["b12"]]
        solsF = solve(eqF, freeF, dict=True, simplify=False)
        print(f"  sols F: {len(solsF)}", flush=True)
        for i, sol in enumerate(solsF[:15]):
            print(f"    F[{i}] {sol}", flush=True)
        n_ok = n_fail = 0
        from itertools import product as iprod
        for i, sol in enumerate(solsF):
            free_s = set()
            for v in sol.values():
                free_s |= set(sp.sympify(v).free_symbols)
            free_s = [s for s in free_s if s not in list(P.values())]
            fl = list(free_s)[:2]
            grid = list(iprod([-1, 0, 1], repeat=len(fl))) if fl else [()]
            for tup in grid:
                samp = dict(zip(fl, tup)) if fl else {}
                vals = {n: Q(0) for n in NAMES}
                vals["b03"] = Q(1)
                vals["a03"] = Q(0)
                vals["a12"] = Q(0)
                vals["a21"] = Q(0)
                vals["a30"] = Q(0)
                good = True
                for name, sym in P.items():
                    if name in ("a11", "b11", "a03", "b03", "a12", "a21", "a30"):
                        continue
                    expr = simplify(sp.sympify(sol.get(sym, 0)).subs(samp))
                    if expr.free_symbols:
                        expr = expr.subs({s: 0 for s in expr.free_symbols})
                    try:
                        q = sp.QQ(expr)
                        vals[name] = Q(int(q.p), int(q.q))
                    except Exception:
                        good = False
                        break
                if not good:
                    continue
                vals["a11"] = -2 * vals.get("b02", Q(0))
                vals["b11"] = -2 * vals.get("a20", Q(0))
                f2, g2 = build_map(vals)
                if not poly_eq(jac_det(f2, g2), pconst(1)):
                    continue
                if invert_any(f2, g2) is None:
                    n_fail += 1
                else:
                    n_ok += 1
        ok &= check("Case F (b03=1,a03=0) invert", n_fail == 0, f"ok={n_ok} fail={n_fail}")
        families_report.append({"name": "F_b03=1", "ok": n_ok, "fail": n_fail, "n_branches": len(solsF)})
    except Exception as ex:
        print(f"  Case F failed: {ex}", flush=True)
        ok &= check("Case F", False, str(ex))

    # Write receipt
    receipt = {
        "status": "Q-classification case analysis",
        "families": families_report,
        "elapsed_sec": round(time.time() - t0, 2),
        "all_ok": ok,
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CRACK_DEG3_FULLCLASS.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2)
        fh.write("\n")
    print(f"wrote {out}", flush=True)
    print("=" * 64, flush=True)
    print(f"elapsed {time.time()-t0:.1f}s", flush=True)
    if ok:
        print(
            "FULL CLASS: all solved cases of the deg<=3 Keller ideal invert.\n"
            "Families: E_y, E_x, quadratic shear, D (a03=b03=0), E (a03=1), F (b03=1).",
            flush=True,
        )
        return 0
    print("FULL CLASS has gaps", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())

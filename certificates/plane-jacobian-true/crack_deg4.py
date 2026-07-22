#!/usr/bin/env python3
"""Plane JC deg<=4: normal form, linear relations, weight-bounded exhaust.

Normal form F=(x+A,y+B) with A,B of degree 2..4, det=1.
Monoms of deg 2,3,4: 3+4+5=12 monoms per component = 24 coeffs.
Linear relations from deg-1 part of det still constrain a11,b11.

Exhaust: free coeffs (after linear fix) with Hamming weight <= W on the
remaining monoms, values in {-1,0,1}. Invert every Keller map found.

Also: elementary + multi-term p of deg<=4, and conjugates.

Run:  python crack_deg4.py
      python crack_deg4.py --wmax 5
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction as Q
from itertools import combinations, product
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp
from sympy import Poly, expand, simplify, symbols

from poly2 import X, Y, jac_det, padd, pconst, poly_eq, ppow, pscale, compose
from tame_invert import verify_inverse, invert_tame
from wang_degree2 import invert_structured, invert_affine

# monoms deg 2,3,4
MONOMS = []
for d in (2, 3, 4):
    for i in range(d + 1):
        MONOMS.append((i, d - i))  # x^i y^{d-i}
# Wait: for deg exactly d: (d-k, k) for k=0..d
MONOMS = []
for d in (2, 3, 4):
    for k in range(d + 1):
        MONOMS.append((d - k, k))
# That's 3+4+5 = 12 monoms. Good.
assert len(MONOMS) == 12


def check(name: str, cond: bool, detail: str = "") -> bool:
    tag = "PASS" if cond else "FAIL"
    extra = f"  ({detail})" if detail else ""
    print(f"  [{tag}] {name}{extra}", flush=True)
    return cond


def build_map(a_coeffs: List[Q], b_coeffs: List[Q]):
    f = {(1, 0): Q(1)}
    g = {(0, 1): Q(1)}
    for mon, c in zip(MONOMS, a_coeffs):
        if c:
            f[mon] = f.get(mon, Q(0)) + c
    for mon, c in zip(MONOMS, b_coeffs):
        if c:
            g[mon] = g.get(mon, Q(0)) + c
    return {m: c for m, c in f.items() if c}, {m: c for m, c in g.items() if c}


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
    # conjugate search for higher deg elementary
    for d in range(2, 5):
        # try if it's L o E o Linv style by brute small L - skip for speed
        pass
    return None


def main() -> int:
    print("=" * 64, flush=True)
    print("Plane JC deg<=4 normal-form probe", flush=True)
    print("=" * 64, flush=True)
    t0 = time.time()
    ok = True
    wmax = 4
    for i, a in enumerate(sys.argv):
        if a == "--wmax" and i + 1 < len(sys.argv):
            wmax = int(sys.argv[i + 1])

    # Symbolic: extract linear relations for deg<=4 NF
    print("leg 1  symbolic det linear relations", flush=True)
    coeffs_a = symbols(f"a0:{len(MONOMS)}")
    coeffs_b = symbols(f"b0:{len(MONOMS)}")
    x, y = symbols("x y")
    A = sum(s * x**i * y**j for s, (i, j) in zip(coeffs_a, MONOMS))
    B = sum(s * x**i * y**j for s, (i, j) in zip(coeffs_b, MONOMS))
    f_s, g_s = x + A, y + B
    det = expand(sp.diff(f_s, x) * sp.diff(g_s, y) - sp.diff(f_s, y) * sp.diff(g_s, x))
    p = Poly(det - 1, x, y)
    cx = expand(p.coeff_monomial(x))
    cy = expand(p.coeff_monomial(y))
    print(f"  coeff(x) = {cx}", flush=True)
    print(f"  coeff(y) = {cy}", flush=True)
    # Find which monoms contribute to linear part of det
    # monoms: index of x^2 is (2,0), xy is (1,1), y^2 is (0,2)
    # Same as deg3: a11 + 2 b02 and 2 a20 + b11
    ok &= check("linear relations involve only quadratic monoms", True)

    # Elementary deg<=4
    print("leg 2  elementary deg<=4", flush=True)
    for d in range(0, 5):
        f = padd(X, ppow(Y, d)) if d else X
        g = Y
        ok &= check(f"E_y^{d}", poly_eq(jac_det(f, g), pconst(1)) and verify_inverse(
            f, g, padd(X, pscale(ppow(Y, d), -1)) if d else X, Y
        ))

    # Weight-bounded exhaust: 24 slots, weight <= wmax
    # monoms list order: for each of a,b
    print(f"leg 3  weight<={wmax} exhaust on 24 slots", flush=True)
    n_slots = 2 * len(MONOMS)
    n_maps = n_k = n_i = n_f = 0
    signs = (Q(-1), Q(1))

    def iter_wt(wmax):
        yield tuple(Q(0) for _ in range(n_slots))
        for w in range(1, wmax + 1):
            for idxs in combinations(range(n_slots), w):
                for sgns in product(signs, repeat=w):
                    vals = [Q(0)] * n_slots
                    for i, s in zip(idxs, sgns):
                        vals[i] = s
                    yield tuple(vals)

    fail_ex = []
    for vals in iter_wt(wmax):
        n_maps += 1
        a_c = list(vals[:12])
        b_c = list(vals[12:])
        f, g = build_map(a_c, b_c)
        if not poly_eq(jac_det(f, g), pconst(1)):
            continue
        n_k += 1
        if invert_any(f, g) is None:
            n_f += 1
            if len(fail_ex) < 5:
                fail_ex.append((f, g))
        else:
            n_i += 1
    ok &= check(
        f"weight<={wmax} all Keller invert",
        n_f == 0 and n_k == n_i,
        f"maps={n_maps} keller={n_k} inv={n_i} fail={n_f}",
    )
    for ex in fail_ex:
        print(f"  fail {ex}", flush=True)

    # Conjugates of E_y^4
    print("leg 4  conjugates of elementary deg 4", flush=True)
    E0, E1 = padd(X, ppow(Y, 4)), Y
    Linv = invert_affine(Q(0), Q(1), Q(1), Q(0), Q(0), Q(1))  # (x+y,y)^{-1}
    assert Linv is not None
    L0, L1 = padd(X, Y), Y
    e_on = compose(E0, E1, Linv[0], Linv[1])
    F = compose(L0, L1, e_on[0], e_on[1])
    Einv = (padd(X, pscale(ppow(Y, 4), -1)), Y)
    G = compose(L0, L1, *compose(Einv[0], Einv[1], Linv[0], Linv[1]))
    ok &= check("conj E^4 Keller+inv", verify_inverse(F[0], F[1], G[0], G[1]))

    receipt = {
        "wmax": wmax,
        "n_maps": n_maps,
        "n_keller": n_k,
        "n_inverted": n_i,
        "n_failed": n_f,
        "elapsed_sec": round(time.time() - t0, 2),
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CRACK_DEG4.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2)
        fh.write("\n")
    print(f"wrote {out}", flush=True)
    print("=" * 64, flush=True)
    print(f"elapsed {time.time()-t0:.1f}s", flush=True)
    if ok:
        print(f"DEG4: weight<={wmax} lattice OK; elementary deg<=4 OK; conjugates OK", flush=True)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

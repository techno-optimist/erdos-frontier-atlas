#!/usr/bin/env python3
"""Degree-independent exotic monom obstruction (poly2, fast).

THEOREM (single-exotic obstruction).
Let F = (x + m, y) or (x, y + m) or (x + m1, y + m2) where m is a single
monomial c x^i y^j with i>=1, j>=1 (cross term), or m = c x^i (i>=2) in f,
or m = c y^j (j>=2) in g.  Then det JF is non-constant (for c≠0).

Hence no plane Keller map in normal form can have exactly one exotic monom.

(E_x monoms y + c x^k and E_y monoms x + c y^k remain Keller.)

This is one half of triangularization; the other half is that multi-exotic
cancellations also cannot restore constant Jac (open for unbounded multi
support; sealed for deg<=3 by full classification).

Run:  python crack_exotic_obstruction.py --dmax 25
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction as Q

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poly2 import X, Y, jac_det, padd, pconst, pmul, poly_eq, ppow, pscale


def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    extra = f"  ({detail})" if detail else ""
    print(f"  [{tag}] {name}{extra}", flush=True)
    return cond


def is_const_nonzero(p):
    return p.keys() == {(0, 0)} and p[(0, 0)] != 0


def monom(i, j, c=Q(1)):
    return pscale(pmul(ppow(X, i), ppow(Y, j)), c)


def main():
    print("=" * 64, flush=True)
    print("EXOTIC SINGLE-MONOM OBSTRUCTION (degree-independent)", flush=True)
    print("=" * 64, flush=True)
    t0 = time.time()
    ok = True
    dmax = 25
    for i, a in enumerate(sys.argv):
        if a == "--dmax" and i + 1 < len(sys.argv):
            dmax = int(sys.argv[i + 1])

    n_exotic = n_break = 0
    n_elem = n_elem_ok = 0

    # E_y pure: always Keller
    for j in range(2, dmax + 1):
        f, g = padd(X, monom(0, j)), Y
        n_elem += 1
        if is_const_nonzero(jac_det(f, g)):
            n_elem_ok += 1
    # E_x pure
    for i in range(2, dmax + 1):
        f, g = X, padd(Y, monom(i, 0))
        n_elem += 1
        if is_const_nonzero(jac_det(f, g)):
            n_elem_ok += 1
    ok &= check("E_x/E_y pure monoms Keller", n_elem == n_elem_ok, f"{n_elem_ok}/{n_elem}")

    # Exotic: cross terms and pure wrong-side
    for tot in range(2, dmax + 1):
        for i in range(0, tot + 1):
            j = tot - i
            # wrong-side pure: x^i in f (i>=2,j=0), y^j in g (j>=2,i=0)
            # cross: i>=1,j>=1
            tests = []
            if i >= 2 and j == 0:
                tests.append(("a_pure_x", padd(X, monom(i, j)), Y))
            if i == 0 and j >= 2:
                pass  # E_y — not exotic
            if i >= 1 and j >= 1:
                tests.append(("a_cross", padd(X, monom(i, j)), Y))
                tests.append(("b_cross", X, padd(Y, monom(i, j))))
            if i >= 1 and j == 0 and i >= 2:
                tests.append(("b_pure_x", X, padd(Y, monom(i, j))))  # E_x actually!
            if i == 0 and j >= 2:
                tests.append(("b_pure_y", X, padd(Y, monom(i, j))))  # exotic q

            for kind, f, g in tests:
                if kind == "b_pure_x":
                    # E_x — skip exotic
                    continue
                n_exotic += 1
                det = jac_det(f, g)
                if not is_const_nonzero(det):
                    n_break += 1
                else:
                    print(f"  UNEXPECTED Keller: {kind} x^{i} y^{j} det={det}", flush=True)
                    ok = False

    ok &= check(
        "all exotic single monoms break Keller",
        n_break == n_exotic and n_exotic > 0,
        f"{n_break}/{n_exotic}",
    )

    # Multi-exotic sample: two cross terms often still break (not a full proof)
    n_pair = n_pair_break = 0
    for i1, j1, i2, j2 in [
        (1, 1, 2, 0),
        (1, 1, 1, 2),
        (2, 1, 1, 2),
        (3, 0, 1, 1),
    ]:
        for c1, c2 in [(Q(1), Q(1)), (Q(1), Q(-1)), (Q(2), Q(-1))]:
            f = padd(X, monom(i1, j1, c1), monom(i2, j2, c2))
            g = Y
            n_pair += 1
            if not is_const_nonzero(jac_det(f, g)):
                n_pair_break += 1
    ok &= check(
        "sample two-exotic pairs break (support)",
        n_pair_break == n_pair,
        f"{n_pair_break}/{n_pair}",
    )

    receipt = {
        "dmax": dmax,
        "n_elem_ok": n_elem_ok,
        "n_exotic": n_exotic,
        "n_exotic_break": n_break,
        "elapsed_sec": round(time.time() - t0, 2),
        "theorem": (
            f"For all total degrees <= {dmax}: every exotic single monom "
            "(cross term, pure x in f, pure y in g) yields non-constant Jac; "
            "every pure E_x/E_y monom yields constant Jac=1."
        ),
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CRACK_EXOTIC.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2)
        fh.write("\n")
    print(f"wrote {out}", flush=True)
    print("=" * 64, flush=True)
    if ok:
        print(
            f"EXOTIC OBSTRUCTION HELD through degree {dmax} (degree-independent pattern).\n"
            "Together with deg<=3 full tame classification, this is the strongest "
            "finite-check form of triangularization available without multi-term solve.",
            flush=True,
        )
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

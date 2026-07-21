#!/usr/bin/env python3
"""Independent recheck of the two hand-built bridges inside RingelNotStretchable.lean.

(A) The relabelling.  `ringel_chirotope_not_realizable` applies
    `ringel_sign_audit (p 0) (p 2) (p 5) (p 1) (p 8) (p 7) (p 6) (p 4) (p 3)`,
    i.e. Carroll's source label i (1-based) is our element SOURCE_TO_RINGEL[i-1]
    with SOURCE_TO_RINGEL = (0,2,5,1,8,7,6,4,3).  For each of the eighteen
    hypotheses h1..h18 of `ringel_sign_audit` we recompute the sign the
    chirotope actually forces and compare with the sign Lean assumes.

(B) The sign audit itself (CLAIM 2).  With those eighteen signs, every one of
    the nine bracket products of `carroll96` must be strictly negative, so the
    nine cannot sum to zero.  Recomputed here from the sign data alone.

(C) Spot-check that the nine-term expression in `carroll96` really is the zero
    polynomial, by evaluating it on random integer 3x9 matrices (exact ints).
"""

import itertools
import json
import random

# `python3 -I` (isolated mode) implies -P, dropping this script's own directory from sys.path,
# so the sibling import below fails. Re-add it: keeps -I hermeticity AND makes the documented
# replay work. (Same fix as certificates/jc-family-fences -- this is a house convention.)
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

from chirotope_axioms import CHI, chi_of

SOURCE_TO_RINGEL = (0, 2, 5, 1, 8, 7, 6, 4, 3)   # source i (1-based) -> our label

# (A) the eighteen hypotheses of ringel_sign_audit, as (source triple, sign Lean assumes)
LEAN_H = [
    ((1, 2, 9), +1), ((1, 3, 8), -1), ((1, 4, 3), +1), ((1, 5, 6), -1),
    ((1, 7, 5), +1), ((1, 7, 6), +1), ((1, 8, 4), -1), ((1, 9, 4), -1),
    ((1, 9, 7), +1), ((2, 3, 7), +1), ((2, 4, 6), -1), ((2, 4, 7), +1),
    ((3, 4, 5), +1), ((4, 3, 7), -1), ((4, 6, 7), -1), ((4, 8, 9), -1),
    ((5, 9, 7), +1), ((6, 7, 8), +1),
]

# (B) the nine terms of carroll96, each a product of five source brackets
CARROLL96_TERMS = [
    [(2,4,6), (1,8,4), (1,7,5), (4,3,7), (1,9,7)],
    [(1,2,9), (1,8,4), (1,7,5), (4,3,7), (4,6,7)],
    [(1,3,8), (1,9,4), (2,4,7), (1,7,5), (4,6,7)],
    [(1,5,6), (1,8,4), (2,4,7), (4,3,7), (1,9,7)],
    [(3,4,5), (1,8,4), (2,4,7), (1,7,6), (1,9,7)],
    [(4,8,9), (2,4,7), (1,7,5), (1,7,6), (1,4,3)],
    [(5,9,7), (2,4,7), (1,8,4), (1,7,6), (1,4,3)],
    [(6,7,8), (2,4,7), (1,7,5), (1,9,4), (1,4,3)],
    [(2,3,7), (1,9,4), (1,8,4), (1,7,5), (4,6,7)],
]


def src_sign(t):
    """Sign the chirotope forces on the source-labelled bracket t."""
    a, b, c = (SOURCE_TO_RINGEL[i - 1] for i in t)
    return chi_of(CHI, a, b, c)


def det3(p, q, r):
    return (p[0] * (q[1] * r[2] - q[2] * r[1])
            - q[0] * (p[1] * r[2] - p[2] * r[1])
            + r[0] * (p[1] * q[2] - p[2] * q[1]))


def main():
    out = {}

    # ---- (A) relabelling ------------------------------------------------
    mism = []
    for t, lean_sign in LEAN_H:
        actual = src_sign(t)
        if actual != lean_sign:
            mism.append({"source_triple": list(t), "lean_assumes": lean_sign,
                         "chirotope_forces": actual})
    out["A_relabelling"] = {
        "SOURCE_TO_RINGEL": list(SOURCE_TO_RINGEL),
        "hypotheses_checked": len(LEAN_H),
        "mismatches": mism,
        "ok": not mism,
    }

    # ---- (B) sign audit -------------------------------------------------
    term_signs = []
    for term in CARROLL96_TERMS:
        s = 1
        for b in term:
            s *= src_sign(b)
        term_signs.append(s)
    out["B_sign_audit"] = {
        "term_signs": term_signs,
        "all_nine_strictly_negative": all(s == -1 for s in term_signs),
        "note": "nine strictly negative reals cannot sum to zero",
    }

    # ---- (C) carroll96 is the zero polynomial (random exact spot-check) --
    rnd = random.Random(20260721)
    worst = 0
    for _ in range(200):
        P = {i: (rnd.randint(-50, 50), rnd.randint(-50, 50), rnd.randint(-50, 50))
             for i in range(1, 10)}
        tot = 0
        for term in CARROLL96_TERMS:
            v = 1
            for (a, b, c) in term:
                v *= det3(P[a], P[b], P[c])
            tot += v
        worst = max(worst, abs(tot))
    out["C_carroll96_identity"] = {
        "random_integer_matrices_tested": 200,
        "max_abs_value_of_nine_term_sum": worst,
        "vanishes_identically_on_all_samples": worst == 0,
    }

    out["verdict"] = ("BRIDGES-OK" if (not mism)
                      and all(s == -1 for s in term_signs) and worst == 0
                      else "BRIDGE-PROBLEM")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

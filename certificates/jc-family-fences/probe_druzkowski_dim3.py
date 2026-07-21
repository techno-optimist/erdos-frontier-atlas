#!/usr/bin/env python3
"""
Druzkowski-style dim-3 Keller maps: F = id + (A x)^3 componentwise cubic.

Scan small integer nilpotent-ish matrices A (3x3) for constant nonzero Jac
with max deg in {3,4,5,6} and rational collisions. Family fence only.
"""

from __future__ import annotations

import itertools
import json
from fractions import Fraction as Q
from pathlib import Path

import search_degree_family as F

HERE = Path(__file__).resolve().parent


def build_druz(A):
    """F_i = x_i + (sum_j A_ij x_j)^3."""
    # A is 3x3 list of lists of ints
    fs = []
    vars_ = [F.X, F.Y, F.Z]
    for i in range(3):
        lin = F.pconst(0)
        for j in range(3):
            if A[i][j]:
                lin = F.padd(lin, F.pscale(vars_[j], A[i][j]))
        cube = F.ppow(lin, 3) if lin else F.pconst(0)
        fs.append(F.padd(vars_[i], cube))
    return tuple(fs)


def main():
    # small integer entries
    range_ = range(-2, 3)
    const_maps = []
    hits = []
    n = 0
    # A not necessarily nilpotent; require det JF constant nonzero
    for entries in itertools.product(range_, repeat=9):
        A = [list(entries[0:3]), list(entries[3:6]), list(entries[6:9])]
        if all(A[i][j] == 0 for i in range(3) for j in range(3)):
            continue
        n += 1
        fs = build_druz(A)
        degs = [F.total_deg(comp) for comp in fs]
        mdeg = max(degs)
        if mdeg < 3 or mdeg > 6:
            continue
        dJ = F.jac_det(fs)
        if not F.is_const_nonzero(dJ):
            continue
        entry = {
            "A": A,
            "degs": degs,
            "max_deg": mdeg,
            "det": str(dJ[(0, 0, 0)]),
        }
        const_maps.append(entry)
        print("const", entry, flush=True)
        col = F.find_collision(fs, bound=4)
        if col:
            p, q, img = col
            hits.append(
                {
                    **entry,
                    "p": [str(x) for x in p],
                    "q": [str(x) for x in q],
                    "image": [str(x) for x in img],
                }
            )
            print("HIT", hits[-1], flush=True)

    out = {
        "schema": "jc.druzkowski_dim3.v1",
        "scanned": n,
        "const_maps": const_maps,
        "hits": hits,
        "status": "FOUND" if hits else "NO_DRUZ_LOW_DEG_CE_IN_BOX",
        "claim_boundary": (
            "Integer A entries in {-2..2}, F=id+(Ax)^3. Family fence only. "
            "Classical Druzkowski reductions change dimension; this is fixed dim-3."
        ),
    }
    path = HERE / "DRUZKOWSKI_DIM3.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "scanned": n,
                "const_count": len(const_maps),
                "hit_count": len(hits),
                "status": out["status"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

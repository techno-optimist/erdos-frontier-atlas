#!/usr/bin/env python3
"""
k=3 Alpöge-neighborhood const-Jac scan for max-deg in {3,4,5,6}.

Fixes (a,b,c,d)=(4,3,3,3) as in Alpöge and sweeps (e,f,g) in a larger box,
plus a modest free-(a,b,c,d) box with smaller ranges. Family fence only.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

# `python3 -I` (isolated mode) implies -P, which drops this script's own directory from
# sys.path, so the sibling import below fails. Re-add it explicitly: that keeps the -I
# hermeticity the replay instructions rely on (no user site-packages) AND makes the
# documented one-liner actually run for a stranger.
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

import search_degree_family as F

HERE = Path(__file__).resolve().parent


def scan(params_iter, label):
    const = []
    hits = []
    n = 0
    for params in params_iter:
        n += 1
        k, a, b, c, d, e, f, g = params
        if (k, a, b, c, d, e, f, g) == (3, 4, 3, 3, 3, 2, -3, -1):
            continue  # known deg-7
        if e == 0 and g == 0:
            continue
        fs = F.build_family(k, a, b, c, d, e, f, g)
        degs = [F.total_deg(comp) for comp in fs]
        mdeg = max(degs)
        if mdeg < 3 or mdeg > 6:
            continue
        dJ = F.jac_det(fs)
        if not F.is_const_nonzero(dJ):
            continue
        entry = {
            "params": dict(k=k, a=a, b=b, c=c, d=d, e=e, f=f, g=g),
            "degs": degs,
            "max_deg": mdeg,
            "det": str(dJ[(0, 0, 0)]),
        }
        const.append(entry)
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
    return n, const, hits


def main():
    # neighborhood of Alpöge f3 coeffs
    near = (
        (3, 4, 3, 3, 3, e, f, g)
        for e in range(-4, 6)
        for f in range(-6, 4)
        for g in range(-4, 4)
    )
    n1, c1, h1 = scan(near, "k3_near")

    # free small a,b,c,d with k=3, modest e,f,g
    free = (
        (3, a, b, c, d, e, f, g)
        for a in range(-1, 6)
        for b in range(-1, 5)
        for c in range(-1, 5)
        for d in range(-1, 5)
        for e in range(-2, 4)
        for f in range(-4, 2)
        for g in range(-2, 2)
    )
    n2, c2, h2 = scan(free, "k3_free_small")

    # control
    control = F.build_family(3, 4, 3, 3, 3, 2, -3, -1)
    dJc = F.jac_det(control)
    control_ok = F.is_const_nonzero(dJc) and max(F.total_deg(x) for x in control) == 7

    out = {
        "schema": "jc.const_jac_k3_near.v1",
        "scanned_near": n1,
        "scanned_free_small": n2,
        "const_maps": c1 + c2,
        "hits": h1 + h2,
        "alpoge_control_ok": control_ok,
        "status": "FOUND" if (h1 or h2) else "NO_LOW_DEGREE_CE_IN_K3_NEAR",
        "claim_boundary": (
            "k=3 neighborhood + small free box; family fence only. "
            "Alpöge itself excluded (deg 7)."
        ),
    }
    path = HERE / "CONST_JAC_K3_NEAR.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        k: (len(v) if isinstance(v, list) else v)
        for k, v in out.items()
        if k not in ("const_maps", "hits")
    }
    summary["const_count"] = len(out["const_maps"])
    summary["hit_count"] = len(out["hits"])
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

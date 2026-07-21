#!/usr/bin/env python3
"""
Exact fiber counts on the smooth Q=0 locus (E=0 off cusp), denser sample.

On Q=0 the anatomy expects fiber size 1 (or 0 on the cusp). A size-2 hit
anywhere would close jc-fiber-count-spectrum-size to 4.
"""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

# `python3 -I` (isolated mode) implies -P, which drops this script's own directory from
# sys.path, so the sibling import below fails. Re-add it explicitly: that keeps the -I
# hermeticity the replay instructions rely on (no user site-packages) AND makes the
# documented one-liner actually run for a stranger.
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

import probe_fiber_size2_exact as F

HERE = Path(__file__).resolve().parent


def Qpoly(t1, t2, t3):
    # same as E
    return F.E(t1, t2, t3)


def on_cusp(t1, t2, t3):
    # gamma: 4 - 3 t2 t3 == 0 and on E
    return 4 - 3 * t2 * t3 == 0


def points_on_q0():
    pts = []
    # fix t1,t2 solve for t3 on E=0 (quadratic)
    for t1n in range(-15, 16):
        for t2n in range(-15, 16):
            for d in (1, 2, 3, 4, 5):
                t1, t2 = Fr(t1n, d), Fr(t2n, d)
                A = 27 * t1**2
                B = t2**3 - 18 * t1 * t2
                C = 16 * t1 - t2**2
                if A == 0:
                    if B != 0:
                        t3 = -C / B
                        pts.append((t1, t2, t3))
                    continue
                disc = B * B - 4 * A * C
                if disc < 0:
                    continue
                for s in range(0, 250):
                    hit = False
                    for sd in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
                        if Fr(s, sd) ** 2 == disc:
                            pts.append((t1, t2, (-B + Fr(s, sd)) / (2 * A)))
                            pts.append((t1, t2, (-B - Fr(s, sd)) / (2 * A)))
                            hit = True
                            break
                    if hit:
                        break
    clean = []
    seen = set()
    for t in pts:
        if Qpoly(*t) != 0:
            continue
        key = tuple(t)
        if key in seen:
            continue
        seen.add(key)
        clean.append(t)
    return clean


def main():
    pts = points_on_q0()
    print(f"Q=0 rational points: {len(pts)}", flush=True)
    hist = Counter()
    size2 = []
    incomplete = 0
    cusp = 0
    smooth = 0
    for i, t in enumerate(pts):
        n, detail, extra = F.fiber_cardinality(*t)
        if extra > 0:
            incomplete += 1
        hist[n] += 1
        if on_cusp(*t):
            cusp += 1
        else:
            smooth += 1
        if n == 2:
            size2.append({"t": [str(c) for c in t], "detail": detail, "cusp": on_cusp(*t)})
            print("SIZE2", t, detail, flush=True)
        if (i + 1) % 100 == 0:
            print("...", i + 1, dict(hist), flush=True)

    out = {
        "schema": "jc.fiber_q0_slice.v1",
        "points_tested": len(pts),
        "cusp_points": cusp,
        "smooth_q0_points": smooth,
        "histogram": {str(k): v for k, v in sorted(hist.items())},
        "size2_hits": size2,
        "incomplete_y_factorizations": incomplete,
        "status": "FOUND_SIZE_2" if size2 else "NO_SIZE_2_ON_Q0_SAMPLE",
        "claim_boundary": (
            "Exact fiber counts on a dense rational sample of V(E)=V(Q). "
            "Not a familywise certificate."
        ),
    }
    path = HERE / "FIBER_Q0_SLICE.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

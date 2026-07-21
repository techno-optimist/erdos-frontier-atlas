#!/usr/bin/env python3
"""
Exact fiber counts on the t2=0 slice of V(E).

E(t1,0,t3)= t1(27 t1 t3^2 + 16). Nonzero t1 forces t3^2 = -16/(27 t1).
"""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

import probe_fiber_size2_exact as F

HERE = Path(__file__).resolve().parent


def points_t2_zero():
    pts = []
    # t1=0,t2=0: any t3
    for t3n in range(-20, 21):
        for d in (1, 2, 3, 4, 5):
            pts.append((Fr(0), Fr(0), Fr(t3n, d)))
    # t1 != 0: t3^2 = -16/(27 t1)
    for t1n in range(-40, 41):
        if t1n == 0:
            continue
        for d in (1, 2, 3, 4, 5, 6, 8, 9, 12, 16, 27):
            t1 = Fr(t1n, d)
            rhs = Fr(-16) / (27 * t1)
            if rhs < 0:
                continue
            for s in range(0, 200):
                for sd in (1, 2, 3, 4, 5, 6, 8, 9, 12, 16, 18, 27):
                    if Fr(s, sd) ** 2 == rhs:
                        pts.append((t1, Fr(0), Fr(s, sd)))
                        pts.append((t1, Fr(0), -Fr(s, sd)))
    clean = []
    seen = set()
    for t in pts:
        if F.E(*t) != 0:
            continue
        key = tuple(t)
        if key in seen:
            continue
        seen.add(key)
        clean.append(t)
    return clean


def main():
    pts = points_t2_zero()
    print(f"t2=0 points: {len(pts)}", flush=True)
    hist = Counter()
    size2 = []
    incomplete = 0
    for t in pts:
        n, detail, extra = F.fiber_cardinality(*t)
        if extra > 0:
            incomplete += 1
        hist[n] += 1
        if n == 2:
            size2.append({"t": [str(c) for c in t], "detail": detail})
            print("SIZE2", t, detail, flush=True)
    out = {
        "schema": "jc.fiber_t2_zero.v1",
        "points_tested": len(pts),
        "histogram": {str(k): v for k, v in sorted(hist.items())},
        "size2_hits": size2,
        "incomplete_y_factorizations": incomplete,
        "status": "FOUND_SIZE_2" if size2 else "NO_SIZE_2_ON_T2_ZERO_SAMPLE",
        "claim_boundary": "Exact fiber counts on rational t2=0 ∩ V(E). Not familywise.",
    }
    (HERE / "FIBER_T2_ZERO.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

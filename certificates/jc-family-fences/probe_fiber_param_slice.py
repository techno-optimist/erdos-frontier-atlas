#!/usr/bin/env python3
"""
Parametrized rational samples on V(E) via the t2-line family.

For fixed rational t2=s ≠ 0 and free rational parameter u, solve E=0 for
(t1,t3) when possible, or sample the known cusp + smooth strata more densely.

Also probes the identity: on E=0 with two distinct rational y-roots of G1,
exactly one y-root lifts (observed pattern → soft conjecture).
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


def y_factor_shape(t1, t2, t3):
    a = F.G1_coeffs(t1, t2, t3)
    p = list(a)
    ys = []
    changed = True
    while changed and F.poly_deg(p) >= 1:
        changed = False
        for r in F.rational_roots(p):
            q, rem = F.poly_divmod(p, [-r, Fr(1)])
            if not rem:
                if r not in ys:
                    ys.append(r)
                p = q
                changed = True
                break
    leftover = F.poly_sqfree(p) if p else []
    return ys, max(0, F.poly_deg(leftover))


def lift_counts(t1, t2, t3, ys):
    """Per rational y, how many fiber points."""
    detail = []
    total = 0
    for y0 in ys:
        c = F.fiber_count_at_y(t1, t2, t3, y0)
        detail.append((str(y0), c))
        total += c
    return total, detail


def denser_points():
    pts = list(F.points_on_E())
    # denser t1,t2 grid
    for t1n in range(-20, 21):
        for t2n in range(-20, 21):
            for d in (1, 2, 3, 4, 5, 6):
                t1, t2 = Fr(t1n, d), Fr(t2n, d)
                A = 27 * t1**2
                B = t2**3 - 18 * t1 * t2
                C = 16 * t1 - t2**2
                if A == 0:
                    if B != 0:
                        pts.append((t1, t2, -C / B))
                    continue
                disc = B * B - 4 * A * C
                if disc < 0:
                    continue
                for s in range(0, 400):
                    hit = False
                    for sd in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16):
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
        if F.E(*t) != 0:
            continue
        key = tuple(t)
        if key in seen:
            continue
        seen.add(key)
        clean.append(t)
    return clean


def main():
    pts = denser_points()
    print("points", len(pts), flush=True)
    hist = Counter()
    two_y_stats = Counter()  # fiber size when exactly 2 rational y
    size2 = []
    lift_patterns = Counter()  # e.g. "1+0", "1+1", "2+0"
    incomplete = 0

    for i, t in enumerate(pts):
        ys, left = y_factor_shape(*t)
        if left > 0:
            incomplete += 1
            n, detail, extra = F.fiber_cardinality(*t)
            hist[n] += 1
            continue
        total, detail = lift_counts(*t, ys)
        hist[total] += 1
        if len(ys) == 2:
            two_y_stats[total] += 1
            pattern = "+".join(str(c) for _, c in detail)
            lift_patterns[pattern] += 1
        if total == 2:
            size2.append(
                {
                    "t": [str(c) for c in t],
                    "ys": [str(y) for y in ys],
                    "detail": detail,
                }
            )
            print("SIZE2", t, detail, flush=True)
        if (i + 1) % 100 == 0:
            print("...", i + 1, dict(hist), flush=True)

    out = {
        "schema": "jc.fiber_param_slice.v1",
        "points_tested": len(pts),
        "histogram_fiber": {str(k): v for k, v in sorted(hist.items())},
        "two_rational_y_fiber_hist": {
            str(k): v for k, v in sorted(two_y_stats.items())
        },
        "two_y_lift_patterns": dict(sorted(lift_patterns.items())),
        "size2_hits": size2,
        "incomplete_y_factorizations": incomplete,
        "status": "FOUND_SIZE_2" if size2 else "NO_SIZE_2_IN_DENSE_SAMPLE",
        "observation": (
            "Among points with exactly two distinct rational y-roots of G1, "
            "the lift pattern and fiber size are recorded. Soft conjecture: "
            "pattern is always 1+0 (one y lifts once, the other never), never 1+1."
        ),
        "claim_boundary": (
            "Dense rational sample; not familywise. Soft conjecture is observational."
        ),
    }
    path = HERE / "FIBER_PARAM_DENSE.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Probe fiber size 2 via the fiber cubic discriminant locus.

On V(E), disc_Y(G1) = -2916 t1^2 E vanishes identically, so G1 always has a
repeated root factor over the algebraic closure when E=0. Size-2 fibers would
require either two distinct simple y-roots each lifting once, or a double y
that lifts to two distinct (x,z). This probe classifies rational points by
squarefree y-factor shape + exact fiber cardinality.
"""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

import probe_fiber_size2_exact as F

HERE = Path(__file__).resolve().parent


def y_factor_shape(t1, t2, t3):
    """Return (num_distinct_rational_y, leftover_sqfree_deg, rational_ys)."""
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
    return len(ys), max(0, F.poly_deg(leftover)), ys


def sample_points():
    # reuse expanded generator logic lightly
    pts = F.points_on_E()
    # denser Q=0
    for t1n in range(-12, 13):
        for t2n in range(-12, 13):
            for d in (1, 2, 3, 4):
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
                for s in range(0, 180):
                    hit = False
                    for sd in (1, 2, 3, 4, 5, 6, 8, 9):
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
    pts = sample_points()
    print("points", len(pts), flush=True)
    hist_fiber = Counter()
    hist_shape = Counter()
    size2 = []
    multi_y_with_fiber = Counter()  # (n_rat_y, fiber) counts
    incomplete = 0

    for i, t in enumerate(pts):
        n_y, left_deg, ys = y_factor_shape(*t)
        n, detail, extra = F.fiber_cardinality(*t)
        if extra > 0:
            incomplete += 1
        hist_fiber[n] += 1
        shape = f"rat_y={n_y},leftover={left_deg}"
        hist_shape[shape] += 1
        multi_y_with_fiber[(n_y, n)] += 1
        if n == 2:
            size2.append(
                {
                    "t": [str(c) for c in t],
                    "fiber": n,
                    "rat_y": n_y,
                    "leftover_deg": left_deg,
                    "ys": [str(y) for y in ys],
                    "detail": detail,
                }
            )
            print("SIZE2", t, n_y, left_deg, detail, flush=True)
        if (i + 1) % 100 == 0:
            print("...", i + 1, dict(hist_fiber), flush=True)

    out = {
        "schema": "jc.fiber_size2_disc_shape.v1",
        "points_tested": len(pts),
        "histogram_fiber": {str(k): v for k, v in sorted(hist_fiber.items())},
        "histogram_y_shape": dict(sorted(hist_shape.items())),
        "fiber_by_rat_y_count": {
            f"rat_y={a}_fiber={b}": c
            for (a, b), c in sorted(multi_y_with_fiber.items())
        },
        "size2_hits": size2,
        "incomplete_y_factorizations": incomplete,
        "status": "FOUND_SIZE_2" if size2 else "NO_SIZE_2_IN_SHAPE_SAMPLE",
        "claim_boundary": (
            "Classifies rational V(E) points by G1 y-factor shape vs fiber size. "
            "Not a familywise no-go for size 2."
        ),
    }
    path = HERE / "FIBER_SIZE2_SHAPE.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

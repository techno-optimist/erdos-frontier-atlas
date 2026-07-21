#!/usr/bin/env python3
"""Expand Alpöge-shaped degree family: wider k=2 box + k=3 neighborhood + k=4 deg≤6 filter."""

from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

import search_degree_family as SDF

HERE = Path(__file__).resolve().parent


def scan_k2_wide():
    hits = []
    const_maps = []
    scanned = 0
    # Wider than original {-2..2} CONST_JAC_K2: a..g in {-3..3} but skip zero-heavy
    for a, b, c, d, e, f, g in itertools.product(range(-3, 4), repeat=7):
        scanned += 1
        if e == 0 and g == 0:
            continue
        fs = SDF.build_family(2, a, b, c, d, e, f, g)
        degs = [SDF.total_deg(comp) for comp in fs]
        mdeg = max(degs)
        if mdeg < 3 or mdeg > 6:
            continue
        dJ = SDF.jac_det(fs)
        if not SDF.is_const_nonzero(dJ):
            continue
        rec = {
            "params": {"k": 2, "a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g},
            "degs": degs,
            "max_deg": mdeg,
            "det": str(dJ[(0, 0, 0)]),
        }
        const_maps.append(rec)
        col = SDF.find_collision(fs, bound=3)
        if col:
            p, q, img = col
            hits.append(
                {
                    **rec,
                    "p": [str(x) for x in p],
                    "q": [str(x) for x in q],
                    "image": [str(x) for x in img],
                }
            )
    return scanned, const_maps, hits


def scan_k3_near():
    hits = []
    const_maps = []
    scanned = 0
    # Neighborhood of Alpöge (4,3,3,3,2,-3,-1) radius 2
    for da, db, dc, dd, de, df, dg in itertools.product(range(-2, 3), repeat=7):
        a, b, c, d, e, f, g = 4 + da, 3 + db, 3 + dc, 3 + dd, 2 + de, -3 + df, -1 + dg
        scanned += 1
        if (a, b, c, d, e, f, g) == (4, 3, 3, 3, 2, -3, -1):
            continue
        if e == 0 and g == 0:
            continue
        fs = SDF.build_family(3, a, b, c, d, e, f, g)
        degs = [SDF.total_deg(comp) for comp in fs]
        mdeg = max(degs)
        if mdeg < 3 or mdeg > 6:
            continue
        dJ = SDF.jac_det(fs)
        if not SDF.is_const_nonzero(dJ):
            continue
        rec = {
            "params": {"k": 3, "a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g},
            "degs": degs,
            "max_deg": mdeg,
            "det": str(dJ[(0, 0, 0)]),
        }
        const_maps.append(rec)
        col = SDF.find_collision(fs, bound=3)
        if col:
            p, q, img = col
            hits.append(
                {
                    **rec,
                    "p": [str(x) for x in p],
                    "q": [str(x) for x in q],
                    "image": [str(x) for x in img],
                }
            )
    return scanned, const_maps, hits


def scan_k4_lowdeg():
    """k=4 maps that still have max total deg ≤ 6 (rare) — const Jac + collision."""
    hits = []
    const_maps = []
    scanned = 0
    for a, b, c, d, e, f, g in itertools.product(
        range(-2, 3), range(-2, 3), range(-2, 3), range(-2, 3),
        range(-2, 3), range(-2, 3), range(-2, 3),
    ):
        scanned += 1
        if e == 0 and g == 0:
            continue
        fs = SDF.build_family(4, a, b, c, d, e, f, g)
        degs = [SDF.total_deg(comp) for comp in fs]
        mdeg = max(degs)
        if mdeg < 3 or mdeg > 6:
            continue
        dJ = SDF.jac_det(fs)
        if not SDF.is_const_nonzero(dJ):
            continue
        rec = {
            "params": {"k": 4, "a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g},
            "degs": degs,
            "max_deg": mdeg,
            "det": str(dJ[(0, 0, 0)]),
        }
        const_maps.append(rec)
        col = SDF.find_collision(fs, bound=3)
        if col:
            p, q, img = col
            hits.append(
                {
                    **rec,
                    "p": [str(x) for x in p],
                    "q": [str(x) for x in q],
                    "image": [str(x) for x in img],
                }
            )
    return scanned, const_maps, hits


def main():
    t0 = time.time()
    s2, c2, h2 = scan_k2_wide()
    print(f"k2 wide: scanned={s2} const_deg3-6={len(c2)} hits={len(h2)}", flush=True)
    s3, c3, h3 = scan_k3_near()
    print(f"k3 near: scanned={s3} const_deg3-6={len(c3)} hits={len(h3)}", flush=True)
    s4, c4, h4 = scan_k4_lowdeg()
    print(f"k4 lowdeg: scanned={s4} const_deg3-6={len(c4)} hits={len(h4)}", flush=True)

    control = SDF.build_family(3, 4, 3, 3, 3, 2, -3, -1)
    dJc = SDF.jac_det(control)
    control_ok = SDF.is_const_nonzero(dJc) and max(SDF.total_deg(f) for f in control) == 7

    all_hits = h2 + h3 + h4
    out = {
        "schema": "jc.degree_family_expand.v1",
        "status": "FOUND_LOW_DEGREE_COUNTEREXAMPLE" if all_hits else "NO_HIT_IN_EXPANDED_FAMILY",
        "k2_wide_m3": {
            "scanned": s2,
            "const_jacobian_deg_3_to_6": len(c2),
            "collision_hits": h2,
            "sample_const": c2[:10],
        },
        "k3_near_radius2": {
            "scanned": s3,
            "const_jacobian_deg_3_to_6": len(c3),
            "collision_hits": h3,
            "sample_const": c3[:10],
        },
        "k4_deg_le6": {
            "scanned": s4,
            "const_jacobian_deg_3_to_6": len(c4),
            "collision_hits": h4,
        },
        "alpoge_control_ok": control_ok,
        "elapsed_sec": round(time.time() - t0, 3),
        "claim_boundary": (
            "Expanded family fence only (k=2 wide, k=3 near, k=4 filtered). "
            "Not a closed degree bracket outside the family."
        ),
    }
    path = HERE / "DEGREE_FAMILY_EXPAND.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("status", "alpoge_control_ok", "elapsed_sec")}, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()

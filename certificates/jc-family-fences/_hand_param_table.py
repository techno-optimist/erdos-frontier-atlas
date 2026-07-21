#!/usr/bin/env python3
"""
Tiny self-contained parametric soft-lemma table (no sibling import).
Produces FIBER_TWO_Y_LEMMA.json when executed.
stdlib only.
"""
from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent


def E(t1, t2, t3):
    return (
        27 * t1**2 * t3**2
        - 18 * t1 * t2 * t3
        + 16 * t1
        + t2**3 * t3
        - t2**2
    )


def lifts(t1, t2, t3, y, x):
    u = 1 + y * x
    eqs = [
        (u**3, (y**2) * u * (4 + 3 * y * x) - t1),
        (3 * x * u**2, y + 3 * x * (y**2) * (4 + 3 * y * x) - t2),
        (-(x**3), 2 * x - 3 * (x**2) * y - t3),
    ]
    if all(a == 0 for a, _ in eqs):
        return all(b == 0 for _, b in eqs)
    z = None
    for a, b in eqs:
        if a != 0:
            z = -b / a
            break
    return all(a * z + b == 0 for a, b in eqs)


def build(a, s):
    a, s = Fr(a), Fr(s)
    if 2 * a == s:
        return None
    t1 = a * (s - a) / 3
    b = 3 * s / 2 - 2 * a
    if a == b:
        return None
    if t1 == 0:
        if a != s or s == 0:
            return None
        t3 = Fr(1) / s
        b = -s / 2
        return (Fr(0), s, t3), a, b
    t3 = (-2 * a * a * b + 18 * t1 * s - s**3) / (27 * t1 * t1)
    return (t1, s, t3), a, b


def grid():
    vals = []
    for n in range(-10, 11):
        for d in (1, 2, 3, 4, 5):
            vals.append(Fr(n, d))
    # unique preserve order
    out, seen = [], set()
    for v in vals:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def main():
    g = grid()
    which = Counter()
    hist = Counter()
    size2 = []
    fails = []
    seen = set()
    points = 0
    cusp_n = 0
    e_fail = 0

    for a in g:
        for s in g:
            built = build(a, s)
            if built is None:
                continue
            t, aa, bb = built
            if t in seen:
                continue
            seen.add(t)
            t1, t2, t3 = t
            if E(*t) != 0:
                e_fail += 1
                fails.append({"kind": "E", "t": list(map(str, t))})
                continue
            points += 1
            d = 4 - 3 * t2 * t3
            if d == 0:
                cusp_n += 1
                # no finite forced x; engine-free: try would need free x — mark cusp
                which["cusp"] += 1
                hist[0] += 1  # cusp theorem: empty (anatomy); not re-proved here
                continue
            x = (2 * t3) / d
            la = lifts(t1, t2, t3, aa, x)
            lb = lifts(t1, t2, t3, bb, x)
            total = (1 if la else 0) + (1 if lb else 0)
            hist[total] += 1
            if la and lb:
                which["both"] += 1
                size2.append({"t": list(map(str, t)), "a": str(aa), "b": str(bb)})
            elif (not la) and lb:
                which["simple_only"] += 1
            elif la and (not lb):
                which["double_only"] += 1
                fails.append({"kind": "double_only", "t": list(map(str, t)), "a": str(aa), "b": str(bb)})
            else:
                which["neither"] += 1
            if total == 2:
                size2.append({"t": list(map(str, t)), "a": str(aa), "b": str(bb), "tag": "size2"})

    soft_ok = which.get("both", 0) == 0 and which.get("double_only", 0) == 0 and not size2 and e_fail == 0
    out = {
        "schema": "jc.fiber_two_y_lemma.v1",
        "points_tested": points,
        "histogram_fiber_forced_x": {str(k): v for k, v in sorted(hist.items())},
        "which_lifts": dict(sorted(which.items())),
        "cusp_count": cusp_n,
        "e_fail": e_fail,
        "size2_hits": size2,
        "failure_samples": fails[:20],
        "soft_lemma": {
            "statement": (
                "If t in V(E) is obtained from rational double root a and t2=s "
                "via the standard parametrization, with simple root b=3s/2-2a, "
                "then on V(E)\\\\gamma the forced-x test lifts exactly the simple "
                "root (never the double root; never both)."
            ),
            "status": "HOLDS_ON_PARAMETRIC_SAMPLE" if soft_ok else "FAILS_ON_SAMPLE",
            "sample_support": points,
        },
        "status": "FOUND_SIZE_2" if size2 else "NO_SIZE_2_IN_PARAMETRIC_SAMPLE",
        "claim_boundary": (
            "Forced-x lift test on parametric rational double+simple family. "
            "Cusp points counted as fiber 0 by anatomy theorem (not re-derived). "
            "Not familywise over C. Does not close spectrum bracket."
        ),
        "method": "forced_x_only_stdlib_fractions",
    }
    path = HERE / "FIBER_TWO_Y_LEMMA.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    print("Wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

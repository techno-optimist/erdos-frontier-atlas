#!/usr/bin/env python3
"""
No size-2 fibers on V(E) for Alpöge's map — identity-shaped certificate.

CONDITIONAL on the anatomy annihilators (G1, Phi_x) already certified in
certificates/jc-anatomy/certify_nonproperness.py.

Argument (human steps elementary; machine checks specializations + samples):

  (H1) disc_Y(G1) = -2916 t1^2 E  (anatomy I4). On V(E), G1 has a multiple
       root over C: either triple, or double root a + simple root b.
  (H2) Phi_x = E X^3 + (4-3 t2 t3) X - 2 t3  (anatomy I2). On V(E),
       Phi_x reduces to (4-3 t2 t3) X - 2 t3. Let d = 4-3 t2 t3.
         - If d ≠ 0: unique forced x* = 2 t3 / d.
         - If d = 0: then Phi_x ≡ -2 t3; on the cusp t3 = 4/(3 t2) ≠ 0
           (t2≠0), so Phi_x is a nonzero constant — no x exists — fiber empty.
         - t1=t2=0: G1=2y^3 (triple at 0); d=4≠0; unique x*; fiber ≤1.
  (H3) Every fiber point has y-root of G1 (anatomy I1) and x-root of Phi_x.
  (H4) DOUBLE-ROOT NON-LIFTING. If a is a multiple root of G1 then
         t1 = a(t2 - a)/3  (from G1'=0), and for every x:
           u(a - t2) + 3 x t1 = a - t2    identically in x
         where u = 1 + a x. Hence R12 ∝ u^2 (a - t2).
         - If a ≠ t2 and u ≠ 0: R12 ≠ 0 ⇒ no lift.
         - If u = 0 (x = -1/a, a≠0): a1 = 0 and b1 = -t1; if t1 ≠ 0 then
           p1 = -t1 ≠ 0 for all z ⇒ no lift.
         - If t1 = 0 and a = t2 ≠ 0: direct forced-x check (sample + identity
           path below) shows inconsistency; covered parametrically.
  (H5) Therefore on V(E)\\{t1=t2=0} the double root never lifts. At most the
       simple root can lift, and with unique x* at most once. Fiber ≤ 1.
  (H6) On {t1=t2=0} ⊂ V(E): unique y=0, unique x*, fiber ≤ 1 (realized =1
       at anchors).

Conclusion: #F^{-1}(t) ∈ {0,1} for all t ∈ V(E). Combined with generic fiber 3
off {t1 t2 E ≠ 0} and empty fibers on the cusp curve, the fiber-count spectrum
is exactly {0,1,3} — size 3. Size 2 does not occur.

Claim boundary: this package machine-checks the R12 double-root identity on a
dense rational (a,s,x) grid, forced-x non-lifting of the double root on a dense
parametric rational sample of V(E), engine fiber counts on an expanded rational
V(E) sample (no size-2), and agreement with Phi_x. The passage from the
identity to all complex t is the elementary algebra in (H4), same style as
anatomy human steps. Full familywise formalization over C[t] without
parametrization remains a human case-split on the annihilator identities
already certified in jc-anatomy.

Does NOT mint DOI. Does NOT edit frozen jc-anatomy certs.
"""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction as Fr
from math import isqrt
from pathlib import Path

import sys as _sys
import pathlib as _pathlib

_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

import probe_fiber_size2_exact as F

HERE = Path(__file__).resolve().parent


# ---------- (H4) identity specializations ----------
def double_root_r12_residual(a, s, x):
    """
    u(a-s) + 3 x t1  with t1 = a(s-a)/3.
    Identity claims this equals a-s for all x.
    """
    t1 = a * (s - a) / 3
    u = 1 + a * x
    return u * (a - s) + 3 * x * t1


def check_r12_identity_grid():
    """Dense rational specializations of the (H4) identity."""
    vals = []
    for n in range(-8, 9):
        for d in (1, 2, 3, 4, 5):
            vals.append(Fr(n, d))
    n_ok = 0
    n_fail = 0
    samples_fail = []
    for a in vals:
        for s in vals:
            t1 = a * (s - a) / 3
            for x in vals:
                lhs = double_root_r12_residual(a, s, x)
                rhs = a - s
                if lhs == rhs:
                    n_ok += 1
                else:
                    n_fail += 1
                    if len(samples_fail) < 5:
                        samples_fail.append(
                            {"a": str(a), "s": str(s), "x": str(x), "lhs": str(lhs), "rhs": str(rhs)}
                        )
    return n_ok, n_fail, samples_fail


def lifts_forced(t1, t2, t3, y, x):
    u = 1 + y * x
    eqs = [
        (u**3, (y**2) * u * (4 + 3 * y * x) - t1),
        (3 * x * u**2, y + 3 * x * (y**2) * (4 + 3 * y * x) - t2),
        (-(x**3), 2 * x - 3 * (x**2) * y - t3),
    ]
    if all(aa == 0 for aa, _ in eqs):
        return all(bb == 0 for _, bb in eqs)
    z = None
    for aa, bb in eqs:
        if aa != 0:
            z = -bb / aa
            break
    return all(aa * z + bb == 0 for aa, bb in eqs)


def u0_obstruction_grid():
    """
    When u=0 (x=-1/a) and t1≠0, b1 should equal -t1 (p1 never zero).
    Check: y=a, x=-1/a, u=0 ⇒ b1 = -t1.
    """
    vals = [Fr(n, d) for n in range(-7, 8) for d in (1, 2, 3, 4) if not (n == 0 and d != 1)]
    # unique nonzero a
    As = []
    seen = set()
    for a in vals:
        if a != 0 and a not in seen:
            seen.add(a)
            As.append(a)
    n_ok = 0
    n_fail = 0
    for a in As:
        for s in As + [Fr(0)]:
            t1 = a * (s - a) / 3
            if t1 == 0:
                continue
            x = -Fr(1) / a
            y = a
            u = 1 + y * x  # 0
            assert u == 0
            b1 = (y**2) * u * (4 + 3 * y * x) - t1
            if b1 == -t1:
                n_ok += 1
            else:
                n_fail += 1
    return n_ok, n_fail


def parametric_double_never_lifts():
    """Parametric (a,s) family: double root never lifts under forced x."""
    vals = []
    for n in range(-10, 11):
        for d in (1, 2, 3, 4, 5):
            vals.append(Fr(n, d))
    # unique
    grid, seen = [], set()
    for v in vals:
        if v not in seen:
            seen.add(v)
            grid.append(v)

    which = Counter()
    size2 = []
    fails = []
    points = 0
    seen_t = set()
    hist = Counter()

    for a in grid:
        for s in grid:
            if 2 * a == s:
                continue
            t1 = a * (s - a) / 3
            b = 3 * s / 2 - 2 * a
            if a == b:
                continue
            if t1 == 0:
                if a != s or s == 0:
                    continue
                t3 = Fr(1) / s
                b = -s / 2
                t = (Fr(0), s, t3)
            else:
                t3 = (-2 * a * a * b + 18 * t1 * s - s**3) / (27 * t1 * t1)
                t = (t1, s, t3)
            if t in seen_t:
                continue
            seen_t.add(t)
            if F.E(*t) != 0:
                fails.append({"kind": "E", "t": list(map(str, t))})
                continue
            points += 1
            t1, t2, t3 = t
            d = Fr(4) - 3 * t2 * t3
            if d == 0:
                which["cusp_or_phi_empty"] += 1
                hist[0] += 1
                continue
            x = (2 * t3) / d
            la = lifts_forced(t1, t2, t3, a, x)
            lb = lifts_forced(t1, t2, t3, b, x)
            # engine cross-check
            ca = F.fiber_count_at_y(t1, t2, t3, a)
            cb = F.fiber_count_at_y(t1, t2, t3, b)
            if (ca >= 1) != la or (cb >= 1) != lb:
                fails.append(
                    {
                        "kind": "engine_fx",
                        "t": list(map(str, t)),
                        "la": la,
                        "lb": lb,
                        "ca": ca,
                        "cb": cb,
                    }
                )
            if la:
                fails.append({"kind": "double_lifted", "t": list(map(str, t)), "a": str(a), "b": str(b)})
                which["double_lifted"] += 1
            elif lb:
                which["simple_only"] += 1
            else:
                which["neither"] += 1
            total = (1 if la else 0) + (1 if lb else 0)
            # also trust engine total for histogram
            total_e = ca + cb
            hist[total_e] += 1
            if total_e == 2 or total == 2:
                size2.append({"t": list(map(str, t)), "ca": ca, "cb": cb, "la": la, "lb": lb})
    return points, which, hist, size2, fails


def large_ve_sample():
    """Expanded rational V(E) sample with shape classification + fiber sizes."""
    pts = list(F.points_on_E())
    dens = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12)
    for t1n in range(-20, 21):
        for t2n in range(-20, 21):
            for d in dens:
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
                num, den = disc.numerator, disc.denominator
                if num >= 0:
                    sn, sdn = isqrt(num), isqrt(den)
                    if sn * sn == num and sdn * sdn == den:
                        s = Fr(sn, sdn)
                        pts.append((t1, t2, (-B + s) / (2 * A)))
                        pts.append((t1, t2, (-B - s) / (2 * A)))
    clean, seen = [], set()
    for t in pts:
        if F.E(*t) != 0:
            continue
        key = tuple(t)
        if key in seen:
            continue
        seen.add(key)
        clean.append(t)
    return clean


def y_shape(t1, t2, t3):
    a = F.G1_coeffs(t1, t2, t3)
    g = F.poly_gcd(a, F.poly_diff(a))
    mult_root = None
    if F.poly_deg(g) == 1:
        mult_root = -g[0] / g[1]
    p = list(a)
    ys = []
    mult = {}
    changed = True
    while changed and F.poly_deg(p) >= 1:
        changed = False
        for r in F.rational_roots(p):
            q, rem = F.poly_divmod(p, [-r, Fr(1)])
            if not rem:
                mult[r] = mult.get(r, 0) + 1
                if r not in ys:
                    ys.append(r)
                p = q
                changed = True
                break
    left = max(0, F.poly_deg(F.poly_sqfree(p) if p else []))
    if left > 0:
        shape = f"rat_y={len(ys)},leftover={left}"
    elif len(ys) == 1 and mult.get(ys[0], 0) == 3:
        shape = "triple"
    elif len(ys) == 2:
        shape = "double+simple"
    else:
        shape = f"rat_y={len(ys)},mult={mult}"
    return ys, mult, mult_root, left, shape


def main():
    print("=== (H4) R12 identity specializations ===", flush=True)
    id_ok, id_fail, id_fail_s = check_r12_identity_grid()
    print(f"  ok={id_ok} fail={id_fail}", flush=True)

    print("=== u=0 obstruction specializations ===", flush=True)
    u0_ok, u0_fail = u0_obstruction_grid()
    print(f"  ok={u0_ok} fail={u0_fail}", flush=True)

    print("=== parametric double-never-lifts ===", flush=True)
    pts_p, which, hist_p, size2_p, fails_p = parametric_double_never_lifts()
    print(f"  points={pts_p} which={dict(which)} hist={dict(hist_p)} size2={len(size2_p)}", flush=True)

    print("=== large rational V(E) sample ===", flush=True)
    pts = large_ve_sample()
    print(f"  points={len(pts)}", flush=True)
    hist = Counter()
    shapes = Counter()
    fiber_by_shape = Counter()
    size2 = []
    leftover_pos = 0
    two_y_which = Counter()
    double_lifted = 0
    incomplete = 0

    for i, t in enumerate(pts):
        ys, mult, mroot, left, shape = y_shape(*t)
        shapes[shape] += 1
        if left > 0:
            leftover_pos += 1
            incomplete += 1
        total = 0
        detail = []
        for y0 in ys:
            c = F.fiber_count_at_y(*t, y0)
            detail.append((y0, c))
            total += c
        hist[total] += 1
        fiber_by_shape[f"{shape}|f={total}"] += 1
        if shape == "double+simple" and mroot in ys:
            c_d = next(c for y, c in detail if y == mroot)
            c_s = next(c for y, c in detail if y != mroot)
            if c_d > 0 and c_s > 0:
                two_y_which["both"] += 1
            elif c_d > 0:
                two_y_which["double_only"] += 1
                double_lifted += 1
            elif c_s > 0:
                two_y_which["simple_only"] += 1
            else:
                two_y_which["neither"] += 1
        if total == 2:
            size2.append(
                {
                    "t": list(map(str, t)),
                    "shape": shape,
                    "detail": [(str(y), c) for y, c in detail],
                }
            )
            print("SIZE2", t, shape, detail, flush=True)
        if (i + 1) % 200 == 0:
            print(f"  ... {i+1} hist={dict(hist)}", flush=True)

    argument_ok = (
        id_fail == 0
        and u0_fail == 0
        and which.get("double_lifted", 0) == 0
        and double_lifted == 0
        and not size2
        and not size2_p
        and leftover_pos == 0
    )

    out = {
        "schema": "jc.fiber_no_size2_ve.v1",
        "r12_identity_specializations": {
            "ok": id_ok,
            "fail": id_fail,
            "fail_samples": id_fail_s,
        },
        "u0_obstruction_specializations": {"ok": u0_ok, "fail": u0_fail},
        "parametric_family": {
            "points": pts_p,
            "which_lifts": dict(sorted(which.items())),
            "histogram_fiber": {str(k): v for k, v in sorted(hist_p.items())},
            "size2_hits": size2_p,
            "failure_samples": fails_p[:20],
        },
        "rational_VE_sample": {
            "points_tested": len(pts),
            "histogram_fiber": {str(k): v for k, v in sorted(hist.items())},
            "histogram_y_shape": dict(sorted(shapes.items())),
            "fiber_by_shape": dict(sorted(fiber_by_shape.items())),
            "two_y_which_lifts": dict(sorted(two_y_which.items())),
            "leftover_positive_count": leftover_pos,
            "incomplete_y_factorizations": incomplete,
            "size2_hits": size2,
        },
        "theorem_sketch": {
            "statement": (
                "On V(E), #F^{-1}(t) ∈ {0,1} for every complex t. Hence size-2 "
                "fibers do not occur. Fiber-count spectrum of F is exactly {0,1,3}."
            ),
            "status": "ARGUMENT_PLUS_SAMPLE_OK" if argument_ok else "NEEDS_REVIEW",
            "human_steps": [
                "disc_Y(G1)=-2916 t1^2 E (anatomy)",
                "Phi_x annihilator (anatomy); reduces on E=0 to linear or empty",
                "R12 identity at double root: residual = a-t2 independent of x",
                "u=0 obstruction: b1=-t1 when t1≠0",
                "case t1=t2=0: triple root, unique x, fiber≤1",
            ],
            "note": (
                "Machine checks specializations + rational samples. Full C-case "
                "split is elementary algebra on certified annihilators. Soft "
                "upgrade of prior two-y conjecture to structural non-lifting of "
                "the double root."
            ),
        },
        "status": "FOUND_SIZE_2" if (size2 or size2_p) else "NO_SIZE_2",
        "spectrum_implication": {
            "known": {"0": "cusp curve (anatomy theorem)", "1": "V(E) generic / anchors", "3": "off {t1 t2 E=0}"},
            "size2": "ruled out by argument above (conditional on anatomy annihilators)",
            "bracket_note": (
                "If the human case-split is accepted, jc-fiber-count-spectrum-size "
                "closes to 3. This package does NOT auto-update the ledger; treat "
                "as a proposed fence pending review of the human steps."
            ),
        },
        "claim_boundary": (
            "Conditional on jc-anatomy annihilators. Identity (H4) checked on a "
            "rational grid (not a formal poly identity certificate in C[a,s,x]). "
            "Does not mint DOI. Ledger update is a separate human decision."
        ),
    }
    path = HERE / "FIBER_NO_SIZE2_VE.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"\nWrote {path}", flush=True)
    return 0 if argument_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

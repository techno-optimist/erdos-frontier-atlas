#!/usr/bin/env python3
"""
Push the size-2 fiber question on Alpöge's map (rational V(E) sample).

Uses probe_fiber_size2_exact engine (stdlib fractions only).

Goals (honest, no false closed brackets):
  1. Larger rational sample on V(E); classify G1 y-factor shapes vs fiber size.
  2. Soft-lemma formalization: if G1 has two distinct rational roots, at most
     one lifts — cross-checked with reduced Phi_x annihilator on V(E)\\γ.
  3. Shape rat_y=1 + quadratic leftover: can fiber be 2? (on rational t ∈ V(E)
     this shape should be empty: disc_Y(G1)=0 ⇒ multiple root ∈ Q).
  4. Multiplicity reading: double root never lifts; simple root always lifts
     off the cusp (observational on the sample).

Does NOT claim jc-fiber-count-spectrum-size is closed. Does NOT mint DOI.
"""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction as Fr
from math import isqrt
from pathlib import Path

# `python3 -I` drops this script's directory from sys.path; re-add for sibling import.
import sys as _sys
import pathlib as _pathlib

_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

import probe_fiber_size2_exact as F

HERE = Path(__file__).resolve().parent


# ---------- reduced Phi_x on V(E) ----------
def delta_phi(t2, t3):
    """Coefficient of X in Phi_x |_{E=0} = (4 - 3 t2 t3) X - 2 t3."""
    return Fr(4) - 3 * t2 * t3


def forced_x(t1, t2, t3):
    """
    On V(E)\\γ, Phi_x reduces to linear: x = 2 t3 / (4 - 3 t2 t3).
    Returns None if on cusp (delta=0) or if residual annihilator is 0=0
    (t3=0 and delta=0 is cusp-ish; t3=0 and delta≠0 forces x=0).
    """
    d = delta_phi(t2, t3)
    if d == 0:
        return None  # cusp stratum γ when also E=0
    return (2 * t3) / d


def on_cusp(t1, t2, t3):
    return delta_phi(t2, t3) == 0 and F.E(t1, t2, t3) == 0


# ---------- G1 multiplicity / shape ----------
def y_factor_full(t1, t2, t3):
    """
    Factor G1 over Q completely for rational roots.
    Returns dict:
      ys: list of distinct rational roots
      mult: {y: multiplicity}
      leftover_deg: deg of squarefree leftover (should be 0 on rational V(E))
      leftover_coeffs: residual poly coeffs
      multiple_root: the rational multiple root from gcd(G1,G1'), or None
      simple_root: the other rational root if shape is double+simple, else None
      shape: tag string
    """
    a = F.G1_coeffs(t1, t2, t3)
    # multiple root via gcd(G1, G1') over Q
    g1p = F.poly_diff(a)
    g = F.poly_gcd(a, g1p)
    multiple_root = None
    if F.poly_deg(g) == 1:
        # monic g = [-r, 1] ⇒ root r
        multiple_root = -g[0] / g[1] if g[1] != 0 else None
    elif F.poly_deg(g) >= 2:
        # unexpected for a genuine cubic double root; record
        multiple_root = "deg>=2"

    p = list(a)
    mult = {}
    ys = []
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
    leftover = F.poly_sqfree(p) if p else []
    left_deg = max(0, F.poly_deg(leftover))

    simple_root = None
    if len(ys) == 2 and multiple_root in ys:
        for y in ys:
            if y != multiple_root:
                simple_root = y
                break
    elif len(ys) == 1 and mult.get(ys[0], 0) == 3:
        simple_root = None  # triple

    if left_deg > 0:
        shape = f"rat_y={len(ys)},leftover={left_deg}"
    elif len(ys) == 1 and mult.get(ys[0], 0) == 3:
        shape = "triple"
    elif len(ys) == 2:
        shape = "double+simple"
    elif len(ys) == 1:
        shape = f"rat_y=1,mult={mult.get(ys[0], 0)}"
    else:
        shape = f"rat_y={len(ys)},leftover={left_deg}"

    return {
        "ys": ys,
        "mult": mult,
        "leftover_deg": left_deg,
        "leftover": leftover,
        "multiple_root": multiple_root,
        "simple_root": simple_root,
        "shape": shape,
    }


def lift_detail(t1, t2, t3, ys):
    detail = []
    total = 0
    for y0 in ys:
        c = F.fiber_count_at_y(t1, t2, t3, y0)
        detail.append((y0, c))
        total += c
    return total, detail


def check_forced_x_consistency(t1, t2, t3, y0, xstar):
    """
    At forced x*, does there exist z solving F(x*,y0,z)=t?
    Linear in z: use any equation with a_i ≠ 0; check all three.
    Returns (lifts: bool, n_consistent_eqns or error tag).
    """
    # a1 = (1+y0 x)^3, b1 = y0^2 (1+y0 x)(4+3 y0 x) - t1
    # a2 = 3x (1+y0 x)^2, b2 = y0 + 3x y0^2 (4+3 y0 x) - t2
    # a3 = -x^3, b3 = 2x - 3 x^2 y0 - t3
    x, y = xstar, y0
    u = 1 + y * x
    a1 = u**3
    b1 = (y**2) * u * (4 + 3 * y * x) - t1
    a2 = 3 * x * u**2
    b2 = y + 3 * x * y**2 * (4 + 3 * y * x) - t2
    a3 = -(x**3)
    b3 = 2 * x - 3 * x**2 * y - t3

    # If all a_i == 0, free/no z
    if a1 == 0 and a2 == 0 and a3 == 0:
        # then need all b_i == 0 for infinite solutions, else none
        if b1 == 0 and b2 == 0 and b3 == 0:
            return True, "all_a_zero_identity"
        return False, "all_a_zero_inconsistent"

    # Find z from first nonzero a_i; verify others
    z = None
    for a, b in ((a1, b1), (a2, b2), (a3, b3)):
        if a != 0:
            z = -b / a
            break
    assert z is not None
    ok = True
    for a, b in ((a1, b1), (a2, b2), (a3, b3)):
        if a * z + b != 0:
            ok = False
            break
    return ok, z


# ---------- denser rational points on V(E) ----------
def large_points_on_E():
    """Larger rational sample than points_on_E / denser_points."""
    pts = list(F.points_on_E())

    # denser (t1,t2) grid with more denominators; disc perfect-square scan
    dens = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12)
    for t1n in range(-24, 25):
        for t2n in range(-24, 25):
            for d in dens:
                t1, t2 = Fr(t1n, d), Fr(t2n, d)
                A = 27 * t1**2
                B = t2**3 - 18 * t1 * t2
                C = 16 * t1 - t2**2
                if A == 0:
                    if B != 0:
                        pts.append((t1, t2, -C / B))
                    elif C == 0:
                        # E degenerates further; sample a few t3
                        for t3n in range(-6, 7):
                            pts.append((t1, t2, Fr(t3n)))
                    continue
                disc = B * B - 4 * A * C
                if disc < 0:
                    continue
                # perfect square search (bounded)
                # scale: try s/sd with s^2 = disc * sd^2
                # disc is a square in Q iff num(disc) and den(disc) are both squares
                # (Fraction is in lowest terms).
                num, den = disc.numerator, disc.denominator
                if num >= 0:
                    sn, sdn = isqrt(num), isqrt(den)
                    if sn * sn == num and sdn * sdn == den:
                        s = Fr(sn, sdn)
                        pts.append((t1, t2, (-B + s) / (2 * A)))
                        pts.append((t1, t2, (-B - s) / (2 * A)))

    # t2=0 slice denser: E = t1(27 t1 t3^2 + 16)=0
    for t1n in range(-30, 31):
        for d in dens:
            t1 = Fr(t1n, d)
            if t1 == 0:
                for t2n in range(-12, 13):
                    if t2n == 0:
                        for t3n in range(-8, 9):
                            pts.append((Fr(0), Fr(0), Fr(t3n)))
                    else:
                        t2 = Fr(t2n)
                        # E(0,t2,t3)= t2^3 t3 - t2^2 = t2^2 (t2 t3 - 1)
                        pts.append((Fr(0), t2, Fr(1) / t2))
                continue
            rhs = Fr(-16) / (27 * t1)
            if rhs < 0:
                continue
            num, den = rhs.numerator, rhs.denominator
            if num < 0:
                continue
            sn, sdn = isqrt(num), isqrt(den)
            if sn * sn == num and sdn * sdn == den:
                s = Fr(sn, sdn)
                pts.append((t1, Fr(0), s))
                pts.append((t1, Fr(0), -s))

    # known anchors + a few more literature-ish points
    pts.extend(
        [
            (Fr(-1, 4), Fr(0), Fr(0)),
            (Fr(-16, 27), Fr(0), Fr(1)),
            (Fr(-4, 27), Fr(0), Fr(2)),
            (Fr(-1), Fr(2), Fr(-2)),
            (Fr(1), Fr(4), Fr(0)),
            (Fr(2), Fr(5), Fr(1, 4)),
            (Fr(2), Fr(5), Fr(7, 27)),
            (Fr(0), Fr(1), Fr(1)),
            (Fr(0), Fr(0), Fr(5)),
            (Fr(0), Fr(2), Fr(3)),
            (Fr(3), Fr(6), Fr(2, 9)),
            (Fr(1, 3), Fr(2), Fr(2, 3)),
            (Fr(4, 3), Fr(4), Fr(1, 3)),
            (Fr(12), Fr(12), Fr(1, 9)),
            (Fr(48), Fr(24), Fr(1, 18)),
        ]
    )

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


def pattern_key(detail):
    return "+".join(str(c) for _, c in detail)


def main():
    pts = large_points_on_E()
    print(f"rational points on V(E): {len(pts)}", flush=True)

    hist_fiber = Counter()
    hist_shape = Counter()
    fiber_by_shape = Counter()
    two_y_patterns = Counter()  # lift patterns for double+simple
    two_y_which_lifts = Counter()  # "simple_only" | "double_only" | "both" | "neither"
    triple_fiber = Counter()
    size2 = []
    incomplete = []
    leftover_quad = []  # rat_y=1 + leftover 2 (or leftover>0)
    mult_root_not_rational = 0
    forced_x_mismatch = []  # fiber points disagreeing with Phi_x force
    double_lifts_hits = []  # double root with fiber_count > 0
    simple_fails_hits = []  # simple root with fiber_count == 0 off cusp
    both_lift_hits = []
    off_cusp = 0
    on_cusp_n = 0

    # algebraic sanity: disc identity on sample (disc_Y(G1) vanishes on E=0)
    # disc of cubic 2y^3 + ... can be checked via resultant G1,G1' ~ 0
    disc_nonzero = 0

    for i, t in enumerate(pts):
        t1, t2, t3 = t
        info = y_factor_full(t1, t2, t3)
        ys = info["ys"]
        total, detail = lift_detail(t1, t2, t3, ys)
        # note: irrational leftover y not counted — flagged incomplete
        if info["leftover_deg"] > 0:
            incomplete.append(
                {
                    "t": [str(c) for c in t],
                    "shape": info["shape"],
                    "leftover_deg": info["leftover_deg"],
                    "partial_fiber": total,
                    "detail": [(str(y), c) for y, c in detail],
                }
            )
            leftover_quad.append(
                {
                    "t": [str(c) for c in t],
                    "shape": info["shape"],
                    "leftover_deg": info["leftover_deg"],
                    "rat_ys": [str(y) for y in ys],
                    "partial_fiber_from_rat_y": total,
                    "detail": [(str(y), c) for y, c in detail],
                }
            )

        hist_fiber[total] += 1
        hist_shape[info["shape"]] += 1
        fiber_by_shape[f"{info['shape']}|fiber={total}"] += 1

        # gcd multiple root should be rational on V(E)
        if info["multiple_root"] is None or info["multiple_root"] == "deg>=2":
            mult_root_not_rational += 1

        # resultant-style: G1 and G1' share a root ⇒ gcd deg >= 1
        g = F.poly_gcd(F.G1_coeffs(t1, t2, t3), F.poly_diff(F.G1_coeffs(t1, t2, t3)))
        if F.poly_deg(g) < 1:
            disc_nonzero += 1

        cusp = on_cusp(t1, t2, t3)
        if cusp:
            on_cusp_n += 1
        else:
            off_cusp += 1

        xstar = forced_x(t1, t2, t3)

        # Cross-check lifts via forced x (off cusp):
        # fiber_count_at_y >= 1  iff  forced-x linear system is consistent.
        # Also flag c >= 2 (would mean two x's despite Phi_x force).
        if xstar is not None and info["leftover_deg"] == 0:
            for y0, c in detail:
                lifts_fx, z_or_tag = check_forced_x_consistency(t1, t2, t3, y0, xstar)
                if (c >= 1) != lifts_fx or c >= 2:
                    forced_x_mismatch.append(
                        {
                            "t": [str(v) for v in t],
                            "y": str(y0),
                            "fiber_count_at_y": c,
                            "forced_x_lifts": lifts_fx,
                            "xstar": str(xstar),
                            "z_or_tag": str(z_or_tag),
                        }
                    )

        # two distinct rational y (double+simple)
        if info["shape"] == "double+simple":
            pat = pattern_key(detail)
            two_y_patterns[pat] += 1
            mr = info["multiple_root"]
            sr = info["simple_root"]
            c_double = next((c for y, c in detail if y == mr), None)
            c_simple = next((c for y, c in detail if y == sr), None)
            if c_double is not None and c_simple is not None:
                if c_double == 0 and c_simple == 1:
                    two_y_which_lifts["simple_only"] += 1
                elif c_double == 1 and c_simple == 0:
                    two_y_which_lifts["double_only"] += 1
                elif c_double >= 1 and c_simple >= 1:
                    two_y_which_lifts["both"] += 1
                    both_lift_hits.append(
                        {
                            "t": [str(v) for v in t],
                            "detail": [(str(y), c) for y, c in detail],
                            "multiple": str(mr),
                            "simple": str(sr),
                        }
                    )
                elif c_double == 0 and c_simple == 0:
                    two_y_which_lifts["neither"] += 1
                else:
                    two_y_which_lifts[f"other:{c_double}+{c_simple}"] += 1

                if c_double and c_double > 0:
                    double_lifts_hits.append(
                        {
                            "t": [str(v) for v in t],
                            "double": str(mr),
                            "c_double": c_double,
                            "c_simple": c_simple,
                        }
                    )
                if not cusp and c_simple == 0:
                    simple_fails_hits.append(
                        {
                            "t": [str(v) for v in t],
                            "simple": str(sr),
                            "c_double": c_double,
                            "c_simple": c_simple,
                        }
                    )

        if info["shape"] == "triple":
            triple_fiber[total] += 1

        if total == 2:
            size2.append(
                {
                    "t": [str(c) for c in t],
                    "shape": info["shape"],
                    "ys": [str(y) for y in ys],
                    "mult": {str(k): v for k, v in info["mult"].items()},
                    "detail": [(str(y), c) for y, c in detail],
                    "leftover_deg": info["leftover_deg"],
                    "cusp": cusp,
                }
            )
            print("SIZE2", t, info["shape"], detail, flush=True)

        if (i + 1) % 200 == 0:
            print(f"... {i+1}/{len(pts)} hist={dict(hist_fiber)}", flush=True)

    # Soft lemma statement status
    two_y_total = sum(two_y_patterns.values())
    soft_lemma_ok = (
        two_y_total > 0
        and two_y_which_lifts.get("both", 0) == 0
        and two_y_which_lifts.get("other:1+1", 0) == 0
        and not both_lift_hits
        and not any(p in two_y_patterns for p in ("1+1", "2+0", "0+2", "1+2", "2+1"))
    )

    status = "FOUND_SIZE_2" if size2 else "NO_SIZE_2_IN_PUSH_SAMPLE"

    out = {
        "schema": "jc.fiber_size2_push.v1",
        "points_tested": len(pts),
        "histogram_fiber": {str(k): v for k, v in sorted(hist_fiber.items())},
        "histogram_y_shape": dict(sorted(hist_shape.items())),
        "fiber_by_shape": dict(sorted(fiber_by_shape.items())),
        "size2_hits": size2,
        "incomplete_y_factorizations": len(incomplete),
        "incomplete_samples": incomplete[:20],  # cap
        "leftover_quad_or_irr_count": len(leftover_quad),
        "leftover_quad_samples": leftover_quad[:20],
        "mult_root_not_rational_count": mult_root_not_rational,
        "disc_nonzero_on_VE_count": disc_nonzero,
        "on_cusp_count": on_cusp_n,
        "off_cusp_count": off_cusp,
        "two_y_count": two_y_total,
        "two_y_lift_patterns": dict(sorted(two_y_patterns.items())),
        "two_y_which_lifts": dict(sorted(two_y_which_lifts.items())),
        "double_lifts_hits": double_lifts_hits[:20],
        "simple_fails_off_cusp": simple_fails_hits[:20],
        "both_lift_hits": both_lift_hits,
        "triple_fiber_hist": {str(k): v for k, v in sorted(triple_fiber.items())},
        "forced_x_mismatch_count": len(forced_x_mismatch),
        "forced_x_mismatch_samples": forced_x_mismatch[:20],
        "soft_lemma_two_y_at_most_one_lifts": {
            "status": "HOLDS_ON_SAMPLE" if soft_lemma_ok else "FAILS_ON_SAMPLE",
            "statement": (
                "For rational t in V(E) at which G1 has exactly two distinct "
                "rational roots (double+simple), at most one of those roots "
                "lifts to a preimage under F. Observed: always simple_only "
                "(double never lifts; simple lifts once) off the empty-fiber "
                "cases."
            ),
            "sample_support": two_y_total,
            "note": (
                "Observational soft lemma on a rational sample, reinforced by "
                "reduced Phi_x (unique forced x on V(E)\\\\gamma). NOT a "
                "familywise certificate over C."
            ),
        },
        "shape_lemma_rational_VE": {
            "statement": (
                "On rational points of V(E), disc_Y(G1)=0 so G1 has a multiple "
                "root; gcd(G1,G1') over Q is linear, so the multiple root is "
                "rational; Vieta then forces the simple root rational too. "
                "Hence shape 'rat_y=1,leftover=2' cannot occur for rational t "
                "in V(E). Size-2 via 'one rational y + two complex y-lifts' is "
                "blocked on rational base points."
            ),
            "leftover_positive_count": len(leftover_quad),
            "status": (
                "CONFIRMED_EMPTY_ON_SAMPLE"
                if len(leftover_quad) == 0 and disc_nonzero == 0
                else "NEEDS_REVIEW"
            ),
        },
        "status": status,
        "claim_boundary": (
            "Expanded rational sample + shape/multiplicity classification + "
            "Phi_x forced-x cross-check. Soft lemma is sample-level, not "
            "familywise. Does not close jc-fiber-count-spectrum-size. "
            "Irrational base points on V(E) remain open for size-2."
        ),
    }

    path = HERE / "FIBER_SIZE2_PUSH.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"\nWrote {path}", flush=True)
    return 0 if not size2 else 0  # always 0; size-2 is a discovery, not failure


if __name__ == "__main__":
    raise SystemExit(main())

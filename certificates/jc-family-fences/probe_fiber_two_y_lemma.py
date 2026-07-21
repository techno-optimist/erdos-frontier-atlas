#!/usr/bin/env python3
"""
Soft-lemma formalization: two distinct rational y-roots of G1 ⇒ at most one lifts.

Algebraic setup (conditional on Alpöge's map / anatomy annihilators):
  On V(E), disc_Y(G1)=0, so G1 = 2(y-a)^2 (y-b) over C.
  For rational t, gcd(G1,G1') ∈ Q[y] is linear ⇒ a ∈ Q; Vieta ⇒ b ∈ Q.
  On V(E)\\γ, Phi_x reduces to (4-3 t2 t3) X - 2 t3, forcing unique
      x* = 2 t3 / (4 - 3 t2 t3).
  Hence #fiber = # of distinct y-roots that admit a z with F(x*,y,z)=t.

Parametric family of rational points with prescribed double/simple roots:
  free rationals (a, s) with a ≠ s/2 (off cusp):
      t2 = s
      t1 = a (s - a) / 3
      b  = 3 s / 2 - 2 a          # simple root
      t3 = (-2 a^2 b + 18 t1 s - s^3) / (27 t1^2)   when t1 ≠ 0
  (t1=0 handled as a separate thin slice).

Machine checks on each sample point:
  (E0)  E(t)=0
  (G1)  G1(t;y) = 2 (y-a)^2 (y-b) as polynomials in y
  (FX)  forced-x consistency: simple lifts once, double never
  (RC)  resultant-gcd fiber_count_at_y agrees with forced-x (via engine)

Soft lemma status: HOLDS_ON_PARAMETRIC_SAMPLE if no counterexample.
NOT a familywise C-certificate. Does not close spectrum bracket.
"""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

import sys as _sys
import pathlib as _pathlib

_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

import probe_fiber_size2_exact as F

HERE = Path(__file__).resolve().parent


def delta(t2, t3):
    return Fr(4) - 3 * t2 * t3


def forced_x(t2, t3):
    d = delta(t2, t3)
    if d == 0:
        return None
    return (2 * t3) / d


def lifts_at_forced_x(t1, t2, t3, y0, xstar):
    x, y = xstar, y0
    u = 1 + y * x
    a1 = u**3
    b1 = (y**2) * u * (4 + 3 * y * x) - t1
    a2 = 3 * x * (u**2)
    b2 = y + 3 * x * (y**2) * (4 + 3 * y * x) - t2
    a3 = -(x**3)
    b3 = 2 * x - 3 * (x**2) * y - t3
    if a1 == 0 and a2 == 0 and a3 == 0:
        return b1 == 0 and b2 == 0 and b3 == 0
    z = None
    for aa, bb in ((a1, b1), (a2, b2), (a3, b3)):
        if aa != 0:
            z = -bb / aa
            break
    for aa, bb in ((a1, b1), (a2, b2), (a3, b3)):
        if aa * z + bb != 0:
            return False
    return True


def g1_from_ab(a, b):
    """2(y-a)^2(y-b) as coeff list low→high."""
    # (y-a)^2 = y^2 - 2a y + a^2
    # times (y-b) = y^3 - (2a+b)y^2 + (a^2+2ab)y - a^2 b
    # times 2
    return [
        -2 * a * a * b,
        2 * (a * a + 2 * a * b),
        -2 * (2 * a + b),
        Fr(2),
    ]


def t3_from_ab(a, s, t1, b):
    """Solve G1 constant term for t3 (requires t1 ≠ 0)."""
    # 27 t1^2 t3 - 18 t1 s + s^3 = -2 a^2 b
    rhs = -2 * a * a * b + 18 * t1 * s - s**3
    return rhs / (27 * t1 * t1)


def point_from_double_simple(a, s):
    """
    Build rational t from double root a and t2=s.
    Returns None if degenerate (t1=0 handled separately, or division by 0).
    """
    a, s = Fr(a), Fr(s)
    if a * 2 == s:
        return None  # triple / cusp candidate
    t1 = a * (s - a) / 3
    b = 3 * s / 2 - 2 * a
    if a == b:
        return None
    if t1 == 0:
        # t1=0, a(s-a)=0 ⇒ a=0 or a=s
        # G1 = 2y^3 - 3 s y^2 + s^3 = 2(y - s/2)^2 (y + something)?
        # With t1=0: multiple root from y^2 - s y = y(y-s)=0 so a∈{0,s}
        # If a=0: b=3s/2, c = s^3, and E(0,s,t3)= s^2(s t3 - 1)=0 ⇒ t3=1/s (s≠0)
        # Check G1(0,s,1/s): 2y^3 - 3s y^2 + s^3. At y=0: s^3 ≠ 0 unless s=0.
        # Actually constant = t2^3 = s^3, and -2 a^2 b = 0, mismatch unless s=0.
        # So a=0,t1=0 is NOT double root of G1 when t3=1/s.
        # If a=s: b=3s/2-2s=-s/2, t1=0
        # constant -2 s^2 (-s/2)= s^3. G1 const with t1=0 is s^3. OK any t3?
        # E(0,s,t3)=s^2(s t3-1)=0 ⇒ t3=1/s
        # G1 = 2y^3 - 3s y^2 + s^3. Factor: try (y-s)^2 (y+s/2)*2?
        # 2(y-s)^2(y+s/2)=2(y^2-2sy+s^2)(y+s/2)=2[y^3+s/2 y^2 -2s y^2 - s^2 y + s^2 y + s^3/2]
        # =2[y^3 - (3s/2)y^2 + 0*y + s^3/2] = 2y^3 - 3s y^2 + s^3. Yes!
        if s == 0:
            return None
        if a != s:
            return None
        t3 = Fr(1) / s
        b = -s / 2
        return (Fr(0), s, t3), a, b
    t3 = t3_from_ab(a, s, t1, b)
    return (t1, s, t3), a, b


def verify_g1_factor(t, a, b):
    got = F.G1_coeffs(*t)
    want = g1_from_ab(a, b)
    # compare as polys (same degree)
    if F.poly_deg(got) != F.poly_deg(want):
        return False
    n = max(len(got), len(want))
    got = got + [Fr(0)] * (n - len(got))
    want = want + [Fr(0)] * (n - len(want))
    return got == want


def rational_grid():
    """Modest dense rational grid for (a,s)."""
    vals = []
    for n in range(-12, 13):
        for d in (1, 2, 3, 4, 5, 6):
            vals.append(Fr(n, d))
    # unique
    out = []
    seen = set()
    for v in vals:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def main():
    grid = rational_grid()
    print(f"grid size |a|×|s| candidates: {len(grid)}^2 = {len(grid)**2}", flush=True)

    hist = Counter()
    which = Counter()
    failures = []
    size2 = []
    points = 0
    e_fail = 0
    g1_fail = 0
    engine_mismatch = 0
    cusp_n = 0
    t1_zero_n = 0
    seen_t = set()

    for a in grid:
        for s in grid:
            built = point_from_double_simple(a, s)
            if built is None:
                continue
            t, aa, bb = built
            if t in seen_t:
                continue
            seen_t.add(t)
            t1, t2, t3 = t

            if F.E(*t) != 0:
                e_fail += 1
                failures.append({"kind": "E_nonzero", "t": [str(c) for c in t], "a": str(aa), "b": str(bb)})
                continue
            if not verify_g1_factor(t, aa, bb):
                g1_fail += 1
                failures.append({"kind": "G1_factor", "t": [str(c) for c in t], "a": str(aa), "b": str(bb)})
                continue

            points += 1
            dlt = delta(t2, t3)
            if dlt == 0:
                cusp_n += 1
                # cusp: expect fiber 0
                c_a = F.fiber_count_at_y(t1, t2, t3, aa)
                c_b = F.fiber_count_at_y(t1, t2, t3, bb)
                total = c_a + c_b
                hist[total] += 1
                which["cusp"] += 1
                if total == 2:
                    size2.append({"t": [str(c) for c in t], "a": str(aa), "b": str(bb), "ca": c_a, "cb": c_b, "cusp": True})
                continue

            xstar = forced_x(t2, t3)
            assert xstar is not None
            la = lifts_at_forced_x(t1, t2, t3, aa, xstar)
            lb = lifts_at_forced_x(t1, t2, t3, bb, xstar)
            c_a = F.fiber_count_at_y(t1, t2, t3, aa)
            c_b = F.fiber_count_at_y(t1, t2, t3, bb)

            # agreement forced-x vs engine
            if (c_a >= 1) != la or (c_b >= 1) != lb or c_a >= 2 or c_b >= 2:
                engine_mismatch += 1
                failures.append(
                    {
                        "kind": "engine_fx_mismatch",
                        "t": [str(c) for c in t],
                        "a": str(aa),
                        "b": str(bb),
                        "la": la,
                        "lb": lb,
                        "ca": c_a,
                        "cb": c_b,
                    }
                )

            total = c_a + c_b
            hist[total] += 1
            if t1 == 0:
                t1_zero_n += 1

            if la and lb:
                which["both"] += 1
                size2.append({"t": [str(c) for c in t], "a": str(aa), "b": str(bb), "ca": c_a, "cb": c_b})
                print("BOTH_LIFT", t, aa, bb, flush=True)
            elif (not la) and lb:
                which["simple_only"] += 1
            elif la and (not lb):
                which["double_only"] += 1
                failures.append(
                    {
                        "kind": "double_only",
                        "t": [str(c) for c in t],
                        "a": str(aa),
                        "b": str(bb),
                        "ca": c_a,
                        "cb": c_b,
                    }
                )
            else:
                which["neither"] += 1

            if total == 2:
                size2.append({"t": [str(c) for c in t], "a": str(aa), "b": str(bb), "ca": c_a, "cb": c_b})
                print("SIZE2", t, c_a, c_b, flush=True)

            if points % 200 == 0:
                print(f"... points={points} which={dict(which)} hist={dict(hist)}", flush=True)

    soft_ok = (
        which.get("both", 0) == 0
        and which.get("double_only", 0) == 0
        and not size2
        and e_fail == 0
        and g1_fail == 0
        and engine_mismatch == 0
    )

    # Stronger observation on this parametric family: simple_only dominates off-cusp
    out = {
        "schema": "jc.fiber_two_y_lemma.v1",
        "points_tested": points,
        "histogram_fiber": {str(k): v for k, v in sorted(hist.items())},
        "which_lifts": dict(sorted(which.items())),
        "cusp_count": cusp_n,
        "t1_zero_count": t1_zero_n,
        "e_fail": e_fail,
        "g1_fail": g1_fail,
        "engine_fx_mismatch": engine_mismatch,
        "size2_hits": size2,
        "failure_samples": failures[:30],
        "soft_lemma": {
            "statement": (
                "If t ∈ V(E) is rational and G1(t;y)=2(y-a)^2(y-b) with a≠b "
                "rational, then at most one of {a,b} lifts under F. On this "
                "parametric sample the lifting root is always the simple root b "
                "(double a never lifts) off the cusp, where both fail (fiber 0)."
            ),
            "status": "HOLDS_ON_PARAMETRIC_SAMPLE" if soft_ok else "FAILS_ON_SAMPLE",
            "sample_support": points,
        },
        "algebraic_notes": {
            "parametrization": "t1=a(s-a)/3, t2=s, b=3s/2-2a, t3 from G1 constant",
            "phi_x_reduced": "on V(E)\\\\γ: x*=2 t3/(4-3 t2 t3) (from anatomy Phi_x)",
            "shape_on_rational_VE": (
                "disc=0 + gcd(G1,G1') linear over Q ⇒ multiple root rational; "
                "Vieta ⇒ simple root rational. Shape rat_y=1+leftover=2 empty."
            ),
        },
        "status": "FOUND_SIZE_2" if size2 else "NO_SIZE_2_IN_PARAMETRIC_SAMPLE",
        "claim_boundary": (
            "Parametric rational sample of double+simple stratum + forced-x "
            "cross-check + engine agreement. Soft lemma holds on sample; NOT "
            "familywise over C. Does not close jc-fiber-count-spectrum-size. "
            "Size-2 could still hide at non-rational t or non-parametrized strata."
        ),
    }
    path = HERE / "FIBER_TWO_Y_LEMMA.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"\nWrote {path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

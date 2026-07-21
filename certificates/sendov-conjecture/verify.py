#!/usr/bin/env python3
"""Replayable certificate: Sendov wall ledger baselines (2026-07-21).

NOT a counterexample certificate. Certifies:

  (1) Unity extremals: beta=1, all critical points at 0 =>
        p(z) = int_1^z w^{n-1} dw = (z^n - 1)/n
      has roots on the unit circle, radius r = min|beta - crit| = 1,
      and is therefore an equality-case near-extremal for Sendov
      (d(p) = 1), not a counterexample.

  (2) Miller 2005 local-extrema seeds (reconstructed from published P')
      for listed n have r < 1 and all roots in the closed unit disk.

  (3) Dual-ray wall (sampled, deterministic seeds): scaling crit = t*u
      from 0 until radius >= R>1 forces max|root| > 1 on every
      direction in a fixed seed list (no ray CE).

  (4) Negative controls: the checker rejects malformed claims.

Requires: numpy (and stdlib). Optional mpmath not required for replay.

Run:  python3 verify.py        (exit 0 = ledger baselines hold)
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def build_poly_from_crit(beta: complex, crit: np.ndarray) -> np.ndarray:
    crit = np.asarray(crit, dtype=np.complex128)
    beta = complex(beta)
    pprime = np.poly(crit).astype(np.complex128)
    p = np.polyint(pprime).astype(np.complex128)
    p = p.copy()
    p[-1] -= np.polyval(p, beta)
    if abs(p[0]) > 0:
        p = p / p[0]
    return p


def radius(beta: complex, crit: np.ndarray) -> float:
    return float(np.min(np.abs(np.asarray(crit, dtype=np.complex128) - beta)))


def max_root_mod(beta: complex, crit: np.ndarray) -> float:
    p = build_poly_from_crit(beta, crit)
    rts = np.roots(p)
    return float(np.max(np.abs(rts))) if len(rts) else 0.0


def evaluate(beta: float, crit: np.ndarray) -> dict:
    r = radius(beta, crit)
    mm = max_root_mod(beta, crit)
    return {
        "radius": r,
        "max_root_mod": mm,
        "feasible": mm <= 1.0 + 1e-8,
        "counterexample": (r > 1.0 + 1e-10) and (mm <= 1.0 + 1e-8),
    }


def unity(n: int):
    return 1.0, np.zeros(n - 1, dtype=np.complex128)


def miller_seed(n: int):
    """Miller arXiv math/0505424 explicit local extrema (P' given)."""
    specs = {
        8: (0.7290857513, -0.2035409790, -0.5410836525, 0.7327229666),
        9: (0.7145672829, -0.2157115753, -0.8021671918, 0.9280147829),
        12: (0.8403619619, -0.1155828545, -0.4090272613, 0.5513532168),
        13: (0.8275325585, -0.1246203379, -0.5415308686, 0.6699194279),
        14: (0.8158105092, -0.1304708647, -0.6885970233, 0.7916663399),
        15: (0.7999767588, -0.1400336168, -0.8389864647, 0.9148263642),
        19: (0.8684432238, -0.0923361850, -0.6503807257, 0.7337221736),
        20: (0.8570396874, -0.0982636528, -0.7563752823, 0.8263310816),
        26: (0.8817716692, -0.0797127446, -0.7969496845, 0.8496586550),
    }
    if n not in specs:
        return None
    beta, a, b, c = specs[n]
    disc = b * b - 4 * c
    z1 = (-b + np.sqrt(disc + 0j)) / 2
    z2 = (-b - np.sqrt(disc + 0j)) / 2
    crit = np.concatenate([np.full(n - 3, a, dtype=np.complex128), [z1, z2]])
    return beta, crit


def dual_ray_check(n: int, R: float = 1.01, n_dirs: int = 40, seed: int = 0) -> dict:
    """Scale crit = t*u until radius >= R; report min maxroot over directions."""
    rng = np.random.default_rng(seed)
    m = n - 1
    beta = 1.0
    dirs = [-np.ones(m, dtype=np.complex128)]
    for _ in range(n_dirs):
        dirs.append(rng.normal(size=m) + 1j * rng.normal(size=m))
    for j in range(min(m, 4)):
        for ph in (1.0, -1.0, 1j, -1j):
            u = np.zeros(m, dtype=np.complex128)
            u[j] = ph
            dirs.append(u)

    maxroots = []
    for u in dirs:
        nrm = np.linalg.norm(u)
        if nrm < 1e-15:
            continue
        u = u / nrm

        def r_at(t):
            return radius(beta, t * u)

        t_max = 5.0
        if r_at(t_max) < R:
            t_max = 20.0
            if r_at(t_max) < R:
                continue
        lo, hi = 0.0, t_max
        for _ in range(36):
            mid = 0.5 * (lo + hi)
            if r_at(mid) >= R:
                hi = mid
            else:
                lo = mid
        crit = hi * u
        if radius(beta, crit) + 1e-9 >= R:
            maxroots.append(max_root_mod(beta, crit))

    if not maxroots:
        return {"ok": False, "reason": "no hits"}
    mn = float(min(maxroots))
    return {
        "ok": True,
        "n_hits": len(maxroots),
        "min_maxroot": mn,
        "slack": mn - 1.0,
        "no_ce": mn > 1.0 + 1e-9,
    }


def load_json(name: str):
    path = os.path.join(HERE, "results", name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    ok = True

    # Leg 1 — unity extremals
    for n in (2, 3, 4, 8, 9, 12, 20, 30):
        beta, crit = unity(n)
        ev = evaluate(beta, crit)
        leg = (
            abs(ev["radius"] - 1.0) < 1e-12
            and ev["feasible"]
            and not ev["counterexample"]
            and abs(ev["max_root_mod"] - 1.0) < 1e-8
        )
        print(
            f"leg1 unity n={n:3d}: r={ev['radius']:.12f} maxroot={ev['max_root_mod']:.8f} "
            f"{'PASS' if leg else 'FAIL'}"
        )
        ok &= leg

    # Leg 2 — Miller local extrema (r < 1, feasible)
    for n in (8, 9, 12, 13, 14, 15, 19, 20, 26):
        ms = miller_seed(n)
        assert ms is not None
        beta, crit = ms
        ev = evaluate(beta, crit)
        leg = (
            ev["feasible"]
            and ev["radius"] < 0.99
            and ev["radius"] > 0.7
            and not ev["counterexample"]
        )
        print(
            f"leg2 miller n={n:3d}: r={ev['radius']:.10f} maxroot={ev['max_root_mod']:.8f} "
            f"{'PASS' if leg else 'FAIL'}"
        )
        ok &= leg

    # Leg 3 — dual-ray wall (sampled, fixed seeds)
    for n in (9, 12, 20):
        for R in (1.01, 1.05, 1.1):
            dr = dual_ray_check(n, R=R, n_dirs=30, seed=n * 17 + int(R * 100))
            leg = dr.get("ok") and dr.get("no_ce") and dr["slack"] > 0
            print(
                f"leg3 dual-ray n={n:3d} R={R:.2f}: hits={dr.get('n_hits')} "
                f"min_maxroot={dr.get('min_maxroot', float('nan')):.8f} "
                f"slack={dr.get('slack', float('nan')):+.6f} {'PASS' if leg else 'FAIL'}"
            )
            ok &= leg

    # Leg 4 — committed dual_ray.json is CE-free and has positive slack
    dual = load_json("dual_ray.json")
    if dual is not None:
        ces = [r for r in dual if r.get("counterexample")]
        bad_slack = [r for r in dual if r.get("slack", 0) <= 0]
        leg = len(ces) == 0 and len(bad_slack) == 0 and len(dual) >= 20
        print(
            f"leg4 dual_ray.json: rows={len(dual)} ces={len(ces)} "
            f"nonpos_slack={len(bad_slack)} {'PASS' if leg else 'FAIL'}"
        )
        ok &= leg
    else:
        print("leg4 dual_ray.json: MISSING FAIL")
        ok = False

    # Leg 5 — squeeze_fast.json: delta=0 => r=1; no CE flags
    sq = load_json("squeeze_fast.json")
    if sq is not None:
        ces = [r for r in sq if r.get("counterexample")]
        d0 = [r for r in sq if abs(r.get("delta", -1)) < 1e-15]
        d0_ok = all(abs(r.get("radius", 0) - 1.0) < 1e-9 for r in d0) and len(d0) >= 3
        leg = len(ces) == 0 and d0_ok
        print(
            f"leg5 squeeze_fast.json: rows={len(sq)} ces={len(ces)} "
            f"delta0_all_r1={d0_ok} {'PASS' if leg else 'FAIL'}"
        )
        ok &= leg
    else:
        print("leg5 squeeze_fast.json: MISSING FAIL")
        ok = False

    # Leg 6 — jet summary CE-free
    jet = load_json("extremal_jet_summary.json")
    if jet is not None:
        leg = len(jet.get("ces", [])) == 0 and jet.get("n_samples", 0) > 1000
        print(
            f"leg6 extremal_jet_summary.json: samples={jet.get('n_samples')} "
            f"ces={len(jet.get('ces', []))} {'PASS' if leg else 'FAIL'}"
        )
        ok &= leg
    else:
        print("leg6 extremal_jet_summary.json: MISSING FAIL")
        ok = False

    # Leg 7 — negative control: crit far left of beta=1 can force r>1 but maxroot>1
    beta = 1.0
    crit = np.full(8, -0.2 + 0j)  # |1-(-0.2)|=1.2 > 1
    ev = evaluate(beta, crit)
    leg = (ev["radius"] > 1.0) and (not ev["counterexample"])
    print(
        f"leg7 negctl r={ev['radius']:.4f} maxroot={ev['max_root_mod']:.4f} "
        f"CE={ev['counterexample']} {'PASS' if leg else 'FAIL'}"
    )
    ok &= leg

    # Leg 8 — lune_force.json: CE-free; every feasible row has radius <= 1
    lf = load_json("lune_force.json")
    if lf is not None:
        ces = [r for r in lf if r.get("counterexample") or r.get("counterexample_mp")]
        feas = [r for r in lf if r.get("feasible")]
        feas_ok = all(float(r.get("radius", 99)) <= 1.0 + 1e-6 for r in feas)
        leg = len(ces) == 0 and feas_ok and len(lf) >= 20
        print(
            f"leg8 lune_force.json: rows={len(lf)} feas={len(feas)} ces={len(ces)} "
            f"feas_r_le_1={feas_ok} {'PASS' if leg else 'FAIL'}"
        )
        ok &= leg
    else:
        print("leg8 lune_force.json: MISSING FAIL")
        ok = False

    # Leg 9 — dual_soft_n12_20.json CE-free with positive slack when r>1
    ds = load_json("dual_soft_n12_20.json")
    if ds is not None:
        ces = [r for r in ds if r.get("counterexample")]
        bad = [
            r
            for r in ds
            if float(r.get("radius", 0)) > 1 + 1e-8
            and float(r.get("max_root_mod", 0)) <= 1 + 1e-8
        ]
        pos = [r for r in ds if float(r.get("slack", -1)) > 0]
        leg = len(ces) == 0 and len(bad) == 0 and len(pos) >= 6
        print(
            f"leg9 dual_soft_n12_20.json: rows={len(ds)} ces={len(ces)} "
            f"bad={len(bad)} pos_slack={len(pos)} {'PASS' if leg else 'FAIL'}"
        )
        ok &= leg
    else:
        print("leg9 dual_soft_n12_20.json: MISSING FAIL")
        ok = False

    # Leg 10 — wave3 free-beta penalty + dual: CE-free; penalty hits r=1
    w3 = load_json("wave3_all.json")
    if w3 is not None:
        ces = [r for r in w3 if r.get("counterexample")]
        pen = [r for r in w3 if r.get("lane") == "penalty"]
        pen_ok = all(abs(float(r.get("radius", 0)) - 1.0) < 1e-9 for r in pen) and len(pen) >= 20
        dual = [r for r in w3 if r.get("lane") == "dual"]
        dual_bad = [
            r
            for r in dual
            if float(r.get("radius", 0)) > 1 + 1e-8
            and float(r.get("max_root_mod", 99)) <= 1 + 1e-8
        ]
        leg = len(ces) == 0 and pen_ok and len(dual_bad) == 0 and len(dual) >= 20
        status = "PASS" if leg else "FAIL"
        print(
            f"leg10 wave3_all.json: rows={len(w3)} pen={len(pen)} dual={len(dual)} "
            f"ces={len(ces)} dual_bad={len(dual_bad)} pen_all_r1={pen_ok} {status}"
        )
        ok &= leg
    else:
        print("leg10 wave3_all.json: MISSING FAIL")
        ok = False

    print()
    print("ALL PASS" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

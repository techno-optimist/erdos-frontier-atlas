#!/usr/bin/env python3
"""
Mine n=7 common-anchor split-weight Fibonacci macros.

Primary attack (suggested order):
  - Port-capacity samples S=5,6 under L-reachability (ge 8 ports) — sample only
  - Pad/mutate sealed N6_L4_S5 clock; exhaust dig/port on high-port clocks
  - Cells: L=4 S=5, L=5 S=5, L=4 S=6, also L=3 S=5/S=6 smoke

Requires: highspy (LP/MIP). Stdlib + highspy.
Writes: N7_L*_S*_SEARCH.json, optional N7_L*_S*_WITNESS.json, PORT_CAPACITY_*_N7_*.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# `python3 -I` (isolated mode) implies -P, dropping this script's own directory from sys.path,
# so the sibling import below fails. Re-add it: keeps -I hermeticity (no user site-packages)
# AND makes the documented replay one-liner actually run. House convention -- see
# certificates/README.md; enforced by tests/test_certificate_replay.py.
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

import macro_engine as M

HERE = Path(__file__).resolve().parent
N6_WIT = HERE / "N6_L4_S5_WITNESS.json"
N = 7
TAGS = N + 1


def feat(role_ports, S):
    cnt = [Counter(), Counter(), Counter()]
    for role in range(3):
        for p in role_ports[role]:
            cnt[role][p] += 1
    keys = [(s, d) for s in range(S) for d in range(3)]
    out = []
    for k in keys:
        out.append(cnt[0][k] - cnt[1][k])
    for k in keys:
        out.append(cnt[2][k] - cnt[1][k])
    return tuple(out)


def enum_routes(delta, ports, origin, tc, L, S):
    u, v, w = origin
    target = (ports[u][0], ports[v][0], ports[w][0])
    uniq = {}

    def rec(step, carry, states, rp, path):
        if step == L:
            if carry == tc and states == target:
                f = feat(rp, S)
                if f not in uniq:
                    uniq[f] = tuple(path)
            return
        for a, b, c in itertools.product(range(3), repeat=3):
            cout = M.carry_step(a, b, c, carry)
            if cout is None:
                continue
            nrp = (rp[0] + [(states[0], a)], rp[1] + [(states[1], b)], rp[2] + [(states[2], c)])
            ns = (
                delta[states[0]][a],
                delta[states[1]][b],
                delta[states[2]][c],
            )
            path.append((a, b, c))
            rec(step + 1, cout, ns, nrp, path)
            path.pop()

    rec(0, 0, (0, 0, 0), ([], [], []), [])
    return list(uniq.items())


def highs_lp_ok(col_data, S):
    import highspy

    dim = 2 * S * 3
    nvars = sum(len(it) for _, _, it in col_data)
    if nvars == 0:
        return False
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.addVars(nvars, [0.0] * nvars, [1e9] * nvars)
    off = 0
    for w, _n, items in col_data:
        k = len(items)
        h.addRow(float(w), float(w), k, list(range(off, off + k)), [1.0] * k)
        off += k
    for j in range(dim):
        idx, vals = [], []
        off = 0
        for w, _n, items in col_data:
            for i, (f, _) in enumerate(items):
                if f[j]:
                    idx.append(off + i)
                    vals.append(float(f[j]))
            off += len(items)
        if idx:
            h.addRow(0.0, 0.0, len(idx), idx, vals)
    h.run()
    return int(h.getModelStatus()) == 7


def highs_mip(col_data, S, time_limit=180.0):
    import highspy

    dim = 2 * S * 3
    nvars = sum(len(it) for _, _, it in col_data)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", time_limit)
    h.addVars(nvars, [0.0] * nvars, [1e6] * nvars)
    h.changeColsIntegrality(
        nvars, list(range(nvars)), [highspy.HighsVarType.kInteger] * nvars
    )
    off = 0
    ranges = []
    for w, name, items in col_data:
        idxs = list(range(off, off + len(items)))
        h.addRow(float(w), float(w), len(idxs), idxs, [1.0] * len(idxs))
        ranges.append((w, name, items, idxs))
        off += len(items)
    for j in range(dim):
        idx, vals = [], []
        for w, name, items, idxs in ranges:
            for oi, (f, _) in enumerate(items):
                if f[j]:
                    idx.append(idxs[oi])
                    vals.append(float(f[j]))
        if idx:
            h.addRow(0.0, 0.0, len(idx), idx, vals)
    h.run()
    if int(h.getModelStatus()) != 7:
        return None
    sol = h.getSolution().col_value
    selected = {}
    for w, name, items, idxs in ranges:
        picks = []
        for oi, (f, d3) in enumerate(items):
            m = int(round(sol[idxs[oi]]))
            if m:
                picks.append({"mult": m, "steps": [list(t) for t in d3]})
        selected[name] = picks
    return selected


def try_assignment(delta, digs, carries, ports, cols, L, S, stats):
    if not M.outward_ok(ports, carries, cols):
        return None
    stats["outward"] += 1
    if not M.all_columns_routable(delta, ports, carries, cols, L):
        return None
    stats["routable"] += 1
    print(
        f"  ROUTABLE digs={list(digs)} ports={[list(ports[t]) for t in range(TAGS)]}",
        flush=True,
    )
    # dump first routable seed for later recovery
    seed_path = HERE / f"N7_L{L}_S{S}_FIRST_ROUTABLE.json"
    if not seed_path.exists():
        seed_path.write_text(
            json.dumps(
                {
                    "delta": delta,
                    "digs": list(digs),
                    "carries": list(carries),
                    "ports": {str(t): list(ports[t]) for t in range(TAGS)},
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print("  wrote", seed_path.name, flush=True)

    col_data = []
    for i, (w, origin, name) in enumerate(cols):
        items = enum_routes(delta, ports, origin, carries[i], L, S)
        if not items:
            stats["enum_empty"] += 1
            return None
        col_data.append((w, name, items))
    stats["route_enum"] += 1
    nvars = sum(len(it) for _, _, it in col_data)
    print(f"  enum nvars={nvars} sizes={[len(it) for _,_,it in col_data]}", flush=True)
    try:
        ok = highs_lp_ok(col_data, S)
    except ImportError:
        print("  highspy missing — cannot LP/MIP", flush=True)
        stats["no_highspy"] += 1
        return None
    if not ok:
        stats["lp_infeas"] += 1
        print("  LP_INFEAS", flush=True)
        return None
    stats["lp"] += 1
    print("  LP_HIT — running MIP", flush=True)
    sel = highs_mip(col_data, S)
    if not sel:
        stats["mip_infeas"] += 1
        print("  MIP_INFEAS", flush=True)
        return None
    stats["mip"] += 1
    return {
        "n": N,
        "L": L,
        "S": S,
        "delta": delta,
        "ports": {str(t): list(ports[t]) for t in range(TAGS)},
        "digs": list(digs),
        "carries": list(carries),
        "selected": sel,
    }


def exhaust_clock(delta, legal, cols, L, S, stats, max_assign=500):
    if not M.clock_reachable(delta, S, L):
        return None
    ap = M.anchor_ports(delta, S)
    if len(ap) < TAGS:
        return None
    stats["clocks_ok"] += 1
    by_d = Counter(p[1] for p in ap)
    for digs, carries in legal:
        need = Counter(digs)
        if any(need[d] > by_d[d] for d in need):
            continue
        count = 0
        for ports in M.assign_ports_for_digs(ap, digs, TAGS):
            count += 1
            if count > max_assign:
                break
            hit = try_assignment(delta, digs, carries, ports, cols, L, S, stats)
            if hit:
                return hit
    return None


def random_clock(S, rng, port_bias=0.40):
    flat = [0 if rng.random() < port_bias else rng.randrange(S) for _ in range(S * 3)]
    return [flat[i * 3 : (i + 1) * 3] for i in range(S)]


def mutate(delta, S, rng, n_mut=1, force_ports=None):
    d = [list(r) for r in delta]
    for _ in range(n_mut):
        d[rng.randrange(S)][rng.randrange(3)] = rng.randrange(S)
    if force_ports is not None:
        g = 0
        while len(M.anchor_ports(d, S)) < force_ports and g < 50:
            s, dig = rng.randrange(S), rng.randrange(3)
            if d[s][dig] != 0:
                d[s][dig] = 0
            g += 1
    return d


def pad_from_n6(base5, new_S, rng):
    out = [list(r) for r in base5]
    while len(out) < new_S:
        out.append([0 if rng.random() < 0.4 else rng.randrange(new_S) for _ in range(3)])
    # ensure new states reachable: point one existing non-port transition at new state
    for s_new in range(5, new_S):
        s = rng.randrange(5)
        dig = rng.randrange(3)
        out[s][dig] = s_new
    return out


def n6_port_boost_seeds(base5, rng):
    """Systematic one-entry mutations that add an 8th anchor port on S=5."""
    seeds = []
    S = 5
    base_ap = set(M.anchor_ports(base5, S))
    for s in range(S):
        for dig in range(3):
            if base5[s][dig] == 0:
                continue
            d = [list(r) for r in base5]
            d[s][dig] = 0
            if len(M.anchor_ports(d, S)) >= TAGS and M.clock_reachable(d, S, 4):
                seeds.append(d)
    # also two-entry boosts
    for _ in range(40):
        seeds.append(mutate(base5, S, rng, n_mut=2, force_ports=TAGS))
    # pad S=6 variants
    for _ in range(20):
        seeds.append(pad_from_n6(base5, 6, rng))
    return seeds


def sample_ports(S, L, trials, seed):
    rng = random.Random(seed)
    hist = Counter()
    reachable = ge8 = 0
    mx = 0
    for _ in range(trials):
        delta = random_clock(S, rng)
        if not M.clock_reachable(delta, S, L):
            continue
        reachable += 1
        np = len(M.anchor_ports(delta, S))
        hist[np] += 1
        mx = max(mx, np)
        if np >= 8:
            ge8 += 1
    return {
        "schema": f"lead.port_capacity_s{S}_L{L}_n7.v1",
        "S": S,
        "L": L,
        "trials": trials,
        "reachable": reachable,
        "ge8_ports": ge8,
        "frac_ge8_among_reachable": (ge8 / reachable) if reachable else 0.0,
        "max_ports": mx,
        "hist": {str(k): hist[k] for k in sorted(hist)},
        "claim_boundary": "Random sample only; not exhaustive.",
    }


def hunt_cell(L, S, mut_n, rand_n, max_assign, seed, budget):
    t0 = time.time()
    cols = M.columns(N)
    legal = M.digit_patterns(cols, TAGS)
    print(f"=== n=7 L={L} S={S} dig_patterns={len(legal)} ===", flush=True)
    stats = Counter()
    rng = random.Random(seed + 17 * L + 31 * S)
    n6 = json.loads(N6_WIT.read_text(encoding="utf-8"))
    base5 = [list(r) for r in n6["delta"]]

    seeds = []
    if S == 5:
        seeds.extend(n6_port_boost_seeds(base5, rng))
    elif S >= 6:
        for _ in range(40):
            seeds.append(pad_from_n6(base5, S, rng))
        seeds.extend(n6_port_boost_seeds(base5, rng)[:10])  # may be S=5 only
        seeds = [d for d in seeds if len(d) == S]
    # dedup
    uniq = []
    seen = set()
    for d in seeds:
        key = tuple(tuple(r) for r in d)
        if key not in seen and len(d) == S:
            seen.add(key)
            uniq.append(d)
    seeds = uniq
    print(f"structured seeds: {len(seeds)}", flush=True)

    found = None
    for i, delta in enumerate(seeds):
        if time.time() - t0 > budget:
            break
        stats["seed_tries"] += 1
        hit = exhaust_clock(delta, legal, cols, L, S, stats, max_assign=max_assign)
        if hit:
            found = hit
            print("FOUND seed", i, flush=True)
            break
        if (i + 1) % 10 == 0:
            print(f"seeds {i+1}/{len(seeds)} {dict(stats)} t={time.time()-t0:.0f}s", flush=True)

    if not found:
        print("mutations", flush=True)
        base = seeds[0] if seeds else (base5 if S == 5 else pad_from_n6(base5, S, rng))
        for k in range(mut_n):
            if time.time() - t0 > budget:
                break
            delta = mutate(base if S == len(base) else pad_from_n6(base5, S, rng), S, rng, 1 + k % 3, force_ports=TAGS)
            stats["mut_tries"] += 1
            hit = exhaust_clock(delta, legal, cols, L, S, stats, max_assign=max(50, max_assign // 3))
            if hit:
                found = hit
                print("FOUND mut", k, flush=True)
                break
            if (k + 1) % 40 == 0:
                print(f"mut {k+1} {dict(stats)} t={time.time()-t0:.0f}s", flush=True)

    if not found:
        print("random high-port", flush=True)
        for k in range(rand_n):
            if time.time() - t0 > budget:
                break
            delta = random_clock(S, rng, port_bias=0.44)
            if len(M.anchor_ports(delta, S)) < TAGS:
                stats["rand_skip"] += 1
                continue
            stats["rand_tries"] += 1
            hit = exhaust_clock(delta, legal, cols, L, S, stats, max_assign=max(30, max_assign // 4))
            if hit:
                found = hit
                print("FOUND rand", k, flush=True)
                break
            if (k + 1) % 80 == 0:
                print(f"rand {k+1} {dict(stats)} t={time.time()-t0:.0f}s", flush=True)

    return found, stats, time.time() - t0, len(legal)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["ports", "hunt", "all"], default="all")
    ap.add_argument("--L", type=int, default=0)
    ap.add_argument("--S", type=int, default=0)
    ap.add_argument("--trials", type=int, default=80_000)
    ap.add_argument("--mut", type=int, default=300)
    ap.add_argument("--rand", type=int, default=600)
    ap.add_argument("--max-assign", type=int, default=250)
    ap.add_argument("--budget", type=float, default=600.0)
    ap.add_argument("--seed", type=int, default=20260721)
    args = ap.parse_args()

    if args.mode in ("ports", "all"):
        # consolidate + refresh samples
        for L in (3, 4, 5):
            for S in (5, 6):
                print(f"port sample S={S} L={L}", flush=True)
                out = sample_ports(S, L, args.trials // (1 if S == 5 else 2), args.seed + L * 10 + S)
                path = HERE / f"PORT_CAPACITY_S{S}_L{L}_N7_SAMPLE.json"
                path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                print(
                    json.dumps(
                        {k: out[k] for k in ("S", "L", "reachable", "ge8_ports", "max_ports", "frac_ge8_among_reachable")},
                        indent=2,
                    ),
                    flush=True,
                )

    if args.mode in ("hunt", "all"):
        if args.L and args.S:
            schedule = [(args.L, args.S)]
        else:
            # cheaper L=3 first (route enum 27^3), then suggested L=4/5
            schedule = [(3, 5), (3, 6), (4, 5), (5, 5), (4, 6)]
        summary = []
        for L, S in schedule:
            found, stats, elapsed, nlegal = hunt_cell(
                L, S, args.mut, args.rand, args.max_assign, args.seed, args.budget
            )
            cell = {
                "L": L,
                "S": S,
                "elapsed_sec": round(elapsed, 3),
                "dig_patterns": nlegal,
                "stats": dict(stats),
                "status": "FOUND_INTEGER" if found else "NO_INTEGER_IN_HUNT",
            }
            out_path = HERE / f"N7_L{L}_S{S}_SEARCH.json"
            if found:
                wit_path = HERE / f"N7_L{L}_S{S}_WITNESS.json"
                wit_path.write_text(json.dumps(found, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                cell["witness"] = wit_path.name
                print("WROTE", wit_path, flush=True)
            out_path.write_text(
                json.dumps(
                    {
                        **cell,
                        "schema": f"lead.n7_l{L}_s{S}_search.v1",
                        "claim_boundary": (
                            f"Seed/mutation/random hunt n=7 L={L} S={S}. Not exhaustive."
                        ),
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            summary.append(cell)
            print(json.dumps(cell, indent=2), flush=True)
            if found:
                break

        HERE.joinpath("N7_HUNT_SUMMARY.json").write_text(
            json.dumps(
                {
                    "schema": "lead.n7_hunt_summary.v1",
                    "cells": summary,
                    "claim_boundary": "Finite hunt; not full classification of n=7.",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()

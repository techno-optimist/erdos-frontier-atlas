#!/usr/bin/env python3
"""
n=7 common-anchor Fibonacci macro hunt.

Attack:
  1) Port-capacity samples S=5 under L-reachability (ge 8 ports).
  2) Pad/mutate the sealed n=6 L=4 S=5 clock; try (L,S) in
     {(4,5), (5,5), (4,6)} with dig/port search + route enum + LP/MIP.

highspy required for LP/MIP. Stdlib + highspy.
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

import highspy

# `python3 -I` (isolated mode) implies -P, dropping this script's own directory from sys.path,
# so the sibling import below fails. Re-add it: keeps -I hermeticity (no user site-packages)
# AND makes the documented replay one-liner actually run. House convention -- see
# certificates/README.md; enforced by tests/test_certificate_replay.py.
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

import macro_engine as M

HERE = Path(__file__).resolve().parent
N6_WIT = HERE / "N6_L4_S5_WITNESS.json"


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
    """Recursive legal-route enum; one representative per Parikh feature."""
    u, v, w = origin
    target = (ports[u][0], ports[v][0], ports[w][0])
    uniq = {}

    def rec(step, carry, states, rp, digs_so_far):
        if step == L:
            if carry == tc and states == target:
                f = feat(rp, S)
                if f not in uniq:
                    uniq[f] = tuple(digs_so_far)
            return
        for a, b, c in itertools.product(range(3), repeat=3):
            cout = M.carry_step(a, b, c, carry)
            if cout is None:
                continue
            nrp = [list(rp[0]), list(rp[1]), list(rp[2])]
            for role, d in enumerate((a, b, c)):
                nrp[role].append((states[role], d))
            ns = (
                delta[states[0]][a],
                delta[states[1]][b],
                delta[states[2]][c],
            )
            digs_so_far.append((a, b, c))
            rec(step + 1, cout, ns, nrp, digs_so_far)
            digs_so_far.pop()

    rec(0, 0, (0, 0, 0), [[], [], []], [])
    return list(uniq.items())


def lp_ok(col_data, S):
    dim = 2 * S * 3
    nvars = sum(len(it) for _, _, it in col_data)
    if nvars == 0:
        return False
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.addVars(nvars, [0.0] * nvars, [1e9] * nvars)
    off = 0
    for w, name, items in col_data:
        k = len(items)
        h.addRow(float(w), float(w), k, list(range(off, off + k)), [1.0] * k)
        off += k
    for j in range(dim):
        idx, vals = [], []
        off = 0
        for w, name, items in col_data:
            for i, (f, _d3) in enumerate(items):
                if f[j]:
                    idx.append(off + i)
                    vals.append(float(f[j]))
            off += len(items)
        if idx:
            h.addRow(0.0, 0.0, len(idx), idx, vals)
    h.run()
    return int(h.getModelStatus()) == 7


def mip_recover(col_data, S, time_limit=120.0):
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
            for oi, (f, _d3) in enumerate(items):
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


def try_assignment(delta, digs, carries, ports, cols, L, S, stats, do_mip=True):
    tags = len(digs)
    ports_list = [ports[t] for t in range(tags)]
    if not M.outward_ok(ports_list, carries, cols):
        return None
    stats["outward"] += 1
    if not M.all_columns_routable(delta, ports_list, carries, cols, L):
        return None
    stats["routable"] += 1
    print(
        f"  ROUTABLE digs={list(digs)} ports={[list(ports[t]) for t in range(tags)]}",
        flush=True,
    )
    col_data = []
    for i, (w, origin, name) in enumerate(cols):
        items = enum_routes(delta, ports_list, origin, carries[i], L, S)
        if not items:
            stats["enum_empty"] += 1
            return None
        col_data.append((w, name, items))
    stats["route_enum"] += 1
    nvars = sum(len(it) for _, _, it in col_data)
    print(f"  enum nvars={nvars} per_col={[len(it) for _,_,it in col_data]}", flush=True)
    if not lp_ok(col_data, S):
        stats["lp_infeas"] += 1
        print("  LP_INFEAS", flush=True)
        return None
    stats["lp"] += 1
    print("  LP_HIT", flush=True)
    if not do_mip:
        return {"lp_only": True, "delta": delta, "digs": digs, "carries": carries, "ports": ports}
    sel = mip_recover(col_data, S)
    if sel:
        stats["mip"] += 1
        return {
            "n": 7,
            "L": L,
            "S": S,
            "delta": delta,
            "ports": {str(t): list(ports[t]) for t in range(tags)},
            "digs": list(digs),
            "carries": list(carries),
            "selected": sel,
        }
    stats["mip_infeas"] += 1
    print("  MIP_INFEAS", flush=True)
    return None


def pad_delta(delta, new_S, rng):
    """Pad Sx3 delta to new_S x 3 with random rows, bias toward anchor ports."""
    S0 = len(delta)
    out = [list(row) for row in delta]
    for s in range(S0, new_S):
        row = []
        for _ in range(3):
            if rng.random() < 0.35:
                row.append(0)
            else:
                row.append(rng.randrange(new_S))
        out.append(row)
    # remap existing entries that might need to stay in range (already < S0)
    # optionally add transitions into new states
    for s in range(S0):
        for d in range(3):
            if rng.random() < 0.08:
                out[s][d] = rng.randrange(new_S)
    return out


def mutate_delta(delta, S, rng, n_mut=1, force_ports=None):
    d = [list(row) for row in delta]
    for _ in range(n_mut):
        s = rng.randrange(S)
        dig = rng.randrange(3)
        d[s][dig] = rng.randrange(S)
    if force_ports is not None:
        # ensure enough anchor ports by flipping non-ports to 0
        ap = M.anchor_ports(d, S)
        guard = 0
        while len(ap) < force_ports and guard < 40:
            s = rng.randrange(S)
            dig = rng.randrange(3)
            if d[s][dig] != 0:
                d[s][dig] = 0
            ap = M.anchor_ports(d, S)
            guard += 1
    return d


def random_clock(S, rng, port_bias=0.38):
    flat = [0 if rng.random() < port_bias else rng.randrange(S) for _ in range(S * 3)]
    return [flat[i * 3 : (i + 1) * 3] for i in range(S)]


def exhaust_clock(delta, legal, cols, L, S, tags, stats, max_assign=300, do_mip=True):
    if not M.clock_reachable(delta, S, L):
        return None
    ap = M.anchor_ports(delta, S)
    if len(ap) < tags:
        return None
    stats["clocks_ok"] += 1
    # Prefer dig patterns whose multiset fits available port digits
    by_d = Counter(p[1] for p in ap)
    for digs, carries in legal:
        need = Counter(digs)
        if any(need[d] > by_d[d] for d in need):
            continue
        count = 0
        for ports in M.assign_ports_for_digs(ap, digs, tags):
            count += 1
            if count > max_assign:
                break
            hit = try_assignment(delta, digs, carries, ports, cols, L, S, stats, do_mip=do_mip)
            if hit and hit.get("selected"):
                return hit
            if hit and hit.get("lp_only"):
                # keep hunting for integer; record but continue
                stats["lp_hits_recorded"] += 1
    return None


def sample_port_capacity(S, L, trials, seed):
    rng = random.Random(seed)
    hist = Counter()
    reachable = 0
    ge8 = 0
    max_ports = 0
    for _ in range(trials):
        delta = random_clock(S, rng, port_bias=0.40)
        if not M.clock_reachable(delta, S, L):
            continue
        reachable += 1
        nports = len(M.anchor_ports(delta, S))
        hist[nports] += 1
        max_ports = max(max_ports, nports)
        if nports >= 8:
            ge8 += 1
    return {
        "schema": f"lead.port_capacity_s{S}_L{L}_sample.v1",
        "S": S,
        "L": L,
        "trials": trials,
        "reachable": reachable,
        "ge8_ports": ge8,
        "max_ports": max_ports,
        "hist": {str(k): hist[k] for k in sorted(hist)},
        "claim_boundary": "Random sample only; not exhaustive port capacity.",
    }


def hunt(L, S, n_seed_mut, n_rand, max_assign, seed, time_budget):
    t0 = time.time()
    N = 7
    tags = N + 1
    cols = M.columns(N)
    legal = M.digit_patterns(cols, tags)
    print(f"=== hunt n=7 L={L} S={S} dig_patterns={len(legal)} ===", flush=True)
    stats = Counter()
    rng = random.Random(seed)
    found = None

    n6 = json.loads(N6_WIT.read_text(encoding="utf-8"))
    base5 = [list(r) for r in n6["delta"]]
    assert len(base5) == 5

    seeds = []
    if S == 5:
        seeds.append(base5)
        # force more ports on base
        for k in range(20):
            seeds.append(mutate_delta(base5, 5, rng, n_mut=1 + k % 3, force_ports=8))
    elif S == 6:
        for k in range(30):
            seeds.append(pad_delta(base5, 6, rng))
        # pure random high-port seeds also in phase later
    else:
        raise ValueError(S)

    print(f"phase1 seeds={len(seeds)}", flush=True)
    for i, delta in enumerate(seeds):
        if time.time() - t0 > time_budget:
            break
        stats["seed_tries"] += 1
        hit = exhaust_clock(delta, legal, cols, L, S, tags, stats, max_assign=max_assign)
        if hit:
            found = hit
            print("FOUND on seed", i, flush=True)
            break
        if (i + 1) % 5 == 0:
            print(f"seeds {i+1}/{len(seeds)} {dict(stats)} t={time.time()-t0:.0f}s", flush=True)

    if not found:
        print("phase2 mutations of base", flush=True)
        for k in range(n_seed_mut):
            if time.time() - t0 > time_budget:
                break
            if S == 5:
                delta = mutate_delta(base5, 5, rng, n_mut=1 + (k % 4), force_ports=8)
            else:
                base = pad_delta(base5, S, rng)
                delta = mutate_delta(base, S, rng, n_mut=1 + (k % 3), force_ports=8)
            stats["mut_tries"] += 1
            hit = exhaust_clock(delta, legal, cols, L, S, tags, stats, max_assign=max(40, max_assign // 3))
            if hit:
                found = hit
                print("FOUND on mutation", k, flush=True)
                break
            if (k + 1) % 50 == 0:
                print(f"mut {k+1} {dict(stats)} t={time.time()-t0:.0f}s", flush=True)

    if not found:
        print("phase3 random high-port clocks", flush=True)
        for k in range(n_rand):
            if time.time() - t0 > time_budget:
                break
            delta = random_clock(S, rng, port_bias=0.42)
            if len(M.anchor_ports(delta, S)) < tags:
                stats["rand_skip_ports"] += 1
                continue
            stats["rand_tries"] += 1
            hit = exhaust_clock(delta, legal, cols, L, S, tags, stats, max_assign=max(30, max_assign // 4))
            if hit:
                found = hit
                print("FOUND on random", k, flush=True)
                break
            if (k + 1) % 100 == 0:
                print(f"rand {k+1} {dict(stats)} t={time.time()-t0:.0f}s", flush=True)

    return found, stats, time.time() - t0, len(legal)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["ports", "hunt", "all"], default="all")
    ap.add_argument("--L", type=int, default=0, help="0 = run default L schedule")
    ap.add_argument("--S", type=int, default=0)
    ap.add_argument("--trials", type=int, default=100_000)
    ap.add_argument("--mut", type=int, default=400)
    ap.add_argument("--rand", type=int, default=800)
    ap.add_argument("--max-assign", type=int, default=200)
    ap.add_argument("--budget", type=float, default=900.0, help="seconds per (L,S) cell")
    ap.add_argument("--seed", type=int, default=20260721)
    args = ap.parse_args()

    if args.mode in ("ports", "all"):
        for L in (3, 4, 5):
            for S in (5, 6):
                print(f"port sample S={S} L={L}", flush=True)
                out = sample_port_capacity(S, L, args.trials // (2 if S == 6 else 1), args.seed + L * 10 + S)
                path = HERE / f"PORT_CAPACITY_S{S}_L{L}_N7_SAMPLE.json"
                path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                print(json.dumps({k: out[k] for k in ("S", "L", "reachable", "ge8_ports", "max_ports")}, indent=2), flush=True)

    if args.mode in ("hunt", "all"):
        schedule = []
        if args.L and args.S:
            schedule = [(args.L, args.S)]
        else:
            # suggested order
            schedule = [(4, 5), (5, 5), (4, 6)]

        summary = []
        for L, S in schedule:
            found, stats, elapsed, nlegal = hunt(
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
                cell["witness"] = str(wit_path.name)
                print("WROTE", wit_path, flush=True)
            out_path.write_text(
                json.dumps(
                    {
                        **cell,
                        "schema": f"lead.n7_l{L}_s{S}_search.v1",
                        "claim_boundary": (
                            f"Seed/mutation/random hunt for n=7 L={L} S={S}. "
                            "Not exhaustive over clocks or assignments."
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
                break  # stop at first integer witness (minimal in schedule order)

        sum_path = HERE / "N7_HUNT_SUMMARY.json"
        sum_path.write_text(
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

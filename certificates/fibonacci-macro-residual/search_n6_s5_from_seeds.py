#!/usr/bin/env python3
"""
n=6 L=3 S=5: exhaust dig/port combos on known-good clocks + neighborhood mutations.

Uses highspy for LP/MIP. Stdlib + highspy.
"""

from __future__ import annotations

import itertools
import json
import random
import time
from collections import Counter
from pathlib import Path

import highspy

# `python3 -I` (isolated mode) implies -P, dropping this script's own directory from sys.path,
# so the sibling import below fails. Re-add it: keeps -I hermeticity (no user site-packages)
# AND makes the documented replay one-liner actually run. House convention -- see
# certificates/README.md; enforced by tests/test_certificate_replay.py.
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

import macro_engine as M

HERE = Path(__file__).resolve().parent
OUT = HERE / "N6_L3_S5_SEED_HUNT.json"
WIT = HERE / "N6_L3_S5_WITNESS.json"

N, L, S = 6, 3, 5
TAGS = N + 1
COLS = M.columns(N)


def feat(role_ports):
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


def enum_routes(delta, ports, origin, tc):
    u, v, w = origin
    target = (ports[u][0], ports[v][0], ports[w][0])
    uniq = {}
    for digs3 in itertools.product(itertools.product(range(3), repeat=3), repeat=L):
        carry = 0
        states = (0, 0, 0)
        rp = [[], [], []]
        ok = True
        for step in range(L):
            a, b, c = digs3[step]
            cout = M.carry_step(a, b, c, carry)
            if cout is None:
                ok = False
                break
            for role, d in enumerate((a, b, c)):
                rp[role].append((states[role], d))
            states = (
                delta[states[0]][a],
                delta[states[1]][b],
                delta[states[2]][c],
            )
            carry = cout
        if ok and carry == tc and states == target:
            uniq.setdefault(feat(rp), digs3)
    return list(uniq.items())


def lp_ok(col_data):
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
            for i, (f, d3) in enumerate(items):
                if f[j]:
                    idx.append(off + i)
                    vals.append(float(f[j]))
            off += len(items)
        if idx:
            h.addRow(0.0, 0.0, len(idx), idx, vals)
    h.run()
    return int(h.getModelStatus()) == 7


def mip_recover(col_data, time_limit=90.0):
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
            for oi, (f, d3) in enumerate(items):
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


def try_assignment(delta, digs, carries, ports, stats):
    if not M.outward_ok(ports, carries, COLS):
        return None
    stats["outward"] += 1
    if not M.all_columns_routable(delta, ports, carries, COLS, L):
        return None
    stats["routable"] += 1
    col_data = []
    for i, (w, origin, name) in enumerate(COLS):
        items = enum_routes(delta, ports, origin, carries[i])
        if not items:
            return None
        col_data.append((w, name, items))
    stats["route_enum"] += 1
    if not lp_ok(col_data):
        stats["lp_infeas"] += 1
        return None
    stats["lp"] += 1
    print("LP_HIT", digs, flush=True)
    sel = mip_recover(col_data)
    if sel:
        stats["mip"] += 1
        return {
            "delta": delta,
            "ports": {str(t): list(ports[t]) for t in range(TAGS)},
            "digs": list(digs),
            "carries": list(carries),
            "selected": sel,
        }
    stats["mip_infeas"] += 1
    return None


def exhaust_clock(delta, legal, stats, max_assign=200):
    """All dig patterns + capped port assignments on one clock."""
    if not M.clock_reachable(delta, S, L):
        return None
    ap = M.anchor_ports(delta, S)
    if len(ap) < TAGS:
        return None
    stats["clocks_ok"] += 1
    for digs, carries in legal:
        count = 0
        for ports in M.assign_ports_for_digs(ap, digs, TAGS):
            count += 1
            if count > max_assign:
                break
            hit = try_assignment(delta, digs, carries, ports, stats)
            if hit:
                return hit
    return None


def mutate_delta(delta, rng, n_mut=1):
    d = [list(row) for row in delta]
    for _ in range(n_mut):
        s = rng.randrange(S)
        dig = rng.randrange(3)
        d[s][dig] = rng.randrange(S)
    return d


def main():
    t0 = time.time()
    stats = Counter()
    legal = M.digit_patterns(COLS, TAGS)
    print("digits", len(legal), flush=True)
    rng = random.Random(20260721)

    seeds = []
    first = HERE / "N6_L3_S5_FIRST_ROUTABLE.json"
    if first.exists():
        seeds.append(json.loads(first.read_text(encoding="utf-8"))["delta"])
    # also n=5 S=4 witness padded
    n5 = HERE / "N5_L3_S4_WITNESS.json"
    if n5.exists():
        base = json.loads(n5.read_text(encoding="utf-8"))["delta"]
        for row in itertools.product(range(S), repeat=3):
            seeds.append([list(r) for r in base] + [list(row)])
            if len(seeds) > 50:
                break

    found = None
    # Phase 1: exhaust seed clocks
    print("phase1 seeds", len(seeds), flush=True)
    for i, delta in enumerate(seeds):
        stats["seed_tries"] += 1
        hit = exhaust_clock(delta, legal, stats, max_assign=500)
        if hit:
            found = hit
            print("FOUND on seed", i, flush=True)
            break
        if (i + 1) % 10 == 0:
            print(f"seeds {i+1}/{len(seeds)} {dict(stats)}", flush=True)

    # Phase 2: mutations of first routable
    if not found and seeds:
        print("phase2 mutations", flush=True)
        base = seeds[0]
        for k in range(5000):
            delta = mutate_delta(base, rng, n_mut=1 + (k % 3))
            stats["mut_tries"] += 1
            hit = exhaust_clock(delta, legal, stats, max_assign=80)
            if hit:
                found = hit
                print("FOUND on mutation", k, flush=True)
                break
            if (k + 1) % 200 == 0:
                print(f"mut {k+1} {dict(stats)} t={time.time()-t0:.0f}s", flush=True)

    # Phase 3: random high-port clocks
    if not found:
        print("phase3 random", flush=True)
        for k in range(3000):
            flat = [
                0 if rng.random() < 0.42 else rng.randrange(S) for _ in range(S * 3)
            ]
            delta = [flat[i * 3 : (i + 1) * 3] for i in range(S)]
            stats["rand_tries"] += 1
            hit = exhaust_clock(delta, legal, stats, max_assign=40)
            if hit:
                found = hit
                print("FOUND on random", k, flush=True)
                break
            if (k + 1) % 200 == 0:
                print(f"rand {k+1} {dict(stats)} t={time.time()-t0:.0f}s", flush=True)

    if found:
        WIT.write_text(json.dumps(found, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out = {
        "schema": "lead.n6_l3_s5_seed_hunt.v1",
        "status": "FOUND_INTEGER" if found else "NO_INTEGER_IN_HUNT",
        "elapsed_sec": round(time.time() - t0, 3),
        "stats": dict(stats),
        "claim_boundary": (
            "Seed+mutation+random hunt for n=6 L=3 S=5 integer macro. "
            "Not exhaustive over all 5^15 clocks."
        ),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Smoke n=8 hunt from n=7 L=5 S=5 witness."""
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
n7 = json.loads((HERE / "N7_L5_S5_WITNESS.json").read_text(encoding="utf-8"))
base = n7["delta"]
N = 8
TAGS = N + 1
COLS = M.columns(N)


def feat(rp, S):
    cnt = [Counter(), Counter(), Counter()]
    for role in range(3):
        for p in rp[role]:
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
            uniq.setdefault(feat(rp, S), digs3)
    return list(uniq.items())


def lp_mip(col_data, S):
    dim = 2 * S * 3
    nvars = sum(len(it) for _, _, it in col_data)
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
    if int(h.getModelStatus()) != 7:
        return None
    h2 = highspy.Highs()
    h2.setOptionValue("output_flag", False)
    h2.setOptionValue("time_limit", 90)
    h2.addVars(nvars, [0.0] * nvars, [1e6] * nvars)
    h2.changeColsIntegrality(
        nvars, list(range(nvars)), [highspy.HighsVarType.kInteger] * nvars
    )
    off = 0
    ranges = []
    for w, name, items in col_data:
        idxs = list(range(off, off + len(items)))
        h2.addRow(float(w), float(w), len(idxs), idxs, [1.0] * len(idxs))
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
            h2.addRow(0.0, 0.0, len(idx), idx, vals)
    h2.run()
    if int(h2.getModelStatus()) != 7:
        return "MIP_INFEAS"
    sol = h2.getSolution().col_value
    selected = {}
    for w, name, items, idxs in ranges:
        picks = []
        for oi, (f, d3) in enumerate(items):
            m = int(round(sol[idxs[oi]]))
            if m:
                picks.append({"mult": m, "steps": [list(t) for t in d3]})
        selected[name] = picks
    return selected


def main():
    rng = random.Random(3)
    found = None
    t0 = time.time()
    for L, S in [(5, 5), (6, 5), (5, 6), (6, 6)]:
        legal = M.digit_patterns(COLS, TAGS)
        stats = Counter()
        print("===", L, S, "digits", len(legal), flush=True)
        deltas = []
        d0 = [list(r) for r in base]
        while len(d0) < S:
            d0.append([0, 0, 0])
        deltas.append(d0)
        for _ in range(80):
            d = [list(r) for r in d0]
            for __ in range(1 + rng.randrange(3)):
                d[rng.randrange(S)][rng.randrange(3)] = rng.randrange(S)
            deltas.append(d)
        for delta in deltas:
            stats["clocks"] += 1
            if not M.clock_reachable(delta, S, L):
                continue
            ap = M.anchor_ports(delta, S)
            if len(ap) < TAGS:
                continue
            stats["ge"] += 1
            for digs, carries in legal:
                nass = 0
                for ports in M.assign_ports_for_digs(ap, digs, TAGS):
                    nass += 1
                    if nass > 20:
                        break
                    if not M.outward_ok(ports, carries, COLS):
                        continue
                    stats["out"] += 1
                    if not M.all_columns_routable(delta, ports, carries, COLS, L):
                        continue
                    stats["rout"] += 1
                    col_data = []
                    ok = True
                    for i, (w, origin, name) in enumerate(COLS):
                        items = enum_routes(delta, ports, origin, carries[i], L, S)
                        if not items:
                            ok = False
                            break
                        col_data.append((w, name, items))
                    if not ok:
                        continue
                    r = lp_mip(col_data, S)
                    if r is None:
                        stats["lp_in"] += 1
                        continue
                    if r == "MIP_INFEAS":
                        stats["mip_in"] += 1
                        continue
                    found = {
                        "L": L,
                        "S": S,
                        "delta": delta,
                        "ports": {str(t): list(ports[t]) for t in range(TAGS)},
                        "digs": list(digs),
                        "carries": list(carries),
                        "selected": r,
                    }
                    print("FOUND", L, S, flush=True)
                    break
                if found:
                    break
            if found:
                break
        print(dict(stats), flush=True)
        if found:
            break
    if found:
        (HERE / f"N8_L{found['L']}_S{found['S']}_WITNESS.json").write_text(
            json.dumps(found, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    out = {
        "status": "FOUND" if found else "NO_HIT",
        "elapsed": round(time.time() - t0, 3),
        "found": bool(found),
    }
    (HERE / "N8_SEARCH_SMOKE.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8"
    )
    print(out)


if __name__ == "__main__":
    main()

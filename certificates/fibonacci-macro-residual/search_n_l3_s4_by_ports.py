#!/usr/bin/env python3
"""
Efficient n∈{6,7,8} L=3 S=4 census: only clocks with enough anchor ports.

For each n, scans all 4^12 clocks but skips early unless len(ap) >= n+1.
LP+MIP on routable assignments when highspy present.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from collections import Counter
from pathlib import Path

# `python3 -I` (isolated mode) implies -P, which drops this script's own directory from
# sys.path, so the sibling import below fails. Re-add it explicitly: that keeps the -I
# hermeticity the replay instructions rely on (no user site-packages) AND makes the
# documented one-liner actually run for a stranger.
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

import macro_engine as M

HERE = Path(__file__).resolve().parent

L, S = 3, 4


def feat_role_ports(role_ports, S_local):
    cnt = [Counter(), Counter(), Counter()]
    for role in range(3):
        for p in role_ports[role]:
            cnt[role][p] += 1
    keys = [(s, d) for s in range(S_local) for d in range(3)]
    out = []
    for k in keys:
        out.append(cnt[0][k] - cnt[1][k])
    for k in keys:
        out.append(cnt[2][k] - cnt[1][k])
    return tuple(out)


def enumerate_routes(delta, ports, origin, tc, S_local):
    u, v, w = origin
    target = (ports[u][0], ports[v][0], ports[w][0])
    uniq = {}
    for digs3 in itertools.product(itertools.product(range(3), repeat=3), repeat=L):
        carry = 0
        states = (0, 0, 0)
        role_ports = [[], [], []]
        ok = True
        for step in range(L):
            a, b, c = digs3[step]
            cout = M.carry_step(a, b, c, carry)
            if cout is None:
                ok = False
                break
            for role, d in enumerate((a, b, c)):
                role_ports[role].append((states[role], d))
            states = (
                delta[states[0]][a],
                delta[states[1]][b],
                delta[states[2]][c],
            )
            carry = cout
        if not ok or carry != tc or states != target:
            continue
        feat = feat_role_ports(role_ports, S_local)
        uniq.setdefault(feat, digs3)
    return list(uniq.items())


def lp_ok(col_data, S_local):
    import highspy

    dim = 2 * S_local * 3
    nvars = sum(len(items) for _, _, items in col_data)
    if nvars == 0:
        return False
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.addVars(nvars, [0.0] * nvars, [1e9] * nvars)
    h.changeColsCost(nvars, list(range(nvars)), [0.0] * nvars)
    off = 0
    for weight, name, items in col_data:
        k = len(items)
        h.addRow(float(weight), float(weight), k, list(range(off, off + k)), [1.0] * k)
        off += k
    for j in range(dim):
        idx, vals = [], []
        off = 0
        for weight, name, items in col_data:
            for i, (feat, digs3) in enumerate(items):
                if feat[j]:
                    idx.append(off + i)
                    vals.append(float(feat[j]))
            off += len(items)
        if idx:
            h.addRow(0.0, 0.0, len(idx), idx, vals)
    h.run()
    return int(h.getModelStatus()) == 7


def mip_recover(col_data, S_local, time_limit=60.0):
    import highspy

    dim = 2 * S_local * 3
    nvars = sum(len(items) for _, _, items in col_data)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", time_limit)
    h.addVars(nvars, [0.0] * nvars, [1e6] * nvars)
    h.changeColsIntegrality(
        nvars, list(range(nvars)), [highspy.HighsVarType.kInteger] * nvars
    )
    h.changeColsCost(nvars, list(range(nvars)), [0.0] * nvars)
    off = 0
    ranges = []
    for weight, name, items in col_data:
        idxs = list(range(off, off + len(items)))
        h.addRow(float(weight), float(weight), len(idxs), idxs, [1.0] * len(idxs))
        ranges.append((weight, name, items, idxs))
        off += len(items)
    for j in range(dim):
        idx, vals = [], []
        for weight, name, items, idxs in ranges:
            for oi, (feat, digs3) in enumerate(items):
                if feat[j]:
                    idx.append(idxs[oi])
                    vals.append(float(feat[j]))
        if idx:
            h.addRow(0.0, 0.0, len(idx), idx, vals)
    h.run()
    st = int(h.getModelStatus())
    if st != 7:
        return {"status": "MIP_INFEAS", "model_status": st}
    sol = h.getSolution().col_value
    selected = {}
    for weight, name, items, idxs in ranges:
        picks = []
        for oi, (feat, digs3) in enumerate(items):
            mult = int(round(sol[idxs[oi]]))
            if mult:
                picks.append({"mult": mult, "steps": [list(t) for t in digs3]})
        selected[name] = picks
    return {"status": "FOUND_INTEGER", "selected": selected}


def run_n(n: int, do_lp: bool = True):
    tags = n + 1
    cols = M.columns(n)
    legal = M.digit_patterns(cols, tags)
    t0 = time.time()
    stats = Counter()
    total = S ** (S * 3)
    found = None
    print(f"=== n={n} tags={tags} digits={len(legal)} ===", flush=True)

    for idx, flat in enumerate(itertools.product(range(S), repeat=S * 3)):
        stats["clocks"] = idx + 1
        delta = [list(flat[i * 3 : (i + 1) * 3]) for i in range(S)]
        ap = M.anchor_ports(delta, S)
        if len(ap) < tags:
            continue
        # cheap filter before reachability BFS
        stats["ge_ports"] += 1
        if not M.clock_reachable(delta, S, L):
            continue
        stats["ge_tags"] += 1
        for digs, carries in legal:
            for ports in M.assign_ports_for_digs(ap, digs, tags):
                if not M.outward_ok(ports, carries, cols):
                    continue
                stats["outward"] += 1
                if not M.all_columns_routable(delta, ports, carries, cols, L):
                    continue
                stats["routable"] += 1
                if not do_lp:
                    continue
                col_data = []
                ok = True
                for i, (weight, origin, name) in enumerate(cols):
                    items = enumerate_routes(delta, ports, origin, carries[i], S)
                    if not items:
                        ok = False
                        break
                    col_data.append((weight, name, items))
                if not ok:
                    continue
                stats["route_enum"] += 1
                try:
                    if not lp_ok(col_data, S):
                        stats["lp_infeas"] += 1
                        continue
                except ImportError:
                    print("no highspy", flush=True)
                    do_lp = False
                    continue
                stats["lp"] += 1
                print(f"LP_HIT n={n} idx={idx}", flush=True)
                r = mip_recover(col_data, S)
                print("  mip", r["status"], flush=True)
                if r["status"] == "FOUND_INTEGER":
                    found = {
                        "n": n,
                        "delta": delta,
                        "ports": {str(t): list(ports[t]) for t in range(tags)},
                        "digs": list(digs),
                        "carries": list(carries),
                        "clock_idx": idx,
                        "selected": r["selected"],
                    }
                    break
                stats["mip_infeas"] += 1
            if found:
                break
        if found:
            break
        if (idx + 1) % 2_000_000 == 0:
            print(
                f"n={n} progress {idx+1}/{total} {dict(stats)} "
                f"t={time.time()-t0:.0f}s",
                flush=True,
            )

    status = (
        "FOUND_INTEGER"
        if found
        else (
            "NO_LP"
            if stats["routable"] and stats.get("lp", 0) == 0
            else (
                "NO_ROUTABLE"
                if stats["routable"] == 0
                else "INCOMPLETE"
            )
        )
    )
    # refine status when full scan done without hit
    if not found and stats["clocks"] == total:
        if stats.get("lp", 0) == 0 and stats["routable"] == 0:
            status = f"NO_N{n}_L3_S4"
        elif stats.get("lp", 0) == 0:
            status = f"NO_N{n}_L3_S4"  # routable but no LP
        else:
            status = f"NO_INTEGER_N{n}_L3_S4"

    out = {
        "schema": f"lead.n{n}_l3_s4_complete.v1",
        "status": status,
        "n": n,
        "L": L,
        "S": S,
        "elapsed_sec": round(time.time() - t0, 3),
        "stats": dict(stats),
        "digit_patterns": len(legal),
        "total_clocks": total,
        "witness": found,
        "claim_boundary": (
            f"Exhaustive n={n} L=3 S=4 common-anchor census with LP/MIP. "
            "NO_* means no integer Parikh-balanced macro."
        ),
    }
    path = HERE / f"N{n}_L3_S4_COMPLETE.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if found:
        (HERE / f"N{n}_L3_S4_WITNESS.json").write_text(
            json.dumps(found, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps({k: v for k, v in out.items() if k != "witness"}, indent=2))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, nargs="+", default=[8, 7])
    args = ap.parse_args()
    for n in args.n:
        run_n(n)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Faster n-hunter: pad prev witness first, early BFS prune, sparse port assigns.
Prints progress every assignment batch. Stops at first INTEGER.

Usage:
  python hunt_n_fast.py --n 11 --from N10_L6_S7_WITNESS.json --configs 7,7 7,8 8,7 8,8 6,8
"""

from __future__ import annotations

import argparse
import json
import random
import time
from collections import Counter
from pathlib import Path

# `python3 -I` (isolated mode) implies -P, dropping this script's own directory from sys.path,
# so the sibling import below fails. Re-add it: keeps -I hermeticity (no user site-packages)
# AND makes the documented replay one-liner actually run. House convention -- see
# certificates/README.md; enforced by tests/test_certificate_replay.py.
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

import macro_engine as M
import route_enum as R

HERE = Path(__file__).resolve().parent


def try_assignment(delta, digs, carries, ports, cols, L, S, stats, samples):
    if not M.outward_ok(ports, carries, cols):
        return None
    stats["outward"] += 1
    if not M.all_columns_routable(delta, ports, carries, cols, L):
        return None
    stats["routable"] += 1
    col_data = []
    for i, (w, origin, name) in enumerate(cols):
        items = R.enum_routes(
            delta, ports, origin, carries[i], L, S, samples=samples
        )
        if not items:
            stats["empty_enum"] += 1
            return None
        col_data.append((w, name, items))
    stats["route_enum"] += 1
    r = R.lp_mip(col_data, S)
    if r is None:
        stats["lp_infeas"] += 1
        return None
    if r == "MIP_INFEAS":
        stats["lp"] += 1
        stats["mip_infeas"] += 1
        return None
    stats["lp"] += 1
    stats["mip"] += 1
    return r


def make_deltas(base, S, muts, rand_n, rng):
    deltas = []
    d0 = [list(r) for r in base]
    while len(d0) < S:
        d0.append([0, 0, 0])
    # trim if base longer than S (shouldn't happen)
    d0 = d0[:S]
    deltas.append(d0)
    for _ in range(muts):
        d = [list(r) for r in d0]
        for __ in range(1 + rng.randrange(5)):
            d[rng.randrange(S)][rng.randrange(3)] = rng.randrange(S)
        deltas.append(d)
    for _ in range(rand_n):
        flat = [
            0 if rng.random() < 0.35 else rng.randrange(S) for _ in range(S * 3)
        ]
        deltas.append([flat[i * 3 : (i + 1) * 3] for i in range(S)])
    return deltas


def hunt(n, prev_path, configs, muts, rand_n, max_assign, samples, seed, dig_cap):
    prev = json.loads(Path(prev_path).read_text(encoding="utf-8"))
    base = prev["delta"]
    tags = n + 1
    cols = M.columns(n)
    rng = random.Random(seed)
    t0 = time.time()
    found = None
    all_stats = []

    for L, S in configs:
        if found:
            break
        legal = M.digit_patterns(cols, tags)
        if dig_cap and len(legal) > dig_cap:
            # prefer mixed dig patterns (not all-zero-ish)
            scored = []
            for digs, carries in legal:
                c = Counter(digs)
                scored.append((len(c), -max(c.values()), digs, carries))
            scored.sort(reverse=True)
            legal = [(d, c) for _, __, d, c in scored[:dig_cap]]
        stats = Counter()
        print(
            f"=== n={n} L={L} S={S} digits={len(legal)} tags={tags} cols={len(cols)} ===",
            flush=True,
        )
        deltas = make_deltas(base, S, muts, rand_n, rng)
        print(f"  clocks={len(deltas)} samples={samples}", flush=True)

        for di, delta in enumerate(deltas):
            stats["clocks"] += 1
            if not M.clock_reachable(delta, S, L):
                continue
            ap = M.anchor_ports(delta, S)
            if len(ap) < tags:
                continue
            stats["ge_tags"] += 1
            for digs, carries in legal:
                nass = 0
                for ports in M.assign_ports_for_digs(ap, digs, tags):
                    nass += 1
                    if nass > max_assign:
                        break
                    stats["tried"] += 1
                    sel = try_assignment(
                        delta, digs, carries, ports, cols, L, S, stats, samples
                    )
                    if sel:
                        found = {
                            "n": n,
                            "L": L,
                            "S": S,
                            "delta": delta,
                            "ports": {str(t): list(ports[t]) for t in range(tags)},
                            "digs": list(digs),
                            "carries": list(carries),
                            "selected": sel,
                        }
                        print("FOUND_INTEGER", L, S, flush=True)
                        break
                if found:
                    break
            if found:
                break
            if (di + 1) % 5 == 0 or di == 0:
                print(
                    f"  clock {di+1}/{len(deltas)} {dict(stats)} t={time.time()-t0:.0f}s",
                    flush=True,
                )
        all_stats.append({"L": L, "S": S, "stats": dict(stats)})
        print("config done", dict(stats), flush=True)

    if found:
        path = HERE / f"N{n}_L{found['L']}_S{found['S']}_WITNESS.json"
        path.write_text(json.dumps(found, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("wrote", path)
    out = {
        "schema": f"lead.n{n}_hunt_fast.v1",
        "status": "FOUND_INTEGER" if found else "NO_INTEGER_IN_HUNT",
        "elapsed_sec": round(time.time() - t0, 3),
        "configs": all_stats,
        "claim_boundary": "Heuristic pad/mutate hunt; not exhaustive.",
    }
    (HERE / f"N{n}_HUNT.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=2))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--from", dest="prev", required=True)
    ap.add_argument("--configs", nargs="+", default=["7,7", "7,8", "8,7", "8,8"])
    ap.add_argument("--muts", type=int, default=80)
    ap.add_argument("--rand", type=int, default=40)
    ap.add_argument("--max-assign", type=int, default=8)
    ap.add_argument("--samples", type=int, default=80000)
    ap.add_argument("--seed", type=int, default=20260721)
    ap.add_argument("--dig-cap", type=int, default=24)
    args = ap.parse_args()
    configs = [tuple(map(int, c.split(","))) for c in args.configs]
    hunt(
        args.n,
        HERE / args.prev if not Path(args.prev).is_absolute() else args.prev,
        configs,
        args.muts,
        args.rand,
        args.max_assign,
        args.samples,
        args.seed,
        args.dig_cap,
    )


if __name__ == "__main__":
    main()

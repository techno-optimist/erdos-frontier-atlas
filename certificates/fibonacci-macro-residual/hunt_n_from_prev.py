#!/usr/bin/env python3
"""
Generic n-hunter: pad/mutate previous witness clock; BFS routability then LP/MIP.

Usage:
  python hunt_n_from_prev.py --n 8 --from N7_L5_S5_WITNESS.json --configs 5,5 6,5 5,6 6,6
"""

from __future__ import annotations

import argparse
import json
import random
import time
from collections import Counter
from pathlib import Path

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


def hunt(n, prev_path, configs, muts, rand_n, max_assign, samples, seed):
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
        stats = Counter()
        print(f"=== n={n} L={L} S={S} digits={len(legal)} ===", flush=True)
        deltas = []
        d0 = [list(r) for r in base]
        while len(d0) < S:
            d0.append([0, 0, 0])
        deltas.append(d0)
        for _ in range(muts):
            d = [list(r) for r in d0]
            for __ in range(1 + rng.randrange(4)):
                d[rng.randrange(S)][rng.randrange(3)] = rng.randrange(S)
            deltas.append(d)
        for _ in range(rand_n):
            flat = [
                0 if rng.random() < 0.38 else rng.randrange(S) for _ in range(S * 3)
            ]
            deltas.append([flat[i * 3 : (i + 1) * 3] for i in range(S)])

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
            if (di + 1) % 40 == 0:
                print(
                    f"  {di+1}/{len(deltas)} {dict(stats)} t={time.time()-t0:.0f}s",
                    flush=True,
                )
        all_stats.append({"L": L, "S": S, "stats": dict(stats)})
        print("config done", dict(stats), flush=True)

    if found:
        path = HERE / f"N{n}_L{found['L']}_S{found['S']}_WITNESS.json"
        path.write_text(json.dumps(found, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("wrote", path)
    out = {
        "schema": f"lead.n{n}_hunt.v1",
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
    ap.add_argument(
        "--configs",
        nargs="+",
        default=["5,5", "6,5", "5,6", "6,6"],
        help="L,S pairs",
    )
    ap.add_argument("--muts", type=int, default=120)
    ap.add_argument("--rand", type=int, default=80)
    ap.add_argument("--max-assign", type=int, default=20)
    ap.add_argument("--samples", type=int, default=60000)
    ap.add_argument("--seed", type=int, default=20260721)
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
    )


if __name__ == "__main__":
    main()

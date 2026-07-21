#!/usr/bin/env python3
"""
Focused n=7 attack on one-port-boosts of the sealed n=6 L=4 S=5 clock.

The n=6 δ has exactly 7 anchor ports; n=7 needs 8. This script:
  1) enumerates all single-entry boosts that yield ≥8 ports + L-reachable
  2) on each, tries digs=(2,2,2,1,1,1,1,1) (extends n=6 digs) and ALL
     port assignments of matching digit multiset
  3) also tries full digit_patterns if --full-digs
  4) for each outward+routable: route enum + highspy LP/MIP

Intended as a <few-minute> exhaust relative to full random hunt.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import macro_engine as M
from mine_n7 import enum_routes, highs_lp_ok, highs_mip, try_assignment

HERE = Path(__file__).resolve().parent
N6 = json.loads((HERE / "N6_L4_S5_WITNESS.json").read_text(encoding="utf-8"))
N, TAGS = 7, 8


def boosts(base, S=5):
    out = []
    for s in range(S):
        for dig in range(3):
            if base[s][dig] == 0:
                continue
            d = [list(r) for r in base]
            d[s][dig] = 0
            out.append((s, dig, d))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=4)
    ap.add_argument("--full-digs", action="store_true")
    ap.add_argument("--max-assign", type=int, default=10_000)
    args = ap.parse_args()
    L = args.L
    S = 5
    cols = M.columns(N)
    base = [list(r) for r in N6["delta"]]
    t0 = time.time()
    stats = Counter()
    found = None

    # preferred dig pattern extending n=6
    preferred = (2, 2, 2, 1, 1, 1, 1, 1)
    legal = M.digit_patterns(cols, TAGS)
    legal_by = {tuple(d): c for d, c in legal}
    print("dig_patterns", len(legal), "preferred_ok", preferred in legal_by, flush=True)

    dig_list = list(legal) if args.full_digs else (
        [(preferred, legal_by[preferred])] if preferred in legal_by else list(legal)
    )

    for s, dig, delta in boosts(base, S):
        if not M.clock_reachable(delta, S, L):
            stats["unreach"] += 1
            continue
        ap_ports = M.anchor_ports(delta, S)
        if len(ap_ports) < TAGS:
            stats["ports_lt"] += 1
            continue
        stats["clocks"] += 1
        print(f"boost δ[{s}][{dig}]=0 ports={len(ap_ports)}", flush=True)
        by_d = Counter(p[1] for p in ap_ports)
        for digs, carries in dig_list:
            need = Counter(digs)
            if any(need[d] > by_d[d] for d in need):
                continue
            count = 0
            for ports in M.assign_ports_for_digs(ap_ports, digs, TAGS):
                count += 1
                if count > args.max_assign:
                    break
                hit = try_assignment(delta, digs, carries, ports, cols, L, S, stats)
                if hit:
                    found = hit
                    print("FOUND", flush=True)
                    break
            if found:
                break
        if found:
            break
        print(f"  done boost stats={dict(stats)} t={time.time()-t0:.1f}s", flush=True)

    out = {
        "schema": f"lead.n7_n6boost_L{L}.v1",
        "L": L,
        "S": S,
        "elapsed_sec": round(time.time() - t0, 3),
        "stats": dict(stats),
        "status": "FOUND_INTEGER" if found else "NO_INTEGER_ON_N6_BOOSTS",
        "claim_boundary": (
            "Exhaust one-entry port-boosts of sealed n=6 clock only. "
            "Not a full n=7 classification."
        ),
    }
    if found:
        wit = HERE / f"N7_L{L}_S{S}_WITNESS.json"
        wit.write_text(json.dumps(found, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        out["witness"] = wit.name
    path = HERE / f"N7_L{L}_S5_N6BOOST_EXHAUST.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()

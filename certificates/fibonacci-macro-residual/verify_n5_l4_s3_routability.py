#!/usr/bin/env python3
"""Exhaustive n=5 L=4 S=3 common-anchor routability census (pure Python)."""

from __future__ import annotations

import itertools
import json
import time
from collections import Counter
from pathlib import Path

import macro_engine as M

HERE = Path(__file__).resolve().parent
OUT = HERE / "N5_L4_S3_COMPLETE.json"

N, L, S = 5, 4, 3
TAGS = N + 1
COLS = M.columns(N)


def main():
    t0 = time.time()
    stats = Counter()
    legal = M.digit_patterns(COLS, TAGS)
    print("digit patterns", len(legal), "L", L, flush=True)
    total = S ** (S * 3)
    found = None

    for flat in itertools.product(range(S), repeat=S * 3):
        stats["clocks"] += 1
        delta = [list(flat[i * 3 : (i + 1) * 3]) for i in range(S)]
        if not M.clock_reachable(delta, S, L):
            continue
        stats["reachable"] += 1
        ap = M.anchor_ports(delta, S)
        if len(ap) < TAGS:
            continue
        stats["ge_tags"] += 1
        for digs, carries in legal:
            for ports in M.assign_ports_for_digs(ap, digs, TAGS):
                if not M.outward_ok(ports, carries, COLS):
                    continue
                stats["outward"] += 1
                if M.all_columns_routable(delta, ports, carries, COLS, L):
                    stats["routable"] += 1
                    found = {
                        "delta": delta,
                        "ports": {str(t): list(ports[t]) for t in range(TAGS)},
                        "digs": list(digs),
                        "carries": list(carries),
                    }
                    print("ROUTABLE", found, flush=True)
                    break
            if found:
                break
        if found:
            break
        if stats["clocks"] % 2000 == 0:
            print(
                f"progress {stats['clocks']}/{total} {dict(stats)} "
                f"t={time.time()-t0:.0f}s",
                flush=True,
            )

    status = "FOUND_ROUTABLE" if found else "NO_N5_L4_S3"
    out = {
        "schema": "lead.n5_l4_s3_complete.v1",
        "status": status,
        "L": L,
        "S": S,
        "n": N,
        "elapsed_sec": round(time.time() - t0, 3),
        "stats": dict(stats),
        "digit_patterns": len(legal),
        "witness": found,
        "claim_boundary": (
            "Exhaustive n=5 L=4 on all 3-state L<=4-reachable clocks. "
            "Pure-Python routability census."
        ),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "witness"}, indent=2))
    if status == "NO_N5_L4_S3":
        print("CERTIFIED: no n=5 L=4 S=3 common-anchor routable assignment")
    else:
        print("FOUND witness — not a no-go")


if __name__ == "__main__":
    main()

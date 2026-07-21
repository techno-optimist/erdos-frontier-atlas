#!/usr/bin/env python3
"""
Exhaustive n=5 L=3 S=4 common-anchor routability census (pure Python).

4^12 = 16_777_216 clocks. Filters: L<=3-reachable, >=6 anchor ports,
digit-driven port assignment (19 digit patterns). Progress JSON for resume.
"""

from __future__ import annotations

import itertools
import json
import time
from collections import Counter
from pathlib import Path

import macro_engine as M

HERE = Path(__file__).resolve().parent
OUT = HERE / "N5_L3_S4_COMPLETE.json"
PROGRESS = HERE / "N5_L3_S4_PROGRESS.json"

N, L, S = 5, 3, 4
TAGS = N + 1
COLS = M.columns(N)
CHECKPOINT_EVERY = 200_000


def main():
    t0 = time.time()
    stats = Counter()
    legal = M.digit_patterns(COLS, TAGS)
    print("digit patterns", len(legal), "S", S, "total clocks", S ** (S * 3), flush=True)
    total = S ** (S * 3)
    found = None
    start_idx = 0
    if PROGRESS.exists():
        prev = json.loads(PROGRESS.read_text(encoding="utf-8"))
        start_idx = int(prev.get("next_idx", 0))
        stats.update(prev.get("stats", {}))
        print("resume from", start_idx, dict(stats), flush=True)

    # enumerate by integer index for resume
    for idx, flat in enumerate(itertools.product(range(S), repeat=S * 3)):
        if idx < start_idx:
            continue
        stats["clocks"] = idx + 1
        delta = [list(flat[i * 3 : (i + 1) * 3]) for i in range(S)]
        if not M.clock_reachable(delta, S, L):
            pass
        else:
            stats["reachable"] += 1
            ap = M.anchor_ports(delta, S)
            if len(ap) >= TAGS:
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
                                "ports": {
                                    str(t): list(ports[t]) for t in range(TAGS)
                                },
                                "digs": list(digs),
                                "carries": list(carries),
                                "clock_idx": idx,
                            }
                            print("ROUTABLE", found, flush=True)
                            break
                    if found:
                        break
        if found:
            break
        if (idx + 1) % CHECKPOINT_EVERY == 0:
            snap = {
                "next_idx": idx + 1,
                "stats": dict(stats),
                "elapsed_sec": round(time.time() - t0, 3),
            }
            PROGRESS.write_text(
                json.dumps(snap, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            print(
                f"progress {idx+1}/{total} {dict(stats)} t={time.time()-t0:.0f}s",
                flush=True,
            )

    status = "FOUND_ROUTABLE" if found else "NO_N5_L3_S4"
    out = {
        "schema": "lead.n5_l3_s4_complete.v1",
        "status": status,
        "L": L,
        "S": S,
        "n": N,
        "elapsed_sec": round(time.time() - t0, 3),
        "stats": dict(stats),
        "digit_patterns": len(legal),
        "total_clocks": total,
        "witness": found,
        "claim_boundary": (
            "Exhaustive n=5 L=3 on all 4-state L<=3-reachable clocks. "
            "Pure-Python routability census."
        ),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if PROGRESS.exists() and not found:
        PROGRESS.unlink()
    print(json.dumps({k: v for k, v in out.items() if k != "witness"}, indent=2))
    if status == "NO_N5_L3_S4":
        print("CERTIFIED: no n=5 L=3 S=4 common-anchor routable assignment")
    else:
        print("FOUND witness")


if __name__ == "__main__":
    main()

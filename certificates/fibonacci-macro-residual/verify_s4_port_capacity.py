#!/usr/bin/env python3
"""
Port-capacity fence for S=4 L=3 common-anchor macros.

Among all 4-state deterministic ternary clocks in which every state is
reachable from the anchor in ≤ L=3 steps, the number of ports (s,d) with
δ(s,d)=0 is at most 9.  Tags for the n-circuit equal n+1, so n ≥ 9 is
impossible in this model at S=4 (needs ≥ 10 anchor-returning ports).

Absolute (no reachability filter): max ports = 12, so the reachability filter
is load-bearing for the n≥9 cut (as it is for S=3 / n≥7).

Companion to verify_s3_port_capacity.py.  THEOREM_S4_PORT_CAPACITY.md shipped
with PORT_CAPACITY_S4.json but no verifier, so the n≥9 row of the scoreboard
was not replayable; this recomputes the census from scratch and checks the
stored artifact against it.  ~4 min (16 777 216 clocks).
"""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "PORT_CAPACITY_S4.json"

S = 4
L = 3
NMAX = 14


def main():
    hist_all = Counter()
    hist_reach = Counter()
    ge = {n: 0 for n in range(3, NMAX + 1)}

    for flat in itertools.product(range(S), repeat=S * 3):
        ap = flat.count(0)
        hist_all[ap] += 1
        reach = {0}
        cur = {0}
        for _ in range(L):
            nxt = {flat[s * 3 + d] for s in cur for d in range(3)}
            cur = nxt - reach
            reach |= nxt
        if len(reach) < S:
            continue
        hist_reach[ap] += 1
        for n in ge:
            if ap >= n + 1:
                ge[n] += 1

    hist = {str(k): v for k, v in sorted(hist_reach.items())}
    rows = [{"n": n, "tags": n + 1, "ge_tags": ge[n]} for n in range(3, NMAX + 1)]
    max_ports = max(hist_reach)

    # check the stored artifact against the recomputed census
    stored = json.loads(OUT.read_text(encoding="utf-8"))
    assert stored["hist"] == hist, f"hist mismatch\n stored {stored['hist']}\n fresh  {hist}"
    assert stored["max_ports"] == max_ports, (
        f"max_ports mismatch: stored {stored['max_ports']} != fresh {max_ports}"
    )
    assert stored["rows"] == rows, "rows mismatch between stored artifact and fresh census"
    print(json.dumps({"hist": hist, "max_ports": max_ports, "rows": rows}, indent=2, sort_keys=True))

    assert max_ports == 9
    assert max(hist_all) == 12, "reachability filter must be load-bearing (unfiltered max 12)"
    assert all(ge[n] == 0 for n in range(9, NMAX + 1))
    print(
        "CERTIFIED: n>=9 impossible at S=4 under L<=3 reachability (max ports 9; "
        "unfiltered max 12)"
    )


if __name__ == "__main__":
    main()

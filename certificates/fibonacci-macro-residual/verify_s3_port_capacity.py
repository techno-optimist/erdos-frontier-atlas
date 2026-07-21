#!/usr/bin/env python3
"""
Port-capacity fence for S=3 L=3 common-anchor macros.

Among all 3-state deterministic ternary clocks in which every state is
reachable from the anchor in ≤ L=3 steps, the number of ports (s,d) with
δ(s,d)=0 is at most 7.  Tags for the n-circuit equal n+1, so n ≥ 7 is
impossible in this model at S=3 (needs ≥ 8 anchor-returning ports).

Absolute (no reachability filter): max ports = 9 (one clock), so the
reachability filter is load-bearing for the n≥7 cut.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "PORT_CAPACITY_S3.json"

S = 3
L = 3


def main():
    hist_all = Counter()
    hist_reach = Counter()
    ge = {}
    for n in range(3, 10):
        ge[n] = 0

    for flat in itertools.product(range(S), repeat=S * 3):
        delta = [list(flat[i * 3 : (i + 1) * 3]) for i in range(S)]
        ap = sum(1 for s in range(S) for d in range(3) if delta[s][d] == 0)
        hist_all[ap] += 1
        reach = {0}
        cur = {0}
        for _ in range(L):
            nxt = {delta[s][d] for s in cur for d in range(3)}
            cur = nxt - reach
            reach |= nxt
        if len(reach) < S:
            continue
        hist_reach[ap] += 1
        for n in range(3, 10):
            if ap >= n + 1:
                ge[n] += 1

    rows = [
        {
            "n": n,
            "tags": n + 1,
            "clocks": S ** (S * 3),
            "reachable": sum(hist_reach.values()),
            "ge_tags": ge[n],
        }
        for n in range(3, 10)
    ]
    out = {
        "schema": "lead.port_capacity_s3.v1",
        "L": L,
        "S": S,
        "rows": rows,
        "anchor_port_hist_all_clocks": {str(k): v for k, v in sorted(hist_all.items())},
        "anchor_port_hist_reachable": {
            str(k): v for k, v in sorted(hist_reach.items())
        },
        "max_anchor_ports_all": max(hist_all) if hist_all else 0,
        "max_anchor_ports_reachable": max(hist_reach) if hist_reach else 0,
        "status": "N_GE_7_S3_REACHABLE_PORT_CAPACITY_NO_GO",
        "claim_boundary": (
            "Under all-states L<=3-reachable filter, max anchor ports is 7, "
            "so common-anchor macros needing n+1>=8 tags (n>=7) are impossible "
            "at S=3. Without reachability filter max is 9."
        ),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    assert out["max_anchor_ports_reachable"] == 7
    assert ge[7] == 0 and ge[8] == 0 and ge[9] == 0
    print("CERTIFIED: n>=7 impossible at S=3 under L<=3 reachability (max ports 7)")


if __name__ == "__main__":
    main()

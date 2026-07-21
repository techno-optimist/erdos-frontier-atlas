#!/usr/bin/env python3
"""Complete n=5 L=3 S=3 census: all 19683 clocks, LP only until hit then integer."""

from __future__ import annotations

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

import search_n5_l3 as N

HERE = Path(__file__).resolve().parent


def main():
    S = 3
    t0 = time.time()
    stats = Counter()
    legal = {d for d, _ in N.digit_patterns()}
    dig_carry = {d: c for d, c in N.digit_patterns()}
    print("digit patterns", len(legal), flush=True)
    found = None
    lp_hits = []

    total_clocks = S ** (S * 3)
    for flat in itertools.product(range(S), repeat=S * 3):
        stats["clocks"] += 1
        delta = [list(flat[i * 3 : (i + 1) * 3]) for i in range(S)]
        reach = {0}
        cur = {0}
        for _ in range(N.L):
            nxt = {delta[s][d] for s in cur for d in range(3)}
            cur = nxt - reach
            reach |= nxt
        if len(reach) < S:
            continue
        stats["reachable"] += 1
        ap = [(s, d) for s in range(S) for d in range(3) if delta[s][d] == 0]
        if len(ap) < N.TAGS:
            continue
        stats["ge_tags"] += 1
        for assignment in itertools.permutations(ap, N.TAGS):
            digs = tuple(assignment[t][1] for t in range(N.TAGS))
            if digs not in legal:
                continue
            ports = {t: assignment[t] for t in range(N.TAGS)}
            carries = dig_carry[digs]
            ok = True
            for i, (_, origin, _) in enumerate(N.COLUMNS):
                u, v, w = origin
                d0, d1, d2 = ports[u][1], ports[v][1], ports[w][1]
                if N.carry_step(d0, d1, d2, carries[i]) != 0:
                    ok = False
                    break
            if not ok:
                continue
            stats["outward"] += 1
            feat_lists, weights = [], []
            for i, (weight, origin, name) in enumerate(N.COLUMNS):
                feats = N.legal_l3_feats(delta, ports, origin, carries[i], S)
                if not feats:
                    ok = False
                    break
                feat_lists.append(feats)
                weights.append(weight)
            if not ok:
                continue
            stats["routable"] += 1
            if N.lp_ok(feat_lists, weights, 2 * S * 3):
                stats["lp"] += 1
                hit = {
                    "delta": delta,
                    "ports": {str(t): list(ports[t]) for t in range(N.TAGS)},
                    "digs": list(digs),
                    "carries": list(carries),
                }
                lp_hits.append(hit)
                print("LP_HIT", hit, flush=True)
                r = N.integer_recover(delta, ports, carries, S)
                print("integer", r["status"], flush=True)
                if r["status"] == "FOUND_INTEGER":
                    found = {**hit, "selected": r["selected"]}
                    break
        if found:
            break
        if stats["clocks"] % 2000 == 0:
            print(
                f"progress {stats['clocks']}/{total_clocks} {dict(stats)} "
                f"t={time.time()-t0:.0f}s",
                flush=True,
            )

    out = {
        "schema": "lead.n5_l3_s3_complete.v1",
        "status": "FOUND" if found else "NO_N5_L3_S3",
        "elapsed_sec": round(time.time() - t0, 3),
        "stats": dict(stats),
        "lp_hit_count": len(lp_hits),
        "lp_hits": lp_hits[:10],
        "witness": found,
        "claim_boundary": (
            "Exhaustive n=5 L=3 on all 3-state clocks with all states L<=3 "
            "reachable; LP then integer. 0 LP => no such macro at S=3."
        ),
    }
    path = HERE / "N5_L3_S3_COMPLETE.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if found:
        (HERE / "N5_L3_WITNESS.json").write_text(
            json.dumps(found, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps({k: v for k, v in out.items() if k not in ("witness", "lp_hits")}, indent=2))


if __name__ == "__main__":
    main()

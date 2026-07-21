#!/usr/bin/env python3
"""
Pure-Python exhaustive n=6 L=3 S=3 common-anchor routability census.

TAGS=7 on a 3-state clock (9 ports): need ≥7 ports returning to anchor.
Obstruction expected at ge_tags / outward / routability — stdlib only.
"""

from __future__ import annotations

import itertools
import json
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "N6_L3_S3_COMPLETE.json"

N = 6
L = 3
S = 3
TAGS = N + 1


def fibs(count):
    f = [1, 1]
    while len(f) < count:
        f.append(f[-1] + f[-2])
    return f


def columns():
    f = fibs(N + 1)
    out = [(1, (1, 0, N), "P0"), (1, (0, 1, N), "Q0")]
    for j in range(1, N - 1):
        out.append((f[j], (j + 1, j, j - 1), f"P{j}"))
        out.append((f[j], (j, j + 1, N), f"Q{j}"))
    out.append((f[N - 1], (N - 1, N - 1, N - 2), f"P{N-1}"))
    out.append((f[N], (N, N, N - 1), f"P{N}"))
    return out


COLUMNS = columns()


def carry_step(a, b, c, cin):
    value = a + c - 2 * b + cin
    if value % 3:
        return None
    cout = value // 3
    return cout if cout in (-1, 0, 1) else None


def digit_patterns():
    out = []
    for digs in itertools.product(range(3), repeat=TAGS):
        carries = []
        ok = True
        for weight, origin, name in COLUMNS:
            u, v, w = origin
            diff = digs[u] + digs[w] - 2 * digs[v]
            if abs(diff) > 1:
                ok = False
                break
            carries.append(-diff)
        if ok:
            out.append((digs, tuple(carries)))
    return out


def has_legal_l3_route(delta, ports, origin, tc):
    u, v, w = origin
    target = (ports[u][0], ports[v][0], ports[w][0])
    for digs3 in itertools.product(itertools.product(range(3), repeat=3), repeat=L):
        carry = 0
        states = (0, 0, 0)
        ok = True
        for step in range(L):
            a, b, c = digs3[step]
            cout = carry_step(a, b, c, carry)
            if cout is None:
                ok = False
                break
            states = (
                delta[states[0]][a],
                delta[states[1]][b],
                delta[states[2]][c],
            )
            carry = cout
        if ok and carry == tc and states == target:
            return True
    return False


def assign_ports_for_digs(ap, digs):
    """Assign distinct anchor ports matching required digits. Yields port maps."""
    by_d = {0: [], 1: [], 2: []}
    for p in ap:
        by_d[p[1]].append(p)
    # need multiset of digs
    need = Counter(digs)
    if any(need[d] > len(by_d[d]) for d in need):
        return
    # ordered unique assignment for tags 0..TAGS-1
    used = set()

    def rec(t, ports):
        if t == TAGS:
            yield dict(ports)
            return
        d = digs[t]
        for p in by_d[d]:
            if p in used:
                continue
            used.add(p)
            ports[t] = p
            yield from rec(t + 1, ports)
            used.remove(p)

    yield from rec(0, {})


def main():
    t0 = time.time()
    stats = Counter()
    legal = digit_patterns()
    print("n=6 columns", len(COLUMNS), "mass", sum(w for w, _, _ in COLUMNS))
    print("digit patterns", len(legal), flush=True)
    total = S ** (S * 3)

    for flat in itertools.product(range(S), repeat=S * 3):
        stats["clocks"] += 1
        delta = [list(flat[i * 3 : (i + 1) * 3]) for i in range(S)]
        reach = {0}
        cur = {0}
        for _ in range(L):
            nxt = {delta[s][d] for s in cur for d in range(3)}
            cur = nxt - reach
            reach |= nxt
        if len(reach) < S:
            continue
        stats["reachable"] += 1
        ap = [(s, d) for s in range(S) for d in range(3) if delta[s][d] == 0]
        if len(ap) < TAGS:
            continue
        stats["ge_tags"] += 1
        for digs, carries in legal:
            for ports in assign_ports_for_digs(ap, digs):
                ok = True
                for i, (_, origin, _) in enumerate(COLUMNS):
                    u, v, w = origin
                    if (
                        carry_step(
                            ports[u][1], ports[v][1], ports[w][1], carries[i]
                        )
                        != 0
                    ):
                        ok = False
                        break
                if not ok:
                    continue
                stats["outward"] += 1
                for i, (_, origin, _) in enumerate(COLUMNS):
                    if not has_legal_l3_route(delta, ports, origin, carries[i]):
                        ok = False
                        break
                if not ok:
                    continue
                stats["routable"] += 1
                print("UNEXPECTED_ROUTABLE", delta, digs, flush=True)
                break
            if stats["routable"]:
                break
        if stats["routable"]:
            break
        if stats["clocks"] % 2000 == 0:
            print(
                f"progress {stats['clocks']}/{total} {dict(stats)} "
                f"t={time.time()-t0:.0f}s",
                flush=True,
            )

    status = "NO_N6_L3_S3" if stats["routable"] == 0 else "FOUND_ROUTABLE"
    out = {
        "schema": "lead.n6_l3_s3_complete.v1",
        "status": status,
        "elapsed_sec": round(time.time() - t0, 3),
        "stats": dict(stats),
        "n_columns": len(COLUMNS),
        "digit_patterns": len(legal),
        "claim_boundary": (
            "Exhaustive n=6 L=3 on all 3-state clocks (L<=3-reachable). "
            "Pure-Python routability; 0 routable => no common-anchor split "
            "macro at S=3."
        ),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    if status != "NO_N6_L3_S3":
        raise SystemExit(1)
    print("CERTIFIED: no n=6 L=3 S=3 common-anchor routable assignment")


if __name__ == "__main__":
    main()

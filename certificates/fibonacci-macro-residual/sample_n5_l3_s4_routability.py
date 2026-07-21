#!/usr/bin/env python3
"""
Smarter n=5 L=3 S=4 sample: digit-driven port assignment (not full P(ap,6)).

Scans random + structured 4-state clocks. Not exhaustive (4^12 clocks).
Stdlib only — routability obstruction first.
"""

from __future__ import annotations

import itertools
import json
import random
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "N5_L3_S4_SAMPLE.json"

N = 5
L = 3
S = 4
TAGS = N + 1
SEED = 20260720
RANDOM_CLOCKS = 8000


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


def has_legal_l3_route(delta, ports, origin, tc, S_local):
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


def assign_ports_for_digs(ap, digs, max_assign=50):
    by_d = {0: [], 1: [], 2: []}
    for p in ap:
        by_d[p[1]].append(p)
    need = Counter(digs)
    if any(need[d] > len(by_d[d]) for d in need):
        return
    used = set()
    count = [0]

    def rec(t, ports):
        if count[0] >= max_assign:
            return
        if t == TAGS:
            count[0] += 1
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
    random.seed(SEED)
    t0 = time.time()
    stats = Counter()
    legal = digit_patterns()
    print("digit patterns", len(legal), flush=True)

    samples = []
    for _ in range(RANDOM_CLOCKS):
        samples.append(tuple(random.randrange(S) for _ in range(S * 3)))
    # structured: fill first 6 slots systematically
    for base in itertools.product(range(S), repeat=6):
        flat = list(base) + [0] * (S * 3 - 6)
        samples.append(tuple(flat))
    # lift-ish: embed 3-state patterns in 4 states
    for flat3 in itertools.islice(itertools.product(range(3), repeat=9), 0, 500):
        # pad to 4 states with transitions into 0..2
        row3 = [list(flat3[i * 3 : (i + 1) * 3]) for i in range(3)]
        row4 = row3 + [[0, 1, 2]]  # state 3 -> cycle
        samples.append(tuple(x for row in row4 for x in row))

    samples = list(dict.fromkeys(samples))
    print("sample clocks", len(samples), flush=True)
    found = None

    for flat in samples:
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
            for ports in assign_ports_for_digs(ap, digs, max_assign=30):
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
                    if not has_legal_l3_route(delta, ports, origin, carries[i], S):
                        ok = False
                        break
                if not ok:
                    continue
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
        if stats["clocks"] % 1000 == 0:
            print(
                f"progress {dict(stats)} t={time.time()-t0:.0f}s",
                flush=True,
            )

    out = {
        "schema": "lead.n5_l3_s4_sample.v1",
        "status": "FOUND_ROUTABLE" if found else "NO_ROUTABLE_IN_SAMPLE",
        "elapsed_sec": round(time.time() - t0, 3),
        "stats": dict(stats),
        "sample_size": len(samples),
        "seed": SEED,
        "witness": found,
        "claim_boundary": (
            "Digit-driven sample of S=4 clocks (random+structured). "
            "Not exhaustive. Exhaustive S=3 remains the sealed no-go."
        ),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "witness"}, indent=2))
    if found:
        print("WITNESS", json.dumps(found, indent=2))


if __name__ == "__main__":
    main()

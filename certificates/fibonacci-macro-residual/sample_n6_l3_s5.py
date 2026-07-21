#!/usr/bin/env python3
"""
n=6 L=3 S=5 sample: random + structured clocks with ≥7 anchor ports.

5^15 is huge; this is a fence sample, not exhaustive.
"""

from __future__ import annotations

import itertools
import json
import random
import time
from collections import Counter
from pathlib import Path

import macro_engine as M

HERE = Path(__file__).resolve().parent
OUT = HERE / "N6_L3_S5_SAMPLE.json"

N, L, S = 6, 3, 5
TAGS = N + 1
COLS = M.columns(N)
SEED = 20260721
RANDOM = 20000


def main():
    random.seed(SEED)
    t0 = time.time()
    stats = Counter()
    legal = M.digit_patterns(COLS, TAGS)
    print("digits", len(legal), flush=True)

    samples = []
    for _ in range(RANDOM):
        samples.append(tuple(random.randrange(S) for _ in range(S * 3)))
    # embed 4-state patterns padded with identity-ish state
    for flat4 in itertools.islice(itertools.product(range(4), repeat=12), 0, 3000):
        row = [list(flat4[i * 3 : (i + 1) * 3]) for i in range(4)]
        row.append([0, 1, 2])  # state 4
        samples.append(tuple(x for r in row for x in r))
    samples = list(dict.fromkeys(samples))
    print("samples", len(samples), flush=True)

    found_routable = None
    for flat in samples:
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
                    found_routable = {
                        "delta": delta,
                        "ports": {str(t): list(ports[t]) for t in range(TAGS)},
                        "digs": list(digs),
                        "carries": list(carries),
                    }
                    print("ROUTABLE", found_routable, flush=True)
                    break
            if found_routable:
                break
        if found_routable:
            break
        if stats["clocks"] % 2000 == 0:
            print(dict(stats), f"t={time.time()-t0:.0f}s", flush=True)

    # try LP on found
    lp = None
    if found_routable:
        try:
            import highspy
            from collections import Counter as C

            def feat(role_ports):
                cnt = [C(), C(), C()]
                for role in range(3):
                    for p in role_ports[role]:
                        cnt[role][p] += 1
                keys = [(s, d) for s in range(S) for d in range(3)]
                out = []
                for k in keys:
                    out.append(cnt[0][k] - cnt[1][k])
                for k in keys:
                    out.append(cnt[2][k] - cnt[1][k])
                return tuple(out)

            delta = found_routable["delta"]
            ports = {int(k): tuple(v) for k, v in found_routable["ports"].items()}
            carries = found_routable["carries"]
            col_data = []
            for i, (weight, origin, name) in enumerate(COLS):
                u, v, w = origin
                target = (ports[u][0], ports[v][0], ports[w][0])
                uniq = {}
                for digs3 in itertools.product(
                    itertools.product(range(3), repeat=3), repeat=L
                ):
                    carry = 0
                    states = (0, 0, 0)
                    role_ports = [[], [], []]
                    ok = True
                    for step in range(L):
                        a, b, c = digs3[step]
                        cout = M.carry_step(a, b, c, carry)
                        if cout is None:
                            ok = False
                            break
                        for role, d in enumerate((a, b, c)):
                            role_ports[role].append((states[role], d))
                        states = (
                            delta[states[0]][a],
                            delta[states[1]][b],
                            delta[states[2]][c],
                        )
                        carry = cout
                    if ok and carry == carries[i] and states == target:
                        uniq.setdefault(feat(role_ports), digs3)
                col_data.append((weight, name, list(uniq.items())))
            dim = 2 * S * 3
            nvars = sum(len(items) for _, _, items in col_data)
            h = highspy.Highs()
            h.setOptionValue("output_flag", False)
            h.addVars(nvars, [0.0] * nvars, [1e9] * nvars)
            off = 0
            for weight, name, items in col_data:
                k = len(items)
                h.addRow(
                    float(weight),
                    float(weight),
                    k,
                    list(range(off, off + k)),
                    [1.0] * k,
                )
                off += k
            for j in range(dim):
                idx, vals = [], []
                off = 0
                for weight, name, items in col_data:
                    for i, (f, digs3) in enumerate(items):
                        if f[j]:
                            idx.append(off + i)
                            vals.append(float(f[j]))
                    off += len(items)
                if idx:
                    h.addRow(0.0, 0.0, len(idx), idx, vals)
            h.run()
            lp = int(h.getModelStatus()) == 7
            print("LP", lp, flush=True)
        except Exception as e:
            lp = f"error:{e}"

    out = {
        "schema": "lead.n6_l3_s5_sample.v1",
        "status": "FOUND_ROUTABLE" if found_routable else "NO_ROUTABLE_IN_SAMPLE",
        "elapsed_sec": round(time.time() - t0, 3),
        "stats": dict(stats),
        "sample_size": len(samples),
        "seed": SEED,
        "lp_on_first_routable": lp,
        "witness": found_routable,
        "claim_boundary": "Sample only; not exhaustive for S=5.",
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "witness"}, indent=2))


if __name__ == "__main__":
    main()

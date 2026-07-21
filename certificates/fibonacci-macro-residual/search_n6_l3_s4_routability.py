#!/usr/bin/env python3
"""
n=6 L=3 S=4 routability hunt (digit-driven).

4^12 clocks; needs ≥7 anchor ports. Checkpointed. On first routable,
attempts LP then MIP integer recovery (highspy).
"""

from __future__ import annotations

import itertools
import json
import time
from collections import Counter
from pathlib import Path

import macro_engine as M

HERE = Path(__file__).resolve().parent
OUT = HERE / "N6_L3_S4_SEARCH.json"
PROGRESS = HERE / "N6_L3_S4_PROGRESS.json"
WIT = HERE / "N6_L3_S4_WITNESS.json"

N, L, S = 6, 3, 4
TAGS = N + 1
COLS = M.columns(N)
CHECKPOINT = 100_000


def feat_role_ports(role_ports, S_local):
    cnt = [Counter(), Counter(), Counter()]
    for role in range(3):
        for p in role_ports[role]:
            cnt[role][p] += 1
    keys = [(s, d) for s in range(S_local) for d in range(3)]
    out = []
    for k in keys:
        out.append(cnt[0][k] - cnt[1][k])
    for k in keys:
        out.append(cnt[2][k] - cnt[1][k])
    return tuple(out)


def enumerate_routes(delta, ports, origin, tc):
    u, v, w = origin
    target = (ports[u][0], ports[v][0], ports[w][0])
    uniq = {}
    for digs3 in itertools.product(itertools.product(range(3), repeat=3), repeat=L):
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
        if not ok or carry != tc or states != target:
            continue
        feat = feat_role_ports(role_ports, S)
        uniq.setdefault(feat, digs3)
    return list(uniq.items())


def lp_ok(col_data):
    import highspy

    dim = 2 * S * 3
    nvars = sum(len(items) for _, _, items in col_data)
    if nvars == 0:
        return False
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.addVars(nvars, [0.0] * nvars, [1e9] * nvars)
    h.changeColsCost(nvars, list(range(nvars)), [0.0] * nvars)
    off = 0
    for weight, name, items in col_data:
        k = len(items)
        h.addRow(float(weight), float(weight), k, list(range(off, off + k)), [1.0] * k)
        off += k
    for j in range(dim):
        idx, vals = [], []
        off = 0
        for weight, name, items in col_data:
            for i, (feat, digs3) in enumerate(items):
                if feat[j]:
                    idx.append(off + i)
                    vals.append(float(feat[j]))
            off += len(items)
        if idx:
            h.addRow(0.0, 0.0, len(idx), idx, vals)
    h.run()
    return int(h.getModelStatus()) == 7


def mip_recover(col_data, time_limit=90.0):
    import highspy

    dim = 2 * S * 3
    nvars = sum(len(items) for _, _, items in col_data)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", time_limit)
    h.addVars(nvars, [0.0] * nvars, [1e6] * nvars)
    h.changeColsIntegrality(
        nvars, list(range(nvars)), [highspy.HighsVarType.kInteger] * nvars
    )
    h.changeColsCost(nvars, list(range(nvars)), [0.0] * nvars)
    off = 0
    ranges = []
    for weight, name, items in col_data:
        idxs = list(range(off, off + len(items)))
        h.addRow(float(weight), float(weight), len(idxs), idxs, [1.0] * len(idxs))
        ranges.append((weight, name, items, idxs))
        off += len(items)
    for j in range(dim):
        idx, vals = [], []
        for weight, name, items, idxs in ranges:
            for oi, (feat, digs3) in enumerate(items):
                if feat[j]:
                    idx.append(idxs[oi])
                    vals.append(float(feat[j]))
        if idx:
            h.addRow(0.0, 0.0, len(idx), idx, vals)
    h.run()
    st = int(h.getModelStatus())
    if st != 7:
        return {"status": "MIP_INFEAS", "model_status": st}
    sol = h.getSolution().col_value
    selected = {}
    for weight, name, items, idxs in ranges:
        picks = []
        for oi, (feat, digs3) in enumerate(items):
            mult = int(round(sol[idxs[oi]]))
            if mult:
                picks.append({"mult": mult, "steps": [list(t) for t in digs3]})
        selected[name] = picks
    return {"status": "FOUND_INTEGER", "selected": selected}


def main():
    t0 = time.time()
    stats = Counter()
    legal = M.digit_patterns(COLS, TAGS)
    total = S ** (S * 3)
    print(
        f"n=6 L=3 S=4 tags={TAGS} digits={len(legal)} total={total}",
        flush=True,
    )
    start = 0
    if PROGRESS.exists():
        prev = json.loads(PROGRESS.read_text(encoding="utf-8"))
        start = int(prev.get("next_idx", 0))
        stats.update(prev.get("stats", {}))
        print("resume", start, dict(stats), flush=True)

    found = None
    first_routable = None
    for idx, flat in enumerate(itertools.product(range(S), repeat=S * 3)):
        if idx < start:
            continue
        stats["clocks"] = idx + 1
        delta = [list(flat[i * 3 : (i + 1) * 3]) for i in range(S)]
        if M.clock_reachable(delta, S, L):
            stats["reachable"] += 1
            ap = M.anchor_ports(delta, S)
            if len(ap) >= TAGS:
                stats["ge_tags"] += 1
                for digs, carries in legal:
                    for ports in M.assign_ports_for_digs(ap, digs, TAGS):
                        if not M.outward_ok(ports, carries, COLS):
                            continue
                        stats["outward"] += 1
                        if not M.all_columns_routable(
                            delta, ports, carries, COLS, L
                        ):
                            continue
                        stats["routable"] += 1
                        seed = {
                            "delta": delta,
                            "ports": {
                                str(t): list(ports[t]) for t in range(TAGS)
                            },
                            "digs": list(digs),
                            "carries": list(carries),
                            "clock_idx": idx,
                        }
                        if first_routable is None:
                            first_routable = seed
                            print("FIRST_ROUTABLE", idx, flush=True)
                        col_data = []
                        ok = True
                        for i, (weight, origin, name) in enumerate(COLS):
                            items = enumerate_routes(
                                delta, ports, origin, carries[i]
                            )
                            if not items:
                                ok = False
                                break
                            col_data.append((weight, name, items))
                        if not ok:
                            continue
                        stats["route_enum"] += 1
                        try:
                            if not lp_ok(col_data):
                                stats["lp_infeas"] += 1
                                continue
                        except ImportError:
                            print("no highspy; stop at routable", flush=True)
                            found = {**seed, "status": "ROUTABLE_ONLY"}
                            break
                        stats["lp"] += 1
                        print(
                            f"LP_HIT idx={idx} routes={[len(c[2]) for c in col_data]}",
                            flush=True,
                        )
                        r = mip_recover(col_data)
                        print("  mip", r["status"], flush=True)
                        if r["status"] == "FOUND_INTEGER":
                            found = {**seed, "selected": r["selected"]}
                            break
                        stats["mip_infeas"] += 1
                    if found:
                        break
        if found:
            break
        # soft stop: if we have scanned a lot after first routable with only MIP fails
        if (idx + 1) % CHECKPOINT == 0:
            snap = {
                "next_idx": idx + 1,
                "stats": dict(stats),
                "elapsed_sec": round(time.time() - t0, 3),
                "first_routable": first_routable,
            }
            PROGRESS.write_text(
                json.dumps(snap, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            print(
                f"progress {idx+1}/{total} {dict(stats)} t={time.time()-t0:.0f}s",
                flush=True,
            )

    status = (
        "FOUND_INTEGER"
        if found and found.get("selected")
        else (
            "FOUND_ROUTABLE"
            if found or first_routable
            else "NO_ROUTABLE_IN_SCAN"
        )
    )
    if found and found.get("selected"):
        WIT.write_text(
            json.dumps(found, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    elif first_routable:
        (HERE / "N6_L3_S4_FIRST_ROUTABLE.json").write_text(
            json.dumps(first_routable, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    res = {
        "schema": "lead.n6_l3_s4_search.v1",
        "status": status,
        "elapsed_sec": round(time.time() - t0, 3),
        "stats": dict(stats),
        "digit_patterns": len(legal),
        "total_clocks": total,
        "first_routable_idx": (
            first_routable["clock_idx"] if first_routable else None
        ),
        "claim_boundary": (
            "n=6 L=3 S=4 common-anchor hunt. FOUND_INTEGER is a witness; "
            "FOUND_ROUTABLE without integer is partial."
        ),
    }
    OUT.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()

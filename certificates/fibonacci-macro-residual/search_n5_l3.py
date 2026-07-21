#!/usr/bin/env python3
"""
Search n=5 common-anchor L=3 split-weight macros.

n=5 columns (Fib weights): total mass 27, 10 columns, 6 tags.
"""

from __future__ import annotations

import itertools
import json
import time
from collections import Counter
from pathlib import Path

import highspy

HERE = Path(__file__).resolve().parent
PROGRESS = HERE / "n5_l3_progress.json"
RESULT = HERE / "N5_L3_SEARCH_RESULT.json"
WITNESS = HERE / "N5_L3_WITNESS.json"

L = 3
N = 5
TAGS = N + 1


def fibs(count):
    f = [1, 1]
    while len(f) < count:
        f.append(f[-1] + f[-2])
    return f


def columns():
    n = N
    f = fibs(n + 1)
    out = [(1, (1, 0, n), "P0"), (1, (0, 1, n), "Q0")]
    for j in range(1, n - 1):
        out.append((f[j], (j + 1, j, j - 1), f"P{j}"))
        out.append((f[j], (j, j + 1, n), f"Q{j}"))
    out.append((f[n - 1], (n - 1, n - 1, n - 2), f"P{n-1}"))
    out.append((f[n], (n, n, n - 1), f"P{n}"))
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


def feat_role_ports(role_ports, S):
    cnt = [Counter(), Counter(), Counter()]
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


def legal_l3_feats(delta, ports, origin, tc, S):
    u, v, w = origin
    target = (ports[u][0], ports[v][0], ports[w][0])
    feats = []
    for digs3 in itertools.product(itertools.product(range(3), repeat=3), repeat=L):
        carry = 0
        states = (0, 0, 0)
        role_ports = [[], [], []]
        ok = True
        for step in range(L):
            a, b, c = digs3[step]
            cout = carry_step(a, b, c, carry)
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
        feats.append(feat_role_ports(role_ports, S))
    return feats


def lp_ok(feat_lists, weights, dim):
    uniques = [list(dict.fromkeys(f)) for f in feat_lists]
    nvars = sum(len(u) for u in uniques)
    if nvars == 0:
        return False
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.addVars(nvars, [0.0] * nvars, [1e9] * nvars)
    h.changeColsCost(nvars, list(range(nvars)), [0.0] * nvars)
    off = 0
    for u, w in zip(uniques, weights):
        k = len(u)
        h.addRow(float(w), float(w), k, list(range(off, off + k)), [1.0] * k)
        off += k
    for j in range(dim):
        idx, vals = [], []
        off = 0
        for u in uniques:
            for i, f in enumerate(u):
                if f[j]:
                    idx.append(off + i)
                    vals.append(float(f[j]))
            off += len(u)
        if idx:
            h.addRow(0.0, 0.0, len(idx), idx, vals)
    h.run()
    return int(h.getModelStatus()) == 7


def integer_recover(delta, ports, carries, S, time_limit=300.0):
    col_data = []
    for i, (weight, origin, name) in enumerate(COLUMNS):
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
                cout = carry_step(a, b, c, carry)
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
            if not ok or carry != carries[i] or states != target:
                continue
            feat = feat_role_ports(role_ports, S)
            uniq.setdefault(feat, digs3)
        if not uniq:
            return {"status": "NO_ROUTES", "column": name}
        col_data.append((weight, name, list(uniq.items())))

    dim = 2 * S * 3
    nvars = sum(len(c[2]) for c in col_data)
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
                picks.append(
                    {"mult": mult, "steps": [list(t) for t in digs3]}
                )
        selected[name] = picks
    return {"status": "FOUND_INTEGER", "selected": selected}


def try_extend_n4():
    """Add tag 5 on the sealed n=4 clock if a free anchor port exists."""
    wit = json.loads((HERE / "N4_L3_WITNESS.json").read_text(encoding="utf-8"))
    delta = wit["delta"]
    S = 3
    base = {int(k): tuple(v) for k, v in wit["ports"].items()}
    used = set(base.values())
    free = [
        (s, d)
        for s in range(S)
        for d in range(3)
        if delta[s][d] == 0 and (s, d) not in used
    ]
    print("n4 free ports", free, flush=True)
    for p5 in free:
        ports = dict(base)
        ports[5] = p5
        carries = []
        ok = True
        for weight, origin, name in COLUMNS:
            u, v, w = origin
            digits = (ports[u][1], ports[v][1], ports[w][1])
            states = (ports[u][0], ports[v][0], ports[w][0])
            if any(delta[st][dg] != 0 for st, dg in zip(states, digits)):
                ok = False
                break
            diff = digits[0] + digits[2] - 2 * digits[1]
            if abs(diff) > 1:
                ok = False
                break
            cin = -diff
            if carry_step(*digits, cin) != 0:
                ok = False
                break
            carries.append(cin)
        if not ok:
            continue
        feat_lists, weights = [], []
        for i, (weight, origin, name) in enumerate(COLUMNS):
            feats = legal_l3_feats(delta, ports, origin, carries[i], S)
            print(f"  p5={p5} {name} routes={len(feats)}", flush=True)
            if not feats:
                ok = False
                break
            feat_lists.append(feats)
            weights.append(weight)
        if not ok:
            continue
        if lp_ok(feat_lists, weights, 2 * S * 3):
            print("LP_HIT extend", p5, flush=True)
            r = integer_recover(delta, ports, carries, S)
            print(" integer", r["status"], flush=True)
            if r["status"] == "FOUND_INTEGER":
                return {
                    "status": "FOUND",
                    "mode": "extend_n4",
                    "delta": delta,
                    "ports": {str(t): list(ports[t]) for t in range(TAGS)},
                    "carries": carries,
                    "selected": r["selected"],
                }
    return {"status": "NO_EXTEND"}


def search_S(S, time_budget=3600.0):
    t0 = time.time()
    stats = Counter()
    legal = {d for d, _ in digit_patterns()}
    dig_carry = {d: c for d, c in digit_patterns()}
    print(f"n=5 digit patterns: {len(legal)}", flush=True)
    found = None
    lp_hits = 0

    for flat in itertools.product(range(S), repeat=S * 3):
        if time.time() - t0 > time_budget:
            stats["timeout"] = 1
            break
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
        for assignment in itertools.permutations(ap, TAGS):
            digs = tuple(assignment[t][1] for t in range(TAGS))
            if digs not in legal:
                continue
            ports = {t: assignment[t] for t in range(TAGS)}
            carries = dig_carry[digs]
            ok = True
            for i, (_, origin, _) in enumerate(COLUMNS):
                u, v, w = origin
                d0, d1, d2 = ports[u][1], ports[v][1], ports[w][1]
                if carry_step(d0, d1, d2, carries[i]) != 0:
                    ok = False
                    break
            if not ok:
                continue
            stats["outward"] += 1
            feat_lists, weights = [], []
            for i, (weight, origin, name) in enumerate(COLUMNS):
                feats = legal_l3_feats(delta, ports, origin, carries[i], S)
                if not feats:
                    ok = False
                    break
                feat_lists.append(feats)
                weights.append(weight)
            if not ok:
                continue
            stats["routable"] += 1
            if lp_ok(feat_lists, weights, 2 * S * 3):
                lp_hits += 1
                stats["lp"] += 1
                print(
                    "LP_HIT",
                    {"delta": delta, "ports": ports, "digs": digs},
                    flush=True,
                )
                r = integer_recover(delta, ports, carries, S)
                print(" integer", r["status"], flush=True)
                if r["status"] == "FOUND_INTEGER":
                    found = {
                        "S": S,
                        "delta": delta,
                        "ports": {str(t): list(ports[t]) for t in range(TAGS)},
                        "digs": list(digs),
                        "carries": list(carries),
                        "selected": r["selected"],
                    }
                    break
        if found:
            break
        if stats["clocks"] % 100 == 0:
            PROGRESS.write_text(
                json.dumps(
                    {
                        "S": S,
                        "stats": dict(stats),
                        "lp_hits": lp_hits,
                        "elapsed": round(time.time() - t0, 1),
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            print(f"S={S} {dict(stats)} t={time.time()-t0:.0f}s", flush=True)

    return {
        "S": S,
        "stats": dict(stats),
        "lp_hits": lp_hits,
        "found": found,
        "elapsed": round(time.time() - t0, 3),
    }


def main():
    t0 = time.time()
    print("COLUMNS", COLUMNS, flush=True)
    rows = []
    found = None

    print("=== extend n=4 ===", flush=True)
    ext = try_extend_n4()
    rows.append(ext)
    if ext.get("status") == "FOUND":
        found = ext

    if not found:
        print("=== S=3 ===", flush=True)
        r3 = search_S(3, time_budget=3600.0)
        rows.append(r3)
        if r3.get("found"):
            found = r3["found"]

    if not found:
        print("=== S=4 timeboxed ===", flush=True)
        r4 = search_S(4, time_budget=2400.0)
        rows.append(r4)
        if r4.get("found"):
            found = r4["found"]

    out = {
        "schema": "lead.n5_l3_search.v1",
        "status": "FOUND_N5_L3" if found else "NO_N5_L3_IN_SEARCH",
        "elapsed_sec": round(time.time() - t0, 3),
        "columns": [
            {"w": w, "origin": list(o), "name": n} for w, o, n in COLUMNS
        ],
        "rows": [
            {k: v for k, v in r.items() if k not in ("selected", "found")}
            for r in rows
        ],
        "witness": found,
    }
    RESULT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if found:
        WITNESS.write_text(
            json.dumps(found, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "witness")}, indent=2))


if __name__ == "__main__":
    main()

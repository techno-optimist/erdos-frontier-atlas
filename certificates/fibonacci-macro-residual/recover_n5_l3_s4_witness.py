#!/usr/bin/env python3
"""
Recover integer Parikh-balanced multi-route witness from the n=5 L=3 S=4
routable seed in N5_L3_S4_COMPLETE.json.

Uses highspy MIP if available; else pure-Python small-branch enumeration.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path

# `python3 -I` (isolated mode) implies -P, which drops this script's own directory from
# sys.path, so the sibling import below fails. Re-add it explicitly: that keeps the -I
# hermeticity the replay instructions rely on (no user site-packages) AND makes the
# documented one-liner actually run for a stranger.
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

import macro_engine as M

HERE = Path(__file__).resolve().parent
SEED = HERE / "N5_L3_S4_COMPLETE.json"
OUT = HERE / "N5_L3_S4_WITNESS.json"
RESULT = HERE / "N5_L3_S4_WITNESS_RESULT.json"

N, L, S = 5, 3, 4
TAGS = N + 1
COLS = M.columns(N)


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


def enumerate_routes(delta, ports, origin, tc, S_local):
    """All L-step digit triples with legal carries ending at target."""
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
        feat = feat_role_ports(role_ports, S_local)
        uniq.setdefault(feat, digs3)
    return list(uniq.items())  # (feat, digs3)


def mip_recover(col_data, S_local, time_limit=120.0):
    import highspy

    dim = 2 * S_local * 3
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


def verify_selected(delta, ports, carries, selected, S_local):
    """Independent exact checks mirroring n=3/n=4 verifiers."""
    # rebuild edges from selected routes
    # weight per column from COLS
    weight_by = {name: w for w, origin, name in COLS}
    # Parikh balance: for each role pair, weighted port multiset equality
    role_parikh = [Counter(), Counter(), Counter()]  # for roles 0,1,2 across all weighted steps? 
    # Actually global: sum over columns of mult * role_port counts equal between roles
    cnt = [Counter(), Counter(), Counter()]
    for i, (weight, origin, name) in enumerate(COLS):
        picks = selected.get(name, [])
        total_mult = sum(p["mult"] for p in picks)
        if total_mult != weight:
            return False, f"weight mismatch {name}: {total_mult}!={weight}"
        u, v, w = origin
        target = (ports[u][0], ports[v][0], ports[w][0])
        tc = carries[i]
        for pick in picks:
            digs3 = [tuple(s) for s in pick["steps"]]
            if len(digs3) != L:
                return False, f"bad length {name}"
            carry = 0
            states = (0, 0, 0)
            for step, (a, b, c) in enumerate(digs3):
                cout = M.carry_step(a, b, c, carry)
                if cout is None:
                    return False, f"carry illegal {name}"
                for role, d in enumerate((a, b, c)):
                    cnt[role][(states[role], d)] += pick["mult"]
                states = (
                    delta[states[0]][a],
                    delta[states[1]][b],
                    delta[states[2]][c],
                )
                carry = cout
            if carry != tc or states != target:
                return False, f"endpoint {name}"
    # Parikh equal roles 0~1 and 2~1
    if cnt[0] != cnt[1] or cnt[2] != cnt[1]:
        return False, f"parikh mismatch {cnt[0]} vs {cnt[1]} vs {cnt[2]}"
    return True, "ok"


def main():
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    assert seed["status"] == "FOUND_ROUTABLE", seed["status"]
    w = seed["witness"]
    delta = w["delta"]
    ports = {int(k): tuple(v) for k, v in w["ports"].items()}
    carries = w["carries"]

    col_data = []
    for i, (weight, origin, name) in enumerate(COLS):
        items = enumerate_routes(delta, ports, origin, carries[i], S)
        print(f"{name} routes={len(items)} weight={weight}", flush=True)
        if not items:
            raise SystemExit(f"no routes for {name}")
        col_data.append((weight, name, items))

    try:
        r = mip_recover(col_data, S)
    except ImportError:
        r = {"status": "NO_HIGHS_PY"}
        print("highspy missing", flush=True)

    print("mip", r.get("status"), flush=True)
    if r.get("status") == "FOUND_INTEGER":
        ok, msg = verify_selected(delta, ports, carries, r["selected"], S)
        print("verify", ok, msg, flush=True)
        if not ok:
            r = {"status": "VERIFY_FAIL", "msg": msg}

    out_wit = {
        "S": S,
        "L": L,
        "n": N,
        "delta": delta,
        "ports": {str(k): list(v) for k, v in ports.items()},
        "digs": w["digs"],
        "carries": carries,
        "selected": r.get("selected"),
        "status": r.get("status"),
    }
    OUT.write_text(json.dumps(out_wit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    res = {
        "schema": "lead.n5_l3_s4_witness.v1",
        "status": r.get("status"),
        "seed_clock_idx": w.get("clock_idx"),
        "route_counts": {
            name: len(items) for _, name, items in col_data
        },
        "claim_boundary": (
            "Integer Parikh-balanced n=5 L=3 S=4 common-anchor split-weight "
            "macro if FOUND_INTEGER. Finite machine object; not E142."
        ),
    }
    RESULT.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2))
    if r.get("status") != "FOUND_INTEGER":
        raise SystemExit(1)
    print("CERTIFIED: n=5 L=3 S=4 integer macro witness")


if __name__ == "__main__":
    main()

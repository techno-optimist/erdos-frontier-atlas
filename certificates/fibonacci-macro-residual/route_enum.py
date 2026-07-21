#!/usr/bin/env python3
"""Route enumeration for Parikh LP: full product for L<=4, sampled DFS for L>=5."""

from __future__ import annotations

import itertools
import random
from collections import Counter

import macro_engine as M


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


def enum_routes_full(delta, ports, origin, tc, L, S):
    u, v, w = origin
    target = (ports[u][0], ports[v][0], ports[w][0])
    uniq = {}
    for digs3 in itertools.product(itertools.product(range(3), repeat=3), repeat=L):
        carry = 0
        states = (0, 0, 0)
        rp = [[], [], []]
        ok = True
        for step in range(L):
            a, b, c = digs3[step]
            cout = M.carry_step(a, b, c, carry)
            if cout is None:
                ok = False
                break
            for role, d in enumerate((a, b, c)):
                rp[role].append((states[role], d))
            states = (
                delta[states[0]][a],
                delta[states[1]][b],
                delta[states[2]][c],
            )
            carry = cout
        if ok and carry == tc and states == target:
            uniq.setdefault(feat_role_ports(rp, S), digs3)
    return list(uniq.items())


def enum_routes_sampled(delta, ports, origin, tc, L, S, samples=80_000, seed=0):
    """Monte-Carlo legal walks; keep unique feats that hit (target, tc)."""
    u, v, w = origin
    target = (ports[u][0], ports[v][0], ports[w][0])
    rng = random.Random(seed + hash((target, tc, L)) % 10_000_007)
    uniq = {}
    # also always include BFS-guided greedy attempts
    for trial in range(samples):
        carry = 0
        states = (0, 0, 0)
        rp = [[], [], []]
        digs3 = []
        ok = True
        for step in range(L):
            # sample random legal digit triple
            choices = []
            for a, b, c in itertools.product(range(3), repeat=3):
                if M.carry_step(a, b, c, carry) is not None:
                    choices.append((a, b, c))
            if not choices:
                ok = False
                break
            a, b, c = choices[rng.randrange(len(choices))]
            cout = M.carry_step(a, b, c, carry)
            for role, d in enumerate((a, b, c)):
                rp[role].append((states[role], d))
            digs3.append((a, b, c))
            states = (
                delta[states[0]][a],
                delta[states[1]][b],
                delta[states[2]][c],
            )
            carry = cout
        if ok and carry == tc and states == target:
            uniq.setdefault(feat_role_ports(rp, S), tuple(digs3))
    return list(uniq.items())


def enum_routes(delta, ports, origin, tc, L, S, samples=80_000):
    if L <= 4:
        return enum_routes_full(delta, ports, origin, tc, L, S)
    return enum_routes_sampled(delta, ports, origin, tc, L, S, samples=samples)


def lp_mip(col_data, S, time_limit=120.0):
    import highspy

    dim = 2 * S * 3
    nvars = sum(len(it) for _, _, it in col_data)
    if nvars == 0:
        return None
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.addVars(nvars, [0.0] * nvars, [1e9] * nvars)
    off = 0
    for w, name, items in col_data:
        k = len(items)
        h.addRow(float(w), float(w), k, list(range(off, off + k)), [1.0] * k)
        off += k
    for j in range(dim):
        idx, vals = [], []
        off = 0
        for w, name, items in col_data:
            for i, (f, d3) in enumerate(items):
                if f[j]:
                    idx.append(off + i)
                    vals.append(float(f[j]))
            off += len(items)
        if idx:
            h.addRow(0.0, 0.0, len(idx), idx, vals)
    h.run()
    if int(h.getModelStatus()) != 7:
        return None
    h2 = highspy.Highs()
    h2.setOptionValue("output_flag", False)
    h2.setOptionValue("time_limit", time_limit)
    h2.addVars(nvars, [0.0] * nvars, [1e6] * nvars)
    h2.changeColsIntegrality(
        nvars, list(range(nvars)), [highspy.HighsVarType.kInteger] * nvars
    )
    off = 0
    ranges = []
    for w, name, items in col_data:
        idxs = list(range(off, off + len(items)))
        h2.addRow(float(w), float(w), len(idxs), idxs, [1.0] * len(idxs))
        ranges.append((w, name, items, idxs))
        off += len(items)
    for j in range(dim):
        idx, vals = [], []
        for w, name, items, idxs in ranges:
            for oi, (f, d3) in enumerate(items):
                if f[j]:
                    idx.append(idxs[oi])
                    vals.append(float(f[j]))
        if idx:
            h2.addRow(0.0, 0.0, len(idx), idx, vals)
    h2.run()
    if int(h2.getModelStatus()) != 7:
        return "MIP_INFEAS"
    sol = h2.getSolution().col_value
    selected = {}
    for w, name, items, idxs in ranges:
        picks = []
        for oi, (f, d3) in enumerate(items):
            m = int(round(sol[idxs[oi]]))
            if m:
                picks.append({"mult": m, "steps": [list(t) for t in d3]})
        selected[name] = picks
    return selected

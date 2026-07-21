#!/usr/bin/env python3
"""Shared pure-Python engine for common-anchor Fibonacci macros (stdlib only)."""

from __future__ import annotations

import itertools
from collections import Counter


def fibs(count):
    f = [1, 1]
    while len(f) < count:
        f.append(f[-1] + f[-2])
    return f


def columns(n):
    f = fibs(n + 1)
    out = [(1, (1, 0, n), "P0"), (1, (0, 1, n), "Q0")]
    for j in range(1, n - 1):
        out.append((f[j], (j + 1, j, j - 1), f"P{j}"))
        out.append((f[j], (j, j + 1, n), f"Q{j}"))
    out.append((f[n - 1], (n - 1, n - 1, n - 2), f"P{n-1}"))
    out.append((f[n], (n, n, n - 1), f"P{n}"))
    return out


def carry_step(a, b, c, cin):
    value = a + c - 2 * b + cin
    if value % 3:
        return None
    cout = value // 3
    return cout if cout in (-1, 0, 1) else None


def digit_patterns(cols, tags):
    out = []
    for digs in itertools.product(range(3), repeat=tags):
        carries = []
        ok = True
        for weight, origin, name in cols:
            u, v, w = origin
            diff = digs[u] + digs[w] - 2 * digs[v]
            if abs(diff) > 1:
                ok = False
                break
            carries.append(-diff)
        if ok:
            out.append((digs, tuple(carries)))
    return out


def has_legal_route(delta, ports, origin, tc, L):
    """Existence of length-L legal return from (0,0,0) to target ports with carry tc."""
    u, v, w = origin
    target = (ports[u][0], ports[v][0], ports[w][0])
    # BFS on (step, states, carry) is huge; product over digit triples is fine for L<=4
    # Pruned iterative: expand step by step
    frontier = {( (0, 0, 0), 0 )}  # (states, carry)
    for _ in range(L):
        nxt = set()
        for states, carry in frontier:
            for a, b, c in itertools.product(range(3), repeat=3):
                cout = carry_step(a, b, c, carry)
                if cout is None:
                    continue
                ns = (
                    delta[states[0]][a],
                    delta[states[1]][b],
                    delta[states[2]][c],
                )
                nxt.add((ns, cout))
        frontier = nxt
        if not frontier:
            return False
    return any(st == target and c == tc for st, c in frontier)


def assign_ports_for_digs(ap, digs, tags):
    by_d = {0: [], 1: [], 2: []}
    for p in ap:
        by_d[p[1]].append(p)
    need = Counter(digs)
    if any(need[d] > len(by_d[d]) for d in need):
        return
    used = set()

    def rec(t, ports):
        if t == tags:
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


def clock_reachable(delta, S, L):
    reach = {0}
    cur = {0}
    for _ in range(L):
        nxt = {delta[s][d] for s in cur for d in range(3)}
        cur = nxt - reach
        reach |= nxt
    return len(reach) >= S


def anchor_ports(delta, S):
    return [(s, d) for s in range(S) for d in range(3) if delta[s][d] == 0]


def outward_ok(ports, carries, cols):
    for i, (_, origin, _) in enumerate(cols):
        u, v, w = origin
        if carry_step(ports[u][1], ports[v][1], ports[w][1], carries[i]) != 0:
            return False
    return True


def all_columns_routable(delta, ports, carries, cols, L):
    for i, (_, origin, _) in enumerate(cols):
        if not has_legal_route(delta, ports, origin, carries[i], L):
            return False
    return True

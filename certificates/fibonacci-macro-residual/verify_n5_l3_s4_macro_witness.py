#!/usr/bin/env python3
"""
Independent exact verifier for the n=5 L=3 S=4 split-weight macro witness.

Does not import the searcher. Rebuilds product edges from sealed routes.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIT = json.loads((HERE / "N5_L3_S4_WITNESS.json").read_text(encoding="utf-8"))
OUT = HERE / "N5_L3_S4_MACRO_WITNESS_RESULT.json"

S = 4
L = 3
N = 5
DELTA = {(s, d): WIT["delta"][s][d] for s in range(S) for d in range(3)}
TAG_PORTS = {int(k): tuple(v) for k, v in WIT["ports"].items()}
ORIGINS = {
    "P0": (1, 0, 5),
    "Q0": (0, 1, 5),
    "P1": (2, 1, 0),
    "Q1": (1, 2, 5),
    "P2": (3, 2, 1),
    "Q2": (2, 3, 5),
    "P3": (4, 3, 2),
    "Q3": (3, 4, 5),
    "P4": (4, 4, 3),
    "P5": (5, 5, 4),
}
OUTWARD_WEIGHT = {
    "P0": 1,
    "Q0": 1,
    "P1": 1,
    "Q1": 1,
    "P2": 2,
    "Q2": 2,
    "P3": 3,
    "Q3": 3,
    "P4": 5,
    "P5": 8,
}


def expand_routes(selected):
    routes = {}
    for name, picks in selected.items():
        unit = []
        for pick in picks:
            steps = tuple(tuple(s) for s in pick["steps"])
            for _ in range(pick["mult"]):
                unit.append(steps)
        routes[name] = unit
    return routes


ROUTES = expand_routes(WIT["selected"])


def carry_step(digits, cin):
    a, b, c = digits
    value = a + c - 2 * b + cin
    assert value % 3 == 0, (digits, cin, value)
    cout = value // 3
    assert cout in (-1, 0, 1), cout
    return cout


def apply_delta(states, digits):
    return tuple(DELTA[(s, d)] for s, d in zip(states, digits))


def tag_column(digits, states):
    ports = tuple((s, d) for s, d in zip(states, digits))
    out = Counter()
    out[(0, ports[0])] += 1
    out[(0, ports[1])] -= 1
    out[(1, ports[2])] += 1
    out[(1, ports[1])] -= 1
    return Counter({k: v for k, v in out.items() if v})


def main():
    assert len(set(TAG_PORTS.values())) == N + 1
    assert all(DELTA[TAG_PORTS[t]] == 0 for t in TAG_PORTS)
    for name, unit in ROUTES.items():
        assert len(unit) == OUTWARD_WEIGHT[name], (name, len(unit), OUTWARD_WEIGHT[name])

    anchor = (0, 0, 0, 0)
    edges = []
    outward_carry = {}

    for name, origin in ORIGINS.items():
        states = tuple(TAG_PORTS[t][0] for t in origin)
        digits = tuple(TAG_PORTS[t][1] for t in origin)
        diff = digits[0] + digits[2] - 2 * digits[1]
        cin = -diff
        assert cin in (-1, 0, 1)
        assert carry_step(digits, cin) == 0
        assert apply_delta(states, digits) == (0, 0, 0)
        source = (cin, *states)
        edges.append(
            (
                f"{name}_out",
                source,
                anchor,
                tag_column(digits, states),
                OUTWARD_WEIGHT[name],
            )
        )
        outward_carry[name] = cin

    for name, route_list in ROUTES.items():
        origin = ORIGINS[name]
        expected = tuple(TAG_PORTS[t][0] for t in origin)
        for ri, steps in enumerate(route_list):
            assert len(steps) == L
            carry = 0
            states = (0, 0, 0)
            for si, digits in enumerate(steps):
                cout = carry_step(digits, carry)
                next_states = apply_delta(states, digits)
                edges.append(
                    (
                        f"{name}_r{ri}_s{si}",
                        (carry, *states),
                        (cout, *next_states),
                        tag_column(digits, states),
                        1,
                    )
                )
                carry = cout
                states = next_states
            assert carry == outward_carry[name], (name, ri, carry, outward_carry[name])
            assert states == expected, (name, ri, states, expected)

    flow = Counter()
    tags = Counter()
    adj = defaultdict(set)
    for name, src, tgt, col, w in edges:
        flow[src] -= w
        flow[tgt] += w
        for k, v in col.items():
            tags[k] += w * v
        adj[src].add(tgt)
        adj[tgt].add(src)

    flow_ok = all(v == 0 for v in flow.values())
    tags_ok = all(v == 0 for v in tags.values())

    used = {v for _, s, t, _, _ in edges for v in (s, t)}
    seen = {anchor}
    todo = deque([anchor])
    while todo:
        cur = todo.popleft()
        for nxt in adj[cur]:
            if nxt in used and nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    connected = seen == used

    role_ports = [Counter(), Counter(), Counter()]
    for name, route_list in ROUTES.items():
        for steps in route_list:
            states = (0, 0, 0)
            for digits in steps:
                for role, d in enumerate(digits):
                    role_ports[role][(states[role], d)] += 1
                states = apply_delta(states, digits)
    parikh_ok = role_ports[0] == role_ports[1] == role_ports[2]

    status = (
        "PASS_N5_L3_S4_SPLIT_MACRO_WITNESS"
        if flow_ok and tags_ok and connected and parikh_ok
        else "FAIL"
    )
    result = {
        "schema": "lead.n5_l3_s4_macro_witness.v1",
        "status": status,
        "state_count": S,
        "return_length": L,
        "n": N,
        "tag_count": N + 1,
        "clock_delta": {f"{s},{d}": t for (s, d), t in DELTA.items()},
        "tag_ports": {str(t): list(p) for t, p in TAG_PORTS.items()},
        "outward_carries": outward_carry,
        "route_unit_counts": {k: len(v) for k, v in ROUTES.items()},
        "edge_count": len(edges),
        "vertex_count": len(used),
        "weighted_flow_boundary_zero": flow_ok,
        "weighted_tag_column_zero": tags_ok,
        "return_role_parikh_equal": parikh_ok,
        "weakly_connected_from_anchor": connected,
        "claim_boundary": (
            "Exact n=5 common-anchor split-weight length-three globally "
            "Parikh-balanced macro on a 4-state deterministic ternary clock. "
            "Not an all-n family and not an Erdős 142 construction."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    assert status.startswith("PASS"), result


if __name__ == "__main__":
    main()

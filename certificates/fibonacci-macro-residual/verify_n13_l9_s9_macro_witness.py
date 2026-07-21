#!/usr/bin/env python3
"""Independent verifier: n=13 L=9 S=9 split-weight macro witness."""

from __future__ import annotations

import json
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIT = json.loads((HERE / "N13_L9_S9_WITNESS.json").read_text(encoding="utf-8"))
OUT = HERE / "N13_L9_S9_MACRO_WITNESS_RESULT.json"

S, L, N = 9, 9, 13
DELTA = {(s, d): WIT["delta"][s][d] for s in range(S) for d in range(3)}
TAG_PORTS = {int(k): tuple(v) for k, v in WIT["ports"].items()}
ORIGINS = {
    "P0": [
        1,
        0,
        13
    ],
    "Q0": [
        0,
        1,
        13
    ],
    "P1": [
        2,
        1,
        0
    ],
    "Q1": [
        1,
        2,
        13
    ],
    "P2": [
        3,
        2,
        1
    ],
    "Q2": [
        2,
        3,
        13
    ],
    "P3": [
        4,
        3,
        2
    ],
    "Q3": [
        3,
        4,
        13
    ],
    "P4": [
        5,
        4,
        3
    ],
    "Q4": [
        4,
        5,
        13
    ],
    "P5": [
        6,
        5,
        4
    ],
    "Q5": [
        5,
        6,
        13
    ],
    "P6": [
        7,
        6,
        5
    ],
    "Q6": [
        6,
        7,
        13
    ],
    "P7": [
        8,
        7,
        6
    ],
    "Q7": [
        7,
        8,
        13
    ],
    "P8": [
        9,
        8,
        7
    ],
    "Q8": [
        8,
        9,
        13
    ],
    "P9": [
        10,
        9,
        8
    ],
    "Q9": [
        9,
        10,
        13
    ],
    "P10": [
        11,
        10,
        9
    ],
    "Q10": [
        10,
        11,
        13
    ],
    "P11": [
        12,
        11,
        10
    ],
    "Q11": [
        11,
        12,
        13
    ],
    "P12": [
        12,
        12,
        11
    ],
    "P13": [
        13,
        13,
        12
    ]
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
    "Q4": 5,
    "P5": 8,
    "Q5": 8,
    "P6": 13,
    "Q6": 13,
    "P7": 21,
    "Q7": 21,
    "P8": 34,
    "Q8": 34,
    "P9": 55,
    "Q9": 55,
    "P10": 89,
    "Q10": 89,
    "P11": 144,
    "Q11": 144,
    "P12": 233,
    "P13": 377
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
        cin = -(digits[0] + digits[2] - 2 * digits[1])
        assert cin in (-1, 0, 1)
        assert carry_step(digits, cin) == 0
        assert apply_delta(states, digits) == (0, 0, 0)
        edges.append(
            (f"{name}_out", (cin, *states), anchor, tag_column(digits, states), OUTWARD_WEIGHT[name])
        )
        outward_carry[name] = cin

    for name, route_list in ROUTES.items():
        expected = tuple(TAG_PORTS[t][0] for t in ORIGINS[name])
        for ri, steps in enumerate(route_list):
            assert len(steps) == L
            carry, states = 0, (0, 0, 0)
            for si, digits in enumerate(steps):
                cout = carry_step(digits, carry)
                ns = apply_delta(states, digits)
                edges.append(
                    (f"{name}_r{ri}_s{si}", (carry, *states), (cout, *ns), tag_column(digits, states), 1)
                )
                carry, states = cout, ns
            assert carry == outward_carry[name]
            assert states == expected

    flow, tags, adj = Counter(), Counter(), defaultdict(set)
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
    seen, todo = {anchor}, deque([anchor])
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
        "PASS_N13_L9_S9_SPLIT_MACRO_WITNESS"
        if flow_ok and tags_ok and connected and parikh_ok
        else "FAIL"
    )
    result = {
        "schema": "lead.n13_l9_s9_macro_witness.v1",
        "status": status,
        "state_count": S,
        "return_length": L,
        "n": N,
        "tag_count": N + 1,
        "route_unit_counts": {k: len(v) for k, v in ROUTES.items()},
        "edge_count": len(edges),
        "vertex_count": len(used),
        "weighted_flow_boundary_zero": flow_ok,
        "weighted_tag_column_zero": tags_ok,
        "return_role_parikh_equal": parikh_ok,
        "weakly_connected_from_anchor": connected,
        "claim_boundary": (
            "Exact n=13 common-anchor split-weight length-nine Parikh-balanced "
            "macro on a 9-state clock. Not Erdős 142."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    assert status.startswith("PASS"), result


if __name__ == "__main__":
    main()

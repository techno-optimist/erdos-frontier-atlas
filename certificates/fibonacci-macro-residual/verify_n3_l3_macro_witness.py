#!/usr/bin/env python3
"""
Independent exact verifier for the n=3 length-three split-weight macro witness.

Does not import the searcher.  Rebuilds product edges from the sealed routes,
checks carry legality, endpoint states, outward edges, global Parikh balance,
weighted flow balance at product vertices, and weak connectivity from the anchor.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "N3_L3_MACRO_WITNESS_RESULT.json"

DELTA = {
    (0, 0): 0,
    (0, 1): 0,
    (0, 2): 1,
    (1, 0): 0,
    (1, 1): 0,
    (1, 2): 2,
    (2, 0): 0,
    (2, 1): 2,
    (2, 2): 0,
}
TAG_PORTS = {0: (0, 0), 1: (2, 0), 2: (1, 0), 3: (0, 1)}
ORIGINS = {
    "P0": (1, 0, 3),
    "Q0": (0, 1, 3),
    "P1": (2, 1, 0),
    "Q1": (1, 2, 3),
    "P2": (2, 2, 1),
    "P3": (3, 3, 2),
}
OUTWARD_WEIGHT = {"P0": 1, "Q0": 1, "P1": 1, "Q1": 1, "P2": 2, "P3": 3}

# unit return routes: list of 3 digit triples each
ROUTES = {
    "P0": [
        ((0, 2, 1), (2, 2, 0), (2, 2, 0)),
    ],
    "Q0": [
        ((0, 2, 1), (2, 2, 0), (0, 1, 0)),
    ],
    "P1": [
        ((1, 0, 2), (1, 2, 2), (2, 2, 2)),
    ],
    "Q1": [
        ((2, 1, 0), (2, 1, 0), (1, 2, 0)),
    ],
    "P2": [
        ((0, 1, 2), (1, 0, 2), (2, 2, 1)),
        ((0, 2, 1), (1, 1, 2), (2, 2, 2)),
    ],
    "P3": [
        ((0, 1, 2), (0, 0, 0), (1, 0, 2)),
        ((2, 0, 1), (1, 0, 1), (0, 0, 2)),
        ((2, 2, 2), (2, 0, 1), (2, 1, 2)),
    ],
}


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
    """AP tag column for one product edge (two free roles)."""
    ports = tuple((s, d) for s, d in zip(states, digits))
    out = Counter()
    out[(0, ports[0])] += 1
    out[(0, ports[1])] -= 1
    out[(1, ports[2])] += 1
    out[(1, ports[1])] -= 1
    return Counter({k: v for k, v in out.items() if v})


def main():
    assert len(set(TAG_PORTS.values())) == 4
    # outward ports return to anchor state 0
    assert all(DELTA[TAG_PORTS[t]] == 0 for t in TAG_PORTS)

    anchor = (0, 0, 0, 0)  # (carry, s0, s1, s2)
    edges = []  # (name, source, target, tag_col)
    outward_carry = {}

    # Outward edges
    for name, origin in ORIGINS.items():
        states = tuple(TAG_PORTS[t][0] for t in origin)
        digits = tuple(TAG_PORTS[t][1] for t in origin)
        diff = digits[0] + digits[2] - 2 * digits[1]
        cin = -diff
        assert cin in (-1, 0, 1)
        assert carry_step(digits, cin) == 0
        assert apply_delta(states, digits) == (0, 0, 0)
        source = (cin, *states)
        edges.append((f"{name}_out", source, anchor, tag_column(digits, states)))
        outward_carry[name] = cin

    # Return routes
    for name, route_list in ROUTES.items():
        assert len(route_list) == OUTWARD_WEIGHT[name]
        origin = ORIGINS[name]
        expected_end_states = tuple(TAG_PORTS[t][0] for t in origin)
        for ri, steps in enumerate(route_list):
            assert len(steps) == 3
            carry = 0
            states = (0, 0, 0)
            vertices = [anchor]
            for si, digits in enumerate(steps):
                cout = carry_step(digits, carry)
                next_states = apply_delta(states, digits)
                edges.append(
                    (
                        f"{name}_r{ri}_s{si}",
                        (carry, *states),
                        (cout, *next_states),
                        tag_column(digits, states),
                    )
                )
                carry = cout
                states = next_states
                vertices.append((carry, *states))
            assert carry == outward_carry[name], (name, ri, carry, outward_carry[name])
            assert states == expected_end_states, (name, ri, states, expected_end_states)

    # Weights: each listed edge once (unit routes already expanded)
    weights = Counter()
    for name, _, _, _ in edges:
        weights[name] += 1
    # outward edges need multiplicity = OUTWARD_WEIGHT
    # Currently each outward is listed once — scale by weight
    scaled_edges = []
    for name, src, tgt, col in edges:
        if name.endswith("_out"):
            base = name[: -len("_out")]
            w = OUTWARD_WEIGHT[base]
        else:
            w = 1
        scaled_edges.append((name, src, tgt, col, w))

    flow = Counter()
    tags = Counter()
    adj = defaultdict(set)
    for name, src, tgt, col, w in scaled_edges:
        flow[src] -= w
        flow[tgt] += w
        for k, v in col.items():
            tags[k] += w * v
        adj[src].add(tgt)
        adj[tgt].add(src)

    flow_ok = all(v == 0 for v in flow.values())
    tags_ok = all(v == 0 for v in tags.values())

    # weak connectivity from anchor among used vertices
    used = {v for _, s, t, _, _ in scaled_edges for v in (s, t)}
    seen = {anchor}
    todo = deque([anchor])
    while todo:
        cur = todo.popleft()
        for nxt in adj[cur]:
            if nxt in used and nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    connected = seen == used

    # return-role complete-port Parikh (return edges only)
    role_ports = [Counter(), Counter(), Counter()]
    for name, src, tgt, col, w in scaled_edges:
        if "_r" not in name:
            continue
        # recover digits from name? better recompute from ROUTES
        pass
    # recompute from ROUTES directly
    role_ports = [Counter(), Counter(), Counter()]
    for name, route_list in ROUTES.items():
        for steps in route_list:
            carry = 0
            states = (0, 0, 0)
            for digits in steps:
                for role, d in enumerate(digits):
                    role_ports[role][(states[role], d)] += 1
                states = apply_delta(states, digits)
                carry = carry_step(digits, carry)
    parikh_ok = role_ports[0] == role_ports[1] == role_ports[2]

    status = (
        "PASS_N3_L3_SPLIT_MACRO_WITNESS"
        if flow_ok and tags_ok and connected and parikh_ok
        else "FAIL"
    )
    result = {
        "schema": "lead.n3_l3_macro_witness.v1",
        "status": status,
        "state_count": 3,
        "return_length": 3,
        "clock_delta": {f"{s},{d}": t for (s, d), t in DELTA.items()},
        "tag_ports": {str(t): list(p) for t, p in TAG_PORTS.items()},
        "outward_carries": outward_carry,
        "route_counts": {k: len(v) for k, v in ROUTES.items()},
        "edge_count": len(scaled_edges),
        "vertex_count": len(used),
        "weighted_flow_boundary_zero": flow_ok,
        "weighted_tag_column_zero": tags_ok,
        "return_role_parikh_equal": parikh_ok,
        "weakly_connected_from_anchor": connected,
        "claim_boundary": (
            "Exact n=3 common-anchor split-weight length-three globally "
            "Parikh-balanced macro on a 3-state deterministic ternary clock. "
            "Not an all-n family and not an Erdős 142 construction."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    assert status.startswith("PASS"), result


if __name__ == "__main__":
    main()

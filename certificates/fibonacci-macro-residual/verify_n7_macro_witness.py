#!/usr/bin/env python3
"""
Independent exact verifier for an n=7 split-weight macro witness.

Usage:
  python verify_n7_macro_witness.py [N7_L*_S*_WITNESS.json]

Does not import the searcher. Product-graph flow + Parikh + connectivity.
Origins/weights from the n=7 Fibonacci column table (tags = 8).
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent

# n=7: fibs F0..F7 with F0=F1=1 → weights on columns
# P0,Q0,P1,Q1,P2,Q2,P3,Q3,P4,Q4,P5,Q5,P6,P7
ORIGINS = {
    "P0": (1, 0, 7),
    "Q0": (0, 1, 7),
    "P1": (2, 1, 0),
    "Q1": (1, 2, 7),
    "P2": (3, 2, 1),
    "Q2": (2, 3, 7),
    "P3": (4, 3, 2),
    "Q3": (3, 4, 7),
    "P4": (5, 4, 3),
    "Q4": (4, 5, 7),
    "P5": (6, 5, 4),
    "Q5": (5, 6, 7),
    "P6": (6, 6, 5),
    "P7": (7, 7, 6),
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
    "P7": 21,
}
N = 7


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


def carry_step(digits, cin):
    a, b, c = digits
    value = a + c - 2 * b + cin
    assert value % 3 == 0, (digits, cin, value)
    cout = value // 3
    assert cout in (-1, 0, 1), cout
    return cout


def main():
    # The witness must be named EXPLICITLY. This is a parameterised tool whose
    # output filename is derived from the witness (N7_L{L}_S{S}_..._RESULT.json),
    # so defaulting to a glob meant that running it bare silently clobbered a
    # receipt owned by a dedicated per-cell verifier (e.g. N7_L5_S5, which
    # verify_n7_l5_s5_macro_witness.py owns) with different wording. Two writers
    # for one receipt is an ownership bug; require the argument instead.
    if len(sys.argv) <= 1:
        raise SystemExit(
            "usage: verify_n7_macro_witness.py N7_L<L>_S<S>_WITNESS.json\n"
            "  (name the witness explicitly -- this tool derives its receipt "
            "filename from it and must not guess, or it will overwrite a "
            "receipt owned by a dedicated verifier)"
        )
    wit_path = HERE / sys.argv[1]
    if not wit_path.exists():
        # try any N7_*_WITNESS.json
        cands = sorted(HERE.glob("N7_L*_S*_WITNESS.json"))
        if not cands:
            raise SystemExit(f"no witness file at {wit_path} and no N7_*_WITNESS.json")
        wit_path = cands[0]
        print("using", wit_path.name, flush=True)

    WIT = json.loads(wit_path.read_text(encoding="utf-8"))
    S = int(WIT["S"])
    L = int(WIT["L"])
    assert int(WIT.get("n", N)) == N
    DELTA = {(s, d): WIT["delta"][s][d] for s in range(S) for d in range(3)}
    TAG_PORTS = {int(k): tuple(v) for k, v in WIT["ports"].items()}
    ROUTES = expand_routes(WIT["selected"])

    out_path = HERE / f"N7_L{L}_S{S}_MACRO_WITNESS_RESULT.json"

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
            assert len(steps) == L, (name, ri, len(steps))
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
        f"PASS_N7_L{L}_S{S}_SPLIT_MACRO_WITNESS"
        if flow_ok and tags_ok and connected and parikh_ok
        else "FAIL"
    )
    result = {
        "schema": f"lead.n7_l{L}_s{S}_macro_witness.v1",
        "status": status,
        "witness_file": wit_path.name,
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
            f"Exact n=7 common-anchor split-weight length-{L} globally "
            f"Parikh-balanced macro on a {S}-state deterministic ternary clock. "
            "Not an all-n family and not an Erdős 142 construction."
        ),
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    assert status.startswith("PASS"), result


if __name__ == "__main__":
    main()

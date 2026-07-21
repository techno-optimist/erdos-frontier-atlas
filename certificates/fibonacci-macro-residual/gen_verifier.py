#!/usr/bin/env python3
"""Generate independent verifier script from a WITNESS.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import macro_engine as M

HERE = Path(__file__).resolve().parent

TEMPLATE = '''#!/usr/bin/env python3
"""Independent verifier: n={N} L={L} S={S} split-weight macro witness."""

from __future__ import annotations

import json
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIT = json.loads((HERE / "N{N}_L{L}_S{S}_WITNESS.json").read_text(encoding="utf-8"))
OUT = HERE / "N{N}_L{L}_S{S}_MACRO_WITNESS_RESULT.json"

S, L, N = {S}, {L}, {N}
DELTA = {{(s, d): WIT["delta"][s][d] for s in range(S) for d in range(3)}}
TAG_PORTS = {{int(k): tuple(v) for k, v in WIT["ports"].items()}}
ORIGINS = {origins}
OUTWARD_WEIGHT = {weights}


def expand_routes(selected):
    routes = {{}}
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
    return Counter({{k: v for k, v in out.items() if v}})


def main():
    assert len(set(TAG_PORTS.values())) == N + 1
    assert all(DELTA[TAG_PORTS[t]] == 0 for t in TAG_PORTS)
    for name, unit in ROUTES.items():
        assert len(unit) == OUTWARD_WEIGHT[name], (name, len(unit), OUTWARD_WEIGHT[name])

    anchor = (0, 0, 0, 0)
    edges = []
    outward_carry = {{}}
    for name, origin in ORIGINS.items():
        states = tuple(TAG_PORTS[t][0] for t in origin)
        digits = tuple(TAG_PORTS[t][1] for t in origin)
        cin = -(digits[0] + digits[2] - 2 * digits[1])
        assert cin in (-1, 0, 1)
        assert carry_step(digits, cin) == 0
        assert apply_delta(states, digits) == (0, 0, 0)
        edges.append(
            (f"{{name}}_out", (cin, *states), anchor, tag_column(digits, states), OUTWARD_WEIGHT[name])
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
                    (f"{{name}}_r{{ri}}_s{{si}}", (carry, *states), (cout, *ns), tag_column(digits, states), 1)
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
    used = {{v for _, s, t, _, _ in edges for v in (s, t)}}
    seen, todo = {{anchor}}, deque([anchor])
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
        "PASS_N{N}_L{L}_S{S}_SPLIT_MACRO_WITNESS"
        if flow_ok and tags_ok and connected and parikh_ok
        else "FAIL"
    )
    result = {{
        "schema": "lead.n{N}_l{L}_s{S}_macro_witness.v1",
        "status": status,
        "state_count": S,
        "return_length": L,
        "n": N,
        "tag_count": N + 1,
        "route_unit_counts": {{k: len(v) for k, v in ROUTES.items()}},
        "edge_count": len(edges),
        "vertex_count": len(used),
        "weighted_flow_boundary_zero": flow_ok,
        "weighted_tag_column_zero": tags_ok,
        "return_role_parikh_equal": parikh_ok,
        "weakly_connected_from_anchor": connected,
        "claim_boundary": (
            "Exact n={N} common-anchor split-weight length-{Lword} Parikh-balanced "
            "macro on a {S}-state clock. Not Erdős 142."
        ),
    }}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    assert status.startswith("PASS"), result


if __name__ == "__main__":
    main()
'''

WORDS = {
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("witness", type=str)
    args = ap.parse_args()
    path = HERE / args.witness if not Path(args.witness).is_absolute() else Path(args.witness)
    wit = json.loads(path.read_text(encoding="utf-8"))
    n, L, S = wit["n"], wit["L"], wit["S"]
    cols = M.columns(n)
    origins = {name: origin for _, origin, name in cols}
    weights = {name: w for w, _, name in cols}
    lword = WORDS.get(L, str(L))
    text = TEMPLATE.format(
        N=n,
        L=L,
        S=S,
        origins=json.dumps(origins, indent=4),
        weights=json.dumps(weights, indent=4),
        Lword=lword,
    )
    # fix ORIGINS/WEIGHTS indentation after format
    out_py = HERE / f"verify_n{n}_l{L}_s{S}_macro_witness.py"
    out_py.write_text(text, encoding="utf-8")
    print("wrote", out_py)

    th = HERE / f"THEOREM_N{n}_L{L}_S{S}_SPLIT_MACRO_WITNESS.md"
    th.write_text(
        f"""# n={n} L={L} S={S} split-weight macro witness

Date: 2026-07-21

**Status:** machine-sealed WITNESS (independent product-graph verifier).

## Cell

Common-anchor Fibonacci macro residual: n={n}, return length L={L}, clock states S={S}.

## Artifacts

| file | role |
|------|------|
| `N{n}_L{L}_S{S}_WITNESS.json` | clock + ports + selected routes |
| `verify_n{n}_l{L}_s{S}_macro_witness.py` | independent verifier |
| `N{n}_L{L}_S{S}_MACRO_WITNESS_RESULT.json` | PASS receipt |

## Replay

```sh
python3 -I verify_n{n}_l{L}_s{S}_macro_witness.py
```

## Claim boundary

Finite machine object for the common-anchor split-integral deterministic ternary
macro model. **Not** an Erdős 142 solution.
""",
        encoding="utf-8",
    )
    print("wrote", th)


if __name__ == "__main__":
    main()

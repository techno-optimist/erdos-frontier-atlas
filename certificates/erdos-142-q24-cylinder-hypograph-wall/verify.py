#!/usr/bin/env python3
"""Stdlib-only semantic verifier for the q=24 cylinder hypograph packet.

Finite q=24 only. Does not claim continuum or new r3 bound.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_PACKET = HERE / "certificate.json"

Q = 24
ROLES = ("P1", "P2", "P3", "B", "K")
WORDS = (
    ("P1", "K", "B"),
    ("B", "K", "P1"),
    ("P2", "B", "P2"),
    ("P3", "B", "B"),
    ("B", "B", "P3"),
)
ASSIGN = (7, 7, 7, 6, 7)
N_G = 2445
N = 2820
EXPECTED_SHA256 = "4F6344025D672E6A6E631BB34B86250AD6423A89EC9C03BF5109AE76EC6C65C8"


def tile():
    out = set()
    for x in range(Q):
        for y in range(Q):
            sm = x + y
            if (
                (x >= 12 and 17 <= sm <= 28)
                or (x >= 12 and y <= 11 and 29 <= sm <= 34)
                or (x <= 11 and y >= 12 and 29 <= sm <= 34 and 4 * x + 2 * y >= 74)
            ):
                out.add((x, y))
    assert len(out) == 163
    return out


def d4(points, k):
    out = []
    for x, y in points:
        if k & 1:
            x, y = 23 - x, y
        if k & 2:
            x, y = x, 23 - y
        if k & 4:
            x, y = y, x
        out.append((x, y))
    return frozenset(out)


def tvar(a, b, c, i):
    return N_G + 3 * ((a * 5 + b) * 5 + c) + i


def sparse(terms):
    acc = {}
    for k, v in terms:
        acc[k] = acc.get(k, 0) + v
    return [[k, v] for k, v in sorted(acc.items()) if v]


def expected_geometry():
    base = tile()
    images = [d4(base, k) for k in range(8)]
    assert len(set(images)) == 8
    supports = {role: images[ASSIGN[i]] for i, role in enumerate(ROLES)}
    assert not (images[7] & images[6])
    labels = []
    index = {}
    for c, word in enumerate(WORDS):
        for i, role in enumerate(word):
            for point in sorted(supports[role]):
                index[c, i, point] = len(labels)
                labels.append((c, i, point))
    assert len(labels) == N_G
    mass = 0
    for size in range(1, 6):
        for chosen in itertools.combinations(WORDS, size):
            product = 1
            for i in range(3):
                common = set(supports[chosen[0][i]])
                for word in chosen[1:]:
                    common &= supports[word[i]]
                product *= len(common)
            mass += product if size % 2 else -product
    assert mass == 5 * 163**3
    return supports, labels, index, mass


def verify(data):
    assert data["schema"] == "erdos142-q24-cylinder-hypograph-farkas-v1"
    assert data["q"] == Q and tuple(data["assignment"]) == ASSIGN
    assert tuple(data["roles"]) == ROLES and tuple(map(tuple, data["codewords"])) == WORDS
    supports, labels, index, mass = expected_geometry()
    assert data["support_size"] == 163 and data["d4_images"] == {
        "A_index": 7,
        "C_index": 6,
        "A_C_intersection": 0,
    }
    assert data["union_mass_count"] == mass == 21653735
    assert data["threshold_count"] == 4741632
    assert data["g_variable_count"] == N_G and data["t_variable_count"] == 375
    assert data["g_variable_labels"] == [[c, i, list(point)] for c, i, point in labels]
    assert "iff" in data["equivalence"]
    assert data["scope"]["finite_q24_only"] and not data["scope"]["continuum_certificate"]
    local = data["local_rows"]
    sums = data["triple_sum_rows"]
    assert len(sums) == 125 and len(local) > 0
    for row in local:
        p = row["provenance"]
        assert p["kind"] == "local-hypograph"
        a, b, c = map(int, p["word_indices"])
        i = int(p["position"])
        assert all(0 <= v < 5 for v in (a, b, c)) and 0 <= i < 3
        w = p["witness"]
        x, y, z = map(tuple, (w["x"], w["y"], w["z"]))
        roles = [WORDS[a][i], WORDS[b][i], WORDS[c][i]]
        assert w["coordinate"] == i and w["cylinders"] == [a, b, c] and w["roles"] == roles
        assert x in supports[roles[0]] and y in supports[roles[1]] and z in supports[roles[2]]
        carry = [(x[j] + z[j] - 2 * y[j]) // Q for j in range(2)]
        assert all((2 * y[j] - x[j] - z[j]) % Q == 0 for j in range(2))
        assert all(v in (-1, 0, 1) for v in carry) and w["carry"] == carry
        cost = sum((x[j] - z[j]) ** 2 for j in range(2))
        assert w["raw_cost_numerator"] == cost
        variables = [index[a, i, x], index[b, i, y], index[c, i, z]]
        assert w["variables"] == variables
        expected = sparse(
            (
                (tvar(a, b, c, i), 1),
                (variables[0], -1),
                (variables[2], -1),
                (variables[1], 2),
            )
        )
        assert row["coefficients"] == expected and row["rhs_num"] == -cost
    expected_sums = []
    for a, b, c in itertools.product(range(5), repeat=3):
        expected_sums.append(
            (
                [[tvar(a, b, c, i), -1] for i in range(3)],
                {
                    "kind": "triple-sum",
                    "word_indices": [a, b, c],
                    "scaled_form": "-t0-t1-t2 <= 0",
                },
            )
        )
    for row, (co, p) in zip(sums, expected_sums):
        assert row["coefficients"] == co and row["rhs_num"] == 0 and row["provenance"] == p
    balance = [0] * N
    rhs = 0
    for entry in data["farkas_rows"]:
        m = int(entry["multiplier"])
        assert m > 0
        if entry["kind"] == "local":
            rows = local
        elif entry["kind"] == "sum":
            rows = sums
        else:
            raise AssertionError("bad farkas kind")
        assert 0 <= int(entry["index"]) < len(rows)
        row = rows[int(entry["index"])]
        rhs += m * int(row["rhs_num"])
        for j, v in row["coefficients"]:
            balance[int(j)] += m * int(v)
    assert not any(balance) and rhs < 0
    return {
        "local_rows": len(local),
        "sum_rows": len(sums),
        "farkas_rows": len(data["farkas_rows"]),
        "positive_contradiction": str(-rhs),
        "mass": mass,
    }


def expect_rejected(data, mutate):
    bad = copy.deepcopy(data)
    mutate(bad)
    try:
        verify(bad)
    except (AssertionError, KeyError, IndexError, TypeError):
        return
    raise AssertionError("planted corruption was accepted")


def self_test(data):
    expect_rejected(data, lambda d: d["farkas_rows"][0].update({"multiplier": "0"}))
    expect_rejected(
        data, lambda d: d["local_rows"][0]["provenance"]["witness"]["x"].__setitem__(0, 99)
    )
    expect_rejected(
        data, lambda d: d["local_rows"][0]["provenance"]["witness"]["carry"].__setitem__(0, 3)
    )
    expect_rejected(
        data,
        lambda d: d["local_rows"][0]["provenance"]["witness"].update({"raw_cost_numerator": -1}),
    )
    expect_rejected(
        data,
        lambda d: d["local_rows"][0]["provenance"]["witness"]["cylinders"].__setitem__(0, 4),
    )
    expect_rejected(data, lambda d: d["local_rows"][0]["provenance"].update({"position": 2}))
    expect_rejected(
        data,
        lambda d: d["local_rows"][0]["provenance"]["witness"]["roles"].__setitem__(0, "B"),
    )
    expect_rejected(data, lambda d: d.__setitem__("triple_sum_rows", d["triple_sum_rows"][:-1]))
    expect_rejected(data, lambda d: d.__setitem__("assignment", [7, 7, 7, 7, 7]))
    expect_rejected(data, lambda d: d.__setitem__("union_mass_count", 0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "packet",
        type=Path,
        nargs="?",
        default=DEFAULT_PACKET,
        help="path to certificate.json (default: sibling certificate.json)",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    raw = args.packet.read_bytes()
    sha = hashlib.sha256(raw).hexdigest().upper()
    if args.packet.resolve() == DEFAULT_PACKET.resolve():
        assert sha == EXPECTED_SHA256, f"certificate hash mismatch: {sha}"
    data = json.loads(raw)
    report = verify(data)
    report["sha256"] = sha
    report["tag"] = "PASS_Q24_CYLINDER_HYPOGRAPH_EXACT_FARKAS"
    report["erdos142_solved"] = False
    report["new_r3_bound"] = False
    report["continuum_certificate"] = False
    if args.self_test:
        self_test(data)
        report["planted_corruptions"] = "all rejected"
    print(report["tag"])
    print(f"certificate_sha256 {sha}")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Primary stdlib-only semantic replay for the q=6/M7 cell-U wall."""
import copy
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CERT_PATH = ROOT / "certificate.json"
Q = D = 6
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
GROUPS = {
    0: (15, 30, 46, 51, 53, 57), 1: (15, 54, 57),
    2: (7, 56), 3: (3, 60), 4: (7, 56), 5: (12, 17, 34),
    6: (3, 12, 17, 18, 36, 40),
}
CELLS = tuple((word, residue) for residue in range(7)
              for word in GROUPS[residue])
POINTS = tuple(itertools.product(range(Q), repeat=2))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def support(bit):
    return frozenset(BASE if bit == 0 else ((Q - 1 - x, y) for x, y in BASE))


SUPPORTS = (support(0), support(1))


def parity(point):
    return (point[0] + point[1]) & 1


def bits(word):
    return tuple((word >> i) & 1 for i in range(D))


STATES = tuple((cell, pattern)
               for cell, (_, residue) in enumerate(CELLS)
               for pattern in itertools.product(range(2), repeat=D)
               if sum(pattern) == residue)


def scalar(a, b, c):
    """Exact 3-scaled half-open-box supremum for one coordinate."""
    defect = a + c - 2 * b
    for k in (-1, 0, 1):
        residual = 6 * k - defect
        if residual not in (-1, 0, 1):
            continue
        if k == 0:
            return 0
        if k < 0:
            return 2 * b - 1 if residual in (-1, 0) else 2 * b - 2
        return -2 * b - 4 if residual == -1 else -2 * b - 3
    return None


def check_record(record, state_agg, local_agg):
    a, b, c = record["state_ids"]
    ca, pa = STATES[a]
    cb, pb = STATES[b]
    cc, pc = STATES[c]
    rhs = 0
    for i, (xi, yi, zi) in enumerate(zip(record["x"], record["y"], record["z"])):
        X, Y, Z = POINTS[xi], POINTS[yi], POINTS[zi]
        assert X in SUPPORTS[bits(CELLS[ca][0])[i]]
        assert Y in SUPPORTS[bits(CELLS[cb][0])[i]]
        assert Z in SUPPORTS[bits(CELLS[cc][0])[i]]
        assert (parity(X), parity(Y), parity(Z)) == (pa[i], pb[i], pc[i])
        sx, sy = scalar(X[0], Y[0], Z[0]), scalar(X[1], Y[1], Z[1])
        assert sx is not None and sy is not None
        rhs += sx + sy
        for cell, point, coefficient in ((ca, xi, 1), (cb, yi, -2), (cc, zi, 1)):
            local_agg[(cell, i, point)] += coefficient * record["weight"]
    assert rhs == record["rhs3"]
    for state, coefficient in ((a, 1), (b, -2), (c, 1)):
        state_agg[state] += coefficient * record["weight"]
    return rhs * record["weight"]


def replay(cert):
    assert cert["format"] == "erdos142-q6-continuous-pattern-cellu-farkas-v1"
    assert cert["scope"] == (
        "H=2norm2+G(cell,pattern)+sum_i U(cell,i,coarsepoint_i) only")
    assert len(CELLS) == 24 and len(STATES) == 148
    assert all(len(s) == 9 for s in SUPPORTS) and SUPPORTS[0].isdisjoint(SUPPORTS[1])
    assert len(cert["records"]) == 358
    state_agg, local_agg = defaultdict(int), defaultdict(int)
    total = 0
    for record in cert["records"]:
        assert isinstance(record["weight"], int) and record["weight"] > 0
        total += check_record(record, state_agg, local_agg)
    assert not {k: v for k, v in state_agg.items() if v}
    assert not {k: v for k, v in local_agg.items() if v}
    assert total == int(cert["weighted_rhs3"]) and total > 0
    assert total == 154549018277281375201164147325396656959271726533395814727855110893018977959197745379570260517107780
    return total


def corruption_controls(cert):
    tests = {
        "rhs": lambda d: d["records"][0].__setitem__("rhs3", d["records"][0]["rhs3"] + 1),
        "point": lambda d: d["records"][0]["x"].__setitem__(0, (d["records"][0]["x"][0] + 1) % 36),
        "state": lambda d: d["records"][0]["state_ids"].__setitem__(0, (d["records"][0]["state_ids"][0] + 1) % 148),
        "weight": lambda d: d["records"][0].__setitem__("weight", d["records"][0]["weight"] + 1),
    }
    rejected = []
    for label, mutate in tests.items():
        bad = copy.deepcopy(cert)
        mutate(bad)
        try:
            replay(bad)
        except (AssertionError, KeyError, TypeError, ValueError):
            rejected.append(label)
        else:
            raise AssertionError("planted corruption escaped: " + label)
    return rejected


def main():
    cert = json.loads(CERT_PATH.read_text())
    total = replay(cert)
    controls = corruption_controls(cert)
    print(json.dumps({
        "status": "verified-q6-m7-cellu-restricted-wall",
        "rows": len(cert["records"]), "states": len(STATES), "cells": len(CELLS),
        "weighted_rhs3": str(total), "certificate_sha256": sha256(CERT_PATH),
        "planted_corruptions_rejected": controls,
        "scope": cert["scope"],
    }, indent=2, sort_keys=True))
    print("PASS_Q6_M7_CELLU_RESTRICTED_WALL")


if __name__ == "__main__":
    main()

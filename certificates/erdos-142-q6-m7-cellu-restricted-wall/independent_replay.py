#!/usr/bin/env python3
"""Independent stdlib-only replay of Terra's q6/M7 cell-U ray.

This file intentionally reconstructs the packet rather than importing any
Terra code.  Coordinates are q6 coarse points; the local costs are derived
from the half-open residual interval xi+zeta-2*eta in (-2,2).
"""
import copy
import hashlib
import itertools
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CERT_PATH = ROOT / "certificate.json"

Q = D = 6
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
GROUPS = {
    0: (15, 30, 46, 51, 53, 57), 1: (15, 54, 57), 2: (7, 56),
    3: (3, 60), 4: (7, 56), 5: (12, 17, 34),
    6: (3, 12, 17, 18, 36, 40),
}
CELLS = tuple((word, residue) for residue in range(7) for word in GROUPS[residue])
POINTS = tuple(itertools.product(range(Q), repeat=2))
PID = {p: i for i, p in enumerate(POINTS)}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def support(bit):
    if bit == 0:
        return frozenset(BASE)
    return frozenset((Q - 1 - x, y) for x, y in BASE)


SUPPORTS = (support(0), support(1))


def parity(p):
    return (p[0] + p[1]) & 1


def patterns(weight):
    return tuple(p for p in itertools.product(range(2), repeat=D) if sum(p) == weight)


STATES = tuple((cell, pattern)
               for cell, (_, residue) in enumerate(CELLS)
               for pattern in patterns(residue))
STATE_ID = {state: i for i, state in enumerate(STATES)}


def scalar_from_half_open_interval(a, b, c):
    """Exact 3-scaled supremum of -(4*y*k+k^2), or None.

    Put x=(a+xi)/6, y=(b+eta)/6, z=(c+zeta)/6 and
    x+z-2y=k.  Then residual e=xi+zeta-2eta=6k-(a+c-2b).
    The half-open box gives eta in [max(0,-e/2), min(1,1-e/2)) in
    the endpoint/supremum sense.  This derives the cost without copying a
    source implementation.
    """
    defect = a + c - 2 * b
    answer = None
    for k in (-1, 0, 1):
        e = 6 * k - defect
        if e not in (-1, 0, 1):
            continue
        eta_inf = max(Fraction(0), -Fraction(e, 2))
        eta_sup = min(Fraction(1), Fraction(2 - e, 2))
        if k == 0:
            value = Fraction(0)
        elif k < 0:
            value = -2 * (b + eta_sup) * k - 3 * k * k
        else:
            value = -2 * (b + eta_inf) * k - 3 * k * k
        assert value.denominator == 1
        answer = int(value)
        break
    return answer


def state_cost(a, b, c):
    """Exact selected-row RHS from its three six-bit state witnesses."""
    ca, pa = STATES[a]
    cb, pb = STATES[b]
    cc, pc = STATES[c]
    return ca, cb, cc, pa, pb, pc


def check_record(rec, physical_agg, feature_agg, local_agg, state_agg):
    assert len(rec["state_ids"]) == 3
    a, b, c = rec["state_ids"]
    assert all(isinstance(v, int) and 0 <= v < len(STATES) for v in (a, b, c))
    ca, pa = STATES[a]
    cb, pb = STATES[b]
    cc, pc = STATES[c]
    assert len(rec["x"]) == len(rec["y"]) == len(rec["z"]) == D
    rhs = 0
    vectors = []
    for i, (xi, yi, zi) in enumerate(zip(rec["x"], rec["y"], rec["z"])):
        assert all(isinstance(v, int) and 0 <= v < len(POINTS)
                   for v in (xi, yi, zi))
        X, Y, Z = POINTS[xi], POINTS[yi], POINTS[zi]
        assert X in SUPPORTS[(CELLS[ca][0] >> i) & 1]
        assert Y in SUPPORTS[(CELLS[cb][0] >> i) & 1]
        assert Z in SUPPORTS[(CELLS[cc][0] >> i) & 1]
        assert (parity(X), parity(Y), parity(Z)) == (pa[i], pb[i], pc[i])
        sx = scalar_from_half_open_interval(X[0], Y[0], Z[0])
        sy = scalar_from_half_open_interval(X[1], Y[1], Z[1])
        assert sx is not None and sy is not None
        rhs += sx + sy
        vectors.append((X, Y, Z))
        # These are the cell-position-coarse-point U coefficients.
        for cell, point, coef in ((ca, xi, 1), (cb, yi, -2), (cc, zi, 1)):
            local_agg[(cell, i, point)] += coef * rec["weight"]
    assert rhs == rec["rhs3"]
    for state, coef in ((a, 1), (b, -2), (c, 1)):
        state_agg[state] += coef * rec["weight"]

    # An unrestricted physical H sees the complete six-point 12D vertex.
    for vector, coef in ((tuple(v[0] for v in vectors), 1),
                         (tuple(v[1] for v in vectors), -2),
                         (tuple(v[2] for v in vectors), 1)):
        physical_agg[vector] += coef * rec["weight"]
        coords = tuple(t for p in vector for t in p)
        for i in range(12):
            for j in range(i, 12):
                feature_agg[(i, j)] += coef * rec["weight"] * coords[i] * coords[j]


def replay(cert):
    assert cert["format"] == "erdos142-q6-continuous-pattern-cellu-farkas-v1"
    assert cert["scope"] == "H=2norm2+G(cell,pattern)+sum_i U(cell,i,coarsepoint_i) only"
    assert len(CELLS) == 24 and len(STATES) == 148
    assert len(set(CELLS)) == 24
    assert all(len(s) == 9 for s in SUPPORTS)
    assert SUPPORTS[0].isdisjoint(SUPPORTS[1])
    physical = defaultdict(int)
    features = defaultdict(int)
    local = defaultdict(int)
    states = defaultdict(int)
    total = 0
    for rec in cert["records"]:
        assert isinstance(rec["weight"], int) and rec["weight"] > 0
        check_record(rec, physical, features, local, states)
        total += rec["rhs3"] * rec["weight"]
    assert math.gcd(*(rec["weight"] for rec in cert["records"])) == 1
    assert total == int(cert["weighted_rhs3"]) and total > 0
    assert not {k: v for k, v in states.items() if v}
    assert not {k: v for k, v in local.items() if v}
    return total, physical, features


def corruption_tests(cert):
    # Each mutation must be rejected by the independent replay.
    cases = []
    for label, mutate in (
        ("rhs", lambda d: d["records"][0].__setitem__("rhs3", d["records"][0]["rhs3"] + 1)),
        ("point", lambda d: d["records"][0]["x"].__setitem__(0, (d["records"][0]["x"][0] + 1) % 36)),
        ("state", lambda d: d["records"][0]["state_ids"].__setitem__(0, (d["records"][0]["state_ids"][0] + 1) % 148)),
        ("weight", lambda d: d["records"][0].__setitem__("weight", d["records"][0]["weight"] + 1)),
    ):
        bad = copy.deepcopy(cert)
        mutate(bad)
        try:
            replay(bad)
        except (AssertionError, ValueError, KeyError, TypeError):
            cases.append(label)
        else:
            raise AssertionError("planted corruption escaped: " + label)
    return cases


def main():
    cert = json.loads(CERT_PATH.read_text())
    total, physical, features = replay(cert)
    corruptions = corruption_tests(cert)
    # Integer-coordinate feature sums are exact.  Normalized real q6
    # coordinates are obtained by dividing every coefficient by 6^2=36.
    physical_nonzero = {k: v for k, v in physical.items() if v}
    feature_nonzero = {k: v for k, v in features.items() if v}
    report = {
        "certificate_sha256": sha256(CERT_PATH),
        "rows": len(cert["records"]),
        "states": len(STATES),
        "cells": len(CELLS),
        "weighted_rhs3": str(total),
        "weights_positive": all(r["weight"] > 0 for r in cert["records"]),
        "weight_gcd": 1,
        "state_and_cellu_cancellation": True,
        "unrestricted_physical_vertices": len(physical_nonzero),
        "quadratic_monomials": 78,
        "nonzero_integer_coordinate_quadratics": len(feature_nonzero),
        "quadratic_ray_cancels": not feature_nonzero,
        "planted_corruptions_rejected": corruptions,
        "physical_vertex_aggregate_sha256": hashlib.sha256(
            json.dumps(sorted((list(k), str(v)) for k, v in physical_nonzero.items()),
                       separators=(",", ":")).encode()).hexdigest().upper(),
        "physical_vertex_aggregate": {
            ";".join(f"{x},{y}" for x, y in key): str(value)
            for key, value in sorted(physical_nonzero.items())
        },
        "quadratic_aggregate": {f"{i},{j}": str(v) for (i, j), v in sorted(feature_nonzero.items())},
        "quadratic_aggregate_all_78": {
            f"{i},{j}": str(features.get((i, j), 0))
            for i in range(12) for j in range(i, 12)
        },
        "quadratic_aggregate_normalized_real_q6": {
            f"{i},{j}": f"{v}/36" for (i, j), v in sorted(feature_nonzero.items())
        },
        "scope": "Exact obstruction only for H=2||x||^2+G(cell,pattern)+sum_i U(cell,i,coarsepoint_i); nonzero physical/quadratic aggregates mean this ray does not obstruct unrestricted H or a general global quadratic correction.",
    }
    out = Path(__file__).with_name("audit_report.json")
    expected = json.loads(out.read_text())
    assert report == expected, "committed audit_report.json is stale or corrupted"
    print(json.dumps({k: v for k, v in report.items() if k not in ("quadratic_aggregate", "quadratic_aggregate_all_78", "quadratic_aggregate_normalized_real_q6", "physical_vertex_aggregate")}, indent=2))
    print("PASS_INDEPENDENT_CELLU_AUDIT")


if __name__ == "__main__":
    main()

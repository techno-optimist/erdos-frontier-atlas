#!/usr/bin/env python3
"""Exact replay for the q=4,5,6,7 full-cell affine-quadratic capacities.

The trusted path is Python's standard library and integer arithmetic only.
Discovery optimizers are intentionally absent.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import tempfile
from collections import Counter
from functools import reduce
from itertools import product
from math import gcd
from pathlib import Path


HERE = Path(__file__).resolve().parent
CAPACITIES = {4: 4, 5: 5, 6: 9, 7: 10}

# Twice the vertices (u,w,v) of
#   {(u,w,v) in [0,1]^3 : u+w-2v=residual}.
VERTICES_X2 = {
    -1: ((0, 0, 1), (0, 2, 2), (2, 0, 2)),
    0: ((0, 0, 0), (0, 2, 1), (2, 0, 1), (2, 2, 2)),
    1: ((0, 2, 0), (2, 0, 0), (2, 2, 1)),
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def residual_vertex_audit():
    need({key: len(value) for key, value in VERTICES_X2.items()}
         == {-1: 3, 0: 4, 1: 3}, "bad residual vertex census")
    for residual, vertices in VERTICES_X2.items():
        for u, w, v in vertices:
            need(u + w - 2 * v == 2 * residual,
                 ("bad residual vertex", residual, (u, w, v)))
            need(all(value in (0, 1, 2) for value in (u, w, v)),
                 "bad twice-coordinate")

    # Exact inward points (denominator 20) prove every closure vertex is a
    # limit of points in the corresponding half-open residual polytope.
    inward = {
        (0, (0, 0, 0)): (0, 0, 0),
        (0, (0, 2, 1)): (0, 18, 9),
        (0, (2, 0, 1)): (18, 0, 9),
        (0, (2, 2, 2)): (18, 18, 18),
        (1, (0, 2, 0)): (2, 18, 0),
        (1, (2, 0, 0)): (18, 2, 0),
        (1, (2, 2, 1)): (18, 18, 8),
        (-1, (0, 0, 1)): (0, 0, 10),
        (-1, (0, 2, 2)): (0, 18, 19),
        (-1, (2, 0, 2)): (18, 0, 19),
    }
    for (residual, vertex), point in inward.items():
        u, w, v = point
        need(u + w - 2 * v == 20 * residual,
             ("bad inward residual", residual, vertex, point))
        need(all(0 <= value < 20 for value in point),
             ("inward point leaves half-open cube", point))


def exact_ledger(q):
    """Rebuild twice the scaled affine defect with integers."""
    points = tuple(product(range(q), repeat=2))
    point_index = {point: i for i, point in enumerate(points)}
    rows = []
    for ix, x in enumerate(points):
        for iz in range(ix, len(points)):
            z = points[iz]
            choices = []
            for coordinate in range(2):
                options = []
                for middle_digit in range(q):
                    digit_defect = x[coordinate] + z[coordinate] - 2 * middle_digit
                    residuals = [
                        q * carry - digit_defect for carry in range(-2, 3)
                        if q * carry - digit_defect in VERTICES_X2
                    ]
                    need(len(residuals) <= 1, "ambiguous physical carry")
                    if residuals:
                        options.append((middle_digit, residuals[0]))
                choices.append(options)
            for first, second in product(*choices):
                middle = (first[0], second[0])
                residuals = (first[1], second[1])
                iy = point_index[middle]
                for vertices in product(VERTICES_X2[residuals[0]],
                                        VERTICES_X2[residuals[1]]):
                    coefficients = {}

                    def add(key, value):
                        coefficients[key] = coefficients.get(key, 0) + value

                    add(("h", ix, 0), 2)
                    add(("h", iz, 0), 2)
                    add(("h", iy, 0), -4)
                    constant = 0
                    for coordinate, (u2, w2, v2) in enumerate(vertices):
                        digit_difference = x[coordinate] - z[coordinate]
                        add(("p", ix, coordinate), u2)
                        add(("p", iz, coordinate), w2)
                        add(("p", iy, coordinate), -2 * v2)
                        numerator = (
                            2 * (u2 * u2 + w2 * w2 - 2 * v2 * v2)
                            - (2 * digit_difference + u2 - w2) ** 2
                        )
                        need(numerator % 2 == 0, "nonintegral scaled constant")
                        constant += numerator // 2
                    rows.append((ix, iy, iz, coefficients, constant,
                                 residuals, vertices))
    return points, tuple(rows)


def verify_packet(item, rows, nvertices):
    support = tuple(int(value) for value in item["support"])
    need(support and support == tuple(sorted(support)), "unsorted packet support")
    need(len(set(support)) == len(support)
         and all(0 <= value < nvertices for value in support),
         "invalid packet support")
    support_set = set(support)
    coefficients = {}
    constant = 0
    weights = []
    used_rows = set()
    for entry in item["entries"]:
        row_number = int(entry["ledger_row"])
        weight = int(entry["weight"])
        need(0 <= row_number < len(rows) and weight > 0,
             "invalid packet entry")
        need(row_number not in used_rows, "duplicate row in packet")
        used_rows.add(row_number)
        row = rows[row_number]
        need(tuple(map(int, entry["triple"])) == row[:3],
             "packet triple does not match ledger")
        need(set(row[:3]) <= support_set, "packet row escapes its support")
        for key, value in row[3].items():
            coefficients[key] = coefficients.get(key, 0) + weight * value
        constant += weight * row[4]
        weights.append(weight)
    need(weights and reduce(gcd, weights) == 1,
         "packet weights are not positive primitive integers")
    need(all(value == 0 for value in coefficients.values()),
         "packet does not cancel every height and slope")
    need(constant == int(item["constant_defect"]) and constant < 0,
         "packet constant is not the certified negative defect")
    return frozenset(support), len(weights), constant


def verify_upper_packet(path, q, rows, points):
    payload = json.loads(path.read_text(encoding="utf-8"))
    need(payload.get("schema") == "affine-quadratic-cegar-farkas-v2",
         "unexpected upper-bound packet schema")
    need(int(payload["q"]) == q and int(payload["target"]) == CAPACITIES[q] + 1,
         "wrong q or target in upper-bound packet")
    need(int(payload["ledger_rows"]) == len(rows), "ledger-row census drift")
    need(payload.get("failures") == [], "packet contains unexactified cuts")
    if "vertex_order" in payload:
        need(payload["vertex_order"] == [list(point) for point in points],
             "vertex order drift")

    edges = []
    packet_sizes = []
    defects = []
    for item in payload["certified_cuts"]:
        edge, size, defect = verify_packet(item, rows, len(points))
        edges.append(edge)
        packet_sizes.append(size)
        defects.append(defect)
    need(edges and len(set(edges)) == len(edges), "duplicate certified support")
    if "distinct_cuts" in payload:
        need(int(payload["distinct_cuts"]) == len(edges), "cut-count drift")
    return tuple(edges), packet_sizes, defects, payload


def find_compiler():
    for name in ("g++", "c++", "clang++"):
        found = shutil.which(name)
        if found:
            return found
    raise AssertionError("a C++17 compiler is required for the coverage replay")


def build_fixed_order_replay(directory):
    source = HERE / "fixed_order_replay.cpp"
    need(source.is_file(), "missing fixed-order Boolean source")
    executable = Path(directory) / ("fixed_order_replay.exe" if os.name == "nt"
                                    else "fixed_order_replay")
    result = subprocess.run([find_compiler(), "-O3", "-std=c++17", "-o",
                             str(executable), str(source)],
                            text=True, capture_output=True, timeout=120)
    need(result.returncode == 0, result.stdout + result.stderr)
    return executable


def fixed_order_cover(executable, q, target, nvertices, edges):
    lines = [f"{q} {target} {nvertices} {len(edges)}"]
    lines.extend(f"{len(edge)} " + " ".join(map(str, sorted(edge)))
                 for edge in edges)
    result = subprocess.run([str(executable)], input="\n".join(lines) + "\n",
                            text=True, capture_output=True, timeout=180)
    need(result.returncode == 0, result.stdout + result.stderr)
    need(f"CAPACITY_AT_MOST {target - 1}" in result.stdout
         and "PASS fixed-order exhaustive Boolean wall" in result.stdout,
         "fixed-order Boolean verdict drift")
    metrics = {}
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[1].isdigit():
            metrics[fields[0]] = int(fields[1])
    return (metrics["SEARCH_NODES"], metrics["EDGE_PRUNES"],
            metrics["CARDINALITY_PRUNES"])


def verify_candidate(candidate, q, points, rows):
    need(int(candidate["q"]) == q, "candidate q mismatch")
    support_points = tuple(tuple(map(int, point)) for point in candidate["support"])
    index = {point: i for i, point in enumerate(points)}
    need(all(point in index for point in support_points), "candidate cell outside grid")
    support = tuple(index[point] for point in support_points)
    need(support == tuple(sorted(support)) and len(set(support)) == len(support),
         "candidate support is not sorted and distinct")
    need(len(support) == CAPACITIES[q], "candidate has wrong cardinality")
    raw_values = candidate["integer_values"]
    need(all(isinstance(value, int) and not isinstance(value, bool)
             for value in raw_values), "candidate values are not integers")
    values = tuple(raw_values)
    need(len(values) == 3 * len(support), "candidate coefficient count mismatch")
    variables = {}
    for local, cell in enumerate(support):
        variables[("h", cell, 0)] = values[3 * local]
        variables[("p", cell, 0)] = values[3 * local + 1]
        variables[("p", cell, 1)] = values[3 * local + 2]
    support_set = set(support)
    active = 0
    minimum = None
    for row in rows:
        if not set(row[:3]) <= support_set:
            continue
        slack = row[4] + sum(coefficient * variables[key]
                             for key, coefficient in row[3].items())
        need(slack >= 0, ("candidate violates a continuum row", q, active, slack))
        active += 1
        minimum = slack if minimum is None else min(minimum, slack)
    need(active == int(candidate["active_rows"]),
         ("candidate active-row census drift", active, candidate["active_rows"]))
    need(minimum == int(candidate["minimum_integer_slack"]),
         "candidate minimum slack drift")
    return active, minimum


def half_period_audit(q, rows, points):
    if q % 2:
        return 0, 0
    signatures = Counter(row[:3] for row in rows)
    index = {point: i for i, point in enumerate(points)}
    total = nontrivial = 0
    half = q // 2
    for ix, point in enumerate(points):
        for mask in product((0, 1), repeat=2):
            middle = tuple((point[j] + mask[j] * half) % q for j in range(2))
            count = signatures[(ix, index[middle], ix)]
            need(count == 16, ("missing x=z half-period branch", q, point, mask))
            total += count
            if any(mask):
                nontrivial += count
    return total, nontrivial


def expect_rejected(label, thunk):
    try:
        thunk()
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError("planted failure was accepted: " + label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    residual_vertex_audit()
    candidates = json.loads((HERE / "candidates.json").read_text(encoding="utf-8"))
    need(candidates.get("schema") == "affine-quadratic-exact-candidates-v1",
         "unexpected candidate packet schema")

    temporary = tempfile.TemporaryDirectory(prefix="e142-fixed-order-")
    boolean_replay = build_fixed_order_replay(temporary.name)
    summaries = {}
    for q, capacity in CAPACITIES.items():
        points, rows = exact_ledger(q)
        edges, packet_sizes, defects, packet = verify_upper_packet(
            HERE / f"upper_q{q}.json", q, rows, points)
        nodes, edge_prunes, cardinality_prunes = fixed_order_cover(
            boolean_replay, q, capacity + 1, len(points), edges)
        active, minimum = verify_candidate(candidates["candidates"][str(q)],
                                           q, points, rows)
        half_rows, nontrivial_half = half_period_audit(q, rows, points)
        need(24 * capacity < 7 * q * q, "capacity does not lie below 7/24")

        if args.self_test and q == 4:
            bad_packet = copy.deepcopy(packet["certified_cuts"][0])
            bad_packet["entries"][0]["weight"] = 0
            expect_rejected("zero Farkas weight",
                            lambda: verify_packet(bad_packet, rows, len(points)))
            bad_candidate = copy.deepcopy(candidates["candidates"]["4"])
            bad_candidate["support"][1] = bad_candidate["support"][0]
            expect_rejected("duplicate candidate cell",
                            lambda: verify_candidate(bad_candidate, 4, points, rows))

        summaries[str(q)] = {
            "capacity": capacity,
            "density": f"{capacity}/{q*q}",
            "target_ruled_out": capacity + 1,
            "ledger_rows": len(rows),
            "farkas_packets": len(edges),
            "edge_sizes": dict(sorted(Counter(map(len, edges)).items())),
            "packet_row_range": [min(packet_sizes), max(packet_sizes)],
            "defect_range": [min(defects), max(defects)],
            "boolean_nodes": nodes,
            "edge_prunes": edge_prunes,
            "cardinality_prunes": cardinality_prunes,
            "candidate_active_rows": active,
            "candidate_minimum_slack": minimum,
            "half_period_rows": half_rows,
            "nontrivial_x_eq_z_rows": nontrivial_half,
        }
    temporary.cleanup()

    if args.self_test:
        print("PLANTED_FAILURES_REJECTED 2")
    print(json.dumps({"capacities": summaries,
                      "fixed_hessian_full_cell_scope": True,
                      "arbitrary_potential_claim": False,
                      "new_r3_bound": False,
                      "erdos142_solved": False}, sort_keys=True))
    print("PASS_Q4_Q7_AFFINE_QUADRATIC_EXACT_CAPACITIES")


if __name__ == "__main__":
    main()

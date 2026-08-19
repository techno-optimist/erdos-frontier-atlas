#!/usr/bin/env python3
"""Hostile replay of the small-q affine-quadratic capacity theorem.

This file imports neither ``verify.py`` nor any discovery module.  It uses a
dense variable encoding and enumerates middle cells directly.  A separately
compiled C++17 backtracker audits the Boolean coverage step.
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
from itertools import product
from math import gcd
from pathlib import Path


BASE = Path(__file__).resolve().parent
CAP = {4: 4, 5: 5, 6: 9, 7: 10}
POLYTOPE = {
    -1: ((0, 0, 1), (0, 2, 2), (2, 0, 2)),
    0: ((0, 0, 0), (0, 2, 1), (2, 0, 1), (2, 2, 2)),
    1: ((0, 2, 0), (2, 0, 0), (2, 2, 1)),
}


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def add(vector, variable, coefficient):
    vector[variable] = vector.get(variable, 0) + coefficient


def rebuild(q):
    """Direct-center enumeration with dense h,p variable numbers."""
    cells = tuple((a, b) for a in range(q) for b in range(q))
    number = {cell: i for i, cell in enumerate(cells)}
    rows = []
    for left_number, left in enumerate(cells):
        for right_number in range(left_number, len(cells)):
            right = cells[right_number]
            for middle in cells:
                residual = []
                for coordinate in range(2):
                    defect = (left[coordinate] + right[coordinate]
                              - 2 * middle[coordinate])
                    matches = [r for r in (-1, 0, 1)
                               if (defect + r) % q == 0]
                    if len(matches) != 1:
                        residual = []
                        break
                    residual.append(matches[0])
                if not residual:
                    continue
                middle_number = number[middle]
                for local_vertices in product(POLYTOPE[residual[0]],
                                              POLYTOPE[residual[1]]):
                    vector = {}
                    add(vector, 3 * left_number, 2)
                    add(vector, 3 * right_number, 2)
                    add(vector, 3 * middle_number, -4)
                    constant = 0
                    for coordinate, (u2, w2, v2) in enumerate(local_vertices):
                        add(vector, 3 * left_number + 1 + coordinate, u2)
                        add(vector, 3 * right_number + 1 + coordinate, w2)
                        add(vector, 3 * middle_number + 1 + coordinate, -2 * v2)
                        delta2 = (2 * (left[coordinate] - right[coordinate])
                                  + u2 - w2)
                        numerator = (2 * (u2 * u2 + w2 * w2 - 2 * v2 * v2)
                                     - delta2 * delta2)
                        check(numerator % 2 == 0, "nonintegral row constant")
                        constant += numerator // 2
                    rows.append((left_number, middle_number, right_number,
                                 tuple(sorted((key, value) for key, value in vector.items()
                                              if value)), constant,
                                 tuple(residual), local_vertices))
    return cells, tuple(rows)


def packet_check(item, rows, n):
    support = tuple(int(x) for x in item["support"])
    check(support == tuple(sorted(set(support)))
          and support and all(0 <= x < n for x in support),
          "bad forbidden support")
    allowed = set(support)
    total = Counter()
    constant = 0
    weights = []
    used = set()
    for term in item["entries"]:
        row_id = int(term["ledger_row"])
        weight = int(term["weight"])
        check(0 <= row_id < len(rows) and weight > 0 and row_id not in used,
              "bad weighted row")
        used.add(row_id)
        row = rows[row_id]
        check(tuple(map(int, term["triple"])) == row[:3], "row semantic mismatch")
        check(set(row[:3]) <= allowed, "row leaves forbidden support")
        for variable, coefficient in row[3]:
            total[variable] += weight * coefficient
        constant += weight * row[4]
        weights.append(weight)
    check(weights and gcd(*weights) == 1, "nonprimitive Farkas packet")
    check(all(value == 0 for value in total.values()),
          "dense coefficients did not cancel")
    check(constant == int(item["constant_defect"]) < 0,
          "wrong Farkas constant")
    return support


def candidate_check(item, q, cells, rows):
    check(int(item["q"]) == q, "candidate q drift")
    cell_number = {cell: i for i, cell in enumerate(cells)}
    selected_cells = tuple(tuple(map(int, cell)) for cell in item["support"])
    check(all(cell in cell_number for cell in selected_cells), "outside candidate cell")
    selected = tuple(cell_number[cell] for cell in selected_cells)
    check(selected == tuple(sorted(set(selected))) and len(selected) == CAP[q],
          "bad candidate support")
    raw_values = item["integer_values"]
    check(all(isinstance(value, int) and not isinstance(value, bool)
              for value in raw_values), "candidate coefficient is not an integer")
    check(len(raw_values) == 3 * len(selected), "candidate coefficient census")
    variables = {}
    for local, cell in enumerate(selected):
        variables[3 * cell] = raw_values[3 * local]
        variables[3 * cell + 1] = raw_values[3 * local + 1]
        variables[3 * cell + 2] = raw_values[3 * local + 2]
    selected = set(selected)
    active = 0
    minimum = None
    for row in rows:
        if not set(row[:3]) <= selected:
            continue
        slack = row[4] + sum(coefficient * variables[variable]
                             for variable, coefficient in row[3])
        check(slack >= 0, ("lower witness fails", q, active, slack))
        minimum = slack if minimum is None else min(minimum, slack)
        active += 1
    check(active == int(item["active_rows"]), "candidate row-count drift")
    check(minimum == int(item["minimum_integer_slack"]), "candidate slack drift")
    return active, minimum


def compiler():
    for name in ("g++", "c++", "clang++"):
        found = shutil.which(name)
        if found:
            return found
    raise AssertionError("a C++17 compiler is required for the independent replay")


def hypergraph_text(q, target, n, supports):
    lines = [f"{q} {target} {n} {len(supports)}"]
    lines.extend(f"{len(edge)} " + " ".join(map(str, edge)) for edge in supports)
    return "\n".join(lines) + "\n"


def run_boolean(executable, text):
    result = subprocess.run([str(executable)], input=text, text=True,
                            capture_output=True, timeout=180)
    return result


def reject(label, action):
    try:
        action()
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError("hostile control accepted: " + label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    candidate_packet = json.loads((BASE / "candidates.json").read_text(encoding="utf-8"))
    check(candidate_packet.get("schema") == "affine-quadratic-exact-candidates-v1",
          "candidate schema drift")

    source = BASE / "boolean_replay.cpp"
    check(source.is_file(), "missing standalone Boolean verifier")
    reports = {}
    with tempfile.TemporaryDirectory(prefix="e142-affine-capacity-") as temporary:
        executable = Path(temporary) / ("boolean_replay.exe" if os.name == "nt"
                                       else "boolean_replay")
        build = subprocess.run([compiler(), "-O3", "-std=c++17", "-o",
                                str(executable), str(source)],
                               text=True, capture_output=True, timeout=120)
        check(build.returncode == 0, build.stdout + build.stderr)

        for q, capacity in CAP.items():
            cells, rows = rebuild(q)
            packet = json.loads((BASE / f"upper_q{q}.json").read_text(encoding="utf-8"))
            check(packet.get("schema") == "affine-quadratic-cegar-farkas-v2",
                  "upper packet schema drift")
            check(int(packet["q"]) == q and int(packet["target"]) == capacity + 1,
                  "upper packet header drift")
            check(int(packet["ledger_rows"]) == len(rows), "ledger census drift")
            check(packet.get("failures") == [], "unexactified packet")
            supports = tuple(packet_check(item, rows, len(cells))
                             for item in packet["certified_cuts"])
            check(len(supports) == len(set(supports)), "duplicate packet supports")
            active, slack = candidate_check(candidate_packet["candidates"][str(q)],
                                             q, cells, rows)
            text = hypergraph_text(q, capacity + 1, len(cells), supports)
            result = run_boolean(executable, text)
            check(result.returncode == 0, result.stdout + result.stderr)
            check(f"CAPACITY_AT_MOST {capacity}" in result.stdout
                  and "PASS solver-independent exhaustive Boolean wall" in result.stdout,
                  "standalone Boolean verdict drift")

            if args.self_test and q == 4:
                damaged = copy.deepcopy(packet["certified_cuts"][0])
                damaged["entries"][0]["triple"][0] = (
                    int(damaged["entries"][0]["triple"][0]) + 1) % len(cells)
                reject("wrong ledger triple",
                       lambda: packet_check(damaged, rows, len(cells)))
                incomplete = hypergraph_text(q, capacity + 1, len(cells), supports[:1])
                failure = run_boolean(executable, incomplete)
                check(failure.returncode == 1
                      and "FAIL uncovered target support" in failure.stdout,
                      "incomplete-wall control did not fail")

            reports[str(q)] = {
                "capacity": capacity,
                "ledger_rows": len(rows),
                "packets": len(supports),
                "edge_sizes": dict(sorted(Counter(map(len, supports)).items())),
                "candidate_active_rows": active,
                "candidate_minimum_slack": slack,
                "cpp_capacity_verdict": capacity,
            }

    if args.self_test:
        print("HOSTILE_CONTROLS_REJECTED 2")
    print(json.dumps({"capacities": reports,
                      "primary_imported": False,
                      "floating_point_used": False,
                      "fixed_hessian_full_cell_scope": True,
                      "arbitrary_potential_claim": False,
                      "new_r3_bound": False,
                      "erdos142_solved": False}, sort_keys=True))
    print("PASS_INDEPENDENT_Q4_Q7_AFFINE_QUADRATIC_CAPACITY_AUDIT")


if __name__ == "__main__":
    main()

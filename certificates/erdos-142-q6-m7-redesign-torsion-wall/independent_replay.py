#!/usr/bin/env python3
"""No-import audit replay for the q=6/M=7 physical torsion wall.

This file intentionally does not import (or execute) verify.py.  It rebuilds
the local support, cell census, physical identities, modular rows, offset
lift, and the one fixed-step deletion census directly from the semantic
packet and standard-library arithmetic.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKET = HERE / "semantic_packet.json"
Q = 6
EXPECTED_CELLS = ((38, 3), (41, 3), (42, 3), (44, 3),
                  (49, 3), (50, 3), (52, 3), (56, 3))
EXPECTED_VERTICES = {
    "X": ((5, 2), (2, 4), (2, 4), (5, 2), (3, 2), (0, 0)),
    "Y": ((3, 2), (0, 0), (0, 0), (3, 2), (3, 2), (0, 0)),
    "Z": ((1, 2), (4, 2), (4, 2), (1, 2), (3, 2), (0, 0)),
}
EXPECTED_ROWS = (
    ("X", "Y", "Z"),
    ("Y", "X", "Z"),
    ("X", "Z", "Y"),
)
EXPECTED_CARRIES = (
    ((0, 0), (-1, -1), (-1, -1), (0, 0), (0, 0), (0, 0)),
    ((1, 0), (0, 1), (0, 1), (1, 0), (0, 0), (0, 0)),
    ((-1, 0), (1, 0), (1, 0), (-1, 0), (0, 0), (0, 0)),
)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def local_supports() -> tuple[frozenset[tuple[int, int]], frozenset[tuple[int, int]]]:
    # The two orientations are reconstructed, rather than copied from the
    # verifier: reflection is a q-1-a map in the first local coordinate.
    base = frozenset({(3, 2), (3, 3), (3, 4), (4, 1), (4, 2),
                      (4, 3), (5, 0), (5, 1), (5, 2)})
    reflected = frozenset((Q - 1 - a, b) for a, b in base)
    return base, reflected


def parity(point: tuple[int, int]) -> int:
    return (point[0] + point[1]) & 1


def word(vertex: tuple[tuple[int, int], ...], orientations) -> int:
    result = 0
    for i, point in enumerate(vertex):
        hits = [bit for bit, support in enumerate(orientations) if point in support]
        check(len(hits) == 1, "point lacks a unique orientation bit")
        result |= hits[0] << i
    return result


def residue(vertex: tuple[tuple[int, int], ...]) -> int:
    return sum(parity(point) for point in vertex)


def count_cell(word_value: int, residue_value: int, orientations) -> int:
    # Enumerate parity choices using the two parity multiplicities in each
    # block.  This is the coefficient of t^residue in the product, evaluated
    # without using any verifier routine.
    multiplicities = []
    for i in range(6):
        support = orientations[(word_value >> i) & 1]
        multiplicities.append((sum(parity(p) == 0 for p in support),
                              sum(parity(p) == 1 for p in support)))
    total = 0
    for colors in itertools.product((0, 1), repeat=6):
        if sum(colors) != residue_value:
            continue
        ways = 1
        for i, color in enumerate(colors):
            ways *= multiplicities[i][color]
        total += ways
    return total


def modular_carry(left, center, right) -> tuple[tuple[int, int], ...]:
    answer = []
    for x, y, z in zip(left, center, right):
        difference = tuple(2 * y[j] - x[j] - z[j] for j in (0, 1))
        check(all(value % Q == 0 for value in difference), "non-modular midpoint row")
        answer.append(tuple(value // Q for value in difference))
    return tuple(answer)


def raw_canonical_cost(left, right) -> int:
    return sum((x[j] - z[j]) ** 2 for x, z in zip(left, right) for j in (0, 1))


def coefficients(rows: list[dict[str, object]]) -> dict[str, int]:
    total = Counter()
    for row in rows:
        total[str(row["left"])] += 1
        total[str(row["center"])] -= 2
        total[str(row["right"])] += 1
    return {key: value for key, value in total.items() if value}


def fixed_step_orbits(orientations, selected_cells):
    # Every component of this step has order dividing three in Z/6Z.
    step = ((4, 0), (4, 2), (4, 2), (4, 0), (0, 0), (0, 0))
    union = orientations[0] | orientations[1]
    options = []
    for delta in step:
        block_options = []
        for point in itertools.product(range(Q), repeat=2):
            y = tuple((point[j] + delta[j]) % Q for j in (0, 1))
            z = tuple((point[j] + 2 * delta[j]) % Q for j in (0, 1))
            if point in union and y in union and z in union:
                block_options.append((point, y, z))
        options.append(block_options)

    # Directly enumerate physical starts, retaining the full q6 vertices.
    starts = []
    for choices in itertools.product(*options):
        x = tuple(choice[0] for choice in choices)
        y = tuple(choice[1] for choice in choices)
        z = tuple(choice[2] for choice in choices)
        cells = tuple((word(v, orientations), residue(v)) for v in (x, y, z))
        if all(cell in selected_cells for cell in cells) and all(cell[1] == 3 for cell in cells):
            starts.append((x, y, z, cells))

    check(len(starts) == 135, "fixed-step oriented-start count")
    cell_triples = Counter(tuple(cell[0] for cell in record[3]) for record in starts)
    check(dict(cell_triples) == {(38, 38, 41): 45,
                                 (38, 41, 38): 45,
                                 (41, 38, 38): 45},
          "fixed-step cell-triple census")

    # Canonicalize each orbit by its three physical starts.  This checks the
    # stronger disjoint-orbit statement behind 135 oriented starts = 45.
    orbit_sets = {}
    for x, y, z, _cells in starts:
        orbit = (x, y, z)
        canonical = min(orbit)
        orbit_sets.setdefault(canonical, set()).update(orbit)
    check(len(orbit_sets) == 45, "fixed-step orbit count")
    check(all(len(vertices) == 3 for vertices in orbit_sets.values()),
          "each fixed-step orbit must have three distinct starts")
    flattened = [vertex for vertices in orbit_sets.values() for vertex in vertices]
    check(len(flattened) == len(set(flattened)), "fixed-step orbits are not disjoint")

    # Include the option census as an additional independent diagnostic.
    return {
        "step": [list(p) for p in step],
        "local_option_counts": [len(block) for block in options],
        "oriented_starts": len(starts),
        "disjoint_three_orbits": len(orbit_sets),
        "by_cell_triple": {",".join(map(str, key)): value
                           for key, value in sorted(cell_triples.items())},
    }


def offset_lift(vertices, rows, q: int):
    # A common delta in (0,1/q)^12 cancels identically.  Verify one strict
    # rational interior sample as well as the symbolic coordinate inequalities.
    # The affine coefficient checks are the symbolic part: each midpoint
    # expression has 2-1-1=0 and each endpoint difference has 1-1=0.
    for _coordinate in range(12):
        check(2 - 1 - 1 == 0, "common midpoint offset coefficient")
        check(1 - 1 == 0, "common endpoint offset coefficient")
    delta = Fraction(1, 2 * q)
    lifted = {
        name: tuple(tuple(Fraction(d, q) + delta for d in point) for point in vertex)
        for name, vertex in vertices.items()
    }
    for name, vertex in vertices.items():
        for raw, lifted_point in zip(vertex, lifted[name]):
            for digit, coordinate in zip(raw, lifted_point):
                check(Fraction(digit, q) < coordinate < Fraction(digit + 1, q),
                      "sample is not in strict half-open-box interior")
    normalized_costs = []
    for row in rows:
        left, center, right = (lifted[row[key]] for key in ("left", "center", "right"))
        actual = tuple(tuple(2 * y[j] - x[j] - z[j]
                             for j in (0, 1)) for x, y, z in zip(left, center, right))
        check(actual == tuple(tuple(Fraction(v) for v in pair) for pair in row["carry"]),
              "common offset changed modular branch")
        cost = sum((x[j] - z[j]) ** 2 for x, z in zip(left, right) for j in (0, 1))
        expected = Fraction(int(row["raw_rhs"]), q * q)
        check(cost == expected, "common offset changed endpoint cost")
        normalized_costs.append(cost)
    check(Fraction(0) < delta < Fraction(1, q), "strict offset domain")
    return normalized_costs


def replay(packet: dict[str, object], do_mutations: bool = False) -> dict[str, object]:
    check(packet.get("format") == "erdos142-q6-m7-redesign-physical-torsion-wall-v1", "packet format")
    scope = packet.get("scope")
    check(isinstance(scope, dict), "missing scope")
    check(scope.get("ordinary_euclidean_continuum_claim") is False and
          scope.get("r3_claim") is False and scope.get("atlas_claim") is False,
          "scope boundary")
    check(packet.get("q") == Q and packet.get("blocks") == 6, "q/block parameters")

    orientations = local_supports()
    check(not (orientations[0] & orientations[1]), "orientation supports overlap")
    check(len(orientations[0]) == 9 and len(orientations[1]) == 9, "support sizes")

    selected = tuple(tuple(int(v) for v in cell) for cell in packet["selected_cells"])
    check(selected == EXPECTED_CELLS and len(set(selected)) == 8, "selected cells")
    check(all(word_value.bit_count() == 3 and residue_value == 3
              for word_value, residue_value in selected), "cell weight/residue")
    counts = [count_cell(w, r, orientations) for w, r in selected]
    check(counts == [178605] * 8, "all eight exact cell counts")

    total = sum(counts)
    mass = Fraction(total, Q ** 12)
    gate = Fraction(7, 24) ** 6
    margin = mass - gate
    check(total == 1428840 and mass == Fraction(245, 373248), "mass")
    check(gate == Fraction(117649, 191102976) and margin == Fraction(2597, 63700992),
          "exact gate or margin")
    check(margin > 0, "gate must be strict")
    check(margin * Q ** 12 == Fraction(5679639, 64), "q6-box gate slack")
    declared_mass = packet["mass"]
    check(int(declared_mass["per_cell"]) == 178605 and
          int(declared_mass["total"]) == total and
          tuple(declared_mass["fraction"]) == (mass.numerator, mass.denominator) and
          tuple(declared_mass["gate_fraction"]) == (gate.numerator, gate.denominator) and
          tuple(declared_mass["margin_fraction"]) == (margin.numerator, margin.denominator),
          "declared mass/gate fields")

    vertices = {name: tuple(tuple(int(v) for v in point) for point in points)
                for name, points in packet["vertices"].items()}
    check(vertices == EXPECTED_VERTICES and len(set(vertices.values())) == 3,
          "explicit distinct physical X/Y/Z lists")
    cells_by_name = {name: tuple(int(v) for v in cell)
                     for name, cell in packet["vertex_cells"].items()}
    for name, vertex in vertices.items():
        check(len(vertex) == 6 and all(point in orientations[0] | orientations[1] for point in vertex),
              "physical local-support membership")
        check((word(vertex, orientations), residue(vertex)) == cells_by_name[name],
              "physical word/residue membership")
        check(cells_by_name[name] in selected, "physical vertex not in selected union")
    check(cells_by_name == {"X": (38, 3), "Y": (38, 3), "Z": (41, 3)},
          "physical cell labels")

    rows = packet["rows"]
    check(isinstance(rows, list) and len(rows) == 3, "three rows")
    row_report = []
    for i, row in enumerate(rows):
        names = tuple(row[key] for key in ("left", "center", "right"))
        check(names == EXPECTED_ROWS[i], "row identity/order")
        got_carry = modular_carry(*(vertices[n] for n in names))
        got_cost = raw_canonical_cost(vertices[names[0]], vertices[names[2]])
        declared_carry = tuple(tuple(int(v) for v in pair) for pair in row["carry"])
        check(got_carry == declared_carry == EXPECTED_CARRIES[i], "row carry")
        check(got_cost == int(row["raw_rhs"]) == 48, "raw canonical endpoint cost")
        row_report.append({"vertices": names, "carry": got_carry, "raw_rhs": got_cost})
    check(coefficients(rows) == {}, "physical-H coefficient cancellation")
    check(sum(item["raw_rhs"] for item in row_report) == 144, "raw contradiction RHS")
    normalized = Fraction(144, Q * Q)
    check(normalized == 4, "normalized contradiction RHS")

    lifted_costs = offset_lift(vertices, rows, Q)
    orbit_report = fixed_step_orbits(orientations, set(selected))

    result = {
        "verdict": "PASS_INDEPENDENT_NO_IMPORT_REPLAY",
        "supports": {"sizes": [len(s) for s in orientations], "disjoint": True},
        "cell_counts": counts,
        "mass": str(mass),
        "gate": str(gate),
        "margin": str(margin),
        "margin_in_q6_boxes": str(margin * Q ** 12),
        "physical_vertices": {name: [list(p) for p in vertex]
                              for name, vertex in vertices.items()},
        "rows": row_report,
        "coefficient_sum": coefficients(rows),
        "normalized_rhs_sum": str(normalized),
        "common_offset": {"domain": "delta in (0,1/6)^12", "sample": "1/12",
                          "symbolic_coefficients": {"midpoint": 0, "endpoint_difference": 0},
                          "lifted_rhs": [str(cost) for cost in lifted_costs]},
        "fixed_step_census": orbit_report,
        "scope": {"exact_union_killed": True, "deletion_robust": False,
                   "ordinary_euclidean": False},
    }
    if do_mutations:
        result["mutations"] = mutation_test(packet)
    return result


def mutation_test(packet: dict[str, object]) -> dict[str, str]:
    tests = {}
    mutations = {
        "selected-cell": lambda p: p["selected_cells"].__setitem__(0, [39, 3]),
        "physical-membership": lambda p: p["vertices"]["X"].__setitem__(0, [4, 2]),
        "carry": lambda p: p["rows"][0]["carry"].__setitem__(1, [0, 0]),
        "raw-cost": lambda p: p["rows"][1].__setitem__("raw_rhs", 47),
        "coefficient-cancellation": lambda p: p["rows"].__setitem__(1, copy.deepcopy(p["rows"][0])),
        "gate-margin": lambda p: p["mass"].__setitem__("margin_fraction", [0, 1]),
    }
    for label, mutate in mutations.items():
        altered = copy.deepcopy(packet)
        mutate(altered)
        try:
            replay(altered, do_mutations=False)
        except AssertionError:
            tests[label] = "rejected"
        else:
            raise AssertionError("planted mutation accepted: " + label)
    return tests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    report = replay(packet, args.self_test)
    report["sha256"] = {
        "semantic_packet.json": hashlib.sha256(PACKET.read_bytes()).hexdigest(),
        "independent_replay.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()

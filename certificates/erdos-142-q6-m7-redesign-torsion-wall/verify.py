#!/usr/bin/env python3
"""Stdlib verifier for the M7 redesign's physical q6 torsion wall.

The wall is intentionally branch-sensitive: it is valid on the q6 quotient,
and on its half-open-box torus lift, but is not an ordinary Euclidean
continuum midpoint theorem.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKET_PATH = HERE / "semantic_packet.json"


def fail(message: str) -> None:
    raise AssertionError(message)


def base_support(q: int) -> frozenset[tuple[int, int]]:
    if q != 6:
        fail("this semantic packet is q=6")
    return frozenset({(3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3), (5, 0), (5, 1), (5, 2)})


def supports(q: int) -> tuple[frozenset[tuple[int, int]], frozenset[tuple[int, int]]]:
    base = base_support(q)
    return base, frozenset((q - 1 - a, b) for a, b in base)


def parity(point: tuple[int, int]) -> int:
    return (point[0] + point[1]) & 1


def word_of(vertex: tuple[tuple[int, int], ...], local_supports: tuple[frozenset[tuple[int, int]], ...]) -> int:
    word = 0
    for position, point in enumerate(vertex):
        memberships = [bit for bit, support in enumerate(local_supports) if point in support]
        if len(memberships) != 1:
            fail("physical point does not have one orientation bit")
        word |= memberships[0] << position
    return word


def residue_of(vertex: tuple[tuple[int, int], ...]) -> int:
    return sum(parity(point) for point in vertex)


def cell_count(word: int, residue: int, local_supports: tuple[frozenset[tuple[int, int]], ...]) -> int:
    counts = []
    for position in range(6):
        support = local_supports[(word >> position) & 1]
        counts.append(tuple(sum(parity(point) == bit for point in support) for bit in (0, 1)))
    total = 0
    for colors in itertools.product((0, 1), repeat=6):
        if sum(colors) == residue:
            product = 1
            for position, color in enumerate(colors):
                product *= counts[position][color]
            total += product
    return total


def carry(left: tuple[tuple[int, int], ...], center: tuple[tuple[int, int], ...], right: tuple[tuple[int, int], ...], q: int) -> tuple[tuple[int, int], ...]:
    answer = []
    for x, y, z in zip(left, center, right):
        values = (2 * y[0] - x[0] - z[0], 2 * y[1] - x[1] - z[1])
        if values[0] % q or values[1] % q:
            fail("row is not a modular midpoint")
        answer.append((values[0] // q, values[1] // q))
    return tuple(answer)


def raw_cost(left: tuple[tuple[int, int], ...], right: tuple[tuple[int, int], ...]) -> int:
    return sum((a - b) ** 2 for x, z in zip(left, right) for a, b in zip(x, z))


def row_coefficients(row: dict[str, object]) -> dict[str, int]:
    answer: dict[str, int] = defaultdict(int)
    answer[str(row["left"])] += 1
    answer[str(row["center"])] -= 2
    answer[str(row["right"])] += 1
    return {key: value for key, value in answer.items() if value}


def aggregate_coefficients(rows: list[dict[str, object]]) -> dict[str, int]:
    answer: dict[str, int] = defaultdict(int)
    for row in rows:
        for key, value in row_coefficients(row).items():
            answer[key] += value
    return {key: value for key, value in answer.items() if value}


def fixed_step_census(local_supports: tuple[frozenset[tuple[int, int]], ...], selected_cells: tuple[tuple[int, int], ...]) -> dict[str, object]:
    """Count the specific order-three step containing the displayed wall.

    This is a factor DP, not a claim to enumerate every order-three step.  It
    documents why this one wall is not a deletion-robust fence.
    """
    q = 6
    step = ((4, 0), (4, 2), (4, 2), (4, 0), (0, 0), (0, 0))
    union = local_supports[0] | local_supports[1]
    local_options = []
    for delta in step:
        options = []
        for point in itertools.product(range(q), repeat=2):
            next_point = tuple((point[i] + delta[i]) % q for i in range(2))
            final_point = tuple((point[i] + 2 * delta[i]) % q for i in range(2))
            if point in union and next_point in union and final_point in union:
                options.append((
                    word_of((point,), local_supports), word_of((next_point,), local_supports), word_of((final_point,), local_supports),
                    parity(point), parity(next_point), parity(final_point),
                ))
        local_options.append(options)
    dp: dict[tuple[int, int, int, int, int, int], int] = {(0, 0, 0, 0, 0, 0): 1}
    for position, options in enumerate(local_options):
        next_dp: dict[tuple[int, int, int, int, int, int], int] = defaultdict(int)
        for (wx, wy, wz, rx, ry, rz), count in dp.items():
            for bx, by, bz, px, py, pz in options:
                key = (wx | (bx << position), wy | (by << position), wz | (bz << position), rx + px, ry + py, rz + pz)
                if max(key[3:]) <= 3:
                    next_dp[key] += count
        dp = next_dp
    selected_words = {word for word, residue in selected_cells if residue == 3}
    by_cells: dict[tuple[int, int, int], int] = defaultdict(int)
    for (wx, wy, wz, rx, ry, rz), count in dp.items():
        if (wx, wy, wz) and wx in selected_words and wy in selected_words and wz in selected_words and (rx, ry, rz) == (3, 3, 3):
            by_cells[(wx, wy, wz)] += count
    oriented_starts = sum(by_cells.values())
    expected = {(38, 38, 41): 45, (38, 41, 38): 45, (41, 38, 38): 45}
    if dict(by_cells) != expected or oriented_starts != 135 or oriented_starts % 3:
        fail("fixed-step factor-DP census")
    return {
        "step": [list(point) for point in step],
        "local_option_counts": [len(options) for options in local_options],
        "oriented_starts": oriented_starts,
        "disjoint_three_orbits_for_this_fixed_step": oriented_starts // 3,
        "by_cell_triple": {"%d,%d,%d" % key: value for key, value in sorted(by_cells.items())},
    }


def check_offset_lift(vertices: dict[str, tuple[tuple[int, int], ...]], rows: list[dict[str, object]], q: int) -> None:
    # A symbolic common delta lies in the open cube (0,1/q)^12.  Strict box
    # membership follows coordinatewise; delta cancels from every carry and
    # from each endpoint difference.  A rational sample is also evaluated.
    sample = Fraction(1, 2 * q)
    lifted = {
        name: tuple(tuple(Fraction(digit, q) + sample for digit in point) for point in vertex)
        for name, vertex in vertices.items()
    }
    for name, vertex in vertices.items():
        for base_point, lifted_point in zip(vertex, lifted[name]):
            for digit, coordinate in zip(base_point, lifted_point):
                if not Fraction(digit, q) < coordinate < Fraction(digit + 1, q):
                    fail("rational common offset is not strict box interior")
    for row in rows:
        left, center, right = (lifted[str(row[key])] for key in ("left", "center", "right"))
        expected = tuple(tuple(Fraction(value, 1) for value in pair) for pair in row["carry"])
        actual = tuple(tuple(2 * y[j] - x[j] - z[j] for j in range(2)) for x, y, z in zip(left, center, right))
        if actual != expected:
            fail("common offset did not preserve the carry branch")
        endpoint_cost = sum((a - b) ** 2 for x, z in zip(left, right) for a, b in zip(x, z))
        if endpoint_cost != Fraction(int(row["raw_rhs"]), q * q):
            fail("common offset changed normalized endpoint cost")
    # The zero offset is deliberately excluded: this distinguishes strict
    # half-open-box interior membership from a mere grid-boundary statement.
    if not (Fraction(0, 1) < sample < Fraction(1, q)):
        fail("open-offset sample")


def verify(packet: dict[str, object]) -> dict[str, object]:
    if packet.get("format") != "erdos142-q6-m7-redesign-physical-torsion-wall-v1":
        fail("packet format")
    scope = packet.get("scope")
    if not isinstance(scope, dict) or scope.get("ordinary_euclidean_continuum_claim") is not False or scope.get("r3_claim") is not False:
        fail("scope boundary")
    q = int(packet["q"])
    if int(packet["blocks"]) != 6:
        fail("block count")
    local_supports = supports(q)
    if local_supports[0] & local_supports[1]:
        fail("orientation supports must be disjoint")

    selected_cells = tuple(tuple(int(value) for value in cell) for cell in packet["selected_cells"])
    expected_cells = ((38, 3), (41, 3), (42, 3), (44, 3), (49, 3), (50, 3), (52, 3), (56, 3))
    if selected_cells != expected_cells or len(set(selected_cells)) != 8:
        fail("selected eight-cell packet")
    if any(word.bit_count() != 3 or residue != 3 for word, residue in selected_cells):
        fail("selected-cell weight/residue structure")
    per_cell_counts = [cell_count(word, residue, local_supports) for word, residue in selected_cells]
    if set(per_cell_counts) != {178605}:
        fail("cell mass")
    mass = packet["mass"]
    if int(mass["per_cell"]) != 178605 or int(mass["total"]) != sum(per_cell_counts):
        fail("declared mass")
    total_fraction = Fraction(sum(per_cell_counts), q ** 12)
    gate = Fraction(7, 24) ** 6
    expected_margin = total_fraction - gate
    if tuple(mass["fraction"]) != (total_fraction.numerator, total_fraction.denominator):
        fail("mass fraction")
    if tuple(mass["gate_fraction"]) != (gate.numerator, gate.denominator):
        fail("gate fraction")
    if tuple(mass["margin_fraction"]) != (expected_margin.numerator, expected_margin.denominator) or expected_margin <= 0:
        fail("strict gate margin")

    raw_vertices = packet["vertices"]
    vertices = {name: tuple(tuple(int(value) for value in point) for point in points) for name, points in raw_vertices.items()}
    if set(vertices) != {"X", "Y", "Z"} or len(set(vertices.values())) != 3:
        fail("three distinct physical vertex identities")
    vertex_cells = {name: tuple(int(value) for value in cell) for name, cell in packet["vertex_cells"].items()}
    if set(vertex_cells) != set(vertices):
        fail("vertex-cell labels")
    for name, vertex in vertices.items():
        if len(vertex) != 6 or any(point not in local_supports[0] | local_supports[1] for point in vertex):
            fail("vertex local support membership")
        actual_cell = (word_of(vertex, local_supports), residue_of(vertex))
        if actual_cell != vertex_cells[name] or actual_cell not in selected_cells:
            fail("physical vertex cell membership")

    rows = packet["rows"]
    if not isinstance(rows, list) or len(rows) != 3:
        fail("three cyclic rows")
    total_rhs = 0
    for row in rows:
        names = tuple(str(row[key]) for key in ("left", "center", "right"))
        if any(name not in vertices for name in names):
            fail("row vertex name")
        left, center, right = (vertices[name] for name in names)
        actual_carry = carry(left, center, right, q)
        declared_carry = tuple(tuple(int(value) for value in pair) for pair in row["carry"])
        if actual_carry != declared_carry:
            fail("semantic carry")
        actual_rhs = raw_cost(left, right)
        if actual_rhs != int(row["raw_rhs"]) or actual_rhs <= 0:
            fail("raw endpoint RHS")
        total_rhs += actual_rhs
    if aggregate_coefficients(rows):
        fail("arbitrary-global-H coefficient cancellation")
    if total_rhs != 144:
        fail("positive q6 contradiction")
    check_offset_lift(vertices, rows, q)
    census = fixed_step_census(local_supports, selected_cells)

    return {
        "verdict": "PASS_Q6_M7_REDESIGN_PHYSICAL_TORSION_WALL",
        "finite_q_contradiction_raw": [0, total_rhs],
        "finite_q_contradiction_normalized": [0, Fraction(total_rhs, q * q)],
        "mass": str(total_fraction),
        "gate": str(gate),
        "margin": str(expected_margin),
        "open_offset_domain": "delta in (0,1/6)^12, common to X,Y,Z",
        "continuum_scope": "branch-sensitive raw-canonical torus only; not ordinary Euclidean midpoint",
        "fixed_step_census": census,
        "deletion_scope": "one fixed step has only 45 disjoint 3-orbits; no all-step deletion lower bound is claimed",
    }


def expect_rejected(packet: dict[str, object], label: str) -> None:
    try:
        verify(packet)
    except AssertionError:
        return
    fail(f"planted mutation accepted: {label}")


def planted_failures(packet: dict[str, object]) -> dict[str, str]:
    bad = copy.deepcopy(packet)
    bad["selected_cells"][0] = [39, 3]
    expect_rejected(bad, "selected-cell")

    bad = copy.deepcopy(packet)
    bad["vertices"]["X"][0] = [4, 2]
    expect_rejected(bad, "physical-vertex-membership")

    bad = copy.deepcopy(packet)
    bad["rows"][0]["carry"][1] = [0, 0]
    expect_rejected(bad, "carry")

    bad = copy.deepcopy(packet)
    bad["rows"][1]["raw_rhs"] = 47
    expect_rejected(bad, "raw-rhs")

    bad = copy.deepcopy(packet)
    # Replace the second valid physical row by a duplicate of the first.
    # Carries and RHS remain individually semantic, but global-H cancellation
    # is destroyed.
    bad["rows"][1] = copy.deepcopy(bad["rows"][0])
    expect_rejected(bad, "row-coefficients")

    bad = copy.deepcopy(packet)
    bad["mass"]["margin_fraction"] = [0, 1]
    expect_rejected(bad, "mass-gate")

    return {label: "rejected" for label in ("selected-cell", "physical-vertex-membership", "carry", "raw-rhs", "row-coefficients", "mass-gate")}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", help="run targeted planted-failure checks")
    args = parser.parse_args()
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    report = verify(packet)
    if args.self_test:
        report["planted_failures"] = planted_failures(packet)
    report["sha256"] = {name: sha256(HERE / name) for name in ("semantic_packet.json", "verify.py")}
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()

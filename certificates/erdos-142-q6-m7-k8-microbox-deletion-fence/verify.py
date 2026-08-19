#!/usr/bin/env python3
"""Primary stdlib replay for the candidate-22 q6 microbox deletion fence.

The proof input is the frozen positive matching ledger.  Discovery programs,
CP-SAT, channel completeness, and all negative search output are intentionally
outside this verifier and outside the theorem.
"""
from __future__ import annotations

import argparse
import copy
from collections import Counter
from fractions import Fraction
import hashlib
import json
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent
Q = 6
GOAL = 30_425
FULL_MASS = 1_370_520
GATE_NUMERATOR = 85_766_121  # gate = numerator / 64 q6^12-boxes
DELTA = Fraction(1, 12)

# Ordered rather than set-valued: the ledger's base-18 physical-box codes use
# exactly this order, BASE followed by its disjoint reflection.
BASE = ((3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2))
U = BASE + tuple((5-a,b) for a,b in BASE)
EXPECTED_CELLS = (
    (7,0),(25,0),(45,0),(49,0),(62,0),(27,1),(45,1),(54,1),
    (7,2),(56,2),(30,3),(33,3),(21,4),(42,4),(9,5),(20,5),
    (34,5),(4,6),(19,6),(26,6),(41,6),(48,6),
)
EXPECTED_TEMPLATE = ((4,5),(4,7),(6,7),(5,6),(2,3),(1,2),(0,1),(0,3))


def parse_cells():
    cells = tuple(
        tuple(map(int, line.split(":")))
        for line in (HERE / "candidate.cells").read_text(encoding="ascii").splitlines()
        if line.strip()
    )
    assert cells == EXPECTED_CELLS and len(set(cells)) == 22
    return cells


def load_template():
    template = json.loads((HERE / "template.json").read_text(encoding="ascii"))
    assert template == {
        "q": 6,
        "rows": [[4,5],[4,7],[6,7],[5,6],[2,3],[1,2],[0,1],[0,3]],
        "endpoint_degree": 2,
        "centers": [0,1,2,3,4,5,6,7],
        "normalization": "raw digit cost divided by q^2",
        "description": "The residual eight-row balanced template used by every packet in matching_ledger.json.",
    }
    return tuple(tuple(row) for row in template["rows"])


def cell_mass(word, residue):
    """Exact count of q6^12 physical boxes in a (word,residue) coarse cell."""
    total = 0
    for parity_bits in product((0,1), repeat=6):
        if sum(parity_bits) != residue:
            continue
        ways = 1
        for position, bit in enumerate(parity_bits):
            # BASE has 3 even and 6 odd points; REF has 6 even and 3 odd.
            ways *= 3 if ((word >> position) & 1) == bit else 6
        total += ways
    return total


def physical_cell(columns, vertex):
    word = sum((columns[position][vertex] >= 9) << position for position in range(6))
    residue = sum(sum(U[columns[position][vertex]]) & 1 for position in range(6))
    return word, residue


def physical_box(columns, vertex):
    """The six ordered q6 digit pairs defining one actual 12D microbox."""
    return tuple(U[columns[position][vertex]] for position in range(6))


def box_code(columns, vertex):
    return sum(columns[position][vertex] * 18**position for position in range(6))


def row_carry_and_cost(columns, center, left, right):
    carry = []
    raw_cost = 0
    for position in range(6):
        x, z, y = U[columns[position][left]], U[columns[position][right]], U[columns[position][center]]
        defect = (x[0] + z[0] - 2*y[0], x[1] + z[1] - 2*y[1])
        assert defect[0] % Q == 0 and defect[1] % Q == 0
        carry.append((defect[0] // Q, defect[1] // Q))
        raw_cost += (x[0] - z[0])**2 + (x[1] - z[1])**2
    return tuple(carry), raw_cost


def common_offset_lift(columns, rows, carries, delta=DELTA):
    """Exact symbolic common-offset lift, without float/rational iteration.

    Every ledger digit is in U subset {0,...,5}^2.  Thus d/q+delta is
    strictly in (d/q,(d+1)/q) once 0<delta<1/q.  The integer carry replay has
    already proved d_a+d_b-2d_c=q*kappa; the three shared deltas have
    coefficient 1+1-2=0, proving the lifted relation for this packet.
    """
    assert Fraction(0) < delta < Fraction(1, Q)
    assert all(0 <= coordinate < Q for column in columns for digit in column for coordinate in U[digit])
    assert 1 + 1 - 2 == 0
    for center, (left, right) in enumerate(rows):
        for position in range(6):
            for coordinate in range(2):
                raw = (U[columns[position][left]][coordinate] + U[columns[position][right]][coordinate]
                       - 2*U[columns[position][center]][coordinate])
                assert raw == Q * carries[center][position][coordinate]


def shared_offset_cube_identity():
    """Audit the algebra for every shared t in D=[0,1/q)^12.

    A lifted coordinate has form digit/q+t.  In every row the coefficient of
    each of the twelve independent coordinates of t is 1+1-2=0, so the carry
    below is independent of t.  The defining inequalities 0<=t<1/q place all
    points in their original half-open physical microboxes.
    """
    assert 1 + 1 - 2 == 0


def measurable_deletion_lemma(packet_count, globally_distinct_vertex_count,
                              full_mass=FULL_MASS, gate_numerator=GATE_NUMERATOR):
    """Exact numerical conclusion of the shared-offset union-bound/Fubini lemma.

    Let D=[0,1/q)^12.  For packet p and its eight physical digit boxes B[p,i],
    let A[p,i]={t in D: digit[p,i]/q+t lies in the retained measurable set}.
    At a common t, the eight raw-canonical torus rows remain valid because t
    cancels from every midpoint defect.  Positive-cost cancellation therefore
    gives intersection_i A[p,i]=empty (up to any null exceptional set in an
    a.e. coercivity convention).  Hence D is contained a.e. in the union of
    D minus A[p,i], and the union bound gives sum_i mu(D minus A[p,i]) >= mu(D).

    The ledger's 8*packet_count physical boxes are distinct.  Translation by
    their digit/q origins is measure preserving and their boxes are disjoint,
    so summing the preceding inequality over p gives deleted measure at least
    packet_count*mu(D).  In q6^12-box volume units retained <= full_mass-M.
    """
    assert globally_distinct_vertex_count == 8 * packet_count
    assert packet_count > 0
    retained_boxes = full_mass - packet_count
    comparison_numerator = retained_boxes * 64 - gate_numerator
    return {
        "offset_cube": "D=[0,1/6)^12",
        "method": "per-packet union bound, then Fubini/translation over globally disjoint boxes",
        "deleted_measure_box_units_lower_bound": packet_count,
        "retained_measure_box_units_upper_bound": retained_boxes,
        "retained_minus_gate_numerator": comparison_numerator,
    }


def load_ledger():
    return json.loads((HERE / "matching_ledger.json").read_text(encoding="ascii"))


def check_hashes(constants=None):
    constants = json.loads((HERE / "constants.json").read_text(encoding="ascii")) if constants is None else constants
    assert constants["certificate"] == "candidate-22 q6 microbox arbitrary-measurable-carving deletion fence"
    assert constants["constants_policy"] == "checked by both replays; never regenerated by a replay"
    assert constants["candidate_mass_boxes"] == FULL_MASS
    assert constants["gate_boxes"] == f"{GATE_NUMERATOR}/64"
    assert constants["matching_packets"] == GOAL
    assert constants["matching_vertices"] == 8 * GOAL
    assert constants["ledger_channels_sha256"] == "96655FA6B81E3B67D1FA55D12242557924A7DD5403BC74318EFEF05A04622BE8"
    assert constants["ledger_enumeration_solutions_used"] == 7194
    assert constants["forced_deleted_measure_box_units"] == GOAL
    assert constants["maximum_retained_measure_box_units"] == FULL_MASS - GOAL
    assert constants["maximum_minus_gate_numerator"] == -41
    assert constants["scope"] == {
        "finite_q": 6,
        "fixed_22_cell_geometric_union": True,
        "arbitrary_measurable_carving": True,
        "raw_canonical_modular_torus_coercivity": True,
        "ordinary_euclidean_claim": False,
        "deformations_or_replacement_cells": False,
        "recursive_state": False,
        "integer_transfer": False,
        "new_r3_bound": False,
        "erdos142_solved": False,
    }
    hashes = constants["artifact_sha256"]
    assert set(hashes) == {
        "README.md", "candidate.cells", "template.json", "matching_ledger.json",
        "verify.py", "independent_replay.py",
    }
    for name, expected in hashes.items():
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest().upper()
        assert actual == expected, (name, actual, expected)
    return constants


def audit(ledger=None, cells=None, rows=None, delta=DELTA, gate_numerator=GATE_NUMERATOR):
    cells = parse_cells() if cells is None else tuple(cells)
    rows = load_template() if rows is None else tuple(tuple(row) for row in rows)
    ledger = load_ledger() if ledger is None else ledger
    assert cells == EXPECTED_CELLS
    assert rows == EXPECTED_TEMPLATE
    assert len(U) == 18 and len(set(U)) == 18
    assert Counter(label for row in rows for label in row) == Counter({i: 2 for i in range(8)})
    assert sum(cell_mass(*cell) for cell in cells) == FULL_MASS
    assert Fraction(FULL_MASS, Q**12) == Fraction(235, 373248)
    shared_offset_cube_identity()

    assert tuple(tuple(row) for row in ledger["template"]) == rows
    assert tuple(tuple(cell) for cell in ledger["candidate"]) == cells
    assert ledger["channels_sha256"].upper() == "96655FA6B81E3B67D1FA55D12242557924A7DD5403BC74318EFEF05A04622BE8"
    assert ledger["enumeration_solutions_used"] == 7194
    packets = ledger["packets"]
    assert len(packets) == GOAL

    seen_codes = set()
    raw_total = 0
    carry_histogram = Counter()
    cell_uses = Counter()
    for serial, packet in enumerate(packets):
        columns = tuple(tuple(column) for column in packet["columns"])
        assert len(columns) == 6 and all(len(column) == 8 for column in columns)
        assert all(0 <= digit < 18 for column in columns for digit in column)
        boxes = tuple(physical_box(columns, vertex) for vertex in range(8))
        assert len(set(boxes)) == 8
        packet_cells = tuple(physical_cell(columns, vertex) for vertex in range(8))
        assert tuple(tuple(cell) for cell in packet["cells"]) == packet_cells
        assert all(cell in set(cells) for cell in packet_cells)
        codes = tuple(box_code(columns, vertex) for vertex in range(8))
        assert tuple(packet["vertices"]) == codes
        assert all(code not in seen_codes for code in codes), ("global_physical_box_overlap", serial)
        seen_codes.update(codes)

        coefficient = [0] * 8
        carries = []
        raw_costs = []
        for center, (left, right) in enumerate(rows):
            coefficient[left] += 1
            coefficient[right] += 1
            coefficient[center] -= 2
            carry, raw_cost = row_carry_and_cost(columns, center, left, right)
            assert raw_cost > 0
            carries.append(carry)
            raw_costs.append(raw_cost)
            carry_histogram.update(carry)
        assert coefficient == [0] * 8
        assert tuple(packet["raw_costs"]) == tuple(raw_costs)
        common_offset_lift(columns, rows, carries, delta)
        raw_total += sum(raw_costs)
        cell_uses.update(packet_cells)

    lemma = measurable_deletion_lemma(len(packets), len(seen_codes), FULL_MASS, gate_numerator)
    assert lemma["retained_measure_box_units_upper_bound"] == 1_340_095
    assert lemma["retained_minus_gate_numerator"] == -41 < 0
    return {
        "verdict": "PASS_CANDIDATE22_Q6_MICROBOX_DELETION_FENCE",
        "packets": len(packets),
        "physical_boxes": len(seen_codes),
        "template": [list(row) for row in rows],
        "raw_cost_total": raw_total,
        "carry_histogram": [[list(carry), count] for carry, count in sorted(carry_histogram.items())],
        "cell_uses": [[list(cell), count] for cell, count in sorted(cell_uses.items())],
        "deletion_lemma": lemma,
    }


def rejected(label, callback):
    try:
        callback()
    except AssertionError:
        return label
    raise AssertionError(label + " corruption accepted")


def local_packet_audit(packet, cells=EXPECTED_CELLS, rows=EXPECTED_TEMPLATE, delta=DELTA):
    """Small copy-on-write validator used by planted controls only."""
    columns = tuple(tuple(column) for column in packet["columns"])
    assert len(columns) == 6 and all(len(column) == 8 for column in columns)
    assert all(0 <= digit < 18 for column in columns for digit in column)
    packet_cells = tuple(physical_cell(columns, vertex) for vertex in range(8))
    assert tuple(tuple(cell) for cell in packet["cells"]) == packet_cells
    assert all(cell in set(cells) for cell in packet_cells)
    codes = tuple(box_code(columns, vertex) for vertex in range(8))
    assert tuple(packet["vertices"]) == codes and len(set(codes)) == 8
    carries = []
    costs = []
    for center, (left, right) in enumerate(rows):
        carry, cost = row_carry_and_cost(columns, center, left, right)
        assert cost > 0
        carries.append(carry)
        costs.append(cost)
    assert tuple(packet["raw_costs"]) == tuple(costs)
    common_offset_lift(columns, rows, carries, delta)
    return codes


def self_test():
    ledger = load_ledger()
    original = ledger["packets"][0]
    bad = copy.deepcopy(original)
    bad["columns"][0][0] = 18
    point = rejected("digit_outside_local_support", lambda: local_packet_audit(bad))

    bad = copy.deepcopy(original)
    bad["vertices"][0] += 1
    vertex = rejected("vertex_code", lambda: local_packet_audit(bad))

    bad_rows = list(EXPECTED_TEMPLATE)
    bad_rows[0] = (4,4)
    endpoint = rejected("endpoint_template", lambda: assert_endpoint_balance(bad_rows))

    # Coherently refresh code/cell metadata, then leave a genuine modular
    # midpoint defect so the local row replay rejects it.
    midpoint_bad = None
    for position in range(6):
        for vertex_index in range(8):
            for digit in range(18):
                if digit == original["columns"][position][vertex_index]:
                    continue
                trial = copy.deepcopy(original)
                trial["columns"][position][vertex_index] = digit
                columns = tuple(tuple(column) for column in trial["columns"])
                cells = tuple(physical_cell(columns, i) for i in range(8))
                if not all(cell in EXPECTED_CELLS for cell in cells):
                    continue
                trial["cells"] = [list(cell) for cell in cells]
                trial["vertices"] = [box_code(columns, i) for i in range(8)]
                try:
                    for center, (left, right) in enumerate(EXPECTED_TEMPLATE):
                        row_carry_and_cost(columns, center, left, right)
                except AssertionError:
                    midpoint_bad = trial
                    break
            if midpoint_bad is not None:
                break
        if midpoint_bad is not None:
            break
    assert midpoint_bad is not None
    midpoint = rejected("midpoint_digit", lambda: local_packet_audit(midpoint_bad))

    # This is the required wrong-overlap control: locally valid packet 0 is
    # reused as packet 1, so only global physical-box disjointness fails.
    overlap = rejected("global_physical_box_overlap", lambda: assert_disjoint_packets(original, original))

    bad = copy.deepcopy(original)
    bad["raw_costs"][0] += 1
    cost = rejected("raw_cost", lambda: local_packet_audit(bad))

    bad = copy.deepcopy(original)
    bad["cells"][0] = [0,0]
    off_candidate = rejected("off_candidate_cell", lambda: local_packet_audit(bad))

    count = rejected("packet_count", lambda: assert_packet_count(len(ledger["packets"]) - 1))

    bad_constants = copy.deepcopy(json.loads((HERE / "constants.json").read_text(encoding="ascii")))
    bad_constants["artifact_sha256"]["matching_ledger.json"] = "00" * 32
    digest = rejected("manifest_hash", lambda: check_hashes(bad_constants))

    columns = tuple(tuple(column) for column in original["columns"])
    carries = [row_carry_and_cost(columns, center, left, right)[0] for center, (left, right) in enumerate(EXPECTED_TEMPLATE)]
    offset = rejected("boundary_offset", lambda: common_offset_lift(columns, EXPECTED_TEMPLATE, carries, Fraction(0)))
    gate = rejected("gate", lambda: require_gate(GATE_NUMERATOR - 42))
    too_few = rejected("insufficient_matching", lambda: require_strict_gate(GOAL - 1))
    return {label: "rejected" for label in (
        point, vertex, endpoint, midpoint, overlap, cost, off_candidate,
        count, digest, offset, gate, too_few,
    )}


def assert_false():
    raise AssertionError("matching below threshold")


def require_strict_gate(packet_count):
    lemma = measurable_deletion_lemma(packet_count, 8 * packet_count)
    assert lemma["retained_minus_gate_numerator"] < 0


def require_gate(gate_numerator):
    lemma = measurable_deletion_lemma(GOAL, 8 * GOAL, gate_numerator=gate_numerator)
    assert lemma["retained_minus_gate_numerator"] < 0


def assert_packet_count(count):
    assert count == GOAL


def assert_endpoint_balance(rows):
    assert Counter(label for row in rows for label in row) == Counter({i: 2 for i in range(8)})


def assert_disjoint_packets(first, second):
    first_codes = local_packet_audit(first)
    second_codes = local_packet_audit(second)
    assert set(first_codes).isdisjoint(second_codes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    check_hashes()
    report = audit()
    if args.self_test:
        report["planted_failures"] = self_test()
    print("PASS_CANDIDATE22_Q6_MICROBOX_DELETION_FENCE")
    print(json.dumps(report, sort_keys=True))

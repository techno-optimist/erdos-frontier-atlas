#!/usr/bin/env python3
"""Primary exact replay of the q6/M7 mass-positive torsion-free selector."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SELECTOR = HERE / "selector.cells"
CONSTANTS = HERE / "constants.json"
Q = 6
BASE = frozenset({(3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2)})
REFLECTED = frozenset((5-x, y) for x, y in BASE)
SUPPORTS = (BASE, REFLECTED)
EXPECTED = (
    (7,0),(11,0),(21,0),(25,0),(35,0),(45,0),(49,0),(62,0),
    (27,1),(45,1),(54,1),(7,2),(56,2),(30,3),(33,3),
    (21,4),(42,4),(9,5),(20,5),(34,5),
    (4,6),(19,6),(25,6),(26,6),(35,6),(41,6),(42,6),(48,6),
)


def parity(point: tuple[int, int]) -> int:
    return (point[0] + point[1]) & 1


def translate(point: tuple[int, int], step: tuple[int, int], times: int) -> tuple[int, int]:
    return ((point[0] + times*step[0]) % Q, (point[1] + times*step[1]) % Q)


def orientation(point: tuple[int, int]) -> int:
    if point in BASE:
        return 0
    if point in REFLECTED:
        return 1
    raise AssertionError("point outside both local supports")


def local_table() -> dict[tuple[int, int, int], set[tuple[int, bool]]]:
    """Return (parity, nonzero-step) options for every orientation triple."""
    table = {bits: set() for bits in itertools.product((0,1), repeat=3)}
    rows = 0
    for step in itertools.product((0,2,4), repeat=2):
        for start in BASE | REFLECTED:
            triple = tuple(translate(start, step, k) for k in range(3))
            if not all(point in BASE or point in REFLECTED for point in triple):
                continue
            bits = tuple(orientation(point) for point in triple)
            table[bits].add((parity(start), step != (0,0)))
            rows += 1
    assert rows == 42
    assert table[(0,0,0)] == table[(1,1,1)] == {(0,False),(1,False)}
    for bits in itertools.product((0,1), repeat=3):
        if len(set(bits)) == 1:
            continue
        forced = 1 if sum(bits) == 1 else 0
        assert table[bits] == {(forced, True)}
    return table


def criterion(a: int, b: int, c: int, residue: int) -> bool:
    columns = [((a>>i)&1, (b>>i)&1, (c>>i)&1) for i in range(6)]
    changing = [column for column in columns if len(set(column)) > 1]
    v = len(changing)
    t = sum(sum(column) == 1 for column in changing)
    return v > 0 and t <= residue <= t + 6 - v


def direct_dynamic_exists(a: int, b: int, c: int, residue: int,
                          table: dict[tuple[int,int,int], set[tuple[int,bool]]]) -> bool:
    states = {(0, False)}
    for i in range(6):
        bits = ((a>>i)&1, (b>>i)&1, (c>>i)&1)
        states = {
            (total+p, active or nonzero)
            for total, active in states
            for p, nonzero in table[bits]
        }
    return (residue, True) in states


def cell_mass(word: int, residue: int) -> int:
    poly = [1]
    for i in range(6):
        support = SUPPORTS[(word >> i) & 1]
        even = sum(parity(p) == 0 for p in support)
        odd = sum(parity(p) == 1 for p in support)
        nxt = [0] * (len(poly)+1)
        for j, value in enumerate(poly):
            nxt[j] += even*value
            nxt[j+1] += odd*value
        poly = nxt
    return poly[residue]


def parse_selector(text: str) -> tuple[tuple[int,int], ...]:
    cells = tuple(tuple(map(int, line.split(":"))) for line in text.splitlines() if line.strip())
    assert len(cells) == 28 and len(set(cells)) == 28
    assert all(0 <= w < 64 and 0 <= r <= 6 for w, r in cells)
    return cells


def validate(cells: tuple[tuple[int,int], ...], *, expected_mass: int = 1_405_512,
             expected_edges: int = 0, gate_numerator: int = 85_766_121) -> dict:
    assert cells == EXPECTED
    assert BASE.isdisjoint(REFLECTED) and len(BASE) == len(REFLECTED) == 9
    assert tuple((sum(parity(p)==0 for p in s), sum(parity(p)==1 for p in s)) for s in SUPPORTS) == ((3,6),(6,3))
    table = local_table()

    by_residue = {r: tuple(w for w, rr in cells if rr == r) for r in range(7)}
    edges = []
    checked = 0
    for residue, words in by_residue.items():
        for a, b, c in itertools.product(words, repeat=3):
            closed = criterion(a,b,c,residue)
            direct = direct_dynamic_exists(a,b,c,residue,table)
            assert closed == direct
            checked += 1
            if direct:
                edges.append((a,b,c,residue))
    assert len(edges) == expected_edges == 0

    masses = {(w,r): cell_mass(w,r) for w,r in cells}
    total = sum(masses.values())
    gate_boxes = Fraction(gate_numerator, 64)
    assert total == expected_mass == 1_405_512
    assert gate_boxes == Fraction(85_766_121,64)
    assert Fraction(total) - gate_boxes == Fraction(4_186_647,64) > 0
    mass = Fraction(total, Q**12)
    gate = Fraction(7,24)**6
    assert mass == Fraction(241,373248)
    assert mass-gate == Fraction(5743,191102976) > 0
    return {
        "selected_cells": len(cells),
        "residue_cell_counts": [len(by_residue[r]) for r in range(7)],
        "ordered_word_triples_checked": checked,
        "nontrivial_order3_hyperedges": len(edges),
        "mass_boxes": total,
        "mass": str(mass),
        "gate": str(gate),
        "gate_excess_boxes": str(Fraction(total)-gate_boxes),
        "normalized_gate_excess": str(mass-gate),
    }


def verify_hashes() -> None:
    data = json.loads(CONSTANTS.read_text(encoding="utf-8"))
    assert data["scope"]["erdos142_solved"] is False
    assert data["scope"]["new_r3_bound"] is False
    assert data["scope"]["potential_feasibility_claim"] is False
    for name, expected in data["sha256"].items():
        got = hashlib.sha256((HERE/name).read_bytes()).hexdigest().upper()
        assert got == expected, f"SHA-256 mismatch: {name}"


def expect_reject(label: str, action) -> str:
    try:
        action()
    except AssertionError:
        return "rejected"
    raise AssertionError("planted failure accepted: " + label)


def assert_no_selected_edge(cells: tuple[tuple[int,int], ...]) -> None:
    table = local_table()
    for residue in range(7):
        words = tuple(w for w, r in cells if r == residue)
        for triple in itertools.product(words, repeat=3):
            assert not direct_dynamic_exists(*triple, residue, table), "selected torsion edge"


def assert_constant_channels_are_trivial(table) -> None:
    assert table[(0,0,0)] == table[(1,1,1)] == {(0,False),(1,False)}


def self_test(cells: tuple[tuple[int,int], ...]) -> dict[str,str]:
    tests = {}
    duplicate = cells[:-1] + (cells[0],)
    tests["duplicate_cell"] = expect_reject("duplicate_cell", lambda: validate(duplicate))
    missing = cells[:-1]
    tests["missing_cell_or_mass"] = expect_reject("missing_cell_or_mass", lambda: validate(missing))
    planted_edge = ((0,0),) + cells
    tests["planted_torsion_edge"] = expect_reject(
        "planted_torsion_edge", lambda: assert_no_selected_edge(planted_edge)
    )
    tests["corrupted_expected_mass"] = expect_reject("corrupted_expected_mass", lambda: validate(cells, expected_mass=1_405_511))
    tests["corrupted_edge_count"] = expect_reject("corrupted_edge_count", lambda: validate(cells, expected_edges=1))
    tests["corrupted_gate"] = expect_reject("corrupted_gate", lambda: validate(cells, gate_numerator=85_766_120))
    # A nonzero local step may never be accepted on a constant orientation triple.
    table = local_table(); bad = {k:set(v) for k,v in table.items()}; bad[(0,0,0)].add((0,True))
    tests["zero_step_nontriviality"] = expect_reject(
        "zero_step_nontriviality", lambda: assert_constant_channels_are_trivial(bad)
    )
    return tests


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--self-test", action="store_true"); args = ap.parse_args()
    verify_hashes()
    cells = parse_selector(SELECTOR.read_text(encoding="ascii"))
    result = validate(cells)
    if args.self_test:
        result["planted_failures"] = self_test(cells)
    print("PASS_Q6_M7_ORBIT_FREE_SELECTOR")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

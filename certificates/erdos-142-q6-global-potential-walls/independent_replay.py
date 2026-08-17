#!/usr/bin/env python3
"""Independent stdlib replay of Terra's q=6 global-potential packets.

This file intentionally does not import any Terra module or verifier.  It
rebuilds the q=6 EHPS support, the eight D4 images, role supports for the two
representatives, all 3,645 cylinder-vertex labels, and every selected
midpoint row from packet provenance.  It then checks exact Farkas cancellation
and the positive raw-cost RHS.

The packet is only a finite-q exclusion for the unrestricted potential on
each of the five 9^3 cylinder vertices.  It is not a continuum claim.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKETS = {"A": HERE / "certificate_A.json", "B": HERE / "certificate_B.json"}
Q = 6
ROLES = ("P1", "P2", "P3", "B", "K")
WORDS = (
    ("P1", "K", "B"),
    ("B", "K", "P1"),
    ("P2", "B", "P2"),
    ("P3", "B", "B"),
    ("B", "B", "P3"),
)
ASSIGNMENTS = {
    "A": (7, 7, 7, 6, 7),
    "B": (7, 6, 7, 6, 7),
}
EXPECTED_WITNESSES_A = (
    {
        "source": 979,
        "words": (2, 3, 3),
        "points": (
            ((4, 0), (1, 3), (3, 1)),
            ((4, 0), (1, 3), (1, 3)),
            ((4, 0), (1, 3), (5, 5)),
        ),
        "carries": ((0, 0), (0, 0), (1, 0)),
        "raw": 20,
    },
    {
        "source": 1312,
        "words": (3, 2, 3),
        "points": (
            ((4, 0), (1, 3), (1, 3)),
            ((4, 0), (1, 3), (3, 1)),
            ((4, 0), (1, 3), (5, 5)),
        ),
        "carries": ((0, 0), (0, 0), (0, 1)),
        "raw": 20,
    },
    {
        "source": 1539,
        "words": (2, 3, 3),
        "points": (
            ((4, 0), (1, 3), (3, 1)),
            ((4, 0), (1, 3), (5, 5)),
            ((4, 0), (1, 3), (1, 3)),
        ),
        "carries": ((0, 0), (0, 0), (-1, -1)),
        "raw": 8,
    },
)


def ehps_support() -> tuple[tuple[int, int], ...]:
    """Exact q=6 support from the three EHPS pieces, epsilon=1/q."""
    out = []
    eps = Fraction(1, Q)
    for x in range(Q):
        for y in range(Q):
            a, b = Fraction(x, Q), Fraction(y, Q)
            s = a + b
            in_t1 = a >= Fraction(1, 2) and s > Fraction(2, 3) and s <= Fraction(7, 6)
            in_t2 = (
                a >= Fraction(1, 2)
                and b < Fraction(1, 2)
                and s >= Fraction(7, 6) + eps
                and s <= Fraction(17, 12)
            )
            in_t3 = (
                a < Fraction(1, 2)
                and b >= Fraction(1, 2)
                and s >= Fraction(7, 6) + eps
                and s <= Fraction(17, 12)
                and 2 * a + b >= Fraction(3, 2) + eps
            )
            if in_t1 or in_t2 or in_t3:
                out.append((x, y))
    return tuple(out)


def d4_image(support: tuple[tuple[int, int], ...], element: int) -> frozenset[tuple[int, int]]:
    out = set()
    for x, y in support:
        if element & 1:
            x = Q - 1 - x
        if element & 2:
            y = Q - 1 - y
        if element & 4:
            x, y = y, x
        out.add((x, y))
    return frozenset(out)


def supports_for(label: str) -> dict[str, frozenset[tuple[int, int]]]:
    assign = ASSIGNMENTS[label]
    images = [d4_image(ehps_support(), k) for k in range(8)]
    return {role: images[assign[i]] for i, role in enumerate(ROLES)}


def midpoint(x: tuple[int, int], y: tuple[int, int], z: tuple[int, int]) -> bool:
    return all((x[i] + z[i] - 2 * y[i]) % Q == 0 for i in range(2))


def midpoint_vertices(vertices: tuple[tuple[tuple[int, int], ...], ...]) -> bool:
    """Check the three-coordinate 6D midpoint witness."""
    return all(midpoint(vertices[0][i], vertices[1][i], vertices[2][i]) for i in range(3))


def carries(x: tuple[int, int], y: tuple[int, int], z: tuple[int, int]) -> tuple[int, int]:
    nums = (x[0] + z[0] - 2 * y[0], x[1] + z[1] - 2 * y[1])
    assert all(n % Q == 0 for n in nums)
    return (nums[0] // Q, nums[1] // Q)


def raw_cost(x: tuple[int, int], z: tuple[int, int]) -> int:
    return (x[0] - z[0]) ** 2 + (x[1] - z[1]) ** 2


def labels_for(label: str):
    """Return role point orders and the independent 3645-label function."""
    supports = supports_for(label)
    orders = {r: tuple(sorted(supports[r])) for r in ROLES}
    positions = {r: {p: i for i, p in enumerate(orders[r])} for r in ROLES}

    def vertex(word_index: int, points: tuple[tuple[int, int], ...]) -> int:
        roles = WORDS[word_index]
        assert len(points) == 3
        digits = tuple(positions[role][point] for role, point in zip(roles, points))
        return word_index * 729 + digits[0] * 81 + digits[1] * 9 + digits[2]

    return supports, orders, vertex


def check_all_vertex_labels(label: str) -> None:
    """Prove independently that the cylinder labels are exactly 0..3644."""
    supports, orders, vertex = labels_for(label)
    values = set()
    for word_index in range(5):
        for points in itertools.product(*(orders[r] for r in WORDS[word_index])):
            values.add(vertex(word_index, points))
    assert len(values) == 3645
    assert values == set(range(3645))


def midpoint_witness_count(supports: dict[str, frozenset[tuple[int, int]]]) -> int:
    """Count all ordered word-triple, 6D midpoint/carry witnesses."""
    total = 0
    for a, b, c in itertools.product(range(5), repeat=3):
        count = 1
        for pos in range(3):
            xs = supports[WORDS[a][pos]]
            ys = supports[WORDS[b][pos]]
            zs = supports[WORDS[c][pos]]
            count *= sum(
                1 for x, y, z in itertools.product(xs, ys, zs) if midpoint(x, y, z)
            )
        total += count
    return total


def check_scope(packet: dict, label: str, supports) -> None:
    assert packet["packet_format"] == "erdos-142-q6-global-potential-semantic-farkas-v1"
    assert packet["representative_label"] == label
    assert packet["q"] == Q
    assert tuple(packet["assignment"]) == ASSIGNMENTS[label]
    assert packet["support_size"] == 9
    assert packet["cylinder_count"] == 5
    assert packet["variable_count"] == 3645
    scope = packet["scope"]
    assert scope["finite_q"] == Q
    assert scope["continuum_claim"] is False
    assert scope["potential_ansatz"] == "one arbitrary potential value for each vertex of each of five codeword cylinders"
    assert scope["ordered_word_triples_in_model"] == 125
    assert scope["all_even_q_midpoint_branches"] is True
    assert "raw canonical" in scope["cost"]
    assert all(len(s) == 9 for s in supports.values())
    base = ehps_support()
    images = [d4_image(base, k) for k in range(8)]
    assert len(base) == 9 and all(len(s) == 9 for s in images)
    assert len(set(images)) == 8
    check_all_vertex_labels(label)


def verify_rows(packet: dict, label: str, mutate: str | None = None) -> dict:
    if mutate:
        packet = copy.deepcopy(packet)
        if mutate == "rhs":
            packet["selected_rows"][0]["rhs_numerator"] += 1
        elif mutate == "carry":
            packet["selected_rows"][0]["provenance"]["carries"][0][0] += 1
        elif mutate == "coefficient":
            packet["selected_rows"][0]["coefficients"][0][0] += 1
        elif mutate == "multiplier":
            packet["integer_multipliers"][0] += 1
        elif mutate == "mass":
            packet["actual_triple_count"] += 1
        elif mutate == "scope":
            packet["scope"]["continuum_claim"] = True
        else:
            raise ValueError(mutate)

    supports, orders, vertex = labels_for(label)
    check_scope(packet, label, supports)
    assert packet["actual_triple_count"] == 1128545
    assert midpoint_witness_count(supports) == packet["actual_triple_count"]
    selected = packet["selected_rows"]
    multipliers = packet["integer_multipliers"]
    source_indices = packet["source_row_indices"]
    assert len(selected) == len(multipliers) == len(source_indices)
    assert len(set(source_indices)) == len(source_indices)
    assert min(source_indices) >= 0
    assert max(source_indices) < packet["recovered_cegar"]["frozen_row_count"]

    aggregate: dict[int, int] = {}
    positive_raw = 0
    for row, multiplier, source in zip(selected, multipliers, source_indices):
        assert multiplier > 0
        assert row["source_row_index"] == source
        sem = row["provenance"]
        words = tuple(sem["word_indices"])
        assert len(words) == 3 and all(0 <= w < 5 for w in words)
        points = tuple(tuple(tuple(p) for p in triple) for triple in sem["points"])
        assert len(points) == 3
        expected = {}
        for wi, triple, sign in zip(words, points, (1, -2, 1)):
            roles = WORDS[wi]
            assert all(p in supports[r] for r, p in zip(roles, triple))
            v = vertex(wi, triple)
            expected[v] = expected.get(v, 0) + sign
        expected_coeffs = [[v, s] for v, s in sorted(expected.items()) if s]
        assert row["coefficients"] == expected_coeffs
        assert midpoint_vertices(points)
        expected_carries = [list(carries(points[0][i], points[1][i], points[2][i])) for i in range(3)]
        assert sem["carries"] == expected_carries
        expected_raw = sum(raw_cost(points[0][i], points[2][i]) for i in range(3))
        assert sem["raw_cost_numerator"] == expected_raw
        assert row["rhs_numerator"] == expected_raw
        # B's exact ray legitimately contains zero-cost midpoint-branch rows;
        # they constrain potentials but contribute zero to the contradiction.
        assert expected_raw >= 0
        positive_raw += multiplier * expected_raw
        for v, coefficient in expected.items():
            aggregate[v] = aggregate.get(v, 0) + multiplier * coefficient

    assert all(value == 0 for value in aggregate.values())
    assert positive_raw == packet["positive_contradiction_raw"]
    return {
        "label": label,
        "assignment": list(ASSIGNMENTS[label]),
        "support_size": len(ehps_support()),
        "variable_count": packet["variable_count"],
        "actual_midpoint_witnesses": packet["actual_triple_count"],
        "selected_rows": len(selected),
        "nonzero_coefficient_residue": 0,
        "positive_raw_rhs": str(positive_raw),
        "packet_rhs_match": True,
        "packet_sha256": hashlib.sha256(PACKETS[label].read_bytes()).hexdigest(),
    }


def print_a_witnesses(packet: dict, vertex) -> None:
    print("A_THREE_ROW_UNIT_MULTIPLIER_CYCLE")
    assert len(packet["selected_rows"]) == len(EXPECTED_WITNESSES_A)
    for row, expected in zip(packet["selected_rows"], EXPECTED_WITNESSES_A):
        sem = row["provenance"]
        points = tuple(tuple(tuple(p) for p in triple) for triple in sem["points"])
        assert row["source_row_index"] == expected["source"]
        assert tuple(sem["word_indices"]) == expected["words"]
        assert points == expected["points"]
        assert tuple(tuple(c) for c in sem["carries"]) == expected["carries"]
        assert sem["raw_cost_numerator"] == expected["raw"]
        labels = [vertex(w, p) for w, p in zip(sem["word_indices"], points)]
        manual_raw = sum(raw_cost(points[0][i], points[2][i]) for i in range(3))
        manual_carries = [list(carries(points[0][i], points[1][i], points[2][i])) for i in range(3)]
        print(
            json.dumps(
                {
                    "source_row_index": row["source_row_index"],
                    "word_indices": sem["word_indices"],
                    "points": sem["points"],
                    "labels": labels,
                    "coefficients": row["coefficients"],
                    "carries_recomputed": manual_carries,
                    "raw_recomputed": manual_raw,
                    "manual_checks": {
                        "midpoint": midpoint_vertices(points),
                        "labels_match": row["coefficients"]
                        == [[v, s] for v, s in sorted({labels[0]: 1, labels[1]: -2, labels[2]: 1}.items()) if s],
                    },
                },
                sort_keys=True,
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    packets = {}
    results = {}
    for label in ("A", "B"):
        packets[label] = json.loads(PACKETS[label].read_text(encoding="utf-8"))
        results[label] = verify_rows(packets[label], label)
    _, _, vertex_a = labels_for("A")
    print_a_witnesses(packets["A"], vertex_a)
    if args.self_test:
        controls = {}
        for label in ("A", "B"):
            controls[label] = {}
            for mutation in ("rhs", "carry", "coefficient", "multiplier", "mass", "scope"):
                try:
                    verify_rows(packets[label], label, mutation)
                except (AssertionError, KeyError, ValueError):
                    controls[label][mutation] = "PASS_MUTATION_REJECTED"
                else:
                    raise AssertionError(f"mutation unexpectedly accepted: {label}/{mutation}")
        results["mutation_controls"] = controls
    print("PASS_INDEPENDENT_Q6_GLOBAL_POTENTIAL_REPLAY")
    print(json.dumps({"replays": results}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

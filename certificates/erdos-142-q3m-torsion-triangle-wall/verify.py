#!/usr/bin/env python3
"""Exact symbolic replay of the q=3m EHPS torsion-triangle wall.

The primary claim is algebraic for every integer m >= 2.  Affine coordinates
are represented as exact pairs (coefficient of m, constant), so the verifier
checks the whole family rather than a finite list of quotient samples.
"""

from __future__ import annotations

import argparse
import copy
import itertools
import json
from collections import defaultdict
from fractions import Fraction

Affine = tuple[int, int]
Polynomial = tuple[int, int, int]
Point = tuple[Affine, Affine]
Vertex = tuple[Point, Point, Point]

Q: Affine = (3, 0)
ONE: Affine = (0, 1)
ZERO: Affine = (0, 0)
ROLES = ("P1", "P2", "P3", "B", "K")
WORDS = (
    ("P1", "K", "B"),
    ("B", "K", "P1"),
    ("P2", "B", "P2"),
    ("P3", "B", "B"),
    ("B", "B", "P3"),
)
VERDICT = "PASS_Q3M_TORSION_TRIANGLE_FAMILY"


SPEC = {
    "assignment": [7, 7, 7, 6, 7],
    "scope": {
        "q_family": "q=3m with integer m>=2",
        "finite_quotient_only": True,
        "continuum_claim": False,
        "new_r3_bound": False,
        "erdos142_solved": False,
    },
    "points": {
        "A": [(3, -3), (1, -1)],
        "B": [(3, -3), (3, -1)],
        "C": [(3, -3), (1, -1)],
        "D": [(3, -3), (2, -1)],
    },
    "preimages": {
        "A": [(2, 0), (0, 2)],
        "B": [(3, -1), (0, 2)],
        "C": [(2, 0), (0, 2)],
        "D": [(2, -1), (0, 2)],
    },
    "d4_indices": {"A": 7, "B": 6, "C": 7, "D": 6},
    "rows": [["X", "Y", "Z"], ["Y", "X", "Z"], ["X", "Z", "Y"]],
    "word_rows": [[2, 3, 3], [3, 2, 3], [2, 3, 3]],
    "rhs_polynomials": [[1, 0, 0], [1, 0, 0], [4, 0, 0]],
}


def aff(value) -> Affine:
    if len(value) != 2 or any(type(item) is not int for item in value):
        raise AssertionError("affine coordinate")
    return int(value[0]), int(value[1])


def point(value) -> Point:
    if len(value) != 2:
        raise AssertionError("point")
    return aff(value[0]), aff(value[1])


def a_add(x: Affine, y: Affine) -> Affine:
    return x[0] + y[0], x[1] + y[1]


def a_sub(x: Affine, y: Affine) -> Affine:
    return x[0] - y[0], x[1] - y[1]


def a_scale(c: int, x: Affine) -> Affine:
    return c * x[0], c * x[1]


def a_eval(x: Affine, m: int) -> int:
    return x[0] * m + x[1]


def nonnegative_tail(x: Affine) -> bool:
    return x[0] >= 0 and a_eval(x, 2) >= 0


def positive_tail(x: Affine) -> bool:
    return x[0] >= 0 and a_eval(x, 2) > 0


def p_add(x: Polynomial, y: Polynomial) -> Polynomial:
    return tuple(x[i] + y[i] for i in range(3))  # type: ignore[return-value]


def p_scale(c: int, x: Polynomial) -> Polynomial:
    return tuple(c * item for item in x)  # type: ignore[return-value]


def square(x: Affine) -> Polynomial:
    return x[0] * x[0], 2 * x[0] * x[1], x[1] * x[1]


def d4_symbolic(p: Point, index: int) -> Point:
    x, y = p
    if index & 1:
        x = a_sub(a_sub(Q, ONE), x)
    if index & 2:
        y = a_sub(a_sub(Q, ONE), y)
    if index & 4:
        x, y = y, x
    return x, y


def canonical_for_all_m(p: Point) -> bool:
    return all(
        nonnegative_tail(coordinate)
        and nonnegative_tail(a_sub(a_sub(Q, ONE), coordinate))
        for coordinate in p
    )


def in_t1_for_all_m(p: Point) -> bool:
    x, y = p
    total = a_add(x, y)
    return (
        nonnegative_tail(a_sub(a_scale(2, x), Q))
        and positive_tail(a_sub(a_scale(3, total), a_scale(2, Q)))
        and nonnegative_tail(a_sub(a_scale(7, Q), a_scale(6, total)))
    )


def midpoint_residual(left: Vertex, middle: Vertex, right: Vertex) -> tuple[Point, Point, Point]:
    return tuple(
        tuple(
            a_sub(a_add(left[slot][coordinate], right[slot][coordinate]), a_scale(2, middle[slot][coordinate]))
            for coordinate in range(2)
        )
        for slot in range(3)
    )  # type: ignore[return-value]


def vertex_cost(left: Vertex, right: Vertex) -> Polynomial:
    result: Polynomial = (0, 0, 0)
    for slot in range(3):
        for coordinate in range(2):
            result = p_add(result, square(a_sub(left[slot][coordinate], right[slot][coordinate])))
    return result


def verify_symbolic(spec: dict) -> dict[str, object]:
    if spec.get("assignment") != [7, 7, 7, 6, 7]:
        raise AssertionError("assignment")
    expected_scope = {
        "q_family": "q=3m with integer m>=2",
        "finite_quotient_only": True,
        "continuum_claim": False,
        "new_r3_bound": False,
        "erdos142_solved": False,
    }
    if spec.get("scope") != expected_scope:
        raise AssertionError("scope")

    points = {name: point(value) for name, value in spec["points"].items()}
    preimages = {name: point(value) for name, value in spec["preimages"].items()}
    if set(points) != {"A", "B", "C", "D"} or set(preimages) != set(points):
        raise AssertionError("named points")
    if points["A"] != points["C"]:
        raise AssertionError("A=C")
    for name in points:
        if not canonical_for_all_m(points[name]) or not canonical_for_all_m(preimages[name]):
            raise AssertionError("canonical range")
        if not in_t1_for_all_m(preimages[name]):
            raise AssertionError("T1 incidence")
        if d4_symbolic(preimages[name], spec["d4_indices"][name]) != points[name]:
            raise AssertionError("D4 image")

    # The two active words are W2=(P2,B,P2) and W3=(P3,B,B).
    supports = {"A": 7, "B": 6, "C": 7, "D": 6}
    if any(spec["d4_indices"][name] != supports[name] for name in supports):
        raise AssertionError("role support")
    vertices: dict[str, Vertex] = {
        "X": (points["A"], points["B"], points["C"]),
        "Y": (points["A"], points["B"], points["B"]),
        "Z": (points["A"], points["B"], points["D"]),
    }
    if len(set(vertices.values())) != 3:
        raise AssertionError("distinct torsion vertices")

    expected_carries = (
        ((0, 0), (0, 0), (0, -1)),
        ((0, 0), (0, 0), (0, 1)),
        ((0, 0), (0, 0), (0, 0)),
    )
    rows = spec["rows"]
    word_rows = spec["word_rows"]
    rhs_expected = [tuple(row) for row in spec["rhs_polynomials"]]
    if len(rows) != 3 or len(word_rows) != 3 or len(rhs_expected) != 3:
        raise AssertionError("three rows")
    cancellation: defaultdict[tuple[int, Vertex], int] = defaultdict(int)
    rhs_actual = []
    for row_number, (names, word_indices) in enumerate(zip(rows, word_rows)):
        if len(names) != 3 or len(word_indices) != 3:
            raise AssertionError("row arity")
        left, middle, right = (vertices[name] for name in names)
        residual = midpoint_residual(left, middle, right)
        expected = tuple(
            tuple(a_scale(component, Q) for component in carry_pair)
            for carry_pair in expected_carries[row_number]
        )
        if residual != expected:
            raise AssertionError("midpoint or carry")
        for vertex_value, word_index, sign in zip((left, middle, right), word_indices, (1, -2, 1)):
            if word_index not in (2, 3):
                raise AssertionError("active word")
            word = WORDS[word_index]
            expected_indices = tuple(7 if role in ("P2", "P3") else 6 for role in word)
            actual_indices = tuple(
                spec["d4_indices"]["A"] if p == points["A"] else
                spec["d4_indices"]["C"] if p == points["C"] else
                spec["d4_indices"]["B"] if p == points["B"] else
                spec["d4_indices"]["D"]
                for p in vertex_value
            )
            # A=C symbolically; their common support is D4[7].
            actual_indices = tuple(7 if p == points["A"] else index for p, index in zip(vertex_value, actual_indices))
            if actual_indices != expected_indices:
                raise AssertionError("word incidence")
            cancellation[word_index, vertex_value] += sign
        rhs_actual.append(vertex_cost(left, right))
    if any(cancellation.values()):
        raise AssertionError("potential coefficients")
    if rhs_actual != rhs_expected or rhs_actual != [(1, 0, 0), (1, 0, 0), (4, 0, 0)]:
        raise AssertionError("raw costs")
    rhs_sum: Polynomial = (0, 0, 0)
    for value in rhs_actual:
        rhs_sum = p_add(rhs_sum, value)
    q_squared = square(Q)
    if rhs_sum != (6, 0, 0) or p_scale(3, rhs_sum) != p_scale(2, q_squared):
        raise AssertionError("normalized contradiction")

    return {
        "q_family": "q=3m, m>=2",
        "selected_rows": 3,
        "raw_contradiction": "6m^2",
        "normalized_contradiction": "2/3",
        "potential_model": "arbitrary per-cylinder vertex (hence arbitrary on the union)",
    }


def d4_finite(p: tuple[int, int], index: int, q: int) -> tuple[int, int]:
    x, y = p
    if index & 1:
        x = q - 1 - x
    if index & 2:
        y = q - 1 - y
    if index & 4:
        x, y = y, x
    return x, y


def base_support_q6() -> frozenset[tuple[int, int]]:
    q = 6
    return frozenset(
        (x, y)
        for x in range(q)
        for y in range(q)
        if (x >= 3 and 5 <= x + y <= 7)
        or (x >= 3 and y < 3 and x + y == 8)
        or (x < 3 and y >= 3 and x + y == 8 and 2 * x + y >= 10)
    )


def q6_scope_audit() -> dict[str, object]:
    q = 6
    base = base_support_q6()
    images = tuple(frozenset(d4_finite(p, index, q) for p in base) for index in range(8))
    if len(base) != 9 or len(set(images)) != 8:
        raise AssertionError("q6 supports")

    def mass(assignment: tuple[int, ...]) -> int:
        union = set()
        for word in WORDS:
            union.update(itertools.product(*(images[assignment[ROLES.index(role)]] for role in word)))
        return len(union)

    torsion = tuple(
        (x, y)
        for x in range(q)
        for y in range(q)
        if (x, y) != (0, 0) and (3 * x) % q == 0 and (3 * y) % q == 0
    )

    def hit(assignment: tuple[int, ...]) -> bool:
        p2, p3, bucket = images[assignment[1]], images[assignment[2]], images[assignment[3]]
        if not p2 & p3:
            return False
        return any(
            ((b[0] + u[0]) % q, (b[1] + u[1]) % q) in p2
            and ((b[0] - u[0]) % q, (b[1] - u[1]) % q) in bucket
            for b in bucket
            for u in torsion
        )

    assignments = tuple(itertools.product(range(8), repeat=5))
    masses = {assignment: mass(assignment) for assignment in assignments}
    maximum = max(masses.values())
    maximizers = tuple(a for a in assignments if masses[a] == maximum)
    covered = tuple(a for a in maximizers if hit(a))
    intersections = tuple(a for a in maximizers if images[a[1]] & images[a[2]])
    if (maximum, len(maximizers), len(covered)) != (3645, 256, 128) or covered != intersections:
        raise AssertionError("q6 torsion coverage")
    return {
        "assignments": 8**5,
        "maximum_mass": maximum,
        "maximum_mass_assignments": len(maximizers),
        "torsion_template_covered": len(covered),
        "outside_this_template": len(maximizers) - len(covered),
        "template_iff_P2_intersects_P3": True,
    }


def planted_failures() -> dict[str, str]:
    mutations = {
        "assignment": lambda s: s["assignment"].__setitem__(1, 6),
        "point": lambda s: s["points"]["D"].__setitem__(1, (2, 0)),
        "preimage": lambda s: s["preimages"]["B"].__setitem__(0, (3, 0)),
        "d4_index": lambda s: s["d4_indices"].__setitem__("B", 7),
        "midpoint_row": lambda s: s["rows"][1].__setitem__(1, "Y"),
        "word_row": lambda s: s["word_rows"][0].__setitem__(0, 3),
        "raw_cost": lambda s: s["rhs_polynomials"][2].__setitem__(0, 3),
        "scope": lambda s: s["scope"].__setitem__("continuum_claim", True),
    }
    report = {}
    for name, mutate in mutations.items():
        bad = copy.deepcopy(SPEC)
        mutate(bad)
        try:
            verify_symbolic(bad)
        except (AssertionError, KeyError, TypeError, ValueError):
            report[name] = "rejected"
        else:
            raise AssertionError(f"planted failure survived: {name}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    family = verify_symbolic(copy.deepcopy(SPEC))
    coverage = q6_scope_audit()
    output = {
        "verdict": VERDICT,
        "family": family,
        "q6_scope": coverage,
        "finite_quotient_only": True,
        "continuum_certificate": False,
        "new_r3_bound": False,
        "erdos142_solved": False,
    }
    if args.self_test:
        controls = planted_failures()
        if len(controls) != 8 or set(controls.values()) != {"rejected"}:
            raise AssertionError("planted failures")
        output["planted_corruptions"] = "all 8 rejected"
    print(VERDICT)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

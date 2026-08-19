#!/usr/bin/env python3
"""Stdlib-only exact replay for the q=24 mirror-exclusive additive wall."""

from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path


Q = 24
ROLES = ("P1", "P2", "P3", "B", "K")
CODEWORDS = (
    ("P1", "K", "B"),
    ("B", "K", "P1"),
    ("P2", "B", "P2"),
    ("P3", "B", "B"),
    ("B", "B", "P3"),
)
THRESHOLD = Fraction(7, 24) ** 3


def published_T():
    t1, t2, t3 = set(), set(), set()
    for i in range(Q):
        for j in range(Q):
            s = i + j
            if 2 * i >= Q and 6 * s > 4 * Q and 6 * s <= 7 * Q:
                t1.add((i, j))
            if (
                2 * i >= Q
                and 2 * j < Q
                and 12 * s >= 14 * Q + 12
                and 12 * s <= 17 * Q
            ):
                t2.add((i, j))
            if (
                2 * i < Q
                and 2 * j >= Q
                and 12 * s >= 14 * Q + 12
                and 12 * s <= 17 * Q
                and 2 * (2 * i + j) >= 3 * Q + 2
            ):
                t3.add((i, j))
    if t1 & t2 or t1 & t3 or t2 & t3:
        raise AssertionError("published pieces unexpectedly overlap")
    return t1 | t2 | t3


def point(value):
    if not (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(x, int) and 0 <= x < Q for x in value)
    ):
        raise AssertionError(f"invalid quotient point: {value!r}")
    return tuple(value)


def verify_orientation(payload, b_support, p3_support):
    supports = {
        "P1": set(),
        "P2": set(),
        "P3": set(p3_support),
        "B": set(b_support),
        "K": set(),
    }
    if payload["b_count"] != len(b_support):
        raise AssertionError("B support count mismatch")
    if payload["p3_count"] != len(p3_support):
        raise AssertionError("P3 support count mismatch")
    if payload["potential_variable_count"] != len(b_support) + len(p3_support):
        raise AssertionError("potential variable count mismatch")
    rows = payload["rows"]
    if payload["farkas_row_count"] != len(rows):
        raise AssertionError("Farkas row count mismatch")

    coefficient_sum = {}
    positive_cost_numerator = 0
    total_multiplicity = 0
    for row_index, row in enumerate(rows):
        multiplier = int(row["multiplier"])
        if multiplier <= 0 or str(multiplier) != row["multiplier"]:
            raise AssertionError(f"row {row_index}: invalid multiplier")
        word_indices = row["word_indices"]
        if not (
            isinstance(word_indices, list)
            and len(word_indices) == 3
            and all(index in (3, 4) for index in word_indices)
        ):
            raise AssertionError(f"row {row_index}: inactive word index")
        u, v, w = (CODEWORDS[index] for index in word_indices)
        witnesses = row["local_witnesses"]
        if not isinstance(witnesses, list) or len(witnesses) != 3:
            raise AssertionError(f"row {row_index}: expected three local witnesses")

        row_cost = 0
        for coordinate, witness in enumerate(witnesses):
            expected_roles = (u[coordinate], v[coordinate], w[coordinate])
            if tuple(witness["roles"]) != expected_roles:
                raise AssertionError(f"row {row_index}: role triple mismatch")
            x = point(witness["x"])
            y = point(witness["y"])
            z = point(witness["z"])
            r, s, t = expected_roles
            if x not in supports[r] or y not in supports[s] or z not in supports[t]:
                raise AssertionError(f"row {row_index}: witness outside exclusive core")

            numerators = (x[0] + z[0] - 2 * y[0], x[1] + z[1] - 2 * y[1])
            if numerators[0] % Q or numerators[1] % Q:
                raise AssertionError(f"row {row_index}: not a modular midpoint")
            carry = (numerators[0] // Q, numerators[1] // Q)
            if list(carry) != witness["carry"]:
                raise AssertionError(f"row {row_index}: carry mismatch")
            if any(value not in (-1, 0, 1) for value in carry):
                raise AssertionError(f"row {row_index}: carry outside canonical range")

            raw_cost = (x[0] - z[0]) ** 2 + (x[1] - z[1]) ** 2
            if raw_cost != witness["cost_numerator"]:
                raise AssertionError(f"row {row_index}: raw cost mismatch")
            row_cost += raw_cost
            for role, p, coefficient in ((r, x, 1), (s, y, -2), (t, z, 1)):
                key = (role, p)
                coefficient_sum[key] = (
                    coefficient_sum.get(key, 0) + multiplier * coefficient
                )

        positive_cost_numerator += multiplier * row_cost
        total_multiplicity += multiplier

    nonzero = {key: value for key, value in coefficient_sum.items() if value}
    if nonzero:
        sample = next(iter(nonzero.items()))
        raise AssertionError(f"potential coefficients do not cancel: {sample}")
    if positive_cost_numerator <= 0:
        raise AssertionError("summed raw cost is not positive")
    if str(positive_cost_numerator) != payload["positive_cost_numerator"]:
        raise AssertionError("positive-cost total mismatch")
    if payload["cost_denominator"] != Q * Q:
        raise AssertionError("cost denominator mismatch")
    return {
        "name": payload["name"],
        "rows": len(rows),
        "total_multiplicity_digits": len(str(total_multiplicity)),
        "positive_cost_numerator_digits": len(str(positive_cost_numerator)),
        "contradiction": f"0 >= {positive_cost_numerator}/{Q * Q}",
    }


def verify_certificate(data):
    if data["schema"] != "erdos142-five-role-additive-farkas-v1":
        raise AssertionError("unknown certificate schema")
    if data["q"] != Q or data["epsilon"] != "1/24":
        raise AssertionError("quotient metadata mismatch")
    if tuple(data["roles"]) != ROLES:
        raise AssertionError("role list mismatch")
    if tuple(tuple(word) for word in data["codewords"]) != CODEWORDS:
        raise AssertionError("codeword list mismatch")
    if data["active_word_indices"] != [3, 4]:
        raise AssertionError("active words mismatch")

    base = published_T()
    transpose = {(j, i) for i, j in base}
    intersection = base & transpose
    base_exclusive = base - transpose
    transpose_exclusive = transpose - base
    census = data["support_definition"]
    expected_census = {
        "T_count": 163,
        "transpose_T_count": 163,
        "intersection_count": 53,
        "exclusive_count_each": 110,
    }
    if census != expected_census:
        raise AssertionError(f"support census mismatch: {census}")
    if (
        len(base) != 163
        or len(transpose) != 163
        or len(intersection) != 53
        or len(base_exclusive) != 110
        or len(transpose_exclusive) != 110
    ):
        raise AssertionError("reconstructed support census mismatch")

    orientations = data["orientations"]
    if len(orientations) != 2:
        raise AssertionError("expected two role orientations")
    summaries = [
        verify_orientation(orientations[0], base_exclusive, transpose_exclusive),
        verify_orientation(orientations[1], transpose_exclusive, base_exclusive),
    ]

    # If k of the 53 intersection points are assigned to B and the rest to P3,
    # the two disjoint cylinders have exactly 2*(110+k)^2*(163-k) points.
    mass_passing_k = []
    for k in range(54):
        b = 110 + k
        p3 = 163 - k
        candidate_mass = Fraction(2 * b * b * p3, Q**6)
        if candidate_mass > THRESHOLD:
            mass_passing_k.append(k)
    if mass_passing_k != list(range(18, 54)):
        raise AssertionError("unexpected mass-passing allocation range")

    scope = data["claim_scope"]
    expected_scope = {
        "additive_role_potential_only": True,
        "finite_q24_only": True,
        "all_disjoint_intersection_allocations": True,
        "arbitrary_global_6d_potential_excluded": False,
        "continuum_certificate": False,
        "new_r3_bound": False,
        "erdos142_solved": False,
    }
    if scope != expected_scope:
        raise AssertionError("claim scope mismatch")
    return {
        "support_census": expected_census,
        "mass_passing_k_range": [18, 53],
        "orientations": summaries,
    }


def expect_failure(data, mutation_name, mutate):
    planted = copy.deepcopy(data)
    mutate(planted)
    try:
        verify_certificate(planted)
    except (AssertionError, KeyError, ValueError, TypeError):
        return mutation_name
    raise AssertionError(f"planted failure was not detected: {mutation_name}")


def main() -> int:
    path = Path(__file__).with_name("certificate.json")
    encoded = path.read_bytes()
    data = json.loads(encoded)
    summary = verify_certificate(data)
    planted = [
        expect_failure(
            data,
            "multiplier",
            lambda d: d["orientations"][0]["rows"][0].__setitem__(
                "multiplier", str(int(d["orientations"][0]["rows"][0]["multiplier"]) + 1)
            ),
        ),
        expect_failure(
            data,
            "raw-cost",
            lambda d: d["orientations"][0]["rows"][0]["local_witnesses"][0].__setitem__(
                "cost_numerator",
                d["orientations"][0]["rows"][0]["local_witnesses"][0]["cost_numerator"] + 1,
            ),
        ),
        expect_failure(
            data,
            "carry",
            lambda d: d["orientations"][1]["rows"][0]["local_witnesses"][0]["carry"].__setitem__(
                0,
                d["orientations"][1]["rows"][0]["local_witnesses"][0]["carry"][0] + 1,
            ),
        ),
        expect_failure(
            data,
            "missing-row",
            lambda d: d["orientations"][1]["rows"].pop(),
        ),
    ]
    print("PASS_MIRROR_EXCLUSIVE_ADDITIVE_WALL")
    print("certificate_sha256", hashlib.sha256(encoded).hexdigest().upper())
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("planted_failures", ",".join(planted))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

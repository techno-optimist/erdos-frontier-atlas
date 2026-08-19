#!/usr/bin/env python3
"""Stdlib-only semantic verifier for the q=6 pair-coordinate Farkas walls."""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q = 6
PAIRS = ((0, 1), (0, 2), (1, 2))
ROLES = ("P1", "P2", "P3", "B", "K")
CODEWORDS = (
    ("P1", "K", "B"),
    ("B", "K", "P1"),
    ("P2", "B", "P2"),
    ("P3", "B", "B"),
    ("B", "B", "P3"),
)
PACKETS = (
    ("A", HERE / "certificate_A.json", "46DEA1B400FE3C7A43F7B6B48107E2F4858EC62661BEF026C3E08182587A2F6E"),
    ("B", HERE / "certificate_B.json", "6A504E00146D97DA7E83E6D77BF37C26CD47A7493D998096236F0212A035F7AF"),
)
VERDICT = "PASS_Q6_PAIR_COORDINATE_EXACT_FARKAS_WALLS"


def ehps_support() -> frozenset[tuple[int, int]]:
    """Reconstruct the published EHPS tile with epsilon=1/q exactly."""
    out = set()
    eps = Fraction(1, Q)
    for x, y in itertools.product(range(Q), repeat=2):
        a, b = Fraction(x, Q), Fraction(y, Q)
        s = a + b
        t1 = a >= Fraction(1, 2) and s > Fraction(2, 3) and s <= Fraction(7, 6)
        t2 = (
            a >= Fraction(1, 2)
            and b < Fraction(1, 2)
            and s >= Fraction(7, 6) + eps
            and s <= Fraction(17, 12)
        )
        t3 = (
            a < Fraction(1, 2)
            and b >= Fraction(1, 2)
            and s >= Fraction(7, 6) + eps
            and s <= Fraction(17, 12)
            and 2 * a + b >= Fraction(3, 2) + eps
        )
        if t1 or t2 or t3:
            out.add((x, y))
    assert len(out) == 9
    return frozenset(out)


def d4_image(base: frozenset[tuple[int, int]], code: int) -> frozenset[tuple[int, int]]:
    out = set()
    for x, y in base:
        if code & 1:
            x = Q - 1 - x
        if code & 2:
            y = Q - 1 - y
        if code & 4:
            x, y = y, x
        out.add((x, y))
    return frozenset(out)


def d4_images() -> tuple[frozenset[tuple[int, int]], ...]:
    images = tuple(d4_image(ehps_support(), code) for code in range(8))
    assert len(set(images)) == 8 and all(len(image) == 9 for image in images)
    return images


def midpoint_scalar_solutions(x: int, z: int) -> tuple[int, ...]:
    s = (x + z) % Q
    g = math.gcd(2, Q)
    if s % g:
        return ()
    reduced = Q // g
    y0 = (s // g) * pow(2 // g, -1, reduced) % reduced
    return tuple(y0 + k * reduced for k in range(g))


def midpoint_solutions(x: tuple[int, int], z: tuple[int, int]) -> tuple[tuple[int, int], ...]:
    return tuple(
        (u, v)
        for u in midpoint_scalar_solutions(x[0], z[0])
        for v in midpoint_scalar_solutions(x[1], z[1])
    )


def carry_vector(x: tuple[int, int], y: tuple[int, int], z: tuple[int, int]) -> tuple[int, int]:
    numerators = tuple(x[i] + z[i] - 2 * y[i] for i in range(2))
    assert all(value % Q == 0 for value in numerators)
    return tuple(value // Q for value in numerators)


def raw_cost_numerator(x: tuple[int, int], z: tuple[int, int]) -> int:
    return sum((x[i] - z[i]) ** 2 for i in range(2))


def supports_and_mass(assignment: tuple[int, ...]):
    images = d4_images()
    supports = {role: images[assignment[i]] for i, role in enumerate(ROLES)}
    cylinders = [set(itertools.product(*(supports[role] for role in word))) for word in CODEWORDS]
    assert all(len(cylinder) == 9**3 for cylinder in cylinders)
    assert all(not (cylinders[i] & cylinders[j]) for i in range(5) for j in range(i))
    union_mass = len(set().union(*cylinders))
    assert union_mass == 3645
    assert union_mass * 24**3 > 7**3 * Q**6
    return supports, union_mass


def verify_packet(packet: dict[str, object]) -> dict[str, object]:
    assert packet.get("packet_format") == "erdos-142-q6-pair-coordinate-semantic-farkas-v1"
    assert packet.get("scope") == {
        "finite_q": 6,
        "continuum_claim": False,
        "potential_ansatz": "separate H[c,01], H[c,02], H[c,12] for each of five codeword cylinders",
        "ordered_word_triples_in_model": 125,
        "all_even_q_midpoint_branches": True,
        "cost": "raw canonical endpoint squared Euclidean cost / q^2",
    }
    assert packet.get("variable_count") == 1215
    assignment = tuple(packet["assignment"])
    assert assignment in ((7, 7, 7, 6, 7), (7, 6, 7, 6, 7))
    label = "A" if assignment == (7, 7, 7, 6, 7) else "B"
    assert packet.get("representative_label") == label
    supports, union_mass = supports_and_mass(assignment)

    variable_id = {}
    variable_count = 0
    for cylinder, word in enumerate(CODEWORDS):
        points = [tuple(sorted(supports[role])) for role in word]
        for pair in PAIRS:
            for x in points[pair[0]]:
                for y in points[pair[1]]:
                    variable_id[cylinder, pair, x, y] = variable_count
                    variable_count += 1
    assert variable_count == 1215

    source_indices = packet["source_row_indices"]
    multipliers = packet["integer_multipliers"]
    rows = packet["selected_rows"]
    assert len(source_indices) == len(multipliers) == len(rows)
    assert len(set(map(int, source_indices))) == len(source_indices)
    assert all(int(index) >= 0 for index in source_indices)

    cancellation = [0] * variable_count
    positive = 0
    for multiplier, row in zip(multipliers, rows):
        assert isinstance(multiplier, int) and multiplier > 0
        provenance = row["provenance"]
        a, b, c = map(int, provenance["triple"])
        assert all(0 <= index < 5 for index in (a, b, c))
        witnesses = provenance["witnesses"]
        assert len(witnesses) == 3
        assert [witness["coordinate"] for witness in witnesses] == [0, 1, 2]

        derived = defaultdict(int)
        rhs = 0
        for coordinate, witness in enumerate(witnesses):
            x, y, z = map(tuple, (witness["x"], witness["y"], witness["z"]))
            for point, word_index in ((x, a), (y, b), (z, c)):
                assert point in supports[CODEWORDS[word_index][coordinate]]
            assert y in midpoint_solutions(x, z)
            carry = carry_vector(x, y, z)
            assert list(carry) == witness["carry"] and all(value in (-1, 0, 1) for value in carry)
            raw = raw_cost_numerator(x, z)
            assert raw == witness["raw_cost_numerator"]
            rhs += raw

        for cylinder, sign, endpoint in ((a, 1, "x"), (b, -2, "y"), (c, 1, "z")):
            points = [tuple(witness[endpoint]) for witness in witnesses]
            for pair in PAIRS:
                key = (cylinder, pair, points[pair[0]], points[pair[1]])
                derived[variable_id[key]] += sign
        derived_items = [[index, value] for index, value in sorted(derived.items()) if value]
        stored_items = [[int(index), int(value)] for index, value in row["coefficients"]]
        assert stored_items == derived_items and int(row["rhs_numerator"]) == rhs

        for index, value in derived.items():
            cancellation[index] += multiplier * value
        positive += multiplier * rhs

    assert not any(cancellation)
    assert positive > 0 and positive == int(packet["positive_contradiction_raw"])
    return {
        "representative": label,
        "assignment": list(assignment),
        "variables": variable_count,
        "selected_rows": len(rows),
        "union_mass_count": union_mass,
        "mass_gate_ratio": "1080/343",
        "positive_contradiction_raw": str(positive),
    }


def expect_rejected(packet: dict[str, object], mutate) -> None:
    bad = copy.deepcopy(packet)
    mutate(bad)
    try:
        verify_packet(bad)
    except (AssertionError, KeyError, IndexError, TypeError, ValueError):
        return
    raise AssertionError("planted corruption was accepted")


def self_test(packet: dict[str, object]) -> None:
    expect_rejected(packet, lambda p: p["integer_multipliers"].__setitem__(0, p["integer_multipliers"][0] + 1))
    expect_rejected(packet, lambda p: p["selected_rows"][0]["provenance"]["witnesses"][0]["y"].__setitem__(0, (p["selected_rows"][0]["provenance"]["witnesses"][0]["y"][0] + 1) % Q))
    expect_rejected(packet, lambda p: p["selected_rows"][0]["provenance"]["witnesses"][0]["carry"].__setitem__(0, 99))
    expect_rejected(packet, lambda p: p["selected_rows"][0]["provenance"]["witnesses"][0].__setitem__("raw_cost_numerator", -1))
    expect_rejected(packet, lambda p: p["selected_rows"][0]["provenance"]["triple"].__setitem__(0, 4))
    expect_rejected(packet, lambda p: p["selected_rows"][0]["coefficients"][0].__setitem__(0, (p["selected_rows"][0]["coefficients"][0][0] + 1) % 1215))
    expect_rejected(packet, lambda p: p.__setitem__("assignment", [0, 0, 0, 0, 0]))
    expect_rejected(packet, lambda p: p["selected_rows"].pop())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    reports = []
    packet_hashes = {}
    packets = []
    for label, path, expected_hash in PACKETS:
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest().upper()
        assert digest == expected_hash
        packet = json.loads(raw)
        report = verify_packet(packet)
        assert report["representative"] == label
        reports.append(report)
        packet_hashes[label] = digest.lower()
        packets.append(packet)
    output = {
        "verdict": VERDICT,
        "replays": reports,
        "packet_sha256": packet_hashes,
        "finite_q_only": True,
        "continuum_certificate": False,
        "new_r3_bound": False,
        "erdos142_solved": False,
    }
    if args.self_test:
        for packet in packets:
            self_test(packet)
        output["planted_corruptions"] = "all 16 rejected"
    print(VERDICT)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

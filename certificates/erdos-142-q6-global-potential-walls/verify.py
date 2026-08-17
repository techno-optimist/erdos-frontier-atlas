#!/usr/bin/env python3
"""Stdlib semantic replay for the recovered global-potential q=6 Farkas rays."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
Q = 6
ROLES = ("P1", "P2", "P3", "B", "K")
WORDS = (("P1", "K", "B"), ("B", "K", "P1"), ("P2", "B", "P2"), ("P3", "B", "B"), ("B", "B", "P3"))
SCOPE = {
    "finite_q": 6,
    "continuum_claim": False,
    "potential_ansatz": "one arbitrary potential value for each vertex of each of five codeword cylinders",
    "ordered_word_triples_in_model": 125,
    "all_even_q_midpoint_branches": True,
    "cost": "raw canonical endpoint squared Euclidean cost / q^2",
}
EXPECTED = {"A": (7, 7, 7, 6, 7), "B": (7, 6, 7, 6, 7)}
PACKETS = {
    "A": (HERE / "certificate_A.json", "4E9FE8E052EE87E519A9D191E3AC46052F032BC7FE474CDD3E3B6D9B903515EF"),
    "B": (HERE / "certificate_B.json", "DC865A45D6281B9640402AE341CB65B5D55B3EAC82AE9F994687C59B81B1240F"),
}
VERDICT = "PASS_Q6_GLOBAL_POTENTIAL_EXACT_FARKAS_WALLS"


def base_support() -> frozenset[tuple[int, int]]:
    # Exact q=6 specialization of the three half-open EHPS pieces with eps=1/q.
    return frozenset(
        (x, y)
        for x in range(Q)
        for y in range(Q)
        if (x >= 3 and 5 <= x + y <= 7)
        or (x >= 3 and y < 3 and x + y == 8)
        or (x < 3 and y >= 3 and x + y == 8 and 2 * x + y >= 10)
    )


def d4_image(support: frozenset[tuple[int, int]], index: int) -> frozenset[tuple[int, int]]:
    image = []
    for x, y in support:
        if index & 1:
            x = Q - 1 - x
        if index & 2:
            y = Q - 1 - y
        if index & 4:
            x, y = y, x
        image.append((x, y))
    return frozenset(image)


def midpoint(x: tuple[int, int], y: tuple[int, int], z: tuple[int, int]) -> bool:
    return all((2 * y[i] - x[i] - z[i]) % Q == 0 for i in range(2))


def carry(x: tuple[int, int], y: tuple[int, int], z: tuple[int, int]) -> list[int]:
    if not midpoint(x, y, z):
        raise AssertionError("not a modular midpoint")
    return [(x[i] + z[i] - 2 * y[i]) // Q for i in range(2)]


def cost(x: tuple[int, int], z: tuple[int, int]) -> int:
    return sum((x[i] - z[i]) ** 2 for i in range(2))


def build_model(assignment: tuple[int, ...]):
    base = base_support()
    if len(base) != 9:
        raise AssertionError("EHPS q=6 support size")
    images = [d4_image(base, index) for index in range(8)]
    if len(set(images)) != 8:
        raise AssertionError("D4 images")
    supports = {role: images[assignment[i]] for i, role in enumerate(ROLES)}
    labels, vid, cylinders = [], {}, []
    for cylinder, word in enumerate(WORDS):
        vertices_here = set()
        for p0 in sorted(supports[word[0]]):
            for p1 in sorted(supports[word[1]]):
                for p2 in sorted(supports[word[2]]):
                    vertex = (p0, p1, p2)
                    vertices_here.add(vertex)
                    vid[cylinder, vertex] = len(labels)
                    labels.append((cylinder, vertex))
        if len(vertices_here) != 9**3:
            raise AssertionError("cylinder size")
        cylinders.append(vertices_here)
    if len(labels) != 3645:
        raise AssertionError("global potential variable count")
    if any(cylinders[i] & cylinders[j] for i in range(5) for j in range(i)):
        raise AssertionError("cylinders overlap")
    union_mass = len(set().union(*cylinders))
    if union_mass != 3645 or union_mass * 24**3 <= 7**3 * Q**6:
        raise AssertionError("finite mass gate")
    actual_count = 0
    for a in range(5):
        for b in range(5):
            for c in range(5):
                local_counts = []
                for coordinate in range(3):
                    count_here = 0
                    for x in supports[WORDS[a][coordinate]]:
                        for z in supports[WORDS[c][coordinate]]:
                            for y in supports[WORDS[b][coordinate]]:
                                if midpoint(x, y, z):
                                    count_here += 1
                    local_counts.append(count_here)
                actual_count += local_counts[0] * local_counts[1] * local_counts[2]
    if actual_count != 1128545:
        raise AssertionError("all even-q global midpoint branches")
    return supports, vid, actual_count, union_mass


def verify(packet: dict[str, object]) -> dict[str, object]:
    if packet.get("packet_format") != "erdos-142-q6-global-potential-semantic-farkas-v1":
        raise AssertionError("packet format")
    if packet.get("scope") != SCOPE or packet.get("q") != Q:
        raise AssertionError("scope")
    label = packet.get("representative_label")
    if label not in EXPECTED or tuple(packet.get("assignment", ())) != EXPECTED[label]:
        raise AssertionError("representative assignment")
    if (packet.get("support_size"), packet.get("cylinder_count"), packet.get("variable_count")) != (9, 5, 3645):
        raise AssertionError("model dimensions")
    supports, vid, actual_count, union_mass = build_model(EXPECTED[label])
    if packet.get("actual_triple_count") != actual_count:
        raise AssertionError("global witness count")
    source_indices = packet.get("source_row_indices")
    multipliers = packet.get("integer_multipliers")
    rows = packet.get("selected_rows")
    if not isinstance(source_indices, list) or len(source_indices) != len(multipliers) or len(rows) != len(multipliers):
        raise AssertionError("ray lengths")
    if len(set(source_indices)) != len(source_indices):
        raise AssertionError("duplicate source index")
    cancellation = defaultdict(int)
    positive = 0
    for source_index, multiplier, row in zip(source_indices, multipliers, rows):
        if not isinstance(source_index, int) or source_index < 0 or not isinstance(multiplier, int) or multiplier <= 0:
            raise AssertionError("source index or multiplier")
        if row.get("source_row_index") != source_index:
            raise AssertionError("source index binding")
        data = row.get("provenance")
        triple = data.get("word_indices")
        points = data.get("points")
        vertices = data.get("vertices")
        if not (isinstance(triple, list) and len(triple) == 3 and all(isinstance(i, int) and 0 <= i < 5 for i in triple)):
            raise AssertionError("word triple")
        if not (isinstance(points, list) and len(points) == 3 and isinstance(vertices, list) and len(vertices) == 3):
            raise AssertionError("global vertices")
        derived = defaultdict(int)
        total_cost = 0
        for coordinate in range(3):
            x, y, z = (tuple(points[k][coordinate]) for k in range(3))
            if any(len(point) != 2 or any(type(v) is not int or not 0 <= v < Q for v in point) for point in (x, y, z)):
                raise AssertionError("canonical coordinate point")
            for point, word_index, slot in ((x, triple[0], coordinate), (y, triple[1], coordinate), (z, triple[2], coordinate)):
                if point not in supports[WORDS[word_index][slot]]:
                    raise AssertionError("role support membership")
            if not midpoint(x, y, z):
                raise AssertionError("midpoint branch")
            # This field is redundant but binds the carry convention used by discovery.
            stored_carries = data.get("carries")
            if not isinstance(stored_carries, list) or len(stored_carries) != 3 or stored_carries[coordinate] != carry(x, y, z):
                raise AssertionError("carry")
            total_cost += cost(x, z)
        if total_cost != data.get("raw_cost_numerator") or total_cost != row.get("rhs_numerator"):
            raise AssertionError("raw cost")
        for point, cylinder, sign, stated_vertex in zip(points, triple, (1, -2, 1), vertices):
            index = vid[cylinder, tuple(tuple(p) for p in point)]
            if index != stated_vertex:
                raise AssertionError("vertex indexing")
            derived[index] += sign
        derived = {index: value for index, value in derived.items() if value}
        stored = [[int(index), int(value)] for index, value in row.get("coefficients", [])]
        expected_coefficients = [[index, value] for index, value in sorted(derived.items())]
        if stored != expected_coefficients:
            raise AssertionError("row coefficients")
        for index, value in derived.items():
            cancellation[index] += multiplier * value
        positive += multiplier * total_cost
    if any(cancellation.values()):
        raise AssertionError("exact coefficient cancellation")
    if positive <= 0 or positive != packet.get("positive_contradiction_raw"):
        raise AssertionError("positive contradiction")
    return {
        "label": label,
        "selected_rows": len(rows),
        "positive_contradiction_raw": str(positive),
        "union_mass_count": union_mass,
        "mass_gate_ratio": "1080/343",
    }


def planted_failures(packet: dict[str, object]) -> dict[str, str]:
    tests = {
        "multiplier": lambda p: p["integer_multipliers"].__setitem__(0, p["integer_multipliers"][0] + 1),
        "midpoint": lambda p: p["selected_rows"][0]["provenance"]["points"][1][0].__setitem__(0, (p["selected_rows"][0]["provenance"]["points"][1][0][0] + 1) % Q),
        "raw_cost": lambda p: p["selected_rows"][0].__setitem__("rhs_numerator", -1),
        "carry": lambda p: p["selected_rows"][0]["provenance"]["carries"][0].__setitem__(0, 99),
        "vertex": lambda p: p["selected_rows"][0]["provenance"]["vertices"].__setitem__(0, 0),
        "coefficients": lambda p: p["selected_rows"][0]["coefficients"][0].__setitem__(0, 0),
        "word": lambda p: p["selected_rows"][0]["provenance"]["word_indices"].__setitem__(0, 4),
        "assignment": lambda p: p.__setitem__("assignment", [0, 0, 0, 0, 0]),
        "missing_row": lambda p: p["selected_rows"].pop(),
    }
    report = {}
    for name, mutate in tests.items():
        bad = copy.deepcopy(packet)
        mutate(bad)
        try:
            verify(bad)
        except (AssertionError, IndexError, KeyError, TypeError, ValueError):
            report[name] = "rejected"
        else:
            raise AssertionError(f"planted failure survived: {name}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    packets, report, hashes = {}, {}, {}
    for label, (path, expected_hash) in PACKETS.items():
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest().upper()
        if digest != expected_hash:
            raise AssertionError(f"{label} packet hash")
        packet = json.loads(raw)
        packets[label] = packet
        report[label] = verify(packet)
        hashes[label] = digest.lower()
    output = {
        "verdict": VERDICT,
        "replays": report,
        "packet_sha256": hashes,
        "finite_q_only": True,
        "continuum_certificate": False,
        "new_r3_bound": False,
        "erdos142_solved": False,
    }
    if args.self_test:
        controls = {label: planted_failures(packet) for label, packet in packets.items()}
        if any(set(item.values()) != {"rejected"} or len(item) != 9 for item in controls.values()):
            raise AssertionError("planted failures")
        output["planted_corruptions"] = "all 18 rejected"
    print(VERDICT)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

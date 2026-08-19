#!/usr/bin/env python3
"""Pure-stdlib replay of the explicit q=18 microbox packing wall.

The frozen JSON contains 433 oriented componentwise-dilation supports and 114
finite common-offset midpoint packets.  This verifier reconstructs every
physical microbox from the q=6 117-cell alphabet and trusts no derived field.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from typing import Any

Q = 6
R = 3
QF = Q * R
MICRO_PER_CELL = R**4
EXPECTED_SCHEMA = "erdos142-q6-r3-explicit-microbox-wall-v1"
EXPECTED_FILE_SHA256 = "e445d0ca22b7c0dcca087bb6bfea60b94cdf30669e59d8b60ea4c9f96e95a18c"
EXPECTED_DILATION_DIGEST = "0bf111f4e4cf673a95de27a5841439d422342ead035ce5ee2fc5901a7166135d"
EXPECTED_PACKETS_DIGEST = "e9f3ecb9c1f30fb0965f1eb9779e7f3ef9799e1fdcb2c36089585e9db3701fa4"
EXPECTED_SEMANTIC_DIGEST = "fda92022923366b59cd065196e84fbb340eadff312284dc8a5fdd7b7ded2fc56"

S0 = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
      (5, 0), (5, 1), (5, 2))
OFFSETS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
           (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
CELLS = tuple((a, b, (a + x) % Q, (b + y) % Q)
              for a, b in S0 for x, y in OFFSETS)


class VerificationError(ValueError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def semantic_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def micro_digits(local: int) -> tuple[int, int, int, int]:
    require(is_plain_int(local) and 0 <= local < MICRO_PER_CELL,
            f"bad local microbox index {local!r}")
    return (local // 27, (local // 9) % 3, (local // 3) % 3, local % 3)


def decode_microbox(identifier: int) -> tuple[int, tuple[int, int, int, int],
                                                  tuple[int, int, int, int]]:
    total = len(CELLS) * MICRO_PER_CELL
    require(is_plain_int(identifier) and 0 <= identifier < total,
            f"microbox id out of range: {identifier!r}")
    cell = identifier // MICRO_PER_CELL
    micro = micro_digits(identifier % MICRO_PER_CELL)
    fine = tuple(R * CELLS[cell][j] + micro[j] for j in range(4))
    return cell, micro, fine


def exact_keyset(value: dict, expected: set[str], where: str) -> None:
    require(isinstance(value, dict), f"{where} is not an object")
    require(set(value) == expected,
            f"{where} keys {sorted(value)} != {sorted(expected)}")


def verify_header(payload: dict) -> None:
    exact_keyset(payload,
                 {"schema", "q", "residual_subdivision", "fine_q",
                  "coarse_cells", "microboxes", "dilation", "packets",
                  "gate", "digests"}, "top level")
    require(payload["schema"] == EXPECTED_SCHEMA, "wrong schema")
    require(payload["q"] == Q, "wrong coarse q")
    require(payload["residual_subdivision"] == R, "wrong subdivision")
    require(payload["fine_q"] == QF, "wrong fine q")
    require(len(CELLS) == len(set(CELLS)) == payload["coarse_cells"] == 117,
            "117-cell alphabet reconstruction failed")
    require(payload["microboxes"] == len(CELLS) * MICRO_PER_CELL == 9477,
            "wrong microbox count")


def verify_declared_digests(payload: dict, enforce_frozen_binding: bool) -> None:
    digests = payload["digests"]
    exact_keyset(digests, {"dilation", "packets", "semantic"}, "digests")
    if enforce_frozen_binding:
        require(digests["dilation"] == EXPECTED_DILATION_DIGEST,
                "declared dilation digest changed")
        require(digests["packets"] == EXPECTED_PACKETS_DIGEST,
                "declared packet digest changed")
        require(digests["semantic"] == EXPECTED_SEMANTIC_DIGEST,
                "declared semantic digest changed")
    require(semantic_sha256(payload["dilation"]) == digests["dilation"],
            "dilation digest mismatch")
    require(semantic_sha256(payload["packets"]) == digests["packets"],
            "packet digest mismatch")
    semantic = dict(payload)
    semantic.pop("digests")
    require(semantic_sha256(semantic) == digests["semantic"],
            "global semantic digest mismatch")


def scalar_scaled_correction(carry: int, center_digit: int,
                             center_residual: F) -> F:
    """36 times the correction after writing F=2||x||^2+h/36."""
    y = F(center_digit, Q) + center_residual / Q
    return -36 * (4 * carry * y + carry * carry)


def verify_dilations(payload: dict) -> tuple[set[int], int]:
    records = payload["dilation"]
    require(isinstance(records, list) and len(records) == 433,
            "expected 433 dilation records")
    used: set[int] = set()
    total_wraps = 0
    for index, record in enumerate(records):
        require(isinstance(record, list) and len(record) == 4,
                f"dilation {index}: expected four fields")
        source, target, active_mask, wrap_mask = record
        require(all(is_plain_int(v) for v in record),
                f"dilation {index}: noninteger field")
        a_cell, a_micro, _ = decode_microbox(source)
        b_cell, b_micro, _ = decode_microbox(target)
        require(source != target, f"dilation {index}: loop")
        require(source not in used and target not in used,
                f"dilation {index}: endpoint reused")
        used.update((source, target))

        a, b = CELLS[a_cell], CELLS[b_cell]
        active = tuple(j for j in range(4) if a[j] != b[j])
        wraps = tuple(j for j in active if a[j] == 0 and b[j] == Q - 1)
        require(active and wraps, f"dilation {index}: no active wrap")
        require(all(a[j] == b[j] or b[j] == (a[j] - 1) % Q
                    for j in range(4)),
                f"dilation {index}: not componentwise predecessor geometry")
        actual_active_mask = sum(1 << j for j in active)
        actual_wrap_mask = sum(1 << j for j in wraps)
        require(active_mask == actual_active_mask,
                f"dilation {index}: active mask mismatch")
        require(wrap_mask == actual_wrap_mask,
                f"dilation {index}: wrap mask mismatch")
        require(wrap_mask & ~active_mask == 0,
                f"dilation {index}: wrap outside active mask")

        for j in range(4):
            if j in active:
                require(a_micro[j] == 0 and b_micro[j] == R - 1,
                        f"dilation {index}: active microinterval mismatch")
            else:
                require(a_micro[j] == b_micro[j],
                        f"dilation {index}: inactive microinterval mismatch")

        row_one_carries = []
        row_two_carries = []
        for j in range(4):
            if j not in active:
                row_one_carries.append(0)
                row_two_carries.append(0)
                continue
            # R1 residual defect is -1; R2 residual defect is +1.
            defect_one = a[j] + b[j] - 2 * b[j] - 1
            defect_two = a[j] + b[j] - 2 * a[j] + 1
            require(defect_one % Q == defect_two % Q == 0,
                    f"dilation {index}: nonintegral carry")
            row_one_carries.append(defect_one // Q)
            row_two_carries.append(defect_two // Q)
        require(tuple(row_one_carries) == tuple(-1 if j in wraps else 0
                                                for j in range(4)),
                f"dilation {index}: R1 carry mismatch")
        require(tuple(row_two_carries) == tuple(1 if j in wraps else 0
                                                for j in range(4)),
                f"dilation {index}: R2 carry mismatch")

        # Replay the exact affine raw-canonical correction at two rational t.
        for t in (F(1, 12), F(1, 100)):
            rhs_one = sum((scalar_scaled_correction(-1, Q - 1, 1 - t)
                           for _ in wraps), F(0))
            rhs_two = sum((scalar_scaled_correction(1, 0, t)
                           for _ in wraps), F(0))
            k = len(wraps)
            require(rhs_one == k * (108 - 24 * t),
                    f"dilation {index}: R1 correction mismatch")
            require(rhs_two == k * (-36 - 24 * t),
                    f"dilation {index}: R2 correction mismatch")
            require(rhs_one + rhs_two == k * (72 - 48 * t) > 0,
                    f"dilation {index}: recurrence gap mismatch")
        total_wraps += len(wraps)

    # Strict-interior telescope stays in low/high thirds at every scale.
    T = F(1, 2 * R)
    require(0 < T < F(1, R), "bad telescope anchor")
    for steps in (1, 2, 20):
        levels = [T / 3**j for j in range(1, steps + 1)]
        require(all(0 < t < 3*t <= T < F(1, R) for t in levels),
                "source dilation points leave low microbox")
        require(all(F(R - 1, R) < 1 - 3*t < 1 - t < 1 for t in levels),
                "target dilation points leave high microbox")
        direct = sum((72 - 48*t for t in levels), F(0))
        closed = 72*steps - 24*T*(1 - F(1, 3**steps))
        require(direct == closed > 0, "finite telescope identity failed")
    return used, total_wraps


def verify_packets(payload: dict, forbidden: set[int]) -> tuple[set[int], int, int]:
    packets = payload["packets"]
    require(isinstance(packets, list) and len(packets) == 114,
            "expected 114 packets")
    globally_used: set[int] = set()
    total_rows = 0
    total_weighted_rhs = 0
    for packet_id, packet in enumerate(packets):
        exact_keyset(packet, {"support", "rows", "weighted_rhs", "digest"},
                     f"packet {packet_id}")
        body = dict(packet)
        declared_digest = body.pop("digest")
        require(isinstance(declared_digest, str) and len(declared_digest) == 64,
                f"packet {packet_id}: malformed digest")
        require(semantic_sha256(body) == declared_digest,
                f"packet {packet_id}: digest mismatch")

        support = packet["support"]
        rows = packet["rows"]
        require(isinstance(support, list) and support,
                f"packet {packet_id}: empty/malformed support")
        require(all(is_plain_int(v) for v in support),
                f"packet {packet_id}: noninteger support id")
        require(support == sorted(set(support)),
                f"packet {packet_id}: support is not strictly sorted")
        for vertex in support:
            decode_microbox(vertex)
        support_set = set(support)
        require(support_set.isdisjoint(forbidden),
                f"packet {packet_id}: overlaps dilation support")
        require(support_set.isdisjoint(globally_used),
                f"packet {packet_id}: overlaps another packet")
        globally_used.update(support_set)

        require(isinstance(rows, list) and len(rows) == len(support),
                f"packet {packet_id}: one row per support vertex required")
        incidence = {vertex: 0 for vertex in support}
        semantic_support: set[int] = set()
        weighted_rhs = 0
        centres = []
        for row_id, row in enumerate(rows):
            require(isinstance(row, list) and len(row) == 9,
                    f"packet {packet_id}, row {row_id}: expected nine fields")
            require(all(is_plain_int(v) for v in row),
                    f"packet {packet_id}, row {row_id}: noninteger field")
            x, y, z, weight, k0, k1, k2, k3, raw_cost = row
            carries = (k0, k1, k2, k3)
            require(weight > 0,
                    f"packet {packet_id}, row {row_id}: nonpositive weight")
            require(x in support_set and y in support_set and z in support_set,
                    f"packet {packet_id}, row {row_id}: vertex outside support")
            require(y == support[row_id],
                    f"packet {packet_id}, row {row_id}: centre/id order mismatch")
            _, _, cx = decode_microbox(x)
            _, _, cy = decode_microbox(y)
            _, _, cz = decode_microbox(z)
            defect = tuple(cx[j] + cz[j] - 2*cy[j] for j in range(4))
            require(all(carries[j] in (-1, 0, 1) for j in range(4)),
                    f"packet {packet_id}, row {row_id}: carry outside range")
            require(defect == tuple(QF*carries[j] for j in range(4)),
                    f"packet {packet_id}, row {row_id}: carry/defect mismatch")

            actual_cost = sum((cx[j] - cz[j])**2 for j in range(4))
            require(raw_cost == actual_cost > 0,
                    f"packet {packet_id}, row {row_id}: raw cost mismatch")
            # Explicit common strict-interior offset u=(1/2,...,1/2).
            px = tuple(F(2*cx[j] + 1, 2*QF) for j in range(4))
            py = tuple(F(2*cy[j] + 1, 2*QF) for j in range(4))
            pz = tuple(F(2*cz[j] + 1, 2*QF) for j in range(4))
            require(tuple(px[j] + pz[j] - 2*py[j] for j in range(4))
                    == carries,
                    f"packet {packet_id}, row {row_id}: physical midpoint mismatch")
            require(sum((px[j] - pz[j])**2 for j in range(4))
                    == F(raw_cost, QF**2),
                    f"packet {packet_id}, row {row_id}: physical raw cost mismatch")

            incidence[x] += weight
            incidence[z] += weight
            incidence[y] -= 2*weight
            semantic_support.update((x, y, z))
            weighted_rhs += weight*raw_cost
            centres.append(y)

        require(centres == support,
                f"packet {packet_id}: centres do not enumerate support")
        require(semantic_support == support_set,
                f"packet {packet_id}: declared semantic support mismatch")
        require(not any(incidence.values()),
                f"packet {packet_id}: potential coefficients do not cancel")
        require(weighted_rhs == packet["weighted_rhs"] > 0,
                f"packet {packet_id}: weighted RHS mismatch/nonpositive")
        total_rows += len(rows)
        total_weighted_rhs += weighted_rhs
    return globally_used, total_rows, total_weighted_rhs


def verify_gate(payload: dict, obstruction_count: int) -> None:
    gate = payload["gate"]
    exact_keyset(gate,
                 {"numerator", "denominator", "forced_deletions",
                  "allowed_deletions", "max_retained",
                  "gate_count_numerator", "gate_count_denominator"}, "gate")
    require(all(is_plain_int(value) for value in gate.values()),
            "gate has noninteger field")
    density_gate = F(gate["numerator"], gate["denominator"])
    require(density_gate == F(49, 576), "wrong density gate")
    gate_count = density_gate * QF**4
    require(gate_count == F(gate["gate_count_numerator"],
                            gate["gate_count_denominator"]) == F(35721, 4),
            "wrong gate count")
    total = len(CELLS) * R**4
    forced = obstruction_count
    require(forced == gate["forced_deletions"] == 547,
            "wrong forced deletion count")
    max_retained = total - forced
    require(max_retained == gate["max_retained"] == 8930,
            "wrong max retained count")
    minimum_strict_retained = gate_count.numerator // gate_count.denominator + 1
    allowed_deletions = total - minimum_strict_retained
    require(allowed_deletions == gate["allowed_deletions"] == 546,
            "wrong strict-gate deletion budget")
    require(max_retained < gate_count < max_retained + 1,
            "packing does not cross the density gate")


def verify_payload(payload: dict, enforce_frozen_binding: bool = True) -> dict[str, int]:
    require(isinstance(payload, dict), "certificate root is not an object")
    verify_header(payload)
    verify_declared_digests(payload, enforce_frozen_binding)
    dilation_used, total_wraps = verify_dilations(payload)
    packet_used, total_rows, total_rhs = verify_packets(payload, dilation_used)
    require(dilation_used.isdisjoint(packet_used), "obstruction supports overlap")
    obstruction_count = len(payload["dilation"]) + len(payload["packets"])
    verify_gate(payload, obstruction_count)
    return {"dilations": len(payload["dilation"]),
            "dilation_vertices": len(dilation_used),
            "dilation_wraps": total_wraps,
            "packets": len(payload["packets"]),
            "packet_vertices": len(packet_used),
            "packet_rows": total_rows,
            "weighted_rhs": total_rhs,
            "obstructions": obstruction_count}


def refresh_digests(payload: dict) -> None:
    """Rebind an intentionally mutated copy so semantic checks are exercised."""
    for packet in payload["packets"]:
        body = dict(packet)
        body.pop("digest", None)
        packet["digest"] = semantic_sha256(body)
    payload["digests"]["dilation"] = semantic_sha256(payload["dilation"])
    payload["digests"]["packets"] = semantic_sha256(payload["packets"])
    semantic = dict(payload)
    semantic.pop("digests")
    payload["digests"]["semantic"] = semantic_sha256(semantic)


def expect_failure(payload: dict, label: str) -> None:
    try:
        # Mutations are internally rebound first, so rejection must come from
        # semantic replay rather than only from the frozen reference hashes.
        verify_payload(payload, enforce_frozen_binding=False)
    except VerificationError:
        return
    fail(f"planted failure was accepted: {label}")


def planted_failures(original: dict) -> int:
    tests = []

    bad = copy.deepcopy(original)
    bad["packets"][0]["rows"][0][4] += 1
    refresh_digests(bad)
    tests.append((bad, "carry corruption"))

    bad = copy.deepcopy(original)
    bad["packets"][0]["rows"][0][8] += 1
    refresh_digests(bad)
    tests.append((bad, "raw-cost corruption"))

    bad = copy.deepcopy(original)
    bad["packets"][0]["rows"][0][3] += 1
    refresh_digests(bad)
    tests.append((bad, "coefficient-cancellation corruption"))

    bad = copy.deepcopy(original)
    bad["dilation"][1] = list(bad["dilation"][0])
    refresh_digests(bad)
    tests.append((bad, "reused obstruction support"))

    bad = copy.deepcopy(original)
    bad["digests"]["semantic"] = "0" * 64
    tests.append((bad, "digest corruption"))

    for payload, label in tests:
        expect_failure(payload, label)
    return len(tests)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", nargs="?",
                        default=str(Path(__file__).with_name(
                            "frozen_semantic_certificate.json")))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    path = Path(args.certificate).resolve()
    before_bytes = path.read_bytes()
    actual_file_hash = hashlib.sha256(before_bytes).hexdigest()
    require(actual_file_hash == EXPECTED_FILE_SHA256,
            f"frozen file hash {actual_file_hash} != {EXPECTED_FILE_SHA256}")
    payload = json.loads(before_bytes)
    snapshot = copy.deepcopy(payload)
    stats = verify_payload(payload)
    require(payload == snapshot, "primary verification mutated parsed payload")
    require(path.read_bytes() == before_bytes, "verification mutated certificate bytes")
    failure_count = planted_failures(payload) if args.self_test else 0
    require(payload == snapshot, "planted tests mutated original payload")
    require(path.read_bytes() == before_bytes, "planted tests mutated certificate bytes")

    print(f"CERTIFICATE_BINDING_OK bytes={len(before_bytes)} sha256={actual_file_hash}")
    print("ALPHABET_OK coarse_q=6 cells=117 residual_subdivision=3 "
          "fine_q=18 microboxes=9477")
    print(f"DILATION_OK records={stats['dilations']} "
          f"vertices={stats['dilation_vertices']} wraps={stats['dilation_wraps']}")
    print(f"PACKETS_OK packets={stats['packets']} rows={stats['packet_rows']} "
          f"vertices={stats['packet_vertices']} weighted_rhs={stats['weighted_rhs']}")
    print(f"DISJOINT_PACKING_OK obstructions={stats['obstructions']} "
          "forced_deletions=547")
    print("GATE_OK total=9477 allowed_deletions=546 max_retained=8930 "
          "gate_count=35721/4")
    print("NONMUTATION_OK parsed_payload_and_frozen_bytes_unchanged")
    if args.self_test:
        print(f"PLANTED_FAILURES_OK count={failure_count}")
    print("PASS_Q18_EXPLICIT_MICROBOX_WALL")


if __name__ == "__main__":
    main()

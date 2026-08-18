#!/usr/bin/env python3
"""Primary semantic replay of the frozen q=6/M7 deletion-fence matching."""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WITNESS = HERE / "matching.txt"
MANIFEST = HERE / "constants.json"
Q, BASE = 6, 36
CELLS = {38, 41, 42, 44, 49, 50, 52, 56}
POW36 = [BASE**i for i in range(7)]
POW9 = [9**i for i in range(7)]

def support(point: int, bit: int) -> bool:
    x, y = divmod(point, Q)
    if bit == 0:
        return (x == 3 and 2 <= y <= 4) or (x == 4 and 1 <= y <= 3) or (x == 5 and y <= 2)
    return (x == 2 and 2 <= y <= 4) or (x == 1 and 1 <= y <= 3) or (x == 0 and y <= 2)

def orient(point: int) -> int:
    if support(point, 0): return 0
    if support(point, 1): return 1
    raise AssertionError("local point outside both supports")

def parity(point: int) -> int:
    return sum(divmod(point, Q)) & 1

def add(point: int, digit: int, times: int = 1) -> int:
    x, y = divmod(point, Q)
    dx, dy = divmod(digit, 3)
    return ((x + 2 * times * dx) % Q) * Q + ((y + 2 * times * dy) % Q)

def digits(code: int):
    return [(code // POW36[i]) % BASE for i in range(6)]

def cell(code: int) -> tuple[int, int]:
    pts = digits(code)
    return sum(orient(p) << i for i, p in enumerate(pts)), sum(parity(p) for p in pts)

def raw_cost(a: int, b: int) -> int:
    return sum((x // Q-y // Q)**2 + (x % Q-y % Q)**2 for x, y in zip(digits(a), digits(b)))

def row_carry(left: int, center: int, right: int):
    result = []
    for a, b, c in zip(digits(left), digits(center), digits(right)):
        u = 2*(b//Q)-a//Q-c//Q; v = 2*(b%Q)-a%Q-c%Q
        assert u % Q == 0 and v % Q == 0
        result.append((u//Q, v//Q))
    return tuple(result)

def fnv64(h: int, value: int) -> int:
    for i in range(8):
        h ^= (value >> (8*i)) & 255
        h = (h * 1099511628211) & ((1 << 64) - 1)
    return h

def reject(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)

def parse(lines: list[str]):
    assert lines and lines[0].startswith("independent_allstep_matching_v1 order=step_then_sorted_orbit_key fnv64=")
    declared = int(lines[0].split("fnv64=")[1], 16)
    return declared, [tuple(map(int, line.split())) for line in lines[1:]]

def replay_records(declared: int, records, expected_matching: int = 102_636,
                   rows_per_orbit: int = 3, require_three: bool = True,
                   force_nonpositive_cost: bool = False):
    assert len(records) == expected_matching, "matching count"
    assert not require_three or rows_per_orbit == 3, "missing cyclic row"
    used: set[int] = set(); h = 1469598103934665603; rhs_total = 0; coeff = Counter()
    previous = None
    for step, x, y, z in records:
        assert step and step < POW9[6]
        key = tuple(sorted((x, y, z)))
        ordering = (step, key)
        assert previous is None or previous < ordering, "witness order changed or duplicate orbit"
        previous = ordering
        assert not (set((x, y, z)) & used), "matching vertices overlap"
        assert len({x, y, z}) == 3
        for vertex in (x, y, z):
            assert cell(vertex)[0] in CELLS and cell(vertex)[1] == 3
        for i, p in enumerate(digits(x)):
            d = (step // POW9[i]) % 9
            assert add(p, d) == digits(y)[i] and add(p, d, 2) == digits(z)[i]
        # Every cyclic midpoint row is modular, has positive canonical cost,
        # and the three row coefficients cancel at physical vertices.
        rows = ((x, y, z), (y, z, x), (z, x, y))[:rows_per_orbit]
        local_coeff = Counter()
        for left, center, right in rows:
            assert row_carry(left, center, right)
            cost = 0 if force_nonpositive_cost else raw_cost(left, right)
            assert cost > 0, "nonpositive cyclic raw cost"; rhs_total += cost
            coeff[left] += 1; coeff[center] -= 2; coeff[right] += 1
            local_coeff[left] += 1; local_coeff[center] -= 2; local_coeff[right] += 1
        assert not {v for v in local_coeff.values() if v}, "cyclic coefficients do not cancel"
        used.update((x, y, z)); h = fnv64(fnv64(fnv64(fnv64(h, step), key[0]), key[1]), key[2])
    assert not {v for v in coeff.values() if v}, "cyclic coefficients do not cancel"
    assert len(used) == 3*expected_matching and h == declared == 0xE274395806684DE3
    deletion, retained, gap = validate_mass()
    return {"matching": len(records), "unique_vertices": len(used), "fnv64": f"{h:016X}",
           "cyclic_total_raw_rhs": rhs_total, "deletion_mass": str(deletion),
           "retained_mass": str(retained), "gate_gap": str(gap)}

def validate_mass(total: int = 1_428_840, matching: int = 102_636,
                  gate: Fraction = Fraction(7,24)**6, slack: int = 5_679_639):
    assert total == 1_428_840 and matching == 102_636 and gate == Fraction(7,24)**6
    deletion = Fraction(matching, Q**12)
    retained = Fraction(total-matching, Q**12)
    gap = gate-retained
    assert gap == Fraction(matching*64-slack, 64*Q**12) and gap > 0
    return deletion, retained, gap

def verify_manifest() -> None:
    """Bind executable semantics to the frozen file hashes and key counts."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["matching"]["count"] == 102_636
    assert manifest["support"]["vertices"] == 1_428_840
    assert manifest["orbit_census"]["distinct_order3_orbits"] == 1_342_512
    for name, expected in manifest["sha256"].items():
        got = hashlib.sha256((HERE / name).read_bytes()).hexdigest().upper()
        assert got == expected, f"SHA-256 mismatch: {name}"

def expect_reject(label: str, declared: int, records, **kwargs) -> str:
    try:
        replay_records(declared, records, **kwargs)
    except AssertionError:
        return "rejected"
    raise AssertionError("planted failure accepted: " + label)

def self_test(declared: int, records) -> dict[str, str]:
    """Plant each certificate-relevant corruption; every case must reject."""
    tests = {}
    duplicate = list(records); duplicate[1] = records[0]
    tests["duplicate_physical_vertex"] = expect_reject("duplicate_physical_vertex", declared, duplicate)
    off_support = list(records); s,x,y,z = off_support[0]; off_support[0] = (s, POW36[6]-1, y, z)
    tests["off_support_or_cell_vertex"] = expect_reject("off_support_or_cell_vertex", declared, off_support)
    wrong_step = list(records); s,x,y,z = wrong_step[0]; wrong_step[0] = ((s+1) % (POW9[6]-1) or 1, x,y,z)
    tests["wrong_step_or_midpoint"] = expect_reject("wrong_step_or_midpoint", declared, wrong_step)
    zero_step = list(records); _,x,y,z = zero_step[0]; zero_step[0] = (0,x,y,z)
    tests["zero_step_or_nonpositive_cost"] = expect_reject("zero_step_or_nonpositive_cost", declared, zero_step)
    tests["forced_nonpositive_cost"] = expect_reject("forced_nonpositive_cost", declared, records, force_nonpositive_cost=True)
    tests["missing_cyclic_row"] = expect_reject("missing_cyclic_row", declared, records, rows_per_orbit=2)
    tests["failed_coefficient_cancellation"] = expect_reject("failed_coefficient_cancellation", declared, records, rows_per_orbit=1, require_three=False)
    tests["corrupted_matching_count"] = expect_reject("corrupted_matching_count", declared, records, expected_matching=102_635)
    # This mutation attacks the exact gate identity rather than witness rows.
    try:
        validate_mass(slack=5_679_638)
    except AssertionError:
        tests["corrupted_mass_or_gate"] = "rejected"
    else:
        raise AssertionError("planted failure accepted: corrupted_mass_or_gate")
    return tests

def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--self-test", action="store_true"); args = ap.parse_args()
    lines = WITNESS.read_text(encoding="ascii").splitlines()
    declared, records = parse(lines)
    verify_manifest()
    result = replay_records(declared, records)
    if args.self_test: result["planted_failures"] = self_test(declared, records)
    print("PASS_Q6_M7_MATCHING_DELETION_FENCE")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__": main()

#!/usr/bin/env python3
"""Fresh, separately written audit of matching.txt.

This checker is standalone: it reconstructs the q=6 local supports, base-36
vertex encoding, base-9 step encoding, selected-cell predicate, cyclic rows,
and the common-offset deletion arithmetic without importing any neighboring
artifact or executing its generator.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
WITNESS = ROOT / "matching.txt"
Q = 6
CELLS = {38, 41, 42, 44, 49, 50, 52, 56}
BASE = {(3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3), (5, 0), (5, 1), (5, 2)}
REF = {(5 - x, y) for x, y in BASE}
UNION = BASE | REF
N = 102_636
EXPECTED_DIGEST = 0xE274395806684DE3


def point(code: int) -> tuple[int, int]:
    return divmod(code, Q)


def digits(code: int) -> list[int]:
    out = []
    for _ in range(6):
        out.append(code % 36)
        code //= 36
    return out


def step_digits(code: int) -> list[int]:
    out = []
    for _ in range(6):
        out.append(code % 9)
        code //= 9
    return out


def support_bit(p: int, bit: int) -> bool:
    x, y = point(p)
    if bit == 0:
        return ((x == 3 and 2 <= y <= 4) or
                (x == 4 and 1 <= y <= 3) or
                (x == 5 and y <= 2))
    return ((x == 2 and 2 <= y <= 4) or
            (x == 1 and 1 <= y <= 3) or
            (x == 0 and y <= 2))


def orientation(p: int) -> int:
    if support_bit(p, 0):
        return 0
    if support_bit(p, 1):
        return 1
    raise AssertionError(f"point outside local union: {p}")


def parity(p: int) -> int:
    x, y = point(p)
    return (x + y) & 1


def cell(code: int) -> tuple[int, int]:
    ds = digits(code)
    return (sum(orientation(p) << i for i, p in enumerate(ds)),
            sum(parity(p) for p in ds))


def translated_point(p: int, d: int, times: int = 1) -> int:
    x, y = point(p)
    dx, dy = divmod(d, 3)
    return ((x + 2 * times * dx) % Q) * Q + ((y + 2 * times * dy) % Q)


def translate(code: int, step: int, times: int = 1) -> int:
    ds = digits(code)
    sd = step_digits(step)
    return sum(translated_point(p, d, times) * (36 ** i)
               for i, (p, d) in enumerate(zip(ds, sd)))


def raw_cost(left: int, right: int) -> int:
    total = 0
    for a, b in zip(digits(left), digits(right)):
        ax, ay = point(a)
        bx, by = point(b)
        total += (ax - bx) ** 2 + (ay - by) ** 2
    return total


def row_carry(left: int, center: int, right: int) -> tuple[tuple[int, int], ...]:
    out = []
    for a, b, c in zip(digits(left), digits(center), digits(right)):
        ax, ay = point(a)
        bx, by = point(b)
        cx, cy = point(c)
        ux, uy = 2 * bx - ax - cx, 2 * by - ay - cy
        assert ux % Q == 0 and uy % Q == 0
        out.append((ux // Q, uy // Q))
    return tuple(out)


def fnv64_words(values: list[int]) -> int:
    # This is the exact declared digest convention: FNV-1a over each word's
    # eight little-endian bytes.  The historical offset value is retained as
    # part of the witness's declared digest convention.
    h = 1_469_598_103_934_665_603
    for value in values:
        for i in range(8):
            h ^= (value >> (8 * i)) & 0xFF
            h = (h * 1_099_511_628_211) & ((1 << 64) - 1)
    return h


def count_cell(w: int, residue: int) -> int:
    choices = []
    for i in range(6):
        bit = (w >> i) & 1
        choices.append([p for p in range(36) if support_bit(p, bit)])
    total = 0
    def rec(i: int, r: int) -> None:
        nonlocal total
        if i == 6:
            if r == residue:
                total += 1
            return
        for p in choices[i]:
            rec(i + 1, r + parity(p))
    rec(0, 0)
    return total


def audit() -> dict[str, object]:
    lines = WITNESS.read_text(encoding="ascii").splitlines()
    assert lines and lines[0].startswith(
        "independent_allstep_matching_v1 order=step_then_sorted_orbit_key fnv64=")
    declared = int(lines[0].split("fnv64=", 1)[1], 16)
    records = [tuple(map(int, line.split())) for line in lines[1:]]
    assert declared == EXPECTED_DIGEST
    assert len(records) == N
    assert all(len(r) == 4 for r in records)

    counts = {w: count_cell(w, 3) for w in sorted(CELLS)}
    assert counts == {w: 178605 for w in CELLS}
    assert sum(counts.values()) == 1_428_840

    used: set[int] = set()
    digest_words: list[int] = []
    step_counts: Counter[int] = Counter()
    rhs_total = 0
    rhs_min = None
    rhs_max = 0
    previous_key = None
    for step, x, y, z in records:
        assert 0 < step < 9 ** 6
        sd = step_digits(step)
        assert any(sd), "zero step"
        key = tuple(sorted((x, y, z)))
        ordering = (step, key)
        assert previous_key is None or previous_key < ordering
        previous_key = ordering
        assert len({x, y, z}) == 3
        assert not used.intersection((x, y, z))
        assert all(cell(v)[0] in CELLS and cell(v)[1] == 3 for v in (x, y, z))
        assert y == translate(x, step, 1)
        assert z == translate(x, step, 2)
        assert x == translate(z, step, 1)
        # The three cyclic midpoint rows have positive raw endpoint costs;
        # each physical vertex has aggregate coefficient 1-2+1=0.
        row_rhs = [raw_cost(x, z), raw_cost(y, x), raw_cost(z, y)]
        assert all(v > 0 for v in row_rhs)
        assert all(row_carry(*row) for row in ((x, y, z), (y, z, x), (z, x, y)))
        rhs_total += sum(row_rhs)
        rhs_min = min(row_rhs) if rhs_min is None else min(rhs_min, *row_rhs)
        rhs_max = max(rhs_max, *row_rhs)
        used.update((x, y, z))
        step_counts[step] += 1
        digest_words.extend((step, *key))

    assert len(used) == 3 * N == 307_908
    got_digest = fnv64_words(digest_words)
    assert got_digest == declared

    total_boxes = 1_428_840
    gate = Fraction(7, 24) ** 6
    slack_boxes = Fraction(5_679_639, 64)
    matching_boxes = Fraction(N, 1)
    excess_boxes = matching_boxes - slack_boxes
    assert excess_boxes == Fraction(889_065, 64)
    exact_margin = excess_boxes / (Q ** 12)
    assert exact_margin == Fraction(889_065, 64 * Q ** 12)
    retained = Fraction(total_boxes - N, Q ** 12)
    assert retained < gate
    # Common delta in (0,1/6)^12 preserves every row's carry and endpoint
    # difference.  Thus a triple of retained boxes would violate its cyclic
    # positive wall for every such delta.  Since matching triples are box-
    # disjoint, at least N boxes must be deleted.
    deletion_lower_bound = Fraction(N, Q ** 12)
    assert deletion_lower_bound > slack_boxes / (Q ** 12)

    report = {
        "verdict": "PASS_FRESH_102636_AUDIT",
        "records": N,
        "unique_boxes": len(used),
        "distinct_steps_in_matching": len(step_counts),
        "cell_counts": counts,
        "support_boxes": total_boxes,
        "cyclic_total_raw_rhs": rhs_total,
        "cyclic_raw_rhs_min": rhs_min,
        "cyclic_raw_rhs_max": rhs_max,
        "digest": f"{got_digest:016X}",
        "deletion_lower_bound": str(deletion_lower_bound),
        "exact_margin_over_gate": str(exact_margin),
        "exact_margin_numerator": 889065,
        "exact_margin_denominator": 64 * Q ** 12,
        "retained_mass": str(retained),
        "gate": str(gate),
        "common_offset_domain": "(0,1/6)^12",
    }
    return report


if __name__ == "__main__":
    report = audit()
    print("PASS_INDEPENDENT_Q6_M7_DELETION_FENCE")
    print(json.dumps(report, sort_keys=True))

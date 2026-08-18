#!/usr/bin/env python3
"""Separately written stdlib audit of the 117-cell Markov Farkas packet.

This program deliberately imports neither the primary replay nor discovery
code.  It independently decodes the alphabet, recalculates the continuous
carry closure, rebuilds the padded rays, and checks the dual cancellation.
"""
from __future__ import annotations

import argparse
import copy
import json
from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path

MODULUS = 6
ANCHORS = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
           (5, 0), (5, 1), (5, 2))
STEPS = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
         (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))


class AuditFailure(ValueError):
    pass


def reject(message: str) -> None:
    raise AuditFailure(message)


ALPHABET = tuple((u, v, (u + du) % MODULUS, (v + dv) % MODULUS)
                 for u, v in ANCHORS for du, dv in STEPS)
if len(ALPHABET) != 117 or len(set(ALPHABET)) != 117:
    raise RuntimeError("independent alphabet decoder failed")


def scalar_closure(first: int, middle: int, last: int) -> Fraction | None:
    """Compute the exact branch supremum by enumerating the carry itself."""
    defect = first + last - 2 * middle
    candidates = []
    for kappa in (-1, 0, 1):
        residue = MODULUS * kappa - defect
        if residue == -1:
            interval = (Fraction(1, 2), Fraction(1))
        elif residue == 0:
            interval = (Fraction(0), Fraction(1))
        elif residue == 1:
            interval = (Fraction(0), Fraction(1, 2))
        else:
            continue
        offset = interval[0] if kappa > 0 else interval[1]
        candidates.append(-2 * MODULUS * kappa *
                          (Fraction(first + last, 2) + middle +
                           2 * offset + Fraction(residue, 2)))
    return max(candidates) if candidates else None


def score(triple: tuple[int, int, int]) -> int | None:
    x, y, z = triple
    if not all(0 <= n < len(ALPHABET) for n in triple):
        return None
    pieces = [scalar_closure(ALPHABET[x][i], ALPHABET[y][i], ALPHABET[z][i])
              for i in range(4)]
    if any(piece is None for piece in pieces):
        return None
    total = sum(pieces, Fraction(0))
    if total.denominator != 1:
        reject("nonintegral independently recomputed q^2 RHS")
    return int(total)


def read_local(value: object, name: str) -> tuple[int, int, int, int]:
    if not isinstance(value, list) or len(value) != 4 or any(type(x) is not int for x in value):
        reject(f"{name}: malformed local row")
    x, y, z, advertised = value
    actual = score((x, y, z))
    if actual is None or advertised != actual:
        reject(f"{name}: raw-canonical carry score mismatch")
    return x, y, z, advertised


def extract(doc: dict) -> tuple[tuple[int, tuple[int, int, int, int], tuple[int, int, int, int]], ...]:
    if (doc.get("schema") != "erdos142-q6-synchronized-transition-wall-v1" or
            doc.get("q") != 6 or doc.get("alphabet_cells") != 117 or
            doc.get("scaled_variables") != "G=36*g and J=36*H"):
        reject("wrong certificate identity or scaling")
    if doc.get("transition_graph") != "all ordered distinct pairs of alphabet cells":
        reject("not the full loopless transition graph")
    raw = doc.get("rows")
    if not isinstance(raw, list) or len(raw) != 5:
        reject("unexpected ray length")
    result = []
    for number, item in enumerate(raw):
        if not isinstance(item, dict) or type(item.get("weight")) is not int or item["weight"] <= 0:
            reject(f"cut {number}: invalid positive dual weight")
        result.append((item["weight"], read_local(item.get("left"), f"cut {number} left"),
                       read_local(item.get("right"), f"cut {number} right")))
    return tuple(result)


def columns(a: tuple[int, int, int, int], b: tuple[int, int, int, int], length: int) -> tuple[tuple[int, int, int, int], ...]:
    if length < 2:
        reject("path length below the two-block model")
    suffix = tuple((v, v, v, 0) for v in
                   (0 if n % 2 == 0 else 1 for n in range(length - 2)))
    for row in suffix:
        if score(row[:3]) != 0:
            reject("claimed common tail is not carry-zero")
    return (a, b) + suffix


def audit_length(ray: tuple[tuple[int, tuple[int, int, int, int], tuple[int, int, int, int]], ...],
                 length: int) -> int:
    endpoint: defaultdict[int, Fraction] = defaultdict(Fraction)
    transition: defaultdict[tuple[int, int], int] = defaultdict(int)
    rhs = 0
    for cut, (weight, first, second) in enumerate(ray):
        table = columns(first, second, length)
        rhs += weight * sum(row[3] for row in table)
        for role, sign in ((0, 1), (1, -2), (2, 1)):
            word = [row[role] for row in table]
            endpoint[word[0]] += Fraction(weight * sign, 2)
            endpoint[word[-1]] += Fraction(weight * sign, 2)
            for start, finish in zip(word, word[1:]):
                if start == finish:
                    reject(f"cut {cut}: locally legal rows produce forbidden loopless transition {(start, finish)}")
                transition[start, finish] += weight * sign
    if any(endpoint.values()) or any(transition.values()):
        reject(f"length {length}: G,J coefficient cancellation failed")
    if rhs <= 0:
        reject(f"length {length}: nonpositive Farkas RHS")
    return rhs


def audit(doc: dict, ceiling: int) -> None:
    ray = extract(doc)
    if ceiling < 2:
        reject("max length must be at least two")
    first_rhs = audit_length(ray, 2)
    if first_rhs != 1032 or doc.get("expected_weighted_rhs") != first_rhs:
        reject("incorrect two-block contradiction total")
    if doc.get("expected_active_cells") != [41, 67, 80, 83]:
        reject("active cell metadata mismatch")
    if doc.get("expected_active_transitions") != [[41, 67], [41, 83], [67, 80], [80, 41], [83, 80]]:
        reject("active transition metadata mismatch")
    for length in range(3, ceiling + 1):
        if audit_length(ray, length) != first_rhs:
            reject("padding altered the Farkas cost")
    perron_base = Fraction(116, 6 ** 4)
    if perron_base <= Fraction(7, 24) ** 2:
        reject("loopless Perron density gate failed")
    print("INDEPENDENT_SEMANTICS_OK q=6 cells=117 scaling=G=36g,J=36H")
    print(f"INDEPENDENT_FARKAS_OK rhs={first_rhs} paths=2..{ceiling}")
    print(f"INDEPENDENT_PERRON_OK rho=116 base={perron_base}")


def planted(doc: dict) -> None:
    before = json.dumps(doc, sort_keys=True, separators=(",", ":"))
    for label, edit, marker in (
        ("rhs", lambda x: x["rows"][0]["left"].__setitem__(3, 169), "score mismatch"),
        # [41,41,80,72] is itself a legal local carry row.  It fails only
        # because its first synchronized transition is the self-loop (41,41).
        ("loop", lambda x: x["rows"][0].__setitem__("right", [41, 41, 80, 72]), "loopless transition"),
        ("weight", lambda x: x["rows"][0].__setitem__("weight", 2), "cancellation"),
    ):
        damaged = copy.deepcopy(doc)
        edit(damaged)
        try:
            audit(damaged, 3)
        except AuditFailure as error:
            if marker not in str(error):
                raise
        else:
            reject(f"planted {label} corruption was accepted")
    after = json.dumps(doc, sort_keys=True, separators=(",", ":"))
    if before != after:
        reject("self-test mutated the input certificate")
    print("INDEPENDENT_PLANTED_FAILURES_AND_NONMUTATION_OK")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--max-length", type=int, default=9)
    args = parser.parse_args()
    try:
        document = json.loads(args.certificate.read_text(encoding="utf-8"))
        if args.self_test:
            planted(document)
        audit(document, args.max_length)
    except (OSError, json.JSONDecodeError, AuditFailure) as error:
        print(f"INDEPENDENT_VERIFY_FAIL: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

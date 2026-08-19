#!/usr/bin/env python3
"""Regenerate and check the complete 24-case four-cap orbit split."""

from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent
POINTS = tuple(product(range(9), repeat=2))
INDEX = {point: i for i, point in enumerate(POINTS)}
SATURATED = {(1, 0), (2, 0), (0, 1), (0, 2)}
FIRST = {"saturated": (1, 0), "center": (0, 0), "corner": (1, 1)}
STEM = {"saturated": "sat", "center": "center", "corner": "corner"}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def qvar(vertex, boundary):
    return vertex * 32 + boundary + 1


def full_stabilizer():
    maps = set()
    quotient = set()
    for a, b, c, d in product(range(9), repeat=4):
        if (a * d - b * c) % 3 == 0:
            continue
        image = {((a * x + b * y) % 3, (c * x + d * y) % 3)
                 for x, y in SATURATED}
        if image != SATURATED:
            continue
        quotient.add((a % 3, b % 3, c % 3, d % 3))
        for ux, uy in product(range(3), repeat=2):
            maps.add(tuple(INDEX[((a * x + b * y + 3 * ux) % 9,
                                  (c * x + d * y + 3 * uy) % 9)]
                           for x, y in POINTS))
    need(len(quotient) == 8 and len(maps) == 5832,
         "full stabilizer census")
    return tuple(sorted(maps))


def point_orbits(group):
    unseen = set(range(81))
    result = []
    while unseen:
        seed = min(unseen)
        orbit = frozenset(mapping[seed] for mapping in group)
        need(all({mapping[v] for v in orbit} == set(orbit)
                 for mapping in group), "orbit invariance")
        result.append(orbit)
        unseen -= orbit
    need(sum(map(len, result)) == 81 and
         len(set().union(*result)) == 81, "orbit partition")
    return tuple(sorted(result, key=lambda orbit: (len(orbit), min(orbit))))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path,
                        default=HERE / "case2_unique_core6.cnf")
    parser.add_argument("--check-dir", type=Path)
    parser.add_argument("--write-dir", type=Path)
    args = parser.parse_args()

    raw = args.base.read_bytes()
    need(sha256(raw).hexdigest() ==
         "3d490be403585b03ddc30b7aff7445b4c4e9d3b7550e2e97077964b627a88108",
         "base hash")
    header, body = raw.split(b"\n", 1)
    need(header == b"p cnf 11203 131681" and body.endswith(b"\n"),
         "base framing")

    full = full_stabilizer()
    first_orbits = point_orbits(full)
    need(sorted(map(len, first_orbits)) == [9, 36, 36],
         "first orbit sizes")
    need(len({next(i for i, orbit in enumerate(first_orbits)
                   if INDEX[point] in orbit)
              for point in FIRST.values()}) == 3,
         "first representatives")

    expected = {"saturated": (162, 10, [1, 1, 2, 2, 2, 9, 9, 18, 18, 18]),
                "center": (648, 4, [4, 4, 36, 36]),
                "corner": (162, 10, [1, 1, 2, 2, 2, 9, 9, 18, 18, 18])}
    total = 0
    print("PASS_FIRST_ORBITS full_group=5832 sizes=9,36,36 reps="
          "center:0,0 saturated:1,0 corner:1,1")
    for name in ("saturated", "center", "corner"):
        first = INDEX[FIRST[name]]
        stabilizer = tuple(mapping for mapping in full
                           if mapping[first] == first)
        second = tuple(orbit for orbit in point_orbits(stabilizer)
                       if first not in orbit)
        expected_stab, expected_count, expected_sizes = expected[name]
        need(len(stabilizer) == expected_stab and
             len(second) == expected_count and
             list(map(len, second)) == expected_sizes and
             sum(map(len, second)) == 80,
             "%s second orbit cover" % name)
        print("SECOND_ORBITS first=%s stabilizer=%d count=%d sizes=%s cover=80" %
              (name, len(stabilizer), len(second),
               ",".join(map(str, map(len, second)))))
        for case, orbit in enumerate(second):
            representative = min(orbit)
            units = ("%d 0\n%d 0\n%d 0\n%d 0\n" %
                     (-qvar(first, 30), qvar(first, 31),
                      -qvar(representative, 29),
                      qvar(representative, 30))).encode("ascii")
            output = b"p cnf 11203 131685\n" + body + units
            filename = "case2_%s_second_%02d.cnf" % (STEM[name], case)
            if args.check_dir:
                need((args.check_dir / filename).read_bytes() == output,
                     "%s byte mismatch" % filename)
            if args.write_dir:
                args.write_dir.mkdir(parents=True, exist_ok=True)
                (args.write_dir / filename).write_bytes(output)
            x, y = POINTS[representative]
            print("CASE first=%s index=%d rep=%d,%d orbit=%d bytes=%d sha256=%s" %
                  (name, case, x, y, len(orbit), len(output),
                   sha256(output).hexdigest()))
            total += 1
    need(total == 24, "case census")
    print("PASS_FOUR_CAP_ORBIT_CNFS cases=24 vars_each=11203 clauses_each=131685")


if __name__ == "__main__":
    main()

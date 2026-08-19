#!/usr/bin/env python3
"""Regenerate the complete transparent template-1 blocker ledger."""
from collections import deque, Counter
from itertools import combinations, product
from pathlib import Path
import json
import argparse


POINTS = tuple(product(range(9), repeat=2))
INDEX = {point: i for i, point in enumerate(POINTS)}
MID = tuple(tuple(INDEX[((5*(a[0]+b[0])) % 9,
                         (5*(a[1]+b[1])) % 9)] for b in POINTS)
            for a in POINTS)
TEMPLATE_POINTS = (
    (0, 0), (0, 3), (1, 0), (1, 6), (2, 3), (2, 6),
    (3, 3), (4, 0), (4, 3), (5, 0), (5, 3), (6, 0),
)
TEMPLATE = frozenset(INDEX[p] for p in TEMPLATE_POINTS)


def core(vertices):
    alive = set(vertices)
    while alive:
        supported = set()
        for a, b in combinations(sorted(alive), 2):
            middle = MID[a][b]
            if middle in alive:
                supported.add(middle)
        if supported == alive:
            return frozenset(alive)
        alive = supported
    return frozenset()


def poison(extra):
    return bool(core(TEMPLATE | set(extra)))


def small_blockers():
    outside = tuple(v for v in range(81) if v not in TEMPLATE)
    by_size = {size: set() for size in range(1, 5)}
    for size in range(1, 5):
        universe = (outside if size == 1 else
                    tuple(v for v in outside
                          if frozenset((v,)) not in by_size[1]))
        for choice in combinations(universe, size):
            if any(frozenset(part) in by_size[old]
                   for old in range(1, size)
                   for part in combinations(choice, old)):
                continue
            if poison(choice):
                by_size[size].add(frozenset(choice))
    return by_size


def stabilizer():
    maps = []
    for a, b, c, d in product(range(9), repeat=4):
        if (a*d-b*c) % 3 == 0:
            continue
        for tx in range(9):
            for ty in range(9):
                image = frozenset(
                    INDEX[((a*x+b*y+tx) % 9, (c*x+d*y+ty) % 9)]
                    for x, y in TEMPLATE_POINTS)
                if image == TEMPLATE:
                    maps.append((a, b, c, d, tx, ty))
    assert len(maps) == 9
    return tuple(maps)


def transform(vertices, affine):
    a, b, c, d, tx, ty = affine
    return frozenset(
        INDEX[((a*POINTS[v][0]+b*POINTS[v][1]+tx) % 9,
               (c*POINTS[v][0]+d*POINTS[v][1]+ty) % 9)]
        for v in vertices)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true",
                        help="write the canonical ledger instead of checking it")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    by_size = small_blockers()
    raw = json.loads((root / "data" / "template1_blocker_reps.json").read_text())
    reps = tuple(frozenset(INDEX[tuple(point)] for point in record)
                 for record in raw)
    maps = stabilizer()
    learned = {transform(rep, affine) for rep in reps for affine in maps}
    assert len(reps) == 4 and len(learned) == 36
    family = set().union(*(by_size[size] for size in range(1, 5)), learned)
    ordered = tuple(sorted(family,
                           key=lambda item: (len(item), tuple(sorted(item)))))
    assert Counter(map(len, ordered)) == Counter(
        {1: 15, 3: 297, 4: 3798, 5: 9, 6: 27})
    assert all(poison(blocker) for blocker in ordered)
    assert all(not poison(blocker-{v}) for blocker in ordered for v in blocker)
    lines = [" ".join("%d,%d" % POINTS[v] for v in sorted(blocker))
             for blocker in ordered]
    output = root / "data" / "template1_blockers.txt"
    data = ("\n".join(lines)+"\n").encode("ascii")
    if args.write:
        output.write_bytes(data)
        action = "WROTE"
    else:
        assert output.read_bytes() == data, "frozen template1 ledger drift"
        action = "CHECKED"
    print("PASS_TEMPLATE1_LEDGER_REGENERATION")
    print("BLOCKERS", len(ordered), tuple(sorted(Counter(map(len, ordered)).items())))
    print("STABILIZER", len(maps), "LEARNED_IMAGES", len(learned))
    print(action, "data/template1_blockers.txt", len(data))


if __name__ == "__main__":
    main()

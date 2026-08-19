#!/usr/bin/env python3
"""Independently validate both blocker ledgers and their frozen DIMACS files."""
from collections import Counter, deque
from itertools import combinations, product
from pathlib import Path
import argparse


POINTS = tuple(product(range(9), repeat=2))
INDEX = {point: i for i, point in enumerate(POINTS)}
MID = tuple(tuple(INDEX[((5*(a[0]+b[0])) % 9,
                         (5*(a[1]+b[1])) % 9)] for b in POINTS)
            for a in POINTS)
TEMPLATES = (
    ((0,3),(0,6),(1,3),(1,6),(2,0),(2,3),
     (3,0),(4,0),(4,3),(5,0),(5,3),(6,0)),
    ((0,0),(0,3),(1,0),(1,6),(2,3),(2,6),
     (3,3),(4,0),(4,3),(5,0),(5,3),(6,0)),
)
EXPECTED_HISTOGRAMS = (
    Counter({1:15, 3:297, 4:3177, 5:11619}),
    Counter({1:15, 3:297, 4:3798, 5:9, 6:27}),
)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def mask_of(vertices):
    return sum(1 << v for v in vertices)


def midpoint_core(vertices):
    members = tuple(sorted(vertices))
    present = [False] * 81
    for vertex in members:
        present[vertex] = True
    incoming = [0] * 81
    for a, b in combinations(members, 2):
        middle = MID[a][b]
        if present[middle]:
            incoming[middle] += 1
    queue = deque(v for v in members if incoming[v] == 0)
    while queue:
        removed = queue.popleft()
        if not present[removed]:
            continue
        present[removed] = False
        for other in members:
            if present[other]:
                middle = MID[removed][other]
                if present[middle]:
                    incoming[middle] -= 1
                    if incoming[middle] == 0:
                        queue.append(middle)
    return frozenset(v for v in members if present[v])


def parse_ledger(path):
    blockers = []
    for line_number, raw in enumerate(path.read_text("ascii").splitlines(), 1):
        need(raw, "blank blocker line %d" % line_number)
        points = []
        for token in raw.split():
            fields = token.split(",")
            need(len(fields) == 2 and all(field.isdigit() for field in fields),
                 "malformed coordinate line %d" % line_number)
            point = tuple(map(int, fields))
            need(point in INDEX, "coordinate outside Z9 line %d" % line_number)
            points.append(INDEX[point])
        need(1 <= len(points) <= 6 and len(set(points)) == len(points),
             "invalid blocker line %d" % line_number)
        need(points == sorted(points), "unsorted blocker line %d" % line_number)
        blockers.append(frozenset(points))
    canonical = tuple(sorted(set(blockers),
                             key=lambda item: (len(item), tuple(sorted(item)))))
    need(tuple(blockers) == canonical, "ledger is not unique canonical order")
    return canonical


def simplify(items):
    clause = []
    for item in items:
        if item is True:
            return None
        if item is False:
            continue
        clause.append(int(item))
    need(clause, "empty counter clause")
    return tuple(clause)


def negate(item):
    return not item if isinstance(item, bool) else -item


def build_cnf(allowed, blockers):
    where = {point: i+1 for i, point in enumerate(allowed)}
    clauses = []
    next_var = 55
    previous = {0: True}
    for i, variable in enumerate(range(1, 55), 1):
        current = {0: True}
        for threshold in range(1, min(i, 20)+1):
            old_same = previous.get(threshold, False)
            old_lower = previous.get(threshold-1, False)
            new = next_var
            next_var += 1
            for raw in ((negate(old_same), new),
                        (-variable, negate(old_lower), new),
                        (-new, old_same, variable),
                        (-new, old_same, old_lower)):
                clause = simplify(raw)
                if clause is not None:
                    clauses.append(clause)
            current[threshold] = new
        previous = current
    clauses.append((previous[20],))
    need(next_var-1 == 944, "counter variable census")

    fibre_clauses = 0
    for rx, ry in product(range(3), repeat=2):
        fibre = tuple(where[v] for v in allowed
                      if POINTS[v][0] % 3 == rx and POINTS[v][1] % 3 == ry)
        if not fibre:
            continue
        need(len(fibre) == 9, "fibre size in CNF construction")
        for five in combinations(fibre, 5):
            clauses.append(tuple(-v for v in five))
            fibre_clauses += 1
    need(fibre_clauses == 756, "fibre clause census")
    for blocker in blockers:
        clauses.append(tuple(-where[v] for v in sorted(blocker)))
    text = "p cnf 944 %d\n" % len(clauses)
    text += "".join(" ".join(map(str, clause))+" 0\n" for clause in clauses)
    return text.encode("ascii"), tuple(clauses)


def enumerate_minimal(template, maximum):
    outside = tuple(v for v in range(81) if v not in template)
    by_size = {size: set() for size in range(1, maximum+1)}
    result = []
    for size in range(1, maximum+1):
        universe = (outside if size == 1 else
                    tuple(v for v in outside
                          if frozenset((v,)) not in by_size[1]))
        for choice in combinations(universe, size):
            if any(frozenset(part) in by_size[old]
                   for old in range(1, size)
                   for part in combinations(choice, old)):
                continue
            if midpoint_core(template | set(choice)):
                blocker = frozenset(choice)
                by_size[size].add(blocker)
                result.append(blocker)
        print("EXHAUSTIVE_TEMPLATE0 size=%d count=%d" %
              (size, len(by_size[size])), flush=True)
    return tuple(sorted(result,
                        key=lambda item: (len(item), tuple(sorted(item)))))


def validate_case(root, template_index):
    template = frozenset(INDEX[p] for p in TEMPLATES[template_index])
    ledger = parse_ledger(root / "data" /
                          ("template%d_blockers.txt" % template_index))
    need(Counter(map(len, ledger)) == EXPECTED_HISTOGRAMS[template_index],
         "template%d blocker histogram" % template_index)
    need(not midpoint_core(template), "template%d is not peelable" % template_index)
    need(all(midpoint_core(template | blocker) for blocker in ledger),
         "template%d unsound blocker" % template_index)
    need(all(not midpoint_core(template | (blocker-{v}))
             for blocker in ledger for v in blocker),
         "template%d nonminimal blocker" % template_index)

    singleton = {next(iter(blocker)) for blocker in ledger if len(blocker) == 1}
    allowed = tuple(v for v in range(81) if v not in template and v not in singleton)
    need(len(singleton) == 15 and len(allowed) == 54,
         "template%d allowed census" % template_index)
    nonsingleton = tuple(blocker for blocker in ledger if len(blocker) >= 2)
    control_mask = (0x8249A6F861C if template_index == 0 else 0x9E88A829374)
    control_selected = frozenset(allowed[local] for local in range(54)
                                 if control_mask >> local & 1)
    need(len(control_selected) == 19,
         "template%d relaxed control size" % template_index)
    need(all(not blocker <= control_selected for blocker in nonsingleton),
         "template%d relaxed control contains blocker" % template_index)
    control_profile = Counter((POINTS[v][0] % 3, POINTS[v][1] % 3)
                              for v in control_selected)
    need(max(control_profile.values()) <= 4,
         "template%d relaxed control fibre cap" % template_index)
    residual = midpoint_core(template | control_selected)
    expected_core = 27 if template_index == 0 else 31
    need(len(residual) == expected_core,
         "template%d relaxed control residual core" % template_index)
    data, clauses = build_cnf(allowed, nonsingleton)
    expected = (19336, 15093) if template_index == 0 else (8374, 4131)
    need((len(clauses), len(nonsingleton)) == expected,
         "template%d CNF census" % template_index)
    frozen = root / "data" / ("template%d.cnf" % template_index)
    need(frozen.read_bytes() == data, "template%d frozen CNF drift" % template_index)
    return len(ledger), len(nonsingleton), len(clauses), len(residual)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exhaustive-template0", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    guarded = {path: path.read_bytes() for path in (
        root / "data" / "template0_blockers.txt",
        root / "data" / "template1_blockers.txt",
        root / "data" / "template0.cnf",
        root / "data" / "template1.cnf")}
    results = tuple(validate_case(root, index) for index in (0, 1))
    if args.exhaustive_template0:
        template0 = frozenset(INDEX[p] for p in TEMPLATES[0])
        need(enumerate_minimal(template0, 5) ==
             parse_ledger(root / "data" / "template0_blockers.txt"),
             "template0 exhaustive family drift")
        print("PASS_TEMPLATE0_EXHAUSTIVE_LEDGER")
    need(all(path.read_bytes() == data for path, data in guarded.items()),
         "data mutation")
    print("PASS_Q9_BLOCKER_SEMANTICS")
    for index, (total, nonsingleton, clauses, residual) in enumerate(results):
        print("TEMPLATE%d blockers_total=%d blockers_nonsingleton=%d cnf_variables=944 cnf_clauses=%d sound=true minimal=true byte_exact=true relaxed_target19_residual_core=%d" %
              (index, total, nonsingleton, clauses, residual))
    print("DATA_NONMUTATION_OK")


if __name__ == "__main__":
    main()

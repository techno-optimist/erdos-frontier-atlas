#!/usr/bin/env python3
"""Independent standard-library hostile replay of the compact q9 certificate."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path, PurePosixPath
import argparse
import os
import shutil
import subprocess
import sys
import tempfile


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
EXPECTED_REPS = TEMPLATES
EXPECTED_HISTOGRAMS = (
    Counter({1:15, 3:297, 4:3177, 5:11619}),
    Counter({1:15, 3:297, 4:3798, 5:9, 6:27}),
)
RELAXED_MASKS = (0x2092080AB4D945, 0x11638C01264C7)
RELAXED_CORE_SIZES = (28, 31)
PRODUCER_RELAXED_MASKS = (0x8249A6F861C, 0x9E88A829374)
PRODUCER_RELAXED_CORE_SIZES = (27, 31)
ORDER30 = (
    (1,7),(5,1),(6,4),(0,4),(3,2),(8,8),(4,5),(6,0),
    (2,6),(3,6),(1,0),(4,7),(8,3),(5,3),(6,6),(3,8),
    (1,2),(8,5),(5,4),(6,8),(5,5),(7,3),(2,7),(7,5),
    (4,4),(1,3),(6,1),(8,7),(0,2),(3,0),
)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    state = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def safe_relative(text):
    path = PurePosixPath(text)
    return (text == path.as_posix() and not path.is_absolute() and
            text not in ("", ".") and "\\" not in text and
            all(part not in ("", ".", "..") for part in path.parts))


def regular_files(root):
    found = set()
    for path in root.rglob("*"):
        if path.is_file():
            need(not path.is_symlink(), "symlink payload is forbidden")
            found.add(path.relative_to(root).as_posix())
    return found


def verify_manifest(root):
    manifest = root / "SHA256SUMS.txt"
    raw = manifest.read_bytes()
    need(raw.endswith(b"\n") and b"\r" not in raw,
         "manifest must be LF-only and terminated")
    result = {}
    for line in raw.decode("ascii").splitlines():
        need(len(line) >= 67 and line[64:66] == " *", "bad manifest row")
        expected, relative = line[:64], line[66:]
        need(all(ch in "0123456789abcdef" for ch in expected), "bad digest")
        need(safe_relative(relative) and relative != manifest.name,
             "unsafe/self manifest path")
        need(relative not in result, "duplicate manifest path")
        path = root.joinpath(*relative.split("/"))
        need(path.is_file() and digest(path) == expected,
             "manifest mismatch: %s" % relative)
        result[relative] = expected
    need(result and list(result) == sorted(result), "empty/unsorted manifest")
    need(regular_files(root) == set(result) | {manifest.name},
         "manifest is not closed over regular files")
    return result


def core(vertices):
    """Greatest fixed point of the midpoint-support operator."""
    alive = frozenset(vertices)
    while alive:
        supported = frozenset(MID[a][b] for a, b in combinations(alive, 2)
                              if MID[a][b] in alive)
        if supported == alive:
            return alive
        alive = supported
    return alive


def parse_ledger(path):
    raw = path.read_bytes()
    need(raw.endswith(b"\n") and b"\r" not in raw,
         "ledger must be LF-only and terminated")
    rows = []
    for line_number, line in enumerate(raw.decode("ascii").splitlines(), 1):
        need(line, "blank ledger line %d" % line_number)
        points = []
        for token in line.split(" "):
            need(len(token) == 3 and token[1] == "," and
                 token[0] in "012345678" and token[2] in "012345678",
                 "noncanonical token line %d" % line_number)
            points.append(INDEX[(int(token[0]), int(token[2]))])
        need(1 <= len(points) <= 6 and points == sorted(set(points)),
             "bad blocker row %d" % line_number)
        rows.append(frozenset(points))
    canonical = tuple(sorted(set(rows),
                             key=lambda row: (len(row), tuple(sorted(row)))))
    need(tuple(rows) == canonical, "ledger order/uniqueness drift")
    return canonical


def verify_ledgers(root):
    summaries = []
    for index in (0, 1):
        template = frozenset(INDEX[p] for p in TEMPLATES[index])
        rows = parse_ledger(root / "data" / ("template%d_blockers.txt" % index))
        need(Counter(map(len, rows)) == EXPECTED_HISTOGRAMS[index],
             "template%d histogram drift" % index)
        need(not core(template), "template%d is not peelable" % index)
        for blocker in rows:
            need(core(template | blocker), "template%d unsound blocker" % index)
            for vertex in blocker:
                need(not core(template | (blocker-{vertex})),
                     "template%d blocker is not outside-minimal" % index)

        singleton = {next(iter(row)) for row in rows if len(row) == 1}
        allowed = tuple(v for v in range(81)
                        if v not in template and v not in singleton)
        need(len(singleton) == 15 and len(allowed) == 54,
             "template%d allowed census" % index)
        fibres = tuple(tuple(v for v in allowed
                             if POINTS[v][0] % 3 == rx and
                                POINTS[v][1] % 3 == ry)
                       for rx, ry in product(range(3), repeat=2)
                       if any(POINTS[v][0] % 3 == rx and
                              POINTS[v][1] % 3 == ry for v in allowed))
        need(len(fibres) == 6 and all(len(fibre) == 9 for fibre in fibres),
             "template%d six-fibre census" % index)
        need(all(core(five) for fibre in fibres for five in combinations(fibre, 5)),
             "template%d unsound local cap" % index)

        nonsingleton = tuple(row for row in rows if len(row) >= 2)
        residual_sizes = []
        for label, masks, expected_sizes in (
                ("independent", RELAXED_MASKS, RELAXED_CORE_SIZES),
                ("producer", PRODUCER_RELAXED_MASKS,
                 PRODUCER_RELAXED_CORE_SIZES)):
            mask = masks[index]
            selected = frozenset(allowed[j] for j in range(54) if mask >> j & 1)
            need(len(selected) == 19 and
                 all(not row <= selected for row in nonsingleton),
                 "template%d %s relaxed control violates blocker master" %
                 (index, label))
            profile = Counter((POINTS[v][0] % 3, POINTS[v][1] % 3)
                              for v in selected)
            need(max(profile.values()) <= 4,
                 "%s relaxed control violates fibre cap" % label)
            residual = core(template | selected)
            need(len(residual) == expected_sizes[index],
                 "template%d %s relaxed residual-core drift" % (index, label))
            residual_sizes.append(len(residual))
        summaries.append((len(rows), len(nonsingleton),
                          residual_sizes[0], residual_sizes[1]))
    print("PASS_HOSTILE_LEDGER_SEMANTICS", summaries, flush=True)
    return summaries


def verify_size30():
    order = tuple(INDEX[p] for p in ORDER30)
    need(len(set(order)) == 30, "size30 duplicate")
    earlier = []
    forbidden = set()
    for rank, vertex in enumerate(order):
        need(vertex not in forbidden, "size30 insertion failure rank %d" % rank)
        forbidden.update(MID[vertex][other] for other in earlier)
        earlier.append(vertex)
    values = {vertex: 4**rank for rank, vertex in enumerate(order)}
    defects = []
    raw_gaps = []
    torus_gaps = []
    for a, b in combinations(order, 2):
        middle = MID[a][b]
        if middle not in values:
            continue
        defect = values[a]+values[b]-2*values[middle]
        raw = sum((POINTS[a][j]-POINTS[b][j])**2 for j in range(2))
        torus = sum(min((POINTS[a][j]-POINTS[b][j]) % 9,
                        (POINTS[b][j]-POINTS[a][j]) % 9)**2
                    for j in range(2))
        need(defect > 0, "size30 potential is not strict")
        defects.append(defect)
        raw_gaps.append(81*defect-raw)
        torus_gaps.append(81*defect-torus)
    profile = tuple(sorted(Counter((x%3,y%3) for x,y in ORDER30).values(),
                           reverse=True))
    result = (len(defects), min(defects), min(raw_gaps), min(torus_gaps), profile)
    need(result == (131,18,1448,1448,(4,4,4,3,3,3,3,3,3)),
         "size30 exact ledger drift")
    print("PASS_HOSTILE_SIZE30", result, flush=True)
    return result


def is_cap(local_vertices):
    keep = set(local_vertices)
    return all(((2*(a[0]+b[0])) % 3, (2*(a[1]+b[1])) % 3) not in keep
               for a, b in combinations(local_vertices, 2))


def mask_of(vertices):
    result = 0
    for vertex in vertices:
        result |= 1 << vertex
    return result


def verify_slab():
    local = tuple(product(range(3), repeat=2))
    caps = tuple(cap for cap in combinations(local, 4) if is_cap(cap))
    need(len(caps) == 54 and
         not any(is_cap(five) for five in combinations(local, 5)),
         "AG(2,3) cap census drift")
    lifted = tuple(tuple(tuple(INDEX[((r+3*u)%9,3*v)] for u,v in cap)
                         for cap in caps) for r in range(3))
    feasible = set()
    for i,j,k in product(range(54), repeat=3):
        slab = lifted[0][i]+lifted[1][j]+lifted[2][k]
        candidate = mask_of(slab)
        if not core(slab):
            feasible.add(candidate)
    need(len(feasible) == 5832, "peelable slab census drift")

    affine = tuple((a,b,c,d,tx,ty)
                   for a,b,c,d in product(range(9), repeat=4)
                   if c%3 == 0 and (a*d-b*c)%3 != 0
                   for tx in range(9) for ty in (0,3,6))
    need(len(affine) == 26244, "slab stabilizer census drift")
    unseen = set(feasible)
    sizes = []
    reps = []
    while unseen:
        representative = min(unseen)
        members = tuple(v for v in range(81) if representative >> v & 1)
        images = set()
        for a,b,c,d,tx,ty in affine:
            images.add(mask_of(INDEX[((a*POINTS[v][0]+b*POINTS[v][1]+tx)%9,
                                      (c*POINTS[v][0]+d*POINTS[v][1]+ty)%9)]
                               for v in members))
        need(images <= feasible, "affine slab image escaped feasible family")
        unseen -= images
        sizes.append(len(images))
        reps.append(tuple(POINTS[v] for v in members))
    need(tuple(sizes) == (2916,2916) and tuple(reps) == EXPECTED_REPS,
         "two-orbit slab reduction drift")
    result = (len(caps), len(feasible), len(affine), tuple(sizes))
    print("PASS_HOSTILE_SLAB_ORBITS", result, flush=True)
    return result


def verify_h8():
    # Exhaust the digit-midpoint lift used in the Fubini slice argument.
    for a,b in combinations(range(81), 2):
        y = MID[a][b]
        need(all((POINTS[a][j]+POINTS[b][j]-2*POINTS[y][j]) % 9 == 0
                 for j in range(2)), "digit midpoint does not lift mod one")
    need(81*Fraction(1,81) == 1, "q9 Jacobian normalization")
    section = Fraction(31,81)
    need(Fraction(49,128)-section == Fraction(1,10368), "slice margin")
    marker0 = 2*Fraction(1,72)*section
    need(marker0 == Fraction(31,2916), "marker normalization")
    zero = Fraction(7,24)**2-8*marker0
    need(zero == Fraction(1,46656), "zero-epsilon gap")
    epsilon = Fraction(1,1_100_000)
    sigma = Fraction(4,3)*epsilon-2*epsilon**2
    gap = (Fraction(7,24)-epsilon)**2-8*(marker0+2*sigma)
    polynomial = (1-1022544*epsilon+1539648*epsilon**2)/46656
    need(gap == polynomial == Fraction(121027187,80190000000000) > 0,
         "round h8 endpoint")
    def g(value):
        return (1-1022544*value+1539648*value**2)/46656
    inside, outside = Fraction(1,1022543), Fraction(1,1022542)
    need(g(inside) == Fraction(517105,48783242381626944) > 0,
         "integer inside bracket")
    need(g(outside) == -Fraction(126359,12195786741535296) < 0,
         "integer outside bracket")
    need(1022544**2-4*1539648 == 1045590073344,
         "root discriminant")
    result = (section, marker0, zero, gap, inside, outside)
    print("PASS_HOSTILE_H8_ARITHMETIC", result, flush=True)
    return result


def run(command, root, expected=0, quiet=False):
    options = {"cwd": str(root), "text": True}
    if quiet:
        options.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    completed = subprocess.run(command, **options)
    need(completed.returncode == expected,
         "command exit %d expected %d: %s\n%s\n%s" %
         (completed.returncode, expected, command,
          completed.stdout if quiet else "", completed.stderr if quiet else ""))
    return completed


def verify_cover(root):
    compiler = next((shutil.which(name) for name in ("g++","clang++","c++")
                     if shutil.which(name)), None)
    need(compiler is not None, "no GCC-compatible C++14 compiler")
    with tempfile.TemporaryDirectory(prefix="q9_hostile_") as temporary:
        binary = Path(temporary) / ("hostile_cover.exe" if os.name == "nt"
                                    else "hostile_cover")
        run([compiler,"-O3","-std=c++14","-Wall","-Wextra","-pedantic",
             "-o",str(binary),str(root/"cover_independent.cpp")], root)
        outputs = []
        for index, expected_nodes in ((0,"nodes=1624151"),(1,"nodes=1192358")):
            completed = run([str(binary),str(root),str(index)], root,
                            quiet=True)
            need(("PASS_INDEPENDENT_TEMPLATE%d_COVER" % index) in completed.stdout and
                 expected_nodes in completed.stdout and "result=UNSAT" in completed.stdout,
                 "independent cover stdout drift")
            print(completed.stdout, end="", flush=True)
            outputs.append(completed.stdout)
        run([str(binary),str(root),"2"], root, expected=2, quiet=True)
        run([str(binary),str(root)], root, expected=2, quiet=True)
        bad = Path(temporary)/"bad"/"data"
        bad.mkdir(parents=True)
        target = bad/"template0_blockers.txt"
        shutil.copyfile(root/"data"/"template0_blockers.txt", target)
        with target.open("ab") as stream:
            stream.write(b"9,0\n")
        run([str(binary),str(bad.parent),"0"], root, expected=2, quiet=True)
    print("PASS_HOSTILE_COVER_NEGATIVE_CONTROLS", flush=True)
    return tuple(outputs)


def main():
    parser = argparse.ArgumentParser()
    parser.parse_args()
    root = Path(__file__).resolve().parent
    before = verify_manifest(root)
    print("PASS_HOSTILE_MANIFEST_INITIAL", flush=True)
    verify_ledgers(root)
    verify_size30()
    verify_slab()
    verify_h8()
    verify_cover(root)
    after = verify_manifest(root)
    need(before == after, "hostile packet mutation")
    print("PASS_HOSTILE_MANIFEST_FINAL", flush=True)
    print("PASS_INDEPENDENT_Q9_HOSTILE_REPLAY 30<=C9<=31", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Replay Ford's search for Erdos #357: A364132(29) = 79.

A364132(n) = least N such that {1..N} contains an increasing n-term sequence with all
n(n+1)/2 segment sums distinct (segment_sums.py has the definition).

Inputs (read, never written):
  ss_cleanroom.c                 Ford's engine, written from the OEIS definition alone
                                 (no atlas code); mode m searches increasing sequences.
                                 With "part k parts", the admissible choices of the second
                                 term are dealt round-robin, so parts 0..P-1 together
                                 cover the whole search.
  ford_searches_a364132_29.txt   its 116 committed answers: the control m27@68 (part
                                 6/14), m29@N for N = 76, 77, 78 (38 parts each, all NONE),
                                 and the first FOUND part at N = 79 (part 14/38; the
                                 remaining m29@79 parts were stopped once it was found)
  ford_searches_a364132_28.txt   the earlier receipt; supplies A364132(28) = 75, so
                                 A364132(29) >= 76 (delete the largest term)
  g4_crosscheck_a364132_29.txt   the second engine, segsum.c in this directory (written
                                 independently), unpartitioned, on m29@76, 77, 78:
                                 "none m n N nodes".
NONE for every part at N = 78 means no increasing 29-sequence has every term <= 78, so
A364132(29) >= 79 (76 and 77 are refuted too, as they must be); the FOUND sequence at 79,
checked by brute force, gives A364132(29) <= 79. No outside input is needed.

default (fast): format and completeness of the parts, brute-force check of the FOUND
  sequence, agreement of the two engines at 76..78, ss_cleanroom.c reproducing
  A364132(1..20) of RESULT.json, and planted-failure controls. No search at 76..79 is
  re-run, so the fast profile does not certify the claim.
--full [--jobs K]: also re-runs all 116 ss searches (about 1.6e12 nodes) and the 3
  segsum searches (about 4.8e11 nodes) and requires each line to be reproduced byte for byte.
An exhaustive computer search by two independent engines, not a formal proof.
"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
NT = 29
EXPECTED = 79
PREV = 75         # A364132(28), ford_searches_a364132_28.txt
LOW = PREV + 1
PARTS = 38
CONTROL = "m 27 68 part 6/14 NONE nodes 1260135573"
CONTROL_KEY = (27, 68, 6, 14)
FOUND_KEY = (NT, EXPECTED, 14, PARTS)
WITNESS = [7, 25, 26, 31, 34, 41, 43, 45, 49, 50, 52, 53, 54, 55, 56, 61, 63, 64, 66, 67,
           69, 70, 71, 72, 73, 74, 76, 77, 79]


def distinct_sums(seq):
    sums = [sum(seq[i:j]) for i in range(len(seq)) for j in range(i + 1, len(seq) + 1)]
    return len(sums) == len(set(sums))


def ok_witness(seq, n, N):
    return (len(seq) == n and all(a < b for a, b in zip(seq, seq[1:])) and min(seq) >= 1
            and max(seq) <= N and distinct_sums(seq))


def parse(lines):
    rows = {}
    for line in lines:
        line = line.rstrip("\n")
        p = line.split()
        if len(p) < 8 or p[0] != "m" or p[3] != "part" or p[-2] != "nodes":
            raise ValueError(f"malformed line: {line!r}")
        k, P = map(int, p[4].split("/"))
        key = (int(p[1]), int(p[2]), k, P)
        if key in rows:
            raise ValueError(f"duplicate {key}")
        rows[key] = {"v": p[5], "seq": [int(x) for x in p[6:-2]], "nodes": int(p[-1]),
                     "line": line}
    return rows


def parse_g4(lines):
    g = {}
    for line in lines:
        line = line.rstrip("\n")
        p = line.split()
        if len(p) != 5 or p[0] not in ("none", "found") or p[1] != "m":
            raise ValueError(f"malformed g4 line: {line!r}")
        key = (int(p[2]), int(p[3]))
        if key in g:
            raise ValueError(f"duplicate g4 {key}")
        g[key] = {"v": p[0], "nodes": int(p[4]), "line": line}
    return g


def derive(rows):
    """A364132(29) from the committed answers alone. Returns (value or None, problems)."""
    probs = []
    if rows.get(CONTROL_KEY, {}).get("line") != CONTROL:
        probs.append("control m27@68 part 6/14 missing or changed")
    for N in range(LOW, EXPECTED):
        for k in range(PARTS):
            r = rows.get((NT, N, k, PARTS))
            if r is None:
                probs.append(f"m29@{N}: part {k}/{PARTS} missing")
            elif r["v"] != "NONE" or r["seq"]:
                probs.append(f"m29@{N}: part {k}/{PARTS} is not a clean NONE")
    f = rows.get(FOUND_KEY)
    if f is None or f["v"] != "FOUND":
        probs.append(f"m29@{EXPECTED} part 14/38: no FOUND line")
    elif f["seq"] != WITNESS or not ok_witness(f["seq"], NT, EXPECTED) or max(f["seq"]) != EXPECTED:
        probs.append(f"m29@{EXPECTED}: witness fails the brute-force check")
    extra = sorted(k for k in rows if k not in (CONTROL_KEY, FOUND_KEY)
                   and not (k[0] == NT and LOW <= k[1] < EXPECTED and k[3] == PARTS
                            and 0 <= k[2] < PARTS))
    if extra:
        probs.append(f"unexpected lines {extra[:5]}")
    return (None if probs else EXPECTED), probs


def engines_agree(g4):
    probs = []
    want = [(NT, N) for N in range(LOW, EXPECTED)]
    if sorted(g4) != want:
        probs.append(f"g4 covers {sorted(g4)}")
    for key, q in g4.items():
        if q["v"] != "none":
            probs.append(f"g4 m{key[0]}@{key[1]}: verdict disagrees (ss: NONE)")
    return probs


def prev_value():
    rows = parse(open(HERE / "ford_searches_a364132_28.txt"))
    for k, r in rows.items():
        if k[:2] == (28, PREV) and r["v"] == "FOUND" and ok_witness(r["seq"], 28, PREV):
            return PREV
    return None


def build(tmp, src, name):
    exe = Path(tmp) / name
    subprocess.run(["gcc", "-O2", "-o", str(exe), str(HERE / src)], check=True)
    return exe


def run(argv):
    return subprocess.run([str(a) for a in argv], capture_output=True, text=True,
                          check=True).stdout.rstrip("\n")


def main():
    args = sys.argv[1:]
    full = "--full" in args
    jobs = int(args[args.index("--jobs") + 1]) if "--jobs" in args else (os.cpu_count() or 1)
    rows = parse(open(HERE / "ford_searches_a364132_29.txt"))
    g4 = parse_g4(open(HERE / "g4_crosscheck_a364132_29.txt"))
    result = json.load(open(HERE / "RESULT.json"))
    fails = []

    val, probs = derive(rows)
    fails += probs
    fails += engines_agree(g4)
    if prev_value() != PREV:
        fails.append("ford_searches_a364132_28.txt has no brute-checked FOUND at 75")
    a = result["claims"]["A364132"]
    if len(a) != 27 or a[26] != 69:
        fails.append("RESULT.json A364132(1..27) changed")
    sums = sorted(sum(WITNESS[i:j]) for i in range(NT) for j in range(i + 1, NT + 1))
    print(f"ss: control + {PARTS} parts NONE at each N = {LOW}..{EXPECTED - 1} + "
          f"FOUND at {EXPECTED} (part 14/38); A364132(29) = {val}")
    print(f"witness {' '.join(map(str, WITNESS))}: strictly increasing in "
          f"{min(WITNESS)}..{max(WITNESS)}, {len(set(sums))} of {len(sums)} segment sums distinct")
    print(f"second engine: none at {LOW}..{EXPECTED - 1}; A364132(28) = {PREV} from the a28 receipt")

    # planted-failure controls: the checker must reject each of these
    bad = {k: dict(v) for k, v in rows.items()}
    planted = WITNESS[:-2] + [77, WITNESS[1] + WITNESS[2] + WITNESS[3]]    # last = 25 + 26 + 31 = 82 > 79
    bad[FOUND_KEY]["seq"] = planted
    if not derive(bad)[1] or ok_witness(planted, NT, EXPECTED):
        fails.append("control: planted out-of-range witness accepted")
    coll = [1, 2, 3] + WITNESS[3:]
    if ok_witness(coll, NT, EXPECTED):
        fails.append("control: planted witness with 1 + 2 = 3 accepted")
    flip = {k: dict(v) for k, v in rows.items()}
    flip[(NT, 78, 37, PARTS)]["v"] = "FOUND"
    if not derive(flip)[1]:
        fails.append("control: planted flipped verdict at m29@78 part 37 accepted")
    drop = {k: v for k, v in rows.items() if k != (NT, 78, 11, PARTS)}
    if not derive(drop)[1]:
        fails.append("control: dropped part 11 of m29@78 accepted")
    g4bad = {k: dict(v) for k, v in g4.items()}
    g4bad[(NT, 78)]["v"] = "found"
    if not engines_agree(g4bad):
        fails.append("control: planted engine disagreement at 78 accepted")
    if ok_witness([2, 1, 4], 3, 4):
        fails.append("control: planted non-increasing sequence accepted")
    print("controls: planted out-of-range witness / collision 1+2 = 3 / flipped verdict / dropped part / "
          "engine disagreement / non-increasing sequence rejected")

    with tempfile.TemporaryDirectory() as tmp:
        ss = build(tmp, "ss_cleanroom.c", "ss")
        for n in range(1, 21):
            hi = run([ss, "m", n, a[n - 1]]).split()
            if hi[5] != "FOUND" or not ok_witness([int(x) for x in hi[6:-2]], n, a[n - 1]):
                fails.append(f"ss does not find a valid sequence at A364132({n}) = {a[n-1]}")
            if a[n - 1] > n:
                lo = run([ss, "m", n, a[n - 1] - 1]).split()
                if lo[5] != "NONE":
                    fails.append(f"ss finds a sequence below A364132({n})")
        print("ss_cleanroom.c reproduces A364132(1..20) of RESULT.json")
        todo = sorted(rows, key=lambda k: -rows[k]["nodes"]) if full else []
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            futs = [(k, ex.submit(run, [ss, "m", k[0], k[1], k[2], k[3]])) for k in todo]
            g4todo = sorted(g4, key=lambda k: -g4[k]["nodes"]) if full else []
            if g4todo:
                seg = build(tmp, "segsum.c", "segsum")
                gfuts = [(k, ex.submit(run, [seg, "m", k[0], k[1]])) for k in g4todo]
            else:
                gfuts = []
            diff = [k for k, fu in futs if fu.result() != rows[k]["line"]]
            gdiff = [k for k, fu in gfuts if fu.result() != g4[k]["line"]]
        if diff:
            fails.append(f"ss re-run differs from committed line at {diff[:5]}")
        if gdiff:
            fails.append(f"segsum re-run differs from committed line at {gdiff}")
        print(f"re-ran {len(todo)} of {len(rows)} ss searches and {len(gfuts)} of {len(g4)} "
              f"segsum searches: {len(todo) - len(diff)} + {len(gfuts) - len(gdiff)} "
              f"reproduced byte for byte")

    if fails:
        for x in fails:
            print("FAIL:", x)
        sys.exit(1)
    print('"verified_ford_a364132_29":true' if full else '"receipt_consistent_a364132_29":true')
    print("all checks passed")


if __name__ == "__main__":
    main()

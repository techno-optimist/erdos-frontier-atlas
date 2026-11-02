#!/usr/bin/env python3
"""Replay Ford's search for Erdos #357: A364153(19) = 29.

A364153(n) = least N such that some n-sequence of distinct values from {1..N}, in any
order, has all n(n+1)/2 segment sums distinct (segment_sums.py has the definition).

Inputs (read, never written):
  ss_cleanroom.c                 Ford's engine (same file as for A364153(17) and (18));
                                 mode a has no symmetry breaking; "part k parts" deals the
                                 second term round-robin, so parts 0..P-1 cover the search.
  ford_searches_a364153_19.txt   its 41 committed answers: the controls a16@23 (part 0/14,
                                 NONE) and a18@28 (part 1/19, FOUND, the A364153(18)
                                 sequence), a19@28 in 38 parts (all NONE) and one FOUND
                                 line at a19@29 (part 8 of 38)
  g4_crosscheck_a364153_19.txt   the second engine, segsum.c in this directory, on a16@23
                                 and a19@28: "none a n N nodes".
NONE for every part at N = 28 means no admissible 19-sequence has every term <= 28, so
A364153(19) >= 29; the FOUND sequence at 29, checked by brute force, gives
A364153(19) <= 29. No outside input is needed.

default (fast): format and completeness, brute-force check of the witness, agreement of
  the two engines at 28, segsum's a16@23 node count equal to the one pinned in
  RESULT.json, ss_cleanroom.c reproducing A364153(1..12) of RESULT.json, a byte-for-byte
  re-run of the a18@28 control, and planted-failure controls. Neither the NONE searches
  nor the a19@29 FOUND search (about 8.8e9 nodes) is re-run, so the fast profile does
  not certify the claim.
--full [--jobs K]: also re-runs all 41 ss searches (about 1.0e12 nodes) and the 2
  segsum searches (about 1.0e12 nodes) and requires each line to be reproduced byte for
  byte.
An exhaustive computer search by two independent engines, not a formal proof.
"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
NT = 19
EXPECTED = 29
PARTS = 38
FOUND_PARTS = (8,)
LO = (28,)
CONTROL = "a 16 23 part 0/14 NONE nodes 586748917"
CONTROL2 = ("a 18 28 part 1/19 FOUND 1 3 2 7 22 25 28 21 27 18 24 20 23 14 26 15 17 19 "
            "nodes 4230925")
CONTROL_KEYS = ((16, 23, 0, 14), (18, 28, 1, 19))


def distinct_sums(seq):
    sums = [sum(seq[i:j]) for i in range(len(seq)) for j in range(i + 1, len(seq) + 1)]
    return len(sums) == len(set(sums))


def ok_witness(seq, n, N):
    return (len(seq) == n and len(set(seq)) == n and min(seq) >= 1 and max(seq) <= N
            and distinct_sums(seq))


def parse(lines):
    rows = {}
    for line in lines:
        line = line.rstrip("\n")
        p = line.split()
        if len(p) < 8 or p[0] != "a" or p[3] != "part" or p[-2] != "nodes":
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
        if len(p) != 5 or p[0] not in ("none", "found") or p[1] != "a":
            raise ValueError(f"malformed g4 line: {line!r}")
        g[(int(p[2]), int(p[3]))] = {"v": p[0], "nodes": int(p[4]), "line": line}
    return g


def derive(rows):
    """A364153(19) from the committed answers alone. Returns (value or None, problems)."""
    probs = []
    if rows.get(CONTROL_KEYS[0], {}).get("line") != CONTROL:
        probs.append("control a16@23 part 0/14 missing or changed")
    c2 = rows.get(CONTROL_KEYS[1])
    if c2 is None or c2["line"] != CONTROL2 or not ok_witness(c2["seq"], 18, 28):
        probs.append("control a18@28 part 1/19 missing, changed or not a valid witness")
    for N in LO:
        for k in range(PARTS):
            r = rows.get((NT, N, k, PARTS))
            if r is None:
                probs.append(f"a19@{N}: part {k}/{PARTS} missing")
            elif r["v"] != "NONE" or r["seq"]:
                probs.append(f"a19@{N}: part {k}/{PARTS} is not a clean NONE")
    for k in FOUND_PARTS:
        f = rows.get((NT, EXPECTED, k, PARTS))
        if f is None or f["v"] != "FOUND":
            probs.append(f"a19@29 part {k} FOUND line missing")
        elif not ok_witness(f["seq"], NT, EXPECTED) or max(f["seq"]) != EXPECTED:
            probs.append(f"a19@29 part {k} witness fails the brute-force check")
    found = {(NT, EXPECTED, k, PARTS) for k in FOUND_PARTS}
    extra = sorted(k for k in rows if k not in CONTROL_KEYS and k not in found
                   and not (k[0] == NT and k[1] in LO and k[3] == PARTS
                            and 0 <= k[2] < PARTS))
    if extra:
        probs.append(f"unexpected lines {extra[:5]}")
    return (None if probs else EXPECTED), probs


def engines_agree(rows, g4):
    probs = []
    if sorted(g4) != [(16, 23), (NT, 28)]:
        probs.append(f"g4 covers {sorted(g4)}")
    for key, q in g4.items():
        if key[0] == NT:
            parts = [r for k, r in rows.items() if k[:2] == key]
            if q["v"] != "none" or not parts or any(r["v"] != "NONE" for r in parts):
                probs.append(f"g4 a{key[0]}@{key[1]}: verdict disagrees")
        elif q["v"] != "none":
            probs.append("g4 control a16@23 is not none")
    return probs


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
    rows = parse(open(HERE / "ford_searches_a364153_19.txt"))
    g4 = parse_g4(open(HERE / "g4_crosscheck_a364153_19.txt"))
    result = json.load(open(HERE / "RESULT.json"))
    fails = []

    val, probs = derive(rows)
    fails += probs
    fails += engines_agree(rows, g4)
    a = result["claims"]["A364153"]
    if len(a) != 16 or a[15] != 24:
        fails.append("RESULT.json A364153(1..16) changed")
    pinned = [s for s in result["searches"] if s[:3] == ["a", 16, 23]]
    if not pinned or pinned[0][3] != g4.get((16, 23), {}).get("nodes") or pinned[0][4]:
        fails.append("segsum a16@23 node count differs from RESULT.json")
    wits = [rows[(NT, EXPECTED, k, PARTS)]["seq"] for k in FOUND_PARTS
            if (NT, EXPECTED, k, PARTS) in rows]
    print(f"ss: 2 controls + {PARTS} parts NONE at 28 + {len(wits)} FOUND at 29; "
          f"A364153(19) = {val}")
    for wit in wits:
        sums = sorted(sum(wit[i:j]) for i in range(NT) for j in range(i + 1, NT + 1))
        print(f"witness {' '.join(map(str, wit))}: {len(set(wit))} distinct terms in "
              f"{min(wit)}..{max(wit)}, {len(set(sums))} of {len(sums)} segment sums distinct")
    print(f"second engine: none at 28, a16@23 nodes {g4[(16, 23)]['nodes']} = RESULT.json")

    # planted-failure controls: the checker must reject each of these
    wit = wits[0]
    bad = {k: dict(v) for k, v in rows.items()}
    bad[(NT, EXPECTED, 8, PARTS)]["seq"] = wit[:-1] + [wit[0] + wit[1]]
    if not derive(bad)[1]:
        fails.append("control: planted bad witness (last term = s1 + s2) accepted")
    rep = {k: dict(v) for k, v in rows.items()}
    rep[(NT, EXPECTED, 8, PARTS)]["seq"] = wit[:-1] + [wit[0]]
    if not derive(rep)[1]:
        fails.append("control: planted witness with a repeated term accepted")
    flip = {k: dict(v) for k, v in rows.items()}
    flip[(NT, 28, 37, PARTS)]["v"] = "FOUND"
    if not derive(flip)[1]:
        fails.append("control: planted flipped verdict at a19@28 part 37 accepted")
    drop = {k: v for k, v in rows.items() if k != (NT, 28, 17, PARTS)}
    if not derive(drop)[1]:
        fails.append("control: dropped part 17 of a19@28 accepted")
    g4bad = {k: dict(v) for k, v in g4.items()}
    g4bad[(NT, 28)]["v"] = "found"
    if not engines_agree(rows, g4bad):
        fails.append("control: planted engine disagreement at 28 accepted")
    if ok_witness([1, 2, 3], 3, 3):
        fails.append("control: planted collision 1+2 = 3 accepted")
    print("controls: planted bad witness / repeated term / flipped verdict / dropped part / "
          "engine disagreement / collision 1+2 = 3 rejected")

    with tempfile.TemporaryDirectory() as tmp:
        ss = build(tmp, "ss_cleanroom.c", "ss")
        for n in range(1, 13):
            hi = run([ss, "a", n, a[n - 1]]).split()
            if hi[5] != "FOUND" or not ok_witness([int(x) for x in hi[6:-2]], n, a[n - 1]):
                fails.append(f"ss does not find a valid sequence at A364153({n}) = {a[n-1]}")
            if a[n - 1] > n:
                lo = run([ss, "a", n, a[n - 1] - 1]).split()
                if lo[5] != "NONE":
                    fails.append(f"ss finds a sequence below A364153({n})")
        print("ss_cleanroom.c reproduces A364153(1..12) of RESULT.json")
        todo = (sorted(rows, key=lambda k: -rows[k]["nodes"]) if full
                else [CONTROL_KEYS[1]])
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            futs = [(k, ex.submit(run, [ss, "a", k[0], k[1], k[2], k[3]])) for k in todo]
            g4todo = sorted(g4, key=lambda k: -g4[k]["nodes"]) if full else []
            if g4todo:
                seg = build(tmp, "segsum.c", "segsum")
                gfuts = [(k, ex.submit(run, [seg, "a", k[0], k[1]])) for k in g4todo]
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
    print('"verified_ford_a364153_19":true' if full else '"receipt_consistent_a364153_19":true')
    print("all checks passed")


if __name__ == "__main__":
    main()

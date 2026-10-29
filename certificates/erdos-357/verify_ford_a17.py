#!/usr/bin/env python3
"""Replay Ford's search for Erdos #357: A364153(17) = 26.

A364153(n) = least N such that some n-sequence of distinct values from {1..N}, in any
order, has all n(n+1)/2 segment sums distinct (segment_sums.py has the definition).

Inputs (read, never written):
  ss_cleanroom.c                 Ford's engine, written from the OEIS definition alone
                                 (no atlas code); mode a has no symmetry breaking. With
                                 "part k parts", the admissible choices of the second
                                 term are dealt round-robin, so parts 0..P-1 together
                                 cover the whole search.
  ford_searches_a364153_17.txt   its 40 committed answers: the control a16@23 (part
                                 0/14), a17@24 and a17@25 (19 parts each, all NONE) and
                                 a17@26 (FOUND with a 17-term sequence)
  g4_crosscheck_a364153_17.txt   the second engine, segsum.c in this directory (written
                                 independently; keeps only s_1 < s_n), on a16@23, a17@24
                                 and a17@25: "none a n N nodes".
NONE for every part at N = 25 means no admissible 17-sequence has every term <= 25, so
A364153(17) >= 26; the FOUND sequence at 26, checked by brute force, gives
A364153(17) <= 26. No outside input is needed.

default (fast): format and completeness of the parts, brute-force check of the witness,
  agreement of the two engines at 24 and 25, segsum's a16@23 node count equal to the one
  pinned in RESULT.json, ss_cleanroom.c reproducing A364153(1..12) of RESULT.json
  (NONE at a(n) - 1, FOUND at a(n), each FOUND sequence brute-checked), a byte-for-byte
  re-run of the FOUND search a17@26, and planted-failure controls. The NONE searches
  are not re-run, so the fast profile does not certify the claim.
--full [--jobs K]: also re-runs all 40 ss searches (about 7.8e10 nodes) and the 3 segsum
  searches (about 8.5e10 nodes) and requires each line to be reproduced byte for byte.
An exhaustive computer search by two independent engines, not a formal proof.
"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
NT = 17
EXPECTED = 26
PARTS = 19
CONTROL = "a 16 23 part 0/14 NONE nodes 586748917"


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
    """A364153(17) from the committed answers alone. Returns (value or None, problems)."""
    probs = []
    if rows.get((16, 23, 0, 14), {}).get("line") != CONTROL:
        probs.append("control a16@23 part 0/14 missing or changed")
    for N in (24, 25):
        for k in range(PARTS):
            r = rows.get((NT, N, k, PARTS))
            if r is None:
                probs.append(f"a17@{N}: part {k}/{PARTS} missing")
            elif r["v"] != "NONE" or r["seq"]:
                probs.append(f"a17@{N}: part {k}/{PARTS} is not a clean NONE")
    f = rows.get((NT, EXPECTED, 0, 1))
    if f is None or f["v"] != "FOUND":
        probs.append("a17@26 FOUND line missing")
    elif not ok_witness(f["seq"], NT, EXPECTED) or max(f["seq"]) != EXPECTED:
        probs.append("a17@26 witness fails the brute-force check")
    extra = sorted(k for k in rows if k != (16, 23, 0, 14) and k != (NT, EXPECTED, 0, 1)
                   and not (k[0] == NT and k[1] in (24, 25) and k[3] == PARTS
                            and 0 <= k[2] < PARTS))
    if extra:
        probs.append(f"unexpected lines {extra[:5]}")
    return (None if probs else EXPECTED), probs


def engines_agree(rows, g4):
    probs = []
    if sorted(g4) != [(16, 23), (NT, 24), (NT, 25)]:
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
    rows = parse(open(HERE / "ford_searches_a364153_17.txt"))
    g4 = parse_g4(open(HERE / "g4_crosscheck_a364153_17.txt"))
    result = json.load(open(HERE / "RESULT.json"))
    fails = []

    val, probs = derive(rows)
    fails += probs
    fails += engines_agree(rows, g4)
    a = result["claims"]["A364153"]
    if len(a) != 16 or a[15] != 24:
        fails.append("RESULT.json A364153(1..16) changed")
    if EXPECTED < a[15]:
        fails.append("A364153 would not be monotone")
    pinned = [s for s in result["searches"] if s[:3] == ["a", 16, 23]]
    if not pinned or pinned[0][3] != g4.get((16, 23), {}).get("nodes") or pinned[0][4]:
        fails.append("segsum a16@23 node count differs from RESULT.json")
    wit = rows[(NT, EXPECTED, 0, 1)]["seq"]
    if wit != result["next_bounds"]["A364153"]["sequence"]:
        fails.append("witness differs from RESULT.json next_bounds")
    sums = sorted(sum(wit[i:j]) for i in range(NT) for j in range(i + 1, NT + 1))
    print(f"ss: control + {PARTS} parts NONE at 24 + {PARTS} parts NONE at 25 + FOUND at 26; "
          f"A364153(17) = {val}")
    print(f"witness {' '.join(map(str, wit))}: {len(set(wit))} distinct terms in "
          f"{min(wit)}..{max(wit)}, {len(set(sums))} of {len(sums)} segment sums distinct")
    print(f"second engine: none at 24 and 25, a16@23 nodes {g4[(16, 23)]['nodes']} = RESULT.json")

    # planted-failure controls: the checker must reject each of these
    bad = {k: dict(v) for k, v in rows.items()}
    bad[(NT, EXPECTED, 0, 1)]["seq"] = wit[:-1] + [wit[0] + wit[1]]
    if not derive(bad)[1]:
        fails.append("control: planted bad witness (last term = s1 + s2) accepted")
    flip = {k: dict(v) for k, v in rows.items()}
    flip[(NT, 25, 18, PARTS)]["v"] = "FOUND"
    if not derive(flip)[1]:
        fails.append("control: planted flipped verdict at a17@25 part 18 accepted")
    drop = {k: v for k, v in rows.items() if k != (NT, 25, 7, PARTS)}
    if not derive(drop)[1]:
        fails.append("control: dropped part 7 of a17@25 accepted")
    g4bad = {k: dict(v) for k, v in g4.items()}
    g4bad[(NT, 25)]["v"] = "found"
    if not engines_agree(rows, g4bad):
        fails.append("control: planted engine disagreement at 25 accepted")
    if ok_witness([1, 2, 3], 3, 3):
        fails.append("control: planted collision 1+2 = 3 accepted")
    print("controls: planted bad witness / flipped verdict / dropped part / engine "
          "disagreement / collision 1+2 = 3 rejected")

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
        todo = sorted(rows, key=lambda k: -rows[k]["nodes"]) if full else [(NT, EXPECTED, 0, 1)]
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
    print('"verified_ford_a364153_17":true' if full else '"receipt_consistent_a364153_17":true')
    print("all checks passed")


if __name__ == "__main__":
    main()

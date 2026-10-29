#!/usr/bin/env python3
"""Replay Ford's search for Erdos #357: A364132(28) = 75.

A364132(n) = least N such that {1..N} contains an increasing n-term sequence with all
n(n+1)/2 segment sums distinct (segment_sums.py has the definition).

Inputs (read, never written):
  ss_cleanroom.c                 Ford's engine, written from the OEIS definition alone
                                 (no atlas code); mode m searches increasing sequences.
                                 With "part k parts", the admissible choices of the second
                                 term are dealt round-robin, so parts 0..P-1 together
                                 cover the whole search.
  ford_searches_a364132_28.txt   its 229 committed answers: the control m27@68 (part
                                 6/14), and m28@N for N = 70..75 (38 parts each): all NONE
                                 for N = 70..74; at N = 75, 36 parts NONE and 2 FOUND
  g4_crosscheck_a364132_28.txt   the second engine, segsum.c in this directory (written
                                 independently), unpartitioned, on m27@68 (control) and
                                 m28@70..75: "none m n N nodes" or "found m n N nodes : seq".
NONE for every part at N = 74 means no increasing 28-sequence has every term <= 74, so
A364132(28) >= 75 (N = 70..73 are refuted too, as they must be); a FOUND sequence at 75,
checked by brute force, gives A364132(28) <= 75. No outside input is needed.

default (fast): format and completeness of the parts, brute-force check of every FOUND
  sequence, agreement of the two engines at 70..75, segsum's m27@68 node count equal to
  the one pinned in RESULT.json, ss_cleanroom.c reproducing A364132(1..20) of RESULT.json
  (NONE at a(n) - 1, FOUND at a(n), each FOUND sequence brute-checked), a byte-for-byte
  re-run of the FOUND search m28@75 part 36/38, and planted-failure controls. The NONE
  searches are not re-run, so the fast profile does not certify the claim.
--full [--jobs K]: also re-runs all 229 ss searches (about 8.8e11 nodes) and the 6
  segsum searches (about 2e11 nodes) and requires each line to be reproduced byte for byte.
An exhaustive computer search by two independent engines, not a formal proof.
"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
NT = 28
EXPECTED = 75
LOW = 70          # A364132(27) = 69 and the sequence is strictly increasing
PARTS = 38
CONTROL = "m 27 68 part 6/14 NONE nodes 1260135573"
CONTROL_KEY = (27, 68, 6, 14)
FAST_FOUND = (NT, EXPECTED, 36, PARTS)
WITNESS = [2, 3, 4, 6, 11, 25, 38, 40, 41, 47, 52, 54, 56, 57, 58, 60, 61, 62, 64, 66,
           67, 68, 69, 70, 71, 72, 73, 75]


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
        if len(p) < 5 or p[0] not in ("none", "found") or p[1] != "m":
            raise ValueError(f"malformed g4 line: {line!r}")
        seq = []
        if p[0] == "found":
            if len(p) < 7 or p[5] != ":":
                raise ValueError(f"malformed g4 found line: {line!r}")
            seq = [int(x) for x in p[6:]]
        elif len(p) != 5:
            raise ValueError(f"malformed g4 line: {line!r}")
        key = (int(p[2]), int(p[3]))
        if key in g:
            raise ValueError(f"duplicate g4 {key}")
        g[key] = {"v": p[0], "nodes": int(p[4]), "seq": seq, "line": line}
    return g


def derive(rows):
    """A364132(28) from the committed answers alone. Returns (value or None, problems)."""
    probs = []
    if rows.get(CONTROL_KEY, {}).get("line") != CONTROL:
        probs.append("control m27@68 part 6/14 missing or changed")
    for N in range(LOW, EXPECTED + 1):
        for k in range(PARTS):
            r = rows.get((NT, N, k, PARTS))
            if r is None:
                probs.append(f"m28@{N}: part {k}/{PARTS} missing")
            elif r["v"] == "NONE":
                if r["seq"]:
                    probs.append(f"m28@{N}: part {k}/{PARTS} NONE carries a sequence")
            elif r["v"] == "FOUND":
                if N < EXPECTED:
                    probs.append(f"m28@{N}: part {k}/{PARTS} is FOUND below {EXPECTED}")
                elif not ok_witness(r["seq"], NT, N) or max(r["seq"]) != N:
                    probs.append(f"m28@{N}: part {k}/{PARTS} witness fails the brute-force check")
            else:
                probs.append(f"m28@{N}: part {k}/{PARTS} bad verdict")
    found = [k for k, r in rows.items() if k[:2] == (NT, EXPECTED) and r["v"] == "FOUND"]
    if not found:
        probs.append(f"m28@{EXPECTED}: no FOUND part")
    if rows.get(FAST_FOUND, {}).get("seq") != WITNESS:
        probs.append("m28@75 part 36/38 is not the recorded witness")
    extra = sorted(k for k in rows if k != CONTROL_KEY
                   and not (k[0] == NT and LOW <= k[1] <= EXPECTED and k[3] == PARTS
                            and 0 <= k[2] < PARTS))
    if extra:
        probs.append(f"unexpected lines {extra[:5]}")
    return (None if probs else EXPECTED), probs


def engines_agree(rows, g4):
    probs = []
    want = [(27, 68)] + [(NT, N) for N in range(LOW, EXPECTED + 1)]
    if sorted(g4) != want:
        probs.append(f"g4 covers {sorted(g4)}")
    for key, q in g4.items():
        if key[0] == NT:
            parts = [r for k, r in rows.items() if k[:2] == key]
            ss_found = any(r["v"] == "FOUND" for r in parts)
            if not parts or (q["v"] == "found") != ss_found:
                probs.append(f"g4 m{key[0]}@{key[1]}: verdict disagrees")
            if q["v"] == "found" and not ok_witness(q["seq"], NT, key[1]):
                probs.append(f"g4 m{key[0]}@{key[1]}: found sequence fails the brute-force check")
        elif q["v"] != "none":
            probs.append("g4 control m27@68 is not none")
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
    rows = parse(open(HERE / "ford_searches_a364132_28.txt"))
    g4 = parse_g4(open(HERE / "g4_crosscheck_a364132_28.txt"))
    result = json.load(open(HERE / "RESULT.json"))
    fails = []

    val, probs = derive(rows)
    fails += probs
    fails += engines_agree(rows, g4)
    a = result["claims"]["A364132"]
    if len(a) != 27 or a[26] != 69 or LOW != a[26] + 1:
        fails.append("RESULT.json A364132(1..27) changed")
    pinned = [s for s in result["searches"] if s[:3] == ["m", 27, 68]]
    if not pinned or pinned[0][3] != g4.get((27, 68), {}).get("nodes") or pinned[0][4]:
        fails.append("segsum m27@68 node count differs from RESULT.json")
    if EXPECTED > result["next_bounds"]["A364132"]["N"]:
        fails.append("value exceeds the RESULT.json next_bounds upper end")
    founds = sorted(k for k, r in rows.items() if r["v"] == "FOUND")
    sums = sorted(sum(WITNESS[i:j]) for i in range(NT) for j in range(i + 1, NT + 1))
    print(f"ss: control + {PARTS} parts NONE at each N = {LOW}..{EXPECTED - 1} + "
          f"{len(founds)} FOUND parts at {EXPECTED}; A364132(28) = {val}")
    print(f"witness {' '.join(map(str, WITNESS))}: strictly increasing in "
          f"{min(WITNESS)}..{max(WITNESS)}, {len(set(sums))} of {len(sums)} segment sums distinct")
    print(f"second engine: none at {LOW}..{EXPECTED - 1}, found at {EXPECTED} (brute-checked), "
          f"m27@68 nodes {g4.get((27, 68), {}).get('nodes')} = RESULT.json")

    # planted-failure controls: the checker must reject each of these
    bad = {k: dict(v) for k, v in rows.items()}
    planted = WITNESS[:-1] + [WITNESS[4] + WITNESS[5] + WITNESS[6]]   # last = 11 + 25 + 38
    bad[FAST_FOUND]["seq"] = planted
    if not derive(bad)[1] or ok_witness(planted, NT, EXPECTED):
        fails.append("control: planted bad witness (last term = 11 + 25 + 38) accepted")
    flip = {k: dict(v) for k, v in rows.items()}
    flip[(NT, 74, 37, PARTS)]["v"] = "FOUND"
    if not derive(flip)[1]:
        fails.append("control: planted flipped verdict at m28@74 part 37 accepted")
    drop = {k: v for k, v in rows.items() if k != (NT, 74, 11, PARTS)}
    if not derive(drop)[1]:
        fails.append("control: dropped part 11 of m28@74 accepted")
    g4bad = {k: dict(v) for k, v in g4.items()}
    g4bad[(NT, 74)]["v"] = "found"
    if not engines_agree(rows, g4bad):
        fails.append("control: planted engine disagreement at 74 accepted")
    if ok_witness([1, 2, 3], 3, 3):
        fails.append("control: planted collision 1+2 = 3 accepted")
    if ok_witness([2, 1, 4], 3, 4):
        fails.append("control: planted non-increasing sequence accepted")
    print("controls: planted bad witness (last term = 11 + 25 + 38) / flipped verdict / dropped part / engine "
          "disagreement / collision 1+2 = 3 / non-increasing sequence rejected")

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
        todo = sorted(rows, key=lambda k: -rows[k]["nodes"]) if full else [FAST_FOUND]
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
    print('"verified_ford_a364132_28":true' if full else '"receipt_consistent_a364132_28":true')
    print("all checks passed")


if __name__ == "__main__":
    main()

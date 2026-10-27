#!/usr/bin/env python3
"""Replay Ford's clean-room search for Erdos #1109 up to N = 3000.

f(N) = A392164(N) = max |S|, S in {1..N}, every a+b (a = b allowed) squarefree.
A392165(k) = least N with f(N) >= k.

ford_searches_2_3000.txt holds one line per N <= 3000 with 2N squarefree:
"N <N> t <t> FOUND|NONE nodes <n> nv <v> [set ...]", the output of sqc_ford.c asked
"is there S of size t+1 with max(S) = N?". Since f(N) <= f(N-1) + 1, chaining those
answers from f(1) = 1 derives f(N) for every N <= 3000 with no external input.

default (fast): chain check, trial-division check of every witness, agreement with the
  promoted A392165(1..54) certificate (RESULT.json), planted-failure controls, a pure
  Python cross-check of the C engine for N <= 60, and a byte-for-byte re-run of every
  committed search with at most 1,000,000 nodes. The expensive NONE searches are NOT
  re-run, so the fast profile does not certify the claim.
--full [--jobs K]: re-runs all 1,213 committed searches (about 1.05e11 nodes, roughly
  40+ core-hours) and requires every line to be reproduced byte for byte.
A verified-search receipt, not a formal proof.
"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
NMAX = 3000
EXPECTED_55_65 = [2071, 2141, 2193, 2287, 2355, 2427, 2455, 2627, 2729, 2741, 2993]
FAST_NODE_LIMIT = 1_000_000


def sqf(x):
    p = 2
    while p * p <= x:
        if x % (p * p) == 0:
            return False
        p += 1
    return True


def parse(lines):
    rows = {}
    for line in lines:
        p = line.split()
        if len(p) < 9 or p[0] != "N":
            raise ValueError(f"malformed line: {line!r}")
        N = int(p[1])
        if N in rows:
            raise ValueError(f"duplicate N {N}")
        rows[N] = {"t": int(p[3]), "v": p[4], "nodes": int(p[6]),
                   "set": [int(x) for x in p[p.index("set") + 1:]] if "set" in p else None,
                   "line": line.rstrip("\n")}
    return rows


def ok_witness(S, N, k):
    return (len(S) == k and len(set(S)) == k and max(S) == N and min(S) >= 1
            and all(sqf(a + b) for i, a in enumerate(S) for b in S[i:]))


def chain(rows):
    """Derive f(1..NMAX) from the committed answers alone. Returns (f, problems)."""
    f = {1: 1}
    probs = []
    for N in range(2, NMAX + 1):
        if not sqf(2 * N):
            if N in rows:
                probs.append(f"N={N}: 2N not squarefree but a search line exists")
            f[N] = f[N - 1]
            continue
        r = rows.get(N)
        if r is None:
            probs.append(f"N={N}: missing search")
            f[N] = f[N - 1]
            continue
        if r["t"] != f[N - 1]:
            probs.append(f"N={N}: target {r['t']} != f(N-1) = {f[N-1]}")
        if r["v"] == "FOUND":
            if r["set"] is None or not ok_witness(r["set"], N, r["t"] + 1):
                probs.append(f"N={N}: FOUND witness fails trial division")
            f[N] = f[N - 1] + 1
        elif r["v"] == "NONE":
            if r["set"] is not None:
                probs.append(f"N={N}: NONE line carries a set")
            f[N] = f[N - 1]
        else:
            probs.append(f"N={N}: bad verdict {r['v']!r}")
            f[N] = f[N - 1]
    extra = sorted(set(rows) - set(range(2, NMAX + 1)))
    if extra:
        probs.append(f"lines outside 2..{NMAX}: {extra[:5]}")
    return f, probs


def records(f):
    rec, best = [], 0
    for N in range(1, NMAX + 1):
        if f[N] > best:
            best = f[N]
            rec.append(N)
    return rec


def py_max(N):
    """Pure-Python exact f(N) for small N (simple maximum-clique recursion)."""
    good = [a for a in range(1, N + 1) if sqf(2 * a)]
    adj = {a: {b for b in good if b != a and sqf(a + b)} for a in good}
    best = 0

    def grow(size, cand):
        nonlocal best
        if size > best:
            best = size
        cand = list(cand)
        while cand:
            if size + len(cand) <= best:
                return
            v = cand.pop()
            grow(size + 1, [u for u in cand if u in adj[v]])
    grow(0, good)
    return best


def build(tmp):
    exe = Path(tmp) / "sqc_ford"
    subprocess.run(["gcc", "-O2", "-o", str(exe), str(HERE / "sqc_ford.c")], check=True)
    return exe


def run_one(exe, N, t):
    out = subprocess.run([str(exe), str(N), str(t)], capture_output=True, text=True, check=True)
    return out.stdout.rstrip("\n")


def main():
    args = sys.argv[1:]
    full = "--full" in args
    jobs = int(args[args.index("--jobs") + 1]) if "--jobs" in args else (os.cpu_count() or 1)
    rows = parse(open(HERE / "ford_searches_2_3000.txt"))
    fails = []

    f, probs = chain(rows)
    fails += probs
    rec = records(f)
    result = json.load(open(HERE / "RESULT.json"))
    a54 = result["claims"]["A392165"]
    if rec[:54] != a54[:54] or len(a54) < 54:
        fails.append("chain disagrees with promoted A392165(1..54)")
    if rec[54:] != EXPECTED_55_65:
        fails.append(f"A392165(55..) derived {rec[54:]} != {EXPECTED_55_65}")
    if f[NMAX] != 65:
        fails.append(f"f(3000) derived {f[NMAX]} != 65")
    print(f"chain: {len(rows)} searches, f(2000) = {f[2000]}, f(3000) = {f[NMAX]}, "
          f"A392165(55..65) = {' '.join(map(str, rec[54:]))}")

    # planted-failure controls: the checker must reject each of these
    if ok_witness([1, 3], 3, 2):
        fails.append("control: planted non-squarefree pair 1+3 accepted")
    N0 = rec[54]
    bad = {k: dict(v) for k, v in rows.items()}
    bad[N0]["set"] = bad[N0]["set"][:-2] + [bad[N0]["set"][-2] + 2, N0]
    if not chain(bad)[1]:
        fails.append("control: planted bad witness accepted")
    flip = {k: dict(v) for k, v in rows.items()}
    M = max(n for n in flip if flip[n]["v"] == "NONE")
    flip[M]["v"] = "FOUND"
    if not chain(flip)[1]:
        fails.append("control: planted flipped verdict accepted")
    print("controls: planted bad witness / flipped verdict / non-squarefree pair rejected")

    with tempfile.TemporaryDirectory() as tmp:
        exe = build(tmp)
        for N in range(2, 61):
            if sqf(2 * N):
                line = run_one(exe, N, f[N - 1])
                if line != rows[N]["line"]:
                    fails.append(f"C engine line differs at N={N}")
            if py_max(N) != f[N]:
                fails.append(f"Python max-clique f({N}) = {py_max(N)} != chain {f[N]}")
        print("C engine and pure-Python cross-check agree for N <= 60")
        todo = sorted(N for N, r in rows.items() if full or r["nodes"] <= FAST_NODE_LIMIT)
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            outs = list(ex.map(lambda N: (N, run_one(exe, N, rows[N]["t"])), todo))
        diff = [N for N, line in outs if line != rows[N]["line"]]
        if diff:
            fails.append(f"re-run differs from committed line at N = {diff[:10]}")
        print(f"re-ran {len(todo)} of {len(rows)} searches"
              f"{'' if full else f' (those with <= {FAST_NODE_LIMIT} nodes)'}: "
              f"{len(todo) - len(diff)} reproduced byte for byte")

    if fails:
        for x in fails:
            print("FAIL:", x)
        sys.exit(1)
    if full:
        print('"verified_ford_3000":true')
    else:
        print('"receipt_consistent_3000":true')
    print("all checks passed")


if __name__ == "__main__":
    main()

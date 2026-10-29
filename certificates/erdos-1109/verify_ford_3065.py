#!/usr/bin/env python3
"""Replay Ford's search for Erdos #1109 up to N = 3065: A392165(66) = 3065.

f(N) = A392164(N) = max |S|, S in {1..N}, every a+b (a = b allowed) squarefree.
A392165(k) = least N with f(N) >= k.

Inputs (read, never written):
  ford_searches_2_3000.txt     the 1,213 committed sqc_ford.c answers for N <= 3000
                               (contract erdos-1109-a392165-55-65)
  ford_searches_3001_3065.txt  29 new answers, same format, for every N in 3001..3065
                               with 2N squarefree: 28 NONE and FOUND at 3065 with a
                               66-element set
  g4_crosscheck_3001_3065.txt  a second engine (sqclique.c, this directory) on the same
                               29 N: "C 66 N nv nodes" (no 66-set with max N) for every
                               NONE and "R 66 3065 nv nodes set ..." at 3065. Static
                               record; it is checked for agreement, not re-run.
Each sqc line is "N <N> t <t> FOUND|NONE nodes <n> nv <v> [set ...]", the answer to
"is there S of size t+1 with max(S) = N?". Since f(N) <= f(N-1) + 1, chaining the
answers from f(1) = 1 derives f(N) for every N <= 3065 with no outside input.

default (fast): chain check, trial-division check of every witness (both engines),
  engine agreement on 3001..3065, agreement with the promoted A392165(1..54)
  (RESULT.json) and with A392165(55..65) of contract erdos-1109-a392165-55-65,
  planted-failure controls, a pure-Python cross-check of the C engine for N <= 60,
  and a byte-for-byte re-run of every committed search with at most 1,000,000 nodes.
  No 3001..3065 search is that cheap, so the fast profile does not certify the claim.
--new [--jobs K]: also re-runs the 29 searches for N in 3001..3065 (about 6e10 nodes)
  and requires each to be reproduced byte for byte. Certifies a(66) = 3065 given
  f(3000) = 65, which contract erdos-1109-a392165-55-65 certifies.
--full [--jobs K]: re-runs all 1,242 committed searches (2..3065) byte for byte.
A verified-search receipt, not a formal proof.
"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOLD = 3000
NMAX = 3065
EXPECTED_55_65 = [2071, 2141, 2193, 2287, 2355, 2427, 2455, 2627, 2729, 2741, 2993]
EXPECTED_66 = 3065
FAST_NODE_LIMIT = 1_000_000


def sqf(x):
    p = 2
    while p * p <= x:
        if x % (p * p) == 0:
            return False
        p += 1
    return True


def parse(lines, lo, hi, rows=None):
    rows = {} if rows is None else rows
    for line in lines:
        p = line.split()
        if len(p) < 9 or p[0] != "N":
            raise ValueError(f"malformed line: {line!r}")
        N = int(p[1])
        if not lo <= N <= hi:
            raise ValueError(f"N {N} outside {lo}..{hi}")
        if N in rows:
            raise ValueError(f"duplicate N {N}")
        rows[N] = {"t": int(p[3]), "v": p[4], "nodes": int(p[6]), "nv": int(p[8]),
                   "set": [int(x) for x in p[p.index("set") + 1:]] if "set" in p else None,
                   "line": line.rstrip("\n")}
    return rows


def parse_g4(lines):
    g = {}
    for line in lines:
        p = line.split()
        if len(p) < 5 or p[0] not in ("C", "R"):
            raise ValueError(f"malformed g4 line: {line!r}")
        N = int(p[2])
        if N in g:
            raise ValueError(f"duplicate g4 N {N}")
        g[N] = {"v": p[0], "k": int(p[1]), "nv": int(p[3]), "nodes": int(p[4]),
                "set": [int(x) for x in p[5:]] if p[0] == "R" else None}
    return g


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


def engines_agree(rows, g4):
    """Second engine must agree on every searched N in NOLD+1..NMAX."""
    probs = []
    new = sorted(N for N in rows if N > NOLD)
    if sorted(g4) != new:
        probs.append(f"g4 covers {len(g4)} N, sqc covers {len(new)} N in {NOLD+1}..{NMAX}")
    for N in new:
        r, q = rows[N], g4.get(N)
        if q is None:
            continue
        if q["k"] != r["t"] + 1:
            probs.append(f"g4 N={N}: size {q['k']} != t+1 = {r['t'] + 1}")
        if q["nv"] != r["nv"]:
            probs.append(f"g4 N={N}: nv {q['nv']} != sqc nv {r['nv']}")
        want = {"FOUND": "R", "NONE": "C"}.get(r["v"])
        if q["v"] != want:
            probs.append(f"g4 N={N}: verdict {q['v']} disagrees with sqc {r['v']}")
        if q["v"] == "R" and (q["set"] is None or not ok_witness(q["set"], N, q["k"])):
            probs.append(f"g4 N={N}: R set fails trial division")
        if q["v"] == "C" and q["set"]:
            probs.append(f"g4 N={N}: C line carries a set")
    return probs


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
    new = "--new" in args or full
    jobs = int(args[args.index("--jobs") + 1]) if "--jobs" in args else (os.cpu_count() or 1)
    rows = parse(open(HERE / "ford_searches_2_3000.txt"), 2, NOLD)
    n_old = len(rows)
    parse(open(HERE / "ford_searches_3001_3065.txt"), NOLD + 1, NMAX, rows)
    g4 = parse_g4(open(HERE / "g4_crosscheck_3001_3065.txt"))
    fails = []

    f, probs = chain(rows)
    fails += probs
    rec = records(f)
    result = json.load(open(HERE / "RESULT.json"))
    a54 = result["claims"]["A392165"]
    if rec[:54] != a54[:54] or len(a54) < 54:
        fails.append("chain disagrees with promoted A392165(1..54)")
    if rec[54:65] != EXPECTED_55_65:
        fails.append(f"A392165(55..65) derived {rec[54:65]} != {EXPECTED_55_65}")
    if rec[65:] != [EXPECTED_66]:
        fails.append(f"A392165(66..) derived {rec[65:]} != [{EXPECTED_66}]")
    if f[NOLD] != 65 or f[NMAX] != 66 or f[NMAX - 1] != 65:
        fails.append(f"f(3000), f(3064), f(3065) derived {f[NOLD]}, {f[NMAX-1]}, {f[NMAX]} != 65, 65, 66")
    fails += engines_agree(rows, g4)
    n_new = len(rows) - n_old
    n_none = sum(1 for N in rows if N > NOLD and rows[N]["v"] == "NONE")
    print(f"chain: {n_old} + {n_new} searches, f(3000) = {f[NOLD]}, f(3064) = {f[NMAX-1]}, "
          f"f(3065) = {f[NMAX]}, A392165(66) = {' '.join(map(str, rec[65:]))}")
    print(f"second engine: {sum(1 for q in g4.values() if q['v'] == 'C')} C (of {n_none} NONE) "
          f"+ {sum(1 for q in g4.values() if q['v'] == 'R')} R at 3065, nv equal on all {len(g4)}")

    # planted-failure controls: the checker must reject each of these
    if ok_witness([1, 3], 3, 2):
        fails.append("control: planted non-squarefree pair 1+3 accepted")
    bad = {k: dict(v) for k, v in rows.items()}
    bad[NMAX]["set"] = bad[NMAX]["set"][:-2] + [bad[NMAX]["set"][-2] + 2, NMAX]
    if not chain(bad)[1]:
        fails.append("control: planted bad witness at 3065 accepted")
    flip = {k: dict(v) for k, v in rows.items()}
    M = max(n for n in flip if flip[n]["v"] == "NONE")
    flip[M]["v"] = "FOUND"
    if not chain(flip)[1]:
        fails.append(f"control: planted flipped verdict at {M} accepted")
    drop = {k: v for k, v in rows.items() if k != M}
    if not chain(drop)[1]:
        fails.append(f"control: dropped search at {M} accepted")
    g4bad = {k: dict(v) for k, v in g4.items()}
    g4bad[M]["v"] = "R"
    g4bad[M]["set"] = list(g4[NMAX]["set"])
    if not engines_agree(rows, g4bad):
        fails.append(f"control: planted engine disagreement at {M} accepted")
    print(f"controls: planted bad witness / flipped verdict at {M} / dropped search / "
          f"engine disagreement / non-squarefree pair rejected")

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
        todo = sorted(N for N, r in rows.items()
                      if full or (new and N > NOLD) or r["nodes"] <= FAST_NODE_LIMIT)
        # longest first so the slow searches start early
        todo.sort(key=lambda N: -rows[N]["nodes"])
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            outs = list(ex.map(lambda N: (N, run_one(exe, N, rows[N]["t"])), todo))
        diff = sorted(N for N, line in outs if line != rows[N]["line"])
        if diff:
            fails.append(f"re-run differs from committed line at N = {diff[:10]}")
        done_new = sum(1 for N in todo if N > NOLD)
        print(f"re-ran {len(todo)} of {len(rows)} searches ({done_new} of {n_new} in 3001..3065)"
              f"{'' if new else f' (those with <= {FAST_NODE_LIMIT} nodes)'}: "
              f"{len(todo) - len(diff)} reproduced byte for byte")

    if fails:
        for x in fails:
            print("FAIL:", x)
        sys.exit(1)
    if full:
        print('"verified_ford_3065":true')
    elif new:
        print('"verified_ford_3001_3065":true')
    else:
        print('"receipt_consistent_3065":true')
    print("all checks passed")


if __name__ == "__main__":
    main()

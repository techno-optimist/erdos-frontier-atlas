#!/usr/bin/env python3
"""Verify the Erdős #864 certificate: A389182, sets with at most one repeated pairwise sum.

  python3 -I verify.py            # A389182(1..80), the published data (~15 s; needs cc)
  python3 -I verify.py --full     # every N in the receipt, the new ones included (see README)

A389182(N) is the largest A in {1..N} such that among the sums a + b (a <= b in A)
at most one value occurs more than once.  a(N) is a(N-1) or a(N-1) + 1, and a set
of size a(N-1) + 1 in {1..N} contains 1 and N (the property survives translation,
so otherwise a translate would lie in {1..N-1}).  So one search per N decides the
table: is there such a set of size a(N-1) + 1 containing 1 and N?

Checks, in order: (1) every witness by brute force alone -- a(N) distinct
integers in 1..N, all sums counted -- sharing no code with the searches, and the
receipt holds exactly one search per N, of size a(N-1) + 1, found iff the table
steps up; (2) the engine onesum.c re-decides every search, and its verdict, node
count and set must agree; (3) the Python reference re-decides the searches for
small N node for node; (4) onesum_naive.c, a second search sharing no code with
onesum.c (inner elements in decreasing order, no candidate lists, no symmetry
breaking), agrees on every verdict it replays; (5) cross-checks against OEIS and
against the externally reported values; (6) planted failures.  RESULT.json is
read, never written; the binaries live in a temporary directory.
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import one_exception as oe  # noqa: E402

# OEIS A389182 as of 2026-09-28: data a(1..80); the b-file (A. Ferudun, n = 1..100) ends at
# a(100) = 16, as recorded in the atlas gap map (row #864, 2026-07-18).
A389182_DATA = [1, 2, 3, 3, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 9, 9, 9, 9,
                9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12,
                12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 14,
                14, 14, 14, 14, 14, 14, 14, 14, 14, 14]
A389182_100 = 16
# Reported without a public copy (erdosproblemaday.com, per the atlas gap map, 2026-09-27):
# a(101..106) = 16, a(107..116) = 17, a(117..134) = 18, a(135..152) = 19, a(153) = 20.
REPORTED = {**{n: 16 for n in range(101, 107)}, **{n: 17 for n in range(107, 117)},
            **{n: 18 for n in range(117, 135)}, **{n: 19 for n in range(135, 153)}, 153: 20}
TOP_FAST = 80                 # the default replay: the published data
REF_FAST, REF_FULL = 45, 70   # Python reference: N <= these
NAIVE_FAST = 60               # onesum_naive.c: every N <= this, and with --full ...
NAIVE_FULL = 80               # ... every N <= this, plus the first new cell (N = 101)

FAILURES = []


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""),
          flush=True)
    if not ok:
        FAILURES.append(label)
    return ok


def run_c(exe, N, K):
    w = subprocess.run([str(exe), str(N), str(K)], capture_output=True, text=True,
                       check=True).stdout.split()
    if w[1:3] != [str(N), str(K)]:
        return None
    return [int(w[3]), w[0] == "found", [int(x) for x in w[5:]] if w[0] == "found" else None]


def run_ref(N, K):
    s = oe.Search(N, K)
    found = s.run()
    return [s.nodes, found, sorted(s.A) if found else None]


def job(kind, exe, N, K):
    """One replay unit, at module level so it runs in a worker process."""
    return run_ref(N, K) if kind == "ref" else run_c(exe, N, K)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    args = ap.parse_args()
    res = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    a = res["claims"]["A389182"]
    NMAX = len(a)
    wit = {int(n): s for n, s in res["witnesses"].items()}
    searches = [tuple(s) for s in res["searches"]]
    top = NMAX if args.full else min(NMAX, TOP_FAST)
    print(f"Erdős #864 — A389182(1..{NMAX})"
          + ("" if args.full else f"  (default replay: N <= {top})") + "\n")

    # 1 ---------------------------------------------------------------
    print("1. every witness, checked by brute force alone; the shape of the receipt")
    steps = [N for N in range(1, NMAX + 1) if a[N - 1] > (a[N - 2] if N > 1 else 0)]
    check(sorted(wit) == steps and all(len(wit[N]) == a[N - 1] and oe.is_valid(wit[N], N)
                                       for N in steps),
          f"at each of the {len(steps)} steps N the witness has a(N) elements in 1..N and at most "
          "one repeated sum")
    prev = [0] + a[:-1]
    check(all(0 <= a[i] - prev[i] <= 1 for i in range(NMAX))
          and [s[:2] for s in searches] == [(N, prev[N - 1] + 1) for N in range(1, NMAX + 1)]
          and all(s[3] == (a[s[0] - 1] == s[1]) for s in searches),
          "one search per N, of size a(N-1) + 1, found exactly where the table steps up",
          f"{len(searches)} searches")
    rec = {s[:2]: [s[2], s[3], wit[s[0]] if s[3] else None] for s in searches}

    cc = shutil.which("cc") or shutil.which("gcc")
    if not check(cc is not None, "a C compiler is available"):
        sys.exit(1)
    replay = [k for k in rec if k[0] <= top]
    ref_top = REF_FULL if args.full else REF_FAST
    ref_keys = [k for k in rec if k[0] <= ref_top]
    naive_keys = [k for k in rec if k[0] <= (NAIVE_FULL if args.full else NAIVE_FAST)
                  or (args.full and k[0] == 101)]
    with tempfile.TemporaryDirectory(prefix="erdos864-") as tmp:
        exe = pathlib.Path(tmp) / "onesum"
        naive = pathlib.Path(tmp) / "onesum_naive"
        subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "onesum.c")], check=True)
        subprocess.run([cc, "-O2", "-o", str(naive), str(HERE / "onesum_naive.c")], check=True)
        units = ([("c", str(exe)) + k for k in replay] + [("ref", "") + k for k in ref_keys]
                 + [("naive", str(naive)) + k for k in naive_keys])
        # longest first: node counts stand in for cost
        weight = {"c": 1, "ref": 40, "naive": 12}
        units.sort(key=lambda u: -weight[u[0]] * rec[u[2:]][0])
        with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as ex:
            outs = list(ex.map(job, *zip(*units)))
        got = {u[:1] + u[2:]: o for u, o in zip(units, outs)}

    # 2 ---------------------------------------------------------------
    print(f"\n2. the engine re-decides every search for N <= {top}")
    check(all(got[("c",) + k] == rec[k] for k in replay),
          f"verdict, node count and set agree on all {len(replay)} searches",
          f"{sum(rec[k][0] for k in replay)} nodes")

    # 3 ---------------------------------------------------------------
    print(f"\n3. the Python reference re-decides the searches for N <= {ref_top}, node for node")
    check(all(got[("ref",) + k] == rec[k] for k in ref_keys),
          f"all {len(ref_keys)} searches agree", f"{sum(rec[k][0] for k in ref_keys)} nodes")

    # 4 ---------------------------------------------------------------
    extra = [k for k in naive_keys if k[0] > NAIVE_FULL]
    print(f"\n4. onesum_naive.c agrees on every verdict for N <= "
          f"{NAIVE_FULL if args.full else NAIVE_FAST}" + (f" and N = {extra[0][0]}" if extra else ""))
    ok = all(got[("naive",) + k][1] == rec[k][1] for k in naive_keys)
    ok &= all(len(got[("naive",) + k][2]) == k[1] and oe.is_valid(got[("naive",) + k][2], k[0])
              for k in naive_keys if rec[k][1])
    check(ok, f"same verdict on all {len(naive_keys)} searches; its own sets pass the brute-force check")

    # 5 ---------------------------------------------------------------
    print("\n5. cross-checks")
    L = min(NMAX, len(A389182_DATA))
    check(a[:L] == A389182_DATA[:L], f"A389182(1..{L}) as published")
    if NMAX >= 100:
        check(a[99] == A389182_100, f"a(100) = {A389182_100}, the last line of the OEIS b-file")
    rep = [n for n in REPORTED if n <= NMAX]
    if rep:
        check(all(a[n - 1] == REPORTED[n] for n in rep),
              f"a({min(rep)}..{max(rep)}) agree with the externally reported values",
              "an unverified report, now replayed")

    # 6 ---------------------------------------------------------------
    print("\n6. planted failures must be refused")
    S = wit[steps[-1]]
    bad = [x for x in range(1, steps[-1] + 1) if x not in S and not oe.one_exception(S + [x])]
    check(bool(bad) and not oe.is_valid(S + [bad[0]], steps[-1]) and not oe.is_valid(S + [S[0]], steps[-1]),
          f"the last witness plus {bad[0] if bad else '?'} (a second repeated sum), or with an element "
          "doubled, is rejected")
    tamper = dict(rec)
    k0 = replay[-1]
    tamper[k0] = [rec[k0][0] + 1] + rec[k0][1:]
    check(any(got[("c",) + k] != tamper[k] for k in replay),
          "a receipt with one node count off by one disagrees with the engine")

    verdict = {"claim": {"A389182": a}, "replayed_through_N": top,
               "verified_published": not FAILURES,
               "verified": not FAILURES and args.full}
    print("\n" + json.dumps(verdict, separators=(",", ":")))
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s)")
        sys.exit(1)
    if args.full:
        # check-only verifier: the receipt was re-derived and compared, not rewritten
        print("receipt-checked: RESULT.json")
    print("\nall checks passed")


if __name__ == "__main__":
    main()

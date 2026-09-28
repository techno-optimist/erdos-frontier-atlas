#!/usr/bin/env python3
"""Verify the Erdős #357 certificate: sequences with distinct segment sums (A364132, A364153).

  python3 -I verify.py            # the published terms A364132(1..22), A364153(1..13) (~10 s; needs cc)
  python3 -I verify.py --full     # every term in the receipt, the new ones included, with the Python
                                  # reference pinned on the new searches it can afford (CPU-hours,
                                  # run in parallel by --jobs; see README)

A segment of (s_1, ..., s_n) is a run s_i + ... + s_j of consecutive terms.
A364132(n) is the least N such that {1..N} has an increasing n-sequence whose
segment sums are all distinct (mode "m"); A364153(n) is the same for sequences
in any order (mode "a").  For each n the receipt holds the two searches that
decide a(n): "none" with every term <= a(n) - 1, which refutes every smaller N
at once, and "found" with every term <= a(n), with its sequence.

Checks, in order: (1) every witness by brute force alone -- n terms, maximum
a(n), increasing in mode m, all n(n+1)/2 segment sums distinct -- sharing no
code with the searches; (2) the engine segsum.c re-decides every search, and
its verdict, node count and sequence must agree; (3) the Python reference
re-decides the searches for small n node for node, and with --full also the
new ones listed in REF_FULL; (4) segsum_naive.c, a second search sharing no
code with segsum.c (increasing sequences built from the largest term down; any
order without symmetry breaking), agrees on every verdict it replays;
(5) cross-checks against the OEIS data; (6) planted failures.  RESULT.json is
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
import segment_sums as ss  # noqa: E402

OEIS = {"m": "A364132", "a": "A364153"}
# OEIS data as of 2026-09-28 (A364132: a(14..22) by J. Wang, Jul 10 2023;
# A364153: a(10..13) by J. Wang, Jul 11 2023).  Everything past these is new.
PUBLISHED = {
    "m": [1, 2, 4, 5, 7, 10, 12, 13, 15, 18, 21, 24, 25, 29, 30, 33, 36, 38, 41, 47, 50, 52],
    "a": [1, 2, 3, 5, 6, 7, 9, 10, 12, 13, 14, 17, 18],
}
REF_FAST = {"m": 18, "a": 11}     # Python reference, default replay: n <= these
REF_FULL = {"m": 24, "a": 15}     # ... and with --full
NAIVE_FAST = {"m": 19, "a": 12}   # segsum_naive.c, default replay
NAIVE_FULL = {"m": 24, "a": 15}   # ... and with --full

FAILURES = []


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""),
          flush=True)
    if not ok:
        FAILURES.append(label)
    return ok


def run_c(exe, mode, n, N):
    w = subprocess.run([str(exe), mode, str(n), str(N)], capture_output=True, text=True,
                       check=True).stdout.split()
    if w[1:4] != [mode, str(n), str(N)]:
        return None
    return [int(w[4]), w[0] == "found", [int(x) for x in w[6:]] if w[0] == "found" else None]


def run_ref(mode, n, N):
    s = ss.Search(mode, n, N)
    found = s.run()
    return [s.nodes, found, list(s.seq) if found else None]


def job(kind, exe, mode, n, N):
    """One replay unit, at module level so it runs in a worker process."""
    return run_ref(mode, n, N) if kind == "ref" else run_c(exe, mode, n, N)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    args = ap.parse_args()
    res = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    terms = {m: res["claims"][OEIS[m]] for m in OEIS}
    wit = {m: {int(n): s for n, s in res["witnesses"][m].items()} for m in OEIS}
    searches = [tuple(s) for s in res["searches"]]
    top = {m: len(terms[m]) if args.full else len(PUBLISHED[m]) for m in OEIS}
    print(f"Erdős #357 — {OEIS['m']}(1..{len(terms['m'])}) and {OEIS['a']}(1..{len(terms['a'])})"
          + ("" if args.full else f"  (default replay: the published n <= {top['m']}, {top['a']})")
          + "\n")

    # 1 ---------------------------------------------------------------
    print("1. every witness, checked by brute force alone")
    for m in OEIS:
        K = len(terms[m])
        ok = sorted(wit[m]) == list(range(1, K + 1))
        ok &= all(len(wit[m][n]) == n and max(wit[m][n]) == terms[m][n - 1]
                  and ss.is_valid(m, wit[m][n], terms[m][n - 1]) for n in range(1, K + 1))
        ok &= all(terms[m][i] <= terms[m][i + 1] for i in range(K - 1))
        check(ok, f"{OEIS[m]}: the n-th witness has n terms, maximum a(n), "
                  + ("increases, " if m == "m" else "") + f"and distinct segment sums, n = 1..{K}")
    nb = res.get("next_bounds", {})
    for m in OEIS:
        b = nb.get(OEIS[m])
        if b:
            s = b["sequence"]
            check(b["n"] == len(terms[m]) + 1 and len(s) == b["n"] and max(s) == b["N"]
                  and b["N"] >= terms[m][-1] and ss.is_valid(m, s, b["N"]),
                  f"{OEIS[m]}({b['n']}) <= {b['N']}: the recorded {b['n']}-sequence passes the same check")
    want = []
    for m in OEIS:
        for n, a in enumerate(terms[m], 1):
            if a > 1:
                want.append((m, n, a - 1))
            want.append((m, n, a))
    check([s[:3] for s in searches] == want and all(s[4] == (s[2] == terms[s[0]][s[1] - 1])
                                                     for s in searches),
          "the receipt holds exactly the deciding searches: none at a(n) - 1, found at a(n)",
          f"{len(searches)} searches")
    rec = {s[:3]: [s[3], s[4], wit[s[0]][s[1]] if s[4] else None] for s in searches}

    cc = shutil.which("cc") or shutil.which("gcc")
    if not check(cc is not None, "a C compiler is available"):
        sys.exit(1)
    replay = [k for k in rec if k[1] <= top[k[0]]]
    ref_top = REF_FULL if args.full else REF_FAST
    naive_top = NAIVE_FULL if args.full else NAIVE_FAST
    ref_keys = [k for k in rec if k[1] <= ref_top[k[0]]]
    naive_keys = [k for k in rec if k[1] <= naive_top[k[0]]]
    with tempfile.TemporaryDirectory(prefix="erdos357-") as tmp:
        exe = pathlib.Path(tmp) / "segsum"
        naive = pathlib.Path(tmp) / "segsum_naive"
        subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "segsum.c")], check=True)
        subprocess.run([cc, "-O2", "-o", str(naive), str(HERE / "segsum_naive.c")], check=True)
        units = ([("c", str(exe)) + k for k in replay] + [("ref", "") + k for k in ref_keys]
                 + [("naive", str(naive)) + k for k in naive_keys])
        # longest first: node counts stand in for cost, the top-down search is ~15x bigger
        weight = {"c": 1, "ref": 40, "naive": 20}
        units.sort(key=lambda u: -weight[u[0]] * rec[u[2:]][0])
        with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as ex:
            outs = list(ex.map(job, *zip(*units)))
        got = {u[:1] + u[2:]: o for u, o in zip(units, outs)}

    # 2 ---------------------------------------------------------------
    print(f"\n2. the engine re-decides every search for n <= {top['m']} ({OEIS['m']}), "
          f"n <= {top['a']} ({OEIS['a']})")
    for m in OEIS:
        ks = [k for k in replay if k[0] == m]
        check(all(got[("c",) + k] == rec[k] for k in ks),
              f"{OEIS[m]}: verdict, node count and sequence agree on all {len(ks)} searches",
              f"{sum(rec[k][0] for k in ks)} nodes")

    # 3 ---------------------------------------------------------------
    print(f"\n3. the Python reference re-decides the searches for n <= {ref_top['m']} ({OEIS['m']}), "
          f"n <= {ref_top['a']} ({OEIS['a']}), node for node")
    for m in OEIS:
        ks = [k for k in ref_keys if k[0] == m]
        new = [k for k in ks if k[1] > len(PUBLISHED[m])]
        check(all(got[("ref",) + k] == rec[k] for k in ks),
              f"{OEIS[m]}: all {len(ks)} searches agree"
              + (f", {len(new)} of them beyond the OEIS data" if new else ""),
              f"{sum(rec[k][0] for k in ks)} nodes")

    # 4 ---------------------------------------------------------------
    print(f"\n4. segsum_naive.c agrees on every verdict for n <= {naive_top['m']} ({OEIS['m']}), "
          f"n <= {naive_top['a']} ({OEIS['a']})")
    for m in OEIS:
        ks = [k for k in naive_keys if k[0] == m]
        ok = all(got[("naive",) + k][1] == rec[k][1] for k in ks)
        ok &= all(len(got[("naive",) + k][2]) == k[1] and ss.is_valid(m, got[("naive",) + k][2], k[2])
                  for k in ks if rec[k][1])
        check(ok, f"{OEIS[m]}: same verdict on all {len(ks)} searches; its own sequences pass "
                  "the brute-force check")

    # 5 ---------------------------------------------------------------
    print("\n5. cross-checks against the OEIS data")
    for m in OEIS:
        P = PUBLISHED[m]
        check(terms[m][:len(P)] == P, f"{OEIS[m]}(1..{len(P)}) as published",
              f"new: a({len(P) + 1}..{len(terms[m])}) = {terms[m][len(P):]}")

    # 6 ---------------------------------------------------------------
    print("\n6. planted failures must be refused")
    s = wit["m"][len(terms["m"])]
    check(not ss.is_valid("m", s[:-1] + [s[-3] + s[-2]], s[-3] + s[-2])
          and not ss.is_valid("m", s[:-2] + [s[-1], s[-2]], s[-1]),
          "a last term equal to the sum of the two before it, or two terms swapped, is rejected")
    tamper = dict(rec)
    k0 = replay[-1]
    tamper[k0] = [rec[k0][0] + 1] + rec[k0][1:]
    check(any(got[("c",) + k] != tamper[k] for k in replay),
          "a receipt with one node count off by one disagrees with the engine")

    verdict = {"claim": {OEIS[m]: terms[m] for m in OEIS},
               "replayed_through_n": top,
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

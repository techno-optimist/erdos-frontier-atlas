#!/usr/bin/env python3
"""Verify the Erdős #962 certificate: OEIS A327909 for 1 <= n <= 1102.

  python3 -I verify.py            # a(1..400) by an exact scan of [1, 2*10^8]; ~20 s, needs cc
  python3 -I verify.py --full     # all of a(1..1102): chunked scan of [1, 4.2*10^10]
                                  # (~15 CPU-minutes, split over --jobs processes)

A327909(n) is the smallest start of a run of n or more consecutive integers
each having a prime factor greater than n.  The OEIS b-file ends at
a(999) = 22369305365; a(1000..1102) are new here.

Checks, in order: (1) every recorded run is checked by gcd alone -- each of its
integers has a prime factor above the class prime p (the largest prime <= n),
the integers just before and after it are p-smooth, and it is at least n long;
(2) the sequential engine runs.c rescans [1, X] and must reproduce every a(n)
and run length it reaches; (3) the chunked engine chunk.c rescans the same
range in pieces, merged by smooth_runs.merge_chunks, and must agree with it;
(4) the Python reference, a smallest-prime-factor sieve sharing no code with
the engines, must agree on [1, 10^6] for n <= 120; (5) cross-checks against
OEIS A327909 (data a(1..44) and the b-file's last term a(999)); (6) planted
failures.  With --full, (3) runs over the whole certified range.  RESULT.json
is read, never written; the binaries live in a temporary directory.
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import smooth_runs as sr  # noqa: E402

X_FAST = 200_000_000
N_FAST = 400
# OEIS A327909 as of 2026-09-27: data a(1..44), and the last b-file term a(999)
# (b-file by D. Spencer, terms 1..369 by T. Garrison), as recorded in the atlas.
A327909_DATA = [2, 5, 13, 19, 55, 65, 113, 151, 151, 226, 364, 406, 736, 736, 1057, 1057, 1409,
                1409, 2059, 2059, 2313, 2313, 2313, 2313, 2313, 2313, 2313, 6007, 6961, 6961,
                10305, 12013, 12013, 12013, 12013, 12013, 12026, 12026, 17501, 17501, 17501,
                17501, 20833, 20833]
A327909_999 = 22369305365

FAILURES = []


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""),
          flush=True)
    if not ok:
        FAILURES.append(label)
    return ok


def build(tmp):
    cc = shutil.which("cc") or shutil.which("gcc")
    if not check(cc is not None, "a C compiler is available"):
        sys.exit(1)
    exes = {}
    for name in ("runs", "chunk"):
        exes[name] = pathlib.Path(tmp) / name
        subprocess.run([cc, "-O2", "-o", str(exes[name]), str(HERE / f"{name}.c")], check=True)
    return exes


def sequential(exe, nmax, X):
    out = subprocess.run([str(exe), str(nmax), str(X)], capture_output=True, text=True,
                         check=True).stdout
    got = {}
    for line in out.splitlines():
        w = line.split()
        if w[0] == "A":
            got[int(w[1])] = (int(w[2]), None if w[3] == "open" else int(w[3]))
    return got


def chunked(exe, nmax, X, jobs, pieces=None):
    pieces = pieces or max(1, jobs)
    step = -(-X // pieces)
    bounds = [(1 + i * step, min(X, (i + 1) * step)) for i in range(pieces) if 1 + i * step <= X]
    run = lambda b: subprocess.run([str(exe), str(b[0]), str(b[1]), str(nmax)],
                                   capture_output=True, text=True, check=True).stdout
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
        texts = list(ex.map(run, bounds))
    return sr.merge_chunks(texts, nmax, X), len(bounds)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    args = ap.parse_args()
    res = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    terms = {int(n): (v["a"], v["run"]) for n, v in res["terms"].items()}
    nmax, X_full = max(terms), res["scan_limit"]
    print(f"Erdős #962 — A327909(1..{nmax})"
          + ("" if args.full else f"  (default replay: exhaustive for n <= {N_FAST})") + "\n")

    # 1 ---------------------------------------------------------------
    print("1. every recorded run, checked by gcd alone")
    ok = sorted(terms) == list(range(1, nmax + 1)) and terms[1] == (2, None)
    triples = {}
    for n in range(2, nmax + 1):
        a, run = terms[n]
        ok &= run is not None and run >= n and a + run - 1 <= X_full
        triples.setdefault((sr.class_prime(n), a, run), []).append(n)
    ok &= all(sr.run_is_gap(a, run, p) for (p, a, run) in triples)
    check(ok, f"each a(n) starts a maximal run of length >= n between p-smooth integers, "
              f"n = 2..{nmax}", f"{len(triples)} distinct runs")
    check(all(terms[n][0] <= terms[n + 1][0] for n in range(1, nmax)),
          "a(n) is nondecreasing, as the definition forces")

    # 2, 3 ------------------------------------------------------------
    X = X_full if args.full else X_FAST
    with tempfile.TemporaryDirectory(prefix="erdos962-") as tmp:
        exes = build(tmp)
        print(f"\n2. the sequential engine rescans [1, {X_FAST}]")
        seq = sequential(exes["runs"], nmax, X_FAST)
        reach = max(n for n in seq if all(k in seq for k in range(1, n + 1)))
        check(reach >= N_FAST and all(seq[n] == terms[n] for n in range(1, reach + 1)),
              f"a(1..{reach}) and their run lengths equal the receipt")
        print(f"\n3. the chunked engine rescans [1, {X}]"
              + (" (the whole certified range)" if args.full else ""))
        mer, pieces = chunked(exes["chunk"], nmax, X, args.jobs, None if args.full else 3)
        check(all(mer.get(n) == seq[n] for n in range(2, reach + 1)),
              f"merged over {pieces} chunks, it agrees with the sequential engine on n = 2..{reach}")
        top = max(n for n in mer if all(k in mer for k in range(2, n + 1)))
        check(all(mer[n] == terms[n] for n in range(2, top + 1)),
              f"a(2..{top}) and their run lengths equal the receipt")
        seam, _ = chunked(exes["chunk"], nmax, 20_000_000, 2, 7)
        closed = [n for n in seam if seam[n][1] is not None]
        seam_ok = len(closed) >= 200 and all(seam[n] == seq[n] for n in closed)

    # 4 ---------------------------------------------------------------
    print("\n4. the Python reference (smallest-prime-factor sieve) on [1, 10^6]")
    ref = sr.a_reference(10 ** 6, 120)
    check(len(ref) == 120 and all(ref[n] == terms[n][0] for n in ref),
          "a(1..120) agree with the receipt", "no code shared with the engines")

    # 5 ---------------------------------------------------------------
    print("\n5. cross-checks against OEIS A327909")
    check([terms[n][0] for n in range(1, 45)] == A327909_DATA, "a(1..44) equal the OEIS data")
    check(terms[999][0] == A327909_999, "a(999) equals the last term of the OEIS b-file",
          f"{A327909_999}")

    # 6 ---------------------------------------------------------------
    print("\n6. planted failures must be refused")
    a1000, run1000 = terms[1000]
    check(not sr.run_is_gap(a1000 - 1, run1000 + 1, 997) and not sr.run_is_gap(a1000, run1000 + 1, 997)
          and not sr.run_is_gap(a1000 + 1, run1000 - 1, 997),
          "the a(1000) run shifted back by one, claimed one longer, or started one late is rejected")
    check(seam_ok, "cutting [1, 2*10^7] into 7 chunks changes no merged value", f"{len(closed)} runs")
    check(seq[N_FAST][0] != terms[N_FAST][0] - 1,
          f"a receipt claiming a({N_FAST}) one smaller disagrees with the engine")

    replayed = top if args.full else reach
    verdict = {"claim": f"A327909(1..{nmax})", "replayed_through": replayed,
               "verified_1_400": not FAILURES and reach >= N_FAST,
               "verified": not FAILURES and args.full and top == nmax}
    print("\n" + json.dumps(verdict, separators=(",", ":")))
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s)")
        sys.exit(1)
    if args.full:
        if top != nmax:
            print(f"\nFAILED: the full scan reached only n = {top}")
            sys.exit(1)
        # check-only verifier: the receipt was re-derived and compared, not rewritten
        print("receipt-checked: RESULT.json")
    print("\nall checks passed")


if __name__ == "__main__":
    main()

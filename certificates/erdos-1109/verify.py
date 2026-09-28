#!/usr/bin/env python3
"""Verify the Erdős #1109 certificate: the records of OEIS A392164 (= A392165).

  python3 -I verify.py            # re-decide every N <= 1103: the 39 published records (~10 s; needs cc)
  python3 -I verify.py --full     # re-decide every N up to the receipt's limit: the new records too
                                  # (~55 CPU-minutes, split over --jobs processes)

f(N) = A392164(N) is the size of the largest S in {1..N} such that every
element of S + S (a + a included) is squarefree; A392165(k) is the least N
with f(N) >= k.  OEIS lists A392165(1..39), up to 1103.

Checks, in order: (1) every record set in RESULT.json is checked by trial
division alone -- k distinct integers, the largest being N, every a + b
squarefree -- sharing no code with the searches; (2) the engine sqclique.c
re-decides every candidate N (2N squarefree) up to the replay limit, and its
verdict, graph size, node count and record set must equal the receipt; (3) the
Python reference re-decides every candidate N <= 400 node for node; (4)
cross-checks against OEIS A392165 (a(1..39)) and the A392164 data; (5)
planted failures.  RESULT.json is read, never written; the binary lives in a
temporary directory.
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
import sqfree_sums as ss  # noqa: E402

N_FAST = 1103
N_REF = 400
# OEIS as of 2026-09-28: A392165(1..39), and the first 98 terms of A392164 (data section).
A392165_OEIS = [1, 5, 19, 23, 37, 41, 59, 87, 101, 105, 113, 131, 151, 159, 167, 195, 203, 239,
                259, 303, 307, 403, 451, 499, 517, 553, 573, 609, 645, 701, 719, 787, 807, 827,
                889, 1003, 1055, 1067, 1103]
A392164_DATA = [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4,
                4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
                7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]

FAILURES = []


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""),
          flush=True)
    if not ok:
        FAILURES.append(label)
    return ok


def engine(exe, nmax, n0=1, f0=0):
    argv = [str(exe), str(nmax)] + ([str(n0), str(f0)] if n0 > 1 else [])
    out = subprocess.run(argv, capture_output=True, text=True, check=True).stdout
    rows = []
    for line in out.splitlines():
        w = line.split()
        if w[0] == "R":
            rows.append([int(w[2]), int(w[1]), int(w[3]), int(w[4]), sorted(int(x) for x in w[5:])])
        elif w[0] == "C":
            rows.append([int(w[2]), int(w[1]), int(w[3]), int(w[4]), None])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--rds", action="store_true",
                    help="also replay the independent Russian-doll cross-check (rds_crosscheck.txt)")
    args = ap.parse_args()
    res = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    nmax = res["nmax"]
    cands = [[N, k, nv, nodes, None] for N, k, nv, nodes, _ in res["candidates"]]
    recs = {int(k): v for k, v in res["records"].items()}
    for N, k, nv, nodes, is_rec in res["candidates"]:
        if is_rec:
            cands[[c[0] for c in cands].index(N)][4] = recs[k]["set"]
    K = max(recs)
    print(f"Erdős #1109 — records of A392164 for N <= {nmax}: A392165(1..{K})"
          + ("" if args.full else f"  (default replay: every N <= {N_FAST})") + "\n")

    # 1 ---------------------------------------------------------------
    print("1. every record set, checked by trial division alone")
    ok = sorted(recs) == list(range(1, K + 1))
    for k, r in recs.items():
        S = r["set"]
        ok &= len(S) == k and max(S) == r["N"] and ss.sumset_squarefree(S)
    ok &= all(recs[k]["N"] < recs[k + 1]["N"] for k in range(1, K))
    check(ok, f"the k-th record set has k elements, maximum A392165(k), and a squarefree sumset, "
              f"k = 1..{K}")

    # 2 ---------------------------------------------------------------
    limit = nmax if args.full else N_FAST
    print(f"\n2. the engine re-decides every candidate N <= {limit}")
    cc = shutil.which("cc") or shutil.which("gcc")
    if not check(cc is not None, "a C compiler is available"):
        sys.exit(1)
    want = [c for c in cands if c[0] <= limit]
    # split into ranges of about equal work; each starts from the receipt's own f(N0 - 1), so
    # agreement everywhere also shows the receipt's f progression is self-consistent
    jobs = max(1, args.jobs if args.full else 1)
    total, bounds, acc, start = sum(c[3] for c in want), [], 0, 1
    for c in want:
        acc += c[3]
        if acc >= total * (len(bounds) + 1) / jobs and len(bounds) < jobs - 1:
            bounds.append((start, c[0]))
            start = c[0] + 1
    bounds.append((start, limit))
    rec_N = sorted(r["N"] for r in recs.values())
    with tempfile.TemporaryDirectory(prefix="erdos1109-") as tmp:
        exe = pathlib.Path(tmp) / "sqclique"
        subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "sqclique.c")], check=True)
        run = lambda b: engine(exe, b[1], b[0], sum(1 for x in rec_N if x < b[0]))
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            got = [row for part in ex.map(run, bounds) for row in part]
    check(got == want, f"verdict, |V_N|, node count and record set agree on all {len(want)} "
                       f"candidates", f"{total} nodes, {len(bounds)} range(s)")

    # 3 ---------------------------------------------------------------
    print(f"\n3. the Python reference re-decides every candidate N <= {N_REF}, node for node")
    ref = [[N, k, nv, nodes, w] for k, N, nv, nodes, w in ss.records(N_REF)]
    check(ref == [c for c in cands if c[0] <= N_REF], f"all {len(ref)} candidates agree")

    # 4 ---------------------------------------------------------------
    print("\n4. cross-checks against OEIS")
    rec_N = [recs[k]["N"] for k in range(1, K + 1)]
    check(rec_N[:39] == A392165_OEIS, "A392165(1..39) equal the published terms")
    f = lambda n: sum(1 for x in rec_N if x <= n)
    check([f(n) for n in range(1, len(A392164_DATA) + 1)] == A392164_DATA,
          f"the records give A392164(1..{len(A392164_DATA)}) as published")

    # 5 ---------------------------------------------------------------
    print("\n5. planted failures must be refused")
    S = recs[40]["set"] if 40 in recs else recs[K]["set"]
    bad = sorted(S[:-1] + [S[-1] + 2])
    check(not ss.sumset_squarefree(bad),
          "moving the largest element of a record set by 2 (into the other class mod 4) is rejected")
    check(not ss.sumset_squarefree([S[0] + 1] + S[1:]),
          "replacing its smallest element by an even number is rejected (4 divides 2a)")
    tamper = [c for c in cands if c[0] <= N_REF]
    tamper[-1] = tamper[-1][:3] + [tamper[-1][3] + 1] + tamper[-1][4:]
    check(tamper != ref, "a receipt with one node count off by one disagrees with the reference")

    if args.rds:
        log = [line.split() for line in (HERE / "rds_crosscheck.txt").read_text().splitlines()
               if line.strip() and not line.startswith("#")]
        lo, hi = int(log[0][0]), int(log[-1][0])
        print(f"\nR. the independent Russian-doll search re-computes omega(G_N) for N in [{lo}, {hi}]")
        rec_set = {recs[k]["N"] for k in recs}
        f_at = lambda n: sum(1 for x in rec_set if x <= n)
        # node-balanced ranges, each started from the receipt's f(N0 - 1)
        jobs, total = max(1, args.jobs), sum(int(r[3]) for r in log)
        cuts, acc, start = [], 0, lo
        for r in log:
            acc += int(r[3])
            if acc >= total * (len(cuts) + 1) / jobs and len(cuts) < jobs - 1 and int(r[0]) < hi:
                cuts.append((start, int(r[0])))
                start = int(r[0]) + 1
        cuts.append((start, hi))
        with tempfile.TemporaryDirectory(prefix="erdos1109-") as tmp:
            exe = pathlib.Path(tmp) / "rds"
            subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "rds.c")], check=True)
            run = lambda b: subprocess.run([str(exe), str(b[0]), str(b[1]), str(f_at(b[0] - 1))],
                                           capture_output=True, text=True, check=True).stdout
            with ThreadPoolExecutor(max_workers=jobs) as ex:
                out = "".join(ex.map(run, cuts))
        rows = [line.split() for line in out.splitlines()]
        check(rows == log, f"omega(G_N) and node counts equal rds_crosscheck.txt for all {len(rows)} "
                           f"candidates", f"{sum(int(r[3]) for r in rows)} nodes")
        ok = all(int(r[1]) + 1 <= f_at(int(r[0])) for r in rows)
        ok &= all((int(r[0]) in rec_set) == (int(r[1]) + 1 > f_at(int(r[0]) - 1)) for r in rows)
        check(ok, "a different algorithm gives the same records: N is a record exactly when "
                  "omega(G_N) + 1 > f(N - 1), and never omega(G_N) + 1 > f(N)",
              f"records in range: {sorted(x for x in rec_set if lo <= x <= hi)}")

    verdict = {"claim": f"A392165(1..{K}); A392164(N) for N <= {nmax}",
               "replayed_through": limit,
               "verified_1103": not FAILURES,
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

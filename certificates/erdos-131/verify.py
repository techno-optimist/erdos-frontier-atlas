#!/usr/bin/env python3
"""Verify the Erdős #131 certificate: thresholds of OEIS A068063 (nondividing sets).

  python3 -I verify.py            # re-decide every search for k <= 8: the published T_1..T_8 (~15 s; needs cc)
  python3 -I verify.py --full     # every search in the receipt (k <= 10: T_9 = 107, T_10 = 155, new),
                                  # and the Python reference on the new k = 9 searches (~40 CPU-minutes)

A068063(n) is the largest nondividing subset of {1..n}: no element divides the
sum of any nonempty subset of the others.  T_k is the least n with a
nondividing k-subset, so A068063(n) = max{k : T_k <= n}.  OEIS lists
A068063(0..100); its data give T_1..T_8 = 1, 3, 7, 10, 21, 31, 43, 65, and its
b-file ends at a(100) = 8.

Checks, in order: (1) every threshold set in RESULT.json is checked by brute
force alone -- k distinct integers with maximum T_k, and every nonempty subset
sum of the others is tested against each element -- sharing no code with the
search; (2) the engine nondiv.c re-decides every (k, N) search in the receipt
(k <= 8 by default), and its verdict, node count and set must agree; (3) the
Python reference re-decides every search for k <= 8 node for node, and with
--full also the k = 9 searches for N = 101..T_9, the range the OEIS b-file
does not cover; (4) cross-checks against OEIS A068063; (5) planted failures.  RESULT.json is read, never written; the
binary lives in a temporary directory.
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
import nondividing as nd  # noqa: E402

K_FAST = 8
K_REF = 8
N_BFILE = 100      # the OEIS b-file ends at a(100)
# OEIS A068063 as of 2026-09-28: data a(0..86); the b-file (C. Sievers) ends at a(100) = 8.
A068063_DATA = [0, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5,
                5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
                7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
                8, 8, 8]
A068063_100 = 8

FAILURES = []


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""),
          flush=True)
    if not ok:
        FAILURES.append(label)
    return ok


def pin9(T, N):
    """The Python reference on one k = 9 search (module level, so it runs in a worker process)."""
    srch = nd.Search(9, T)
    found = srch.run(N)
    return [9, N, srch.nodes, sorted(srch.S, reverse=True) if found else None]


def engine(exe, kmax, nmax):
    out = subprocess.run([str(exe), str(kmax), str(nmax)], capture_output=True, text=True,
                         check=True).stdout
    rows = []
    for line in out.splitlines():
        w = line.split()
        if w[0] == "T":
            rows.append([int(w[1]), int(w[2]), int(w[3]), sorted((int(x) for x in w[4:]), reverse=True)])
        elif w[0] == "C":
            rows.append([int(w[1]), int(w[2]), int(w[3]), None])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    args = ap.parse_args()
    res = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    th = {int(k): v for k, v in res["thresholds"].items()}
    searches = [[k, N, nodes, (th[k]["set"] if found else None)] for k, N, nodes, found in res["searches"]]
    K = max(th)
    kmax = K if args.full else min(K, K_FAST)
    print(f"Erdős #131 — thresholds T_1..T_{K} of A068063"
          + ("" if args.full else f"  (default replay: k <= {kmax})") + "\n")

    # 1 ---------------------------------------------------------------
    print("1. every threshold set, checked by brute force alone")
    ok = sorted(th) == list(range(1, K + 1))
    for k, t in th.items():
        ok &= len(t["set"]) == k and max(t["set"]) == t["N"] and nd.is_nondividing(t["set"])
    ok &= all(th[k]["N"] < th[k + 1]["N"] for k in range(1, K))
    check(ok, f"the k-th set has k elements, maximum T_k, and is nondividing, k = 1..{K}")

    # 2 ---------------------------------------------------------------
    print(f"\n2. the engine re-decides every search for k <= {kmax}")
    cc = shutil.which("cc") or shutil.which("gcc")
    if not check(cc is not None, "a C compiler is available"):
        sys.exit(1)
    nmax = max(N for k, N, _, _ in searches if k <= kmax)
    with tempfile.TemporaryDirectory(prefix="erdos131-") as tmp:
        exe = pathlib.Path(tmp) / "nondiv"
        subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "nondiv.c")], check=True)
        got = engine(exe, kmax, nmax)
    want = [s for s in searches if s[0] <= kmax]
    check(got == want, f"verdict, node count and set agree on all {len(want)} searches",
          f"{sum(s[2] for s in want)} nodes")

    # 3 ---------------------------------------------------------------
    print(f"\n3. the Python reference re-decides every search for k <= {K_REF}, node for node"
          + (" (and the new k = 9 range)" if args.full else ""))
    out, per = nd.thresholds(K_REF, th[K_REF]["N"])
    by_k = {k: S for k, N, nodes, S in out}
    ref = [[k, N, nodes, (by_k[k] if found else None)] for k, N, nodes, found in per]
    check(ref == [s for s in searches if s[0] <= K_REF], f"all {len(ref)} searches agree")
    if args.full and 9 in th:
        T = [0] + [th[k]["N"] for k in range(1, 9)]
        rows = [s for s in searches if s[0] == 9 and s[1] > N_BFILE]
        with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as ex:
            got9 = list(ex.map(pin9, [T] * len(rows), [r[1] for r in rows]))
        check(got9 == rows, f"the k = 9 searches for N = {N_BFILE + 1}..{th[9]['N']}, beyond the "
                            f"b-file, agree node for node", f"{sum(r[2] for r in rows)} nodes")

    # 4 ---------------------------------------------------------------
    print("\n4. cross-checks against OEIS A068063")
    T_data = [min(n for n, v in enumerate(A068063_DATA) if v >= k) for k in range(1, 9)]
    check([th[k]["N"] for k in range(1, 9)] == T_data, "T_1..T_8 are where the OEIS data a(0..86) step up",
          f"{T_data}")
    check(th[9]["N"] > 100 and sum(1 for k in th if th[k]["N"] <= 100) == A068063_100,
          "T_9 > 100, so a(100) = 8 as the b-file says")

    # 5 ---------------------------------------------------------------
    print("\n5. planted failures must be refused")
    S = th[9]["set"]
    check(not nd.is_nondividing(S + [S[-1] // 2]) and not nd.is_nondividing([2 * S[-1]] + S),
          "adding half of the smallest element, or twice it, is rejected")
    tamper = [list(s) for s in searches if s[0] <= K_REF]
    tamper[-1][2] += 1
    check(tamper != ref, "a receipt with one node count off by one disagrees with the reference")

    verdict = {"claim": f"A068063 thresholds T_1..T_{K} = {[th[k]['N'] for k in range(1, K + 1)]}",
               "replayed_through_k": kmax,
               "verified_t8": not FAILURES and kmax >= 8,
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

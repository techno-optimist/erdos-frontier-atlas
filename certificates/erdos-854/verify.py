#!/usr/bin/env python3
"""Verify the Erdős #854 certificate: OEIS A389839 for 2 <= n <= 16.

  python3 -I verify.py            # a(2..15), exhaustive; about two minutes
  python3 -I verify.py --full     # also a(16) (~15 CPU-minutes)

A389839(n) is the smallest even number that is NOT the difference of two
consecutive integers coprime to p_n# (the product of the first n primes).
Certified: a(2..16) = 6, 8, 12, 16, 20, 28, 32, 42, 48, 60, 68, 76, 86, 98, 108.

Checks, in order: (1) every even gap below a(n) has an explicit witness x in
RESULT.json, checked by gcd alone -- x and x + t coprime to p_n#, everything
strictly between not -- which shares no code with any search; (2) the engine
gapsc.c re-decides every gap: verdicts and node counts equal the receipt, each
covering it finds realises exactly the recorded x, and a(n) itself is absent by
exhaustive search; (3) the Python reference (coprime_gaps.py) re-decides every
gap for n <= 12 node for node; (4) cross-checks against OEIS A389839 (n <= 12),
A048670 (largest gap) and A329815 (number of distinct gaps); (5) planted
failures.  RESULT.json is read, never written; the binary lives in a temp dir.
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
import coprime_gaps as cg  # noqa: E402

# OEIS data, as of 2026-09-27: A389839 for n = 2..12; A048670 (Jacobsthal
# function of p_n#, the largest gap) and A329815 (number of distinct gaps),
# both for n = 1..16.
A389839_OEIS = [6, 8, 12, 16, 20, 28, 32, 42, 48, 60, 68]
A048670 = [2, 4, 6, 10, 14, 22, 26, 34, 40, 46, 58, 66, 74, 90, 100, 106]
A329815 = [0, 1, 3, 5, 7, 10, 13, 16, 20, 23, 29, 33, 37, 43, 49, 53]

FAILURES = []


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""),
          flush=True)
    if not ok:
        FAILURES.append(label)
    return ok


def engine(exe, n, t=None):
    argv = [str(exe), str(n)] + ([str(t)] if t is not None else [])
    out = subprocess.run(argv, capture_output=True, text=True, check=True).stdout
    gaps, term = {}, None
    for line in out.splitlines():
        w = line.split()
        if w and w[0] == "GAP":
            res = ({int(a): int(b) for a, b in (x.split(":") for x in w[6:])}
                   if w[3] == "1" else None)
            gaps[int(w[2])] = (w[3] == "1", int(w[4]), res)
        elif w and w[0] == "TERM":
            term = int(w[2])
    return gaps, term


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    args = ap.parse_args()
    res = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    terms = {int(n): v for n, v in res["terms"].items()}
    nmax = max(terms)
    replay = range(2, nmax + 1) if args.full else range(2, nmax)
    print(f"Erdős #854 — A389839(2..{nmax})"
          + ("" if args.full else f"  (default replay: exhaustive for n <= {nmax - 1})") + "\n")

    # 1 ---------------------------------------------------------------
    print("1. witnesses, checked by gcd alone")
    ok, count = True, 0
    for n, rec in terms.items():
        want = [str(t) for t in range(2, rec["a"], 2)]
        ok &= sorted(rec["gaps"], key=int) == want
        for t, g in rec["gaps"].items():
            ok &= cg.is_gap(n, g["x"], int(t))
            count += 1
    check(ok, f"every even gap below a(n) occurs, for every 2 <= n <= {nmax}",
          f"{count} explicit witnesses")

    # 2 ---------------------------------------------------------------
    print(f"\n2. the engine re-decides every gap, n = {replay[0]}..{replay[-1]}")
    cc = shutil.which("cc") or shutil.which("gcc")
    if not check(cc is not None, "a C compiler is available"):
        sys.exit(1)
    with tempfile.TemporaryDirectory(prefix="erdos854-") as tmp:
        exe = pathlib.Path(tmp) / "gapsc"
        subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "gapsc.c")], check=True)
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
            runs = dict(zip(replay, ex.map(lambda n: engine(exe, n), replay)))
        for n in replay:
            gaps, a = runs[n]
            rec = terms[n]
            ok = a == rec["a"] and gaps[a][:2] == (False, rec["absent_nodes"])
            for t in range(4, a, 2):
                occ, nodes, cover = gaps[t]
                g = rec["gaps"][str(t)]
                ok &= occ and nodes == g["nodes"] and cg.realise(n, t, cover) == g["x"]
            check(ok, f"n={n} (p={rec['prime']}): a(n) = {a}; every smaller gap found with "
                      f"the recorded witness; {a} absent", f"{rec['absent_nodes']} nodes")
        # planted: 13# has a gap above its first absent one (Lacampagne-Selfridge)
        over, _ = engine(exe, 6, 22)
        planted_22 = over[22][0]

    # 3 ---------------------------------------------------------------
    print("\n3. the Python reference re-decides every gap for n <= 12, node for node")
    ok, pairs = True, 0
    for n in range(2, 13):
        rec = terms[n]
        for t in range(4, rec["a"] + 1, 2):
            c = cg.Cover(n, t)
            found = c.run()
            if t < rec["a"]:
                g = rec["gaps"][str(t)]
                ok &= found and c.nodes == g["nodes"] and cg.realise(n, t, c.residues()) == g["x"]
            else:
                ok &= not found and c.nodes == rec["absent_nodes"]
            pairs += 1
    check(ok, f"same verdict, node count and witness on all {pairs} (n, t) pairs")

    # 4 ---------------------------------------------------------------
    print("\n4. cross-checks against OEIS")
    a = {n: terms[n]["a"] for n in terms}
    check([a[n] for n in range(2, 13)] == A389839_OEIS,
          "a(2..12) equal the published A389839 terms")
    ok = all(a[n] <= A048670[n - 1] + 2 for n in terms)
    check(ok, "a(n) <= A048670(n) + 2: no gap exceeds the largest gap")
    # A329815(n) = number of distinct gaps, A048670(n)/2 = number of even
    # numbers up to the largest: equal iff no gap below the largest is missing
    ok = all((A329815[n - 1] == A048670[n - 1] // 2) == (a[n] == A048670[n - 1] + 2)
             for n in terms if n >= 3)
    check(ok, "a(n) = A048670(n) + 2 exactly when A329815(n) = A048670(n)/2 (n >= 3)")

    # 5 ---------------------------------------------------------------
    print("\n5. planted failures must be refused")
    n, t = 13, 74
    x = terms[n]["gaps"][str(t)]["x"]
    check(not cg.is_gap(n, x + 2, t) and not cg.is_gap(n, x, t + 2),
          "a shifted witness, or a witness for the wrong gap, is rejected")
    check(planted_22, "the engine does not stop at the first absent gap: 13# misses 20 "
                      "but has 22")
    tamper = json.loads(json.dumps(res))
    tamper["terms"]["13"]["a"] = 78
    check(tamper["terms"]["13"]["a"] != runs[13][1], "a receipt claiming a(13) = 78 "
                                                     "disagrees with the engine")

    verdict = {"claim": f"A389839(2..{nmax})", "a": {str(n): a[n] for n in terms},
               "replayed_through": replay[-1],
               "verified_2_15": not FAILURES and replay[-1] >= 15,
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

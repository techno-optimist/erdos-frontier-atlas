#!/usr/bin/env python3
"""Verify the second extension of the Erdős #962 certificate: OEIS A327909 for 1 <= n <= 1300.

  python3 -I verify_ford_1300.py            # receipt checks, gcd witnesses, engines on [1, 2*10^8] (~1 min);
                                            # checks the receipt, does NOT certify minimality of a(1201..1300)
  python3 -I verify_ford_1300.py --full     # also rescans [1, 10^11] with chunk.c and certifies a(1..1300)
                                            # (~20 CPU-minutes, split over --jobs processes; 173 s wall with --jobs 8)
  python3 -I verify_ford_1300.py --full --runs   # also re-runs runs.c NMAX 1300 over [1, 10^11]
                                                 # (~17 min, single core) and compares it with runs_ford_1300.txt

This file extends the frozen certificate (RESULT.json, a(1..1102), contract
erdos-962-a327909-1-1102) and the first extension (RESULT_ford_1200.json, a(1..1200),
contract erdos-962-a327909-1103-1200) without touching either.  RESULT_ford_1300.json was
written by the certificate's own emit_result.py (--nmax 1300 --limit 100000000000);
runs_ford_1300.txt is the output of runs.c (NMAX 1300, X = 100000000000), the second engine.

Checks: (1) the first 1102 entries of RESULT_ford_1300.json equal RESULT.json exactly and
the first 1200 equal RESULT_ford_1200.json exactly;
(2) every recorded run is checked by gcd alone (each integer has a prime factor above the
class prime p, the neighbours are p-smooth, the run is >= n long and ends inside the scan),
and a(n) is nondecreasing; (3) the committed runs.c output equals the receipt for every
n <= 1300; (4) both engines rescan [1, 2*10^8] (with --full: chunk.c rescans [1, 10^11])
and must reproduce the receipt; (5) OEIS cross-checks (data a(1..44), b-file a(999));
(6) planted failures must be refused.  Nothing is written.
"""
import argparse
import json
import os
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import smooth_runs as sr  # noqa: E402
import verify as base  # noqa: E402  (frozen verifier: reuse its engine drivers and OEIS constants)

NMAX = 1300
FAILURES = []


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""), flush=True)
    if not ok:
        FAILURES.append(label)
    return ok


def load_terms(path):
    res = json.loads(path.read_text(encoding="utf-8"))
    return res, {int(n): (v["a"], v["run"], v["class_prime"]) for n, v in res["terms"].items()}


def prefix_equal(ext, frozen):
    return all(ext.get(n) == frozen[n] for n in frozen)


def runs_ok(terms, X):
    """The gcd witness check over all distinct runs; returns (ok, number of runs)."""
    ok = sorted(terms) == list(range(1, NMAX + 1)) and terms[1][:2] == (2, None)
    triples = set()
    for n in range(2, NMAX + 1):
        a, run, p = terms[n]
        ok &= p == sr.class_prime(n) and run is not None and run >= n and a + run - 1 <= X
        triples.add((p, a, run))
    ok &= all(sr.run_is_gap(a, run, p) for (p, a, run) in triples)
    return ok, len(triples)


def parse_runs(text):
    got = {}
    for line in text.splitlines():
        w = line.split()
        if w and w[0] == "A":
            got[int(w[1])] = (int(w[2]), None if w[3] == "open" else int(w[3]))
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--runs", action="store_true")
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    args = ap.parse_args()
    res, terms = load_terms(HERE / "RESULT_ford_1300.json")
    _, frozen = load_terms(HERE / "RESULT.json")
    _, ext1200 = load_terms(HERE / "RESULT_ford_1200.json")
    X_full = res["scan_limit"]
    print(f"Erdős #962 — A327909(1..{NMAX}), extension of the frozen a(1..1102) and a(1..1200) receipts\n")

    print("1. the frozen prefixes")
    check(len(frozen) == 1102 and prefix_equal(terms, frozen),
          "a(1..1102), run lengths and class primes equal RESULT.json exactly")
    check(len(ext1200) == 1200 and prefix_equal(terms, ext1200),
          "a(1..1200), run lengths and class primes equal RESULT_ford_1200.json exactly")

    print("\n2. every recorded run, checked by gcd alone")
    ok, nruns = runs_ok(terms, X_full)
    check(ok, f"each a(n) starts a maximal run of length >= n between p-smooth integers, n = 2..{NMAX}",
          f"{nruns} distinct runs")
    check(all(terms[n][0] <= terms[n + 1][0] for n in range(1, NMAX)), "a(n) is nondecreasing")

    print("\n3. the committed second-engine output (runs_ford_1300.txt)")
    second = parse_runs((HERE / "runs_ford_1300.txt").read_text(encoding="utf-8"))
    check(sorted(second) == list(range(1, NMAX + 1))
          and all(second[n] == terms[n][:2] for n in range(1, NMAX + 1)),
          f"runs.c (NMAX {NMAX}, X = {X_full}) gives the same a(n) and run length for every n <= {NMAX}")

    with tempfile.TemporaryDirectory(prefix="erdos962-") as tmp:
        exes = base.build(tmp)
        print(f"\n4. both engines rescan [1, {base.X_FAST}]")
        seq = base.sequential(exes["runs"], NMAX, base.X_FAST)
        reach = max(n for n in seq if all(k in seq for k in range(1, n + 1)))
        check(reach >= base.N_FAST and all(seq[n] == terms[n][:2] for n in range(1, reach + 1)),
              f"runs.c: a(1..{reach}) equal the receipt")
        mer, pieces = base.chunked(exes["chunk"], NMAX, base.X_FAST, args.jobs, 3)
        check(all(mer.get(n) == seq[n] for n in range(2, reach + 1)),
              f"chunk.c over {pieces} chunks agrees with runs.c on n = 2..{reach}")
        top = None
        if args.full:
            print(f"\n4b. chunk.c rescans the whole certified range [1, {X_full}]")
            mer, pieces = base.chunked(exes["chunk"], NMAX, X_full, args.jobs)
            top = max(n for n in mer if all(k in mer for k in range(2, n + 1)))
            check(top >= NMAX and all(mer[n] == terms[n][:2] for n in range(2, NMAX + 1)),
                  f"merged over {pieces} chunks: a(2..{NMAX}) and their run lengths equal the receipt")
        if args.runs:
            print(f"\n4c. runs.c rescans [1, {X_full}] (single core)")
            again = base.sequential(exes["runs"], NMAX, X_full)
            check(again == second, "runs.c output equals runs_ford_1300.txt for every n")

    print("\n5. cross-checks against OEIS A327909")
    check([terms[n][0] for n in range(1, 45)] == base.A327909_DATA, "a(1..44) equal the OEIS data")
    check(terms[999][0] == base.A327909_999, "a(999) equals the last term of the OEIS b-file")

    print("\n6. planted failures must be refused")
    a, run, p = terms[1212]
    check(not sr.run_is_gap(a - 1, run, p), "a(1212) claimed one smaller (80437383603) is rejected by gcd")
    a, run, p = terms[1300]
    check(not sr.run_is_gap(a, run + 1, p), "run(1300) claimed one longer is rejected by gcd")
    a, run, p = terms[1201]
    check(not sr.run_is_gap(a + 1, run - 1, p), "the a(1201) run started one late is rejected by gcd")
    drift = dict(terms)
    drift[1150] = (terms[1150][0] + 1,) + terms[1150][1:]
    check(not prefix_equal(drift, ext1200), "a receipt with a(1150) altered fails the a(1..1200) prefix check")

    verdict = {"claim": f"A327909(1..{NMAX})",
               "receipt_consistent_1300": not FAILURES,
               "verified_1300": not FAILURES and args.full and top is not None and top >= NMAX}
    print("\n" + json.dumps(verdict, separators=(",", ":")))
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s)")
        sys.exit(1)
    print("\nall checks passed")


if __name__ == "__main__":
    main()

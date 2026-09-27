#!/usr/bin/env python3
"""Verify the Erdős #1016 certificate (minimal pancyclic graphs). Exact, stdlib only.

  python3 -I verify.py              # full replay (default; ~5 CPU-minutes, parallel)
  python3 -I verify.py --jobs 1     # the same, in one process
  python3 -I verify.py --quick      # skip the heavy k=6 levels n=67..79 (sampled instead)
  python3 -I verify.py --with-c     # also build and run the independent C cross-check

Certified by the full replay (see README.md for the argument):

  (A) h(n) for every 3 <= n <= 108 is the value in RESULT.json, where
      m(n) = n + h(n) is the least number of edges of a pancyclic graph on
      n vertices.  In particular t_1..t_6 = 5, 8, 14, 24, 40, 67, where t_k is
      the largest n with h(n) <= k.
  (B) No graph C_n + 6 chords is pancyclic for any n >= 68, so h(n) >= 7 for
      every n >= 68, and h(n) = 7 for 68 <= n <= 108.

Checks, in order: skeleton census against an inclusion-exclusion formula;
two self-tests of the reduction and of the search against independent
oracles; planted failures that must be refused; the exhaustive table for
k <= 5; the complete k = 6 census at n = 67 (exactly the two known classes)
and exhaustion for 68 <= n <= 111; capacity beyond; every witness re-checked
by a DFS that shares no code with the search.  RESULT.json and witnesses.json
are read, never written.
"""
import argparse
import json
import os
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from math import comb

HERE = pathlib.Path(__file__).resolve().parent
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import pancyclic as pc  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""),
          flush=True)
    if not ok:
        FAILURES.append(label)
    return ok


def pmap(ex, fn, tasks):
    return list(ex.map(fn, tasks, chunksize=8)) if ex else [fn(t) for t in tasks]


# ------------------------------------------------------------ oracles

def brute_force(t, chords, n, forms):
    """Enumerate every arc-length vector; the search's independent oracle."""
    lb = pc.arc_lower_bounds(t, chords)

    def rec(i, left, x):
        if i == t - 1:
            if left >= lb[i]:
                x.append(left)
                ok = all(l in pc.evaluate(forms, x) for l in range(3, n + 1))
                x.pop()
                return ok
            return False
        for v in range(lb[i], left - sum(lb[i + 1:]) + 1):
            x.append(v)
            if rec(i + 1, left - v, x):
                x.pop()
                return True
            x.pop()
        return False

    return rec(0, n, [])


def random_chords(rng, n, k):
    chords = set()
    while len(chords) < k:
        u, v = sorted(rng.sample(range(n), 2))
        if v - u not in (1, n - 1):
            chords.add((u, v))
    return sorted(chords)


# --------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--with-c", action="store_true")
    args = ap.parse_args()
    result = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    wit = json.loads((HERE / "witnesses.json").read_text(encoding="utf-8"))["witnesses"]
    ex = ProcessPoolExecutor(max_workers=args.jobs) if args.jobs > 1 else None
    print("Erdős #1016 — minimal pancyclic graphs: h(n) for n <= 108, and t_6 = 67\n")

    # 1 ---------------------------------------------------------------
    print("1. skeleton census (one skeleton per dihedral class)")
    cache = {}
    for k in range(1, 7):
        classes, labeled = pc.skeleton_classes(k)
        forms = pmap(ex, pc.forms_task, classes)
        cache[k] = (classes, forms)
        want = result["census"][str(k)]
        formula = {t: pc.labeled_count_formula(t, k) for t in range(2, 2 * k + 1)}
        check(all(formula[t] == labeled.get(t, 0) for t in formula)
              and {str(t): c for t, c in labeled.items()} == want["labeled"]
              and len(classes) == want["classes"]
              and max(len(f) for f in forms) == result["max_distinct_forms"][str(k)],
              f"k={k}: {len(classes)} classes, labeled counts = inclusion-exclusion, "
              f"max distinct cycle forms {max(len(f) for f in forms)}")

    # 2 ---------------------------------------------------------------
    print("\n2. self-tests against independent oracles")
    rng = random.Random(1016)
    bad = 0
    for _ in range(250):
        k = rng.randint(1, 6)
        n = rng.randint(2 * k + 2, 111)
        chords = random_chords(rng, n, k)
        t, sk, x = pc.skeleton_of(n, chords)
        if pc.evaluate(pc.cycle_forms(t, sk), x) != pc.graph_cycle_lengths(n, chords):
            bad += 1
    check(bad == 0, "cycle forms equal the DFS cycle lengths of 250 random graphs C_n + k chords")
    pool = [(t, ch, f) for k in (3, 4, 5, 6) for (t, ch), f in zip(*cache[k])]
    small = [p for p in pool if p[0] <= 5]
    agree = sat = 0
    while agree < 240:
        # odd draws: a small skeleton near the top of its brute-forceable
        # range, where the search's exclusion rules actually fire (UNSAT)
        t, ch, forms = rng.choice(small if agree % 2 else pool)
        lb = pc.arc_lower_bounds(t, ch)
        ns = [n for n in range(max(3, sum(lb)), len(forms) + 3)
              if comb(n - sum(lb) + t - 1, t - 1) <= 25000]
        if not ns:
            continue
        n = ns[-1 - rng.randrange(min(4, len(ns)))] if agree % 2 else rng.choice(ns)
        x, _ = pc.decide(t, ch, n, forms)
        b = brute_force(t, ch, n, forms)
        if (x is not None) != b:
            break
        agree += 1
        sat += b
    check(agree == 240 and 0 < sat < agree, "search verdict equals brute-force enumeration",
          f"{agree} instances ({sat} SAT, {agree - sat} UNSAT)")

    # 3 ---------------------------------------------------------------
    print("\n3. planted failures must be refused")
    f68 = pc.family_f(68)
    missing = sorted(set(range(3, 69)) - pc.graph_cycle_lengths(68, f68))
    check(missing == [33], "the 6-chord family F_n at n = 68 is rejected", f"missing {missing}")
    try:
        pc.graph_cycle_lengths(10, [(0, 1)])
        refused = False
    except ValueError:
        refused = True
    check(refused, "a chord duplicating a cycle edge is rejected (multigraphs are not graphs)")
    tamper = json.loads(json.dumps(result))
    tamper["t"]["6"] = 68
    check(tamper["t"] != result["t"], "a receipt claiming t_6 = 68 differs from the certified one")
    minus = [n for n, w in wit.items() if w["k"] >= 1]
    ok = all(not pc.is_pancyclic(int(n), wit[n]["chords"][:-1]) for n in minus)
    check(len(minus) > 0 and ok,
          f"each of {len(minus)} witnesses with its last chord deleted is NOT pancyclic")

    # 4 ---------------------------------------------------------------
    print("\n4. exhaustive table, k <= 5 chords, 3 <= n <= 65")
    for k in range(1, 6):
        classes, forms = cache[k]
        sat = []
        for n in range(3, 66):
            if n - 2 > 2 ** (k + 1) - 1:
                continue
            for (t, ch), f in zip(classes, forms):
                if len(f) >= n - 2 and pc.decide(t, ch, n, f)[0] is not None:
                    sat.append(n)
                    break
        check(sat == result["sat_orders"][str(k)],
              f"k={k}: pancyclic exactly for n in {sat[0]}..{sat[-1]}" if sat else f"k={k}")

    # 5 ---------------------------------------------------------------
    print("\n5. k = 6: census at n = 67, exhaustion for 68 <= n <= 111")
    classes, forms = cache[6]
    heavy = set(range(67, 80))
    for n in [67] + list(range(68, 112)):
        idx = [i for i in range(len(classes)) if len(forms[i]) >= n - 2]
        if args.quick and n in heavy:
            idx = idx[::25]
        res = pmap(ex, pc.decide_task, [(classes[i][0], classes[i][1], forms[i], n) for i in idx])
        sat = [(classes[i], x) for i, (x, _) in zip(idx, res) if x is not None]
        if n == 67:
            want = sorted((c["t"], tuple(tuple(p) for p in c["skeleton"]))
                          for c in result["k6_census_n67"]["sat_classes"])
            got = sorted(c for c, _ in sat)
            ok = all(pc.is_pancyclic(67, pc.realise(t, ch, x)[1]) for (t, ch), x in sat)
            if args.quick:
                check(set(got) <= set(want) and ok, "n=67 (sampled): pancyclic classes are known ones")
            else:
                check(got == want and ok and len(idx) == result["k6_census_n67"]["eligible_classes"],
                      f"n=67: exactly {len(got)} of {len(idx)} classes pancyclic, both re-checked by DFS")
        else:
            want = result["k6_exclusion"][str(n)]["eligible_classes"]
            full = not (args.quick and n in heavy)
            check(not sat and (not full or len(idx) == want),
                  f"n={n}: {'all' if full else 'sampled'} {len(idx)} eligible classes excluded")
    cap = result["max_distinct_forms"]["6"]
    check(cap + 2 == 111 and result["k6_capacity_limit"] == 111,
          f"n >= 112: no 6-chord skeleton has n - 2 > {cap} distinct cycles (capacity)")

    # 6 ---------------------------------------------------------------
    print("\n6. witnesses, re-checked by DFS on the actual graph")
    h = {int(n): v for n, v in result["h"].items()}
    ok = True
    for n in range(3, 109):
        w = wit.get(str(n))
        ok &= (w is not None and w["k"] == h[n] == len(w["chords"])
               and pc.is_pancyclic(n, w["chords"]))
    check(ok, "every n in 3..108 has a pancyclic witness with exactly h(n) chords")
    ok = all(pc.is_pancyclic(n, pc.family_f(n)) for n in range(41, 68))
    check(ok, "cross-reference: the external family F_n is pancyclic for 41 <= n <= 67")

    # 7 ---------------------------------------------------------------
    print("\n7. assembling h(n)")
    # For k <= 5 the table covers n <= 65; n >= 66 is excluded by counting,
    # since k chords give at most 2^(k+1) - 1 cycles and n - 2 lengths are needed.
    # For k = 6, n >= 68 is excluded by step 5.  Adding a chord keeps a graph
    # pancyclic, so the least k with a pancyclic C_n + k chords is h(n); the
    # matching upper bounds are the witnesses of step 6.
    sat_orders = {k: set(result["sat_orders"][str(k)]) for k in range(1, 6)}
    derived = {}
    for n in range(3, 109):
        if n == 3:
            derived[n] = 0                        # C_3 is a triangle
            continue
        k = next((k for k in range(1, 6) if n in sat_orders[k]), None)
        derived[n] = k if k is not None else (6 if n <= 67 else 7)
    check(derived == h, "h(n) = least k with a k-chord pancyclic C_n + k chords, for 3 <= n <= 108")
    t = {k: max(n for n in derived if derived[n] <= k) for k in range(1, 7)}
    check({str(k): v for k, v in t.items()} == result["t"], f"t_1..t_6 = {[t[k] for k in range(1, 7)]}")

    if args.with_c:
        print("\n8. independent C cross-check (all labeled skeletons, DFS cycle forms)")
        cc = shutil.which("cc") or shutil.which("gcc")
        if not check(cc is not None, "a C compiler is available"):
            pass
        else:
            with tempfile.TemporaryDirectory(prefix="erdos1016-") as tmp:
                exe = pathlib.Path(tmp) / "xcheck"
                subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "xcheck.c")], check=True)
                want = (HERE / "xcheck_summary.txt").read_text(encoding="utf-8").split("\n")
                got = []
                for k, lo, hi in ((5, 3, 65), (6, 67, 111)):
                    run = subprocess.run([str(exe), str(k), str(lo), str(hi)],
                                         capture_output=True, text=True, check=True)
                    got += [l for l in run.stdout.splitlines() if l.startswith("SUMMARY")]
                check(got == [l for l in want if l.startswith("SUMMARY")],
                      "C summaries equal the committed xcheck_summary.txt")

    if ex:
        ex.shutdown()
    verdict = {"claim": "h(n) exact for 3<=n<=108; no 6-chord pancyclic graph for n>=68",
               "t": t, "h_68_108": 7, "t6": t[6], "quick": args.quick,
               "verified": not FAILURES and not args.quick}
    print("\n" + json.dumps(verdict, separators=(",", ":")))
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s)")
        sys.exit(1)
    if not args.quick:
        # check-only verifier: the receipts were re-derived and compared, not rewritten
        print("receipt-checked: RESULT.json")
        print("receipt-checked: witnesses.json")
    print("\nall checks passed" + (" (quick mode: not a certification)" if args.quick else ""))


if __name__ == "__main__":
    main()

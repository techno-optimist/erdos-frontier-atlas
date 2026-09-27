#!/usr/bin/env python3
"""Verify the k = 7 extension of the Erdős #1016 certificate: t_7 = 114.

  python3 -I verify_k7.py                  # quick replay (about a minute on 4 cores)
  python3 -I verify_k7.py --full           # the certifying replay (~80 CPU-minutes, parallel)
  python3 -I verify_k7.py --full --jobs 1  # the same, in one process
  python3 -I verify_k7.py --with-c         # also rerun xcheck.c at k = 7 (slow, one process)
  python3 -I verify_k7.py --python-levels 115-115   # Python re-decides the boundary
                                           #   level class by class (~2.6 CPU-hours)

Needs a C compiler (cc or gcc).  Certified by the full replay (see README.md):

  (C) No graph C_n + 7 chords is pancyclic for any n >= 115, while one is for
      every 109 <= n <= 114.  With (B) of verify.py (no 6-chord pancyclic graph
      for n >= 68): h(n) = 7 for 68 <= n <= 114, t_7 = 114, and h(n) >= 8 for
      every n >= 115.
  (D) h(n) = 8 for 115 <= n <= NMAX (the last order in witnesses_k7.json), by
      8-chord witnesses; with verify.py, h(n) is exact for every 3 <= n <= NMAX.

The exhaustion runs in pancyc.c, a C port of pancyclic.Search.  Checks, in
order: (1) the port reproduces RESULT.json at k = 6 node for node (the census
at n = 67 and the 44 exclusion levels 68..111), and its orbit-weighted
eligible counts equal the labeled counts recorded by the independent xcheck.c;
(2) the k = 7 class census, orbit sizes summing to the inclusion-exclusion
count of labeled skeletons; (3) positive controls: at every 109 <= n <= 114 the
engine finds the recorded pancyclic class, realised and re-checked by a DFS
that shares no code with it; (4) exhaustion of every eligible class for
115 <= n <= 215 (quick mode: 150..215 only), counts equal to RESULT_k7.json;
at 150..215 (quick: 180..215) the Python reference re-decides every eligible
class with the same verdict and node count; where xcheck_k7_summary.txt
reaches, the independent xcheck.c sees the same labeled skeletons eligible and
none pancyclic; capacity beyond; (5) planted failures; (6) every witness
re-checked by DFS; (7) assembly of h(n) and t_7.  RESULT_k7.json and
witnesses_k7.json are read, never written.
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import k7lib  # noqa: E402
import pancyclic as pc  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""),
          flush=True)
    if not ok:
        FAILURES.append(label)
    return ok


def xcheck_summaries(name):
    """Recorded SUMMARY lines of the independent xcheck.c, {(k, n): (labeled, sat)}."""
    path = HERE / name
    if not path.exists():
        return {}
    pat = re.compile(r"^SUMMARY k=(\d+) n=(\d+) eligible_labeled=(\d+) sat_labeled=(\d+)")
    return {(int(m.group(1)), int(m.group(2))): (int(m.group(3)), int(m.group(4)))
            for m in map(pat.match, path.read_text(encoding="utf-8").splitlines()) if m}


def ranges(levels):
    """Contiguous (lo, hi) runs of a sorted list of orders."""
    out = []
    for n in levels:
        if out and out[-1][1] == n - 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--with-c", action="store_true")
    ap.add_argument("--python-levels", metavar="LO-HI",
                    help="orders at which the Python reference re-decides every eligible "
                         "class (default 150-215 with --full, 180-215 without)")
    args = ap.parse_args()
    ref = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    res = json.loads((HERE / "RESULT_k7.json").read_text(encoding="utf-8"))
    wit = json.loads((HERE / "witnesses_k7.json").read_text(encoding="utf-8"))["witnesses"]
    nmax = max(int(n) for n in res["h"])
    exclude = k7lib.K7_EXCLUDE if args.full else k7lib.K7_QUICK_EXCLUDE
    if args.python_levels:
        lo, hi = (int(v) for v in args.python_levels.split("-"))
        pylevels = range(lo, hi + 1)
    else:
        pylevels = k7lib.K7_PYTHON if args.full else k7lib.K7_PYTHON_QUICK
    if not (k7lib.K7_EXCLUDE[0] <= pylevels[0] <= pylevels[-1] <= k7lib.K7_EXCLUDE[-1]):
        sys.exit(f"--python-levels must lie in {k7lib.K7_EXCLUDE[0]}..{k7lib.K7_EXCLUDE[-1]}")
    replayed = sorted(set(exclude) | set(pylevels))
    print("Erdős #1016 — k = 7 extension: t_7 = 114"
          + ("" if args.full else "  (quick replay: not a certification)") + "\n")

    # 1 ---------------------------------------------------------------
    print("1. the C engine reproduces the k = 6 receipt node for node")
    eng = k7lib.Engine()
    k6 = eng.census(6, 67, 111, args.jobs)
    want = {67: {"eligible_classes": ref["k6_census_n67"]["eligible_classes"],
                 "sat_classes": len(ref["k6_census_n67"]["sat_classes"]),
                 "nodes": ref["k6_census_n67"]["nodes"]}}
    want.update({int(n): v for n, v in ref["k6_exclusion"].items()})
    check(k6["classes"] == ref["census"]["6"]["classes"]
          and k6["orbit_sum"] == sum(int(c) for c in ref["census"]["6"]["labeled"].values())
          and k6["max_forms"] == ref["max_distinct_forms"]["6"],
          f"k=6: {k6['classes']} classes, orbit sizes summing to the labeled count, "
          f"at most {k6['max_forms']} distinct cycle forms, as in pancyclic.py")
    keys = ("eligible_classes", "sat_classes", "nodes")
    check({n: {key: v[key] for key in keys} for n, v in k6["levels"].items()} == want,
          "k=6: eligible, pancyclic and node counts equal RESULT.json at all 45 levels 67..111",
          f"{sum(v['nodes'] for v in k6['levels'].values())} nodes")
    xc = xcheck_summaries("xcheck_summary.txt")
    check(all(k6["levels"][n]["eligible_labeled"] == xc[(6, n)][0] for n in range(67, 112))
          and all(xc[(6, n)][1] == 0 for n in range(68, 112)),
          "k=6: orbit-weighted eligible counts equal the labeled counts recorded by the "
          "independent xcheck.c at every level")
    got67 = sorted((s["n"], s["t"], s["skeleton"], s["arcs"]) for s in k6["sat"])
    want67 = sorted((67, c["t"], c["skeleton"], c["arcs"]) for c in ref["k6_census_n67"]["sat_classes"])
    check(got67 == want67, "k=6: the only pancyclic classes are the two recorded at n = 67, same arcs")

    # 2 ---------------------------------------------------------------
    print("\n2. k = 7 class census")
    classes = res["census"]["classes"]
    sat_classes = sorted({v["class"] for v in res["k7_sat"].values()})
    with ThreadPoolExecutor(max_workers=2) as ex:
        singles = dict(zip(sat_classes, ex.map(
            lambda c: eng.one_class(7, k7lib.K7_SAT[0], k7lib.K7_EXCLUDE[0], c, classes),
            sat_classes)))
    # every replayed level; the Python levels also report per class
    runs = [eng.census(7, pylevels[0], pylevels[-1], args.jobs, mode="classes")]
    for lo, hi in ranges([n for n in replayed if n not in pylevels]):
        runs.append(eng.census(7, lo, hi, args.jobs))
    k7 = {"levels": {n: v for r in runs for n, v in r["levels"].items()},
          "max_forms": runs[0]["max_forms"], "per_class": runs[0]["per_class"]}
    formula = sum(pc.labeled_count_formula(t, 7) for t in range(2, 15))
    heads = {(r["classes"], r["orbit_sum"], r["max_forms"]) for r in [*runs, *singles.values()]}
    check(heads == {(classes, formula, res["census"]["max_distinct_forms"])}
          and res["census"]["labeled"] == formula,
          f"{classes} dihedral classes; orbit sizes sum to {formula}, the inclusion-exclusion "
          f"count of labeled 7-chord skeletons")
    xl = [l.split() for l in (HERE / "xcheck_k7_summary.txt").read_text(encoding="utf-8")
          .splitlines() if l.startswith("LABELED")]
    got_t = {int(w[1][2:]): int(w[2]) for w in xl}
    check(got_t == {t: pc.labeled_count_formula(t, 7) for t in range(2, 15)
                    if pc.labeled_count_formula(t, 7)},
          "labeled 7-chord skeletons enumerated by the independent xcheck.c, per t, equal the "
          "inclusion-exclusion counts")
    cap = res["census"]["max_distinct_forms"] + 2
    check(k7["max_forms"] + 2 == cap == res["k7_capacity_limit"] == k7lib.K7_EXCLUDE[-1],
          f"at most {k7['max_forms']} distinct cycle forms: no 7-chord graph is pancyclic "
          f"for n >= {cap + 1} (capacity)")

    # 3 ---------------------------------------------------------------
    print("\n3. positive controls: the engine finds the recorded pancyclic classes")
    for n in k7lib.K7_SAT:
        rec = res["k7_sat"][str(n)]
        run = singles[rec["class"]]
        hit = [s for s in run["sat"] if s["n"] == n]
        ok = (len(hit) == 1 and run["levels"][n]["nodes"] == rec["nodes"]
              and (hit[0]["t"], hit[0]["skeleton"], hit[0]["arcs"])
              == (rec["t"], rec["skeleton"], rec["arcs"]))
        if ok:
            m, chords = pc.realise(rec["t"], [tuple(c) for c in rec["skeleton"]], rec["arcs"])
            ok = (m == n and [list(c) for c in chords] == rec["chords"]
                  and pc.is_pancyclic(n, chords))
        check(ok, f"n={n}: class {rec['class']} is pancyclic, arcs {rec['arcs']}; DFS-checked")

    # 4 ---------------------------------------------------------------
    skipped = [n for n in k7lib.K7_EXCLUDE if n not in replayed]
    print(f"\n4. k = 7 exhaustion, {k7lib.K7_EXCLUDE[0]} <= n <= {k7lib.K7_EXCLUDE[-1]}"
          + ("" if not skipped else " (quick: levels " + ", ".join(
              f"{a}..{b}" for a, b in ranges(skipped)) + " are read from the receipt, "
              "not replayed)"))
    for n in replayed:
        got, rec = k7["levels"][n], res["k7_exclusion"][str(n)]
        check(got == rec and got["sat_classes"] == 0,
              f"n={n}: all {got['eligible_classes']} eligible classes "
              f"({got['eligible_labeled']} labeled) excluded", f"{got['nodes']} nodes")
    by_class = {}
    for c in k7["per_class"]:
        if c["n"] in pylevels:
            by_class.setdefault((c["class"], c["t"], c["skeleton"]), []).append(c)
    tasks = [(t, sk, [c["n"] for c in cs]) for (_, t, sk), cs in by_class.items()]
    with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        again = list(ex.map(k7lib.python_decide, tasks, chunksize=16))
    pairs = [(c, r) for cs, rs in zip(by_class.values(), again) for c, r in zip(cs, rs)]
    check(bool(pairs) and all((c["sat"], c["nodes"]) == r for c, r in pairs)
          and sum(c["nodes"] for c, _ in pairs)
          == sum(k7["levels"][n]["nodes"] for n in pylevels),
          f"the Python reference re-decides all {len(pairs)} (class, n) pairs at "
          f"{pylevels[0]}..{pylevels[-1]}: same verdicts, same node counts",
          f"{sum(r[1] for _, r in pairs)} nodes")
    xc7 = xcheck_summaries("xcheck_k7_summary.txt")
    both = sorted(n for (k, n) in xc7 if k == 7 and n in replayed)
    check(bool(both) and all(xc7[(7, n)] == (k7["levels"][n]["eligible_labeled"], 0)
                             for n in both),
          f"independent xcheck.c (all labeled skeletons, DFS cycle forms, no memo): "
          f"the same labeled skeletons eligible and none pancyclic at "
          f"{both[0] if both else '-'}..{both[-1] if both else '-'} ({len(both)} levels)")
    check(sorted(int(n) for n in res["k7_exclusion"]) == list(k7lib.K7_EXCLUDE),
          f"the receipt covers every level {k7lib.K7_EXCLUDE[0]}..{k7lib.K7_EXCLUDE[-1]}")

    # 5 ---------------------------------------------------------------
    print("\n5. planted failures must be refused")
    g114 = sorted(set(range(3, 115)) - pc.graph_cycle_lengths(114, k7lib.g7(114)))
    check(g114 == [61], "the 7-chord family G7(n) at n = 114 is rejected", f"missing {g114}")
    s_end = sorted(set(range(3, nmax + 2)) - pc.graph_cycle_lengths(nmax + 1, k7lib.s8(nmax + 1)))
    check(s_end == [108], f"the 8-chord family S8(n) at n = {nmax + 1} is rejected (the table's "
          f"end is the family's, not a claim about h({nmax + 1}))", f"missing {s_end}")
    ok = all(run["levels"][115]["sat_classes"] == 0 for run in singles.values())
    check(ok, f"the classes {sat_classes} that work at n <= 114 are refuted at n = 115")
    tamper = json.loads(json.dumps(res))
    tamper["k7_exclusion"]["215"]["nodes"] += 1
    check(k7["levels"][215] != tamper["k7_exclusion"]["215"],
          "a receipt with one node count altered disagrees with the engine")
    ok = all(not pc.is_pancyclic(int(n), w["chords"][:-1]) for n, w in wit.items())
    check(ok, f"each of {len(wit)} witnesses with its last chord deleted is NOT pancyclic")

    # 6 ---------------------------------------------------------------
    print("\n6. witnesses, re-checked by DFS on the actual graph")
    ok = all(w["k"] == len(w["chords"]) == len({tuple(c) for c in w["chords"]})
             and pc.is_pancyclic(int(n), w["chords"]) for n, w in wit.items())
    check(ok and sorted(int(n) for n in wit) == list(range(k7lib.K7_SAT[0], nmax + 1)),
          f"every n in {k7lib.K7_SAT[0]}..{nmax} has a pancyclic witness with exactly k chords")
    ok = all(wit[str(n)]["chords"] == res["k7_sat"][str(n)]["chords"] for n in k7lib.K7_SAT)
    check(ok, "the 7-chord witnesses are the positive controls of step 3")
    ok = all(wit[str(n)]["chords"] == [list(c) for c in k7lib.s8(n)]
             for n in range(k7lib.K7_EXCLUDE[0], nmax + 1))
    check(ok, f"the 8-chord witnesses are the family S8(n), {k7lib.K7_EXCLUDE[0]} <= n <= {nmax}")
    ok = all(pc.is_pancyclic(n, k7lib.g7(n)) for n in range(61, 114))
    check(ok, "cross-reference: G7(n) is pancyclic for every 61 <= n <= 113")
    ok = all(pc.is_pancyclic(n, k7lib.s8(n)) for n in range(108, 115))
    check(ok, "cross-reference: S8(n) is pancyclic for 108 <= n <= 114 as well")

    # 7 ---------------------------------------------------------------
    print("\n7. assembling h(n)")
    # k <= 6 chords: excluded for n >= 68 by RESULT.json (certified by
    # verify.py; its k = 6 levels were re-derived by the engine in step 1, and
    # n >= 112 is capacity).  Exactly 7 chords: pancyclic at 109..114 (step 3),
    # excluded at 115..215 (step 4) and beyond by capacity (step 2).  Adding a
    # chord keeps a graph pancyclic, so k-chord exclusion covers fewer chords.
    derived = {n: 7 for n in k7lib.K7_SAT}
    derived.update({n: 8 for n in range(k7lib.K7_EXCLUDE[0], nmax + 1)})
    ok = (ref["claims"]["no_6_chord_pancyclic_for_n_at_least"] == 68
          and all(wit[str(n)]["k"] == derived[n] for n in derived))
    check(ok and {str(n): v for n, v in derived.items()} == res["h"],
          f"h(n) = 7 for 109 <= n <= 114 and h(n) = 8 for 115 <= n <= {nmax}")
    t7 = max(n for n in derived if derived[n] <= 7)
    check(t7 == res["t7"] == res["claims"]["t7"]
          and res["claims"]["no_7_chord_pancyclic_for_n_at_least"] == t7 + 1
          and res["claims"]["h_exact"] == [3, nmax],
          f"t_7 = {t7}; with RESULT.json, h(n) is exact for 3 <= n <= {nmax}")

    if args.with_c:
        print("\n8. independent C cross-check at k = 7 (all labeled skeletons, DFS cycle forms)")
        want = [l for l in (HERE / "xcheck_k7_summary.txt").read_text(encoding="utf-8")
                .splitlines() if l.startswith(("LABELED", "SUMMARY"))]
        ns = [int(re.search(r" n=(\d+) ", l).group(1)) for l in want if l.startswith("SUMMARY")]
        cc = shutil.which("cc") or shutil.which("gcc")
        if check(cc is not None, "a C compiler is available"):
            with tempfile.TemporaryDirectory(prefix="erdos1016-") as tmp:
                exe = pathlib.Path(tmp) / "xcheck"
                subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "xcheck.c")], check=True)
                run = subprocess.run([str(exe), "7", str(min(ns)), str(max(ns))],
                                     capture_output=True, text=True, check=True)
            got = [l for l in run.stdout.splitlines() if l.startswith(("LABELED", "SUMMARY"))]
            check(got == want, f"C output equals the committed xcheck_k7_summary.txt "
                               f"({min(ns)} <= n <= {max(ns)})")

    verdict = {"claim": f"t7=114: no 7-chord pancyclic graph for n>=115; "
                        f"h(n)=8 for 115<=n<={nmax}",
               "t7": t7, "h_109_114": 7, f"h_115_{nmax}": 8, "full": args.full,
               "verified": not FAILURES and args.full}
    print("\n" + json.dumps(verdict, separators=(",", ":")))
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s)")
        sys.exit(1)
    # check-only verifier: receipts are re-derived and compared, never rewritten.
    # Every witness is re-derived in both modes (steps 3 and 6); the per-level
    # exclusion counts of RESULT_k7.json only by the full replay.
    if args.full:
        print("receipt-checked: RESULT_k7.json")
    print("receipt-checked: witnesses_k7.json")
    print("\nall checks passed" + ("" if args.full else " (quick mode: not a certification)"))


if __name__ == "__main__":
    main()

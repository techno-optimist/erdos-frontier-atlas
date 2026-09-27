#!/usr/bin/env python3
"""EMIT the k = 7 receipt and witnesses of the Erdős #1016 certificate.

  python3 -I emit_result_k7.py --out-dir DIR [--jobs N]

Writes DIR/RESULT_k7.json and DIR/witnesses_k7.json.  It refuses to write into
its own directory: the committed files are only ever replaced deliberately, by
copying from a fresh emission after review.  ``verify_k7.py`` never calls this.

Runs, with pancyc.c: first-mode searches at 109 <= n <= 114 (the first
pancyclic class in descending form-count order), one-class replays of those
classes (the numbers verify_k7.py recomputes), and the exhaustion of every
eligible class for 115 <= n <= 215 (~80 CPU-minutes).  Then the 8-chord
witnesses S8(n) for 115 <= n <= NMAX, the last order of the contiguous range
where that family is pancyclic.
"""
import argparse
import json
import os
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import k7lib  # noqa: E402
import pancyclic as pc  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    args = ap.parse_args()
    out = pathlib.Path(args.out_dir).resolve()
    if out == HERE:
        sys.exit("refusing to overwrite the committed receipt in place")
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    eng = k7lib.Engine()
    sat_n, excl = k7lib.K7_SAT, k7lib.K7_EXCLUDE

    # the first pancyclic class at each 109 <= n <= 114
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        firsts = list(ex.map(lambda n: eng.first(7, n, n), sat_n))
    pick = {}
    for n, run in zip(sat_n, firsts):
        hit = [s for s in run["sat"] if s["n"] == n]
        assert len(hit) == 1, n
        pick[n] = hit[0]["class"]
    classes = firsts[0]["classes"]
    print(f"first pancyclic classes: {pick}  ({time.time() - t0:.0f}s)", flush=True)

    # one-class replays: node counts and arcs exactly as verify_k7.py sees them
    distinct = sorted(set(pick.values()))
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        singles = dict(zip(distinct, ex.map(
            lambda c: eng.one_class(7, sat_n[0], excl[0], c, classes), distinct)))
    k7_sat = {}
    for n in sat_n:
        run = singles[pick[n]]
        hit = [s for s in run["sat"] if s["n"] == n]
        assert len(hit) == 1, n
        s = hit[0]
        m, chords = pc.realise(s["t"], [tuple(c) for c in s["skeleton"]], s["arcs"])
        assert m == n and pc.is_pancyclic(n, chords), n
        k7_sat[str(n)] = {"class": s["class"], "t": s["t"], "skeleton": s["skeleton"],
                          "arcs": s["arcs"], "chords": [list(c) for c in chords],
                          "nodes": run["levels"][n]["nodes"]}
    for c, run in singles.items():
        assert run["levels"][excl[0]]["sat_classes"] == 0, c

    # exhaustion 115..215
    k7 = eng.census(7, excl[0], excl[-1], args.jobs)
    assert not k7["sat"], k7["sat"][:3]
    formula = sum(pc.labeled_count_formula(t, 7) for t in range(2, 15))
    assert k7["orbit_sum"] == formula and k7["classes"] == classes
    assert k7["max_forms"] + 2 == excl[-1]
    print(f"exhaustion {excl[0]}..{excl[-1]}: no pancyclic class  ({time.time() - t0:.0f}s)",
          flush=True)

    # 8-chord witnesses: the family S8(n), as far as it stays pancyclic
    witnesses = {}
    for n in sat_n:
        witnesses[str(n)] = {"k": 7, "chords": k7_sat[str(n)]["chords"],
                             "source": "found by pancyc.c (first pancyclic class)"}
    nmax = excl[0] - 1
    while pc.is_pancyclic(nmax + 1, k7lib.s8(nmax + 1)):
        nmax += 1
        witnesses[str(nmax)] = {"k": 8, "chords": [list(c) for c in k7lib.s8(nmax)],
                                "source": "the 8-chord family S8(n)"}
    print(f"S8(n) is pancyclic for {excl[0]} <= n <= {nmax}, not at {nmax + 1}")
    h = {n: 7 for n in sat_n}
    h.update({n: 8 for n in range(excl[0], nmax + 1)})
    t7 = max(n for n in h if h[n] <= 7)
    result = {
        "schema": "erdos-1016-pancyclic-k7-result-v1",
        "engine": "pancyc.c (C port of pancyclic.Search; k = 6 agreement: verify_k7.py step 1)",
        "census": {"classes": classes, "labeled": formula,
                   "max_distinct_forms": k7["max_forms"]},
        "k7_capacity_limit": k7["max_forms"] + 2,
        "k7_sat": k7_sat,
        "k7_exclusion": {str(n): k7["levels"][n] for n in excl},
        "h": {str(n): h[n] for n in sorted(h)},
        "t7": t7,
        "claims": {"t7": t7, "no_7_chord_pancyclic_for_n_at_least": excl[0],
                   "h_exact": [3, nmax]},
    }
    (out / "RESULT_k7.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    (out / "witnesses_k7.json").write_text(json.dumps(
        {"schema": "erdos-1016-witnesses-v1",
         "witnesses": {n: witnesses[n] for n in sorted(witnesses, key=int)}}, indent=1) + "\n",
        encoding="utf-8")
    print(f"wrote {out}/RESULT_k7.json and witnesses_k7.json in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

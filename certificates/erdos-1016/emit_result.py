#!/usr/bin/env python3
"""EMIT the committed receipt and witnesses for the Erdős #1016 certificate.

  python3 -I emit_result.py --out-dir DIR [--jobs N]

Writes DIR/RESULT.json and DIR/witnesses.json.  It refuses to write into its
own directory: the committed files are only ever replaced deliberately, by
copying from a fresh emission after review.  ``verify.py`` never calls this.
"""
import argparse
import json
import os
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import pancyclic as pc  # noqa: E402

KMAX_TABLE = 5            # exhaustive table over k <= 5 for 3 <= n <= NMAX_TABLE
NMAX_TABLE = 65           # 5 chords give at most 2^6 - 1 = 63 cycles, so n <= 65
K6_WITNESS = range(41, 67)
K6_CENSUS_N = 67
K6_EXCLUDE = range(68, 112)
K7_WITNESS = range(68, 109)


def pool(jobs):
    return ProcessPoolExecutor(max_workers=jobs) if jobs > 1 else None


def pmap(ex, fn, tasks):
    return list(ex.map(fn, tasks, chunksize=8)) if ex else [fn(t) for t in tasks]


def census(k, ex):
    classes, labeled = pc.skeleton_classes(k)
    forms = pmap(ex, pc.forms_task, classes)
    return classes, labeled, forms


def first_sat(classes, forms, n, order):
    for i in order:
        if len(forms[i]) < n - 2:
            continue
        t, ch = classes[i]
        x, _ = pc.decide(t, ch, n, forms[i])
        if x is not None:
            return i, x
    return None


def all_classes(ex, classes, forms, n):
    idx = [i for i in range(len(classes)) if len(forms[i]) >= n - 2]
    res = pmap(ex, pc.decide_task, [(classes[i][0], classes[i][1], forms[i], n) for i in idx])
    return idx, res


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
    ex = pool(args.jobs)
    result = {"schema": "erdos-1016-pancyclic-result-v1", "census": {}, "sat_orders": {},
              "max_distinct_forms": {}}
    witnesses = {}
    cache = {}
    for k in range(1, 7):
        classes, labeled, forms = census(k, ex)
        cache[k] = (classes, forms)
        result["census"][str(k)] = {"classes": len(classes),
                                    "labeled": {str(t): c for t, c in sorted(labeled.items())}}
        result["max_distinct_forms"][str(k)] = max(len(f) for f in forms)
        print(f"k={k}: {len(classes)} classes, max forms {result['max_distinct_forms'][str(k)]}",
              flush=True)

    # exhaustive table, k <= 5
    h = {3: 0}
    witnesses[3] = {"k": 0, "chords": [], "source": "C_3 itself"}
    for k in range(1, KMAX_TABLE + 1):
        classes, forms = cache[k]
        order = list(range(len(classes)))
        sat = []
        for n in range(3, NMAX_TABLE + 1):
            if n - 2 > 2 ** (k + 1) - 1:
                continue
            hit = first_sat(classes, forms, n, order)
            if hit is not None:
                sat.append(n)
                if n not in h:
                    i, x = hit
                    t, ch = classes[i]
                    m, chords = pc.realise(t, ch, x)
                    assert m == n and pc.is_pancyclic(n, chords)
                    h[n] = k
                    witnesses[n] = {"k": k, "chords": chords, "source": "found by pancyclic.Search"}
        result["sat_orders"][str(k)] = sat
        print(f"k={k}: pancyclic orders {sat}", flush=True)

    # k = 6: witnesses 41..66, full census at 67, exclusion 68..111
    classes, forms = cache[6]
    order = sorted(range(len(classes)), key=lambda i: (-len(forms[i]), classes[i]))
    for n in K6_WITNESS:
        i, x = first_sat(classes, forms, n, order)
        t, ch = classes[i]
        m, chords = pc.realise(t, ch, x)
        assert m == n and pc.is_pancyclic(n, chords) and n not in h
        h[n] = 6
        witnesses[n] = {"k": 6, "chords": chords, "source": "found by pancyclic.Search"}
    idx, res = all_classes(ex, classes, forms, K6_CENSUS_N)
    sat67 = []
    for i, (x, _) in zip(idx, res):
        if x is not None:
            t, ch = classes[i]
            m, chords = pc.realise(t, ch, x)
            assert m == K6_CENSUS_N and pc.is_pancyclic(m, chords)
            sat67.append({"t": t, "skeleton": [list(c) for c in ch], "arcs": x, "chords": chords})
    h[K6_CENSUS_N] = 6
    witnesses[K6_CENSUS_N] = {"k": 6, "chords": sat67[0]["chords"],
                              "source": "found by pancyclic.Search (full census at n=67)"}
    result["k6_census_n67"] = {"eligible_classes": len(idx), "sat_classes": sat67,
                               "nodes": sum(r[1] for r in res)}
    print(f"n=67: {len(idx)} eligible classes, {len(sat67)} pancyclic", flush=True)
    excl = {}
    for n in K6_EXCLUDE:
        idx, res = all_classes(ex, classes, forms, n)
        assert all(x is None for x, _ in res), n
        excl[str(n)] = {"eligible_classes": len(idx), "sat_classes": 0,
                        "nodes": sum(r[1] for r in res)}
        print(f"n={n}: {len(idx)} eligible classes, all excluded", flush=True)
    result["k6_exclusion"] = excl
    capacity = result["max_distinct_forms"]["6"] + 2
    result["k6_capacity_limit"] = capacity

    # k = 7 upper bounds 68..108: family F_n plus one chord (first in lex order)
    for n in K7_WITNESS:
        base = [tuple(sorted(c)) for c in pc.family_f(n)]
        edges = set(base) | {tuple(sorted((v, (v + 1) % n))) for v in range(n)}
        found = None
        for u in range(n):
            for v in range(u + 2, n):
                if (u, v) in edges:
                    continue
                if pc.is_pancyclic(n, base + [(u, v)]):
                    found = (u, v)
                    break
            if found:
                break
        assert found, n
        h[n] = 7
        witnesses[n] = {"k": 7, "chords": sorted(base + [found]),
                        "source": "family F_n of Pinckard et al. (2026) plus one chord found here"}
    result["h"] = {str(n): h[n] for n in sorted(h)}
    result["t"] = {str(k): max(n for n in h if h[n] <= k) for k in range(1, 7)}
    result["claims"] = {
        "h_exact": [3, max(h)],
        "no_6_chord_pancyclic_for_n_at_least": 68,
        "t6": 67,
    }
    if ex:
        ex.shutdown()
    (out / "RESULT.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    (out / "witnesses.json").write_text(json.dumps(
        {"schema": "erdos-1016-witnesses-v1",
         "witnesses": {str(n): witnesses[n] for n in sorted(witnesses)}}, indent=1) + "\n",
        encoding="utf-8")
    print(f"wrote {out}/RESULT.json and witnesses.json in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

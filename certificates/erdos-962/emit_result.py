#!/usr/bin/env python3
"""EMIT the committed receipt of the Erdős #962 certificate (OEIS A327909).

  python3 -I emit_result.py --out-dir DIR [--nmax 1102] [--limit 42000000000] [--jobs N]

Writes DIR/RESULT.json.  It refuses to write into its own directory: the
committed receipt is only ever replaced deliberately, by copying from a fresh
emission after review.  ``verify.py`` never calls this.

It scans [1, limit] with chunk.c in parallel pieces, merges the pieces with
smooth_runs.merge_chunks, and records for every n <= nmax the start a(n) and
the length of the maximal run there (the gap between consecutive p-smooth
integers, p the largest prime <= n).  a(1) = 2 is recorded by hand: every
integer >= 2 has a prime factor > 1, so that run never closes.
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import smooth_runs as sr  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--nmax", type=int, default=1102)
    ap.add_argument("--limit", type=int, default=42_000_000_000)
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    args = ap.parse_args()
    out = pathlib.Path(args.out_dir).resolve()
    if out == HERE:
        sys.exit("refusing to overwrite the committed receipt in place")
    out.mkdir(parents=True, exist_ok=True)
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        sys.exit("no C compiler (cc or gcc) on PATH")
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="erdos962-") as tmp:
        exe = pathlib.Path(tmp) / "chunk"
        subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "chunk.c")], check=True)
        X, pieces = args.limit, max(1, args.jobs)
        step = -(-X // pieces)
        bounds = [(1 + i * step, min(X, (i + 1) * step)) for i in range(pieces)]
        run = lambda b: subprocess.run([str(exe), str(b[0]), str(b[1]), str(args.nmax)],
                                       capture_output=True, text=True, check=True).stdout
        with ThreadPoolExecutor(max_workers=pieces) as ex:
            texts = list(ex.map(run, bounds))
    merged = sr.merge_chunks(texts, args.nmax, X)
    missing = [n for n in range(2, args.nmax + 1) if n not in merged or merged[n][1] is None]
    if missing:
        sys.exit(f"limit too small: no closed run yet for n = {missing[:5]}...")
    terms = {"1": {"a": 2, "run": None, "class_prime": None}}
    for n in range(2, args.nmax + 1):
        a, run = merged[n]
        terms[str(n)] = {"a": a, "run": run, "class_prime": sr.class_prime(n)}
    result = {
        "schema": "erdos-962-a327909-v1",
        "sequence": "A327909",
        "definition": "a(n) = smallest start of a run of n or more consecutive integers each "
                      "having a prime factor greater than n",
        "engine": "chunk.c (exact smoothness sieve; record gaps per prime class), merged by "
                  "smooth_runs.merge_chunks; cross-checked by runs.c and a Python sieve",
        "scan_limit": X,
        "terms": terms,
        "claims": {"a": {n: v["a"] for n, v in terms.items()},
                   "exhaustive_through": args.nmax},
    }
    (out / "RESULT.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out}/RESULT.json: a(1..{args.nmax}), a({args.nmax}) = "
          f"{terms[str(args.nmax)]['a']}, scan of [1, {X}] in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

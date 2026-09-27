#!/usr/bin/env python3
"""EMIT the committed receipt of the Erdős #854 certificate (OEIS A389839).

  python3 -I emit_result.py --out-dir DIR [--nmax 16] [--jobs N]

Writes DIR/RESULT.json.  It refuses to write into its own directory: the
committed receipt is only ever replaced deliberately, by copying from a fresh
emission after review.  ``verify.py`` never calls this.

For each 2 <= n <= NMAX it runs gapsc.c on p_n#, gap by gap, until the first
absent gap a(n); every gap below a(n) gets an explicit witness x (realised by
CRT from the covering the engine found, then checked by gcd).
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
from math import prod

HERE = pathlib.Path(__file__).resolve().parent
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import coprime_gaps as cg  # noqa: E402


def build(tmp):
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        sys.exit("no C compiler (cc or gcc) on PATH")
    exe = pathlib.Path(tmp) / "gapsc"
    subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "gapsc.c")], check=True)
    return exe


def parse(text):
    """{t: (occurs, nodes, residues or None)} and the term a(n)."""
    gaps, term = {}, None
    for line in text.splitlines():
        w = line.split()
        if w and w[0] == "GAP":
            t, occ, nodes = int(w[2]), w[3] == "1", int(w[4])
            res = None
            if occ:
                res = {int(a): int(b) for a, b in (x.split(":") for x in w[6:])}
            gaps[t] = (occ, nodes, res)
        elif w and w[0] == "TERM":
            term = int(w[2])
    return gaps, term


def term(exe, n):
    out = subprocess.run([str(exe), str(n)], capture_output=True, text=True, check=True).stdout
    gaps, a = parse(out)
    P = prod(cg.primes(n))
    rec = {"prime": cg.primes(n)[-1], "a": a, "absent_nodes": gaps[a][1],
           "gaps": {"2": {"nodes": 0, "x": P - 1}}}
    for t in range(4, a, 2):
        occ, nodes, res = gaps[t]
        assert occ, (n, t)
        x = cg.realise(n, t, res)
        assert cg.is_gap(n, x, t), (n, t)
        rec["gaps"][str(t)] = {"nodes": nodes, "x": x}
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--nmax", type=int, default=16)
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    args = ap.parse_args()
    out = pathlib.Path(args.out_dir).resolve()
    if out == HERE:
        sys.exit("refusing to overwrite the committed receipt in place")
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="erdos854-") as tmp:
        exe = build(tmp)
        ns = list(range(2, args.nmax + 1))
        with ThreadPoolExecutor(max_workers=args.jobs) as ex:
            recs = dict(zip(ns, ex.map(lambda n: term(exe, n), ns)))
    result = {
        "schema": "erdos-854-a389839-v1",
        "sequence": "A389839",
        "definition": "a(n) = smallest even number that is not the difference of two "
                      "consecutive integers coprime to prime(n)#",
        "engine": "gapsc.c (C port of coprime_gaps.Cover; node counts comparable)",
        "terms": {str(n): recs[n] for n in ns},
        "claims": {"a": {str(n): recs[n]["a"] for n in ns},
                   "exhaustive_through": args.nmax},
    }
    (out / "RESULT.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out}/RESULT.json: a(2..{args.nmax}) = "
          f"{[recs[n]['a'] for n in ns]} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

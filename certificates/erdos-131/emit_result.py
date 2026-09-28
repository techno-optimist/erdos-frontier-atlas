#!/usr/bin/env python3
"""EMIT the committed receipt of the Erdős #131 certificate (thresholds of OEIS A068063).

  python3 -I emit_result.py --out-dir DIR [--kmax 9] [--nmax 400]

Writes DIR/RESULT.json.  It refuses to write into its own directory: the
committed receipt is only ever replaced deliberately, by copying from a fresh
emission after review.  ``verify.py`` never calls this.

It runs nondiv.c for k = 1..kmax and records every (k, N) search -- verdict and
node count -- and each threshold's set, checked here by brute force.
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import nondividing as nd  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--kmax", type=int, default=9)
    ap.add_argument("--nmax", type=int, default=400)
    args = ap.parse_args()
    out = pathlib.Path(args.out_dir).resolve()
    if out == HERE:
        sys.exit("refusing to overwrite the committed receipt in place")
    out.mkdir(parents=True, exist_ok=True)
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        sys.exit("no C compiler (cc or gcc) on PATH")
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="erdos131-") as tmp:
        exe = pathlib.Path(tmp) / "nondiv"
        subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "nondiv.c")], check=True)
        text = subprocess.run([str(exe), str(args.kmax), str(args.nmax)], capture_output=True,
                              text=True, check=True).stdout
    searches, th = [], {}
    for line in text.splitlines():
        w = line.split()
        if w[0] == "NONE":
            sys.exit(f"no threshold found for k = {w[1]} up to {args.nmax}")
        k, N, nodes = int(w[1]), int(w[2]), int(w[3])
        searches.append([k, N, nodes, w[0] == "T"])
        if w[0] == "T":
            S = sorted((int(x) for x in w[4:]), reverse=True)
            assert len(S) == k and max(S) == N and nd.is_nondividing(S), (k, N)
            th[str(k)] = {"N": N, "set": S}
    K = len(th)
    result = {
        "schema": "erdos-131-a068063-thresholds-v1",
        "sequence": "A068063",
        "definition": "a(n) = largest nondividing subset of {1..n} (no element divides the sum of "
                      "any nonempty subset of the others); T_k = least n with a(n) >= k",
        "engine": "nondiv.c (decreasing-order search pruned by the smaller thresholds; C port of "
                  "nondividing.Search, node for node)",
        "searches": searches,
        "thresholds": th,
        "claims": {"T": [th[str(k)]["N"] for k in range(1, K + 1)], "kmax": K},
    }
    (out / "RESULT.json").write_text(json.dumps(result, separators=(",", ":")) + "\n",
                                     encoding="utf-8")
    print(f"wrote {out}/RESULT.json: T_1..T_{K} = {result['claims']['T']}, "
          f"{len(searches)} searches, in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

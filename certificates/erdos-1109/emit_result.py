#!/usr/bin/env python3
"""EMIT the committed receipt of the Erdős #1109 certificate (records of OEIS A392164).

  python3 -I emit_result.py --out-dir DIR [--nmax 2000]

Writes DIR/RESULT.json.  It refuses to write into its own directory: the
committed receipt is only ever replaced deliberately, by copying from a fresh
emission after review.  ``verify.py`` never calls this.

It runs sqclique.c over every N <= nmax with 2N squarefree and records, per
candidate N, the size k it tried, |V_N|, the node count, and whether N is a
record; each record comes with its set, checked here by trial division.
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
import sqfree_sums as ss  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--nmax", type=int, default=2000)
    args = ap.parse_args()
    out = pathlib.Path(args.out_dir).resolve()
    if out == HERE:
        sys.exit("refusing to overwrite the committed receipt in place")
    out.mkdir(parents=True, exist_ok=True)
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        sys.exit("no C compiler (cc or gcc) on PATH")
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="erdos1109-") as tmp:
        exe = pathlib.Path(tmp) / "sqclique"
        subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "sqclique.c")], check=True)
        text = subprocess.run([str(exe), str(args.nmax)], capture_output=True, text=True,
                              check=True).stdout
    cands, records = [], {}
    for line in text.splitlines():
        w = line.split()
        k, N, nv, nodes = int(w[1]), int(w[2]), int(w[3]), int(w[4])
        cands.append([N, k, nv, nodes, w[0] == "R"])
        if w[0] == "R":
            S = sorted(int(x) for x in w[5:])
            assert len(S) == k and max(S) == N and ss.sumset_squarefree(S), (k, N)
            records[str(k)] = {"N": N, "set": S}
    K = len(records)
    result = {
        "schema": "erdos-1109-a392165-v1",
        "sequences": {"A392164": "f(N) = largest S in {1..N} with every element of S+S squarefree",
                      "A392165": "least N with f(N) >= k (indices of records of A392164)"},
        "engine": "sqclique.c (clique decision search with a greedy-colouring bound; C port of "
                  "sqfree_sums.Clique, node for node)",
        "nmax": args.nmax,
        "candidates": cands,
        "records": records,
        "claims": {"A392165": [records[str(k)]["N"] for k in range(1, K + 1)],
                   "f_nmax": K, "exhaustive_through": args.nmax},
    }
    (out / "RESULT.json").write_text(json.dumps(result, separators=(",", ":")) + "\n",
                                     encoding="utf-8")
    print(f"wrote {out}/RESULT.json: {len(cands)} candidates, records 1..{K} "
          f"(last at N = {records[str(K)]['N']}), in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

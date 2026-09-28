#!/usr/bin/env python3
"""EMIT the committed receipt of the Erdős #357 certificate (OEIS A364132, A364153).

  python3 -I emit_result.py --out-dir DIR [--nmax-m 26] [--nmax-a 16] [--next-m N] [--next-a N]
                            [--jobs J]

Writes DIR/RESULT.json.  It refuses to write into its own directory: the
committed receipt is only ever replaced deliberately, by copying from a fresh
emission after review.  ``verify.py`` never calls this.

For each mode and n it runs segsum.c for N = a(n-1), a(n-1) + 1, ..., J values
at a time, until a sequence is found; the least such N is a(n).  The receipt keeps the two searches that
decide a(n): "none" with every term <= a(n) - 1, which refutes every smaller N
at once, and "found" at a(n), whose sequence is checked here by brute force.
With --next-m / --next-a it also records one sequence for the next, undecided
term, found with every term <= N: an upper bound for that cell.
"""
import argparse
import json
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
import segment_sums as ss  # noqa: E402

OEIS = {"m": "A364132", "a": "A364153"}


def search(exe, mode, n, N):
    w = subprocess.run([str(exe), mode, str(n), str(N)], capture_output=True, text=True,
                       check=True).stdout.split()
    assert w[1:4] == [mode, str(n), str(N)], w
    return int(w[4]), ([int(x) for x in w[6:]] if w[0] == "found" else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--nmax-m", type=int, default=26)
    ap.add_argument("--nmax-a", type=int, default=16)
    ap.add_argument("--next-m", type=int)
    ap.add_argument("--next-a", type=int)
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    out = pathlib.Path(args.out_dir).resolve()
    if out == HERE:
        sys.exit("refusing to overwrite the committed receipt in place")
    out.mkdir(parents=True, exist_ok=True)
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        sys.exit("no C compiler (cc or gcc) on PATH")
    t0 = time.time()
    searches, witnesses, claims, bounds = [], {"m": {}, "a": {}}, {}, {}
    with tempfile.TemporaryDirectory(prefix="erdos357-") as tmp:
        exe = pathlib.Path(tmp) / "segsum"
        subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "segsum.c")], check=True)
        for mode, nmax in (("m", args.nmax_m), ("a", args.nmax_a)):
            terms, N = [], 1
            for n in range(1, nmax + 1):
                ran = {}
                with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
                    while True:
                        batch = list(range(N, N + max(1, args.jobs)))
                        for b, r in zip(batch, ex.map(lambda b: search(exe, mode, n, b), batch)):
                            ran[b] = r
                        hits = [b for b in batch if ran[b][1] is not None]
                        if hits:
                            N = hits[0]
                            break
                        N += len(batch)
                if N > 1 and N - 1 not in ran:
                    ran[N - 1] = search(exe, mode, n, N - 1)
                    assert ran[N - 1][1] is None
                seq = ran[N][1]
                assert len(seq) == n and max(seq) == N and ss.is_valid(mode, seq, N), (mode, n)
                if N > 1:
                    searches.append([mode, n, N - 1, ran[N - 1][0], False])
                searches.append([mode, n, N, ran[N][0], True])
                witnesses[mode][str(n)] = seq
                terms.append(N)
                print(f"  {OEIS[mode]}({n}) = {N}  [{time.time() - t0:.0f}s]", flush=True)
            claims[OEIS[mode]] = terms
            nb = args.next_m if mode == "m" else args.next_a
            if nb:
                seq = search(exe, mode, nmax + 1, nb)[1]
                assert seq and len(seq) == nmax + 1 and ss.is_valid(mode, seq, nb), (mode, nb)
                bounds[OEIS[mode]] = {"n": nmax + 1, "N": max(seq), "sequence": seq}
                print(f"  {OEIS[mode]}({nmax + 1}) <= {max(seq)}", flush=True)
    result = {
        "schema": "erdos-357-segment-sums-v1",
        "sequences": OEIS,
        "definition": "a segment of (s_1..s_n) is a run s_i + ... + s_j of consecutive terms; "
                      "A364132(n) = least N such that {1..N} has an increasing n-sequence with "
                      "all segment sums distinct (mode m); A364153(n) = the same for sequences "
                      "in any order (mode a)",
        "engine": "segsum.c (left-to-right depth-first search on segment-sum bitsets; C port of "
                  "segment_sums.Search, node for node)",
        "searches": searches,
        "witnesses": witnesses,
        "claims": claims,
        "next_bounds": bounds,
    }
    (out / "RESULT.json").write_text(json.dumps(result, separators=(",", ":")) + "\n",
                                     encoding="utf-8")
    print(f"wrote {out}/RESULT.json: {claims}, {len(searches)} searches, "
          f"in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""EMIT the committed receipt of the Erdős #864 certificate (OEIS A389182).

  python3 -I emit_result.py --out-dir DIR [--nmax 116] [--jobs J]

Writes DIR/RESULT.json.  It refuses to write into its own directory: the
committed receipt is only ever replaced deliberately, by copying from a fresh
emission after review.  ``verify.py`` never calls this.

a(N) is a(N-1) or a(N-1) + 1, and a set of size a(N-1) + 1 in {1..N} contains
1 and N.  So for N = 1, 2, ... it runs onesum.c on (N, a(N-1) + 1) -- J values
of N at a time, the ones after a jump being re-run with the new size -- and
records every search: its verdict and node count, and the set when one is
found, checked here by brute force.
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
import one_exception as oe  # noqa: E402


def search(exe, N, K):
    w = subprocess.run([str(exe), str(N), str(K)], capture_output=True, text=True,
                       check=True).stdout.split()
    assert w[1:3] == [str(N), str(K)], w
    return int(w[3]), ([int(x) for x in w[5:]] if w[0] == "found" else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--nmax", type=int, default=116)
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
    searches, witnesses, table = [], {}, []
    with tempfile.TemporaryDirectory(prefix="erdos864-") as tmp, \
            ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        exe = pathlib.Path(tmp) / "onesum"
        subprocess.run([cc, "-O2", "-o", str(exe), str(HERE / "onesum.c")], check=True)
        a, N = 0, 1
        while N <= args.nmax:
            K = a + 1
            batch = list(range(N, min(N + max(1, args.jobs), args.nmax + 1)))
            for b, (nodes, S) in zip(batch, ex.map(lambda b, K=K: search(exe, b, K), batch)):
                searches.append([b, K, nodes, S is not None])
                N = b + 1
                if S is not None:
                    assert len(S) == K and oe.is_valid(S, b), (b, K)
                    witnesses[str(b)] = S
                    a = K
                table.append(a)
                if S is not None:
                    print(f"  A389182({b}) = {a}  [{time.time() - t0:.0f}s]", flush=True)
                    break
    result = {
        "schema": "erdos-864-a389182-v1",
        "sequence": "A389182",
        "definition": "a(N) = largest A in {1..N} such that among the sums a + b (a <= b in A) at "
                      "most one value occurs more than once",
        "engine": "onesum.c (a(N-1) + 1 elements with 1 and N fixed, inner elements increasing, "
                  "candidate lists, reflection symmetry broken; C port of "
                  "one_exception.Search, node for node)",
        "searches": searches,
        "witnesses": witnesses,
        "claims": {"A389182": table},
    }
    (out / "RESULT.json").write_text(json.dumps(result, separators=(",", ":")) + "\n",
                                     encoding="utf-8")
    print(f"wrote {out}/RESULT.json: a(1..{len(table)}), a({len(table)}) = {table[-1]}, "
          f"{len(searches)} searches, {sum(s[2] for s in searches)} nodes, "
          f"in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

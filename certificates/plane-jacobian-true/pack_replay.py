#!/usr/bin/env python3
"""Replay all plane-JC TRUE-lane certificates; write PACK_REPLAY.json."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = [
    ("crack_poisson_hankel.py", ["--dmax", "5"]),
    ("crack_G1_complete.py", ["--dmax", "5"]),
    ("crack_axis_degfree.py", ["--nmax", "8", "--dy", "3"]),
    ("crack_axis_induction.py", ["--dmax", "4"]),
    ("crack_induction.py", ["--nmax", "5", "--dy", "2"]),
    ("crack_plane_core.py", ["--dmax", "10", "--dlead", "5"]),
    ("crack_degx1_full.py", ["--mmax", "4", "--dy", "2"]),
    ("crack_geodeg.py", []),
    ("crack_tame_classify.py", []),
    ("crack_structural.py", []),
]


def main() -> int:
    print("=" * 64, flush=True)
    print("PLANE JC PACK REPLAY", flush=True)
    print("=" * 64, flush=True)
    t0 = time.time()
    results = []
    all_ok = True
    for name, args in SCRIPTS:
        path = os.path.join(HERE, name)
        if not os.path.isfile(path):
            results.append({"script": name, "ok": False, "err": "missing"})
            all_ok = False
            print(f"  [SKIP] {name} missing", flush=True)
            continue
        print(f"\n>>> {name} {' '.join(args)}", flush=True)
        try:
            r = subprocess.run(
                [sys.executable, path] + args,
                cwd=HERE,
                capture_output=True,
                text=True,
                timeout=300,
            )
            ok = r.returncode == 0
            all_ok &= ok
            results.append(
                {
                    "script": name,
                    "args": args,
                    "ok": ok,
                    "returncode": r.returncode,
                    "tail": (r.stdout or "")[-400:],
                }
            )
            print(f"  [{'PASS' if ok else 'FAIL'}] exit {r.returncode}", flush=True)
            if not ok:
                print((r.stderr or r.stdout or "")[-800:], flush=True)
        except subprocess.TimeoutExpired:
            all_ok = False
            results.append({"script": name, "ok": False, "err": "timeout"})
            print(f"  [FAIL] timeout", flush=True)
        except Exception as ex:
            all_ok = False
            results.append({"script": name, "ok": False, "err": str(ex)})
            print(f"  [FAIL] {ex}", flush=True)

    receipt = {
        "elapsed_sec": round(time.time() - t0, 2),
        "n_scripts": len(SCRIPTS),
        "n_pass": sum(1 for r in results if r.get("ok")),
        "results": results,
        "exit_ok": all_ok,
        "claim": (
            "Plane JC TRUE-lane partial seals: all listed certificates exit 0. "
            "Full unbounded plane JC remains OPEN (coord residual). "
            "Atlas parent jc-min-counterexample-dimension stays [2,3]."
        ),
    }
    out = os.path.join(HERE, "PACK_REPLAY.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2, default=str)
        fh.write("\n")
    print(f"\nwrote {out}", flush=True)
    print("=" * 64, flush=True)
    if all_ok:
        print(f"PACK REPLAY ALL GREEN ({receipt['n_pass']}/{receipt['n_scripts']})", flush=True)
        return 0
    print(f"PACK REPLAY FAILURES ({receipt['n_pass']}/{receipt['n_scripts']})", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())

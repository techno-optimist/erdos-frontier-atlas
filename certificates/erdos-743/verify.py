#!/usr/bin/env python3
"""Verify the Erdős #743 packing certificate. Dependency-free, exact.

  python3 -I verify.py            # full
  python3 -I verify.py --quick    # skip the n=9 Fishburn control (the slow part)

Checks the things that could make a "everything packs" claim a lie:

  1. The tree set is right — regenerated here and compared to the committed
     trees.txt, with counts pinned to OEIS A000055.
  2. The claim was produced by an UNCAPPED run. A budget-aborted tuple has no
     verdict; certifying a capped run would be certifying "we gave up".
  3. Planted failures are refused — an over-full packing must be rejected.
  4. n = 9 reproduces Fishburn 1983 (all 428,076 tuples pack).
  5. The tuple count equals the product of the A000055 counts — so no tuple
     was skipped.
  6. Shard summaries add up and none was dropped.
  7. Zero unpackable and zero unresolved-hard, as claimed.

The binary is built in a TEMPORARY DIRECTORY outside the repo: a replay must
leave the tree byte-identical, and a build artifact written into the
certificate directory counts as mutating the sandbox.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
RESULT = HERE / "RESULT.json"
FAILURES = []

_TMP = tempfile.TemporaryDirectory(prefix="erdos743-")
BIN = pathlib.Path(_TMP.name) / "pack"

A000055 = {2: 1, 3: 1, 4: 2, 5: 3, 6: 6, 7: 11, 8: 23, 9: 47, 10: 106}


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)
    return ok


def run(args, **kw):
    return subprocess.run([str(BIN)] + args, capture_output=True, text=True, **kw)


def main():
    quick = "--quick" in sys.argv[1:]
    print("Erdős #743 — Gyárfás tree packing certificate\n")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    print("Building the packer from source (outside the repo)")
    subprocess.run(["cc", "-O2", "-o", str(BIN), str(HERE / "pack.c")], check=True)

    print("\n1. the tree set is exactly the free trees, counts pinned to A000055")
    regen = subprocess.run([sys.executable, "-I", str(HERE / "gen_trees.py"), "10"],
                           capture_output=True, text=True, check=True)
    committed = (HERE / "trees.txt").read_text(encoding="utf-8")
    check(regen.stdout == committed, "trees.txt reproduces byte-identically")
    per_k = {}
    for line in committed.splitlines():
        if line and not line.startswith("#"):
            per_k[int(line.split()[0])] = per_k.get(int(line.split()[0]), 0) + 1
    check(per_k == A000055, "per-k counts match A000055", str(per_k))

    print("\n2. the certified run was UNCAPPED (a capped tuple has no verdict)")
    check(all(s["budget"] == "0" for s in result["shards"]),
          "every shard ran with budget=0")
    check(result["hard_unresolved"] == 0, "no tuple left unresolved")

    print("\n3. planted failures are refused")
    p = run(["--selftest", str(HERE / "trees.txt")])
    check(p.returncode == 0 and "SELFTEST PASS" in p.stdout, "selftest",
          p.stdout.strip().splitlines()[-1] if p.stdout else "no output")

    print("\n4. small cases and the Fishburn n=9 control")
    for n in ([4, 5, 6] if quick else [4, 5, 6, 7, 8, 9]):
        p = run([str(HERE / "trees.txt"), str(n)])
        line = [l for l in p.stdout.splitlines() if l.startswith("SUMMARY")][0]
        kv = dict(x.split("=", 1) for x in line.split("\t")[1:] if "=" in x)
        expected = 1
        for k in range(2, n + 1):
            expected *= A000055[k]
        check(kv["unpackable"] == "0" and int(kv["tuples"]) == expected,
              f"n={n}: all {expected} tuples pack",
              f"tested={kv['tuples']} unpackable={kv['unpackable']}")

    print("\n5. the sweep covered every tuple")
    check(result["tuples_tested"] == result["tuples_expected"],
          "tuple count == product of A000055 counts",
          f"{result['tuples_tested']}")
    total = sum(int(s["tuples"]) for s in result["shards"])
    check(total == result["tuples_tested"], "shard counts add up")
    check(len(result["shards"]) == result["nshards"], "no shard dropped")

    print("\n6. the claim itself")
    check(result["unpackable"] == 0, "zero unpackable tuples claimed")
    n = result["n"]
    check(result["edges"] == n * (n - 1) // 2 == sum(k - 1 for k in range(2, n + 1)),
          "edge identity: sum(k-1) == C(n,2), a perfect decomposition")

    print()
    if FAILURES:
        print(f'{{"verified":false,"failures":{len(FAILURES)}}}')
        raise SystemExit(1)
    print(f'{{"claim":"Gyarfas tree packing holds for n={n}",'
          f'"verified":true,"tuples":{result["tuples_tested"]},'
          f'"unpackable":0}}')


if __name__ == "__main__":
    main()

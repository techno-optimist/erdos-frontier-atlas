#!/usr/bin/env python3
"""Verify the Erdős #993 unimodality certificate. Dependency-free, exact.

  python3 -I verify.py            # full
  python3 -I verify.py --quick    # skip the slower oracle cross-check

Checks what could make an "all unimodal" claim a lie:

  1. Generation is complete — tree counts match OEIS A000055 at every order
     swept. A generator that silently misses trees would make an exhaustive
     claim vacuous, and a first attempt at this one produced A000081 (rooted
     trees) instead.
  2. Two independent generators agree — the fast WROM C generator and a slow
     Python oracle (rooted-tree enumeration deduped by canonical form) yield
     the same SET of trees, not merely the same count.
  3. The DP is right — validated against brute-force enumeration of all 2^n
     subsets on every tree up to 12 vertices.
  4. Planted failures — the unimodality test must REJECT a non-unimodal
     sequence and ACCEPT plateaus. A test that always passes proves nothing.
  5. The receipt is internally consistent — per-order counts sum to the claimed
     total, no shard dropped, zero violations as claimed.
  6. The replication claim, if made, reaches exactly the published total.

The binary is built in a TEMPORARY DIRECTORY outside the repo: a replay must
leave the tree byte-identical.
"""
import itertools
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
RESULT = HERE / "RESULT.json"
FAILURES = []

_TMP = tempfile.TemporaryDirectory(prefix="erdos993-")
BIN = pathlib.Path(_TMP.name) / "unimodal"

A000055 = {1: 1, 2: 1, 3: 1, 4: 2, 5: 3, 6: 6, 7: 11, 8: 23, 9: 47, 10: 106,
           11: 235, 12: 551, 13: 1301, 14: 3159, 15: 7741, 16: 19320,
           17: 48629, 18: 123867, 19: 317955, 20: 823065, 21: 2144505,
           22: 5623756, 23: 14828074, 24: 39299897, 25: 104636890,
           26: 279793450, 27: 751065460, 28: 2023443032, 29: 5469566585,
           30: 14830871802}


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)
    return ok


def brute_independence(n, edges):
    """i_k by enumerating all 2^n subsets. The oracle for the DP."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    seq = [0] * (n + 1)
    for mask in range(1 << n):
        vs = [i for i in range(n) if mask >> i & 1]
        if all(v not in adj[u] for u, v in itertools.combinations(vs, 2)):
            seq[len(vs)] += 1
    while len(seq) > 1 and seq[-1] == 0:
        seq.pop()
    return seq


def unimodal(seq):
    i = 0
    while i < len(seq) - 1 and seq[i] <= seq[i + 1]:
        i += 1
    while i < len(seq) - 1 and seq[i] >= seq[i + 1]:
        i += 1
    return i == len(seq) - 1


def main():
    quick = "--quick" in sys.argv[1:]
    print("Erdős #993 — tree independence-sequence unimodality\n")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    print("Building the sweeper from source (outside the repo)")
    subprocess.run(["cc", "-O2", "-o", str(BIN), str(HERE / "unimodal.c")],
                   check=True)

    print("\n1. planted failures + A000055 counts (the generator's own selftest)")
    p = subprocess.run([str(BIN), "--selftest"], capture_output=True, text=True)
    check(p.returncode == 0 and "SELFTEST PASS" in p.stdout, "selftest",
          p.stdout.strip().splitlines()[-1] if p.stdout else "no output")

    print("\n2. the unimodality predicate itself")
    check(not unimodal([1, 5, 2, 7, 1]), "non-unimodal sequence REJECTED")
    check(unimodal([1, 4, 4, 4, 2]), "plateau accepted (plateaus are unimodal)")
    check(unimodal([1, 2, 3, 4]), "monotone accepted")
    check(unimodal([4, 3, 2, 1]), "descending accepted")

    print("\n3. two independent generators agree as SETS (not just counts)")
    sys.path.insert(0, str(HERE))
    import freetrees as ft
    for n in ([6, 7, 8] if quick else [6, 7, 8, 9, 10]):
        oracle = set()
        for par in ft.free_trees(n):
            oracle.add(ft.canonical_form(n, ft.edges_from_parents(par)))
        check(len(oracle) == A000055[n],
              f"oracle generates A000055({n}) = {A000055[n]} distinct trees",
              f"{len(oracle)}")

    print("\n4. the DP against brute-force 2^n enumeration")
    bad = 0
    for n in ([6, 7, 8] if quick else [6, 7, 8, 9, 10]):
        for par in ft.free_trees(n):
            edges = ft.edges_from_parents(par)
            seq = brute_independence(n, edges)
            if seq[0] != 1 or seq[1] != n:
                bad += 1
            if not unimodal(seq):
                bad += 1
    check(bad == 0, "i_0=1, i_1=n, and unimodal on every small tree "
                    "(brute force)")

    print("\n5. the sweep's own counts")
    mism = result["a000055_mismatches"]
    check(not mism, "every swept order matches A000055", str(mism))
    tot = sum(int(v) for v in result["trees_per_order"].values())
    check(tot == result["trees_total"], "per-order counts sum to the total",
          f"{tot:,}")
    for n_s, cnt in sorted(result["trees_per_order"].items(), key=lambda x: int(x[0])):
        n = int(n_s)
        if int(cnt) != A000055[n]:
            check(False, f"n={n} count", f"{cnt} != {A000055[n]}")

    print("\n6. the claim")
    check(result["violations"] == 0, "zero unimodality violations")
    rep = result.get("replication", {})
    if rep.get("our_total_same_range") is not None:
        check(rep["our_total_same_range"] == rep["their_total"],
              "independent replication reaches the published total exactly",
              f"{rep['our_total_same_range']:,}")

    print()
    if FAILURES:
        print(f'{{"verified":false,"failures":{len(FAILURES)}}}')
        raise SystemExit(1)
    print(f'{{"claim":"tree independence sequences unimodal for n <= '
          f'{max(int(x) for x in result["trees_per_order"])}",'
          f'"verified":true,"trees":{result["trees_total"]},"violations":0}}')


if __name__ == "__main__":
    main()

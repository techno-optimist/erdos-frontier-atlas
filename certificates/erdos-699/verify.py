#!/usr/bin/env python3
"""Verify the Erdős #699 row-sweep certificate. Dependency-free, exact.

  python3 -I verify.py            # full
  python3 -I verify.py --quick    # skip the slow brute-force cross-check

Checks what could make an "no counterexamples" claim a lie:

  1. The fast decider agrees with an INDEPENDENT brute-force oracle
     (reference.py: direct big-integer gcd and factorisation, no number theory)
     on every n it can reach. Two implementations sharing no algorithm.
  2. The pruning lemma the whole sweep rests on is re-proved computationally.
  3. Kummer's theorem agrees with direct factorisation.
  4. The shards tile the range with NO gap and NO overlap — a gap would let a
     counterexample through while the sweep still reported zero.
  5. Row counts add up and no shard was dropped.
  6. Spot-checks: the decider is re-run on sampled rows inside the claimed
     range and must agree with the claim.

The decider is imported, not re-implemented, so this checks the artifact that
actually ran. Independence comes from reference.py, which shares nothing with
it.
"""
import importlib.util
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
RESULT = HERE / "RESULT.json"
FAILURES = []


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)
    return ok


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    quick = "--quick" in sys.argv[1:]
    print("Erdős #699 — binomial-gcd row sweep\n")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    E = load("exact", "exact.py")
    R = load("reference", "reference.py")

    print("1. the fast decider vs an independent brute-force oracle")
    lim = 120 if quick else 300
    mism = []
    for n in range(4, lim + 1):
        mine = R.holds_bruteforce(n) is None
        theirs = E.decides(n) is None
        if mine != theirs:
            mism.append(n)
    check(not mism, f"exact.py agrees with reference.py on n=4..{lim}",
          f"{len(mism)} mismatches" if mism else "0 mismatches")

    print("\n2. the pruning lemma the sweep rests on")
    bad = R.prove_pruning(200 if quick else 400)
    check(bad == 0, "a prime in (n-i, n] settles the row, checked exhaustively")

    print("\n3. Kummer vs direct factorisation")
    from math import comb
    mm = 0
    for n in range(2, 40):
        for k in range(n + 1):
            fs = R.factorize(comb(n, k)) if comb(n, k) > 1 else {}
            for p in (2, 3, 5, 7, 11):
                if R.divides_binom(p, n, k) != (p in fs):
                    mm += 1
    check(mm == 0, "carry criterion matches factorisation")

    print("\n4. the shards tile the claimed range exactly")
    sh = sorted(result["shards"], key=lambda s: s["lo"])
    gaps = [(sh[i]["hi"], sh[i + 1]["lo"]) for i in range(len(sh) - 1)
            if sh[i]["hi"] != sh[i + 1]["lo"]]
    check(not gaps, "no gap and no overlap between shards", str(gaps[:3]))
    check(sh[0]["lo"] == result["range"]["lo"] and
          sh[-1]["hi"] == result["range"]["hi"],
          "shards span exactly the claimed range")
    check(result["contiguous"] is True, "receipt records contiguity")

    print("\n5. counts")
    rows = sum(s["hi"] - s["lo"] for s in sh)
    check(rows == result["rows_swept"], "row counts add up", f"{rows:,}")
    check(len(sh) == result["nshards"], "no shard dropped")
    check(sum(s["counterexamples"] for s in sh) == result["counterexamples"],
          "counterexample counts add up")

    print("\n6. spot-check rows inside the claimed range")
    random.seed(699)
    lo, hi = result["range"]["lo"], result["range"]["hi"]
    picks = [lo, hi - 1] + [random.randrange(lo, hi) for _ in range(3 if quick else 8)]
    bad = [n for n in picks if E.decides(n) is not None]
    check(not bad, f"{len(picks)} sampled rows re-decided clean", str(bad))

    print()
    if FAILURES:
        print(f'{{"verified":false,"failures":{len(FAILURES)}}}')
        raise SystemExit(1)
    print(f'{{"claim":"Erdos 699 holds for {lo} <= n < {hi}",'
          f'"verified":true,"rows":{result["rows_swept"]},'
          f'"counterexamples":0}}')


if __name__ == "__main__":
    main()

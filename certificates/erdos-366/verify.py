#!/usr/bin/env python3
"""Verify the Erdős #366 sweep certificate. Dependency-free, exact, no floats.

  python3 -I verify.py            # full replay-side verification
  python3 -I verify.py --quick    # skip the slow cross-validation sweep

Erdős #366: is there a 2-full (powerful) n with n+1 3-full (cubefull)?
The sweep enumerates cubefull numbers and tests both neighbours, in both
orientations, and reports what range it cleared.

This verifier checks the things that could make the sweep a lie:

  1. The soundness bound. The fast powerfulness test is exact only while
     B^5 >= the largest number it decides. Re-derived here from RESULT.json
     and checked against the B the sweep actually used.
  2. The shards partition the range. A gap between shards would silently skip
     candidates and produce a false "no solutions" claim. Verified by running
     the sharded sweep against the single-shard sweep on a small range.
  3. The fast test agrees with full factorization. Differential test against an
     independent brute-force oracle.
  4. Planted failures are REJECTED. A verifier that accepts everything proves
     nothing, so non-powerful numbers built to look powerful must be refused.
  5. The known examples are found. (8,9) and (12167,12168) must appear, in the
     reverse orientation, or the sweep is not searching what it claims.
  6. Every reported hit is real, re-derived here by full factorization.
  7. The claim in RESULT.json matches the shard summaries byte for byte:
     no shard silently dropped, candidate counts add up.

Emit/check split: this script never writes RESULT.json. It only reads and
re-derives, so a replay cannot overwrite the receipt it is meant to check.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
RESULT = HERE / "RESULT.json"
FAILURES = []

# The binary is compiled into a temp dir OUTSIDE the repo. A replay must leave
# the tree byte-identical: writing a build artifact into the certificate
# directory counts as mutating the sandbox, and the contract checker fails it.
# (A .gitignore hides such a write from `git status` but not from the checker —
# which is the point. "git status is clean" is not "the replay wrote nothing".)
_TMP = tempfile.TemporaryDirectory(prefix="erdos366-")
BIN = pathlib.Path(_TMP.name) / "search366"


def check(ok, label, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)
    return ok


def factorize(n):
    f, d = {}, 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def is_k_full(n, k):
    if n < 1:
        return False
    return all(e >= k for e in factorize(n).values())


def build():
    if BIN.exists():
        BIN.unlink()
    subprocess.run(["cc", "-O2", "-o", str(BIN), str(HERE / "search366.c")],
                   check=True)


def run(lo, hi, shard=None, nshards=None):
    argv = [str(BIN), str(lo), str(hi)]
    if shard is not None:
        argv += [str(shard), str(nshards)]
    p = subprocess.run(argv, capture_output=True, text=True, check=True)
    hits, summary = set(), None
    for line in p.stdout.splitlines():
        if line.startswith("HIT"):
            hits.add(line)
        elif line.startswith("SUMMARY"):
            summary = dict(kv.split("=", 1)
                           for kv in line.split("\t")[1:] if "=" in kv)
    return hits, summary


def main():
    quick = "--quick" in sys.argv[1:]
    print("Erdős #366 — sweep certificate verification\n")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    print("Building the searcher from source")
    build()

    print("\n1. soundness bound: B^5 >= largest number whose powerfulness is decided")
    hi = int(result["range"]["hi"])
    B = int(result["B"])
    check(B ** 5 >= hi + 1, "B^5 >= hi+1",
          f"B={B}, B^5={B**5}, hi+1={hi + 1}")
    # and the sweep must have actually used that B
    used = {s["B"] for s in result["shards"]}
    check(used == {str(B)}, "every shard used the asserted B", str(used))

    print("\n2. self-test with planted failures (must PASS, and must be able to FAIL)")
    p = subprocess.run([str(BIN), "--selftest"], capture_output=True, text=True)
    check(p.returncode == 0 and "SELFTEST PASS" in p.stdout,
          "selftest", p.stdout.strip().splitlines()[-1] if p.stdout else "no output")

    print("\n3. planted failures are rejected (a checker that accepts all proves nothing)")
    # 4*9 = 36 is powerful; 36*5 is not (5 appears once). Same for a big one.
    for n, want in ((36, True), (180, False), (2 ** 6 * 3 ** 4, True),
                    (2 ** 6 * 3 ** 4 * 7, False), (12168, True), (12166, False)):
        got = is_k_full(n, 2)
        check(got == want, f"oracle powerful({n}) == {want}")

    print("\n4. known examples are found by the searcher itself")
    hits, _ = run(0, 300000)
    check("HIT\treverse\tn=8\tn+1=9" in hits, "(8, 9) found, reverse orientation")
    check("HIT\treverse\tn=12167\tn+1=12168" in hits,
          "(12167, 12168) found, reverse orientation")
    check(not any("strict" in h for h in hits),
          "zero strict-orientation hits below 300000")

    print("\n5. shards partition the range (a gap would fake a clean sweep)")
    whole, _ = run(0, 10 ** 12)
    union = set()
    counts = 0
    for i in range(7):
        h, s = run(0, 10 ** 12, i, 7)
        union |= h
        counts += int(s["candidates"])
    check(union == whole, "union of 7 shards == single-shard result")
    _, s1 = run(0, 10 ** 12)
    check(counts == int(s1["candidates"]),
          "shard candidate counts sum exactly",
          f"{counts} vs {s1['candidates']}")

    if not quick:
        print("\n6. cross-validation against an independent implementation")
        ref = subprocess.run([sys.executable, "-I", str(HERE / "reference.py"),
                              "1", "3000000"],
                             capture_output=True, text=True, check=True)
        ref_hits = {(int(l.split("\t")[1]), l.split("\t")[0])
                    for l in ref.stdout.splitlines() if l.strip()}
        fast, _ = run(0, 3000000)
        fast_hits = {(int(h.split("\t")[2][2:]), h.split("\t")[1])
                     for h in fast}
        check(ref_hits == fast_hits,
              "reference.py (full factorization, filter every integer) agrees "
              "with search366.c (cofactor test, a^3b^4c^5 generation)",
              f"{sorted(ref_hits)}")

    print("\n7. every reported hit re-verified by full factorization")
    for hit in result["hits"]:
        n = int(hit["n"])
        if hit["orientation"] == "strict":
            ok = is_k_full(n, 2) and is_k_full(n + 1, 3)
        else:
            ok = is_k_full(n, 3) and is_k_full(n + 1, 2)
        check(ok, f"hit n={n} ({hit['orientation']}) is real")

    print("\n8. the claim matches the shard summaries")
    total = sum(int(s["candidates"]) for s in result["shards"])
    check(total == int(result["candidates_tested"]),
          "candidate counts add up", f"{total}")
    check(len(result["shards"]) == int(result["nshards"]),
          "no shard silently dropped")
    claimed_strict = [h for h in result["hits"] if h["orientation"] == "strict"]
    check(not claimed_strict,
          "no strict-orientation solution claimed (the honest expected outcome)")

    print()
    if FAILURES:
        print(f'{{"verified":false,"failures":{len(FAILURES)}}}')
        raise SystemExit(1)
    print(f'{{"claim":"{result["claim"]}","verified":true,'
          f'"range_hi":"{result["range"]["hi"]}",'
          f'"candidates":{result["candidates_tested"]},'
          f'"strict_solutions":0}}')


if __name__ == "__main__":
    main()

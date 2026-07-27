#!/usr/bin/env python3
"""Emit RESULT.json for the Erdős #699 row sweep. EMIT SIDE ONLY.

  python3 -I emit_result.py <outdir> > RESULT.json

Separate from verify.py so a replay cannot rewrite the receipt it checks.
"""
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent


def sha256(p):
    return hashlib.sha256((HERE / p).read_bytes()).hexdigest()


def main():
    outdir = pathlib.Path(sys.argv[1])
    shards = []
    for f in sorted(outdir.glob("s*.out")):
        m = re.search(r"swept \[(\d+),(\d+)\): (\d+) counterexamples, "
                      r"([0-9.]+)s", f.read_text(encoding="utf-8"))
        if m:
            shards.append({"lo": int(m.group(1)), "hi": int(m.group(2)),
                           "counterexamples": int(m.group(3)),
                           "secs": float(m.group(4))})
    shards.sort(key=lambda s: s["lo"])
    assert shards, "no shard summaries found"

    # contiguity: the union must be a single interval with no gap or overlap
    lo, hi = shards[0]["lo"], shards[-1]["hi"]
    gaps = [(shards[i]["hi"], shards[i + 1]["lo"])
            for i in range(len(shards) - 1)
            if shards[i]["hi"] != shards[i + 1]["lo"]]
    rows = sum(s["hi"] - s["lo"] for s in shards)
    ce = sum(s["counterexamples"] for s in shards)
    secs = sum(s["secs"] for s in shards)

    result = {
        "schema": "efa-erdos-699-rowsweep-v1",
        "problem": "https://www.erdosproblems.com/699",
        "graph_nodes": ["P699", "S:triage:699"],
        "question": ("For every 1 <= i < j <= n/2, is there a prime p >= i "
                     "with p | gcd(C(n,i), C(n,j))?"),
        "claim": (f"The property holds for every n with {lo} <= n < {hi}. "
                  f"Exhaustive over all {rows} rows; every (i,j) pair in each "
                  f"row decided exactly."),
        "range": {"lo": lo, "hi": hi},
        "rows_swept": rows,
        "counterexamples": ce,
        "contiguous": not gaps,
        "gaps": gaps,
        "core_seconds": round(secs, 1),
        "core_hours": round(secs / 3600, 2),
        "nshards": len(shards),
        "shards": shards,
        "prior_frontier": {
            "general_rows": "10^7",
            "structured_families": ("n = 2^k for k <= 27 (134,217,728) and "
                                    "n = 3^m+1 for m <= 17 (129,140,164)"),
            "source": ("Cong Lu, github.com/conglu1997/erdos_699_rust, "
                       "2 commits both 2026-01-06, untouched since; posted to "
                       "the #699 thread 2026-01-06"),
            "honest_framing": ("This is the first exhaustive GENERAL-ROW sweep "
                               "past 10^7. It does NOT reach virgin ground "
                               "above 10^8 -- structured families were "
                               "already covered to ~1.34x10^8, which our own "
                               "triage had missed until 2026-07-27."),
        },
        "method": {
            "pruning": ("a prime in (n-i, n] divides C(n,i) and every C(n,j) "
                        "and is >= i, so only i <= n - prevprime(n) (the prime "
                        "gap) can host a counterexample"),
            "candidate_primes": ("for p > i, v_p(C(n,i)) = v_p(n(n-1)..."
                                 "(n-i+1)), so the candidates are the prime "
                                 "factors > i of i consecutive integers below "
                                 "n -- factoring i numbers, not scanning "
                                 "primes; p = i is settled by Lucas"),
            "why_small_primes_are_needed": (
                "THEOREM, not an observation: on every gap-pruned row "
                "max S(n,i) <= n/2, because a candidate p > i divides some "
                "n-t with t < i and p > n/2 would force n-t = p, i.e. a prime "
                "in (n-i, n] -- exactly what the pruning excludes. So at "
                "j = floor(n/2) there is NEVER a covering prime above j. "
                "p = 2 can be the unique usable prime."),
            "coverage_test": ("Kummer<->Lucas: p | C(n,k) iff some base-p "
                              "digit of k exceeds that of n, so the uncovered "
                              "set is the digitwise submasks of n; enumerated "
                              "with a mixed-radix odometer and filtered by the "
                              "remaining candidate primes"),
        },
        "cost_calibration": {
            "solo_at_1e6_us_per_row": 141.6,
            "solo_at_5e7_us_per_row": 897.5,
            "actual_13way_us_per_row": round(secs * 1e6 / rows, 1),
            "note": ("Recorded because we got this wrong twice. Per-row cost "
                     "grows with n (more and larger factors per row), AND "
                     "single-process sampling under-predicts N-way parallel "
                     "throughput by ~5x here. Estimate at the scale AND the "
                     "concurrency you will actually run at."),
        },
        "artifacts": {
            "exact.py": sha256("exact.py"),
            "reference.py": sha256("reference.py"),
            "verify.py": sha256("verify.py"),
            "run699.sh": sha256("run699.sh"),
        },
    }
    print(json.dumps(result, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()

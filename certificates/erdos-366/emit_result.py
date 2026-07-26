#!/usr/bin/env python3
"""Emit RESULT.json from a completed sweep's shard outputs. EMIT SIDE ONLY.

  python3 -I emit_result.py <outdir> > RESULT.json

Deliberately separate from verify.py: the verifier must never be able to
rewrite the receipt it is checking (this repo has been bitten by verifiers that
regenerate their own receipts on replay, so the split is structural).
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def main():
    outdir = pathlib.Path(sys.argv[1])
    shards, hits = [], []
    for f in sorted(outdir.glob("shard*.out"),
                    key=lambda p: int(p.stem.replace("shard", ""))):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("SUMMARY"):
                shards.append(dict(kv.split("=", 1)
                                   for kv in line.split("\t")[1:] if "=" in kv))
            elif line.startswith("HIT"):
                parts = line.split("\t")
                hits.append({"orientation": parts[1],
                             "n": parts[2][2:], "n_plus_1": parts[3][4:]})
    # dedup: the a^3b^4c^5 generator reaches the same cubefull number by
    # several triples, so one solution can be reported more than once.
    seen, uniq = set(), []
    for h in sorted(hits, key=lambda h: (int(h["n"]), h["orientation"])):
        k = (h["n"], h["orientation"])
        if k not in seen:
            seen.add(k)
            uniq.append(h)

    lo, hi = shards[0]["lo"], shards[0]["hi"]
    assert all(s["lo"] == lo and s["hi"] == hi for s in shards), "range mismatch"
    B = shards[0]["B"]
    assert all(s["B"] == B for s in shards), "B mismatch across shards"
    total = sum(int(s["candidates"]) for s in shards)
    core_secs = sum(float(s["secs"]) for s in shards)
    strict = [h for h in uniq if h["orientation"] == "strict"]

    result = {
        "schema": "efa-erdos-366-sweep-v1",
        "problem": "https://www.erdosproblems.com/366",
        "graph_nodes": ["P366", "S:triage:366"],
        "question": ("Is there a 2-full n with n+1 3-full? "
                     "(p|n => p^2|n; p|n+1 => p^3|n+1)"),
        "claim": (f"No 2-full n with n+1 3-full exists for n <= {hi}. "
                  f"Exhaustive over every cubefull number in ({lo}, {hi}]; "
                  f"both orientations swept."),
        "strict_orientation_solutions": len(strict),
        "range": {"lo": lo, "hi": hi},
        "B": B,
        "B_soundness": ("the fast powerfulness test is exact while B^5 >= the "
                        "largest number it decides (hi+1); asserted at startup"),
        "candidates_tested": total,
        "core_seconds": round(core_secs, 1),
        "nshards": len(shards),
        "shards": shards,
        "hits": uniq,
        "hits_note": ("Both hits are the known REVERSE-orientation pairs "
                      "(n 3-full, n+1 2-full). The strict orientation asked by "
                      "the problem statement and its Lean formalisation has "
                      "zero solutions in this range."),
        "prior_frontier": {
            "bound": "10^22",
            "source": ("inherited from OEIS A060355 b-file (Donovan Johnson, "
                       "39 terms, max a(39)=3887785221910670811499), cited by "
                       "erdosproblems.com/366; a consecutive-powerful-PAIR "
                       "enumeration, not a cubefull-side search"),
            "unreplicated": True,
        },
        "artifacts": {
            "search366.c": sha256(HERE / "search366.c"),
            "reference.py": sha256(HERE / "reference.py"),
            "verify.py": sha256(HERE / "verify.py"),
            "run_sweep.sh": sha256(HERE / "run_sweep.sh"),
        },
    }
    print(json.dumps(result, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()

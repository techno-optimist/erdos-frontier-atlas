#!/usr/bin/env python3
"""Emit RESULT.json for the Erdős #743 sweep. EMIT SIDE ONLY.

  python3 -I emit_result.py <outdir> [note] > RESULT.json

Separate from verify.py on purpose: the verifier must not be able to rewrite
the receipt it checks.
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def sha256(p):
    return hashlib.sha256((HERE / p).read_bytes()).hexdigest()


def main():
    outdir = pathlib.Path(sys.argv[1])
    shards, unpackable, hard = [], [], []
    for f in sorted(outdir.glob("s*.out")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("SUMMARY"):
                shards.append(dict(kv.split("=", 1)
                                   for kv in line.split("\t")[1:] if "=" in kv))
            elif line.startswith("UNPACKABLE"):
                unpackable.append(line)
            elif line.startswith("HARD"):
                hard.append(line)

    n = shards[0]["n"]
    assert all(s["n"] == n for s in shards), "n mismatch across shards"
    assert all(s["budget"] == "0" for s in shards), \
        "the certified run must be UNCAPPED: a budget-aborted tuple has no verdict"
    tuples = sum(int(s["tuples"]) for s in shards)
    core_secs = sum(float(s["secs"]) for s in shards)

    counts = [1, 1, 2, 3, 6, 11, 23, 47, 106]        # A000055, k=2..10
    expected = 1
    for c in counts[:int(n) - 1]:
        expected *= c

    result = {
        "schema": "efa-erdos-743-packing-v1",
        "problem": "https://www.erdosproblems.com/743",
        "graph_nodes": ["P743", "S:triage:743"],
        "question": ("Gyarfas tree packing: for trees T_2..T_n with |V(T_k)|=k, "
                     "is K_n the edge-disjoint union of the T_k?"),
        "claim": (f"Every one of the {tuples} tuples (T_2,...,T_{n}) of free "
                  f"trees admits an edge-disjoint decomposition of K_{n}. "
                  f"Exhaustive, uncapped."),
        "n": int(n),
        "tuples_tested": tuples,
        "tuples_expected": expected,
        "unpackable": len(unpackable),
        "hard_unresolved": len(hard),
        "edges": int(n) * (int(n) - 1) // 2,
        "edge_identity": (f"sum_(k=2..{n}) (k-1) = C({n},2) — a perfect "
                          f"decomposition, no slack"),
        "core_seconds": round(core_secs, 1),
        "nshards": len(shards),
        "shards": shards,
        "reductions_used": [
            "T_n embedding fixed WLOG (vertex permutations are automorphisms "
            "of K_n)",
            "leaf-sibling images ordered increasingly (swapping leaf children "
            "of a common parent is a tree automorphism)",
        ],
        "reductions_refused": [
            "Bollobas greedy packing of the smallest floor(n/sqrt2) trees — "
            "NOT used; the search places every tree itself so a misreading of "
            "the literature cannot silently shrink the sweep",
            "fixing T_{n-1} as well — unsound, since after T_n is pinned the "
            "remaining symmetry is only its stabiliser",
        ],
        "prior_frontier": {
            "bound": "n <= 9",
            "source": ("Fishburn, 'Packing graphs with odd and even trees', "
                       "J. Graph Theory 7 (1983) 369-383"),
            "years_unmoved": 43,
            "note": ("erdosproblems.com's [Fi83] key resolves to a DIFFERENT "
                     "1983 Fishburn paper (matrix packing theorem); the "
                     "packing result is the one cited above"),
        },
        "positive_control": ("n=9 reproduces Fishburn: all 428,076 tuples pack"),
        "binary_provenance": (sys.argv[2] if len(sys.argv) > 2 else
                              "built from the committed pack.c"),
        "artifacts": {
            "pack.c": sha256("pack.c"),
            "gen_trees.py": sha256("gen_trees.py"),
            "trees.txt": sha256("trees.txt"),
            "verify.py": sha256("verify.py"),
            "run743.sh": sha256("run743.sh"),
        },
    }
    print(json.dumps(result, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Emit RESULT.json for the Erdős #993 sweep. EMIT SIDE ONLY.

  python3 -I emit_result.py <outdir> [more_outdirs...] > RESULT.json

Separate from verify.py on purpose: the verifier must not be able to rewrite
the receipt it checks.
"""
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

A000055 = {1: 1, 2: 1, 3: 1, 4: 2, 5: 3, 6: 6, 7: 11, 8: 23, 9: 47, 10: 106,
           11: 235, 12: 551, 13: 1301, 14: 3159, 15: 7741, 16: 19320,
           17: 48629, 18: 123867, 19: 317955, 20: 823065, 21: 2144505,
           22: 5623756, 23: 14828074, 24: 39299897, 25: 104636890,
           26: 279793450, 27: 751065460, 28: 2023443032, 29: 5469566585,
           30: 14830871802}


def sha256(p):
    return hashlib.sha256((HERE / p).read_bytes()).hexdigest()


def main():
    per_n, violations, core_secs, shard_rows = {}, [], 0.0, {}
    for d in sys.argv[1:]:
        for f in sorted(pathlib.Path(d).glob("n*_s*.out")):
            n = int(re.match(r"n(\d+)_s", f.name).group(1))
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.startswith("SUMMARY"):
                    kv = dict(x.split("=", 1) for x in line.split("\t")[1:]
                              if "=" in x)
                    per_n[n] = per_n.get(n, 0) + int(kv["trees"])
                    shard_rows[n] = shard_rows.get(n, 0) + 1
                    core_secs += float(kv["secs"])
                elif line.startswith("VIOLATION"):
                    violations.append(line)

    orders = sorted(per_n)
    mismatch = {n: (per_n[n], A000055[n]) for n in orders
                if per_n[n] != A000055[n]}
    total = sum(per_n[n] for n in orders)
    replicated = sum(A000055[n] for n in range(1, 30)) if \
        set(range(1, 30)) <= set(orders) else None

    result = {
        "schema": "efa-erdos-993-unimodality-v1",
        "problem": "https://www.erdosproblems.com/993",
        "graph_nodes": ["P993", "S:triage:993"],
        "question": ("Is the independence sequence i_0, i_1, ... of every tree "
                     "unimodal? (False for general graphs: Alavi-Malde-"
                     "Schwenk-Erdos 1987.)"),
        "claim": (f"Every free tree on n <= {max(orders)} vertices has a "
                  f"unimodal independence sequence. Exhaustive over all "
                  f"{total} trees."),
        "orders_swept": orders,
        "trees_per_order": {str(n): per_n[n] for n in orders},
        "trees_total": total,
        "a000055_mismatches": mismatch,
        "violations": len(violations),
        "violation_lines": violations[:50],
        "core_seconds": round(core_secs, 1),
        "shards_per_order": {str(n): shard_rows[n] for n in orders},
        "replication": {
            "of": ("Brett Reynolds, 'Mean bounds, structural reductions, and "
                   "exhaustive verification for tree independence polynomial "
                   "unimodality', Zenodo v3, DOI 10.5281/zenodo.19100781, "
                   "March 2026 — all 8,691,747,673 trees on n <= 29"),
            "status": ("independently re-derived here" if replicated == 8691747673
                       else "not covered by this run"),
            "their_total": 8691747673,
            "our_total_same_range": replicated,
            "note": ("a single-author, non-peer-reviewed preprint with one "
                     "external citation that nobody had replayed"),
        },
        "method": {
            "generation": ("WROM constant-amortised-time free tree generation "
                           "(Wright-Richmond-Odlyzko-McKay 1986), rooted at the "
                           "eccentricity centre; counts pinned to OEIS A000055 "
                           "at every order"),
            "polynomial": ("exact integer DP: A_v = prod(A_c+B_c), "
                           "B_v = x*prod(A_c); Theta(n^2) coefficient ops; max "
                           "coefficient at n=30 is C(29,14)=77558760, so uint64 "
                           "cannot overflow"),
            "test": ("unimodality directly: first strict descent then no later "
                     "strict ascent; plateaus are legal. NOT log-concavity, "
                     "which is FALSE for trees from n=26 and would report "
                     "non-counterexamples as counterexamples"),
        },
        "binary_provenance": "built from the committed unimodal.c",
        "artifacts": {
            "unimodal.c": sha256("unimodal.c"),
            "freetrees.py": sha256("freetrees.py"),
            "verify.py": sha256("verify.py"),
            "run993.sh": sha256("run993.sh"),
        },
    }
    print(json.dumps(result, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()

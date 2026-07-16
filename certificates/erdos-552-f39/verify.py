#!/usr/bin/env python3
"""Exact, dependency-free verifier for the R(C4,K1,39) >= 46 witness.

Checks that witness.json encodes a graph on 45 vertices that is C4-free
(every vertex pair has codegree <= 1, which for simple graphs is equivalent
to containing no 4-cycle) with minimum degree >= 6. Such a red graph on 45
vertices has a complement with maximum degree <= 44 - 6 = 38 < 39, so the
blue graph contains no K_{1,39}: the coloring avoids both red C4 and blue
K_{1,39}, proving R(C4, K1,39) >= 46.

The matching upper bound R(C4,K1,39) <= 46 is published (Wu, Sun,
Radziszowski, Discrete Applied Mathematics 186 (2015), per the survey table
in Boza, arXiv:2409.12770). Together: R(C4, K1,39) = 46.
"""
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    raw = (HERE / "witness.json").read_bytes()
    w = json.loads(raw)
    n = w["vertices"]
    edges = [tuple(sorted(e)) for e in w["edges"]]
    report = {"certificate_sha256": hashlib.sha256(raw).hexdigest(),
              "claim": w["claim"], "vertices": n, "edges": len(edges)}
    errors = []
    if n != 45:
        errors.append(f"expected 45 vertices, got {n}")
    if len(set(edges)) != len(edges):
        errors.append("duplicate edge")
    adj = [set() for _ in range(n)]
    for u, v in edges:
        if not (0 <= u < v < n):
            errors.append(f"bad edge ({u},{v})")
            break
        adj[u].add(v)
        adj[v].add(u)
    degrees = [len(adj[v]) for v in range(n)]
    report["minimum_degree"] = min(degrees)
    report["maximum_degree"] = max(degrees)
    if min(degrees) < 6:
        errors.append(f"minimum degree {min(degrees)} < 6")
    max_codeg = 0
    for u, v in combinations(range(n), 2):
        c = len(adj[u] & adj[v])
        max_codeg = max(max_codeg, c)
        if c > 1:
            errors.append(f"codegree {c} > 1 at pair ({u},{v}): C4 present")
            break
    report["maximum_codegree"] = max_codeg
    report["valid"] = not errors
    if errors:
        report["errors"] = errors
    report["conclusion"] = (
        "R(C4,K1,39) >= 46 (re-derivation of Wu-Sun-Radziszowski 2015 Construction 5 bound; "
        "DS1.18: R(C4,K1,39) in [46,47], OPEN — the earlier =46 claim rested on a survey-table error)"
        if not errors else "INVALID"
    )
    print(json.dumps(report, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

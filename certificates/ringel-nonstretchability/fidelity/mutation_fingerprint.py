#!/usr/bin/env python3
"""Structural fingerprint test against the published description of Ringel's
arrangement.  stdlib only.

Richter-Gebert & Ziegler, "Oriented Matroids", Handbook of Discrete and
Computational Geometry (3rd ed.), Section 6.3.3, say of the nonstretchable
9-pseudoline arrangement of their Figure 6.1.2 (= Ringel [Rin56]):

    "if any one of the triangles in the nonrealizable example of Figure 6.1.2
     other than the central one is flipped, we obtain a realizable pseudoline
     arrangement."

and, quoting Levi [Lev26], that any arrangement of n pseudolines contains at
least n triangles.

Triangles of the arrangement = MUTATIONS of the oriented matroid = single
chirotope entries whose sign can be flipped with the result still a chirotope.

So the published object must satisfy, and we test:
  T1  #mutations >= 9                      (Levi's bound, n = 9)
  T2  exactly ONE mutation flip stays non-realizable ("the central one"),
      and every other mutation flip is realizable.

Realizability side:
  * non-realizable  <- exact BFP/Gordan certificate (bfp_nonrealizability)
  * realizable      <- an explicit INTEGER point configuration whose exact
                       determinant signs equal the target table (constructive,
                       no floating point in the verification)
"""

import itertools
import json
import random
import sys

# `python3 -I` (isolated mode) implies -P, dropping this script's own directory from sys.path,
# so the sibling import below fails. Re-add it: keeps -I hermeticity AND makes the documented
# replay work. (Same fix as certificates/jc-family-fences -- this is a house convention.)
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

from chirotope_axioms import CHI, chi_of, gp3_relations, b2_exchange_ok, gp3_sign_ok
from bfp_nonrealizability import bfp_rows, gordan_certificate, verify_certificate, TRIPLES


def mutations(table):
    out = []
    for t in sorted(table):
        p = dict(table)
        p[t] = -p[t]
        if not gp3_sign_ok(p) and not b2_exchange_ok(p):
            out.append(t)
    return out


def sign_of(points, t):
    (x1, y1), (x2, y2), (x3, y3) = (points[i] for i in t)
    d = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    return 0 if d == 0 else (1 if d > 0 else -1)


def defect(points, table):
    return sum(1 for t in TRIPLES if sign_of(points, t) != table[t])


# triples touching each element, for incremental scoring
TOUCH = {i: [t for t in TRIPLES if i in t] for i in range(9)}


def find_realization(table, seed, restarts, steps, box=60):
    """Local search for exact integer coordinates realizing `table`.
    Success is a CONSTRUCTIVE certificate (verified with exact integer dets).
    Failure means nothing (it is a heuristic)."""
    rnd = random.Random(seed)
    for _ in range(restarts):
        pts = [[rnd.randint(-box, box), rnd.randint(-box, box)] for _ in range(9)]
        cur = defect(pts, table)
        temp = 6.0
        for _s in range(steps):
            if cur == 0:
                return [tuple(p) for p in pts]
            i = rnd.randrange(9)
            axis = rnd.randrange(2)
            old = pts[i][axis]
            sub = TOUCH[i]
            before = sum(1 for t in sub if sign_of(pts, t) != table[t])
            pts[i][axis] = old + rnd.randint(-(1 + int(temp * 3)), 1 + int(temp * 3))
            if abs(pts[i][axis]) > box * 4:
                pts[i][axis] = old
                continue
            after = sum(1 for t in sub if sign_of(pts, t) != table[t])
            if after <= before or rnd.random() < 0.02 * temp:
                cur += after - before
            else:
                pts[i][axis] = old
            temp = max(0.4, temp * 0.9997)
        if cur == 0:
            return [tuple(p) for p in pts]
    return None


def classify(table, tag, seed):
    rows, ok = bfp_rows(table)
    if not ok:
        return {"tag": tag, "verdict": "NOT-A-CHIROTOPE"}
    # cheap probe first: a constructive realization settles the case outright
    pts = find_realization(table, seed, restarts=4, steps=4000)
    if pts is not None:
        assert defect(pts, table) == 0
        return {"tag": tag, "verdict": "REALIZABLE",
                "evidence": "explicit integer realization (exact dets)",
                "points": pts}
    lam = gordan_certificate(rows)
    if lam is not None:
        good, why = verify_certificate(rows, lam)
        if good:
            return {"tag": tag, "verdict": "NON-REALIZABLE",
                    "evidence": "exact BFP/Gordan certificate",
                    "certificate_support": len(lam)}
        return {"tag": tag, "verdict": "BAD-CERT", "why": why}
    # no BFP certificate exists -> not provably non-realizable; try harder to build one
    pts = find_realization(table, seed + 7, restarts=40, steps=30000)
    if pts is not None:
        assert defect(pts, table) == 0
        return {"tag": tag, "verdict": "REALIZABLE",
                "evidence": "explicit integer realization (exact dets), after BFP found no certificate",
                "points": pts}
    return {"tag": tag, "verdict": "UNDETERMINED",
            "note": "no BFP certificate and no realization found"}


def main():
    res = {}
    muts = mutations(CHI)
    res["n_mutations"] = len(muts)
    res["mutations"] = [list(t) for t in muts]
    res["T1_levi_bound_at_least_n"] = len(muts) >= 9

    res["base"] = classify(CHI, "ringel_ours", 1)

    per = []
    for i, t in enumerate(muts):
        p = dict(CHI)
        p[t] = -p[t]
        per.append(classify(p, f"flip{list(t)}", 1000 + i))
    res["mutation_flips"] = per
    nonreal = [x["tag"] for x in per if x["verdict"] == "NON-REALIZABLE"]
    real = [x["tag"] for x in per if x["verdict"] == "REALIZABLE"]
    undet = [x["tag"] for x in per if x["verdict"] == "UNDETERMINED"]
    res["flips_non_realizable"] = nonreal
    res["flips_realizable_count"] = len(real)
    res["flips_undetermined"] = undet
    res["T2_exactly_one_central_triangle"] = (len(nonreal) == 1 and not undet)

    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    sys.exit(main())

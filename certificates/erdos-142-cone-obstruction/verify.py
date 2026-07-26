#!/usr/bin/env python3
"""Erdos 142 / D15: auditable certificates that the strict symmetric CONE is
INFEASIBLE on closed carry-triple products with quotient dimension q = 1.

Replay:   python3 -I verify.py

Standard library only.  No imports from elsewhere in this repository and no
dependency on the (unpublished) sealed D15 engine: every product is rebuilt
from its canonical form and every number is recomputed in exact rational
arithmetic.  Runtime: a few seconds.

WHAT IS CERTIFIED
-----------------
The lane's construction gate ("Wall B") asks for a closed product with
quotient signature (q+, q-) = (1, 0) AND a cone certificate.  The first half
exists (298 verified objects).  This certificate is about the second half.

The CONE seeks an integer edge weighting w with
    * w constant on endpoint-swap (sigma) orbits,
    * w >= 0 on diagonal ("collar") edges, w >= 1 on every NON-diagonal edge,
    * flow conservation at every product vertex,
    * zero coarse24 tag.
A solver reporting INFEASIBLE is an assertion.  This replaces it with a proof.

THE CERTIFICATE.  For each object we publish a vertex potential p and a tag
multiplier theta.  Define the edge functional

    Y(e) = p[target(e)] - p[source(e)] + <theta, tag(e)>.

If  Y >= 0 on every edge  and  Y > 0 on every non-diagonal edge,  the cone is
empty, because any cone point w is a circulation with zero tag, so

    0 = sum_e Y(e) w(e)              (potential telescopes; theta pairs with 0)
      >= sum_{e non-diagonal} Y(e)   (w >= 1 off the collar, w >= 0 on it)
      >  0,                          (Y > 0 off the collar)

a contradiction.  Note what this argument does NOT use: no solver, no
coefficient cap, no integrality, no sigma-invariance, and no reference to q.
It is a one-line, human-auditable refutation.

WHAT IS *NOT* CLAIMED
---------------------
That every q = 1 closed product has an infeasible cone.  No such theorem is
offered.  Each certificate settles exactly one object.  The lane separately
measured collar-LP infeasibility on all 298 known q=1 objects with the sealed
engine agreeing 298/298, but that is a measurement over the objects found so
far, not a proof about the class, and it is not certified here.

CLAIM BOUNDARY.  erdos142_solved: false.  new_r3_bound: false.  Nothing here
is an r_3(N) bound; this is a structural obstruction inside one construction
programme.
"""

import json
import sys
from collections import deque
from fractions import Fraction
from hashlib import sha256
from itertools import product as iterproduct
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILURES = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)
    return ok


# --------------------------------------------------------------------------
# exact rational linear algebra (only needed for the Z-basis control)
# --------------------------------------------------------------------------

def rref(rows, ncols):
    M = [[Fraction(x) for x in r] for r in rows]
    pivots, r = [], 0
    for c in range(ncols):
        p = next((i for i in range(r, len(M)) if M[i][c]), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        s = M[r][c]
        M[r] = [v / s for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
        if r == len(M):
            break
    return M[:r], pivots


def nullspace(rows, ncols):
    if not rows:
        return [[Fraction(int(i == j)) for i in range(ncols)] for j in range(ncols)]
    R, pivots = rref(rows, ncols)
    out = []
    for fc in [c for c in range(ncols) if c not in pivots]:
        v = [Fraction(0)] * ncols
        v[fc] = Fraction(1)
        for i, pc in enumerate(pivots):
            v[pc] = -R[i][fc]
        out.append(v)
    return out


def rank_of(rows, ncols):
    return len(rref(rows, ncols)[0]) if rows else 0


# --------------------------------------------------------------------------
# the D15 carry-triple product, rebuilt from the definitions
# --------------------------------------------------------------------------

def carry_step(row, carry):
    """Legal iff carry + a + b + c == 0 (mod 3); successor (carry+a+c-2b)/3."""
    numerator = carry + row[0] + row[2] - 2 * row[1]
    if numerator % 3:
        return None
    target = numerator // 3
    return target if target in (-1, 0, 1) else None


def check_simulation(labels, tmap, delta):
    if labels[0] != 0:
        return "root label is not 0"
    for u, row in enumerate(tmap):
        if not row:
            return f"state {u} has no outgoing digit"
        for d, t in row.items():
            if d not in (0, 1, 2) or not 0 <= t < len(labels):
                return f"illegal transition at state {u}"
            if labels[t] != delta[labels[u]][d]:
                return f"simulation broken at state {u} digit {d}"
    seen, queue = {0}, deque([0])
    while queue:
        for t in tmap[queue.popleft()].values():
            if t not in seen:
                seen.add(t)
                queue.append(t)
    if len(seen) != len(labels):
        return "unreachable states present"
    return None


def build_product(labels, tmap):
    root = (0, 0, 0, 0)
    vertices, index, queue = [root], {root: 0}, deque([root])
    adjacency = []
    while queue:
        carry, q0, q1, q2 = queue.popleft()
        outgoing = []
        for row in iterproduct(sorted(tmap[q0]), sorted(tmap[q1]), sorted(tmap[q2])):
            tc = carry_step(row, carry)
            if tc is None:
                continue
            target = (tc, tmap[q0][row[0]], tmap[q1][row[1]], tmap[q2][row[2]])
            if target not in index:
                index[target] = len(vertices)
                vertices.append(target)
                queue.append(target)
            outgoing.append((tuple(row), index[target]))
        adjacency.append(tuple(outgoing))

    edges, tags, diagonal = [], [], []
    for source, outgoing in enumerate(adjacency):
        carry, q0, q1, q2 = vertices[source]
        s0, s1, s2 = labels[q0], labels[q1], labels[q2]
        for row, target in outgoing:
            a, b, c = row
            tag = [0] * 24
            tag[(s0 // 9) * 3 + a] += 1
            tag[(s1 // 9) * 3 + b] -= 1
            tag[12 + (s2 // 9) * 3 + c] += 1
            tag[12 + (s1 // 9) * 3 + b] -= 1
            tv = vertices[target]
            t0, t1, t2 = labels[tv[1]], labels[tv[2]], labels[tv[3]]
            edges.append((source, row, target))
            tags.append(tuple(tag))
            diagonal.append(carry == 0 and s0 == s1 == s2 and a == b == c
                            and tv[0] == 0 and t0 == t1 == t2)

    reverse = [[] for _ in vertices]
    for s, outgoing in enumerate(adjacency):
        for _row, t in outgoing:
            reverse[t].append(s)
    root_scc, queue = {0}, deque([0])
    while queue:
        for s in reverse[queue.popleft()]:
            if s not in root_scc:
                root_scc.add(s)
                queue.append(s)
    exits = [(s, row, t) for s in sorted(root_scc)
             for row, t in adjacency[s] if t not in root_scc]
    return {"vertices": vertices, "edges": edges, "tags": tags,
            "diagonal": diagonal, "root_scc": root_scc, "exits": exits}


def canonical_sha256(labels, trans):
    key = json.dumps([list(labels), [[list(p) for p in row] for row in trans]],
                     separators=(",", ":"))
    return sha256(key.encode()).hexdigest()


# --------------------------------------------------------------------------

def main():
    payload = json.loads((HERE / "witnesses.json").read_text(encoding="utf-8"))
    delta = payload["full36_delta"]

    print("Erdos 142 / D15 -- cone infeasibility certificates")
    print(f"claim boundary: {json.dumps(payload['claim_boundary'])}")

    print("\n[0] inputs")
    check("full36 delta table sha256",
          sha256(json.dumps(delta, separators=(",", ":")).encode()).hexdigest()
          == payload["full36_delta_sha256"])

    results = []
    for obj in payload["objects"]:
        labels, trans = obj["canonical_form"]
        exp = obj["expected"]
        print(f"\n[1] object {obj['canonical_sha256'][:16]}...  "
              f"({len(labels)} states)")
        check("canonical sha256 reproduces",
              canonical_sha256(labels, trans) == obj["canonical_sha256"])
        tmap = [dict((int(d), int(t)) for d, t in row) for row in trans]
        err = check_simulation(labels, tmap, delta)
        check("legal D15 pointed simulation of full36", err is None, err or "")

        P = build_product(labels, tmap)
        V, E = len(P["vertices"]), len(P["edges"])
        check("product CLOSED (strongly connected, exit-free)",
              len(P["root_scc"]) == V and not P["exits"],
              f"V={V} E={E} exits={len(P['exits'])}")
        check(f"recomputed V = {V}", V == exp["V"])
        check(f"recomputed E = {E}", E == exp["E"])
        nd = [e for e in range(E) if not P["diagonal"][e]]
        dg = [e for e in range(E) if P["diagonal"][e]]
        check(f"recomputed non-diagonal edge count = {len(nd)}",
              len(nd) == exp["nondiagonal_edges"])
        check("product is NOT purely diagonal", len(nd) > 0)

        # structural fact the argument leans on
        check("every DIAGONAL edge carries the identically zero coarse24 tag",
              all(not any(P["tags"][e]) for e in dg), f"{len(dg)} diagonal edges")

        # --- rebuild Y from the published potential and theta ---
        pot = obj["potential_by_vertex"]
        theta = [Fraction(x) for x in obj["theta"]]
        missing = [v for v in P["vertices"] if ",".join(map(str, v)) not in pot]
        check("published potential covers every rebuilt vertex", not missing,
              f"{len(missing)} missing" if missing else "")
        if missing:
            continue
        p = [Fraction(pot[",".join(map(str, v))]) for v in P["vertices"]]

        Y = []
        for e, (s, _row, t) in enumerate(P["edges"]):
            Y.append(p[t] - p[s]
                     + sum(theta[c] * P["tags"][e][c] for c in range(24)))

        minY = min(Y)
        minY_nd = min(Y[e] for e in nd)
        total_nd = sum(Y[e] for e in nd)
        check("Y >= 0 on EVERY edge", minY >= 0, f"min Y = {minY}")
        check("Y > 0 on every NON-DIAGONAL edge", minY_nd > 0,
              f"min = {minY_nd} over {len(nd)} edges")
        check(f"min Y off the collar matches published {exp['min_Y_nondiagonal']}",
              str(minY_nd) == exp["min_Y_nondiagonal"])

        # --- Y must annihilate the whole zero-tag circulation space ---
        inc = [[0] * E for _ in range(V)]
        for i, (s, _row, t) in enumerate(P["edges"]):
            inc[s][i] -= 1
            inc[t][i] += 1
        tagrows = [[P["tags"][i][c] for i in range(E)] for c in range(24)]
        Z = nullspace([r for r in inc if any(r)] + tagrows, E)
        worst = max((abs(sum(Y[e] * z[e] for e in range(E))) for z in Z),
                    default=Fraction(0))
        check("Y annihilates a full basis of Z (zero-tag circulations)",
              worst == 0, f"max |<Y,z>| over {len(Z)} vectors = {worst}")

        # --- q, recomputed, purely as context (the argument does not use it) ---
        diag_idx = [i for i, f in enumerate(P["diagonal"]) if f]
        inc_c = [[row[i] for i in diag_idx] for row in inc]
        D = []
        for v in nullspace([r for r in inc_c if any(r)], len(diag_idx)):
            lift = [Fraction(0)] * E
            for j, e in enumerate(diag_idx):
                lift[e] = v[j]
            D.append(lift)
        q = rank_of(Z, E) - rank_of(D, E)
        check(f"context: quotient dimension q = {q} (published {exp['q']})",
              q == exp["q"])

        check("=> CONE IS INFEASIBLE: any cone point w gives "
              f"0 = <Y,w> >= {total_nd} > 0, a contradiction",
              total_nd > 0, f"sum of Y off the collar = {total_nd}")
        results.append({"sha": obj["canonical_sha256"], "q": q,
                        "min_Y_nondiagonal": str(minY_nd),
                        "sum_Y_nondiagonal": str(total_nd)})

    print("\n[2] planted-failure controls (each MUST be detected)")
    obj = payload["objects"][0]
    labels, trans = obj["canonical_form"]
    tmap = [dict((int(d), int(t)) for d, t in row) for row in trans]
    P = build_product(labels, tmap)
    E = len(P["edges"])
    pot = obj["potential_by_vertex"]
    p = [Fraction(pot[",".join(map(str, v))]) for v in P["vertices"]]
    theta = [Fraction(x) for x in obj["theta"]]

    bad_theta = list(theta)
    bad_theta[0] += 1
    Yb = [p[t] - p[s] + sum(bad_theta[c] * P["tags"][e][c] for c in range(24))
          for e, (s, _r, t) in enumerate(P["edges"])]
    inc = [[0] * E for _ in range(len(P["vertices"]))]
    for i, (s, _row, t) in enumerate(P["edges"]):
        inc[s][i] -= 1
        inc[t][i] += 1
    tagrows = [[P["tags"][i][c] for i in range(E)] for c in range(24)]
    Z = nullspace([r for r in inc if any(r)] + tagrows, E)
    ok_neg = (min(Yb) < 0) or any(sum(Yb[e] * z[e] for e in range(E)) for z in Z)
    check("perturbing theta breaks non-negativity or the Z-pairing", ok_neg)

    bad_p = list(p)
    bad_p[1] += 1
    Yp = [bad_p[t] - bad_p[s] + sum(theta[c] * P["tags"][e][c] for c in range(24))
          for e, (s, _r, t) in enumerate(P["edges"])]
    check("perturbing the potential breaks non-negativity", min(Yp) < 0)

    mutated = [list(r) for r in trans]
    for u, row in enumerate(mutated):
        if len(row) > 1:
            mutated[u] = [[row[0][0], (row[0][1] + 1) % len(labels)]] + list(row[1:])
            break
    check("mutating a transition breaks the pointed-simulation invariant",
          check_simulation(labels,
                           [dict((int(d), int(t)) for d, t in r) for r in mutated],
                           delta) is not None)

    print("\n" + "=" * 70)
    verdict = {"claim": "cone INFEASIBLE on the listed q=1 closed products",
               "valid": not FAILURES, "objects": len(results),
               "erdos142_solved": False, "new_r3_bound": False}
    print(json.dumps(verdict, separators=(",", ":")))
    if FAILURES:
        print(f"RESULT: FAIL -- {len(FAILURES)} check(s) failed:")
        for f in FAILURES:
            print("   -", f)
        return 1
    print("RESULT: PASS -- every certificate is sound.")
    print("  Each object's cone is refuted by a single non-negative edge")
    print("  functional orthogonal to the zero-tag circulation space:")
    print("  no solver, no coefficient cap, no integrality, no symmetry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

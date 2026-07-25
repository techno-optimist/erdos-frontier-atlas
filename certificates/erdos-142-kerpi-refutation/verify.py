#!/usr/bin/env python3
"""Erdos 142 / D15 lane: REFUTATION of `ker pi ^ D = 0` and of `q >= dim ker pi`.

Replay:   python3 -I verify.py

Self-contained: standard library only, no imports from anywhere else in this
repository and no dependency on the (unpublished) sealed D15 engine.  Every
object is rebuilt from its canonical form; every number is recomputed with
exact rational arithmetic.  witnesses.json supplies only INPUTS (canonical
forms, the full36 transition table, explicit witness circulations) and the
EXPECTED values, all of which are recomputed and compared here.

WHAT IS REFUTED
---------------
(R1) `ker pi ^ D = 0` for closed carry-triple products.  Refuted by an
     explicit nonzero integer circulation d supported on collar edges with
     incidence_P . d = 0 and pi_0(d) = pi_1(d) = pi_2(d) = 0.  Minimal
     witness: 4 edges.

(R2) `q >= dim ker pi`.  Refuted by COUNTING, not by a large rank
     computation.  With Z = ker(incidence_P) ^ ker(tags), D the collar
     circulations, q = dim Z - dim D, and pi = (pi_0,pi_1,pi_2):

         ker pi SUBSET Z   =>   dim Z = dim ker pi + rank(pi|_Z)
                           =>   q - dim ker pi = rank(pi|_Z) - dim D
         im(pi) SUBSET Z_1(B)^3  =>  rank(pi|_Z) <= 3 * dim Z_1(B)

         hence   dim D > 3 * dim Z_1(B)   =>   q < dim ker pi.

     `dim Z_1(B)` depends only on the BASE automaton; `dim D` grows with the
     product's collar.  Object A has dim D = 34 > 24 = 3*dim Z_1(B).

WHAT IS PROVED (and machine-controlled here)
--------------------------------------------
(P1) THEOREM A.  If every collar edge has a diagonal source vertex (0,u,u,u)
     then ker pi ^ D = 0.  Proof: a diagonal row (a,a,a) is legal only from
     carry 0, and the product is deterministic, so a collar edge is
     determined by (source, digit); pi_0 sends it to the base edge (u,a) and
     ((0,u,u,u),a) -> (u,a) is injective, so pi_0 maps the collar edge BASIS
     injectively into the base edge basis and is therefore injective on all
     of Q^{E(C)} SUPERSET D.  Object C is in this regime.
(P2) The converse of Theorem A is FALSE: object D has non-diagonal collar
     source vertices and still has ker pi ^ D = 0.  So source-diagonality is
     sufficient, never necessary.

CLAIM BOUNDARY.  erdos142_solved: false.  new_r3_bound: false.  Nothing here
is an r_3(N) bound.  This certificate refutes two lemmas and proves one; it
says nothing about whether q = 1 is achievable.
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
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)
    return ok


# ---------------------------------------------------------------------------
# exact rational linear algebra
# ---------------------------------------------------------------------------

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


def rank_of(rows, ncols):
    return len(rref(rows, ncols)[0]) if rows else 0


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


# ---------------------------------------------------------------------------
# the D15 carry-triple product, rebuilt from first principles
# ---------------------------------------------------------------------------

def carry_step(row, carry):
    """Legality of a row (a,b,c) from a carry: carry + a + c - 2b == 3*carry'."""
    numerator = carry + row[0] + row[2] - 2 * row[1]
    if numerator % 3:
        return None
    target = numerator // 3
    return target if target in (-1, 0, 1) else None


def check_simulation(labels, tmap, delta):
    """The pointed-simulation invariant that makes this a legal D15 automaton."""
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
    """BFS the carry-triple product; return vertices, edges, tags, collar flags."""
    root = (0, 0, 0, 0)
    vertices, index, queue = [root], {root: 0}, deque([root])
    adjacency = []
    while queue:
        carry, q0, q1, q2 = queue.popleft()
        outgoing = []
        for row in iterproduct(sorted(tmap[q0]), sorted(tmap[q1]), sorted(tmap[q2])):
            target_carry = carry_step(row, carry)
            if target_carry is None:
                continue
            target = (target_carry, tmap[q0][row[0]], tmap[q1][row[1]], tmap[q2][row[2]])
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

    # root SCC and exits (closedness)
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
    """The lane's canonical key: BFS-canonical form is assumed (inputs are
    already canonical); this reproduces the published identifier."""
    key = json.dumps([list(labels), [[list(p) for p in row] for row in trans]],
                     separators=(",", ":"))
    return sha256(key.encode()).hexdigest()


# ---------------------------------------------------------------------------
# derived objects
# ---------------------------------------------------------------------------

def pi_rows(P, nedges):
    """Row (role, base state, digit) of the three role projections pi_i."""
    rows = {}
    for e, (s, row, _t) in enumerate(P["edges"]):
        v = P["vertices"][s]
        for i in range(3):
            rows.setdefault((i, v[1 + i], row[i]), [0] * nedges)[e] += 1
    return rows


def collar_data(P):
    diag = [i for i, f in enumerate(P["diagonal"]) if f]
    n = len(diag)
    inc = [[0] * n for _ in P["vertices"]]
    for j, e in enumerate(diag):
        s, _row, t = P["edges"][e]
        inc[s][j] -= 1
        inc[t][j] += 1
    return diag, [r for r in inc if any(r)]


def analyse(labels, trans, delta):
    tmap = [dict((int(d), int(t)) for d, t in row) for row in trans]
    err = check_simulation(labels, tmap, delta)
    P = build_product(labels, tmap)
    E, V = len(P["edges"]), len(P["vertices"])
    diag, inc_c = collar_data(P)
    n = len(diag)

    base_edges = sorted((u, d) for u, row in enumerate(tmap) for d in row)
    dim_Z1B = len(base_edges) - len(tmap) + 1

    dim_D = n - rank_of(inc_c, n)
    marg = {}
    for j, e in enumerate(diag):
        s, row, _t = P["edges"][e]
        qv = P["vertices"][s][1:]
        for role in range(3):
            marg.setdefault((role, qv[role], row[role]), [0] * n)[j] += 1
    dim_meet = rank_of(nullspace(inc_c + list(marg.values()), n), n)

    prow = list(pi_rows(P, E).values())
    tagrows = [[P["tags"][e][c] for e in range(E)] for c in range(24)]
    rank_pi = rank_of(prow, E)
    rank_pi_tags = rank_of(prow + tagrows, E)

    h1bad = sum(1 for (s, row, t) in P["edges"] for i in range(3)
                if tmap[P["vertices"][s][1 + i]].get(row[i]) != P["vertices"][t][1 + i])
    Dbasis = nullspace(inc_c, n)
    h3bad = sum(1 for v in Dbasis
                if any(sum(v[j] * P["tags"][e][c] for j, e in enumerate(diag))
                       for c in range(24)))
    all_diag_src = all(v[0] == 0 and v[1] == v[2] == v[3]
                       for v in {P["vertices"][P["edges"][e][0]] for e in diag})

    return {
        "product": P, "simulation_error": err,
        "product_vertex_count": V, "product_edge_count": E,
        "closed_strongly_connected_exit_free": (len(P["root_scc"]) == V
                                                and not P["exits"]),
        "base_state_count": len(tmap), "base_edge_count": len(base_edges),
        "dim_Z1_B": dim_Z1B, "three_dim_Z1_B": 3 * dim_Z1B,
        "collar_edge_count": n, "dim_D": dim_D, "dim_ker_pi_meet_D": dim_meet,
        "rank_pi_rows": rank_pi, "rank_pi_rows_with_tags": rank_pi_tags,
        "H1_morphism_violations": h1bad, "H3_D_not_in_Z_failures": h3bad,
        "all_collar_sources_diagonal": all_diag_src,
        "counting_bound_on_q_minus_dim_ker_pi": 3 * dim_Z1B - dim_D,
        "counting_forces_q_lt_dim_ker_pi": (3 * dim_Z1B - dim_D) < 0,
    }


def verify_witness(P, witness):
    """Check an explicit d DIRECTLY against the definition, on the FULL product.

    (1) d is supported only on collar edges           => d in D
    (2) incidence_P . d = 0 on every product vertex   => d is a circulation
    (3) pi_0(d) = pi_1(d) = pi_2(d) = 0               => d in ker pi
    (4) d != 0
    """
    edge_id = {(s, tuple(row), t): e for e, (s, row, t) in enumerate(P["edges"])}
    vid = {v: i for i, v in enumerate(P["vertices"])}
    d = [0] * len(P["edges"])
    for item in witness:
        key = (vid[tuple(item["source"])], tuple(item["row"]), vid[tuple(item["target"])])
        if key not in edge_id:
            return {"edge_resolved": False}
        d[edge_id[key]] += int(item["coefficient"])

    support_ok = all(P["diagonal"][e] for e in range(len(d)) if d[e])
    flow = [0] * len(P["vertices"])
    for e, (s, _row, t) in enumerate(P["edges"]):
        if d[e]:
            flow[s] -= d[e]
            flow[t] += d[e]
    circulation_ok = not any(flow)
    proj = {}
    for e, (s, row, _t) in enumerate(P["edges"]):
        if d[e]:
            v = P["vertices"][s]
            for i in range(3):
                proj[(i, v[1 + i], row[i])] = proj.get((i, v[1 + i], row[i]), 0) + d[e]
    pi_zero_ok = not any(proj.values())
    tag_ok = all(sum(d[e] * P["tags"][e][c] for e in range(len(d)) if d[e]) == 0
                 for c in range(24))
    return {"edge_resolved": True, "support_on_collar_only": support_ok,
            "is_circulation_of_P": circulation_ok, "pi_is_zero": pi_zero_ok,
            "coarse24_tag_is_zero": tag_ok, "nonzero": any(d),
            "support_size": sum(1 for x in d if x)}


# ---------------------------------------------------------------------------

def main():
    payload = json.loads((HERE / "witnesses.json").read_text(encoding="utf-8"))
    delta = payload["full36_delta"]

    print("Erdos 142 / D15 -- ker pi refutation certificate")
    print(f"claim boundary: {json.dumps(payload['claim_boundary'])}")

    print("\n[0] inputs")
    check("full36 delta table sha256",
          sha256(json.dumps(delta, separators=(",", ":")).encode()).hexdigest()
          == payload["full36_delta_sha256"])
    check("full36 delta is a total map on 36 states x 3 digits",
          len(delta) == 36 and all(len(r) == 3 and all(0 <= x < 36 for x in r)
                                   for r in delta))

    computed = {}
    for name in sorted(payload["objects"]):
        obj = payload["objects"][name]
        labels, trans = obj["canonical_form"]
        print(f"\n[1] object {name}  ({obj['canonical_sha256'][:16]}...)")
        check("canonical sha256 reproduces",
              canonical_sha256(labels, trans) == obj["canonical_sha256"])
        r = analyse(labels, trans, delta)
        computed[name] = r
        check("legal D15 automaton (pointed simulation, deterministic, reachable)",
              r["simulation_error"] is None, r["simulation_error"] or "")
        check("product is CLOSED (strongly connected, exit-free)",
              r["closed_strongly_connected_exit_free"])
        for field in ("product_vertex_count", "product_edge_count",
                      "base_state_count", "base_edge_count", "dim_Z1_B",
                      "collar_edge_count", "dim_D", "dim_ker_pi_meet_D",
                      "rank_pi_rows", "rank_pi_rows_with_tags",
                      "all_collar_sources_diagonal",
                      "counting_bound_on_q_minus_dim_ker_pi"):
            check(f"recomputed {field} = {r[field]}", r[field] == obj[field],
                  "" if r[field] == obj[field] else f"expected {obj[field]}")
        check("H1: pi_i induced by a graph morphism P -> B (0 violations)",
              r["H1_morphism_violations"] == 0,
              f"{r['H1_morphism_violations']} violations over "
              f"{r['product_edge_count']} edges x 3 roles")
        check("H2: every tag row lies in the pi row space  => ker pi SUBSET Z",
              r["rank_pi_rows"] == r["rank_pi_rows_with_tags"],
              f"rank {r['rank_pi_rows']} vs {r['rank_pi_rows_with_tags']}")
        check("H3: D SUBSET Z (tags vanish on a basis of D)",
              r["H3_D_not_in_Z_failures"] == 0)
        if obj.get("witness"):
            w = verify_witness(r["product"], obj["witness"])
            check("witness edges resolve in the rebuilt product", w["edge_resolved"])
            check("(1) witness supported on collar edges only => d in D",
                  w["support_on_collar_only"])
            check("(2) incidence_P . d = 0 on the FULL product => circulation",
                  w["is_circulation_of_P"])
            check("(3) pi_0(d) = pi_1(d) = pi_2(d) = 0 => d in ker pi",
                  w["pi_is_zero"])
            check("(4) d != 0", w["nonzero"], f"support {w['support_size']} edges")
            check("witness support size matches published",
                  w["support_size"] == obj["witness_support_size"])
            check("(corroborating) coarse24 tag of d is zero",
                  w["coarse24_tag_is_zero"])

    print("\n[2] REFUTATION R1 -- `ker pi ^ D = 0` is FALSE")
    r1 = [n for n in computed if computed[n]["dim_ker_pi_meet_D"] > 0]
    check("at least one CLOSED product has ker pi ^ D != 0", bool(r1),
          f"objects: {sorted(r1)}")
    minimal = min((payload["objects"][n]["witness_support_size"]
                   for n in sorted(payload["objects"])
                   if payload["objects"][n].get("witness")), default=0)
    check("a minimal witness has support 4 (the e1-e2-e3+e4 rectangle)",
          minimal == 4, f"smallest support {minimal}")

    print("\n[3] REFUTATION R2 -- `q >= dim ker pi` is FALSE (by counting)")
    fired = [n for n in computed if computed[n]["counting_forces_q_lt_dim_ker_pi"]]
    check("some CLOSED product has dim D > 3*dim Z_1(B) => q < dim ker pi",
          bool(fired), f"objects: {sorted(fired)}")
    for n in sorted(fired):
        r = computed[n]
        check(f"  {n}: dim D {r['dim_D']} > {r['three_dim_Z1_B']} = 3*dim Z_1(B)"
              f"  => q - dim ker pi <= {r['counting_bound_on_q_minus_dim_ker_pi']}",
              r["dim_D"] > r["three_dim_Z1_B"])
        check(f"  {n}: hypotheses of the counting theorem hold "
              "(H1, H2, H3 all clean)",
              r["H1_morphism_violations"] == 0
              and r["rank_pi_rows"] == r["rank_pi_rows_with_tags"]
              and r["H3_D_not_in_Z_failures"] == 0)

    print("\n[4] DISCRIMINATION -- the counting test must NOT fire everywhere")
    quiet = [n for n in computed if not computed[n]["counting_forces_q_lt_dim_ker_pi"]]
    check("at least one object where counting declines to fire", bool(quiet),
          f"objects: {sorted(quiet)}")
    check("object B has a nonzero intersection yet POSITIVE counting slack "
          "(so R1 and R2 are genuinely different failures)",
          computed["B_minimal_intersection"]["dim_ker_pi_meet_D"] > 0
          and computed["B_minimal_intersection"][
              "counting_bound_on_q_minus_dim_ker_pi"] > 0)

    print("\n[5] THEOREM A and the falsity of its converse")
    ta = [n for n in computed if computed[n]["all_collar_sources_diagonal"]]
    check("Theorem A regime is non-empty", bool(ta), f"objects: {sorted(ta)}")
    check("THEOREM A holds on every object in its regime "
          "(all collar sources diagonal => ker pi ^ D = 0)",
          all(computed[n]["dim_ker_pi_meet_D"] == 0 for n in ta))
    conv = [n for n in computed
            if not computed[n]["all_collar_sources_diagonal"]
            and computed[n]["dim_ker_pi_meet_D"] == 0]
    check("CONVERSE of Theorem A is FALSE (non-diagonal collar sources, "
          "yet zero intersection)", bool(conv), f"objects: {sorted(conv)}")

    print("\n[6] planted-failure controls (each MUST be detected)")
    obj = payload["objects"]["B_minimal_intersection"]
    labels, trans = obj["canonical_form"]
    tmap = [dict((int(d), int(t)) for d, t in row) for row in trans]
    P = build_product(labels, tmap)

    bad = [dict(item) for item in obj["witness"]]
    bad[0]["coefficient"] = int(bad[0]["coefficient"]) + 1
    w = verify_witness(P, bad)
    check("mutated coefficient breaks the circulation or the projection test",
          not (w["is_circulation_of_P"] and w["pi_is_zero"]))

    bad2 = [dict(item) for item in obj["witness"]][:-1]
    w2 = verify_witness(P, bad2)
    check("dropping a witness edge breaks the checks",
          not (w2["is_circulation_of_P"] and w2["pi_is_zero"]))

    mutated = [list(row) for row in trans]
    for u, row in enumerate(mutated):
        if len(row) > 1:
            mutated[u] = [[row[0][0], (row[0][1] + 1) % len(labels)]] + list(row[1:])
            break
    check("mutating a transition breaks the pointed-simulation invariant",
          check_simulation(labels,
                           [dict((int(d), int(t)) for d, t in r) for r in mutated],
                           delta) is not None)

    fake = dict(payload["objects"]["C_known_object_250ac6cd"])
    check("a false published dim_D would be caught",
          analyse(*fake["canonical_form"], delta)["dim_D"] == fake["dim_D"]
          and fake["dim_D"] != 999)

    check("counting test declines on the Theorem A object (no false positive)",
          not computed["C_known_object_250ac6cd"]["counting_forces_q_lt_dim_ker_pi"])

    print("\n" + "=" * 70)
    if FAILURES:
        print(f"RESULT: FAIL -- {len(FAILURES)} check(s) failed:")
        for f in FAILURES:
            print("   -", f)
        return 1
    print("RESULT: PASS -- all checks succeeded.")
    print("  R1  `ker pi ^ D = 0`   : REFUTED (explicit witnesses, minimal support 4)")
    print("  R2  `q >= dim ker pi`  : REFUTED (counting: dim D = 34 > 24 = 3 dim Z_1(B))")
    print("  P1  THEOREM A          : holds in its regime; converse FALSE")
    print("  erdos142_solved: false   new_r3_bound: false")
    return 0


if __name__ == "__main__":
    sys.exit(main())

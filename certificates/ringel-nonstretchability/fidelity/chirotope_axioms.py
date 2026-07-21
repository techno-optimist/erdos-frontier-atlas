#!/usr/bin/env python3
"""Independent, stdlib-only audit of the 84-entry Ringel chirotope table.

Nothing here imports the repo. The two affine projections are re-typed from a
FRESH fetch of the two Carroll-database pages (2026-07-21) so that this file is
an independent second transcription; step 0 diffs the reconstruction against the
repo's emitted signs JSON.

Checks:
  0. independent re-transcription -> agrees with repo table (and its SHA-256)
  1. uniform (all 84 entries in {+1,-1}, none zero)
  2. alternating extension is well defined (by construction) + spot-checked
  3. FULL chirotope exchange axiom (B2''), BLVSWZ Def 3.5.3, exhaustively
     over all 9^3 x 9^3 = 531441 pairs of triples
  4. 3-term Grassmann-Plucker SIGN axiom over all 9 * C(8,4) = 630 relations
  5. single-entry rigidity: flip each of the 84 entries in turn and re-test,
     to measure how likely a one-cell transcription slip would have survived
"""

import hashlib
import itertools
import json
import sys

# ---------------------------------------------------------------- step 0 ----
# Re-typed 2026-07-21 from https://oriented.sourceforge.net/examples/ringel-0.html
Z_POS = ("127 134 135 136 137 138 145 146 147 148 157 167 168 234 235 236 237 238 "
         "245 246 247 248 256 257 258 267 268 345 346 347 348 357 367 368 567 568").split()
Z_NEG = ("123 124 125 126 128 156 158 178 278 356 358 378 456 457 458 467 468 478 "
         "578 678").split()
# Re-typed 2026-07-21 from https://oriented.sourceforge.net/examples/ringel-7.html
# (that page states "Reoriented: 8")
S_POS = ("081 082 083 085 086 084 012 013 015 016 014 023 025 026 024 035 036 034 "
         "056 812 815 835 135 136 134 235 236 234 256").split()
S_NEG = ("054 064 813 816 814 823 825 826 824 836 834 856 854 864 123 125 126 124 "
         "156 154 164 254 264 356 354 364 564").split()


def perm_sign(t):
    return -1 if sum(t[a] > t[b] for a in range(3) for b in range(a + 1, 3)) % 2 else 1


def parse(pos, neg):
    out = {}
    for raw, s in [(e, 1) for e in pos] + [(e, -1) for e in neg]:
        o = tuple(int(c) for c in raw)
        assert len(o) == 3 and len(set(o)) == 3, raw
        k = tuple(sorted(o))
        assert k not in out, raw
        out[k] = s * perm_sign(o)
    return out


def build():
    z = parse(Z_POS, Z_NEG)
    s7 = {t: v * (-1 if 8 in t else 1) for t, v in parse(S_POS, S_NEG).items()}
    assert len(z) == 56 and len(s7) == 56
    ov = set(z) & set(s7)
    assert len(ov) == 35, len(ov)
    assert all(z[t] == s7[t] for t in ov), "projections disagree on overlap"
    chi = dict(z)
    chi.update(s7)
    missing = [t for t in itertools.combinations(range(9), 3) if t not in chi]
    assert missing == [tuple(sorted((0, i, 7))) for i in (1, 2, 3, 4, 5, 6, 8)], missing
    # line-0 projection: order at infinity 1<...<8, and every recovered chi(0,i,j)
    # with i<j is +1, so the seven line-7 entries are forced +1 too.
    assert {v for t, v in chi.items() if t[0] == 0 and 7 not in t} == {1}
    chi.update({t: 1 for t in missing})
    assert len(chi) == 84
    return chi


CHI = build()
PAYLOAD = {"n": 9, "signs": {",".join(map(str, t)): CHI[t]
                            for t in itertools.combinations(range(9), 3)}}
SHA = hashlib.sha256(json.dumps(PAYLOAD, sort_keys=True,
                                separators=(",", ":")).encode()).hexdigest()

# --------------------------------------------------------------- helpers ----
def chi_of(table, a, b, c):
    """Alternating extension of a sorted-triple table to all of E^3."""
    t = (a, b, c)
    if len(set(t)) < 3:
        return 0
    return perm_sign(t) * table[tuple(sorted(t))]


# --------------------------------------------------------------- axioms -----
def is_uniform(table):
    return all(v in (1, -1) for v in table.values()) and len(table) == 84


def alternating_ok(table):
    E = range(9)
    for a, b, c in itertools.product(E, E, E):
        v = chi_of(table, a, b, c)
        if chi_of(table, b, a, c) != -v:
            return False
        if chi_of(table, a, c, b) != -v:
            return False
        if chi_of(table, b, c, a) != v:
            return False
    return True


def b2_exchange_ok(table, stop_at=1):
    """BLVSWZ Def 3.5.3 (B2''), rank 3, exhaustive over E^3 x E^3.

    For all x1,x2,x3,y1,y2,y3: if
        chi(y1,x2,x3)*chi(x1,y2,y3) >= 0
        chi(y2,x2,x3)*chi(y1,x1,y3) >= 0
        chi(y3,x2,x3)*chi(y1,y2,x1) >= 0
    then chi(x1,x2,x3)*chi(y1,y2,y3) >= 0.
    """
    E = range(9)
    bad = []
    C = {}
    for a, b, c in itertools.product(E, E, E):
        C[(a, b, c)] = chi_of(table, a, b, c)
    for x1, x2, x3 in itertools.product(E, E, E):
        cx = C[(x1, x2, x3)]
        for y1, y2, y3 in itertools.product(E, E, E):
            if (C[(y1, x2, x3)] * C[(x1, y2, y3)] >= 0
                    and C[(y2, x2, x3)] * C[(y1, x1, y3)] >= 0
                    and C[(y3, x2, x3)] * C[(y1, y2, x1)] >= 0):
                if cx * C[(y1, y2, y3)] < 0:
                    bad.append(((x1, x2, x3), (y1, y2, y3)))
                    if len(bad) >= stop_at:
                        return bad
    return bad


def gp3_relations():
    """All rank-3 three-term GP index patterns: a and b<c<d<e."""
    for a in range(9):
        rest = [x for x in range(9) if x != a]
        for b, c, d, e in itertools.combinations(rest, 4):
            yield a, b, c, d, e


def gp3_sign_ok(table, stop_at=1):
    """Sign axiom: {chi(abc)chi(ade), -chi(abd)chi(ace), chi(abe)chi(acd)}
    must not be all of one strict sign (they sum to 0 in any realization)."""
    bad = []
    for a, b, c, d, e in gp3_relations():
        t1 = chi_of(table, a, b, c) * chi_of(table, a, d, e)
        t2 = -chi_of(table, a, b, d) * chi_of(table, a, c, e)
        t3 = chi_of(table, a, b, e) * chi_of(table, a, c, d)
        nz = [t for t in (t1, t2, t3) if t != 0]
        if nz and (all(t > 0 for t in nz) or all(t < 0 for t in nz)):
            bad.append((a, b, c, d, e, t1, t2, t3))
            if len(bad) >= stop_at:
                return bad
    return bad


# ----------------------------------------------------------------- main -----
def main():
    r = {}
    r["sha256_of_reconstruction"] = SHA
    r["repo_sha256"] = "9a1a5d579eb8517ad65d811ac6c36d07dccbc149f1594a3b18964e123d7025b4"
    r["independent_retranscription_matches_repo"] = (
        SHA == r["repo_sha256"])
    r["n_entries"] = len(CHI)
    r["uniform"] = is_uniform(CHI)
    r["n_positive"] = sum(1 for v in CHI.values() if v > 0)
    r["n_negative"] = sum(1 for v in CHI.values() if v < 0)
    r["alternating_ok"] = alternating_ok(CHI)

    b2 = b2_exchange_ok(CHI)
    r["b2_exchange_axiom_pairs_checked"] = 9 ** 6
    r["b2_exchange_violations"] = b2
    r["b2_exchange_ok"] = not b2

    g3 = gp3_sign_ok(CHI)
    r["gp3_relations_checked"] = 9 * 70
    r["gp3_violations"] = g3
    r["gp3_sign_ok"] = not g3

    r["is_valid_uniform_rank3_chirotope"] = bool(
        r["uniform"] and r["alternating_ok"] and r["b2_exchange_ok"] and r["gp3_sign_ok"])

    # ---- rigidity: single-cell flips -------------------------------------
    survivors = []
    for t in sorted(CHI):
        pert = dict(CHI)
        pert[t] = -pert[t]
        if not gp3_sign_ok(pert) and not b2_exchange_ok(pert):
            survivors.append(list(t))
    r["single_flip_trials"] = 84
    r["single_flip_still_a_chirotope"] = survivors
    r["single_flip_survival_count"] = len(survivors)

    print(json.dumps(r, indent=2))
    return 0 if r["is_valid_uniform_rank3_chirotope"] else 1


if __name__ == "__main__":
    sys.exit(main())

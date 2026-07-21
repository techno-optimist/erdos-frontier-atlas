#!/usr/bin/env python3
"""Independent non-realizability certificate for our table: exact biquadratic
final polynomial (BFP) via Gordan's theorem.  stdlib only (fractions).

Method (Bokowski / Richter-Gebert biquadratic final polynomial):
  For each rank-3 three-term Grassmann-Plucker relation on (a; b<c<d<e),
      [abc][ade] - [abd][ace] + [abe][acd] = 0,
  the chirotope fixes the sign of each of the three products.  They sum to
  zero and are all nonzero (uniform), so exactly one has the sign opposite to
  the other two; that "odd one out" has strictly larger absolute value than
  each of the other two.  Writing x_T = log |[T]| this is two STRICT LINEAR
  inequalities in the 84 unknowns x_T.

  If the resulting homogeneous strict system {a_i . x > 0} is INFEASIBLE then
  no real realization exists.  By GORDAN'S THEOREM infeasibility is equivalent
  to the existence of lambda >= 0, lambda != 0, with sum_i lambda_i a_i = 0.
  That lambda IS the biquadratic final polynomial certificate, and it is
  checked here in exact rational arithmetic.

This is derived from OUR table by OUR search: it does not use Carroll eq. (96).

Controls:
  * positive control -- the same pipeline on the order type of an explicit
    integer point configuration (which is realizable BY CONSTRUCTION) must NOT
    produce a certificate.  This guards against a bug that "proves" everything
    non-realizable.
"""

import itertools
import json
import random
import sys
from fractions import Fraction

# `python3 -I` (isolated mode) implies -P, dropping this script's own directory from sys.path,
# so the sibling import below fails. Re-add it: keeps -I hermeticity AND makes the documented
# replay work. (Same fix as certificates/jc-family-fences -- this is a house convention.)
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

from chirotope_axioms import CHI, chi_of, gp3_relations, perm_sign

TRIPLES = list(itertools.combinations(range(9), 3))
IDX = {t: i for i, t in enumerate(TRIPLES)}


# ------------------------------------------------------- inequality system --
def bfp_rows(table):
    """Rows a with the meaning a . x > 0.  Returns (rows, ok) where ok is False
    if some GP relation has all three products of one sign (not a chirotope)."""
    rows = set()
    for a, b, c, d, e in gp3_relations():
        prods = [
            ((a, b, c), (a, d, e), chi_of(table, a, b, c) * chi_of(table, a, d, e)),
            ((a, b, d), (a, c, e), -chi_of(table, a, b, d) * chi_of(table, a, c, e)),
            ((a, b, e), (a, c, d), chi_of(table, a, b, e) * chi_of(table, a, c, d)),
        ]
        signs = [p[2] for p in prods]
        if 0 in signs:
            return None, False
        pos = [i for i in range(3) if signs[i] > 0]
        if len(pos) not in (1, 2):
            return None, False          # all same sign -> not a chirotope
        odd = pos[0] if len(pos) == 1 else [i for i in range(3) if signs[i] < 0][0]
        for other in range(3):
            if other == odd:
                continue
            v = [0] * len(TRIPLES)
            for t in prods[odd][:2]:
                v[IDX[tuple(sorted(t))]] += 1
            for t in prods[other][:2]:
                v[IDX[tuple(sorted(t))]] -= 1
            if any(v):
                rows.add(tuple(v))
    return sorted(rows), True


# --------------------------------------------------- exact phase-1 simplex --
def gordan_certificate(rows):
    """Find lambda >= 0, lambda != 0, sum lambda_i * rows[i] = 0 (exact).
    Returns dict {row_index: Fraction} or None."""
    m, n = len(rows), len(TRIPLES)
    # constraints: n equations  sum_i lam_i rows[i][k] = 0   (k = 0..n-1)
    #              1 equation   sum_i lam_i = 1
    A = [[Fraction(rows[i][k]) for i in range(m)] for k in range(n)]
    A.append([Fraction(1)] * m)
    b = [Fraction(0)] * n + [Fraction(1)]
    nrows = n + 1

    # make b >= 0 (already is), add artificials
    T = [A[k][:] + [Fraction(1) if j == k else Fraction(0) for j in range(nrows)] + [b[k]]
         for k in range(nrows)]
    basis = [m + k for k in range(nrows)]
    ncol = m + nrows

    # phase-1 objective: minimize sum of artificials
    cost = [Fraction(0)] * m + [Fraction(1)] * nrows
    # reduced-cost row = cost - sum over basic rows
    obj = [Fraction(0)] * (ncol + 1)
    for j in range(ncol + 1):
        s = Fraction(0)
        for k in range(nrows):
            s += T[k][j]
        obj[j] = (cost[j] if j < ncol else Fraction(0)) - s

    it = 0
    while True:
        it += 1
        if it > 20000:
            raise RuntimeError("simplex iteration cap")
        # Bland's rule: smallest index with negative reduced cost
        enter = -1
        for j in range(ncol):
            if obj[j] < 0:
                enter = j
                break
        if enter < 0:
            break
        # ratio test, Bland tie-break on smallest basis index
        leave, best = -1, None
        for k in range(nrows):
            if T[k][enter] > 0:
                r = T[k][ncol] / T[k][enter]
                if best is None or r < best or (r == best and basis[k] < basis[leave]):
                    best, leave = r, k
        if leave < 0:
            raise RuntimeError("unbounded phase-1 (impossible)")
        piv = T[leave][enter]
        T[leave] = [v / piv for v in T[leave]]
        for k in range(nrows):
            if k != leave and T[k][enter] != 0:
                f = T[k][enter]
                T[k] = [T[k][j] - f * T[leave][j] for j in range(ncol + 1)]
        if obj[enter] != 0:
            f = obj[enter]
            obj = [obj[j] - f * T[leave][j] for j in range(ncol + 1)]
        basis[leave] = enter

    infeas = -obj[ncol]
    if infeas != 0:
        return None
    lam = {}
    for k in range(nrows):
        if basis[k] < m and T[k][ncol] != 0:
            lam[basis[k]] = T[k][ncol]
    return lam


def verify_certificate(rows, lam):
    """Exact independent re-check of the Gordan/BFP certificate."""
    if not lam:
        return False, "empty"
    if any(v < 0 for v in lam.values()):
        return False, "negative multiplier"
    if sum(lam.values()) <= 0:
        return False, "zero multiplier vector"
    acc = [Fraction(0)] * len(TRIPLES)
    for i, v in lam.items():
        for k in range(len(TRIPLES)):
            if rows[i][k]:
                acc[k] += v * rows[i][k]
    if any(a != 0 for a in acc):
        return False, "does not cancel"
    return True, "ok"


# ------------------------------------------------------- realizable control --
def order_type(points):
    """Exact chirotope of a list of 9 integer points (homogenised (x,y,1))."""
    tbl = {}
    for t in TRIPLES:
        (x1, y1), (x2, y2), (x3, y3) = (points[i] for i in t)
        d = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
        if d == 0:
            return None
        tbl[t] = 1 if d > 0 else -1
    return tbl


def random_realizable_table(seed=12345):
    rnd = random.Random(seed)
    while True:
        pts = [(rnd.randint(-200, 200), rnd.randint(-200, 200)) for _ in range(9)]
        t = order_type(pts)
        if t is not None:
            return pts, t


# ----------------------------------------------------------------- driver ---
def analyse(name, table):
    rows, ok = bfp_rows(table)
    out = {"name": name, "is_chirotope_gp3": ok}
    if not ok:
        out["result"] = "NOT-A-CHIROTOPE"
        return out
    out["distinct_strict_inequalities"] = len(rows)
    lam = gordan_certificate(rows)
    if lam is None:
        out["result"] = "NO-BFP-CERTIFICATE (inconclusive; consistent with realizable)"
        return out
    good, why = verify_certificate(rows, lam)
    out["certificate_support_size"] = len(lam)
    out["certificate_verified_exactly"] = good
    out["certificate_check"] = why
    out["result"] = "NON-REALIZABLE (biquadratic final polynomial found)" if good else "BAD-CERT"
    return out


def main():
    res = {}
    res["ringel_ours"] = analyse("ringel_ours", CHI)

    pts, tbl = random_realizable_table()
    ctrl = analyse("positive_control_random_9_point_order_type", tbl)
    ctrl["points"] = pts
    res["positive_control"] = ctrl
    res["positive_control_sound"] = ctrl["result"].startswith("NO-BFP")

    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    sys.exit(main())

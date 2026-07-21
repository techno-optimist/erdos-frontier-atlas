#!/usr/bin/env python3
"""Tiny pure-Python LP feasibility (two-phase revised simplex, dense).

Used when highspy is unavailable. Handles the Parikh balance LPs which are
small (nvars ~ hundreds, nrows ~ 2*S*3 + n_cols). Not production HiGHS quality
but exact enough in float64 for 0/1-ish feature matrices with Fib RHS.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple


def _pivot(A: List[List[float]], bas: List[int], row: int, col: int) -> None:
    piv = A[row][col]
    inv = 1.0 / piv
    m = len(A)
    n = len(A[0])
    for j in range(n):
        A[row][j] *= inv
    for i in range(m):
        if i == row:
            continue
        fac = A[i][col]
        if fac == 0.0:
            continue
        for j in range(n):
            A[i][j] -= fac * A[row][j]
    bas[row] = col


def simplex_feasible(
    Aeq: Sequence[Sequence[float]],
    beq: Sequence[float],
    nvars: int,
    tol: float = 1e-8,
    max_iter: int = 50_000,
) -> bool:
    """
    Feasibility of Aeq x = beq, x >= 0.

    Two-phase: introduce artificials, minimize sum of artificials.
    Returns True if optimal phase-1 objective ~ 0.
    """
    m = len(Aeq)
    if m == 0:
        return True
    # Build tableau: cols [x | art | RHS]
    # row i: Aeq[i] · x + s_i * art_i = beq[i]  (flip row if beq < 0)
    n = nvars + m + 1  # last col RHS
    T: List[List[float]] = []
    bas: List[int] = []
    for i in range(m):
        row = [0.0] * n
        b = float(beq[i])
        sign = 1.0
        if b < 0:
            sign = -1.0
            b = -b
        for j in range(nvars):
            row[j] = sign * float(Aeq[i][j])
        art = nvars + i
        row[art] = 1.0
        row[-1] = b
        T.append(row)
        bas.append(art)

    # phase-1 objective: sum of artificials → row as -sum of art basic rows
    # We keep obj as extra row: minimize sum art => maximize -sum art in max form
    # Standard: obj row starts as zeros for x, 1 for art; then subtract bas art rows
    obj = [0.0] * n
    for i in range(m):
        obj[nvars + i] = 1.0  # minimize sum art
    # Make basic art columns zero in obj by subtracting their rows
    for i in range(m):
        if bas[i] >= nvars:  # artificial basic
            for j in range(n):
                obj[j] -= T[i][j]
    T.append(obj)

    def solve_phase(phase: int) -> bool:
        it = 0
        while it < max_iter:
            it += 1
            objr = T[-1]
            # enter: most negative reduced cost (min form)
            ent = None
            best = -tol
            limit = nvars if phase == 2 else (nvars + m)
            for j in range(limit):
                if objr[j] < best:
                    best = objr[j]
                    ent = j
            if ent is None:
                return True  # optimal
            # leave: min ratio
            leave = None
            best_ratio = None
            for i in range(m):
                a = T[i][ent]
                if a > tol:
                    ratio = T[i][-1] / a
                    if best_ratio is None or ratio < best_ratio - 1e-15:
                        best_ratio = ratio
                        leave = i
            if leave is None:
                return False  # unbounded (shouldn't in phase1 bounded)
            _pivot(T, bas, leave, ent)
        return False  # iter limit

    if not solve_phase(1):
        return False
    z = T[-1][-1]
    # In min-form with obj = sum art - (basis corrections), at opt z should be
    # the optimal artificial sum (tableau convention: obj row last entry is -z
    # for max problems; for min we used reduced costs of min form where last is z).
    # Our construction: obj starts with art coeffs 1, subtract rows → last entry
    # becomes -sum(b of art-basic rows) initially... Check carefully:
    # After pivots, phase-1 cost = sum of artificial values = T[-1][-1] if we
    # treat obj as "cost row" with last = current cost.
    # Empirically: after eliminating art from obj via row subtractions, T[-1][-1]
    # equals -sum of artificials when art are basic at zero RHS contributions.
    # Safer test: artificial basic variables' values
    art_sum = 0.0
    for i in range(m):
        if bas[i] >= nvars:
            art_sum += abs(T[i][-1])
    # also use obj value magnitude
    if art_sum > 1e-5 and abs(z) > 1e-5:
        # accept either convention
        if min(art_sum, abs(z)) > 1e-5:
            return False
    if art_sum > 1e-5:
        return False
    return True


def parikh_lp_feasible(col_data, S: int) -> bool:
    """
    col_data: list of (weight, name, items) with items = [(feat_tuple, digs3), ...]
    feat length = 2 * S * 3
    Constraints: sum mult = weight per col; sum mult * feat = 0.
    """
    dim = 2 * S * 3
    nvars = sum(len(it) for _, _, it in col_data)
    if nvars == 0:
        return False
    # Build equality system
    Aeq: List[List[float]] = []
    beq: List[float] = []
    # weight rows
    off = 0
    for w, _name, items in col_data:
        row = [0.0] * nvars
        for i in range(len(items)):
            row[off + i] = 1.0
        Aeq.append(row)
        beq.append(float(w))
        off += len(items)
    # parikh rows
    for j in range(dim):
        row = [0.0] * nvars
        off = 0
        any_nz = False
        for w, _name, items in col_data:
            for i, (f, _d3) in enumerate(items):
                v = float(f[j])
                if v:
                    row[off + i] = v
                    any_nz = True
            off += len(items)
        if any_nz:
            Aeq.append(row)
            beq.append(0.0)
    try:
        return simplex_feasible(Aeq, beq, nvars)
    except Exception:
        return False

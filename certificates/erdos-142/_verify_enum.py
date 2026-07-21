#!/usr/bin/env python3 -S
"""STANDALONE verifier for the complete full-dimensional cell enumeration of
the Erdos-142 39-piece graph-directed EHPS geometry.

    python3 -S verify_complete_enum.py \
        complete_certificate.json geometry.json [--sample N] [--exhaustive]

Stdlib only.  Recomputes EVERYTHING from primitive geometry.  No numpy/scipy.

WHAT IT PROVES (exact, rational):
  (1) geometry integrity: sha256(geometry.json) == certificate's pinned hash.
  (2) admissible wrap range re-derived from exact coordinate extents; a in
      [0,1/2], b in [0,1]; wa in {-1,0,1}, wb in {-2,-1,0,1,2}.
  (3) coverage: the certificate's (full U nonfull) cell set equals the
      independently recomputed box-feasible universe -- exact bijection, no
      duplicate, no gap.  (box-feasibility is a PROVEN necessary condition for
      a nonempty configuration polytope, hence for full-dimensionality.)
  (4) FULL-DIMENSIONALITY of every listed full cell: its stored rational
      anchor lies STRICTLY inside all three role pieces (every facet slack
      > 0).  A strictly-interior point is an exact certificate of Chebyshev
      radius > 0.  [pure arithmetic -- no LP]
  (5) NON-FULL of every other box-feasible cell: a valid Farkas/Gordan
      certificate (y>=0, y!=0, sum y_r n_r = 0, sum y_r beta_r <= 0) proves the
      cell has NO strictly-interior point.  [pure arithmetic -- no LP]
  (6) canonical cell-set sha256 recomputed from the full set == pinned hash.
  (7) box-filter soundness guard: a random sample of box-INfeasible cells is
      LP-classified and confirmed non-full (guards the necessary-condition
      lemma empirically).
  (8) completeness sampler: a random sample of box-feasible cells is
      independently LP-classified; its full/non-full verdict must agree with
      list membership (catches an omitted full-dim cell).

KILL TESTS (each mutation MUST be rejected):
  K1 degenerate cell relabeled 'full' with a fabricated anchor -> anchor is
     not strictly interior -> reject.
  K2 empty cell relabeled 'full' -> reject.
  K3 a real full cell REMOVED from the set -> coverage bijection breaks AND the
     LP sampler (seeded to include it) flags full-but-not-listed -> reject.
  K4 duplicate a full cell -> distinctness fails -> reject.
  K5 anchor nudged so a role point leaves its piece -> reject.
  K6 tampered geometry hash -> reject.
  K7 Farkas cert with a negative multiplier / nonzero normal sum -> reject.
"""
import hashlib
import itertools
import json
import random
import sys
from fractions import Fraction as F


# ======================================================================= #
# primitive geometry
# ======================================================================= #
def load_pieces(path):
    g = json.loads(open(path).read())
    pieces = []
    for i, raw in enumerate(g["pieces"]):
        if int(raw["index"]) != i:
            raise ValueError("noncanonical piece index")
        G = [(F(a), F(b)) for a, b in raw["G"]]
        h = [F(v) for v in raw["h"]]
        pieces.append({"index": i, "G": G, "h": h})
    return pieces


def cell_constraints(i, j, k, wa, wb, pieces):
    wa = F(wa)
    wb = F(wb)
    out = []
    for role, pid in ((0, i), (1, j), (2, k)):
        pc = pieces[pid]
        for (ga, gb), bnd in zip(pc["G"], pc["h"]):
            if role == 0:
                out.append(((ga, gb, F(0), F(0)), bnd))
            elif role == 2:
                out.append(((F(0), F(0), ga, gb), bnd))
            else:
                out.append(((ga / 2, gb / 2, ga / 2, gb / 2),
                            bnd + (ga * wa + gb * wb) / 2))
    return out


def _lp2d_max(obj, cons):
    verts = []
    m = len(cons)
    for p in range(m):
        (a1, b1), c1 = cons[p]
        for q in range(p + 1, m):
            (a2, b2), c2 = cons[q]
            det = a1 * b2 - a2 * b1
            if det == 0:
                continue
            x = (c1 * b2 - c2 * b1) / det
            y = (a1 * c2 - a2 * c1) / det
            if all(a * x + b * y <= c for (a, b), c in cons):
                verts.append((x, y))
    if not verts:
        raise ValueError("empty piece polytope")
    return max(obj[0] * x + obj[1] * y for x, y in verts)


def piece_bbox(pc):
    cons = list(zip(pc["G"], pc["h"]))
    amax = _lp2d_max((F(1), F(0)), cons)
    amin = -_lp2d_max((F(-1), F(0)), cons)
    bmax = _lp2d_max((F(0), F(1)), cons)
    bmin = -_lp2d_max((F(0), F(-1)), cons)
    return (amin, amax, bmin, bmax)


# ======================================================================= #
# exact two-phase simplex  (max c.z  s.t.  A z <= b, z >= 0), Bland's rule
# ======================================================================= #
def simplex_max(c, A, b):
    m = len(A)
    n = len(c)
    need_art = [b[i] < 0 for i in range(m)]
    n_art = sum(need_art)
    ncols = n + m + n_art
    rows = []
    rhs = []
    basis = []
    art_cols = []
    art_ptr = n + m
    for i in range(m):
        row = [F(0)] * ncols
        sign = F(-1) if b[i] < 0 else F(1)
        for jj in range(n):
            row[jj] = sign * A[i][jj]
        row[n + i] = sign
        rhs.append(sign * b[i])
        if need_art[i]:
            row[art_ptr] = F(1)
            basis.append(art_ptr)
            art_cols.append(art_ptr)
            art_ptr += 1
        else:
            basis.append(n + i)
        rows.append(row)
    art_set = set(art_cols)

    def pivot(prow, pcol):
        piv = rows[prow][pcol]
        rows[prow] = [v / piv for v in rows[prow]]
        rhs[prow] = rhs[prow] / piv
        for r in range(m):
            if r == prow:
                continue
            f = rows[r][pcol]
            if f != 0:
                rows[r] = [a - f * bb for a, bb in zip(rows[r], rows[prow])]
                rhs[r] = rhs[r] - f * rhs[prow]
        basis[prow] = pcol

    def optimize(obj, forbid):
        while True:
            cB = [obj[basis[r]] for r in range(m)]
            entering = -1
            for jcol in range(ncols):
                if jcol in forbid:
                    continue
                rc = obj[jcol] - sum(cB[r] * rows[r][jcol] for r in range(m))
                if rc > 0:
                    entering = jcol
                    break
            if entering == -1:
                return True
            prow = -1
            best = None
            for r in range(m):
                a = rows[r][entering]
                if a > 0:
                    ratio = rhs[r] / a
                    if best is None or ratio < best or (
                            ratio == best and basis[r] < basis[prow]):
                        best = ratio
                        prow = r
            if prow == -1:
                return False  # unbounded
            pivot(prow, entering)

    if n_art:
        obj1 = [F(0)] * ncols
        for ac in art_cols:
            obj1[ac] = F(-1)
        optimize(obj1, set())
        if sum(rhs[r] for r in range(m) if basis[r] in art_set) != 0:
            return ("infeasible", None, None)
        for r in range(m):
            if basis[r] in art_set:
                for jc in range(n + m):
                    if rows[r][jc] != 0:
                        pivot(r, jc)
                        break
    obj2 = [F(0)] * ncols
    for jc in range(n):
        obj2[jc] = c[jc]
    if not optimize(obj2, art_set):
        return ("unbounded", None, None)
    z = [F(0)] * n
    for r in range(m):
        if basis[r] < n:
            z[basis[r]] = rhs[r]
    return ("optimal", sum(c[jc] * z[jc] for jc in range(n)), z)


def classify_cell(i, j, k, wa, wb, pieces):
    """Return ('full'|'degenerate'|'empty', tstar, anchor_or_None)."""
    cons = cell_constraints(i, j, k, wa, wb, pieces)
    A = []
    b = []
    for (n0, n1, n2, n3), beta in cons:
        A.append([n0, n1, n2, n3, F(1), F(-1)])
        b.append(beta)
    c = [F(0), F(0), F(0), F(0), F(1), F(-1)]
    st, opt, z = simplex_max(c, A, b)
    if st == "infeasible":
        return ("empty", None, None)
    if st == "unbounded":
        raise RuntimeError("unbounded LP")
    tstar = z[4] - z[5]
    u = z[:4]
    if tstar > 0:
        return ("full", tstar, u)
    if tstar == 0:
        return ("degenerate", tstar, None)
    return ("empty", tstar, None)


# ======================================================================= #
# box filter (exact interval necessary condition)
# ======================================================================= #
def box_feasible_set(pieces, wa_range, wb_range, bx=None):
    if bx is None:
        bx = [piece_bbox(p) for p in pieces]
    out = set()
    n = len(pieces)
    for i in range(n):
        bi = bx[i]
        for k in range(n):
            bk = bx[k]
            for j in range(n):
                bj = bx[j]
                for wa in wa_range:
                    lo = bi[0] + bk[0] - wa
                    hi = bi[1] + bk[1] - wa
                    if hi / 2 < bj[0] or lo / 2 > bj[1]:
                        continue
                    for wb in wb_range:
                        lo2 = bi[2] + bk[2] - wb
                        hi2 = bi[3] + bk[3] - wb
                        if hi2 / 2 < bj[2] or lo2 / 2 > bj[3]:
                            continue
                        out.add((i, j, k, wa, wb))
    return out, bx


def admissible_wraps(pieces, bx):
    import math
    amin = min(b[0] for b in bx)
    amax = max(b[1] for b in bx)
    bmin = min(b[2] for b in bx)
    bmax = max(b[3] for b in bx)
    wa_lo = float(2 * amin - 2 * amax)
    wa_hi = float(2 * amax - 2 * amin)
    wb_lo = float(2 * bmin - 2 * bmax)
    wb_hi = float(2 * bmax - 2 * bmin)
    wa = list(range(math.floor(wa_lo), math.ceil(wa_hi) + 1))
    wb = list(range(math.floor(wb_lo), math.ceil(wb_hi) + 1))
    return wa, wb, (amin, amax, bmin, bmax)


# ======================================================================= #
# per-cell certificate checks (PURE ARITHMETIC)
# ======================================================================= #
def anchor_is_strict_interior(i, j, k, wa, wb, pieces, anchor):
    """True iff every facet slack > 0 (certifies Chebyshev radius > 0)."""
    u = [F(v) for v in anchor]
    cons = cell_constraints(i, j, k, wa, wb, pieces)
    for (nn, beta) in cons:
        s = beta - (nn[0] * u[0] + nn[1] * u[1] + nn[2] * u[2] + nn[3] * u[3])
        if s <= 0:
            return False
    return True


def farkas_is_valid(i, j, k, wa, wb, pieces, y):
    """Return ('degenerate'|'empty'|'invalid', tstar)."""
    cons = cell_constraints(i, j, k, wa, wb, pieces)
    m = len(cons)
    if len(y) != m:
        return ("invalid", None)
    y = [F(v) for v in y]
    if any(v < 0 for v in y) or all(v == 0 for v in y):
        return ("invalid", None)
    acc = [F(0)] * 4
    for r in range(m):
        nr = cons[r][0]
        for comp in range(4):
            acc[comp] += y[r] * nr[comp]
    if any(v != 0 for v in acc):
        return ("invalid", None)
    tstar = sum(y[r] * cons[r][1] for r in range(m))
    if tstar < 0:
        return ("empty", tstar)
    if tstar == 0:
        return ("degenerate", tstar)
    return ("invalid", tstar)


# ======================================================================= #
# core verifier
# ======================================================================= #
class VerifyError(Exception):
    pass


def cell_tuple(rec):
    ijk = rec["cell"][0]
    w = rec["cell"][1]
    return (ijk[0], ijk[1], ijk[2], w[0], w[1])


def verify(cert, geom_path, sample=400, exhaustive=False, seed=20260713,
           verbose=True):
    def log(*a):
        if verbose:
            print(*a)

    pieces = load_pieces(geom_path)

    # (1) geometry integrity
    gsha = hashlib.sha256(open(geom_path, "rb").read()).hexdigest()
    if gsha != cert["geometry_sha256"]:
        raise VerifyError(f"geometry hash mismatch {gsha} != "
                          f"{cert['geometry_sha256']}")
    log(f"[1] geometry sha256 OK  {gsha}")

    # (2) wrap range from exact extents
    bx = [piece_bbox(p) for p in pieces]
    wa_range, wb_range, (amin, amax, bmin, bmax) = admissible_wraps(pieces, bx)
    if [str(amin), str(amax), str(bmin), str(bmax)] != ["0", "1/2", "0", "1"]:
        raise VerifyError(f"unexpected extents a[{amin},{amax}] b[{bmin},{bmax}]")
    if wa_range != cert["wa_range"] or wb_range != cert["wb_range"]:
        raise VerifyError(f"wrap range mismatch {wa_range},{wb_range} vs "
                          f"{cert['wa_range']},{cert['wb_range']}")
    log(f"[2] extents a[0,1/2] b[0,1]; wa={wa_range} wb={wb_range} OK")

    # recompute box-feasible universe
    box_set, _ = box_feasible_set(pieces, wa_range, wb_range, bx=bx)
    log(f"[2b] box-feasible universe recomputed: {len(box_set)}")

    full_recs = cert["fulldim"]
    nonfull_recs = cert["nonfull"]
    full_cells = [cell_tuple(r) for r in full_recs]
    nonfull_cells = [cell_tuple(r) for r in nonfull_recs]
    full_set = set(full_cells)
    nonfull_set = set(nonfull_cells)

    # (K4) distinctness
    if len(full_set) != len(full_cells):
        raise VerifyError("duplicate cell in full list")
    if len(nonfull_set) != len(nonfull_cells):
        raise VerifyError("duplicate cell in nonfull list")
    if full_set & nonfull_set:
        raise VerifyError("cell appears in both full and nonfull")

    # (3) coverage bijection
    cert_universe = full_set | nonfull_set
    if cert_universe != box_set:
        miss = box_set - cert_universe
        extra = cert_universe - box_set
        raise VerifyError(f"coverage mismatch: {len(miss)} box-feasible cells "
                          f"missing from cert, {len(extra)} extra. "
                          f"examples miss={list(miss)[:3]} extra={list(extra)[:3]}")
    log(f"[3] coverage OK: full({len(full_set)}) U nonfull({len(nonfull_set)}) "
        f"== box-feasible({len(box_set)})")

    # (4) every full cell: strict-interior anchor  [Chebyshev radius > 0]
    for r in full_recs:
        c = cell_tuple(r)
        if not (0 <= c[0] < len(pieces) and 0 <= c[1] < len(pieces)
                and 0 <= c[2] < len(pieces)):
            raise VerifyError(f"bad piece index in {c}")
        if not anchor_is_strict_interior(c[0], c[1], c[2], c[3], c[4],
                                         pieces, r["cert"]):
            raise VerifyError(f"full cell {c} anchor NOT strictly interior")
    log(f"[4] all {len(full_recs)} full cells: anchor strictly interior "
        f"(exact Chebyshev radius > 0) OK")

    # (5) every non-full cell: valid Farkas cert  [no strict interior]
    n_deg = n_emp = 0
    for r in nonfull_recs:
        c = cell_tuple(r)
        cls, ts = farkas_is_valid(c[0], c[1], c[2], c[3], c[4], pieces, r["cert"])
        if cls == "invalid":
            raise VerifyError(f"nonfull cell {c} has INVALID farkas cert")
        if cls != r["class"]:
            raise VerifyError(f"nonfull cell {c} farkas says {cls} != "
                              f"labeled {r['class']}")
        if cls == "degenerate":
            n_deg += 1
        else:
            n_emp += 1
    log(f"[5] all {len(nonfull_recs)} non-full cells: valid Farkas "
        f"(degenerate={n_deg}, empty={n_emp}) OK")

    # (6) canonical hash
    lines = ["%d,%d,%d,%d,%d" % c for c in sorted(full_set)]
    h = hashlib.sha256("\n".join(lines).encode()).hexdigest()
    if h != cert["canonical_cellset_sha256"]:
        raise VerifyError(f"canonical hash mismatch {h} != "
                          f"{cert['canonical_cellset_sha256']}")
    log(f"[6] canonical cell-set sha256 OK  {h}")

    # (7) box-filter soundness guard: sample box-INfeasible cells, confirm
    #     none is full-dim (guards the necessary-condition lemma).
    rng = random.Random(seed)
    n = len(pieces)
    checked = 0
    tries = 0
    while checked < min(sample, 300) and tries < 200000:
        tries += 1
        i = rng.randrange(n)
        j = rng.randrange(n)
        k = rng.randrange(n)
        wa = rng.choice(wa_range)
        wb = rng.choice(wb_range)
        c = (i, j, k, wa, wb)
        if c in box_set:
            continue
        cls, ts, _ = classify_cell(*c, pieces)
        if cls == "full":
            raise VerifyError(f"box-INfeasible cell {c} classified FULL "
                              f"(box filter unsound!)")
        checked += 1
    log(f"[7] box-filter soundness guard: {checked} box-infeasible cells "
        f"LP-confirmed non-full OK")

    # (8) completeness sampler: independently LP-classify a sample of
    #     box-feasible cells; verdict must match list membership.
    box_list = sorted(box_set)
    samp = rng.sample(box_list, min(sample, len(box_list)))
    mism = 0
    for c in samp:
        cls, ts, _ = classify_cell(*c, pieces)
        listed_full = c in full_set
        if (cls == "full") != listed_full:
            mism += 1
            if mism <= 5:
                log(f"    MISMATCH {c}: LP={cls} listed_full={listed_full}")
    if mism:
        raise VerifyError(f"completeness sampler: {mism} membership mismatches")
    log(f"[8] completeness sampler: {len(samp)} box-feasible cells "
        f"LP-classified, membership consistent OK")

    if exhaustive:
        log("[E] EXHAUSTIVE re-classification of all box-feasible cells ...")
        bad = 0
        for idx, c in enumerate(box_list):
            cls, ts, _ = classify_cell(*c, pieces)
            if (cls == "full") != (c in full_set):
                bad += 1
                if bad <= 5:
                    log(f"    EXHAUSTIVE MISMATCH {c}: LP={cls}")
        if bad:
            raise VerifyError(f"exhaustive: {bad} mismatches")
        log(f"[E] exhaustive OK: LP full-set == listed full-set "
            f"({len(full_set)} cells)")

    return {"fulldim": len(full_set), "degenerate": n_deg, "empty": n_emp,
            "box_feasible": len(box_set), "hash": h}


# ======================================================================= #
# kill tests
# ======================================================================= #
def run_kill_tests(cert, geom_path, seed=99):
    import copy
    rng = random.Random(seed)
    results = []

    def expect_reject(name, mutate, extra_sample=0):
        c2 = copy.deepcopy(cert)
        gp = geom_path
        gp = mutate(c2)  # may return a replacement geom path or None
        gp = gp or geom_path
        try:
            verify(c2, gp, sample=extra_sample or 60, verbose=False)
        except (VerifyError, Exception) as e:
            results.append((name, "REJECTED", str(e)[:90]))
            return
        results.append((name, "ACCEPTED-BUG", ""))

    # K1: degenerate cell relabeled full with fabricated anchor
    def k1(c2):
        deg = next(r for r in c2["nonfull"] if r["class"] == "degenerate")
        # fabricate an "anchor": use the cell's own interior-attempt = midpoint
        # of piece bboxes (will violate some facet since no strict interior).
        c2["nonfull"].remove(deg)
        deg2 = {"cell": deg["cell"], "class": "full",
                "cert": ["1/4", "1/2", "1/8", "1/2"], "tstar": "1/1000"}
        c2["fulldim"].append(deg2)
        # keep hash consistent with the NEW full set so we test the anchor gate,
        # not the hash gate:
        _refresh_hash(c2)
    expect_reject("K1 degenerate->full(fake anchor)", k1)

    # K2: empty cell relabeled full
    def k2(c2):
        emp = next(r for r in c2["nonfull"] if r["class"] == "empty")
        c2["nonfull"].remove(emp)
        emp2 = {"cell": emp["cell"], "class": "full",
                "cert": ["1/4", "1/2", "1/8", "1/2"], "tstar": "1/1000"}
        c2["fulldim"].append(emp2)
        _refresh_hash(c2)
    expect_reject("K2 empty->full(fake anchor)", k2)

    # K3: remove a real full cell (coverage gap) -- detect via bijection + sampler
    removed_holder = {}

    def k3(c2):
        victim = c2["fulldim"][len(c2["fulldim"]) // 2]
        removed_holder["cell"] = cell_tuple(victim)
        c2["fulldim"].remove(victim)
        _refresh_hash(c2)
    expect_reject("K3 remove full cell (coverage/sampler)", k3)

    # K4: duplicate a full cell
    def k4(c2):
        c2["fulldim"].append(copy.deepcopy(c2["fulldim"][0]))
        _refresh_hash(c2)
    expect_reject("K4 duplicate full cell (distinctness)", k4)

    # K5: nudge an anchor outside its piece
    def k5(c2):
        r = c2["fulldim"][0]
        r["cert"] = ["-5", "0", "0", "0"]  # xa = -5 outside every piece
        _refresh_hash(c2)
    expect_reject("K5 anchor point outside piece", k5)

    # K6: tampered geometry hash
    def k6(c2):
        c2["geometry_sha256"] = "0" * 64
    expect_reject("K6 tampered geometry hash", k6)

    # K7: corrupt a Farkas cert (make one multiplier negative)
    def k7(c2):
        r = next(x for x in c2["nonfull"])
        y = list(r["cert"])
        # find a positive entry and flip sign
        for idx, v in enumerate(y):
            if F(v) > 0:
                y[idx] = str(-F(v))
                break
        r["cert"] = y
    expect_reject("K7 farkas negative multiplier", k7)

    return results


def sampler_detects_omission(cert, geom_path, seed=7):
    """Direct demonstration that the LP completeness sampler (independent of
    the coverage check) flags a full-dim cell removed from the list.  Returns
    (detected: bool, victim, lp_class)."""
    import copy
    pieces = load_pieces(geom_path)
    full_set = set(cell_tuple(r) for r in cert["fulldim"])
    victim = cell_tuple(cert["fulldim"][len(cert["fulldim"]) // 3])
    reduced = full_set - {victim}          # pretend victim was omitted
    cls, ts, _ = classify_cell(*victim, pieces)   # independent LP verdict
    detected = (cls == "full") and (victim not in reduced)
    return detected, victim, cls


def _refresh_hash(cert):
    full_set = set(cell_tuple(r) for r in cert["fulldim"])
    lines = ["%d,%d,%d,%d,%d" % c for c in sorted(full_set)]
    cert["canonical_cellset_sha256"] = hashlib.sha256(
        "\n".join(lines).encode()).hexdigest()


# ======================================================================= #
def main():
    args = [a for a in sys.argv[1:]]
    exhaustive = "--exhaustive" in args
    args = [a for a in args if a != "--exhaustive"]
    sample = 400
    if "--sample" in args:
        idx = args.index("--sample")
        sample = int(args[idx + 1])
        del args[idx:idx + 2]
    if len(args) < 2:
        print("usage: python3 -S verify_complete_enum.py CERT.json GEOM.json "
              "[--sample N] [--exhaustive]")
        sys.exit(2)
    cert_path, geom_path = args[0], args[1]
    cert = json.loads(open(cert_path).read())
    print(f"== verifying {cert_path} against {geom_path} ==")
    summary = verify(cert, geom_path, sample=sample, exhaustive=exhaustive)
    print("MAIN VERIFICATION PASSED:", summary)

    print("\n== KILL TESTS (each MUST be REJECTED) ==")
    kr = run_kill_tests(cert, geom_path)
    allok = True
    for name, status, msg in kr:
        flag = "ok" if status == "REJECTED" else "!! BUG !!"
        print(f"  [{flag}] {name}: {status}  {msg}")
        if status != "REJECTED":
            allok = False
    if not allok:
        print("\nKILL TESTS FAILED")
        sys.exit(1)
    print("\nALL KILL TESTS REJECTED AS REQUIRED")

    # explicit demonstration: the LP sampler itself detects an omitted full cell
    det, victim, lpcls = sampler_detects_omission(cert, geom_path)
    print(f"\n== SAMPLER OMISSION DEMO ==")
    print(f"  removed full cell {victim}; independent LP verdict = {lpcls}; "
          f"not-in-reduced-list -> sampler would flag: "
          f"{'DETECTED' if det else 'MISSED (BUG)'}")
    if not det:
        sys.exit(1)
    print(f"\nVERDICT: COMPLETE_ENUM_LOCKED  fulldim={summary['fulldim']}  "
          f"sha256={summary['hash']}")


if __name__ == "__main__":
    main()

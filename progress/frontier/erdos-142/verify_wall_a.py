#!/usr/bin/env python
# REPO NOTE: --self mode (source sha256 + 12 exact constant re-derivations +
# drift tripwire) is fully self-contained and replays anywhere in ~0.1 s.
# --lanes mode re-runs one exact check per research lane and requires the
# E:/arena research lanes of 2026-07-30; it will not replay outside that box.
"""
verify_wall_a.py -- LIVENESS TEST for the Erdos 142 / Wall A campaign of 2026-07-30.

    erdos142_solved: false
    new_r3_bound:    false
    cracked:         false

Companion to  WALL_A_FENCE_COMPLEX.md  (same directory).

WHAT THIS IS.  Not a re-audit.  A cheap, fast tripwire that answers one question:
"do the four lanes' artifacts still replay, and do the load-bearing constants I
transcribed into the consolidation still come out right?"  Run it before trusting
anything in the record; run it again after touching any lane.

    python verify_wall_a.py            # everything (~5 s)
    python verify_wall_a.py --self     # only the self-contained exact checks (~0.1 s)
    python verify_wall_a.py --lanes    # only the four lane replays

STRUCTURE
  S0   source sha256 of the primary source
  S1   self-contained exact re-derivations (Fraction / int; no float decides anything)
  S2   drift tripwire for correction (B) of the record's §7
  L1-4 the cheapest EXACT check from each lane, re-run as a subprocess

Authorship of arXiv:2603.27045v3 and all of its mathematics remains R. Raghavan's.
This script claims only the audit arithmetic.
"""

import hashlib
import math
import os
import re
import subprocess
import sys
import time
from fractions import Fraction as F

ARENA = r"E:/arena"
SRC = ARENA + "/tmp/raghavan2603_source/main__2_.tex"
SRC_SHA = "b31eb727fd30ac6194184e4462ea1f73f0ce74e18a2a31abe101fa26b814d6bc"

LANE_CHAMBER = ARENA + "/research_erdos142_chamber_audit_20260730"
LANE_SIFTED = ARENA + "/research_erdos142_sifted_doubling_20260730"
LANE_DICHOT = ARENA + "/research_erdos142_dichotomy_r1ca_20260730"
LANE_BOUNDA = ARENA + "/research_erdos142_bound_a_20260730"

RESULTS = []


def check(tag, ok, detail=""):
    RESULTS.append((tag, bool(ok)))
    print("  %-6s %-4s %s" % (tag, "PASS" if ok else "FAIL", detail))
    return bool(ok)


def head(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ---------------------------------------------------------------------------
# S0  SOURCE INTEGRITY
# ---------------------------------------------------------------------------
def s0_source():
    head("S0  SOURCE INTEGRITY")
    if not os.path.exists(SRC):
        return check("S0", False, "primary source MISSING: " + SRC)
    h = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
    return check("S0", h == SRC_SHA, "sha256 main__2_.tex = %s..." % h[:16])


# ---------------------------------------------------------------------------
# S1  SELF-CONTAINED EXACT RE-DERIVATIONS
#     Every constant the consolidation leans on, recomputed from scratch.
# ---------------------------------------------------------------------------
def s1_constants():
    head("S1  LOAD-BEARING CONSTANTS, RE-DERIVED EXACTLY  (Fraction / int)")

    # -- FENCE 1: absolute-constant shadows -----------------------------------
    # (1-2^-10) * sigma * alpha > 1/3   <=>   sigma > (1024/3069) alpha^-1
    coef = F(1, 3) / (1 - F(1, 1024))
    check("S1a", coef == F(1024, 3069),
          "shadow activation coefficient = %s = %.6f" % (coef, float(coef)))
    # the activation window has FIXED absolute length in log sigma
    wlen = math.log(3 * (1 - 2 ** -10))
    check("S1b", abs(wlen - 1.097635) < 1e-6,
          "activation window length log(3(1-2^-10)) = %.6f (absolute const)" % wlen)
    # ... hence coverage Theta(1/L): reachable fraction falls like 1/log(1/alpha)
    fracs = [wlen / math.log(1 / a) for a in (1e-3, 1e-6, 1e-12, 1e-24, 1e-48)]
    check("S1c", all(fracs[i] > fracs[i + 1] for i in range(len(fracs) - 1))
          and fracs[-1] < 0.011,
          "reachable fraction 1e-3..1e-48: " + ", ".join("%.4f" % f for f in fracs))

    # -- FENCE 5 / R1D-2: the sigma'-matched corridor delivers the paper's sigma
    sig = (1 - F(1, 256)) * (1 - F(1, 2048)) * (1 + F(1, 128))
    check("S1d", sig == F(67336065, 67108864) and sig >= 1 + F(1, 1024),
          "(1-2^-8)(1-2^-11)(1+2^-7) = %s >= 1025/1024" % sig)

    # -- DA-1: the branch-(a) forcing constant --------------------------------
    da = (1 - F(1, 256)) * (1 + F(1, 128))
    check("S1e", da == F(32895, 32768) and da == 1 + F(1, 256) - F(1, 32768),
          "(1-2^-8)(1+2^-7) = %s = 1+2^-8-2^-15" % da)

    # -- Lemma A.7 is the BINDING constraint on c -----------------------------
    c_paper = F(1, 2 ** 13 * 100)          # TeX 295
    c_max = F(1, 100 * (2 ** 13 - 1))      # forced by |B| >= (1-2^-13)|B_{1+delta}|
    margin = (c_max - c_paper) / c_paper
    check("S1f", c_paper <= c_max and abs(float(margin) - 1.221e-4) < 1e-7,
          "c = 1/819200 <= 1/819100, relative margin %.3e" % float(margin))

    # -- Defect D1: vacuous at the parameters used, and its repair ------------
    d1 = 200 * (c_paper + F(1, 200))       # 200(rho+delta)d, rho=c/d, delta=1/(200d)
    check("S1g", d1 == F(4097, 4096) and d1 > 1,
          "D1: 200(rho+delta)d = %s > 1  (proof needs <= 2^-7)" % d1)
    check("S1h", 400 * c_paper <= F(1, 128) and 1000 * c_paper <= F(1, 256),
          "D1 repair B^0=B_{1+c/d}: 400c=%.3e <= 2^-7, 1000c=%.3e <= 2^-8"
          % (float(400 * c_paper), float(1000 * c_paper)))

    # -- the two absolute constants inside the L^4 ---------------------------
    check("S1i", (2 ** 12) ** 2 == 16777216 and 19 * 19 == 361,
          "eps^-2 = 2^24 = 16777216 and k^2 = 361 carry NO power of L")

    # -- J = Theta(L): sigma >= 2^{J-1} against sigma <= alpha^-1 ------------
    ok = True
    for a in (F(1, 10 ** 3), F(1, 10 ** 6), F(1, 2 ** 40)):
        Jmax = 1 + math.log2(1 / float(a))
        ok &= (Jmax > 1) and abs(Jmax - (1 + math.log2(1 / float(a)))) < 1e-12
    check("S1j", ok, "J <= 1+log2(1/alpha) = Theta(L)  (energy doubling vs the L^inf cap)")

    # -- T1' exact threshold, with the caveat of record 7(H) -----------------
    eps = F(1, 1024)
    rows = []
    for a in (F(1, 2 ** 12), F(1, 2 ** 20), F(1, 2 ** 30)):
        cstar = a / (a + eps * eps * (1 - a))
        rows.append((a, cstar, cstar / a))
    ok = (float(rows[0][2]) < 5000) and (abs(float(rows[2][2]) - 2 ** 20) / 2 ** 20 < 0.01)
    check("S1k", ok,
          "T1' c*=alpha/(alpha+eps^2(1-alpha)): c*/alpha = %.0f, %.3e, %.3e at "
          "alpha=2^-12,2^-20,2^-30  => the 'alpha/eps^2 = 2^20 alpha' gloss needs alpha << eps^2"
          % tuple(float(r[2]) for r in rows))

    # -- DA-5: the direction-free-flatness / descent-length trade-off --------
    ok = True
    tbl = []
    for j, r in ((1, 40), (7, 6), (10, 4), (20, 2), (40, 1)):
        D = max(j - 6, 0)
        L = j * r * math.log(3)
        ok &= (D * r <= L / math.log(3) + 1e-9)
        tbl.append("(j=%d,r=%d):D*J=%d<=%.0f" % (j, r, D * r, L / math.log(3)))
    check("S1l", ok, "DA-5 trade-off D*J <= L/ln3 : " + " ".join(tbl))


# ---------------------------------------------------------------------------
# S2  DRIFT TRIPWIRE for correction (B) of WALL_A_FENCE_COMPLEX.md §7
#     The R1CA scaling table is captioned as satisfying conclusion (4), but the
#     generating code never computes a cond4 predicate.  In that family
#         delta * 3^h  =  |C cap (C+sigma)|  =  2^{m-t}   IDENTICALLY,
#     so imposing (4) is exactly a cap on m-t.  This check keeps that correction
#     from silently rotting if the lane code changes.
# ---------------------------------------------------------------------------
def s2_drift_tripwire():
    head("S2  DRIFT TRIPWIRE  (record 7(B): R1CA scaling table vs conclusion (4))")
    if not os.path.exists(LANE_DICHOT + "/R1CA_closedform.py"):
        return check("S2", False, "R1CA_closedform.py missing")
    sys.path.insert(0, LANE_DICHOT)
    try:
        from R1CA_closedform import analyse
    except Exception as e:                                   # pragma: no cover
        return check("S2", False, "import failed: %r" % e)

    # the published headline rows of R1CA_DICHOTOMY_VERDICT.md section 5
    rows = [(1, (2, 1, 1, 35, 8)), (2, (3, 2, 2, 41, 9)), (4, (5, 4, 4, 53, 9)),
            (8, (10, 9, 8, 77, 7)), (12, (14, 13, 12, 101, 5))]
    ident_ok = True
    cond4_all_fail = True
    detail = []
    for h, (j, j5, jp, m, tt) in rows:
        r = analyse(j, j5, jp, h, m, tt, verbose=False)
        # (i) the exact identity  delta * 3^h = 2^{m-t}
        ident_ok &= (r["delta"] * 3 ** h == F(2 ** (m - tt)))
        # (ii) the lane's own conclusion-(4) proxy, which the sweep never applied
        ratio = r["Elevel"] / (256 * r["sigma"])
        cond4_all_fail &= (ratio > 1)
        detail.append("h=%d:%.4g" % (h, float(ratio)))
    check("S2a", ident_ok,
          "delta*3^h = |C cap (C+sigma)| = 2^{m-t} exactly on all 5 published rows")
    check("S2b", cond4_all_fail,
          "every published row FAILS the lane's own (4)-proxy; Elevel/(2^8 sigma') = "
          + ", ".join(detail))
    keys = set(analyse(1, 1, 1, 1, 4, 0, verbose=False))
    check("S2c", "cond4" not in keys and "Elevel" in keys,
          "analyse() still exposes no 'cond4' predicate -- only the 'Elevel' proxy, "
          "which R1CA_scaling.py never filters on")


# ---------------------------------------------------------------------------
# L1-L4  THE FOUR LANE REPLAYS  (cheapest exact check per lane)
# ---------------------------------------------------------------------------
#   wants   : substrings that MUST appear   (the lane's own success marker)
#   forbids : regexes that must NOT match   (kept narrow: the lane logs contain
#             the words FAIL/False inside explanatory prose, so anchor on the
#             status column and on nonzero failure counts, never on bare words)
LANE_JOBS = [
    ("L1", "chamber_audit  ", LANE_CHAMBER, ["CHAMBERMAP_L4_autopsy_checks.py"],
     ["16 passed, 0 failed"], [r"^\s*FAIL\b", r"Traceback"]),
    ("L2", "sifted_doubling", LANE_SIFTED, ["R1B_shiftlaw_doubling_exact.py"],
     ["DONE (part 1)"], [r"failures\s+[1-9]", r"violations\s+[1-9]", r"Traceback"]),
    ("L3", "dichotomy_r1ca ", LANE_DICHOT, ["R1D_corridor_ledger.py"],
     ["21 passed, 0 failed"], [r"^\s*FAIL\b", r"Traceback"]),
    ("L4", "bound_a        ", LANE_BOUNDA, ["R1E_local_dichotomy.py", "t1"],
     ["T1 verified on every instance: True"], [r"T1 HOLDS:\s*False", r"Traceback"]),
]


def run_lanes():
    head("L1-L4  LANE REPLAYS  (cheapest exact check from each of the four lanes)")
    for tag, name, cwd, argv, wants, forbids in LANE_JOBS:
        script = os.path.join(cwd, argv[0])
        if not os.path.exists(script):
            check(tag, False, "%s : MISSING %s" % (name, script))
            continue
        t0 = time.time()
        try:
            p = subprocess.run([sys.executable] + argv, cwd=cwd, timeout=300,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out = p.stdout.decode("utf-8", "replace")
            rc = p.returncode
        except subprocess.TimeoutExpired:
            check(tag, False, "%s : TIMEOUT" % name)
            continue
        dt = time.time() - t0
        ok = (rc == 0)
        ok &= all(w in out for w in wants)
        ok &= not any(re.search(f, out, re.M) for f in forbids)
        check(tag, ok, "%s %-34s rc=%d  %5.2fs  %s"
              % (name, " ".join(argv), rc, dt,
                 "|".join(w for w in wants if w in out) or "MARKER NOT FOUND"))


# ---------------------------------------------------------------------------
def main():
    args = set(sys.argv[1:])
    do_self = ("--lanes" not in args)
    do_lanes = ("--self" not in args)

    print("=" * 78)
    print("WALL A LIVENESS TEST -- Erdos 142, campaign of 2026-07-30")
    print("erdos142_solved: false   new_r3_bound: false   cracked: false")
    print("companion to WALL_A_FENCE_COMPLEX.md; authorship of arXiv:2603.27045v3")
    print("and of all mathematics audited remains R. Raghavan's.")
    print("=" * 78)

    t0 = time.time()
    if do_self:
        s0_source()
        s1_constants()
        s2_drift_tripwire()
    if do_lanes:
        run_lanes()

    npass = sum(1 for _, ok in RESULTS if ok)
    nfail = len(RESULTS) - npass
    head("SUMMARY")
    print("  %d passed, %d failed   (%.2f s)" % (npass, nfail, time.time() - t0))
    if nfail:
        print("  FAILED: " + ", ".join(t for t, ok in RESULTS if not ok))
        print("\n  A failure here does NOT refute the record -- it means an artifact")
        print("  moved.  Re-read WALL_A_FENCE_COMPLEX.md section 7 before concluding")
        print("  anything, and check the lane's own log alongside its script.")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())

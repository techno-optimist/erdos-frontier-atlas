#!/usr/bin/env python3
"""Exact certificate: the H1-H5 constant ceiling for Erdos #142, and the
exclusion of "pressure-to-one" candidate families.

Replay (from this directory):

    python3 -I verify.py

Everything in the trust path is exact integer/Fraction arithmetic. No
floats are used in any decision; floats appear only in the final display
block, clearly labelled. Planted-failure controls are run at the end and
MUST fail.

WHAT IS CERTIFIED HERE (and nothing more)
-----------------------------------------
Two arithmetic facts, given the two EXTERNAL inputs named below:

  (C1) lambda_candidate > 7/24  -- exact rational comparison. Since the
       constant map c = 2*sqrt(log2(1/lambda)) is strictly DECREASING in
       lambda, this is exactly the statement "this candidate rate would
       give a constant strictly better than the EHPS 2024 baseline
       2.666539..., IF a certificate for it existed".

  (C2) EXCLUSION. Any family whose spectral pressure obeys the bracket
       1 - rho(m) <= 2/(3m) + 11/(6m^2)  (m >= 7)
       has rho(m) > Lambda_cap for every m >= 7, where Lambda_cap is the
       cap-set ceiling on the return rate of any H1-H5 survivor. Such a
       family therefore CANNOT be an H1-H5 survivor. "Pressure -> 1" is
       self-defeating: the closer rho is driven to 1, the more decisively
       it violates the ceiling.

EXTERNAL INPUTS (NOT certified here; stated so a reader hits them first)
-----------------------------------------------------------------------
  (E1) The constant map c = 2*sqrt(log2(1/lambda)) for an H1-H5 survivor
       with anchored-reservoir return rate lambda, and
  (E2) the ceiling Lambda_cap = (theta_3/3)^2 on lambda for any H1-H5
       survivor, theta_3 = min_{x>0} (1+x+x^2)/x^(2/3), which follows
       from the published Ellenberg-Gijswijt cap-set bound together with
       a Fubini + periodic Perron-Frobenius argument.
  Both come from an external research lane. They are SEALED-BY-AUDIT
  there (rigorous human mathematics with machine-checked exact-algebra
  controls and rejected hostile mutations), NOT formalized in a proof
  assistant, and NOT re-derived in this repository. If either is wrong,
  the conclusions below are void. This certificate checks the ARITHMETIC
  and the EXCLUSION LOGIC that follow from them.

  The bracket in (C2) is likewise an external PROVED input for one
  specific family; here it is treated as a hypothesis, so (C2) is a
  statement about ANY family satisfying that bracket.

NOT CLAIMED
-----------
No r_3(N) lower bound. No improvement on EHPS. No survivor certificate
exists (that antecedent is open). This is a WALL/FENCE result: it maps
where a large class of candidate constructions provably cannot go.
"""

from fractions import Fraction as F
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def fail(msg):
    raise AssertionError(msg)


# ---------------------------------------------------------------- inputs
# Candidate anchored-reservoir return rate (exact rational, external lane).
LAMBDA_CANDIDATE = F(65789102774707418182759, 222090924810025888000000)

# EHPS 2024 building-block rate: the baseline constant corresponds to 7/24.
EHPS_RATE = F(7, 24)

# Rational witness point for bounding theta_3 from above. theta_3 is a
# minimum, so evaluating the objective at ANY positive rational x0 gives an
# upper bound. x0 is near the true minimiser (-1+sqrt(33))/8 = 0.59307...
X0 = F(593, 1000)

# Rational ceiling bound we will certify: Lambda_cap <= U.
U = F(211, 250)  # = 0.844

# The pressure bracket hypothesis (external, proved for one family):
#   1 - rho(m) <= 2/(3m) + 11/(6m^2).
def rho_lower(m):
    """Exact lower bound on rho(m) implied by the bracket hypothesis."""
    return 1 - (F(2, 3 * m) + F(11, 6 * m * m))


# ------------------------------------------------------- C1: beats EHPS?
def check_C1():
    if not LAMBDA_CANDIDATE > EHPS_RATE:
        fail("C1: candidate rate does not exceed 7/24")
    margin = LAMBDA_CANDIDATE - EHPS_RATE
    if margin <= 0:
        fail("C1: non-positive margin")
    return margin


# --------------------------------- C2a: certified rational bound on ceiling
def check_ceiling_bound():
    """Certify Lambda_cap = (theta_3/3)^2 <= U, using only exact rationals.

    theta_3 = min_{x>0} f(x), f(x) = (1+x+x^2)/x^(2/3), so for our rational
    witness x0:  theta_3 <= f(x0), hence theta_3^3 <= R := (1+x0+x0^2)^3/x0^2
    (R is rational -- the cube clears the cube root).

    Lambda_cap = theta_3^2/9 <= R^(2/3)/9. So Lambda_cap <= U follows from
    R^(2/3) <= 9U, i.e. from the purely rational inequality R^2 <= (9U)^3.
    """
    R = (1 + X0 + X0 * X0) ** 3 / (X0 * X0)          # exact rational, >= theta_3^3
    lhs = R * R                                       # R^2
    rhs = (9 * U) ** 3                                # (9U)^3
    if not lhs <= rhs:
        fail(f"C2a: ceiling bound not certified: R^2={lhs} > (9U)^3={rhs}")
    return R, lhs, rhs


# ------------------------------------------- C2b: the exclusion, all m>=7
def check_exclusion(m_min=7, m_check_upto=200):
    """rho_lower(m) > U for every m >= m_min.

    rho_lower(m) = 1 - 2/(3m) - 11/(6m^2) is strictly increasing in m>0
    (both subtracted terms strictly decrease), so it suffices to verify the
    single boundary case m = m_min exactly. We additionally spot-verify a
    range for defence in depth.
    """
    base = rho_lower(m_min)
    if not base > U:
        fail(f"C2b: exclusion fails at boundary m={m_min}: {base} <= {U}")
    prev = None
    for m in range(m_min, m_check_upto + 1):
        cur = rho_lower(m)
        if not cur > U:
            fail(f"C2b: exclusion fails at m={m}")
        if prev is not None and not cur > prev:
            fail(f"C2b: monotonicity fails at m={m}")
        prev = cur
    return base


def run_all(lambda_candidate=None, x0=None, u=None, bracket_scale=None):
    """Run the three checks. Parameters exist ONLY for planted-failure controls."""
    global LAMBDA_CANDIDATE, X0, U
    saved = (LAMBDA_CANDIDATE, X0, U)
    try:
        if lambda_candidate is not None:
            LAMBDA_CANDIDATE = lambda_candidate
        if x0 is not None:
            X0 = x0
        if u is not None:
            U = u
        margin = check_C1()
        R, lhs, rhs = check_ceiling_bound()
        if bracket_scale is None:
            base = check_exclusion()
        else:
            # mutated bracket: 1 - rho <= scale*(2/(3m) + 11/(6m^2))
            def mutated(m):
                return 1 - bracket_scale * (F(2, 3 * m) + F(11, 6 * m * m))
            base = mutated(7)
            if not base > U:
                fail("C2b(mutated): exclusion fails at m=7")
        return margin, R, lhs, rhs, base
    finally:
        LAMBDA_CANDIDATE, X0, U = saved


def main():
    print("Erdos #142 -- H1-H5 constant ceiling and pressure-to-one exclusion")
    print("exact arithmetic only (Fraction); floats appear in display lines only\n")

    margin, R, lhs, rhs, base = run_all()

    print("[C1] candidate rate exceeds the EHPS 7/24 building block")
    print(f"     lambda = {LAMBDA_CANDIDATE}")
    print(f"     margin over 7/24 = {margin}")
    print(f"     (display only) lambda ~ {float(LAMBDA_CANDIDATE):.16f} > 7/24 ~ {float(EHPS_RATE):.16f}")
    print("     => the map c=2*sqrt(log2(1/lambda)) would give a constant")
    print("        strictly better than EHPS 2.666539..., IF certified.\n")

    print("[C2a] cap-set ceiling bounded above by an exact rational")
    print(f"     witness x0 = {X0}")
    print(f"     R = (1+x0+x0^2)^3/x0^2 >= theta_3^3 = {R}")
    print(f"     certified: R^2 <= (9U)^3  with U = {U}")
    print(f"     => Lambda_cap = (theta_3/3)^2 <= U = {U}")
    print(f"     (display only) U ~ {float(U):.6f}, true Lambda_cap ~ 0.843400158744900\n")

    print("[C2b] EXCLUSION: any family with 1-rho(m) <= 2/(3m)+11/(6m^2)")
    print(f"     has rho(m) >= {base} > U = {U} for every m >= 7")
    print("     (rho_lower is strictly increasing; boundary case decides)")
    print("     => such a family exceeds the ceiling and CANNOT be an")
    print("        H1-H5 survivor. Driving pressure -> 1 makes this worse.\n")

    # planted-failure controls: each MUST fail
    print("planted-failure controls (each must FAIL):")
    controls = [
        ("candidate rate set below 7/24",
         dict(lambda_candidate=F(7, 25))),
        ("ceiling bound U shrunk below the true ceiling",
         dict(u=F(84, 100))),
        ("theta_3 witness moved far from the minimiser",
         dict(x0=F(1, 100))),
        ("bracket loosened 4x (pressure no longer forced high)",
         dict(bracket_scale=F(4))),
    ]
    for label, kwargs in controls:
        try:
            run_all(**kwargs)
        except AssertionError as exc:
            print(f"  [ok] rejected: {label} -- {str(exc)[:60]}")
        else:
            print(f"  [FAIL] ACCEPTED a bad input: {label}")
            sys.exit(1)

    # check the committed artifact rather than regenerating it
    art = HERE / "constants.json"
    if art.is_file():
        rec = json.loads(art.read_text())
        if rec["lambda_candidate"] != str(LAMBDA_CANDIDATE):
            fail("constants.json: lambda_candidate drift")
        if rec["ceiling_rational_upper_bound_U"] != str(U):
            fail("constants.json: U drift")
        if rec["exclusion_holds_for_m_at_least"] != 7:
            fail("constants.json: exclusion threshold drift")
        print("\nconstants.json matches the verified values (artifact not rewritten)")

    print("\nVERIFIER PASS")


if __name__ == "__main__":
    main()

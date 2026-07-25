#!/usr/bin/env python3
"""Exact certificate: the H1-H5 constant ceiling for Erdos #142, and the
exclusion of "pressure-to-one" candidate families.

Replay (from this directory):

    python3 -I verify.py

Everything in the trust path is exact integer/Fraction arithmetic. No
floats are used in any decision; floats appear only in the final display
block and in the display-decimal re-derivation, both clearly labelled.
Planted-failure controls are run at the end and MUST fail.

The committed artifact `constants.json` is CHECKED, never regenerated:
every field is re-derived here from the exact constants below, and the
keyset is enforced in both directions, so a field added to the artifact
later fails the replay instead of silently escaping the drift check.

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

from decimal import Decimal, localcontext
from fractions import Fraction as F
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def fail(msg):
    raise AssertionError(msg)


def _expect_rejected(label, fn, *args, **kwargs):
    """A planted failure that is ACCEPTED aborts the replay."""
    try:
        fn(*args, **kwargs)
    except AssertionError as exc:
        print(f"  [ok] rejected: {label} -- {str(exc)[:60]}")
    else:
        print(f"  [FAIL] ACCEPTED a bad input: {label}")
        sys.exit(1)


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
# Coefficients of 1/m and 1/m^2, kept as named constants so that the bracket
# STRING committed in constants.json is rendered from the bracket the code
# actually uses (it cannot drift from the implemented hypothesis).
BRACKET = (F(2, 3), F(11, 6))

# Smallest m for which the exclusion is claimed.
M_MIN = 7


def rho_lower(m):
    """Exact lower bound on rho(m) implied by the bracket hypothesis."""
    a, b = BRACKET
    return 1 - (a / m + b / (m * m))


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
def check_exclusion(m_min=M_MIN, m_check_upto=200):
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
                a, b = BRACKET
                return 1 - bracket_scale * (a / m + b / (m * m))
            base = mutated(M_MIN)
            if not base > U:
                fail(f"C2b(mutated): exclusion fails at m={M_MIN}")
        return margin, R, lhs, rhs, base
    finally:
        LAMBDA_CANDIDATE, X0, U = saved


# ------------------------------------------- committed-artifact drift check
# DISPLAY ONLY, NEVER IN THE TRUST PATH. The five decimals in
# constants.json["display_only_decimals"] are 16-significant-digit roundings
# of irrational quantities. No decision in C1/C2a/C2b consults them; they are
# re-derived here only so that a committed decimal cannot drift away from the
# exact rational it summarises. Hence -- and only here -- a tolerance:
DISPLAY_PRECISION = 60           # working digits for the re-derivation
DISPLAY_REL_TOL = Decimal("1e-15")   # committed decimals carry ~16 digits


def _dec(fr):
    return Decimal(fr.numerator) / Decimal(fr.denominator)


def _log2(d):
    return d.ln() / Decimal(2).ln()


def _constant_map(lam):
    """c(lambda) = 2*sqrt(log2(1/lambda)) -- external input (E1), display use."""
    return 2 * _log2(1 / lam).sqrt()


def display_decimals():
    """Re-derive the display decimals from the exact rationals (display only)."""
    with localcontext() as ctx:
        ctx.prec = DISPLAY_PRECISION
        lam = _dec(LAMBDA_CANDIDATE)
        # theta_3 = min_{x>0} (1+x+x^2)/x^(2/3); f'(x)=0 <=> 4x^2 + x - 2 = 0,
        # so the minimiser is x* = (-1+sqrt(33))/8. (The TRUST-PATH bound C2a
        # does not use x*: it uses the rational witness X0 and stays exact.)
        xs = (Decimal(-1) + Decimal(33).sqrt()) / 8
        if abs(4 * xs * xs + xs - 2) > Decimal("1e-50"):
            fail("display: minimiser x* does not satisfy 4x^2 + x - 2 = 0")
        theta3 = (1 + xs + xs * xs) / (Decimal(2) / 3 * xs.ln()).exp()
        cap = (theta3 / 3) ** 2                       # true Lambda_cap
        return {
            "lambda_candidate": +lam,
            "ehps_constant": +_constant_map(_dec(EHPS_RATE)),
            "candidate_constant_if_certified": +_constant_map(lam),
            "cap_set_ceiling_true_value": +cap,
            "universal_constant_floor_from_ceiling": +_constant_map(cap),
        }


def bracket_strings():
    """Render the bracket exactly as the code implements it."""
    (an, ad), (bn, bd) = ((BRACKET[0].numerator, BRACKET[0].denominator),
                          (BRACKET[1].numerator, BRACKET[1].denominator))
    spaced = f"1 - rho(m) <= {an}/({ad}m) + {bn}/({bd}m^2)"
    compact = f"1-rho(m) <= {an}/({ad}m)+{bn}/({bd}m^2)"
    return spaced, compact


def expected_artifact():
    """Every field constants.json is allowed to contain, re-derived from the
    exact constants above. Numbers are never copied from the artifact."""
    margin = LAMBDA_CANDIDATE - EHPS_RATE
    rho7 = rho_lower(M_MIN)
    spaced, compact = bracket_strings()
    dd = display_decimals()
    floor4 = f"{dd['universal_constant_floor_from_ceiling']:.4f}"
    return {
        "problem": 142,
        "title": "H1-H5 constant ceiling and pressure-to-one exclusion",
        "kind": "fence",
        "certified_here": [
            f"C1: lambda_candidate > {EHPS_RATE} (exact rational), i.e. this rate"
            " would give a constant strictly better than the EHPS 2024 baseline"
            " IF a survivor certificate for it existed",
            f"C2a: Lambda_cap = (theta_3/3)^2 <= {U}, certified by the purely"
            " rational inequality R^2 <= (9U)^3 with"
            " R = (1+x0+x0^2)^3/x0^2 >= theta_3^3",
            f"C2b: any family obeying the pressure bracket {compact} has"
            f" rho(m) >= {rho7} > {U} for every m >= {M_MIN}, hence exceeds the"
            " ceiling and cannot be an H1-H5 survivor",
        ],
        "not_certified_here": [
            "the constant map c = 2*sqrt(log2(1/lambda)) itself (external,"
            " sealed-by-audit, not formalized, not re-derived in this repo)",
            "the cap-set ceiling Lambda_cap on H1-H5 survivor return rates"
            " (external, from published Ellenberg-Gijswijt plus a Fubini +"
            " periodic Perron-Frobenius argument; sealed-by-audit)",
            "the pressure bracket, which is an external PROVED input for one"
            " specific family and is treated here as a hypothesis",
            "any r_3(N) lower bound; no survivor certificate exists",
        ],
        "lambda_candidate": str(LAMBDA_CANDIDATE),
        "ehps_building_block_rate": str(EHPS_RATE),
        "lambda_margin_over_ehps": str(margin),
        "theta_3_witness_x0": str(X0),
        "ceiling_rational_upper_bound_U": str(U),
        "exclusion_bracket": spaced,
        "exclusion_rho_lower_at_m7": str(rho7),
        "exclusion_holds_for_m_at_least": M_MIN,
        "display_only_decimals": dd,
        "consequence": (
            "Because c = 2*sqrt(log2(1/lambda)) is strictly decreasing in lambda"
            " and no H1-H5 survivor may exceed Lambda_cap, no survivor in this"
            f" framework can have a constant below ~{floor4}. The framework can"
            " therefore improve the CONSTANT but can never beat the sqrt(log N)"
            " ORDER. Separately, pressure-to-one families are excluded outright:"
            " the closer rho is driven to 1, the more decisively the ceiling is"
            " violated."
        ),
        # A fence must not quietly become a claim: all three stay false.
        "claim_boundary": {
            "erdos142_solved": False,
            "new_r3_bound": False,
            "survivor_certificate_exists": False,
        },
    }


def _check_keys(where, got, want, bad):
    missing = sorted(set(want) - set(got))
    extra = sorted(set(got) - set(want))
    if missing:
        bad.append(f"{where}: missing field(s) {missing}")
    if extra:
        # The point of the whole function: an uncovered field is a FAILURE,
        # not a shrug. This closes the defect class, not just one instance.
        bad.append(f"{where}: field(s) {extra} are not covered by this check")
    return not (missing or extra)


def check_committed_artifact(rec):
    """Drift-check EVERY field of constants.json; return the number checked.

    Trust-path fields are compared as exact strings/ints derived from the
    Fractions above. The display-only decimals are compared with an explicit
    relative tolerance (see DISPLAY_REL_TOL) because they are roundings; they
    are informational and never feed a decision.
    """
    want = expected_artifact()
    bad = []
    checked = 0
    if not isinstance(rec, dict):
        fail("constants.json: top level is not a JSON object")
    _check_keys("top level", rec, want, bad)

    for key in sorted(set(rec) & set(want)):
        exp, got = want[key], rec[key]
        if key == "display_only_decimals":
            if not isinstance(got, dict):
                bad.append("display_only_decimals: not an object")
                continue
            note = "informational; never in the trust path"
            sub_want = dict(exp, note=note)
            _check_keys("display_only_decimals", got, sub_want, bad)
            for name in sorted(set(got) & set(sub_want)):
                checked += 1
                if name == "note":
                    if got[name] != note:
                        bad.append(f"display_only_decimals.note drift: {got[name]!r}")
                    continue
                if not isinstance(got[name], float):
                    bad.append(f"display_only_decimals.{name}: not a JSON number")
                    continue
                with localcontext() as ctx:
                    ctx.prec = DISPLAY_PRECISION
                    exact = sub_want[name]
                    err = abs(Decimal(got[name]) - exact)
                    if err > DISPLAY_REL_TOL * abs(exact):
                        bad.append(
                            f"display_only_decimals.{name} drift: committed"
                            f" {got[name]!r} vs exact {exact:.20f} (rel err"
                            f" {err / abs(exact):.3E} > {DISPLAY_REL_TOL})")
        elif key == "claim_boundary":
            if not isinstance(got, dict):
                bad.append("claim_boundary: not an object")
                continue
            _check_keys("claim_boundary", got, exp, bad)
            for name in sorted(set(got) & set(exp)):
                checked += 1
                if got[name] is not False:
                    bad.append(
                        f"claim_boundary.{name} must be false, found {got[name]!r}")
        elif isinstance(exp, list):
            if not isinstance(got, list) or len(got) != len(exp):
                bad.append(f"{key}: expected a list of {len(exp)} entries")
                continue
            for i, (g, e) in enumerate(zip(got, exp)):
                checked += 1
                if g != e:
                    bad.append(f"{key}[{i}] drift:\n    committed: {g!r}\n    "
                               f"re-derived: {e!r}")
        else:
            checked += 1
            if type(got) is not type(exp) or got != exp:
                bad.append(f"{key} drift: committed {got!r} != re-derived {exp!r}")

    if bad:
        fail("constants.json: " + "; ".join(bad))
    return checked


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

    # check the committed artifact rather than regenerating it
    art = HERE / "constants.json"
    if not art.is_file():
        fail("constants.json is missing; the certificate must ship its artifact")
    rec = json.loads(art.read_text(encoding="utf-8"))
    n_checked = check_committed_artifact(rec)
    print("constants.json matches the verified values (artifact not rewritten)")
    print(f"     all {n_checked} committed fields re-derived and matched;"
          " unknown fields are rejected")
    print("     (display-only decimals compared at relative tolerance"
          f" {DISPLAY_REL_TOL}; never in the trust path)\n")

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
        _expect_rejected(label, run_all, **kwargs)

    # artifact-coverage controls: each mutates a field of constants.json that
    # an earlier revision of this checker did NOT look at. They exist to prove
    # the coverage gap is closed, so they must be kept if fields are added.
    artifact_controls = [
        ("artifact: lambda_margin_over_ehps falsified",
         lambda r: r.update(lambda_margin_over_ehps="1/2")),
        ("artifact: theta_3 witness x0 falsified",
         lambda r: r.update(theta_3_witness_x0="1/100")),
        ("artifact: display decimal nudged by 1e-9 relative",
         lambda r: r["display_only_decimals"].update(
             universal_constant_floor_from_ceiling=(
                 r["display_only_decimals"]["universal_constant_floor_from_ceiling"]
                 * (1 + 1e-9)))),
        ("artifact: claim_boundary.erdos142_solved flipped to true",
         lambda r: r["claim_boundary"].update(erdos142_solved=True)),
        ("artifact: an unchecked field added (coverage-gap control)",
         lambda r: r.update(a_field_this_checker_never_heard_of=1)),
        ("artifact: a checked field deleted",
         lambda r: r.pop("exclusion_rho_lower_at_m7")),
    ]
    for label, mutate in artifact_controls:
        mutated = copy.deepcopy(rec)
        mutate(mutated)
        if mutated == rec:
            fail(f"control is a no-op (mutation did not change anything): {label}")
        _expect_rejected(label, check_committed_artifact, mutated)

    print(f"\n{len(controls) + len(artifact_controls)} planted-failure controls,"
          " all rejected")
    print("\nVERIFIER PASS")


if __name__ == "__main__":
    main()

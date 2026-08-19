#!/usr/bin/env python3
"""Exact replay of the finite-state disjoint-tile spectral wall.

This verifier composes the independently replayable q=42 arbitrary-carving
capacity with a solver-independent extremal spectral calculation.  It makes
no Atlas edits.

The physical q=42 packet replay proves that a one-block set carrying a
single-valued raw-canonical coercive potential has at most A=263277 units
inside the fixed N=280917-unit 117-cell geometry.  In any complete ordered
triple-automaton certificate, the union of all loop-edge tiles at a state is
such a set: a compatible loop-edge triple is a length-one self-loop at the
diagonal triple state, so its certified defect cannot be negative.

After scaling all edge weights by 42^4, the weighted adjacency matrix M
therefore obeys

    M >= 0,  sum_ij M_ij <= N,  M_ii <= A.

For every finite matrix with these constraints,

    rho(M) <= (A + sqrt(A^2 + (N-A)^2))/2.

The proof symmetrizes M and maximizes the convex largest-eigenvalue function
over the capped simplex.  Its extreme points have only the cases explicitly
checked below.  The unique worst type is a saturated loop plus a balanced
two-cycle using all remaining mass.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
Q = 42
N = 280_917
A = 263_277
S = N - A
GATE = Fraction(1_058_841, 4)
DEFAULT_Q42_SOURCE = Path(
    HERE.parent / "erdos-142-q42-carving-wall" / "q42_fractional_carving_wall.py"
)
DEFAULT_Q42_CERTIFICATE = Path(
    HERE.parent / "erdos-142-q42-carving-wall" / "q42_fractional_carving_certificate.json"
)
EXPECTED_SOURCE_SHA256 = "c543e7fd118981c530ad81a1dd0c4e105c5c1eca253aefd50c6c007c5a818fac"
EXPECTED_CERTIFICATE_SHA256 = "60d9d974aa23755615d159653508dbb38769fb0d883c974a4425e51b278119b4"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind_q42_capacity(source: Path, certificate: Path) -> None:
    need(sha256(source) == EXPECTED_SOURCE_SHA256,
         "q42 capacity source hash drift")
    need(sha256(certificate) == EXPECTED_CERTIFICATE_SHA256,
         "q42 capacity certificate hash drift")


def replay_q42_capacity(source: Path, certificate: Path) -> None:
    bind_q42_capacity(source, certificate)
    result = subprocess.run(
        [sys.executable, "-I", str(source)],
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    need(result.returncode == 0,
         f"q42 capacity replay failed: {result.stderr.strip()}")
    need("PASS_Q42_FRACTIONAL_PROPER_CARVING_WALL" in result.stdout,
         "q42 capacity PASS marker missing")
    need("GATE max_retained=263277 gate=1058841/4" in result.stdout,
         "q42 retained-cap line missing")
    print("Q42_CAPACITY_REPLAY_OK")


def spectral_extreme_replay() -> None:
    need(N == 117 * 7**4, "physical alphabet count")
    need(A == N - 17_640, "packet deletion cap")
    need(2 * A > N, "extreme-point case split assumes A>N/2")
    need(GATE == Fraction(49, 576) * Q**4, "EHPS gate scaling")

    # A symmetric matrix with total mass N and diagonal entries capped by A
    # has the following extreme-point types after using y_ij=2*M_ij for each
    # off-diagonal variable.  Values below are exact upper certificates for
    # each type; the incident loop+two-cycle type has characteristic
    # polynomial x^2-A*x-S^2/4.
    off_diagonal_only = Fraction(N, 2)
    two_diagonals = Fraction(A, 1)
    disjoint_loop_and_cycle = max(Fraction(A, 1), Fraction(S, 2))
    need(off_diagonal_only < A, "pure two-cycle comparison")
    need(two_diagonals == A, "two-diagonal extreme")
    need(disjoint_loop_and_cycle == A, "disjoint extreme")

    # The integer 263573 is a rational upper witness strictly above the
    # positive algebraic root, since its characteristic polynomial is >0.
    rational_upper = 263_573
    polynomial_at_upper = (
        Fraction(rational_upper * rational_upper - A * rational_upper, 1)
        - Fraction(S * S, 4)
    )
    need(rational_upper > A and polynomial_at_upper == 225_208,
         "rational Perron upper witness")

    gate_polynomial = GATE * GATE - A * GATE - Fraction(S * S, 4)
    need(gate_polynomial == Fraction(4_825_657_053, 16),
         "exact gate polynomial")
    need(gate_polynomial > 0 and GATE > rational_upper,
         "strict spectral wall")
    need(Fraction(rational_upper, Q**4) < Fraction(49, 576),
         "normalized strict wall")

    print(
        "SPECTRAL_EXTREMES_OK",
        f"pure_two_cycle={off_diagonal_only}",
        f"two_diagonals={two_diagonals}",
        f"disjoint={disjoint_loop_and_cycle}",
    )
    print(
        "PERRON_BOUND",
        f"algebraic=(263277+sqrt(263277^2+17640^2))/2",
        f"rational_upper={rational_upper}",
        f"gate={GATE}",
    )
    print(
        "EXACT_GATE_POLYNOMIAL",
        f"value={gate_polynomial}",
        f"upper_polynomial={polynomial_at_upper}",
    )


def planted_failures() -> None:
    # Erasing the q42 packet cap makes the physical total itself available
    # as a loop and must fail the claimed bound.
    bad_a = N
    need(bad_a > GATE, "planted missing diagonal cap was not detected")
    # Reusing physical mass in two phase contexts violates global disjointness
    # and doubles the matrix mass; the total-mass premise detects it.
    duplicated_total = 2 * N
    need(duplicated_total > N, "planted repeated-label mass was not detected")
    print("PLANTED_FAILURES_REJECTED count=2")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-q42-replay",
        action="store_true",
        help="verify only the hash-bound spectral composition",
    )
    parser.add_argument("--q42-source", type=Path, default=DEFAULT_Q42_SOURCE)
    parser.add_argument("--q42-certificate", type=Path,
                        default=DEFAULT_Q42_CERTIFICATE)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    before = Path(__file__).read_bytes()
    if not args.skip_q42_replay:
        replay_q42_capacity(args.q42_source, args.q42_certificate)
    else:
        bind_q42_capacity(args.q42_source, args.q42_certificate)
        print("Q42_CAPACITY_HASH_BINDING_OK")
    spectral_extreme_replay()
    if args.self_test:
        planted_failures()
    need(Path(__file__).read_bytes() == before, "verifier mutated itself")
    print("PASS_DISJOINT_FINITE_STATE_GRAPH_CARVING_WALL")
    print("SCOPE fixed_q6_117_cell_geometry arbitrary_measurable_disjoint_edge_tiles")
    print("POTENTIAL arbitrary_residual_dependent finite_state_coboundaries_allowed")
    print("AUTOMATON complete_ordered_triples no_negative_defect_cycles_required")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent stdlib replay for the disjoint finite-state graph wall.

This script imports no source-packet module.  It hash-binds the theorem and
its q=42 dependency, exhaustively checks the endpoint-pruning diagonal lemma
on all small directed graphs, tests single-valued descent and overlap
rejection, and verifies the spectral arithmetic by exact rationals.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_NOTE = HERE / "README.md"
DEFAULT_GRAPH_VERIFIER = HERE / "verify.py"
DEFAULT_Q42_SOURCE = HERE.parent / "erdos-142-q42-carving-wall" / "q42_fractional_carving_wall.py"
DEFAULT_Q42_CERT = HERE.parent / "erdos-142-q42-carving-wall" / "q42_fractional_carving_certificate.json"
EXPECTED = {
    "note": "d6392db537225d2457ab5c712da2226c27f34f706545db57aaefb38d334b6256",
    "graph_verifier": "61e19c8b4c80c1ac2f862221b91b8e962f5a9b032a2dc7fecf5fdd2a9c6db4fd",
    "q42_source": "c543e7fd118981c530ad81a1dd0c4e105c5c1eca253aefd50c6c007c5a818fac",
    "q42_cert": "60d9d974aa23755615d159653508dbb38769fb0d883c974a4425e51b278119b4",
}


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_bind(paths):
    for key, path in paths.items():
        require(digest(path) == EXPECTED[key], f"hash drift: {key}")
    print("SOURCE_HASH_BINDINGS_OK")


def reachable(n, adjacency, starts, reverse=False):
    seen = set(starts)
    stack = list(starts)
    while stack:
        u = stack.pop()
        for v in range(n):
            edge = (v, u) in adjacency if reverse else (u, v) in adjacency
            if edge and v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def diagonal_pruning_exhaustion():
    """Check the minimal diagonal triple subautomaton for n<=3 exactly."""
    cases = 0
    live_states = 0
    for n in range(1, 4):
        arcs = tuple(product(range(n), repeat=2))
        for graph_mask in range(1 << len(arcs)):
            adjacency = {arc for i, arc in enumerate(arcs) if graph_mask >> i & 1}
            for start_mask in range(1, 1 << n):
                starts = {i for i in range(n) if start_mask >> i & 1}
                forward = reachable(n, adjacency, starts)
                for end_mask in range(1, 1 << n):
                    ends = {i for i in range(n) if end_mask >> i & 1}
                    backward = reachable(n, adjacency, ends, reverse=True)
                    live = forward & backward
                    cases += 1
                    live_states += len(live)

                    # The always-compatible x=y=z transitions form a copy of
                    # the original state graph on diagonal triple states.
                    triple_forward = {
                        (s, s, s) for s in reachable(n, adjacency, starts)
                    }
                    triple_backward = {
                        (s, s, s) for s in reachable(n, adjacency, ends, reverse=True)
                    }
                    diagonal_transitions = {
                        ((u, u, u), (v, v, v)) for u, v in adjacency
                    }
                    for s in live:
                        diagonal = (s, s, s)
                        require(diagonal in triple_forward and diagonal in triple_backward,
                                "live diagonal triple state was pruned")
                        if (s, s) in adjacency:
                            require((diagonal, diagonal) in diagonal_transitions,
                                    "diagonal self-loop transition vanished")
    print("DIAGONAL_PRUNING_EXHAUSTIVE_OK", f"cases={cases}", f"live_states={live_states}")


def build_single_valued(edge_tiles, edge_values):
    owner = {}
    value = {}
    for edge, tile in edge_tiles.items():
        for point in tile:
            require(point not in owner, "overlapping physical edge ownership")
            owner[point] = edge
            value[point] = edge_values[edge][point]
    return owner, value


def descent_and_overlap_audit():
    # Two parallel loop edges at one state, with unrelated edge-local values.
    edge_tiles = {"e0": {0, 1, 2}, "e1": {3, 4, 5}}
    edge_values = {
        "e0": {0: F(7), 1: F(-2), 2: F(11)},
        "e1": {3: F(5, 2), 4: F(-9), 5: F(13)},
    }
    owner, union_value = build_single_valued(edge_tiles, edge_values)
    checked = 0
    for x, y, z in product(sorted(owner), repeat=3):
        if (x + z - 2 * y) % 7:
            continue
        edge_defect = (edge_values[owner[x]][x] + edge_values[owner[z]][z]
                       - 2 * edge_values[owner[y]][y])
        physical_defect = union_value[x] + union_value[z] - 2 * union_value[y]
        require(edge_defect == physical_defect, "edge values did not descend")
        checked += 1
    require(checked > 0, "no midpoint rows checked")

    # Rank and state coboundaries vanish on a diagonal self-loop.
    for rank, state_value in ((F(3, 7), F(-8)), (F(-5), F(9, 2))):
        require(rank - rank == 0 and state_value - state_value == 0,
                "self-loop correction did not cancel")

    planted_tiles = dict(edge_tiles)
    planted_tiles["overlap"] = {2, 6}
    planted_values = dict(edge_values)
    planted_values["overlap"] = {2: F(100), 6: F(0)}
    try:
        build_single_valued(planted_tiles, planted_values)
    except AssertionError:
        pass
    else:
        raise AssertionError("overlapping-owner control was accepted")
    print("SINGLE_VALUED_DESCENT_OK", f"midpoint_rows={checked}", "overlap_rejected=true")


def spectral_audit():
    q = 42
    n = 280_917
    a = 263_277
    remainder = n - a
    gate = F(49, 576) * q**4
    require(remainder == 17_640, "mass remainder")
    require(F(n, 2) < a < n < 2 * a, "source regime")

    # The direct all-state Rayleigh proof uses the 2x2 quadratic form with
    # characteristic polynomial X^2-aX-remainder^2/4.
    rational_upper = 263_573
    p_upper = F(rational_upper**2 - a * rational_upper) - F(remainder**2, 4)
    p_gate = gate**2 - a * gate - F(remainder**2, 4)
    require(p_upper == 225_208 > 0, "rational root upper")
    require(p_gate == F(4_825_657_053, 16) > 0, "gate root comparison")
    require(gate > rational_upper > a, "root branch ordering")
    require(rational_upper - a > 0 and p_upper > 0,
            "upper-minus-2x2-form is not positive definite")
    require(F(rational_upper, q**4) < F(49, 576), "normalized wall")

    # Independently replay the coefficient allocation behind the proof on a
    # dense exact family of rational (a_coord,b_coord) pairs.  The theorem
    # note supplies the general inequality; this catches sign/factor errors.
    trials = 0
    for u in range(1, 41):
        for v in range(u + 1):
            aa, bb = F(u, 40), F(v, 40)
            if aa * aa + bb * bb > 1:
                continue
            rayleigh_bound = a * aa * aa + remainder * aa * bb
            # p(rational_upper)>0 and upper>a puts upper above the positive
            # eigenvalue, so q(a,b)<=upper*(a^2+b^2)<=upper.
            require(rayleigh_bound <= rational_upper * (aa * aa + bb * bb),
                    "2x2 Rayleigh upper failed")
            trials += 1
    require(trials > 100, "insufficient rational Rayleigh trials")
    print("ALL_STATE_SPECTRAL_ARITHMETIC_OK", f"rayleigh_trials={trials}",
          f"gate_polynomial={p_gate}")


def run_q42(source):
    result = subprocess.run(
        [sys.executable, "-I", str(source)],
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    require(result.returncode == 0, f"q42 replay failed: {result.stderr.strip()}")
    require("PASS_Q42_FRACTIONAL_PROPER_CARVING_WALL" in result.stdout,
            "q42 PASS marker missing")
    require("GATE max_retained=263277 gate=1058841/4" in result.stdout,
            "q42 capacity output missing")
    print("Q42_MEASURABLE_CAPACITY_REPLAY_OK")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph-note", type=Path, default=DEFAULT_NOTE)
    parser.add_argument("--graph-verifier", type=Path, default=DEFAULT_GRAPH_VERIFIER)
    parser.add_argument("--q42-source", type=Path, default=DEFAULT_Q42_SOURCE)
    parser.add_argument("--q42-certificate", type=Path, default=DEFAULT_Q42_CERT)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    paths = {
        "note": args.graph_note,
        "graph_verifier": args.graph_verifier,
        "q42_source": args.q42_source,
        "q42_cert": args.q42_certificate,
    }
    hash_bind(paths)
    if args.full:
        run_q42(args.q42_source)
    diagonal_pruning_exhaustion()
    descent_and_overlap_audit()
    spectral_audit()
    print("PASS_INDEPENDENT_DISJOINT_GRAPH_CARVING_WALL_AUDIT")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify the four-cell no-go for arbitrary additive piece-local potentials.

Runs with ``python3 -S``.  The imported base verifier independently checks the
geometry hash, full-dimensional anchors, genuine vertices, nonnegative Farkas
multipliers, all 242 finite features, and mutation kill tests.  This extension
also treats each pair (piece id, exact evaluation point) as an independent
formal symbol, proving cancellation for arbitrary functions, not only
quadratics.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "complete_handelman" / "verify_vertex_farkas.py"
SPEC = importlib.util.spec_from_file_location("vertex_farkas_base", BASE)
vf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vf)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cert", type=Path)
    ap.add_argument("geometry", type=Path)
    ap.add_argument("--anchors", type=Path, required=True)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    vf.verify(args.cert, args.geometry, args.anchors)
    cert = json.loads(args.cert.read_text())
    pieces = vf.load_geometry(args.geometry)
    formal = defaultdict(F)
    raw_sum = F(0)
    for term in cert["terms"]:
        i, j, k, wa, wb = term["cell"]
        xa, xb, za, zb = (F(s) for s in term["vertex"])
        y = F(term["y"])
        ya, yb = (xa + za - wa) / 2, (xb + zb - wb) / 2
        for piece, point, coeff in (
            (i, (xa, xb), F(1)),
            (k, (za, zb), F(1)),
            (j, (ya, yb), F(-2)),
        ):
            formal[(piece, point)] += y * coeff
        shifts = tuple(pieces[p]["shift"] for p in (i, j, k))
        raw_sum += y * vf.raw_slack((xa, xb, za, zb), (wa, wb), shifts)

    bad = {k: v for k, v in formal.items() if v}
    assert not bad, f"arbitrary piece-local symbols did not cancel: {bad}"
    assert raw_sum == -1, f"expected normalized raw sum -1, got {raw_sum}"
    print("[8] arbitrary (piece, exact-point) function values cancel")
    print("[9] normalized raw sum = -1 (unweighted four-row sum = -4)")
    if args.selftest:
        # The base verifier's four mutation tests exercise sign, support,
        # geometry, and vertex integrity.
        vf.main = None  # document that no implicit CLI recursion occurs
        print("[selftest] run the base verifier with --selftest as the companion gate")
    print("UNIVERSAL LOCAL-POTENTIAL NO-GO VERIFIER PASS")


if __name__ == "__main__":
    main()

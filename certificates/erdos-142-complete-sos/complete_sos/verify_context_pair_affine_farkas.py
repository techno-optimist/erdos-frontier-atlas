#!/usr/bin/env python3
"""Standalone exact verifier for the order-two pair-affine no-go."""
from __future__ import annotations

import argparse
import copy
import hashlib
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


def verify(doc, geometry, cells_path, verbose=True):
    def log(msg):
        if verbose:
            print(msg)

    pieces = vf.load_geometry(geometry)
    assert hashlib.sha256(Path(geometry).read_bytes()).hexdigest() == doc["geometry_sha256"]
    cells = json.loads(Path(cells_path).read_text())["cells"]
    triples = {tuple(map(int, x["cell"][0])) for x in cells}
    context = defaultdict(F)
    flow = defaultdict(F)
    raw_sum = F(0)
    seen = set()
    for term in doc["terms"]:
        J = tuple(map(int, term["predecessor_triple"]))
        iidx = int(term["current_cell_index"])
        jidx = int(term["predecessor_cell_index"])
        i, j, k, wa, wb = map(int, term["current_cell"])
        I = (i, j, k)
        assert 0 <= iidx < len(cells) and 0 <= jidx < len(cells)
        assert tuple(map(int, cells[iidx]["cell"][0])) == I
        assert tuple(map(int, cells[jidx]["cell"][0])) == J
        assert tuple(map(int, cells[iidx]["cell"][1])) == (wa, wb)
        assert I in triples and J in triples
        assert tuple(pieces[p]["target"] for p in J) == tuple(pieces[p]["source"] for p in I)
        point = tuple(F(s) for s in term["vertex"])
        y = F(term["y"])
        assert y >= 0
        key = (jidx, iidx, point)
        assert key not in seen
        seen.add(key)
        facets = vf.cell_facets(I, (wa, wb), pieces)
        anchor = tuple(F(s) for s in cells[iidx]["anchor"])
        assert vf.strict_interior_ok(facets, anchor)
        feasible, rank, _ = vf.on_facets_rank(facets, point)
        assert feasible and rank >= 4
        xa, xb, za, zb = point
        ya, yb = (xa + za - wa) / 2, (xb + zb - wb) / 2
        role_points = ((xa, xb), (ya, yb), (za, zb))
        for role, coeff in ((0, F(1)), (1, F(-2)), (2, F(1))):
            a, b = role_points[role]
            for mon, value in enumerate((F(1), a, b)):
                context[(J[role], I[role], mon)] += y * coeff * value
        flow[J] += y
        flow[I] -= y
        raw = vf.raw_slack(point, (wa, wb), tuple(pieces[p]["shift"] for p in I))
        assert raw == F(term["raw"])
        raw_sum += y * raw
    assert all(v == 0 for v in context.values())
    assert all(v == 0 for v in flow.values())
    assert raw_sum == F(-1) == F(doc["sum_y_raw"])
    log(f"[1] geometry and {len(doc['terms'])} full-dimensional vertex rows OK")
    log("[2] all predecessor/current history edges compatible")
    log("[3] nonnegative multipliers and distinct lifted rows OK")
    log("[4] all pair-context affine monomials cancel exactly")
    log("[5] Bellman node flow cancels exactly")
    log(f"[6] sum y*raw = {raw_sum} < 0")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cert", type=Path)
    ap.add_argument("geometry", type=Path)
    ap.add_argument("cells", type=Path)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    doc = json.loads(args.cert.read_text())
    verify(doc, args.geometry, args.cells)
    if args.selftest:
        def reject(mut, label):
            try:
                verify(mut, args.geometry, args.cells, verbose=False)
            except (AssertionError, KeyError, ValueError):
                print(f"  kill test OK (rejected): {label}")
                return
            raise AssertionError(f"accepted mutation: {label}")

        mut = copy.deepcopy(doc); mut["terms"][0]["y"] = "-1"
        reject(mut, "negative multiplier")
        mut = copy.deepcopy(doc); mut["terms"] = mut["terms"][1:]
        reject(mut, "dropped circulation term")
        mut = copy.deepcopy(doc)
        mut["terms"][0]["predecessor_triple"][0] = (
            int(mut["terms"][0]["predecessor_triple"][0]) + 1
        ) % 39
        reject(mut, "broken history compatibility")
        mut = copy.deepcopy(doc); mut["terms"][0]["vertex"][0] = "1/7"
        reject(mut, "nonvertex point")
        print("ALL PAIR-AFFINE FARKAS KILL TESTS REJECTED")
    print("ORDER-TWO PAIR-AFFINE FARKAS VERIFIER PASS")


if __name__ == "__main__":
    main()

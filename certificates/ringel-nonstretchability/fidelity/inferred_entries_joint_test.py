#!/usr/bin/env python3
"""How pinned are the seven entries that were NEVER read off either projection?

Provenance of the 84 entries:
  35  appear in BOTH published affine projections and agree      (cross-checked)
  42  appear in exactly one projection                            (single read)
   7  appear in NEITHER: chi(0,i,7) for i in 1..6 and chi(0,7,8).
      es7_ringel_chirotope.py sets these by an argument about the order of the
      lines at infinity, not by transcription.  They are the weakest link, and
      TWO of them -- chi(0,6,7) and chi(0,7,8) -- are load-bearing in the Lean
      proof.

This script enumerates ALL 2^7 = 128 sign assignments to those seven cells,
holding the 77 transcribed cells fixed, and asks how many give a valid uniform
rank-3 chirotope.  That is a JOINT test of the inference step (single-cell flip
tests cannot rule out a correlated error).
"""

import itertools
import json

# `python3 -I` (isolated mode) implies -P, dropping this script's own directory from sys.path,
# so the sibling import below fails. Re-add it: keeps -I hermeticity AND makes the documented
# replay work. (Same fix as certificates/jc-family-fences -- this is a house convention.)
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

from chirotope_axioms import CHI, b2_exchange_ok, gp3_sign_ok

INFERRED = [(0, 1, 7), (0, 2, 7), (0, 3, 7), (0, 4, 7), (0, 5, 7), (0, 6, 7), (0, 7, 8)]


def main():
    assert all(CHI[t] == 1 for t in INFERRED)
    survivors = []
    for bits in itertools.product((1, -1), repeat=7):
        cand = dict(CHI)
        for t, b in zip(INFERRED, bits):
            cand[t] = b
        if gp3_sign_ok(cand):
            continue
        if b2_exchange_ok(cand):
            continue
        survivors.append(list(bits))

    ours = [1] * 7
    print(json.dumps({
        "inferred_cells": [list(t) for t in INFERRED],
        "assignments_tested": 128,
        "assignments_that_are_valid_uniform_rank3_chirotopes": len(survivors),
        "survivors": survivors,
        "our_assignment": ours,
        "our_assignment_is_a_survivor": ours in survivors,
        "inference_uniquely_forced_by_axioms": survivors == [ours],
    }, indent=2))


if __name__ == "__main__":
    main()

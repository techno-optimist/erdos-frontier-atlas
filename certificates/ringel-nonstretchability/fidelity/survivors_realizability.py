#!/usr/bin/env python3
"""Realizability of the 5 axiom-surviving assignments to the 7 inferred cells."""
import json
# `python3 -I` (isolated mode) implies -P, dropping this script's own directory from sys.path,
# so the sibling import below fails. Re-add it: keeps -I hermeticity AND makes the documented
# replay work. (Same fix as certificates/jc-family-fences -- this is a house convention.)
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

from chirotope_axioms import CHI
from mutation_fingerprint import classify

INFERRED = [(0,1,7),(0,2,7),(0,3,7),(0,4,7),(0,5,7),(0,6,7),(0,7,8)]
SURV = [[1,1,1,1,1,1,1],[1,1,1,1,1,1,-1],[-1,1,1,1,1,1,-1],
        [-1,-1,1,1,1,1,-1],[-1,-1,-1,1,1,1,-1]]
out=[]
for i,bits in enumerate(SURV):
    c=dict(CHI)
    for t,b in zip(INFERRED,bits): c[t]=b
    r=classify(c, f"survivor{i}:{bits}", 5000+i)
    r.pop("points", None)
    out.append(r)
    print(json.dumps(r), flush=True)
print(json.dumps({"non_realizable": [r["tag"] for r in out if r["verdict"]=="NON-REALIZABLE"]}, indent=2))

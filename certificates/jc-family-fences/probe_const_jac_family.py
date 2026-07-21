#!/usr/bin/env python3
"""Count constant-Jacobian maps in k=2 Alpoge-shaped family; collision scan on hits."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import search_degree_family as F

HERE = Path(__file__).resolve().parent


def main():
    const = []
    hits = []
    n = 0
    for a, b, c, d, e, f, g in itertools.product(
        range(-2, 3),
        range(-2, 3),
        range(-2, 3),
        range(-2, 3),
        range(-2, 3),
        range(-2, 3),
        range(-2, 3),
    ):
        n += 1
        if e == 0 and g == 0:
            continue
        fs = F.build_family(2, a, b, c, d, e, f, g)
        degs = [F.total_deg(comp) for comp in fs]
        mdeg = max(degs)
        if mdeg < 3 or mdeg > 6:
            continue
        dJ = F.jac_det(fs)
        if not F.is_const_nonzero(dJ):
            continue
        entry = {
            "params": dict(k=2, a=a, b=b, c=c, d=d, e=e, f=f, g=g),
            "degs": degs,
            "max_deg": mdeg,
            "det": str(dJ[(0, 0, 0)]),
        }
        const.append(entry)
        print("const", entry, flush=True)
        col = F.find_collision(fs, bound=5)
        if col:
            p, q, img = col
            hits.append(
                {
                    **entry,
                    "p": [str(x) for x in p],
                    "q": [str(x) for x in q],
                    "image": [str(x) for x in img],
                }
            )
            print("HIT", hits[-1], flush=True)

    # k=3: only (e,f,g) near Alpoge with a,b,c,d fixed
    for e, f, g in itertools.product(range(-2, 5), range(-4, 1), range(-2, 2)):
        if (e, f, g) == (2, -3, -1):
            continue
        fs = F.build_family(3, 4, 3, 3, 3, e, f, g)
        degs = [F.total_deg(comp) for comp in fs]
        mdeg = max(degs)
        if not (3 <= mdeg <= 6):
            continue
        dJ = F.jac_det(fs)
        if not F.is_const_nonzero(dJ):
            continue
        entry = {
            "params": dict(k=3, a=4, b=3, c=3, d=3, e=e, f=f, g=g),
            "degs": degs,
            "max_deg": mdeg,
            "det": str(dJ[(0, 0, 0)]),
        }
        const.append(entry)
        print("const", entry, flush=True)
        col = F.find_collision(fs, bound=5)
        if col:
            p, q, img = col
            hits.append({**entry, "p": [str(x) for x in p], "q": [str(x) for x in q]})
            print("HIT", hits[-1], flush=True)

    out = {
        "schema": "jc.const_jac_k2.v1",
        "scanned_k2": n,
        "const_maps": const,
        "hits": hits,
        "status": "FOUND" if hits else "NO_LOW_DEGREE_CE_IN_BOX",
    }
    (HERE / "CONST_JAC_K2.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in out.items()}, indent=2))


if __name__ == "__main__":
    main()

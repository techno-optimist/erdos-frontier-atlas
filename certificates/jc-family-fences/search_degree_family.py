#!/usr/bin/env python3
"""
Structured degree hunt for dim-3 Keller counterexamples of max degree < 7.

Family (Alpöge-shaped, integer parameters a,b,c,d,e,k):
  u = 1 + x y
  f1 = u^k * z + y^2 * u * (a + b x y)
  f2 = y + c x u^{k-1} z + d x y^2 (a + b x y)
  f3 = e x + f x^2 y + g x^3 z

Require det JF identically constant nonzero, max total degree in {3,4,5,6},
and a rational collision (non-injectivity).

Alpöge: k=3,a=4,b=3,c=3,d=3,e=2,f=-3,g=-1 -> deg 7, det -2.
"""

from __future__ import annotations

import itertools
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent


def pconst(c):
    c = Q(c)
    return {(0, 0, 0): c} if c else {}


X, Y, Z = {(1, 0, 0): Q(1)}, {(0, 1, 0): Q(1)}, {(0, 0, 1): Q(1)}


def padd(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            s = out.get(m, Q(0)) + c
            if s:
                out[m] = s
            elif m in out:
                del out[m]
    return out


def pmul(a, b):
    out = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            m = (ma[0] + mb[0], ma[1] + mb[1], ma[2] + mb[2])
            s = out.get(m, Q(0)) + ca * cb
            if s:
                out[m] = s
            elif m in out:
                del out[m]
    return out


def pscale(a, c):
    c = Q(c)
    return {m: v * c for m, v in a.items()} if c else {}


def ppow(a, n):
    out = pconst(1)
    for _ in range(n):
        out = pmul(out, a)
    return out


def pdiff(a, axis):
    out = {}
    for m, c in a.items():
        e = m[axis]
        if e:
            dm = tuple(v - (1 if i == axis else 0) for i, v in enumerate(m))
            out[dm] = out.get(dm, Q(0)) + c * e
    return {m: c for m, c in out.items() if c}


def peval(a, pt):
    x, y, z = pt
    return sum((c * x ** m[0] * y ** m[1] * z ** m[2] for m, c in a.items()), Q(0))


def det3(rows):
    (a, b, c), (d, e, f), (g, h, i) = rows
    return padd(
        pmul(a, padd(pmul(e, i), pscale(pmul(f, h), -1))),
        pscale(pmul(b, padd(pmul(d, i), pscale(pmul(f, g), -1))), -1),
        pmul(c, padd(pmul(d, h), pscale(pmul(e, g), -1))),
    )


def jac_det(fs):
    return det3([[pdiff(f, ax) for ax in (0, 1, 2)] for f in fs])


def total_deg(f):
    return max((sum(m) for m in f), default=0)


def build_family(k, a, b, c, d, e, f, g):
    u = padd(pconst(1), pmul(X, Y))
    w = padd(pconst(a), pscale(pmul(X, Y), b))
    f1 = padd(pmul(ppow(u, k), Z), pmul(pmul(ppow(Y, 2), u), w))
    f2 = padd(
        Y,
        pscale(pmul(pmul(X, ppow(u, k - 1)), Z), c),
        pscale(pmul(pmul(X, ppow(Y, 2)), w), d),
    )
    f3 = padd(
        pscale(X, e),
        pscale(pmul(ppow(X, 2), Y), f),
        pscale(pmul(ppow(X, 3), Z), g),
    )
    return f1, f2, f3


def is_const_nonzero(d):
    if not d:
        return False
    return set(d.keys()) == {(0, 0, 0)} and d[(0, 0, 0)] != 0


def find_collision(fs, bound=4):
    """Search small rational grid for two distinct points with same image."""
    coords = [Q(i, den) for den in (1, 2) for i in range(-bound, bound + 1)]
    images = {}
    for x in coords:
        for y in coords:
            for z in coords:
                img = tuple(peval(f, (x, y, z)) for f in fs)
                key = img
                pt = (x, y, z)
                if key in images and images[key] != pt:
                    return images[key], pt, img
                images[key] = pt
    return None


def main():
    hits = []
    const_maps = []
    # k=2,3; integer coeffs small
    for k in (2, 3):
        for a, b, c, d, e, f, g in itertools.product(
            range(-4, 5),  # a
            range(-4, 5),  # b
            range(-4, 5),  # c
            range(-4, 5),  # d
            range(-3, 4),  # e
            range(-4, 5),  # f
            range(-3, 4),  # g
        ):
            if k == 3 and (a, b, c, d, e, f, g) == (4, 3, 3, 3, 2, -3, -1):
                continue  # known deg-7 Alpöge
            if e == 0 and g == 0:
                continue  # degenerate f3
            fs = build_family(k, a, b, c, d, e, f, g)
            degs = [total_deg(comp) for comp in fs]
            mdeg = max(degs)
            if mdeg < 3 or mdeg > 6:
                continue
            dJ = jac_det(fs)
            if not is_const_nonzero(dJ):
                continue
            const_maps.append(
                {
                    "params": {
                        "k": k,
                        "a": a,
                        "b": b,
                        "c": c,
                        "d": d,
                        "e": e,
                        "f": f,
                        "g": g,
                    },
                    "degs": degs,
                    "max_deg": mdeg,
                    "det": str(dJ[(0, 0, 0)]),
                }
            )
            col = find_collision(fs, bound=3)
            if col:
                p, q, img = col
                hits.append(
                    {
                        "params": const_maps[-1]["params"],
                        "degs": degs,
                        "max_deg": mdeg,
                        "det": str(dJ[(0, 0, 0)]),
                        "p": [str(c) for c in p],
                        "q": [str(c) for c in q],
                        "image": [str(c) for c in img],
                    }
                )
                print("HIT", hits[-1], flush=True)

    # Always re-verify Alpöge control still deg 7 const
    control = build_family(3, 4, 3, 3, 3, 2, -3, -1)
    dJc = jac_det(control)
    control_ok = is_const_nonzero(dJc) and max(total_deg(f) for f in control) == 7

    result = {
        "schema": "jc.degree_family_hunt.v1",
        "family": "Alpoge-shaped (k,a,b,c,d,e,f,g)",
        "const_jacobian_maps_deg_3_to_6": len(const_maps),
        "collision_hits": hits,
        "sample_const_maps": const_maps[:20],
        "alpoge_control_ok": control_ok,
        "status": (
            "FOUND_LOW_DEGREE_COUNTEREXAMPLE"
            if hits
            else "NO_HIT_IN_FAMILY"
        ),
        "claim_boundary": (
            "Exhaustive small-integer scan of one parametric family. "
            "Absence of hits is not a no-go outside the family."
        ),
    }
    out = HERE / "DEGREE_FAMILY_RESULT.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in ("sample_const_maps", "collision_hits")
            },
            indent=2,
        )
    )
    print("hits", len(hits), "const_maps", len(const_maps))


import itertools  # noqa: E402

if __name__ == "__main__":
    main()

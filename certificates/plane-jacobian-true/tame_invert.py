#!/usr/bin/env python3
"""Shared tame-inverse pipeline for plane Keller maps."""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import product
from typing import Dict, List, Optional, Tuple

from poly2 import X, Y, compose, padd, pconst, poly_eq, ppow, pscale, total_degree

Poly = Dict[Tuple[int, int], Q]


def c(p: Poly, mon) -> Q:
    return p.get(mon, Q(0))


def verify_inverse(f, g, h0, h1) -> bool:
    fg0, fg1 = compose(f, g, h0, h1)
    gf0, gf1 = compose(h0, h1, f, g)
    return poly_eq(fg0, X) and poly_eq(fg1, Y) and poly_eq(gf0, X) and poly_eq(gf1, Y)


def try_elementary_y(f: Poly, g: Poly) -> Optional[Tuple[Poly, Poly]]:
    if any(i != 0 for i, j in g):
        return None
    a = c(f, (1, 0))
    if a == 0:
        return None
    for (i, j), _ in f.items():
        if i >= 2 or (i == 1 and j != 0):
            return None
    b0, b1 = c(g, (0, 0)), c(g, (0, 1))
    if b1 == 0 or any(j >= 2 for i, j in g):
        return None
    p_y = {(0, j): coeff for (i, j), coeff in f.items() if i == 0}
    y_inv = padd(pscale(Y, Q(1) / b1), pconst(-b0 / b1))
    p_at = pconst(0)
    for (i, j), coeff in p_y.items():
        p_at = padd(p_at, pscale(ppow(y_inv, j), coeff))
    x_inv = padd(pscale(X, Q(1) / a), pscale(p_at, -Q(1) / a))
    return x_inv, y_inv


def try_elementary_x(f: Poly, g: Poly) -> Optional[Tuple[Poly, Poly]]:
    if any(j != 0 for i, j in f):
        return None
    b = c(g, (0, 1))
    if b == 0:
        return None
    for (i, j), _ in g.items():
        if j >= 2 or (j == 1 and i != 0):
            return None
    a0, a1 = c(f, (0, 0)), c(f, (1, 0))
    if a1 == 0 or any(i >= 2 for i, j in f):
        return None
    q_x = {(i, 0): coeff for (i, j), coeff in g.items() if j == 0}
    x_inv = padd(pscale(X, Q(1) / a1), pconst(-a0 / a1))
    q_at = pconst(0)
    for (i, j), coeff in q_x.items():
        q_at = padd(q_at, pscale(ppow(x_inv, i), coeff))
    y_inv = padd(pscale(Y, Q(1) / b), pscale(q_at, -Q(1) / b))
    return x_inv, y_inv


def linear_domain(a11, a12, a21, a22):
    det = a11 * a22 - a12 * a21
    if det == 0:
        return None
    return (
        padd(pscale(X, a11), pscale(Y, a12)),
        padd(pscale(X, a21), pscale(Y, a22)),
    )


def try_conjugate_elementary(f, g, entries=None):
    if entries is None:
        entries = [Q(-1), Q(0), Q(1)]
    for a11, a12, a21, a22 in product(entries, repeat=4):
        T = linear_domain(a11, a12, a21, a22)
        if T is None:
            continue
        det = a11 * a22 - a12 * a21
        if det not in (Q(1), Q(-1)):
            continue
        fT, gT = compose(f, g, T[0], T[1])
        inv_el = try_elementary_y(fT, gT) or try_elementary_x(fT, gT)
        if inv_el is None:
            continue
        return compose(T[0], T[1], inv_el[0], inv_el[1])
    return None


def try_codomain_shear(f, g, kmax=3):
    for k in [Q(t) for t in range(-kmax, kmax + 1)]:
        for fsh, gsh, kind in (
            (padd(f, pscale(g, -k)), g, "uv"),
            (f, padd(g, pscale(f, -k)), "vu"),
        ):
            inv_sh = (
                try_elementary_y(fsh, gsh)
                or try_elementary_x(fsh, gsh)
                or try_conjugate_elementary(fsh, gsh)
            )
            if inv_sh is None:
                continue
            h0, h1 = inv_sh
            if kind == "uv":
                s0, s1 = padd(X, pscale(Y, -k)), Y
            else:
                s0, s1 = X, padd(Y, pscale(X, -k))
            return compose(h0, h1, s0, s1)
    return None


def invert_tame(f, g):
    d = max(total_degree(f), total_degree(g), 0)
    # local wang for deg<=2 via elementary/shear/conj only if structured
    pipeline = [
        ("elem_y", lambda: try_elementary_y(f, g)),
        ("elem_x", lambda: try_elementary_x(f, g)),
        ("conj", lambda: try_conjugate_elementary(f, g)),
        ("shear", lambda: try_codomain_shear(f, g)),
    ]
    for name, fn in pipeline:
        inv = fn()
        if inv is not None and verify_inverse(f, g, inv[0], inv[1]):
            return name, inv
    return None

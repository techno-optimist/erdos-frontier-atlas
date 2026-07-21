#!/usr/bin/env python3
"""Exact bivariate polynomial engine over Q (Fraction)."""
from __future__ import annotations

from fractions import Fraction as Q
from typing import Dict, Iterable, Tuple

Mon = Tuple[int, int]
Poly = Dict[Mon, Q]


def pconst(c) -> Poly:
    c = Q(c)
    return {(0, 0): c} if c else {}


X: Poly = {(1, 0): Q(1)}
Y: Poly = {(0, 1): Q(1)}


def padd(*ps: Poly) -> Poly:
    out: Poly = {}
    for p in ps:
        for m, c in p.items():
            s = out.get(m, Q(0)) + c
            if s:
                out[m] = s
            elif m in out:
                del out[m]
    return out


def pscale(a: Poly, c) -> Poly:
    c = Q(c)
    return {m: v * c for m, v in a.items()} if c else {}


def pmul(a: Poly, b: Poly) -> Poly:
    out: Poly = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            m = (ma[0] + mb[0], ma[1] + mb[1])
            s = out.get(m, Q(0)) + ca * cb
            if s:
                out[m] = s
            elif m in out:
                del out[m]
    return out


def ppow(a: Poly, n: int) -> Poly:
    out = pconst(1)
    for _ in range(n):
        out = pmul(out, a)
    return out


def pdiff(a: Poly, axis: int) -> Poly:
    out: Poly = {}
    for m, c in a.items():
        e = m[axis]
        if e:
            dm = (m[0] - (1 if axis == 0 else 0), m[1] - (1 if axis == 1 else 0))
            out[dm] = out.get(dm, Q(0)) + c * e
    return {m: c for m, c in out.items() if c}


def peval(a: Poly, pt) -> Q:
    x, y = pt
    return sum((c * x ** m[0] * y ** m[1] for m, c in a.items()), Q(0))


def total_degree(a: Poly) -> int:
    if not a:
        return -1
    return max(i + j for i, j in a)


def is_const(a: Poly) -> bool:
    return all(m == (0, 0) for m in a)


def jac_det(f: Poly, g: Poly) -> Poly:
    return padd(pmul(pdiff(f, 0), pdiff(g, 1)), pscale(pmul(pdiff(f, 1), pdiff(g, 0)), -1))


def compose(f: Poly, g: Poly, u: Poly, v: Poly) -> Tuple[Poly, Poly]:
    def subst(p: Poly) -> Poly:
        out = pconst(0)
        for (i, j), c in p.items():
            term = pconst(c)
            if i:
                term = pmul(term, ppow(u, i))
            if j:
                term = pmul(term, ppow(v, j))
            out = padd(out, term)
        return out

    return subst(f), subst(g)


def poly_eq(a: Poly, b: Poly) -> bool:
    return padd(a, pscale(b, -1)) == {}


def monoms_upto(d: int) -> Iterable[Mon]:
    for i in range(d + 1):
        for j in range(d + 1 - i):
            yield (i, j)

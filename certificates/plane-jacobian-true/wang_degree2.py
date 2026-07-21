#!/usr/bin/env python3
"""Wang deg<=2 plane maps: structured inverse (restored core)."""
from __future__ import annotations

import os
import sys
from fractions import Fraction as Q
from typing import Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poly2 import (
    X,
    Y,
    compose,
    jac_det,
    padd,
    pconst,
    pmul,
    poly_eq,
    ppow,
    pscale,
    total_degree,
)

Poly = dict


def is_const_nonzero(p: Poly) -> bool:
    return p.keys() == {(0, 0)} and p[(0, 0)] != 0


def linear_solve_2x2(M, b):
    (a, c), (d, e) = M
    det = a * e - c * d
    if det == 0:
        return None
    return ((e * b[0] - c * b[1]) / det, (-d * b[0] + a * b[1]) / det)


def invert_affine(a00, a10, a01, b00, b10, b01):
    inv = linear_solve_2x2(((a10, a01), (b10, b01)), (Q(1), Q(0)))
    inv2 = linear_solve_2x2(((a10, a01), (b10, b01)), (Q(0), Q(1)))
    if inv is None or inv2 is None:
        return None
    A10, B10 = inv
    A01, B01 = inv2
    c_shift = linear_solve_2x2(((a10, a01), (b10, b01)), (a00, b00))
    if c_shift is None:
        return None
    g0 = padd(pscale(X, A10), pscale(Y, A01), pconst(-c_shift[0]))
    g1 = padd(pscale(X, B10), pscale(Y, B01), pconst(-c_shift[1]))
    return g0, g1


def build_affine(a00, a10, a01, b00, b10, b01):
    f = padd(pconst(a00), pscale(X, a10), pscale(Y, a01))
    g = padd(pconst(b00), pscale(X, b10), pscale(Y, b01))
    return f, g


def map_from_coeffs(
    a00, a10, a01, a20, a11, a02, b00, b10, b01, b20, b11, b02
):
    f = padd(
        pconst(a00), pscale(X, a10), pscale(Y, a01),
        pscale(ppow(X, 2), a20), pscale(pmul(X, Y), a11), pscale(ppow(Y, 2), a02),
    )
    g = padd(
        pconst(b00), pscale(X, b10), pscale(Y, b01),
        pscale(ppow(X, 2), b20), pscale(pmul(X, Y), b11), pscale(ppow(Y, 2), b02),
    )
    return f, g


def reconstruct_square_form(d, e, f_, D, E, F_):
    if d * E != e * D or d * F_ != f_ * D or e * F_ != f_ * E:
        return None
    if all(c == 0 for c in (d, e, f_, D, E, F_)):
        return None
    for (a2, a1, a0, tag) in ((d, e, f_, "f"), (D, E, F_, "g")):
        if a2 == a1 == a0 == 0:
            continue
        disc = a1 * a1 - 4 * a2 * a0
        if disc != 0:
            return None
        if a2 != 0:
            p, alpha, q = Q(1), a2, a1 / (2 * a2)
            if alpha * q * q != a0:
                return None
        elif a0 != 0:
            p, q, alpha = Q(0), Q(1), a0
        else:
            return None
        if tag == "f":
            if p != 0:
                beta = D / (p * p)
            else:
                beta = F_ / (q * q)
            if beta * p * p != D or 2 * beta * p * q != E or beta * q * q != F_:
                return None
            return (alpha, beta, p, q)
        else:
            if p != 0:
                alpha_f = d / (p * p)
            else:
                alpha_f = f_ / (q * q)
            if alpha_f * p * p != d or 2 * alpha_f * p * q != e or alpha_f * q * q != f_:
                return None
            return (alpha_f, alpha, p, q)
    return None


def elementary_keller_and_inverse(a, b, c, alpha, A, C):
    if b == 0 or C == 0:
        return None
    f = padd(pconst(a), pscale(X, b), pscale(Y, c), pscale(ppow(Y, 2), alpha))
    g = padd(pconst(A), pscale(Y, C))
    if not poly_eq(jac_det(f, g), pconst(b * C)):
        return None
    y = padd(pscale(Y, Q(1) / C), pconst(-A / C))
    x = padd(
        pscale(X, Q(1) / b), pconst(-a / b),
        pscale(y, -c / b), pscale(ppow(y, 2), -alpha / b),
    )
    return (f, g), (x, y)


def invert_structured(f: Poly, g: Poly) -> Optional[Tuple[Poly, Poly]]:
    def coeff(poly, mon):
        return poly.get(mon, Q(0))

    a20, a11, a02 = coeff(f, (2, 0)), coeff(f, (1, 1)), coeff(f, (0, 2))
    b20, b11, b02 = coeff(g, (2, 0)), coeff(g, (1, 1)), coeff(g, (0, 2))
    a00, a10, a01 = coeff(f, (0, 0)), coeff(f, (1, 0)), coeff(f, (0, 1))
    b00, b10, b01 = coeff(g, (0, 0)), coeff(g, (1, 0)), coeff(g, (0, 1))

    if a20 == a11 == a02 == b20 == b11 == b02 == 0:
        return invert_affine(a00, a10, a01, b00, b10, b01)

    rec = reconstruct_square_form(a20, a11, a02, b20, b11, b02)
    if rec is None:
        return None
    alpha, beta, p, q = rec
    if p == 0 and q == 0:
        return None

    shear_k = Q(0)
    swapped = False
    if beta != 0:
        k = alpha / beta
        f_sh = padd(f, pscale(g, -k))
        g_sh = g
        shear_k = k
        beta_eff = beta
    elif alpha != 0:
        f_sh, g_sh = g, f
        swapped = True
        beta_eff = alpha
    else:
        return None

    den = p * p + q * q
    if den == 0:
        return None
    x_of_st = padd(pscale(X, q / den), pscale(Y, p / den))
    y_of_st = padd(pscale(X, -p / den), pscale(Y, q / den))
    fT, gT = compose(f_sh, g_sh, x_of_st, y_of_st)

    def cc(poly, mon):
        return poly.get(mon, Q(0))

    if any(cc(fT, m) != 0 for m in ((2, 0), (1, 1), (0, 2))):
        return None
    if cc(gT, (2, 0)) != 0 or cc(gT, (1, 1)) != 0:
        return None
    if cc(gT, (0, 2)) != beta_eff:
        return None

    A0, As, At = cc(fT, (0, 0)), cc(fT, (1, 0)), cc(fT, (0, 1))
    B0, Bs, Bt = cc(gT, (0, 0)), cc(gT, (1, 0)), cc(gT, (0, 1))
    Btt = cc(gT, (0, 2))

    if Btt != 0:
        if As != 0 or At == 0 or Bs == 0:
            return None
        t_uv = padd(pscale(X, Q(1) / At), pconst(-A0 / At))
        s_uv = padd(
            pscale(Y, Q(1) / Bs), pconst(-B0 / Bs),
            pscale(t_uv, -Bt / Bs), pscale(ppow(t_uv, 2), -Btt / Bs),
        )
    else:
        inv_aff = invert_affine(A0, As, At, B0, Bs, Bt)
        if inv_aff is None:
            return None
        s_uv, t_uv = inv_aff

    x_sh, y_sh = compose(x_of_st, y_of_st, s_uv, t_uv)
    if shear_k != 0:
        x_out, y_out = compose(x_sh, y_sh, padd(X, pscale(Y, -shear_k)), Y)
    else:
        x_out, y_out = x_sh, y_sh
    if swapped:
        x_out, y_out = compose(x_out, y_out, Y, X)
    return x_out, y_out

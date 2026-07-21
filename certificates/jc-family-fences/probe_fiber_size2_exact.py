#!/usr/bin/env python3
"""
Exact search for fiber cardinality 2 of Alpöge's map on V(E).

Uses the fiber_anchors methodology: for fixed rational t on E=0,
factor G1(t;y) over Q, for each y0 solve the (x,z) system via resultants
in Q[x] and count complex roots of the squarefree gcd.

A size-2 hit closes jc-fiber-count-spectrum-size to 4.
"""

from __future__ import annotations

import json
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ---------- univariate Q[x] engine ----------
def poly_add(a, b):
    n = max(len(a), len(b))
    a = a + [Fr(0)] * (n - len(a))
    b = b + [Fr(0)] * (n - len(b))
    out = [a[i] + b[i] for i in range(n)]
    while out and out[-1] == 0:
        out.pop()
    return out


def poly_sub(a, b):
    return poly_add(a, [-c for c in b])


def poly_scale(a, s):
    return [c * s for c in a] if s else []


def poly_mul(a, b):
    if not a or not b:
        return []
    out = [Fr(0)] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            out[i + j] += ca * cb
    while out and out[-1] == 0:
        out.pop()
    return out


def poly_deg(a):
    return len(a) - 1 if a else -1


def poly_divmod(a, b):
    a = list(a)
    b = list(b)
    assert b and b[-1] != 0
    if poly_deg(a) < poly_deg(b):
        return [], a
    q = [Fr(0)] * (poly_deg(a) - poly_deg(b) + 1)
    while poly_deg(a) >= poly_deg(b):
        k = poly_deg(a) - poly_deg(b)
        coef = a[-1] / b[-1]
        q[k] = coef
        mon = [Fr(0)] * k + [coef * c for c in b]
        a = poly_sub(a, mon)
    while a and a[-1] == 0:
        a.pop()
    return q, a


def poly_gcd(a, b):
    a, b = list(a), list(b)
    while b:
        _, r = poly_divmod(a, b)
        a, b = b, r
    if not a:
        return []
    # monic
    lead = a[-1]
    return [c / lead for c in a]


def poly_diff(a):
    return [a[i] * i for i in range(1, len(a))]


def poly_sqfree(a):
    if not a:
        return []
    g = poly_gcd(a, poly_diff(a))
    q, r = poly_divmod(a, g)
    assert not r
    if not q:
        return []
    lead = q[-1]
    return [c / lead for c in q]


def poly_eval(a, x):
    s = Fr(0)
    p = Fr(1)
    for c in a:
        s += c * p
        p *= x
    return s


def rational_roots(a):
    """Possible rational roots of monic-ish poly over Q."""
    if not a:
        return []
    # clear dens: multiply by common denom
    from math import gcd
    dens = [c.denominator for c in a]
    lcm = 1
    for d in dens:
        lcm = lcm * d // gcd(lcm, d)
    coeffs = [int(c * lcm) for c in a]
    # integer poly
    while coeffs and coeffs[-1] == 0:
        coeffs.pop()
    if not coeffs:
        return []
    # make content-free
    g = 0
    for c in coeffs:
        g = gcd(g, abs(c)) if g else abs(c)
    if g:
        coeffs = [c // g for c in coeffs]
    a0, an = coeffs[0], coeffs[-1]
    def factors(n):
        n = abs(n)
        out = {1}
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                out.add(i)
                out.add(n // i)
        if n:
            out.add(n)
        return out
    cands = set()
    for p in factors(a0):
        for q in factors(an):
            cands.add(Fr(p, q))
            cands.add(Fr(-p, q))
    cands.add(Fr(0))
    roots = []
    for r in cands:
        if poly_eval(a, r) == 0:
            roots.append(r)
    return sorted(set(roots))


# ---------- map F and G1 ----------
def F(x, y, z):
    u = 1 + x * y
    return (
        u**3 * z + y**2 * u * (4 + 3 * x * y),
        y + 3 * x * u**2 * z + 3 * x * y**2 * (4 + 3 * x * y),
        2 * x - 3 * x**2 * y - x**3 * z,
    )


def E(t1, t2, t3):
    return (
        27 * t1**2 * t3**2
        - 18 * t1 * t2 * t3
        + 16 * t1
        + t2**3 * t3
        - t2**2
    )


def G1_coeffs(t1, t2, t3):
    # 2 y^3 - 3 t2 y^2 + 18 t1 y + (27 t1^2 t3 - 18 t1 t2 + t2^3)
    return [
        27 * t1**2 * t3 - 18 * t1 * t2 + t2**3,
        18 * t1,
        -3 * t2,
        Fr(2),
    ]


def y_roots_exact(t1, t2, t3):
    """All rational y-roots of G1; for remaining quadratic factor count complex roots."""
    a = G1_coeffs(t1, t2, t3)
    roots = rational_roots(a)
    # factor out (y-r) for each rational root with multiplicity
    p = list(a)
    found = []
    for r in roots:
        while poly_deg(p) >= 1 and poly_eval(p, r) == 0:
            # synthetic divide by (y-r)
            # p = c0 + c1 y + ...
            q = []
            acc = Fr(0)
            for c in reversed(p):
                acc = acc * r + c  # wrong direction
            # monic-ish division
            b = list(p)
            quot = []
            while poly_deg(b) >= 1:
                coef = b[-1] / Fr(1)  # leading of (y-r) is 1 after scale
                # divide by monic (y-r): use poly_divmod with [ -r, 1 ]
                q2, rem = poly_divmod(b, [-r, Fr(1)])
                if rem:
                    break
                found.append(r)
                b = q2
            break
        else:
            continue
        p = b
        # restart roots on residual
        for r2 in rational_roots(p):
            while poly_deg(p) >= 1:
                q2, rem = poly_divmod(p, [-r2, Fr(1)])
                if rem:
                    break
                found.append(r2)
                p = q2
    # any leftover poly of deg 1 or 2 contributes that many complex roots if nonzero
    leftover = poly_sqfree(p) if p else []
    return found, leftover


def y_roots_full(t1, t2, t3):
    """Return list of (y0, multiplicity contribution as distinct root flag)."""
    a = G1_coeffs(t1, t2, t3)
    # Use rational root factoring completely
    p = list(a)
    distinct = []
    # strip rational roots
    changed = True
    while changed and poly_deg(p) >= 1:
        changed = False
        for r in rational_roots(p):
            q, rem = poly_divmod(p, [-r, Fr(1)])
            if not rem:
                if r not in distinct:
                    distinct.append(r)
                p = q
                changed = True
                break
    leftover_deg = poly_deg(poly_sqfree(p)) if p else -1
    # irrational roots from leftover: if deg 2 irreducible, 2 complex; deg 1 one more rational?
    extra = max(0, leftover_deg)  # squarefree leftover degree = number of additional distinct complex roots
    return distinct, extra


def fiber_count_at_y(t1, t2, t3, y0):
    """#complex solutions of F(x,y0,z)=t via resultant gcd in Q[x]."""
    # p_i = a_i(x) z + b_i(x) - t_i = 0
    # a1=(1+y0 x)^3, b1 = y0^2 (1+y0 x)(4+3 y0 x)
    # a2=3x(1+y0 x)^2, b2 = y0 + 3x y0^2 (4+3 y0 x)
    # a3=-x^3, b3 = 2x - 3 x^2 y0
    # With t subtracted from constants in b
    # Represent a_i, b_i as polys in x

    def pconst(c):
        return [Fr(c)] if c else []

    def px():
        return [Fr(0), Fr(1)]

    def padd(*ps):
        out = []
        for p in ps:
            out = poly_add(out, p)
        return out

    def pmul(a, b):
        return poly_mul(a, b)

    def ppow(a, n):
        out = [Fr(1)]
        for _ in range(n):
            out = pmul(out, a)
        return out

    x = px()
    u = padd([Fr(1)], poly_scale(x, y0))  # 1 + y0 x
    a1 = ppow(u, 3)
    b1 = padd(
        pmul(pmul([y0**2], u), padd([Fr(4)], poly_scale(x, 3 * y0))),
        [-t1],
    )
    a2 = pmul(poly_scale(x, 3), ppow(u, 2))
    b2 = padd(
        [y0],
        pmul(poly_scale(x, 3 * y0**2), padd([Fr(4)], poly_scale(x, 3 * y0))),
        [-t2],
    )
    a3 = poly_scale(ppow(x, 3), -1)
    b3 = padd(poly_scale(x, 2), poly_scale(pmul(ppow(x, 2), [y0]), -3), [-t3])

    def Rij(ai, bi, aj, bj):
        return poly_sub(pmul(ai, bj), pmul(aj, bi))

    R12 = Rij(a1, b1, a2, b2)
    R13 = Rij(a1, b1, a3, b3)
    R23 = Rij(a2, b2, a3, b3)
    g = poly_gcd(R12, R13)
    g = poly_gcd(g, R23)
    if not g:
        return 0  # g==0 boundary: whole line (should not happen)
    sf = poly_sqfree(g)
    return max(0, poly_deg(sf))


def fiber_cardinality(t1, t2, t3):
    ys, extra_irr = y_roots_full(t1, t2, t3)
    total = 0
    detail = []
    for y0 in ys:
        c = fiber_count_at_y(t1, t2, t3, y0)
        total += c
        detail.append((str(y0), c))
    # irrational y roots: we don't solve fully — skip extra_irr contribution
    # unless leftover is deg 0
    return total, detail, extra_irr


def points_on_E():
    """Generate many rational points on E=0."""
    pts = []
    # t2=0 slice: E = 27 t1^2 t3^2 + 16 t1 = t1 (27 t1 t3^2 + 16)
    for t1n in range(-12, 13):
        for den in (1, 2, 3, 4):
            t1 = Fr(t1n, den)
            if t1 == 0:
                # E = -t2^2 + t2^3 t3; need t2=0 any t3 or t3=1/t2
                for t2n in range(-8, 9):
                    if t2n == 0:
                        for t3n in range(-5, 6):
                            pts.append((Fr(0), Fr(0), Fr(t3n)))
                    else:
                        t2 = Fr(t2n)
                        pts.append((Fr(0), t2, Fr(1) / t2))  # if E=0?
                continue
            # 27 t1 t3^2 + 16 = 0 => t3^2 = -16/(27 t1)
            # only if RHS perfect square in Q
            rhs = Fr(-16) / (27 * t1)
            if rhs < 0:
                continue
            for s in range(0, 80):
                for sd in (1, 2, 3, 4, 5, 6, 9):
                    if Fr(s, sd) ** 2 == rhs:
                        pts.append((t1, Fr(0), Fr(s, sd)))
                        pts.append((t1, Fr(0), -Fr(s, sd)))
    # parametric: fix t1,t2 solve quadratic in t3
    for t1n in range(-8, 9):
        for t2n in range(-8, 9):
            for d in (1, 2, 3):
                t1, t2 = Fr(t1n, d), Fr(t2n, d)
                A = 27 * t1**2
                B = t2**3 - 18 * t1 * t2
                C = 16 * t1 - t2**2
                if A == 0:
                    if B != 0:
                        pts.append((t1, t2, -C / B))
                    continue
                disc = B * B - 4 * A * C
                if disc < 0:
                    continue
                for s in range(0, 200):
                    for sd in (1, 2, 3, 4, 5):
                        if Fr(s, sd) ** 2 == disc:
                            pts.append((t1, t2, (-B + Fr(s, sd)) / (2 * A)))
                            pts.append((t1, t2, (-B - Fr(s, sd)) / (2 * A)))
                            break
                    else:
                        continue
                    break
    # known anchors
    pts.extend(
        [
            (Fr(-1, 4), Fr(0), Fr(0)),
            (Fr(-16, 27), Fr(0), Fr(1)),
            (Fr(-4, 27), Fr(0), Fr(2)),
            (Fr(-1), Fr(2), Fr(-2)),
            (Fr(1), Fr(4), Fr(0)),
            (Fr(2), Fr(5), Fr(1, 4)),
            (Fr(2), Fr(5), Fr(7, 27)),
            (Fr(0), Fr(1), Fr(1)),
            (Fr(0), Fr(0), Fr(5)),
            (Fr(0), Fr(2), Fr(3)),
            (Fr(3), Fr(6), Fr(2, 9)),
            (Fr(1, 3), Fr(2), Fr(2, 3)),
        ]
    )
    # unique with E==0
    clean = []
    seen = set()
    for t in pts:
        if E(*t) != 0:
            continue
        key = tuple(t)
        if key in seen:
            continue
        seen.add(key)
        clean.append(t)
    return clean


def main():
    pts = points_on_E()
    print(f"rational points on V(E): {len(pts)}", flush=True)
    hist = Counter()
    size2 = []
    incomplete = 0
    for t in pts:
        n, detail, extra = fiber_cardinality(*t)
        if extra > 0:
            # may undercount if irrational y
            incomplete += 1
            hist["incomplete_y"] += 1
        hist[n] += 1
        if n == 2:
            size2.append(
                {
                    "t": [str(c) for c in t],
                    "detail": detail,
                    "extra_irr_y": extra,
                }
            )
            print("SIZE2", t, detail, flush=True)
        if n not in (0, 1, 2, 3):
            print("ODD", n, t, detail, flush=True)

    result = {
        "schema": "jc.fiber_size2_exact.v1",
        "points_tested": len(pts),
        "histogram": {str(k): v for k, v in sorted(hist.items(), key=lambda x: str(x[0]))},
        "size2_hits": size2,
        "incomplete_y_factorizations": incomplete,
        "status": "FOUND_SIZE_2" if size2 else "NO_SIZE_2_IN_EXACT_PROBE",
        "claim_boundary": (
            "Exact fiber counts for rational points on V(E) with rational y-roots "
            "fully factored. Points whose G1 has irreducible quadratic/cubic "
            "y-factor are flagged incomplete. Not a familywise no-go."
        ),
    }
    out = HERE / "FIBER_SIZE2_EXACT.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


from collections import Counter  # noqa: E402

if __name__ == "__main__":
    main()

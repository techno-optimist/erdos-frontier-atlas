#!/usr/bin/env python3
"""Machine check for the stabilization edge of the JC crater graph.

Claim (folklore padding argument): if F : C^n -> C^n is a Keller counterexample
(constant nonzero Jacobian determinant, not injective), then G = F x id :
C^(n+1) -> C^(n+1), G(x, w) = (F(x), w), is a Keller counterexample in
dimension n+1 -- the Jacobian is block triangular so det JG = det JF, and any
collision of F extends to a collision of G with the same w.

The general argument is two lines of algebra; this script EXECUTES it on the
concrete object so the graph's status lift FALSE(n=3) -> FALSE(all n>=3) rests
on a machine check, not prose: it rebuilds Alpöge's dim-3 map inside a
dimension-generic exact polynomial engine, pads it to dimension 4, and verifies
   (1) det JG == -2 identically (symbolic polynomial identity in Q[x,y,z,w]),
   (2) the three padded points (p, 0) are distinct and share one image.
Exit 0 = both hold. Stdlib only.
"""
from fractions import Fraction as Q
import sys

# --- generic-dimension exact polynomial engine: {exponent-tuple: coeff} ------
def var(i, nv):
    e = [0] * nv; e[i] = 1
    return {tuple(e): Q(1)}

def const(c, nv):
    c = Q(c)
    return {(0,) * nv: c} if c else {}

def padd(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            s = out.get(m, Q(0)) + c
            if s: out[m] = s
            elif m in out: del out[m]
    return out

def pmul(a, b):
    out = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            m = tuple(x + y for x, y in zip(ma, mb))
            s = out.get(m, Q(0)) + ca * cb
            if s: out[m] = s
            elif m in out: del out[m]
    return out

def pscale(a, c):
    c = Q(c)
    return {m: v * c for m, v in a.items()} if c else {}

def ppow(a, n, nv):
    out = const(1, nv)
    for _ in range(n): out = pmul(out, a)
    return out

def pdiff(a, i):
    out = {}
    for m, c in a.items():
        if m[i]:
            dm = tuple(e - (1 if j == i else 0) for j, e in enumerate(m))
            out[dm] = out.get(dm, Q(0)) + c * m[i]
    return {m: c for m, c in out.items() if c}

def peval(a, pt):
    total = Q(0)
    for m, c in a.items():
        term = c
        for e, v in zip(m, pt): term *= v ** e
        total += term
    return total

def det(rows, nv):
    n = len(rows)
    if n == 1: return rows[0][0]
    out = {}
    for j in range(n):
        minor = det([r[:j] + r[j + 1:] for r in rows[1:]], nv)
        term = pmul(rows[0][j], minor)
        out = padd(out, term if j % 2 == 0 else pscale(term, -1))
    return out

# --- the padded map G = F x id in dimension 4 --------------------------------
def build_padded():
    nv = 4
    x, y, z = var(0, nv), var(1, nv), var(2, nv)
    w = var(3, nv)
    u = padd(const(1, nv), pmul(x, y))                       # 1 + xy
    v = padd(const(4, nv), pscale(pmul(x, y), 3))            # 4 + 3xy
    f1 = padd(pmul(ppow(u, 3, nv), z), pmul(pmul(ppow(y, 2, nv), u), v))
    f2 = padd(y, pscale(pmul(pmul(x, ppow(u, 2, nv)), z), 3),
              pscale(pmul(pmul(x, ppow(y, 2, nv)), v), 3))
    f3 = padd(pscale(x, 2), pscale(pmul(ppow(x, 2, nv), y), -3),
              pscale(pmul(ppow(x, 3, nv), z), -1))
    return [f1, f2, f3, w], nv

def main():
    G, nv = build_padded()
    J = [[pdiff(g, i) for i in range(nv)] for g in G]
    d = det(J, nv)
    ok1 = (d == const(-2, nv))
    print(f"padding check 1  det J(F x id) == -2 identically in Q[x,y,z,w]: "
          f"{'PASS' if ok1 else 'FAIL'}")

    pts = [(Q(0), Q(0), Q(-1, 4), Q(0)),
           (Q(1), Q(-3, 2), Q(13, 2), Q(0)),
           (Q(-1), Q(3, 2), Q(13, 2), Q(0))]
    imgs = [tuple(peval(g, p) for g in G) for p in pts]
    ok2 = (len(set(pts)) == 3 and len(set(imgs)) == 1
           and imgs[0] == (Q(-1, 4), Q(0), Q(0), Q(0)))
    print(f"padding check 2  three distinct padded points share one image: "
          f"{'PASS' if ok2 else 'FAIL'}")

    ok = ok1 and ok2
    print("STABILIZATION EDGE " + ("MACHINE-VERIFIED (dim 3 -> dim 4 instance; "
          "the same block argument iterates to every n >= 3)" if ok else "FAILED"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())

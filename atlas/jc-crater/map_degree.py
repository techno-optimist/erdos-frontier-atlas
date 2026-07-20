#!/usr/bin/env python3
"""Certify the exact component degrees of Alpoge's dim-3 Keller counterexample.

Backs the UPPER bound of the newborn quantity 'minimal degree of a dim-3
counterexample' (quantities.json): the map is a counterexample (that is
certified separately by certificates/jacobian-conjecture/verify.py) AND its
components have total degrees (7, 6, 4), so a degree-7 counterexample exists.
This script certifies the degree half exactly, in stdlib rational arithmetic
via the same monomial-dict engine used by the certificate -- so the
replay_receipt cited for the degree bound actually performs the degree
computation (verify.py does not).

Exit 0 iff the expanded components have total degrees (7, 6, 4).
"""
from fractions import Fraction as Q
import sys


def const(c):
    c = Q(c)
    return {(0, 0, 0): c} if c else {}

X, Y, Z = {(1, 0, 0): Q(1)}, {(0, 1, 0): Q(1)}, {(0, 0, 1): Q(1)}


def add(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            s = out.get(m, Q(0)) + c
            if s: out[m] = s
            elif m in out: del out[m]
    return out


def mul(a, b):
    out = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            m = (ma[0] + mb[0], ma[1] + mb[1], ma[2] + mb[2])
            s = out.get(m, Q(0)) + ca * cb
            if s: out[m] = s
            elif m in out: del out[m]
    return out


def scale(a, c):
    c = Q(c)
    return {m: v * c for m, v in a.items()} if c else {}


def powp(a, n):
    out = const(1)
    for _ in range(n): out = mul(out, a)
    return out


def total_degree(p):
    return max((sum(m) for m in p), default=0)


def build_components():
    u = add(const(1), mul(X, Y))                       # 1 + xy
    v = add(const(4), scale(mul(X, Y), 3))             # 4 + 3xy
    f1 = add(mul(powp(u, 3), Z), mul(mul(powp(Y, 2), u), v))
    f2 = add(Y, scale(mul(mul(X, powp(u, 2)), Z), 3),
             scale(mul(mul(X, powp(Y, 2)), v), 3))
    f3 = add(scale(X, 2), scale(mul(powp(X, 2), Y), -3),
             scale(mul(powp(X, 3), Z), -1))
    return [f1, f2, f3]


EXPECTED = (7, 6, 4)


def main():
    degs = tuple(total_degree(f) for f in build_components())
    ok = degs == EXPECTED
    print(f"component total degrees = {degs}; expected {EXPECTED}: "
          f"{'PASS' if ok else 'FAIL'}")
    print(f"map degree = {max(degs)} "
          f"(=> a degree-{max(degs)} dim-3 Keller counterexample exists)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

"""Independent exact audit of the q=3m torsion-triangle family.

This file deliberately reimplements the EHPS grid pieces, D4 action, product
cylinders, modular midpoint test, and q=6 mass screen.  It does not import
Terra's replay or any atlas module.  It is stdlib-only and writes no files.
"""
from __future__ import annotations

import itertools
from fractions import Fraction

Point = tuple[int, int]
ROLES = ("P1", "P2", "P3", "B", "K")
WORDS = (("P1", "K", "B"), ("B", "K", "P1"),
         ("P2", "B", "P2"), ("P3", "B", "B"), ("B", "B", "P3"))


def ehps_piece(p: Point, q: int) -> str | None:
    """EHPS Definition-4.1 faces using exact rational inequalities."""
    x, y = p
    a, b = Fraction(x, q), Fraction(y, q)
    s, eps = a + b, Fraction(1, q)
    if a >= Fraction(1, 2) and s > Fraction(2, 3) and s <= Fraction(7, 6):
        return "T1"
    if (a >= Fraction(1, 2) and b < Fraction(1, 2)
            and s >= Fraction(7, 6) + eps and s <= Fraction(17, 12)):
        return "T2"
    if (a < Fraction(1, 2) and b >= Fraction(1, 2)
            and s >= Fraction(7, 6) + eps and s <= Fraction(17, 12)
            and 2 * a + b >= Fraction(3, 2) + eps):
        return "T3"
    return None


def base_support(q: int) -> frozenset[Point]:
    return frozenset((x, y) for x in range(q) for y in range(q)
                     if ehps_piece((x, y), q) is not None)


def d4(p: Point, k: int, q: int) -> Point:
    """The eight atlas D4 maps: complements then optional coordinate swap."""
    x, y = p
    if k & 1:
        x = q - 1 - x
    if k & 2:
        y = q - 1 - y
    if k & 4:
        x, y = y, x
    return x, y


def image(q: int, k: int) -> frozenset[Point]:
    return frozenset(d4(p, k, q) for p in base_support(q))


def add(p: Point, u: Point, q: int) -> Point:
    return ((p[0] + u[0]) % q, (p[1] + u[1]) % q)


def sub(p: Point, u: Point, q: int) -> Point:
    return ((p[0] - u[0]) % q, (p[1] - u[1]) % q)


def mid(x: Point, y: Point, z: Point, q: int) -> bool:
    return all((2 * y[i] - x[i] - z[i]) % q == 0 for i in (0, 1))


def carry(x: Point, y: Point, z: Point, q: int) -> Point:
    assert mid(x, y, z, q)
    return ((x[0] + z[0] - 2 * y[0]) // q,
            (x[1] + z[1] - 2 * y[1]) // q)


def cost(x: Point, z: Point) -> int:
    return (x[0] - z[0]) ** 2 + (x[1] - z[1]) ** 2


def family(q: int) -> dict[str, object]:
    assert q >= 6 and q % 3 == 0
    m = q // 3
    # Assignment P2=P3=D4(7), B=D4(6), as in Terra's packet.
    p2, p3, buck = image(q, 7), image(q, 7), image(q, 6)
    a = c = (q - 3, m - 1)
    b = (q - 3, q - 1)
    d = (q - 3, 2 * m - 1)
    assert a in p2 and c in p2 and a in p3 and b in buck and d in buck
    # Independently identify preimages and EHPS pieces; catches inverse-D4
    # and orientation mistakes rather than trusting a hand-written inverse.
    pre = {}
    for name, p, k in (("A", a, 7), ("B", b, 6), ("C", c, 7), ("D", d, 6)):
        got = [r for r in base_support(q) if d4(r, k, q) == p]
        assert len(got) == 1
        pre[name] = (got[0], ehps_piece(got[0], q))
        assert pre[name][1] is not None
    u = (0, m)
    assert c == add(b, u, q) and d == sub(b, u, q)
    assert u != (0, 0) and ((3 * u[0]) % q, (3 * u[1]) % q) == (0, 0)
    # Three rows over cylinder words W2=(P2,B,P2), W3=(P3,B,B).
    X, Y, Z = (a, b, c), (a, b, b), (a, b, d)
    assert X != Y != Z and X != Z
    assert mid(X[2], Y[2], Z[2], q)
    assert mid(Y[2], X[2], Z[2], q)
    assert mid(X[2], Z[2], Y[2], q)
    rows = ((X, Y, Z), (Y, X, Z), (X, Z, Y))
    # Variable identity is (word index, cylinder vertex), exactly the
    # arbitrary per-cylinder global-potential model.
    row_words = ((2, 3, 3), (3, 2, 3), (2, 3, 3))
    for (left, middle, right), wi in zip(rows, row_words):
        for vertex, word_index in zip((left, middle, right), wi):
            for slot, point in enumerate(vertex):
                assert point in image(q, 7 if WORDS[word_index][slot] in ("P2", "P3") else 6)
    # Explicit coefficient cancellation for the three global vertices.
    coeff = {}
    for (left, middle, right), wi in zip(rows, row_words):
        for vertex, word_index, sign in ((left, wi[0], 1), (middle, wi[1], -2),
                                         (right, wi[2], 1)):
            coeff[(word_index, vertex)] = coeff.get((word_index, vertex), 0) + sign
    assert not [v for v in coeff.values() if v]
    rhs = (cost(X[2], Z[2]), cost(Y[2], Z[2]), cost(X[2], Y[2]))
    assert rhs == (m * m, m * m, 4 * m * m)
    carries = (carry(X[2], Y[2], Z[2], q), carry(Y[2], X[2], Z[2], q),
               carry(X[2], Z[2], Y[2], q))
    return {"q": q, "m": m, "preimages": pre, "points": (a, b, c, d),
            "u": u, "rhs": rhs, "carries": carries,
            "rhs_sum": sum(rhs), "normalized_sum": str(Fraction(sum(rhs), q*q)),
            "rows": 3, "global_coefficients_cancel": True}


def union_mass(assign: tuple[int, ...], ims: list[frozenset[Point]]) -> int:
    points: set[tuple[Point, Point, Point]] = set()
    for w in WORDS:
        points.update(itertools.product(*(ims[assign[ROLES.index(r)]] for r in w)))
    return len(points)


def template_hit(assign: tuple[int, ...], ims: list[frozenset[Point]]) -> bool:
    p2, p3, buck = ims[assign[1]], ims[assign[2]], ims[assign[3]]
    if not p2 & p3:
        return False
    six = 6
    torsion = [(x, y) for x in range(six) for y in range(six)
               if (x, y) != (0, 0) and (3*x) % six == 0 and (3*y) % six == 0]
    return any(add(b, u, six) in p2 and sub(b, u, six) in buck
               for b in buck for u in torsion)


def legacy_hit(assign: tuple[int, ...], ims: list[frozenset[Point]]) -> bool:
    supports = {r: ims[assign[i]] for i, r in enumerate(ROLES)}
    for g in range(8):
        a, b, c, d = (d4(p, g, 6) for p in ((4, 0), (1, 3), (3, 1), (5, 5)))
        if (a in supports["P2"] and c in supports["P2"] and a in supports["P3"]
                and b in supports["B"] and d in supports["B"]):
            return True
    return False


def coverage_q6() -> dict[str, object]:
    q = 6
    ims = [image(q, k) for k in range(8)]
    assignments = list(itertools.product(range(8), repeat=5))
    masses = {a: union_mass(a, ims) for a in assignments}
    maximum = max(masses.values())
    maxes = [a for a in assignments if masses[a] == maximum]
    templ = [a for a in maxes if template_hit(a, ims)]
    inter = [a for a in maxes if ims[a[1]] & ims[a[2]]]
    legacy = [a for a in maxes if legacy_hit(a, ims)]
    assert maximum == 3645 and len(maxes) == 256
    assert len(templ) == 128 and templ == inter and len(legacy) == 32
    # On maxes, the iff is checked assignment-by-assignment, not by counts.
    assert all(template_hit(a, ims) == bool(ims[a[1]] & ims[a[2]]) for a in maxes)
    return {"assignments": len(assignments), "maximum_mass": maximum,
            "maximizers": len(maxes), "legacy_covered": len(legacy),
            "template_covered": len(templ), "survivors": len(maxes)-len(templ),
            "template_iff_intersection": True}


def main() -> None:
    try:
        family(7)
    except AssertionError:
        negative_control = "PASS_INVALID_QUOTIENT_REJECTED"
    else:
        raise AssertionError("invalid q=7 family member was accepted")
    qs = list(range(6, 61, 3))
    families = [family(q) for q in qs]
    cov = coverage_q6()
    print("PASS_INDEPENDENT_Q3M_TORSION_TRIANGLE_AUDIT")
    print("INDEPENDENT_NEGATIVE_CONTROL", negative_control)
    print("FAMILY_PASS", {"q_min": qs[0], "q_max": qs[-1], "count": len(qs),
                           "all_rhs_sum_2q2_over_3": all(x["rhs_sum"] * 3 == 2*x["q"]*x["q"] for x in families),
                           "all_normalized": sorted({x["normalized_sum"] for x in families})})
    print("SAMPLE_FAMILY", families[0])
    print("SAMPLE_FAMILY_LARGE", families[-1])
    print("Q6_COVERAGE_PASS", cov)
    print("SCOPE finite_quotient_only continuum_claim=false r3_claim=false")


if __name__ == "__main__":
    main()

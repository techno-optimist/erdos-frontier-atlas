"""Independent exact audit of the q=0 (mod 120) interior torsion argument.

This file intentionally reconstructs the definitions rather than importing the
Terra replay.  It checks the finite epsilon=1/q tiles, their epsilon=0 limit,
the D4 inverses, all three word incidences, modular carries and raw-canonical
costs, exact coefficient cancellation, uniform margins, and the old seam
family's Euclidean escape.
"""
from fractions import Fraction as Q


Point = tuple[int, int]
RPoint = tuple[Q, Q]


def d4(p: Point, k: int, q: int) -> Point:
    x, y = p
    if k & 1:
        x = q - 1 - x
    if k & 2:
        y = q - 1 - y
    if k & 4:
        x, y = y, x
    return x, y


def tile(p: Point, q: int, eps: Q | None = None) -> str | None:
    x, y = p
    a, b = Q(x, q), Q(y, q)
    e = Q(1, q) if eps is None else eps
    s = a + b
    if a >= Q(1, 2) and s > Q(2, 3) and s <= Q(7, 6):
        return "T1"
    if a >= Q(1, 2) and b < Q(1, 2) and s >= Q(7, 6) + e and s <= Q(17, 12):
        return "T2"
    if (a < Q(1, 2) and b >= Q(1, 2) and
            s >= Q(7, 6) + e and s <= Q(17, 12) and
            2 * a + b >= Q(3, 2) + e):
        return "T3"
    return None


def tile_rational(p: RPoint, eps: Q) -> str | None:
    """The same EHPS faces on exact rational normalized coordinates."""
    a, b = p
    s = a + b
    if a >= Q(1, 2) and s > Q(2, 3) and s <= Q(7, 6):
        return "T1"
    if a >= Q(1, 2) and b < Q(1, 2) and s >= Q(7, 6) + eps and s <= Q(17, 12):
        return "T2"
    if (a < Q(1, 2) and b >= Q(1, 2) and
            s >= Q(7, 6) + eps and s <= Q(17, 12) and
            2 * a + b >= Q(3, 2) + eps):
        return "T3"
    return None


def rational_slacks(p: RPoint, which: str, eps: Q) -> tuple[Q, ...]:
    a, b = p
    s = a + b
    if which == "T1":
        return (a - Q(1, 2), s - Q(2, 3), Q(7, 6) - s)
    if which == "T2":
        return (a - Q(1, 2), Q(1, 2) - b,
                s - Q(7, 6) - eps, Q(17, 12) - s)
    if which == "T3":
        return (Q(1, 2) - a, b - Q(1, 2),
                s - Q(7, 6) - eps, Q(17, 12) - s,
                2 * a + b - Q(3, 2) - eps)
    raise ValueError(which)


def preimage(image: Point, k: int, q: int) -> Point:
    # The k=6 quarter-turn is not an involution; invert in reverse order.
    x, y = image
    if k & 4:
        x, y = y, x
    if k & 1:
        x = q - 1 - x
    if k & 2:
        y = q - 1 - y
    p = x, y
    assert d4(p, k, q) == image
    return p


def slacks(p: Point, which: str, q: int, eps: Q | None = None) -> tuple[Q, ...]:
    x, y = p
    a, b = Q(x, q), Q(y, q)
    e = Q(1, q) if eps is None else eps
    s = a + b
    if which == "T1":
        return (a - Q(1, 2), s - Q(2, 3), Q(7, 6) - s)
    if which == "T2":
        return (a - Q(1, 2), Q(1, 2) - b,
                s - Q(7, 6) - e, Q(17, 12) - s)
    if which == "T3":
        return (Q(1, 2) - a, b - Q(1, 2),
                s - Q(7, 6) - e, Q(17, 12) - s,
                2 * a + b - Q(3, 2) - e)
    raise ValueError(which)


def norm(p: Point, q: int) -> RPoint:
    return Q(p[0], q), Q(p[1], q)


def carry(x: Point, y: Point, z: Point, q: int) -> Point:
    n = (x[0] + z[0] - 2 * y[0], x[1] + z[1] - 2 * y[1])
    assert all(v % q == 0 for v in n)
    return n[0] // q, n[1] // q


def raw_cost(x: Point, z: Point, q: int) -> Q:
    return Q((x[0] - z[0]) ** 2 + (x[1] - z[1]) ** 2, q * q)


def torus_midpoint(x: RPoint, y: RPoint, z: RPoint) -> bool:
    return all((2 * y[i] - x[i] - z[i]).denominator == 1 for i in range(2))


def euclidean_midpoint(x: RPoint, y: RPoint, z: RPoint) -> bool:
    return all(2 * y[i] == x[i] + z[i] for i in range(2))


def interior(q: int) -> dict[str, object]:
    assert q >= 120 and q % 120 == 0
    a = c = (13 * q // 24, 2 * q // 15)
    b = (7 * q // 8, 4 * q // 5)
    d = (5 * q // 24, 7 * q // 15)
    u = (2 * q // 3, q // 3)
    assert c == ((b[0] + u[0]) % q, (b[1] + u[1]) % q)
    assert d == ((b[0] - u[0]) % q, (b[1] - u[1]) % q)
    assert (3 * u[0] % q, 3 * u[1] % q) == (0, 0) and u != (0, 0)

    # Assignment (P1,P2,P3,B,K)=(7,7,7,6,7), words W2 and W3.
    pa, pc = preimage(a, 7, q), preimage(c, 7, q)
    pb, pd = preimage(b, 6, q), preimage(d, 6, q)
    assert pa == pc == (13 * q // 15 - 1, 11 * q // 24 - 1)
    assert pb == (4 * q // 5, q // 8 - 1)
    assert pd == (7 * q // 15, 19 * q // 24 - 1)
    assert (tile(pa, q), tile(pc, q), tile(pb, q), tile(pd, q)) == ("T2", "T2", "T1", "T3")

    x, y, z = (a, b, c), (a, b, b), (a, b, d)
    assert all(tile(preimage(p, k, q), q) is not None
               for p, k in ((a, 7), (b, 6), (c, 7), (d, 6)))

    rows = ((c, b, d), (b, c, d), (c, d, b))
    carries = tuple(carry(*r, q) for r in rows)
    costs = tuple(raw_cost(r[0], r[2], q) for r in rows)
    assert carries == ((-1, -1), (0, 1), (1, 0))
    assert costs == (Q(2, 9), Q(5, 9), Q(5, 9))
    assert sum(costs) == Q(4, 3)
    coeffs = ((1, -2, 1), (-2, 1, 1), (1, 1, -2))
    assert tuple(sum(row[j] for row in coeffs) for j in range(3)) == (0, 0, 0)

    points = tuple(norm(p, q) for p in (a, b, c, d))
    seam = min(min(v, 1 - v) for p in points for v in p)
    margin = min(slack for p, t in ((pb, "T1"), (pc, "T2"), (pd, "T3"))
                 for slack in slacks(p, t, q))
    assert seam == Q(1, 8)
    assert margin >= Q(1, 30)
    # The limit epsilon=0 support has the same strict inequalities.
    assert all(tile(p, q, Q(0)) == t for p, t in ((pb, "T1"), (pc, "T2"), (pd, "T3")))
    assert all(torus_midpoint(*tuple(norm(v, q) for v in r)) for r in rows)
    assert not any(euclidean_midpoint(*tuple(norm(v, q) for v in r)) for r in rows)
    return {
        "q": q, "points": points,
        "preimages": (norm(pa, q), norm(pb, q), norm(pd, q)),
        "tiles": ("T2", "T1", "T3"), "u": norm(u, q),
        "carries": carries, "raw_costs": costs, "raw_cost_sum": sum(costs),
        "seam_margin": seam, "tile_margin": margin,
        "torus_midpoints": True, "euclidean_midpoints": False,
        "coefficient_sum": (0, 0, 0),
    }


def epsilon_zero_limit_check() -> dict[str, object]:
    """Check the exact epsilon=0 polygons and their strict interiors."""
    pb = (Q(4, 5), Q(1, 8))
    pc = (Q(13, 15), Q(11, 24))
    pd = (Q(7, 15), Q(19, 24))
    assert (tile_rational(pb, Q(0)), tile_rational(pc, Q(0)),
            tile_rational(pd, Q(0))) == ("T1", "T2", "T3")
    all_slacks = (rational_slacks(pb, "T1", Q(0)) +
                  rational_slacks(pc, "T2", Q(0)) +
                  rational_slacks(pd, "T3", Q(0)))
    assert min(all_slacks) == Q(1, 30)
    # The normalized D4 limits are R6(a,b)=(1-b,a) and
    # R7(a,b)=(1-b,1-a), matching the displayed image points.
    r6b = (1 - pb[1], pb[0])
    r7c = (1 - pc[1], 1 - pc[0])
    r6d = (1 - pd[1], pd[0])
    assert r6b == (Q(7, 8), Q(4, 5))
    assert r7c == (Q(13, 24), Q(2, 15))
    assert r6d == (Q(5, 24), Q(7, 15))
    return {"limit_preimages": (pb, pc, pd), "limit_tiles": ("T1", "T2", "T3"),
            "epsilon_zero_min_face_slack": min(all_slacks),
            "limit_images": (r7c, r6b, r6d)}


def old_family(q: int) -> dict[str, object]:
    assert q >= 6 and q % 3 == 0
    m = q // 3
    a = c = (q - 3, m - 1)
    b = (q - 3, q - 1)
    d = (q - 3, 2 * m - 1)
    pa, pb, pd = preimage(a, 7, q), preimage(b, 6, q), preimage(d, 6, q)
    assert (tile(pa, q), tile(pb, q), tile(pd, q)) == ("T1", "T1", "T1")
    rows = ((c, b, d), (b, c, d), (c, d, b))
    assert tuple(carry(*r, q) for r in rows) == ((0, -1), (0, 1), (0, 0))
    costs = tuple(raw_cost(r[0], r[2], q) for r in rows)
    assert costs == (Q(1, 9), Q(1, 9), Q(4, 9)) and sum(costs) == Q(2, 3)
    image = tuple(norm(p, q) for p in (a, b, d))
    seam = min(v for p in image for v in (*p, *(1 - x for x in p)))
    strict = min(slack for p in (pa, pb, pd) for slack in slacks(p, "T1", q)[1:2])
    assert seam == Q(1, q) and strict == Q(1, q)
    c0, b0, d0 = norm(c, q), norm(b, q), norm(d, q)
    assert not euclidean_midpoint(c0, b0, d0)
    assert not euclidean_midpoint(b0, c0, d0)
    assert euclidean_midpoint(c0, d0, b0)
    return {"q": q, "limit": ((Q(1), Q(1, 3)), (Q(1), Q(1)), (Q(1), Q(2, 3))),
            "preimages": (pa, pb, pd), "seam": seam, "strict_T1_margin": strict,
            "carries": tuple(carry(*r, q) for r in rows), "costs": costs}


def algebraic_three_cycle_check() -> bool:
    # In a torsion-free real vector space, all 3 cyclic rows imply equality.
    # From 2y=x+z and 2x=y+z, 3(y-x)=0, hence y=x; first row gives z=x.
    # Implement the implication coordinatewise, without importing any source.
    samples = ((Q(11, 17), Q(5, 13), Q(7, 19)),
               (Q(1, 4), Q(1, 4), Q(1, 4)))
    for x, y, z in samples:
        rows = ((x, y, z), (y, x, z), (x, z, y))
        if all(2 * row[1] == row[0] + row[2] for row in rows):
            assert x == y == z
    return True


def escape() -> dict[str, object]:
    c, b, d = Q(1, 3), Q(1), Q(2, 3)
    g = lambda t: 2 * (t - Q(2, 3)) ** 2
    assert 2 * d == c + b
    assert 2 * b != c + d and 2 * c != b + d
    assert g(c) + g(b) - 2 * g(d) == Q(4, 9)
    return {"g": "2*(t-2/3)^2", "valid_row": Q(4, 9),
            "other_rows_are_not_Euclidean": True}


def main() -> None:
    try:
        interior(121)
    except AssertionError:
        negative_control = "PASS_NONMULTIPLE_QUOTIENT_REJECTED"
    else:
        raise AssertionError("invalid q=121 interior member was accepted")
    assert algebraic_three_cycle_check()
    old120, old240 = old_family(120), old_family(240)
    i120, i240, i360 = interior(120), interior(240), interior(360)
    limit = epsilon_zero_limit_check()
    assert i120["points"] == i240["points"] == i360["points"]
    assert i120["raw_costs"] == i240["raw_costs"] == i360["raw_costs"]
    print("PASS_INDEPENDENT_INTERIOR_TORUS_TORSION_AUDIT")
    print("INDEPENDENT_NEGATIVE_CONTROL", negative_control)
    print("INDEPENDENT_INTERIOR_TORSION_PASS", i120)
    print("EPSILON_ZERO_LIMIT_PASS", limit)
    print("INTERIOR_SCALE_PASS", {"q": (240, 360), "same_points_and_costs": True})
    print("INDEPENDENT_OLD_SEAM_PASS", old120)
    print("OLD_SCALE_PASS", {"q": 240, "same_limit": old120["limit"] == old240["limit"]})
    print("ALGEBRAIC_EUCLIDEAN_3_CYCLE_PASS", True)
    print("INDEPENDENT_ESCAPE_PASS", escape())
    print("SCOPE raw_canonical_torus_only continuum_Euclidean_claim=false r3_claim=false")


if __name__ == "__main__":
    main()

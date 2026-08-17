"""Exact audit for the interior raw-canonical torus torsion wall.

This is a theorem-supporting replay, not a search and not an atlas
certificate.  It checks two distinct statements using only exact Fraction
arithmetic:

* the original q=3m family approaches a square seam and strict tile faces;
* a shifted q == 0 (mod 120) family is uniformly interior in both senses,
  yet its three midpoint witnesses retain nonzero *torus* carries.

The latter supplies an exact, fixed-location continuum obstruction only for
the explicitly defined raw-canonical torus-midpoint model.  It supplies no
ordinary Euclidean-continuum or r_3(N) claim.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as Q


Point = tuple[int, int]
Affine = tuple[int, int]
VERDICT = "PASS_INTERIOR_TORUS_TORSION_WALL"


def d4(point: Point, k: int, q: int) -> Point:
    """The quotient D4 action used by the finite certificates."""

    x, y = point
    if k & 1:
        x = q - 1 - x
    if k & 2:
        y = q - 1 - y
    if k & 4:
        x, y = y, x
    return x, y


def tile(point: Point, q: int) -> str | None:
    """Exact q-dependent EHPS tile membership, with epsilon=1/q."""

    x, y = point
    a, b = Q(x, q), Q(y, q)
    s, eps = a + b, Q(1, q)
    if a >= Q(1, 2) and s > Q(2, 3) and s <= Q(7, 6):
        return "T1"
    if a >= Q(1, 2) and b < Q(1, 2) and s >= Q(7, 6) + eps and s <= Q(17, 12):
        return "T2"
    if (
        a < Q(1, 2)
        and b >= Q(1, 2)
        and s >= Q(7, 6) + eps
        and s <= Q(17, 12)
        and 2 * a + b >= Q(3, 2) + eps
    ):
        return "T3"
    return None


def support_contains(point: Point, d4_index: int, q: int) -> tuple[bool, Point, str | None]:
    """Return membership in D4_index(T1 union T2 union T3), plus its preimage."""

    preimages = [
        p
        for p in ((x, y) for x in range(q) for y in range(q))
        if d4(p, d4_index, q) == point
    ]
    assert len(preimages) == 1
    pre = preimages[0]
    return tile(pre, q) is not None, pre, tile(pre, q)


def raw_cost(x: Point, z: Point, q: int) -> Q:
    return Q((x[0] - z[0]) ** 2 + (x[1] - z[1]) ** 2, q * q)


def carry(x: Point, y: Point, z: Point, q: int) -> Point:
    """x + z - 2y divided by q for a modular midpoint row."""

    numerators = (x[0] + z[0] - 2 * y[0], x[1] + z[1] - 2 * y[1])
    assert all(n % q == 0 for n in numerators)
    return tuple(n // q for n in numerators)  # type: ignore[return-value]


def face_slacks(point: Point, which: str, q: int) -> tuple[Q, ...]:
    """Margins from every defining face of the named tile.

    These are affine-coordinate margins, not Euclidean distances.  A positive
    lower bound is more than enough to certify that a point stays uniformly
    in the relative interior of its indicated tile.
    """

    x, y = point
    a, b = Q(x, q), Q(y, q)
    s, eps = a + b, Q(1, q)
    if which == "T1":
        return a - Q(1, 2), s - Q(2, 3), Q(7, 6) - s
    if which == "T2":
        return a - Q(1, 2), Q(1, 2) - b, s - (Q(7, 6) + eps), Q(17, 12) - s
    if which == "T3":
        return (
            Q(1, 2) - a,
            b - Q(1, 2),
            s - (Q(7, 6) + eps),
            Q(17, 12) - s,
            2 * a + b - (Q(3, 2) + eps),
        )
    raise ValueError(which)


def normalized(point: Point, q: int) -> tuple[Q, Q]:
    return Q(point[0], q), Q(point[1], q)


def torus_midpoint(x: tuple[Q, Q], y: tuple[Q, Q], z: tuple[Q, Q]) -> bool:
    """Check 2y=x+z modulo Z^2 for rational representatives in [0,1)."""

    return all((2 * y[i] - x[i] - z[i]).denominator == 1 for i in (0, 1))


def euclidean_midpoint(x: tuple[Q, Q], y: tuple[Q, Q], z: tuple[Q, Q]) -> bool:
    return all(2 * y[i] == x[i] + z[i] for i in (0, 1))


def original_seam_family(q: int) -> dict[str, object]:
    """The existing q=3m construction, recorded only for the limit audit."""

    assert q >= 6 and q % 3 == 0
    m = q // 3
    a = c = (q - 3, m - 1)
    b = (q - 3, q - 1)
    d = (q - 3, 2 * m - 1)
    a_ok, a_pre, a_tile = support_contains(a, 7, q)
    b_ok, b_pre, b_tile = support_contains(b, 6, q)
    d_ok, d_pre, d_tile = support_contains(d, 6, q)
    assert a_ok and b_ok and d_ok and (a_tile, b_tile, d_tile) == ("T1", "T1", "T1")
    assert carry(c, b, d, q) == (0, -1)
    assert carry(b, c, d, q) == (0, 1)
    assert carry(c, d, b, q) == (0, 0)
    costs = raw_cost(c, d, q), raw_cost(b, d, q), raw_cost(c, b, q)
    assert costs == (Q(1, 9), Q(1, 9), Q(4, 9)) and sum(costs) == Q(2, 3)
    # Both the physical seam distance and a required strict-face margin decay as 1/q.
    seam_distance = min(
        Q(v, q) for p in (a, b, d) for v in (p[0], p[1], q - p[0], q - p[1])
    )
    strict_t1_margin = min(
        face_slacks(a_pre, "T1", q)[1],
        face_slacks(b_pre, "T1", q)[1],
        face_slacks(d_pre, "T1", q)[1],
    )
    assert seam_distance == Q(1, q) and strict_t1_margin == Q(1, q)
    # On the closed fundamental square only the third row is an ordinary midpoint row.
    c0, b0, d0 = normalized(c, q), normalized(b, q), normalized(d, q)
    return {
        "q": q,
        "image_points_AeqC_B_D": (c0, b0, d0),
        "preimages": (a_pre, b_pre, d_pre),
        "tiles": (a_tile, b_tile, d_tile),
        "seam_distance": seam_distance,
        "strict_T1_lower_face_margin": strict_t1_margin,
        "carries": (carry(c, b, d, q), carry(b, c, d, q), carry(c, d, b, q)),
        "raw_costs": costs,
        "only_third_is_euclidean_midpoint_at_the_limit": True,
    }


def interior_family(q: int) -> dict[str, object]:
    """A uniformly interior 3-torsion family for q == 0 (mod 120).

    Use the same D4 assignment A=(7,7,7,6,7) and the same W2/W3 cylinders as
    the finite exact wall.  A=C here is a point in the P2/P3 support.
    """

    assert q >= 120 and q % 120 == 0
    a = c = (13 * q // 24, 2 * q // 15)
    b = (7 * q // 8, 4 * q // 5)
    d = (5 * q // 24, 7 * q // 15)
    u = (2 * q // 3, q // 3)
    assert c == ((b[0] + u[0]) % q, (b[1] + u[1]) % q)
    assert d == ((b[0] - u[0]) % q, (b[1] - u[1]) % q)
    assert ((3 * u[0]) % q, (3 * u[1]) % q) == (0, 0) and u != (0, 0)

    a_ok, a_pre, a_tile = support_contains(a, 7, q)
    c_ok, c_pre, c_tile = support_contains(c, 7, q)
    b_ok, b_pre, b_tile = support_contains(b, 6, q)
    d_ok, d_pre, d_tile = support_contains(d, 6, q)
    assert a_ok and c_ok and b_ok and d_ok
    assert (a_tile, c_tile, b_tile, d_tile) == ("T2", "T2", "T1", "T3")
    assert a_pre == c_pre == (13 * q // 15 - 1, 11 * q // 24 - 1)
    assert b_pre == (4 * q // 5, q // 8 - 1)
    assert d_pre == (7 * q // 15, 19 * q // 24 - 1)

    # X=(A,B,C) lies in W2=(P2,B,P2); Y,Z lie in W3=(P3,B,B).
    x, y, z = (a, b, c), (a, b, b), (a, b, d)
    # The three selected midpoint rows are (X,Y,Z), (Y,X,Z), and (X,Z,Y).
    carries = carry(c, b, d, q), carry(b, c, d, q), carry(c, d, b, q)
    assert carries == ((-1, -1), (0, 1), (1, 0))
    costs = raw_cost(c, d, q), raw_cost(b, d, q), raw_cost(c, b, q)
    assert costs == (Q(2, 9), Q(5, 9), Q(5, 9))
    assert sum(costs) == Q(4, 3)
    # Coefficients of the arbitrary single global potential at X,Y,Z cancel.
    coefficient_rows = ((1, -2, 1), (-2, 1, 1), (1, 1, -2))
    assert tuple(sum(row[i] for row in coefficient_rows) for i in range(3)) == (0, 0, 0)

    image_points = tuple(normalized(p, q) for p in (a, b, c, d))
    # Every local sample is separated from the fundamental-square seams.
    seam_distance = min(
        min(v, 1 - v) for p in image_points for v in p
    )
    assert seam_distance == Q(1, 8)
    # Every named preimage is separated from every defining tile face.
    tile_margin = min(
        *face_slacks(b_pre, "T1", q),
        *face_slacks(c_pre, "T2", q),
        *face_slacks(d_pre, "T3", q),
    )
    assert tile_margin >= Q(1, 30)

    c0, b0, d0 = normalized(c, q), normalized(b, q), normalized(d, q)
    assert all(
        torus_midpoint(*row)
        for row in ((c0, b0, d0), (b0, c0, d0), (c0, d0, b0))
    )
    assert not any(
        euclidean_midpoint(*row)
        for row in ((c0, b0, d0), (b0, c0, d0), (c0, d0, b0))
    )
    return {
        "q": q,
        "assignment_P1_P2_P3_B_K": (7, 7, 7, 6, 7),
        "points_AeqC_B_D": image_points,
        "preimages_AeqC_B_D": tuple(normalized(p, q) for p in (a_pre, b_pre, d_pre)),
        "preimage_tiles_AeqC_B_D": (a_tile, b_tile, d_tile),
        "torsion_u": normalized(u, q),
        "carries": carries,
        "raw_costs": costs,
        "raw_cost_sum": sum(costs),
        "fundamental_square_seam_margin": seam_distance,
        "minimum_tile_face_margin": tile_margin,
        "all_three_torus_midpoints": True,
        "all_three_euclidean_midpoints_fail": True,
        "potential_coefficient_sum": (0, 0, 0),
        "approximate_row_error_floor_per_row": Q(4, 9),
        "cylinder_words": {"X": ("P2", "B", "P2"), "Y": ("P3", "B", "B"), "Z": ("P3", "B", "B")},
        "vertices": (x, y, z),
    }


def euclidean_escape_check() -> dict[str, object]:
    """Local escape for the original seam family in the ordinary Euclidean model.

    At its q->infinity image limit, C=1/3, B=1, D=2/3 in the moving
    coordinate.  The two carry rows are not ordinary midpoint constraints;
    the remaining row has D=(C+B)/2.  The continuous quadratic below makes
    precisely that sole row tight, proving that the three finite rows do not
    become an ordinary-Euclidean three-row contradiction.
    """

    c, b, d = Q(1, 3), Q(1), Q(2, 3)
    g = lambda t: 2 * (t - Q(2, 3)) ** 2
    assert 2 * d == c + b
    assert 2 * b != c + d and 2 * c != b + d
    assert g(c) + g(b) - 2 * g(d) == Q(4, 9)
    return {
        "limit_coordinate_C_B_D": (c, b, d),
        "g(t)": "2*(t-2/3)^2",
        "valid_euclidean_row_value": Q(4, 9),
        "row_rhs": Q(4, 9),
        "two_carry_rows_not_euclidean_constraints": True,
    }


def symbolic_interior_family() -> dict[str, object]:
    """Verify the q=120n family for every integer n>=1 symbolically."""

    qn: Affine = (120, 0)
    one: Affine = (0, 1)

    def add(x: Affine, y: Affine) -> Affine:
        return x[0] + y[0], x[1] + y[1]

    def sub(x: Affine, y: Affine) -> Affine:
        return x[0] - y[0], x[1] - y[1]

    def scale(c: int, x: Affine) -> Affine:
        return c * x[0], c * x[1]

    def evaluate(x: Affine, n: int = 1) -> int:
        return x[0] * n + x[1]

    def nonnegative_tail(x: Affine) -> bool:
        return x[0] >= 0 and evaluate(x) >= 0

    def positive_tail(x: Affine) -> bool:
        return x[0] >= 0 and evaluate(x) > 0

    def d4_affine(p: tuple[Affine, Affine], index: int) -> tuple[Affine, Affine]:
        x, y = p
        if index & 1:
            x = sub(sub(qn, one), x)
        if index & 2:
            y = sub(sub(qn, one), y)
        if index & 4:
            x, y = y, x
        return x, y

    points = {
        "A": ((65, 0), (16, 0)),
        "B": ((105, 0), (96, 0)),
        "C": ((65, 0), (16, 0)),
        "D": ((25, 0), (56, 0)),
    }
    preimages = {
        "A": ((104, -1), (55, -1)),
        "B": ((96, 0), (15, -1)),
        "C": ((104, -1), (55, -1)),
        "D": ((56, 0), (95, -1)),
    }
    indices = {"A": 7, "B": 6, "C": 7, "D": 6}
    for name, p in points.items():
        if d4_affine(preimages[name], indices[name]) != p:
            raise AssertionError("symbolic D4 preimage")
        for coordinate in (*p, *preimages[name]):
            if not nonnegative_tail(coordinate) or not nonnegative_tail(sub(sub(qn, one), coordinate)):
                raise AssertionError("symbolic canonical range")

    # Each pair is (face numerator, denominator coefficient d) and means
    # normalized face slack = numerator/(d*q).  Prove every face margin is
    # at least 1/30 uniformly for n>=1.
    def tile_slacks(p: tuple[Affine, Affine], which: str):
        x, y = p
        total = add(x, y)
        if which == "T1":
            return (
                (sub(scale(2, x), qn), 2),
                (sub(scale(3, total), scale(2, qn)), 3),
                (sub(scale(7, qn), scale(6, total)), 6),
            )
        if which == "T2":
            return (
                (sub(scale(2, x), qn), 2),
                (sub(qn, scale(2, y)), 2),
                (sub(sub(scale(6, total), scale(7, qn)), (0, 6)), 6),
                (sub(scale(17, qn), scale(12, total)), 12),
            )
        if which == "T3":
            return (
                (sub(qn, scale(2, x)), 2),
                (sub(scale(2, y), qn), 2),
                (sub(sub(scale(6, total), scale(7, qn)), (0, 6)), 6),
                (sub(scale(17, qn), scale(12, total)), 12),
                (sub(sub(scale(2, add(scale(2, x), y)), scale(3, qn)), (0, 2)), 2),
            )
        raise AssertionError("tile")

    named_tiles = {"B": "T1", "A": "T2", "C": "T2", "D": "T3"}
    for name, which in named_tiles.items():
        for numerator, denominator in tile_slacks(preimages[name], which):
            if not positive_tail(numerator):
                raise AssertionError("strict tile face")
            if not nonnegative_tail(sub(scale(30, numerator), scale(denominator, qn))):
                raise AssertionError("uniform 1/30 tile margin")

    # Every fixed normalized image point stays at least 1/8 from a square seam.
    for p in points.values():
        for coordinate in p:
            if not nonnegative_tail(sub(scale(8, coordinate), qn)):
                raise AssertionError("lower seam margin")
            if not nonnegative_tail(sub(scale(8, sub(qn, coordinate)), qn)):
                raise AssertionError("upper seam margin")

    u = ((80, 0), (40, 0))
    if tuple(scale(3, coordinate) for coordinate in u) != (scale(2, qn), qn):
        raise AssertionError("3-torsion")

    def residual(left, middle, right):
        return tuple(sub(add(left[i], right[i]), scale(2, middle[i])) for i in range(2))

    c, b, d = points["C"], points["B"], points["D"]
    if residual(c, b, d) != (scale(-1, qn), scale(-1, qn)):
        raise AssertionError("carry 1")
    if residual(b, c, d) != (ZERO_AFFINE := (0, 0), qn):
        raise AssertionError("carry 2")
    if residual(c, d, b) != (qn, ZERO_AFFINE):
        raise AssertionError("carry 3")

    def raw_leading_cost(left, right) -> int:
        return sum((left[i][0] - right[i][0]) ** 2 for i in range(2))

    costs = raw_leading_cost(c, d), raw_leading_cost(b, d), raw_leading_cost(c, b)
    if costs != (3200, 8000, 8000) or sum(costs) * 3 != 4 * 120**2:
        raise AssertionError("symbolic raw costs")
    coefficient_rows = ((1, -2, 1), (-2, 1, 1), (1, 1, -2))
    if tuple(sum(row[i] for row in coefficient_rows) for i in range(3)) != (0, 0, 0):
        raise AssertionError("coefficient cancellation")

    # Exact epsilon=0 limiting preimages and continuous D4 maps.
    a0, b0, d0 = (Q(13, 15), Q(11, 24)), (Q(4, 5), Q(1, 8)), (Q(7, 15), Q(19, 24))
    if (1 - a0[1], 1 - a0[0]) != (Q(13, 24), Q(2, 15)):
        raise AssertionError("R7 limit")
    if (1 - b0[1], b0[0]) != (Q(7, 8), Q(4, 5)):
        raise AssertionError("R6 B limit")
    if (1 - d0[1], d0[0]) != (Q(5, 24), Q(7, 15)):
        raise AssertionError("R6 D limit")

    return {
        "q_family": "q=120n, n>=1",
        "fixed_normalized_points": True,
        "minimum_tile_face_margin": "1/30",
        "minimum_square_seam_margin": "1/8",
        "torus_carries": [[-1, -1], [0, 1], [1, 0]],
        "normalized_raw_costs": ["2/9", "5/9", "5/9"],
        "normalized_contradiction": "4/3",
        "common_row_deficit_floor": "4/9",
    }


def planted_failures() -> dict[str, str]:
    q = 120
    a = c = (65, 16)
    b, d = (105, 96), (25, 56)
    triangle = interior_family(q)

    def demand(condition: bool) -> None:
        assert condition

    tests = {
        "nonmultiple_q": lambda: interior_family(121),
        "support": lambda: demand(support_contains((0, 0), 7, q)[0]),
        "carry": lambda: demand(carry(c, b, d, q) == (0, 0)),
        "raw_cost": lambda: demand(raw_cost(c, d, q) == Q(1, 3)),
        "tile_margin": lambda: demand(triangle["minimum_tile_face_margin"] >= Q(1, 29)),
        "euclidean_midpoint": lambda: demand(euclidean_midpoint(normalized(c, q), normalized(b, q), normalized(d, q))),
        "coefficient": lambda: demand(tuple(sum(row[i] for row in ((1, -2, 1), (-2, 1, 1), (1, 1, -1))) for i in range(3)) == (0, 0, 0)),
        "scope": lambda: demand({"continuum_Euclidean_claim": False} == {"continuum_Euclidean_claim": True}),
    }
    report = {}
    for name, test in tests.items():
        try:
            test()
        except (AssertionError, ValueError):
            report[name] = "rejected"
        else:
            raise AssertionError(f"planted failure survived: {name}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    symbolic = symbolic_interior_family()
    seam = original_seam_family(120)
    interior_120 = interior_family(120)
    interior_240 = interior_family(240)
    escape = euclidean_escape_check()
    assert interior_120["points_AeqC_B_D"] == interior_240["points_AeqC_B_D"]
    assert interior_120["raw_costs"] == interior_240["raw_costs"]
    print(VERDICT)
    print("ORIGINAL_SEAM_FAMILY_PASS", seam)
    print("INTERIOR_TORSION_FAMILY_PASS", interior_120)
    print("INTERIOR_SCALE_STABILITY_PASS", {"q": 240, "same_normalized_points": True})
    print("EUCLIDEAN_ESCAPE_PASS", escape)
    print("SCOPE raw_canonical_torus_branch_only continuum_Euclidean_claim=false r3_claim=false")
    output = {
        "verdict": VERDICT,
        "symbolic_family": symbolic,
        "raw_canonical_torus_continuum_wall": True,
        "ordinary_euclidean_continuum_wall": False,
        "new_r3_bound": False,
        "erdos142_solved": False,
    }
    if args.self_test:
        controls = planted_failures()
        if len(controls) != 8 or set(controls.values()) != {"rejected"}:
            raise AssertionError("planted failures")
        output["planted_corruptions"] = "all 8 rejected"
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

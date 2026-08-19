from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
from math import comb


B_WEIGHT = 263_277
R_WEIGHT = 17_640
GATE = Fraction(1_058_841, 4)
X = Fraction(R_WEIGHT, B_WEIGHT)
Y = GATE / B_WEIGHT


def maximum_matching(edges: tuple[tuple[int, int], ...]) -> int:
    vertices = sorted({v for edge in edges for v in edge})
    relabel = {v: i for i, v in enumerate(vertices)}
    adjacency = [0] * len(vertices)
    for a, b in edges:
        i, j = relabel[a], relabel[b]
        adjacency[i] |= 1 << j
        adjacency[j] |= 1 << i

    @lru_cache(maxsize=None)
    def solve(mask: int) -> int:
        if not mask:
            return 0
        i = (mask & -mask).bit_length() - 1
        without_i = mask & ~(1 << i)
        best = solve(without_i)
        choices = adjacency[i] & without_i
        while choices:
            j_bit = choices & -choices
            best = max(best, 1 + solve(without_i & ~j_bit))
            choices ^= j_bit
        return best

    return solve((1 << len(vertices)) - 1)


def maximum_degree(edges: tuple[tuple[int, int], ...]) -> int:
    degree: dict[int, int] = {}
    for a, b in edges:
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1
    return max(degree.values(), default=0)


def clique(offset: int, size: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (offset + i, offset + j)
        for i in range(size)
        for j in range(i + 1, size)
    )


def complete_bipartite(
    left_offset: int, left_size: int, right_offset: int, right_size: int
) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left_offset + i, right_offset + j)
        for i in range(left_size)
        for j in range(right_size)
    )


def chvatal_hanson_unrestricted(delta: int, matching: int) -> int:
    """Sharp large-active-vertex cap from Chvatal--Hanson (1976)."""
    half_up = (delta + 1) // 2
    return delta * matching + (delta // 2) * (matching // half_up)


def verify_graph_bases() -> None:
    # A_2: two disjoint K_7 components.
    a_witness = clique(0, 7) + clique(7, 7)
    assert len(a_witness) == 42
    assert maximum_degree(a_witness) == 6
    assert maximum_matching(a_witness) == 6

    # B_2: K_7 disjoint union K_{2,6}.
    b_witness = clique(0, 7) + complete_bipartite(7, 2, 9, 6)
    assert len(b_witness) == 33
    assert maximum_degree(b_witness) == 6
    assert maximum_matching(b_witness) == 5

    assert chvatal_hanson_unrestricted(6, 6) == 42
    assert chvatal_hanson_unrestricted(6, 5) == 33

    # For at most 2*nu+1 active vertices, the degree sum already gives the
    # same bounds.  Beyond that range the displayed Chvatal--Hanson formula
    # applies (isolated vertices are immaterial).
    assert max(6 * n // 2 for n in range(1, 2 * 6 + 2)) <= 42
    assert max(6 * n // 2 for n in range(1, 2 * 5 + 2)) <= 33


def two_level_caps(limit: int) -> tuple[dict[int, int], dict[int, int]]:
    # A_k bounds a k-uniform seven-sunflower-free family.  Such a family
    # automatically has matching number at most six.  B_k adds matching
    # number at most five.
    a = {1: 6, 2: 42}
    b = {1: 5, 2: 33}
    for k in range(3, limit + 1):
        bracket = k * (a[k - 1] + b[k - 1]) - (k - 2)
        a[k] = 3 * bracket
        b[k] = (5 * bracket) // 2
    return a, b


def verify_two_level_recurrence_arithmetic() -> tuple[dict[int, int], dict[int, int]]:
    a, b = two_level_caps(80)
    assert [a[k] for k in range(1, 8)] == [
        6,
        42,
        672,
        14_778,
        406_386,
        13_410_726,
        516_312_936,
    ]
    assert [b[k] for k in range(1, 8)] == [
        5,
        33,
        560,
        12_315,
        338_655,
        11_175_605,
        430_260_780,
    ]

    # The first new rank-three cap is strictly stronger than the old
    # one-level 6*(3*42-2)=744 recursion.
    assert a[3] == 672 < 6 * (3 * 42 - 2) == 744
    return a, b


def lym_cap_upper(
    dimension: int, caps: dict[int, int]
) -> tuple[Fraction, tuple[tuple[int, Fraction, Fraction], ...]]:
    items: list[tuple[Fraction, int, Fraction]] = []
    for rank in range(1, dimension + 1):
        layer = comb(dimension, rank)
        cap_fraction = Fraction(min(layer, caps[rank]), layer)
        density = layer * X**rank
        items.append((density, rank, cap_fraction))
    items.sort(key=lambda item: (item[0], -item[1]), reverse=True)

    remaining = Fraction(1)
    total = Fraction(0)
    allocation: list[tuple[int, Fraction, Fraction]] = []
    for density, rank, cap_fraction in items:
        take = min(remaining, cap_fraction)
        if take:
            total += take * density
            allocation.append((rank, take, density))
            remaining -= take
        if remaining == 0:
            break
    return total, tuple(allocation)


def verify_exact_lym_horizons(caps: dict[int, int]) -> None:
    bounds = {d: lym_cap_upper(d, caps)[0] for d in range(1, 61)}

    assert all(bounds[d] < 1 for d in range(1, 29))
    assert bounds[29] > 1
    assert all(bounds[d] < Y**d for d in range(1, 34))
    assert bounds[34] > Y**34
    assert min(d for d in bounds if bounds[d] > 1) == 29
    assert min(d for d in bounds if bounds[d] > Y**d) == 34

    print("d   nonempty_two_level_LYM_upper   gate=y^d")
    for d in range(28, 35):
        print(f"{d:2d}  {float(bounds[d]):.12f}              {float(Y**d):.12f}")

    for d in (33, 34):
        bound, allocation = lym_cap_upper(d, caps)
        print(
            f"allocation d={d}, exact_bound={bound.numerator}/{bound.denominator}"
        )
        for rank, take, density in allocation:
            print(
                f"  rank={rank:2d} LYM_take={take.numerator}/{take.denominator} "
                f"density={density.numerator}/{density.denominator}"
            )


def main() -> None:
    assert X == Fraction(40, 597)
    assert Y == Fraction(2401, 2388)
    print("PASS_EXACT_CONSTANTS")
    verify_graph_bases()
    print("PASS_CHVATAL_HANSON_BASES_AND_WITNESSES")
    caps, restricted_caps = verify_two_level_recurrence_arithmetic()
    assert restricted_caps[3] == 560
    print("PASS_TWO_LEVEL_LINK_RECURRENCE")
    verify_exact_lym_horizons(caps)
    print("PASS_GATE_EXCLUSION_THROUGH_DIMENSION_33")
    print("PASS_WEIGHTED_MULTISET7_TWO_LEVEL_BOUND")


if __name__ == "__main__":
    main()

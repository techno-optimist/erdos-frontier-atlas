#!/usr/bin/env python3
"""Exact verifier for the weighted multiset-7-sunflower scratch packet.

Only Python's standard library is used.  All theorem-critical arithmetic uses
fractions.Fraction; floating-point values are display-only.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations, combinations_with_replacement
from math import comb


B = 263_277
R = 17_640
G = Fraction(1_058_841, 4)
X = Fraction(R, B)
Y = G / B


def subset(a: int, b: int) -> bool:
    """Return whether the support encoded by a is contained in b."""
    return (a & ~b) == 0


def forbidden_septuple(words: tuple[int, ...] | list[int], d: int) -> bool:
    """Literal multiset obstruction: every column has weight 0, 1, or 7,
    and at least one column has weight 1.
    """
    if len(words) != 7:
        raise ValueError("a septuple must contain exactly seven supports")
    saw_one = False
    for j in range(d):
        weight = sum((word >> j) & 1 for word in words)
        if weight not in (0, 1, 7):
            return False
        saw_one |= weight == 1
    return saw_one


def comparable_witness(family: tuple[int, ...]) -> tuple[int, ...] | None:
    """Return six copies of A and one B when A is a proper subset of B."""
    for a, b in combinations(family, 2):
        if a != b and subset(a, b):
            return (a,) * 6 + (b,)
        if a != b and subset(b, a):
            return (b,) * 6 + (a,)
    return None


def is_antichain(family: tuple[int, ...]) -> bool:
    return comparable_witness(family) is None


def distinct_sunflower(seven: tuple[int, ...] | list[int], d: int) -> bool:
    """Check seven distinct sets for the ordinary nontrivial sunflower rule."""
    return len(set(seven)) == 7 and forbidden_septuple(seven, d)


def has_distinct_seven_sunflower(family: tuple[int, ...], d: int) -> bool:
    return any(distinct_sunflower(seven, d) for seven in combinations(family, 7))


def structural_safe(family: tuple[int, ...], d: int) -> bool:
    """The reduced criterion proved in THEOREM.md."""
    return is_antichain(family) and not has_distinct_seven_sunflower(family, d)


def literal_safe(family: tuple[int, ...], d: int) -> bool:
    """Brute-force literal multiset criterion; intended only for small tests."""
    return not any(
        forbidden_septuple(tuple(family[i] for i in indices), d)
        for indices in combinations_with_replacement(range(len(family)), 7)
    )


def all_antichains(d: int):
    """Enumerate all antichains of 2^[d]; only used at d <= 4."""
    universe = tuple(range(1 << d))
    for selector in range(1 << len(universe)):
        family = tuple(universe[i] for i in range(len(universe)) if selector >> i & 1)
        if is_antichain(family):
            yield family


def tensor(c_family: tuple[int, ...], c_dim: int, d_family: tuple[int, ...]) -> tuple[int, ...]:
    """Cartesian/tensor product on disjoint coordinate blocks."""
    return tuple(a | (b << c_dim) for a in c_family for b in d_family)


def weighted_mass(family: tuple[int, ...]) -> Fraction:
    return sum((X ** word.bit_count() for word in family), start=Fraction(0))


def two_disjoint_k7_edges() -> tuple[int, ...]:
    edges: list[int] = []
    for offset in (0, 7):
        for i, j in combinations(range(offset, offset + 7), 2):
            edges.append((1 << i) | (1 << j))
    return tuple(edges)


def graph_degrees(edges: tuple[int, ...], vertices: int) -> tuple[int, ...]:
    return tuple(sum((edge >> v) & 1 for edge in edges) for v in range(vertices))


def maximum_matching_size(edges: tuple[int, ...], vertices: int) -> int:
    neighbors = [0] * vertices
    for edge in edges:
        endpoints = tuple(i for i in range(vertices) if edge >> i & 1)
        if len(endpoints) != 2:
            raise ValueError("not a simple graph edge")
        u, v = endpoints
        neighbors[u] |= 1 << v
        neighbors[v] |= 1 << u

    @lru_cache(maxsize=None)
    def solve(available: int) -> int:
        if available == 0:
            return 0
        v_bit = available & -available
        v = v_bit.bit_length() - 1
        remainder = available ^ v_bit
        best = solve(remainder)
        candidates = neighbors[v] & remainder
        while candidates:
            u_bit = candidates & -candidates
            candidates ^= u_bit
            best = max(best, 1 + solve(remainder ^ u_bit))
        return best

    return solve((1 << vertices) - 1)


def uniform_cap(k: int) -> int:
    """Proved universal cap M_k for k-uniform safe families."""
    if k < 1:
        raise ValueError("uniform_cap is defined for positive ranks")
    if k == 1:
        return 6
    value = 42
    for rank in range(3, k + 1):
        # Link-summing over the union of a maximal matching necessarily counts
        # each matching member rank times, producing (rank-1) units of known
        # overcount per matching member.
        value = 6 * (rank * value - (rank - 1))
    return value


def lym_cap_upper(d: int) -> tuple[Fraction, tuple[tuple[int, Fraction, Fraction], ...]]:
    """Solve the exact fractional LYM-plus-uniform-cap relaxation.

    Returns the upper bound and allocations (rank, LYM mass, density).
    Empty-set families are handled separately in the theorem.
    """
    items: list[tuple[Fraction, int, Fraction]] = []
    for k in range(1, d + 1):
        layer = comb(d, k)
        cap_fraction = Fraction(min(layer, uniform_cap(k)), layer)
        density = layer * X**k
        items.append((density, k, cap_fraction))
    items.sort(key=lambda item: (item[0], -item[1]), reverse=True)

    remaining = Fraction(1)
    total = Fraction(0)
    allocation: list[tuple[int, Fraction, Fraction]] = []
    for density, k, cap_fraction in items:
        take = min(remaining, cap_fraction)
        if take:
            total += take * density
            allocation.append((k, take, density))
            remaining -= take
        if remaining == 0:
            break
    return total, tuple(allocation)


def verify_constants() -> None:
    assert X == Fraction(40, 597)
    assert Y == Fraction(2401, 2388)
    assert 1 / X == Fraction(597, 40)
    assert Y / (1 + X) == Fraction(2401, 2548)


def verify_multiset_reduction() -> None:
    # Planted comparable obstruction: six copies of A and one strict superset B.
    comparable = (0b001, 0b011)
    witness = comparable_witness(comparable)
    assert witness is not None and forbidden_septuple(witness, 3)
    assert not structural_safe(comparable, 3)
    assert not literal_safe(comparable, 3)

    # Planted ordinary seven-sunflower and its six-petal safe control.
    seven_singletons = tuple(1 << i for i in range(7))
    six_singletons = seven_singletons[:6]
    assert forbidden_septuple(seven_singletons, 7)
    assert not structural_safe(seven_singletons, 7)
    assert structural_safe(six_singletons, 6)
    assert literal_safe(six_singletons, 6)

    # Exhaust every antichain on four coordinates against the literal multiset
    # definition.  (There are 168, independently checked below.)
    antichain_count = 0
    for family in all_antichains(4):
        antichain_count += 1
        assert literal_safe(family, 4) == structural_safe(family, 4)
    assert antichain_count == 168

    # Every one of all 2^(2^4) families either has a directly verified
    # comparable witness or is one of those exhaustively checked antichains.
    universe = tuple(range(16))
    checked = 0
    for selector in range(1 << 16):
        family = tuple(universe[i] for i in range(16) if selector >> i & 1)
        witness = comparable_witness(family)
        if witness is not None:
            assert forbidden_septuple(witness, 4)
        else:
            checked += 1
    assert checked == antichain_count


def verify_tensor_closure() -> None:
    small = tuple(all_antichains(3))
    assert len(small) == 20
    for c_family in small:
        for d_family in small:
            product = tensor(c_family, 3, d_family)
            assert structural_safe(product, 6)
            assert weighted_mass(product) == weighted_mass(c_family) * weighted_mass(d_family)

    # Planted negative control: tensoring does not repair an unsafe factor.
    unsafe = (0b01, 0b11)
    singleton = (0b1,)
    product = tensor(unsafe, 2, singleton)
    witness = comparable_witness(product)
    assert witness is not None and forbidden_septuple(witness, 3)


def verify_uniform_extrema_and_constructions() -> None:
    assert uniform_cap(1) == 6
    assert uniform_cap(2) == 42
    assert uniform_cap(3) == 744
    assert uniform_cap(4) == 17_838
    assert uniform_cap(5) == 535_116
    assert uniform_cap(6) == 19_264_146

    witness = two_disjoint_k7_edges()
    assert len(witness) == 42 and len(set(witness)) == 42
    assert set(graph_degrees(witness, 14)) == {6}
    assert maximum_matching_size(witness, 14) == 6
    assert weighted_mass(witness) == 42 * X**2
    assert weighted_mass(witness) < 1

    # The standard six-symbol transversal block: q one-hot choices.  For seven
    # words and q <= 6, valid 0/1/7 column counts force unanimity.
    for q in range(1, 7):
        for counts in _compositions(7, q):
            if all(count in (0, 1, 7) for count in counts):
                assert 7 in counts  # hence exactly one symbol was used
    assert 6 * X == Fraction(240, 597) < 1

    # Planted warning control: 15 singletons have mass > 1 but are forbidden.
    bad = tuple(1 << i for i in range(15))
    assert weighted_mass(bad) > 1
    assert has_distinct_seven_sunflower(bad, 15)


def _compositions(total: int, parts: int):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions(total - first, parts - 1):
            yield (first,) + rest


def verify_lym_cap_lp() -> None:
    bounds = {d: lym_cap_upper(d)[0] for d in range(1, 34)}

    # Exact rational comparisons, not decimal tolerances.
    assert all(bounds[d] < 1 for d in range(1, 29))
    assert bounds[29] > 1
    assert all(bounds[d] < Y**d for d in range(1, 32))
    assert bounds[32] > Y**32

    # Confirm that these are the first failures in the tested consecutive range.
    assert min(d for d in bounds if bounds[d] > 1) == 29
    assert min(d for d in bounds if bounds[d] > Y**d) == 32

    print("d   nonempty_LYM_cap_upper       gate=y^d")
    for d in range(20, 33):
        print(f"{d:2d}  {float(bounds[d]):.12f}        {float(Y**d):.12f}")

    # Show the exact greedy allocations at the two relaxation seams.
    for d in (29, 32):
        bound, allocation = lym_cap_upper(d)
        print(f"allocation d={d}, exact_bound={bound.numerator}/{bound.denominator}")
        for k, take, density in allocation:
            print(
                f"  rank={k:2d} LYM_take={take.numerator}/{take.denominator} "
                f"density={density.numerator}/{density.denominator}"
            )


def main() -> None:
    verify_constants()
    print("PASS_CONSTANTS")
    verify_multiset_reduction()
    print("PASS_MULTISET_REDUCTION_EXHAUSTIVE_D4")
    verify_tensor_closure()
    print("PASS_TENSOR_CLOSURE_SMALL_EXHAUSTIVE")
    verify_uniform_extrema_and_constructions()
    print("PASS_M1_M2_STRENGTHENED_RECURSION_AND_CONSTRUCTIONS")
    verify_lym_cap_lp()
    print("PASS_EXACT_RATIONAL_LYM_CAP_HORIZONS")
    print("PASS_WEIGHTED_MULTISET7_SUNFLOWER_PACKET")


if __name__ == "__main__":
    main()

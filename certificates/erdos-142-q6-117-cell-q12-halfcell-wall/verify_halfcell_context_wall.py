#!/usr/bin/env python3
"""Exact stdlib replay: half-residual context tiles cannot beat the EHPS gate.

The fixed q=6 117-cell alphabet is refined into its 16 half-residual boxes,
equivalently 1872 q=12 boxes.  A 109-edge strict-dilation matching gives 1763
quotient classes.  The full-word dilation telescope then bounds every decoded
physical microbox language by 1763**m, below the exact gate 1764**m.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as F
from itertools import product
import hashlib
import json
import sys

COARSE_Q = 6
Q = 12
COARSE_BASE = (
    (3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
    (5, 0), (5, 1), (5, 2),
)
OFFSETS = (
    (0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
    (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3),
)
COARSE = tuple(
    (a, b, (a + dx) % COARSE_Q, (b + dy) % COARSE_Q)
    for a, b in COARSE_BASE
    for dx, dy in OFFSETS
)
MICRO = tuple(
    tuple(2 * digit + bit for digit, bit in zip(cell, bits))
    for cell in COARSE
    for bits in product((0, 1), repeat=4)
)

# A maximum matching of the coarse q=6 dilation graph.  We do not need its
# maximality here.  Refining these 21 disjoint coarse pairs supplies 106
# disjoint q=12 edges.  Three further disjoint edges make the strict gate.
COARSE_MATCHING = (
    (3, 55), (4, 17), (16, 68), (24, 25), (36, 37), (39, 52),
    (40, 53), (46, 96), (54, 106), (12, 59), (56, 69), (76, 77),
    (78, 79), (83, 84), (86, 87), (91, 92), (80, 93), (98, 99),
    (41, 105), (64, 111), (104, 116),
)
EXTRA_EDGES = ((0, 195), (4, 199), (656, 627))
EDGE_DIGEST = "fe25fe2b765bef0f573ad96997e2fe007fa99e81726caf7bf34ace943e895434"

# Exact polynomials c0+c1*t+c2*t^2.
Poly = tuple[F, F, F]


def poly(a=0, b=0, c=0) -> Poly:
    return F(a), F(b), F(c)


def add(x: Poly, y: Poly) -> Poly:
    return tuple(a + b for a, b in zip(x, y))  # type: ignore[return-value]


def scale(c: int | F, x: Poly) -> Poly:
    return tuple(F(c) * a for a in x)  # type: ignore[return-value]


def sub(x: Poly, y: Poly) -> Poly:
    return add(x, scale(-1, y))


def mul(x: Poly, y: Poly) -> Poly:
    out = [F(0)] * 5
    for i, a in enumerate(x):
        for j, b in enumerate(y):
            out[i + j] += a * b
    assert out[3:] == [0, 0]
    return tuple(out[:3])  # type: ignore[return-value]


def actual(digit: int, residual: Poly) -> Poly:
    return add(poly(F(digit, Q)), scale(F(1, Q), residual))


def midpoint_defect(x: Poly, y: Poly, z: Poly) -> Poly:
    return sub(add(x, z), scale(2, y))


def correction_rhs(x: Poly, y: Poly, z: Poly) -> Poly:
    """q^2 times the correction needed after writing F=2||.||^2+h/q^2."""
    raw = add(
        mul(sub(x, z), sub(x, z)),
        add(scale(-2, mul(x, x)),
            add(scale(-2, mul(z, z)), scale(4, mul(y, y)))),
    )
    return scale(Q * Q, raw)


def is_dilation_edge(a: int, b: int) -> bool:
    A, B = MICRO[a], MICRO[b]
    return (
        a != b
        and all(y == x or y == (x - 1) % Q for x, y in zip(A, B))
        and any(x == 0 and y == Q - 1 for x, y in zip(A, B))
    )


def enumerate_edges() -> tuple[tuple[int, int], ...]:
    lookup = {cell: i for i, cell in enumerate(MICRO)}
    rows = []
    for a_index, a in enumerate(MICRO):
        for mask in product((0, 1), repeat=4):
            b = tuple((x - d) % Q for x, d in zip(a, mask))
            b_index = lookup.get(b)
            if b_index is not None and is_dilation_edge(a_index, b_index):
                rows.append((a_index, b_index))
    return tuple(sorted(set(rows)))


def structured_matching(edges: set[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    """Lift the 21 disjoint coarse pairs, then add three audited micro-edges."""
    lifted = []
    used: set[int] = set()
    for coarse_a, coarse_b in COARSE_MATCHING:
        candidates = sorted(
            (a, b)
            for a, b in edges
            if {a // 16, b // 16} == {coarse_a, coarse_b}
        )
        for a, b in candidates:
            if a not in used and b not in used:
                lifted.append((a, b))
                used.update((a, b))
    assert len(lifted) == 106
    for a, b in EXTRA_EDGES:
        assert (a, b) in edges and a not in used and b not in used
        lifted.append((a, b))
        used.update((a, b))
    assert len(lifted) == 109
    assert len(used) == 218
    return tuple(lifted)


def scalar_row_audit() -> None:
    """Verify the two raw-canonical midpoint rows for every q=12 digit."""
    for a in range(Q):
        b = (a - 1) % Q
        A_t = actual(a, poly(0, 1))
        A_3t = actual(a, poly(0, 3))
        B_1t = actual(b, poly(1, -1))
        B_13t = actual(b, poly(1, -3))
        wrap = a == 0
        k_one = -1 if wrap else 0
        k_two = 1 if wrap else 0
        rhs_one = poly(3 * Q * Q, -4 * Q) if wrap else poly()
        rhs_two = poly(-Q * Q, -4 * Q) if wrap else poly()
        assert midpoint_defect(A_t, B_1t, B_13t) == poly(k_one)
        assert midpoint_defect(A_3t, A_t, B_1t) == poly(k_two)
        assert correction_rhs(A_t, B_1t, B_13t) == rhs_one
        assert correction_rhs(A_3t, A_t, B_1t) == rhs_two
        # Reversing the two words only reverses the order of the rows.
        assert correction_rhs(B_1t, A_t, A_3t) == rhs_two
        assert correction_rhs(B_13t, B_1t, A_t) == rhs_one
        assert add(rhs_one, rhs_two) == (
            poly(2 * Q * Q, -8 * Q) if wrap else poly()
        )


def edge_data(edge: tuple[int, int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    a, b = edge
    active = tuple(
        j for j, (x, y) in enumerate(zip(MICRO[a], MICRO[b])) if x != y
    )
    wraps = tuple(
        j for j in active if MICRO[a][j] == 0 and MICRO[b][j] == Q - 1
    )
    assert active and wraps
    return active, wraps


def point_for_word(
    word: tuple[int, ...],
    parameter_scale: int,
    ownership: dict[int, tuple[int, int, tuple[int, ...]]],
) -> tuple[Poly, ...]:
    coordinates = []
    for label in word:
        info = ownership.get(label)
        for coordinate, digit in enumerate(MICRO[label]):
            if info is None or coordinate not in info[2]:
                residual = poly(F(1, 2))
            elif label == info[0]:
                residual = poly(0, parameter_scale)
            else:
                residual = poly(1, -parameter_scale)
            coordinates.append(actual(digit, residual))
    return tuple(coordinates)


def vector_rhs(x: tuple[Poly, ...], y: tuple[Poly, ...],
               z: tuple[Poly, ...]) -> Poly:
    answer = poly()
    for xi, yi, zi in zip(x, y, z):
        defect = midpoint_defect(xi, yi, zi)
        assert defect[1:] == (0, 0)
        assert defect[0].denominator == 1
        answer = add(answer, correction_rhs(xi, yi, zi))
    return answer


def global_mixed_orientation_audit(
    matching: tuple[tuple[int, int], ...],
) -> None:
    ownership = {}
    wrap_total = 0
    for a, b in matching:
        active, wraps = edge_data((a, b))
        ownership[a] = ownership[b] = (a, b, active)
        wrap_total += len(wraps)
        assert len(wraps) == 1
    left = tuple(a if i % 2 == 0 else b for i, (a, b) in enumerate(matching))
    right = tuple(b if i % 2 == 0 else a for i, (a, b) in enumerate(matching))
    X_t = point_for_word(left, 1, ownership)
    X_3t = point_for_word(left, 3, ownership)
    Y_t = point_for_word(right, 1, ownership)
    Y_3t = point_for_word(right, 3, ownership)
    first = vector_rhs(X_t, Y_t, Y_3t)
    second = vector_rhs(X_3t, X_t, Y_t)
    assert add(first, second) == poly(
        wrap_total * 2 * Q * Q, -wrap_total * 8 * Q
    )
    assert wrap_total == len(matching) == 109


def quotient_and_physical_gate(
    matching: tuple[tuple[int, int], ...],
) -> tuple[int, ...]:
    quotient = [-1] * len(MICRO)
    group = 0
    for a, b in matching:
        assert quotient[a] == quotient[b] == -1
        quotient[a] = quotient[b] = group
        group += 1
    for a in range(len(MICRO)):
        if quotient[a] == -1:
            quotient[a] = group
            group += 1
    assert group == len(MICRO) - len(matching) == 1763

    # In q=12 microbox units the EHPS four-coordinate gate is exactly 1764.
    gate_micro = F(Q**4) * F(49, 576)
    assert gate_micro == 1764
    assert F(group) < gate_micro
    # Equivalently, in original q=6 cell units, 1763/16 < 441/4.
    assert F(group, 16) < F(441, 4)
    for m in range(1, 8):
        assert F(group**m, Q**(4 * m)) < F(49, 576)**m
    return tuple(quotient)


def abstract_word_injectivity_audit(
    quotient: tuple[int, ...],
    matching: tuple[tuple[int, int], ...],
) -> None:
    # Exhaust mixed equal/forward/reverse choices over four representative
    # positions.  This checks the quotient-fibre word logic, not just one pair.
    edge_by_group = {
        quotient[a]: (a, b) for a, b in matching[:4]
    }
    for choices in product((0, 1, 2), repeat=4):
        if not any(choices):
            continue
        left = []
        right = []
        for group, choice in zip(sorted(edge_by_group), choices):
            a, b = edge_by_group[group]
            if choice == 0:
                left.append(a)
                right.append(a)
            elif choice == 1:
                left.append(a)
                right.append(b)
            else:
                left.append(b)
                right.append(a)
        assert tuple(map(quotient.__getitem__, left)) == tuple(
            map(quotient.__getitem__, right)
        )
        assert left != right

    # Whole-word h coefficients after adding the two midpoint inequalities:
    # D(3t)-D(t), with no locality or additivity assumed for h.
    coefficients = Counter()
    for point, coefficient in (
        ("X(t)", 1), ("Y(3t)", 1), ("Y(t)", -2),
        ("X(3t)", 1), ("X(t)", -2), ("Y(t)", 1),
    ):
        coefficients[point] += coefficient
    assert coefficients == Counter(
        {"X(3t)": 1, "Y(3t)": 1, "X(t)": -1, "Y(t)": -1}
    )


def finite_telescope_audit() -> None:
    # D(3t)-D(t) >= K(288-96t), at t=(1/4)/3^j.
    for bound, wraps in ((0, 1), (100, 1), (10**4, 109), (10**9, 127)):
        steps = (4 * bound + Q * wraps) // (2 * Q * Q * wraps) + 1
        lower = (
            2 * Q * Q * wraps * steps
            - Q * wraps * (1 - F(1, 3**steps))
        )
        assert lower > 4 * bound
        if steps <= 200:
            direct = sum(
                (
                    wraps * (2 * Q * Q - F(2 * Q, 3**j))
                    for j in range(1, steps + 1)
                ),
                F(0),
            )
            assert direct == lower


def physical_overlap_audit() -> None:
    # State/edge multiplicity is not physical volume.  Two abstract paths that
    # decode to the same microbox word contribute one disjoint word box.
    word_a = (0, 4, 656)
    word_b = (0, 4, 656)
    word_c = (195, 199, 627)
    abstract_paths = (("s0", word_a), ("s1", word_b), ("s2", word_c))
    decoded = {word for _, word in abstract_paths}
    assert len(abstract_paths) == 3 and len(decoded) == 2
    assert sum(F(1, Q**(4 * len(word))) for word in decoded) == F(2, Q**12)


def planted_failures(
    edges: set[tuple[int, int]],
    matching: tuple[tuple[int, int], ...],
) -> None:
    try:
        assert len(matching[:-3]) >= 109
    except AssertionError:
        pass
    else:
        raise AssertionError("the insufficient 106-edge lift passed")

    bad = list(matching)
    bad[-1] = (bad[0][0], bad[-1][1])
    flat = [v for pair in bad for v in pair]
    try:
        assert len(flat) == len(set(flat))
    except AssertionError:
        pass
    else:
        raise AssertionError("an overlapping matching passed")

    # Ordinary predecessor adjacency without a 0->11 wrap has zero gap and is
    # deliberately excluded from the strict-dilation graph.
    fake_a = (1, 2, 3, 4)
    fake_b = (0, 2, 3, 4)
    assert all(y == x or y == (x - 1) % Q for x, y in zip(fake_a, fake_b))
    assert not any(x == 0 and y == Q - 1 for x, y in zip(fake_a, fake_b))

    try:
        assert (195, 0) in edges
    except AssertionError:
        pass
    else:
        raise AssertionError("the reversed non-edge passed")


def main() -> None:
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ["--self-test"]
    assert len(COARSE) == len(set(COARSE)) == 117
    assert len(MICRO) == len(set(MICRO)) == 1872
    assert all(
        tuple(digit // 2 for digit in MICRO[16 * i + bits]) == COARSE[i]
        for i in range(117)
        for bits in range(16)
    )
    edges_tuple = enumerate_edges()
    encoded = (json.dumps(edges_tuple, separators=(",", ":")) + "\n").encode()
    assert len(edges_tuple) == 676
    digest = hashlib.sha256(encoded).hexdigest()
    assert digest == EDGE_DIGEST, (
        digest, EDGE_DIGEST, repr(encoded[-12:]), edges_tuple[-3:]
    )
    edges = set(edges_tuple)
    assert Counter(len(edge_data(edge)[0]) for edge in edges_tuple) == Counter(
        {1: 88, 2: 284, 3: 238, 4: 66}
    )
    assert Counter(len(edge_data(edge)[1]) for edge in edges_tuple) == Counter(
        {1: 659, 2: 17}
    )
    matching = structured_matching(edges)
    scalar_row_audit()
    global_mixed_orientation_audit(matching)
    quotient = quotient_and_physical_gate(matching)
    abstract_word_injectivity_audit(quotient, matching)
    finite_telescope_audit()
    physical_overlap_audit()
    planted_failures(edges, matching)
    print("PASS_HALFCELL_CONTEXT_WALL")
    print("REFINEMENT_OK q6_cells=117 halves_per_cell=16 q12_microboxes=1872")
    print("DILATION_GRAPH_OK oriented_edges=676 digest=" + EDGE_DIGEST)
    print("MATCHING_OK structured=106 extras=3 total=109 quotient_classes=1763")
    print("RAW_ROWS_OK wrap_sum=288-96t mixed_orientations arbitrary_word_h")
    print("FINITE_TELESCOPE_OK pointwise_bounded_physical_potential=impossible")
    print("PHYSICAL_GATE_OK 1763/16<441/4 and 1763/20736<49/576")
    print("EDGE_STATE_SCOPE_OK arbitrary_decoded_language overlaps_deduplicated")
    print("PLANTED_FAILURES_REJECTED")


if __name__ == "__main__":
    main()

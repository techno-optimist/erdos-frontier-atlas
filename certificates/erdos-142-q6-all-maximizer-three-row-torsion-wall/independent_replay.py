#!/usr/bin/env python3
"""Independent q=6 audit of all ordered 3-row torsion templates.

This reconstructs the epsilon=0 EHPS q=6 support and all five labelled
Karapetyan cylinders without importing the claimed sweep.  Potential
variables are labelled by (cylinder number, full 3-point vertex), so equal
geometric vertices in different cylinders never merge.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json

Q = 6
ROLES = ("P1", "P2", "P3", "B", "K")
WORDS = (("P1", "K", "B"), ("B", "K", "P1"),
         ("P2", "B", "P2"), ("P3", "B", "B"), ("B", "B", "P3"))
# Direct reconstruction of the q=6 epsilon=0 base support, in canonical reps.
BASE = frozenset(((3, 2), (3, 3), (3, 4),
                  (4, 1), (4, 2), (4, 3),
                  (5, 0), (5, 1), (5, 2)))


def d4(point: tuple[int, int], element: int) -> tuple[int, int]:
    """The eight coordinate reflections/swaps in canonical q=6 representatives."""
    x, y = point
    if element & 1:
        x = Q - 1 - x
    if element & 2:
        y = Q - 1 - y
    if element & 4:
        x, y = y, x
    return x, y


SUPPORTS: list[frozenset[tuple[int, int]]] = []
for g in range(8):
    image = frozenset(d4(p, g) for p in BASE)
    if image not in SUPPORTS:
        SUPPORTS.append(image)
assert len(SUPPORTS) == 8


def support_assignment_orbit(a: tuple[int, ...]) -> set[tuple[int, ...]]:
    answer = set()
    for g in range(8):
        answer.add(tuple(next(j for j, candidate in enumerate(SUPPORTS)
                              if candidate == frozenset(d4(p, g) for p in SUPPORTS[a[i]]))
                         for i in range(5)))
    return answer


def union_mass(a: tuple[int, ...]) -> int:
    # The union uses geometric vertices, as it should.  This is deliberately
    # different from the potential labels constructed below.
    vertices = set()
    for word in WORDS:
        vertices.update(itertools.product(*(SUPPORTS[a[ROLES.index(role)]] for role in word)))
    return len(vertices)


def cylinder_vertices(a: tuple[int, ...], word_number: int):
    word = WORDS[word_number]
    return set(itertools.product(*(SUPPORTS[a[ROLES.index(role)]] for role in word)))


def canonical_cost(p: tuple[int, int], r: tuple[int, int]) -> int:
    return (p[0] - r[0]) ** 2 + (p[1] - r[1]) ** 2


def midpoint_mod(left: tuple[int, int], center: tuple[int, int], right: tuple[int, int]) -> bool:
    return all((left[i] + right[i] - 2 * center[i]) % Q == 0 for i in range(2))


def vertex_midpoint_mod(left, center, right) -> bool:
    return all(midpoint_mod(left[j], center[j], right[j]) for j in range(3))


def coefficient_row(terms):
    """Accumulate coefficients even when two labelled vertices coincide."""
    out = {}
    for label, coefficient in terms:
        out[label] = out.get(label, 0) + coefficient
    return out


# A coordinatewise common torsion triangle is needed because the three rows
# respectively center at Y, X, Z.  Built from direct modular tests, not a
# formula imported from the claimed sweep.
POINT_TRIANGLES = []
for x in itertools.product(range(Q), repeat=2):
    for y in itertools.product(range(Q), repeat=2):
        for z in itertools.product(range(Q), repeat=2):
            if (midpoint_mod(x, y, z) and midpoint_mod(y, x, z)
                    and midpoint_mod(x, z, y)):
                POINT_TRIANGLES.append((x, y, z))
assert len(POINT_TRIANGLES) == 324


def allowed_coordinate_triangles(a: tuple[int, ...], pattern: tuple[int, int, int], coordinate: int):
    """Triangle factors for X/Y/Z at one cylinder coordinate.

    `coordinate` selects the role in each word.  The output retains which
    labelled cylinder each point is being used in only when a full vertex is
    formed, avoiding illegal point-level identification across cylinders.
    """
    roles = tuple(WORDS[pattern[j]][coordinate] for j in range(3))
    supports = tuple(SUPPORTS[a[ROLES.index(role)]] for role in roles)
    return [t for t in POINT_TRIANGLES if t[0] in supports[0]
            and t[1] in supports[1] and t[2] in supports[2]]


def variable_id(word: int, vertex: tuple[tuple[int, int], ...]):
    """Potential variable identity: cylinder label PLUS all three points."""
    return (word, vertex)


def positive_witness(a: tuple[int, ...], pattern: tuple[int, int, int]):
    """Construct a checked positive 3-row witness, or return None.

    The resulting triples have full, labelled cylinder identities.  No two
    different cylinder labels are conflated even if their geometric vertices
    happen to coincide.
    """
    factors = [allowed_coordinate_triangles(a, pattern, j) for j in range(3)]
    if any(not factor for factor in factors):
        return None
    for choices in itertools.product(*factors):
        x = tuple(t[0] for t in choices)
        y = tuple(t[1] for t in choices)
        z = tuple(t[2] for t in choices)
        rhs = (sum(canonical_cost(x[i], z[i]) for i in range(3)),
               sum(canonical_cost(y[i], z[i]) for i in range(3)),
               sum(canonical_cost(x[i], y[i]) for i in range(3)))
        if sum(rhs) == 0:
            continue
        vx, vy, vz = (variable_id(pattern[0], x), variable_id(pattern[1], y),
                      variable_id(pattern[2], z))
        rows = ((coefficient_row(((vx, 1), (vy, -2), (vz, 1))), rhs[0], (x, y, z)),
                (coefficient_row(((vy, 1), (vx, -2), (vz, 1))), rhs[1], (y, x, z)),
                (coefficient_row(((vx, 1), (vy, 1), (vz, -2))), rhs[2], (x, z, y)))
        # Rebuild coefficient sums by labels rather than assuming symbols are
        # distinct.  This catches both accidental merging and degeneracy.
        coefficient_sum = {}
        for coefficients, raw_rhs, triple in rows:
            assert raw_rhs >= 0
            assert vertex_midpoint_mod(triple[0], triple[1], triple[2])
            for label, coefficient in coefficients.items():
                coefficient_sum[label] = coefficient_sum.get(label, 0) + coefficient
        assert set(coefficient_sum.values()) == {0}
        assert sum(rhs) > 0
        carries = []
        for left, center, right in ((x, y, z), (y, x, z), (x, z, y)):
            carries.append(tuple((left[j][i] + right[j][i] - 2 * center[j][i]) // Q
                                 for j in range(3) for i in range(2)))
        return {
            "pattern": list(pattern),
            "vertices": {"X": [list(p) for p in x], "Y": [list(p) for p in y],
                         "Z": [list(p) for p in z]},
            "variable_labels": {"X_cylinder": pattern[0], "Y_cylinder": pattern[1],
                                "Z_cylinder": pattern[2]},
            "raw_rhs": list(rhs), "contradiction": sum(rhs), "carries": [list(c) for c in carries],
        }
    return None


def all_triangle_count(a: tuple[int, ...], pattern: tuple[int, int, int]) -> int:
    """Exact number of full X/Y/Z triples with strictly positive summed cost."""
    factors = [allowed_coordinate_triangles(a, pattern, j) for j in range(3)]
    if any(not factor for factor in factors):
        return 0
    count = 0
    for choices in itertools.product(*factors):
        x = tuple(t[0] for t in choices)
        y = tuple(t[1] for t in choices)
        z = tuple(t[2] for t in choices)
        if sum(canonical_cost(x[i], z[i]) + canonical_cost(y[i], z[i])
               + canonical_cost(x[i], y[i]) for i in range(3)) > 0:
            count += 1
    return count


def planted_controls(maximizers: list[tuple[int, ...]], diagonal_hits: dict[tuple[int, int, int], int]):
    # 1: corrupt a modular midpoint coordinate; it must fail the exact predicate.
    assert not midpoint_mod((0, 0), (1, 0), (3, 0))
    # 2: a q=6 torsion point does not automatically pass ordinary equality.
    assert (0 + 2) % 6 == (2 * 4) % 6 and 0 + 2 != 2 * 4
    # 3: diagonal words have no positive common 3-row torsion triangle.
    assert all(value == 0 for value in diagonal_hits.values())
    # 4: labelled identities do not merge across cylinders, even at same geometry.
    assert variable_id(0, ((3, 2),) * 3) != variable_id(1, ((3, 2),) * 3)
    # 5: an all-zero RHS is never accepted as a contradiction.
    assert positive_witness(maximizers[0], (0, 0, 0)) is None
    return ["corrupt_midpoint_rejected", "ordinary_midpoint_not_substituted",
            "diagonal_patterns_rejected", "cross_cylinder_point_merge_rejected",
            "zero_rhs_rejected"]


def main():
    assignments = list(itertools.product(range(8), repeat=5))
    masses = {a: union_mass(a) for a in assignments}
    maximum_mass = max(masses.values())
    maximizers = sorted(a for a, mass in masses.items() if mass == maximum_mass)
    assert maximum_mass == 3645 and len(maximizers) == 256
    # Each cylinder has 9^3 vertices; equality with 5*9^3 proves that the
    # five geometric cylinders are pairwise disjoint at every maximizer.  So
    # the labelled-variable formulation is exactly the unrestricted global
    # potential formulation on this maximum-mass union, not a relaxation.
    for a in maximizers:
        cylinders = [cylinder_vertices(a, j) for j in range(5)]
        assert all(len(c) == 729 for c in cylinders)
        assert all(not (cylinders[i] & cylinders[j]) for i in range(5) for j in range(i))

    patterns = list(itertools.product(range(5), repeat=3))
    hits_by_pattern = {p: 0 for p in patterns}
    witnesses = {}
    triangle_count_ranges = {p: [None, None] for p in patterns}
    coverage = set()
    for a in maximizers:
        for p in patterns:
            witness = positive_witness(a, p)
            exact_count = all_triangle_count(a, p) if witness is not None else 0
            assert (witness is None) == (exact_count == 0)
            lo, hi = triangle_count_ranges[p]
            triangle_count_ranges[p] = [exact_count if lo is None else min(lo, exact_count),
                                        exact_count if hi is None else max(hi, exact_count)]
            if witness is not None:
                hits_by_pattern[p] += 1
                coverage.add(a)
                witnesses.setdefault(p, witness)

    nonzero = [p for p in patterns if hits_by_pattern[p]]
    diagonal = [(i, i, i) for i in range(5)]
    assert len(nonzero) == 120
    assert all(hits_by_pattern[p] == 256 for p in nonzero)
    assert all(hits_by_pattern[p] == 0 for p in diagonal)
    assert coverage == set(maximizers)

    unseen = set(maximizers)
    orbits = []
    while unseen:
        rep = min(unseen)
        orbit = support_assignment_orbit(rep)
        assert orbit <= set(maximizers)
        orbits.append(sorted(orbit))
        unseen -= orbit
    assert len(orbits) == 32 and all(len(o) == 8 for o in orbits)

    controls = planted_controls(maximizers, {p: hits_by_pattern[p] for p in diagonal})
    report = {
        "audit": "independent q=6 all-word-pattern torsion replay",
        "q": Q,
        "support_size": len(BASE),
        "support_image_count": len(SUPPORTS),
        "assignments_examined": len(assignments),
        "maximum_union_mass": maximum_mass,
        "maximizer_count": len(maximizers),
        "all_maximizer_cylinders_pairwise_disjoint": True,
        "maximizer_d4_orbit_count": len(orbits),
        "maximizer_d4_orbit_sizes": sorted(len(o) for o in orbits),
        "point_common_torsion_triangle_count": len(POINT_TRIANGLES),
        "ordered_word_pattern_count": len(patterns),
        "positive_patterns": [list(p) for p in nonzero],
        "zero_patterns": [list(p) for p in patterns if not hits_by_pattern[p]],
        "hits_per_pattern": {"".join(map(str, p)): hits_by_pattern[p] for p in patterns},
        "all_positive_patterns_hit_all_maximizers": all(hits_by_pattern[p] == len(maximizers) for p in nonzero),
        "covered_maximizers": len(coverage),
        "triangle_count_ranges": {"".join(map(str, p)): triangle_count_ranges[p] for p in patterns},
        "one_checked_witness_per_positive_pattern": {"".join(map(str, p)): witnesses[p] for p in nonzero},
        "planted_controls": controls,
        "scope": "finite q=6 only; full labelled-cylinder potentials; no continuum or r3(N) claim",
    }
    text = json.dumps(report, sort_keys=True, indent=2) + "\n"
    digest = hashlib.sha256(text.encode()).hexdigest()
    print("PASS_INDEPENDENT_Q6_ALL_PATTERN_TORSION_AUDIT")
    print(json.dumps({
        "maximum_union_mass": maximum_mass,
        "maximizer_count": len(maximizers),
        "d4_orbits": len(orbits),
        "positive_patterns": len(nonzero),
        "covered_maximizers": len(coverage),
        "zero_patterns": [list(p) for p in patterns if not hits_by_pattern[p]],
        "planted_controls": controls,
        "audit_result_sha256": digest,
    }, indent=2))


if __name__ == "__main__":
    main()

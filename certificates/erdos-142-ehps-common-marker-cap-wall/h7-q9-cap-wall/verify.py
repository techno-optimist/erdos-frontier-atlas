#!/usr/bin/env python3
"""Exact AG(2,3) cap classification and q=9 square-packet audit."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import gcd


Q = 9
F3 = tuple(product(range(3), repeat=2))
K = frozenset(product(range(6), repeat=2))

# weight, endpoint x, midpoint y, endpoint z, raw q^2-scaled cost
ROWS = (
    (2065936, (0, 0), (5, 5), (1, 1), 2),
    (1471148, (0, 1), (0, 3), (0, 5), 16),
    (4762508, (0, 1), (1, 1), (2, 1), 4),
    (1880560, (0, 2), (1, 2), (2, 2), 4),
    (940280, (0, 2), (2, 2), (4, 2), 16),
    (5530617, (0, 2), (5, 1), (1, 0), 5),
    (1664735, (0, 2), (5, 2), (1, 2), 1),
    (2942296, (0, 3), (5, 3), (1, 3), 1),
    (5706416, (0, 4), (1, 0), (2, 5), 5),
    (569696, (0, 4), (5, 4), (1, 4), 1),
    (516484, (0, 5), (5, 0), (1, 4), 2),
    (2267876, (1, 0), (1, 5), (1, 1), 1),
    (2381254, (1, 0), (2, 1), (3, 2), 8),
    (1233085, (1, 0), (3, 1), (5, 2), 20),
    (2195572, (1, 1), (1, 3), (1, 5), 16),
    (2995632, (1, 1), (2, 5), (3, 0), 5),
    (2096385, (1, 2), (3, 2), (5, 2), 16),
    (1448848, (1, 3), (1, 4), (1, 5), 4),
    (1811516, (1, 4), (2, 3), (3, 2), 8),
    (891332, (1, 5), (2, 4), (3, 3), 8),
    (569696, (2, 0), (3, 5), (4, 1), 5),
    (3623032, (2, 3), (3, 3), (4, 3), 4),
    (284848, (2, 4), (2, 0), (2, 5), 1),
    (1497816, (2, 4), (3, 0), (4, 5), 5),
    (2466170, (3, 1), (4, 1), (5, 1), 4),
    (470140, (3, 3), (4, 2), (5, 1), 8),
    (5884592, (3, 3), (4, 3), (5, 3), 4),
    (1139392, (3, 5), (4, 0), (5, 4), 5),
    (1032968, (4, 0), (0, 0), (5, 0), 1),
    (1245816, (4, 0), (4, 5), (4, 1), 1),
    (3116828, (4, 1), (0, 1), (5, 1), 1),
    (5008096, (4, 3), (0, 2), (5, 1), 5),
    (3138056, (4, 3), (0, 4), (5, 5), 5),
    (993816, (4, 5), (0, 5), (5, 5), 1),
)
PACKET_SUPPORT = frozenset(point for _w, x, y, z, _r in ROWS
                           for point in (x, y, z))

# A cleaner one-dimensional certificate on {0,...,5} in Z/9Z.  It is the
# direct trust path for every six-point primitive-line obstruction below.
SCALAR_ROWS = (
    (3, 4, 0, 5, 1),
    (2, 0, 1, 2, 4),
    (1, 0, 2, 4, 16),
    (1, 1, 3, 5, 16),
    (2, 3, 4, 5, 4),
    (3, 0, 5, 1, 1),
)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def is_cap(points, modulus=3):
    points = tuple(points)
    for triple in combinations(points, 3):
        if all(sum(point[j] for point in triple) % modulus == 0
               for j in range(len(points[0]))):
            return False
    return True


def add3(*points):
    return tuple(sum(p[j] for p in points) % 3 for j in range(2))


def direction(v):
    """Canonical representative of a projective direction in F_3^2."""
    need(v != (0, 0), "zero projective direction")
    return min(v, tuple((-x) % 3 for x in v))


def cap_signature(cap):
    anchor = add3(*cap)
    need(anchor not in cap, "4-cap contains its anchor")
    directions = set()
    for p in cap:
        mate = tuple((2*anchor[j]-p[j]) % 3 for j in range(2))
        need(mate in cap and mate != p, "anchor does not pair cap vertices")
        directions.add(direction(tuple((p[j]-anchor[j]) % 3 for j in range(2))))
    need(len(directions) == 2, "4-cap does not have two directions")
    return anchor, frozenset(directions)


def classify_caps():
    caps = tuple(frozenset(s) for s in combinations(F3, 4) if is_cap(s))
    need(len(caps) == len(set(caps)) == 54, "AG(2,3) 4-cap census")
    anchors = Counter()
    direction_pairs = Counter()
    for cap in caps:
        anchor, directions = cap_signature(cap)
        anchors[anchor] += 1
        direction_pairs[directions] += 1
    need(set(anchors.values()) == {6} and len(anchors) == 9,
         "4-caps are not six per anchor")
    need(set(direction_pairs.values()) == {9} and len(direction_pairs) == 6,
         "4-cap direction-pair census")

    standard = frozenset(((0, 0), (0, 1), (1, 0), (1, 1)))
    orbit = set()
    matrices = []
    for a, b, c, d in product(range(3), repeat=4):
        if (a*d-b*c) % 3:
            matrices.append((a, b, c, d))
            for tx, ty in F3:
                orbit.add(frozenset((((a*x+b*y+tx) % 3),
                                     ((c*x+d*y+ty) % 3))
                                    for x, y in standard))
    need(len(matrices) == 48 and orbit == set(caps),
         "AGL(2,3) is not transitive on the 54 caps")
    point_incidence = Counter(point for cap in caps for point in cap)
    need(set(point_incidence.values()) == {24}, "4-cap point incidence")
    return caps


def verify_double_plane_sharpness():
    cap = frozenset(((1, 0), (2, 0), (0, 1), (0, 2)))
    need(is_cap(cap), "chosen anchored cap is not a cap")
    first = {(0, 0, x, y) for x, y in cap}
    second = {(x, y, 0, 0) for x, y in cap}
    union = first | second
    need(len(union) == 8 and is_cap(union),
         "two perpendicular exceptional planes do not support an 8-cap")
    return union


def verify_packet():
    coefficients = Counter()
    support = set()
    weighted_raw = 0
    need(len(ROWS) == 34, "q9 row census")
    for weight, x, y, z, raw in ROWS:
        need(weight > 0, "nonpositive packet weight")
        need(all((x[j]+z[j]-2*y[j]) % Q == 0 for j in range(2)),
             "q9 row lost midpoint congruence")
        need(raw == sum((x[j]-z[j])**2 for j in range(2)) > 0,
             "q9 row raw cost")
        coefficients[x] += weight
        coefficients[z] += weight
        coefficients[y] -= 2*weight
        support.update((x, y, z))
        weighted_raw += weight*raw
    need(support == set(PACKET_SUPPORT) and support < set(K),
         "q9 active support binding")
    need(len(support) == 34 and set(K)-support == {(3, 4), (4, 4)},
         "q9 inactive square-ledger vertices")
    need(all(coefficients[p] == 0 for p in K),
         "q9 Farkas coefficients do not cancel")
    need(weighted_raw == 403824960, "q9 weighted raw-cost sum")
    return weighted_raw


CAP_A = frozenset(((1, 0), (2, 0), (0, 1), (0, 2)))
CAP_B = frozenset(((1, 0), (2, 0), (1, 1), (2, 2)))


def selector():
    """A q9-box selector with four cap boxes in every H_3 fibre."""
    chosen = set()
    signatures = set()
    for residue in F3:
        cap = CAP_A if residue == (0, 0) else CAP_B
        need(is_cap(cap), "selector fibre is not a cap")
        signatures.add(cap_signature(cap)[1])
        for high in cap:
            chosen.add((residue[0]+3*high[0], residue[1]+3*high[1]))
    need(len(chosen) == 36 and len(signatures) == 2,
         "selector census/direction variation")
    for residue in F3:
        fibre = frozenset(((x-residue[0])//3, (y-residue[1])//3)
                          for x, y in chosen
                          if (x % 3, y % 3) == residue)
        need(len(fibre) == 4 and is_cap(fibre), "bad H_3 selector fibre")
    return frozenset(chosen), signatures


def mat_point(matrix, point, translation=(0, 0)):
    a, b, c, d = matrix
    x, y = point
    return ((a*x+b*y+translation[0]) % Q,
            (c*x+d*y+translation[1]) % Q)


def affine_automorphism_audit(chosen):
    matrices = tuple(m for m in product(range(Q), repeat=4)
                     if gcd((m[0]*m[3]-m[1]*m[2]) % Q, Q) == 1)
    need(len(matrices) == 3888, "GL(2,Z/9Z) census")
    comparisons = 0
    constant_direction_checks = 0
    for matrix in matrices:
        full_image = frozenset(mat_point(matrix, p) for p in K)
        base_image = frozenset(mat_point(matrix, p) for p in PACKET_SUPPORT)
        need(len(full_image) == 36 and len(base_image) == 34,
             "automorphic square image collapsed")
        for translation in product(range(Q), repeat=2):
            image = frozenset(((x+translation[0]) % Q,
                               (y+translation[1]) % Q)
                              for x, y in base_image)
            comparisons += 1
            need(not image <= chosen,
                 "selector contains an affine q9 active packet support")
            constant_direction_checks += 1
    need(comparisons == 3888*81 == constant_direction_checks,
         "affine square comparison census")
    return len(matrices), comparisons


def affine_endomorphism_probe(chosen):
    """Search even singular affine pushforwards for supports inside selector.

    This is stronger than the automorphism orbit normally meant by an affine
    copy.  A hit is reported rather than silently treated as impossible.
    """
    positive_maps = 0
    contained = []
    for matrix in product(range(Q), repeat=4):
        image = frozenset(mat_point(matrix, p) for p in PACKET_SUPPORT)
        positive = any(mat_point(matrix, x) != mat_point(matrix, z)
                       for _weight, x, _y, z, _raw in ROWS)
        if not positive:
            continue
        positive_maps += 1
        for translation in product(range(Q), repeat=2):
            shifted = frozenset(((x+translation[0]) % Q,
                                 (y+translation[1]) % Q) for x, y in image)
            if shifted <= chosen:
                contained.append((matrix, translation, len(shifted)))
                return positive_maps, tuple(contained)
    return positive_maps, tuple(contained)


def packet_projection_edges():
    """Push the exact packet through all affine maps with six-point image."""
    witnesses = {}
    six_image_matrices = 0
    for matrix in product(range(Q), repeat=4):
        base = frozenset(mat_point(matrix, point) for point in PACKET_SUPPORT)
        if len(base) != 6:
            continue
        six_image_matrices += 1
        for translation in product(range(Q), repeat=2):
            edge = frozenset(((x+translation[0]) % Q,
                              (y+translation[1]) % Q) for x, y in base)
            witnesses.setdefault(edge, (matrix, translation))
    need(len(witnesses) == 2916, "six-point packet-projection census")

    # Every stored support carries a literal pushed-forward Farkas packet.
    for edge, (matrix, translation) in witnesses.items():
        coefficients = Counter()
        support = set()
        positive_cost = 0
        for weight, x, y, z, _raw in ROWS:
            xx = mat_point(matrix, x, translation)
            yy = mat_point(matrix, y, translation)
            zz = mat_point(matrix, z, translation)
            need(all((xx[j]+zz[j]-2*yy[j]) % Q == 0 for j in range(2)),
                 "projected packet midpoint failure")
            coefficients[xx] += weight
            coefficients[zz] += weight
            coefficients[yy] -= 2*weight
            support.update((xx, yy, zz))
            positive_cost += weight*sum((xx[j]-zz[j])**2 for j in range(2))
        need(support == set(edge), "projected packet support mismatch")
        need(all(coefficients[point] == 0 for point in edge),
             "projected packet incidence mismatch")
        need(positive_cost > 0, "projected packet lost every endpoint cost")
    return frozenset(witnesses), six_image_matrices


def direct_scalar_edges():
    """Build all primitive-line edges from the six-row scalar certificate."""
    coefficients = Counter()
    scalar_support = set()
    weighted_raw = 0
    for weight, x, y, z, raw in SCALAR_ROWS:
        need((x+z-2*y) % Q == 0, "scalar q9 midpoint failure")
        need(raw == (x-z)**2 > 0, "scalar q9 raw cost")
        coefficients[x] += weight
        coefficients[z] += weight
        coefficients[y] -= 2*weight
        scalar_support.update((x, y, z))
        weighted_raw += weight*raw
    need(scalar_support == set(range(6)), "scalar packet support")
    need(all(coefficients[t] == 0 for t in scalar_support),
         "scalar packet incidence")
    need(weighted_raw == 54, "scalar packet weighted RHS")

    units = tuple(a for a in range(Q) if gcd(a, Q) == 1)
    patterns = {}
    for a in units:
        for b in range(Q):
            pattern = frozenset((a*t+b) % Q for t in scalar_support)
            patterns.setdefault(pattern, (a, b))
    need(len(patterns) == 27, "AGL(1,Z/9Z) scalar-pattern orbit")
    residue_balanced = frozenset(
        frozenset(t for residue in range(3) for t in choice[residue])
        for choice in product(*(tuple(combinations(range(residue, Q, 3), 2))
                                for residue in range(3))))
    need(frozenset(patterns) == residue_balanced,
         "scalar orbit is not every 2+2+2 pattern")

    witnesses = {}
    for vector in product(range(Q), repeat=2):
        if len({((k*vector[0]) % Q, (k*vector[1]) % Q)
                for k in range(Q)}) != Q:
            continue
        for origin in product(range(Q), repeat=2):
            for pattern, (a, b) in patterns.items():
                edge = frozenset(((origin[0]+t*vector[0]) % Q,
                                  (origin[1]+t*vector[1]) % Q)
                                 for t in pattern)
                witnesses.setdefault(edge, (origin, vector, a, b))
    need(len(witnesses) == 2916, "direct scalar-edge census")

    for edge, (origin, vector, a, b) in witnesses.items():
        incidence = Counter()
        support = set()
        positive = 0
        for weight, x, y, z, _raw in SCALAR_ROWS:
            def lift(t):
                parameter = (a*t+b) % Q
                return ((origin[0]+parameter*vector[0]) % Q,
                        (origin[1]+parameter*vector[1]) % Q)
            xx, yy, zz = lift(x), lift(y), lift(z)
            need(all((xx[j]+zz[j]-2*yy[j]) % Q == 0 for j in range(2)),
                 "embedded scalar midpoint failure")
            incidence[xx] += weight
            incidence[zz] += weight
            incidence[yy] -= 2*weight
            support.update((xx, yy, zz))
            positive += weight*sum((xx[j]-zz[j])**2 for j in range(2))
        need(support == set(edge), "embedded scalar support")
        need(all(incidence[point] == 0 for point in edge),
             "embedded scalar incidence")
        need(positive > 0, "embedded scalar packet lost positive cost")
    return frozenset(witnesses), len(patterns), weighted_raw


def primitive_line_edges():
    """All 2+2+2 six-subsets of primitive affine lines in Z/9Z squared."""
    subgroups = set()
    for vector in product(range(Q), repeat=2):
        subgroup = frozenset(((k*vector[0]) % Q, (k*vector[1]) % Q)
                             for k in range(Q))
        if len(subgroup) == Q:
            subgroups.add(subgroup)
    need(len(subgroups) == 12, "primitive direction census")

    lines = set()
    for subgroup in subgroups:
        for translate in product(range(Q), repeat=2):
            lines.add(frozenset(((x+translate[0]) % Q,
                                 (y+translate[1]) % Q)
                                for x, y in subgroup))
    need(len(lines) == 108, "primitive affine-line census")

    edges = set()
    grouped_lines = {}
    for line in lines:
        groups = {}
        for point in line:
            groups.setdefault((point[0] % 3, point[1] % 3), set()).add(point)
        need(len(groups) == 3 and set(map(len, groups.values())) == {3},
             "primitive line residue decomposition")
        base_line = tuple(sorted(groups))
        grouped_lines.setdefault(base_line, []).append(line)
        group_tuple = tuple(tuple(sorted(groups[key])) for key in base_line)
        for omitted in product(range(3), repeat=3):
            edge = frozenset(point for at, group in enumerate(group_tuple)
                             for j, point in enumerate(group) if j != omitted[at])
            need(len(edge) == 6, "geometric six-edge collapsed")
            edges.add(edge)
    need(len(grouped_lines) == 12
         and set(map(len, grouped_lines.values())) == {9},
         "q9 lines above AG(2,3) base lines")
    need(len(edges) == 2916, "geometric six-edge census")
    return (frozenset(edges),
            {base: tuple(sorted(line_group, key=lambda line: tuple(sorted(line))))
             for base, line_group in sorted(grouped_lines.items())})


KNOWN_34 = (4, 7, 8, 11, 14, 15, 24, 25, 30, 32, 33, 37, 39,
            40, 45, 47, 48, 52, 53, 57, 58, 60, 61, 62, 65, 66,
            67, 68, 70, 73, 76, 77, 78, 80)


def verify_known_34(edges):
    chosen = frozenset((encoded % Q, encoded // Q) for encoded in KNOWN_34)
    need(len(chosen) == 34, "known lower-bound set census")
    for residue in F3:
        fibre = frozenset(((x-residue[0])//3, (y-residue[1])//3)
                          for x, y in chosen
                          if (x % 3, y % 3) == residue)
        need(len(fibre) <= 4 and is_cap(fibre),
             "known lower-bound set violates a torsion fibre")
    need(all(not edge <= chosen for edge in edges),
         "known lower-bound set contains a projected packet")
    return chosen


def cap_normalizers(caps, edges):
    """Certify the WLOG normalization of the residue-zero four-cap."""
    matrices = tuple(matrix for matrix in product(range(3), repeat=4)
                     if (matrix[0]*matrix[3]-matrix[1]*matrix[2]) % 3)
    normalizers = []
    for cap in caps:
        witness = None
        for matrix in matrices:
            for translation in F3:
                image = frozenset((((matrix[0]*x+matrix[1]*y+translation[0]) % 3),
                                   ((matrix[2]*x+matrix[3]*y+translation[1]) % 3))
                                  for x, y in cap)
                if image == CAP_A:
                    witness = (matrix, translation)
                    break
            if witness is not None:
                break
        need(witness is not None, "cap has no affine normalizer")
        normalizers.append(witness)

    # Lift h -> A h+t to d -> A d+3t.  It fixes the residue-zero
    # fibre, sends the chosen cap there to CAP_A, and permutes all six-edges.
    for matrix, high_translation in normalizers:
        translation = (3*high_translation[0], 3*high_translation[1])
        transformed = frozenset(
            frozenset(mat_point(matrix, point, translation) for point in edge)
            for edge in edges)
        need(transformed == edges, "normalizer does not preserve packet edges")
    return tuple(normalizers)


def target36_exhaustion(caps, grouped_lines):
    """Solver-free complete CSP search over 54^9 cap assignments."""
    residues = tuple(F3)
    residue_index = {residue: i for i, residue in enumerate(residues)}
    cap_masks = {}
    for i, residue in enumerate(residues):
        masks = []
        for cap in caps:
            mask = 0
            for high in cap:
                point = (residue[0]+3*high[0], residue[1]+3*high[1])
                mask |= 1 << (point[0]+Q*point[1])
            masks.append(mask)
        cap_masks[i] = tuple(masks)

    line_masks = {}
    index_lines = {}
    for base_residues, lines in grouped_lines.items():
        base = tuple(sorted(residue_index[r] for r in base_residues))
        masks = tuple(sum(1 << (x+Q*y) for x, y in line) for line in lines)
        need(len(masks) == 9, "CSP lifted-line census")
        line_masks[base] = masks
        index_lines[base] = lines

    lines_for_variable = {i: [] for i in range(9)}
    for base in sorted(line_masks):
        for i in base:
            lines_for_variable[i].append(base)

    @lru_cache(None)
    def valid(base, cap0, cap1, cap2):
        values = (cap0, cap1, cap2)
        mask = 0
        for i, value in zip(base, values):
            mask |= cap_masks[i][value]
        # Within each residue fibre a cap meets a line at most twice.  Six
        # selected points on a lifted line are therefore exactly a forbidden
        # 2+2+2 projected-packet support.
        return all((mask & line_mask).bit_count() < 6
                   for line_mask in line_masks[base])

    @lru_cache(None)
    def allowed(base, variable, other0, value0, other1, value1):
        answer = 0
        for candidate in range(len(caps)):
            assignment = {variable: candidate, other0: value0, other1: value1}
            if valid(base, *(assignment[i] for i in base)):
                answer |= 1 << candidate
        return answer

    full_domain = (1 << len(caps))-1
    fixed = caps.index(CAP_A)
    nodes = 0
    completed = 0

    def search(assignment):
        nonlocal nodes, completed
        nodes += 1
        if len(assignment) == 9:
            completed += 1
            return tuple(assignment[i] for i in range(9))
        best_variable = None
        best_domain = None
        for variable in range(9):
            if variable in assignment:
                continue
            domain = full_domain
            for base in lines_for_variable[variable]:
                others = tuple(i for i in base if i != variable)
                if all(i in assignment for i in others):
                    domain &= allowed(base, variable,
                                      others[0], assignment[others[0]],
                                      others[1], assignment[others[1]])
            if not domain:
                return None
            if best_domain is None or domain.bit_count() < best_domain.bit_count():
                best_variable, best_domain = variable, domain
        for candidate in range(len(caps)):
            if (best_domain >> candidate) & 1:
                assignment[best_variable] = candidate
                result = search(assignment)
                if result is not None:
                    return result
                del assignment[best_variable]
        return None

    result = search({residue_index[(0, 0)]: fixed})
    need(result is None and completed == 0, "target-36 cap selector survived")
    need(nodes == 716176, "deterministic target-36 search ledger changed")
    return nodes, valid.cache_info(), allowed.cache_info()


def verify_h7_arithmetic():
    old_plane = Fraction(4, 9)
    new_plane = Fraction(35, 81)
    exceptional = Fraction(1, 72)
    beta0 = 2*exceptional*new_plane
    gate0 = Fraction(7, 24)**2/Fraction(7)
    need(old_plane == Fraction(36, 81), "old plane normalization")
    need(beta0 == Fraction(35, 2916), "new marker bound")
    need(gate0 == Fraction(7, 576), "h7 density gate")
    need(gate0-beta0 == Fraction(7, 46656), "h7 exact margin")

    epsilon = Fraction(1, 20000)
    sigma = Fraction(4, 3)*epsilon-2*epsilon**2
    beta = beta0+2*sigma
    gap = (Fraction(7, 24)-epsilon)**2/Fraction(7)-beta
    formula = Fraction(7, 46656)-Fraction(11, 4)*epsilon+Fraction(29, 7)*epsilon**2
    need(gap == formula == Fraction(25606141, 2041200000000) > 0,
         "h7 epsilon-window arithmetic")
    return beta0, gate0, gap


def main():
    caps = classify_caps()
    eight_cap = verify_double_plane_sharpness()
    weighted_raw = verify_packet()
    chosen, signatures = selector()
    matrices, comparisons = affine_automorphism_audit(chosen)
    positive_maps, singular_hits = affine_endomorphism_probe(chosen)
    need(singular_hits == (((0, 0, 0, 1), (4, 0), 6),),
         "expected six-point singular projection changed")
    projected_edges, six_image_matrices = packet_projection_edges()
    direct_edges, scalar_patterns, scalar_raw = direct_scalar_edges()
    geometric_edges, grouped_lines = primitive_line_edges()
    need(projected_edges == direct_edges == geometric_edges,
         "three constructions of primitive-line six-edges disagree")
    lower_bound = verify_known_34(geometric_edges)
    normalizers = cap_normalizers(caps, geometric_edges)
    nodes, valid_cache, allowed_cache = target36_exhaustion(caps, grouped_lines)
    beta0, gate0, epsilon_gap = verify_h7_arithmetic()
    print("PASS_H7_Q9_CAP_AUDIT")
    print(f"AG23_CAPS {len(caps)} anchors=9 caps_per_anchor=6 direction_pairs=6")
    print(f"DOUBLE_PLANE_CAP size={len(eight_cap)} old_bound_is_sharp")
    print(f"Q9_PACKET rows={len(ROWS)} active_support={len(PACKET_SUPPORT)}/36 weighted_raw={weighted_raw}")
    print(f"SELECTOR boxes={len(chosen)}/81 every_H3_fibre=4-cap direction_types={len(signatures)}")
    print(f"AFFINE_AUTOMORPHISMS matrices={matrices} comparisons={comparisons} contained=0")
    print(f"AFFINE_ENDOMORPHISM_PROBE positive_maps_scanned={positive_maps} hits={singular_hits}")
    print(f"SCALAR_PACKET rows={len(SCALAR_ROWS)} raw={scalar_raw} "
          f"AGL1_patterns={scalar_patterns}")
    print(f"SIX_POINT_PROJECTIONS matrices={six_image_matrices} edges={len(projected_edges)}")
    print("PRIMITIVE_LINES directions=12 lines=108 patterns_per_line=27 exact_projection_match")
    print(f"TARGET36_UNSAT nodes={nodes} normalizers={len(normalizers)} "
          f"valid_cache={valid_cache.currsize} allowed_cache={allowed_cache.currsize}")
    print(f"LOWER_BOUND projected_packet_independent_set={len(lower_bound)}")
    print(f"H7_BOUND beta={beta0} gate={gate0} margin={gate0-beta0}")
    print(f"EPSILON_WINDOW endpoint=1/20000 gap={epsilon_gap}")
    print("SCOPE full_affine_endomorphism_closure_closes_target36; "
          "invertible_square_orbit_alone_does_not")


if __name__ == "__main__":
    main()

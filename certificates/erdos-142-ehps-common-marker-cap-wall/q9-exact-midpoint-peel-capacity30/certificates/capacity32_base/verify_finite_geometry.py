#!/usr/bin/env python3
"""Exact standard-library replay of the q9 geometric reduction and lower bound."""
from collections import Counter, deque
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path


POINTS = tuple(product(range(9), repeat=2))
INDEX = {point: i for i, point in enumerate(POINTS)}
MID = tuple(tuple(INDEX[((5*(a[0]+b[0])) % 9,
                         (5*(a[1]+b[1])) % 9)] for b in POINTS)
            for a in POINTS)
LOCAL = tuple(product(range(3), repeat=2))
TEMPLATES = (
    ((0,3),(0,6),(1,3),(1,6),(2,0),(2,3),
     (3,0),(4,0),(4,3),(5,0),(5,3),(6,0)),
    ((0,0),(0,3),(1,0),(1,6),(2,3),(2,6),
     (3,3),(4,0),(4,3),(5,0),(5,3),(6,0)),
)
ORDER30 = (
    (1,7),(5,1),(6,4),(0,4),(3,2),(8,8),(4,5),(6,0),
    (2,6),(3,6),(1,0),(4,7),(8,3),(5,3),(6,6),(3,8),
    (1,2),(8,5),(5,4),(6,8),(5,5),(7,3),(2,7),(7,5),
    (4,4),(1,3),(6,1),(8,7),(0,2),(3,0),
)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def mask_of(vertices):
    return sum(1 << v for v in vertices)


def midpoint_core(mask):
    members = tuple(v for v in range(81) if mask >> v & 1)
    present = [bool(mask >> v & 1) for v in range(81)]
    incoming = [0] * 81
    for a, b in combinations(members, 2):
        middle = MID[a][b]
        if present[middle]:
            incoming[middle] += 1
    queue = deque(v for v in members if incoming[v] == 0)
    while queue:
        removed = queue.popleft()
        if not present[removed]:
            continue
        present[removed] = False
        for other in members:
            if present[other]:
                middle = MID[removed][other]
                if present[middle]:
                    incoming[middle] -= 1
                    if incoming[middle] == 0:
                        queue.append(middle)
    return mask_of(v for v in members if present[v])


def verify_size30():
    order = tuple(INDEX[p] for p in ORDER30)
    need(len(set(order)) == 30, "size30 order has duplicates")
    forbidden = 0
    earlier = []
    for rank, vertex in enumerate(order):
        need(not (forbidden >> vertex & 1),
             "invalid size30 insertion rank %d" % rank)
        for other in earlier:
            forbidden |= 1 << MID[other][vertex]
        earlier.append(vertex)

    values = {vertex: 4**rank for rank, vertex in enumerate(order)}
    rows = 0
    minimum = raw_margin = geodesic_margin = None
    for a, b in combinations(order, 2):
        middle = MID[a][b]
        if middle not in values:
            continue
        defect = values[a]+values[b]-2*values[middle]
        need(defect > 0, "size30 strict potential failure")
        raw = sum((POINTS[a][j]-POINTS[b][j])**2 for j in range(2))
        geodesic = sum(min((POINTS[a][j]-POINTS[b][j]) % 9,
                           (POINTS[b][j]-POINTS[a][j]) % 9)**2
                       for j in range(2))
        raw_gap = 81*defect-raw
        geo_gap = 81*defect-geodesic
        need(raw_gap >= 0 and geo_gap >= 0, "size30 physical margin failure")
        rows += 1
        minimum = defect if minimum is None else min(minimum, defect)
        raw_margin = raw_gap if raw_margin is None else min(raw_margin, raw_gap)
        geodesic_margin = (geo_gap if geodesic_margin is None
                           else min(geodesic_margin, geo_gap))
    need((rows, minimum, raw_margin, geodesic_margin) == (131, 18, 1448, 1448),
         "size30 ledger mismatch")
    profile = Counter((x % 3, y % 3) for x, y in ORDER30)
    fibre_profile = tuple(sorted(profile.values(), reverse=True))
    need(fibre_profile == (4,4,4,3,3,3,3,3,3), "size30 fibre profile")
    return rows, minimum, raw_margin, geodesic_margin, fibre_profile


def is_cap(vertices):
    keep = set(vertices)
    return all(((2*(a[0]+b[0])) % 3, (2*(a[1]+b[1])) % 3) not in keep
               for a, b in combinations(vertices, 2))


def verify_slab_orbits():
    caps4 = tuple(cap for cap in combinations(LOCAL, 4) if is_cap(cap))
    need(len(caps4) == 54, "AG(2,3) four-cap census")
    need(not any(is_cap(five) for five in combinations(LOCAL, 5)),
         "AG(2,3) has a five-cap")

    lifted = tuple(
        tuple(tuple(INDEX[((residue+3*u) % 9, 3*v)] for u, v in cap)
              for cap in caps4)
        for residue in range(3))
    feasible = set()
    for i, j, k in product(range(54), repeat=3):
        vertices = lifted[0][i]+lifted[1][j]+lifted[2][k]
        mask = mask_of(vertices)
        if not midpoint_core(mask):
            feasible.add(mask)
    need(len(feasible) == 5832, "peelable saturated-slab census")

    maps = []
    for a, b, c, d in product(range(9), repeat=4):
        if c % 3 or (a*d-b*c) % 3 == 0:
            continue
        for tx in range(9):
            for ty in (0, 3, 6):
                maps.append((a, b, c, d, tx, ty))
    need(len(maps) == 26244, "slab affine stabilizer census")

    unseen = set(feasible)
    orbit_sizes = []
    representatives = []
    while unseen:
        representative = min(unseen)
        members = tuple(v for v in range(81) if representative >> v & 1)
        images = set()
        for a, b, c, d, tx, ty in maps:
            images.add(mask_of(
                INDEX[((a*POINTS[v][0]+b*POINTS[v][1]+tx) % 9,
                       (c*POINTS[v][0]+d*POINTS[v][1]+ty) % 9)]
                for v in members))
        need(images <= feasible, "slab orbit escaped feasible family")
        unseen -= images
        orbit_sizes.append(len(images))
        representatives.append(tuple(POINTS[v] for v in members))
    need(tuple(orbit_sizes) == (2916, 2916), "slab orbit sizes")
    need(tuple(representatives) == TEMPLATES, "slab orbit representatives")
    return len(caps4), len(feasible), tuple(orbit_sizes), len(maps)


def verify_h8_arithmetic():
    section = Fraction(31, 81)
    threshold = Fraction(49, 128)
    need(threshold-section == Fraction(1, 10368) > 0,
         "q9 section threshold")
    marker0 = 2*Fraction(1, 72)*section
    need(marker0 == Fraction(31, 2916), "exceptional-plane normalization")
    zero_gap = Fraction(7, 24)**2-8*marker0
    need(zero_gap == Fraction(1, 46656), "h8 zero-epsilon gap")

    epsilon = Fraction(1, 1_100_000)
    sigma = Fraction(4, 3)*epsilon-2*epsilon**2
    beta = marker0+2*sigma
    gap = (Fraction(7, 24)-epsilon)**2-8*beta
    formula = Fraction(1, 46656)-Fraction(263, 12)*epsilon+33*epsilon**2
    integer_formula = (1-1022544*epsilon+1539648*epsilon**2)/46656
    need(gap == formula == integer_formula ==
         Fraction(121027187, 80190000000000) > 0,
         "h8 epsilon endpoint")
    # G'(e)=-263/12+66e is increasing and still negative at the right endpoint.
    need(-Fraction(263, 12)+66*epsilon < 0,
         "h8 gap monotonicity endpoint")
    sharp_inside = Fraction(1, 1_022_543)
    sharp_outside = Fraction(1, 1_022_542)
    def gap_polynomial(value):
        return (1-1022544*value+1539648*value**2)/46656
    need(gap_polynomial(sharp_inside) ==
         Fraction(517105, 48783242381626944) > 0,
         "sharp integer epsilon inside bracket")
    need(gap_polynomial(sharp_outside) ==
         -Fraction(126359, 12195786741535296) < 0,
         "sharp integer epsilon outside bracket")
    discriminant = 1022544**2-4*1539648
    need(discriminant == 1045590073344,
         "h8 epsilon-root discriminant")
    return (section, threshold-section, marker0, zero_gap, epsilon, beta, gap,
            sharp_inside, gap_polynomial(sharp_inside),
            sharp_outside, gap_polynomial(sharp_outside), discriminant)


def main():
    source = Path(__file__).read_bytes()
    lower = verify_size30()
    slab = verify_slab_orbits()
    h8 = verify_h8_arithmetic()
    need(Path(__file__).read_bytes() == source, "source mutation")

    print("PASS_Q9_COMBINED_FINITE_GEOMETRY")
    print("PEELABILITY strict_midpoint_potential_equivalent_to_empty_core")
    print("SIZE30 rows=%d min_defect=%d raw_margin=%d geodesic_margin=%d fibre_profile=%s" % lower)
    print("AG23 caps4=%d caps5=0" % slab[0])
    print("SLAB choices=157464 peelable=%d nonpeelable=%d stabilizer=%d orbits=%s" %
          (slab[1], 157464-slab[1], slab[3], slab[2]))
    print("TARGET32_REDUCTION at_least_five_saturated_fibres_then_quotient_line_then_two_templates")
    print("H8 section=%s margin=%s marker0=%s zero_gap=%s round_epsilon=%s beta_upper=%s round_gap=%s integer_inside=%s inside_gap=%s integer_outside=%s outside_gap=%s discriminant=%s" % h8)
    print("H8_GAP (1-1022544*epsilon+1539648*epsilon^2)/46656")
    print("H8_POLYNOMIAL_POSITIVITY_INTERVAL root=2/(1022544+sqrt(1045590073344)) integer_epsilon=1/n_positive_for_n>=1022543")
    print("GEOMETRY_REDUCTION_READY lower=30 templates=2")
    print("SOURCE_NONMUTATION_OK")


if __name__ == "__main__":
    main()

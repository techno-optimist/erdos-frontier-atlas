#!/usr/bin/env python3
"""Exact quotient-profile reduction for a hypothetical peelable q9 31-set."""

from collections import Counter
from itertools import combinations, product


QPTS = tuple(product(range(3), repeat=2))
QINDEX = {point: i for i, point in enumerate(QPTS)}
NORMAL_CAP = frozenset(QINDEX[p] for p in ((1, 0), (2, 0), (0, 1), (0, 2)))


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    lines = set()
    for base in QPTS:
        for vector in QPTS[1:]:
            lines.add(frozenset(QINDEX[((base[0] + k * vector[0]) % 3,
                                        (base[1] + k * vector[1]) % 3)]
                               for k in range(3)))
    need(len(lines) == 12, "AG(2,3) line census")

    caps = {frozenset(chosen) for chosen in combinations(range(9), 4)
            if not any(line <= set(chosen) for line in lines)}
    need(len(caps) == 54, "four-cap census")

    affine = set()
    for a, b, c, d, tx, ty in product(range(3), repeat=6):
        if (a * d - b * c) % 3 == 0:
            continue
        affine.add(tuple(QINDEX[((a * x + b * y + tx) % 3,
                                 (c * x + d * y + ty) % 3)]
                         for x, y in QPTS))
    need(len(affine) == 432, "AGL(2,3) census")
    orbit = {frozenset(mapping[v] for v in NORMAL_CAP) for mapping in affine}
    need(orbit == caps, "four-caps are not one affine orbit")

    profiles = []
    by_saturated = Counter()
    slab_profiles = 0
    cap_profiles = 0
    for profile in product(range(5), repeat=9):
        if sum(profile) != 31:
            continue
        saturated = frozenset(v for v, size in enumerate(profile) if size == 4)
        need(len(saturated) >= 4, "31-set has fewer than four saturated fibres")
        by_saturated[len(saturated)] += 1
        profiles.append(profile)
        if any(line <= saturated for line in lines):
            slab_profiles += 1
        else:
            need(len(saturated) == 4 and saturated in caps,
                 "non-slab saturated set is not a four-cap")
            need(set(profile[v] for v in range(9) if v not in saturated) == {3},
                 "non-slab residual fibres are not all size three")
            cap_profiles += 1
    need(len(profiles) == 1278, "profile census")
    need(by_saturated == Counter({4: 126, 5: 504, 6: 504, 7: 144}),
         "saturated-fibre histogram")
    need(slab_profiles == 1224 and cap_profiles == 54,
         "slab/cap profile census")

    print("PASS_Q9_SIZE31_QUOTIENT_PROFILE_REDUCTION")
    print("PROFILES total=1278 saturated_histogram=4:126,5:504,6:504,7:144")
    print("SLAB_PROFILES 1224")
    print("NONSLAB_PROFILES 54 all=4,4,4,4,3,3,3,3,3")
    print("AGL23 size=432 four_caps=54 orbit=1 normalized_cap=(+-e1,+-e2)")


if __name__ == "__main__":
    main()

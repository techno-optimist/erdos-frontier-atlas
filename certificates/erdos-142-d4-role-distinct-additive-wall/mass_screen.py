"""Exact mass screen for all 8^5 q=24 D4 role assignments."""
from __future__ import annotations

from itertools import combinations, product

Q = 24
ROLES = ("P1", "P2", "P3", "B", "K")
ROLE_INDEX = {role: i for i, role in enumerate(ROLES)}
WORDS = (
    ("P1", "K", "B"),
    ("B", "K", "P1"),
    ("P2", "B", "P2"),
    ("P3", "B", "B"),
    ("B", "B", "P3"),
)
THRESHOLD_COUNT = 4_741_632
TARGET = (7, 7, 7, 6, 7)


def tile() -> frozenset[tuple[int, int]]:
    out = set()
    for x, y in product(range(Q), repeat=2):
        s = x + y
        t1 = 2 * x >= Q and 6 * s > 4 * Q and 6 * s <= 7 * Q
        t2 = (
            2 * x >= Q
            and 2 * y < Q
            and 12 * s >= 14 * Q + 12
            and 12 * s <= 17 * Q
        )
        t3 = (
            2 * x < Q
            and 2 * y >= Q
            and 12 * s >= 14 * Q + 12
            and 12 * s <= 17 * Q
            and 2 * (2 * x + y) >= 3 * Q + 2
        )
        if t1 or t2 or t3:
            out.add((x, y))
    assert len(out) == 163
    return frozenset(out)


def d4_image(base: frozenset[tuple[int, int]], code: int) -> frozenset[tuple[int, int]]:
    out = set()
    for x, y in base:
        if code & 1:
            x = Q - 1 - x
        if code & 2:
            y = Q - 1 - y
        if code & 4:
            x, y = y, x
        out.add((x, y))
    return frozenset(out)


def main() -> None:
    base = tile()
    images = tuple(d4_image(base, code) for code in range(8))
    assert len(set(images)) == 8 and all(len(image) == 163 for image in images)

    # Every inclusion-exclusion coordinate needs only the intersection size of
    # a nonempty subset of the eight images. Precompute those 255 values.
    image_intersections = {}
    for mask in range(1, 1 << 8):
        chosen = [images[i] for i in range(8) if mask & (1 << i)]
        common = set(chosen[0])
        for image in chosen[1:]:
            common.intersection_update(image)
        image_intersections[mask] = len(common)

    # Compile the 31 five-cylinder inclusion-exclusion terms into subsets of
    # role indices for each physical coordinate.
    terms = []
    for size in range(1, 6):
        sign = 1 if size & 1 else -1
        for selected in combinations(range(5), size):
            coordinate_role_masks = []
            for coordinate in range(3):
                role_mask = 0
                for word_index in selected:
                    role_mask |= 1 << ROLE_INDEX[WORDS[word_index][coordinate]]
                coordinate_role_masks.append(role_mask)
            terms.append((sign, tuple(coordinate_role_masks)))
    assert len(terms) == 31

    maximum = -1
    maximizers = []
    passing = 0
    for assignment in product(range(8), repeat=5):
        role_intersections = {}
        for role_mask in range(1, 1 << 5):
            image_mask = 0
            for role_index in range(5):
                if role_mask & (1 << role_index):
                    image_mask |= 1 << assignment[role_index]
            role_intersections[role_mask] = image_intersections[image_mask]
        count = sum(
            sign
            * role_intersections[masks[0]]
            * role_intersections[masks[1]]
            * role_intersections[masks[2]]
            for sign, masks in terms
        )
        if count > THRESHOLD_COUNT:
            passing += 1
        if count > maximum:
            maximum = count
            maximizers = [assignment]
        elif count == maximum:
            maximizers.append(assignment)

    assert maximum == 21_653_735
    assert len(maximizers) == 16 and TARGET in maximizers
    assert passing == 32_760
    print("PASS_Q24_D4_MASS_SCREEN")
    print(f"assignments=32768 passing={passing} maximum={maximum} maximizers={len(maximizers)}")
    print(f"target={TARGET}")


if __name__ == "__main__":
    main()

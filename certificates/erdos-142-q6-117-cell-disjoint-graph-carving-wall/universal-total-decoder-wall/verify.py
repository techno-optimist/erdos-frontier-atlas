#!/usr/bin/env python3
"""Exact primary replay for the universal total deterministic decoder wall."""

from collections import Counter
from fractions import Fraction
from itertools import product
from math import lcm


Q0, R, Q = 6, 7, 42
BASE = ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3),
        (5, 0), (5, 1), (5, 2))
OFF = ((0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
       (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3))
SHAPE = ((2, 29), (8, 41), (14, 11), (20, 23),
         (26, 35), (32, 5), (38, 17))
PLAN = ((1, 0, 6), (0, 1, 2), (0, 2, 4), (1, 3, 5),
        (3, 4, 5), (4, 5, 6), (2, 6, 3))


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def then(first, second):
    """Apply transformation first, then transformation second."""
    return tuple(second[first[state]] for state in range(len(first)))


def rank(function):
    return len(set(function))


def power(function, exponent):
    result = tuple(range(len(function)))
    for _ in range(exponent):
        result = then(result, function)
    return result


def permutation_order_on_image(function, image):
    current = {state: function[state] for state in image}
    need(set(current.values()) == set(image), "restriction is not a permutation")
    order = 1
    for start in image:
        length = 1
        point = current[start]
        while point != start:
            point = current[point]
            length += 1
            need(length <= len(image), "permutation orbit failed to close")
        order = lcm(order, length)
    return order


def reconstruct_packet():
    coarse = tuple((a, b, (a + dx) % Q0, (b + dy) % Q0)
                   for a, b in BASE for dx, dy in OFF)
    need(len(coarse) == len(set(coarse)) == 117, "coarse support census")
    alphabet = {
        tuple(R * cell[j] + residual[j] for j in range(4))
        for cell in coarse for residual in product(range(R), repeat=4)
    }
    need(len(alphabet) == 280_917, "q42 full-box alphabet census")
    a, b = BASE[0]
    roles = tuple((R * a, R * b, (x + R * a) % Q, (y + R * b) % Q)
                  for x, y in SHAPE)
    need(len(set(roles)) == 7 and set(roles) <= alphabet, "packet membership")

    coefficient = Counter()
    geodesic = Fraction(0)
    raw = Fraction(0)
    for x, y, z in PLAN:
        need(all((roles[x][c] + roles[z][c] - 2 * roles[y][c]) % Q == 0
                 for c in range(4)), "physical packet midpoint")
        coefficient[x] += 1
        coefficient[z] += 1
        coefficient[y] -= 2
        for left, right in zip(roles[x], roles[z]):
            distance = (left - right) % Q
            distance = min(distance, Q - distance)
            geodesic += Fraction(distance * distance, Q * Q)
            raw += Fraction((left - right) * (left - right), Q * Q)
    need(set(coefficient) == set(range(7)) and not any(coefficient.values()),
         "packet incidence cancellation")
    need(geodesic == Fraction(11, 7), "packet intrinsic geodesic cost")
    need(raw == Fraction(16, 7), "packet raw canonical-coordinate cost")
    need(Fraction(len(alphabet), Q ** 4) == Fraction(13, 144), "rate")
    need(Fraction(13, 144) - Fraction(49, 576) == Fraction(1, 192),
         "rate margin")
    return roles, geodesic, raw


def exhaustive_sandwich_lemma(max_states=5):
    census = []
    for states in range(1, max_states + 1):
        identity = tuple(range(states))
        maps = tuple(product(range(states), repeat=states))
        idempotents = tuple(e for e in maps if then(e, e) == e)
        qualifying = 0
        max_order = 1
        for e in idempotents:
            image = frozenset(e)
            need(all(e[x] == x for x in image), "idempotent not identity on image")
            for transition in maps:
                sandwich = then(then(e, transition), e)
                need(rank(sandwich) <= rank(e), "sandwich rank exceeds idempotent")
                # This equality is exactly what minimum rank in the containing
                # transition monoid forces.  Exhaust every finite map shape
                # satisfying that implication.
                if rank(sandwich) != rank(e):
                    continue
                qualifying += 1
                restricted = tuple(sandwich[x] for x in image)
                need(set(restricted) == set(image), "full-rank restriction not onto")
                need(len(set(restricted)) == len(image), "restriction not one-to-one")
                max_order = max(max_order,
                                permutation_order_on_image(sandwich, image))
        need(identity in idempotents, "identity idempotent missing")
        census.append((states, len(maps), len(idempotents), qualifying, max_order))
    return tuple(census)


def generated_monoid(generators):
    states = len(generators[0])
    identity = tuple(range(states))
    monoid = {identity}
    frontier = [identity]
    while frontier:
        left = frontier.pop()
        for generator in generators:
            for value in (then(left, generator), then(generator, left)):
                if value not in monoid:
                    monoid.add(value)
                    frontier.append(value)
    return frozenset(monoid)


def four_state_word_instance(geodesic_cost, raw_cost):
    # This monoid is transitive, nonsynchronizing, and nonpermutation.  It
    # preserves the two blocks {0,1}|{2,3} up to swapping.
    within_swap = (1, 0, 3, 2)
    block_swap = (2, 3, 0, 1)
    collapse = (0, 0, 2, 2)
    monoid = generated_monoid((within_swap, block_swap, collapse))
    need(any(rank(f) < 4 for f in monoid), "example lacks nonpermutation")
    minimum_rank = min(rank(f) for f in monoid)
    need(minimum_rank == 2, "example unexpectedly synchronizes")
    need(all(any(f[source] == target for f in monoid) for source in range(4)
             for target in range(4)), "example is not transitive")

    min_idempotents = tuple(f for f in monoid
                            if rank(f) == minimum_rank and then(f, f) == f)
    need(min_idempotents, "minimum-rank idempotent missing")
    e = min_idempotents[0]
    image = frozenset(e)
    role_maps = (within_swap, block_swap, collapse,
                 then(within_swap, block_swap),
                 then(block_swap, collapse),
                 then(collapse, within_swap),
                 then(then(within_swap, block_swap), collapse))
    need(all(t in monoid for t in role_maps), "role code left monoid")
    orders = []
    for transition in role_maps:
        sandwich = then(then(e, transition), e)
        need(rank(sandwich) == minimum_rank, "minimum-rank sandwich")
        orders.append(permutation_order_on_image(sandwich, image))
    common_order = lcm(*orders)
    start = 3
    point = e[start]
    endpoints = []
    for transition in role_maps:
        state = point
        for _ in range(common_order):
            state = e[transition[state]]  # physical chunk: role, then word u
        endpoints.append(state)
    need(set(endpoints) == {point}, "seven word endpoints did not synchronize")
    need(common_order * geodesic_cost > 0, "geodesic word wall cost")
    need(common_order * raw_cost > 0, "raw word wall cost")
    return len(monoid), minimum_rank, len(min_idempotents), common_order


def main():
    roles, geodesic_cost, raw_cost = reconstruct_packet()
    census = exhaustive_sandwich_lemma()
    example = four_state_word_instance(geodesic_cost, raw_cost)
    print("Q42_PACKET",
          f"actual_roles={roles}",
          f"geodesic_cost={geodesic_cost}",
          f"raw_cost={raw_cost}")
    print("SANDWICH_CENSUS", census)
    print("FOUR_STATE_INSTANCE",
          f"monoid_size={example[0]}",
          f"minimum_rank={example[1]}",
          f"minimum_idempotents={example[2]}",
          f"common_order={example[3]}",
          f"geodesic_cost={example[3] * geodesic_cost}",
          f"raw_cost={example[3] * raw_cost}")
    print("PASS_UNIVERSAL_TOTAL_DECODER_WALL")


if __name__ == "__main__":
    main()

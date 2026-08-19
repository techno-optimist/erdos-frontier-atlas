#!/usr/bin/env python3
"""Independent exact replay for live Perron SCCs of sizes one through four."""
from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

BLUE, RED = 263_277, 17_640
GATE = Fraction(1_058_841, 4)
UNDEFINED = -1


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def strongly_connected(delta, states):
    for start in range(states):
        seen, todo = {start}, [start]
        while todo:
            source = todo.pop()
            for target in delta[2*source:2*source+2]:
                if target >= 0 and target not in seen:
                    seen.add(target)
                    todo.append(target)
        if len(seen) != states:
            return False
    return True


def determinant(matrix):
    size = len(matrix)
    answer = 0
    for permutation in permutations(range(size)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(size) for j in range(i+1, size))
        term = 1
        for row in range(size):
            term *= matrix[row][permutation[row]]
        answer += -term if inversions & 1 else term
    return answer


def weighted_matrix(delta, states):
    matrix = [[0]*states for _ in range(states)]
    for source in range(states):
        for bit, weight in ((0, BLUE), (1, RED)):
            target = delta[2*source+bit]
            if target >= 0:
                matrix[source][target] += weight
    return tuple(tuple(row) for row in matrix)


def rate_above(matrix, scalar):
    numerator, denominator = scalar.numerator, scalar.denominator
    states = len(matrix)
    for size in range(1, states+1):
        for subset in combinations(range(states), size):
            minor = tuple(tuple((numerator if i == j else 0)
                                - denominator*matrix[subset[i]][subset[j]]
                                for j in range(size))
                          for i in range(size))
            if determinant(minor) < 0:
                return True
    return False


def successors(delta, counts, active):
    states = len(counts)
    answer = set()
    for bit in (0, 1):
        image = [0]*states
        for source, multiplicity in enumerate(counts):
            if not multiplicity:
                continue
            target = delta[2*source+bit]
            if target < 0:
                break
            image[target] += multiplicity
        else:
            answer.add((tuple(image), active))

    for selected, selected_count in enumerate(counts):
        if not selected_count:
            continue
        red_target = delta[2*selected+1]
        if red_target < 0:
            continue
        image = [0]*states
        for source, multiplicity in enumerate(counts):
            blue_multiplicity = multiplicity-int(source == selected)
            if not blue_multiplicity:
                continue
            blue_target = delta[2*source]
            if blue_target < 0:
                break
            image[blue_target] += blue_multiplicity
        else:
            image[red_target] += 1
            answer.add((tuple(image), True))
    return answer


def singleton_horizons(delta, states, start):
    initial = (tuple(7 if state == start else 0 for state in range(states)), False)
    queue = deque([initial])
    distance = {initial: 0}
    horizons = {}
    while queue:
        counts, active = queue.popleft()
        level = distance[(counts, active)]
        if active:
            support = tuple(state for state, count in enumerate(counts) if count)
            if len(support) == 1:
                horizons.setdefault(support[0], level)
                if len(horizons) == states:
                    return horizons, len(distance)
        for nxt in successors(delta, counts, active):
            if nxt not in distance:
                distance[nxt] = level+1
                queue.append(nxt)
    return horizons, len(distance)


EXPECTED = {
    1: (4, 4, 1, 1, Counter({1: 1})),
    2: (81, 25, 17, 15, Counter({1: 8, 2: 32, 3: 22, 4: 6})),
    3: (4096, 828, 644, 566,
        Counter({1: 288, 2: 1386, 3: 2148, 4: 1254,
                 5: 390, 6: 162, 7: 108, 8: 42, 9: 18})),
    4: (390625, 60654, 49662, 44370,
        Counter({1: 23112, 2: 119040, 3: 245520, 4: 228000,
                 5: 115800, 6: 40320, 7: 13152, 8: 5304,
                 9: 2232, 10: 720, 11: 216, 12: 312,
                 13: 360, 14: 264, 15: 168, 16: 72})),
}


def replay_size(states):
    tables = strong = above_blue = above_gate = 0
    horizon_histogram = Counter()
    max_search_states = 0
    for delta in product(range(-1, states), repeat=2*states):
        tables += 1
        if not strongly_connected(delta, states):
            continue
        strong += 1
        matrix = weighted_matrix(delta, states)
        blue = rate_above(matrix, Fraction(BLUE))
        gate = rate_above(matrix, GATE)
        above_gate += gate
        need(not gate or blue, "above-gate but not above-blue")
        if not blue:
            continue
        above_blue += 1
        for start in range(states):
            horizons, reached = singleton_horizons(delta, states, start)
            max_search_states = max(max_search_states, reached)
            need(len(horizons) == states,
                 f"lower live-SCC escape: {states=} {delta=} {start=}")
            horizon_histogram.update(horizons.values())
    expected = EXPECTED[states]
    need((tables, strong, above_blue, above_gate, horizon_histogram) == expected,
         f"lower live-SCC census {states=}")
    return (tables, strong, above_blue, above_gate,
            sum(horizon_histogram.values()),
            tuple(sorted(horizon_histogram.items())), max_search_states)


def main():
    source_before = Path(__file__).read_bytes()
    outputs = {states: replay_size(states) for states in range(1, 5)}
    need(GATE-BLUE == Fraction(5733, 4), "gate gap")
    need(Path(__file__).read_bytes() == source_before, "source mutation")
    for states, output in outputs.items():
        print("LOWER_LIVE_SCC", states, output)
    print("PASS_LOWER_ONE_THROUGH_FOUR_LIVE_SCC_WALL")
    print("RATE_SCOPE accepted_language_limsup_equals_rho_of_reachable_coaccessible_trim")
    print("AMBIENT_DEAD_SINK_RHO_EXCLUDED")
    print("SOURCE_NONMUTATION_OK")


if __name__ == "__main__":
    main()

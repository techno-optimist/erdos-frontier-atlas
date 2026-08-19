#!/usr/bin/env python3
"""Independent lower-SCC, live-rate scope, and full q42 physical audit."""

from collections import Counter, deque
from fractions import Fraction
from itertools import combinations, permutations, product


BLUE, RED = 263_277, 17_640
GATE = Fraction(1_058_841, 4)
Q = 42
UNDEFINED = -1
ROLES = ((21, 14, 23, 1), (21, 14, 29, 13), (21, 14, 35, 25),
         (21, 14, 41, 37), (21, 14, 5, 7), (21, 14, 11, 19),
         (21, 14, 17, 31))
PLAN = ((1, 0, 6), (0, 1, 2), (0, 2, 4), (1, 3, 5),
        (3, 4, 5), (4, 5, 6), (2, 6, 3))
EXPECTED_CARRIES = (
    ((0, 0, 0, 1), (0, 0, 0, 0), (0, 0, -1, -1),
     (0, 0, -1, -1), (0, 0, 1, 1), (0, 0, 0, 0), (0, 0, 1, 0)),
    ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, -1, -1),
     (0, 0, 1, 1), (0, 0, 0, 0), (0, 0, 0, -1), (0, 0, 0, 1)),
    ((0, 0, 0, 0), (0, 0, -1, -1), (0, 0, 1, 1),
     (0, 0, 1, 0), (0, 0, 0, -1), (0, 0, 0, 1), (0, 0, -1, 0)),
    ((0, 0, -1, -1), (0, 0, 1, 1), (0, 0, 1, 0),
     (0, 0, 0, -1), (0, 0, 0, 1), (0, 0, 0, 0), (0, 0, -1, 0)),
    ((0, 0, 1, 1), (0, 0, 0, 0), (0, 0, 0, -1),
     (0, 0, 0, 1), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, -1, -1)),
    ((0, 0, 0, 0), (0, 0, 0, -1), (0, 0, 0, 1),
     (0, 0, 0, 1), (0, 0, 0, 0), (0, 0, -1, -1), (0, 0, 1, 0)),
    ((0, 0, 0, -1), (0, 0, 0, 1), (0, 0, 0, 1),
     (0, 0, -1, -1), (0, 0, -1, -1), (0, 0, 1, 1), (0, 0, 1, 0)),
)


def need(condition, note):
    if not condition:
        raise AssertionError(note)


def strongly_connected(delta, states):
    for start in range(states):
        reached, pending = {start}, [start]
        while pending:
            source = pending.pop()
            for target in delta[2 * source:2 * source + 2]:
                if target >= 0 and target not in reached:
                    reached.add(target)
                    pending.append(target)
        if len(reached) != states:
            return False
    return True


def determinant(matrix):
    size = len(matrix)
    answer = 0
    for permutation in permutations(range(size)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(size) for j in range(i + 1, size))
        term = 1
        for row in range(size):
            term *= matrix[row][permutation[row]]
        answer += -term if inversions & 1 else term
    return answer


def weighted_matrix(delta, states):
    matrix = [[0] * states for _ in range(states)]
    for source in range(states):
        for bit, weight in ((0, BLUE), (1, RED)):
            target = delta[2 * source + bit]
            if target >= 0:
                matrix[source][target] += weight
    return tuple(tuple(row) for row in matrix)


def rate_above(matrix, threshold):
    numerator, denominator = threshold.numerator, threshold.denominator
    states = len(matrix)
    for size in range(1, states + 1):
        for subset in combinations(range(states), size):
            minor = tuple(tuple((numerator if row == column else 0)
                                - denominator * matrix[subset[row]][subset[column]]
                                for column in range(size))
                          for row in range(size))
            if determinant(minor) < 0:
                return True
    return False


def product_successors(delta, counts, active):
    states = len(counts)
    successors = set()
    for bit in (0, 1):
        image = [0] * states
        for source, count in enumerate(counts):
            if not count:
                continue
            target = delta[2 * source + bit]
            if target < 0:
                break
            image[target] += count
        else:
            successors.add((tuple(image), active))
    for selected, selected_count in enumerate(counts):
        if not selected_count:
            continue
        red_target = delta[2 * selected + 1]
        if red_target < 0:
            continue
        image = [0] * states
        for source, count in enumerate(counts):
            blue_count = count - int(source == selected)
            if not blue_count:
                continue
            blue_target = delta[2 * source]
            if blue_target < 0:
                break
            image[blue_target] += blue_count
        else:
            image[red_target] += 1
            successors.add((tuple(image), True))
    return successors


def singleton_horizons(delta, states, start):
    initial = (tuple(7 if state == start else 0 for state in range(states)), False)
    pending = deque([initial])
    distance = {initial: 0}
    horizons = {}
    while pending:
        counts, active = pending.popleft()
        level = distance[(counts, active)]
        support = [state for state, count in enumerate(counts) if count]
        if active and len(support) == 1:
            horizons.setdefault(support[0], level)
            if len(horizons) == states:
                return horizons, len(distance)
        for successor in product_successors(delta, counts, active):
            if successor not in distance:
                distance[successor] = level + 1
                pending.append(successor)
    return horizons, len(distance)


EXPECTED_LOWER = {
    1: (4, 4, 1, 1, Counter({1: 1}), 2),
    2: (81, 25, 17, 15, Counter({1: 8, 2: 32, 3: 22, 4: 6}), 10),
    3: (4096, 828, 644, 566,
        Counter({1: 288, 2: 1386, 3: 2148, 4: 1254,
                 5: 390, 6: 162, 7: 108, 8: 42, 9: 18}), 39),
    4: (390625, 60654, 49662, 44370,
        Counter({1: 23112, 2: 119040, 3: 245520, 4: 228000,
                 5: 115800, 6: 40320, 7: 13152, 8: 5304,
                 9: 2232, 10: 720, 11: 216, 12: 312,
                 13: 360, 14: 264, 15: 168, 16: 72}), 124),
}


def lower_scc_replay():
    outputs = {}
    for states in range(1, 5):
        tables = strong = above_blue = above_gate = max_reached = 0
        horizons = Counter()
        for delta in product(range(-1, states), repeat=2 * states):
            tables += 1
            if not strongly_connected(delta, states):
                continue
            strong += 1
            matrix = weighted_matrix(delta, states)
            blue = rate_above(matrix, Fraction(BLUE))
            gate = rate_above(matrix, GATE)
            above_gate += gate
            need(not gate or blue, "gate must imply blue")
            if not blue:
                continue
            above_blue += 1
            for start in range(states):
                found, reached = singleton_horizons(delta, states, start)
                need(len(found) == states, "lower SCC missing singleton witness")
                horizons.update(found.values())
                max_reached = max(max_reached, reached)
        result = (tables, strong, above_blue, above_gate, horizons, max_reached)
        need(result == EXPECTED_LOWER[states], f"lower SCC census {states}")
        outputs[states] = (tables, strong, above_blue, above_gate,
                           sum(horizons.values()), max_reached)
    return outputs


def dead_sink_scope_control():
    # Fixed start and sole accept are state 0. State 1 is reached by red and
    # loops forever, so it is reachable but cannot reach acceptance.
    delta = (0, 1, 1, 1)
    accepting = frozenset({0})
    forward = {0, 1}
    reverse_live = {0}
    need(delta[1] == 1 and delta[2:] == (1, 1), "dead-sink table")
    need(forward & reverse_live == {0} and 1 not in accepting, "live trim")
    ambient = weighted_matrix(delta, 2)
    need(ambient == ((BLUE, RED), (0, BLUE + RED)), "ambient matrix")
    need(rate_above(ambient, Fraction(BLUE)), "ambient rho above blue")
    mass = [1, 0]
    for horizon in range(1, 10):
        following = [0, 0]
        for source in range(2):
            for bit, weight in ((0, BLUE), (1, RED)):
                following[delta[2 * source + bit]] += mass[source] * weight
        mass = following
        need(mass[0] == BLUE ** horizon, "accepted-language mass")
    found, _ = singleton_horizons(delta, 2, 0)
    need(0 not in found, "blue-only accepted language must be safe")
    return (BLUE + RED, BLUE, ((BLUE,),))


def physical_replay():
    incidence = Counter()
    for left, middle, right in PLAN:
        incidence[left] += 1
        incidence[right] += 1
        incidence[middle] -= 2
    need(not any(incidence.values()), "role incidence cancellation")

    raw_costs, torus_costs, carry_ledgers = [], [], []
    for shift in range(7):
        shifted = tuple(ROLES[(role + shift) % 7] for role in range(7))
        raw = torus = Fraction(0)
        ledger = []
        for left, middle, right in PLAN:
            x, y, z = shifted[left], shifted[middle], shifted[right]
            displacement = tuple(x[c] + z[c] - 2 * y[c] for c in range(4))
            need(all(value % Q == 0 for value in displacement), "modular row")
            ledger.append(tuple(value // Q for value in displacement))
            for coordinate in range(4):
                difference = Fraction(x[coordinate] - z[coordinate], Q)
                raw += difference * difference
                residue = difference % 1
                torus += min(residue, 1 - residue) ** 2

        actual_rows = x_equals_z = 0
        for x, y, z in product(shifted, repeat=3):
            if all((x[c] + z[c] - 2 * y[c]) % Q == 0 for c in range(4)):
                actual_rows += 1
                if x == z:
                    x_equals_z += 1
                    need(x == y, "nontrivial x=z row")
        need((actual_rows, x_equals_z) == (49, 7), "actual row census")
        raw_costs.append(raw)
        torus_costs.append(torus)
        carry_ledgers.append(tuple(ledger))

    expected_raw = (Fraction(16, 7), Fraction(22, 7), Fraction(20, 7),
                    Fraction(24, 7), Fraction(22, 7), Fraction(18, 7),
                    Fraction(18, 7))
    need(tuple(raw_costs) == expected_raw, "raw canonical costs")
    need(tuple(torus_costs) == (Fraction(11, 7),) * 7, "torus costs")
    need(tuple(carry_ledgers) == EXPECTED_CARRIES, "all carry ledgers")
    return tuple(raw_costs), tuple(torus_costs), tuple(carry_ledgers)


def main():
    lower = lower_scc_replay()
    dead_sink = dead_sink_scope_control()
    raw, torus, carries = physical_replay()
    need(GATE - BLUE == Fraction(5733, 4), "gate gap")
    print("INDEPENDENT_LOWER_SCC", lower)
    print("INDEPENDENT_DEAD_SINK ambient_rho,accepted_rate,trim", dead_sink)
    print("INDEPENDENT_PHYSICAL_RAW", raw)
    print("INDEPENDENT_PHYSICAL_TORUS", torus)
    for shift, ledger in enumerate(carries):
        print("INDEPENDENT_PHYSICAL_CARRIES", shift, ledger)
    print("PASS_INDEPENDENT_LOWER_SCOPE_AND_FULL_Q42_PHYSICAL_AUDIT")


if __name__ == "__main__":
    main()

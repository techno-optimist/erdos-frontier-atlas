#!/usr/bin/env python3
"""Exact structural replay for the homogeneous q42 partial-decoder wall.

The proof has two branches.  An acyclic blue map admits an explicit positive
Collatz vector.  A cyclic blue map in a nontrivial strong table admits an
explicit seven-word multisunflower.  This replay exhausts every blue map
through seven states and every binary partial table through four states.
"""

from collections import deque
from itertools import combinations


BLUE = 263_277
RED = 17_640
BLUE_UNIT = 597
RED_UNIT = 40
MAX_CLOSED_STATES = 14
UNDEFINED = -1


def need(condition, note):
    if not condition:
        raise AssertionError(note)


def decode(code, length, states):
    base = states + 1
    values = []
    for _ in range(length):
        values.append(code % base - 1)
        code //= base
    need(code == 0, "table decode")
    return tuple(values)


def strongly_connected(table, states):
    forward = [[] for _ in range(states)]
    reverse = [[] for _ in range(states)]
    for source in range(states):
        for color in range(2):
            target = table[2 * source + color]
            if target >= 0:
                forward[source].append(target)
                reverse[target].append(source)

    def reaches_all(graph):
        seen = {0}
        queue = deque([0])
        while queue:
            source = queue.popleft()
            for target in graph[source]:
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        return len(seen) == states

    return reaches_all(forward) and reaches_all(reverse)


def blue_cycle(blue):
    """Return one directed blue cycle in its transition order, or ()."""
    states = len(blue)
    finished = [False] * states
    for initial in range(states):
        if finished[initial]:
            continue
        position = {}
        path = []
        state = initial
        while state >= 0 and not finished[state] and state not in position:
            position[state] = len(path)
            path.append(state)
            state = blue[state]
        if state >= 0 and state in position:
            return tuple(path[position[state]:])
        for state in path:
            finished[state] = True
    return ()


def acyclic_blue_potential(blue):
    """Return v=(I+A+...+A^(m-1))1 for an acyclic partial map."""
    need(not blue_cycle(blue), "potential requires acyclic blue")
    states = len(blue)
    potential = [0] * states

    def visit(source):
        if potential[source]:
            return potential[source]
        target = blue[source]
        potential[source] = 1 if target < 0 else 1 + visit(target)
        return potential[source]

    for state in range(states):
        visit(state)
    return tuple(potential)


def collatz_margin(table, states):
    blue = table[0::2]
    potential = acyclic_blue_potential(blue)
    margins = []
    for source in range(states):
        blue_target = table[2 * source]
        red_target = table[2 * source + 1]
        weighted_image = 0
        if blue_target >= 0:
            weighted_image += BLUE * potential[blue_target]
        if red_target >= 0:
            weighted_image += RED * potential[red_target]
        margins.append(BLUE * potential[source] - weighted_image)
    need(min(margins) > 0, "strict Collatz margin")
    return potential, tuple(margins)


def determinant(matrix):
    """Fraction-free Bareiss determinant over exact Python integers."""
    size = len(matrix)
    if size == 0:
        return 1
    work = [list(row) for row in matrix]
    sign = 1
    previous = 1
    for column in range(size - 1):
        pivot = next((row for row in range(column, size)
                      if work[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        value = work[column][column]
        for row in range(column + 1, size):
            for output in range(column + 1, size):
                numerator = (work[row][output] * value
                             - work[row][column] * work[column][output])
                need(numerator % previous == 0, "Bareiss exact division")
                work[row][output] = numerator // previous
        previous = value
    return sign * work[-1][-1]


def exact_rate_sign(table, states):
    """Compare rho(W) with BLUE via the exact principal-minor criterion."""
    z_matrix = [[0] * states for _ in range(states)]
    for source in range(states):
        z_matrix[source][source] = BLUE_UNIT
        blue_target = table[2 * source]
        red_target = table[2 * source + 1]
        if blue_target >= 0:
            z_matrix[source][blue_target] -= BLUE_UNIT
        if red_target >= 0:
            z_matrix[source][red_target] -= RED_UNIT

    full = None
    for count in range(1, states + 1):
        for subset in combinations(range(states), count):
            principal = [[z_matrix[row][column] for column in subset]
                         for row in subset]
            value = determinant(principal)
            if value < 0:
                return 1
            if count == states:
                full = value
    return 0 if full == 0 else -1


def shortest_word(table, states, start, target):
    parents = [None] * states
    parents[start] = (-1, -1)
    queue = deque([start])
    while queue and parents[target] is None:
        source = queue.popleft()
        for color in range(2):
            following = table[2 * source + color]
            if following >= 0 and parents[following] is None:
                parents[following] = (source, color)
                queue.append(following)
    need(parents[target] is not None, "strong path exists")
    word = []
    state = target
    while state != start:
        source, color = parents[state]
        word.append(color)
        state = source
    return tuple(reversed(word))


def apply_word(table, start, word):
    state = start
    for color in word:
        state = table[2 * state + color]
        need(state >= 0, "word transition defined")
    return state


def pure_blue_cycle_table(table, states, cycle):
    return (len(cycle) == states
            and all(table[2 * state + 1] < 0 for state in range(states)))


def construct_words(table, states, start, target):
    """Construct seven accepted words with column red counts in {0,1,7}."""
    cycle = blue_cycle(table[0::2])
    need(cycle, "witness requires blue cycle")
    need(not pure_blue_cycle_table(table, states, cycle),
         "equality table has no nondegenerate witness")
    cycle_set = set(cycle)
    if len(cycle) < states:
        candidates = [source for source in cycle
                      if table[2 * source + 1] not in cycle_set
                      and table[2 * source + 1] >= 0]
    else:
        candidates = [source for source in cycle
                      if table[2 * source + 1] >= 0]
    need(candidates, "strong table has red edge from blue cycle")
    anchor = candidates[0]
    red_target = table[2 * anchor + 1]
    return_word = shortest_word(table, states, red_target, anchor)
    loop = (1,) + return_word
    need(apply_word(table, anchor, loop) == anchor, "closed red loop")

    exceptional_block = loop * len(cycle)
    blue_block = (0,) * len(exceptional_block)
    need(apply_word(table, anchor, exceptional_block) == anchor,
         "exceptional block closes")
    need(apply_word(table, anchor, blue_block) == anchor,
         "blue phase block closes")

    prefix = shortest_word(table, states, start, anchor)
    suffix = shortest_word(table, states, anchor, target)
    ordinary = prefix + blue_block + suffix
    exceptional = prefix + exceptional_block + suffix
    words = (exceptional,) + (ordinary,) * 6
    need(all(apply_word(table, start, word) == target for word in words),
         "common accepted endpoint")
    red_counts = tuple(sum(word[column] for word in words)
                       for column in range(len(ordinary)))
    need(set(red_counts) <= {0, 1, 7}, "multisunflower columns")
    need(1 in red_counts, "nondegenerate unit column")
    need(len(ordinary) <= states * states + 2 * states - 2,
         "uniform horizon bound")
    return words


def blue_map_census():
    rows = []
    for states in range(1, 8):
        total = (states + 1) ** states
        acyclic = cyclic = maximum_height = 0
        for code in range(total):
            blue = decode(code, states, states)
            if blue_cycle(blue):
                cyclic += 1
            else:
                acyclic += 1
                potential = acyclic_blue_potential(blue)
                maximum_height = max(maximum_height, max(potential))
                for source, target in enumerate(blue):
                    image = 0 if target < 0 else potential[target]
                    need(potential[source] == image + 1,
                         "blue-tail potential identity")
        need(acyclic == (states + 1) ** (states - 1),
             "rooted-forest blue count")
        need(acyclic + cyclic == total, "blue-map partition")
        need(maximum_height == states, "sharp blue height")
        rows.append((states, total, acyclic, cyclic, maximum_height))
    return rows


def exhaustive_small_tables():
    expected_strong = {1: 4, 2: 25, 3: 828, 4: 60_654}
    rows = []
    for states in range(1, 5):
        total = (states + 1) ** (2 * states)
        strong = acyclic_below = cyclic_equal = cyclic_above = 0
        witnessed_pairs = maximum_horizon = 0
        for code in range(total):
            table = decode(code, 2 * states, states)
            if not strongly_connected(table, states):
                continue
            strong += 1
            cycle = blue_cycle(table[0::2])
            rate = exact_rate_sign(table, states)
            if not cycle:
                need(rate < 0, "acyclic exact rate below")
                potential, margins = collatz_margin(table, states)
                need(max(potential) <= states, "acyclic potential height")
                need(min(margins) >= BLUE - states * RED,
                     "uniform integer Collatz margin")
                acyclic_below += 1
            elif pure_blue_cycle_table(table, states, cycle):
                need(rate == 0, "pure blue cycle equality")
                cyclic_equal += 1
            else:
                need(rate > 0, "nontrivial cyclic-blue rate above")
                cyclic_above += 1
                for start in range(states):
                    for target in range(states):
                        words = construct_words(table, states, start, target)
                        witnessed_pairs += 1
                        maximum_horizon = max(maximum_horizon, len(words[0]))
        need(strong == expected_strong[states], "known strong-table count")
        need(strong == acyclic_below + cyclic_equal + cyclic_above,
             "strong structural trichotomy")
        # On a labeled state set there are (m-1)! spanning directed cycles.
        factorial = 1
        for value in range(2, states):
            factorial *= value
        need(cyclic_equal == factorial, "labeled blue-cycle equality count")
        need(witnessed_pairs == cyclic_above * states * states,
             "every cyclic-above start/target pair witnessed")
        rows.append((states, total, strong, acyclic_below, cyclic_equal,
                     cyclic_above, witnessed_pairs, maximum_horizon))
    return rows


def sharp_cutoff_control():
    need(BLUE == 441 * BLUE_UNIT and RED == 441 * RED_UNIT,
         "common weight factor")
    need(BLUE - MAX_CLOSED_STATES * RED == 16_317,
         "fourteen-state positive margin")
    need(BLUE - (MAX_CLOSED_STATES + 1) * RED == -1_323,
         "fifteen-state uniform margin fails")

    states = 15
    table = []
    for source in range(states):
        table.extend((source + 1 if source + 1 < states else UNDEFINED, 0))
    table = tuple(table)
    need(strongly_connected(table, states), "fifteen-state sharp control strong")
    need(not blue_cycle(table[0::2]), "fifteen-state sharp control acyclic")
    potential = acyclic_blue_potential(table[0::2])
    need(potential == tuple(range(states, 0, -1)),
         "fifteen-state chain potential")
    # P*R is rank one with nonzero eigenvalue 15, so at lambda=BLUE the
    # feedback factor is 15*RED/BLUE = 600/597 > 1.
    need(states * RED > BLUE, "fifteen-state feedback exceeds threshold")
    return states * RED_UNIT, BLUE_UNIT


def main():
    blue_rows = blue_map_census()
    small_rows = exhaustive_small_tables()
    feedback, threshold = sharp_cutoff_control()
    for row in blue_rows:
        print("BLUE_MAPS states=%d total=%d acyclic=%d cyclic=%d max_height=%d"
              % row)
    for row in small_rows:
        print("SMALL_TABLES states=%d total=%d strong=%d acyclic_below=%d "
              "cyclic_equal=%d cyclic_above=%d witnessed_pairs=%d "
              "max_horizon=%d" % row)
    print("STRUCTURAL_CUTOFF closed_states=14 margin=16317",
          f"next_chain_feedback={feedback}/{threshold}")
    print("PASS_EXACT_Q42_HOMOGENEOUS_PARTIAL_STRUCTURAL_CLOSURE")


if __name__ == "__main__":
    main()

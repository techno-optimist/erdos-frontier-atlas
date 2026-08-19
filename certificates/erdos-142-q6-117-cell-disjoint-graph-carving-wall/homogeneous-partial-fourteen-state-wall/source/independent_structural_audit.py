#!/usr/bin/env python3
"""Independent audit of the structural q42 partial-decoder closure.

This implementation does not import the primary verifier.  It uses Kahn
peeling for blue-cycle detection and a direct histogram-product BFS for all
strong partial tables through three states and for planted tables through
fourteen states.
"""

from collections import deque
from fractions import Fraction
from itertools import product


B = 263_277
R = 17_640
UNDEF = -1
COPIES = 7


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def splitmix64(value):
    value = (value + 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & ((1 << 64) - 1)
    return value ^ (value >> 31)


def decode_map(code, size):
    base = size + 1
    result = []
    for _ in range(size):
        result.append(code % base - 1)
        code //= base
    check(code == 0, "map decode exhausted")
    return tuple(result)


def peel_cycles(mapping):
    """Return vertices on directed cycles using indegree-zero Kahn peeling."""
    size = len(mapping)
    indegree = [0] * size
    for target in mapping:
        if target >= 0:
            indegree[target] += 1
    queue = deque(vertex for vertex in range(size) if indegree[vertex] == 0)
    removed = [False] * size
    while queue:
        vertex = queue.popleft()
        removed[vertex] = True
        target = mapping[vertex]
        if target >= 0:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return tuple(vertex for vertex in range(size) if not removed[vertex])


def tail_vector(mapping):
    check(not peel_cycles(mapping), "tail vector is acyclic only")
    size = len(mapping)
    answer = [None] * size
    for initial in range(size):
        if answer[initial] is not None:
            continue
        path = []
        vertex = initial
        while vertex >= 0 and answer[vertex] is None:
            path.append(vertex)
            vertex = mapping[vertex]
        height = 0 if vertex < 0 else answer[vertex]
        for vertex in reversed(path):
            height += 1
            answer[vertex] = height
    return tuple(answer)


def blue_audit():
    summaries = []
    for size in range(1, 8):
        acyclic_codes = []
        height_histogram = [0] * (size + 1)
        for code in range((size + 1) ** size):
            mapping = decode_map(code, size)
            if peel_cycles(mapping):
                continue
            heights = tail_vector(mapping)
            maximum = max(heights)
            height_histogram[maximum] += 1
            for source, target in enumerate(mapping):
                image = 0 if target < 0 else heights[target]
                check(heights[source] - image == 1, "tail recursion")
            # This is the exact worst row over every possible partial red map.
            check(B - R * maximum > 0, "seven-state worst red row margin")
            acyclic_codes.append(code)
        expected = (size + 1) ** (size - 1)
        check(len(acyclic_codes) == expected, "rooted-forest count")
        code_sum = sum(acyclic_codes)
        code_xor = 0
        for code in acyclic_codes:
            code_xor ^= splitmix64(code)
        summaries.append((size, expected, tuple(height_histogram[1:]),
                          code_sum, code_xor))
    return summaries


def reachable(graph, start):
    seen = {start}
    queue = deque([start])
    while queue:
        source = queue.popleft()
        for target in graph[source]:
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def strong(blue, red):
    size = len(blue)
    graph = [[] for _ in range(size)]
    reverse = [[] for _ in range(size)]
    for source in range(size):
        for target in (blue[source], red[source]):
            if target >= 0:
                graph[source].append(target)
                reverse[target].append(source)
    return (len(reachable(graph, 0)) == size
            and len(reachable(reverse, 0)) == size)


def histograms(size):
    output = []

    def visit(prefix, remaining):
        if len(prefix) == size - 1:
            output.append(tuple(prefix + [remaining]))
            return
        for amount in range(remaining + 1):
            visit(prefix + [amount], remaining - amount)

    visit([], COPIES)
    return tuple(output)


def histogram_action(histogram, blue, red, action):
    size = len(blue)
    image = [0] * size
    if action < 2:
        transition = blue if action == 0 else red
        for source, amount in enumerate(histogram):
            if not amount:
                continue
            target = transition[source]
            if target < 0:
                return None
            image[target] += amount
        return tuple(image)

    selected = action - 2
    if not histogram[selected] or red[selected] < 0:
        return None
    image[red[selected]] += 1
    for source, amount in enumerate(histogram):
        amount -= source == selected
        if not amount:
            continue
        target = blue[source]
        if target < 0:
            return None
        image[target] += amount
    return tuple(image)


def direct_product_complete(blue, red):
    size = len(blue)
    histogram_list = histograms(size)
    index = {histogram: number for number, histogram in enumerate(histogram_list)}
    pure = []
    for state in range(size):
        histogram = [0] * size
        histogram[state] = COPIES
        pure.append(index[tuple(histogram)])
    transitions = []
    for histogram in histogram_list:
        transitions.append(tuple(
            None if (image := histogram_action(histogram, blue, red, action)) is None
            else index[image]
            for action in range(size + 2)))

    for start in range(size):
        initial = pure[start]
        seen = {(initial, False)}
        queue = deque([(initial, False)])
        while queue:
            current, active = queue.popleft()
            for action, following in enumerate(transitions[current]):
                if following is None:
                    continue
                node = (following, active or action >= 2)
                if node not in seen:
                    seen.add(node)
                    queue.append(node)
        check(all((pure[target], True) in seen for target in range(size)),
              "cyclic-above table missing a direct product goal")


def pure_spanning_cycle(blue, red):
    cycle_vertices = peel_cycles(blue)
    return (len(cycle_vertices) == len(blue)
            and all(target < 0 for target in red))


def exhaustive_product_through_three():
    expected_strong = (4, 25, 828)
    rows = []
    for size in range(1, 4):
        maps = tuple(decode_map(code, size)
                     for code in range((size + 1) ** size))
        strong_count = cyclic_above = equality = 0
        for blue, red in product(maps, repeat=2):
            if not strong(blue, red):
                continue
            strong_count += 1
            if not peel_cycles(blue):
                continue
            if pure_spanning_cycle(blue, red):
                equality += 1
            else:
                cyclic_above += 1
                direct_product_complete(blue, red)
        check(strong_count == expected_strong[size - 1], "strong census")
        rows.append((size, strong_count, cyclic_above, equality))
    return rows


def shortest_colors(blue, red, start, target):
    size = len(blue)
    previous = [None] * size
    previous[start] = (-1, -1)
    queue = deque([start])
    while queue and previous[target] is None:
        source = queue.popleft()
        for color, following in enumerate((blue[source], red[source])):
            if following >= 0 and previous[following] is None:
                previous[following] = (source, color)
                queue.append(following)
    check(previous[target] is not None, "planted return path")
    word = []
    vertex = target
    while vertex != start:
        vertex, color = previous[vertex]
        word.append(color)
    return tuple(reversed(word))


def follow(mapping_pair, start, word):
    blue, red = mapping_pair
    vertex = start
    for color in word:
        vertex = (blue if color == 0 else red)[vertex]
        check(vertex >= 0, "planted word is defined")
    return vertex


def planted_all_sizes():
    checked_pairs = 0
    maximum_horizon = 0
    for size in range(1, 15):
        for cycle_length in range(1, size + 1):
            blue = [UNDEF] * size
            for source in range(cycle_length):
                blue[source] = (source + 1) % cycle_length
            red = [(source + 1) % size for source in range(size)]
            blue, red = tuple(blue), tuple(red)
            check(strong(blue, red), "planted union strong")
            cycle = tuple(range(cycle_length))
            candidates = ([cycle_length - 1] if cycle_length < size else [0])
            anchor = candidates[0]
            red_target = red[anchor]
            loop = (1,) + shortest_colors(blue, red, red_target, anchor)
            special_block = loop * cycle_length
            common_block = (0,) * len(special_block)
            check(follow((blue, red), anchor, special_block) == anchor,
                  "planted special block closes")
            check(follow((blue, red), anchor, common_block) == anchor,
                  "planted blue block closes")
            for start in range(size):
                for target in range(size):
                    prefix = shortest_colors(blue, red, start, anchor)
                    suffix = shortest_colors(blue, red, anchor, target)
                    special = prefix + special_block + suffix
                    common = prefix + common_block + suffix
                    check(follow((blue, red), start, special) == target,
                          "planted special endpoint")
                    check(follow((blue, red), start, common) == target,
                          "planted common endpoint")
                    counts = tuple(special[column] + 6 * common[column]
                                   for column in range(len(special)))
                    check(set(counts) <= {0, 1, 7} and 1 in counts,
                          "planted column pattern")
                    check(len(special) <= size * size + 2 * size - 2,
                          "planted horizon theorem")
                    checked_pairs += 1
                    maximum_horizon = max(maximum_horizon, len(special))
            if size == 7:
                direct_product_complete(blue, red)
    return checked_pairs, maximum_horizon


def cutoff_audit():
    for size in range(1, 15):
        check(B - size * R > 0, "closed-state Collatz margin")
    check(B - 14 * R == 16_317, "fourteen margin")
    check(B - 15 * R == -1_323, "fifteen sign reversal")
    feedback = Fraction(15 * R, B)
    check(feedback == Fraction(600, 597) > 1,
          "fifteen-state rank-one feedback")
    return feedback


def main():
    blue_rows = blue_audit()
    product_rows = exhaustive_product_through_three()
    planted_pairs, maximum_horizon = planted_all_sizes()
    feedback = cutoff_audit()
    for size, count, heights, code_sum, code_xor in blue_rows:
        print("AUDIT_BLUE", f"states={size}", f"acyclic={count}",
              f"height_hist={heights}", f"code_sum={code_sum}",
              f"code_xor={code_xor}")
    for size, strong_count, cyclic_above, equality in product_rows:
        print("AUDIT_PRODUCT", f"states={size}", f"strong={strong_count}",
              f"cyclic_above={cyclic_above}", f"equality={equality}")
    print("AUDIT_PLANTED", f"pairs={planted_pairs}",
          f"max_horizon={maximum_horizon}")
    print("AUDIT_CUTOFF", "states=14", "margin=16317",
          f"next_feedback={feedback}")
    print("PASS_INDEPENDENT_Q42_PARTIAL_STRUCTURAL_AUDIT")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent replay of every product-incomplete six-state orbit certificate."""

from collections import deque
from itertools import combinations, permutations
from pathlib import Path
import sys


MASK64 = (1 << 64) - 1
FNV_PRIME = 1_099_511_628_211
FNV_INITIAL = 1_469_598_103_934_665_603


def need(condition, note):
    if not condition:
        raise AssertionError(note)


def decode_table(code):
    table = [0] * 12
    original = code
    for position in range(11, -1, -1):
        table[position] = code % 7 - 1
        code //= 7
    need(code == 0, f"table code overflow {original}")
    return tuple(table)


def strongly_connected(table):
    for start in range(6):
        reached, pending = {start}, [start]
        while pending:
            state = pending.pop()
            for target in table[2 * state:2 * state + 2]:
                if target >= 0 and target not in reached:
                    reached.add(target)
                    pending.append(target)
        if len(reached) != 6:
            return False
    return True


PERMUTATIONS = {
    size: tuple(permutations(range(size))) for size in range(1, 7)
}


def determinant(matrix):
    size = len(matrix)
    answer = 0
    for permutation in PERMUTATIONS[size]:
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(size) for j in range(i + 1, size))
        term = 1
        for row in range(size):
            term *= matrix[row][permutation[row]]
        answer += -term if inversions & 1 else term
    return answer


def rate_compare_blue(table):
    z_matrix = [[0] * 6 for _ in range(6)]
    for state in range(6):
        z_matrix[state][state] = 597
        blue, red = table[2 * state:2 * state + 2]
        if blue >= 0:
            z_matrix[state][blue] -= 597
        if red >= 0:
            z_matrix[state][red] -= 40
    full = None
    for size in range(1, 7):
        for subset in combinations(range(6), size):
            minor = tuple(tuple(z_matrix[subset[row]][subset[column]]
                                for column in range(size))
                          for row in range(size))
            value = determinant(minor)
            if value < 0:
                return 1
            if size == 6:
                full = value
    return 0 if full == 0 else -1


def successors(table, counts, active):
    output = set()
    for bit in (0, 1):
        image = [0] * 6
        for state, count in enumerate(counts):
            if not count:
                continue
            target = table[2 * state + bit]
            if target < 0:
                break
            image[target] += count
        else:
            output.add((tuple(image), active))
    for selected, selected_count in enumerate(counts):
        if not selected_count:
            continue
        red_target = table[2 * selected + 1]
        if red_target < 0:
            continue
        image = [0] * 6
        for state, count in enumerate(counts):
            blue_count = count - int(state == selected)
            if not blue_count:
                continue
            blue_target = table[2 * state]
            if blue_target < 0:
                break
            image[blue_target] += blue_count
        else:
            image[red_target] += 1
            output.add((tuple(image), True))
    return output


def missing_pair_mask(table):
    mask = 0
    for start in range(6):
        initial = (tuple(7 if state == start else 0 for state in range(6)), False)
        pending = deque([initial])
        reached = {initial}
        pure_targets = set()
        while pending:
            counts, active = pending.popleft()
            if active:
                support = [state for state, count in enumerate(counts) if count]
                if len(support) == 1:
                    pure_targets.add(support[0])
            for successor in successors(table, counts, active):
                if successor not in reached:
                    reached.add(successor)
                    pending.append(successor)
        for target in range(6):
            if target not in pure_targets:
                mask |= 1 << (6 * start + target)
    return mask


def planted_controls():
    blue_cycle = tuple(value for state in range(6)
                       for value in ((state + 1) % 6, -1))
    need(strongly_connected(blue_cycle), "blue-cycle control strong")
    need(rate_compare_blue(blue_cycle) == 0, "blue-cycle equality")
    need(missing_pair_mask(blue_cycle) == (1 << 36) - 1,
         "blue-cycle incomplete control")
    above = list(blue_cycle)
    above[1] = 0
    above = tuple(above)
    need(rate_compare_blue(above) == 1, "above-blue control rate")
    need(missing_pair_mask(above) == 0, "above-blue control product")


def main():
    need(len(sys.argv) == 2, "usage: verify_six_boundary.py CERTIFICATE")
    planted_controls()
    lines = Path(sys.argv[1]).read_text(encoding="ascii").splitlines()
    need(len(lines) == 1641, "incomplete certificate line count")
    checksum = FNV_INITIAL
    code_sum = missing_total = below = equal = above = 0
    seen = set()
    equality_tables = []
    for line_number, line in enumerate(lines, 1):
        fields = line.split("\t")
        need(len(fields) == 3, f"certificate fields line {line_number}")
        code, claimed_mask, claimed_rate = map(int, fields)
        need(code not in seen, "duplicate incomplete orbit code")
        seen.add(code)
        table = decode_table(code)
        need(strongly_connected(table), "certificate table not strong")
        actual_mask = missing_pair_mask(table)
        actual_rate = rate_compare_blue(table)
        need(actual_mask == claimed_mask and actual_mask != 0,
             "incomplete product mismatch")
        need(actual_rate == claimed_rate and actual_rate <= 0,
             "boundary rate mismatch")
        checksum ^= code
        checksum = (checksum * FNV_PRIME) & MASK64
        checksum ^= claimed_mask
        checksum = (checksum * FNV_PRIME) & MASK64
        code_sum += code
        missing_total += claimed_mask.bit_count()
        below += actual_rate < 0
        equal += actual_rate == 0
        above += actual_rate > 0
        if actual_rate == 0:
            equality_tables.append(table)
    need((below, equal, above) == (1640, 1, 0), "boundary rate census")
    need(missing_total == 59076, "missing pair census")
    need(checksum == 9_776_710_376_808_584_319, "boundary checksum")
    need(code_sum == 1_041_120_840_919, "boundary code sum")
    expected_equality = tuple(value for state in range(6)
                              for value in ((state + 1) % 6, -1))
    need(equality_tables == [expected_equality], "unique equality orbit")
    print("INDEPENDENT_BOUNDARY",
          f"orbits={len(lines)} missing_pairs={missing_total}",
          f"below={below} equal={equal} above={above}",
          f"checksum={checksum} code_sum={code_sum}")
    print("PASS_INDEPENDENT_SIX_STATE_INCOMPLETE_BOUNDARY_REPLAY")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact structural verifier for the fifteen-state Hamiltonian-chain residual."""

from fractions import Fraction
from itertools import combinations, product


N = 15
COPIES = 7
BLUE_UNIT = 597
RED_UNIT = 40
THRESHOLD = Fraction(BLUE_UNIT, RED_UNIT)
U = -1
COMMON_BLUE = 0
COMMON_RED = 1


def need(condition, note):
    if not condition:
        raise AssertionError(note)


def blue_chain():
    return tuple(state + 1 if state + 1 < N else U for state in range(N))


def feedback(red):
    """Q=(I-A)^(-1)C; row i sums red rows with sources j>=i."""
    rows = []
    counts = [0] * N
    for source in range(N - 1, -1, -1):
        target = red[source]
        if target >= 0:
            counts[target] += 1
        rows.append(tuple(counts))
    return tuple(reversed(rows))


def matvec(matrix, vector):
    return tuple(sum(Fraction(entry) * value
                     for entry, value in zip(row, vector))
                 for row in matrix)


def collatz_leq(matrix, vector, bound):
    image = matvec(matrix, vector)
    need(all(value > 0 for value in vector), "positive Collatz vector")
    need(all(left <= bound * right for left, right in zip(image, vector)),
         "Collatz upper certificate")
    return image


def determinant(matrix):
    """Exact Bareiss determinant."""
    size = len(matrix)
    work = [list(row) for row in matrix]
    sign, previous = 1, Fraction(1)
    for column in range(size - 1):
        pivot = next((row for row in range(column, size)
                      if work[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        value = work[column][column]
        for row in range(column + 1, size):
            for output in range(column + 1, size):
                work[row][output] = (
                    work[row][output] * value
                    - work[row][column] * work[column][output]) / previous
        previous = value
    return sign * work[-1][-1]


def normalized_threshold_determinant(red):
    blue = blue_chain()
    matrix = [[Fraction(int(row == column)) for column in range(N)]
              for row in range(N)]
    epsilon = Fraction(RED_UNIT, BLUE_UNIT)
    for source in range(N):
        if blue[source] >= 0:
            matrix[source][blue[source]] -= 1
        if red[source] >= 0:
            matrix[source][red[source]] -= epsilon
    return determinant(matrix)


def spectral_partition():
    # A partial red map has Q row sums at most its support.  Thus support<=14
    # is uniformly below the threshold 597/40.
    need(Fraction(14) < THRESHOLD < 15, "threshold interval")

    # If at least two of the 15 total red transitions avoid the chain head,
    # this common vector handles every placement and every nonzero target.
    common = (Fraction(1),) + (Fraction(77, 80),) * (N - 1)
    need(15 - 2 * (1 - Fraction(77, 80)) == THRESHOLD,
         "two-nonhead row-zero equality")
    need(14 < THRESHOLD * Fraction(77, 80),
         "two-nonhead lower-row slack")
    # Exhaust the extremal q=2 layer; q>2 only lowers row zero further.
    q2_checked = 0
    for sources in combinations(range(N), 2):
        for targets in product(range(1, N), repeat=2):
            red = [0] * N
            for source, target in zip(sources, targets):
                red[source] = target
            collatz_leq(feedback(tuple(red)), common, THRESHOLD)
            q2_checked += 1
    need(q2_checked == 20_580, "q=2 exhaustive controls")

    # With exactly one nonhead target j>=2, lower only coordinate j.
    q1_high_checked = 0
    for source in range(N):
        for target in range(2, N):
            red = [0] * N
            red[source] = target
            vector = [Fraction(560, 597)] * N
            vector[0] = 1
            vector[target] = Fraction(37, 40)
            image = collatz_leq(feedback(tuple(red)), tuple(vector), THRESHOLD)
            need(image[0] == THRESHOLD, "unique-high row-zero equality")
            need(image[target] <= 13 < THRESHOLD * vector[target],
                 "unique-high special-row slack")
            q1_high_checked += 1
    need(q1_high_checked == 195, "q=1 high-target controls")

    # The only strict-above feedback maps are reset and one target-1 anomaly.
    critical = []
    reset = (0,) * N
    critical.append(reset)
    need(max(sum(row) for row in feedback(reset)) == 15,
         "reset feedback root")
    need(normalized_threshold_determinant(reset) < 0,
         "reset exact threshold sign")

    at_p_gt_zero = THRESHOLD**2 - 15 * THRESHOLD + 1
    at_p_zero = THRESHOLD**2 - 14 * THRESHOLD - 14
    need(at_p_gt_zero == Fraction(-191, 1600),
         "nonzero-source anomaly polynomial sign")
    need(at_p_zero == Fraction(-311, 1600),
         "source-zero anomaly polynomial sign")
    for source in range(N):
        red = [0] * N
        red[source] = 1
        red = tuple(red)
        critical.append(red)
        need(normalized_threshold_determinant(red) < 0,
             "one-target-1 exact threshold sign")

    need(len(critical) == 16 and len(set(critical)) == 16,
         "critical red maps")
    return tuple(critical), q2_checked, q1_high_checked


def apply_action(blue, red, histogram, active, action):
    image = [0] * N
    if action in (COMMON_BLUE, COMMON_RED):
        transition = blue if action == COMMON_BLUE else red
        for source, amount in enumerate(histogram):
            if not amount:
                continue
            target = transition[source]
            need(target >= 0, "common transition defined")
            image[target] += amount
        return tuple(image), active

    selected = action - 2
    need(histogram[selected] > 0 and red[selected] >= 0,
         "unit red transition defined")
    image[red[selected]] += 1
    for source, amount in enumerate(histogram):
        amount -= source == selected
        if not amount:
            continue
        target = blue[source]
        need(target >= 0, "unit-column ordinary blue defined")
        image[target] += amount
    return tuple(image), True


def reaches_zero_prefix(anomaly_source, start):
    if anomaly_source is None:
        return (COMMON_RED,)
    if anomaly_source == 0:
        return () if start == 0 else (COMMON_RED,)
    if anomaly_source == 1:
        return ((COMMON_BLUE, COMMON_RED) if start == 1
                else (COMMON_RED,))
    return ((COMMON_RED, COMMON_RED) if start == anomaly_source
            else (COMMON_RED,))


def explicit_actions(anomaly_source, start, target):
    prefix = reaches_zero_prefix(anomaly_source, start)
    unit_zero = 2
    if anomaly_source is None:
        core = (unit_zero, COMMON_RED)
        suffix = (COMMON_BLUE,) * target
    elif anomaly_source == 0:
        core = (unit_zero,)  # exceptional red and six blue copies all reach 1
        suffix = ((COMMON_RED,) if target == 0
                  else (COMMON_BLUE,) * (target - 1))
    elif anomaly_source == 1:
        # After the first unit column: one copy at 0 and six at 1.
        # A second unit at 0 sends the six ordinary copies to 2; red then
        # sends both occupied states to 0.
        core = (unit_zero, unit_zero, COMMON_RED)
        suffix = (COMMON_BLUE,) * target
    else:
        core = (unit_zero, COMMON_RED)
        suffix = (COMMON_BLUE,) * target
    return prefix + core + suffix


def explicit_product_witnesses(critical):
    blue = blue_chain()
    checked = maximum_horizon = 0
    horizon_histogram = {}
    for index, red in enumerate(critical):
        anomaly_source = None if index == 0 else index - 1
        expected = [0] * N
        if anomaly_source is not None:
            expected[anomaly_source] = 1
        need(red == tuple(expected), "critical ordering")
        for start in range(N):
            for target in range(N):
                histogram = [0] * N
                histogram[start] = COPIES
                histogram = tuple(histogram)
                active = False
                actions = explicit_actions(anomaly_source, start, target)
                red_counts = []
                for action in actions:
                    red_counts.append(0 if action == COMMON_BLUE
                                      else COPIES if action == COMMON_RED
                                      else 1)
                    histogram, active = apply_action(
                        blue, red, histogram, active, action)
                expected_histogram = [0] * N
                expected_histogram[target] = COPIES
                need(histogram == tuple(expected_histogram) and active,
                     "explicit active pure endpoint")
                need(set(red_counts) <= {0, 1, 7} and 1 in red_counts,
                     "explicit multisunflower columns")
                checked += 1
                maximum_horizon = max(maximum_horizon, len(actions))
                horizon_histogram[len(actions)] = (
                    horizon_histogram.get(len(actions), 0) + 1)
    need(checked == 16 * N * N, "critical pair count")
    need(maximum_horizon == 19, "construction horizon")
    return checked, maximum_horizon, tuple(sorted(horizon_histogram.items()))


def main():
    critical, q2_checked, q1_high_checked = spectral_partition()
    pairs, horizon, histogram = explicit_product_witnesses(critical)
    print("FIFTEEN_SPECTRAL_PARTITION",
          "partial_support_below_if_at_most=14",
          f"q2_controls={q2_checked}",
          f"q1_high_controls={q1_high_checked}",
          "critical_maps=16")
    print("FIFTEEN_CRITICAL_POLYNOMIALS",
          "reset_root=15",
          "source0=lambda^2-14lambda-14",
          "other=lambda^2-15lambda+1",
          "at_threshold=-311/1600,-191/1600")
    print("FIFTEEN_EXPLICIT_PRODUCTS", f"pairs={pairs}",
          f"max_horizon={horizon}", f"horizons={histogram}")
    print("PASS_EXACT_FIFTEEN_CHAIN_RESIDUAL_CLOSURE")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exhaustive small-DFA probe for the multiset-7 support screen.

For a complete deterministic binary automaton A, C_d is the family of length-d
binary words accepted by A.  The synchronized seven-fold reachability test is
exact for safety simultaneously at every length.  The enumeration fixes the
start state to 0 and covers every transition table and accepting-state set for
one, two, and three states (state renaming is deliberately not quotiented).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from itertools import product


X = Fraction(40, 597)
Y = Fraction(2401, 2388)


def globally_safe(delta: tuple[tuple[int, int], ...], accepting: frozenset[int]) -> bool:
    """Exact orbit-quotiented reachability in the synchronized 7-fold DFA."""
    start = ((0,) * 7, False)
    queue = deque([start])
    seen = {start}
    while queue:
        states, saw_singleton = queue.popleft()
        if saw_singleton and all(state in accepting for state in states):
            return False

        next_orbits: set[tuple[tuple[int, ...], bool]] = set()
        next_orbits.add((tuple(sorted(delta[state][0] for state in states)), saw_singleton))
        next_orbits.add((tuple(sorted(delta[state][1] for state in states)), saw_singleton))

        # An exactly-one column: by symmetry, it is enough to choose one
        # representative of each state value present in the orbit.
        for chosen_state in set(states):
            chosen = False
            image: list[int] = []
            for state in states:
                if state == chosen_state and not chosen:
                    image.append(delta[state][1])
                    chosen = True
                else:
                    image.append(delta[state][0])
            next_orbits.add((tuple(sorted(image)), True))

        for nxt in next_orbits:
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return True


def globally_safe_ordered(
    delta: tuple[tuple[int, int], ...], accepting: frozenset[int]
) -> bool:
    """Independent ordered-state replay, used exhaustively for q <= 2."""
    start = ((0,) * 7, False)
    queue = deque([start])
    seen = {start}
    while queue:
        states, saw_singleton = queue.popleft()
        if saw_singleton and all(state in accepting for state in states):
            return False
        columns = [(0,) * 7, (1,) * 7]
        columns.extend(tuple(int(i == chosen) for i in range(7)) for chosen in range(7))
        for column in columns:
            image = tuple(delta[state][bit] for state, bit in zip(states, column))
            nxt = (image, saw_singleton or sum(column) == 1)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return True


def weighted_sequence(
    delta: tuple[tuple[int, int], ...], accepting: frozenset[int], horizon: int
) -> tuple[Fraction, ...]:
    counts = [Fraction(0) for _ in delta]
    counts[0] = Fraction(1)
    answer: list[Fraction] = []
    for _d in range(horizon + 1):
        answer.append(sum((counts[q] for q in accepting), start=Fraction(0)))
        nxt = [Fraction(0) for _ in delta]
        for state, value in enumerate(counts):
            nxt[delta[state][0]] += value
            nxt[delta[state][1]] += value * X
        counts = nxt
    return tuple(answer)


def weighted_matrix(delta: tuple[tuple[int, int], ...]) -> tuple[tuple[Fraction, ...], ...]:
    matrix = [[Fraction(0) for _ in delta] for _ in delta]
    for q in range(len(delta)):
        matrix[q][delta[q][0]] += 1
        matrix[q][delta[q][1]] += X
    return tuple(tuple(row) for row in matrix)


def characteristic_polynomial(matrix: tuple[tuple[Fraction, ...], ...]) -> tuple[Fraction, ...]:
    """Coefficients in ascending powers for det(lambda I - M), q <= 3."""
    q = len(matrix)
    if q == 1:
        return (-matrix[0][0], Fraction(1))
    if q == 2:
        a, b = matrix[0]
        c, d = matrix[1]
        return (a * d - b * c, -(a + d), Fraction(1))
    if q == 3:
        trace = sum((matrix[i][i] for i in range(3)), start=Fraction(0))
        principal_two = (
            matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
            + matrix[0][0] * matrix[2][2] - matrix[0][2] * matrix[2][0]
            + matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]
        )
        determinant = (
            matrix[0][0]
            * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
            - matrix[0][1]
            * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
            + matrix[0][2]
            * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
        )
        return (-determinant, principal_two, -trace, Fraction(1))
    raise ValueError("the exhaustive certificate is implemented only for q <= 3")


def polynomial_divides(divisor: tuple[Fraction, ...], dividend: tuple[Fraction, ...]) -> bool:
    """Exact polynomial divisibility, coefficients in ascending powers."""
    remainder = list(dividend)
    divisor_degree = len(divisor) - 1
    while len(remainder) - 1 >= divisor_degree:
        factor = remainder[-1] / divisor[-1]
        shift = len(remainder) - len(divisor)
        for i, coefficient in enumerate(divisor):
            remainder[i + shift] -= factor * coefficient
        while remainder and remainder[-1] == 0:
            remainder.pop()
    return not remainder or all(coefficient == 0 for coefficient in remainder)


@dataclass(frozen=True)
class SequenceCertificate:
    label: str
    annihilator: tuple[Fraction, ...]
    values: tuple[Fraction, ...]  # Enough initial terms for q <= 3.


def certificate_catalog() -> tuple[SequenceCertificate, ...]:
    """Bounded exact sequences covering every safe minimal q <= 3 DFA.

    If P(E) annihilates a candidate sequence and P divides the DFA's
    characteristic polynomial, Cayley-Hamilton plus the first q terms proves
    equality for every length, not merely to a finite horizon.
    """
    candidates: list[SequenceCertificate] = []

    def add(label: str, annihilator: tuple[Fraction, ...], term) -> None:
        values = tuple(term(n) for n in range(4))
        assert all(Fraction(0) <= value <= 1 for value in values)
        candidates.append(SequenceCertificate(label, annihilator, values))

    add("zero", (Fraction(1),), lambda _n: Fraction(0))
    add("constant_one", (-Fraction(1), Fraction(1)), lambda _n: Fraction(1))
    add("geometric_x", (-X, Fraction(1)), lambda n: X**n)
    add("delta_zero", (Fraction(0), Fraction(1)), lambda n: Fraction(n == 0))

    alphabet = (Fraction(0), X, Fraction(1))
    for a0 in alphabet:
        for a1 in alphabet:
            add(
                f"finite2_{a0}_{a1}",
                (Fraction(0), Fraction(0), Fraction(1)),
                lambda n, a0=a0, a1=a1: a0 if n == 0 else a1 if n == 1 else Fraction(0),
            )
    for a0 in (Fraction(0), Fraction(1)):
        for tail in (X, Fraction(1)):
            add(
                f"constant_tail_{a0}_{tail}",
                (Fraction(0), -Fraction(1), Fraction(1)),
                lambda n, a0=a0, tail=tail: a0 if n == 0 else tail,
            )
            add(
                f"geometric_tail_{a0}_{tail}",
                (Fraction(0), -X, Fraction(1)),
                lambda n, a0=a0, tail=tail: a0 if n == 0 else tail * X ** (n - 1),
            )
    for ratio2 in (Fraction(1), X, X**2):
        for a0 in alphabet:
            for a1 in alphabet:
                add(
                    f"parity_{ratio2}_{a0}_{a1}",
                    (-ratio2, Fraction(0), Fraction(1)),
                    lambda n, ratio2=ratio2, a0=a0, a1=a1: (
                        a0 * ratio2 ** (n // 2)
                        if n % 2 == 0
                        else a1 * ratio2 ** ((n - 1) // 2)
                    ),
                )
    for scale in (X, Fraction(1)):
        add(
            f"scaled_derivative_{scale}",
            (X**2, -2 * X, Fraction(1)),
            lambda n, scale=scale: Fraction(0) if n == 0 else scale * n * X ** (n - 1),
        )

    return tuple(candidates)


def all_length_mass_certificate(
    delta: tuple[tuple[int, int], ...], accepting: frozenset[int]
) -> str | None:
    q = len(delta)
    actual = weighted_sequence(delta, accepting, q - 1)
    charpoly = characteristic_polynomial(weighted_matrix(delta))
    for candidate in certificate_catalog():
        if (
            candidate.values[:q] == actual
            and polynomial_divides(candidate.annihilator, charpoly)
        ):
            return candidate.label
    return None


def cardinality_sequence(
    delta: tuple[tuple[int, int], ...], accepting: frozenset[int], horizon: int
) -> tuple[int, ...]:
    counts = [0 for _ in delta]
    counts[0] = 1
    answer: list[int] = []
    for _d in range(horizon + 1):
        answer.append(sum(counts[q] for q in accepting))
        nxt = [0 for _ in delta]
        for state, value in enumerate(counts):
            nxt[delta[state][0]] += value
            nxt[delta[state][1]] += value
        counts = nxt
    return tuple(answer)


def accepted_words(
    delta: tuple[tuple[int, int], ...], accepting: frozenset[int], d: int
) -> tuple[str, ...]:
    words: list[str] = []
    for bits in product((0, 1), repeat=d):
        state = 0
        for bit in bits:
            state = delta[state][bit]
        if state in accepting:
            words.append("".join(map(str, bits)))
    return tuple(words)


def enumerate_dfas(states: int):
    for flat_delta in product(range(states), repeat=2 * states):
        delta = tuple((flat_delta[2 * q], flat_delta[2 * q + 1]) for q in range(states))
        for mask in range(1 << states):
            accepting = frozenset(q for q in range(states) if mask >> q & 1)
            yield delta, accepting


def canonical_minimal_dfa(
    delta: tuple[tuple[int, int], ...], accepting: frozenset[int]
) -> tuple[tuple[tuple[int, int], ...], frozenset[int]]:
    reachable = {0}
    queue = deque([0])
    while queue:
        q = queue.popleft()
        for nxt in delta[q]:
            if nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)

    block = {q: int(q in accepting) for q in reachable}
    while True:
        signatures = {
            q: (q in accepting, block[delta[q][0]], block[delta[q][1]]) for q in reachable
        }
        ordered = {sig: i for i, sig in enumerate(sorted(set(signatures.values())))}
        refined = {q: ordered[signatures[q]] for q in reachable}
        if all(refined[q] == block[q] for q in reachable):
            break
        block = refined

    quotient_blocks = sorted(set(block.values()))
    representative = {b: next(q for q in reachable if block[q] == b) for b in quotient_blocks}
    qdelta = {
        b: (block[delta[representative[b]][0]], block[delta[representative[b]][1]])
        for b in quotient_blocks
    }
    qaccept = {b for b in quotient_blocks if representative[b] in accepting}

    # Canonical breadth-first numbering from the start, with label order 0, 1.
    start = block[0]
    number = {start: 0}
    queue = deque([start])
    while queue:
        b = queue.popleft()
        for nxt in qdelta[b]:
            if nxt not in number:
                number[nxt] = len(number)
                queue.append(nxt)
    canonical_delta = [None] * len(number)
    for old, new in number.items():
        canonical_delta[new] = tuple(number[nxt] for nxt in qdelta[old])
    canonical_accept = frozenset(number[b] for b in qaccept)
    return tuple(canonical_delta), canonical_accept


def planted_controls() -> None:
    # One-state accept-all recognizes comparable words and is globally unsafe.
    assert not globally_safe(((0, 0),), frozenset({0}))

    # Exactly one 1 in a two-bit block, repeated blockwise, is represented here
    # only as a finite sample: the direct literal DFA test below catches the
    # simpler safe language 1* (one support per length).
    assert globally_safe(((1, 0), (1, 1)), frozenset({0}))  # language 1*

    # Exact-singleton language 0*10* is unsafe globally once d >= 7 because it
    # contains seven singleton supports.
    exact_singleton = ((0, 1), (1, 2), (2, 2))
    assert not globally_safe(exact_singleton, frozenset({1}))

    # Independently validate the orbit quotient on every complete q <= 2 DFA.
    for states in (1, 2):
        for delta, accepting in enumerate_dfas(states):
            assert globally_safe(delta, accepting) == globally_safe_ordered(delta, accepting)


def main() -> None:
    planted_controls()
    print("PASS_DFA_PLANTED_CONTROLS_AND_ORDERED_Q2_REPLAY")

    for states in (1, 2, 3):
        total = 0
        safe = 0
        max_mass = Fraction(0)
        max_cardinality_by_d = [0] * 97
        max_record = None
        any_above_one = False
        any_above_gate = False
        minimal_languages = set()
        for delta, accepting in enumerate_dfas(states):
            total += 1
            if not globally_safe(delta, accepting):
                continue
            safe += 1
            minimal_languages.add(canonical_minimal_dfa(delta, accepting))
            sequence = weighted_sequence(delta, accepting, 96)
            cardinalities = cardinality_sequence(delta, accepting, 96)
            max_cardinality_by_d = [
                max(old, new) for old, new in zip(max_cardinality_by_d, cardinalities)
            ]
            local_max = max(sequence)
            if local_max > max_mass:
                max_mass = local_max
                d = sequence.index(local_max)
                max_record = (delta, accepting, d, accepted_words(delta, accepting, min(d, 12)))
            any_above_one |= any(mass > 1 for mass in sequence)
            any_above_gate |= any(mass > Y**d for d, mass in enumerate(sequence))
        print(
            f"states={states} enumerated={total} globally_safe={safe} "
            f"distinct_minimal_languages={len(minimal_languages)} "
            f"max_mass_d<=96={float(max_mass):.12f} "
            f"above_one={any_above_one} above_gate={any_above_gate}"
        )
        if max_record is not None:
            delta, accepting, d, words = max_record
            print(f"  maximizer delta={delta} accepting={sorted(accepting)} d={d}")
            if d <= 12:
                print(f"  accepted_words={words}")
        print(f"  max_cardinality_d=0..16={max_cardinality_by_d[:17]}")
        print(f"  max_cardinality_d=96={max_cardinality_by_d[96]}")
        if states == 3:
            certificate_labels = set()
            for automaton in sorted(minimal_languages, key=repr):
                mdelta, maccepting = automaton
                label = all_length_mass_certificate(mdelta, maccepting)
                assert label is not None
                certificate_labels.add(label)
                print(f"  ALL_LENGTH_CERTIFICATE {label}: {automaton}")
            print(f"  distinct_certificate_forms={len(certificate_labels)}")
        assert not any_above_one
        assert not any_above_gate

    print("PASS_EXHAUSTIVE_COMPLETE_DFA_Q_LE_3_ALL_LENGTHS")


if __name__ == "__main__":
    main()

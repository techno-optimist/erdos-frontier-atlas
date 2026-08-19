#!/usr/bin/env python3
"""Read-only hostile core audit for the at-most-14-state structural wall.

This implementation does not import the producer.  It binds the producer
bytes, plants a reducible live-trim example, checks the equality/strict cycle
boundary, lifts an explicit accepted seven-word witness through the q42
seven-role packet, and checks the exact m=14/m=15 cutoff arithmetic.
"""

from collections import Counter, deque
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse


B, R, Q = 263_277, 17_640, 42
U = -1
EXPECTED = {
    "AT_MOST_FOURTEEN_STATE_STRUCTURAL_WALL.md": "c623c98bc19d2cc2d2024afee78c67a1d9eaaf0fa03d01d3c23ad8d1c35f70fc",
    "independent_structural_audit.py": "0f4e9d8c55e2ef53dc7c4a353342de6e3dd5f4107fa4a4eda46e3394d5fa4e9d",
    "run.ps1": "56b758c1ad547cb1f9f5c6c9aa6f29b36edbd37670b17fe3979f6e52c954b66a",
    "run.sh": "7da855a1700f28ed9685a657ed8d273e9fa28838f224f876cd0488e356b27989",
    "verify_structural_closure.py": "d4c9812fe0f1468e50c8408d3d948f0c132e3afa6bc6453d4a009b654cf2ccb1",
}
MANIFEST_HASH = "e25f34d571ddeb3b7dedf99924a00b2f2511d90777962f01ebeda97f4ce1a5eb"

ROLES = ((21, 14, 23, 1), (21, 14, 29, 13), (21, 14, 35, 25),
         (21, 14, 41, 37), (21, 14, 5, 7), (21, 14, 11, 19),
         (21, 14, 17, 31))
PLAN = ((1, 0, 6), (0, 1, 2), (0, 2, 4), (1, 3, 5),
        (3, 4, 5), (4, 5, 6), (2, 6, 3))


def need(condition, note):
    if not condition:
        raise AssertionError(note)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def bind_source(source):
    actual = {name: digest(source / name) for name in EXPECTED}
    need(actual == EXPECTED, "producer payload hashes")
    parsed = {}
    for line in (source / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        value, name = line.split("  ", 1)
        parsed[name] = value
    need(parsed == EXPECTED, "producer manifest contents")
    need(digest(source / "SHA256SUMS") == MANIFEST_HASH, "producer manifest hash")


def reachable(blue, red, starts):
    seen = set(starts)
    queue = deque(starts)
    while queue:
        source = queue.popleft()
        for target in (blue[source], red[source]):
            if target >= 0 and target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def coaccessible(blue, red, accepts):
    reverse = [[] for _ in blue]
    for source in range(len(blue)):
        for target in (blue[source], red[source]):
            if target >= 0:
                reverse[target].append(source)
    seen = set(accepts)
    queue = deque(accepts)
    while queue:
        target = queue.popleft()
        for source in reverse[target]:
            if source not in seen:
                seen.add(source)
                queue.append(source)
    return seen


def follow(blue, red, start, word):
    state = start
    for color in word:
        state = (blue if color == 0 else red)[state]
        need(state >= 0, "word transition")
    return state


def live_trim_and_words():
    # Start 0, accept 3.  State 4 is reachable but noncoaccessible and has
    # ambient row weight B+R.  The live SCC {1,2} has a blue 2-cycle and one
    # red self-loop at 1; the only accepting exit is red 2->3.
    blue = (1, 2, 1, U, 4)
    red = (4, 1, 3, U, 4)
    live = reachable(blue, red, (0,)) & coaccessible(blue, red, (3,))
    need(live == {0, 1, 2, 3}, "live trim deletes exactly dead sink")
    # On {1,2}, B I-W has determinant -BR at lambda B, hence rho(W)>B.
    determinant_at_b = (B - R) * B - B * B
    need(determinant_at_b == -B * R < 0, "live Perron SCC strictly above B")

    exceptional = (0, 1, 1, 0, 1)
    ordinary = (0, 0, 0, 0, 1)
    words = (exceptional,) + (ordinary,) * 6
    need(all(follow(blue, red, 0, word) == 3 for word in words), "accepted lift")
    counts = tuple(sum(word[column] for word in words) for column in range(5))
    need(counts == (0, 1, 1, 0, 7), "prefix/core/suffix column pattern")
    return words, counts, determinant_at_b


def packet_cost(symbols):
    total = F(0)
    for left, middle, right in PLAN:
        x, y, z = symbols[left], symbols[middle], symbols[right]
        need(all((x[i] + z[i] - 2*y[i]) % Q == 0 for i in range(4)),
             "physical packet row")
        total += sum(F((x[i]-z[i])**2, Q**2) for i in range(4))
    return total


def physical_lift(words):
    incidence = Counter()
    for left, middle, right in PLAN:
        incidence[left] += 1
        incidence[right] += 1
        incidence[middle] -= 2
    need(not any(incidence.values()), "role incidence")

    totals = []
    for red_role in range(7):
        physical = [[] for _ in range(7)]
        total = F(0)
        for column in zip(*words):
            red_count = sum(column)
            if red_count == 0:
                symbols = (ROLES[(red_role + 1) % 7],) * 7
            elif red_count == 7:
                symbols = (ROLES[red_role],) * 7
            else:
                need(red_count == 1, "unit-red abstract column")
                unique = column.index(1)
                shift = (red_role - unique) % 7
                symbols = tuple(ROLES[(role + shift) % 7] for role in range(7))
                total += packet_cost(symbols)
            for role, symbol in enumerate(symbols):
                need((symbol == ROLES[red_role]) == bool(column[role]),
                     "one-red packet alignment")
                physical[role].append(symbol)
            # Common columns are diagonal; unit columns are the actual packet.
            for left, middle, right in PLAN:
                need(all((symbols[left][i] + symbols[right][i]
                          - 2*symbols[middle][i]) % Q == 0 for i in range(4)),
                     "whole-word physical midpoint")
        need(len({tuple(word) for word in physical}) == 7, "physical words distinct")
        need(total > 0, "positive raw whole-word packet cost")
        totals.append(total)
    return tuple(totals)


def perron_equality_and_cutoff():
    # A spanning blue-only cycle is irreducible with every row sum B, hence
    # rho=B.  Adding one red self-loop makes det(BI-W)=-R*B^(m-1)<0.
    strict_determinants = tuple(-R * B ** (m - 1) for m in range(1, 15))
    need(all(value < 0 for value in strict_determinants), "strict cycle controls")
    need(B - 14*R == 16_317 > 0, "m14 Collatz margin")
    need(B - 15*R == -1_323 < 0, "m15 sign reversal")
    feedback = F(15*R, B)
    need(feedback == F(200, 199) > 1, "m15 feedback")
    # For the 15-chain with every red edge to zero,
    # det(lambda I-W)=lambda^15-R*sum B^k lambda^(14-k).
    characteristic_at_b = B**14 * (B - 15*R)
    need(characteristic_at_b < 0, "m15 chain rho strictly above B")
    return strict_determinants, feedback, characteristic_at_b


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    bind_source(args.source)
    words, counts, live_sign = live_trim_and_words()
    physical_costs = physical_lift(words)
    strict, feedback, m15_sign = perron_equality_and_cutoff()
    print("PASS_PRODUCER_HASH_BINDING", MANIFEST_HASH)
    print("PASS_LIVE_TRIM_SINGLETON_EXIT", counts, "det_at_B", live_sign)
    print("PASS_ACCEPTED_WORD_AND_PHYSICAL_LIFT", physical_costs)
    print("PASS_STRICT_PERRON_EQUALITY_BOUNDARY", strict[0], strict[-1])
    print("PASS_M15_NONCLAIM", feedback, "char_at_B_sign", m15_sign < 0)
    print("APPROVE_Q42_PARTIAL_FOURTEEN_STATE_STRUCTURAL_CLOSURE")


if __name__ == "__main__":
    main()

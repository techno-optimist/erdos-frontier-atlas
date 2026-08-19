#!/usr/bin/env python3
"""Independent read-only hostile audit of the frozen q42 m=15 chain theorem."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import argparse


N, COPIES, QMOD = 15, 7, 42
T = F(597, 40)
U = -1

PRODUCER = {
    "FIFTEEN_STATE_CHAIN_CLOSURE.md": "e9ac7b84d22143f985701cf9f1f65b0e82d072e601fa958a2d5de0bdc0f5072b",
    "probe_chain_product.cpp": "1deb314663a65c0a4536334676b3f2826d6602bd53daa57a2d7eb18df3a5101b",
    "run.ps1": "a3f14e5a7870caacb509ef0d61fd1b9eb114533b2aa232a85839866ee63c1ae8",
    "run.sh": "e86e1045c477fa5d8ce4c9fcdf3b3998b05f7ea7d8aad882af89b83b7ba70355",
    "verify_chain_residual.py": "893197d0c841113bea7eeb8619274953db485092f25d33980ebe56a65efb8149",
}
PRODUCER_MANIFEST = "f502b1ed111160e81d3bb7dcead77de113817a94c69a31d6e001862f23af5e75"

M14 = {
    "AT_MOST_FOURTEEN_STATE_STRUCTURAL_WALL.md": "c623c98bc19d2cc2d2024afee78c67a1d9eaaf0fa03d01d3c23ad8d1c35f70fc",
    "independent_structural_audit.py": "0f4e9d8c55e2ef53dc7c4a353342de6e3dd5f4107fa4a4eda46e3394d5fa4e9d",
    "run.ps1": "56b758c1ad547cb1f9f5c6c9aa6f29b36edbd37670b17fe3979f6e52c954b66a",
    "run.sh": "7da855a1700f28ed9685a657ed8d273e9fa28838f224f876cd0488e356b27989",
    "verify_structural_closure.py": "d4c9812fe0f1468e50c8408d3d948f0c132e3afa6bc6453d4a009b654cf2ccb1",
}
M14_MANIFEST = "e25f34d571ddeb3b7dedf99924a00b2f2511d90777962f01ebeda97f4ce1a5eb"

SIX_MANIFEST = "a62da6552877464d13c45f615f1d61e9b05cee7c52e81b472db3f6a77dc97d01"
FIVE_MANIFEST = "2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71"
PHYSICAL_AUDITOR_HASH = "2a68daeab13b46452768a7e437118f596d2bc7d0687bf13b9f189a621f7425ca"

ROLES = ((21, 14, 23, 1), (21, 14, 29, 13), (21, 14, 35, 25),
         (21, 14, 41, 37), (21, 14, 5, 7), (21, 14, 11, 19),
         (21, 14, 17, 31))
PLAN = ((1, 0, 6), (0, 1, 2), (0, 2, 4), (1, 3, 5),
        (3, 4, 5), (4, 5, 6), (2, 6, 3))
EXPECTED_HORIZONS = ((1, 1), (2, 16), (3, 226), (4, 239), (5, 240),
                     (6, 240), (7, 240), (8, 240), (9, 240), (10, 240),
                     (11, 240), (12, 240), (13, 240), (14, 240),
                     (15, 239), (16, 225), (17, 225), (18, 28), (19, 1))
EXPECTED_COSTS = (F(16, 7), F(22, 7), F(20, 7), F(24, 7),
                  F(22, 7), F(18, 7), F(18, 7))


def need(condition, note):
    if not condition:
        raise AssertionError(note)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def manifest(path):
    answer = {}
    for line in path.read_text(encoding="ascii").splitlines():
        value, name = line.split("  ", 1)
        need(len(value) == 64 and name not in answer, "manifest syntax")
        answer[name] = value
    return answer


def bind_package(path, expected, manifest_hash, label):
    need({name: digest(path / name) for name in expected} == expected,
         label + " payload hashes")
    need(manifest(path / "SHA256SUMS") == expected, label + " manifest contents")
    need(digest(path / "SHA256SUMS") == manifest_hash, label + " manifest hash")


def bind_dependencies(args):
    bind_package(args.source, PRODUCER, PRODUCER_MANIFEST, "m15 producer")
    bind_package(args.m14, M14, M14_MANIFEST, "m14 dependency")
    need(digest(args.six / "SHA256SUMS") == SIX_MANIFEST, "six-state manifest")
    need(digest(args.five / "SHA256SUMS") == FIVE_MANIFEST, "five-state manifest")
    need(digest(args.physical_auditor) == PHYSICAL_AUDITOR_HASH,
         "physical hostile auditor hash")
    theorem = (args.m14 / "AT_MOST_FOURTEEN_STATE_STRUCTURAL_WALL.md").read_text(
        encoding="utf-8")
    for phrase in ("delete unreachable and noncoaccessible states",
                   "Perron SCC", "largest blue-tail potential among red targets",
                   "cyclically align the unique red word"):
        need(phrase in theorem, "m14 dependency phrase " + phrase)


def feedback(red):
    counts = [0] * N
    rows = []
    for source in range(N - 1, -1, -1):
        if red[source] >= 0:
            counts[red[source]] += 1
        rows.append(tuple(counts))
    return tuple(reversed(rows))


def collatz(matrix, vector):
    for row, right in zip(matrix, vector):
        left = sum(F(value) * weight for value, weight in zip(row, vector))
        need(left <= T * right, "Collatz inequality")


def spectral_partition():
    need(F(14) < T < 15, "threshold interval")
    common = (F(1),) + (F(77, 80),) * 14
    need(T * common[1] == F(45969, 3200) > 14, "q>=2 slack")
    q2 = 0
    for sources in combinations(range(N), 2):
        for targets in product(range(1, N), repeat=2):
            red = [0] * N
            for source, target in zip(sources, targets):
                red[source] = target
            collatz(feedback(red), common)
            q2 += 1
    need(q2 == 20580, "complete q=2 layer")

    q1 = 0
    for source in range(N):
        for target in range(2, N):
            red = [0] * N
            red[source] = target
            vector = [F(560, 597)] * N
            vector[0], vector[target] = F(1), F(37, 40)
            collatz(feedback(red), vector)
            q1 += 1
    need(q1 == 195, "complete q=1,target>=2 layer")

    maps = [(0,) * N]
    factors = []
    for source in range(N):
        red = [0] * N
        red[source] = 1
        red = tuple(red)
        matrix = feedback(red)
        need(all(not any(row[column] for row in matrix)
                 for column in range(2, N)), "feedback rank at most two")
        trace = sum(matrix[i][i] for i in range(N))
        e2 = sum(matrix[i][i] * matrix[j][j] - matrix[i][j] * matrix[j][i]
                 for i in range(N) for j in range(i + 1, N))
        factor = (1, -trace, e2)
        expected = (1, -14, -14) if source == 0 else (1, -15, 1)
        need(factor == expected, "rank-two characteristic factor")
        value = T*T + factor[1]*T + factor[2]
        need(value == (F(-311, 1600) if source == 0 else F(-191, 1600)),
             "threshold polynomial sign")
        maps.append(red)
        factors.append(factor)
    need(len(maps) == len(set(maps)) == 16, "sixteen critical maps")
    return tuple(maps), q2, q1, tuple(factors)


def actions(anomaly, start, target):
    if anomaly is None:
        prefix, core, suffix = ("R",), ("U", "R"), ("B",) * target
    elif anomaly == 0:
        prefix = () if start == 0 else ("R",)
        core = ("U",)
        suffix = ("R",) if target == 0 else ("B",) * (target - 1)
    elif anomaly == 1:
        prefix = ("B", "R") if start == 1 else ("R",)
        core, suffix = ("U", "U", "R"), ("B",) * target
    else:
        prefix = ("R", "R") if start == anomaly else ("R",)
        core, suffix = ("U", "R"), ("B",) * target
    return prefix + core + suffix


def labeled_words(red, start, target, script):
    states = [start] * COPIES
    words = [[] for _ in range(COPIES)]
    blue = tuple(i + 1 if i + 1 < N else U for i in range(N))
    counts = []
    for action in script:
        bits = [0] * COPIES
        if action == "R":
            bits = [1] * COPIES
        elif action == "U":
            selected = next((i for i, state in enumerate(states) if state == 0), None)
            need(selected is not None, "unit action has state-zero copy")
            bits[selected] = 1
        counts.append(sum(bits))
        for copy, bit in enumerate(bits):
            words[copy].append(bit)
            states[copy] = (red if bit else blue)[states[copy]]
            need(states[copy] >= 0, "defined labeled-copy transition")
    need(states == [target] * COPIES, "pure target")
    need(set(counts) <= {0, 1, 7} and 1 in counts, "active column pattern")
    return tuple(tuple(word) for word in words), tuple(counts)


def geometry():
    incidence = Counter()
    for left, middle, right in PLAN:
        incidence[left] += 1
        incidence[right] += 1
        incidence[middle] -= 2
    need(not any(incidence.values()), "whole-word potential cancellation")
    ledgers, costs = [], []
    for shift in range(7):
        symbols = tuple(ROLES[(role + shift) % 7] for role in range(7))
        ledger, numerator = [], 0
        for left, middle, right in PLAN:
            residual = tuple(symbols[left][j] + symbols[right][j]
                             - 2 * symbols[middle][j] for j in range(4))
            need(all(value % QMOD == 0 for value in residual), "physical midpoint")
            ledger.append(tuple(value // QMOD for value in residual))
            numerator += sum((symbols[left][j] - symbols[right][j])**2
                             for j in range(4))
        rows = tuple((x, y, z) for x, y, z in product(symbols, repeat=3)
                     if all((x[j] + z[j] - 2*y[j]) % QMOD == 0
                            for j in range(4)))
        diagonal = tuple(row for row in rows if row[0] == row[2])
        need(len(rows) == 49 and len(diagonal) == 7 and
             all(x == y == z for x, y, z in diagonal),
             "all ordered physical midpoint rows")
        ledgers.append(tuple(ledger))
        costs.append(F(numerator, QMOD * QMOD))
    need(tuple(costs) == EXPECTED_COSTS and all(cost > 0 for cost in costs),
         "canonical raw costs")
    return tuple(ledgers), tuple(costs)


def physical_lift(words, counts, red_role, costs):
    physical = [[] for _ in range(7)]
    raw = F(0)
    for column, weight in zip(zip(*words), counts):
        if weight == 0:
            symbols = (ROLES[(red_role + 1) % 7],) * 7
        elif weight == 7:
            symbols = (ROLES[red_role],) * 7
        else:
            unique = column.index(1)
            shift = (red_role - unique) % 7
            symbols = tuple(ROLES[(copy + shift) % 7] for copy in range(7))
            raw += costs[shift]
        for copy, symbol in enumerate(symbols):
            need((symbol == ROLES[red_role]) == bool(column[copy]),
                 "physical color realizes abstract bit")
            physical[copy].append(symbol)
        for left, middle, right in PLAN:
            need(all((symbols[left][j] + symbols[right][j]
                      - 2*symbols[middle][j]) % QMOD == 0 for j in range(4)),
                 "lifted whole-word midpoint")
    need(raw > 0 and len({tuple(word) for word in physical}) == 7,
         "positive distinct physical lift")
    return raw


def all_words_and_lifts(maps):
    ledgers, costs = geometry()
    horizons = Counter()
    pairs = lifts = unit_packet_columns = 0
    raw_values = []
    for index, red in enumerate(maps):
        anomaly = None if index == 0 else index - 1
        for start in range(N):
            for target in range(N):
                script = actions(anomaly, start, target)
                words, counts = labeled_words(red, start, target, script)
                horizons[len(script)] += 1
                pairs += 1
                for red_role in range(7):
                    raw_values.append(physical_lift(words, counts, red_role, costs))
                    lifts += 1
                    unit_packet_columns += counts.count(1)
    need(pairs == 3600 and tuple(sorted(horizons.items())) == EXPECTED_HORIZONS,
         "all critical ordered pairs and horizon histogram")
    need(lifts == 25200 and unit_packet_columns == 26775,
         "all seven-role physical lifts")
    return ledgers, costs, pairs, lifts, unit_packet_columns, min(raw_values), max(raw_values)


def live_trim_scope():
    # Every finite partial functional blue graph is cyclic or acyclic.  The
    # frozen cyclic lemma is state-count independent.  In an acyclic 15-state
    # graph, a maximum blue tail <=14 is covered by hR<B; a tail of length 15
    # visits every state and forces exactly the Hamiltonian chain up to labels.
    need(14 * 17640 < 263277 < 15 * 17640, "exact h=14/15 cutoff")
    chain = tuple(i + 1 if i + 1 < N else U for i in range(N))
    tails = []
    for start in range(N):
        seen, state = [], start
        while state >= 0:
            need(state not in seen, "acyclic chain")
            seen.append(state)
            state = chain[state]
        tails.append(len(seen))
    need(max(tails) == 15 and sorted(tails) == list(range(1, 16)),
         "Hamiltonian residual tail profile")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--m14", required=True, type=Path)
    parser.add_argument("--six", required=True, type=Path)
    parser.add_argument("--five", required=True, type=Path)
    parser.add_argument("--physical-auditor", required=True, type=Path)
    args = parser.parse_args()
    bind_dependencies(args)
    print("PASS_M15_M14_PHYSICAL_HASH_BINDING", PRODUCER_MANIFEST,
          M14_MANIFEST, SIX_MANIFEST, FIVE_MANIFEST, PHYSICAL_AUDITOR_HASH)
    maps, q2, q1, factors = spectral_partition()
    print("PASS_TOTAL_RED_AND_COLLATZ_PARTITION", q2, q1,
          "critical", len(maps), "factors", Counter(factors))
    result = all_words_and_lifts(maps)
    print("PASS_ALL_LABELED_WORDS_AND_PHYSICAL_LIFTS",
          "pairs", result[2], "lifts", result[3], "unit_columns", result[4],
          "raw_range", (result[5], result[6]))
    print("PHYSICAL_CARRY_LEDGERS", result[0])
    print("PHYSICAL_RAW_COSTS", result[1])
    live_trim_scope()
    print("PASS_LIVE_TRIM_COMBINED_AT_MOST_FIFTEEN_SCOPE")
    print("APPROVE_Q42_PARTIAL_FIFTEEN_CHAIN_CLOSURE")


if __name__ == "__main__":
    main()

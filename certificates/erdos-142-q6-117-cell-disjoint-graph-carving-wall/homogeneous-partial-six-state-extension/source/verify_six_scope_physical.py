#!/usr/bin/env python3
"""Bind the <=5 dependency and replay live-rate scope plus q42 geometry."""

from collections import Counter, deque
from fractions import Fraction
from hashlib import sha256
from itertools import product
import os
from pathlib import Path
import sys


BLUE, RED = 263_277, 17_640
GATE = Fraction(1_058_841, 4)
Q = 42
if len(sys.argv) > 2:
    raise SystemExit("usage: verify_six_scope_physical.py [five-state-directory]")
_sibling_five = (Path(__file__).resolve().parent.parent /
                 "erdos142_q42_partial_at_most_five_state_wall_20260819")
# The fallback is only a local convenience.  Every accepted dependency is
# authenticated below by the same pinned hashes, independent of its location.
FIVE = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(
    os.environ.get("Q42_FIVE_STATE_DIR", _sibling_five))
FIVE_HASHES = {
    "AT_MOST_FIVE_STATE_SUNFLOWER_WALL.md":
        "6fa6b6b2fb2a113f837e37960a63edb17c759691af982fa24e3a6ab3c575eb72",
    "exhaust_five_state_orbits.cpp":
        "2f311d5aa389cca75ba75c1d21a6fc13d8612ba013a952704a8163103e00c6cb",
    "verify_lower_state_live_sccs.py":
        "b59ac9c7da552ff520755a43ebd317c51b0d5ebdfd41ae835a90515e9d9b1139",
    "run.ps1":
        "302a244d71a4f5668239c388cc4ba6237ea44a54a3b9a4999ccdd1bd87038631",
    "run.sh":
        "853d765139a5839ae4f90fe357abf13a1f96115ce6389f499195cd229d947c74",
    "SHA256SUMS":
        "2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71",
}
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


def bind_five_state_dependency():
    for name, expected in FIVE_HASHES.items():
        actual = sha256((FIVE / name).read_bytes()).hexdigest()
        need(actual == expected, f"<=5 dependency hash {name}")


def dead_sink_control():
    # Fixed start/accept zero; red enters reachable noncoaccessible state one.
    delta = (0, 1, 1, 1)
    mass = [1, 0]
    for horizon in range(1, 9):
        following = [0, 0]
        for source in range(2):
            for bit, weight in ((0, BLUE), (1, RED)):
                following[delta[2 * source + bit]] += mass[source] * weight
        mass = following
        need(mass[0] == BLUE ** horizon, "accepted dead-sink mass")
    ambient_rho = BLUE + RED
    trim_rho = BLUE
    need(ambient_rho > GATE > trim_rho, "dead-sink scope separation")
    return ambient_rho, trim_rho


def physical_replay():
    packet_histogram = {5: 13_671, 6: 3_528, 7: 441}
    need(sum(packet_histogram.values()) == 17_640, "packet count")
    need(280_917 - 17_640 == BLUE, "one-red-per-packet coloring")
    need(packet_histogram[7] > 0, "actual size-seven packet exists")

    incidence = Counter()
    for left, middle, right in PLAN:
        incidence[left] += 1
        incidence[right] += 1
        incidence[middle] -= 2
    need(not any(incidence.values()), "role cancellation")

    raw_costs, torus_costs, ledgers = [], [], []
    for shift in range(7):
        shifted = tuple(ROLES[(role + shift) % 7] for role in range(7))
        raw = torus = Fraction(0)
        ledger = []
        for left, middle, right in PLAN:
            x, y, z = shifted[left], shifted[middle], shifted[right]
            displacement = tuple(x[c] + z[c] - 2 * y[c] for c in range(4))
            need(all(value % Q == 0 for value in displacement), "physical row")
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
                    need(x == y, "nontrivial x=z")
        need((actual_rows, x_equals_z) == (49, 7), "actual row census")
        raw_costs.append(raw)
        torus_costs.append(torus)
        ledgers.append(tuple(ledger))

    expected_raw = (Fraction(16, 7), Fraction(22, 7), Fraction(20, 7),
                    Fraction(24, 7), Fraction(22, 7), Fraction(18, 7),
                    Fraction(18, 7))
    need(tuple(raw_costs) == expected_raw, "raw costs")
    need(tuple(torus_costs) == (Fraction(11, 7),) * 7, "wrapped costs")
    need(tuple(ledgers) == EXPECTED_CARRIES, "carry ledgers")
    return tuple(raw_costs), tuple(torus_costs)


def main():
    bind_five_state_dependency()
    ambient_rho, trim_rho = dead_sink_control()
    raw, torus = physical_replay()
    print("SIX_SCOPE accepted_language_limsup_equals_live_trim_rho",
          f"dead_sink_ambient={ambient_rho}", f"trim={trim_rho}")
    print("SIX_PHYSICAL frozen_one_red_per_17640_packets",
          f"raw={raw}", f"wrapped={torus}")
    print("PASS_SIX_STATE_SCOPE_DEPENDENCY_AND_Q42_PHYSICAL_REPLAY")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read-only hostile audit of the two-level weighted multiset-7 bound."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
import os
import sys


SOURCE_HASHES = {
    "THEOREM.md": "92d2690ac412dcf5438e63f3ac56c6095801ac9b9bfdc1343ac9aa77df70afc4",
    "verify.py": "bae091ada91a3266c066386fa13e00a94a7a81e480a02186b848007b2414a122",
    "run.ps1": "9b17764fcc51b63288b4d3509d84e310d7b80cf3a1375e936939acacf98f0414",
    "SHA256SUMS": "d73625924640cb570077f0cff5128eee8591503ef65743458e748ed7892da1cf",
}
DEFAULT_SOURCE = (Path(__file__).resolve().parent.parent /
                  "erdos142_weighted_multiset7_twolevel_20260819")
SOURCE = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(
    os.environ.get("TWOLEVEL_SOURCE_DIR", DEFAULT_SOURCE))
if len(sys.argv) > 2:
    raise SystemExit("usage: independent_audit.py [source-directory]")

B_WEIGHT = 263_277
R_WEIGHT = 17_640
GATE = Fraction(1_058_841, 4)
X = Fraction(40, 597)
Y = Fraction(2401, 2388)


def require(condition, note):
    if not condition:
        raise AssertionError(note)


def bind_source():
    for name, expected in SOURCE_HASHES.items():
        actual = sha256((SOURCE / name).read_bytes()).hexdigest()
        require(actual == expected, f"source hash: {name}")

    manifest = {}
    for line in (SOURCE / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, name = line.split()
        manifest[name.lstrip("*")] = digest.lower()
    require(manifest == {name: SOURCE_HASHES[name]
                         for name in ("THEOREM.md", "verify.py", "run.ps1")},
            "source manifest projection")


def matching_number(edges):
    """Independent subset recursion on edges, not the source vertex DP."""
    edges = tuple(edges)
    best = 0

    def search(position, used, size):
        nonlocal best
        if size + len(edges) - position <= best:
            return
        if position == len(edges):
            best = max(best, size)
            return
        left, right = edges[position]
        search(position + 1, used, size)
        if left not in used and right not in used:
            search(position + 1, used | {left, right}, size + 1)

    search(0, frozenset(), 0)
    return best


def graph_parameters(edges):
    degree = {}
    for left, right in edges:
        require(left != right, "simple graph loop")
        degree[left] = degree.get(left, 0) + 1
        degree[right] = degree.get(right, 0) + 1
    require(len(set(edges)) == len(edges), "simple graph duplicate edge")
    return max(degree.values(), default=0), matching_number(edges)


def complete_graph(first, size):
    return tuple((first + left, first + right)
                 for left in range(size)
                 for right in range(left + 1, size))


def complete_bipartite(left_first, left_size, right_first, right_size):
    return tuple((left_first + left, right_first + right)
                 for left in range(left_size)
                 for right in range(right_size))


def chvatal_hanson(nu, delta):
    return (nu * delta
            + (delta // 2) * (nu // ((delta + 1) // 2)))


def audit_graph_bases():
    # Chvatal--Hanson: f(nu,Delta)=nu*Delta
    # +floor(Delta/2)*floor(nu/ceil(Delta/2)).
    require(chvatal_hanson(6, 6) == 42, "A2 upper")
    require(chvatal_hanson(5, 6) == 33, "B2 upper")

    a_graph = complete_graph(0, 7) + complete_graph(7, 7)
    b_graph = (complete_graph(0, 7)
               + complete_bipartite(7, 2, 9, 6))
    require((len(a_graph),) + graph_parameters(a_graph) == (42, 6, 6),
            "A2 lower witness")
    require((len(b_graph),) + graph_parameters(b_graph) == (33, 6, 5),
            "B2 lower witness")

    # A simple 2-uniform seven-sunflower has core empty (a matching) or
    # singleton (a star), so Delta<=6 and nu<=6 are exactly applicable.
    return 42, 33


def audit_link_algebra(limit=100):
    a = {1: 6, 2: 42}
    b = {1: 5, 2: 33}
    floor_events = []
    for rank in range(3, limit + 1):
        bracket = rank * (a[rank - 1] + b[rank - 1]) - (rank - 2)
        unrestricted = Fraction(6, 2) * bracket
        restricted = Fraction(5, 2) * bracket
        require(unrestricted.denominator == 1, "A recurrence integral")
        a[rank] = unrestricted.numerator
        b[rank] = restricted.numerator // restricted.denominator
        floor_events.append((rank, bracket & 1))

        # Coefficient audit of
        # 2|F|=e1+sum(j*e_j)-sum_{j>=3}((j-2)e_j), using e0=0.
        coefficients = []
        for intersection in range(1, rank + 1):
            coefficient = intersection
            if intersection == 1:
                coefficient += 1
            if intersection >= 3:
                coefficient -= intersection - 2
            coefficients.append(coefficient)
        require(coefficients == [2] * rank, "double-count coefficients")
        require((rank - 2) >= 1, "e_k subtraction nonnegative")

    expected_a = (6, 42, 672, 14_778, 406_386, 13_410_726,
                  516_312_936)
    expected_b = (5, 33, 560, 12_315, 338_655, 11_175_605,
                  430_260_780)
    require(tuple(a[rank] for rank in range(1, 8)) == expected_a,
            "A cap prefix")
    require(tuple(b[rank] for rank in range(1, 8)) == expected_b,
            "B cap prefix")
    require(a[3] == 672 < 744, "rank-three improvement")
    return a, b, tuple(floor_events)


def dual_lym_upper(dimension, caps):
    """Solve by the one-constraint LP dual, independent of greedy code.

    For q_k=n_k/C(d,k), the dual at threshold theta is
      theta + sum c_k max(density_k-theta,0),
    where c_k=min(1,A_k/C(d,k)).  The minimum occurs at theta=0 or at a
    density breakpoint.
    """
    items = []
    for rank in range(1, dimension + 1):
        layer = comb(dimension, rank)
        cap = min(Fraction(1), Fraction(caps[rank], layer))
        density = layer * X**rank
        items.append((rank, cap, density))

    candidates = {Fraction(0)} | {density for _, _, density in items}
    duals = []
    for theta in candidates:
        value = theta + sum(cap * max(Fraction(0), density - theta)
                            for _, cap, density in items)
        duals.append((value, theta))
    optimum, theta = min(duals)

    # Recover a primal allocation only to prove strong dual equality.
    larger = [(rank, cap, density) for rank, cap, density in items
              if density > theta]
    tied = [(rank, cap, density) for rank, cap, density in items
            if density == theta]
    used = sum(cap for _, cap, _ in larger)
    require(used <= 1, "dual breakpoint below capacity")
    remaining = 1 - used
    primal = sum(cap * density for _, cap, density in larger)
    for _, cap, density in tied:
        take = min(cap, remaining)
        primal += take * density
        remaining -= take
    require(primal == optimum, "exact primal-dual equality")
    return optimum, theta


def audit_lym(caps):
    require(Fraction(R_WEIGHT, B_WEIGHT) == X, "x constant")
    require(GATE / B_WEIGHT == Y, "y constant")
    bounds = {}
    thresholds = {}
    for dimension in range(1, 81):
        bounds[dimension], thresholds[dimension] = dual_lym_upper(
            dimension, caps)

    require(all(bounds[d] < 1 for d in range(1, 29)), "U<1 through 28")
    require(bounds[29] > 1, "U29 relaxation failure")
    require(all(bounds[d] < Y**d for d in range(1, 34)),
            "gate excluded through 33")
    require(bounds[34] > Y**34, "d34 relaxation failure")
    require(min(d for d in bounds if bounds[d] > 1) == 29,
            "first unit failure")
    require(min(d for d in bounds if bounds[d] > Y**d) == 34,
            "first gate failure")

    margins = {
        "one_minus_U28": 1 - bounds[28],
        "U29_minus_one": bounds[29] - 1,
        "gate33_minus_U33": Y**33 - bounds[33],
        "U34_minus_gate34": bounds[34] - Y**34,
    }
    require(all(value > 0 for value in margins.values()), "strict horizons")
    require(bounds[33] == Fraction(29_626_668_521_680,
                                   25_278_447_680_919), "U33 exact")
    require(bounds[34] == Fraction(30_583_883_241_680,
                                   25_278_447_680_919), "U34 exact")
    return bounds, thresholds, margins


def main():
    bind_source()
    a2, b2 = audit_graph_bases()
    caps, restricted, floor_events = audit_link_algebra()
    bounds, thresholds, margins = audit_lym(caps)
    print("AUDIT_SOURCE_BOUND", sha256((SOURCE / "SHA256SUMS").read_bytes()).hexdigest())
    print("AUDIT_GRAPH_BASES", f"A2={a2}", f"B2={b2}")
    print("AUDIT_CAPS", "A3=672", "B3=560",
          f"odd_brackets={sum(parity for _, parity in floor_events)}")
    for name, value in margins.items():
        print("AUDIT_MARGIN", name,
              f"{value.numerator}/{value.denominator}")
    for dimension in (28, 29, 33, 34):
        bound = bounds[dimension]
        theta = thresholds[dimension]
        print("AUDIT_LYM", f"d={dimension}",
              f"U={bound.numerator}/{bound.denominator}",
              f"dual_theta={theta.numerator}/{theta.denominator}")
    print("PASS_INDEPENDENT_TWO_LEVEL_WEIGHTED_HOSTILE_AUDIT")


if __name__ == "__main__":
    main()

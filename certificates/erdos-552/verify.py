#!/usr/bin/env python3
"""Exact verifier for the certified Erdős #552 small-value witnesses."""

from __future__ import annotations

import hashlib
import json
from itertools import combinations
from math import isqrt
from pathlib import Path


HERE = Path(__file__).resolve().parent
WITNESSES = HERE / "witnesses.json"
EXPECTED_CLAIM = "R(C4,K1,n) = n + ceil(sqrt(n)) + 1 for 12 <= n <= 16"
EXPECTED_UPPER_BOUND = "Parsons (1975): R(C4,K1,n) <= n + ceil(sqrt(n)) + 1"


def ceil_sqrt(n: int) -> int:
    root = isqrt(n)
    return root if root * root == n else root + 1


def verify_witness(
    witness: dict[str, object], *, expected_vertices: int, exact: bool
) -> dict[str, object]:
    n = witness.get("n")
    vertices = witness.get("vertices")
    raw_edges = witness.get("edges")
    if isinstance(n, bool) or not isinstance(n, int) or not 12 <= n <= 17:
        raise ValueError("n must be an integer in [12,17]")
    if isinstance(vertices, bool) or not isinstance(vertices, int):
        raise ValueError(f"n={n}: vertices must be an integer")
    if vertices != expected_vertices:
        raise ValueError(f"n={n}: expected {expected_vertices} vertices")
    if not isinstance(raw_edges, list):
        raise ValueError(f"n={n}: edges must be an array")

    edges: set[tuple[int, int]] = set()
    for index, edge in enumerate(raw_edges):
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError(f"n={n}: edge {index} must have two endpoints")
        u, v = edge
        if any(isinstance(x, bool) or not isinstance(x, int) for x in (u, v)):
            raise ValueError(f"n={n}: edge {index} endpoints must be integers")
        if not (0 <= u < vertices and 0 <= v < vertices) or u == v:
            raise ValueError(f"n={n}: edge {index} is out of range or a loop")
        normalized = (min(u, v), max(u, v))
        if normalized in edges:
            raise ValueError(f"n={n}: duplicate edge {normalized}")
        edges.add(normalized)

    adjacency = [set() for _ in range(vertices)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    degrees = [len(neighbors) for neighbors in adjacency]
    required_degree = vertices - n
    if min(degrees) < required_degree:
        raise ValueError(f"n={n}: minimum degree is below {required_degree}")

    maximum_codegree = 0
    for u, v in combinations(range(vertices), 2):
        codegree = len(adjacency[u] & adjacency[v])
        maximum_codegree = max(maximum_codegree, codegree)
        if codegree > 1:
            raise ValueError(f"n={n}: vertices {u},{v} have codegree {codegree}")

    # The graph avoids red C4 and its complement has maximum degree <= n-1,
    # so it is a coloring of K_vertices avoiding red C4 and blue K1,n.
    lower_bound = vertices + 1
    parsons_upper_bound = n + ceil_sqrt(n) + 1
    if exact and lower_bound != parsons_upper_bound:
        raise ValueError(f"n={n}: witness does not meet the cited upper bound")
    return {
        "n": n,
        "value": lower_bound,
        "vertices": vertices,
        "edges": len(edges),
        "minimum_degree": min(degrees),
        "maximum_codegree": maximum_codegree,
        "parsons_upper_bound": parsons_upper_bound,
        "status": "EXACT" if exact else "LOWER_BOUND",
    }


def main() -> None:
    raw = WITNESSES.read_bytes()
    document = json.loads(raw)
    if document.get("schema") != "erdos-552-c4-star-witness-set/v2":
        raise ValueError("unexpected witness-set schema")
    if document.get("claim") != EXPECTED_CLAIM:
        raise ValueError("witness-set claim does not match the verified theorem")
    if document.get("upper_bound") != EXPECTED_UPPER_BOUND:
        raise ValueError("witness-set upper-bound citation contract changed")
    witnesses = document.get("witnesses")
    if not isinstance(witnesses, list) or len(witnesses) != 5:
        raise ValueError("expected exactly five witnesses")
    results = [
        verify_witness(
            witness,
            expected_vertices=n + ceil_sqrt(n),
            exact=True,
        )
        for n, witness in zip(range(12, 17), witnesses, strict=True)
    ]
    if [result["n"] for result in results] != list(range(12, 17)):
        raise ValueError("witnesses must cover n=12..16 in order")
    lower_bound_witnesses = document.get("lower_bound_witnesses")
    if not isinstance(lower_bound_witnesses, list) or len(lower_bound_witnesses) != 1:
        raise ValueError("expected exactly one lower-bound witness")
    lower_bounds = [
        verify_witness(
            lower_bound_witnesses[0],
            expected_vertices=21,
            exact=False,
        )
    ]
    if lower_bounds[0]["n"] != 17 or lower_bounds[0]["value"] != 22:
        raise ValueError("lower-bound witness must prove R(C4,K1,17) >= 22")
    report = {
        "certificate_sha256": hashlib.sha256(raw).hexdigest(),
        "claim": EXPECTED_CLAIM,
        "results": results,
        "lower_bounds": lower_bounds,
        "valid": True,
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

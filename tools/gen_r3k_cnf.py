#!/usr/bin/env python3
"""Deterministic CNF generator for the R(3,k) upper-half family.

Encoding: ``r3k-edge-cnf`` v1.0.0  (the encoding pinned by
``observatory/pipeline.json`` — change the version string if you change ANY
emission detail, because emitted-proof sizes depend on it).

The formula asserts "there exists a 2-coloring of the edges of K_n with no
red triangle and no blue K_k".  At n = R(3,k) this is UNSAT, and a DRAT
proof of that unsatisfiability is a machine-checkable certificate of the
upper-bound half of the Ramsey number.

Encoding details (all deterministic, no randomness, no timestamps):

* **Variables** — one per edge of K_n.  Edges are the pairs ``(i, j)`` with
  ``1 <= i < j <= n`` in lexicographic order; the variable index is the
  1-based position in that order.  ``x_e = true`` means edge ``e`` is red,
  ``false`` means blue.
* **Red-triangle clauses** — for every 3-subset ``{a, b, c}`` (lexicographic
  order), the clause ``(-x_ab  -x_ac  -x_bc)``: the three edges are not all
  red.  C(n,3) clauses.
* **Blue-K_k clauses** — for every k-subset (lexicographic order), the
  positive clause over its C(k,2) edge variables (edges in lexicographic
  order): the subset's edges are not all blue.  C(n,k) clauses.
* **Emission order** — header comments, ``p cnf`` line, ALL red-triangle
  clauses, then ALL blue-K_k clauses.

Relation to ``certificates/ramsey-3-3/problem.cnf`` (k=3, n=6): this
generator reproduces it **logically but not byte-identically** — the
variable numbering and the clause *set* are exactly equal (unit-tested in
``tests/test_gen_r3k_cnf.py``), but the committed file interleaves the
negative/positive clause pair per triangle while this generator emits the
negative block then the positive block, and the header comments differ.

Usage::

    python3 tools/gen_r3k_cnf.py K N [-o OUT.cnf]

Writes DIMACS CNF to stdout (or OUT.cnf).  Exact and total: any k >= 3 and
n >= k is accepted; whether the instance is SAT or UNSAT is the solver's
business, not the generator's.
"""

import argparse
import sys
from itertools import combinations

ENCODING_NAME = "r3k-edge-cnf"
ENCODING_VERSION = "1.0.0"


def edge_vars(n):
    """Map each edge (i, j), 1 <= i < j <= n, to its 1-based variable index."""
    return {e: idx for idx, e in enumerate(combinations(range(1, n + 1), 2), start=1)}


def generate_clauses(k, n):
    """Yield the clauses of the r3k-edge-cnf encoding, in emission order."""
    if k < 3:
        raise ValueError(f"k must be >= 3 (got {k}): the red side is a triangle")
    if n < k:
        raise ValueError(f"n must be >= k (got n={n}, k={k})")
    var = edge_vars(n)
    # Red-triangle clauses: no 3-subset has all edges red.
    for a, b, c in combinations(range(1, n + 1), 3):
        yield (-var[(a, b)], -var[(a, c)], -var[(b, c)])
    # Blue-K_k clauses: no k-subset has all edges blue.
    for subset in combinations(range(1, n + 1), k):
        yield tuple(var[e] for e in combinations(subset, 2))


def generate_dimacs(k, n):
    """Return the full DIMACS CNF text for (k, n) as a string."""
    clauses = list(generate_clauses(k, n))
    nvars = n * (n - 1) // 2
    lines = [
        f"c {ENCODING_NAME} v{ENCODING_VERSION}: R(3,{k}) upper half at n={n}",
        f"c 2-color E(K_{n}) (var true = red), no red K_3, no blue K_{k}",
        f"c edges lexicographic; {nvars} vars; "
        f"C({n},3)={n*(n-1)*(n-2)//6} red + C({n},{k}) blue clauses",
        f"p cnf {nvars} {len(clauses)}",
    ]
    lines.extend(" ".join(str(lit) for lit in clause) + " 0" for clause in clauses)
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Deterministic CNF generator for the R(3,k) upper-half family "
                    f"(encoding {ENCODING_NAME} v{ENCODING_VERSION}).")
    ap.add_argument("k", type=int, help="forbid a blue K_k (k >= 3)")
    ap.add_argument("n", type=int, help="number of vertices of K_n (n >= k)")
    ap.add_argument("-o", "--output", metavar="FILE",
                    help="write CNF here instead of stdout")
    args = ap.parse_args(argv)
    text = generate_dimacs(args.k, args.n)
    if args.output:
        with open(args.output, "w") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

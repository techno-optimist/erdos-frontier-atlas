#!/usr/bin/env python3
"""Deterministic CNF generator for the R(3,k) upper-half family.

Encoding: ``r3k-edge-cnf`` — two pinned emission-order variants of the SAME
clause set (both registered in ``observatory/pipeline.json``; change the
version string if you change ANY emission detail, because emitted-proof
sizes depend on it):

* ``--order lex`` (default) — encoding **v1.0.0**.  Byte-frozen: the
  default output is regression-tested against recorded sha256s and must
  never change.
* ``--order interleaved`` — encoding **v1.0.0-interleaved**.  Same clause
  set and variable numbering, different clause order (details below).

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
* **Emission order, ``lex``** — header comments (3 lines), ``p cnf`` line,
  ALL red-triangle clauses, then ALL blue-K_k clauses.
* **Emission order, ``interleaved``** — header comment (1 line, exemplar
  format, see below), ``p cnf`` line, then the two lexicographic clause
  streams alternating: red_1, blue_1, red_2, blue_2, ...; when the shorter
  stream is exhausted, the remainder of the longer one follows.  For k=3
  both streams run over the same 3-subsets, so this is exactly the
  negative/positive pair-per-triangle order of the committed
  ``certificates/ramsey-3-3/problem.cnf`` (produced by an independent
  earlier session).

Relation to ``certificates/ramsey-3-3/problem.cnf`` (k=3, n=6):

* ``--order lex`` reproduces it **logically but not byte-identically** —
  the variable numbering and the clause *set* are exactly equal
  (unit-tested in ``tests/test_gen_r3k_cnf.py``), but the committed file
  interleaves the negative/positive clause pair per triangle while lex
  emits the negative block then the positive block, and the headers differ.
* ``--order interleaved`` reproduces it **byte-identically**
  (regression-tested).  To achieve that, the interleaved variant emits the
  exemplar's single-line header format, and preserves the exemplar's
  phrasing "no monochromatic K_3" exactly when k=3 — accurate there and
  only there, because at k=3 the red and blue sides are both K_3.  For
  k>3 the honest asymmetric phrasing ("no red K_3, no blue K_k") is used
  in the same one-line format.  Note the interleaved output therefore
  carries no encoding-version stamp in its comments; its identity is
  pinned by the manifest and the recorded generation command.

Usage::

    python3 tools/gen_r3k_cnf.py K N [-o OUT.cnf] [--order {lex,interleaved}]

Writes DIMACS CNF to stdout (or OUT.cnf).  Exact and total: any k >= 3 and
n >= k is accepted; whether the instance is SAT or UNSAT is the solver's
business, not the generator's.
"""

import argparse
import sys
from itertools import combinations

ENCODING_NAME = "r3k-edge-cnf"
ENCODING_VERSION = "1.0.0"                          # --order lex (the default)
ENCODING_VERSION_INTERLEAVED = "1.0.0-interleaved"  # --order interleaved
ORDERS = ("lex", "interleaved")


def edge_vars(n):
    """Map each edge (i, j), 1 <= i < j <= n, to its 1-based variable index."""
    return {e: idx for idx, e in enumerate(combinations(range(1, n + 1), 2), start=1)}


def generate_clauses(k, n, order="lex"):
    """Yield the clauses of the r3k-edge-cnf encoding, in emission order.

    ``order`` selects the emission order of the SAME clause set:

    * ``"lex"`` (default, v1.0.0): all red-triangle clauses in lexicographic
      3-subset order, then all blue-K_k clauses in lexicographic k-subset
      order.
    * ``"interleaved"`` (v1.0.0-interleaved): the two lexicographic streams
      alternate (red_1, blue_1, red_2, blue_2, ...); the remainder of the
      longer stream follows once the shorter is exhausted.  At k=3 this is
      exactly the pair-per-triangle order of the committed
      ``certificates/ramsey-3-3/problem.cnf``.
    """
    if k < 3:
        raise ValueError(f"k must be >= 3 (got {k}): the red side is a triangle")
    if n < k:
        raise ValueError(f"n must be >= k (got n={n}, k={k})")
    if order not in ORDERS:
        raise ValueError(f"order must be one of {ORDERS} (got {order!r})")
    var = edge_vars(n)
    # Red-triangle clauses: no 3-subset has all edges red.
    red = [(-var[(a, b)], -var[(a, c)], -var[(b, c)])
           for a, b, c in combinations(range(1, n + 1), 3)]
    # Blue-K_k clauses: no k-subset has all edges blue.
    blue = [tuple(var[e] for e in combinations(subset, 2))
            for subset in combinations(range(1, n + 1), k)]
    if order == "lex":
        yield from red
        yield from blue
    else:  # interleaved
        m = min(len(red), len(blue))
        for i in range(m):
            yield red[i]
            yield blue[i]
        yield from red[m:]
        yield from blue[m:]


def generate_dimacs(k, n, order="lex"):
    """Return the full DIMACS CNF text for (k, n) as a string.

    The default (``order="lex"``) output is byte-frozen — regression-tested
    against recorded sha256s; do not change a byte of it.  The interleaved
    output reproduces ``certificates/ramsey-3-3/problem.cnf`` byte-for-byte
    at (k=3, n=6); see the module docstring for its header rule.
    """
    clauses = list(generate_clauses(k, n, order=order))
    nvars = n * (n - 1) // 2
    if order == "lex":
        lines = [
            f"c {ENCODING_NAME} v{ENCODING_VERSION}: R(3,{k}) upper half at n={n}",
            f"c 2-color E(K_{n}) (var true = red), no red K_3, no blue K_{k}",
            f"c edges lexicographic; {nvars} vars; "
            f"C({n},3)={n*(n-1)*(n-2)//6} red + C({n},{k}) blue clauses",
        ]
    else:  # interleaved: exemplar-format single-line header (see docstring)
        if k == 3:
            lines = [f"c Ramsey: 2-color E(K_{n}), no monochromatic K_3 "
                     f"({nvars} edges)"]
        else:
            lines = [f"c Ramsey: 2-color E(K_{n}), no red K_3, no blue K_{k} "
                     f"({nvars} edges)"]
    lines.append(f"p cnf {nvars} {len(clauses)}")
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
    ap.add_argument("--order", choices=ORDERS, default="lex",
                    help="clause emission order: 'lex' (default; encoding "
                         f"v{ENCODING_VERSION} — red block then blue block; "
                         "byte-frozen) or 'interleaved' (encoding "
                         f"v{ENCODING_VERSION_INTERLEAVED} — alternating "
                         "red/blue streams, the clause order of "
                         "certificates/ramsey-3-3/problem.cnf; SAME clause "
                         "set, different order)")
    args = ap.parse_args(argv)
    text = generate_dimacs(args.k, args.n, order=args.order)
    if args.output:
        with open(args.output, "w") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

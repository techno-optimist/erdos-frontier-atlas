# R(C4, K1,39) = 46 — witness certificate

This directory certifies the lower-bound half of a new exact C4-vs-star Ramsey
value:

```text
R(C4, K1,39) = 46.
```

- **Lower bound (this certificate):** `witness.json` encodes a graph on 45
  vertices with 146 edges, minimum degree 6, and maximum codegree 1 (hence
  C4-free). Its complement has maximum degree `44 - 6 = 38 < 39`, so the blue
  graph contains no `K_{1,39}`. The coloring avoids both red `C4` and blue
  `K_{1,39}`, proving `R(C4, K1,39) >= 46`.
- **Upper bound (published):** `R(C4, K1,39) <= 46` — Wu, Sun, Radziszowski,
  *Wheel and Star-Critical Ramsey Numbers for Quadrilateral*, Discrete Applied
  Mathematics 186 (2015), as tabulated in Boza's survey
  ([arXiv:2409.12770](https://arxiv.org/abs/2409.12770)), which lists the cell
  as open (`f(39) <= 46`, no matching lower bound) as of June 2026.

Run:

```sh
python3 certificates/erdos-552-f39/verify.py
```

The check is dependency-free and exact: degree recount plus codegree `<= 1`
over all 990 vertex pairs. The witness was additionally verified by an
independent hostile checker (brute-force 4-cycle enumeration over all 148,995
4-subsets, all cyclic orderings — zero C4s found).

## Construction and provenance

The witness is an induced subgraph of the Erdős–Rényi polarity graph `ER_7`
of `PG(2,7)` (57 vertices, C4-free, degrees 7/8) obtained by deleting 12
vertices. The deletion set was selected exactly (SAT over keep-variables with
sequential-counter cardinality constraints, CaDiCaL): the constraint "keep 45
vertices, every kept vertex keeps >= 6 kept neighbors" is satisfiable, and the
model is this witness. Polarity-graph deletions are the classical technique
for these numbers (Parsons 1976, *Graphs from projective planes*); the new
content is the exact feasible deletion certificate at this cell.

## Negative coverage (same technique, sibling open cells)

Exhaustive SAT over the same construction families proved the sibling cells do
NOT fall to polarity-graph deletion:

- no 49-vertex min-degree-7 induced subgraph of `ER_7` or `ER_8` (`f(42)` cell),
- no 51-vertex min-degree-7 induced subgraph of `ER_7` or `ER_8` (`f(44)` cell),
- no 53-vertex min-degree-7 induced subgraph of `ER_8` (`f(46)` cell).

Those cells remain open and need different constructions or general SAT on the
full graph space.

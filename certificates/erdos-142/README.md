# Erdős #142 (r₃(N)) — a certified construction no-go

**Problem.** Erdős [#142](https://www.erdosproblems.com/142): prove an asymptotic
formula for `r_k(N)`, the largest subset of `{1,…,N}` with no non-trivial
`k`-term arithmetic progression. The headline is **asymptotic** — a theorem
question, open even for `k = 3`, carrying a $10,000 prize — and it is **not** what
this certificate touches. It is a **WALL**.

**The finite object.** On the *lower-bound* side of `r₃(N)`, the current record is
built from a 2-D torus building block `T ⊆ [0,1)²` with measure `μ(T) ≥ 7/24`
(Elsholtz–Hunter–Proske–Sauermann, [arXiv:2406.12290](https://arxiv.org/abs/2406.12290),
2024 — the first improvement of Behrend's constant in ~80 years). Beating `7/24`
improves the best-known `r₃(N)` lower bound. This directory studies **one fixed,
hash-pinned 39-piece graph-directed EHPS geometry** — a natural candidate to beat
`7/24` — and asks the exact question that decides whether it can: *does a per-piece
potential `f` exist making the EHPS convexity `V_f ≥ 0` hold on it?* (If one did,
the geometry would realize a rate above `7/24`.)

## What is certified (two exact, machine-checkable facts)

1. **The complete constraint class is exactly 12,349 cells.** The EHPS convexity
   must hold on every full-dimensional `(piece-triple, wrap)` cell — a
   positive-measure family of interior AP triples. An independent exact
   re-enumeration from the primitive geometry finds **exactly 12,349** such cells
   (of 18,691 box-feasible: 12,349 full + 4,464 degenerate + 1,878 empty),
   canonical cell-set `sha256 35fb1967…a859b6`. Every cell carries a
   self-validating exact certificate (a strict-interior rational anchor if full;
   an exact Farkas/Gordan certificate if not), so correctness does not rest on any
   floating-point solver. `verify.py --exhaustive` re-classifies the entire
   box-feasible universe.

2. **No affine potential works — the natural sub-family is exactly dead.** Fixing
   every piece's quadratic to the unique curvature-cancelling value makes `V_f`
   affine on every cell; over that family an **exact 34-term rational
   vertex-Farkas certificate** (positive multipliers, coefficient row cancels over
   all free columns, negative constant, full-dimensionality-checked on every
   support cell) proves **no such `f` satisfies `V_f ≥ 0`**. Consequence: any
   potential on this geometry that could beat `7/24` must be **genuinely
   quadratic** (curved on some cell) — the affine/additive approach cannot.

Geometry `sha256 607841…92ada`. Both checks are pure Python-stdlib exact
arithmetic (`fractions.Fraction`); no floating point on the certified path.

## Reproduce

```sh
python3 certificates/erdos-142/verify.py               # both checks, ~1 min
python3 certificates/erdos-142/verify.py --exhaustive  # full re-classification
```

Dependency-free. Exit 0 iff both certificates verify.

## Honest scope

- **The #142 headline is a WALL** (an open asymptotic problem); this certificate
  yields **no bound on `r₃(N)`** and does not beat `7/24`. It is a rigorous
  **no-go on a natural construction sub-family** on one fixed geometry: the
  affine/additive potentials cannot realize this geometry's rate, so a beat (if
  the geometry admits one at all) requires genuine curvature. The geometry's own
  metadata disclaims a continuum construction (`continuum_claim = false`).
- **What this certificate deliberately does *not* claim.** A stronger result — that
  *no* per-piece potential of any kind (a full quadratic "additive-local" family)
  works on this geometry — was explored in the same campaign, but its specific
  proof artifacts were not preserved (they lived untracked in a working tree and
  were overwritten as the work moved to a context-dependent lift). This
  certificate therefore certifies only what is independently re-verifiable today:
  the enumeration lock and the affine-family no-go. The genuinely-quadratic and
  context-lift questions remain open lines, not settled here.
- **Method, for reuse.** Exact enumeration of a construction's constraint class
  into self-certifying cells, plus exact Farkas no-gos on parameter sub-families,
  is a general lane for deciding "can this fixed geometry realize the target rate"
  questions without trusting any solver.

## Provenance

ProjectForty2 / CHRONOS — session
`arena/research_sessions/res_20260712_erdos142_graph_directed_crossing` (E142
agent `be9535f51392`), 2026-07-13; artifacts re-verified from the DGX mirror
`~/erdos142_scratch/{complete_enum,complete_handelman}_20260713/` before
packaging. Related campaign context:
[`certificates/erdos-13`](../erdos-13), the R(5,5) and kissing certificate repos.

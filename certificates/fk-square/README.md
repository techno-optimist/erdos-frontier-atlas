# Furstenberg–Katznelson square — certified `D(N)` table + density fences

**Problem.** `D(N)` = maximum size of `A ⊆ [N]²` containing **no** axis-aligned
square `{(x,y), (x+d,y), (x,y+d), (x+d,y+d)}`, `d ≥ 1` (all four corners in `A`).
The Furstenberg–Katznelson multidimensional Szemerédi theorem (J. Analyse Math.
34, 1978), instantiated at the pattern `F = {(0,0),(1,0),(0,1),(1,1)}`, gives
`D(N) = o(N²)`: for every `δ > 0` there is an `N₀(δ)` beyond which every subset
of density `≥ δ` contains such a square. The ergodic proof produces **no
computable `N₀(δ)`**, and no effective bound for the four-point square is known
(the two-dimensional *corner* is effective — Shkredov — but corner-effectivity
does not transfer to the square; see `atlas/effectivization_shortlist.json`).
This directory certifies the exact finite table, which the theorem does not give.

## What is certified

```
D(1..9) = 1, 3, 7, 12, 17, 24, 32, 41, 51
```

Exact, by a dependency-free branch-and-bound over row bitmasks (decision search
at `D` and at `D+1`), cross-checked inside `verify.py` by:

- **exhaustive enumeration for `N ≤ 4`** — all `2^(N²)` subsets of the grid are
  checked, nothing pruned (that is the entirety of what is brute-forced);
- **an independent cell-level DFS for `N ≤ 6`** — different model, no shared
  code path with the row solver;
- **a stored extremal witness per `N`**, re-verified square-free by an `O(N³)`
  scan over all `(x, y, d)`;
- **planted-square negative controls** — the same scan must *flag* each witness
  with a square forced into it, and the full grid (the checker is shown to be
  able to fail).

**Cutoff, stated honestly.** Per-`N` wall budget: 600 s, single-threaded
CPython, one laptop core. `N = 10` did **not** close within budget (best
square-free configuration found before the wall: 60 cells — not certified).
The table stops at `N = 9` because of compute, not because the problem ends
there.

**External consistency (not part of the certificate).** The values coincide
with [OEIS A227133](https://oeis.org/A227133)(1..9) = 1,3,7,12,17,24,32,41,51;
a(9) is credited there to an independent exhaustive search. The larger known
values (a(10) = 61 … a(13) = 98) required, per the OEIS comments, up to a
141-day 32-core Gurobi MIP run — the practical wall for exact values is real.
No novelty is claimed for the numbers; the artifact is the replayable
certificate and the fence framing. (The WS4 shortlist's feasibility guess of
"pure-Python exact to N ≈ 15–18" was optimistic; measured: `N ≤ 9` at
≤ 10 min/`N`.)

## The fence

For pinned densities `c`, the last `N` in the computed range with
`D(N) ≥ ⌈cN²⌉`:

| `c` | `⌈cN²⌉` at `N = 9` | last `N` with `D(N) ≥ ⌈cN²⌉` | crossed within range? |
|-----|--------------------|-------------------------------|------------------------|
| 1/2 | 41 | **9** | no |
| 1/3 | 27 | **9** | no |
| 1/4 | 21 | **9** | no |

This is an empirical LOWER FENCE for the ineffective F-K threshold at density
c — larger exceptions NOT excluded.

Reading it: square-free sets of density `≥ c` exist at **every** `N ≤ 9` for
all three pinned densities (`D(9)/81 ≈ 0.63`), so within the computed range no
pinned density has been crossed — each fence is the degenerate value `N = 9`,
i.e. the certificate establishes `N₀(c) > 9` and nothing more. For `c = 1/2`
the best-known constructions in the OEIS entry (uncertified here) already push
the last exception to `≥ 24`; for `c = 1/3` and `1/4`, corner-free
Behrend-type constructions (corner-free ⇒ square-free) keep the density above
`c` to astronomically large `N`. A fence table for *this* statement becomes
non-degenerate only far beyond exact single-machine search — that is itself a
measured finding about the statement, and it is recorded as such rather than
dressed up.

## Honest scope

- The certificate certifies the computed range **only** (`N ≤ 9`). Nothing
  about `N ≥ 10` is certified; larger exceptions are not excluded, and for
  `c = 1/2` they are in fact expected (see above).
- The ineffectivity re-verification is a separate gate the lead applies before
  any fence claim ships — the effectivization frontier moves (the shortlist's
  check is dated; re-verify at ship time).
- Generation and the main recompute share the algorithm (a replay, not an
  independent proof of the solver's correctness); independence comes from the
  `N ≤ 4` exhaustive check, the `N ≤ 6` cell-DFS, the witness scans, and the
  external OEIS agreement.
- The solver's symmetry breaking (column flip on the first row, vertical flip
  via a popcount constraint) and pair-cap pruning are exactness-preserving
  reductions of the *decision* problem; they are documented in `verify.py`
  where they are used.

## Reproduce

```sh
python3 certificates/fk-square/verify.py
```

Dependency-free (Python stdlib only, no third-party imports). Recomputes the
whole table — the `N = 9` optimality proof dominates the runtime (~2 min
measured on a laptop core; per-`N` generation times are in `table.json`) —
then re-checks every witness, the negative controls, and the fence table.
Exit 0 iff everything holds; the JSON verdict is printed to stdout.

`table.json` carries `D`, per-`N` extremal witnesses, per-`N` compute seconds,
densities, the fence table, and the cutoff record.

## sha256

```
eabaebd03fb7640a666fd3e2a34d2a4d269b3111ecdaded2718f58d4c5c12f7e  table.json
4b2b8599308b892c879a6ce8ffdee4aa2594b684bbac6b4bde88caa96ea9d700  verify.py
```

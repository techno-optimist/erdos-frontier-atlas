# Certificate-size observatory — first emitted-size measurements (WS5)

Every number in this directory is an **emitted-proof size**: the size of the
DRAT proof one *pinned pipeline* (encoding + solver version + config + seed)
happened to emit for a formula — an **achievable upper bound on proof length
under that pipeline, not a minimal certificate**. Minimal proof size is a
proof-complexity quantity solvers do not compute, and no claim about shortest
proofs is made here. The charter's cautionary exhibit
([`FRONTIER_CARTOGRAPHY.md`](../FRONTIER_CARTOGRAPHY.md), WS5) is the standing
reminder: CDCL emits exponential DRAT for pigeonhole formulas whose *minimal*
DRAT certificates are polynomial — the observatory measures the former and must
never call it the latter.

## What was measured

The `R(3,k)` upper-half family: the deterministic encoding `r3k-edge-cnf`
([`tools/gen_r3k_cnf.py`](../tools/gen_r3k_cnf.py)) of "`K_n` (at `n = R(3,k)`)
admits a 2-coloring with no red triangle and no blue `K_k`", which is UNSAT —
under **two pinned pipelines that differ only in the encoding's clause order**
(the charter's encoding-variance axis):

- `r3k-cadical300-drat-v1` — encoding `r3k-edge-cnf v1.0.0`, **lex** order
  (red block then blue block);
- `r3k-cadical300-drat-v1-interleaved` — encoding
  `r3k-edge-cnf v1.0.0-interleaved`, the **same clause set** with the red/blue
  streams interleaved pair-wise (`--order interleaved`). At `(k=3, n=6)` this
  reproduces the committed
  [`certificates/ramsey-3-3/problem.cnf`](../certificates/ramsey-3-3/problem.cnf)
  — produced by an independent earlier session — **byte-identically**
  (regression-tested in
  [`tests/test_gen_r3k_cnf.py`](../tests/test_gen_r3k_cnf.py)).

Everything else is shared and pinned in full in [`pipeline.json`](pipeline.json):
CaDiCaL 3.0.0 (Homebrew), default config, plain-text DRAT via `--no-binary`,
seeds {1, 2, 3} via `--seed`, checked by drat-trim @
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985` (verdict = the `s VERIFIED`
substring, never the exit code). Raw records with commands and sha256s:
[`measurements.json`](measurements.json).

| point | n | vars / clauses | order | emitted DRAT bytes (seeds 1/2/3) | solve s | check s | status |
|---|---|---|---|---|---|---|---|
| `R(3,3)` | 6 | 15 / 40 | lex | 247 / 247 / 247 (byte-identical) | ~0.005 | ~0.04 | all `s VERIFIED` |
| `R(3,3)` | 6 | 15 / 40 | interleaved | 247 / 247 / 247 (byte-identical, **same proof as lex**) | ~0.005 | ~0.05 | all `s VERIFIED` |
| `R(3,4)` | 9 | 36 / 210 | lex | 565,470 / 574,869 / 561,523 | ~0.06 | ~0.1 | all `s VERIFIED` |
| `R(3,4)` | 9 | 36 / 210 | interleaved | 577,593 / 559,037 / 547,216 | ~0.07 | ~0.1 | all `s VERIFIED` |
| `R(3,5)` | 14 | 91 / 2,366 | lex | **5,253,767,512 B** (seed 1, solve 2,531 s) · **6,033,729,549 B** (seed 2, solve 3,981 s) — both **s VERIFIED** (memory-guarded drat-trim); seed 3 aborted by the operator (shared-host protection), no datum | ~13.8% spread over 2 seeds | sha256-pinned, retained off-repo (5.0/5.6 GiB) | measured at a 6 GiB cap on an aarch64-linux host (source-built CaDiCaL 3.0.0; same CNF sha256 as the Mac — the generator is cross-platform byte-deterministic). The earlier 300 MB-cap DNFs (kept below) were **cap artifacts** |
| `R(3,5)` | 14 | 91 / 2,366 | lex (300 MB cap, superseded) | DNF at every seed (>316 MB at abort, ~60–70 s in) — retained as the honest record of the first attempt's cap | — | — | superseded by the 6 GiB-cap run above |
| `R(3,5)` | 14 | 91 / 2,366 | interleaved | not attempted (Mac-tier tiny instances only) | — | — | — |

Timings are wall-clock on one arm64 macOS machine — context, not pinned
quantities.

## Seed variance

- **R(3,3), n=6:** degenerate under both orders — all six runs (2 orders × 3
  seeds) emit the byte-identical 247-byte proof (one sha256), which is also
  byte-identical to the committed
  [`certificates/ramsey-3-3/proof.drat`](../certificates/ramsey-3-3/proof.drat)
  from an independent earlier run. The instance is decided before the search
  ever consults the seed *or* feels the clause order. This point says nothing
  about variance; it does show pipeline stability. (One instance; not a
  general claim.)
- **R(3,4), n=9, lex:** real — 561,523 to 574,869 bytes across seeds, a spread
  of 13,346 bytes ≈ **2.4 % of the mean** (567,287). All three verified.
- **R(3,4), n=9, interleaved:** real — 547,216 to 577,593 bytes across seeds,
  a spread of 30,377 bytes ≈ **5.4 % of the mean** (561,282). All three
  verified.
- **R(3,5), n=14, lex:** two completed seeds spread ~13.8% of their mean
  (5.25 vs 6.03 GB) — the relative seed spread GROWS with instance size
  (0% at R(3,3), 2.4–5.4% at R(3,4), ~13.8% here over only 2 seeds). The
  earlier 300 MB-cap DNFs were seed-robust but measured only the cap.

## Cross-encoding variance (order vs seed)

The charter requires the encoding axis be measured before any family trend is
read. Two encodings of the **same clause set** — lex and interleaved order —
now have full 3-seed measurements on both completed family points. The key
question: does clause ORDER move emitted size more or less than seed does?

- **R(3,3), n=6:** both axes degenerate — order spread 0, seed spread 0; one
  proof sha256 across all six runs.
- **R(3,4), n=9:** **order does not move emitted size more than seed does.**
  The shift of per-order means is 6,005 bytes (~1.1 % of the pooled mean
  564,285); the seed spread *within* an order is larger — 13,346 bytes (lex)
  and 30,377 bytes (interleaved). The two per-order seed ranges fully overlap
  (the lex range [561,523, 574,869] sits inside the interleaved range
  [547,216, 577,593]). Both axes land in the same few-percent band. Three
  seeds per order: a coarse reading, no significance claim.
- Seed pairing across encodings is **not meaningful** (seed *i* under lex has
  no correspondence to seed *i* under interleaved), so no paired-difference
  statistic is quoted; per-record numbers are in
  [`measurements.json`](measurements.json).

## What is *not* claimed

- **No growth-law fit.** The charter gate requires **≥ 3–4 completed family
  points before any fit**; we now have **three** (k=3, k=4, k=5) — the bare
  minimum — and the fit is still withheld: the R(3,5) order axis is unmeasured,
  only 2 seeds completed there, and cross-machine size comparability is untested.
  The observed ratios (~×2,284 then ~×10,000) are reported as ratios, not a law.
  named. The jump 247 → ~567 K → >300 MB is *suggestive* of rapid growth under
  this pipeline and is left at that. Points from the two pipelines are two
  separate series and are never mixed into one curve.
- **The DNF is pipeline-relative.** Under this no-symmetry-breaking encoding
  and default CaDiCaL, the emitted plain-text DRAT for `R(3,5)` exceeds 300 MB.
  That is a recorded property of the pipeline on this instance — not of the
  instance in itself. A symmetry-broken encoding would be a **new pipeline_id**
  and a new curve, per the pinning discipline; cross-pipeline comparison is the
  point of recording both, but points from different pipelines are never mixed
  into one curve.
- **The encoding axis is two points wide.** Lex vs interleaved varies *clause
  order only* — the mildest possible encoding perturbation. Encodings that
  change the clause set itself (symmetry breaking, different variable schemes)
  are unexplored here, and the order axis at `R(3,5)` is unmeasured. "Order
  moves size less than seed at R(3,4)" is an observation about this instance
  under this pipeline pair, not a general law.

**Operational lesson (recorded 2026-07-19).** Gigabyte-scale solve + verification
twice destabilized the shared host it ran on (load events from proof-stream writes
and memory-guarded checking beside production services), and the third seed was
aborted rather than risk a third event. Heavy observatory points are
dedicated-window work; the caps and the abort are part of the record.

## Replay

```sh
# lex (default; encoding v1.0.0)
python3 tools/gen_r3k_cnf.py 4 9 -o problem.cnf
# interleaved (encoding v1.0.0-interleaved; same clause set, different order)
python3 tools/gen_r3k_cnf.py 4 9 --order interleaved -o problem.cnf

cadical --no-binary --seed=1 problem.cnf proof.drat   # CaDiCaL 3.0.0; exit 20 = UNSAT
drat-trim problem.cnf proof.drat                      # expect substring: s VERIFIED
```

CaDiCaL is deterministic for a fixed version, options, and input, so
`emitted_drat_bytes` and the proof sha256 are expected to reproduce exactly
with the pinned version (observed here: the R(3,3) rerun reproduced a
proof emitted in an independent session byte-for-byte — under both clause
orders). The k=4 lex seed-1 artifacts are archived under
[`certificates/ramsey-3-4/`](../certificates/ramsey-3-4/) (with the mandatory
truncated-proof negative control, which must report `s NOT VERIFIED`); the
interleaved runs are not separately archived — their CNFs and proofs
reproduce deterministically from the pinned pipeline (and at `R(3,3)` they
*are* the committed `ramsey-3-3` files, byte for byte). The `R(3,5)` attempts
produced no completed proof, so nothing from them is archived.

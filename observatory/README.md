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

The `R(3,k)` upper-half family: the deterministic encoding
`r3k-edge-cnf v1.0.0` ([`tools/gen_r3k_cnf.py`](../tools/gen_r3k_cnf.py)) of
"`K_n` (at `n = R(3,k)`) admits a 2-coloring with no red triangle and no blue
`K_k`", which is UNSAT. Pipeline `r3k-cadical300-drat-v1`, pinned in full in
[`pipeline.json`](pipeline.json): CaDiCaL 3.0.0 (Homebrew), default config,
plain-text DRAT via `--no-binary`, seeds {1, 2, 3} via `--seed`, checked by
drat-trim @ `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` (verdict = the
`s VERIFIED` substring, never the exit code). Raw records with commands and
sha256s: [`measurements.json`](measurements.json).

| point | n | vars / clauses | emitted DRAT bytes (seeds 1/2/3) | solve s | check s | status |
|---|---|---|---|---|---|---|
| `R(3,3)` | 6 | 15 / 40 | 247 / 247 / 247 (byte-identical) | ~0.005 | ~0.04 | all `s VERIFIED` |
| `R(3,4)` | 9 | 36 / 210 | 565,470 / 574,869 / 561,523 | ~0.06 | ~0.1 | all `s VERIFIED` |
| `R(3,5)` | 14 | 91 / 2,366 | **DNF** — proof stream crossed the 300 MB cap at every seed (>316 MB at abort, ~60–70 s in; 900 s budget unused) | — | — | nothing verified, nothing archived |

Timings are wall-clock on one arm64 macOS machine — context, not pinned
quantities.

## Seed variance

- **R(3,3), n=6:** degenerate — the three proofs are byte-identical (one
  sha256). The instance is decided before the search ever consults the seed.
  This point therefore says nothing about seed sensitivity. (It does show
  pipeline stability: the emitted proof is byte-identical to the committed
  [`certificates/ramsey-3-3/proof.drat`](../certificates/ramsey-3-3/proof.drat)
  from an independent earlier run, even though the generated CNF differs from
  the committed one in clause order — logically identical, unit-tested in
  [`tests/test_gen_r3k_cnf.py`](../tests/test_gen_r3k_cnf.py). One instance;
  not a general claim.)
- **R(3,4), n=9:** real — 561,523 to 574,869 bytes across seeds, a spread of
  13,346 bytes ≈ **2.4 % of the mean** (567,287). All three verified.
- **R(3,5), n=14:** the DNF is seed-robust — all three seeds hit the size cap.

## What is *not* claimed

- **No growth-law fit.** The charter gate requires **≥ 3–4 completed family
  points before any fit**; we have **two** (k=3, k=4) plus a seed-robust DNF at
  k=5. Two points constrain nothing, so no curve is drawn and no growth rate is
  named. The jump 247 → ~567 K → >300 MB is *suggestive* of rapid growth under
  this pipeline and is left at that.
- **The DNF is pipeline-relative.** Under this no-symmetry-breaking encoding
  and default CaDiCaL, the emitted plain-text DRAT for `R(3,5)` exceeds 300 MB.
  That is a recorded property of the pipeline on this instance — not of the
  instance in itself. A symmetry-broken encoding would be a **new pipeline_id**
  and a new curve, per the pinning discipline; cross-pipeline comparison is the
  point of recording both, but points from different pipelines are never mixed
  into one curve.
- **Variance axes are incomplete.** The charter asks for variance across the
  encoding axis too before a family trend is read; only the seed axis is
  measured here.

## Replay

```sh
python3 tools/gen_r3k_cnf.py 4 9 -o problem.cnf
cadical --no-binary --seed=1 problem.cnf proof.drat   # CaDiCaL 3.0.0; exit 20 = UNSAT
drat-trim problem.cnf proof.drat                      # expect substring: s VERIFIED
```

CaDiCaL is deterministic for a fixed version, options, and input, so
`emitted_drat_bytes` and the proof sha256 are expected to reproduce exactly
with the pinned version (observed here: the R(3,3) rerun reproduced a
proof emitted in an independent session byte-for-byte). The k=4 seed-1
artifacts are archived under
[`certificates/ramsey-3-4/`](../certificates/ramsey-3-4/) (with the mandatory
truncated-proof negative control, which must report `s NOT VERIFIED`); the
`R(3,5)` attempts produced no completed proof, so nothing from them is
archived.

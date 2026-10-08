# F003 selected Lean source audit

**Verdict: source trace found no added analytic premise in the selected theorem; formal verification remains unperformed.** This is an independent model review of source wiring and selected definitions, not a human mathematical audit or a proof certificate. The source pin is `adc7f1241b42e322a6451854ab7e4b4c146bf78a` in [openai/math](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a). No canonical graph status changes follow.

## What was actually selected

[QuasiRiemannHypothesis.json](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/ComparatorChallenges/QuasiRiemannHypothesis.json) selects solution module `OAI.NumberTheory.DirichletL.Nonvanishing` and theorem `OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re`. Its permitted axiom list is exactly `propext`, `Quot.sound`, `Classical.choice`; `enable_nanoda` is false. This is configuration, not evidence that the comparator passed locally.

The selected [solution](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/OAI/NumberTheory/DirichletL/Nonvanishing.lean#L29) has only `{s : ℂ}` and `hs : (7 / 8 : ℝ) < s.re`, concluding `riemannZeta s ≠ 0`. The neighboring Dirichlet theorem explicitly uses `_root_.DirichletCharacter.LFunction`, with positive modulus and the principal-pole exclusion. The comparator challenge's `sorry` is a target placeholder; it is not the selected implementation.

## Dependency trace and nonvacuity checks

The following is a trace of proof calls and selected semantic definitions, not a line-by-line proof review of the entire imported library.

1. `Nonvanishing.lean:29` calls `Detector/FinalAssemblyUnconditional.lean:43`. Its `detector_certified_bands` at line 15 constructs the needed universal certified-band proposition by calling `Energy/CertifiedExistence.terminal_certificate`, with explicit smooth conjugate source window and scalar parameters. The temporary hypothesis `7/8 < beta` is the contradiction branch, not an extra hypothesis in the result.
2. `Energy/CertifiedExistence` inducts from `certified_floor` through `CappedAnalyticSuccessor.actual_successor`. That step combines `CappedLowStage.actual_capped_low`, `NaturalHighStage.actual_high_stage`, and `NaturalZeroStage.actual_zero_stage`. Their previous-band hypotheses are threaded from the induction, rather than retained as assumptions of the exported theorem. These three interface proofs were read, but their full analytic dependency trees were not reviewed mathematically.
3. `FinalAssemblyCertifiedBands` turns the certificate into the three source moment estimates. `FinalAssemblyChosenData` chooses actual data, source, and counting parameters, absorbs polynomial height loss by choosing a positive height exponent, and supplies `UniformCommonProbe`.
4. Nonemptiness is explicitly addressed: `ParametersHighDataFine.exists_high_data_fine` constructs a `HighData` record from positive scalar budgets and physical slot lengths; `FinalAssemblyData.exists_source_data` chooses a nonzero smooth source, and `source_count_parameters` calls the counting-parameter existence theorem. This rules out the immediate concern that the final universal source statement works only because its displayed data type is empty. The underlying existence lemmas still require a formal build and mathematical review.
5. `Hecke/CommonProbe.beta_le_seven_eighths` combines the constructed common probe with a zero near the supremum, then applies `HeckeSignal.nonzero_of_probe_bounds` to contradict that zero. `Hecke/ZeroSupremum.zeroRealParts` is defined using actual zeros of `HeckeFamily.LFunction`; `beta` is their supremum after adjoining the sentinel `1/2`. The sentinel handles the empty-zero case, and the bound by 1 comes from the classical Euler-product region. There is no definition setting beta to 7/8.
6. `Hecke/IdealBridge.lean:95` defines the auxiliary Hecke function as `continuedLattice χ s / 6` and proves its ideal Dirichlet-series identity for `Re s > 1`. `Hecke/Family.lean:91` identifies `continuedLattice` with the theta-defined lattice L-function. `Hecke/Dirichlet.lean:112,128` proves that the norm-pullback Hecke function equals the product of two Mathlib Dirichlet L-functions, first in the Euler-product half-plane and then by analytic continuation away from 0 and 1. The nonzero product supplies the canonical Dirichlet conclusion. Thus this inspected endpoint is not merely a statement about an unrelated function named zeta.
7. The zeta wrapper explicitly handles `s = 1` via Mathlib's `riemannZeta_one_ne_zero`. Lean treats zeta as a total function with an assigned value at its pole. This does not assert that the meromorphic zeta function has a finite analytic value there; away from that convention the region is the intended open half-plane. No claim at the line `Re s = 7/8` is made.

## Bounded scan and build boundary

The read-only import scanner in [fetch_source_closure.py](fetch_source_closure.py) fetched a breadth-first prefix of **2,000 OAI source files, 20,015,600 bytes**, following imports from the actual solution. The limit was deliberate. **84 distinct OAI modules remain on the frontier**, so this is not a complete transitive closure. There were no fetch errors in the recorded prefix. The scan strips nested comments and strings and looks for the explicit token classes recorded in the script, including `axiom`, `sorry`, `sorryAx`, `admit`, `unsafe`, `native_decide`, and command-elaboration hooks. It found zero such flags in this OAI prefix. This lexical observation is weaker than an elaborated axiom report, and says nothing about unseen or external modules. Some broad Foundation imports are irrelevant to the theorem's eventual proof term.

The external import boundary includes Mathlib, `PrimeNumberTheoremAnd.Wiener`, and `RellichKondrachov.Analysis.FunctionalSpaces.Sobolev.Euclidean.Rellich`. These dependency sources were not scanned here. The manifest contains 42 packages; Mathlib is pinned to `d13f23b723b8a846827a245b89c10fc7d3f11612`.

The required toolchain is `leanprover/lean4:v4.34.1`. `lean`, `lake`, `elan`, and `comparator` were absent from PATH. No installation, build, comparator run, `#print axioms`, or independent kernel check was performed.

**A material reproducibility finding:** `lean/lakefile.lean` contains executable configuration. At lines 263 onward, a `run_cmd` invokes compatibility preparation before dependency resolution, cloning and patching 11 pinned packages. Its `post_update` verifies these and applies patches to 12 further packages. The configuration uses `unsafe env.evalConstCheck` to read Lake dependency declarations. This is outside the OAI theorem-source scan and is not itself evidence of a logical axiom or theorem flaw. A faithful build audit must inspect the patch files and resulting package state; merely recording Git revisions is insufficient. The lakefile was read, never executed. Patch contents and external packages remain unaudited.

Other open obligations are full OAI import closure, actual Lean elaboration and axiom dependency checking, comparator statement equivalence, and mathematical review of the low/high/zero moment estimates and signal contradiction. Therefore downstream F003 deductions remain **conditional on the external theorem**, even though this source trace found no immediate assumption-smuggling or endpoint-function substitution.

## Receipts and reproduction

[audit.json](audit.json) records exact paths, SHA-256 hashes, scope and verdicts. [source-prefix-manifest.json](source-prefix-manifest.json) records every scanned source's hash/imports plus the unvisited frontier and external boundary. Source bytes remain in `/tmp/efa-f003-source-audit`; they were fetched from pinned raw GitHub URLs, never executed. The repository's earlier recursive GitHub tree cache was truncated, so this audit followed actual import paths instead of interpreting absent tree entries as absent files.

Command used, from the repository root:

```sh
python3 experiments/openai-math-20261006/research-sprint/source-audit/fetch_source_closure.py --cache /tmp/efa-f003-source-audit --output /tmp/efa-f003-source-audit/closure.json --limit 2000
```

The scanner is a locally written standard-library HTTP reader. It does not execute Lean or downloaded build scripts. Cached files retain their recorded hashes; for a fresh independent fetch, use an empty cache directory.

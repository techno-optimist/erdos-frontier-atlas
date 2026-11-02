# Erdős #357: arbitrary-order improvement

This project formalizes the theorem in the adjacent `PROOF.md` for the
arbitrary-order sequence A364153. It assumes no monotonicity of the row.
The conclusion is

```
((3 : ℝ) / 2 + 1 / (10 : ℝ) ^ 10) * (k : ℝ) < (N : ℝ)
```

under the exact hypotheses in `Challenge.lean`, including `10^22 ≤ k` and
injectivity of **all** inclusive consecutive-block sums together.
`Challenge.lean` and `Solution.lean` have identical theorem headers.
The challenge is deliberately excluded from the build and the import graph.

The pins are Lean `leanprover/lean4:v4.33.1` and Mathlib commit
`0df444a360eaa60ab8c11dca51a86af692955474`. The manifest also fixes every
transitive Lake dependency.

From this directory, with Elan installed:

```sh
lake exe cache get
lake build
python3 verify_source.py
```

`lake build` builds `Solution` and `AxiomAudit`. The latter checks the main
theorem's printed transitive axiom list against exactly
`[propext, Classical.choice, Quot.sound]`.

| PROOF.md step | Lean theorem | File |
|---|---|---|
| 1: span bound | `Erdos357.step1_span` | `Erdos357/Span.lean` |
| 2: small entries | `Erdos357.step2_few_small` | `Erdos357/SmallEntries.lean` |
| 3: displacement | `Erdos357.step3_packing_stability` | `Erdos357/Stability.lean` |
| 4: bounded Lipschitz estimate | `Erdos357.step4_test_function` | `Erdos357/Empirical.lean` |
| 5: eight correlations | `Erdos357.step5_negative_correlations` | `Erdos357/Correlation.lean` |
| 6: nine-term contradiction | `Erdos357.step6_nine_term_contradiction` | `Erdos357/Gram.lean` |

The span lemma writes the real quantity `k^(3/2)` as `k * Real.sqrt k`.
The cutoff uses the natural-number ceiling of `(1/2 - 1/10000) * k`.

There is one convenient change in the retained set: the formal proof retains
every block sum at least `L`. This includes all blocks retained in PROOF.md.
A discarded block has its first entry below `L`, so at most `h*q` blocks are
discarded. This is at most the note's `h*(h+1)/2*q` for `h ≥ 1`.
The lower packing bound and upper total-sum bound still apply, and every
displayed final constant is unchanged. This is a stronger counting estimate,
not a correction to the argument.

The integral in step 4 is formalized directly. The trigonometric computation
uses Mathlib's exact sine and cosine theorems and the rational bound
`Real.pi < 63/20 < 10/3`. No numerical quadrature is used.
The nine-term identity is written as the sum of the squared real cosine sum
and the squared real sine sum. Its exact boundary correction is `273`, as in
PROOF.md.

The source audit reports line counts including comments and blank lines, and
hashes all Lean sources and dependency pins. It is supplementary to the Lean
kernel build; it is not itself a proof checker.

## Verification recorded on 2026-11-02

Proof commit: `a1d06748b5507a62a9d3c068b55b202875354684`.
A fresh Git clone rebuilt all project modules successfully. Only the pinned
dependency cache was reused; no project build objects were copied.
The clone remained clean, and its source audit matched the committed audit.

- [Complete build output](verification/clean-build.log):
  `Build completed successfully (8718 jobs).`
- [Axioms output](verification/axioms.log):
  `[propext, Classical.choice, Quot.sound]`.
- [Machine-readable receipt](verification/receipt.json).
- [Source audit and hashes](source-audit.json): 1,153 proof lines, or 1,172
  total Lean lines including the 14-line challenge and 5-line axiom audit.
  Counts include comments and blank lines; `Solution.lean` itself is 20 lines.

The repository graph check passed, and the repository test suite reported
275 passed and 2 skipped. The earlier nineteen-value and finite-example
checks were rerun without any numerical changes.

# Erdős #357, any order: a Lean-checked lower bound a(k) > (3/2 + 10⁻¹⁰)k for k ≥ 10²²

**Problem node `P357`; OEIS [A364153](https://oeis.org/A364153) (sequences in any order).**
a(k) is the least N such that some k distinct integers in {1, …, N}, listed in some
order, have all consecutive-block sums x_u + ⋯ + x_v pairwise distinct.

## What is here

**For every k ≥ 10²², a(k) > (3/2 + 10⁻¹⁰)k: a Lean-checked lower bound for the
any-order version, AI-written and with AI-only review, not refereed.** With the trivial
bound and the span estimate it gives, for every k, a(k) ≥ max{k, ⌈(3/2 + 10⁻¹⁰)k − 12√k⌉}.
The lower bound previously cited for the any-order version is (3/2 − o(1))k (Hegyvári 1986).

- **Credit.** The argument and the Lean formalization are by Kevin Russell with GPT Astra.
  Ford (ProjectForty2) did the math audit, the exact-arithmetic checks and numerics, the
  literature check and the Lean audit.
- **Lean.** Lean 4.33.1, Mathlib `0df444a360eaa60ab8c11dca51a86af692955474`, theorem
  `erdos357_any_order_improvement` in `lean/Solution.lean`. Ford rebuilt it from the pinned
  source; the theorem and its six step lemmas depend only on `propext`,
  `Classical.choice` and `Quot.sound`; three kernels accepted it (nanoda, 42,184
  declarations; con-ron, 40,350; Lean's own `leanchecker --fresh`); the statement was judged
  faithful and non-vacuous (the k = 19, N = 29 row satisfies every hypothesis except
  k ≥ 10²², kernel-checked in `lean_audit/Witness.lean`).
- **How small.** The gain over 3/2 is 10⁻¹⁰ in the constant, and it applies only for
  k ≥ 10²². It says nothing about any computed value of A364153.
- **Review.** The argument and the formalization are AI-written, and review so far is
  AI-only (Ford's audit plus one outside model reading). No human expert has reviewed it.
  It needs expert eyes before anyone relies on it. Erdős #357 itself remains open.

## Scope note: increasing order versus any order

Two different functions share problem #357. Erdős and Harzheim's f(n) counts
*increasing* sequences (OEIS A364132); the any-order g(n) (OEIS A364153 is its inverse)
drops monotonicity. Results for increasing sequences do not transfer to any order:

- The 2026 increasing-order claims (Lenthall-Cleary; Pickhardt / Paratelligent) are about
  increasing sequences and say nothing directly about A364153 or the any-order g.
- Coppersmith and Phillips's bound 2/3 − 1/512
  ([abstract](https://research.ibm.com/publications/on-a-question-of-erdos-on-subsequence-sums))
  is stated for an increasing sequence.
- The [erdosproblems.com page for #357](https://www.erdosproblems.com/357) currently
  attributes the Coppersmith–Phillips bound to the any-order g. Adenwalla's
  [forum post #5308](https://www.erdosproblems.com/forum/thread/357#post-5308)
  (2026-04-09) notes that it should apply only to f. We agree with that reading, but we
  would welcome correction. Either way the bound proved here is a lower bound on a(k)
  and does not depend on that question.

The novelty search found no earlier any-order improvement over Hegyvári's 3/2, but the
search is not exhaustive.

## Replay

```sh
python3 -I certificates/erdos-357/anyorder/verify_anyorder_lean.py          # static audit, ~1 s, dependency-free; not certifying
python3 -I certificates/erdos-357/anyorder/verify_anyorder_lean.py --full   # + lake build and axiom checks (needs elan and the Mathlib cache)
```

The fast run checks the pinned sha256 of the zip, the receipts and the audit files;
that `lean/` equals the zip byte for byte; the 15 source hashes printed in the Lean
receipt; identical Challenge and Solution headers; an escape-hatch grep; the toolchain and
Mathlib pins; and it rejects eight planted failures (a flipped zip bit, `sorry` in
Solution, a declared axiom, the Challenge bound weakened to 10², a `native_decide`, and
three bad axiom lists). `--full` copies `lean/` and `lean_audit/` to a temporary
directory outside the repository, runs `lake exe cache get` and `lake build`, and
requires the printed axioms of the theorem, its six step lemmas and the cross-check to be
the standard three, the witness file to elaborate, and the `pp.all` statements of
Challenge and Solution to agree. The independent-kernel runs are recorded in the Lean
receipt and are not re-run by this script. Ford ran `--full` on these exact files on 2026-11-02 and it
passed: `lake build` clean, the eight declarations on `[propext, Classical.choice, Quot.sound]`,
and the CrossCheck, Witness and `pp.all` checks all matched.

## Files

| file | role |
|---|---|
| `erdos_357_anyorder_math_audit_20261102.txt` | the math audit receipt (Ford) |
| `erdos_357_anyorder_lean_audit_20261102.txt` | the Lean audit receipt (Ford); sha256 e0eba9c3… pinned, kept byte for byte |
| `erdos357_anyorder_lean_a1d0674.zip` | the Lean project as received (sha256 52a688a1a16a7b0c9e133cd1f61a3562e8c101740d440dbcd8b795410aa7602f) |
| `lean/` | the same project unpacked (no `.lake`) |
| `lean_audit/` | Ford's audit files: AuditAxioms, CrossCheck, IdChallenge, IdSolution, Witness |
| `proof_for_review.md` | a compact restatement of the full argument |
| `audit.md` | the step-by-step math audit and the reviewer concerns resolved |
| `check_constants.py` / `.out` | every numeric constraint in exact rationals at K = 10²² |
| `verify_eps_exact.py` / `.out` | the epsilon bookkeeping, exact (needs mpmath) |
| `check_delta_symbolic.py` / `.out` | the step-3 Δ bound, symbolic (needs sympy) |
| `numerics.py` / `.out` | the window identity and partial-sum bounds on small admissible rows (needs mpmath) |
| `review_nvidia_nemotron-3-ultra-550b-a55b.txt` | one outside model reading (verdict VALID) |
| `verify_anyorder_lean.py` | the replay above; reads the files, never writes them |

`lean/README.md` is GPT Astra's and refers to an adjacent `PROOF.md` that is not in the
zip; `proof_for_review.md` restates the same argument. The proof and zip commit hashes
it quotes (a1d0674, e5e5e75) are as claimed but unverified, since the zip has no git
metadata; the zip sha256 is the pin. The Lean receipt's caveat line says
"erdosproblems.ai page"; the page meant is erdosproblems.com/357. The receipt is kept
unedited because its sha256 is pinned.

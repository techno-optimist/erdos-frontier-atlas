# Formal (Lean 4 + mathlib) refutation of the Jacobian Conjecture at n = 3

`JacobianConjectureFalse.lean` is a **machine-checked** proof that the Jacobian Conjecture, *as
formalised by the community*, is false for `k = ℚ`, `σ = Fin 3`.

## What is proved

Against the statement in [`formal-conjectures`](https://github.com/google-deepmind/formal-conjectures)
`FormalConjectures/Wikipedia/JacobianConjecture.lean`, restated **verbatim** (same `RegularFunction`,
`Jacobian`, `comp`, `id`) so the goalposts are the community's and not ours:

```lean
theorem jacobian_conjecture_false :
    ¬ ∀ (F : RegularFunction ℚ (Fin 3) (Fin 3)), IsUnit F.Jacobian.det →
        ∃ G, G.comp F = RegularFunction.id ℚ (Fin 3) ∧ F.comp G = RegularFunction.id ℚ (Fin 3)
```

Two load-bearing facts, both fully machine-checked here:

* `alpoge_jacobian_det` — `det J_F = C (-2)`, via nine explicit partial-derivative lemmas and `ring`.
* `alpoge_collision` — `F` identifies `P = (0,0,-1/4)` and `Q = (1,-3/2,13/2)`.

The bridge is the upstream `comp_aeval` lemma: a regular right inverse forces the point map to be
injective, which the collision contradicts.

## Replay

Requires the `formal-conjectures` project (Lean toolchain + mathlib):

```bash
git clone https://github.com/google-deepmind/formal-conjectures
cd formal-conjectures
lake exe cache get                       # downloads prebuilt mathlib
cp /path/to/JacobianConjectureFalse.lean FormalConjectures/Refutations/
lake build FormalConjectures.Refutations.JacobianConjectureFalse
```

Expected output includes the axiom audit:

```
'JacobianConjecture.jacobian_conjecture_false' depends on axioms:
  [propext, Classical.choice, Quot.sound]
Build completed successfully.
```

Those are Lean's three standard axioms. **No `sorryAx`** — the proof has no gaps.

## Claim-typing (read before citing)

* **The map is NOT ours.** It is Levent Alpöge's (2026-07-19, found with Claude Fable; question
  credited to Akhil), still "awaiting confirmation" — widely verified, not peer-reviewed.
* **What changes with this file.** Our earlier `verify.py` certificate established `det ≡ -2` and
  the collision by exact rational arithmetic in Python — you had to trust that engine. Those two
  facts are now proved *in Lean against mathlib's own `MvPolynomial.pderiv` and `Matrix.det`*, so
  they no longer rest on any code of ours. The remaining external dependencies are (a) attribution
  of the construction, and (b) whether the community's formalisation faithfully captures the
  informal conjecture — the standing caveat of all formalisation, which we do not claim to settle.
* This refutes the **formal statement**. It is not a claim about priority, novelty, or the
  informal conjecture's sociological status.

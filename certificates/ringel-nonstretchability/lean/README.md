# Ringel 9-element nonstretchability — machine-checked in Lean 4 + mathlib

A `sorry`-free formal proof that **Ringel's 9-element uniform rank-3 oriented matroid is not
stretchable**: no configuration of nine real points realizes its chirotope, in *either* orientation.

Unlike our [Jacobian-conjecture Lean proof](../../jacobian-conjecture/lean/), where the object was
external, **the result here is ours**. The final polynomial is Carroll (arXiv:0704.3424 eq. 96,
reproducing Björner–Las Vergnas–Sturmfels–White–Ziegler); the chirotope is Ringel's.

## What is proved

```lean
theorem ringel_not_stretchable (p : Fin 9 → Pt ℝ) :
    ¬ IsRingelRealization p ∧ ¬ IsRingelRealizationRev p
```

`IsRingelRealization` constrains only *sorted* triples — the weakest hypothesis, so the strongest
theorem. Both orientations are covered because an oriented matroid is the pair {χ, −χ}.

Four load-bearing facts:

1. **`carroll96`** — the nine-term identity (each term a product of five 3×3 brackets) is *identically
   zero* over any `CommRing`. This is stronger than the Python certificate: it is kernel-proven, so
   the identity no longer depends on our monomial expansion at all.
2. **`ringel_sign_audit`** — Ringel's chirotope forces all nine products strictly negative.
3. The contradiction: nine same-sign nonzero reals cannot sum to zero.
4. **`br_neg` (trilinearity)** — negating all nine points negates every bracket, so the reversed
   orientation reduces to the forward theorem applied to `fun i => -(p i)`.

Note on (4): there are *two independent* parity arguments. Trilinearity (3 is odd) is the one used.
The alternative — five brackets per term, and five is odd, so all nine products flip to positive and
still cannot sum to zero — is recorded in the file. Had the final polynomial been of even bracket
degree, the second route dies and trilinearity survives.

## How the certificate was found

Brute `ring` on the full identity is **not viable**: 27 variables at degree 15 (~70k monomials)
crashed at ~2 min by default and made no progress in 46 min at 3.5 GB. mathlib has no
Plücker/Grassmann-syzygy machinery to reuse (zero hits repo-wide).

Instead: enumerate all **1890** quadratic Grassmann–Plücker relations on 9 elements (630 three-term,
1260 four-term), BFS two levels of degree-5 bracket monomials → 8367 candidate columns over 1598
monomials, solve over GF(2⁶¹−1) → support **10**, re-solve exactly over ℚ → **all coefficients ±1,
residual 0**. Because `br` is a plain `def`, `ring` treats brackets as opaque atoms, so each of the
ten syzygies is a small (≤6 point, degree-6) `ring` call and the assembly is one `linear_combination`.

**Structural fact worth recording: no certificate exists using only 3-term relations.** Six of the ten
required are genuine 4-term Plücker relations — a "classical syzygy only" approach dead-ends.

## Replay

```bash
git clone https://github.com/google-deepmind/formal-conjectures && cd formal-conjectures
lake exe cache get
cp /path/to/RingelNotStretchable.lean Scratch/ && lake env lean Scratch/RingelNotStretchable.lean
```

Expected: exit 0, and **39 axiom-audit lines with no other output**. Every theorem reports
`[propext, Classical.choice, Quot.sound]`, except the 18 table lookups which report `[propext]` only
(a strict subset — they are `rfl`, nothing classical enters). **No `sorry`, no `decide`, no
`native_decide`, no new axioms.** ~5–12 s warm.

`RevNonVacuity.lean` is a companion showing the predicates are genuinely inhabited: the moment curve
satisfies the forward predicate and the antipodal moment curve the reversed one, for the all-`+1`
chirotope. So the obstruction is about Ringel's data, not about our definitions.

## Honest boundary

**The proof consumes 18 of the 84 chirotope entries — and this makes the theorem STRONGER, not weaker.**
`IsRingelRealization` demands all 84 sorted triples match, but the contradiction is derived from only
18 of them. So what is actually proved is that even those 18 constraints are jointly unsatisfiable;
`¬(all 84)` follows a fortiori. Fewer hypotheses, stronger theorem.

The real exposure is therefore NOT soundness but **data fidelity**: is this 84-entry table actually
Ringel's chirotope? A transcription error in the other 66 entries would be invisible to Lean — the
theorem would remain true *about the table as written*, while no longer being a theorem about Ringel's
matroid. That is a question about our input, not about the proof. Provenance is two links:

```
Ringel's published affine projections --(human transcription)--> es7_ringel_chirotope.py --(SHA-256)--> this table
```

Hash-pinned at the second link only; eyeball at the first. Closing this needs either a final
polynomial touching more entries, or an independent re-derivation of the table from the published
projections. Neither is a Lean problem.

Mutation-tested: flipping χ(4,6,7) breaks the build (`linarith` fails, `sorryAx` propagates into all
four results), as does replacing the table with all-`+1`. The sign data is load-bearing.

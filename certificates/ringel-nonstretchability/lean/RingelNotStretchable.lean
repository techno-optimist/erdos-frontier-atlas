/-
Copyright (c) 2026 Cultural Soliton Observatory / Project Forty Two.
Released under the Apache 2.0 license.
-/
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Data.Real.Basic

/-!
# Ringel's 9-element uniform rank-3 oriented matroid is not stretchable

## What is claimed

`ringel_not_stretchable` : for **every** map `p : Fin 9 → Pt ℝ` assigning a point of the affine
cone over the real projective plane to each of the nine elements, `p` realizes **neither
orientation** of Ringel's chirotope — neither `χ` (`ringel_chirotope_not_realizable`: it is
impossible that every sorted triple `i < j < k` have `0 < χ i j k * [p i, p j, p k]`) nor `−χ`
(`ringel_chirotope_rev_not_realizable`: nor that every sorted triple have
`0 < -χ i j k * [p i, p j, p k]`). `ringel_not_realizable_of_sign` packages the two as one
orientation-parameterised statement: for either `ε = 1` or `ε = -1`, no `p` satisfies
`0 < (ε * χ i j k) * [p i, p j, p k]` on all sorted triples.

Both orientations are needed for the headline claim, because an oriented matroid **is** the pair
`{χ, −χ}` — a configuration all of whose brackets carry the opposite sign is just as much a
stretching of Ringel's arrangement. `ringel_chirotope_not_realizable` on its own falls exactly one
reorientation short of "not stretchable"; see the parity note above
`ringel_chirotope_rev_not_realizable` for how the reversed case closes.

## Claim typing (who owns what)

* The **result** — this executable, sign-audited final-polynomial certificate and its
  formalization — is **ours** (Cultural Soliton Observatory / Project Forty Two).
* The **nine-term biquadratic final polynomial** is **Carroll, arXiv:0704.3424, equation (96)**,
  reproducing the standard final polynomial of Björner–Las Vergnas–Sturmfels–White–Ziegler,
  *Oriented Matroids*.
* The **chirotope** is **Ringel's**, transcribed from the two published affine projections in the
  oriented-matroid example database
  (`oriented.sourceforge.net/examples/ringel-0.html`, `.../ringel-7.html`).
* The Lean file is a formalization of the Python certificate
  `es7_ringel_final_polynomial.py` + `es7_ringel_chirotope.py`; the term list, the chirotope table,
  and the relabelling below were **machine-extracted** from those scripts, not retyped.

## The four load-bearing facts

1. `carroll96` — **CLAIM 1, the syzygy identity.** The nine-term sum of five-fold bracket products
   is *identically zero* as a polynomial in the 27 matrix entries, over every commutative ring.
   (Carroll eq. (96), in verbatim term-and-bracket ordering.)
2. `ringel_sign_audit` — **CLAIM 2, the sign audit.** Given the eighteen bracket signs Ringel's
   chirotope forces, each of the nine products is `< 0`; nine negatives cannot sum to `0`.
3. `ringel_chirotope_not_realizable` — the conclusion for the orientation `χ`, deriving `h1 … h18`
   from the chirotope table `chiSorted` via the relabelling `SOURCE_TO_RINGEL = (0,2,5,1,8,7,6,4,3)`.
4. `ringel_chirotope_rev_not_realizable` — **CLAIM 3, the reorientation.** The same conclusion for
   `−χ`, obtained from fact 3 by the antipodal map: `br` is trilinear and `3` is odd, so negating
   all nine points negates every bracket (`br_neg`). `ringel_not_stretchable` is the conjunction.

## Method note

`br` is a plain `def`, so `ring` treats a bracket application as an opaque **atom**. CLAIM 1 is
therefore assembled by one `linear_combination` over ten Grassmann–Plücker syzygies `gp1 … gp10`
(found by exact linear algebra over ℚ in the bracket ring; all ten coefficients are `±1`), each of
which is itself a small `ring` call on at most six points. Six of the ten are genuine **four-term**
Plücker relations: no certificate using three-term relations alone exists in the searched span.

The direct 27-variable `ring` attack does **not** work: it overflows the `Mathlib.Tactic.Ring`
interpreter stack (crash at ~2 min on the default stack; no progress in 46 min at 2 GB stack).

## Trust base

No `sorry`. No `native_decide`. No `decide`. No new axioms. The `#print axioms` audit at the bottom
is **exhaustive** — every theorem in the file, not a selection of headline ones. Each depends on at
most `[propext, Classical.choice, Quot.sound]`; the eighteen `chi_i_j_k` table lookups depend on
`[propext]` alone, since they are closed by `rfl` and nothing classical enters.

## BOUNDARY — what this file does *not* prove

**(1) Only 18 of the 84 table entries are load-bearing; the other 66 are unchecked decoration.**
The proof consumes exactly eighteen chirotope entries — the ones occurring in Carroll eq. (96)
under the relabelling — via the eighteen `chi_i_j_k` lookup lemmas:

    (0,1,3) (0,1,4) (0,1,5) (0,2,3) (0,3,6) (0,4,5) (0,6,7) (0,6,8) (0,7,8)
    (1,2,6) (1,2,7) (1,3,4) (1,5,6) (1,5,8) (1,6,7) (2,5,6) (3,6,8) (4,6,7)

The remaining **66 entries are never consumed by any proof in this file**: a transcription error in
any of them would be entirely invisible to Lean, and the file would still compile. They are
tabulated below for human auditability and to make the object a chirotope on paper, not because
anything here checks them. What is actually formalized is therefore: *no real configuration
realizes (either orientation of) a chirotope whose values on those eighteen sorted triples are the
ones tabulated.* That is strictly stronger than the headline statement as a mathematical
implication, and strictly weaker as a claim about Ringel's specific matroid, since it is blind to
the other 66 cells.

**(2) The table is Ringel's only by *transcription*, and the hash pins the wrong end of the
chain.** The canonical payload SHA-256 of the 84-entry table is
`9a1a5d579eb8517ad65d811ac6c36d07dccbc149f1594a3b18964e123d7025b4`. That digest certifies that the
table below is byte-identical to what `es7_ringel_chirotope.py` emitted; it certifies **nothing**
about whether the Python reconstruction agrees with what Ringel published. The provenance chain is

    Carroll's two rendered affine projections  →  es7_ringel_chirotope.py  →  this table
                        (human transcription)        (SHA-256 pinned)

— hash-pinned at the second link only, eyeball at the first. The transcription is the sole
unverified load-bearing input, and it is *explicit and auditable*: the table below is the whole
of it, and the eighteen lookup lemmas name exactly the part of it the proof leans on.

**(3) The table is not reproved here to be a valid chirotope.** The uniform rank-3 chirotope axiom
check — 126 rank-3 packets and 126 ordered signotope 4-sets — is carried by
`es7_ringel_chirotope.py` and is not needed for the nonrealizability argument: a table that failed
to be a chirotope would only make the nonrealizability statement vacuously stronger.
-/

open Matrix

variable {R : Type*} [CommRing R]

/-- A point of the affine cone over the projective plane. -/
abbrev Pt (R : Type*) := R × R × R

/-- `br a b c` = det of the 3×3 matrix with columns `a b c`, by the Laplace formula. -/
def br (a b c : Pt R) : R :=
  a.1 * (b.2.1 * c.2.2 - b.2.2 * c.2.1)
  - b.1 * (a.2.1 * c.2.2 - a.2.2 * c.2.1)
  + c.1 * (a.2.1 * b.2.2 - a.2.2 * b.2.1)

/-- The explicit formula really is mathlib's determinant. -/
theorem br_eq_det (a b c : Pt R) :
    br a b c = Matrix.det !![a.1, b.1, c.1; a.2.1, b.2.1, c.2.1; a.2.2, b.2.2, c.2.2] := by
  simp [br, Matrix.det_fin_three]
  ring


variable {R : Type*} [CommRing R]

/-- Grassmann-Plücker syzygy on {1,3,4,6,7,8} (4 terms). -/
theorem gp1 (p1 p3 p4 p6 p7 p8 : Pt R) :
    br p1 p3 p4 * br p6 p7 p8 - br p1 p3 p6 * br p4 p7 p8 + br p1 p3 p7 * br p4 p6 p8 - br p1 p3 p8 * br p4 p6 p7 = 0 := by
  simp only [br]; ring

/-- Grassmann-Plücker syzygy on {1,3,4,5,7,9} (4 terms). -/
theorem gp2 (p1 p3 p4 p5 p7 p9 : Pt R) :
    br p1 p3 p4 * br p5 p7 p9 - br p1 p5 p7 * br p3 p4 p9 + br p1 p5 p9 * br p3 p4 p7 - br p1 p7 p9 * br p3 p4 p5 = 0 := by
  simp only [br]; ring

/-- Grassmann-Plücker syzygy on {1,3,4,8,9} (3 terms). -/
theorem gp3 (p1 p3 p4 p8 p9 : Pt R) :
    -br p1 p3 p4 * br p4 p8 p9 + br p1 p4 p8 * br p3 p4 p9 - br p1 p4 p9 * br p3 p4 p8 = 0 := by
  simp only [br]; ring

/-- Grassmann-Plücker syzygy on {1,3,4,6,7,8} (4 terms). -/
theorem gp4 (p1 p3 p4 p6 p7 p8 : Pt R) :
    -br p1 p3 p6 * br p4 p7 p8 - br p1 p3 p8 * br p4 p6 p7 + br p1 p4 p7 * br p3 p6 p8 - br p1 p6 p8 * br p3 p4 p7 = 0 := by
  simp only [br]; ring

/-- Grassmann-Plücker syzygy on {1,3,4,6,7,8} (4 terms). -/
theorem gp5 (p1 p3 p4 p6 p7 p8 : Pt R) :
    -br p1 p3 p7 * br p4 p6 p8 + br p1 p3 p8 * br p4 p6 p7 + br p1 p4 p6 * br p3 p7 p8 - br p1 p7 p8 * br p3 p4 p6 = 0 := by
  simp only [br]; ring

/-- Grassmann-Plücker syzygy on {1,3,4,6,7,8} (4 terms). -/
theorem gp6 (p1 p3 p4 p6 p7 p8 : Pt R) :
    -br p1 p3 p8 * br p4 p6 p7 + br p1 p4 p8 * br p3 p6 p7 - br p1 p6 p8 * br p3 p4 p7 + br p1 p7 p8 * br p3 p4 p6 = 0 := by
  simp only [br]; ring

/-- Grassmann-Plücker syzygy on {1,2,4,6,7,9} (4 terms). -/
theorem gp7 (p1 p2 p4 p6 p7 p9 : Pt R) :
    -br p1 p2 p9 * br p4 p6 p7 + br p1 p4 p9 * br p2 p6 p7 - br p1 p6 p9 * br p2 p4 p7 + br p1 p7 p9 * br p2 p4 p6 = 0 := by
  simp only [br]; ring

/-- Grassmann-Plücker syzygy on {1,3,4,6,7,8} (4 terms). -/
theorem gp8 (p1 p3 p4 p6 p7 p8 : Pt R) :
    br p1 p3 p8 * br p4 p6 p7 + br p1 p4 p6 * br p3 p7 p8 - br p1 p4 p7 * br p3 p6 p8 + br p1 p6 p7 * br p3 p4 p8 = 0 := by
  simp only [br]; ring

/-- Grassmann-Plücker syzygy on {2,3,4,6,7} (3 terms). -/
theorem gp9 (p2 p3 p4 p6 p7 : Pt R) :
    -br p2 p3 p7 * br p4 p6 p7 + br p2 p4 p7 * br p3 p6 p7 - br p2 p6 p7 * br p3 p4 p7 = 0 := by
  simp only [br]; ring

/-- Grassmann-Plücker syzygy on {1,5,6,7,9} (3 terms). -/
theorem gp10 (p1 p5 p6 p7 p9 : Pt R) :
    -br p1 p5 p6 * br p1 p7 p9 + br p1 p5 p7 * br p1 p6 p9 - br p1 p5 p9 * br p1 p6 p7 = 0 := by
  simp only [br]; ring

/-- Antisymmetry of the bracket in the last two slots. -/
theorem br_swap23 (a b c : Pt R) : br a b c = - br a c b := by simp only [br]; ring

/-- Antisymmetry of the bracket in the first two slots. -/
theorem br_swap12 (a b c : Pt R) : br a b c = - br b a c := by simp only [br]; ring

/-- **Parity of the antipodal map.** `br` is trilinear and `3` is odd, so negating *all three*
arguments multiplies the bracket by `(-1)^3 = -1`. This is what makes the reversed orientation
`−χ` a mirror of `χ` rather than a separate problem: see `ringel_chirotope_rev_not_realizable`. -/
theorem br_neg (a b c : Pt R) : br (-a) (-b) (-c) = - br a b c := by
  simp only [br, Prod.fst_neg, Prod.snd_neg]; ring

set_option maxHeartbeats 1000000 in
/-- Carroll eq. (96), sorted-bracket normal form. -/
theorem carroll96_sorted (p1 p2 p3 p4 p5 p6 p7 p8 p9 : Pt R) :
    -br p1 p2 p9 * br p1 p4 p8 * br p1 p5 p7 * br p3 p4 p7 * br p4 p6 p7 + br p1 p3 p4 * br p1 p4 p8 * br p1 p6 p7 * br p2 p4 p7 * br p5 p7 p9 - br p1 p3 p4 * br p1 p4 p9 * br p1 p5 p7 * br p2 p4 p7 * br p6 p7 p8 - br p1 p3 p4 * br p1 p5 p7 * br p1 p6 p7 * br p2 p4 p7 * br p4 p8 p9 + br p1 p3 p8 * br p1 p4 p9 * br p1 p5 p7 * br p2 p4 p7 * br p4 p6 p7 - br p1 p4 p8 * br p1 p4 p9 * br p1 p5 p7 * br p2 p3 p7 * br p4 p6 p7 - br p1 p4 p8 * br p1 p5 p6 * br p1 p7 p9 * br p2 p4 p7 * br p3 p4 p7 + br p1 p4 p8 * br p1 p5 p7 * br p1 p7 p9 * br p2 p4 p6 * br p3 p4 p7 - br p1 p4 p8 * br p1 p6 p7 * br p1 p7 p9 * br p2 p4 p7 * br p3 p4 p5 = 0 := by
  linear_combination (-1 : R) * (br p1 p4 p9 * br p1 p5 p7 * br p2 p4 p7) * gp1 p1 p3 p4 p6 p7 p8
      + (1 : R) * (br p1 p4 p8 * br p1 p6 p7 * br p2 p4 p7) * gp2 p1 p3 p4 p5 p7 p9
      + (1 : R) * (br p1 p5 p7 * br p1 p6 p7 * br p2 p4 p7) * gp3 p1 p3 p4 p8 p9
      + (1 : R) * (br p1 p4 p9 * br p1 p5 p7 * br p2 p4 p7) * gp4 p1 p3 p4 p6 p7 p8
      + (-1 : R) * (br p1 p4 p9 * br p1 p5 p7 * br p2 p4 p7) * gp5 p1 p3 p4 p6 p7 p8
      + (-1 : R) * (br p1 p4 p9 * br p1 p5 p7 * br p2 p4 p7) * gp6 p1 p3 p4 p6 p7 p8
      + (1 : R) * (br p1 p4 p8 * br p1 p5 p7 * br p3 p4 p7) * gp7 p1 p2 p4 p6 p7 p9
      + (1 : R) * (br p1 p4 p9 * br p1 p5 p7 * br p2 p4 p7) * gp8 p1 p3 p4 p6 p7 p8
      + (1 : R) * (br p1 p4 p8 * br p1 p4 p9 * br p1 p5 p7) * gp9 p2 p3 p4 p6 p7
      + (1 : R) * (br p1 p4 p8 * br p2 p4 p7 * br p3 p4 p7) * gp10 p1 p5 p6 p7 p9

set_option maxHeartbeats 1000000 in
/-- **Carroll eq. (96)**, verbatim ordering: the nine-term biquadratic final polynomial for
Ringel's configuration vanishes identically on every 3×9 matrix over any commutative ring. -/
theorem carroll96 (p1 p2 p3 p4 p5 p6 p7 p8 p9 : Pt R) :
    br p2 p4 p6 * br p1 p8 p4 * br p1 p7 p5 * br p4 p3 p7 * br p1 p9 p7
    + br p1 p2 p9 * br p1 p8 p4 * br p1 p7 p5 * br p4 p3 p7 * br p4 p6 p7
    + br p1 p3 p8 * br p1 p9 p4 * br p2 p4 p7 * br p1 p7 p5 * br p4 p6 p7
    + br p1 p5 p6 * br p1 p8 p4 * br p2 p4 p7 * br p4 p3 p7 * br p1 p9 p7
    + br p3 p4 p5 * br p1 p8 p4 * br p2 p4 p7 * br p1 p7 p6 * br p1 p9 p7
    + br p4 p8 p9 * br p2 p4 p7 * br p1 p7 p5 * br p1 p7 p6 * br p1 p4 p3
    + br p5 p9 p7 * br p2 p4 p7 * br p1 p8 p4 * br p1 p7 p6 * br p1 p4 p3
    + br p6 p7 p8 * br p2 p4 p7 * br p1 p7 p5 * br p1 p9 p4 * br p1 p4 p3
    + br p2 p3 p7 * br p1 p9 p4 * br p1 p8 p4 * br p1 p7 p5 * br p4 p6 p7 = 0 := by
  rw [br_swap23 p1 p4 p3, br_swap23 p1 p7 p5, br_swap23 p1 p7 p6, br_swap23 p1 p8 p4, br_swap23 p1 p9 p4, br_swap23 p1 p9 p7, br_swap12 p4 p3 p7, br_swap23 p5 p9 p7]
  linear_combination carroll96_sorted p1 p2 p3 p4 p5 p6 p7 p8 p9


/-! ## CLAIM 2 — the sign audit: nine terms, all of sign `-1`. -/

/-- **CLAIM 2 (sign audit) + the contradiction, at the bracket level.**

Given the eighteen bracket signs that Ringel's chirotope forces on a realization (each hypothesis
`h1 … h18` is written so that the stated quantity is *positive*), every one of the nine
bracket-products of eq. (96) is strictly negative. Nine strictly negative reals cannot sum to `0`,
so `carroll96` is contradicted.

This is the lemma-level statement; `ringel_chirotope_not_realizable` below supplies `h1 … h18`
from the chirotope table itself. -/
theorem ringel_sign_audit (p1 p2 p3 p4 p5 p6 p7 p8 p9 : Pt ℝ)
    (h1 : (0:ℝ) < br p1 p2 p9)
    (h2 : (0:ℝ) < (-br p1 p3 p8))
    (h3 : (0:ℝ) < br p1 p4 p3)
    (h4 : (0:ℝ) < (-br p1 p5 p6))
    (h5 : (0:ℝ) < br p1 p7 p5)
    (h6 : (0:ℝ) < br p1 p7 p6)
    (h7 : (0:ℝ) < (-br p1 p8 p4))
    (h8 : (0:ℝ) < (-br p1 p9 p4))
    (h9 : (0:ℝ) < br p1 p9 p7)
    (h10 : (0:ℝ) < br p2 p3 p7)
    (h11 : (0:ℝ) < (-br p2 p4 p6))
    (h12 : (0:ℝ) < br p2 p4 p7)
    (h13 : (0:ℝ) < br p3 p4 p5)
    (h14 : (0:ℝ) < (-br p4 p3 p7))
    (h15 : (0:ℝ) < (-br p4 p6 p7))
    (h16 : (0:ℝ) < (-br p4 p8 p9))
    (h17 : (0:ℝ) < br p5 p9 p7)
    (h18 : (0:ℝ) < br p6 p7 p8) : False := by
  have key := carroll96 p1 p2 p3 p4 p5 p6 p7 p8 p9
  have hP1 : (0:ℝ) < (-br p2 p4 p6) * (-br p1 p8 p4) * br p1 p7 p5 * (-br p4 p3 p7) * br p1 p9 p7 := (mul_pos (mul_pos (mul_pos (mul_pos h11 h7) h5) h14) h9)
  have ht1 : br p2 p4 p6 * br p1 p8 p4 * br p1 p7 p5 * br p4 p3 p7 * br p1 p9 p7 < 0 := by
    have e : br p2 p4 p6 * br p1 p8 p4 * br p1 p7 p5 * br p4 p3 p7 * br p1 p9 p7 = -((-br p2 p4 p6) * (-br p1 p8 p4) * br p1 p7 p5 * (-br p4 p3 p7) * br p1 p9 p7) := by ring
    rw [e]; linarith
  have hP2 : (0:ℝ) < br p1 p2 p9 * (-br p1 p8 p4) * br p1 p7 p5 * (-br p4 p3 p7) * (-br p4 p6 p7) := (mul_pos (mul_pos (mul_pos (mul_pos h1 h7) h5) h14) h15)
  have ht2 : br p1 p2 p9 * br p1 p8 p4 * br p1 p7 p5 * br p4 p3 p7 * br p4 p6 p7 < 0 := by
    have e : br p1 p2 p9 * br p1 p8 p4 * br p1 p7 p5 * br p4 p3 p7 * br p4 p6 p7 = -(br p1 p2 p9 * (-br p1 p8 p4) * br p1 p7 p5 * (-br p4 p3 p7) * (-br p4 p6 p7)) := by ring
    rw [e]; linarith
  have hP3 : (0:ℝ) < (-br p1 p3 p8) * (-br p1 p9 p4) * br p2 p4 p7 * br p1 p7 p5 * (-br p4 p6 p7) := (mul_pos (mul_pos (mul_pos (mul_pos h2 h8) h12) h5) h15)
  have ht3 : br p1 p3 p8 * br p1 p9 p4 * br p2 p4 p7 * br p1 p7 p5 * br p4 p6 p7 < 0 := by
    have e : br p1 p3 p8 * br p1 p9 p4 * br p2 p4 p7 * br p1 p7 p5 * br p4 p6 p7 = -((-br p1 p3 p8) * (-br p1 p9 p4) * br p2 p4 p7 * br p1 p7 p5 * (-br p4 p6 p7)) := by ring
    rw [e]; linarith
  have hP4 : (0:ℝ) < (-br p1 p5 p6) * (-br p1 p8 p4) * br p2 p4 p7 * (-br p4 p3 p7) * br p1 p9 p7 := (mul_pos (mul_pos (mul_pos (mul_pos h4 h7) h12) h14) h9)
  have ht4 : br p1 p5 p6 * br p1 p8 p4 * br p2 p4 p7 * br p4 p3 p7 * br p1 p9 p7 < 0 := by
    have e : br p1 p5 p6 * br p1 p8 p4 * br p2 p4 p7 * br p4 p3 p7 * br p1 p9 p7 = -((-br p1 p5 p6) * (-br p1 p8 p4) * br p2 p4 p7 * (-br p4 p3 p7) * br p1 p9 p7) := by ring
    rw [e]; linarith
  have hP5 : (0:ℝ) < br p3 p4 p5 * (-br p1 p8 p4) * br p2 p4 p7 * br p1 p7 p6 * br p1 p9 p7 := (mul_pos (mul_pos (mul_pos (mul_pos h13 h7) h12) h6) h9)
  have ht5 : br p3 p4 p5 * br p1 p8 p4 * br p2 p4 p7 * br p1 p7 p6 * br p1 p9 p7 < 0 := by
    have e : br p3 p4 p5 * br p1 p8 p4 * br p2 p4 p7 * br p1 p7 p6 * br p1 p9 p7 = -(br p3 p4 p5 * (-br p1 p8 p4) * br p2 p4 p7 * br p1 p7 p6 * br p1 p9 p7) := by ring
    rw [e]; linarith
  have hP6 : (0:ℝ) < (-br p4 p8 p9) * br p2 p4 p7 * br p1 p7 p5 * br p1 p7 p6 * br p1 p4 p3 := (mul_pos (mul_pos (mul_pos (mul_pos h16 h12) h5) h6) h3)
  have ht6 : br p4 p8 p9 * br p2 p4 p7 * br p1 p7 p5 * br p1 p7 p6 * br p1 p4 p3 < 0 := by
    have e : br p4 p8 p9 * br p2 p4 p7 * br p1 p7 p5 * br p1 p7 p6 * br p1 p4 p3 = -((-br p4 p8 p9) * br p2 p4 p7 * br p1 p7 p5 * br p1 p7 p6 * br p1 p4 p3) := by ring
    rw [e]; linarith
  have hP7 : (0:ℝ) < br p5 p9 p7 * br p2 p4 p7 * (-br p1 p8 p4) * br p1 p7 p6 * br p1 p4 p3 := (mul_pos (mul_pos (mul_pos (mul_pos h17 h12) h7) h6) h3)
  have ht7 : br p5 p9 p7 * br p2 p4 p7 * br p1 p8 p4 * br p1 p7 p6 * br p1 p4 p3 < 0 := by
    have e : br p5 p9 p7 * br p2 p4 p7 * br p1 p8 p4 * br p1 p7 p6 * br p1 p4 p3 = -(br p5 p9 p7 * br p2 p4 p7 * (-br p1 p8 p4) * br p1 p7 p6 * br p1 p4 p3) := by ring
    rw [e]; linarith
  have hP8 : (0:ℝ) < br p6 p7 p8 * br p2 p4 p7 * br p1 p7 p5 * (-br p1 p9 p4) * br p1 p4 p3 := (mul_pos (mul_pos (mul_pos (mul_pos h18 h12) h5) h8) h3)
  have ht8 : br p6 p7 p8 * br p2 p4 p7 * br p1 p7 p5 * br p1 p9 p4 * br p1 p4 p3 < 0 := by
    have e : br p6 p7 p8 * br p2 p4 p7 * br p1 p7 p5 * br p1 p9 p4 * br p1 p4 p3 = -(br p6 p7 p8 * br p2 p4 p7 * br p1 p7 p5 * (-br p1 p9 p4) * br p1 p4 p3) := by ring
    rw [e]; linarith
  have hP9 : (0:ℝ) < br p2 p3 p7 * (-br p1 p9 p4) * (-br p1 p8 p4) * br p1 p7 p5 * (-br p4 p6 p7) := (mul_pos (mul_pos (mul_pos (mul_pos h10 h8) h7) h5) h15)
  have ht9 : br p2 p3 p7 * br p1 p9 p4 * br p1 p8 p4 * br p1 p7 p5 * br p4 p6 p7 < 0 := by
    have e : br p2 p3 p7 * br p1 p9 p4 * br p1 p8 p4 * br p1 p7 p5 * br p4 p6 p7 = -(br p2 p3 p7 * (-br p1 p9 p4) * (-br p1 p8 p4) * br p1 p7 p5 * (-br p4 p6 p7)) := by ring
    rw [e]; linarith
  linarith


/-! ## Ringel's chirotope, and what it means to realize it -/

/-- **Ringel's 9-element uniform rank-3 chirotope**, on sorted triples `i < j < k` from `0 … 8`.

All 84 entries are `±1` (the matroid is uniform); every unsorted or repeated argument returns `0`
and is never used. Machine-extracted from `es7_ringel_chirotope.ringel_signs()`, which reconstructs
the table from Carroll's two rendered affine projections. -/
def chiSorted : ℕ → ℕ → ℕ → ℤ
  | 0, 1, 2 => 1
  | 0, 1, 3 => 1
  | 0, 1, 4 => 1
  | 0, 1, 5 => 1
  | 0, 1, 6 => 1
  | 0, 1, 7 => 1
  | 0, 1, 8 => 1
  | 0, 2, 3 => 1
  | 0, 2, 4 => 1
  | 0, 2, 5 => 1
  | 0, 2, 6 => 1
  | 0, 2, 7 => 1
  | 0, 2, 8 => 1
  | 0, 3, 4 => 1
  | 0, 3, 5 => 1
  | 0, 3, 6 => 1
  | 0, 3, 7 => 1
  | 0, 3, 8 => 1
  | 0, 4, 5 => 1
  | 0, 4, 6 => 1
  | 0, 4, 7 => 1
  | 0, 4, 8 => 1
  | 0, 5, 6 => 1
  | 0, 5, 7 => 1
  | 0, 5, 8 => 1
  | 0, 6, 7 => 1
  | 0, 6, 8 => 1
  | 0, 7, 8 => 1
  | 1, 2, 3 => -1
  | 1, 2, 4 => -1
  | 1, 2, 5 => -1
  | 1, 2, 6 => -1
  | 1, 2, 7 => 1
  | 1, 2, 8 => -1
  | 1, 3, 4 => 1
  | 1, 3, 5 => 1
  | 1, 3, 6 => 1
  | 1, 3, 7 => 1
  | 1, 3, 8 => 1
  | 1, 4, 5 => 1
  | 1, 4, 6 => 1
  | 1, 4, 7 => 1
  | 1, 4, 8 => 1
  | 1, 5, 6 => -1
  | 1, 5, 7 => 1
  | 1, 5, 8 => -1
  | 1, 6, 7 => 1
  | 1, 6, 8 => 1
  | 1, 7, 8 => -1
  | 2, 3, 4 => 1
  | 2, 3, 5 => 1
  | 2, 3, 6 => 1
  | 2, 3, 7 => 1
  | 2, 3, 8 => 1
  | 2, 4, 5 => 1
  | 2, 4, 6 => 1
  | 2, 4, 7 => 1
  | 2, 4, 8 => 1
  | 2, 5, 6 => 1
  | 2, 5, 7 => 1
  | 2, 5, 8 => 1
  | 2, 6, 7 => 1
  | 2, 6, 8 => 1
  | 2, 7, 8 => -1
  | 3, 4, 5 => 1
  | 3, 4, 6 => 1
  | 3, 4, 7 => 1
  | 3, 4, 8 => 1
  | 3, 5, 6 => -1
  | 3, 5, 7 => 1
  | 3, 5, 8 => -1
  | 3, 6, 7 => 1
  | 3, 6, 8 => 1
  | 3, 7, 8 => -1
  | 4, 5, 6 => -1
  | 4, 5, 7 => -1
  | 4, 5, 8 => -1
  | 4, 6, 7 => -1
  | 4, 6, 8 => -1
  | 4, 7, 8 => -1
  | 5, 6, 7 => 1
  | 5, 6, 8 => 1
  | 5, 7, 8 => -1
  | 6, 7, 8 => -1
  | _, _, _ => 0

/-- The chirotope as a function of element indices. -/
def chiRingel (i j k : Fin 9) : ℤ := chiSorted i.val j.val k.val

/-! ### The eighteen table lookups actually used

Each is closed by `rfl` — kernel reduction of one `Nat`-literal `match`, no `decide`, no
`native_decide`, no `simp` search. -/

/-- Chirotope lookup: `χ(0,2,3) = +1`. -/
theorem chi_0_2_3 : chiRingel 0 2 3 = 1 := rfl

/-- Chirotope lookup: `χ(0,4,5) = +1`. -/
theorem chi_0_4_5 : chiRingel 0 4 5 = 1 := rfl

/-- Chirotope lookup: `χ(0,1,5) = +1`. -/
theorem chi_0_1_5 : chiRingel 0 1 5 = 1 := rfl

/-- Chirotope lookup: `χ(0,7,8) = +1`. -/
theorem chi_0_7_8 : chiRingel 0 7 8 = 1 := rfl

/-- Chirotope lookup: `χ(0,6,8) = +1`. -/
theorem chi_0_6_8 : chiRingel 0 6 8 = 1 := rfl

/-- Chirotope lookup: `χ(0,6,7) = +1`. -/
theorem chi_0_6_7 : chiRingel 0 6 7 = 1 := rfl

/-- Chirotope lookup: `χ(0,1,4) = +1`. -/
theorem chi_0_1_4 : chiRingel 0 1 4 = 1 := rfl

/-- Chirotope lookup: `χ(0,1,3) = +1`. -/
theorem chi_0_1_3 : chiRingel 0 1 3 = 1 := rfl

/-- Chirotope lookup: `χ(0,3,6) = +1`. -/
theorem chi_0_3_6 : chiRingel 0 3 6 = 1 := rfl

/-- Chirotope lookup: `χ(2,5,6) = +1`. -/
theorem chi_2_5_6 : chiRingel 2 5 6 = 1 := rfl

/-- Chirotope lookup: `χ(1,2,7) = +1`. -/
theorem chi_1_2_7 : chiRingel 1 2 7 = 1 := rfl

/-- Chirotope lookup: `χ(1,2,6) = -1`. -/
theorem chi_1_2_6 : chiRingel 1 2 6 = -1 := rfl

/-- Chirotope lookup: `χ(1,5,8) = -1`. -/
theorem chi_1_5_8 : chiRingel 1 5 8 = -1 := rfl

/-- Chirotope lookup: `χ(1,5,6) = -1`. -/
theorem chi_1_5_6 : chiRingel 1 5 6 = -1 := rfl

/-- Chirotope lookup: `χ(1,6,7) = +1`. -/
theorem chi_1_6_7 : chiRingel 1 6 7 = 1 := rfl

/-- Chirotope lookup: `χ(1,3,4) = +1`. -/
theorem chi_1_3_4 : chiRingel 1 3 4 = 1 := rfl

/-- Chirotope lookup: `χ(3,6,8) = +1`. -/
theorem chi_3_6_8 : chiRingel 3 6 8 = 1 := rfl

/-- Chirotope lookup: `χ(4,6,7) = -1`. -/
theorem chi_4_6_7 : chiRingel 4 6 7 = -1 := rfl

/-- `p : Fin 9 → Pt ℝ` **realizes** Ringel's chirotope when every sorted triple's bracket is
nonzero with the sign the chirotope prescribes. -/
def IsRingelRealization (p : Fin 9 → Pt ℝ) : Prop :=
  ∀ i j k : Fin 9, i < j → j < k → 0 < (chiRingel i j k : ℝ) * br (p i) (p j) (p k)

/-- **Ringel's 9-element uniform rank-3 chirotope is not stretchable**: no assignment of nine real
points realizes it.

The proof reads the eighteen bracket signs occurring in Carroll eq. (96) off the table `chiSorted`
under the relabelling `SOURCE_TO_RINGEL = (0,2,5,1,8,7,6,4,3)` (source label `i`, 1-based, is
Ringel element `SOURCE_TO_RINGEL[i-1]`), then invokes `ringel_sign_audit`. -/
theorem ringel_chirotope_not_realizable (p : Fin 9 → Pt ℝ) : ¬ IsRingelRealization p := by
  intro hR
  -- source bracket [129] = Ringel [023]; χ(0,2,3) = +1, reordering sign +1, so [129] is positive.
  have h1 : (0:ℝ) < br (p 0) (p 2) (p 3) := by
    have h := hR 0 2 3 (by simp) (by simp)
    rw [chi_0_2_3] at h
    norm_num at h
    linarith
  -- source bracket [138] = Ringel [054]; χ(0,4,5) = +1, reordering sign -1, so [138] is negative.
  have h2 : (0:ℝ) < (-br (p 0) (p 5) (p 4)) := by
    have h := hR 0 4 5 (by simp) (by simp)
    rw [chi_0_4_5] at h
    norm_num at h
    have e : br (p 0) (p 5) (p 4) = -br (p 0) (p 4) (p 5) := by
      simp only [br]; ring
    rw [e]; linarith
  -- source bracket [143] = Ringel [015]; χ(0,1,5) = +1, reordering sign +1, so [143] is positive.
  have h3 : (0:ℝ) < br (p 0) (p 1) (p 5) := by
    have h := hR 0 1 5 (by simp) (by simp)
    rw [chi_0_1_5] at h
    norm_num at h
    linarith
  -- source bracket [156] = Ringel [087]; χ(0,7,8) = +1, reordering sign -1, so [156] is negative.
  have h4 : (0:ℝ) < (-br (p 0) (p 8) (p 7)) := by
    have h := hR 0 7 8 (by simp) (by simp)
    rw [chi_0_7_8] at h
    norm_num at h
    have e : br (p 0) (p 8) (p 7) = -br (p 0) (p 7) (p 8) := by
      simp only [br]; ring
    rw [e]; linarith
  -- source bracket [175] = Ringel [068]; χ(0,6,8) = +1, reordering sign +1, so [175] is positive.
  have h5 : (0:ℝ) < br (p 0) (p 6) (p 8) := by
    have h := hR 0 6 8 (by simp) (by simp)
    rw [chi_0_6_8] at h
    norm_num at h
    linarith
  -- source bracket [176] = Ringel [067]; χ(0,6,7) = +1, reordering sign +1, so [176] is positive.
  have h6 : (0:ℝ) < br (p 0) (p 6) (p 7) := by
    have h := hR 0 6 7 (by simp) (by simp)
    rw [chi_0_6_7] at h
    norm_num at h
    linarith
  -- source bracket [184] = Ringel [041]; χ(0,1,4) = +1, reordering sign -1, so [184] is negative.
  have h7 : (0:ℝ) < (-br (p 0) (p 4) (p 1)) := by
    have h := hR 0 1 4 (by simp) (by simp)
    rw [chi_0_1_4] at h
    norm_num at h
    have e : br (p 0) (p 4) (p 1) = -br (p 0) (p 1) (p 4) := by
      simp only [br]; ring
    rw [e]; linarith
  -- source bracket [194] = Ringel [031]; χ(0,1,3) = +1, reordering sign -1, so [194] is negative.
  have h8 : (0:ℝ) < (-br (p 0) (p 3) (p 1)) := by
    have h := hR 0 1 3 (by simp) (by simp)
    rw [chi_0_1_3] at h
    norm_num at h
    have e : br (p 0) (p 3) (p 1) = -br (p 0) (p 1) (p 3) := by
      simp only [br]; ring
    rw [e]; linarith
  -- source bracket [197] = Ringel [036]; χ(0,3,6) = +1, reordering sign +1, so [197] is positive.
  have h9 : (0:ℝ) < br (p 0) (p 3) (p 6) := by
    have h := hR 0 3 6 (by simp) (by simp)
    rw [chi_0_3_6] at h
    norm_num at h
    linarith
  -- source bracket [237] = Ringel [256]; χ(2,5,6) = +1, reordering sign +1, so [237] is positive.
  have h10 : (0:ℝ) < br (p 2) (p 5) (p 6) := by
    have h := hR 2 5 6 (by simp) (by simp)
    rw [chi_2_5_6] at h
    norm_num at h
    linarith
  -- source bracket [246] = Ringel [217]; χ(1,2,7) = +1, reordering sign -1, so [246] is negative.
  have h11 : (0:ℝ) < (-br (p 2) (p 1) (p 7)) := by
    have h := hR 1 2 7 (by simp) (by simp)
    rw [chi_1_2_7] at h
    norm_num at h
    have e : br (p 2) (p 1) (p 7) = -br (p 1) (p 2) (p 7) := by
      simp only [br]; ring
    rw [e]; linarith
  -- source bracket [247] = Ringel [216]; χ(1,2,6) = -1, reordering sign -1, so [247] is positive.
  have h12 : (0:ℝ) < br (p 2) (p 1) (p 6) := by
    have h := hR 1 2 6 (by simp) (by simp)
    rw [chi_1_2_6] at h
    norm_num at h
    have e : br (p 2) (p 1) (p 6) = -br (p 1) (p 2) (p 6) := by
      simp only [br]; ring
    rw [e]; linarith
  -- source bracket [345] = Ringel [518]; χ(1,5,8) = -1, reordering sign -1, so [345] is positive.
  have h13 : (0:ℝ) < br (p 5) (p 1) (p 8) := by
    have h := hR 1 5 8 (by simp) (by simp)
    rw [chi_1_5_8] at h
    norm_num at h
    have e : br (p 5) (p 1) (p 8) = -br (p 1) (p 5) (p 8) := by
      simp only [br]; ring
    rw [e]; linarith
  -- source bracket [437] = Ringel [156]; χ(1,5,6) = -1, reordering sign +1, so [437] is negative.
  have h14 : (0:ℝ) < (-br (p 1) (p 5) (p 6)) := by
    have h := hR 1 5 6 (by simp) (by simp)
    rw [chi_1_5_6] at h
    norm_num at h
    linarith
  -- source bracket [467] = Ringel [176]; χ(1,6,7) = +1, reordering sign -1, so [467] is negative.
  have h15 : (0:ℝ) < (-br (p 1) (p 7) (p 6)) := by
    have h := hR 1 6 7 (by simp) (by simp)
    rw [chi_1_6_7] at h
    norm_num at h
    have e : br (p 1) (p 7) (p 6) = -br (p 1) (p 6) (p 7) := by
      simp only [br]; ring
    rw [e]; linarith
  -- source bracket [489] = Ringel [143]; χ(1,3,4) = +1, reordering sign -1, so [489] is negative.
  have h16 : (0:ℝ) < (-br (p 1) (p 4) (p 3)) := by
    have h := hR 1 3 4 (by simp) (by simp)
    rw [chi_1_3_4] at h
    norm_num at h
    have e : br (p 1) (p 4) (p 3) = -br (p 1) (p 3) (p 4) := by
      simp only [br]; ring
    rw [e]; linarith
  -- source bracket [597] = Ringel [836]; χ(3,6,8) = +1, reordering sign +1, so [597] is positive.
  have h17 : (0:ℝ) < br (p 8) (p 3) (p 6) := by
    have h := hR 3 6 8 (by simp) (by simp)
    rw [chi_3_6_8] at h
    norm_num at h
    have e : br (p 8) (p 3) (p 6) = br (p 3) (p 6) (p 8) := by
      simp only [br]; ring
    rw [e]; linarith
  -- source bracket [678] = Ringel [764]; χ(4,6,7) = -1, reordering sign -1, so [678] is positive.
  have h18 : (0:ℝ) < br (p 7) (p 6) (p 4) := by
    have h := hR 4 6 7 (by simp) (by simp)
    rw [chi_4_6_7] at h
    norm_num at h
    have e : br (p 7) (p 6) (p 4) = -br (p 4) (p 6) (p 7) := by
      simp only [br]; ring
    rw [e]; linarith
  exact ringel_sign_audit (p 0) (p 2) (p 5) (p 1) (p 8) (p 7) (p 6) (p 4) (p 3)
    h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18


/-! ## CLAIM 3 — the reversed orientation, and the honest "not stretchable" statement

An oriented matroid is the **pair** `{χ, −χ}`. A configuration whose brackets all carry the
opposite sign realizes `−χ`, and it is just as much a stretching of Ringel's arrangement as one
realizing `χ`; so `ringel_chirotope_not_realizable` by itself falls exactly **one reorientation**
short of "not stretchable". Two independent parity facts close that gap. The formalization below
uses the first; the second is recorded because it is what makes the gap *obviously* closable, and
a reader should not have to rediscover it.

* **`br` is trilinear and 3 is odd.** Negating all nine points (the antipodal map on the affine
  cone over `ℝP²`) multiplies every bracket by `(-1)^3 = -1` — this is `br_neg`. Hence `p`
  realizes `−χ` if and only if `-p` realizes `χ`, and the reversed case is *literally* the forward
  theorem applied to `fun i => -(p i)`. No duplicated sign audit, no second `linear_combination`.

* **Each term of `carroll96` is a product of FIVE brackets, and five is odd.** Argued directly at
  the sign-audit level instead: under `−χ` each of the eighteen bracket signs in
  `ringel_sign_audit` flips, so each of the nine products is multiplied by `(-1)^5 = -1`. All nine
  turn from strictly negative to strictly *positive* — still all of one nonzero sign, still unable
  to sum to `0`. The contradiction against `carroll96` is the identical one. (Had the final
  polynomial's terms been of even bracket-degree, this route would fail and only the trilinearity
  route would survive; the two are genuinely different arguments.)
-/

/-- `p : Fin 9 → Pt ℝ` realizes the **reversed orientation** `−χ` of Ringel's chirotope when every
sorted triple's bracket is nonzero with the sign *opposite* to the one the table prescribes. -/
def IsRingelRealizationRev (p : Fin 9 → Pt ℝ) : Prop :=
  ∀ i j k : Fin 9, i < j → j < k → 0 < -(chiRingel i j k : ℝ) * br (p i) (p j) (p k)

/-- **The reversed orientation `−χ` is not realizable either.**

Proof: the antipodal map. `br_neg` says negating all three points negates the bracket (trilinear,
`(-1)^3 = -1`), so a realization `p` of `−χ` yields the realization `fun i => -(p i)` of `χ`,
which `ringel_chirotope_not_realizable` forbids. -/
theorem ringel_chirotope_rev_not_realizable (p : Fin 9 → Pt ℝ) : ¬ IsRingelRealizationRev p := by
  intro hR
  refine ringel_chirotope_not_realizable (fun i => -(p i)) (fun i j k hij hjk => ?_)
  show (0:ℝ) < (chiRingel i j k : ℝ) * br (-(p i)) (-(p j)) (-(p k))
  have h := hR i j k hij hjk
  have e : (chiRingel i j k : ℝ) * br (-(p i)) (-(p j)) (-(p k))
      = -(chiRingel i j k : ℝ) * br (p i) (p j) (p k) := by
    rw [br_neg]; ring
  rw [e]
  exact h

/-- **Ringel's 9-element uniform rank-3 oriented matroid is not stretchable.**

Neither orientation of the chirotope has a real realization, so no nine points of the affine cone
over `ℝP²` stretch Ringel's arrangement. This — not `ringel_chirotope_not_realizable` alone — is
the statement the file's title claims. -/
theorem ringel_not_stretchable (p : Fin 9 → Pt ℝ) :
    ¬ IsRingelRealization p ∧ ¬ IsRingelRealizationRev p :=
  ⟨ringel_chirotope_not_realizable p, ringel_chirotope_rev_not_realizable p⟩

/-- Orientation-parameterised form of `ringel_not_stretchable`: for **either** sign `ε = ±1`, no
`p` realizes the chirotope `ε · χ`. `ε = 1` is `ringel_chirotope_not_realizable`, `ε = -1` is
`ringel_chirotope_rev_not_realizable`. -/
theorem ringel_not_realizable_of_sign (ε : ℤ) (hε : ε = 1 ∨ ε = -1) (p : Fin 9 → Pt ℝ) :
    ¬ ∀ i j k : Fin 9, i < j → j < k →
        0 < ((ε * chiRingel i j k : ℤ) : ℝ) * br (p i) (p j) (p k) := by
  intro h
  rcases hε with rfl | rfl
  · refine ringel_chirotope_not_realizable p (fun i j k hij hjk => ?_)
    have hijk := h i j k hij hjk
    rwa [one_mul] at hijk
  · refine ringel_chirotope_rev_not_realizable p (fun i j k hij hjk => ?_)
    have hijk := h i j k hij hjk
    rwa [neg_one_mul, Int.cast_neg] at hijk

/-! ## Axiom audit — the trust base of every named result in this file. -/

-- bracket infrastructure
#print axioms br_eq_det
#print axioms br_swap23
#print axioms br_swap12
#print axioms br_neg
-- the ten Grassmann-Plücker syzygies
#print axioms gp1
#print axioms gp2
#print axioms gp3
#print axioms gp4
#print axioms gp5
#print axioms gp6
#print axioms gp7
#print axioms gp8
#print axioms gp9
#print axioms gp10
-- the eighteen load-bearing chirotope lookups
#print axioms chi_0_1_3
#print axioms chi_0_1_4
#print axioms chi_0_1_5
#print axioms chi_0_2_3
#print axioms chi_0_3_6
#print axioms chi_0_4_5
#print axioms chi_0_6_7
#print axioms chi_0_6_8
#print axioms chi_0_7_8
#print axioms chi_1_2_6
#print axioms chi_1_2_7
#print axioms chi_1_3_4
#print axioms chi_1_5_6
#print axioms chi_1_5_8
#print axioms chi_1_6_7
#print axioms chi_2_5_6
#print axioms chi_3_6_8
#print axioms chi_4_6_7
-- the results
#print axioms carroll96_sorted
#print axioms carroll96
#print axioms ringel_sign_audit
#print axioms ringel_chirotope_not_realizable
#print axioms ringel_chirotope_rev_not_realizable
#print axioms ringel_not_stretchable
#print axioms ringel_not_realizable_of_sign

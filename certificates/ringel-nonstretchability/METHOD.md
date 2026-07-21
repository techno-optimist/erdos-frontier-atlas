# Formalizing Ringel nonstretchability in Lean 4: a syzygy-assembled final-polynomial certificate

*Cultural Soliton Observatory / Project Forty Two.*
Companion to `lean/RingelNotStretchable.lean`, `lean/RevNonVacuity.lean`, and `fidelity/`.

---

## Claim typing (read first)

- **The theorem is classical.** Ringel's 9-element uniform rank-3 oriented matroid is not
  stretchable; the final polynomial that witnesses this is Björner–Las Vergnas–Sturmfels–White–Ziegler
  (BLVSWZ), reproduced as equation (96) in Carroll, arXiv:0704.3424. We claim **no new mathematics**
  about the matroid.
- **The contribution is the formalization method.** What is ours, and what this paper makes precise
  and defensible, is *how* a degree-15 bracket identity in 27 variables is turned into a `sorry`-free
  Lean 4 + mathlib proof that runs in seconds — after brute `ring` on the raw identity fails outright,
  and after establishing that mathlib carries none of the specialized machinery one might hope to
  reuse. The method is a template (instantiated once here, for Ringel).
- **Every quantitative claim below was re-derived for this paper** by independent reimplementation and
  by grepping the actual pinned mathlib checkout, not copied from commit messages. Where a figure
  could *not* be independently reproduced, it is labelled as such at the point of use. One number in
  the prior informal notes was found to be wrong and is corrected here (§4).

---

## Abstract

We report a machine-checked proof, in Lean 4 against mathlib, that Ringel's 9-element uniform rank-3
oriented matroid admits no real point realization in either orientation — i.e. it is not stretchable.
The obstruction is the standard BLVSWZ final polynomial (Carroll eq. 96): a nine-term sum, each term
a product of five 3×3 brackets, that is identically zero as a polynomial in the 27 coordinate
variables, yet whose nine terms Ringel's chirotope forces to a common nonzero sign — a contradiction.

The engineering problem is that the identity, written out, is a degree-15 polynomial over 27 variables
whose naive expansion is ~70k signed monomial products spanning 19,656 distinct monomials, all of
which must cancel. Brute `ring` on it does not merely time out; it overruns mathlib's `ring`
normal-form interpreter (a runtime observation reproduced by the authors, not by this paper — see §2).
mathlib also provides no Plücker/Grassmann-syzygy machinery to lean on: a grep of the pinned checkout
(7,516 `.lean` files) returns **zero** hits for "Plücker", "syzygy", "chirotope", "oriented matroid",
or "bracket ring", and its single "Grassmann" file defines the Grassmannian as a moduli functor with
no Plücker relations.

The method that works decomposes the identity into Grassmann–Plücker relations. We enumerate all 1890
quadratic GP relations on nine elements (630 three-term, 1260 four-term), search a degree-5 candidate
space for a sparse combination reproducing eq. (96), and obtain a support-10 certificate with all
coefficients ±1 and exact residual 0. The crux is that in Lean, because the bracket `br` is a plain
`def`, `ring` treats every bracket as an **opaque atom**: each of the ten syzygies is then a small
degree-6 `ring` call on ≤ 6 points, and the whole nine-term identity assembles as a single
`linear_combination`. No axiomatization of brackets, no loss of rigor — the intractable expansion is
simply never performed. We also record a structural finding, corrected here to its verified value:
of the ten relations, **seven** (not six, as earlier notes stated) are genuine four-term Plücker
relations, so within the searched candidate set no certificate using three-term relations alone exists.

Finally, because no sign table for Ringel's arrangement has ever been published (Carroll §8.1 states
outright that he chooses not to give the chirotope), the identity of our 84-entry table with Ringel's
object cannot be established by diffing against a reference. We resolve this by a *uniqueness*
argument (Richter-Gebert–Ziegler: this is the only simple nonstretchable arrangement of nine
pseudolines) plus independent verification, and describe the reusable "is our data the published
object?" pattern that results.

---

## 1. What is being formalized

An oriented matroid of rank 3 on 9 elements is a chirotope χ: a sign function on sorted triples
`i < j < k` from `{0,…,8}`. A *realization* (a "stretching") is nine points p₀,…,p₈ of the affine
cone over ℝP² such that for every sorted triple the 3×3 bracket (determinant)
`[pᵢ pⱼ pₖ]` is nonzero with sign χ(i,j,k). The oriented matroid is the pair `{χ, −χ}`, so "not
stretchable" means **neither** χ nor −χ has a realization.

The Lean file proves exactly this:

```lean
theorem ringel_not_stretchable (p : Fin 9 → Pt ℝ) :
    ¬ IsRingelRealization p ∧ ¬ IsRingelRealizationRev p
```

with `IsRingelRealization` quantifying only over **sorted** triples (the weakest hypothesis, hence the
strongest theorem), and both orientations discharged. The obstruction is Carroll eq. (96): a nine-term
biquadratic final polynomial

```
Σⱼ (± product of five brackets) ≡ 0    identically in the 27 coordinates,
```

for which Ringel's chirotope forces all nine bracket-products to a common nonzero sign. Nine nonzero
reals of one sign cannot sum to zero; the identity is contradicted; no realization exists.

**Contrast with our first Lean proof.** In the Jacobian-conjecture refutation
(`../jacobian-conjecture/lean/`) the *object* was external — Alpöge's counterexample map — and our
contribution was verification: re-proving `det J ≡ −2` and a point collision against mathlib's own
`pderiv` and `det`. Here the object is **ours**: the executable, sign-audited certificate is a Project
Forty Two artifact, and the theorem it formalizes is Ringel's classical one. The JC file leaned on
nine small `ring` calls (one per partial derivative) with no obstruction; the Ringel file is the
case where the natural `ring` attack collapses and the method below is what rescues it.

---

## 2. The negative result: why brute `ring` is not viable

The failure of the obvious approach is the reason the method exists, so it is stated with numbers.

**The raw object.** Each point carries 3 coordinates, so 9 points = **27 variables**. Each bracket
`[abc]` is a 3×3 determinant, degree 3. Each term of eq. (96) is a product of **five** brackets, so
degree **15**; there are **nine** terms. Verified by expanding the certificate exactly over integer
coefficient dictionaries (`es7_ringel_final_polynomial.py`, and an independent reimplementation for
this paper):

| quantity | value | how verified |
|---|---:|---|
| variables | 27 | 9 points × 3 coords |
| total degree per term | 15 | 5 brackets × degree 3 |
| terms | 9 | eq. (96) |
| monomials per expanded term | 6,768 | exact expansion, all 9 terms equal |
| naive unreduced signed products | 69,984 | 6⁵ × 9 (each determinant = 6 signed products) |
| distinct degree-15 monomials across the nine terms | 19,656 | union of the expansions |
| residual after cancellation | **0** | the identity holds exactly |

So a reflective normalizer must build a canonical form over ~70k signed monomial products in 27
variables at degree 15, spanning nearly 20k distinct monomials, every one of which must cancel to
prove `= 0`. This is worst-case for `Mathlib.Tactic.Ring`, whose normal form is a fully reflected
polynomial: the difficulty is the size of the intermediate normal form, not the search for a proof.

**The runtime observation (authors' environment; not reproduced in this paper).** The direct
27-variable `ring` on eq. (96) crashed at ~2 min on the default stack, and made no measurable progress
in 46 min at 3.5 GB with a 2 GB stack. Because this is an out-of-memory / stack-overflow on the
`ring` interpreter rather than a heartbeat timeout, raising `maxHeartbeats` does not help. We label
this a runtime observation: this paper independently confirms the *structural cause* (the size figures
above, and that `ring` has no way to abstract brackets — §3) but did not re-run the 46-minute
experiment.

**No machinery to reuse.** One might hope mathlib already knows about Plücker relations, the bracket
ring, or chirotopes. It does not. Grepping the pinned mathlib checkout used for the build
(`formal-conjectures/.lake/packages/mathlib`, **7,516** `.lean` files) for this paper:

| search | hits |
|---|---:|
| `plucker` / `plücker` | **0** |
| `syzygy` | **0** |
| `chirotope` | **0** |
| `oriented matroid` | **0** |
| `bracket ring` | **0** |
| `grassmann` | 1 file |

The single "Grassmann" hit is `Mathlib/RingTheory/Grassmannian.lean` (Kenny Lau, 2025), which defines
`Module.Grassmannian` as the moduli of locally-free rank-k quotients — algebraic geometry, with **no**
Plücker embedding, Plücker relations, or syzygies. So there is nothing to import; the certificate must
be built from `ring` on the bracket *definition* alone.

---

## 3. The method that works

### 3.1 Enumerate the syzygies

The Grassmann–Plücker relations are the quadratic syzygies among brackets — the defining relations of
the Grassmannian in its Plücker embedding — and they hold for *every* matrix, over any commutative
ring. On 9 elements at rank 3 there are two families, both re-enumerated exactly for this paper:

- **Three-term relations** (a common first point `a`, four others `b,c,d,e`):
  `[abc][ade] − [abd][ace] + [abe][acd] = 0`. Count: 9 · C(8,4) = **630**.
- **Four-term relations** (a common pair `{a,b}`, four others; the general rank-3 Plücker relation):
  `Σᵢ (−1)ⁱ [ab cᵢ][others] = 0`. Count: C(9,2) · C(7,4) = **1260**.

Total **1890** distinct relations (630 + 1260, verified pairwise-distinct after sign normalization).
The 630 three-term relations are linearly independent (their span has dimension 630).

### 3.2 Search a degree-5 candidate space

Eq. (96) is a degree-5 element of the bracket ring (five brackets per term). We want to write it as a
ℤ-combination `Σ mₜ · rₜ`, where each `rₜ` is a GP relation (degree 2) multiplied by a degree-3
bracket monomial `mₜ`. The candidate columns are generated by BFS: start from the nine bracket
monomials of eq. (96); for each degree-5 monomial reached, and each pair of its five brackets that
matches a bracket-pair occurring in some relation, multiply that relation by the remaining degree-3
monomial to obtain a new degree-5 candidate; close under two levels.

The reference pipeline reported a candidate space of **8,367 columns over 1,598 monomials**; a
support-10 solution was located over GF(2⁶¹−1) and then re-solved exactly over ℚ. Those two figures
(8,367 / 1,598) are *bookkeeping-dependent* and were **not** independently reproduced for this paper —
an independent BFS with different deduplication produced a smaller candidate set (2,469 columns over
1,003 monomials). Both bookkeepings reproduced the qualitative verdicts of §3.3 and §4 and recovered
the *identical* shipped certificate, so the certificate does not depend on the exact search size; the
search size is not a load-bearing claim.

### 3.3 The shipped certificate

The result, independently re-verified here by expanding both sides over canonicalized bracket
monomials, is a combination of **ten** distinct GP relations reproducing eq. (96) exactly:

- support **10**;
- **every** scalar coefficient is **±1** (no denominators, no growth);
- exact residual **0**;
- the certificate spans **18** distinct brackets and uses **6** distinct degree-3 multiplier monomials.

These ten relations are the lemmas `gp1 … gp10` in the Lean file, and the assembly is
`carroll96_sorted`'s single `linear_combination`.

### 3.4 The crux: brackets as opaque atoms

Here is why the decomposition converts an intractable problem into a tractable one, and why it does so
without any axiomatization or loss of rigor.

In the Lean file `br` is a **plain `def`**:

```lean
def br (a b c : Pt R) : R := a.1 * (b.2.1*c.2.2 - b.2.2*c.2.1) - … + …
```

`ring` does not unfold definitions. So when it normalizes an expression built from `br`-applications,
it treats each distinct application `br pᵢ pⱼ pₖ` as an **opaque atom** — a single indeterminate — not
as its degree-3 coordinate expansion. Consequently:

- Each syzygy `gpₜ` is proved by `simp only [br]; ring`: unfold the ≤ 6 brackets it mentions into
  coordinates, then a `ring` call on a degree-6 polynomial in ≤ 18 variables. Small and instantaneous.
- The assembly `carroll96_sorted` is `linear_combination (Σ mₜ · gpₜ)`. `linear_combination` reduces
  the goal to a `ring` identity **in the atoms** — i.e. `ring` sees a linear/quadratic identity among
  bracket *symbols*, never their 27-variable expansion. The 70k-monomial blowup of §2 simply never
  occurs.

The final theorem `carroll96` then `rw`s eight bracket antisymmetries (`br_swap12`, `br_swap23`) to
convert Carroll's verbatim term ordering into the sorted normal form and closes by
`linear_combination carroll96_sorted`.

The key point for reproducibility: **this is not an axiom.** The brackets are the genuine mathlib
determinant (`br_eq_det` proves `br a b c = Matrix.det !![…]`), fully unfolded inside each small `gpₜ`.
Opacity is used only as a *proof-search boundary* in the assembly step, where every atom is
independently justified. The identity that `linear_combination` finally checks is true in the free
commutative ring on the bracket atoms, and each atom's realization as a determinant is proved
separately — so soundness is exactly that of unfolding everything at once, at a fraction of the cost.

The reversed orientation costs nothing extra: `br_neg` proves `br (−a) (−b) (−c) = −br a b c`
(trilinearity, `(−1)³ = −1`), so a realization of −χ is a realization of χ under the antipodal map,
and `ringel_chirotope_rev_not_realizable` is the forward theorem applied to `fun i => −(p i)`.

### 3.5 Trust base

39 `#print axioms` statements audit **every** named result (bracket infrastructure ×4, syzygies ×10,
the 18 chirotope lookups, and the 7 headline results). Each depends on at most
`[propext, Classical.choice, Quot.sound]`; the 18 table lookups are closed by `rfl` and report
`[propext]` alone. No `sorry`, no `decide`, no `native_decide`, no new axioms.

---

## 4. The structural finding — and its exact scope

**Verified statement.** Of the ten GP relations in the shipped certificate, **seven** are genuine
four-term Plücker relations and **three** are three-term relations. "Genuine four-term" is given a
precise, machine-checked meaning: a relation that does **not** lie in the linear span of the 630
three-term relations. Testing each `gpₜ` against that span (echelon reduction over ℚ; the 3-term span
has dimension 630):

| lemma | written terms | in 3-term span? | verdict |
|---|:--:|:--:|---|
| gp1, gp2, gp4, gp5, gp6, gp7, gp8 | 4 | no | **genuine four-term** (7 of them) |
| gp3, gp9, gp10 | 3 | yes | three-term |

All ten relations are pairwise distinct, so this is seven *distinct* four-term relations, not a
smaller set with repetition.

> **Correction.** Earlier informal notes (the lean README and the commit history) state "six of the
> ten are genuine four-term relations." That count is wrong: the Lean file's own docstrings label
> `gp1,gp2,gp4,gp5,gp6,gp7,gp8` as four-term (seven lemmas), and independent verification confirms all
> seven lie outside the three-term span. The correct number is **seven**. This does not affect any
> theorem — it is a description of the shipped certificate — but the paper states the verified value.

**Exactly what this rules out — and what it does not.** There are two separable statements, and the
distinction is the most over-claimable point in this work, so it is drawn sharply:

1. **Unconditional, about the shipped object.** The shipped certificate demonstrably *uses* seven
   genuine four-term relations; three-term relations alone do not appear sufficient within it. This is
   a fact about one certificate, verified exactly.

2. **Search-bounded, a fence not a theorem.** Within the specific degree-5 candidate column set
   reached by the two-level BFS from the nine target monomials, eq. (96) lies in the full relation
   span but **not** in the sub-span generated by three-term relations alone (independently reproduced:
   over the reimplemented candidate set, the full span contains the target while the three-term-only
   span, of strictly smaller rank, does not). This is a statement about **that candidate set**. It is
   **not** a theorem that no three-term-only certificate exists anywhere in the degree-5 part of the
   Plücker ideal. A different multiplier basis, or a higher-degree lift, is outside what was searched.

The honest headline is therefore: *the certificate we ship, and the candidate space we searched,
both require genuine four-term Plücker relations; a "classical three-term syzygies only" route
dead-ends in the searched span.* We do not claim it is impossible in principle.

---

## 5. Generality: a template extracted from one instance

> **Scope of this claim.** The Lean pipeline below has been instantiated **exactly once** — for Ringel.
> What follows is the template *extracted from that single instance*: its universality is a design
> claim, not a demonstrated one. Everything the machine checks in this bundle concerns one certificate.
> A second worked example, run end-to-end through the same Lean pipeline, would be required to promote
> "recipe" from design intent to fact. (The Farkas/simplex run on a realizable order type in the
> fidelity check is **not** such an instance — it exercises the certificate-*search* method, not the
> Lean *formalization* recipe.)

Subject to that caveat, the method is not structurally specific to Ringel: it should formalize any
oriented-matroid nonrealizability proof that proceeds by a final polynomial. To reuse it, a user supplies:

1. **A final polynomial**: a bracket-ring identity `Σⱼ ±(product of brackets) ≡ 0`, verbatim, with its
   term and bracket ordering.
2. **A chirotope**: a sign on sorted triples (or r-subsets, for rank r) that forces every term of the
   identity to a common nonzero sign under the labelling used by the polynomial.
3. **The labelling/relabelling** between the polynomial's element names and the chirotope's, together
   with the induced reordering sign for each bracket.

The pipeline then, generically:

- expands the identity once over exact integers to confirm it is genuinely `≡ 0` (a self-check);
- enumerates the GP relations for the relevant `(n, r)`, BFS-generates a candidate space at the
  identity's bracket-degree, and solves for a sparse ±1 (or small-rational) support over a prime field,
  re-solving exactly over ℚ;
- emits a Lean file: `br` as a plain `def` = mathlib determinant; one small `simp only [br]; ring`
  lemma per relation used; one `linear_combination` assembling the identity over the atoms; a sign-audit
  lemma turning the chirotope signs into `linarith False`; the relabelling discharged bracket by
  bracket via antisymmetry lemmas.

**Where it breaks.**

- *If the identity is not a linear combination of quadratic GP relations at the searched degree.* Not
  every bracket identity is; some need higher-degree syzygies or the full ideal membership certificate,
  which the two-level BFS will not find. The failure mode is benign (the solver returns "not in span"),
  but the recipe then needs a deeper search or a different generating set.
- *Higher rank / more elements.* The GP relation count and candidate space grow fast; the GF(prime)
  solve keeps memory bounded, but the BFS closure can blow up. The opaque-atom assembly step, however,
  stays cheap regardless of the coordinate dimension — that scaling is the method's whole point.
- *If the chirotope does not force a common sign on the terms.* Then there is no contradiction to
  formalize; the object may be realizable, and the method correctly produces nothing (its positive
  control on a realizable order type finds no certificate).
- *Fidelity of the input table* is outside the method entirely — see §6.

---

## 6. The fidelity problem, and the "is our data the published object?" pattern

A formal proof is sound **about the table it is given**. The proof consumes only 18 of the 84 chirotope
entries (the ones occurring in eq. (96) under the relabelling), which makes the *theorem* stronger — it
shows even those 18 constraints are jointly unsatisfiable, so `¬(all 84)` follows a fortiori. But it
relocates all the real risk onto a single question that Lean cannot touch: **is this table Ringel's
object?**

**Why the usual answer is unavailable.** The standard way to answer "is our data the published thing?"
is to diff against the published thing. Here there is nothing to diff against: Carroll (arXiv:0704.3424,
§8.1) states that Ringel's arrangement *"is not even defined, except by a picture,"* and explicitly
declines to give the chirotope. **No sign table for Ringel's arrangement has ever been published,
anywhere.** The table was human-transcribed from two rendered affine projections; the SHA-256 pin
(`9a1a5d57…3d7025b4`, re-verified here) certifies only that our bytes match what our own reconstruction
script emitted — it says nothing about agreement with Ringel.

**The pattern that resolves it: uniqueness + independent verification, in place of a diff.** When the
published object exists only up to isomorphism and no canonical encoding is available, identity can be
pinned *structurally* instead of *byte-wise*. Establish two things about your data from scratch:

1. **It is an object of the right kind.** Verified here (`chirotope_axioms.py`, runs under the repo's
   isolated replay contract): the 84-entry table is a valid **uniform rank-3 chirotope** — 84 entries
   all ±1 (64 positive, 20 negative), the B2″ exchange axiom holds across all **531,441** (= 9⁶)
   checked instances, and all **630** three-term GP sign relations hold. Zero violations.

2. **It has the property that makes the published object unique.** Richter-Gebert & Ziegler (*Oriented
   Matroids*, Handbook of DCG): up to relabelling and reorientation this is *the only* simple
   nonstretchable arrangement of nine pseudolines (independently corroborated by Celaya–Loho–Yuen for
   Rin(3,9)). "Identity of an oriented matroid" *means* up to relabelling and reorientation — exactly
   what uniqueness delivers. So it suffices to show our table is a uniform rank-3 chirotope (leg 1) and
   is **non-realizable** by an argument independent of eq. (96). The fidelity directory supplies that
   independent leg via a fresh biquadratic final polynomial built by Gordan/Farkas duality and solved
   with an exact-`Fraction` simplex over the 1260 strict inequalities — a certificate structurally
   different from the Lean one (a Farkas combination in log|bracket| space, not a syzygy combination in
   the bracket ring), with a realizable-order-type positive control that correctly finds no certificate.

A further structural signature is matched (established by the fidelity directory's
`mutation_fingerprint.py`, an exact simplex run cited here rather than re-executed for this paper):
single-flip mutation of the triangles reproduces Richter-Gebert & Ziegler §6.3.3 — flipping the
central triangle keeps non-realizability while flipping any other yields a realizable arrangement
(each with an explicit integer realization). An object that walks and mutates like the published one
is the published one, up to the isomorphism that "identity" here means.

**What this audit found that was worse than first documented, and how it was closed.** Of the 84
entries, 35 are cross-checked by both projections (they overlap in exactly 35 triples, re-verified:
each projection lists all 56 = C(8,3) bases on its eight elements, and 56 + 56 − 35 = 77), 42 are
single-read, and **7 were never transcribed at all** — the χ(0,i,7) family, which appears in neither
projection and was *inferred* from a line-at-infinity argument. **Two of those seven are load-bearing
in the Lean proof.** This was closed by exhaustion (`inferred_entries_joint_test.py`, re-run here): of
all 2⁷ = 128 assignments to those cells, only **5** yield a valid uniform rank-3 chirotope, and of
those only ours is non-realizable — so the inference is uniquely pinned by chirotope-hood *plus*
non-realizability, not by the eye. (Notably, chirotope-hood alone does not pin it: 5 assignments
survive the axioms; non-realizability is what forces the choice.)

The reusable lesson: **"is our data the published object?" does not require the published object to be
comparable byte-for-byte.** When the source is a picture, or exists only up to isomorphism, substitute
(a) intrinsic well-formedness, (b) the uniqueness theorem that makes the property characteristic, and
(c) an independent re-derivation of that property — and close any un-transcribed cells by exhaustion
over their finitely many completions. This converts an un-diffable provenance link into a checkable one.

---

## 7. Limitations and boundary

- **Only 18 of 84 entries are load-bearing.** A transcription error in the other 66 would be invisible
  to Lean; the theorem would remain true *about the table as written* while ceasing to be about
  Ringel's matroid. The 66 are decoration for human auditability. (This makes the formal theorem
  strictly stronger as an implication and strictly weaker as a claim about Ringel's specific object;
  both directions are stated in the Lean header.)
- **The hash pins the wrong end of the chain.** SHA-256 certifies table = reconstruction-script output,
  not reconstruction = Ringel. The remaining unverified load-bearing input is the human transcription
  from the two projections; it is explicit and auditable (the whole table is written out, and the 18
  lookup lemmas name exactly the part the proof uses), but it is an eyeball step. The fidelity argument
  of §6 is what stands in for closing it; it is a strong structural argument, not a byte-level proof.
- **The three-term-impossibility is a fence, not a theorem** (§4): it is bounded by the searched
  candidate set, and does not preclude a three-term-only certificate at higher degree or under a
  different multiplier basis.
- **The `ring`-failure figures for 46 min / 3.5 GB / 2 GB stack are a runtime observation** in the
  authors' environment, not reproduced in this paper; only the structural cause (the size figures and
  the absence of bracket abstraction / reusable machinery) was independently confirmed.
- **The search-space size (8,367 / 1,598) was not independently reproduced** and is bookkeeping-
  dependent; it is not load-bearing (the shipped ±1 support-10 certificate was recovered under a
  different, smaller bookkeeping and re-verified directly).
- **The independent fidelity final polynomial** (support 17) and the full mutation-fingerprint
  simplex runs are exact but slow; their headline verdicts are cited from the `fidelity/` scripts,
  and the fast checks (`chirotope_axioms.py`, `inferred_entries_joint_test.py`) were re-run here under
  the repo's isolated (`python3 -I`) replay contract.

---

## 8. Citations

- **Ringel, G.** *Teilungen der Ebene durch Geraden oder topologische Geraden.* Math. Z. **64** (1956),
  79–102. [doi:10.1007/BF01166556](https://doi.org/10.1007/BF01166556). Ringel introduces the
  arrangement. **Ringel 1956 does not publish the chirotope**; the object there is a construction, not
  a sign table.
- **Björner, Las Vergnas, Sturmfels, White, Ziegler.** *Oriented Matroids*, 2nd ed. (Encyclopedia of
  Mathematics and its Applications 46), Cambridge Univ. Press. The final polynomial (eq. 96 below) is
  standard here; Carroll cites p. 349.
- **Carroll, G.** arXiv:0704.3424. Source of **equation (96)** used verbatim, which Carroll states he
  takes from BLVSWZ 2nd ed. p. 349. The two **affine projections** transcribed into our chirotope are
  **Carroll's renderings** in the oriented-matroid example database
  (`oriented.sourceforge.net/examples/ringel-0.html`, `…/ringel-7.html`), **not Ringel's own figures**.
  §8.1 is where Carroll declines to publish the chirotope.
- **Richter-Gebert, J., & Ziegler, G. M.** *Oriented Matroids*, in *Handbook of Discrete and
  Computational Geometry*. Uniqueness ("the only simple nonstretchable arrangement of nine
  pseudolines") and the §6.3.3 single-flip mutation signature.
- **Celaya, Loho, Yuen.** *Selecta Math.* — independent corroboration of the uniqueness for Rin(3,9).

**Attribution summary.** Theorem and final polynomial: classical (BLVSWZ / Ringel, via Carroll).
Chirotope data: transcribed from Carroll's renderings. **This paper's contribution: the formalization
method** — the negative result on brute `ring`, the syzygy-assembled opaque-atom certificate, the
seven-four-term structural finding, and the uniqueness-not-diff fidelity pattern — is ours
(Cultural Soliton Observatory / Project Forty Two).

### 5.9 The recent two-piece amplified-moment result

The search also located Durkan–Page, *Amplified moments of the Riemann zeta function*, `2606.27323`. The live arXiv history showed **v2**; both v1 and v2 were downloaded, and the v2 setup and main second-moment statement were read directly. This version check matters: v2 expands the smoothing/recombination and shift-uniformity discussion. An initial assumption that the full local text was byte-identical was rejected by comparison, not propagated into the audit.[23][28]

The coefficients here are \(P(\log(y/n)/\log y)\), with \(P\) a fixed real polynomial. For the moments with \(|A|^{2k}\) and their two-piece AFE-shaped extensions, the stated second-moment exponent is

\[
 y=T^{\theta_k},\qquad \theta_k<1/(2k).
\]

In particular, the source's theorem labeled `thm:Ik0` has error \(O(T(\log T)^{(k+1)^2-1})\). Its allowed amplifier powers and two-piece shape do not supply a square-supported Möbius polynomial of length \(T^{5/3}\); even the ordinary index length of \(A^k\) stays below \(T^{1/2}\). The source explicitly notes that its result would improve if the permissible underlying second-moment polynomial length improved.[28]

The v2 discussion recombines signed AFE pieces **before** using nonnegative majorants/minorants, which is appropriate, but correct smoothing alone does not fix the arithmetic support, coefficient family, or required absolute error scale. This is another recent arXiv lead, not a published sparse-square theorem used to certify a saving.

### 5.10 Other searches and the scope of the negative finding

Searches covered “square-supported”, “sparse mollifier”, “squares”, squarefree variance, shifted/twisted second moments, and recent amplified/reciprocal results. The saved `final-search-sweep.json` records the final search batch. A failed squarefree/Möbius query was retried with broader wording rather than treated as an empty literature result.

Li–Radziwill's source `1208.2684v1` was used to verify the AFE input behind BCR; its arithmetic-progression mean-value setting is not a replacement theorem for this continuous long square-supported moment.[21] The recent *Critical Zeros and Unconditional Mean Value Theorems for twisted PGL(2) and PGL(3) L-functions* lead concerns averages over primitive Dirichlet twists of automorphic L-functions, not the requested t-aspect zeta polynomial moment; only its abstract was screened, not its proof.[26]

**No published theorem explicitly covering this sparse-square block with the requisite absolute saving was located in this audit.** This statement is intentionally weaker than “none exists,” and much weaker than “such an estimate is impossible.”

## 6. A sparsity-only check of the underlying trilinear ingredient

BCR's proof uses a Bettin–Chandee trilinear Kloosterman-fraction estimate. The version displayed as BCR Lemma 3 is, schematically and with its actual exponents,

\[
 \sum_{a\sim A}\sum_{u\sim U}\sum_{v\sim V}
    \nu_a\alpha_u\beta_v e(a\bar u/v)
\ll_\varepsilon \|\alpha\|_2\|\beta\|_2\|\nu\|_2
 \left(1+\frac{A}{UV}\right)^{1/2}
 \left((AUV)^{7/20+\varepsilon}(U+V)^{1/4}
 +(AUV)^{3/8+\varepsilon}(A(U+V))^{1/8}\right),
 \tag{6.1}
\]

with the coprimality needed to define \(\bar u\bmod v\). The paper then separates the Poisson nonzero-frequency weights, absorbs a divisor-bounded sum over factorizations of its frequency parameter into \(\nu_a\), and estimates norms.[7] (Source lines 678–710.)

A useful **diagnostic, not a new mixed-moment theorem**, is to ask whether merely replacing dense coefficient norms by the norms of square-supported sequences makes this ingredient strong enough. In the primitive common-divisor sector, write

\[
 U\asymp V\asymp L\asymp D^2,\qquad
 A\asymp L^2/T,
\]

as in the separated nonzero-frequency block. Optimistically retain the usual geometric prefactor \(T/L^2\), use square-support norms \(\|\alpha\|_2\|\beta\|_2\ll D\), and \(\|\nu\|_2\ll A^{1/2+\varepsilon}\). Then (6.1) returns scales

\[
 T^{3/20+\varepsilon}D^{23/10}
        +D^{11/4+\varepsilon}.
 \tag{6.2}
\]

At \(D=T^{5/6}\) these are \(T^{31/15+\varepsilon}\) and \(T^{55/24+\varepsilon}\), nowhere near \(T^{1/3}\). The exact exponent algebra is in `checks.json`.

This calculation is deliberately limited. It does **not** assert that the whole BCR Poisson/Taylor reduction, including every error and coprimality decomposition, is already valid with these same bounds outside the theorem's length range. Nor does it give a lower bound on the real off-diagonal. It shows that simply inserting “only \(D\) coefficients” into this published general-purpose norm inequality is not the missing argument. A successful use would have to exploit more: the arithmetic of square moduli, Möbius weights, correlations between the frequency weights, additional averaging, a different decomposition, or a stronger applicable estimate.

Together with Section 4.1 this separates two issues:

* The positive near-collision majorant already costs at least \(T^{1/2}\).
* Even a standard oscillatory trilinear norm estimate, fed only the obvious support sparsity, is not an automatic route to the needed saving.

Neither is a no-go theorem for the signed kernel sum (3.2).

## 7. Neighborhood uniformity and the finite-block Mellin transfer

The supplied baseline's finite-block Mellin calculation concerns the actual coefficients and high-height shells. After Mellin–Plancherel and averaging the interval variable \(h\asymp H\), its kernel has a bound of the form

\[
 \mathscr K(t)\ll
 \min\left(\frac{H^2}{X},\frac{X}{1+t^2}\right).
 \tag{7.1}
\]

On the critical shell \(T\asymp X/H\), normalization by \(1/H\) gives a contribution bounded by

\[
 \frac{H}{T}\,\mathcal I(T,D),
 \tag{7.2}
\]

up to the specified cutoffs and dyadic decomposition. This is the supplied baseline deduction, not a replacement of the variance by an unweighted full-line long-polynomial mean square. At \(H=T^{4/3}\), the old \(T^{1/3}\) mixed bound gives exactly \(T^{2/3}=\sqrt H\). A genuine \(T^{1/3-\eta}\) bound would instead give \(T^{2/3-\eta}\) on this shell.

For this to become a transferred improvement, the following must be proved, not inferred from the center exponent:

1. Fixed positive \(\eta,\rho\), with a bound uniform for all sufficiently large \(T\) and
   \[
      T^{5/6-\rho}\le D\le T^{5/6+\rho}.
   \]
2. Uniformity for the shell weights used by Mellin localization, or a fixed finite collection of high-shell majorants with controlled derivatives.
3. Uniformity for the **actual arithmetic cutoffs**: full finite divisor blocks and any interval truncations or bounded-variation tapers needed to enforce the application’s support. A full-block result need not imply all truncations when its saving uses cancellation. This does not demand arbitrary adversarial complex masks; those are a different, stronger theorem.
4. Constants controlled independently of \(D\); no hidden \(O_D\) or \(O_{D^2}\) constants, no endpoint limit in \(\sigma\) with uncontrolled constants.
5. Every epsilon, logarithmic factor, partition, and interpolation loss charged against one fixed positive part of \(\eta\).
6. Retention of the other height and divisor ranges from the established sufficient system. Saving this single critical shell is not by itself an RH proof or a complete new variance theorem.

The diagonal is not the obstruction to such neighborhood uniformity. Formula (3.11) gives uniformly

\[
 \mathcal D_w\ll T^{1/6+\rho}\log T
\]

through that neighborhood, including an upper bound for bounded interval masks. For example, the condition \(\eta+\rho<1/6\), with room for epsilon losses, makes it fit below the target. The precise missing input remains uniform control of (3.2), or of its correctly transformed signed dual analogue.

**This audit establishes no new variance range.** The accepted \(H\le X^{4/7-\varepsilon}\) deduction and its qualification as the ceiling of the *tested sufficient system* remain unchanged. There is no RH deduction and no novelty claim.

## 8. Reproducibility, verification, and limitations

### What was actually checked

* Version-pinned primary theorem text, coefficient definitions, ordinary index lengths, smoothness and shift conditions, displayed error terms, and whether a reciprocity formula retains an unestimated dual moment.
* BCR's deposited journal version and PRZZ's publisher PDF against the relevant arXiv theorem text; publication metadata separately for Pratt–Robles and Khan.
* The derivation in Sections 2–4, with independent finite exact-rational checks of the gcd/Jordan identity, the square-collision parametrization, and all critical exponent substitutions. These tests verify algebra and finite cases, not an asymptotic off-diagonal estimate.
* The live version history of the newly located amplified-moment lead, then v2 rather than assuming v1 remained current.
* The original local baselines and pinned GM/GMRR sources were read-only; their hashes were captured and checked unchanged. No repository edits, staging, commits, or publication were performed.

### Files and commands

The final report is assembled from `audit-mathematics.md`, `audit-theorems.md`, and `audit-conclusion.md`, with the rendered citation ledger. Supporting files include:

* `open-target.md`: the precise next estimate, clearly labeled unproved.
* `primary/`: downloaded source archives/PDFs, extracted TeX and PDF text.
* `retrieval.jsonl`: URLs, HTTP outcomes, byte counts, and SHA-256 hashes.
* `citations.json`, `source-excerpts.md`, `evidence.json`: source ledger, inspected passages, local line locators.
* `check_algebra.py`, `checks.json`: executable exact-rational/finite checks and their real output.
* `prepare_evidence.py`, `verify_and_assemble.py`, `verification.json`: evidence preparation, assembly, and final checks.
* `final-search-sweep.json`: search-scope evidence, not a replacement for primary theorem statements.

Run from this scratch directory with Python 3:

```text
python3 check_algebra.py
python3 prepare_evidence.py
python3 verify_and_assemble.py
```

### Issues and exclusions

* Some initial web extraction routes did not return usable theorem text. Versioned arXiv source archives and author/institutional PDFs were used instead.
* The Pratt–Robles publisher-PDF URL returned subscription HTML. Publication is verified from the publisher page; the audited detailed theorem version is identified as arXiv v3, not mislabeled as a successfully retrieved final PDF.
* A newly discovered amplified-moment paper had a newer version than the first source retrieved. A text-equality test failed; direct inspection of v2 identified its expanded smoothing and shift-uniformity discussion. The length/coefficient obstruction remained after reading that version.
* This is not a proof audit of every line of every cited paper, nor an exhaustive theorem nonexistence search. Additional arXiv leads are explicitly separated from published inputs.
* No numerical quadrature, fabricated asymptotic data, or synthetic off-diagonal cancellation is used to certify the result. The symbolic/finite test pass is not advertised as proving the new analytic estimate.

## Bottom line

The localized diagonal really is \(\asymp T\log T/D\), including exact cross-collisions, so at \(D=T^{5/6}\) it is \(T^{1/6+o(1)}\). The actual task is to save a fixed power from the current \(T^{1/3+o(1)}\) upper bound for the **signed localized off-diagonal**. At the largest AFE scale, a sufficient normalized bound is \(T^{3/2-\eta}\); an unsigned near-collision treatment already costs \(T^{5/3}\) before restoring its weight. The inspected twisted-moment, special-mollifier, amplified-moment, and reciprocity results do not supply that estimate under their stated hypotheses. The remaining opportunity is real, but unproved here—not forbidden by a length mismatch.


# Guth–Maynard → GMRR: a focused proof-transfer audit

## Outcome and scope

**The direct transfer works.** Replacing GMRR's use of Huxley's large-values estimate in Section 5, equation (42), by Guth–Maynard Theorem 1.1 gives the squarefree-variance asymptotic throughout

\[
1\le H\le X^{4/7-\varepsilon},\qquad 0<\varepsilon<1/100.
\]

More precisely, the audited deduction retains the conclusion of GMRR Theorem 1,
\[
\frac1X\int_X^{2X}\left|\sum_{x<n\le x+H}\mu^2(n)-\frac{6H}{\pi^2}\right|^2dx
=C\sqrt H+O_\varepsilon(H^{1/2-\varepsilon/16}),
\]
with the same constant \(C\), and replaces its \(6/11-\varepsilon\) range by \(4/7-\varepsilon\). This is a deduction from the actual proof and cited inputs, not a claim that the deduction is new or that this is the current best published range.[1][3]

The exact rational exponent increase is \(4/7-6/11=2/77\). **The ceiling of the audited single-polynomial large-values + zeta fourth-moment implementation is still \(4/7\)**, even after checking GM's more precise Proposition 12.1. A proof reorganization exploiting mixed moments or arithmetic structure is not excluded.

No RH claim follows. GMRR Theorem 3 requires the near-optimal upper bound for *every* \(H\le X^{1-\varepsilon}\), for every allowed \(\varepsilon\), with every \(H^\delta\) loss; a fixed exponent range does not meet that quantifier.[1]

## 1. Primary versions and provenance

- GMRR: `arXiv:2006.04060v2`; full 40-page PDF and complete 131,422-byte main TeX source obtained directly. The original 50,000-character extraction limitation was avoided, not worked around by reconstructing omitted formulas. The complete local layout-text extraction has 100,219 characters; TeX is the formula authority.[1][5]
- GM: `arXiv:2405.20552v2`, revised 7 April 2026, saved as full PDF, full HTML with MathML `alttext`, and full TeX.[4][6][7]
- GM's actual PDF has 52 pages although the abstract's comments still say 48 pages.[3][6]
- The Annals landing page identifies the article in volume 203 (2026), issue 2, pp. 623–675. Its DOI download redirects to Project Euclid, which returned an Incapsula interstitial. **The publisher's final PDF was not inspected.** The proof input is the explicitly pinned arXiv manuscript.[2]
- To rule out an unnoticed change to the replacement theorem, the original `2405.20552v1` source was also retrieved. The complete TeX block for Theorem 1.1 is byte-for-byte identical between v1 and v2 (`gm-main-theorem-v1-v2-comparison.json`).[7][8]

Primary SHA-256 digests:

| File | SHA-256 |
|---|---|
| `gmrr-v2.pdf` | `f59fafc77d44d9f78e34a234d716b9e5d7b38619f7f327b2c506c1e2a841ddab` |
| `gm-v2.pdf` | `915392cf7d0ecd108479814a9a1481e23423ef63415776471cec3975ae482cae` |

`primary-manifest.json` pins all reading copies. `source-locators.json` and `source-excerpts.md` preserve exact supporting blocks and source-line ranges. No repository files, staging, commits, or repository gates were touched.

## 2. Load-bearing parameter ledger

The table records original GMRR notation. Here \(d\) is an integer variable, \(D\) its dyadic size, and \(z\) is a cutoff for \(d^2\), **not** for \(d\).[1][5]

| Proof edge | Exact data / bound | Source locator |
|---|---|---|
| Main-term piece | \(X^\varepsilon\le H\le X^{2/3-\varepsilon}\); \(H^{1+\varepsilon}\le z\le\min\{X/H^{1/2+\varepsilon},H^{1/2-\varepsilon}X^{1/2}\}\) | GMRR Prop. 1, p. 6, (11); TeX 217–222.[1][5] |
| Original tail piece | \(H\le X^{4/7-\varepsilon}\), \(z\ge H^{4/3+\varepsilon}\) | GMRR Prop. 2, p. 6, (12).[1] |
| Polynomial | \(M_D(s)=\sum_{d\sim D}\mu(d)d^{-s}\), \(z^{1/2}\le D\le(2X)^{1/2}\) | GMRR §5, pp. 20–21, (36)–(38).[1][5] |
| Mellin kernel and measure | \(X\int_{\mathbb R}\min\{(H/X)^2,|t|^{-2}\}|\zeta(1/2+it)M_D(1+2it)|^2dt\) | GMRR (39)–(40), p. 21. The spatial Plancherel measure is \(du/e^u\), then \(du/u^2\) after changing variables.[1][5] |
| Height | \(X/H\le T\le X^2\); target \(\frac HT\int_{|t|\le T}|\zeta(1/2+it)M_D(1+2it)|^2dt\ll H^{1/2-c\varepsilon}\) | GMRR (41), p. 22. The \(|t|>X^2\) part is \(O(1)\).[1][5] |
| Level sets | \(S(V)=\{t\in[-T,T]:V\le|M_D(1+2it)|<2V\}\), \(D^{-1/2}\le V\le1\) | GMRR §5, p. 22, immediately before (42).[1][5] |
| Original generic LV theorem | \(R\ll(GNV^{-2}+T\min\{GV^{-2},G^3NV^{-6}\})(\log 2NT)^6\), \(G=\sum|a_n|^2\); 1-spaced times | GMRR Lemma 1, pp. 9–10.[1] |
| Original application | \(G\ll D^{-1}\), length \(\asymp D\), and \(|S(V)|\ll(V^{-2}+T\min\{D^{-1}V^{-2},D^{-2}V^{-6}\})(\log2X)^6\) | GMRR (42), p. 22.[1][5] |
| Zeta inputs retained | \(\int_{|t|\le T}|\zeta(1/2+it)|^4dt\ll T\log^4T\); \(|\zeta(1/2+it)|\ll |t|^{1/6}\log^2|t|\) | GMRR Lemmas 3 and 5, p. 10; their uses on p. 23.[1] |
| Main-piece cutoff bottleneck | Off-diagonal bound \(H^{\varepsilon/2}(D_1D_2H/X+1+D_1D_2/X^{1/2})\), with \(D_1D_2\le z\) | GMRR §4, p. 19, between (34) and (35); TeX 724–728.[1][5] |

The original tail estimate uses the first term of (42) with the Weyl bound, giving \(HT^{-2/3+o(1)}\), and the second term with Cauchy–Schwarz and the zeta fourth moment, giving
\[
H\min(D^{-1/2}V,D^{-1}V^{-1})X^{o(1)}\le HD^{-3/4}X^{o(1)}.
\]
The maximum is at \(V=D^{-1/4}\). Thus \(z\ge H^{4/3+o(1)}\) is required; overlap with \(z\le X/H^{1/2+o(1)}\) gives \(H\le X^{6/11-o(1)}\).[1][5]

At that old endpoint, \(D=X^{4/11}\), \(T=X^{5/11}\), so \(D=T^{4/5}\). The **unnormalized** polynomial value is \(U=DV=D^{3/4}\): exactly GM's improved large-values regime, not merely an analogy to its zero-density corollary.

## 3. Exact replacement and hypothesis check

GM Theorem 1.1 says that if \(|b_n|\le1\), the times are 1-separated in \([0,\mathcal T]\), and
\[
\left|\sum_{n=N}^{2N}b_n n^{it_r}\right|\ge U,
\]
then
\[
R\le\mathcal T^{o(1)}\left(N^2U^{-2}+N^{18/5}U^{-4}+\mathcal T N^{12/5}U^{-4}\right).
\tag{GM}
\]
This is Theorem 1.1, p. 1 / HTML `#S1.Thmthrm1`, TeX lines 68–79. Its stronger \(\ell^\infty\) hypothesis is explicitly essential in the authors' remark after Lemma 1.7.[3][4][7]

Apply (GM) with
\[
N=D,\qquad b_d=D\mu(d)/d,\qquad U=DV,\qquad \mathcal T\asymp T.
\]
Then \(|b_d|\le1\) **pointwise**. No assumption about cancellation of Möbius coefficients, no Heath–Brown identity, no divisor-bounded coefficient extension, and no \(\ell^2\)-to-\(\ell^\infty\) inference are needed.

The phase \(2it\) is handled by rescaling time, not by treating the polynomial as length \(D^2\): put \(u=-2t\), translate \([-2T,2T]\) to \([0,4T]\), and absorb the translation into unimodular coefficient factors. For Lebesgue measure of a level set, partition into unit intervals in \(u\), pick an occupied point from alternate intervals, and apply the 1-separated count. This bounds the measure by a constant times the count. Endpoint truncations can be absorbed with zero coefficients.

This yields, uniformly over the ledger's \(D,T,V\),
\[
|S(V)|\ll X^{o(1)}\left(V^{-2}+D^{-2/5}V^{-4}+TD^{-8/5}V^{-4}\right).
\tag{R}
\]
GM §3 proves its full-range theorem by reduction to \(T=N^{6/5}\) and subdivision, so \(N\le T^{5/6}\) is **not** an extra hypothesis on Theorem 1.1; it describes the advantageous range. The paper explicitly disposes of \(N\ge T\) using the classical bound.[4]

## 4. Propagation through the actual GMRR proof

Write
\[
E(V)=\frac HT V^2\int_{S(V)}|\zeta(1/2+it)|^2dt.
\]
If the \(V^{-2}\) term dominates (R), use Weyl as in GMRR:
\[
E(V)\ll X^{o(1)}HT^{-2/3}.
\]
Otherwise the sum of the other two terms controls the measure; Cauchy–Schwarz and the retained fourth moment give
\[
\begin{aligned}
E(V)&\ll X^{o(1)}\frac{H}{\sqrt T}V^2
\left(D^{-2/5}V^{-4}+TD^{-8/5}V^{-4}\right)^{1/2}\\
&\ll X^{o(1)}H\left(D^{-1/5}T^{-1/2}+D^{-4/5}\right).
\end{aligned}
\]
The low levels \(|M_D|\le D^{-1/2}\) contribute \(HD^{-1}\log^2T\). Absorb all dyadic counts into \(X^{o(1)}\). Thus the replacement for GMRR's Section 5 estimate is
\[
\frac HT\int_{|t|\le T}|\zeta(1/2+it)M_D(1+2it)|^2dt
\ll X^{o(1)}H\left(D^{-1}+T^{-2/3}+D^{-1/5}T^{-1/2}+D^{-4/5}\right).
\tag{*}
\]
This is a derived inequality, not a quotation. Its only analytic inputs are (GM) and the retained GMRR lemmas.[1][3]

### Exact exponent constraints

Set \(H=X^h,z=X^a,D=X^{a/2},T_{\min}=X^{1-h}\). Suppressing only the positive epsilon margins, the conditions from (*) and the main-term piece are:

| Requirement | Linear exponent constraint |
|---|---|
| Main piece lower cutoff | \(a\ge h\) |
| Main piece upper cutoffs | \(a\le1-h/2\), \(a\le1/2+h/2\) |
| Main piece / deterministic tail | \(h\le2/3\) |
| Weyl / \(V^{-2}\) term | \(h\le4/7\) |
| GM \(TD^{-8/5}V^{-4}\) term | \(a\ge5h/4\) |
| GM \(D^{-2/5}V^{-4}\) term | \(a\ge10h-5\) |
| Low values | \(a\ge h\), already redundant |

Exact vertex enumeration in `check_exponents.py` gives
\[
\boxed{h_{\max}=4/7,\quad a=5/7,\quad D=X^{5/14},\quad T=X^{3/7},\quad D=T^{5/6}.}
\]
Deleting the Weyl constraint alone still leaves maximum \(4/7\). The old constraints independently reproduce \(6/11\).

### Positive epsilon margins, not only a formal endpoint

For the desired \(0<\varepsilon<1/100\), take
\[
X^\varepsilon\le H\le X^{4/7-\varepsilon},\qquad z=H^{5/4+\varepsilon}.
\]
The original Proposition 1's cutoffs hold. Exact polynomial slacks at the largest allowed \(h\) are
\[
1-(7/4+2\varepsilon)(4/7-\varepsilon)=17\varepsilon/28+2\varepsilon^2>0,
\]
\[
1/2-(3/4+2\varepsilon)(4/7-\varepsilon)=1/14-11\varepsilon/28+2\varepsilon^2>0.
\]
Moreover \(D\ge H^{5/8+\varepsilon/2}\) and \(T\ge H^{3/4+3\varepsilon}\), since
\[
1-(7/4+3\varepsilon)(4/7-\varepsilon)=\varepsilon/28+3\varepsilon^2>0.
\]
The three nontrivial terms of (*) are therefore at most, before \(X^{o(1)}\) losses,
\[
H^{1/2-2\varepsilon},\quad H^{1/2-8\varepsilon/5},\quad H^{1/2-2\varepsilon/5}.
\]
Since \(H\ge X^\varepsilon\), choose all subpower losses below \(X^{\varepsilon^2/10}\le H^{\varepsilon/10}\). This gives the tail piece \(\mathcal I_2\ll_\varepsilon H^{1/2-\varepsilon/4}\), comfortably stronger than the original needed \(H^{1/2-\varepsilon/8}\).

GMRR Proposition 1 supplies \(\mathcal I_1=C\sqrt H+O(H^{1/2-\varepsilon/10})\). Its same recombination \(\mathcal I_1+O(\sqrt{\mathcal I_1\mathcal I_2}+\mathcal I_2)\), and its unchanged deterministic tail treatment (valid through \(X^{2/3-\varepsilon}\)), retain at least the original \(O_\varepsilon(H^{1/2-\varepsilon/16})\) error. For \(H<X^\varepsilon\), the original GMRR Theorem 1 already supplies the result.[1]

## 5. Exact remaining bottleneck, including GM's refinement

At \(h=4/7,a=5/7\), the following **upper-bound terms**, not actual lower bounds for the variance, all equal \(H^{1/2}\) in exponent:
\[
HT^{-2/3},\quad HD^{-1/5}T^{-1/2},\quad HD^{-4/5},\quad zH/X.
\]
Thus a stronger subconvexity estimate alone would not move the ceiling of this implementation: the last three retain it. Conversely, improving only the main-piece cutoff does not remove the retained Weyl term.

The more precise GM Proposition 12.1 must not be overlooked. For \(T^{5/6}\le N\le T\), \(U=N^\sigma\), \(\sigma\ge7/10\), it gives
\[
R\lessapprox N^{2-2\sigma}+T^{1/2}N^{3-4\sigma}
+T^{(30\sigma-21)/5}N^{(46-60\sigma)/5},
\]
and also a version with an infimum over integer \(k\). The \(T^{1/2}N^{3-4\sigma}\) term remains in both versions.[4]

At the admissible critical level \(\sigma=3/4\), its displayed simplified bound is \(R\lessapprox T^{1/2}\): the other two terms are no larger for \(N\le T\). With \(N=D\), \(V=D^{-1/4}\), GMRR's fourth-moment treatment consequently yields
\[
E(V)\ll X^{o(1)}H D^{-1/2}T^{-1/4}.
\]
To make this below \(H^{1/2}\) requires \(a\ge3h-1\). But the main piece still requires \(a\le1-h/2\), so
\[
3h-1\le1-h/2\quad\Longrightarrow\quad h\le4/7.
\]
The refined-region exact constraint solver reproduces this ceiling even with the Weyl constraint removed. This does **not** prove a universal obstruction to every use of GM's ideas; it identifies the surviving moment/cutoff loss in the concrete substitution.

A precise next obligation is a power-saving bound for the **mixed level-set integral**
\[
\frac HT V^2\int_{S_D(V)}|\zeta(1/2+it)|^2dt
\]
at and beyond \(H=X^{4/7},D=X^{5/14},T=X^{3/7}\), strong enough to beat the separate large-values plus fourth-moment estimate. At \(V=D^{-1/4}\), a pure cardinality route with the same fourth moment would need a power saving over \(|S(V)|\lessapprox T^{1/2}\); alternatively it must exploit the correlation between the exceptional sets of \(M_D(1+2it)\) and \(\zeta(1/2+it)\). The large-value \(V^{-2}\)/Weyl branch must also remain controlled. Another route would change the small-divisor off-diagonal estimate, rather than pretending its \(zH/X\) restriction vanished.

GMRR's p. 9 discussion of three smooth sums with phases \(it,2it,2it\) correctly motivates a transfer, but the proof above does not rely on its heuristic equivalences: it operates directly at the actual equation (42), before factorization.[1][5]

## 6. Verification and limitations

- `python3 check_exponents.py`: all assertions passed. Exact `Fraction` arithmetic verifies normalization, old and new optima, the GM Proposition 12.1 obstruction, and epsilon slack polynomials.
- A negative control at \(h=4/7+1/1000\), using the largest permitted \(z\), violates all three new tail constraints. It tests the same constraint code, rather than a separate hard-coded rejection path.
- `gm-main-theorem-v1-v2-comparison.json`: Theorem 1.1 source blocks identical.
- Full source copies, complete formula-preserving TeX, HTML math expressions, locator excerpts, citation evidence, and arithmetic output are local. Initial PDF font-decoding warnings were addressed with an isolated `uv` run including `fonttools`; mathematical formulas were checked in TeX/MathML, not guessed from layout text.
- Publisher download blocked; pinned arXiv v2 used openly. The v1 source was a gzip-compressed single TeX file, not a tar archive; it was decoded accordingly.
- The proof transfer is an informal mathematical audit backed by exact parameter verification, not a formalized proof, priority search, or certification of a current record. No numerical search for zeta zeros or larger finite RH computation was performed.

## Sources

[1] https://arxiv.org/pdf/2006.04060v2
[2] https://annals.math.princeton.edu/2026/203-2/p06
[3] https://arxiv.org/pdf/2405.20552v2
[4] https://arxiv.org/html/2405.20552v2
[5] https://arxiv.org/src/2006.04060v2
[6] https://arxiv.org/abs/2405.20552v2
[7] https://arxiv.org/src/2405.20552v2
[8] https://arxiv.org/src/2405.20552v1

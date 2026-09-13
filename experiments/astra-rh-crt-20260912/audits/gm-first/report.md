# Independent audit: GM → GMRR squarefree variance

## Verdict

**PASSED, within the scope of this focused deductive audit.** I found no fatal flaw in the proposed mixed-integral estimate or in obtaining the stated variance formula for fixed `0 < ε < 1/100` and `X^ε ≤ H ≤ X^(4/7−ε)`, using `z=H^(5/4+ε)`. This verdict takes the pinned GM theorem, GMRR Proposition 1, and the stated standard zeta estimates as inputs; it is not a formal verification of their underlying proofs.

There is one concrete omission that should be repaired in `audit.md`: **zero-padding dyadic polynomials does not by itself account for actual terms with `2X < d² ≤ 2X+H`.** These terms are harmless, but require the explicit endpoint estimate in §3 below. The square-integrability hypothesis of GMRR's Saffari–Vaughan lemma also warrants a one-sentence localization. Neither repair changes the claimed range or error exponent.

The conclusion survives with the original centering and constant:

\[
\frac1X\int_X^{2X}\left|\sum_{x<n\le x+H}\mu^2(n)-\frac{6H}{\pi^2}\right|^2dx
=C\sqrt H+O_\varepsilon(H^{1/2-\varepsilon/16}),
\qquad
C=\frac{\zeta(3/2)}\pi\prod_p(1-3p^{-2}+2p^{-3}).
\]

GMRR's existing Theorem 1 supplies the remaining `1 ≤ H < X^ε` range with the same error exponent. Its original large-divisor Proposition 2 already had the `4/7−ε` range; the substantive change here is lowering that component's admissible **z cutoff**, not discovering that range in the original proposition.[1]

## 1. Materials actually checked

I read the complete `audit.md` and `check_exponents.py`, not only the supplied summary. I then checked the relevant original TeX directly:

- **GMRR** `gmrr-source/squfv.tex`: Theorem 1 and constant, lines 88–99; conventions, 203–204; Proposition 1 and original Proposition 2, 217–231; full variance recombination and centering, 240–258; zeta inputs, 339–372; the complete Saffari–Vaughan lemma/proof, 516–553; small-divisor proof and cutoffs, 637–753; **all of §5, 756–859**, including the portions before equation (42).[1]
- **GM** `gm-source/LargevaluesDirichlet17.tex`: Theorem 1.1, 68–79; coefficient warning and asymptotic conventions, 279–290; full reduction proving the theorem from Proposition 3.1, 424–473; Proposition 12.1 statement and relevant comparison, 2235–2252.[2]

The original-source root was `gm-candidate/`. Fresh SHA-256 calculations for both main TeX files and both v2 PDFs matched the supplied manifest. Mathematical formulas were read in TeX; I did not independently reread the publisher PDFs or refetch the sources.

## 2. GM application: coefficient, length, spacing, and measure

GM Theorem 1.1 requires **pointwise** `|b_n|≤1`, not merely an ℓ² bound, and applies to arbitrary complex coefficients and 1-separated times in `[0,𝒯]`. Its bound is

\[
R\ll_\delta \mathcal T^\delta
\left(N^2U^{-2}+N^{18/5}U^{-4}+\mathcal T N^{12/5}U^{-4}\right).
\]

The pointwise requirement is explicitly emphasized by the authors, and is genuinely satisfied here.[2]

For any fixed, possibly truncated, integer block `B⊂[D,2D)`, write

\[
M_B(1+2it)=\sum_{d\in B}\frac{\mu(d)}d d^{-2it}.
\]

Use the translated, rescaled variable `u=2T−2t∈[0,4T]` and coefficients

\[
b_d=\frac{D\mu(d)}d\,d^{-2iT}\mathbf1_B(d),
\qquad N=D,\qquad U=DV.
\]

Then `|b_d|≤1` exactly, and the polynomial at `u` is `D M_B(1+2it)`. **The length is D, not D².** The exponent `2it` changes the time scale only. Translation preserves coefficient magnitudes, and arbitrary complex coefficients are allowed.

For the continuous level set, take its image in the u variable, partition `[0,4T]` into half-open unit intervals, and select one occupied point from each interval of each parity. Within either parity the chosen points are 1-separated. The measure of the image is no greater than the number of occupied intervals, hence is bounded by the sum of two GM cardinality bounds. Finally `du=2|dt|`. No derivative bound, thickening argument, or sampling estimate for zeta is needed.

Consequently, for `S_B(V)={t∈[−T,T]: V≤|M_B(1+2it)|<2V}`,

\[
|S_B(V)|\ll X^{o(1)}
\left(V^{-2}+D^{-2/5}V^{-4}+TD^{-8/5}V^{-4}\right).
\tag{R}
\]

These substitutions and the exponents were independently checked with exact rational arithmetic. There is **no additional hypothesis `D≤T^(5/6)`**: GM's theorem is full-range, and its proof explicitly handles both sides of `T=N^(6/5)` as well as `N≥T`.[2]

## 3. Dyadic endpoints: a necessary explicit repair

To remove all integer-rounding ambiguity, set

\[
d_0=\lfloor\sqrt z\rfloor+1,\qquad D_j=2^j d_0,
\qquad B_j=[D_j,2D_j)\cap\{d\in\mathbb N:d^2\le2X\}.
\]

The nonempty blocks partition exactly `z<d²≤2X`. Their origins are integers with `D_j>√z`, their number is `O(log X)`, and the final truncation is an x-independent coefficient mask. Zero-padding therefore preserves every GM hypothesis and the Mellin identity. More generally, a partial lower or upper dyadic end block is handled by replacing its coefficients with `μ(d)·1_(z<d²≤2X)` and setting all other coefficients in the enclosing block to zero; no smoothness is required. With conventional power-of-two origins the first D can be as small as `√z/2`, changing only absolute constants; the integer-origin construction above avoids even that notational change. Cauchy–Schwarz over these blocks costs at most `O((log X)^2)` relative to a uniform block estimate.

However, the first sum in GMRR Proposition 2 is not truncated at `d²=2X`, while its centering sum is. For `x∈[X,2X]`, the omitted contribution is exactly

\[
R_\partial(x)=\sum_{2X<d^2\le x+H}\mu(d),
\]

because `H≤X` forces the corresponding n to equal 1. It is supported on `x>2X−H`, and the number of potentially present squares is `O(1+H/√X)`. Thus

\[
\frac1X\int_X^{2X}|R_\partial(x)|^2dx
\ll\frac HX\left(1+\frac H{\sqrt X}\right)^2
\ll\frac HX+\frac{H^3}{X^2}=O(1).
\tag{endpoint}
\]

This is harmless even through `H≤X^(2/3−ε)`, and a fortiori in the proposed range. Combining it with the dyadic tail in L² preserves the desired bound. **This is the precise addition needed after the sentence about zero coefficients in `audit.md`, line 83.** No enlargement to an effective length D², extra z hypothesis, or change of centering is required.

## 4. Every earlier GMRR §5 reduction remains available

The original reduction is at lines 756–815, before the conditional/unconditional branches.[1]

| Step | Audit finding after lowering z |
|---|---|
| Dyadic reduction, (36) | Valid for the fixed truncated blocks above, plus `(endpoint)`. No `z≥H^(4/3+ε)` is needed. |
| Saffari–Vaughan, (37) | Uses `H≤X` and local integrability, not the old z exponent. The stated lemma asks for global square-integrability; apply it to a compactly supported function agreeing with `A` on `[X,12X]`, which contains every argument occurring in the lemma when `H≤X`. |
| Perron / contour shift, (38) | For each finite block, `ζ(s)M_B(2s)` has only the zeta pole in the shifted strip. Its residue is exactly `y Σ_B μ(d)/d²`, canceled by the subtracted centering. Endpoint jumps are a null set for the spatial integral. |
| Plancherel, (39)–(40) | The factor `e^(−u/2)` gives measure `e^(−u)du`; with `y=e^u` this is `dy/y²`. Restricting to y of size X introduces the displayed factor X, not X². The kernel is bounded by `min((H/X)²,t^(−2))`. |
| High t tail, lines 804–807 | `|M_B(1+2it)|≤1` for these integer blocks. Weyl gives `X∫_(X²)^∞ t^(−5/3)(log t)^4 dt≪X^(−1/3)(log X)^4=O(1)`, independently of the lower cutoff. |
| Height reduction, (41) | Splitting below and above `X/H` gives `H sup_(X/H≤T≤X²) T^(−1)∫_(|t|≤T)|ζM_B|²`, up to harmless constants and the high tail. No D/T ordering is assumed. |
| Conditional branch, lines 818–829 | Not used. There is no Lindelöf input hidden in the unconditional replacement. |
| Small levels before (42), lines 831–840 | The original estimate remains acceptable at the lowered D cutoff; the simpler threshold `D^(−1/2)` used in the candidate is also sufficient. Details below. |

For a direct justification avoiding any contour-convergence concern, the finite-block identity

\[
A_B(y)=\sum_{d\in B}\mu(d)(\lfloor y/d^2\rfloor-y/d^2)
\]

has Mellin transform `ζ(s)M_B(2s)/s` on `0<Re s<1`. Its defining Mellin integral converges absolutely: `A_B(y)=O_B(y)` at zero and `A_B(y)=O_B(1)` at infinity. The Mellin transform of `A_B(e^w y)−A_B(y)` adds the factor `e^(ws)−1`; Mellin Plancherel at `Re s=1/2` gives the same `dy/y²` identity. Thus no hidden uniform contour error depends on z.

## 5. The two moment uses and the mixed-integral estimate

The only moment input needed is GMRR Lemma 3,

\[
\int_{|t|\le T}|\zeta(1/2+it)|^4dt\ll T(\log T)^4.
\]

The first use is at low values, and the second is on large-value sets. GMRR Lemma 5 supplies Weyl's pointwise bound for the other branch and for the high-t truncation.[1]

**Low values.** On `|M_B|≤D^(−1/2)`, Cauchy–Schwarz applied to the full interval gives

\[
\frac HT\int |\zeta M_B|^2dt
\ll HD^{-1}(\log T)^2.
\]

This does not assume an additional zeta second-moment theorem. Moreover, even the original, larger threshold `D^(−1/2+ε/16)` remains admissible: the original displayed bound is

\[
H^{1+\varepsilon/16}D^{-1+\varepsilon/8}
\le H^{3/8-23\varepsilon/64+\varepsilon^2/16}
\ll H^{1/2-\varepsilon/4}
\]

at `D≥H^(5/8+ε/2)`. Thus the pre-(42) small-level step does not retain a hidden `4/3` barrier.

**Large values.** Put `E(V)=(H/T)V²∫_(S_B(V))|ζ|²`. Compare the numerical terms in `(R)`, not alleged pieces of the set:

- If `V^(−2)` dominates the sum of the other terms, Weyl gives `E(V)≪X^{o(1)}HT^(−2/3)`. The bounded interval `|t|≤2` is absorbed in the same bound for `T≥2`.
- Otherwise the other two terms bound the measure. The fourth moment gives

\[
E(V)\ll X^{o(1)}\frac H{\sqrt T}V^2
\left(D^{-2/5}V^{-4}+TD^{-8/5}V^{-4}\right)^{1/2}
\ll X^{o(1)}H(D^{-1/5}T^{-1/2}+D^{-4/5}).
\]

No independence or decorrelation between zeta and M is asserted: this is ordinary continuous Cauchy–Schwarz on the actual set. Since `|M_B|≤1`, the remaining dyadic levels number `O(log D)`. Including their loss proves exactly

\[
\boxed{\frac HT\int_{|t|\le T}|\zeta(1/2+it)M_B(1+2it)|^2dt
\ll X^{o(1)}H\left(D^{-1}+T^{-2/3}+D^{-1/5}T^{-1/2}+D^{-4/5}\right).}
\]

## 6. Strict epsilon slack, not an endpoint-only check

Take `z=H^(5/4+ε)` and `X^ε≤H≤X^(4/7−ε)`. Both upper cutoffs of the stated Proposition 1 hold, because at the worst h (`H=X^h`) their slacks are

\[
1-(7/4+2\varepsilon)(4/7-\varepsilon)
=17\varepsilon/28+2\varepsilon^2>0,
\]

\[
1/2-(3/4+2\varepsilon)(4/7-\varepsilon)
=1/14-11\varepsilon/28+2\varepsilon^2>0.
\]

The lower cutoff `z≥H^(1+ε)` and the upper H condition are immediate. I also checked a discrepancy within the source: the intermediate small-divisor proposition at line 641 states the stronger cutoff `z≤X^(1−ε)/H^(1/2)`, whereas Proposition 1 and the later proof use `z≤X/H^(1/2+ε)`. The candidate satisfies **even the stronger** condition: its endpoint slack is `5ε/28+ε²>0`. This textual mismatch therefore cannot block this deduction.[1]

The height witness is strict as well:

\[
1-(7/4+3\varepsilon)(4/7-\varepsilon)
=\varepsilon/28+3\varepsilon^2>0,
\]

so `D≥H^(5/8+ε/2)` and `T≥H^(3/4+3ε)`. Before subpower losses, the four mixed-integral terms are at most

\[
H^{3/8-\varepsilon/2},\quad
H^{1/2-2\varepsilon},\quad
H^{1/2-8\varepsilon/5},\quad
H^{1/2-2\varepsilon/5}.
\]

For each fixed ε, choose the exponent in GM's `𝒯^δ` sufficiently small, and allocate **all** moment logarithms, V dyadic factors, and D dyadic Cauchy–Schwarz factors a total budget of `X^(ε²/10)≤H^(ε/10)`. For example, `δ=ε²/40` costs at most `X^(ε²/20)` for `𝒯=4T≤4X²`; all fixed logarithmic factors fit in the remaining budget. The weakest nontrivial saving is then `3ε/10`, stronger than `ε/4`. The low-value term and the O(1) endpoint/high-t terms are also smaller. Thus the **entire** large-divisor component satisfies

\[
\mathcal I_2\ll_\varepsilon H^{1/2-\varepsilon/4}.
\]

The old per-level `ε/3` target was an intermediate sufficient choice, not a hypothesis. One can also retain it by allocating a smaller per-level loss and reserving the remaining logarithmic budget for summing levels/blocks. There is no need to quote the original Proposition 2 outside its stated z range.

## 7. Recombination and centering

The unchanged Proposition 1 gives `I₁=C√H+O(H^(1/2−ε/10))`. GMRR's Cauchy–Schwarz recombination is `I₁+O(√(I₁I₂)+I₂)`.[1]

With the strengthened tail bound above, the cross term is `O(H^(1/2−ε/8))`. Both that and the Proposition 1 error fit the requested `O(H^(1/2−ε/16))` without rescaling ε.

The intermediate center is `HΣ_(d²≤2X)μ(d)/d²`. Absolute convergence gives its difference from `6H/π²` as `O(H/√X)`, so the change in variance is

\[
O(H^{5/4}X^{-1/2}+H^2/X).
\]

This fits the same error throughout the proposed range, with strict epsilon slack; it is already harmless in GMRR's wider deterministic range `H≤X^(2/3−ε)`. The endpoint sliver was included in I₂ before this recombination, not silently discarded. Thus the conclusion concerns the **specified density centering**, not an empirical mean or a different truncated center.

## 8. Boundaries, computation, and remaining unverified inputs

- **No fatal analytic issue found.** The only required additions to the written derivation are the explicit endpoint-sliver treatment and, for literal use of the lemma's hypotheses, localization of A. Choosing integer dyadic origins makes the GM normalization exact.
- GM Proposition 12.1 does not invalidate the claimed implementation-specific ceiling. At `U=D^(3/4)` its explicit `T^(1/2)D^(3−4σ)` term is `T^(1/2)`, and the displayed other terms are no larger when `D≤T`. Separate fourth-moment treatment gives `HD^(−1/2)T^(−1/4)`, requiring `a≥3h−1`; combining with `a≤1−h/2` gives `h≤4/7`. This is a limitation of these upper-bound manipulations, not an actual lower bound on the mixed integral or an obstruction to other arguments.[2]
- The copied original arithmetic checker passed in this **new scratch directory**, leaving the original files untouched. Its old/new optimization outputs were `6/11` and `4/7`.
- `independent_checks.py` independently verified the GM substitution and produced **36 strict-positivity certificates** and **15 integer dyadic partition checks**, all passing. The positivity checks use exact rational Bernstein coefficients on the whole interval `0<ε<1/100`, after factoring vanishing powers of ε. Since each tested exponent slack is affine in h, checking the two h endpoints certifies every `ε≤h≤4/7−ε`. This also checks aggregate loss, original pre-(42) low levels, endpoint errors, centering, and final error terms.
- **Not independently proved in this bounded review:** the deep proof of GM Theorem 1.1, the full foundational proof of GMRR Proposition 1, or the classical zeta estimates cited in GMRR. Their actual statements and applicable hypotheses were inspected; they are declared theorem inputs, not claims supplied by numerical checks.
- No literature survey, novelty assessment, or claim beyond the fixed-range deduction was made. The supplied source versions, not an uninspected publisher revision, are the inputs.

### Files created and scope

All audit artifacts are under `gm-first/`:

- `report.md` — this complete report.
- `independent_checks.py`, `independent-results.json` — independent exact checks and full certificates.
- `original_check_exponents.py`, `exponent-results.json` — scratch-only copy/run of the supplied checker.
- `ledger.json` — task-isolated citations and verbatim source evidence.

No source/repository files were edited, no staging or commits occurred, and no repository gates were run. Separately, the reusable audit procedure was saved as the user-local `proof-transfer-audit` skill; it is procedural memory, not a change to either mathematical source tree.

## Sources

[1] https://arxiv.org/pdf/2006.04060v2 — GMRR, On the variance of squarefree integers, v2
[2] https://arxiv.org/pdf/2405.20552v2 — Guth–Maynard, New large value estimates, v2

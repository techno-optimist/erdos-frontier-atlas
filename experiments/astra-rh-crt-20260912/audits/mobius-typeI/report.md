# Independent adversarial audit: exact Möbius split and long-factor Type I estimate

## Verdict

**PASSED for the stated partial result, with the scope qualifications below. No blocking analytic error was found in the exact identity, the long-factor estimate, or its transfer to the original sharp Type I subfamily.** This is not a pass for a power saving in the complete Möbius mixed moment, a new variance range, or RH. The residual joint estimate remains unproved.

The reviewed proposal is `mobius-factorization/report.md`, especially lines 27–266. Its explicit outcome is a saving for the long coefficient-1 factor subfamily, not for the full block.[1] The baseline asks for a uniform neighborhood improvement in the complete moment, which this partial result does not provide.[2]

The reconstruction below obtains the actual bound

\[
 \int_T^{2T}|\zeta(\tfrac12+it)B(1+i(2t+u))C(1+i(2t+u))|^2dt
 \ll_{\epsilon,\eta,K}T^\epsilon
 \left(1+\frac TD+\frac{T^{3/2}}{C_0^2}\right),
\]

including its coefficient norm, functional-equation amplitude, moving dual interval, Mellin normalization, and sharp-cutoff error. It is not an exponent-only check. Here `K` represents fixed support-width and comparability constants. In particular the initially advertised constant `≪ε` must be read with these fixed ambient constants; the full sharp-family estimate also depends on fixed `η`.

### Scope that must remain explicit

1. The application has **fixed `k=2`, `D≍T^(5/6)`, `U=(2D)^(1/2)`**, real `0<η<1/48`, and `C0≥T^(7/12+η)`. All constants in `≍` and in support widths are fixed. The introductory (TI) formula should not be detached from this context and asserted for unrestricted `D,C0`.
2. The proof also works uniformly in a small fixed neighborhood `D=T^d`, `1/2<d<1`, bounded away from both endpoints. It does not prove every height/length regime required by a variance transfer.
3. Shifts are **real imaginary-part shifts**, `|u|≤T^(1/2+η)`, with zeta still evaluated at `1/2+it`. There is no claimed uniformity for shifts in the real part, for `u` that brings `2t+u` close to zero, or for arbitrary time-dependent coefficients. For each fixed `u`, any coefficient sequence satisfying the same stated bounds is allowed; the constants are uniform in that sequence.
4. The dual factor has **real coefficient 1**. The modulus conjugation is not valid for an arbitrary complex-weighted dual sum without changing its coefficients. Arbitrary fixed complex coefficients are allowed in the other polynomial subject to the specified divisor bound.
5. Sharp interval endpoints and a bounded number of endpoint masks are covered. An arbitrary oscillatory mask on the product index is not an endpoint mask and is not covered by the cutoff argument.
6. This is an informal mathematical deduction using the cited classical AFE, polynomial mean value, and zeta fourth moment as theorem inputs. Their deep proofs have not been re-proved, and finite checks are not substitutes for them.

`blocking_issues: []` for this scope. The qualifications prevent stronger, unsupported interpretations; they are not unresolved gaps in the partial Type I conclusion.

## 1. Sources, pinning, and independence

The complete proposal and reconciled baseline were read. Their roles were kept distinct: the proposal is an object under review, not an independent acceptance verdict.[1][2] The load-bearing statements were checked against the supplied formula-preserving DLMF reading copy and GMRR v2 TeX:

- DLMF §25.9, equations 25.9.1–25.9.2, with hypotheses `x,y≥1`, `2πxy=v`, fixed `0≤σ≤1`; DLMF identifies Titchmarsh (1986), (4.12.4), p. 79.[3]
- GMRR v2 TeX lines 339–348, the zeta fourth moment (Lemma 3), and lines 392–403, the polynomial mean-value theorem at `q=1` (Lemma 7).[4]

These are enough for the Type I proof. No Watt, same-frequency twisted-moment, GM large-value, Möbius cancellation, independence, or conjectural input is needed here. The broader literature comparison and entire reconciled variance transfer were not independently re-certified in this focused audit.

All 36 supplied proposal-bundle files and the baseline were hashed at the start. Exact reading copies used here are in `readings/`; the manifest pins the reviewed source bytes. Fresh DLMF HTML and TeX requests returned HTTP 403; the alternate web extraction also failed with 403. Consequently this audit relies on the supplied archived source statements, explicitly not on a purported successful fresh retrieval. No formula was fabricated to replace a failed fetch.

## 2. Exact truncated reciprocal identity

Let

\[
 A_U(s)=\sum_{a\le U}\mu(a)a^{-s},\qquad E_U(s)=1-\zeta(s)A_U(s),
\]

with real `U≥1` and a fixed positive integer `k`. First work in `Re(s)>1`. For every integer `n≤U`, the coefficient of `ζA_U` is the complete divisor sum, equal to 1 at `n=1` and 0 otherwise. Thus every nonzero coefficient of `E_U` has integer index at least `floor(U)+1`.

The finite binomial calculation is

\[
 \sum_{j=1}^k(-1)^{j-1}\binom kj\zeta^{j-1}A_U^j
 =\frac{1-(1-\zeta A_U)^k}{\zeta}
 =\frac{1-E_U^k}{\zeta}.
\]

Hence

\[
 \frac1\zeta
 =\sum_{j=1}^k(-1)^{j-1}\binom kj\zeta^{j-1}A_U^j
  +\frac{E_U^k}{\zeta}. \tag{I}
\]

Multiplication by `1/ζ`, whose indices are positive integers, cannot decrease the first possible index of `E_U^k`. The remainder is supported on

\[
 n\ge(\lfloor U\rfloor+1)^k>U^k.
\]

Therefore coefficient extraction gives the proposal's displayed truncated formula for every integer `n≤U^k`. This support proof is valid for real, not just integer, `U`. There is no pole or convergence claim on the line `Re(s)=1`: after coefficient extraction, the restricted identity is an equality of finite Dirichlet polynomials.

For the entire half-open block `D≤n<2D`, **`U^k≥2D` is a sufficient safe condition**. It is not necessary in every individual finite example, since the exact integer support can be larger. Setting `U^k=D` does not suffice in general. A genuine negative control gives `U=2,k=2,n=9`: the truncated coefficient is `−1`, `μ(9)=0`, and the missing remainder is `+1`.

With `k=2` and `U=√(2D)`, the equality `U²=2D` is exact. For `D>2`, `U<D`, so the `2A_U` term contributes no coefficient in the block. Thus

\[
 M_D(s)=-\sum_{\substack{a,b\le\sqrt{2D}\\D\le abc<2D}}
          \mu(a)\mu(b)(abc)^{-s}. \tag{II}
\]

All variables are positive integers. The singleton variables equal to 1 are included. The free `c` variable has coefficient exactly 1, not an approximation to a Möbius or prime weight. There is no discarded analytic remainder.

The proposal explicitly keeps `k` fixed and uses `k=2` for the actual split.[1] This is essential: the binomial constants, divisor orders, numbers of dyadic boxes, and subpower constants are not uniformly controlled if `k=k(T)` grows. Nothing in this audit relaxes that requirement.

## 3. Complete marked-box decomposition

Set `C*=T^(7/12+η)`. In (II), mark exactly the tuples with `c≥C*`; assign the rest, `c<C*`, to the residual. If `C*` happens to be an integer, its equality case belongs to Type I. The two conditions are genuinely complementary.

Use disjoint half-open dyadic integer intervals for `a,b,c`, truncated at the actual upper bounds and at `C*`. A first Type I interval may be `[C*,2^m)` rather than an entire dyadic interval. Its actual lower endpoint `C0` is at least `C*` and its upper endpoint is at most `2C0`. This is why a dyadic interval crossing the threshold is not accidentally treated using a too-small lower endpoint.

In one box let the lower scales for `a,b` be `A,B`, put `R=AB`, and group `r=ab`. The fixed coefficients are

\[
 \beta_r=\sum_{\substack{ab=r\\a\in I_A,b\in I_B\\a,b\le U}}
            \mu(a)\mu(b),\qquad |\beta_r|\le\tau_2(r).
\]

They are supported in `[R,4R)`, possibly with gaps. A nonempty product-restricted box satisfies

\[
 D/8<RC_0<2D. \tag{III}
\]

The bounded width, not the exact constant 4, is what is used. Partial `a,b` intervals do not change the divisor bound. The number of all boxes is `O(log^3(2D))`; using a maximum after Cauchy–Schwarz in the final squared norm costs its square, `O(log^6(2D))`.

This covers every marked long-factor box, not merely a selected representative or the most favorable scales. There is only one free smooth variable in the chosen `k=2` identity. For a different fixed order with several long factors, one would also need a deterministic disjoint marking rule rather than count a tuple repeatedly. That is not needed for (II).

## 4. Sharp product cutoff, with its actual payment

The condition `D≤rc<2D` cannot be discarded from a complex sum. The proposal supplies a legitimate replacement-and-error argument, not a positivity argument.[1]

Choose a fixed-form smooth taper `hΔ` with `Δ=T^(−1/2)`, supported in `[1,2]`, equal to 1 on `[1+Δ,2−Δ]`, with values in `[0,1]`. It can be chosen with all derivatives supported in the two transition strips and derivative bounds `O_j(Δ^(−j))`. For either Type I or Type II separately, the coefficient at an index `n` is bounded in absolute value by `τ3(n)`. Consequently the replacement error, **including integer endpoints**, obeys

\[
 |E(t)|\le\sum_{n\text{ in boundary strips}}\frac{\tau_3(n)}n
 \ll_\rho D^\rho(\Delta+D^{-1}). \tag{IV}
\]

The `D^(−1)` term matters for a strip containing an isolated endpoint integer. By Cauchy–Schwarz and the cited fourth moment,

\[
 \int_T^{2T}|\zeta(\tfrac12+it)|^2dt\ll T\log^2(2T),
\]

so

\[
 \int_T^{2T}|\zeta E|^2dt
 \ll_\rho T\log^2(2T)D^{2\rho}(T^{-1/2}+D^{-1})^2
 \ll_\epsilon T^\epsilon(1+T/D^2). \tag{V}
\]

At `D≍T^(5/6)`, and uniformly when `d` stays above `1/2`, this is `O(T^ε)`. It would not be an `O(T^ε)` bound for arbitrary much smaller `D`; that restriction must not be lost in a generalized statement. The error can be bounded for the whole Type I subfamily before separating boxes, so it does not require a new power-sized box summation.

The taper is supported **inside the original block**. Therefore it introduces no coefficient with index beyond `U²=2D`. This is a substantive advantage over an outward smoothing that would require another boundary/support argument.

### Fourier/Mellin convention

For `gΔ(x)=hΔ(e^x)`, define

\[
 \widehat h_\Delta(u)=\int_{\mathbb R}g_\Delta(x)e^{iux}\,dx
 =\int_0^\infty h_\Delta(y)y^{iu}\,\frac{dy}{y}.
\]

Then

\[
 h_\Delta(y)=\frac1{2\pi}\int_{\mathbb R}\widehat h_\Delta(u)y^{-iu}\,du.
\]

For a box at `s=1+2it`, its smoothed polynomial is **exactly**

\[
 \frac1{2\pi}\int_{\mathbb R}\widehat h_\Delta(u)D^{iu}
 B(1+i(2t+u))C(1+i(2t+u))\,du. \tag{VI}
\]

The measure is `du/(2π)`, the product cutoff produces the unimodular factor `D^(iu)`, and both factors receive the same shift `+u`. The zeta factor receives no shift.

Since `||gΔ'||1=O(1)` and `||gΔ^(j)||1=O_j(Δ^(1−j))`, integration by parts gives

\[
 |\widehat h_\Delta(u)|\ll_j
 \min(1,|u|^{-1},\Delta^{1-j}|u|^{-j}),
\]

interpreting the first estimate near zero. Thus

\[
 ||\widehat h_\Delta||_1\ll1+\log(1/\Delta)\ll\log(2T),
\]

and, with `V=T^(1/2+η)` and fixed `j>1`,

\[
 \int_{|u|>V}|\widehat h_\Delta(u)|\,du
 \ll_j(\Delta V)^{1-j}=T^{-\eta(j-1)}. \tag{VII}
\]

Choose `j` once, sufficiently large depending on fixed `η` and a chosen absolute error power. Absolute coefficient sums, valid even at the omitted very large shifts, bound the tail of (VI). For example one may make its pointwise size `O(T^(−10))` after all divisor allowances. Its mixed squared norm is then negligible. No constants depend on a growing differentiation order.

Minkowski in the weighted `L²` norm of `ζ(t)` costs `||ĥΔ||1`; the squared-norm cost is `O(log²T)`. This argument uses **no truncated Perron formula** and no unbounded-height contour. It has paid the unsmoothing, Fourier tail, and separation costs explicitly. One could not instead use a smooth-only estimate without (IV)–(VII).

## 5. Sharp AFE, endpoints, both phases, and all normalizations

For a separated box write `C=C0`, `v=2t+u`, and

\[
 B_v=\sum_{r\asymp R}\beta_r r^{-1-iv},\qquad
 C_v=\sum_{C\le c<C_1}c^{-1-iv},\quad C_1\le2C.
\]

For `T` sufficiently large, the allowed shift satisfies `|u|≤T`, so on `t∈[T,2T]` one has `T≤v≤5T`. There is no approach to the pole at height zero. Also `C1≪D≍T^(5/6)`, hence `v/(2πC1)≥1` for all sufficiently large `T`, uniformly in the boxes. The remaining bounded `T` range is absorbed in the fixed constants.

The actual sharp AFE input is

\[
 \zeta(\sigma+iv)=\sum_{n\le x}n^{-\sigma-iv}
  +\chi(\sigma+iv)\sum_{\ell\le v/(2\pi x)}\ell^{\sigma-1+iv}
  +O(x^{-\sigma})+O(y^{\sigma-1}v^{1/2-\sigma}),
 \quad y=v/(2\pi x)\ge1. \tag{VIII}
\]

Its fixed `σ=1` specialization is exactly the one needed, including the endpoint `σ=1` in the cited range.[3]

Apply it at `x=C` and `x=C1` and subtract. If

\[
 y_1(v)=v/(2\pi C_1),\qquad y_0(v)=v/(2\pi C),
\]

then the precise resulting orientation is

\[
 C_v=\chi(1+iv)\sum_{y_1(v)<\ell\le y_0(v)}\ell^{iv}
      +O(C^{-1}+T^{-1/2}). \tag{IX}
\]

The difference of primal sums naturally has endpoints `C<n≤C1`; replacing it by `C≤c<C1` changes at most two terms, each `O(C^(−1))`. Both AFE errors are also included in (IX). No small-denominator or integer-distance factor is being suppressed.

### Exact gamma factor

DLMF gives

\[
 \chi(s)=\pi^{s-1/2}\frac{\Gamma((1-s)/2)}{\Gamma(s/2)}. \tag{X}
\]

This is a quotient, not its reciprocal.[3] At `s=1+iv`, the standard gamma reflection identities yield the exact modulus

\[
 |\chi(1+iv)|^2=\frac{2\pi}{|v|}\coth\!\left(\frac{\pi|v|}{2}\right)
 \asymp T^{-1}. \tag{XI}
\]

In particular the amplitude is `T^(−1/2)` and its square is `T^(−1)`. The dual summands at `σ=1` have coefficient **1**, not `1/ℓ` or `1/√ℓ`. The dual length is `L=T/C`, with constants containing `2π`.

For an independent normalization cross-check, use `e(z)=exp(2πiz)` and Poisson phase `−v log x−2πmx`. For positive `v`, its stationary frequencies are `m=−ℓ<0`, with stationary point `x=v/(2πℓ)`. The stationary amplitude with weight `x^(−1)` is

\[
 x^{-1}\sqrt{2\pi/(v/x^2)}=\sqrt{2\pi/v},
\]

and the phase is

\[
 v\log\ell+v-v\log(v/(2\pi))+\pi/4.
\]

This agrees with the sign, amplitude, and leading phase of (X). For negative `v` the stationary frequency and the `π/4` sign reverse by conjugation. This is a normalization cross-check, **not** a replacement for a rigorous uniform sharp-endpoint B-process theorem; the proof uses (VIII).

### Conjugation and the doubled frequency

For any real `v` and any interval `J`,

\[
 \sum_{\ell\in J}\ell^{iv}
 =\overline{\sum_{\ell\in J}\ell^{-iv}}.
\]

It follows, even if `βr` are complex, that

\[
 |B_v\sum_{\ell\in J}\ell^{iv}|
 =|B_v\sum_{\ell\in J}\ell^{-iv}|. \tag{XII}
\]

This is an equality of **moduli**, not of the complex products. It keeps `B_v` unchanged; it is justified by the reality of the dual coefficients. Applying it after including the common shift `u` causes no loss because `v` is real. For a complex-weighted dual sum the same assertion with unchanged coefficients is generally false.

We may therefore estimate the ordinary-index product

\[
 F_J(v)=B_v\sum_{\ell\in J}\ell^{-iv}
       =\sum_n f_J(n)n^{-iv},\qquad n=r\ell.
\]

Its integer-index cutoff is `O(RL)`. In its fourth moment the **square** has cutoff `O(R²L²)`. The time substitution is `v=2t+u`, **`dt=dv/2`**, over an interval of length `2T`. Shifting this interval only multiplies fixed polynomial coefficients by unit complex numbers. It does not multiply the integer cutoff by 2 or square it again. Zeta is held at the original argument and handled by its separate fourth moment, not inserted into this ordinary polynomial theorem.

For a negative-height shell, the AFE is conjugated and the same argument uses `|v|≍T`; the polynomial mean-value theorem permits either sign of frequency. The actual real-coefficient sharp Möbius families also satisfy the expected conjugation symmetry. None of this authorizes allowing `v` to pass through zero in a high-height shell.

## 6. Coefficient norm and moving intervals: a full reconstruction

By (IX), every dual interval lies in the fixed integer envelope

\[
 \mathcal L=\{\ell:L/(4\pi)<\ell\le5L/(2\pi)\},\qquad L=T/C,
\]

up to harmless inclusion of an endpoint integer. It has `O(L)` members in the present range, including when the actual interval is empty or very short. The envelope is independent of the allowed `u` and of `t`.

Define the actual coefficient norm

\[
 W_B=\sum_{r\asymp R}\frac{|\beta_r|^2}{r^2}\ll_\epsilon T^\epsilon/R.
\]

Let `d_J(m)` be the coefficient of `m^(−iv)` in `F_J(v)^2`. Expanding gives

\[
 d_J(m)=\sum_{\substack{r_1r_2\ell_1\ell_2=m\\\ell_1,\ell_2\in J}}
             \frac{\beta_{r_1}\beta_{r_2}}{r_1r_2}.
\]

Each `m` has at most `τ4(m)` such ordered representations when support restrictions are dropped. Cauchy–Schwarz **inside each coefficient**, followed by summing over `m`, therefore gives

\[
 \sum_m|d_J(m)|^2
 \le\mathcal D_4 W_B^2|J|^2,
 \qquad \mathcal D_4=\max_{m\ll R^2L^2}\tau_4(m). \tag{XIII}
\]

This is the concrete coefficient-norm bound behind the advertised `T^ε L²/R²`. It allows arbitrary signs, actual truncated Möbius convolutions, and fixed complex `βr`; it invokes no Möbius cancellation.

The ordinary polynomial mean-value input, for arbitrary fixed complex coefficients, gives

\[
 \int_T^{2T}|F_J(2t+u)|^4dt
 \ll (T+K R^2L^2)\sum_m|d_J(m)|^2. \tag{XIV}
\]

The hypotheses and translation argument match the `q=1` statement in the cited GMRR input.[4]

### Why the moving endpoint does not cost a power

The AFE interval is genuinely `J(v)=(y1(v),y0(v)]`. It is not legal to replace it with a single fixed interval solely because both endpoints have size `L`.

Pad the fixed envelope to a binary tree of `O(L)` leaves, assigning coefficient zero to padding. Every consecutive integer interval is a disjoint union of at most two canonical tree intervals at each of `O(log(2L))` levels. By Hölder,

\[
 \sup_J|F_J(v)|^4
 \ll\log^3(2L)\sum_{I\text{ canonical}}|F_I(v)|^4.
\]

At each fixed level the intervals are disjoint. For (XIII), summing the squared tuple weights over all intervals at that level counts each ordered pair `(ℓ1,ℓ2)` in at most one interval. Equivalently,

\[
 \sum_{I\text{ at one level}}\sum_m|d_I(m)|^2
 \le\mathcal D_4 W_B^2\sum_I|I|^2
 \le\mathcal D_4 W_B^2|\mathcal L|^2.
\]

Apply (XIV) separately to each fixed polynomial and then sum the `O(log(2L))` levels. This proves

\[
 \int_T^{2T}\sup_J|F_J(2t+u)|^4dt
 \ll\log^4(2L)(T+K R^2L^2)\mathcal D_4 W_B^2L^2. \tag{XV}
\]

No factor equal to the number `L` of possible cutoffs is lost. Very short and empty dual intervals, dual endpoint crossings of integers, and cutoffs arbitrarily close to integers are all included in the same supremum. The primal endpoint conventions were already paid in (IX). The AFE is the cited uniform sharp form; there is no excluded resonance set or uncontrolled near-transition term in this step.

### Reconstructing the actual three terms

Let `A_B=Σr |βr|/r≪T^ε`. The error in (IX) contributes, by the squared triangle inequality,

\[
 E_{\rm AFE}\ll T\log^2(2T)A_B^2(C^{-1}+T^{-1/2})^2
 \ll T^\epsilon(1+T/C^2)=O(T^\epsilon), \tag{XVI}
\]

since `C≥T^(7/12+η)>√T`. Cross terms with this error are bounded by the same squared triangle inequality; they are not omitted.

Combining (XI), the zeta fourth moment, and (XV) gives the uncompressed estimate

\[
\begin{split}
 \int_T^{2T}|\zeta B_v C_v|^2dt
 &\ll E_{\rm AFE}
  +K T^{-1/2}\log^2(2T)\log^2(2L)
       (T+K R^2L^2)^{1/2}\mathcal D_4^{1/2}W_B L. \tag{XVII}
\end{split}
\]

Here the factor `T^(−1/2)` is the product of the **squared** AFE amplitude `T^(−1)` and the square root `T^(1/2)` of the zeta fourth moment. It is not a missing or guessed power of `T`.

Using (XIII)'s divisor bounds and `W_B≪T^ε/R` now gives

\[
\begin{split}
 \int_T^{2T}|\zeta B_v C_v|^2dt
 &\ll_\epsilon T^\epsilon\left[1+
       T^{-1/2}(T+K R^2L^2)^{1/2}\frac LR\right]\\
 &\ll_\epsilon T^\epsilon\left[1+\frac LR+T^{-1/2}L^2\right]\\
 &\ll_\epsilon T^\epsilon\left[1+\frac TD+\frac{T^{3/2}}{C^2}\right]. \tag{TI-audited}
\end{split}
\]

The last line uses the actual comparability `RC≍D`, and `L=T/C`. Thus `L/R=T/(RC)≍T/D`, while `T^(−1/2)L²=T^(3/2)/C²` exactly. The initial `1` pays the sharp AFE error and endpoints; later (V) supplies another term of the same allowed size for unsmoothing. This establishes the claimed bound, not just its exponents.

## 7. Summing every marked box, with one aggregate loss

At `D=T^(5/6)` and `C≥T^(7/12+η)`, the three raw terms are

\[
 1,\qquad T^{1/6},\qquad T^{1/3-2\eta}.
\]

For all `0<η<1/48`, the last is the largest raw power. The following fixed-logarithm ledger is more than sufficient:

| Source | Squared-norm loss |
|---|---|
| All three variable dyadics, Cauchy over boxes using a maximum | `O(log^6 T)` |
| Fourier/Mellin separation | `O(log^2 T)` |
| Moving interval maximal fourth moment, after its square root | `O(log^2 T)` |
| Zeta fourth moment, after its square root | `O(log^2 T)` |
| Endpoint and taper errors | Lower-order terms; at most fixed logarithms |

Thus a safe `log^20(2T)` allowance, as in the proposal, is sufficient.[1] There is no need to hide any power-sized multiplicity in it.

Here is one explicit divisor-loss budget. Fix `α=η/20` in the pointwise estimates `τj(n)≪α,j n^α`, with fixed divisor orders. All divisor-function indices in the central Type I proof are `O(T²)`. Bounding each such divisor factor by `Oα(T^(2α))`, the tuple-energy proof (XIII) costs at most `T^(10α)` before the outer square root: `T^(2α)` for `τ4(m)` and `T^(8α)` for the four absolute β factors in the squared weights. Consequently (XVII) costs at most `T^(5α)` from these crude divisor estimates. The absolute AFE and taper errors cost at most `T^(4α)` in their squared norms.

For sufficiently large `T`, absorb **all** `log^20(2T)` into `T^(η/2)`. The total allowance is at most

\[
 5\alpha+\eta/2=3\eta/4<\eta.
\]

Choose the fixed integration-by-parts order in (VII) after this allocation, so its power error is negligible. All fixed constants may depend on `η`; none may grow with `T`.

Applying Minkowski to each separated box and Cauchy to their finite sum, adding the original sharp-boundary error, proves

\[
 \int_T^{2T}|\zeta(\tfrac12+it)\mathcal R_{\rm I,D}(1+2it)|^2dt
 \ll_\eta T^{1/3-\eta}. \tag{XVIII}
\]

This is a statement about the **entire actual sharp Type I family**. It is not restricted to a smooth model or to one box. The choice `η=1/120` gives `1/3−η=13/40`. At exactly `C=T^(7/12)` there is no strict saving from this bound; spending all `2η` in aggregate losses would likewise destroy a strict saving. Both are genuine negative controls.

### Transition and exceptional-range ledger

- **`RL≈√T`**, equivalently `C≈T^(2/3)` at the critical `D`: (XVII) retains `T+KR²L²`; no switch loses a range. The bound is then of diagonal size `T^(1/6+ε)` up to constants.
- **`R≈1`, `C≈D`**: the short convolution can be a singleton; the same proof applies, with `L≈T^(1/6)` and `T/D` retained.
- **A singleton or very short `C` interval**: its error is still within (XVI), and the maximal dual interval argument includes empty and singleton intervals.
- **Primal or dual endpoints at integers**: primal differences cost `O(C^(−1))`; a dual jump has size `O(T^(−1/2))`, within the uniform AFE remainder. No averaging over distance to integers is required.
- **`C≈√T` or `C=T^(7/12)`**: the formula does not imply the advertised strict saving there. These ranges are not marked Type I under the fixed positive `η` threshold.
- **`C≈T` or larger, dual cutoff below 1**: the AFE application used here is not automatically valid. These ranges do not occur for `C≪D≍T^(5/6)`, or in the small fixed neighborhood specified below. No claim for them is certified.
- **`v≈0` because of a huge shift**, or **low-height shells**: not covered by this high-height argument. The Fourier tail is disposed of absolutely, not by pretending (TI) holds there.
- **`d≤1/2` in sharp unsmoothing**: (V) retains `T/D²`; the `+1` alone would not cover it.

## 8. The residual J-rem is exact, and what its equivalence means

Define, as finite polynomials,

\[
 \mathcal R_{\rm I,D}(s)=
 \sum_{\substack{a,b\le\sqrt{2D}\\c\ge C_*\\D\le abc<2D}}
 \mu(a)\mu(b)(abc)^{-s},
\]

\[
 \mathcal R_{\rm II,D}(s)=
 \sum_{\substack{a,b\le\sqrt{2D}\\c<C_*\\D\le abc<2D}}
 \mu(a)\mu(b)(abc)^{-s}.
\]

Then **exactly**

\[
 M_D=-\mathcal R_{\rm I,D}-\mathcal R_{\rm II,D}.
\]

These are the original sharp product restrictions, not the smoothed versions. There is no residual Perron error, endpoint fragment, unmarked long box, or contribution from the deleted `2A_U` term in this identity. Smoothing was solely an estimate for the first summand, with its error already paid.

Let `||F||ζ²=∫_T^(2T)|ζ(1/2+it)F(1+2it)|²dt`. The ordinary triangle inequality in this weighted Hilbert space gives both

\[
 ||M_D||_\zeta\le||\mathcal R_{\rm I,D}||_\zeta+||\mathcal R_{\rm II,D}||_\zeta,
\]

and the analogous reverse reconstruction bound for `RII`. Together with (XVIII), a fixed saving for the complete sharp moment and a fixed saving for the **whole** residual are equivalent after replacing the saving by a suitable minimum. The squared triangle inequality gives a minimum of the two squared-norm savings; there is no necessary halving of that exponent just from recombination.

The exact unproved obligation remains

\[
 \int_T^{2T}|\zeta(\tfrac12+it)\mathcal R_{\rm II,D}(1+2it)|^2dt
 \ll T^{1/3-\delta},\qquad D=T^{5/6},\quad\delta>0\text{ fixed}. \tag{J-rem}
\]

A termwise shifted box estimate is a stronger sufficient route, not an equivalent statement. It would need enough fixed slack for all dyadic and Mellin losses, and uniformity in `|u|≤T^(1/2+η)` or a suitably controlled weighted average over those shifts. A theorem only at `u=0` cannot be substituted by moving `t`, because doing so moves zeta's argument as well. Cancellation between different residual boxes is retained in (J-rem) and could be important.

For completeness, the claimed elementary Type II length range is consistent: the largest of three logarithmic lengths is at least `d/3` and at most `7/12+η` at `d=5/6`; the other two grouped together have length exponent at least `1/4−η`. Ordering the two groups gives `T^(1/4−η)≪P≪T^(5/12)≪Q≪T^(7/12+η)`. No cancellation estimate follows from that regrouping alone.

## 9. Required height-length neighborhood uniformity

The audited Type I proof itself survives uniformly for

\[
 D=T^d,\quad |d-5/6|\le\omega,\qquad
 0<\omega<1/6,
\]

with fixed constants, provided the neighborhood remains above `d=1/2`, `C≤KD`, `C≥T^(7/12+η)`, and the same real shift range is used. The restrictions ensure `y1≫T^(1−d)≥1`, sharp-boundary cost `1+T/D²=O(1)`, and polynomial-sized coefficient indices. The resulting formula is still (TI-audited) with the **actual** `D`, not a frozen `T^(5/6)`.

For a variance extension, this is not enough. Write `H=T^q`. The relevant unweighted mixed moment must have uniform saving below `T^(1−q/2)`. With aggregate loss `λ`, the three Type I terms require the simultaneous strict margins

\[
 1-q/2>\delta+\lambda,\qquad
 d-q/2>\delta+\lambda,\qquad
 2c-1/2-q/2>\delta+\lambda. \tag{XIX}
\]

At `c=7/12+η`, the last raw margin is `2η−(q−4/3)/2`. This shows explicitly why even a fixed partial saving needs room when `q` increases.

For example, `ω≤η/4` and `|q−4/3|≤ω` leave strict Type I saving `η/2` below `T^(1−q/2)` after an aggregate allowance `η`. Indeed the long-factor margin after this allowance is at least `η−ω/2>η/2`; the diagonal margin is at least `1/6−3ω/2−η>η/2` for `η<1/48`; the constant term has still more room. These are affine inequalities on the full neighborhood, not merely a sampled numerical assertion.

The **unproved residual** would need corresponding uniformity: fixed positive saving constants throughout a fixed open neighborhood of `(d,q)=(5/6,4/3)`, the actual sharp endpoint masks, the fixed `k=2` decomposition and `U²=2D` at each length, and the separation shifts or their controlled weighted average. A single isolated equality case would not supply it.[1][2]

The formal maximal small-divisor boundary gives, with `H=X^h` and `T=X/H`,

\[
 d=\frac{1/2-h/4}{1-h},\qquad q=\frac h{1-h}=4d-2.
\]

Thus increasing `h` beyond `4/7` moves to `d>5/6` and `q>4/3`; it is not another use at the old central point. Actual epsilon margins require a region around this direction.

Finally a complete variance argument requires all its tail blocks and cumulative heights, schematically a uniform bound for

\[
 \sup_{X/H\le T\le X^2}\frac HT
 \int_{|t|\le T}|\zeta(\tfrac12+it)M_{D,\mathcal B}(1+2it)|^2dt,
 \qquad \sqrt z\le D\ll\sqrt X,
\]

or an adequate direct spectral-kernel replacement, together with the true small-divisor cutoffs, low heights, far-frequency tail, endpoint squares, localization, cross term, and density centering. The baseline has its own complete current-range bookkeeping; a new central Type I estimate is not a new proof of those requirements in an enlarged range.[2]

## 10. Executed independent checks and their limits

`independent_checks.py` was written in this new scratch directory and actually executed with exit code 0. It does not import or call the proposal's checker. It uses a linear Möbius sieve, direct restricted tuple enumeration, the prime-exponent formula for coefficients of zeta powers, exact rational sharp endpoints, and exact rational coefficient energies.

The recorded results in `checks.json`, `checks-summary.json`, and `execution.log` are:

- **28** real-cutoff/order identity cases, covering **774** coefficients in their truncated validity ranges and **1,728** coefficients in the full identity with remainder.
- **70** sharp split cases, covering **1,547** block coefficients and **12,278** tuple assignments; all marked tuples assigned once, with **883** distinct marked boxes across these test cases. These are bounded test totals, not a count of all asymptotic boxes.
- Exact fourth-coefficient norm inequalities for **6** binary levels and disjoint canonical decompositions for all **528** intervals in a 32-element model.
- **18** floating-point sign/modulus diagnostics with both signs of height and real shifts. These illustrate (XII); the proof is the exact conjugation identity, not the floating-point values.
- Negative controls reject: unsafe remainder deletion, omission of an integer threshold case, conjugation with unchanged complex dual coefficients, replacing a moving interval by a fixed cancelling interval, claiming saving at `η=0`, and using up the complete `2η` saving.
- Exact rational scaling and neighborhood endpoint checks accompany the analytic full-neighborhood inequalities above. They certify arithmetic bookkeeping, not the AFE or any missing joint moment.

The interval-freezing control is particularly concrete: at `v=π/log(3/2)` the full dual interval `{2,3}` sums to zero while the singleton `{2}` has modulus 1. A proof that replaced all partial intervals by the full one would fail even in that model. The proposal's binary maximal argument avoids precisely that failure.

The proposal's own checker was inspected but was not treated as independent analytic evidence. No numerical zeta moment experiment, repository gate, staging, commit, publishing, or repository modification was performed. All task artifacts are inside the newly created directory named below; no supplied scratch file was edited.

## 11. Deliverables and stopping point

- `report.md` — this complete audit.
- `verdict.json` — machine-readable `passed`, `blocking_issues`, `required_qualifications`, `reviewed_claims`, `checks`, `report_path`, and `summary`.
- `independent_checks.py`, `checks.json`, `checks-summary.json`, `execution.log` — independent replayable checks and actual execution output.
- `input-manifest-start.json`, `input-preservation.json` — source-byte pinning and final preservation check.
- `readings/`, `citations.json`, `citation-evidence-execution.json`, `citation-verification.log`, `fresh-fetches.json` — reviewed reading copies, source evidence, citation verification, and honest network-failure records.
- `delivery-verification.json` — final artifact/field verification and hashes.

Absolute scratch directory:

`mobius-typeI`

**Bottom line:** the sharp Type I partial saving survives this adversarial reconstruction. The exact split genuinely reduces the remaining complete-moment goal to a joint estimate for the whole sharp residual. That remaining estimate, and the required neighborhood/all-height transfer, have not been proved.

## Sources

[1] file://mobius-factorization/report.md — Proposed Möbius factorization report; reviewed local bytes
    > "A fixed-order, exact Möbius identity does give a genuine power-saving treatment of its long-smooth-factor Type I terms."
[2] file://<repo>/experiments/astra-rh-crt-20260912/GM_TRANSFER.md — Reconciled baseline, GM_TRANSFER
    > "uniform in a neighborhood of that critical length-height relation."
[3] https://dlmf.nist.gov/25.9 — DLMF 25.9, AFE and chi, archived formula-preserving source
    > "If  $x\geq 1$ ,  $y\geq 1$ ,  $2\pi xy=t$ , and  $0\leq\sigma\leq 1$ , then as"
    > "Titchmarsh (1986b, (4.12.4), p. 79)"
    > "\[\zeta\left(\sigma+it\right)=\sum_{1\leq n\leq x}\frac{1}{n^{s}}+\chi(s)\sum_{1%
\leq n\leq y}\frac{1}{n^{1-s}}+O\left(x^{-\sigma}\right)+O\left(y^{\sigma-1}t^%
{\frac{1}{2}-\sigma}\right),\]"
    > "where  $s=\sigma+it$  and
25.9.2
$\chi(s)\equiv\pi^{s-\frac{1}{2}}\Gamma\left(\tfrac{1}{2}-\tfrac{1}{2}s\right)/%
\Gamma\left(\tfrac{1}{2}s\right).$"
[4] https://arxiv.org/src/2006.04060v2 — GMRR v2, archived TeX, Lemmas 3 and 7
    > "Let $a(n)$ be an arbitrary sequence of coefficients and $N, q \geq 1$ be integers and $T \geq 1$ real."
    > "\int_{|t| \leq T} |\zeta(\tfrac 12 + it)|^4 dt \ll T (\log T)^4."
    > "\sum_{\chi \Mod{q}} \int_{|t| \leq T} \Big | \sum_{n \leq N} a(n) \chi^2(n) n^{it} \Big |^2 dt \ll q^{\varepsilon} (q T + N) \sum_{n \leq N} |a(n)|^2."

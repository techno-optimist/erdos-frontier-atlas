# An RH-equivalent squarefree energy target

**Status:** human-readable proof using explicitly named classical analytic
inputs, independently model-audited; review details belong in `review.json`.
Not human peer review, not a Lean theorem, not an unconditional estimate.
No novelty or priority claim: the exact global biconditional below was not
located verbatim in the primary literature inspected. Its ingredients are
classical; a published related equivalence is GMRR's short-interval criterion.[13][14]

Define, for real `x>=1`,

\[
 Q(x)=\sum_{n\le x}\mu(n)^2,\qquad
 c=\frac1{\zeta(2)},\qquad E(x)=Q(x)-cx.
\]

## 1. The exact target

**Proposition.** The following are equivalent:

1. The Riemann Hypothesis.
2. For every `epsilon>0`,
   \[
   V(X):=\int_1^X|E(x)|^2\,dx
        =O_\epsilon(X^{3/2+\epsilon})\quad(X\to\infty). \tag{MS}
   \]

Every epsilon and the integration measure `dx` are part of the statement.
This is not the stronger pointwise quarter-power claim. RH by itself is not
known to imply the conjectural pointwise bound; the k-free literature explicitly
warns about an earlier incorrect claim of such an implication.[15]

## 2. Initial Mellin identity

Absolute convergence of the squarefree Dirichlet series in `Re(s)>1` gives

\[
 F(s):=\int_1^\infty E(x)x^{-s-1}\,dx
 =\frac{\zeta(s)}{s\zeta(2s)}-\frac{c}{s-1}. \tag{1}
\]

Indeed, integrate each indicator `1_{x>=n}` to obtain `n^{-s}/s`, then use
`sum mu(n)^2 n^{-s}=zeta(s)/zeta(2s)`. The subtracted linear term integrates
to `c/(s-1)`. The value at each integer has no effect on this integral.
The same transform is used in the published k-free literature.[15]

## 3. RH implies (MS)

### Named external inputs

- The functional equation and meromorphic continuation of the zeta function.
- The usual unconditional convexity bound: on any fixed strip `a<=u<=b`,
  with `0<a<1<b`, `|zeta(u+it)|` is at most
  `O_{a,b,eta}((1+|t|)^{(1-a)/2+eta})` for large `|t|`.
- Littlewood's RH consequence: for every `d,eta>0`,
  \[
  1/\zeta(u+it)\ll_{d,\eta}(1+|t|)^\eta
  \quad(u\ge1/2+d).
  \]
  This is not assumed unconditionally. Simonič records the underlying
  Littlewood estimate and cites Titchmarsh, Theorem 14.2.[16]
- Cauchy's theorem and the Fourier Plancherel theorem with inverse factor
  `1/(2 pi)`.

These classical inputs are not formalized in this bundle.

### Analyticity and a vertical bound

Under RH, (1) continues holomorphically to `Re(s)>1/4`. At `s=1` the pole
of the quotient has residue `c` and is removed by the subtraction. At `s=1/2`,
the pole of `zeta(2s)` makes its reciprocal zero, not singular. All zeros of
the denominator in the critical strip lie on the boundary `Re(s)=1/4`.

Fix `1/4<a<1<b`. Apply Littlewood with `d=2a-1/2` to the denominator,
and convexity to the numerator. Combining the arbitrarily small exponents,
uniformly in `a<=u<=b`,

\[
 F(u+it)\ll_{a,b,\eta}
 (1+|t|)^{-(1+a)/2+\eta}+(1+|t|)^{-1}. \tag{2}
\]

Small heights are harmless by holomorphy on the compact strip segment.
Choose `0<eta<a/2`. The bound is square-integrable in `t`.

### Why this is the transform of the original error

A vertical L2 estimate alone is insufficient: the no-pole contour argument
below is essential. Extend `g(y)=E(exp(y))` by zero on `y<0`. For `b>1`,
`exp(-by)g(y)` belongs to `L1 intersect L2`; its Fourier transform is
`F(b+it)`, by the original absolutely convergent integral.

For `phi in C_c^infinity(R)`, put

\[
 \Phi(s)=\int_{\mathbb R}\phi(y)e^{sy}\,dy.
\]

Repeated integration by parts makes this entire function decrease faster
than every power of `|Im(s)|`, uniformly on the closed strip. Thus (2) and
Cauchy's theorem allow shifting

\[
 \frac1{2\pi i}\int_{(b)}F(s)\Phi(s)\,ds
 \quad\hbox{to}\quad
 \frac1{2\pi i}\int_{(a)}F(s)\Phi(s)\,ds.
\]

No poles are crossed and the horizontal integrals vanish. The first pairing
is `integral g(y) phi(y) dy`. If `f_a` is the inverse L2 Fourier transform of
`F(a+it)`, the second is `integral f_a(y) exp(ay) phi(y) dy`. Equality for
every test function identifies `f_a(y)=exp(-ay)g(y)` almost everywhere.
Plancherel therefore gives the **original-error** identity

\[
 J_a:=\int_1^\infty |E(x)|^2x^{-2a-1}\,dx
    =\frac1{2\pi}\int_{\mathbb R}|F(a+it)|^2\,dt<\infty. \tag{3}
\]

Hence `V(X)<=X^{2a+1}J_a`. For `0<epsilon<1`, take
`a=1/4+epsilon/2`. This proves (MS) for small epsilon and therefore for all
positive epsilon. No assumption on simplicity or `zeta'(rho)` was used. ∎

## 4. (MS) implies RH, including possible cancellation

For `R>=1`, Cauchy–Schwarz on a dyadic interval gives

\[
 \int_R^{2R}|E(x)|x^{-\sigma-1}\,dx
 \ll_\epsilon R^{1/4+\epsilon/2-\sigma}. \tag{4}
\]

For `sigma>1/4`, choose `epsilon<2(sigma-1/4)` and sum (4) dyadically.
The integral in (1) then converges absolutely. On compact subsets of this
half-plane choose a fixed smaller epsilon; the same summable bounds allow
arbitrary fixed powers of `log x`. This proves holomorphy in `Re(s)>1/4`.

Suppose RH fails. Functional equation and conjugation give a right-of-line
zero `rho=beta+i gamma`, `beta>1/2`, of smallest positive height. Such a
minimum exists because zeros are discrete, finitely many occur up to any
fixed height, and there are no real nontrivial zeros.

If `zeta(rho/2)=0`, reflection and conjugation produce another nontrivial zero

\[
 1-\overline{\rho}/2=1-\beta/2+i\gamma/2,
\]

also strictly right of the line, at smaller positive height. This is a
contradiction. Therefore `zeta(rho/2) != 0` and (1) has a genuine pole at
`rho/2`, of the same multiplicity as the denominator zero. The subtraction
is regular there. This contradicts the established holomorphy and proves RH.
The descending-height mechanism also appears in the k-free literature.[15] ∎

## 5. Analytic negative control: a finite line norm is not enough

Take the toy error `E_theta(x)=x^theta`, with `theta=3/8`. Its transform is
`F_theta(s)=1/(s-theta)` initially for `Re(s)>theta`. On the line `a=5/16`,
the meromorphic continuation has finite norm

\[
 \int_{\mathbb R}|F_\theta(a+it)|^2\,dt=16\pi.
\]

But the corresponding **original** weighted error norm is infinite:

\[
 \int_1^\infty |E_\theta(x)|^2x^{-2a-1}\,dx
 =\int_1^\infty x^{-7/8}\,dx=\infty.
\]

The inverse L2 transform on the left of the pole is
`-exp(y/16) 1_{y<=0}`, not `exp(y/16) 1_{y>=0}`. The missing residue is the
whole issue. This example is an analytic control, not a zeta counterexample.

## 6. Strike map: the remaining unconditional step

For each `delta>0`, prove, **without RH or an equivalent input**, the bound

\[
 \sup_{Y\ge0}\int_0^Y
 |e^{-y/4}E(e^y)|^2e^{-2\delta y}\,dy<\infty. \tag{ENERGY}
\]

Here `J_{1/4+delta}` in (3) is exactly the infinite version of this integral.
(MS) implies it by partial summation using a smaller epsilon; conversely,
(ENERGY) gives (MS) by taking `delta=epsilon/2`. Thus this is an explicit
remaining RH obligation, **not a discharged lemma**.

- Finite quadrature cannot prove uniformity in `Y`.
- Positive-proportion theorems—even asymptotic density one—allow exceptional
  zeros. One least-height exception is enough to obstruct the pole-free shift.
- A zero-density upper bound is not the assertion that the exceptional set is
  empty, and does not control reciprocal-zeta spikes near remaining zeros.
- Do not assume (2) unconditionally; its reciprocal-zeta input uses RH.
- `RESULT.md` gives a fixed generic coefficient countermodel to (ENERGY)'s
  corresponding mean-square scale despite a uniform square-root prefix bound.
  Additional arithmetic structure is necessary for that route.
- A concrete intermediate candidate is GMRR's squarefree short-interval
  variance method: its published range reaches `H<=X^{6/11-epsilon}`, and
  near-optimal upper variance through every `H<=X^{1-epsilon}` is equivalent
  to RH. Testing whether newer large-values bounds enlarge the intermediate
  range is a candidate transfer, not an established improvement.[13][14]
  Its Theorem 3 cannot be applied at `H=X` without leaving the stated range.

No all-height energy estimate, new Möbius bound, or RH solution has been
established by this bundle.

## Sources

[13] https://arxiv.org/pdf/2006.04060v2
[14] https://link.springer.com/article/10.1007/s00039-021-00557-5
[15] https://arxiv.org/html/1912.04972v2
[16] https://link.springer.com/content/pdf/10.1007/s00009-023-02289-2.pdf

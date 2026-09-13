# A quantitative variance-to-Mellin interface

Research derivation for P969. Independent model review passed the transfer and
strict-strip arguments; see `REVIEW_STATUS.json` for scope. This is a
**conditional transfer theorem**, not a proof of its variance hypothesis, an
unconditional new zero-free region, or a novelty claim.
GMRR prove that near-optimal squarefree variance uniformly through every
`H≤X^(1−epsilon)` is equivalent to RH. Their theorem is the external research
target; the derivation here exposes what a fixed range exponent buys.[3]

Put

\[
Q(x)=\sum_{n\le x}\mu(n)^2,\quad \rho=1/\zeta(2),\quad E(x)=Q(x)-\rho x.
\]

The elementary square-divisor identity gives E(x)=O(√x). Hence the original
Mellin integral

\[
F(s)=\int_1^\infty E(x)x^{-s-1}\,dx
\]

converges absolutely for Re(s)>1/2. Initially for Re(s)>1,

\[
F(s)=\frac{\zeta(s)}{s\zeta(2s)}-\frac{\rho}{s-1}.
\tag{M}
\]

The result below gives **analytic continuation** of this function. It does
not assert absolute convergence of the original integral in the larger domain.

## 1. Fixed-range transfer

**Theorem 1.** Fix 0<θ<1. Suppose that for every ν>0,

\[
\frac1X\int_X^{2X}|E(x+H)-E(x)|^2dx
\ll_{\theta,\nu}H^{1/2+\nu}
\tag{Vθ}
\]

uniformly for all sufficiently large real X and integers 1≤H≤X^θ.
Then F has a holomorphic continuation to

\[
\boxed{\operatorname{Re}s>a_\theta:=1-3\theta/4.}
\tag{Aθ}
\]

When a_θ≥1/2 this does not improve the elementary domain already available.

### Proof

Choose a smooth cutoff χ with χ(t)=1 for t≤1 and χ(t)=0 for t≥2.
Put φ(t)=χ(t)−χ(2t) and X_j=2^(j+1), j≥0. Then, locally finitely for x≥1,

\[
\chi(x)+\sum_{j\ge0}\phi(x/X_j)=1.
\]

The dyadic pieces have support [X/2,2X] and derivatives bounded by the
corresponding powers of X⁻¹. Define

\[
g_{X,s}(x)=\phi(x/X)x^{-s},\qquad
I_X(s)=\int_1^\infty E(x)g'_{X,s}(x)\,dx,
\]

extending g by zero to x≤0. Retain the compact initial piece

\[
I_{\rm init}(s)=\int_1^\infty E(x)(\chi(x)x^{-s})'\,dx.
\]

Each I_X is entire in s, since its x-support is compact and bounded away
from zero. For s in a fixed compact set with Re(s)≥a₀>a_θ, choose ν>0 and
an integer K≥1 so that

\[
\nu\theta/2<a_0-a_\theta,\qquad
K(1-\theta)>1/2-a_0.
\tag{CHOICES}
\]

For δ=a₀−a_θ>0, an explicit admissible choice is

\[
\nu=\min(1,\delta/\theta),\qquad
K=1+\left\lfloor\max\left(0,\frac{3\theta-2}{4(1-\theta)}\right)\right\rfloor.
\]

In particular K can depend only on θ; it does not grow with the dyadic index.
For sufficiently large X put
`h=floor((X/2)^theta/K)`. Then h≥1, h is comparable to X^θ with constants
depending on θ,K, and mh≤(X/2)^θ for 1≤m≤K.

Use the backward-derivative coefficients

\[
c_m=\frac{(-1)^{m+1}}m\binom Km\quad(1\le m\le K).
\]

They satisfy

\[
\sum_{m=1}^Kc_mm=1,\qquad
\sum_{m=1}^Kc_mm^j=0\quad(2\le j\le K).
\]

These are the binomial finite-difference identities for polynomials of degree
less than K. Taylor's theorem consequently gives

\[
g'(x)=\frac1h\sum_{m=1}^Kc_m(g(x)-g(x-mh))
+O_K\!\left(h^K\sup_{u\in[x-Kh,x]}|g^{(K+1)}(u)|\right).
\]

The nonzero remainder is supported in [X/2,2X+Kh]⊆[X/2,5X/2] for X≥2,
since Kh≤(X/2)^θ≤X/2. Its support has length O(X) with x comparable to X.
Derivatives of g on that interval are bounded by
`O_(K,compact)(X^(-Re(s)-K-1))`. Since E(x)=O(√x), pairing the remainder
against E costs

\[
O_{K,\mathrm{compact}}\left(X^{1/2-\operatorname{Re}s-K(1-\theta)}\right).
\tag{ERR}
\]

For the main term change variables exactly:

\[
\int E(x)(g(x)-g(x-mh))dx
=-\int (E(x+mh)-E(x))g(x)dx.
\]

The support [X/2,2X] is covered by [X/2,X] and [X,2X], and (Vθ) applies to
both with the integer shift mh. Cauchy–Schwarz gives

\[
\left|\frac1h\sum_{m=1}^Kc_m\int(E(x+mh)-E(x))g(x)dx\right|
\ll_{K,\mathrm{compact},\nu}
X^{1-\operatorname{Re}s}h^{-3/4+\nu/2}.
\tag{DIFF}
\]

Thus, uniformly on the compact set,

\[
|I_X(s)|\ll
X^{a_\theta-a_0+\nu\theta/2}
+X^{1/2-a_0-K(1-\theta)}.
\]

Both exponents are negative by (CHOICES), so the dyadic series of I_X
converges normally. Keep as entire terms the finitely many initial scales
where h=0 or the variance hypothesis does not yet apply; do not use the
stencil at those scales.

On the overlap with Re(s)>1/2, bounded support overlap and E(x)=O(√x)
justify summing inside the integral. Differentiating the partition gives

\[
I_{\rm init}(s)+\sum_j I_{X_j}(s)
=\int_1^\infty E(x)(x^{-s})'\,dx=-sF(s).
\]

Consequently `−(I_init+sum I_X)/s` gives the desired continuation, agreeing
with (M) on the overlap. Division by s is harmless since a_θ>1/4. This uses
no integration by parts against discontinuous E and discards no lower-end
term. ∎

### Why a first-order difference is insufficient

Taking only K=1 leaves the error exponent `theta−1/2−Re(s)`. For θ near one,
that prevents the desired extension. The arbitrarily high but **fixed** order
K absorbs the loss `(h/X)^K` for each θ<1. Neither K nor its implicit constant
is silently kept uniform as θ tends to one.

### Sharpness in the generic analytic class

The proof above uses E(x)=O(√x) and (Vθ), but not the zeta identity (M).
Together with the elementary integral domain, it gives the effective threshold

\[
b_\theta=\min(1/2,1-3\theta/4).
\]

This threshold is sharp for those **generic** hypotheses. Set E_b(x)=x^b
with b=b_θ. It is O(√x), and the mean-value theorem gives, for X≥1 and
1≤H≤X^θ,

\[
\frac1X\int_X^{2X}|E_b(x+H)-E_b(x)|^2dx
\le b^2 H^2 X^{2b-2}
\le b^2 H^{1/2}X^{3\theta/2+2b-2}
\le b^2 H^{1/2}.
\]

Its Mellin transform is 1/(s−b), with a pole exactly at b. Thus neither
boundary holomorphy nor a strictly larger full half-plane follows in this
class. For θ≤2/3 the example is √x; for θ≥2/3 it is x^(a_θ). This is a
parent extension of the audit's latter endpoint control. These power functions
are **not the squarefree error** and do not obey (M); the example does not
rule out stronger conclusions using additional arithmetic information.

## 2. Pole visibility is not automatic zero exclusion

Holomorphy of (M) for Re(s)>a does not, by this argument alone, exclude every
zeta zero with real part greater than 2a. At s=ρ₀/2 a numerator zero can cancel
a denominator zero. For a fixed a>1/4, the reflected numerator zero may leave
the region whose poles the continuation detects. A separate noncancellation
argument is necessary; no theorem forbidding all such coincidences is assumed.

There is, however, an invariant strip where reflection remains visible.

**Theorem 2.** If `1/4<a<1/3` and F is holomorphic for Re(s)>a, then ζ has no
nontrivial zero with

\[
\boxed{2a<\operatorname{Re}\rho_0<2-4a.}
\tag{STRIP}
\]

**Proof.** Suppose ρ₀=β+iγ is such a zero, with γ>0. Nontrivial real zeros
in (0,1) do not occur, as follows for example from the alternating eta series;
complex conjugation therefore permits this choice of sign.
At s=ρ₀/2, holomorphy in (M) forces ζ(ρ₀/2)=0: the factors s and s−1 are
nonzero there and the subtracted elementary term is regular. This argument
works with any multiplicity.

The functional equation and complex conjugation produce another zero

\[
\rho_1=1-\overline{\rho_0}/2,
\quad\beta_1=1-\beta/2,\quad\gamma_1=\gamma/2.
\]

If 2a<β<2−4a, then

\[
2a<\beta_1<1-a<2-4a,
\]

where the last inequality uses a<1/3. The map preserves the same open strip.
It can therefore be iterated, giving distinct zeros with
`gamma_j=gamma/2^j` and `beta_j−2/3=(-1/2)^j(beta−2/3)`.
They accumulate at 2/3, contradicting isolated zeros of the nonzero holomorphic
function ζ near that point. ∎

Neither boundary of (STRIP) is included. In particular, the proof does not
exclude zeros at the analytic-continuation boundary by continuity.

## 3. Parameter ledger and what it does not prove

Substituting a=a_θ gives a nonempty invariant zero strip only when θ>8/9:

\[
2-3\theta/2<\beta<3\theta-2.
\]

| Range parameter θ | Continuation threshold a_θ | Conditional invariant zero strip |
|---|---|---|
| 6/11 | 13/22 | none; weaker than elementary continuation |
| 4/7 (proposed range; audit pending) | 4/7 | none; weaker than elementary continuation |
| 2/3 | 1/2 | none; elementary boundary |
| 3/4 | 7/16 | none from this particular strip argument |
| 4/5 | 2/5 | none from this particular strip argument |
| 8/9 | 1/3 | empty at the endpoint |
| 9/10 | 13/40 | 13/20 < β < 7/10 |
| 19/20 | 23/80 | 23/40 < β < 17/20 |

The 6/11 and 2/3 rows are **limiting reference exponents**, not assertions of
endpoint estimates. GMRR's unconditional and Lindelöf-conditional ranges,
respectively, carry a negative epsilon in the exponent.[3]
The proposed 4/7 row is also only a limiting diagnostic, not an endpoint
estimate or an established new asymptotic. Even if that variance transfer
survives its separate audits, this Mellin route gives no new zero exclusion.
The last rows are hypothetical applications of (Vθ), not currently proved
zero exclusions. The thresholds 2/3 and 8/9 price **these transfers**, not all
possible approaches to RH.

If (Vθ) were established for θ arbitrarily close to one, the intervals
`(2a_θ,2−4a_θ)` would exhaust (1/2,1). The functional equation would then give
RH. No simplicity of zeros or reciprocal derivative-moment bound is needed.
The missing step is still the all-scale variance hypothesis.

### A continuation-to-energy negative control

For the generic function E_*(x)=√x sin(2πx), repeated integration by parts
of its oscillatory Mellin integrals gives an entire continuation. The
lower-end terms are entire in s. Nevertheless, for integer X≥1,

\[
\int_X^{2X}|E_*(x)|^2\,dx=\frac34X^2.
\]

The equality follows by integrating x(1−cos(4πx))/2; the trigonometric
boundary terms cancel at integer endpoints. This function is not the
squarefree error and is not asserted to satisfy the all-θ variance hypothesis.
It shows why continuation **alone** cannot be promoted to the desired global
mean-square estimate without a separate growth/boundary argument.

## 4. What the Atlas gets

Input: an actual finite-X variance estimate with specified θ and every ν>0.

Operator: high-order finite differences dual to a compactly supported Mellin
test, followed by a normally convergent dyadic sum.

Output: a precisely stated continuation domain, and an invariant zero strip
only where repeated pole cancellation cannot leave that domain.

Losses: `h^(-3/4+nu/2)` in the main term and `(h/X)^K` against the elementary
error bound. Constants depend on θ, K, ν and the compact s-set.

Still missing: a stronger actual variance estimate. Guth–Maynard's
large-values theorem is a potential input to a separate parameter audit,
not an automatically applicable replacement for every bound in GMRR.[3][4]

The exact coefficient moments for orders 1 through 12 and the original rational
table are recorded in `mellin_arithmetic.json`. The audit replay and the added
4/7 diagnostic are recorded separately in `REVIEW_STATUS.json`. Those calculations do not establish
normal convergence, a zeta zero-free region, or RH. This document does not
claim a vertical L² estimate or an inverse-Mellin identification below the
original integral's convergence domain.

## Sources

[3] https://arxiv.org/html/2006.04060v2
[4] https://annals.math.princeton.edu/2026/203-2/p06

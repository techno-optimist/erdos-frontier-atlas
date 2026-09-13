# Removing the small-prime phase energy

Research derivation for P969. No unconditional RH-scale bound on the actual
integers is proved here. No novelty claim is made. The classical antecedents
are Mirsky's correlation formula, the squarefree dynamical system described by
Cellarosi–Sinai, and the variance theory of squarefrees and B-free integers.[1][2]
Independent review status is recorded separately; finite replay is not a proof
of the all-parameter statements below.

## 1. Two averaging spaces

Let P be a finite set of distinct primes, M its product (empty product 1),
L=M², and

\[
f_P(n)=\prod_{p\in P}(1-\mathbf1_{p^2\mid n}),\qquad
\rho_P=\prod_{p\in P}(1-p^{-2}),\qquad
A_P(x,H)=\sum_{x<n\le x+H}f_P(n).
\]

Here f_P is defined on all integer n, and A_P counts integer points in the
indicated window. This gives its periodic extension also for negative starts.

Define the **continuous, uniform-phase** variance for every real H≥0 by

\[
V_P(H)=\frac1L\int_0^L|A_P(x,H)-\rho_PH|^2\,dx.
\]

For integer H this is exactly the average over integer residues n modulo L
of `(sum_{j=1}^H f_P(n+j)-rho_P H)^2`. For noninteger H one must also average
over the fractional part of x; simply replacing H by floor(H) is wrong.
Neither averaging space is an arbitrary finite interval of actual integers.

Write ψ(t)={t}(1−{t}) and

\[
w_{P,d}=\prod_{\substack{p\in P\\p\nmid d}}(1-2p^{-2})\quad(d\mid M).
\]

## 2. Exact positive divisor formula

**Theorem 1.** For every finite P and real H≥0,

\[
\boxed{V_P(H)=\sum_{d\mid M}w_{P,d}\,\psi(H/d^2).}
\tag{CRT}
\]

**Proof for integer H.** CRT gives the two-point correlation

\[
R_P(k)=\frac1L\sum_{n\bmod L}f_P(n)f_P(n+k)
=\prod_{p\in P}\left(1-\frac2{p^2}+\frac{\mathbf1_{p^2\mid k}}{p^2}\right)
=\sum_{d\mid M}\frac{w_{P,d}}{d^2}\mathbf1_{d^2\mid k}.
\]

This is the finite-prime counterpart of the classical correlation expansion;
the factor d⁻² must not be dropped.[1]
For an integer modulus q and H=kq+r, 0≤r<q, counting pairs of offsets with
identical residues gives

\[
\sum_{i,j=1}^H\mathbf1_{q\mid i-j}
=(q-r)k^2+r(k+1)^2
=H^2/q+q\psi(H/q).
\]

Consequently the uncentered second moment is

\[
H^2\sum_{d\mid M}w_{P,d}/d^4+\sum_{d\mid M}w_{P,d}\psi(H/d^2).
\]

The coefficient of H² is **exactly**

\[
\sum_{d\mid M}w_{P,d}/d^4
=\prod_{p\in P}(1-2p^{-2}+p^{-4})=\rho_P^2.
\]

Subtracting the square of the mean proves (CRT) without estimating two large
terms separately.

**Extension to real H.** Put H=m+α, m integer and 0≤α<1. The fractional part
of a uniform x selects an m-offset window with probability 1−α and an
(m+1)-offset window with probability α. Its integer residue is independent
of that choice. Thus

\[
V_P(m+\alpha)=(1-\alpha)V_P(m)+\alpha V_P(m+1)
+\rho_P^2\alpha(1-\alpha).
\]

The right side of (CRT), considered as a function of H, has second derivative
`−2 sum_{d|M} w_{P,d}/d^4 = −2 rho_P²` on every open interval (m,m+1).
It has the correct values at the two endpoints, so the same interpolation
identity proves equality for all real H. ∎

### Uniform bound with no dependence on the prime cutoff

**Corollary 1.** `0≤V_P(H)≤sqrt(H)` for every finite P and H≥0.

Indeed, 0<w≤1 and ψ(H/d²)≤min(1/4,H/d²). For H>0 the latter majorant,
as a function of a positive real variable d, is nonincreasing, so

\[
V_P(H)\le\sum_{d\ge1}\min(1/4,H/d^2)
\le\int_0^\infty\min(1/4,H/t^2)\,dt=\sqrt H.
\]

The integral is split at t=2√H. The H=0 case is immediate. This is a bound in
the phase model, **not yet in the empirical average over [X,2X]**.

## 3. Prime addition and an orthogonal refinement

For the real kernel W_P defined by the right side of (CRT),

\[
W_{P\cup\{p\}}(t)=(1-2p^{-2})W_P(t)+W_P(t/p^2),\qquad p\notin P.
\]

The operators `T_p W(t)=(1-2p^-2)W(t)+W(t/p²)` commute, and W_empty=ψ.
This is an exact prime-by-prime operator, not a fit to numerical data.

Let P⊆Q and normalize the centered window counts by their own densities:

\[
S_P=A_P/\rho_P-H,\qquad U_P=V_P/\rho_P^2.
\]

Under uniform continuous phase modulo L_Q, condition on the integer phase
modulo L_P **and on its fractional part**. The omitted prime coordinates are
independent by CRT, giving

\[
\mathbb E(S_Q\mid P\text{-phase})=S_P,
\qquad
\boxed{\mathbb E|S_Q-S_P|^2=U_Q-U_P\ge0.}
\tag{REFINE}
\]

The equality follows by expanding the square and using the vanishing
conditional expectation of the increment. This is a martingale in the
**prime coordinates**, not a temporal independence or mixing assertion about
successive integers. The classical squarefree system has pure point spectrum;
its phase description must not be mistaken for temporal mixing.[1]

Explicitly define the unnormalized, centered difference by

\[
D_{P,Q}(x,H)=(A_P(x,H)-\rho_PH)-(A_Q(x,H)-\rho_QH).
\]

The same computation gives

\[
\mathbb E|D_{P,Q}|^2
=V_Q+(1-2\rho_Q/\rho_P)V_P.
\tag{DEFECT-PHASE}
\]

Because ρ_Q/ρ_P≥1/ζ(2)>1/2, this is at most V_Q≤√H. Positivity is supplied
by its squared-norm interpretation, not by the sign of the displayed
coefficient. Do not replace (REFINE) by an unnormalized variance difference.

## 4. The actual-integer transfer and its remaining obligation

For x≥0 define `Q(x)=sum_{1<=n<=x} mu(n)^2`, with an empty sum interpreted
as zero. Put ρ=1/ζ(2), and define the **centered omitted-prime defect**

\[
D_P(x,H)=\sum_{x<n\le x+H}(f_P(n)-\mu(n)^2)-H(\rho_P-\rho).
\]

The uncentered summand is the indicator that n passes the P-filters but is
not squarefree. Its nonnegativity does not bound the second moment of its
centered count.
Let

\[
\mathcal V_X(H)=\frac1X\int_X^{2X}|Q(x+H)-Q(x)-\rho H|^2dx,
\qquad
\mathcal D_{X,P}(H)=\frac1X\int_X^{2X}|D_P(x,H)|^2dx.
\]

**Theorem 2 (exact norm transfer).** For X>0, H≥0,

\[
\left|\sqrt{\mathcal V_X(H)}-\sqrt{\mathcal D_{X,P}(H)}\right|
\le\sqrt{\frac{L\lceil X/L\rceil}{X}V_P(H)}.
\tag{TRANSFER}
\]

**Proof.** The true centered count is the filtered centered count minus D_P.
Use the triangle inequality and its reverse in the empirical L² space. The
square of the filtered centered count is a nonnegative L-periodic function.
An interval of length X consists of complete periods and at most one residual
arc. That arc contributes at most one whole-period integral, giving the
factor `L ceil(X/L)/X`. This works for real X and H as defined above. ∎

For X≥1, choose any finite-prime rule P=P(X) with L_P≤X, for example
the largest initial segment of primes whose squared product does not exceed
X (the empty set is allowed). Then

\[
\boxed{\left|\sqrt{\mathcal V_X(H)}-
\sqrt{\mathcal D_{X,P(X)}(H)}\right|\le\sqrt2\,H^{1/4}.}
\tag{LOCAL-DEFLATION}
\]

In particular, the two directions give the explicit energy inequalities

\[
\mathcal D_{X,P(X)}(H)\le2\mathcal V_X(H)+4\sqrt H,\qquad
\mathcal V_X(H)\le2\mathcal D_{X,P(X)}(H)+4\sqrt H.
\]

For H≥1, either bound `C H^(1/2+delta)` transfers with constant at most
`2C+4`, independently of the prime-selection rule. The restriction X≥1 is
necessary for L_P≤X even for the empty set, whose period is 1.

GMRR's Theorem 3 therefore gives the following **equivalent obligation**:[3]

> RH holds if and only if, for every ε∈(0,1/100) and δ>0,
> `D_(X,P(X))(H) <<_(epsilon,delta) H^(1/2+delta)` uniformly for
> `1≤H≤X^(1−epsilon)`, where D here denotes the energy `mathcal D`.

Both implications follow from (LOCAL-DEFLATION) and H≥1. The filtered part
has been removed with a proved uniform bound. **No required estimate for
mathcal D is proved here.** This is an explicit localization of the remaining
problem, not a claim that its difficulty has decreased.

### Why the fixed-H limit does not finish the transfer

As P exhausts the primes, the product-phase model converges in L² for each
fixed H; the normalized variables are uniformly bounded for fixed H and
ρ_P stays above 1/2. Dominated convergence in (CRT) is also justified by
`min(1/4,H/d²)`, which is summable over positive integers d. The limit retains
`V_infinity(H)≤sqrt(H)`. The classical correlation formulas identify this
with the limiting empirical variance for **fixed H** as X→∞.[1][2]

This does not give a uniform rate when H grows with X. A finite period can be
far larger than X, and a small omitted-prime density does not by itself
control its centered energy. The unresolved estimate in (LOCAL-DEFLATION)
is precisely a finite-scale statement.

## 5. A concrete control against confusing phase and sample

For P={2,3,5}, the CRT conditions
`n≡−1 (mod 4), n≡−2 (mod 9), n≡−3 (mod 25)` give n=547 modulo 900.
All three numbers 548,549,550 fail their assigned square filters. Thus at
that selected phase, for H=3 and ρ_P=16/25, the squared centered error is

\[
(0-3\cdot16/25)^2=2304/625>\sqrt3.
\]

The checker verifies this exactly by squaring the comparison. This disproves
a pointwise reading of the unit-constant phase bound. It is **not** a
counterexample to GMRR's averaged estimate or to RH.

## 6. Transfer beyond squarefrees

For an integer r≥2, filter by p^r instead of p². The density and period are

\[
\rho_{P,r}=\prod_{p\in P}(1-p^{-r}),\qquad L_{P,r}=M^r.
\]

Use this density for centering and this period for the continuous-phase
average. The same proof gives

\[
V_{P,r}(H)=\sum_{d\mid M}\prod_{\substack{p\in P\\p\nmid d}}
(1-2p^{-r})\psi(H/d^r)
\le\frac r{r-1}4^{1/r-1}H^{1/r}.
\]

For integer H the pair-counting calculation uses moduli d^r. The continuous
extension uses the same interpolation argument. The integral majorant is
split at `(4H)^(1/r)`. The shipped executable replay covers r=2 only; the
general-r statement is an informal all-parameter derivation. A corresponding
periodic norm transfer uses M^r, not M². No r-free RH equivalence is inferred
from this extension. General B-free variance results are already in the
literature.[2]

## Scope of this contribution

- A self-contained finite-prime operator and exact centering mechanism.
- A continuous-phase interpretation and normalized orthogonal refinement.
- An actual-integer norm transfer with an explicit periodicity cost.
- An RH-equivalent centered-defect obligation, **still undischarged**.
- A separate quantitative analytic interface in `MELLIN_TRANSFER.md`.
- No new unconditional squarefree estimate, accepted RH result, or novelty claim.

## Sources

[1] https://arxiv.org/html/1112.4691v2
[2] https://arxiv.org/html/2112.12234v1
[3] https://arxiv.org/html/2006.04060v2

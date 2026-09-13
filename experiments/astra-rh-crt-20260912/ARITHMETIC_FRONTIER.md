# Arithmetic frontier beyond the squarefree-variance transfer

This note consolidates two independently model-audited arguments. They isolate
controlled parts of the arithmetic problem, **not a further variance-range
extension or an RH proof**. The established deduction in this packet remains
`GM_TRANSFER.md`: the GMRR asymptotic in the range
`H <= X^(4/7-epsilon)`, using its stated external theorem inputs. No novelty or
current-record claim is made.

There are two complementary decompositions below. They are **not three
independent positive contributions that can simply be added together**.

## 1. The remaining scale

Write
$$
M_D(s)=\sum_{D\le d<2D}\mu(d)d^{-s},\qquad
I(T,D)=\int_T^{2T}|\zeta(\tfrac12+it)M_D(1+2it)|^2\,dt.
$$
At the critical relation `D = T^(5/6)`, the reconciled generic estimate is
$$
I(T,D)\ll_\varepsilon T^{1/3+\varepsilon}.
$$
A further advance through this route needs a fixed saving, with appropriate
uniformity in a neighborhood of that relation—not another finite evaluation.
The polynomial has standalone length `D`; at the original zeta time its
frequencies are indexed by squares `d^2`. These descriptions are not
interchangeable when applying a twisted-moment theorem.

## 2. An exact sharp Möbius decomposition

Let `A_U(s) = sum_(n<=U) mu(n)n^(-s)` and `E_U(s)=1-zeta(s)A_U(s)`.
For a fixed positive integer `k`, the finite algebraic identity is
$$
\frac1{\zeta(s)}=
\sum_{j=1}^k(-1)^{j-1}\binom{k}{j}\zeta(s)^{j-1}A_U(s)^j
+\frac{E_U(s)^k}{\zeta(s)}.
$$
It is first an identity in the absolutely convergent half-plane. Coefficient
comparison is then finite. The coefficients of `E_U` vanish through `floor(U)`,
so the remainder starts at an integer at least `(floor(U)+1)^k > U^k`.
Consequently `U^k >= 2D` suffices for the entire half-open block `[D,2D)`.
Do not let `k` grow with `T` without new loss accounting.

For the audited split take **`k=2`, `U=sqrt(2D)`, and `D>2`**. Since `U<D`,
the `2A_U` term has no coefficient in the block. Exactly,
$$
M_D(s)=-\sum_{\substack{a,b\le\sqrt{2D}\\D\le abc<2D}}
\mu(a)\mu(b)(abc)^{-s}.
$$
Fix `0<eta<1/48` and put `C_*=T^(7/12+eta)`. Define the actual finite
polynomials
$$
\mathcal R_{\mathrm I,D}(s)=
\sum_{\substack{a,b\le\sqrt{2D}\\c\ge C_*\\D\le abc<2D}}
\mu(a)\mu(b)(abc)^{-s},
$$
$$
\mathcal R_{\mathrm {II},D}(s)=
\sum_{\substack{a,b\le\sqrt{2D}\\c<C_*\\D\le abc<2D}}
\mu(a)\mu(b)(abc)^{-s}.
$$
Thus
$$
\boxed{M_D=-\mathcal R_{\mathrm I,D}-\mathcal R_{\mathrm {II},D}.}
$$
This partitions representations `(a,b,c)`, not integers into a claimed
positive-proportion subclass. Singleton factors, the exact threshold, and the
sharp product endpoints are retained. Here “Type I” means a long
**coefficient-one factor** `c`; it is not a claim about smooth numbers.

## 3. The controlled Type I operator

For a marked dyadic box, group `r=ab` and write
$$
B(v)=\sum_{r\asymp R}\frac{\beta(r)}{r^{1+iv}},\qquad
C(v)=\sum_{C_0\le c<C_1}c^{-1-iv},\qquad RC_0\asymp D,
$$
with fixed support-width constants and `|beta(r)| <= tau_2(r)`. The audited
estimate, in the stated critical neighborhood, is
$$
\boxed{
\int_T^{2T}|\zeta(\tfrac12+it)B(2t+u)C(2t+u)|^2dt
\ll_\varepsilon T^\varepsilon
\left(\frac TD+\frac{T^{3/2}}{C_0^2}+1\right),
}
$$
uniform for real `|u| <= T^(1/2+eta)`. Zeta stays at its **original argument**.
The proof is as follows.

1. Use the classical sharp approximate functional equation at `s=1+iv`,
   `v=2t+u`, at both endpoints. Its hypotheses include `x,y>=1` and
   `2*pi*x*y=v`. Here `v` is comparable to `T` and `C_1` is well below `T`,
   so both dual cutoffs are admissible.[6]
2. Subtraction gives
   $$
   C(v)=-\chi(1+iv)
   \sum_{v/(2\pi C_1)<\ell\le v/(2\pi C_0)}\ell^{iv}
   +O(C_0^{-1}+T^{-1/2}).
   $$
   The exact squared amplitude is
   `|chi(1+iv)|^2=(2*pi/|v|) coth(pi*|v|/2)`, hence it is of order `T^-1`.
   Conjugating the coefficient-one dual sum changes its phase sign without
   changing its modulus. This is not valid with arbitrary complex dual
   coefficients left unchanged.
3. The dual interval moves with `v`. Its length scale is `L=T/C_0`.
   It cannot be replaced by a fixed interval. A binary-interval maximal
   argument handles all its endpoints with logarithmic loss. At each level
   the intervals are disjoint, so the relevant coefficient energies sum
   without a factor `L`.
4. For a fixed dual interval `J`, put
   `F_J(v)=B(v) sum_(ell in J) ell^(-iv)`. Its length is `P~RL`.
   If `d_J(m)` are the coefficients of `F_J^2`, Cauchy–Schwarz over
   multiplicative representations gives
   $$
   \sum_m|d_J(m)|^2
   \le \max_{m\ll P^2}\tau_4(m)
   \left(\sum_{r\asymp R}\frac{|\beta(r)|^2}{r^2}\right)^2 |J|^2.
   $$
   The inner energy is `O_epsilon(T^epsilon/R)`. Apply the ordinary
   polynomial mean-value theorem to `F_J^2`, then Cauchy–Schwarz with the
   zeta fourth moment. These are GMRR's Lemma 7 at modulus `q=1`, and
   Lemma 3, respectively.[3]
5. With the squared functional-equation amplitude paid, the resulting cost is
   $$
   T^\varepsilon T^{-1/2}(T+(RL)^2)^{1/2}\frac{L}{R}
   \ll T^\varepsilon\left(\frac TD+\frac{T^{3/2}}{C_0^2}\right).
   $$
   The AFE remainder adds `O(T^epsilon)`.

The sharp product cutoff is not silently discarded. An inside-supported taper
with transition width `Delta=T^-1/2` has a squared mixed-norm boundary cost
$$
\ll T^\varepsilon(1+T/D^2),
$$
which is `O(T^epsilon)` here. Mellin separation costs a logarithmic `L1` norm;
the relevant real imaginary-part shifts satisfy the displayed `u` range.
Fixed-order tails, all dyadic boxes, divisor bounds and maximal losses share
**one aggregate budget**.

At `D=T^(5/6)` and `C_0>=T^(7/12+eta)`, the three raw terms have exponents
`1/6`, at most `1/3-2*eta`, and `0`. Spending at most `eta` in aggregate
still yields the sharp partial saving
$$
\boxed{
\int_T^{2T}|\zeta(\tfrac12+it)
\mathcal R_{\mathrm I,D}(1+2it)|^2dt
\ll_\eta T^{1/3-\eta}.
}
$$

### What remains after this exact split

The whole residual estimate
$$
\boxed{
\int_T^{2T}|\zeta(\tfrac12+it)
\mathcal R_{\mathrm {II},D}(1+2it)|^2dt
\ll T^{1/3-\delta},\qquad\delta>0,
}
$$
is **unproved**. A fixed saving for it and a fixed saving for the full moment
are equivalent after taking the appropriate minimum with the Type I saving,
by the triangle inequality in the weighted `L2` norm. There is no automatic
need to halve that squared-norm saving.

At the critical point, elementary regrouping puts the residual in Type II
lengths
$$
T^{1/4-\eta}\ll P\ll T^{5/12}\ll Q\ll T^{7/12+\eta}.
$$
This regrouping supplies no cancellation estimate. A bound for each separated
box is a stronger sufficient approach; cancellation between residual boxes
must remain available. A theorem at `u=0` does not supply uniform separation
shifts by moving `t`, since that also moves zeta.

The Type I proof has a justified small neighborhood version with actual
`D=T^d`, `1/2<d<1`. For a prospective variance extension write `H=T^q`.
With an aggregate allowance `lambda`, its terms require strict margins
$$
1-q/2>\delta+\lambda,\quad
 d-q/2>\delta+\lambda,\quad
 2c-1/2-q/2>\delta+\lambda.
$$
For example, `|d-5/6|<=omega`, `|q-4/3|<=omega`, and `omega<=eta/4`
leave a Type I saving `eta/2` after an aggregate allowance `eta`.
The full residual still needs a uniform estimate in such a neighborhood,
with all actual endpoint masks, blocks, and heights. No unrestricted
`C_0~T` regime, real-part shift, or arbitrary oscillatory product mask is
certified by this argument.

## 4. The entire signed arithmetic diagonal

This is a different decomposition of the same moment. Fix nonzero
`w>=0` in `C_c^infinity((1,2))` and set
$$
I_w(T,D)=\int_{\mathbb R}w(t/T)
|\zeta(\tfrac12+it)M_D(1+2it)|^2dt.
$$
Use the BCR product AFE with
$$
G(z)=(1-4z^2)e^{z^2},\qquad
W(x)=\frac1{2\pi i}\int_{(2)}x^{-z}G(z)\frac{dz}{z}.
$$
This `G` meets the stated evenness, normalization, decay and `G(1/2)=0`
conditions. The AFE error is `O(T^-2/3)` on the high shell.[7]
The **outer weight** `w` is nonnegative; the **AFE weight** `W` changes sign.

The ordinary mean value at standalone length `D` gives
`integral_(T)^(2T) |M_D(1+2it)|^2 dt << T/D+1`. Thus the paid AFE error is
$$
E_w\ll_{w,\varepsilon}T^{-2/3+\varepsilon}(T/D+1),
$$
not an unpaid integral of a pointwise remainder. At the critical relation it
is `O(T^(-1/2+epsilon))`.

Define
$$
K_{T,w}(\xi,y)=\int_{\mathbb R}w(t/T)
W(2\pi y/t)e^{it\xi}\,dt.
$$
The exact decomposition is
$$
I_w=\mathcal D_w+\mathcal O_w+E_w,
$$
where the diagonal includes **every** equality `m e^2 = n d^2`, not only
`d=e` and `n=m`. Put `d=g a`, `e=g b`, `(a,b)=1`. Then
`n=b^2 ell`, `m=a^2 ell`.

For `q=ab`, the relevant harmonic sum has Mellin representation
$$
J_q(t)=\frac{2}{2\pi i}\int_{(c)}
\zeta(1+2z)G(z)\left(\frac{t}{2\pi q^2}\right)^z\frac{dz}{z}.
$$
Shift to `Re(z)=-sigma`, with fixed `0<sigma<1/4`. The double-pole residue
at zero is
`log(t/(2*pi))-2 log(q)+2*gamma`; evenness gives `G'(0)=0`.

The required uniform summation is justified by
$$
\sum_{d,e\asymp D}\frac{(d,e)^2}{d^2e^2}
\left(\frac{de}{(d,e)^2}\right)^{2\sigma}
\ll_\sigma D^{-1}.
$$
Indeed `a` and `b` are comparable. On a dyadic scale `a,b~R`, the contribution
is `O(D^-1 R^(-1+4*sigma))`, and the scale sum converges. The same argument
controls an extra logarithm.

Consequently, with
$$
Q_D=\sum_{D\le d,e<2D}\mu(d)\mu(e)\frac{(d,e)^2}{d^2e^2},
$$
the full signed diagonal is
$$
\mathcal D_w(T,D)=
T\log T\,Q_D\int_0^\infty w(v)\,dv+O_w(T/D).
$$

### Positive leading coefficient, not positive AFE terms

The Jordan identity `sum_(r|n) J_2(r)=n^2` gives the finite Gram decomposition
$$
Q_D=\sum_r J_2(r)
\left(\sum_{\substack{D\le d<2D\\r\mid d}}
\frac{\mu(d)}{d^2}\right)^2.
$$
For `D<=r<2D`, the only multiple of `r` in the block is `r`. Therefore
$$
Q_D\ge\sum_{D\le r<2D}\frac{\mu(r)^2J_2(r)}{r^4}
\ge\frac1{\zeta(2)}\sum_{D\le r<2D}\frac{\mu(r)^2}{r^2}
\gg D^{-1}.
$$
Here `J_2(r)/r^2=product_(p|r)(1-p^-2) >= 1/zeta(2)` and the elementary
squarefree count supplies the last bound. The absolute gcd estimate gives
the matching upper bound. Hence, for the **full Möbius block** and fixed
nonzero nonnegative `w`,
$$
\boxed{\mathcal D_w(T,D)\asymp_w T\log T/D.}
$$
At `D=T^(5/6)`, this is `T^(1/6+o(1))`.

This lower scale is **not** a lower bound for the full mixed moment.
It also does not extend uniformly to arbitrary masks: the zero mask is an
immediate counterexample. Bounded masks retain the upper bound; complex
coefficients require the corresponding conjugates and absolute squares.

## 5. The signed off-diagonal obligation

With the exact cutoffs retained,
$$
\mathcal O_w=
2\sum_{D\le d,e<2D}\frac{\mu(d)\mu(e)}{de}
\sum_{\substack{n,m\ge1\\m e^2\ne n d^2}}
\frac{K_{T,w}(\log(m e^2/(n d^2)),nm)}{\sqrt{nm}}.
$$
The product AFE and high-shell integration justify localization to comparable
dyadic `n,m` and the effective scales from order `1` through
`T^(1/2+epsilon)`, with controlled tails. One must retain all these scales,
the bounded comparable partners, and the actual interval masks.

For a localized scale `n,m~N`, define the dimensionless signed sum
$$
S_{w,N}=\sum \mu(d)\mu(e)
\frac{D^2}{de}\frac{N}{\sqrt{nm}}
\frac{K_{T,w}(\log(m e^2/(n d^2)),nm)}{T},
$$
where the sum includes that scale's specified cutoffs and excludes equality.
Then the exact prefactor is
$$
\boxed{\mathcal O_{w,N}=\frac{2T}{N D^2}S_{w,N}.}
$$

The missing **aggregate** signed target is a fixed power saving
`|O_w(T,D)| << T^(1/3-delta)`. A stronger sufficient boxwise route, with a
positive reserve `lambda`, is
$$
|S_{w,N}|\ll N D^2 T^{-2/3-\delta-\lambda}.
$$
At `N~sqrt(T)`, `D~T^(5/6)`, this asks for
`T^(3/2-delta-lambda)`. It is not a necessary bound for each box:
cancellation between boxes is allowed in the aggregate target.

For `D=T^alpha`, `|alpha-5/6|<=rho`, the diagonal is at most
`T^(1/6+rho) log T`. Keep `delta+rho<1/6`, with positive room for all intended
losses. A sufficient allocation can impose `delta+rho+lambda<1/6`.
The bound must cover a fixed open neighborhood, all contributing scales,
and the masks required by the actual application. A full sharp-shell result
uses a smooth majorant on a larger high shell or a genuine overlapping smooth
cover; a smooth weight confined strictly inside `(T,2T)` cannot by itself
dominate the full sharp interval.

## 6. A genuine obstruction to a completely unsigned majorant

For a suitable fixed small constant, choose `N~sqrt(T)` and consider the
actual integer-entry cloud
$$
(n,d)\longmapsto \log(nd^2),\qquad n\asymp N,\ d\asymp D.
$$
It has order `ND` entries in a bounded logarithmic interval. Partition into
`O(T)` bins of sufficiently small width `c/T`. Cauchy–Schwarz gives at least
order `(ND)^2/T` ordered same-bin pairs before equality subtraction.
The coprime collision parametrization bounds exact equalities by `O(ND)`.
At the critical relation `ND/T` grows like `T^(1/3)`, so the remaining
nonzero near-pair count satisfies
$$
\boxed{\#\text{near pairs}\gg T^{5/3}.}
$$
This is a lower bound for an actual point cloud, not a merely saturable scalar
upper-bound model. It is **not** an asymptotic pair-count formula.

In this small-product region `W` is positive because `W(x)->1` as `x->0`;
small logarithmic phase also gives a positive real part of the kernel.
Thus the resulting unsigned counting majorant already has weighted cost
`T^(1/2)`. Relative to the stronger normalized box target it would have to
retain cancellation of order `T^(1/6+delta+lambda)`.

This concerns the specified majorant with bounded arithmetic coefficients
replaced by their absolute majorants. It is not a lower bound for the signed
off-diagonal or for `I_w`, and it does not exclude other cancellation methods.
Global nonnegativity of `W` is neither true nor used.

## 7. What this leaves on the strike map

- **Controlled operator:** dualize a sufficiently long coefficient-one factor,
  keep the moving interval maximal estimate, and pay sharp unsmoothing.
- **Controlled operator:** extract the full signed diagonal through a positive
  gcd/Jordan Gram coefficient with the correct mask limitations.
- **Uncontrolled arithmetic input:** a neighborhood-uniform saving for the
  whole sharp residual, or the appropriately aggregated signed off-diagonal.
- **Still required for any variance extension:** all tail blocks and heights,
  all required masks, low/far-frequency regions, small-divisor cutoffs,
  endpoint squares, recombination, and centering.

Neither a regrouping into Type II lengths nor another length-range comparison
with a published theorem discharges that input. The inspections conducted in
this run did not justify such a saving. The current `4/7-epsilon` variance
transfer has therefore **not been extended**. Its separate Mellin interface
also yields no new zero exclusion at this exponent.

The independent audits and their qualifications are recorded in
`REVIEW_STATUS.json` and the two mathematical verdict files. Finite checks
verify algebra and accounting; illustrative floating-point phase/weight
values are not proof of an analytic estimate. The DLMF formula used in the
Type I audit was read from archived formula-preserving material after a
fresh retrieval returned 403. No successful fresh DLMF retrieval is claimed.
No human peer review, formal kernel check, or novelty assessment is asserted.

## Sources

[3] https://arxiv.org/html/2006.04060v2
[6] https://dlmf.nist.gov/25.9
[7] https://arxiv.org/pdf/1411.7764v1

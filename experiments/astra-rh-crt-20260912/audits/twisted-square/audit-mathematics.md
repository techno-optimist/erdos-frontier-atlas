# Sparse-square mixed second moment: sourced transfer audit

## Outcome and scope

**No fixed saving below \(T^{1/3+o(1)}\) is justified by the published twisted-second-moment or mollifier theorems inspected here.** This is a failure to certify a transfer, not an impossibility theorem for the actual integral. The useful positive result is an explicit localized diagonal/off-diagonal interface, including a proof that the full arithmetic diagonal has scale

\[
\boxed{\mathcal D_w(T,D)\asymp_w \frac{T\log T}{D}}
\]

for the complete Möbius block. In particular it is \(T^{1/6+o(1)}\) at \(D=T^{5/6}\), not an obstruction at \(T^{1/3}\). The missing estimate is cancellation in a precisely specified **signed, oscillatory off-diagonal**, uniformly in a neighborhood of this length-height relation. No new squarefree-variance range, RH consequence, or novelty claim is made.

This audit takes as its baseline the supplied `GM_TRANSFER.md` and earlier second audit, copied without modification under `baseline/` and pinned in `baseline-provenance.json`. The original consolidated baseline is

`<repo>/experiments/astra-rh-crt-20260912/GM_TRANSFER.md`.

Its \(4/7\) ceiling is only the ceiling of its tested sufficient system. Its legitimate weighted Mellin reduction for finite divisor blocks is retained. This audit does not replace it with a formal divergent transform or silently strengthen a bound-method ceiling into an arithmetic lower bound.

The analytic inputs below are read from primary texts, not reconstructed from remembered admissible lengths. Their proofs are not formally verified here. The diagonal analysis and interface deductions are the calculations of this audit; exact finite algebra checks are supporting checks, not evidence for an unproved moment estimate.

## 1. The object, normalizations, and the target neighborhood

Write

\[
 M_D(1+2it)=\sum_{D\le d<2D}\frac{\mu(d)}{d}\,(d^2)^{-it},
 \qquad I_D(T)=\int_T^{2T}|\zeta(1/2+it)M_D(1+2it)|^2dt.
\]

There are two different, legitimate length conventions, applicable to different theorems:

* For a theorem about **the polynomial alone**, change variables \(u=2t\). Its integer length is \(D\), and its time interval has length \(2T\). In particular,
  \[
  \int_{cT}^{CT}|M_D(1+2it)|^2dt\ll (T+D)\sum_{d\sim D}\frac{\mu(d)^2}{d^2}\ll T/D+1.
  \tag{1.1}
  \]
  This is the ordinary mean-value theorem, also the \(q=1\) case of the mean-value input recorded by GMRR after rescaling time.[25]
* For the **standard zeta twisted second moment**, both factors must use the same \(t\). Set
  \[
  A(s)=\sum_{k\le 4D^2}\frac{a_k}{k^s},\qquad
  a_{d^2}=\mu(d)\,1_{D\le d<2D},\quad a_k=0\text{ otherwise}.
  \tag{1.2}
  \]
  Then \(A(1/2+it)=M_D(1+2it)\). The index length is \(L\asymp D^2\), while the number of nonzero coefficients is \(\asymp D\). We have \(|a_k|\le1\), \(\sum|a_k|^2\asymp D\), and \(\sum|a_k|^2/k\asymp D^{-1}\). Sparsity is not permission to replace \(L\) by \(D\) in a stated length hypothesis.

Changing \(u=2t\) in the *mixed* integral instead produces \(\zeta(1/2+iu/2)\), not \(\zeta(1/2+iu)\). An ordinary common-frequency twisted-moment theorem cannot be invoked on the resulting expression without a new theorem handling the two slopes.

The supplied GM scalar bound gives, on a high shell and with aggregate subpowers,

\[
 I_D(T)\ll T^{o(1)}\left(T/D+T^{1/3}+T^{1/2}D^{-1/5}+TD^{-4/5}\right).
 \tag{1.3}
\]

At \(D=T^{5/6}\) the last three terms are all \(T^{1/3}\); the first is \(T^{1/6}\). When \(H=T^{4/3}\), multiplication by \(H/T=T^{1/3}\) makes \(T^{1/3}\) cost \(T^{2/3}=\sqrt H\). A bound \(I_D(T)\ll T^{1/3-\eta}\), with fixed \(\eta>0\), would instead cost \(\sqrt H\,T^{-\eta}\) at this cell.

An appropriate local target is: for some fixed \(\eta,\rho>0\), prove this saving uniformly for

\[
 T^{5/6-\rho}\le D\le T^{5/6+\rho},\qquad T\ge T_0,
 \tag{1.4}
\]

with constants uniform for the bounded family of shell cutoffs used below and the fixed interval truncations of the Möbius block needed by the variance decomposition. A result only on the curve \(D=T^{5/6}\), only for a sequence of \(T\)'s, or only for one taper does not establish the required transfer. Arbitrary complex coefficients need not be allowed by a future Möbius-specific improvement, but the actual endpoint masks cannot simply be ignored.

## 2. A high-height approximate functional equation with a small paid error

Fix a real nonnegative \(w\in C_c^\infty((c,C))\), where \(0<c<C<\infty\) are constants independent of \(T,D\). Work with

\[
 I_w(T,D)=\int_0^\infty w(t/T)|\zeta(1/2+it)M_D(1+2it)|^2dt.
\]

One may take a fixed smooth majorant of \(1_{[1,2]}\) supported, for example, in \((1/2,3)\). Alternatively finitely many rescaled smooth windows supported in \([1,2]\) cover the requested sharp shell. Thus estimates uniform for these weights imply the sharp-shell upper bound; there is no need for a shrinking transition whose derivatives introduce an uncharged power loss.

Choose explicitly

\[
 G(z)=(1-4z^2)e^{z^2},\qquad
 W(x)=\frac1{2\pi i}\int_{(2)}G(z)x^{-z}\frac{dz}{z}.
 \tag{2.1}
\]

This is even in \(z\), real under conjugation, has \(G(0)=1\), \(G(1/2)=0\), and rapid vertical decay. The AFE used in BCR, Lemma 1, with its cited Li–Radziwill proof, gives uniformly on high shells

\[
 |\zeta(1/2+it)|^2
 =2\sum_{n,m\ge1}\frac{1}{\sqrt{nm}}
       (n/m)^{-it}W(2\pi nm/t)+O_\varepsilon(T^{-2/3+\varepsilon}).
 \tag{2.2}
\]

The sign of the phase is changed from the source by interchanging the two summation variables. BCR states \(O(T^{-2/3})\); the harmless \(T^\varepsilon\) here conservatively pays all logarithmic/subconvexity losses. The gamma-factor version is also available; the source proves the displayed simplification by Stirling on a near-central contour, not by a termwise crude approximation on the whole double series.[7][21]

The decisive normalization of the AFE error is

\[
 E_{\rm AFE}\ll_{w,\varepsilon}
 T^{-2/3+\varepsilon}\int_{cT}^{CT}|M_D(1+2it)|^2dt
 \ll_{w,\varepsilon}T^{-2/3+\varepsilon}(T/D+1).
 \tag{2.3}
\]

At the critical cell this is \(T^{-1/2+\varepsilon}\). Thus the \(T^{1/3+\varepsilon}\) AFE-error term appearing in the generic BCR theorem is **not** an intrinsic floor here: it comes from a different, generic treatment of the multiplier. Our correctly normalized error is already negligible.

The sum may be restricted to \(nm\le T^{1+\varepsilon}\) at an arbitrarily small negative-power cost by rapid decay of \(W\), with the loss parameters chosen first. Keep \(t\asymp T\) throughout. Do not put a fixed length-\(\sqrt T\) zeta polynomial into an integral through \(t=0\): its artificial coherent peak is not a zeta peak. A majorant for the **actual** nonnegative mixed integrand over a larger interval is legitimate, but an AFE valid only at high height may not be extended to low height by that observation.

Using an AFE for \(|\zeta|^2\), rather than retaining just one half of a single-zeta AFE, also avoids silently dropping the dual half or its cross terms. In the near-collision range below, \(n\) and \(m\) are comparable and individually at most about \(\sqrt T\); the product AFE is consistent with, not a way around, the usual \(\sqrt T\) zeta-factor length.

## 3. Exact signed interface and the full arithmetic diagonal

Define

\[
 K_{T,w}(n,m;d,e)=\int_0^\infty w(t/T)W(2\pi nm/t)
     e^{-it\log(nd^2/(me^2))}\,dt.
 \tag{3.1}
\]

Then (up to the paid error (2.3))

\[
 \begin{split}
 I_w(T,D)&=\mathcal D_w(T,D)+\mathcal O_w(T,D)+E_{\rm AFE},\\
 \mathcal D_w&=2\sum_{d,e\sim D}\frac{\mu(d)\mu(e)}{de}
       \sum_{nd^2=me^2}\frac{K_{T,w}(n,m;d,e)}{\sqrt{nm}},\\
 \mathcal O_w&=2\sum_{d,e\sim D}\frac{\mu(d)\mu(e)}{de}
       \sum_{nd^2\ne me^2}\frac{K_{T,w}(n,m;d,e)}{\sqrt{nm}}.
 \end{split}
 \tag{3.2}
\]

Both sums are real after pairing \((n,d)\) with \((m,e)\). The off-diagonal is a signed sum, not a count of solutions and not a nonnegative error.

### 3.1 Collision parametrization

Let \(g=(d,e)\), \(d=ga\), \(e=gb\), \((a,b)=1\). Then

\[
 nd^2=me^2\quad\Longleftrightarrow\quad n=b^2\ell,\ m=a^2\ell
 \quad(\ell\ge1).
\]

Consequently

\[
 \mathcal D_w
 =2\sum_{\substack{(a,b)=1\\ga,gb\in[D,2D)}}
 \frac{\mu(ga)\mu(gb)}{g^2a^2b^2}
 \int_0^\infty w(t/T)\sum_{\ell\ge1}\frac1\ell
 W\!\left(\frac{2\pi\ell^2a^2b^2}{t}\right)dt.
 \tag{3.3}
\]

In particular, \(d=e,n=m\) is **not** the entire diagonal. Exact collisions with distinct \(d,e\) have Möbius signs and must be included before inferring its scale.

### 3.2 A uniform absolute gcd estimate

For every fixed \(0\le\sigma<1/4\),

\[
 \sum_{d,e\sim D}\frac{(d,e)^2}{d^2e^2}
 \left(\frac{de}{(d,e)^2}\right)^{2\sigma}\ll_\sigma D^{-1}.
 \tag{3.4}
\]

Proof: in (3.3), \(a/b\in(1/2,2)\). Put \(\max(a,b)\asymp R\) dyadically. There are \(O(R^2)\) pairs, and their allowed \(g\)'s have \(\sum g^{-2}\ll R/D\), including the possible \(g\asymp1\) edge. The contribution is at most

\[
 O_\sigma\big(D^{-1}R^{-1+4\sigma}\big).
\]

The dyadic geometric series converges for \(4\sigma<1\). The same argument gives

\[
 \sum_{d,e\sim D}\frac{(d,e)^2}{d^2e^2}
      \log\left(\frac{de}{(d,e)^2}\right)\ll D^{-1}.
 \tag{3.5}
\]

These bounds use no cancellation in \(\mu\). They are uniform for fixed masks and coefficients of modulus at most one as upper bounds.

### 3.3 Evaluate, rather than guess, the diagonal

For \(q\ge1\), contour shifting in the absolutely convergent Mellin expression gives

\[
 \begin{split}
 2\sum_{\ell\ge1}\frac1\ell W(2\pi\ell^2q^2/t)
 &=\frac{2}{2\pi i}\int_{(2)}
 \left(\frac{t}{2\pi q^2}\right)^z\zeta(1+2z)G(z)\frac{dz}{z}\\
 &=\log\frac{t}{2\pi q^2}+2\gamma
       +O_\sigma\big((q^2/t)^\sigma\big),\qquad 0<\sigma<1/4.
 \end{split}
 \tag{3.6}
\]

The second line is valid also for large \(q\); its error can then be large. What makes its sum useful is precisely (3.4). The only pole crossed is the double pole at zero, and evenness gives \(G'(0)=0\). No uniform replacement of the weight by 1 at large \(q\) has been made.

Set

\[
 Q_D=\sum_{d,e\sim D}\mu(d)\mu(e)\frac{(d,e)^2}{d^2e^2},\qquad
 L_D=\sum_{d,e\sim D}\mu(d)\mu(e)\frac{(d,e)^2}{d^2e^2}
                   \log\frac{de}{(d,e)^2}.
 \tag{3.7}
\]

Equations (3.3)–(3.6) prove

\[
 \boxed{\mathcal D_w
  =Q_D\int_0^\infty w(t/T)(\log(t/(2\pi))+2\gamma)dt
   -2L_D T\int_0^\infty w(u)du
   +O_{w,\sigma}(T^{1-\sigma}/D).}
 \tag{3.8}
\]

Here \(|L_D|\ll D^{-1}\). This has the same gcd-log expression as the formal specialization of the generic twisted-moment main term, but it has been proved directly for the diagonal without an out-of-range invocation of that theorem.

To show that \(Q_D\) really has order \(D^{-1}\), not merely an upper bound of that size, use the elementary identity

\[
 J_2(r)=r^2\prod_{p\mid r}(1-p^{-2}),\qquad
 (d,e)^2=\sum_{r\mid(d,e)}J_2(r).
\]

It implies the positive Gram representation

\[
 Q_D=\sum_{r<2D}J_2(r)
          \left(\sum_{\substack{d\sim D\\r\mid d}}\frac{\mu(d)}{d^2}\right)^2.
 \tag{3.9}
\]

For \(D\le r<2D\), the only multiple of \(r\) in the block is \(r\). Hence

\[
 Q_D\ge\sum_{r\sim D}\frac{\mu(r)^2J_2(r)}{r^4}
 \ge\zeta(2)^{-1}\sum_{r\sim D}\frac{\mu(r)^2}{r^2}\gg D^{-1}.
 \tag{3.10}
\]

The last bound follows from the elementary positive density of squarefree integers; one obtains \(\sum_{r\le x}\mu(r)^2=x/\zeta(2)+O(\sqrt x)\) by opening \(\mu(r)^2=\sum_{h^2\mid r}\mu(h)\) and summing. Combining (3.4) at \(\sigma=0\) with (3.10) proves \(Q_D\asymp D^{-1}\).

For fixed nonzero nonnegative \(w\), therefore,

\[
 \mathcal D_w=T\log T\,Q_D\int w+O_w(T/D)
       \asymp_w T\log T/D.
 \tag{3.11}
\]

This is not an asymptotic with a claimed new universal constant: \(Q_D\) is the explicit finite quadratic form. Its scale is proved, not inferred from independence or from the \(d=e\) subtotal. For an interval-truncated or tapered block the uniform upper bound remains \(O_w(T\log T/D)\); a positive lower bound of that size is asserted here only for the complete Möbius block.

Nor is (3.11) a lower bound for \(I_w\): the off-diagonal in (3.2) can be negative. It is a statement about this precise AFE decomposition.

## 4. The signed off-diagonal still needed

Repeated integration by parts, using the smooth high-shell weight, gives for arbitrary fixed \(A,B>0\)

\[
 K_{T,w}(n,m;d,e)\ll_{A,B,w}
 T(1+nm/T)^{-A}
 (1+T|\log(nd^2/(me^2))|)^{-B}.
 \tag{4.1}
\]

Thus, after negligible tails and dyadic decomposition, the relevant tuples have

\[
 n\asymp m\asymp N\le T^{1/2+\varepsilon},\quad d,e\asymp D,
 \quad 0<|nd^2-me^2|\ll T^{\varepsilon}\frac{ND^2}{T}.
 \tag{4.2}
\]

Comparability of \(n,m\) follows from the closeness of the products and \(d/e\in(1/2,2)\); it is not an extra assumption imposed on the AFE. Dyadic classes with ratios outside a fixed bounded range contribute negligibly. The kernel, not just its envelope (4.1), is the object to estimate.

For a symmetric smooth dyadic partition factor \(\Psi_N(n,m)\) in the comparable range, define the dimensionless signed sum

\[
 \mathcal R_N=\sum_{\substack{d,e\sim D\\nd^2\ne me^2}}
 \mu(d)\mu(e)\frac{D^2}{de}\frac{N}{\sqrt{nm}}
 \Psi_N(n,m)\frac{K_{T,w}(n,m;d,e)}{T}.
 \tag{4.3}
\]

Then

\[
 \mathcal O_w=2\sum_N\frac{T}{ND^2}\mathcal R_N+O(T^{-A}).
 \tag{4.4}
\]

One may group the bounded number of comparable dyadic pairs at each \(N\); all resulting weights have controlled derivatives. No factor \(T\), \(D^{-2}\), or \(N^{-1}\) is hidden in the definition.

For any \(0<\eta<1/6\), the critical-cell goal is equivalent, at the level of (3.2), to

\[
 \boxed{\mathcal O_w(T,T^{5/6})=O_w(T^{1/3-\eta}).}
 \tag{4.5}
\]

Indeed the diagonal and AFE error are smaller. Since \(I_w\ge0\), the negative part of \(\mathcal O_w\) is bounded by the diagonal plus the paid error, so asking for an absolute bound here does not create a hidden necessary negative-cancellation target.

A convenient stronger sufficient input, uniform for all contributing \(N\), is

\[
 |\mathcal R_N|\ll ND^2 T^{-2/3-\eta-\delta}
 \tag{4.6}
\]

with fixed \(\delta>0\) enough to pay all dyadic/subpower losses. A global estimate for the signed combination (4.4) could also suffice; we do **not** assert that every dyadic sum must separately satisfy (4.6).

At \(N\asymp\sqrt T\), \(D=T^{5/6}\), the exponent ledger is

| Quantity | Scale, ignoring allocated subpowers |
|---|---:|
| ordinary square index \(d^2\) | \(T^{5/3}\) |
| product index \(nd^2\) | \(T^{13/6}\) |
| number of pairs \((n,d)\) | \(T^{4/3}\) |
| near-collision gap \(ND^2/T\) | \(T^{7/6}\) |
| prefactor \(T/(ND^2)\) | \(T^{-7/6}\) |
| signed sum sufficient for \(T^{1/3-\eta}\) | \(T^{3/2-\eta}\) |
| signed sum corresponding to diagonal order \(T/D\) | \(T^{4/3+o(1)}\) |

So reaching the diagonal would be a much stronger achievement than required. The immediate goal needs a fixed saving beyond the current \(T^{1/3+o(1)}\), not a full asymptotic.

### 4.1 Why the unsigned route loses a real amount

There is an elementary diagnostic stronger than a vague appeal to sparsity. Take \(N=c_0\sqrt T\), with \(c_0>0\) a sufficiently small fixed constant, \(n\in[N,2N)\), and squarefree \(d\in[D,2D)\). There are \(\asymp ND\) such entries. Put their values \(nd^2\), all in an interval of length \(O(ND^2)\), into \(O(T)\) bins of width \(c_1ND^2/T\). Cauchy–Schwarz gives at least

\[
 \gg N^2D^2/T
 \tag{4.7}
\]

ordered pairs of entries in a common bin. Exact equalities contribute only \(O(ND)\): parameterize by \(g,a,b,\ell\), put \(a,b\asymp R\), and use \(O(R^2)\) choices, \(O(D/R)\) possible \(g\)'s and \(O(N/R^2)\) possible \(\ell\)'s; the dyadic sum is \(O(ND)\). At the critical cell (4.7) is \(T^{5/3}\), while \(ND=T^{4/3}\), so nonzero near-collisions dominate this count.

For \(c_0,c_1\) sufficiently small, \(W(2\pi nm/t)\) is close to 1 and the phase in (3.1) stays close to 1 throughout the shell for these pairs. Thus even the near-core sum formed by replacing \(\mu(d)\mu(e)K\) by its absolute value has size at least

\[
 \frac{T}{ND^2}\frac{N^2D^2}{T}\asymp N\asymp T^{1/2}.
 \tag{4.8}
\]

The target is \(T^{1/3-\eta}\). Relative to this positive near-core majorant, at least a factor \(T^{1/6+\eta}\) must be recovered through the actual signed/oscillatory combination. This is **not** a lower bound for the original integral, and does not rule out cancellation between the very close core and the more oscillatory surrounding terms. It explains precisely why counting near-collisions after deleting every sign and phase cannot certify the desired saving.

### 4.2 Neighborhood uniformity and losses

For \(D=T^\alpha\), \(|\alpha-5/6|\le\rho\), the diagonal bound is uniformly \(T^{1-\alpha}\log T\le T^{1/6+\rho}\log T\). The proposed off-diagonal target remains \(T^{1/3-\eta}\), and the normalized dyadic target is

\[
 |\mathcal R_N|\ll ND^2T^{-2/3-\eta-\delta}.
\]

A sufficient numerical separation is \(\rho+\eta+\delta<1/6\), with a separate aggregate allowance for logarithms in \(\delta\). For example, one can **hypothetically** request an off-diagonal bound with raw saving \(2\eta\), restrict \(\rho=\eta/100\), and spend total loss \(\eta/100\), leaving a saving larger than \(\eta\) for any fixed sufficiently small \(\eta\) such as \(1/100\). This is a loss budget, not an established bound.

Uniformity must also cover bounded shell-weight seminorms, comparable dyadic \(n,m\) classes, and the interval cutoffs in \(d\). The sharp full-block estimate alone does not automatically give every partial-block estimate by positivity, since the polynomial has signs. A finite divisor block has a valid weighted Mellin transform as in the baseline; its spectral weight still requires all relevant heights. A gain in (1.4) would have to be spliced with the other ranges and the small-divisor cutoff conditions before any improved variance exponent could be announced.

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

## 5. Theorem-by-theorem hypothesis audit

The following is a bounded literature audit, not an assertion that no unlocated paper or new argument could help. Primary TeX, primary/deposited PDFs, metadata, and exact locators are preserved in `primary/`, `retrieval.jsonl`, and `source-excerpts.md`.

### 5.1 Bettin–Chandee–Radziwill: the genuine 17/33 result

BCR is published in *J. reine angew. Math.* **729** (2017), 51–79. Its deposited journal PDF was checked as well as `1411.7764v1` source; Theorem 1 has the same displayed hypothesis and error in these copies.[19][7]

For a smooth cutoff supported in \([1,2]\), \(A(s)=\sum_{k\le L}a_k k^{-s}\), \(a_k\ll_\varepsilon k^\varepsilon\), \(L=T^\theta\), **Theorem 1 assumes**

\[
 \theta<17/33.
\]

It gives the standard gcd-log main term with error

\[
 O_\varepsilon\left(T^{3/20+\varepsilon}L^{33/20}
                       +T^{1/3+\varepsilon}\right).
 \tag{5.1}
\]

These are actual theorem hypotheses and errors, not only a historical summary.[7]

Our coefficients (1.2) pass the size condition, and zero-padding is allowed in this general coefficient class. But \(L\asymp D^2\) requires \(D\ll T^{17/66-\delta}\), whereas the proposed block has \(D=T^{5/6}\), \(L\asymp T^{5/3}\). Even the introductory \(\theta<1\) setup is exceeded. Thus the theorem cannot be applied to this block.

An **out-of-range formal substitution**, not a valid bound, puts \(T^{29/10}\) into the first error of (5.1). This underscores that the displayed error does not claim a small error for arbitrary sparse long supports. The \(T^{1/3}\) second error is not itself a no-go result: Section 2 already reduced its AFE source to \(T^{-1/2+\varepsilon}\) using the actual multiplier norm. A useful refinement must also revisit the off-diagonal, not just erase this one generic error.

The fact that the main term specializes to order \(T\log T/D\) does not make the error automatically that small. An error \(o(T)\), or an asymptotic suitable for an ordinary mollifier of mean-square size \(T\), is insufficient for an absolute target \(T^{1/3-\eta}\).

**Status:** exact coefficient normalization passes; support-length hypothesis fails; no fixed saving transfers. This is not a proof that a sparse refinement of BCR is impossible.

### 5.2 BCR product structure and the Watt-based 3/4 lead

BCR also supplies stronger results for restricted product shapes, so stopping after Theorem 1 would be incomplete. With ordinary-index polynomials of lengths \(L_1\ge L_2\), Theorem 3 has the error

\[
 T^\varepsilon\left(T^{1/2}L_1^{3/4}L_2
       +T^{1/2}L_1L_2^{1/2}+L_1^{7/4}L_2^{3/2}\right).
 \tag{5.2}
\]

Its favorable product-length range reaches exponents below \(3/5\) with suitable factor lengths; it is not a theorem for arbitrary products of unlimited total length.[7][19]

The especially promising **Theorem 4** is a moment with a zeta factor and **two additional polynomials**. Its hypotheses include

\[
 L_1\ll T^{1/2+\varepsilon}\text{ for every }\varepsilon>0,
 \qquad L_2\ll T^{1/4},
\]

\(\alpha_n=\psi(n)\) with \(\psi^{(j)}(x)\ll_j x^{-j}\), \(\beta_k\ll_\varepsilon k^\varepsilon\), and supports

\[
 \alpha_n:\ [L_1T^{-\xi_1},2L_1],\quad
 \beta_k:\ [L_2T^{-\xi_2},2L_2],\quad
 0\le\xi_1\le1/5,\quad0\le\xi_2\le1/16.
\]

The error is

\[
 O_\varepsilon\left(T^{1/2+\varepsilon}L_2^2
 +L_2L_1^{3/4}T^{3/8+\varepsilon}
 +T^{39/40+\xi_1/8+2\xi_2/5+\varepsilon}\right).
 \tag{5.3}
\]

This is the source of the advertised polynomial product length approaching \(T^{3/4}\), with the short arbitrary factor at most \(T^{1/4}\). The weaker \(L_2\ll T^{1/2-\varepsilon}\) wording in the following remark must not be used to discard the actual \(L_2\ll T^{1/4}\) hypothesis or the first term of (5.3).[7][19]

There are several distinct failures of a proposed direct transfer:

1. Taking the square-supported multiplier as the arbitrary factor would require \(D^2\ll T^{1/4}\), i.e. \(D\ll T^{1/8}\), not \(T^{5/6}\).
2. A polynomial smooth in the root variable \(d\) but supported at indices \(d^2\) is not \(\alpha_n=\psi(n)\) smooth in the ordinary index with derivative bounds \(x^{-j}\). Intervening zeros cannot be ignored.
3. If one calls the zeta AFE polynomial the smooth factor while also retaining the theorem's zeta factor, the moment has acquired an **extra zeta-sized factor**. The theorem treats \(|\zeta|^2|A|^2|B|^2\); replacing zeta in our original moment gives \(|P M_D|^2\), not that theorem's integrand. This is a change of object, not a harmless relabeling.
4. Opening \(\mu(d)\) by a factorization identity leaves squared indices in the factors; their ordinary-index product length is still about \(D^2\). No decomposition into the theorem's permitted smooth/short shape, with a controlled number of pieces and paid losses, has been supplied.

There is a minor source notation caveat: BCR's displayed introductory definition of \(J\), equation (1.5), omits the cutoff even though the theorem main terms and proof use it. This audit reads these as the intended smooth localized moments, not as a convergent unweighted integral over all real \(t\). None of the failures above depends on that typographical omission.[7][19]

**Status:** the 3/4 lead is real but its additional shape, length, and integrand hypotheses do not cover this mixed second moment. A new use of Watt's machinery is not ruled out.

### 5.3 Pratt–Robles: shifted moments, Feng coefficients, and Conrey coefficients

Pratt–Robles, *Perturbed moments and a longer mollifier for critical zeros of zeta*, is published in *Research in Number Theory* **4** (2018), article 9. The publisher page verifies the publication; the detailed statements read here are pinned `1706.04593v3`. The attempted publisher PDF returned the subscription HTML page, not a PDF, so no uninspected publisher-final equation is being substituted.[17][8]

The setup is a common-frequency zeta second moment, shifts \(\alpha,\beta\ll1/\log T\), a smooth \(\Phi\) supported in \([1,2]\) with \(\Phi^{(j)}\ll_j\log^jT\), and ordinary integer-index length \(L=T^\theta\), initially \(\theta<1\). The first main theorem distinguishes:[8]

| Coefficients | Error up to the stated arbitrary epsilon factors | Range giving a power saving relative to \(T\) |
|---|---|---|
| arbitrary \(a_k\ll k^\varepsilon\) | \(T^{3/20}L^{33/20}+L^{1/2}T^{1/2+\varepsilon}\) | \(\theta<17/33\) |
| \(\mu^2(k)(\mu*\Lambda^{*j})(k)f(k)\) | \(T^\varepsilon(L^{11/6}+L^{11/12}T^{1/2})\) | \(\theta<6/11\) |
| \(\mu(k)f(k)\) | \(T^\varepsilon(L^{7/4}+L^{7/8}T^{1/2})\) | \(\theta<4/7\) |

Here \(j\) is fixed and \(f(k)=P(\log(L/k)/\log L)\) with \(P\) a fixed polynomial. The paper also has bilinear versions for two different coefficient sequences and a product-polynomial version; the latter retains errors of the form (5.2).[8]

The arithmetic mismatch is particularly sharp: \(\mu(k)\), and also \(\mu^2(k)\), vanish at every square \(k=d^2>1\). Our nonzero coefficients are \(\mu(d)\) at exactly those squares. A “squarefree coefficient” theorem is not a “coefficient supported on squares” theorem. Setting \(k=d\) instead changes the frequency to \(d^{-it}\) and does not represent our object. Ordinary smooth logarithmic weights also do not encode an arbitrary sharp interval mask without a separately justified reduction.

Even disregarding that coefficient mismatch, the index length would still have to satisfy \(D^2<T^{4/7-\delta}\) for the Conrey case, not \(D=T^{5/6}\). The formal error at the latter length is dominated by \(T^{35/12+\varepsilon}\), again an out-of-range algebraic diagnostic, **not** an asserted estimate.

**Status:** neither the shifted result nor its special Möbius cases supplies the square-supported input; shape and ordinary-index length both fail. Small shift-uniformity is not length-uniformity near \(D=T^{5/6}\).

### 5.4 PRZZ's generalized mollifier theorem

Pratt–Robles–Zaharescu–Zeindler, *More than five-twelfths of the zeros of zeta are on the critical line*, has a published **Theorem 4.1**, checked in the publisher PDF (*Res. Math. Sci.* **7** (2020), article 2, pp. 21–22) and in `1802.10521v2`.[18][13]

Its ordinary-index polynomials have coefficients \(a_k,b_k\ll k^\varepsilon\), length \(L=T^\theta\), \(\theta<1\), small shifts, and the same logarithmically controlled smooth shell cutoff. The special coefficient families include fixed convolutions

\[
 (\mu*\Lambda_1^{*j_1}*\cdots*\Lambda_r^{*j_r})(k)
\]

with, or without, the \(\mu^2(k)\) restriction. Its relevant special-family errors are again

\[
 T^\varepsilon(L^{11/6}+L^{11/12}T^{1/2}),\qquad
 T^\varepsilon(L^{7/4}+L^{7/8}T^{1/2}),
\]

respectively, with the latter allowing the stated mollifier exponents below \(4/7\).[18][13]

Removing a squarefree restriction is not the same operation as restricting to perfect squares. No representation of our coefficient sequence by these prescribed fixed convolution families and allowed weights has been provided. Even such a representation would not change its ordinary index length \(D^2\). This important generalized result therefore does not repair the transfer.

### 5.5 Wu's more general Dirichlet-L mollifier result

Theorem 1 in the source `1802.09704v2` allows a primitive character of modulus \(q\) with **\(\log q=o(\log T)\)**, arbitrary coefficients for \(\theta<17/33\), and \(\theta<4/7\) for

\[
 a(k)=\mu(k)\big(\mathcal F_0+\mathcal F_1(\mathcal F_2*\mathcal F_3)\big)(k),
\]

with explicit smoothness/separability hypotheses on the \(\mathcal F_i\) (and a stated alternative short-support condition for one factor). Its displayed error is \(O(T^{1-\varepsilon_\theta})\).[9]

This does not make \(\mu(\sqrt{k})1_{k=\square}\) a permitted coefficient, nor replace \(D^2\) by \(D\). Also it is not a black-box bound for the large square moduli that might arise on the dual side of reciprocity: \(q\asymp D^2\) has \(\log q\asymp\log T\), contrary to the small-modulus condition. There is no transferred saving here.[9]

### 5.6 Khan reciprocity: a promising transformation, not an off-diagonal bound

Khan's *A reciprocity relation for the twisted second moment of the Riemann Zeta function* is recorded as a 2025 *Proceedings of the AMS* publication by NSF PAR, DOI `10.1090/proc/17003`. Its theorem was read in `2401.01057v1` and compared with the NSF-deposited manuscript, pp. 2–3.[24][11][27]

For **distinct odd primes** \(p,q\) and \(T>1\), Theorem 1 evaluates

\[
 \int_{\mathbb R}(p/q)^{it}|\zeta(1/2+it)|^2e^{-t^2/T^2}\,dt
\]

as an explicit main term of the form

\[
 \sqrt{\pi/(pq)}\,T
 \left(\log(T/(2\pi pq))+2\gamma+\tfrac12\Gamma'(1/2)/\Gamma(1/2)\right)
\]

**plus a dual moment**

\[
 \left(\frac{T}{2\pi}\right)^{1/2}\frac{p^{1/2}}{p-1}
 \sum_{\substack{\chi\bmod p\text{ primitive}\\\chi(-1)=1}}
 \chi(q)\int_{\mathbb R}\Gamma\!\left(\frac{1-2iu}{4}\right)
      \left(\frac{T}{2q}\right)^{iu}|L(1/2+iu,\chi)|^2du,
 \tag{5.4}
\]

with error

\[
 O_\varepsilon\left((pqT)^\varepsilon
       \left(\sqrt{q/p}+\sqrt{p/q}\right)\right).
 \tag{5.5}
\]

The rapidly decaying gamma factor shortens the dual archimedean integration. It does **not** eliminate the dual family or bound its twisted character average. The source explicitly emphasizes asymptotics for a **difference** between moments in a wider range than an asymptotic for the original moment alone.[11][27]

For our terms the reduced twist is \((a^2/b^2)^{it}\), with \((a,b)=1\), not \((p/q)^{it}\) for distinct odd primes. Even taking \(d,e\) prime does not fix this: the twists are their squares. Khan says the restriction to primes is not serious for the method, but the composite-modulus character orthogonality becomes more complicated. That is an invitation to carry out an extension, not the displayed prime theorem covering all the needed square twists as written.[11][27]

This lead deserves more than dismissal by length:

* If a correct composite-square extension retained an error like (5.5), the reduced ratio \(a/b\asymp1\) and \(\sum_{d,e\sim D}1/(de)\ll1\) would make its summed weighted errors \(T^{o(1)}\), which is small enough. There is no asserted polynomial-length restriction here comparable to BCR's \(17/33\).
* The missing step would be a bound of size \(T^{1/3-\eta}\) for the resulting **Möbius-weighted sum of composite-square-modulus dual moments**, with all divisor/primitive-character correction terms and cutoff uniformity accounted for. The theorem does not supply that estimate.
* The centered-at-zero Gaussian is not by itself a fatal issue for an upper bound on the **actual** nonnegative integral: it majorizes a high shell up to a fixed constant. What is forbidden is inserting a fixed high-height AFE through its low-height part. The exact reciprocity identity is not that invalid AFE extension. If one needs specifically localized identities, their transforms must be recomputed rather than merely translating \(t\) and pretending zeta is translation-invariant.

**Status:** potentially useful analytic reorganization; no current transferred saving. The precise missing hypotheses/output are composite-square twists, their corrections, and control of the signed dual-family sum—not simply an inadmissible remembered length.

### 5.7 The high-height short-interval reciprocity lead

Tang's `2608.14852v1`, *Reciprocity for the Short Twisted Second Moment of the Riemann Zeta Function*, explicitly considers a Gaussian centered at height \(T\), with width \(U=T^\delta\), \(1/2<\delta<1\). Its Theorem 1 again assumes distinct odd primes \(p,q\), has a dual Dirichlet-L moment with Mellin-transform support about \(T/U\), and error

\[
 O_\varepsilon\left((T/U)(pqT)^\varepsilon
        (\sqrt{p/q}+\sqrt{q/p})\right).
 \tag{5.6}
\]

It is included as a recent version-pinned arXiv lead, not silently promoted into a published theorem input. The source describes \(U^2/\max(p,q)>T^{1+\varepsilon}\) as the condition for main-term dominance over the error, **not** an extra validity hypothesis of the reciprocity identity.[12]

This is well aligned with the high-height caution. Nevertheless the square twists and unestimated dual moment remain. If one informally tested individual main-term dominance with \(p,q\asymp D^2\), \(D=T^{5/6}\), it would ask for \(U\gg T^{4/3}\), outside the short-interval setup. This is not a claim that an averaged use of the identity is impossible: weighted summation and cancellation could be much better than individual main-term dominance, and large common divisors have smaller reduced twists.

### 5.8 The Atkinson-type formula with a length-dependent constant

Yu Jinbo's `2312.10614v2`, Theorems 1.1–1.2, concerns

\[
 \int_T^{2T}|\zeta(\sigma+it)A(\sigma+it)|^2dt,
 \qquad 1/4<\sigma<1/2,
\]

and provides explicit oscillatory \(\Sigma_1,\Sigma_2\) terms with a remainder

\[
 R(T,2T,A)\ll_M T^{1-2\sigma}\log T,
\]

where \(M\) is the polynomial length. The endpoint \(\sigma=1/2\) is excluded and the implicit constant is explicitly allowed to depend on \(M\).[10]

Consequently one cannot take \(M\asymp D^2\asymp T^{5/3}\), suppress this dependence, then pass to \(\sigma=1/2\) and announce a small remainder. Even apart from these issues, the retained \(\Sigma_i\)'s are the oscillatory work still to be done, not proved negligible errors. This result gives no uniform critical-line saving for our moment.

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

## Sources

[7] https://arxiv.org/src/1411.7764v1 — bcr-v1
[8] https://arxiv.org/src/1706.04593v3 — pr-v3
[9] https://arxiv.org/src/1802.09704v2 — wu-v2
[10] https://arxiv.org/src/2312.10614v2 — yu-v2
[11] https://arxiv.org/src/2401.01057v1 — khan-v1
[12] https://arxiv.org/src/2608.14852v1 — tang-v1
[13] https://arxiv.org/src/1802.10521v2 — przz-v2
[17] https://doi.org/10.1007/s40993-018-0103-4 — pr-publisher
[18] https://link.springer.com/content/pdf/10.1007/s40687-019-0199-8.pdf — przz-publisher
[19] https://unige.iris.cineca.it/bitstream/11567/896399/3/bettin2015.pdf — bcr-deposited
[21] https://arxiv.org/src/1208.2684v1 — lr-v1
[23] https://arxiv.org/abs/2606.27323 — amplified-abs
[24] https://par.nsf.gov/biblio/10585520-reciprocity-relation-twisted-second-moment-riemann-zeta-function — khan-nsf
[25] https://arxiv.org/src/2006.04060v2 — gmrr-v2
[26] https://arxiv.org/abs/2607.00282 — gl23-abs
[27] https://par.nsf.gov/servlets/purl/10585520 — khan-final
[28] https://arxiv.org/src/2606.27323v2 — amplified-v2

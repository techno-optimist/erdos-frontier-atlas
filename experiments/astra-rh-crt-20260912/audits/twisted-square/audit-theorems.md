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


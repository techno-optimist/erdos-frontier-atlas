# Möbius factorization at the critical squarefree mixed moment

## Verdict and scope

**No fixed power saving for the complete Möbius mixed moment is established by this audit.** A fixed-order, exact Möbius identity does give a genuine power-saving treatment of its long-smooth-factor Type I terms. The remaining Type II expression still requires a joint estimate with zeta that is not supplied by the published estimates matched here. This is a limitation of the deductions in this report, not a lower bound, an optimality result, or a claim that such an estimate is unavailable anywhere in the literature.

Write
\[
 I_D(T)=\int_T^{2T}|\zeta(\tfrac12+it)M_D(1+2it)|^2dt,
 \qquad M_D(s)=\sum_{D\le d<2D}\mu(d)d^{-s}.
\]
The primary focus is \(D=T^{5/6}\), with fixed-factor changes in endpoints harmless. The established baseline is \(I_D(T)\ll T^{1/3+o(1)}\), not a fixed saving below that exponent. The baseline uses GM Theorem 1.1 and the standard estimates in GMRR; it does not use cancellation of Möbius coefficients.[1][2]

The positive, partial result below is this **derived Type I lemma**:
\[
 \boxed{\int_T^{2T}|\zeta(\tfrac12+it)
 B(1+i(2t+u))C(1+i(2t+u))|^2dt
 \ll_\epsilon T^\epsilon
 \left(\frac{T}{D}+\frac{T^{3/2}}{C_0^2}+1\right).}\tag{TI}
\]
Here \(B(s)=\sum_{r\asymp R}\beta_r r^{-s}\), \(|\beta_r|\le\tau_2(r)\); \(C(s)=\sum_{C_0\le c<C_1}c^{-s}\), \(C_1\le2C_0\); \(RC_0\asymp D\), \(C_0\ge T^{7/12+\eta}\), and \(|u|\le T^{1/2+\eta}\), for fixed \(0<\eta<1/48\). Intervals for \(r\) can have any fixed bounded multiplicative width. The constant is uniform in these intervals, in the actual truncated Möbius convolutions, and in \(u\). The proof in §4 uses the classical sharp approximate functional equation, the ordinary polynomial mean-value theorem, and the zeta fourth moment, with all arguments matched explicitly.[1][6]

At \(D=T^{5/6}\), (TI) gives \(T^{1/3-2\eta+\epsilon}+T^{1/6+\epsilon}+T^\epsilon\). After **one aggregate** loss allocation, the entire Type I contribution is \(\ll_\eta T^{1/3-\eta}\). For example \(\eta=1/120\) gives the proved partial exponent \(13/40<1/3\). It is not a bound for the full \(I_D(T)\).

No repository was edited, staged, committed, or published. Outside the supplied repository, the default-profile `proof-transfer-audit` and `pdf` procedural skills were updated with the reusable frequency/cutoff audit lessons and the isolated PDF-rendering dependency fix. The supplied audits and the subsequently supplied `GM_TRANSFER.md` were read as baseline material, not as new analytic hypotheses. This is a bounded informal mathematical audit; no RH, novelty, or new variance-range claim is made.

## 1. Exact truncated Möbius identity — no missing remainder

Fix an **integer \(k\ge1\)** and a **real \(U\ge1\)**. Set
\[
 A_U(s)=\sum_{n\le U}\mu(n)n^{-s},\qquad E_U(s)=1-\zeta(s)A_U(s).
\]
Initially work in \(\Re s>1\), where all relevant Dirichlet series converge absolutely. For \(n\le U\), the coefficient of \(n^{-s}\) in \(\zeta A_U\) is the complete divisor sum \(\sum_{d\mid n}\mu(d)=\mathbf1_{n=1}\). Consequently
\[
 E_U(s)=\sum_{n>U}e_U(n)n^{-s}.
\]
Every product contributing to \(E_U(s)^k\) has index at least \((\lfloor U\rfloor+1)^k>U^k\). Multiplication by \(1/\zeta(s)=\sum\mu(n)n^{-s}\) cannot introduce a smaller index. The binomial identity therefore gives
\[
 \frac1{\zeta(s)}=
 \sum_{j=1}^k(-1)^{j-1}\binom{k}{j}
       \zeta(s)^{j-1}A_U(s)^j
 +\frac{E_U(s)^k}{\zeta(s)}.\tag{1}
\]
In particular, for every integer \(n\le U^k\),
\[
 \boxed{\mu(n)=\sum_{j=1}^k(-1)^{j-1}\binom{k}{j}
 \sum_{\substack{a_1\cdots a_jb_1\cdots b_{j-1}=n\\a_i\le U}}
 \mu(a_1)\cdots\mu(a_j).}\tag{2}
\]
The \(b_i\) have coefficient **1**, not Möbius or prime coefficients. Empty products have their usual value.

Choose \(U=(2D)^{1/k}\), or any larger cutoff satisfying \(U^k\ge2D\). Then (2) holds throughout the entire requested half-open block \([D,2D)\). One must not take \(U^k=D\) and silently use the formula up to \(2D\). Nor is (1), with its remainder removed, an analytic identity for all \(s\) or all coefficients. After coefficient extraction, the resulting **finite** polynomial identity is valid at \(s=1+2it\) without any assertion about convergence of \(\sum\mu(n)n^{-1-2it}\).

This reciprocal-zeta identity is proved here. Its binomial/support mechanism is the same one as Heath-Brown's published Lemma 1 and equation (7), but **his displayed equation (6) is a logarithmic-derivative identity**, not (1) verbatim. The original page 1367 was inspected, including a rendered page to check the OCR-damaged formula and the condition \(X^k\ge x\).[7]

### Fixed \(k\) ledger

For the term indexed by \(j\):

| Item | Exact information |
|---|---|
| Möbius variables | \(j\), each \(a_i\le U\) |
| Smooth variables | \(j-1\), each with coefficient 1 |
| Product restriction | \(D\le\prod a_i\prod b_i<2D\) |
| Dyadic boxes | At most \(O_k((\log(2D))^{2j-1})\) |
| Grouped coefficient bound | At most \(\tau_{2j-1}(n)\) before a fixed binomial constant |
| Fixed coefficient multiplier | \(\binom{k}{j}\) |
| Squared-norm summation | Cauchy over all boxes costs the square of their number when using a maximum |
| Allowable power notation | \(\tau_m(n)\ll_{m,\epsilon}n^\epsilon\) for **fixed** \(m\); aggregate losses must be allocated after all applications |

No \(k=k(T)\) is used. Allowing it to grow would require new accounting for \(2^k\), the number of boxes, divisor-function constants and norms, and all moment powers. The notation \(T^{o(1)}\) does not pay those costs automatically.

## 2. A complete Type I / Type II split with \(k=2\)

Take
\[
 U=(2D)^{1/2}\asymp T^{5/12}.
\]
For \(D>2\), \(U<D\), so the \(2A_U\) term in \(2A_U-\zeta A_U^2\) has no coefficients in the block. Thus, **exactly**,
\[
 M_D(s)=-\sum_{\substack{a,b\le U\\D\le abc<2D}}
               \frac{\mu(a)\mu(b)}{(abc)^s}.\tag{3}
\]
There are two short Möbius variables and one free, coefficient-1 variable. Dyadic decomposition gives \(a\asymp A\), \(b\asymp B\), \(c\asymp C_0\), with
\[
 A,B\ll T^{5/12},\qquad ABC_0\asymp D=T^{5/6}.
\]
Singleton ranges, especially \(a=1,b=1,c=1\), must be retained.

Fix \(0<\eta<1/48\) and put \(C_* =T^{7/12+\eta}\).

* **Type I:** \(c\ge C_*\). Split into dyadic intervals, allowing the first interval to be truncated at \(C_*\). Group \(r=ab\). The coefficients are
  \(\beta_r=\sum_{ab=r,\ a\in I_A,b\in I_B,\ a,b\le U}\mu(a)\mu(b)\),
  hence \(|\beta_r|\le\tau_2(r)\), with \(R=AB\asymp D/C_0\).
* **Type II:** \(c<C_*\). All individual factors have size at most \(T^{7/12+\eta}\), up to fixed constants. Group the variable with largest dyadic length against the product of the other two, and order the resulting group lengths \(P\le Q\). Then
  \[
   \boxed{PQ\asymp T^{5/6},\quad
   T^{1/4-\eta}\ll P\ll T^{5/12},\quad
   T^{5/12}\ll Q\ll T^{7/12+\eta}.}\tag{4}
  \]
  Indeed, the largest individual logarithmic length lies between \(5/18\) and \(7/12+\eta\). Its complementary length is at least \(1/4-\eta\); the smaller of the two groups is at most \(5/12\). Since \(5/18>1/4-\eta\), both groups meet the lower bound.

The Type II coefficients are not arbitrary coefficients invented for a reduction: they are an interval-restricted \(\mu\) or 1, paired with an interval-restricted convolution \(\mu*\mu\) or \(\mu*1\), possibly with the two groups exchanged. The two-group notation does not assert cancellation of either coefficient sequence.

### Sharp product cutoff: a paid separation step

The condition \(D\le abc<2D\) couples the variables. It cannot just be dropped when estimating a complex sum. Here is one rigorous separation sufficient for this audit.

Let \(\Delta=T^{-1/2}\), and choose a smooth \(h_\Delta\), supported **inside** \([1,2]\), equal to 1 on \([1+\Delta,2-\Delta]\), between 0 and 1, with transition derivatives \(O_j(\Delta^{-j})\). Replacing the sharp product indicator by \(h_\Delta(abc/D)\) has coefficient-wise absolute error at most
\[
 \sum_{\substack{n\text{ in the two boundary strips}}}
 \frac{\tau_3(n)}n\ll_\epsilon T^\epsilon(\Delta+D^{-1}).
\]
Its squared mixed norm is therefore \(\ll T^\epsilon\), by \(\int_T^{2T}|\zeta|^2\ll T\log^2T\), derived from the fourth moment. This estimate also holds for either Type subfamily. Keeping the smooth support inside \([1,2]\) is important: no coefficients beyond \(U^2=2D\) are silently introduced.[1]

With the Mellin/Fourier convention
\[
 h_\Delta(y)=\frac1{2\pi}\int_{\mathbb R}\widehat h_\Delta(u)y^{-iu}\,du,
\]
its transform has \(L^1\)-norm \(O(\log T)\). The tail beyond \(|u|>T^{1/2+\eta}\) has arbitrarily large fixed power decay: repeated integration by parts gives a bound \(O_j((\Delta T^{1/2+\eta})^{1-j})\). Choose \(j\) large but fixed in terms of \(\eta\) and the required error. Absolute coefficient bounds dispose of that tail. Thus each box is an integral of a genuinely separated product at the **common shifted argument**
\[
 v=2t+u\asymp T,\qquad |u|\le T^{1/2+\eta}.
\]
Minkowski, or weighted Cauchy–Schwarz in \(u\), costs \(O(\log^2T)\) in the squared norm. There is no unbounded-height Perron contour hidden here.

## 3. Precisely matched analytic inputs

These are the positive inputs, in the exact forms used:

1. **Polynomial mean value.** For arbitrary fixed complex \(c_n\), supported on \(n\le N\),
   \[
   \int_{J}|\sum c_n n^{-it}|^2dt\ll (|J|+N)\sum|c_n|^2,
   \]
   for an interval \(J\) of length comparable to \(T\). This follows directly from GMRR Lemma 7 at \(q=1\), whose displayed statement is for \([-T,T]\); a translation is absorbed into unimodular coefficient factors. The use on powers of a polynomial requires writing out their convolution coefficients and bounding their \(\ell^2\) norm.[1]
2. **Zeta fourth moment and Weyl.** The displayed estimates in GMRR **Lemma 3** and **Lemma 5** are
   \[
   \int_{|t|\le T}|\zeta(\tfrac12+it)|^4dt\ll T\log^4T,
   \quad |\zeta(\tfrac12+it)|\ll |t|^{1/6}\log^2|t|\quad(|t|\ge2).
   \]
   We keep zeta at its original continuous argument \(t\), not at rescaled sampling points.[1]
3. **Sharp approximate functional equation.** For fixed \(0\le\sigma\le1\), \(x,y\ge1\), \(2\pi xy=v\),
   \[
   \zeta(\sigma+iv)=\sum_{n\le x}n^{-\sigma-iv}
   +\chi(\sigma+iv)\sum_{n\le y}n^{\sigma-1+iv}
   +O(x^{-\sigma})+O(y^{\sigma-1}v^{1/2-\sigma}).\tag{AFE}
   \]
   This is Titchmarsh (1986), (4.12.4), p. 79, reproduced with the hypotheses and exact formula in DLMF 25.9.1. The NIST MathML and TeX, not its math-stripped extraction, were inspected. This classical published reference is the one secondary/reference-work input; the other mathematical papers cited here are primary reading copies. At \(\sigma=1\), Stirling applied to the displayed gamma quotient for \(\chi\) gives \(|\chi(1+iv)|\asymp v^{-1/2}\).[6]
4. **GM Theorem 1.1.** For pointwise \(|b_n|\le1\) and 1-separated times,
   \[
   R\ll T^{o(1)}(N^2V^{-2}+N^{18/5}V^{-4}+TN^{12/5}V^{-4}).
   \]
   We use the pinned v2 statement, including arbitrary complex coefficients. Divisor-bounded coefficients must first be divided by their actual uniform upper bound. That division costs a subpower for fixed \(k\), not zero.[2]

Useful source locators in the archived copies: `gmrr.tex` lines 339–370, 392–403; `gm.tex` lines 68–79; `dlmf-25.9.html.txt` lines 35–66. No independent zeta first- or second-moment theorem is assumed; the second-moment upper bound used here follows from the stated fourth moment.

## 4. Proof of the Type I estimate and its length ledger

For a separated Type I box let
\[
 B_v=\sum_{r\asymp R}\frac{\beta_r}{r^{1+iv}},
 \quad C_v=\sum_{C_0\le c<C_1}c^{-1-iv},
 \quad R C_0\asymp D,
 \quad v=2t+u.
\]
Apply (AFE) at \(\sigma=1\) with \(x=C_0\) and \(x=C_1\), and subtract. Endpoint changes cost \(O(C_0^{-1})\). Both dual cutoffs are \(\asymp v/C_0\), and are \(\ge1\), since \(C_0\ll D=T^{5/6}\) and \(v\asymp T\). Thus
\[
 C_v=\chi(1+iv)\sum_{\ell\in J(v)}\ell^{iv}
       +O(C_0^{-1}+T^{-1/2}),\tag{5}
\]
up to an immaterial sign, where \(J(v)\) is an interval contained in a fixed range \(\ell\asymp L=T/C_0\). The interval may depend on \(t\). Since \(C_0>T^{1/2}\), the error is \(O(T^{-1/2})\). Multiplying by \(B_v\), whose absolute coefficient sum is \(T^{o(1)}\), and integrating against \(|\zeta|^2\), gives error \(\ll T^\epsilon\).[6][1]

**Phase bookkeeping.** The dual sum in (5) has the opposite sign of frequency. Only its modulus is needed:
\[
 \left|B_v\sum_{\ell\in J(v)}\ell^{iv}\right|
   =\left|B_v\sum_{\ell\in J(v)}\ell^{-iv}\right|,
\]
because the coefficient-1 dual sum is conjugated. This equality does **not** change zeta's argument, and does not assert equality of the two complex products. It permits the polynomial mean value on the product indexed by \(r\ell\).

For a fixed interval \(J\subseteq\{\ell\asymp L\}\), set
\[
 F_J(v)=B_v\sum_{\ell\in J}\ell^{-iv}.
\]
The polynomial \(F_J\) has integer index length \(P_0\asymp RL\), and coefficients bounded by \(T^\epsilon/R\). Its square has length \(O(P_0^2)\) and squared coefficient norm
\[
 \sum_m|[m^{-iv}]F_J(v)^2|^2
   \ll_\epsilon T^\epsilon\frac{L^2}{R^2}.\tag{6}
\]
For example, expand the coefficient using \(r_1r_2\ell_1\ell_2=m\); the number of representations is divisor-bounded, each weight is \(\ll T^\epsilon/R^2\), and there are \(O(R^2L^2)\) tuples. Hence mean value gives
\[
 \int_T^{2T}|F_J(2t+u)|^4dt
   \ll_\epsilon T^\epsilon(T+R^2L^2)\frac{L^2}{R^2}.\tag{7}
\]

### The moving dual interval is not silently frozen

The same bound, with logarithmic loss, holds for the supremum over intervals \(J\). Decompose any interval into \(O(\log L)\) canonical binary intervals. Fourth-power Cauchy costs \(O(\log^3L)\). At a fixed binary level the intervals are disjoint. In the coefficient-norm proof of (6), summing over all intervals of that level counts each ordered pair \((\ell_1,\ell_2)\) in at most one interval. Thus the **sum** of squared coefficient norms at that level is still bounded by the right side of (6). Sum over \(O(\log L)\) levels and apply mean value to each fixed polynomial. This proves the maximal version of (7) with at most \(O(\log^4L)\), not a loss of \(L\).

Now apply Cauchy–Schwarz with the continuous zeta fourth moment, and \(|\chi(1+iv)|^2\ll T^{-1}\):
\[
 \begin{aligned}
 \int_T^{2T}|\zeta B_v C_v|^2dt
 &\ll T^\epsilon+
 T^{-1}\left(\int_T^{2T}|\zeta|^4dt\right)^{1/2}
 \left(\int_T^{2T}\sup_J|F_J(2t+u)|^4dt\right)^{1/2}\\
 &\ll_\epsilon T^\epsilon
 \left(1+T^{-1/2}(T+R^2L^2)^{1/2}\frac LR\right)\\
 &\ll_\epsilon T^\epsilon
 \left(1+\frac LR+T^{-1/2}L^2\right)\\
 &\ll_\epsilon T^\epsilon
 \left(1+\frac TD+\frac{T^{3/2}}{C_0^2}\right).
 \end{aligned}\tag{8}
\]
This proves (TI). No Möbius cancellation theorem has been inserted into (6) or (7).

### Length-and-loss table at the endpoint

Write \(C_0=T^c\) and \(D=T^{5/6}\), ignoring fixed factors only.

| Object or contribution | Length/exponent |
|---|---|
| Original smooth factor | \(C_0=T^c\) |
| Grouped Möbius convolution | \(R=T^{5/6-c}\), coefficients \(\beta_r/r\) |
| Dual coefficient-1 sum | \(L=T^{1-c}\), coefficients 1 |
| Functional-equation amplitude | \(T^{-1/2}\), squared amplitude \(T^{-1}\) |
| Product used in the fourth moment | \(RL=T^{11/6-2c}\) |
| Square used in ordinary mean value | \((RL)^2=T^{11/3-4c}\) |
| Squared coefficient norm of that square | \(T^{o(1)}L^2/R^2\) |
| Diagonal-size part of (8) | \(T/D=T^{1/6}\) |
| Long-product mean-value loss | \(T^{3/2}/C_0^2=T^{3/2-2c}\) |
| Functional-equation and endpoint errors | \(T^{o(1)}\) in the mixed squared norm |
| At \(c\ge2/3\) | \(RL\le T^{1/2}\); (8) is \(T^{1/6+o(1)}\) |
| At \(c=7/12+\eta\) | \(T^{1/3-2\eta+o(1)}\) |
| At \(c=7/12\) | Only \(T^{1/3+o(1)}\); no strict saving from this bound |

For \(k=2\), a safe fixed-logarithm allowance is \((\log T)^{20}\): it exceeds the costs of the three variable dyadics and their squared-norm summation, Mellin separation, the maximal interval argument, and the zeta moments. All divisor-bound losses and logarithms together can be bounded by \(T^\eta\), by choosing their individual fixed loss parameters first, sufficiently small. The raw saving \(2\eta\) then leaves \(\eta\). Nothing is absorbed into a constant while depending on \(T\).

## 5. What remains: an exact joint Type II obligation

Define the actual residual, with the sharp cutoff and actual Möbius coefficients,
\[
 \mathcal R_{\rm II,D}(s)=
 \sum_{\substack{a,b\le(2D)^{1/2}\\c<C_*\\D\le abc<2D}}
       \mu(a)\mu(b)(abc)^{-s},
\]
and define \(\mathcal R_{\rm I,D}\) by the complementary condition \(c\ge C_*\). Then
\[
 M_D=-\mathcal R_{\rm I,D}-\mathcal R_{\rm II,D}
\]
is exact, and §4, including §2's cutoff repair, proves a fixed saving for \(\mathcal R_{\rm I,D}\).

The **exact remaining analytic obligation for this split** is therefore: for some fixed \(\delta>0\),
\[
 \boxed{\int_T^{2T}|\zeta(\tfrac12+it)
          \mathcal R_{\rm II,D}(1+2it)|^2dt
      \ll T^{1/3-\delta},\qquad D=T^{5/6}.}\tag{J-rem}
\]
Up to replacing a saving by the minimum of two savings, (J-rem) and a fixed saving for \(M_D\) are equivalent, by the triangle inequality in weighted \(L^2\) and the proved Type I saving. This is a statement about the **whole residual**, retaining cancellation between its boxes.

A stronger sufficient, termwise route would establish, uniformly for the actual coefficient pairs in §2 and the length range (4),
\[
 \int_T^{2T}|\zeta(\tfrac12+it)|^2
 \left|\sum_{p\asymp P}\frac{\alpha_p}{p^{1+i(2t+u)}}\right|^2
 \left|\sum_{q\asymp Q}\frac{\beta_q}{q^{1+i(2t+u)}}\right|^2dt
 \ll T^{1/3-\delta},\quad |u|\le T^{1/2+\eta},\tag{J-box}
\]
with enough uniform slack to pay the aggregate loss. Alternatively a suitable Mellin-weighted average in \(u\), rather than this supremum, would suffice. A theorem only for \(u=0\) cannot be used as (J-box) by moving \(t\): such a move also moves zeta. Neither (J-rem) nor (J-box) is proved here.

### A concrete balanced member which is not discharged

Let \(L=\sqrt D=T^{5/12}\) and
\[
 A_L(s)=\sum_{L\le a<\sqrt2L}\mu(a)a^{-s}.
\]
The rectangle \(a,b\in[L,\sqrt2L)\), \(c=1\), lies entirely in \(D\le ab<2D\), and is present in (3). A termwise proof encounters
\[
 \int_T^{2T}|\zeta(\tfrac12+it)|^2|A_L(1+2it)|^4dt.\tag{9}
\]
With
\[
 \mathcal A_L(t)=\sum_{L\le a<\sqrt2L}
       \mu(a)(L/a)^{1/2}a^{-1/2-2it},
 \qquad A_L(1+2it)=L^{-1/2}\mathcal A_L(t),
\]
the desired estimate for (9) becomes
\[
 \int_T^{2T}|\zeta(\tfrac12+it)|^2|\mathcal A_L(t)|^4dt
       \ll T^{7/6-\delta}.\tag{10}
\]
This is a genuine \(1:2\)-frequency joint moment, not the usual same-argument mollified second or fourth moment. Failure to bound (9) separately is **not** a lower-bound obstruction to the full residual: signed cancellation between identity terms or boxes could avoid a termwise estimate.

### Taking \(k=3\) does not license discarding the difficult part

For \(U=(2D)^{1/3}\asymp T^{5/18}\), the block identity is
\[
 M_D=[-3\zeta A_U^2+\zeta^2A_U^3]_D.\tag{11}
\]
The notation means coefficient restriction to \([D,2D)\), not evaluation of an unrestricted infinite Dirichlet series on \(\Re s=1\). The \(3A_U\) term vanishes on the block. The \(j=3\) term has three Möbius variables \(\le U\) and two free smooth variables. Setting all three Möbius variables to 1 leaves, among its boxes, two smooth variables of lengths \(T^{5/12}\) each. The analogue of (9) then has two coefficient-1 factors, neither long enough for (TI). Thus shrinking the Möbius cutoff does not by itself finish even the smooth case.

GMRR explicitly discusses two equal smooth factors and phases \(it,2it,2it\) as its original obstruction. Its equations there are stated as rough equivalences at its older parameter point; they are motivation, **not a matched theorem proving a saving at the present point**.[1] No claim that every larger fixed \(k\), regrouping, or cancellation-preserving argument fails has been proved.

## 6. Published estimate checks: why the missing joint bound is not supplied

### 6.1 GM remains available, but only at the baseline exponent here

Every fixed box after recombination into its product index has divisor-bounded coefficients, supported on an interval of length \(\asymp D\) and bounded multiplicative width. Split that support into a bounded number of dyadic intervals and divide by its pointwise divisor bound before applying GM. The arbitrary common shift \(u\) is absorbed into unimodular coefficients. This gives, after allocating losses,
\[
 I_{\rm box}(T)\ll_\epsilon T^\epsilon
 \left(TD^{-1}+T^{1/3}+T^{1/2}D^{-1/5}+TD^{-4/5}\right).
\]
At \(D=T^{5/6}\), the exponents are \(1/6,1/3,1/3,1/3\). Thus all the residual terms have a **non-improving** baseline control. Factorization has not worsened the bound by a fixed power, but has not improved its difficult terms.[1][2]

The original Möbius polynomial's low values \(|M_D|\le D^{-1/2}\) separately contribute at most \(TD^{-1}\log^2T=T^{1/6+o(1)}\), so this part is already controlled with a fixed power margin.[1]

At the critical normalized level \(V=D^{-1/4}=T^{-5/24}\), GM gives measure majorant \(T^{1/2+o(1)}\). The global fourth moment permits a zeta second integral of size \(T^{3/4+o(1)}\) on such a set. Multiplying by \(V^2=T^{-5/12}\) leaves \(T^{1/3+o(1)}\). A saving for its actual mixed integral would require additional joint information or a saving in the actual large-value count; it is not implied by renaming the coefficients as a convolution.[2][1]

Ordinary Cauchy with the zeta fourth moment and the fourth moment of a generic normalized product of length \(D\) gives only
\[
 T^{1/2+o(1)}\left(1+T/D^2\right)^{1/2}
      =T^{1/2+o(1)}
\]
here. Taking powers of equal factors does not automatically improve this: squaring a factor of length \(T^{5/12}\) returns the GM critical length \(T^{5/6}\).

### 6.2 Same-frequency twisted moment theorems: the correct index is squared

The apparent conflict in length conventions must be resolved:

* For a **standalone** polynomial in \(2t\), GM sees length \(D\), after rescaling the interval.
* For a theorem keeping **zeta at \(t\)** and requiring a twist \(\sum a_m m^{-1/2-it}\),
  \[
   M_D(1+2it)=\sum_{m\le4D^2}a_m m^{-1/2-it},
   \quad a_{d^2}=\mu(d),\quad a_m=0\ \text{otherwise}.
  \]
  Its integer-index cutoff is \(D^2=T^{5/3}\), not \(D\). One may not rescale the twist alone and still apply a same-argument zeta theorem.
* An individual balanced factor has square-index cutoff \(L^2=T^{5/6}\).
* If zeta is first replaced by its symmetric length-\(T^{1/2}\) approximate functional equation, the direct product has integer index \(n d^2\), extending to \(T^{13/6}\). Ordinary mean value on that product does not see merely \(T^{1/2}D\).

Bettin–Chandee–Radziwiłł Theorem 1 treats \(\zeta(1/2+it)A(1/2+it)\), with \(a_n\ll_\epsilon n^\epsilon\) and twist cutoff \(T^\theta\), **\(\theta<17/33\)**. Its displayed error is \(O(T^{3/20+\epsilon}N^{33/20}+T^{1/3+\epsilon})\). Neither the full cutoff \(T^{5/3}\) nor the individual balanced cutoff \(T^{5/6}\) satisfies the theorem's length hypothesis. Sparsity on squares is allowed as coefficients, but does not change that stated hypothesis.[3]

Their Theorem 4 requires one ordinary-index coefficient sequence to equal a smooth function \(\psi(n)\), with \(\psi^{(j)}(x)\ll_j x^{-j}\), length \(N\ll T^{1/2+\epsilon}\), and a second length \(K\ll T^{1/4}\), together with the specified support-width assumptions. A coefficient-1 sum in the variable \(c\) at phase \(2t\) becomes **square-supported**, not a smoothly varying coefficient sequence in its ordinary index \(m=c^2\). The length and smoothness hypotheses cannot be asserted for our balanced Type II factors. Their product-factor theorem is not a theorem that removes these hypotheses at total square-index cutoff \(T^{5/3}\).[3]

Watt's familiar same-frequency fourth-moment bound is recorded explicitly by Ivić as
\[
 \int_0^T|\zeta(\tfrac12+it)|^4
       |\sum_{m\le N}a_m m^{it}|^2dt
 \ll_\epsilon T^{1+\epsilon}N(1+N^2T^{-1/2})\max|a_m|^2.
\]
Here again the index of a \(2t\)-factor is squared; the favorable cutoff is not obtained by counting only its nonzero terms. Moreover the zeta power is four, not two. This quotation was checked in Ivić's formula (2.2), including MathML, and agrees with BCR's discussion. **Watt's original 1995 paper was not independently inspected, and this bound is not used as a load-bearing saving input in this audit.** No unverified extension to different frequencies or sparse-square improvement is being applied.[4][3] Ivić–Zhai, Lemma 2.1, provides the same displayed quotation, not a different-frequency extension.[5]

### 6.3 Möbius prefix cancellation and prime-local signs are not substitutes

For the actual prefix \(S_D(x)=\sum_{D\le n\le x}\mu(n)\), partial summation gives
\[
 |M_D(1+2it)|\ll \frac{1+T}{D}
        \sup_{D\le x\le2D}|S_D(x)|.
\]
The derivative of the oscillatory weight costs \(T\). Untwisted prefix cancellation therefore does not establish the required high-frequency joint estimate. Even a hypothetical square-root prefix bound would give the useless bound \(T D^{-1/2}=T^{7/12}\) at this point, before comparing with the trivial bound \(O(1)\). This is an elementary calculation, not a claim that such a uniform prefix hypothesis is known.

The signs of \(\mu(p)\) in an Euler product similarly do not imply a quantitative inequality for the intersection of the large-value sets of a **dyadically truncated** polynomial and zeta. Nothing here asserts prime-local anticorrelation, independence, or a random-Möbius model.

## 7. Uniformity required before a variance-range extension

A saving at the isolated equation \(D=T^{5/6}\) is not an extended variance theorem. At a minimum, a proposed new estimate must control an open fixed neighborhood of the length-height exponents, fixed endpoint masks, and the shifts or averaged shifts introduced by its actual separation argument. Write
\[
 D=T^d,\quad H=T^q,\qquad (d,q)=(5/6,4/3)
\]
at the critical point. The unweighted moment target needed for the tail is
\[
 I_D(T)\ll T H^{-1/2}\times\text{a fixed saving}
       =T^{1-q/2}\times\text{a fixed saving}.\tag{12}
\]
For example a uniform bound \(I_D(T)\ll T^{1/3-\delta}\) for \(|d-5/6|<\omega\) only has room for \(q=4/3+\nu\) if \(\nu/2<\delta\), with strict additional room for all losses. A continuous exponent formula with uniform strict slack would also work. Neither is proved by (J-rem) at a single point, even if that point were solved.

The actual formal small-divisor boundary illustrates the necessary direction of uniformity. If \(H=X^h\), choose the largest zero-margin cutoff exponent \(z=X^{1-h/2}\), and use \(T=X/H\). Then
\[
 d=\frac{1/2-h/4}{1-h},\qquad q=\frac h{1-h}=4d-2.
\]
For \(h>4/7\), this moves to \(d>5/6\) and \(q>4/3\). Thus the extended problem is not just another test at the old equality. Actual epsilon margins make the required uniform region a region, not a single boundary curve.

Even a neighborhood result is **not alone a complete variance proof**. To reuse GMRR's argument one must obtain, or replace by an equally strong spectral-kernel bound, a bound of the form
\[
 \sup_{X/H\le T\le X^2}\frac HT
   \int_{|t|\le T}|\zeta(\tfrac12+it)M_{D,\mathcal B}(1+2it)|^2dt
     \ll H^{1/2-c\varepsilon}
\]
for **every** tail block \(\sqrt z\le D\ll\sqrt X\), with its actual fixed endpoint masks \(\mathcal B\), and a common aggregate loss budget. All other length/height regimes, including cumulative low heights, must be covered by proved estimates; they cannot simply be assumed harmless because the critical point improved. The chosen \(z\) must still satisfy the actual GMRR Proposition 1 cutoffs. Localization, the \(d^2>2X\) endpoint squares, the far-frequency tail, the variance cross term, and density centering must still be verified. The parent baseline has already incorporated these repairs **for its present range**, not for a prospective extension.[1]

## 8. Additional baseline read: one locator correction, no fatal analytic issue found

The supplied consolidated file was read in full:
`<repo>/experiments/astra-rh-crt-20260912/GM_TRANSFER.md`.

I found no genuine new analytic failure in its stated transfer during this focused follow-up. Its atomless measurable partition of a level set into pieces of bounded measure is legitimate; it does not assert arithmetic independence. Its localization, endpoint-square estimate, aggregate budget, and implementation-specific ceiling are consistent with the named inputs.

**There are source-locator errors in its input list:** lines 53–55 call the Saffari–Vaughan reduction “Lemma 3”; in pinned GMRR v2 it is **Lemma 10**, label `le:SV`, TeX lines 518–524. Lines 58–61 refer to the zeta fourth moment via “Lemmas 5 and 7”; the relevant lemmas are **Lemma 3 (fourth moment)** and **Lemma 5 (Weyl)**. Lemma 7 is the hybrid polynomial mean-value theorem. The formulas themselves are correct. The lemma numbers were checked by enumerating the independent `lemma` counter in the source, which has no section reset. These are citation repairs, not new theorem assumptions or a reason to retract the deduction.[1]

## 9. Executed verification, evidence, and stopping point

`check_ledger.py` was actually executed. Its exact-integer checks cover **16** cutoff/order cases and **1,270** coefficients through their entire \(U^k\) cutoffs. It also checks the full remainder identity beyond a valid cutoff and rejects the unsafe deletion of the remainder at \(U=2,k=2,n=9\): the truncated expression is \(-1\), whereas \(\mu(9)=0\), and the remainder is 1.

The same run uses exact `Fraction` arithmetic for the critical GM exponents, the Type I dual-length and coefficient-norm ledger, the Type II interval endpoints, the square-index length warning, the half-normalized joint target, and two points on the variance boundary. Negative controls reject both claiming a strict Type I saving at \(C_0=T^{7/12}\) and spending the entire \(2\eta\) saving in losses. These computations check algebra and accounting, **not** the analytic truth of a missing moment estimate; no numerical zeta-value experiment was performed.

Primary reading copies, formula-preserving local text, the Heath-Brown formula image, source hashes, a task-isolated citation ledger, and verbatim source evidence are saved in this scratch bundle. The input hash check confirms the six original supplied report/source files were unchanged. The subsequently supplied `GM_TRANSFER.md` acquired an externally appended Sources block while this audit was running; a byte comparison verified that its entire mathematical body remained unchanged. Both reading copies and the exact append, with hashes, are archived. The initial fail-closed hash check detected this append before it was classified; no repository write was made by this audit. Search requests intermittently returned 403, but alternate targeted queries and direct public source fetches succeeded. PDF rendering initially needed additional isolated `uv` dependencies; the actual formula image was subsequently rendered and inspected. No plausible formula was substituted for a failed extraction.

The bounded audit stops at **(J-rem)**, with (J-box) and (10) specifying stronger termwise targets. A complete gain for the critical Möbius moment, let alone the necessary uniform gain for a variance extension, remains an open obligation of this investigation.

### Files in this new scratch directory

* `report.md` — complete report.
* `check_ledger.py`, `checks.json`, `execution.log` — replayable exact checks and actual output.
* `collect_sources.py`, `source-manifest.json`, `sources/` — archived source material and provenance.
* `citations.json`, `source-excerpts.md`, `collect_evidence.py` — task-isolated source ledger and exact evidence.
* `verification.json` — delivery checks and input-preservation status.

The intended result is a narrowed, mathematically explicit obligation and a proved controlled subfamily, not a fabricated theorem completing the uncontrolled family.

## Sources

[1] https://arxiv.org/src/2006.04060v2 — Gorodetsky–Matomäki–Radziwiłł–Rodgers, squarefree variance, pinned TeX v2
[2] https://arxiv.org/src/2405.20552v2 — Guth–Maynard, New large value estimates for Dirichlet polynomials, pinned TeX v2
[3] https://www.math.mcgill.ca/radziwill/BCR.pdf — Bettin–Chandee–Radziwiłł, author PDF dated January 15, 2015
[4] https://arxiv.org/html/math/0305179 — Ivić, fourth-moment paper, inspected HTML identifies v3
[5] https://ar5iv.labs.arxiv.org/html/1305.2685 — Ivić–Zhai, On a hybrid fourth moment involving the Riemann zeta-function
[6] https://dlmf.nist.gov/25.9 — DLMF 25.9: sharp approximate functional equation, citing Titchmarsh (4.12.4)
[7] https://www.cambridge.org/core/services/aop-cambridge-core/content/view/D6C21FF61C1489E5856AA5ED276CB0A9/S0008414X00033307a.pdf/div-class-title-prime-numbers-in-short-intervals-and-a-generalized-vaughan-identity-div.pdf

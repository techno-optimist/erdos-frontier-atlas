# Independent audit of sparse-square report, Sections 1–4

## Verdict

**passed: true — the mathematical deductions in Sections 1–4 pass, with the scope and qualifications below.**

**blocking_issues: none found in the reviewed deductions.** The signed off-diagonal saving is explicitly an **unproved target**, not an achievement of the candidate or of this audit. Its absence blocks an improved mixed-moment/variance theorem, but is not a defect in a report that correctly identifies it as missing.

The entire arithmetic diagonal, including collisions with distinct root indices, satisfies

\[
\mathcal D_w(T,D)=T\log T\,Q_D\int w+O_w(T/D),\qquad Q_D\asymp D^{-1},
\]

for the full Möbius block and fixed nonzero nonnegative high-shell weight. This is **not a lower bound for the mixed moment**.

The unsigned near-core assertion is stronger than a merely plausible or saturable upper-bound model: it is a **proved lower bound for an actual integer-entry point cloud**. It gives \(\gg T^{5/3}\) nonzero very-near-collision pairs at the critical scales, and \(\gg_w T^{1/2}\) after restoring the kernel and coefficient weights. That positive unsigned quantity is itself a majorant used in a triangle-inequality approach. It is not the signed off-diagonal or the original integral, and no corresponding lower bound for either signed object follows.

This review does not certify Sections 5–8's literature audit, establish a new signed moment estimate, audit the deep input proofs in full, or make any publication, novelty, or RH claim.

## 1. Exact artifacts reviewed, including the failed-patch concern

I read the existing final files, rather than reconstructing an intended patch:

- Candidate: `twisted-square/report.md`.
- Mathematical core: `twisted-square/audit-mathematics.md`.
- Target: `twisted-square/open-target.md`.
- Supplied baseline: `<repo>/experiments/astra-rh-crt-20260912/GM_TRANSFER.md`.

The core is **byte-for-byte the prefix of the final report**. Its Section 4.1 actually contains the pigeonhole argument, exact-collision subtraction, small-argument weight argument, and limitation to an unsigned majorant. Its Sections 3.3 and 4 explicitly reject a lower bound for the integral and distinguish the stronger boxwise target. No presumed later edit was used.

Pinned SHA-256 values:

| Artifact | SHA-256 |
|---|---|
| `report.md` | `e8ab36422d02bc2b7d611163730744a4472d5a724d838dca074b6bc3cb8fa6b8` |
| `audit-mathematics.md` | `b443e1de695eac45061c3bea1fd728514b885bae7160b316d26d2dca5c558021` |
| `open-target.md` | `5b75f07bbe124cbd1132b480238e84f94048d39609e08de173353a153e53df3b` |

Line locators below refer to the candidate/core, which have the same line numbering through Section 4.2. Source citation numbers in this independent report are its own ledger numbers, not the candidate's numbers.

## 2. Hypothesis ledger: normalization and the BCR AFE

### 2.1 Two lengths, not one

For

\[
M_D(1+2it)=\sum_{D\le d<2D}\frac{\mu(d)}d\,d^{-2it},
\]

the standalone change of variable \(u=2t\) gives a Dirichlet polynomial of ordinary index cutoff \(2D\), hence length \(\asymp D\). The measure also changes: \(dt=du/2\). The mean-value theorem gives

\[
\int_{cT}^{CT}|M_D(1+2it)|^2dt
 \ll_{c,C}(T+D)\sum_{d\sim D}\frac{\mu(d)^2}{d^2}
 \ll T/D+1.
\]

The supplied GMRR text explicitly allows arbitrary coefficients and \(q=1\) in its hybrid mean-value lemma; this yields the stated unweighted case. An interval translation merely inserts unimodular coefficients.[4] (Primary `gmrr-v2/squfv.tex:392–403`.)

If zeta remains at \(1/2+it\), the common-frequency twist instead has coefficients \(a_{d^2}=\mu(d)\), all other coefficients zero, and index cutoff \(\asymp D^2\). Indeed \((d^2)^{-1/2-it}=d^{-1-2it}\). The stated coefficient norms follow from the squarefree count. The candidate's distinction at lines 30–46 is correct; the standalone time change cannot change only the polynomial's frequency in a mixed-moment theorem.

The baseline high-shell exponent specialization in lines 48–55 is correct. This review uses that supplied scalar bound as a baseline, not as a new independently rebuilt Guth–Maynard proof.

### 2.2 Exact AFE hypotheses checked from the primary text

BCR's Section 3 assumes an **entire** function \(G\), rapidly decreasing on fixed vertical lines, with

\[
G(-z)=G(z),\quad G(0)=1,\quad G(1/2)=0.
\]

Its Lemma 1 is for \(T<t<2T\), and defines

\[
W(x)=\frac1{2\pi i}\int_{(2)}x^{-z}G(z)\frac{dz}{z}.
\]

The lemma states

\[
|\zeta(1/2+it)|^2
=2\sum_{m_1,m_2\ge1}\frac{(m_1/m_2)^{it}}{\sqrt{m_1m_2}}
W(2\pi m_1m_2/t)+O(T^{-2/3}).
\]

These are the actual source conditions, not inferred from BCR's twist-length theorem.[1] (`bcr-v1/main.tex:460–477`.) The deposited journal text has the same conditions and AFE on printed page 58, PDF page 8.[3] (`bcr-deposited.txt:458–478`.) **The standalone AFE has no hypothesis \(D^2<T^{17/33}\).** That belongs to a different theorem concerning the subsequently integrated twisted moment.

The selected \(G(z)=(1-4z^2)e^{z^2}\) satisfies every condition and additionally \(G(\bar z)=\overline{G(z)}\). The latter makes \(W\) real on positive arguments. Li–Radziwill explicitly imposes this conjugation condition and explains the gamma-factor simplification.[2] (`lr-v1/draft.tex:994–1009,1023–1064`.)

Interchanging the AFE variables gives the candidate's phase \((n/m)^{-it}\). A fixed shell \([cT,CT]\), with \(c>0\), is covered by a fixed number of height-rescaled dyadic shells, so the error remains uniform with constants depending on \(c,C,G\). Nothing is extended through \(t=0\).

**Error qualification.** The candidate safely uses \(O_\varepsilon(T^{-2/3+\varepsilon})\), although both source lemmas display the loss-free exponent. This relaxed version follows from the near-central gamma contour, Weyl subconvexity, and Stirling, after allowing small contour/logarithmic losses. It is not justified by replacing the gamma weight termwise on an absolutely summed long double polynomial. For the explicit Gaussian \(G\), one can restrict the contour's imaginary part to a small power of \(T\), use uniform Stirling there, and make its complement negligible by Gaussian decay. The zeta poles at \(z=1/2\pm it\) encountered when opening the Dirichlet series also have negligible Gaussian-weighted residues. This is the source proof's relevant mechanism.[2]

### 2.3 The paid error is correctly priced

Multiplying the pointwise error by the **actual** \(|M_D|^2\), not by a generic dense-polynomial norm, gives

\[
|E_{\rm AFE}|
\ll_{w,\varepsilon}T^{-2/3+\varepsilon}
\int_{cT}^{CT}|M_D(1+2it)|^2dt
\ll_{w,\varepsilon}T^{-2/3+\varepsilon}(T/D+1).
\]

At \(D=T^{5/6}\), the two powers are \(T^{-1/2+\varepsilon}\) and \(T^{-2/3+\varepsilon}\). The first dominates. BCR explicitly obtains a generic \(T^{1/3+\varepsilon}\) integrated AFE error in its own setting, but that is not an intrinsic floor for this multiplier.[1] (`main.tex:481–485`.) Candidate lines 95–104 pass.

Rapid decay allows the AFE product tail \(nm>T^{1+\varepsilon_0}\) to be removed at any prescribed negative power, with \(\varepsilon_0>0\) fixed first and the decay order then chosen large. The coefficient sum \(\sum_{d\sim D}1/d\ll1\) prevents an unnoticed power of \(D\) in an absolute tail estimate. Alternatively the standalone mean-value estimate prices a pointwise truncated-AFE remainder. Neither route requires a low-height AFE.

## 3. The chosen AFE weight changes sign

This is worth making explicit, although the candidate's argument does not need global positivity.

Put \(y=\log x\). Inverse Gaussian Mellin/Laplace inversion gives

\[
\frac1{2\pi i}\int_{(2)}e^{z^2-yz}\,dz
=\frac1{2\sqrt\pi}e^{-y^2/4}.
\]

Integrating with respect to \(y\), or differentiating the definition with its \(1/z\) factor and using the limit at \(+\infty\), gives

\[
\boxed{W(e^y)=\frac12\operatorname{erfc}(y/2)
-\frac{y}{\sqrt\pi}e^{-y^2/4}.}
\]

Consequences derived from this formula:

- \(W(x)\to1\) as \(x\to0^+\), and \(W(x)\ge1/2\) for \(0<x\le1\).
- It need not lie below 1 either.
- \(W(e^2)<0\): the elementary Gaussian-tail inequality \(\operatorname{erfc}(1)\le e^{-1}/\sqrt\pi\) already makes the displayed expression negative. The independent sanity computation returns approximately `-0.3364578938954522`.

Thus **a proof that drops arbitrary AFE pieces by nonnegativity would fail**. No such proof occurs in the reviewed final contents. The only needed weight positivity is local, on deliberately small arguments in Section 4.1, where it is valid. The diagonal is evaluated by contour shifting, not by declaring \(W\ge0\).

## 4. Full signed diagonal: independent derivation

### 4.1 Every exact collision is retained

Write \(d=ga\), \(e=gb\), \(g=(d,e)\), \((a,b)=1\). Then

\[
nd^2=me^2\iff na^2=mb^2
\iff n=b^2\ell,\quad m=a^2\ell,\quad \ell\ge1.
\]

On these tuples,

\[
\frac{\mu(d)\mu(e)}{de\sqrt{nm}}
=\frac{\mu(ga)\mu(gb)}{g^2a^2b^2\ell},
\qquad nm=a^2b^2\ell^2.
\]

This proves the candidate's (3.3), including its outer factor 2. Terms with \(a\ne b\), hence generally \(d\ne e\), remain with their Möbius signs. It is not the \(d=e\) subtotal.

### 4.2 Uniform gcd and logarithmic estimates

For \(0\le\sigma<1/4\), put

\[
S_\sigma(D)=\sum_{d,e\sim D}\frac{(d,e)^2}{d^2e^2}
\left(\frac{de}{(d,e)^2}\right)^{2\sigma}.
\]

Since \(d,e\) lie in one dyadic interval, \(a,b\) are comparable. On a dyadic class \(\max(a,b)\asymp R\):

1. There are \(O(R^2)\) choices of \(a,b\), even before imposing coprimality.
2. Allowed \(g\) satisfy \(g\asymp D/R\), and
   \(\sum g^{-2}\ll R/D\). This remains valid at \(g\asymp1\); when \(R\) approaches \(D\), the right side is a constant, not an omitted endpoint error.
3. The remaining weight is \((ab)^{-2+2\sigma}\ll_\sigma R^{-4+4\sigma}\).

Their product is \(\ll_\sigma D^{-1}R^{-1+4\sigma}\). The **dyadic** sum converges for \(\sigma<1/4\), giving \(S_\sigma(D)\ll_\sigma D^{-1}\). Inserting \(\log(ab)\ll1+\log R\) at \(\sigma=0\) still gives a convergent dyadic series and hence

\[
\sum_{d,e\sim D}\frac{(d,e)^2}{d^2e^2}
\log\frac{de}{(d,e)^2}\ll D^{-1}.
\]

These are absolute estimates, uniform for all coefficients or masks of modulus at most one. The strict \(\sigma<1/4\) is real; the endpoint is not certified. This verifies (3.4)–(3.5).

### 4.3 Contour residue and summed remainder

Let \(q=ab\), \(X=t/(2\pi q^2)\). Absolute convergence on \(\Re z=2\) gives

\[
2\sum_{\ell\ge1}\frac{W(2\pi\ell^2q^2/t)}\ell
=\frac2{2\pi i}\int_{(2)}X^z\zeta(1+2z)G(z)\frac{dz}{z}.
\]

The only pole crossed in moving to \(\Re z=-\sigma\) is the double pole at zero. Expand

\[
\zeta(1+2z)=\frac1{2z}+\gamma+O(z),\quad
X^z=1+z\log X+O(z^2),\quad G(z)=1+O(z^2).
\]

Including the factor 2, the residue is exactly \(\log X+2\gamma\). If \(G'(0)\ne0\), the residue would also contain \(G'(0)\); evenness removes it. An independent formal Laurent-polynomial calculation checks these coefficients.

The new contour is bounded by \(O_\sigma(X^{-\sigma})\). Fixed-strip polynomial bounds for zeta and Gaussian decay suffice, uniformly for every \(q\ge1\). Consequently

\[
2\sum_{\ell\ge1}\frac{W(2\pi\ell^2q^2/t)}\ell
=\log\frac{t}{2\pi q^2}+2\gamma
+O_\sigma((q^2/t)^\sigma).
\]

The error is allowed to be large for large \(q\); summing it with the original arithmetic weight costs

\[
\int w(t/T)t^{-\sigma}dt\;S_\sigma(D)
\ll_{w,\sigma}T^{1-\sigma}/D.
\]

This is the crucial uniformity justification. One never replaces \(W\) by 1 uniformly at large \(q\).

With

\[
Q_D=\sum_{d,e\sim D}\mu(d)\mu(e)\frac{(d,e)^2}{d^2e^2},\qquad
L_D=\sum_{d,e\sim D}\mu(d)\mu(e)\frac{(d,e)^2}{d^2e^2}
\log\frac{de}{(d,e)^2},
\]

the resulting formula is

\[
\mathcal D_w
=Q_D\int w(t/T)(\log(t/(2\pi))+2\gamma)dt
-2L_DT\int w+O_{w,\sigma}(T^{1-\sigma}/D),
\]

exactly (3.8). In particular \(|L_D|\ll D^{-1}\). The signs and the coefficient \(-2\) in front of \(L_D\) are correct.

### 4.4 Jordan-totient Gram representation and a full-block lower bound

The divisor identity

\[
\sum_{r\mid n}J_2(r)=n^2,\qquad
J_2(r)=r^2\prod_{p\mid r}(1-p^{-2})>0
\]

gives the exact finite Gram expansion

\[
Q_D=\sum_{1\le r<2D}J_2(r)
\left(\sum_{\substack{d\sim D\\r\mid d}}\frac{\mu(d)}{d^2}\right)^2.
\]

For every integer \(r\in[D,2D)\), the only multiple of \(r\) in the block is \(r\) itself. The half-open endpoint ensures \(2r\) is not included even if \(r=D\). Therefore

\[
Q_D\ge\sum_{r\sim D}\frac{\mu(r)^2J_2(r)}{r^4}
\ge\frac1{\zeta(2)}\sum_{r\sim D}\frac{\mu(r)^2}{r^2}\gg D^{-1}.
\]

The Euler-product inequality is in the right direction: a product over a subset of the factors \((1-p^{-2})\), each between 0 and 1, is at least the product over all primes. The squarefree lower bound is elementary: opening \(\mu(r)^2=\sum_{h^2\mid r}\mu(h)\), summing floors, and estimating the absolutely convergent tail gives \(\sum_{r\le x}\mu(r)^2=x/\zeta(2)+O(\sqrt x)\). Thus the full dyadic block contains \(\asymp D\) squarefree integers for large \(D\).

Together with \(S_0(D)\ll D^{-1}\), this proves \(Q_D\asymp D^{-1}\) without assuming Möbius independence or positivity of individual cross terms.

### 4.5 Actual conclusion and its limits

Fix, for example, \(\sigma=1/8\); no limiting contour parameter is needed. Since \(|L_D|\ll D^{-1}\), \(Q_D\ll D^{-1}\), and \(w\) is supported away from zero,

\[
\mathcal D_w=T\log T\,Q_D\int w+O_w(T/D).
\]

For fixed nonzero nonnegative \(w\), this is \(\asymp_w T\log T/D\), with relative error \(O_w(1/\log T)\) against its explicit finite-form leading term. No universal limiting value for \(DQ_D\) is asserted. At \(D=T^{5/6}\), the scale is \(T^{1/6}\log T\).

For a fixed real or complex mask \(b_d\), replace coefficients by \(\mu(d)b_d\). The Gram square becomes an absolute square and the cross coefficient is \(\mu(d)\mu(e)b_d\overline{b_e}\). All the stated absolute upper bounds persist when \(|b_d|\le1\). A uniform \(D^{-1}\) lower bound does not persist for arbitrary interval truncations or tapers; the zero mask already rules it out.

The candidate explicitly says at lines 254–256 that its lower bound is for the full block and is not a lower bound for \(I_w\). This is correct: \(I_w=\mathcal D_w+\mathcal O_w+E_{\rm AFE}\), and \(\mathcal O_w\) can be negative.

## 5. Signed off-diagonal normalization, ranges, and masks

Let \(\lambda=\log(nd^2/(me^2))\). After \(t=Tu\), the kernel is

\[
K=T\int w(u)W(2\pi nm/(Tu))e^{-iTu\lambda}\,du.
\]

Mellin decay and integration by parts give, for arbitrary fixed orders \(A,B\),

\[
K\ll_{A,B,w}T(1+nm/T)^{-A}(1+T|\lambda|)^{-B}.
\]

Both derivative constants and shell support must be controlled. This requires no \(W\ge0\). With the explicit \(G\), derivatives at zero and infinity have more than enough decay; BCR also records the needed weight-derivative bounds.[1]

After a product-tail cutoff and a phase-tail cutoff \(T|\lambda|\le T^{\varepsilon_0}\), absolute summation makes the discarded tails \(O(T^{-A_0})\) for any fixed prescribed \(A_0\). A simple bound is to sum \(d(k)k^{-1/2}\) over \(k=nm\) and use \(\sum_{d,e\sim D}1/(de)\ll1\), then choose the decay orders after \(\varepsilon_0\). There is no hidden power-length obstruction in these tails.

For the remaining terms, \(d/e\in(1/2,2)\) and \(nd^2/(me^2)=1+O(T^{-1+\varepsilon_0})\). Thus \(n/m\) lies in a fixed compact subinterval of \((0,\infty)\). Consequently

\[
1\lesssim N,\quad n\asymp m\asymp N\ll T^{1/2+\varepsilon},\quad
0<|nd^2-me^2|\ll T^\varepsilon ND^2/T.
\]

The product truncation initially gives \(N\ll T^{(1+\varepsilon_0)/2}\); renaming the small loss yields the candidate's notation. The lower end includes \(N\asymp1\). The square-root box is not the entire problem. A bounded number of comparable dyadic pairs can be grouped at each scale, leaving \(O(\log T)\) scales.

For a symmetric partition \(\Psi_N\), the exact algebra is

\[
\mathcal R_N=
\sum_{d,e\sim D}\sum_{nd^2\ne me^2}
\mu(d)\mu(e)\frac{D^2}{de}\frac{N}{\sqrt{nm}}
\Psi_N(n,m)\frac{K}{T},
\]

\[
\boxed{\mathcal O_w=2\sum_N\frac{T}{ND^2}\mathcal R_N+O(T^{-A_0}).}
\]

Multiplication cancels every artificial normalization: \(T\), \(D^2\), and \(N\). The factor 2 from the AFE remains. Swapping \((n,d)\leftrightarrow(m,e)\) conjugates \(K\), so the full sums are real; a symmetric partition preserves this property scale by scale.

**Masks:** for an actual partial polynomial, insert the *same* factor \(b_d\overline{b_e}\) in this definition, the diagonal, and the AFE multiplier norm. The target must hold uniformly for the interval endpoints/tapers used in the application. A result for the full block does not imply every masked result by positivity, and arbitrary tuple-dependent or time-dependent masks are not silently covered. Candidate lines 64 and 359 correctly preserve this missing requirement.

## 6. Actual aggregate target versus a stronger sufficient boxwise bound

At \(D=T^{5/6}\) and \(0<\eta<1/6\), put \(B(T)=T^{1/3-\eta}\). The diagonal and paid AFE error are \(o(B(T))\). Therefore

\[
I_w\ll B(T)\quad\Longleftrightarrow\quad |\mathcal O_w|\ll B(T).
\]

The reverse direction is immediate from the decomposition. In the forward direction,
\(-\mathcal O_w\le\mathcal D_w+|E_{\rm AFE}|\) follows from \(I_w\ge0\), while the positive side is bounded by \(I_w+|\mathcal D_w|+|E_{\rm AFE}|\). Thus an absolute aggregate off-diagonal target does not impose an unjustified negative-cancellation condition.

The actual normalized target is

\[
\left|2\sum_N\frac{T}{ND^2}\mathcal R_N\right|
\ll T^{1/3-\eta}.
\]

It is **not** a claim that every box must be small separately. A sufficient stronger input is

\[
|\mathcal R_N|\ll ND^2T^{-2/3-\eta-\delta}
\]

for every contributing scale, with a fixed reserve \(\delta>0\) paying the dyadic and other explicitly allocated losses. Cross-scale signed cancellation can make the aggregate bound true without this stronger assertion. Candidate lines 306–313 state the distinction correctly.

At \(N\asymp T^{1/2},D=T^{5/6}\), exact rational exponent checks give:

| Quantity | Power of \(T\), before reserved losses |
|---|---:|
| square index cutoff | \(5/3\) |
| product index \(nd^2\) | \(13/6\) |
| entry count \(ND\) | \(4/3\) |
| near gap \(ND^2/T\) | \(7/6\) |
| restoring prefactor \(T/(ND^2)\) | \(-7/6\) |
| sufficient normalized target | \(3/2-\eta\) |
| normalized diagonal-scale target | \(4/3+o(1)\) |

The last row is a stronger possible achievement, not a necessary intermediate result.

## 7. Pigeonhole near-core claim: an actual lower bound, with exact subtraction

This is the main distinction from a scalar-majorant saturation example.

### 7.1 Define the actual cloud and count same-bin pairs

Take the entry set

\[
\mathscr P=\{(n,d):N\le n<2N,\ D\le d<2D,\ \mu(d)^2=1\},
\qquad N=c_0\sqrt T,
\]

with integer endpoints understood in the inequalities. There are \(M\asymp ND\) entries. Map each entry to its integer value \(v=nd^2\), retaining multiplicity. All values lie in \([ND^2,8ND^2)\).

Partition that interval into bins of width

\[
h=c_1ND^2/T.
\]

For fixed \(c_1>0\), at most \(B\ll_{c_1}T\) bins are needed. If their occupancies are \(b_j\), Cauchy–Schwarz gives the deterministic count

\[
P_{\rm bin}=\sum_jb_j^2\ge M^2/B\gg_{c_1}N^2D^2/T.
\]

This counts ordered pairs of actual entries, initially including repeated values and self-pairs. It is not a statistical distribution hypothesis.

### 7.2 Exact collisions are only \(O(ND)\)

Let \(E\) be the number of ordered entry pairs with exactly equal values. Dropping the squarefree restrictions can only enlarge it. Write each equality using \(d=ga,e=gb,n=b^2\ell,m=a^2\ell\), as above.

In the dyadic class \(\max(a,b)\asymp R\), with \(a,b\) comparable:

- \(O(R^2)\) choices of \(a,b\);
- \(O(D/R)\) choices of \(g\);
- \(O(N/R^2)\) choices of \(\ell\).

The apparent floor issues do **not** introduce an uncharged \(+1\): an existing \(g\ge1\) forces \(R\ll D\), and an existing \(\ell\ge1\) forces \(R^2\ll N\). Thus the quoted bounds, with absolute constants, cover the last nonempty classes; later classes are empty.

A class costs \(O(ND/R)\). Since \(R\) is dyadic, its sum is \(O(ND)\), **not** \(O(ND\log D)\) or a larger hidden contribution. This includes the self-pairs and all distinct-entry exact collisions.

All exact equalities lie in a common bin, so the nonzero count is exactly \(P_{\rm bin}-E\), and hence

\[
P_{\ne0}\ge cN^2D^2/T-CND.
\]

At the critical cell, \(ND/T\asymp T^{1/3}\to\infty\); therefore the subtraction leaves

\[
\boxed{P_{\ne0}\gg T^{5/3}.}
\]

Here \(ND\asymp T^{4/3}\). This assertion is for all sufficiently large \(T\), with fixed positive constants, not for every small finite test box. The estimate is a lower bound, not an asymptotic evaluation or matching upper bound for the actual pair count.

### 7.3 Local positivity of the exact kernel makes it a weighted lower bound too

For a same-bin pair,

\[
|\log(nd^2/(me^2))|
\le\frac{|nd^2-me^2|}{\min(nd^2,me^2)}\le c_1/T.
\]

Choose \(c_1\) so that \(Cc_1\le\pi/3\). Then the real part of the phase is at least \(1/2\) throughout the shell.

Also \(nm<4N^2\), so on \(t\ge cT\),

\[
2\pi nm/t\le8\pi c_0^2/c.
\]

Choose \(c_0\) small enough that the right side is at most 1. The explicit weight formula above then gives \(W\ge1/2\). Hence for fixed nonzero nonnegative \(w\),

\[
\operatorname{Re}K\ge\frac T4\int w>0,
\qquad |K|\ge\operatorname{Re}K.
\]

The candidate's stronger wording “close to 1” is also justified by taking \(c_0,c_1\) smaller, but the displayed weaker constants already prove everything needed.

Because \(d,e\) are squarefree, \(|\mu(d)\mu(e)|=1\), and throughout this box \(de\sqrt{nm}\asymp D^2N\). Thus the actual absolute-term near-core contribution satisfies

\[
2\sum_{\text{nonzero same-bin pairs}}
\frac{|\mu(d)\mu(e)K|}{de\sqrt{nm}}
\gg_w\frac{T}{ND^2}\frac{N^2D^2}{T}
\asymp_w N\asymp T^{1/2}.
\]

This proves the stated unsigned cost for the actual coefficients and exact kernel, not merely an envelope with artificially assigned values.

### 7.4 What this does not prove

Deleting signs and taking absolute values creates a positive majorant. A lower bound for that majorant cannot be reversed into a lower bound for the signed sum it bounds. The \(T^{1/2}\) cost only shows that a completely absolute treatment cannot certify \(T^{1/3-\eta}\); the factor to recover relative to it is at least \(T^{1/6+\eta}\), before reserved losses.

Cancellation can occur between Möbius signs in the close core and/or between that core and more oscillatory surroundings. No smallness of the isolated signed core, no lower bound for \(I_w\), and no impossibility theorem follow. Nor is this a claim that every arbitrarily chosen dyadic taper has the same lower bound: it is a positive hard-box diagnostic; smooth versions require a nonvanishing inner box or summation over a bounded overlapping partition.

Candidate lines 331–347 state this limitation correctly. The final `open-target.md` likewise calls the boxwise estimate sufficient and the target unproved.

## 8. Neighborhood, cutoffs, and aggregate loss conditions

For \(D=T^\alpha\), \(|\alpha-5/6|\le\rho\), the uniform diagonal upper bound is

\[
|\mathcal D_w|\ll_w T^{1-\alpha}\log T
\le T^{1/6+\rho}\log T.
\]

It lies strictly below \(T^{1/3-\eta}\) when \(\eta+\rho<1/6\). With an additional requested reserve, the candidate's \(\eta+\rho+\delta<1/6\) is stronger and sufficient. A reserve for the dyadic bound is not logically required in this diagonal comparison, but it is safe to demand the stronger separation.

The AFE error is uniformly

\[
T^{-2/3+\varepsilon}(T^{1/6+\rho}+1),
\]

and remains negligible after choosing its loss parameter sufficiently small. The kernel-tail loss parameter, the theorem's future subpowers, dyadic summation, and any divisor-block recombination must be budgeted together, not each independently allowed to exhaust the reserve.

The example \(\eta=1/100\), \(\rho=1/10000\), raw saving \(2\eta\), and aggregate loss \(1/10000\) leaves saving \(199/10000>\eta\). Taking \(\delta=\eta\) also satisfies the stronger numerical separation. These are exact rational checks of a **hypothetical loss budget**, not verification of a bound with that saving.

The target must cover all sufficiently large \(T\), all \(D\) in an open fixed exponent neighborhood, all contributing \(N\), the specified bounded smooth-shell class, and the actual fixed interval masks. Full-block or one-taper positivity cannot fill a missing signed-mask estimate. An improvement in this neighborhood alone would still require the baseline's other height/divisor ranges and endpoint conditions to be reassembled before any variance deduction.

## 9. Required qualifications and limited wording clarifications

These are not undisclosed new theorem hypotheses that invalidate the existing argument; they delimit the pass and should accompany any condensed reuse.

1. **Weight signs:** \(w\ge0\) is the outer averaging weight; \(W\) is sign-changing. Local \(W\to1\) is sufficient for Section 4.1. Adding an explicit sentence to that effect would improve the candidate, but no erroneous global-positivity step was found.
2. **Full-block lower bound:** the lower bound is for the entire Möbius block and fixed nonzero nonnegative \(w\). Uniform upper bounds allow bounded masks and bounded shell seminorms. A lower constant uniform over a weight family would additionally need \(\int w\) bounded below; the report does not claim it for a degenerating family.
3. **No mixed-moment lower bound:** neither the positive leading coefficient of the diagonal nor the positive absolute core is a lower bound for the full mixed moment. Preserve the candidate's explicit disclaimers.
4. **Actual cloud versus majorant:** the \(T^{5/3}\) lower bound is genuinely proved for the entry cloud after exact-collision subtraction; it is not a mere saturable scalar model. It nevertheless concerns an unsigned quantity that majorizes signed terms. Do not upgrade \(\gg\) to \(\asymp\), or transfer it to every taper/box.
5. **Aggregate, not boxwise necessity:** (4.6) is a sufficient stronger uniform bound. The actual target is the weighted signed sum (4.4), and cross-box cancellation is allowed.
6. **All scales and masks:** retain \(N\asymp1\) through \(T^{1/2+\varepsilon}\), the bounded comparable dyadic partners, actual interval masks, and explicit conjugates for complex masks. Do not silently freeze time-dependent arithmetic support.
7. **Neighborhood and losses:** keep \(\eta+\rho<1/6\), with positive room for the chosen aggregate loss budget. All contour/decay constants must be fixed before taking \(T,D\to\infty\). The open-target file can always narrow \(\eta,\rho\), but the separation should be explicit when inferring the mixed-moment saving.
8. **Smooth shell wording:** the first option at candidate line 74—a fixed smooth majorant supported in a larger high shell—is valid and sufficient. The alternative “rescaled smooth windows” should mean a positive covering/majorant with overlapping rescaled supports. It must not be read as a finite smooth majorant confined to exactly \([T,2T]\) with no support extension, since smooth functions supported there vanish at its endpoints and cannot uniformly dominate the indicator near them. This ambiguity does not affect the valid first option.
9. **Review status:** the candidate's prior machine `PASS` only checked its stated algebra/provenance gates. The independent analytic pass here is bounded to Sections 1–4. The missing off-diagonal bound, literature exhaustiveness, a new variance range, and RH remain uncertified.

## 10. Reviewed claims ledger

| Candidate locator | Claim | Verdict |
|---|---|---|
| lines 30–46; (1.1)–(1.2) | Standalone root length versus common-frequency square-index cutoff | Pass |
| lines 48–64 | Baseline critical exponents; neighborhood and masks required | Pass as a deduction from supplied baseline |
| lines 76–104; (2.1)–(2.3) | Exact admissible AFE weight, phase convention, paid error | Pass |
| lines 106–108 | High-shell product truncation and retention of full AFE | Pass |
| lines 112–155; (3.1)–(3.3) | Exact signed decomposition and all cross-collisions | Pass |
| lines 157–181; (3.4)–(3.5) | Uniform gcd/log upper bounds | Pass, strict fixed \(\sigma<1/4\) |
| lines 183–219; (3.6)–(3.8) | Residue, logarithmic coefficient, summed contour error | Pass |
| lines 221–254; (3.9)–(3.11) | Gram positivity, full-block lower bound, diagonal scale | Pass with stated full-block/nonzero-weight scope |
| lines 256, 304, 347 | No false lower bound for the mixed moment | Pass |
| lines 260–295; (4.1)–(4.4) | Kernel bounds, all dyadic ranges, normalization | Pass with controlled partitions and actual masks |
| lines 297–327; (4.5)–(4.6) | Aggregate equivalence and stronger sufficient boxwise target | Pass |
| lines 329–347; (4.7)–(4.8) | Actual-cloud pigeonhole lower bound and exact-collision subtraction | Pass; unsigned method cost only |
| lines 349–359 | Neighborhood, masks, reserve, unproved status | Pass |
| `open-target.md:5–36` | Extracted unproved target and normalized exponents | Pass with qualifications in Section 9 |

## 11. Executed checks, reproducibility, and issues encountered

All scripts and output created by this review are in the new scratch directory:

`sparse-square/`.

The independent script executed successfully and saved `independent-checks.json`:

- 11 exact full-block Gram/quadratic checks, including explicit singleton-multiple lower bounds.
- 12 exact masked checks, including zero-mask examples showing why no uniform full-scale masked lower bound follows.
- 200 Jordan divisor identities.
- 5 direct-versus-parametrized equality and signed rational-weight checks on actual dyadic integer boxes.
- 3 actual finite point-cloud/bin-count checks with exact equality subtraction.
- A formal Laurent residue check and exact prefactor cancellation checks.
- 21 critical exponent entries and a strict rational loss budget.
- Noncertifying sanity values for the analytically derived sign-changing weight.
- Byte-for-byte equality of the inspected BCR, Li–Radziwill, and GMRR TeX with the corresponding stored version-pinned source archive payloads.

For an illustrative finite cloud \(T=64,N=1,D=8192,c_1=1/16\), the executed count returned 4,980 entries, 9,854 ordered same-bin pairs, 4,980 exact equalities, and 4,874 nonzero same-bin pairs; the Cauchy–Schwarz bound after subtraction was positive. Another deliberately smaller-density finite box had a negative CS-minus-equalities lower bound even though it had nonzero near pairs. This is expected: the proof needs \(ND/T\to\infty\), and finite enumeration is not evidence for an asymptotic analytic saving.

The candidate's original `check_algebra.py` was read, copied unmodified to `replayed-original/`, and run **there**; its 7 finite block checks and 29 exponent entries returned `PASS`. Its outputs never overwrote the candidate's checks. This corroborates finite algebra only; it does not substitute for the derivations in this report.

Primary evidence spans were attached mechanically to a scratch-only citation ledger; six evidence attachments succeeded. The final preservation/citation gate is recorded in `verification.json`. All 83 initial files (the candidate directory's files and the original baseline) were hashed before this audit and are checked again by that gate.

Resolved tooling issue: the first independent script run assumed every arXiv `.src` was a tar archive. BCR's file is instead a single gzip-compressed TeX payload. The scratch checker was corrected to distinguish tar archives from plain gzip sources and then rerun successfully. This was a checker-format issue, not a failed mathematical identity or presumed candidate patch. The live `python3` used by the terminal was Python 3.9.6; the scripts are standard-library compatible and required no installation.

Reproduce from the given workspace:

```text
python3 sparse-square/independent_checks.py
python3 sparse-square/prepare_evidence.py
python3 sparse-square/finalize_verification.py
```

No input report, baseline, primary source, or repository was modified. This is an independently derived bounded audit, not formal proof-assistant verification.

## Sources

[1] https://arxiv.org/src/1411.7764v1
[2] https://arxiv.org/src/1208.2684v1
[3] https://unige.iris.cineca.it/bitstream/11567/896399/3/bettin2015.pdf
[4] https://arxiv.org/src/2006.04060v2

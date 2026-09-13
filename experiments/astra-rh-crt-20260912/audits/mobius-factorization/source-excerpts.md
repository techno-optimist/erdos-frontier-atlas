# Literal source evidence

Formulas in scanned Heath-Brown text are OCR-damaged; see the accompanying inspected page003.png. The report proves the reciprocal identity independently.

## Source [1]: GMRR Lemma 3: zeta fourth moment
`sources/gmrr.tex` lines 339–348

```text
\begin{lemma}[Fourth moment estimate]
\label{le:ZetaFourth}
  Let $T \geq 2$. Then
  $$
  \int_{|t| \leq T} |\zeta(\tfrac 12 + it)|^4 dt \ll T (\log T)^4. 
  $$
\end{lemma}

\begin{proof} 
See e.g. \cite[formula (7.6.1)]{Titchmarsh86}.
```

## Source [1]: GMRR Lemma 5: Weyl bound
`sources/gmrr.tex` lines 364–371

```text
\begin{lemma}[Subconvexity estimate]
\label{le:ZetaSC}
One has, for $|t| \geq 2$,
\[
\zeta(1/2 + it) \ll |t|^{1/6} (\log |t|)^2.
\]
\end{lemma}
\begin{proof} See e.g. \cite[formula (8.22)]{iwaniec2004analytic}.
```

## Source [1]: GMRR Lemma 7: mean value, used at q=1
`sources/gmrr.tex` lines 392–403

```text
\begin{lemma}[Hybrid mean-value theorem] \label{le:hmvt}
  Let $a(n)$ be an arbitrary sequence of coefficients and $N, q \geq 1$ be integers and $T \geq 1$ real. Then, for any given $\varepsilon > 0$, 
  $$
  \sum_{\chi \Mod{q}} \int_{|t| \leq T} \Big | \sum_{n \leq N} a(n) \chi^2(n) n^{it} \Big |^2 dt \ll q^{\varepsilon} (q T + N) \sum_{n \leq N} |a(n)|^2. 
  $$
\end{lemma}
\begin{proof}
  We notice that given a character $\psi \Mod{q}$ there are at most $\ll q^{\varepsilon}$ characters $\chi$ such that $\chi^2 = \psi$. Therefore the left-hand side of the claim is bounded by
  $$
  \ll q^{\varepsilon} \sum_{\psi \Mod{q}} \int_{|t| \leq T} \Big | \sum_{n \leq N} a(n) \psi(n) n^{it} \Big |^2 dt 
  $$
  and the result follows from the standard hybrid mean-value theorem, see e.g. \cite[Theorem 6.4]{Montgomery71}. 
```

## Source [1]: GMRR Lemma 10: Saffari–Vaughan locator correction
`sources/gmrr.tex` lines 518–526

```text
\begin{lemma}
\label{le:SV}
  If $F \colon \mathbb{R} \rightarrow \mathbb{C}$ is square-integrable and $H \leq X$, then
  $$
  \int_{X}^{2X} |F(x + H) - F(x)|^2 dx \ll \sup_{\theta \in [\frac{H}{3X}, \frac{3 H}{X}]} \int_{X}^{3X} |F(u + \theta u) - F(u)|^2 du
  $$
\end{lemma}

\begin{proof} The proof can be found in a paper by Saffari and Vaughan~\cite[Page 25]{SaffariVaughan77} but for the convenience of the reader we include the proof here.
```

## Source [1]: GMRR explicitly labels its smooth-factor discussion as rough equivalences
`sources/gmrr.tex` lines 292–308

```text
Finally let us make a few remarks on the bottleneck that prevents us from pushing our result further. Taking $H = X^{6/11}$, we are unable to show the following estimate,
$$
\frac{1}{X} \int_{X}^{2X} \Big | \sum_{\substack{x \leq n d^2 \leq x + H \\ d^2 \sim X^{8/11}}} \mu(d) - H \sum_{d^2 \sim X^{8/11}} \frac{\mu(d)}{d^2}\Big |^2 dx \ll_{A} \frac{\sqrt{H}}{\log^{A} X} 
$$
Specifically opening $\mu(d)$ using Heath-Brown's identity (see \cite{HBV}) the only situation that we are not able to estimate is the one in which $\mu(d)$ is replaced by two smooth sums of equal length. Roughly speaking this corresponds to estimating,
$$
\frac{1}{X} \int_{X}^{2X} \Big | \sum_{\substack{x \leq n a^2 b^2 \leq x + H \\ a, b \sim X^{2/11}}} 1 - H \sum_{a, b \sim X^{2/11}} \frac{1}{a^2 b^2} \Big |^2 dx \ll \frac{\sqrt{H}}{\log^{A} X}
$$
Opening the above expression into Dirichlet polynomials this is roughly equivalent to
$$
\int_{|t| \leq X^{5/11}} \Big | \sum_{n \sim X^{3/11}} \frac{1}{n^{1/2 + it}} \sum_{a \sim X^{2/11}} \frac{1}{a^{1/2 + 2 it}} \sum_{b \sim X^{2/11}} \frac{1}{b^{1/2 + 2 it}} \Big |^2 dt \ll \frac{X^{6/11}}{\log^{A} X}
$$
Applying the functional equation on the Dirichlet polynomial over $n$, and setting $Y = X^{12/11}$ we then see that obtaining the above estimate is equivalent to showing that,
$$
\int_{|t| \leq Y^{5/12}} \Big | \sum_{n \sim Y^{1/6}} \frac{1}{n^{1/2 + it}} \sum_{a \sim Y^{1/6}} \frac{1}{a^{1/2 + 2 it}} \sum_{b \sim Y^{1/6}} \frac{1}{b^{1/2 + 2 it}} \Big |^2 dt \ll \frac{Y^{1/2}}{\log^{A} Y}. 
$$ 
If the $2 i t$ in the Dirichlet polynomial over $a$ and $b$ were replaced by $i t$ then we would be facing exactly the same bottleneck as in the case of improving Huxley's prime number theorem in short intervals (by a variant of the computations in \cite{HBV}, see also \cite[Chapter 7]{Harman}). In particular to make further progress we either need to find a way to improve Huxley's estimate or find a way to exploit the fact that the phases in two of the Dirichlet polynomials are $2 it $ and not $it$. Unfortunately we do not see how to make progress on either of these questions. 
```

## Source [2]: GM Theorem 1.1: coefficient, spacing, and bound
`sources/gm.tex` lines 68–79

```text
\begin{thrm}[Large values estimate]\label{thrm:LargeValues}
Suppose $(b_n)$ is a sequence of complex numbers with $|b_n| \le 1$,  and $(t_r)_{r\le R}$ is a sequence of $1$-separated points in $[0,T]$ such that
\[
\Bigl|\sum_{n= N}^{2N}b_n n^{it_r}\Bigr|\ge V
\]

for all $r\le R$. Then we have
\[
R\le T^{o(1)}\Bigl(N^2V^{-2}+N^{18/5}V^{-4}+TN^{12/5}V^{-4}\Bigr).
\]

\end{thrm}
```

## Source [3]: BCR Theorem 1 as rendered in the author PDF
`sources/bcr.pdf.txt` lines 98–131

```text
Theorem 1. LetI and A(s) be as above. If θ <1
2 +δ, with δ = 1
66 then,
I =
∑
d,e⩽Tθ
adae
[d,e ]·
∫
R
(
log
(t (d,e )2
2πde
)
+ 2γ
)
φ
(t
T
)
dt +O
(
T
3
20 +εN
33
20 +T
1
3 +ε
)
,
whereN :=Tθ.
We notice that the oﬀ-diagonal terms contribute to the main term roughly those d
```

## Source [3]: BCR Theorem 4, support/smoothness/length conditions and surrounding comparison
`sources/bcr.pdf.txt` lines 359–427

```text
Theorem 4. Let J,A (s) and B(s) be as deﬁned in (1.5) and (1.6). Let N ≪ T
1
2 +ε
for all ε > 0 and assume that αn = ψ(n) with ψ(x) a smooth function such that
ψ(j)(x)≪j x−j for all j > 0. Let K ≪ T
1
4 and βk ≪ kε for all ε > 0. Moreover
assume αn is supported on [NT−ξ1, 2N] and βk is supported on [KT−ξ2, 2K], where
0≤ξ1≤ 1
5, 0≤ξ2≤ 1
16. Then,
J =
∑
d,e⩽NK
adae
[d,e ]·
∫
R
(
log
(t(d,e )2
2πde
)
+ 2γ
)
φ
(t
T
)
dt +
+O
(
T
1
2 +εK2 +KN
3
4T
3
8 +ε + T
39
40 + 1
8ξ1+ 2
5ξ2+ε
)
,
wheread =∑
nk=dαnβk.
Remark. Theorem 4 yields an asymptotic formula for 5ξ1 + 16ξ2 < 1 (and N≪ T
1
2 ,
K≪T
1
2−ε). We remark that this range could be enlarged with a little more work.
We notice that Theorem 4 allows us to take θ < 3
4 for Dirichlet polynomials of
the form A(s)B(s) with A(s) pretending to be ζ(s) and B(s) of length up to T 1/4−ε.
Thus, following the work of Radziwi l l [Rad12], Theorem 4 could be applied to give
a sharp upper bound for the 2 k-th moment of the Riemann zeta function for 2 k <
5, conditionally on the Riemann hypothesis (however, we remark that this has been
recently proven for all k≥ 0 by Harper [Har]). It would be interesting to investigate if
Theorem 4 has other applications, for example to the study of large gaps between the
zeros of the Riemann zeta-function (see [Bre]).
Theorem 4 reﬁnes upon Watt’s result, who uses his Kloosterman sum estimate to give
(essentially) an upper bound of the form J≪ T 1+ε +T 1/2+εK2, for an,bn supported
on dyadic intervals. Theorem 4 should also be compared with the asymptotic formula
for the twisted fourth moment of Hughes and Young [HY10]. Their result allows to get
an asymptotic formula for the second moment of ζ2(s)B(s) with B(s) of length up to
T 1/11−ε.
Acknowledgments
```

## Source [4]: Ivic formula (2.2): quotation of Watt, not independently used as a primary saving input
`sources/ivic-watt.html.txt` lines 121–126

```text
The essential tool in our considerations is the following theorem for
the fourth moment of  $|\zeta({\textstyle{1\over 2}}+it)|$ , weighted by a Dirichlet polynomial, due
to N. Watt [9]. This is built on the works of J.-M. Deshouillers
and H. Iwaniec [1], [2], involving the use of Kloosterman sums,
but it contains the following sharper result: Let  $a_{1},a_{2},\ldots$  be complex numbers. Then, for  $\varepsilon>0,M\geq 1$  and  $T\geq 1$ ,
$\int_{0}^{T}|\sum_{m\leq M}a_{m}m^{it}|^{2}|\zeta({\textstyle{1\over 2}}+it)|^{4}\,{\roman{d}}t\ll_{\varepsilon}T^{1+\varepsilon}M(1+M^{2}T^{-1/2})\max_{m\leq M}|a_{m}|^{2}.$
```

## Source [5]: Ivic–Zhai Lemma 2.1: corroborating same-frequency quotation of Watt
`sources/ivic-zhai.html.txt` lines 143–153

```text
2 The necessary lemmas
In order to prove our results, we require some lemmas which will be given in this section.
The first lemma is the following
upper bound for the fourth moment of $\zeta(\frac{1}{2}+it),$ weighted by a Dirichlet polynomial.
Lemma 2.1 . Let $a_{1},a_{2},\ldots,a_{M}$ be complex numbers. Then we have,
for $\varepsilon>0,M\geqslant 1$ and $T\geqslant 1$ ,
(2.1)
$\int_{0}^{T}|\zeta({\textstyle{\frac{1}{2}}}+it)|^{4}\Bigl|\sum_{m\leqslant M}a_{m}m^{it}\Bigr|^{2}dt\ll_{\varepsilon}T^{1+\varepsilon}M(1+M^{2}T^{-1/2})\max_{m\leqslant M}|a_{m}|^{2}.$
This result is due to N. Watt [ 17 ] . It is founded on the earlier works of
J.-M. Deshouillers and H. Iwaniec [ 2 ] , which involved the use of Kloosterman sums, but
Watt’s result is sharper.
```

## Source [6]: Sharp asymmetric AFE with all displayed hypotheses
`sources/dlmf-25.9.html.txt` lines 35–40

```text
If  $x\geq 1$ ,  $y\geq 1$ ,  $2\pi xy=t$ , and  $0\leq\sigma\leq 1$ , then as
$t\to\infty$  with  $\sigma$  fixed,
25.9.1
$\zeta\left(\sigma+it\right)=\sum_{1\leq n\leq x}\frac{1}{n^{s}}+\chi(s)\sum_{1%
\leq n\leq y}\frac{1}{n^{1-s}}+O\left(x^{-\sigma}\right)+O\left(y^{\sigma-1}t^%
{\frac{1}{2}-\sigma}\right),$
```

## Source [6]: Gamma quotient defining chi
`sources/dlmf-25.9.html.txt` lines 63–66

```text
where  $s=\sigma+it$  and
25.9.2
$\chi(s)\equiv\pi^{s-\frac{1}{2}}\Gamma\left(\tfrac{1}{2}-\tfrac{1}{2}s\right)/%
\Gamma\left(\tfrac{1}{2}s\right).$
```

## Source [7]: HB page 1367: binomial mechanism and support cutoff (formula image is authoritative)
`sources/heath-brown-1982.pdf.txt` lines 97–117

```text
We shall therefore use the following trivial identity (which is not, 
strictly speaking, a generalization of Vaughan's). 
LEMMA 1. For any integer k ^ 1 we have 
(6) rwr(s)  = E (-iy-1(k)ns)i-Y(s)M(sy 
To apply Lemma 1 to the sum 
5 = £ A(n)/(»), 
for example, one chooses X k ^ x and picks out the relevant coefficients 
of n~ s. The last term on the right hand side of (6) therefore makes no 
contribution, since 
(7) Ç(s)M(s)-l = Zc(n)n-\ 
n>X 
with c(n) as in (3). On splitting up each range of summation into inter­
vals N < n S 2iV, one finds that 5 is a linear combination of O((log x) 2k) 
sums of the form 
(8) £ (log fli)/i(»*+i) • •  • V>(n2k)f(nin2. . . n 2*), 
wi€ Ii ,n\ri2.. .nzk^-x 
in which I t = (N u 2N t]% YiNt < x } and 2N t ^ X if i > k. (Some of 
the intervals I t may contain only the integer 1.) By choosing k to be 
large, and X to be a small power of x, one may bring the part of the sum 
(8) involving the 'unknown' coefficients  M(^0  as closely under control 
as one likes. 
```

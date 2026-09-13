# Verbatim primary-source excerpts

These are extracted source blocks, not independent proof claims.

## GMRR-P1
Proposition 1, PDF p.6, eq.(11); source lines 217-222

```tex
\begin{proposition} \label{pr:prop1}
  Let $\varepsilon \in (0, \tfrac{1}{100})$ be given.
  Let $X \geq 1$ and $X^{\varepsilon} \leq H \leq X^{2/3 - \varepsilon}$. Let $H^{1+\varepsilon} \leq z \leq \min\{X/H^{1/2+\varepsilon}, H^{1/2-\varepsilon}X^{1/2}\}$. Then, as $X \rightarrow \infty$, 
  \begin{equation} \label{eq:prop1}  \frac{1}{X} \int_{X}^{2X} \Big | \sum_{\substack{x < n d^2 \leq x + H \\ d^2 \le z}} \mu(d) - H \sum_{d^2 \le z} \frac{\mu(d)}{d^2} \Big |^2 \, dx = C \sqrt{H} + O(H^{1/2-\varepsilon/10})
    \end{equation}
    with $C$ as in~\eqref{eq:C_dfn}.
```

## GMRR-P2
Proposition 2, PDF p.6, eq.(12); source lines 225-230

```tex
\begin{proposition} \label{pr:prop2}
  Let $\varepsilon \in (0, \tfrac{1}{100})$ be given. Let $X \geq 1$ and $X^{\varepsilon} \leq H \leq X^{4/7 - \varepsilon}$. Let $z \geq H^{4/3+\varepsilon}$. Then
  \begin{equation} \label{eq:prop2}
  \frac{1}{X} \int_{X}^{2X} \Big | \sum_{\substack{x < n d^2 \leq x + H \\ d^2 > z}} \mu(d) - H \sum_{\substack{2X \geq d^2 > z}} \frac{\mu(d)}{d^2} \Big |^2 dx \ll H^{1/2 - \varepsilon / 8}. 
  \end{equation}
  Assuming the Lindel\"of Hypothesis, the claim holds in the wider range $X^\varepsilon \leq H \leq X^{2/3-\varepsilon}$ and $z \geq H^{1+\varepsilon}$.
```

## GMRR-LV
Lemma 1, PDF pp.9-10; source lines 314-319

```tex
\begin{lemma}[Large-value theorem]
\label{le:LVT}
Let $N, T \geq 1$ and $V > 0$. Let $F(s) = \sum_{n \leq N} a_n n^{-s}$ be a Dirichlet polynomial and let $G = \sum_{n \leq N} |a_n|^2$. Let $\mathcal{T}$ be a set of $1$-spaced points $t_r \in [-T, T]$ such that $|F(it_r)| \geq V$. Then
\[
|\mathcal{T}| \ll (GNV^{-2} + T \min\{GV^{-2}, G^3 N V^{-6}\})(\log 2NT)^6
\]
```

## GMRR-CUTOFF
Section 4, PDF p.19, bound after eq.(34); source lines 724-728

```tex
Using this bound in~\eqref{eq:tobound}, and summing over $n_1$ and $n_2$, we note that the maximum is attained for $N_j = D_j^2/H$ and thus the contribution to \eqref{eq:tobound} from $\sqrt{n_2/n_1}$ quadratic irrational is bounded by
\[
\ll H^{\varepsilon/2}\left(\frac{D_1 D_2 H}{X} + 1 +\frac{D_1 D_2}{X^{1/2}} \right) = O(H^{1/2-\varepsilon/2})
\]
since $D_1 \cdot D_2 \leq z \leq \min\{X/H^{1/2+\varepsilon}, H^{1/2-\varepsilon} X^{1/2}\}$.
```

## GMRR-REDUCTION
Section 5, PDF pp.20-22, eqs.(36)-(41); source lines 756-815

```tex
\section{The range $z \geq H^{4/3+\varepsilon}$ in the $t$-aspect : Proof of Proposition \ref{pr:prop2}}
\label{se:prop2}
We would like to establish that
$$
\frac{1}{X} \int_{X}^{2X} \Big | \sum_{\substack{x < n d^2 \leq x + H \\ d^2 > z}} \mu(d) - H \sum_{\substack{z < d^2 \leq 2 X}} \frac{\mu(d)}{d^2} \Big |^2 dx \ll H^{1/2 - \varepsilon / 8}. 
$$
Splitting into dyadic ranges according to the size of $d$, 
it essentially suffices to show that, for each $D \in [z^{1/2}, (2X)^{1/2}]$, we have
\begin{equation}
\label{eq:varDlar}
\frac{1}{X} \int_{X}^{2X} \Big | \sum_{\substack{x < n d^2 \leq x + H \\ d \sim D}} \mu(d) - H \sum_{d \sim D} \frac{\mu(d)}{d^2} \Big |^2 dx \ll H^{1/2 - \varepsilon / 4}. 
\end{equation}

Let
$$
A(x) := \sum_{\substack{n d^2 \leq x \\ d \sim D}} \mu(d) - x \sum_{d \sim D} \frac{\mu(d)}{d^2}. 
$$
Using this definition and Lemma~\ref{le:SV}, we see that the left-hand side of~\eqref{eq:varDlar} is
\begin{equation} \label{eq:saffari}
\frac{1}{X} \int_{X}^{2X} |A (x + H) - A(x) |^2 dx \ll \frac{1}{X} \int_{X}^{3X} |A(u ( 1+ \theta)) - A(u)|^2 du
\end{equation}
for some $\theta \in [\frac{H}{3X}, \frac{3 H}{X}]$. Choose $w$ such that $e^w = 1 + \theta$, so that $w \asymp \frac{H}{X}$. 
By contour integration
\begin{equation}
\label{eq:Aey}
A(e^y) = \frac{1}{2\pi i} \int_{2-i\infty}^{2+i\infty} \frac{e^{y s}}{s} \zeta(s) M(2s) ds - e^y \sum_{d \sim D} \frac{\mu(d)}{d^2},
\end{equation}
where
$$
M(s) := \sum_{d \sim D} \frac{\mu(d)}{d^{s}}.
$$
Moving the contour to the line $\Re s= 1/2$ we notice that the residue from $s = 1$ cancels with the second term on the right-hand side of~\eqref{eq:Aey}, and we obtain
$$
\frac{A(e^{w + x}) - A(e^x)}{e^{x / 2}} = \frac{1}{2\pi} \int_{\mathbb{R}} \frac{e^{w (\tfrac 12 + it)} - 1}{\tfrac 12 + it} e^{i t x} \zeta(\tfrac 12 + it) M(1 + 2it) dt.
$$
Therefore, by Plancherel,
\begin{equation} \label{eq:plancherel}
\int_{0}^{\infty} | A(e^{u + w}) - A(e^u) |^2 \cdot \frac{du}{e^u} \ll \int_{\mathbb{R}} \Big | \frac{e^{w (\tfrac 12 + it)} - 1}{\tfrac 12 + it} \Big |^2 \cdot |\zeta(\tfrac 12 + it) M(1 + 2it)|^2 dt. 
\end{equation}
Combining \eqref{eq:saffari} and \eqref{eq:plancherel} we get after a change of variable, 
\begin{equation}
\label{eq:Asqdiff}
\begin{split}
  \frac{1}{X} \int_{X}^{2X} |A(x + H) - A(x)|^2 dx & \ll X \int_{0}^{\infty}  |A( u (1 + \theta) ) - A(u) |^2 \frac{du}{u^2} \\
  & \ll X \int_{\mathbb{R}} \Big | \frac{e^{w (\tfrac 12 + it)} - 1}{\tfrac 12 + it} \Big |^2 \cdot |\zeta(\tfrac 12 + it) M(1 + 2it)|^2 dt \\
  & \ll X \int_{\mathbb{R}} \min\Bigl\{ \Bigl(\frac{H}{X}\Bigr)^2, \frac{1}{|t|^2}\Bigr\} \cdot |\zeta(\tfrac 12 + it) M(1 + 2it)|^2 dt.
\end{split}
\end{equation}
By Lemma~\ref{le:ZetaSC} the part with $|t| \geq X^2$ contributes
\[
\ll X \int_{X^2}^\infty |t|^{-5/3+\varepsilon} dt = O(1).
\]
On the other hand, the contribution of $|t|\le X^2$ to the right-hand side of \eqref{eq:Asqdiff} is at most
\begin{align}
\nonumber
&\ll    \frac{H^2}{X}	\int_{|t| \le 2X/H} |\zeta(\tfrac 12 + it) M(1 + 2it)|^2 dt \\
\nonumber
& \qquad \qquad + X \int_{X/H}^{X^2} \frac{1}{T^2} \cdot \frac{1}{T} \int_{T \le |t|\le 2T} |\zeta(\tfrac 12 + it) M(1 + 2it)|^2 dt dT\\
\label{eq:final}
&\ll H \Big ( \sup_{X / H \leq T \leq X^2} \frac{1}{T} \int_{|t| \leq T} |\zeta(\tfrac 12 + it) M(1 + 2it)|^2 dt \Big ) + O(1).
```

## GMRR-LEVELS
Section 5, PDF pp.22-23, eq.(42) and following bounds; source lines 831-859

```tex
Let us now prove the unconditional part of the proposition. 
First notice that the values of $t$ for which $|M(1+2it)| \leq D^{-1/2 + \varepsilon/16}$ contribute to~\eqref{eq:final} by Cauchy-Schwarz and the fourth moment bound (Lemma~\ref{le:ZetaFourth}) $O(H^{1+\varepsilon/16}D^{-1+\varepsilon/8}) = O(H^{1/2-\varepsilon/4})$, and therefore their contribution is always acceptable.
Writing 
\[
S(V) = \{t \in [-T, T] \colon V \leq |M(1+2it)| < 2V\},
\]
by dyadic splitting, it suffices to show that, for each $V \in [D^{-1/2}, 1]$ and $T \in [X/H, X^2]$, we have
\[
\frac{H}{T} V^2 \int_{S(V)} |\zeta(1/2+it)|^2 dt \ll H^{1/2-\varepsilon/3}.
\]
Now by Lemma~\ref{le:LVT} we have
\begin{equation}
\label{eq:S(V)bound}
|S(V)| \ll (V^{-2} + T\min\{D^{-1}V^{-2}, D^{-2} V^{-6}\}) (\log 2X)^6.
\end{equation}

Consider first the case when the first term dominates here. Then by Lemma~\ref{le:ZetaSC} we have
\[
\frac{H}{T} V^2 \int_{S(V)} |\zeta(1/2+it)|^2 dt \ll \frac{H}{T} T^{1/3+\varepsilon/2} \ll \frac{H}{T^{2/3-\varepsilon/2}} \ll \frac{H^{5/3}}{X^{2/3-\varepsilon/2}} \leq H^{1/2-\varepsilon/3}
\] 
since $H \leq X^{4/7-\varepsilon}$. 

Consider now the case that the second term dominates in~\eqref{eq:S(V)bound}. Then, by Cauchy-Schwarz and the fourth moment estimate (Lemma~\ref{le:ZetaFourth}),
\begin{align*}
&\frac{H}{T} V^2 \int_{S(V)} |\zeta(1/2+it)|^2 dt \ll \frac{H}{T} V^2 |S(V)|^{1/2} \left(\int_{|t| \leq T} |\zeta(\tfrac 12 + it)|^4 dt \right )^{1/2} \\
& \ll H V^2 \min\{D^{-1}V^{-2}, D^{-2} V^{-6}\}^{1/2} (\log 2X)^5 \ll H\min\{D^{-1/2} V, D^{-1} V^{-1}\} (\log 2X)^5 \\
&\ll H (D^{-1/2} V)^{1/2} (D^{-1} V^{-1})^{1/2} (\log 2X)^5 \ll H D^{-3/4} (\log 2X)^5 \ll H z^{-3/8} (\log 2X)^5 \ll H^{1/2-\varepsilon/3}
\end{align*}
since $z \geq H^{4/3+\varepsilon}$. This finishes the proof of Proposition~\ref{pr:prop2}.
```

## GMRR-HEURISTIC
Section 2 closing bottleneck discussion, PDF p.9; source lines 292-308

```tex
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

## GM-THEOREM
Theorem 1.1, PDF p.1; HTML #S1.Thmthrm1; source lines 68-79

```tex
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

## GM-HYPOTHESES
Remark after Lemma 1.7; HTML #Thmrmkx1

```tex
[Thmrmkx1] 

Remark.

[Thmrmkx1.p1] 

[Thmrmkx1.p1.1] Many earlier results on large values of Dirichlet polynomials (such as those stemming from the Mean Value Theorem or the Montgomery-Huxley-Halász large values estimate) allowed one to relax the $\ell^{\infty}$ constraint $|b_{n}|\leq 1$ on the coefficients to a weaker $\ell^{2}$ constraint $(\sum_{n=N}^{2N}|b_{n}|^{2})^{1/2}=O(N^{1/2})$. Our argument crucially relies on the stronger $\ell^{\infty}$ assumption to bound the additive energy $E(W)$ efficiently, and we do not know how to obtain Theorem 1.1 if we only have $\ell^{2}$ bounds on the coefficients. The remark after Lemma 11.4 highlights where we use this assumption.

1.2. Notations and conventions

[S1.SS2.p1] 

[S1.SS2.p1.1] We write $A\ll B$ to mean that $|A|\leq CB$ for an absolute constant $C$, and $A\ll_{z}B$ to denote that the constant $C$ may depend on the parameter $z$. We write $A\asymp B$ to mean $A\ll B$ and $B\ll A$ both hold, and $A\sim B$ to mean $B<A\leq 2B$. Similarly, we write $A\lessapprox B$ to mean that for any $\epsilon>0$, there is a constant $C(\epsilon)>0$ depending only on $\epsilon$ such that $|A|\leq C(\epsilon)T^{\epsilon}B$ for all large $T$, and $A\lessapprox_{z}B$ to denote a dependency on a parameter $z$. Asymptotic quantities such as $o(1)$ are interpreted as $T\rightarrow\infty$.
```

## GM-REDUCTION
Section 3, Proposition 3.1 and proof of Theorem 1.1; HTML #S3

```tex
Proposition 3.1.

[S3.Thmthrm1.p1] 

[S3.Thmthrm1.p1.1] Let $\sigma\in[7/10,8/10]$ and $\epsilon>0$. Let $b_{n}$ be a sequence of complex numbers with $|b_{n}|\leq 1$ and $W$ be a set of $T^{\epsilon}$-separated points in an interval of length $T=N^{6/5}$ such that

[S3.Thmthrm1.p2] 

$\Bigl|\sum_{n}w\Bigl(\frac{n}{N}\Bigr)b_{n}n^{it}\Bigr|\geq N^{\sigma}$

[S3.Thmthrm1.p3] 

[S3.Thmthrm1.p3.1] for all $t\in W$. Then we have

[S3.Thmthrm1.p4] 

$|W|\leq TN^{(12-20\sigma)/5+o_{\epsilon}(1)}.$

[S3.2] 

Proof of Theorem 1.1 assuming Proposition 3.1.

[S3.p2] 

[S3.p2.1] As mentioned in the introduction, the result follows from (1.1) if $V\leq N^{7/10+o(1)}$ or if $V\geq N^{8/10-o(1)}$, so we may assume $V\in[4N^{7/10},N^{8/10}]$, in which case $N^{2}V^{-2}\leq N^{18/5}V^{-4}$. Similarly, Theorem 1.1 follows from (1.1) if $N\geq T$ since then $R\leq T^{o(1)}N^{2}V^{-2}$, so we may assume $N<T$. By splitting $D(t)$ into 3 separate pieces (and using the triangle bound), we see that it suffices to show the result when $b_{n}=0$ unless $n\in[6N/5,9N/5]$. Since the function $w$ is 1 on $[6/5,9/5]$, we then have that $b_{n}=b_{n}w(n/N)$, so we may insert the weight $w(n/N)$. Finally, having inserted the smooth weights we now relax the vanishing condition on the $b_{n}$. Thus, letting $V=N^{\sigma}$, it suffices to show that whenever $\sigma\in[7/10,8/10]$, $N\ll T$, $(a_{n})$ is a 1-bounded complex sequence and $\mathcal{W}$ is a set of $1$-separated points such that

[S3.p3] 

$\Bigl|\sum_{n}w\Bigl(\frac{n}{N}\Bigr)a_{n}n^{it}\Bigr|\geq N^{\sigma}$

[S3.p4] 

[S3.p4.1] for each $t\in\mathcal{W}$, we have

[S3.p5] 

$|\mathcal{W}|\leq T^{o(1)}(N^{18/5-4\sigma}+TN^{12/5-4\sigma}).$

[S3.p6] 

[S3.p6.1] We now fix $\eta>0$ and choose $\mathcal{W}^{\prime}\subset\mathcal{W}$ so that $\mathcal{W}^{\prime}$ is $T^{\eta}$-separated and $|\mathcal{W}^{\prime}|\geq|\mathcal{W}|/T^{\eta}$ (this can be achieved by picking the smallest element of $\mathcal{W}$ and then repeatedly choosing the next smallest element which is at least $T^{\eta}$ away from all picked elements). If $T\leq N^{6/5}$, then we apply Proposition 3.1 to bound $\mathcal{W}^{\prime}$ directly (taking $\epsilon=\eta/2$ so that $\mathcal{W}^{\prime}$ is $N^{6\epsilon/5}$-separated since $M\ll T$), which implies that

[S3.p7] 

$|\mathcal{W}|\leq T^{\eta}|\mathcal{W}^{\prime}|\leq T^{\eta}N^{(18-20\sigma)/5+o_{\eta}(1)}.$

[S3.p8] 

[S3.p8.1] Letting $\eta\rightarrow 0$ sufficiently slowly then gives the result in this case. If instead $T>N^{6/5}$, then we divide $\mathcal{W}^{\prime}$ into $\lceil T/N^{6/5}\rceil$ subsets $\mathcal{W}_{j}^{\prime}$ each supported on an interval of length $N^{6/5}$, and we apply Proposition 3.1 to bound each $\mathcal{W}_{j}^{\prime}$ separately. This gives
```

## GM-REFINEMENT
Proposition 12.1, PDF p.47; HTML #S12.Thmthrm1

```tex
Proposition 12.1 (Large values estimate for $N\geq T^{5/6}$).

[S12.Thmthrm1.p1] 

[S12.Thmthrm1.p1.1] Suppose $(b_{n})_{n\sim N}$, $(t_{r})_{r\leq R}$ are as in Theorem 1.1, and that $T^{5/6}\leq N\leq T$ and $V=N^{\sigma}$ with $\sigma\geq 7/10$. Then we have

[S12.Thmthrm1.p2] 

$R\lessapprox N^{2-2\sigma}+T^{1/2}N^{3-4\sigma}+\inf_{k\in\mathbb{N}}\Bigl(T^{\frac{k}{k+1}}N^{(4-6\sigma)\frac{k}{k+1}}+N^{(5-6\sigma)\frac{4k}{4k+3}}T^{\frac{2}{4k+3}}\Bigr).$

[S12.Thmthrm1.p3] 

[S12.Thmthrm1.p3.1] In particular, we have

[S12.Thmthrm1.p4] 

$R\lessapprox N^{2-2\sigma}+T^{1/2}N^{3-4\sigma}+T^{(30\sigma-21)/5}N^{(46-60\sigma)/5}.$

[S12.p13] 

[S12.p13.1] Proposition 12.1 implies that the $N^{18/5}V^{-4}$ term in Theorem 1.1 can be replaced by $T^{1/2}N^{3-4\sigma}+T^{(30\sigma-21)/5}N^{(46-60\sigma)/5}$, which is smaller. When $\sigma=3/4$, Proposition 12.1 improves on (1.1) by a factor of $(T/N)^{1/2}$. Since we anticipate the main uses of Theorem 1.1 to be when $N<T^{5/6}$ we content ourselves with the simpler formulation of Theorem 1.1.
```

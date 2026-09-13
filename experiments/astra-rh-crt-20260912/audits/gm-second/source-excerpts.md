# Read-only source excerpts

## GM Theorem 1.1

Input `gm-source/LargevaluesDirichlet17.tex`, lines 68–79, citation [1].

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

## GM uniform subpower convention

Input `gm-source/LargevaluesDirichlet17.tex`, lines 288–290, citation [1].

```tex
\subsection{Notations and conventions} \label{subsecdeltalessapprox}

We write $A \ll B$ to mean that $ |A| \le C B$ for an absolute constant $C$, and $A \ll_z B$ to denote that the constant $C$ may depend on the parameter $z$. We write $A\asymp B$ to mean $A\ll B$ and $B\ll A$ both hold, and $A\sim B$ to mean $B<A\le 2B$. Similarly,  we write $A \lessapprox B$ to mean that for any $\epsilon > 0$, there is a constant $C(\epsilon)>0$ depending only on $\epsilon$ such that $|A| \le C(\epsilon) T^{\epsilon} B$ for all large $T$, and $A \lessapprox_z B$ to denote a dependency on a parameter $z$. Asymptotic quantities such as $o(1)$ are interpreted as $T\rightarrow \infty$.
```

## GM Proposition 12.1

Input `gm-source/LargevaluesDirichlet17.tex`, lines 2235–2252, citation [1].

```tex
When $N>T^{5/6}$ the process of going from Proposition \ref{prpstn:KeyProp} to Theorem \ref{thrm:LargeValues} is somewhat wasteful since it actually bounds the number of large values in $[0,N^{6/5}]$. By using a variation of the above argument, the bound in Theorem \ref{thrm:LargeValues} could be improved. We record one such improvement here.

\begin{prpstn}[Large values estimate for $N\ge T^{5/6}$]\label{prpstn:BigN}
Suppose $(b_n)_{n\sim N}$, $(t_r)_{r\le R}$ are as in Theorem \ref{thrm:LargeValues}, and that $T^{5/6}\le N\le T$ and $V=N^\sigma$ with $\sigma\ge 7/10$. Then we have

\[
R\lessapprox N^{2-2\sigma}+T^{1/2}N^{3-4\sigma}+\inf_{k\in\mathbb{N}}\Bigl(T^{\frac{k}{k+1}}N^{(4-6\sigma)\frac{k}{k+1}}+N^{(5-6\sigma)\frac{4k}{4k+3}}T^{\frac{2}{4k+3}}\Bigr).
\]

In particular, we have

\[
R\lessapprox N^{2-2\sigma}+T^{1/2}N^{3-4\sigma}+T^{(30\sigma-21)/5}N^{(46-60\sigma)/5}.
\]

\end{prpstn}

Proposition \ref{prpstn:BigN} implies that the $N^{18/5}V^{-4}$ term in Theorem \ref{thrm:LargeValues} can be replaced by $T^{1/2}N^{3-4\sigma}+T^{(30\sigma-21)/5}N^{(46-60\sigma)/5}$, which is smaller. When $\sigma=3/4$, Proposition \ref{prpstn:BigN} improves on \eqref{eq:ClassicalLargeValue} by a factor of $(T/N)^{1/2}$.  Since we anticipate the main uses of Theorem \ref{thrm:LargeValues} to be when $N<T^{5/6}$ we content ourselves with the simpler formulation of Theorem \ref{thrm:LargeValues}.
```

## GMRR Theorem 1 and constant

Input `gmrr-source/squfv.tex`, lines 88–99, citation [2].

```tex
\begin{theorem} \label{thm:main}
  Let $\varepsilon \in (0, \tfrac{1}{100})$ be given.
  Let $X \geq 1$ and $1 \le H \leq X^{6/11 - \varepsilon}$. Then 
  \begin{equation} \label{eq:main}
  \frac{1}{X} \int_{X}^{2X} \Big | \sum_{x < m \leq x + H} \mu^2(m) - \frac{6H}{\pi^2} \Big |^2 dx = C \sqrt{H} + O_{\varepsilon}(H^{1/2-\varepsilon/16})
  \end{equation}
  with 
  \begin{equation}\label{eq:C_dfn}
  C:= \frac{\zeta(3/2)}{\pi} \prod_p \Big(1 - \frac{3}{p^2} + \frac{2}{p^3}\Big).
  \end{equation}
  Assuming the Lindel\"of Hypothesis \eqref{eq:main} holds in the wider range $H \leq X^{2/3-\varepsilon}$.
\end{theorem}
```

## GMRR Proposition 1

Input `gmrr-source/squfv.tex`, lines 217–223, citation [2].

```tex
\begin{proposition} \label{pr:prop1}
  Let $\varepsilon \in (0, \tfrac{1}{100})$ be given.
  Let $X \geq 1$ and $X^{\varepsilon} \leq H \leq X^{2/3 - \varepsilon}$. Let $H^{1+\varepsilon} \leq z \leq \min\{X/H^{1/2+\varepsilon}, H^{1/2-\varepsilon}X^{1/2}\}$. Then, as $X \rightarrow \infty$, 
  \begin{equation} \label{eq:prop1}  \frac{1}{X} \int_{X}^{2X} \Big | \sum_{\substack{x < n d^2 \leq x + H \\ d^2 \le z}} \mu(d) - H \sum_{d^2 \le z} \frac{\mu(d)}{d^2} \Big |^2 \, dx = C \sqrt{H} + O(H^{1/2-\varepsilon/10})
    \end{equation}
    with $C$ as in~\eqref{eq:C_dfn}.
\end{proposition}
```

## GMRR Proposition 2 and limitations

Input `gmrr-source/squfv.tex`, lines 225–238, citation [2].

```tex
\begin{proposition} \label{pr:prop2}
  Let $\varepsilon \in (0, \tfrac{1}{100})$ be given. Let $X \geq 1$ and $X^{\varepsilon} \leq H \leq X^{4/7 - \varepsilon}$. Let $z \geq H^{4/3+\varepsilon}$. Then
  \begin{equation} \label{eq:prop2}
  \frac{1}{X} \int_{X}^{2X} \Big | \sum_{\substack{x < n d^2 \leq x + H \\ d^2 > z}} \mu(d) - H \sum_{\substack{2X \geq d^2 > z}} \frac{\mu(d)}{d^2} \Big |^2 dx \ll H^{1/2 - \varepsilon / 8}. 
  \end{equation}
  Assuming the Lindel\"of Hypothesis, the claim holds in the wider range $X^\varepsilon \leq H \leq X^{2/3-\varepsilon}$ and $z \geq H^{1+\varepsilon}$.
\end{proposition}

Under the assumption of the Lindel\"of Hypothesis, the above propositions cover all the possible values of $d^2$ for $X^{\varepsilon} \leq H \leq X^{2/3-\varepsilon}$. However, unconditionally they cover all the possible values of $d^2$ only for $X^{\varepsilon} \leq H \leq X^{6/(11+12\varepsilon)}$.
It would be possible to improve on the exponent $4/7$ in Proposition~\ref{pr:prop2}, but this would not help. Similarly it should be possible to prove Proposition \ref{pr:prop1} only with the condition $H^{1 + \varepsilon} \leq z \leq X / H^{1/2 + \varepsilon}$ by adapting the proof of Proposition \ref{prop:prop1q} below. 

We note that only the terms $d$ with $d^2 \in [H^{1 - \varepsilon}, H^{1 + \varepsilon}]$ contribute to the main term $C \sqrt{H}$ in Proposition \ref{pr:prop1}. 

Roughly speaking Proposition \ref{pr:prop1} depends only on ``convex" inputs such as a Fourier expansion and a point-counting lemma, whereas Proposition \ref{pr:prop2} exploits large value estimates of Huxley and subconvexity and fourth moment estimates for the Riemann zeta-function. 
```

## GMRR recombination and centering

Input `gmrr-source/squfv.tex`, lines 240–258, citation [2].

```tex
\begin{proof}[Proof of Theorem \ref{thm:main} assuming Proposition \ref{pr:prop1} and Proposition \ref{pr:prop2}]
Let $\varepsilon \in (0, \tfrac{1}{100})$. If $H \leq X^{\varepsilon}$ then the result already follows from Hall's theorem. We can therefore assume that $H > X^{\varepsilon}$. 

For $H \in [X^\varepsilon, X^{6/11-\varepsilon}]$, take $z = \min\{X/H^{1/2+\varepsilon}, H^{1/2-\varepsilon}X^{1/2}\}$. Note that $z \geq H^{4/3+\varepsilon}$. Denoting by $\mathcal{I}_1$ the left-hand side of \eqref{eq:prop1} and by $\mathcal{I}_2$ the left-hand side of \eqref{eq:prop2}, we get, using Cauchy-Schwarz, that
$$
\frac{1}{X} \int_{X}^{2X} \Big | \sum_{\substack{x < n d^2 \leq x + H}} \mu(d) - H \sum_{d^2 \leq 2X} \frac{\mu(d)}{d^2} \Big |^2 dx = \mathcal{I}_1 + O(\sqrt{\mathcal{I}_1 \mathcal{I}_2} + \mathcal{I}_2).
$$
Using the bounds in \eqref{eq:prop1} and \eqref{eq:prop2}, we conclude that
\begin{equation}
\label{eq:truncclaim}
\frac{1}{X} \int_{X}^{2X} \Big | \sum_{\substack{x < n d^2 \leq x + H}} \mu(d) - H \sum_{d^2 \leq 2X} \frac{\mu(d)}{d^2} \Big |^2 dx = C \sqrt{H} + O(H^{1/2 - \varepsilon / 16}).
\end{equation}
Notice that the tail $H\sum_{d^2 > 2X} \mu(d)/d^2$ is $\ll H/\sqrt{X}$. Hence the claim reduces to showing that
\[
\frac{1}{X} \int_{X}^{2X} \Big | \sum_{\substack{x < n d^2 \leq x + H}} \mu(d) - H \sum_{d^2 \leq 2X} \frac{\mu(d)}{d^2} \Big | \cdot \frac{H}{\sqrt{X}} + \Bigl(\frac{H}{\sqrt{X}}\Bigr)^2 dx \ll H^{1/2 - \varepsilon / 16}.
\]
Applying Cauchy-Schwarz and~\eqref{eq:truncclaim} we see that the left hand side
 is $\ll H^{1/4}(H/\sqrt{X}) + H^2/X \ll H^{1/2-\varepsilon/16}$ since $H \leq X^{2/3 - \varepsilon}$. 
\end{proof}
```

## GMRR fourth moment

Input `gmrr-source/squfv.tex`, lines 339–345, citation [2].

```tex
\begin{lemma}[Fourth moment estimate]
\label{le:ZetaFourth}
  Let $T \geq 2$. Then
  $$
  \int_{|t| \leq T} |\zeta(\tfrac 12 + it)|^4 dt \ll T (\log T)^4. 
  $$
\end{lemma}
```

## GMRR Weyl

Input `gmrr-source/squfv.tex`, lines 364–370, citation [2].

```tex
\begin{lemma}[Subconvexity estimate]
\label{le:ZetaSC}
One has, for $|t| \geq 2$,
\[
\zeta(1/2 + it) \ll |t|^{1/6} (\log |t|)^2.
\]
\end{lemma}
```

## GMRR Mellin reduction and time tail

Input `gmrr-source/squfv.tex`, lines 756–816, citation [2].

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
\end{align}
```

## GMRR low levels and unconditional proof

Input `gmrr-source/squfv.tex`, lines 831–859, citation [2].

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

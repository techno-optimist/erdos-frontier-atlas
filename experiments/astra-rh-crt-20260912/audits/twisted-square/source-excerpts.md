# Primary-source locators and verbatim excerpts

## Source [7], twisted-square/primary/bcr-v1/main.tex:199–206

```text
\begin{theorem} \label{thm:asymptotic}
  Let $I$ and $A (s)$ be as above. If $\theta < \tfrac{1}{2} + \delta$, with
  $\delta = \frac{1}{66}$ then,
  \est{ I &=  \sum_{d, e \leqslant T^{\theta}} \frac{a_d
     \overline{a_e}}{[d, e]} \cdot \int_\R \left( \log \left( \frac{t\, (d, e)^2}{2
     \pi de} \right) + 2 \gamma\right)\,{\phi} \pr{\frac tT} \mathd t + O \left( T^{\frac 3{20} + \varepsilon} N^{\frac{33}{20}} +T^{\frac13+\eps}\right) , }
where $N := T^{\theta}$. 
\end{theorem}
```

## Source [7], twisted-square/primary/bcr-v1/main.tex:347–359

```text
\begin{theorem}\label{thm:zetatimesproductoftwosmooth}
  Let $J, A (s)$ and $B (s)$ be as defined in~\eqref{eqn:defofJ} and~\eqref{afr}. Let $N \ll T^{\frac12+\eps}$
  for all $\eps>0$ and assume that $\alpha_n = \psi (n)$ with $\psi (x)$ a smooth
  function such that $\psi^{(j)} (x) \ll_j x^{-
  j}$ for all $j > 0$. Let $K\ll T^{\frac14}$ and $\beta_k \ll k^{\varepsilon}$ for all $\eps>0$. Moreover assume $\alpha_n$ is supported on $[N T^{-\xi_1}, 2N]$ and $\beta_k$ is supported on $[K T^{-\xi_2}, 2K]$, where $0\leq \xi_1\leq \frac15,$ $0\leq \xi_2\leq \frac1{16}$.  Then,
\est{    J & =  \sum_{d, e \leqslant NK} \frac{a_d 
      \overline{a_e
    }}{[d, e]} \cdot \int_\R \left( \log \left( \frac{t (d, e)^2}{2 \pi de} \right)
    + 2 \gamma \right)\phi\pr{\frac tT} \mathd t  +{}\\
    &\quad  + O \left( T^{\tfrac{1}{2} + \varepsilon } K^2 + KN^\frac34T^{\frac 38 + \eps} + \ T^{\frac{39}{40}+ \frac18\xi_1 + \frac{2}{5}\xi_2+ \eps}\right) ,
}
  where $a_d = \sum_{nk = d} \alpha_n \beta_k$.
\end{theorem}
```

## Source [7], twisted-square/primary/bcr-v1/main.tex:460–475

```text
We start by expressing $\pmd{\zeta\pr{\frac12+it}}^2$  as a sum of length approximately $T^{1+\eps}$. Let $G(w)$ be an entire function with rapid decay along vertical lines, that is $G(x + iy) \ll y^{-A}$ for any fixed $x$ and $A > 0.$ Suppose $G(-w) = G(w), G(0) =1, G(1/2) = 0$. 
We will use the following form of the approximate functional equation for
$|\zeta(s)|^2$. 

\begin{lemma}[Approximate functional equation] \label{lem:fncofZetasq}For $T < t < 2T,$ we have
\est{
\pmd{\zeta\pr{\frac12+it}}^2= 2 \sum_{m_1, m_2}\frac{1}{(m_1m_2)^{\frac12}}\pr{\frac{m_1}{m_2}}^{it}W\pr{\frac{2\pi m_1m_2}t} + O\left(T^{-2/3} \right),
}
where
\est{
W(x):= \frac{1}{2\pi i} \int_{(2)}x^{-w}G(w)\frac{dw}w,
}
and where we use the notation $\int_{(c)}$ to mean an integration up the vertical line from $c-i\infty$ to $c+i\infty$.

\end{lemma}
The proof of the lemma can be found in Lemma 3 of \cite{LR}.
```

## Source [7], twisted-square/primary/bcr-v1/main.tex:389–396

```text
\begin{prop}\label{prop:DFIimproved}
Let $\alpha_m$, $\beta_n$, $\nu_a$ be complex numbers, where $M \leq m < 2M,$ $N \leq n < 2N$, and $A \leq a < 2A$.  Then for any $\eps > 0$, we have
\es{\label{mpb}
\sum_a  \sumtwo_{(m,n) = 1} \nu_a\alpha_m \beta_n \e{\frac{a\overline{m}}{n}}&\ll_\eps \|\alpha\| \|\beta\|\|\nu\| \Big(1+\frac{A}{MN}\Big)^\frac{1}{2}\\
&\quad\times\hspace{-0.25em}\pr{(AMN)^{\frac7{20}+\eps}(M+N)^{\frac14}+(AMN)^{\frac38+\eps}(AN+AM)^\frac18},
}
where $\|\cdot\|$ denotes the $L_2$ norm.
\end{prop}
```

## Source [19], twisted-square/primary/bcr-deposited.txt:1–11

```text
=== PAGE 1 ===
J. reine angew. Math. 729 (2017), 51–79                                   Journal für die reine und angewandte Mathematik
DOI 10.1515/crelle-2014-0133                                                                                                      © De Gruyter 2017



  The mean square of the product of the Riemann
          zeta-function with Dirichlet polynomials

                 By Sandro Bettin at Montreal, Vorrapan Chandee at Chonburi and
                                      Maksym Radziwiłłat Princeton
```

## Source [8], twisted-square/primary/pr-v3/main.tex:110–145

```text
where $\alpha,\beta \ll (\log T)^{-1}$. We consider three cases for the coefficients $a_n$, namely
\begin{equation} \label{3cases}
a_n = \begin{cases}
O(n^\varepsilon), & \mbox{ for } \theta<\frac{17}{33}, \\
\mu^2(n) (\mu * \Lambda^{*k})(n)f(n), & \mbox{ with $f(n) \in \mathcal{F}$ and for } \theta<\frac{6}{11}, \\
\mu(n)f(n), & \mbox{ with $f(n) \in \mathcal{F}$ and for } \theta<\frac{4}{7}. 
\end{cases}
\end{equation}
Here $\mathcal{F}$ denotes the class of smooth functions given by
\[
f(n) = P\bigg( \frac{\log (N/n)}{\log N} \bigg),
\]
where $P(x)$ is a polynomial.

The third case $\mu(n)f(n)$ of \eqref{3cases} was studied by Conrey in 1989, and we call this third case the ``Levinson-Conrey,'' or simply ``Conrey,'' mollifier. The main innovations of this paper lie in studying the second case of \eqref{3cases}, and extending the range of $\theta$ for which one may prove an asymptotic formula. The second case  is colloquially known as the ``Feng'' mollifier, since it was first exploited in \cite{feng, krz01}.

The reason behind the choice of \eqref{generalI} needs to be explained. As it will be elaborated in $\mathsection$5, the presence of the terms $\alpha$ and $\beta$ is due to the fact that in order to compute the percentage of zeros on the critical line, one first computes $I(\alpha,\beta)$ and then sets $\alpha=\beta=-R/\log T$, where $R$ is a bounded positive real number of our choice (to be optimized). Therefore, the integral $I$ in \eqref{Iintegral} needs to be generalized to accommodate the variables $\alpha$ and $\beta$.

The strength of the result appearing in \cite{bcr} is the generality of $a_n$. However, often times applications of $I$ or $I(\alpha,\beta)$ allow for specialization of the shape of $a_n$. In fact, the mollifier encountered earlier to produce percentages of zeros requires that $a_n$ should be close to the M\"{o}bius function $\mu(n)$. The precise bonus coming from the shape $\mu^2(n) (\mu * \Lambda^{*k})(n)f(n)$ will be explained in $\mathsection$5. 

\subsection{Main result}
Set $L=\log T$. We are now in a position to state the results of the paper.
\begin{theorem} \label{theorem1}
Let $\alpha, \beta \ll L^{-1}$. Then one has
\begin{align}
  I(\alpha ,\beta ) = \sum\limits_{d,e \le N}  \frac{a_d \overline{a}_e}{[d,e]}\frac{(d,e)^{\alpha  + \beta }}{d^\alpha e^\beta }\int_{ - \infty }^\infty   \bigg( \zeta (1 + \alpha  + \beta ) + \zeta (1 - \alpha  - \beta )\bigg( \frac{2\pi de}{t(d,e)^2} \bigg)^{\alpha  + \beta } \bigg)\Phi\bigg(\frac{t}{T}\bigg)dt  + O(\mathcal{E}), \nonumber
\end{align}
with $\mathcal{E}$ given by the following cases
\begin{equation}
\mathcal{E} = \begin{cases}
T^{\frac{3}{20}} N^{\frac{33}{20}}+N^{1/2}T^{\frac{1}{2}+\varepsilon}, & \mbox{ if } \quad a_n \ll n^\varepsilon, \\
T^{\varepsilon}(N^{\frac{11}{6}}+N^{\frac{11}{12}}T^{\frac{1}{2}}), & \mbox{ if } \quad a_n =\mu^2(n) (\mu * \Lambda^{*k})(n)f(n), \\
T^{\varepsilon}(N^{\frac{7}{4}}+N^{\frac{7}{8}}T^{\frac{1}{2}}), & \mbox{ if } \quad a_n =\mu(n)f(n), \nonumber
\end{cases}
\end{equation}
with $f \in \mathcal{F}$. %Here $d\Phi = \Phi(\frac{t}{T})dt$.
```

## Source [17], twisted-square/primary/pr-publisher-page.txt:14–34

```text
Perturbed moments and a longer mollifier for critical zeros of
\(\zeta \)
Research
Published:
06 February 2018
Volume 4
, article number
9
(
2018
)
Cite this article
Save article
View saved research
Research in Number Theory
Aims and scope
Submit manuscript
Kyle Pratt
1
&
Nicolas Robles
```

## Source [13], twisted-square/primary/przz-v2/PRZZPOST.tex:769–798

```text
\section{Main result for the moment integral}
Recall that $L := \log T$ and let
\[
\psi_1(s) := \sum_{n \le N} \frac{a_n}{n^s}, \quad \psi_2(s) := \sum_{n \le N} \frac{b_n}{n^s}, \quad \textnormal{with} \quad a_n, b_n \ll_\varepsilon n^\varepsilon, \quad N:= T^{\theta} \quad \textnormal{and} \quad \theta<1.
\]
Moreover, we shall denote the twisted second moment by
\begin{align*}
I(\alpha,\beta) := \int_{-\infty}^\infty \zeta(\tfrac{1}{2}+\alpha+it)\zeta(\tfrac{1}{2}+\beta-it) \psi_1 \overline{\psi_2} (\tfrac{1}{2}+it) \Phi\bigg(\frac{t}{T}\bigg)dt,
\end{align*}
where $\Phi$ is a smooth function supported on $[1,2]$ and satisfying $\Phi^{(j)}(x) \ll_j \log^j T$. The starting point is the following improvement of \cite[Theorem 1.2]{pr01}.
\begin{theorem} \label{meanvalueintegral}
Let $\alpha, \beta \ll L^{-1}$. Then one has
\begin{align*}
I(\alpha,\beta) = \sumtwo_{1 \le d,e \le N}\frac{a_d \overline{b_e}}{[d,e]} \frac{(d,e)^{\alpha+\beta}}{d^\alpha e^\beta} \int_{-\infty}^\infty \bigg(\zeta(1+\alpha+\beta)+\zeta(1-\alpha-\beta)\bigg(\frac{2\pi de}{t(d,e)^2}\bigg)^{\alpha+\beta} \bigg)\Phi\bigg(\frac{t}{T}\bigg)dt + O(\mathcal{E}),
\end{align*}
with $\mathcal{E}$ given by the following choices
\begin{equation}
\mathcal{E} = 
\begin{cases}
T^{\frac{3}{20}}N^{\frac{33}{20}}+N^{\frac{1}{2}}T^{\frac{1}{2}+\varepsilon}, & \mbox{if} \quad a_n \ll n^{\varepsilon}, \\
T^{\varepsilon}(N^{\frac{11}{6}}+N^{\frac{11}{12}}T^{\frac{1}{2}}), & \mbox{if} \quad a_n = \mu^2(n) (\mu \star \Lambda_1^{\star k_1}\star \Lambda_2^{\star k_2} \star \cdots \star \Lambda_D^{\star k_D})(n), \\
T^{\varepsilon}(N^{\frac{7}{4}}+N^{\frac{7}{8}}T^{\frac{1}{2}}), & \mbox{if} \quad a_n =  (\mu \star \Lambda_1^{\star k_1}\star \Lambda_2^{\star k_2} \star \cdots \star \Lambda_D^{\star k_D})(n). \nonumber
\end{cases}
\end{equation}
%with $f \in \mathcal{F}$.
\end{theorem}

We note that the second case was only proved for $D=1$ in \cite{pr01}, but the proof below shows that it can be adapted to $D \ge 0$. This second case will no longer be needed as we can `improve' it to the third case by relaxing the condition that discriminates square-free numbers\footnote{It is not exactly an improvement but rather a different problem altogether.}. However, we leave it in the theorem for chronological accuracy or in case it becomes useful in another moment integral problem of this type. The first case (when $\alpha=\beta=0$) is due to Bettin, Chandee and Radziwi\l{}\l{} \cite{bcr}. As mentioned earlier, the key to that result is the recent improvement of bilinear Kloosterman sums of Duke, Friedlander and Iwaniec \cite{dfi} due to Bettin and Chandee \cite{bc}.

Effectively, this means that if one considers a Dirichlet polynomial whose coefficients are given by the third case, then one can `push' the size of $\theta$ from $\frac{6}{11}$ to $\frac{4}{7}$. Also note that if $D=0$ in the third case, then one recovers $\mu \star \Lambda^{\star 0} = \mu$, that is the Conrey-Levinson mollifier. This means that the Feng mollifier \cite{feng, krz01, rrz01} and all its generalizations can be taken to have size $\theta_d = \frac{4}{7} - \varepsilon$ for $D \ge 0$ just as in Conrey's mollifier.
```

## Source [18], twisted-square/primary/przz-publisher.txt:1240–1289

```text
                                                                 4          Main    result    for    the    moment    integral
                                                                 Recall     that         L     :=     log       T       and     let
                                                                                      ψ1 (s):=     ∑                                              an                                                    =     ∑                        bn                                                                                                                                       :=           T   θ                     and           θ<1.
                                                                                                                                                   ns         ,                         ψ2 (s):                                         ns         ,                     with                                   an ,bn          ≪       ε             nε ,N
                                                                                                                              n≤N                                                                                  n≤N
                                                                 Moreover,     we     shall     denote     the     twisted     second     moment     by
                                                                                                                                   ∫∞                                                                                                                                                                                                              (           t    )
                                                                                      I  (α  ,    β ):=                                                             2          +     α        +        it )ζ   (  12          +     β         −        it )ψ1ψ2 (  12          +        it )Φ                                                              T               d t,
                                                                                                                                         −∞     ζ   (  1

                                                                 where       Φ       is      a      smooth      function      supported      on      [1,   2]      and      satisfying       Φ (j ) (x)           ≪            j         log j         T .The
                                                                 starting     point     is     the     following     improvement     of     [58,     Theorem     1.2].

                                                                 Theorem         4.1                       Let     α  ,    β          ≪                       L−1 .Then,onehas

                                                                                      I  (α  ,    β )        =   ∑∑adbe                                                                      (d,      e)α +β
                                                                                                                                 1≤d,e≤N                             [d,      e]                     d α   eβ
                                                                                                                                         ∫∞                     (                                                                                                                                     (         2π    de                      )      α +β )                           (           t     )
                                                                                                                               ×                                       ζ   (1       +     α        +     β )       +     ζ   (1       −     α        −     β )                                                t (d,      e)2                                                 Φ                T                d t         +        O(E  ),
                                                                                                                                               −∞

=== PAGE 22 ===
2                                      Page       22       of       74                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           K.Prattetal.Res      Math      Sci        (2020)       7:2




                                   with             E            given         by         the         following         choices
                                                           ⎧         3        33                1       1
                                                           ⎪T       20       N20            +        N2       T2    +ε,ifa
                                                           ⎪                                                                           n          ≪                       nε   ,
                                                           ⎨                  11               11       1                                                                      ⋆k1             ⋆k2                          ⋆kD
                                               E           =⎪T   ε (N         6                +        N12       T2   ),ifan          =      μ2 (n)(μ⋆/Lambda11              ⋆/Lambda12                      ⋆··· ⋆/Lambda1D              )(n),
                                                           ⎪                  7              7       1
                                                           ⎩T   ε (N          4            +        N8       T2   ),ifan          =     (μ⋆/Lambda1⋆k1                            ⋆k2                         ⋆kD
                                                                                                                                                                 1              ⋆/Lambda12                      ⋆··· ⋆/Lambda1D              )(n).

                                        We      note      that      the      second      case      was      only      proved      for           D           =    1in[58],      but      the      proof      below
                                   shows     that     it     can     be     adapted     to          D          ≥       0.     This     second     case     will     no     longer     be     needed     as     we
                                   can     ‘improve’     it     to     the     third     case     by     relaxing     the     condition     that     discriminates     square-free
                                   numbers.2       However,      we      leave      it      in      the      theorem      for      chronological      accuracy      or      in      case      it
                                   becomes      useful      in      another      moment      integral      problem      of      this      type.      The      ﬁrst      case      (when
                                   α          =       β           =      0)     is     due     to     Bettin,     Chandee     and     Radziwiłł     [4].     As     mentioned     earlier,     the     key     to
                                   that     result     is     the    recent     improvement    of     bilinear    Kloosterman     sums     of     Duke,     Friedlander
                                   and     Iwaniec     [29]     due     to     Bettin     and     Chandee     [3].
                                        Eﬀectively,      this      means      that      if      one      considers      a      Dirichlet      polynomial      whose      coeﬃcients
                                   are     given     by     the     third     case,     then     one     can     ‘push’     the     size     of      θ       from           611       to       47   .     Also     note     that
                                   if          D           =       0     in     the     third     case,     then     one     recovers    μ⋆/Lambda1⋆0            =        μ,     that     is     the     Conrey–Levinson
                                   molliﬁer.     This     means     that     the     Feng     molliﬁer     [33,  48,  60]     and     all     its     generalizations     can     be
                                   taken     to     have     size     θd           =        47          −     ε     for         D         ≥     0     just     as     in     Conrey’s     molliﬁer.
```

## Source [9], twisted-square/primary/wu-v2/main.tex:199–218

```text
\begin{theorem}\label{thm1}
Let $\chi$ be a primitive Dirichlet character (mod $q$) with $\log q=o(\log T)$ and $\alpha=a/\mathcal{L}_\chi,~\beta=b/\mathcal{L}_\chi$ with $a,~b\in\mathbb{C}$ and $a,~b\ll1$. Let $I_R(Q,\chi)$ be defined as in \eqref{x1.6}. Suppose that $a(m)\ll_\epsilon m^{\epsilon}$ for any $\epsilon>0$ and $y=T^\theta$, then we have
\begin{align}\label{+1.10}
I_R(Q,\chi)&=TQ\bigg(\frac{-d}{da}\bigg)\overline{Q}\bigg(\frac{-d}{db}\bigg) \Bigg\{\sum_{h,k\le y}\frac{\chi_0(hk)(h,k)^{\alpha+\beta}a(h)\overline{a(k)}}{h^{1+\beta} k^{1+\alpha}}\\
&\times\Bigg(\frac{2^{1+\alpha+\beta}-1}{1+\alpha+\beta}\bigg(\frac {2\pi hk}{qT(h,k)^2}\bigg)^{\alpha+\beta}L(1-\alpha-\beta,\chi_0) +L(1+\alpha+\beta,\chi_0)\Bigg)\Bigg\}\Bigg|_{a=b=-R}+O(T^{1-\epsilon_\theta}),\notag
\end{align}
and, in the particular case $\alpha=\beta=0$,
\begin{align}\label{+1.12}
I(\chi)=T\frac{\phi(q)}{q}\sum_{h,k\le y}\frac{a(h)\overline{a(k)}}{[h,k]}\chi_0(hk)\bigg(\log\frac{Tq(h,k)^2}{2\pi HK}+2\gamma-1+c_q+2\log2)\bigg)+O(T^{1-\epsilon_\theta})
\end{align}
with $c_q=\sum_{p\mid q}(\log p)/(p-1)$ and $\gamma$ is the Euler's constant. Here $\epsilon_\theta$ is a constant depending on $\theta$ as follows:
\begin{description}
  \item[(A)] In general, we have $\epsilon_\theta>0$ for any given $\theta<\frac{17}{33}$;
  \item[(B)] We have $\epsilon_\theta>0$ for any given $\theta<\frac{4}{7}$ when $a(n)$ has a special form
\begin{align}
a(n)=\mu(n)(\mathcal{F}_0+\mathcal{F}_1\cdot(\mathcal{F}_2*\mathcal{F}_3))(n)\notag
\end{align}
with $\mathcal{F}_i$ separable in $\mathbb{F}=\big\{\mathcal{F}:\mathcal{F}(x)\ll_\epsilon x^\epsilon,~ \mathcal{F}'(x)\ll\frac1x\big\}$ for $0\le i\le 3$. In addition, it also holds when one of $\mathcal{F}_2$ and $\mathcal{F}_3$ is separable in $\big\{\mathcal{F}:\mathcal{F}(x)\ll_\epsilon x^\epsilon,~\mathcal{F}(x)=0\ \ \text{for}\ \ x> y^{\frac34}\big\}$ and other $\mathcal{F}_i$ are separable in $\mathbb{F}$.
\end{description}
\end{theorem}
```

## Source [10], twisted-square/primary/yu-v2/main.tex:165–181

```text
\begin{theorem}\label{thm1}
    Let $T,Y > 0$ with $C_1T<Y<C_2T$ and $T\ge C^{\star}=\max\{e,\ C_1^{-1}\}$, where $C_1$ and $C_2$ are fixed constants with $0<C_1<C_2$. Then for $1/4<\sigma<1/2$ we have
    $$\int_T^{2T} |\zeta(\sigma+it)A(\sigma+it)|^2dt=\mathcal{M}(2T,A)+\Sigma_1(2T,2Y)+\Sigma_2(2T,\xi(2T,2Y))$$
$$-\mathcal{M}(T,A)-\Sigma_1(T,Y)-\Sigma_2(T,\xi(T,Y))+R(T,2T,A),$$
where $R(T,2T,A)$ is the error term satisfying
$$R(T,2T,A)\ll_{M} T^{1-2\sigma}\log(T).$$
\end{theorem}
\begin{theorem}\label{thm2}
    Under the same assumptions as in Theorem\ref{thm1}, we have
    \begin{align*}
        E(T,A;\sigma)=I(T,A;\sigma)-\mathcal{M}(T,A)=\Sigma_1(T,Y)+\Sigma_2(T,\xi(T,Y))+R(T,A)
    \end{align*}
    with 
    \begin{align*}
        R(T,A)\ll _M\log^{(2-2\sigma)\alpha}(T)+\log^{(3/2-2\sigma+\varepsilon)\alpha}(T)+\log^{\alpha}(T)\log T+ T^{1-2\sigma}\log^2 T
    \end{align*}
    for any $\alpha>0$.
```

## Source [11], twisted-square/primary/khan-v1/2nd-moment-zeta.tex:100–124

```text
\begin{theorem}\label{main}
Let $p$ and $q$ be distinct odd primes. Let $T>1$. We have
\begin{align}
\label{thmline} \intt \Big(\frac{p}{q}\Big)^{it} |\zeta(\thalf+it)|^2 & \exp\Big(-\frac{t^2}{T^2}\Big)   dt  \\
\nonumber &=  \Big(\frac{\pi}{pq}\Big)^\half T\Big( \log \Big(\frac{T}{2\pi pq}\Big)+2\gamma+\half \frac{\Gamma'}{\Gamma}\Big(\half\Big)\Big)\\
\nonumber &\ +  \Big( \frac{T}{2\pi}\Big)^\half    \frac{p^\half }{p-1} \summ_{\substack{\chi\bmod p\\ \chi(-1)=1}}  \chi(q)  \ \intt \Gamma\Big(\frac{1-2it}{4}\Big) \Big( \frac{T}{2 q}\Big)^{it}  |L(\thalf+it,\chi)|^2 \ dt\\
\nonumber &\ +O \left((pqT)^\epsilon \Big(\frac{q}{p} \Big)^\half +  (pqT)^\epsilon \Big(\frac{p}{q} \Big)^\half  \right).
\end{align}
\end{theorem}
\noindent Since $\Gamma(\frac{1-2it}{4}) $ decays exponentially fast as $|t|\to\infty$, we should think of the dual moment integral as essentially being of finite length. We can also see that the dual moment is real, by pairing the contributions of $t$ and $-t$ and using that the complex conjugate of $\Gamma(\frac{1-2it}{4}) ( \frac{T}{2 q})^{it}$ is $\Gamma(\frac{1+2it}{4}) ( \frac{T}{2 q})^{-it}$, and pairing the contributions of $\chi$ and $\overline{\chi}$ when $\chi$ is not real.

Observe that the moment on the left hand side of \eqref{thmline} remains invariant if we interchange $p$ and $q$, by the substitution $t\to -t$ and the fact that $ \exp(-\frac{t^2}{T^2})$ is an even function. All other terms on the right hand side are also clearly symmetric in $p\leftrightarrow q$, except, at first glance, the dual moment. However we are reassured by the reciprocity relation \eqref{dirrec} which tells us that such expressions may be symmetric in $p\leftrightarrow q$. In fact, this {\it must} be the case as a direct consequence of our reciprocity relation \eqref{thmline}. So our reciprocity relation contains another one for free.
\begin{corollary}
Let $p$ and $q$ be distinct odd primes. Let $T>1$. We have
\begin{multline}
\label{corline}  \frac{p^\half }{p-1} \summ_{\substack{\chi\bmod p\\ \chi(-1)=1}}  \chi(q)  \ \intt \Gamma\Big(\frac{1-2it}{4}\Big) \Big( \frac{T}{2 q}\Big)^{it}  |L(\thalf+it,\chi)|^2 \ dt \\
 =  \frac{q^\half }{q-1} \summ_{\substack{\chi\bmod q\\ \chi(-1)-1}}  \chi(p)  \ \intt  \Gamma\Big(\frac{1-2it}{4}\Big) \Big( \frac{T}{2 p}\Big)^{it}  |L(\thalf+it,\chi)|^2 \ dt+O \left((pqT)^\epsilon \Big(\frac{q}{pT} \Big)^\half +  (pqT)^\epsilon \Big(\frac{p}{qT} \Big)^\half  \right).
\end{multline}
\end{corollary}
\noindent Unlike \eqref{dirrec}, we do not have a main term because of the extra oscillation arising from the integral. Also note that the error term $O((pqT)^\epsilon (\frac{p}{qT})^\half )$ is the expected order of magnitude for the moment on the left hand side of \eqref{corline}, while $O((pqT)^\epsilon (\frac{q}{pT})^\half )$ is the expected order of magnitude for the dual moment on the right hand side. Such expectations however are known in only limited ranges, as we discuss in the next paragraph, so \eqref{corline} is non-trivial.


Going back to the reciprocity relation \eqref{dirrec}, one interesting consequence is the following. While an asymptotic is known \cite[Corollary 2]{bet} for the moment on the left hand side for $p<q^{\half-\epsilon}$, by \eqref{dirrec} we have an asymptotic for the {\it difference} between the moment on the left hand side and the dual moment on the right hand side in the wider range $p<q^{1-\epsilon}$. To see that we get the analogue of this for the Riemann Zeta function, suppose that $p\asymp q$. While an asymptotic is known for the moment on left hand side of \eqref{thmline} only for $p<T^{\half-\epsilon}$, we get an asymptotic for the {\it difference} between the moment on the left hand side and the dual moment on the right hand side in the wider range $p<T^{1-\epsilon}$. 

We have tried to present the reciprocity relation in a straightforward form, and therefore opted to make some simplifications. We have worked with prime twists in Theorem \ref{main}, although this restriction is not a serious one. For general integer value twists, the entire proof would go through in the same way but the orthogonality property of primitive Dirichlet characters, used in \eqref{dirchar} and \eqref{2nd}, would be more complicated than the prime case. We have also worked with the specific weight function  $\exp(-\frac{t^2}{T^2})$ on the left hand side of \eqref{thmline} so that all transforms which arise can be explicitly evaluated. 
```

## Source [27], twisted-square/primary/khan-final.txt:68–141

```text
Theorem 1.  Let p and q  be distinct odd primes.  Let T > 1.  We have
(1.2)Z ∞
           p it|ζ( 1
                     2 +it)|2 exp      − t2     dt
     −∞     q                             T 2
                                    π     12T         T                    Γ′  1
                                =    pq         log   2πpq     + 2γ + 12   Γ    2
                                     T     1     1    X⋆             Z ∞      1− 2it      T    it|L( 1
                                           2 p2
                                 +    2π     p− 1             χ(q)                4        2q         2 +it,χ)|2 dt
                                                     χ modp           −∞ Γ
                                                    χ(−1)=1
                                                       1                  1
                                                       2 + (pqT)ϵ p       2
                                 +O      (pqT)ϵ qp                    q       .

Since Γ( 1−  2it4   ) decays exponentially fast as|t|→∞ , we should think of the dual moment integral
as essentially being of finite length.  We can also see that the dual moment is real, by pairing the
contributions oft and−t and using that the complex conjugate of Γ( 1−  2it4   )(T2q  )it is Γ( 1+2it4   )(T2q  )−it,
and pairing the contributions of χ and           χ when χ is not real.
   Observe that the moment on the left hand side of (1.2) remains invariant if we interchange p and
q, by the substitution t→−t and the fact that exp(−t2T 2 ) is an even function.  All other terms on
the right hand side are also clearly symmetric in p↔ q, except, at first glance, the dual moment.
However we are reassured by the reciprocity relation (1.1) which tells us that such expressions may
be symmetric in p↔ q.  In fact, this  must be the case as a direct consequence of our reciprocity
relation (1.2).  So our reciprocity relation contains another one for free.
Corollary 2.  Let p and q  be distinct odd primes.  Let T > 1.  We have

            1     X⋆            Z ∞      1− 2it      T     it|L( 1
            2
(1.3)   pp− 1            χ(q)                 4        2q         2 +it,χ)|2 dt
                χ modp            −∞ Γ
                χ(− 1)=1
       1                   Z ∞      1− 2it      T     it|L( 1                                      1                    1
       2     X⋆                                                                                    2 + (pqT)ϵ  p        2
= qq− 1             χ(p)                4        2p         2+it,χ)|2dt+O          (pqT)ϵ  qpT                    qT        .
           χ modq            −∞ Γ
           χ(−1)−1
Unlike (1.1), we do not have a main term because of the extra oscillation arising from the integral.
                                                       1
Also note that the error term O((pqT)ϵ( pqT )2 ) is the expected order of magnitude for the moment

                                                              1
on the left hand side of (1.3), whileO((pqT)ϵ( qpT )2 ) is the expected order of magnitude for the dual
moment on the right hand side.  Such expectations however are known in only limited ranges, as we
discuss in the next paragraph, so (1.3) is non-trivial.
   Going back to the reciprocity relation (1.1), one interesting consequence is the following.  While
                                                                                                                  1
an  asymptotic  is  known  [2,  Corollary  2]  for  the  moment  on  the  left  hand  side  for p < q             2−ϵ,  by
(1.1) we have an asymptotic for the  difference between the moment on the left hand side and the
dual moment on the right hand side in the wider range p<q1− ϵ.  To see that we get the analogue
of this for the Riemann Zeta function, suppose that p≍ q.  While an asymptotic is known for the

=== PAGE 3 ===
 A  RECIPROCITY  RELATION  FOR  THE  TWISTED  SECOND  MOMENT  OF  THE  RIEMANN  ZETA  FUNCTION 3


                                                         1
moment on left hand side of (1.2) only forp<T            2−ϵ, we get an asymptotic for the difference between
the moment on the left hand side and the dual moment on the right hand side in the wider range
p<T 1−ϵ.
   We have tried to present the reciprocity relation in a straightforward form, and therefore opted
to  make  some  simplifications.   We  have  worked  with  prime  twists  in  Theorem  1,  although  this
restriction is not a serious one.  For general integer value twists, the entire proof would go through
in the same way but the orthogonality property of primitive Dirichlet characters, used in (3.8) and
(3.9), would be more complicated than the prime case. We have also worked with the specific weight
function exp(−t2T 2 ) on the left hand side of (1.2) so that all transforms which arise can be explicitly
evaluated.
   Instead of considering a second moment of the Riemann Zeta function along a dyadic interval with
twists as long as possible, one may consider the opposite scenario of an untwisted second moment
along  as  short  an  interval  as  possible,  say  using  a  weight  function  exp(− (t− T )2H2   )  with H ≤ T.
The dual moment in this case would be a second moment of the Riemann Zeta function against a
transform function with (inverted) support of size TH .  We do not pursue this as it may already be
derivable from an Atkinson type formula [12, Theorem 4.1].
```

## Source [24], twisted-square/primary/khan-nsf-page.txt:92–103

```text
PAR ID:
10585520
Author(s) / Creator(s):
Khan, Rizwanur
Publisher / Repository:
American Mathematical Society
Date Published:
2025-01-01
Journal Name:
Proceedings of the American Mathematical Society
Volume:
153
```

## Source [28], twisted-square/primary/amplified-v2/main.tex:348–376

```text
\subsection{Amplified moments}
A natural way to probe higher moments is via twisted and amplified mean values. Given a Dirichlet polynomial

$$A(s)=\sum_{n\le y}\frac{a(n)}{n^s} \qquad (a(n)\ll n^{\varepsilon})$$
with $y$ given by a power of $T$, one would like to choose $a(n)$ so as to model high powers of $\zeta(s)$. There are two natural and complementary ways to encode such powers.

\begin{itemize}
    \item In one approach, used recently by Bui, Hall and Subira Jorge \cite{bui2025amplified}, one chooses $A(s)$ so that its coefficients mimic those of $\zeta(s)^r$ for some $r>0$, for instance $a(n)\approx d_r(n)$ where $d_r(n)$ are the $r$-fold divisor coefficients.
    \item In the present paper we adopt a different point of view. We fix a relatively short Dirichlet polynomial $A(s)$ of length $y=T^{\theta_k}$ or $y=T^{\vartheta_k}$ for twisted second and fourth moments respectively, with smooth polynomial coefficients 
    
    \begin{equation}\label{eqn:smooth_coeffs}
        P[n]=P\left(\frac{\log(y/n)}{\log y}\right),
    \end{equation}
for $1\le n\le y$ where $P(x)=\sum_{j\ge 0}c_jx^j$ is a certain polynomial with real coefficients. We set also $P[n]=0$ for $n\ge y$ by convention.
    \
    We allow arbitrary even powers $|A|^{2k}$ to appear inside twisted moments of zeta. From the perspective of modelling $\zeta(s)^{2k}$, this amounts to representing large powers of $\zeta(s)$ by the product $|A(\tfrac{1}{2}+it)|^{2k}$, rather than by a single long Dirichlet polynomial with divisor-type coefficients.
\end{itemize}

\vspace{2mm}

These two frameworks behave rather differently analytically. In our setup, the presence of the high power $|A|^{2k}$ forces the admissible exponent to decrease with $k$ for the twisted second moment we can take $\theta_k< \tfrac{1}{2k}$, while for the twisted fourth moment we require $\vartheta_k< \tfrac{1}{4k}$. In particular, our method does not recover the phenomenon of \cite{bui2025amplified} that one can take amplifiers of length $T^{1/8-\varepsilon}$ uniformly in $k$. On the other hand, the polynomial structure of the coefficients and the flexibility in the amplifier power make our approach very effective for acquiring bounds on joint moments. We note that our coefficients are chosen to be polynomial, largely for technical convenience -- with a much more technical argument one should be able to modify our results to handle more general coefficients $a(n)$.

In what follows we focus on twisted second and fourth moments with a high power of the amplifier attached, namely integrals of the form

\begin{equation}\label{eqn:twists}
\int_0^T|\zeta(\tfrac{1}{2}+it)|^2|A(\tfrac{1}{2}+it)|^{2k}\;dt, \ \ \ \ \ \ \ \int_0^T|\zeta(\tfrac{1}{2}+it)|^4|A(\tfrac{1}{2}+it)|^{2k}\;dt
\end{equation}

with $A$ of length $T^{\theta_k}$ in the twisted second moment and length $T^{\vartheta_k}$ in the twisted fourth moment. The case $k=1$ in the second moment was treated by Balasubramanian, Conrey and Heath-Brown \cite{BCHB} to handle Dirichlet polynomials with length up to $T^{1/2-\delta}$; for general coefficients this range has since been pushed slightly beyond $T^{1/2}$ by Bettin, Chandee and Radziwi{\l}{\l} \cite{BCR}. Any improvement to the length of the permissible Dirichlet polynomial for the twisted second moment would automatically yield a stronger result for our twisted second moment.
```

## Source [28], twisted-square/primary/amplified-v2/main.tex:466–494

```text
\begin{thm}\label{thm:Ik0}

We have, for $\theta_k < \frac{1}{2k}$,

\begin{align*}
\mathcal{I}_{k,0}(\alpha_1,\alpha_2)&= a_{k+1}T \log T \, (\log y)^{k^2+2k}\,\widehat{\Phi}(0)  \int_0^1 \int_{\substack{
0 \leq t_{i,j} \leq 1 \\0 \leq x_i, w_i \leq 1 }} 
\int_{\substack{
\sum_{j=1}^k t_{i,j} +w_i\le 1 \\
\sum_{i=1}^k t_{i,j} +x_j \le 1 }} 
\\
&\qquad \times y^{-\alpha_1\sum_{i=1}^k w_i-\alpha_2\sum_{i=1}^k x_i} \left(1-\theta_k  \sum_{i=1}^{k} (w_i +x_i)  \right)
\left(Ty^{-\sum_{i=1}^{k} (w_i +x_i)}\right)^{-v (\alpha_1+\alpha_2)}
\\
&\qquad \times
\prod_{i =1}^k
P\left(1-\sum_{j=1}^k t_{i,j} -w_i \right)
\prod_{j=1}^k
P\left(1-\sum_{i=1}^k t_{i,j} -x_j \right)
\,
\\
&\qquad 
dv \, 
dt_{1,1}\cdots dt_{k,k} \, 
dw_1 \cdots dw_{k} \,
dx_1 \cdots dx_k   
+ O\left(T(\log T)^{(k+1)^2-1}\right).
\end{align*}
\end{thm}
```

## Source [23], twisted-square/primary/amplified-abs.html:173–177

```text
      <h2>Submission history</h2> From: Benjamin Durkan [<a href="/show-email/2610aff3/2606.27323" rel="nofollow">view email</a>]      <br/>            <strong><a href="/abs/2606.27323v1" rel="nofollow">[v1]</a></strong>
        Thu, 25 Jun 2026 17:36:12 UTC (104 KB)<br/>
    <strong>[v2]</strong>
        Wed, 5 Aug 2026 12:32:00 UTC (119 KB)<br/>
</div>
```

## Source [12], twisted-square/primary/tang-v1/main.tex:170–192

```text
\begin{thm}\label{thm1}
    Let $p,q$ be distinct odd primes, $T>1$ and $H=T^{\delta}$ for $\delta \in \lc \h,1 \rc$. We have
    \begin{equation}\label{eqthm1}
    \begin{aligned}
        \inftyInt \lc \frac{p}{q} \rc^{it} &\lv \zeta\lc \tfrac{1}{2}+it \rc \rv^2 \exp\lc -\frac{(t-T)^2}{H^2} \rc dt =\\
        &\frac{2 \pi}{\sqrt{pq}}\lc G_{T,H}'(1)-G_{T,H}(1)\log(pq)+2\gamma G_{T,H}(1) \rc \\
        &+ \sumstar_{\chi \bmod p} \frac{\sqrt{p}}{i^{\alpha}(p-1)}\chi(q) \inftyInt G_{T,H}\lc \tfrac{1}{2}+it \rc \lc \frac{\pi}{q}\rc^{it} \frac{\Gamma \lc \frac{1+2\alpha-2it}{4} \rc}{\Gamma \lc \frac{1+2\alpha+2it}{4} \rc} \lv L\lc \tfrac{1}{2}+it,\chi \rc \rv^2 dt\\
        &+ O\lc \frac{T}{H}(pqT)^{\epsilon} \left[\lc \frac{p}{q} \rc^{\h} + \lc \frac{q}{p} \rc^{\h} \right] \rc,
    \end{aligned}
    \end{equation}
    for $\alpha= 0$ if $\chi(-1)=1$ and $\alpha=1$ if $\chi(-1)=-1$.
\end{thm}
By Lemma \ref{mellin2}, the main term of \eqref{eqthm1} has size 
\begin{equation}
    \frac{1}{\sqrt{pq}}\lc G_{T,H}'(1)-G_{T,H}(1)\log(pq)+2\gamma G_{T,H}(1)\rc \asymp \frac{H}{\sqrt{pq}}\log\lc \frac{T}{pq} \rc.
\end{equation}
Moreover, as shown by Lemma \ref{weight}, $G_{T,H}\lc \tfrac{1}{2}+it \rc$ decays rapidly for $\lv t \rv \gg \frac{T}{H}$. Thus, the integral in the dual moment is essentially supported on an interval of length $\frac{T}{H}$. Two types of reciprocity appear in our result. The first is a type of arithmetic reciprocity which was already presented in Khan's result. The second is a type of analytic reciprocity in which the original length of support $H$ is transformed into $\frac{T}{H}$ in the dual moment.

Another objective of this paper is to observe the relation between the size of twisting parameter and the length of interval of integral. In general, the twisting parameter cannot be arbitrarily large, while the integral cannot be supported on an interval that is arbitrarily small. However, the relation between these two quantities has not been made explicit in previous results. In our result, this relation is given by 
\begin{equation}
    \frac{H^2}{\max\{p,q\}}>T^{1+\epsilon},
\end{equation}
which follows naturally from requiring the main term to dominate the error term. We comment in Remark \ref{remark1} how our lower bound on $H$ arises, and on the possibility of improvement.
```

## Source [22], twisted-square/primary/amplified-v1/main.tex:348–376

```text
\subsection{Amplified moments}
A natural way to probe higher moments is via twisted and amplified mean values. Given a Dirichlet polynomial

$$A(s)=\sum_{n\le y}\frac{a(n)}{n^s} \qquad (a(n)\ll n^{\varepsilon})$$
with $y$ given by a power of $T$, one would like to choose $a(n)$ so as to model high powers of $\zeta(s)$. There are two natural and complementary ways to encode such powers.

\begin{itemize}
    \item In one approach, used recently by Bui, Hall and Subira Jorge \cite{bui2025amplified}, one chooses $A(s)$ so that its coefficients mimic those of $\zeta(s)^r$ for some $r>0$, for instance $a(n)\approx d_r(n)$ where $d_r(n)$ are the $r$-fold divisor coefficients.
    \item In the present paper we adopt a different point of view. We fix a relatively short Dirichlet polynomial $A(s)$ of length $y=T^{\theta_k}$ or $y=T^{\vartheta_k}$ for twisted second and fourth moments respectively, with smooth polynomial coefficients 
    
    \begin{equation}\label{eqn:smooth_coeffs}
        P[n]=P\left(\frac{\log(y/n)}{\log y}\right),
    \end{equation}
for $1\le n\le y$ where $P(x)=\sum_{j\ge 0}c_jx^j$ is a certain polynomial with real coefficients. We set also $P[n]=0$ for $n\ge y$ by convention.
    \
    We allow arbitrary even powers $|A|^{2k}$ to appear inside twisted moments of zeta. From the perspective of modelling $\zeta(s)^{2k}$, this amounts to representing large powers of $\zeta(s)$ by the product $|A(\tfrac{1}{2}+it)|^{2k}$, rather than by a single long Dirichlet polynomial with divisor-type coefficients.
\end{itemize}

\vspace{2mm}

These two frameworks behave rather differently analytically. In our setup, the presence of the high power $|A|^{2k}$ forces the admissible exponent to decrease with $k$ for the twisted second moment we can take $\theta_k< \tfrac{1}{2k}$, while for the twisted fourth moment we require $\vartheta_k< \tfrac{1}{4k}$. In particular, our method does not recover the phenomenon of \cite{bui2025amplified} that one can take amplifiers of length $T^{1/8-\varepsilon}$ uniformly in $k$. On the other hand, the polynomial structure of the coefficients and the flexibility in the amplifier power make our approach very effective for acquiring bounds on joint moments. We note that our coefficients are chosen to be polynomial, largely for technical convenience -- with a much more technical argument one should be able to modify our results to handle more general coefficients $a(n)$.

In what follows we focus on twisted second and fourth moments with a high power of the amplifier attached, namely integrals of the form

\begin{equation}\label{eqn:twists}
\int_0^T|\zeta(\tfrac{1}{2}+it)|^2|A(\tfrac{1}{2}+it)|^{2k}\;dt, \ \ \ \ \ \ \ \int_0^T|\zeta(\tfrac{1}{2}+it)|^4|A(\tfrac{1}{2}+it)|^{2k}\;dt
\end{equation}

with $A$ of length $T^{\theta_k}$ in the twisted second moment and length $T^{\vartheta_k}$ in the twisted fourth moment. The case $k=1$ in the second moment was treated by Balasubramanian, Conrey and Heath-Brown \cite{BCHB} to handle Dirichlet polynomials with length up to $T^{1/2-\delta}$; for general coefficients this range has since been pushed slightly beyond $T^{1/2}$ by Bettin, Chandee and Radziwi{\l}{\l} \cite{BCR}. Any improvement to the length of the permissible Dirichlet polynomial for the twisted second moment would automatically yield a stronger result for our twisted second moment.
```

## Source [22], twisted-square/primary/amplified-v1/main.tex:466–494

```text
\begin{thm}\label{thm:Ik0}

We have, for $\theta_k < \frac{1}{2k}$,

\begin{align*}
\mathcal{I}_{k,0}(\alpha_1,\alpha_2)&= a_{k+1}T \log T \, (\log y)^{k^2+2k}\,\widehat{\Phi}(0)  \int_0^1 \int_{\substack{
0 \leq t_{i,j} \leq 1 \\0 \leq x_i, w_i \leq 1 }} 
\int_{\substack{
\sum_{j=1}^k t_{i,j} +w_i\le 1 \\
\sum_{i=1}^k t_{i,j} +x_j \le 1 }} 
\\
&\qquad \times y^{-\alpha_1\sum_{i=1}^k w_i-\alpha_2\sum_{i=1}^k x_i} \left(1-\theta_k  \sum_{i=1}^{k} (w_i +x_i)  \right)
\left(Ty^{-\sum_{i=1}^{k} (w_i +x_i)}\right)^{-v (\alpha_1+\alpha_2)}
\\
&\qquad \times
\prod_{i =1}^k
P\left(1-\sum_{j=1}^k t_{i,j} -w_i \right)
\prod_{j=1}^k
P\left(1-\sum_{i=1}^k t_{i,j} -x_j \right)
\,
\\
&\qquad 
dv \, 
dt_{1,1}\cdots dt_{k,k} \, 
dw_1 \cdots dw_{k} \,
dx_1 \cdots dx_k   
+ O\left(T(\log T)^{(k+1)^2-1}\right).
\end{align*}
\end{thm}
```

## Source [21], twisted-square/primary/lr-v1/draft.tex:994–1014

```text
Let $G(\cdot)$ be an entire function with rapid decay along vertical lines, 
that is $G(x + iy) \ll |y|^{-A}$ for any fixed $x$ and $A > 0$.
Suppose also that $G(-w) = G(w)$, $G(0) = 1$
and $\overline{G(w)} = G(\bar{w})$. An example of
such a function is $G(w) = e^{w^2}$. For such a function $G(x)$
we define a smooth function 
$$
W(x) := \frac{1}{2\pi} \int_{(\varepsilon)} x^{-w}  G(w) \cdot \frac{d w}{w}.
$$
Notice that $W$ is real.
\begin{lemma}[Approximate function equation]
We have, for $T < t < 2T$, 
  \[ | \zeta ( \tfrac{1}{2} + i t) |^2 = 2 \sum_{mn < T^{1 + \varepsilon}}
     \frac{1}{\sqrt{mn}} \cdot \bigg ( \frac{m}{n} \bigg )^{i t} 
     W \bigg ( \frac{2 \pi mn}{t}
\bigg ) + O (T^{- 2 / 3}) . \]
\end{lemma}
\begin{rem}
Of course we could work with the usual smoothing $V$ involving the 
Gamma factors on the Mellin transform side. We believe the 
smoothing $W(2\pi m n / t)$ to be (slightly) more transparent.
```

## Source [25], twisted-square/primary/gmrr-v2/squfv.tex:392–403

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

## Source [25], twisted-square/primary/gmrr-v2/squfv.tex:296–308

```text
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

## Source [26], twisted-square/primary/gl23-abs-page.txt:27–29

```text
Abstract:
Let $\Pi_{0}$ be a cuspidal automorphic representation of $\mathrm{PGL}_{3}(\mathbb{A}_{\mathbb{Q}})$. In this paper, we use Levinson's method to prove that, as $Q\to \infty$, at least $1/9$ of the zeros of the $L$-functions $L(s, \Pi_{0}\,\times\, \chi)$ lie on the critical line, where $\chi$ ranges over the family of primitive Dirichlet characters of conductor up to $Q$. This result is unconditional when $\Pi_{0}$ is self-dual, and otherwise holds under a mild condition.
The key technical input is a new asymptotic formula with a power-saving error term for the mean square of the product of $L(s, \Pi_{0}\times \chi)$ and a Dirichlet polynomial with arbitrary coefficients in both the $T$- and $Q$-aspects for the range $Q^{\epsilon}\le T \le Q^{1/3-\epsilon}$. When $T=Q^{\epsilon}$, our asymptotic formula allows Dirichlet polynomials of length $\theta <1/2-\epsilon$; when $\theta=0$, it gives a strong error term of size $O_{\epsilon}(Q^{7/4+\epsilon})$. Furthermore, our result provides evidence for the CFKRS conjectures for large twists and large vertical shifts.
```

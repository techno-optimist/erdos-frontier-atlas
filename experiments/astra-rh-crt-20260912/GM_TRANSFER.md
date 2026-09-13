# Guth–Maynard into squarefree variance: a reconciled transfer

**Status:** research deduction from explicitly named analytic theorem inputs.
Two independent model mathematical audits passed, with the qualifications below
incorporated. This is not human peer review, kernel verification, a novelty or
current-record claim, or a proof of RH. The deep input proofs were not rebuilt.
The exact versions inspected are GMRR `2006.04060v2` and Guth–Maynard
`2405.20552v2`; no uninspected publisher-final text is being substituted.[3][5]

## 1. The deduction

Let

$$
Q(x)=\sum_{1\le n\le x}\mu(n)^2,\qquad \rho=\frac1{\zeta(2)}=\frac6{\pi^2},
$$

and define the actual, density-centered variance

$$
\mathcal V_X(H)=\frac1X\int_X^{2X}|Q(x+H)-Q(x)-\rho H|^2\,dx.
$$

**Transfer theorem.** For every fixed $0<\varepsilon<1/100$, uniformly for
real $X\ge1$ and $1\le H\le X^{4/7-\varepsilon}$,

$$
\boxed{\mathcal V_X(H)=C\sqrt H+
 O_\varepsilon(H^{1/2-\varepsilon/16}),}
$$

where the unchanged GMRR constant is

$$
C=\frac{\zeta(3/2)}{\pi}
  \prod_p\left(1-\frac3{p^2}+\frac2{p^3}\right).
$$

Here “unconditional” means that this deduction assumes neither RH nor
Lindelöf; it uses the analytic theorems listed below. The error is a bound
uniform in the stated range. It is an asymptotic relative to $C\sqrt H$ when
$H\to\infty$, not a claim of relative error tending to zero for fixed $H$.

The improvement is relative to GMRR's pinned Theorem 1 range
$H\le X^{6/11-\varepsilon}$. Its Proposition 2 already has a $4/7$ range for
one component, but with the old cutoff it does not give this full variance
statement. Overlapping the two component cutoffs is essential.[3]

## 2. Inputs and the small-divisor window

The externally supplied inputs are:

- GMRR Proposition 1, its Theorem 1 for the low-$H$ overlap, and its
  Saffari–Vaughan reduction (Lemma 10, label `le:SV`). The relevant Mellin reduction is in
  GMRR Section 5, equations (36)–(40).[3]
- Guth–Maynard Theorem 1.1, with pointwise 1-bounded coefficients and separated
  times. Proposition 12.1 is used only to inspect the remaining bottleneck.[5]
- The classical Weyl bound and zeta fourth moment, in the forms recalled in
  GMRR Lemma 5 (`le:ZetaSC`, Weyl) and Lemma 3
  (`le:ZetaFourth`, fourth moment):
  $|\zeta(1/2+it)|\ll(1+|t|)^{1/6}\log^2(2+|t|)$ and
  $\int_{-T}^T|\zeta(1/2+it)|^4dt\ll T\log^4(2+T)$ for $T\ge1$.[3]

It suffices first to treat $X^\varepsilon\le H\le X^{4/7-\varepsilon}$.
Choose the real cutoff

$$
z=H^{5/4+\varepsilon}.
$$

GMRR Proposition 1 applies if

$$
X^\varepsilon\le H\le X^{2/3-\varepsilon},\qquad
H^{1+\varepsilon}\le z\le
\min\left(\frac X{H^{1/2+\varepsilon}},
           X^{1/2}H^{1/2-\varepsilon}\right).
$$

All these inequalities hold with positive slack. In addition, the displayed
intermediate proposition in GMRR Section 4 uses the stricter first upper bound
$X^{1-\varepsilon}/H^{1/2}$. Our choice also satisfies that bound, so this
internal difference of statements causes no gap in this transfer.[3]

For example, at the largest permitted exponent $h=4/7-\varepsilon$ in
$H=X^h$, the following slacks are positive:

$$
\begin{aligned}
1-(4/7-\varepsilon)(7/4+2\varepsilon)
 &=\varepsilon(17/28+2\varepsilon),\\
1-\varepsilon-(4/7-\varepsilon)(7/4+\varepsilon)
 &=\varepsilon(5/28+\varepsilon),\\
1-(4/7-\varepsilon)(7/4+3\varepsilon)
 &=\varepsilon(1/28+3\varepsilon).
\end{aligned}
$$

The second cutoff condition is
$1/2-(4/7-\varepsilon)(3/4+2\varepsilon)>0$ on the same epsilon interval.
The last displayed slack will also give $X/H\ge H^{3/4+3\varepsilon}$.
These are continuous-parameter inequalities, not checks of a sampled grid.

Write the density-centered small-divisor piece as

$$
B_1(x)=\sum_{d^2\le z}\mu(d)
 \left(\left\lfloor\frac{x+H}{d^2}\right\rfloor
       -\left\lfloor\frac x{d^2}\right\rfloor-\frac H{d^2}\right).
$$

The supplied Proposition 1 gives

$$
I_1:=\frac1X\int_X^{2X}|B_1(x)|^2dx
 =C\sqrt H+O_\varepsilon(H^{1/2-\varepsilon/10}).
$$

## 3. A bounded-coefficient mixed-integral operator

For an integer $D\ge1$, let $a_d$ be any fixed complex coefficients supported
on $D\le d<2D$ with $|a_d|\le1$. Fixed masks and partial blocks are allowed.
Put

$$
M_D(s)=\sum_{D\le d<2D}\frac{a_d}{d^s},\qquad
\mathcal I_D(T)=\frac HT\int_{-T}^T
 |\zeta(1/2+it)M_D(1+2it)|^2dt.
$$

For the application, $D\le\sqrt{2X}$ and $X/H\le T\le X^2$.
The following estimate does not require Möbius cancellation:

$$
\boxed{\mathcal I_D(T)\ll X^{o(1)}H
 \left(D^{-1}+T^{-2/3}+D^{-1/5}T^{-1/2}+D^{-4/5}\right).}
\qquad\text{(GM-MIX)}
$$

### Coefficients, length and time

Apply GM Theorem 1.1 with polynomial length $N=D$, not $D^2$.
For $t\in[-T,T]$, put $u=2T-2t\in[0,4T]$ and
$b_d=(Da_d/d)d^{-2iT}$. Then

$$
|b_d|\le1,\qquad
\sum b_dd^{iu}=D M_D(1+2it).
$$

Set the coefficient at the unused endpoint $d=2D$ to zero if needed.
Thus a level $|M_D|\ge V$ corresponds to the GM level $U=DV$.
The doubled phase changes the time scale, not the polynomial length.[5]

For a continuous level set, divide the $t$-axis into half-open unit intervals
and choose one point from each occupied interval of the larger parity class.
The selected times are 1-separated, and the set's measure is at most twice
the number selected. The transformed times are still 1-separated. Applying
GM at height $4T$ therefore gives

$$
|S(V)|\ll (4T)^{o(1)}
 \left(V^{-2}+D^{-2/5}V^{-4}+T D^{-8/5}V^{-4}\right).
\qquad\text{(LEVEL)}
$$

The theorem input is the three-term bound
$N^2U^{-2}+N^{18/5}U^{-4}+TN^{12/5}U^{-4}$; the last term in (LEVEL)
includes the rescaled-height constant in the implicit constant.[5]

### Moment treatments

On $|M_D|<D^{-1/2}$, Cauchy–Schwarz and the zeta fourth moment give
$\int_{-T}^T|\zeta|^2\ll T\log^2(2+T)$, hence the contribution
$\ll HD^{-1}\log^2(2+T)$.

For $D^{-1/2}\le V\le1$, split into dyadic levels
$S(V)=\{V\le|M_D|<2V\}$. Let $R_0,R_1,R_2$ be the three measure
majorants in (LEVEL), including their common constant. Partition $S(V)$
into measurable pieces of measures at most $R_0,R_1,R_2$. Such a partition
exists because their sum bounds the measure and Lebesgue measure is atomless.
This does not assert arithmetic independence.

Use Weyl on the first piece and Cauchy–Schwarz with the fourth moment on
the other two. Apart from the indicated subpower and logarithmic factors,

$$
\int_{S(V)}|\zeta|^2
 \ll T^{1/3}V^{-2}
     +T^{1/2}D^{-1/5}V^{-2}
     +T D^{-4/5}V^{-2}.
$$

Multiplication by $(H/T)(2V)^2$ removes $V$. There are $O(\log X)$ levels,
since $|M_D|\le1$. This proves (GM-MIX). The use of the fourth moment on
low values and on exceptional sets are separate steps; both must be paid for.

## 4. From the mixed integral back to a local divisor block

Define the centered block function on positive arguments by

$$
A_D(v)=\sum_{D\le d<2D}a_d
 \left(\left\lfloor\frac v{d^2}\right\rfloor-\frac v{d^2}\right).
$$

It is bounded, but is not in general globally square-integrable on the real
line. Before applying the Saffari–Vaughan lemma, multiply it by a compactly
supported cutoff equal to 1 on $[X,12X]$. All arguments of the lemma lie in
that interval when $H\le X$. Its conclusion on the relevant interval is
therefore about the original $A_D$, with no derivative-of-cutoff cost.[3]

After this localization, the GMRR reduction gives

$$
J_D:=\frac1X\int_X^{2X}|A_D(x+H)-A_D(x)|^2dx
 \ll X\int_{\mathbb R}\min\left(\frac{H^2}{X^2},\frac1{t^2}\right)
 |\zeta(1/2+it)M_D(1+2it)|^2dt.
\qquad\text{(SPECTRAL)}
$$

At $t=0$ the minimum is interpreted as $H^2/X^2$.
Here is why the Mellin step is legitimate rather than merely formal:
$A_D(v)=O(v/D)$ near zero and $A_D(v)=O(D)$ at infinity. Its Mellin
transform converges absolutely for $0<\Re s<1$ and equals
$\zeta(s)M_D(2s)/s$. Also $e^{-y/2}A_D(e^y)$ is genuinely in
$L^2(\mathbb R)$. Mellin–Plancherel applies to the multiplicative increment;
its multiplier is $((1+\theta)^s-1)/s$ with $\theta\asymp H/X$.
Its squared magnitude is bounded by the kernel in (SPECTRAL).
These are the endpoint and norm conditions behind GMRR's equations (38)–(40).[3]

To control all heights, write $A=X/H$, $Y=X^2$ and
$F_D(T)=\int_{-T}^T|\zeta M_D|^2dt$. If
$\sup_{A\le T\le Y}(H/T)F_D(T)\le B$, then the low part of (SPECTRAL)
is at most $B$. Stieltjes integration by parts bounds its middle part by

$$
X\int_A^Y t^{-2}\,dF_D(t)
 \le X\left(Y^{-2}F_D(Y)+2\int_A^Y\frac{F_D(t)}{t^3}dt\right)
 \le2B.
$$

Thus no uncontrolled height sum is omitted. For $|t|>X^2$, use $|M_D|\le1$
and Weyl directly; the contribution is
$O(X^{-1/3}\log^4(2+X))=O(1)$. In particular, no GM estimate beyond the
stated height box is required.

## 5. Integer blocks and the actual squares beyond the cutoff

Partition the integers with $z<d^2\le2X$ by taking
$D_0=\lfloor\sqrt z\rfloor+1$, $D_j=2^jD_0$, and intervals
$[D_j,2D_j)$, masking out integers with $d^2>2X$.
These disjoint blocks have integer origins and are all covered by Section 3.
There are $L=O(\log X)$ of them. Cauchy–Schwarz costs

$$
\frac1X\int_X^{2X}\left|\sum_j\Delta A_{D_j}\right|^2dx
 \le L\sum_jJ_{D_j}\le L^2\max_jJ_{D_j}.
$$

**Zero-padding does not account for the actual terms with $d^2>2X$.**
The identity $\mu(n)^2=\sum_{d^2\mid n}\mu(d)$ also has a remainder
$R_{\rm end}$ from $2X<d^2\le2X+H$. Here the cofactor must be 1.
The remainder is supported on $2X-H<x\le2X$ and has magnitude
$O(1+H/\sqrt X)$. Therefore

$$
\frac1X\int_X^{2X}|R_{\rm end}(x)|^2dx
 \ll \frac HX+\frac{H^3}{X^2}=O(1)
$$

in the proposed range. This is a separate endpoint estimate, not a claim
that a Dirichlet-polynomial mask recovers those terms.

## 6. One aggregate epsilon budget and final centering

Fix $\delta=\varepsilon^2/100$ when interpreting the GM subpower.
At height $4T\le4X^2$ it costs $O_\varepsilon(X^{2\delta})$.
Budget a further $X^\delta$ for all the logarithms together, including
moment estimates, value bins and divisor-block Cauchy–Schwarz. A bound
by $\log^{10}(2+X)$ suffices. For sufficiently large $X$ this is
$O_\varepsilon(X^\delta)$, and

$$
X^{3\delta}\le H^{3\varepsilon/100}
\quad\text{because}\quad H\ge X^\varepsilon.
$$

Now $D\ge\sqrt z=H^{5/8+\varepsilon/2}$ and the cutoff slack in
Section 2 gives $T\ge X/H\ge H^{3/4+3\varepsilon}$.
The raw terms in (GM-MIX) are consequently at most

| Term | Bound before the aggregate loss |
|---|---|
| $HD^{-1}$ | $H^{3/8-\varepsilon/2}$ |
| $HT^{-2/3}$ | $H^{1/2-2\varepsilon}$ |
| $HD^{-1/5}T^{-1/2}$ | $H^{1/2-8\varepsilon/5}$ |
| $HD^{-4/5}$ | $H^{1/2-2\varepsilon/5}$ |

After the full budget, the weakest saving still exceeds $\varepsilon/4$.
Sections 4 and 5 therefore establish, including $R_{\rm end}$,

$$
I_2:=\frac1X\int_X^{2X}|B_2(x)|^2dx
 \ll_\varepsilon H^{1/2-\varepsilon/4},
$$

where $B_2$ is the actual large-divisor count centered at
$H\sum_{z<d^2\le2X}\mu(d)/d^2$.

Recombining $B_1$ and $B_2$ gives a cross term at most
$2\sqrt{I_1I_2}\ll_\varepsilon H^{1/2-\varepsilon/8}$.
Their combined center is still truncated at $2X$. Replacing it by $\rho H$
changes the centered function by a constant $O(H/\sqrt X)$, hence changes
the variance by

$$
O_\varepsilon\left(H^{5/4}X^{-1/2}+H^2/X\right).
$$

Both terms fit $H^{1/2-\varepsilon/16}$ in the proposed range: the required
inequalities are
$H^{3/4+\varepsilon/16}\le X^{1/2}$ and
$H^{3/2+\varepsilon/16}\le X$, again with positive slack.
This proves the high-$H$ part of the stated theorem.

Finally, $1\le H\le X^\varepsilon$ lies inside the original GMRR Theorem 1
range, with its stated $\varepsilon/16$ error. No independent invocation of
Hall's older proof is needed. Bounded $X$ is absorbed into the implicit
constant. This completes the deduction.[3]

## 7. What the present estimates do not certify

Ignoring epsilon slack solely to locate the critical cell, write $H=X^h$
and $z=X^a$. The sufficient conditions from the displayed route are

$$
a\le\min(1-h/2,1/2+h/2),\qquad
a\ge5h/4,\qquad a\ge10h-5,\qquad h\le4/7.
$$

They meet at $h=4/7$, $a=5/7$, $D=X^{5/14}$ and
$T=X^{3/7}=D^{6/5}$. This is a ceiling of this sufficient-inequality system,
not a lower bound on the actual variance and not an endpoint-saving theorem.

GM Proposition 12.1 has also been checked. At the critical unnormalized level
$U=D^{3/4}$, and in the exponent regime $T^{5/6}\le D\le T$, it supplies
measure majorant $T^{1/2}$, giving the mixed majorant
$HD^{-1/2}T^{-1/4}$. Combining its saving condition $a\ge3h-1$ with
$a\le1-h/2$ again gives $h\le4/7$.[5]

The comparison was not restricted to a single additive term:

| Cardinality estimate at the critical level | Dominant measure majorant | Fourth-moment mixed majorant |
|---|---|---|
| GM Theorem 1.1 | $D^{3/5}$ | $HD^{-1/5}T^{-1/2}$ |
| Classical/Huxley estimate used by GMRR | $TD^{-1/2}$ | $HD^{-3/4}$ |
| GM Proposition 12.1 | $T^{1/2}$ | $HD^{-1/2}T^{-1/4}$ |

In this regime the fourth-moment treatment is better than the Weyl treatment
for all three rows. Near the constant-factor boundary caused by height $4T$,
GM Theorem 1.1 itself supplies the same exponents; no exactly out-of-range use
of Proposition 12.1 is needed.[3][5]

Nor does taking a much smaller cutoff evade this particular test. For
$4/7<h<2/3$, either the tail contains the transition block $D\asymp T^{5/6}$,
whose displayed majorant is too large, or its smallest block is in the refined
region and the two cutoff inequalities above are incompatible.

**These are limitations of the specified majorants.** No actual polynomial,
Möbius sequence, or zeta-value counterexample is constructed. A scalar model
that assigns a set measure $T^{1/2}$, $|M|=D^{-1/4}$ and
$|Z|=T^{1/8}$ can saturate their summary bounds, but is not an arithmetic
example. Empty exceptional sets are also consistent with those upper bounds.

A blanket statement that stronger subconvexity cannot help would be wrong.
Under a pointwise hypothesis $|\zeta|\ll T^{\kappa+o(1)}$, applying it on
the refined critical set gives $HD^{-1/2}T^{-1/2+2\kappa}$, which improves
that set's fourth-moment treatment precisely if $\kappa<1/8$.
No such additional hypothesis is used here, and improvement on one set alone
would still require rechecking every other range.

## 8. The remaining arithmetic target and verification scope

At $D=T^{5/6}$ the current mixed-integral scale is $T^{1/3+o(1)}$.
A concrete next target is a genuine fixed saving in

$$
\int_T^{2T}|\zeta(1/2+it)M_D(1+2it)|^2dt,
$$

uniform in a neighborhood of that critical length-height relation. Actual
Möbius factorization and the square-supported twisted-moment structure are
possible sources of information not retained by the scalar estimates. They
are research directions, not established improvements.

The variance exponent $4/7$ remains below $2/3$. Thus the generic Mellin
interface in `MELLIN_TRANSFER.md` yields no enlarged continuation domain or
new zero exclusion from this range alone. The full RH-equivalent actual
variance/centered-defect estimate remains unproved.

Both independent analytic reports were read and reconciled. Their unmodified
arithmetic scripts were copied to fresh scratch and run successfully:
36 and 21 continuous-epsilon positivity certificates, respectively; the first
also checks 15 integer dyadic partitions. The second rejects both a
beyond-ceiling majorant claim and an exhausted epsilon budget. These checks
certify the recorded algebra, not the deep analytic inputs or optimality of
all possible methods. Provenance and scope are in `REVIEW_STATUS.json`;
`gm_parameter_check.json` records the parent's separate rational ledger.

## Sources

[3] https://arxiv.org/html/2006.04060v2
[5] https://arxiv.org/pdf/2405.20552v2 — Guth–Maynard, New large value estimates for Dirichlet polynomials, v2

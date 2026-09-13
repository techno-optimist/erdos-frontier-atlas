# Adversarial second audit: Guth–Maynard → GMRR

## Verdict — qualified transfer pass, not an optimality certificate

**No fatal epsilon, low-height, or recombination error was found in the proposed transfer.** Accepting the pinned GM Theorem 1.1 and GMRR Proposition 1 as theorem inputs, the Section 5 argument can be rerun with the proposed smaller cutoff and with an explicit aggregate loss budget. It supplies the claimed formula for every fixed `0 < epsilon < 1/100`:

\[
\frac1X\int_X^{2X}\left|\sum_{x<n\le x+H}\mu^2(n)-\frac{6H}{\pi^2}\right|^2dx
=C\sqrt H+O_\varepsilon(H^{1/2-\varepsilon/16}),
\qquad 1\le H\le X^{4/7-\varepsilon}.
\]

Here `C` is precisely the constant in GMRR Theorem 1, not a newly computed constant.[2] This verdict is **conditional on the cited analytic inputs being accepted, not on an additional conjecture**. It is an informal proof-transfer audit, not a formal proof or an independent reconstruction of GM's proof and GMRR's Proposition 1. The parent's separate source/hypothesis audit remains relevant.

**Do not certify a mathematical “4/7 barrier.”** What has been checked is a ceiling of particular scalar majorants coupled to the unchanged Proposition 1 cutoff. Neither a positive term in an upper bound nor infeasibility of a sufficient-condition linear program gives a lower bound for the actual mixed moment or squarefree variance. The original report already calls the relevant expressions upper-bound terms, but its “requires,” “ceiling,” and “stronger subconvexity alone” language needs the narrower interpretation in Sections 7–8 below.

### Required qualifications and repairs to the report under review

| Item | Audit result |
|---|---|
| GM coefficient and level-set substitution | Independently recovered; correct, including time rescaling and arbitrary endpoint zero-padding. |
| `X^{o(1)}` | Must be an **aggregate** loss budget after all value dyadics, divisor dyadics, and Cauchy–Schwarz factors. An explicit sufficient choice is given below. |
| Published GMRR Proposition 2 | **Cannot be invoked** at `z=H^{5/4+epsilon}`: it assumes `z>=H^{4/3+epsilon}`. This audit reruns its proof instead.[2] |
| Divisors with `d^2>2X` | A literal split at `sqrt(2X)` misses squares in `(2X,2X+H]`. They are harmless, but must be retained or bounded. Explicit bound below. |
| Mellin/Saffari–Vaughan formalities | Can be made exact for finite dyadic coefficient supports, without new epsilon losses; a direct Fourier/Mellin argument is supplied. |
| Final `epsilon/16` | Survives both variance Cauchy–Schwarz and changing the centering constant. |
| Low `H` | Use the original GMRR Theorem 1 with the **same** epsilon; do not extend the `X^{o(1)}` absorption into this range.[2] |
| Proposition 12.1 “barrier” | Certifies failure of the specified numerical upper-bound route, **not** a lower-bound obstruction to the mathematics. |
| Novelty, current record, publisher-final version, RH | Not certified by this audit. |

## 1. Inputs and read-only scope

The reviewed report is `gm-candidate/audit.md`, with initial SHA-256 `e61abeaf8f060178f259f613d540399119f00910119885d396551f64ae176b2d`.

The authoritative local reading copies for this task are:

- GM: `gm-source/LargevaluesDirichlet17.tex`, Theorem 1.1 at lines 68–79; the uniform subpower convention at 288–290; Proposition 12.1 at 2237–2250.[1]
- GMRR: `gmrr-source/squfv.tex`, Theorem 1 at 88–99; Proposition 1 at 217–223; Proposition 2 at 225–231; recombination/centering at 240–258; Section 5 at 756–859.[2]

`input-hashes-initial.json` pins the report, both TeX files, the original checker, and the supplied locator file. All work is in this new isolated directory. The original checker was read but **not executed in place**, since it writes its sibling results file. No supplied report/source/checker, repository, staging area, or commit was changed.

## 2. Independent derivation of the GM level-set bound

Take a finite dyadic block, allowing fixed zero-padding at its ends,

\[
M_D(1+2it)=\sum_{D\le d<2D}\frac{c_d}{d^{1+2it}},\qquad |c_d|\le1.
\]

For the squarefree application `c_d=mu(d)` on the required truncated block and zero elsewhere. Define

\[
S_D(V)=\{t\in[-T,T]:V\le |M_D(1+2it)|<2V\}.
\]

GM states that a 1-separated set of times in `[0,mathcal T]` at which a polynomial with pointwise 1-bounded coefficients has modulus at least `U` satisfies

\[
R\ll_\delta \mathcal T^\delta
\left(N^2U^{-2}+N^{18/5}U^{-4}+\mathcal T N^{12/5}U^{-4}\right)
\tag{2.1}
\]

for every fixed `delta>0`; its convention makes the implicit constant depend only on the loss parameter, not on the chosen coefficients or value level.[1]

Put `u=-2t`, then `v=u+2T`. For `v in [0,4T]`, the normalized polynomial is

\[
D M_D(1+2it)=\sum_d\left(\frac{Dc_d}{d}\,d^{-2iT}\right)d^{iv}.
\]

The coefficient modulus is at most 1 **pointwise**. If `D` is not an integer, take `N=ceil(D)` in GM; the support lies in `[N,2N]`, and `N asymp D`. The normalizing factor can remain `D`. Thus no factorization of `mu`, extension to merely square-summable coefficients, or reinterpretation as length `D^2` occurs.

Partition `[0,4T]` into half-open unit intervals. From every occupied interval choose one point of the transformed set. Separate even and odd intervals; each selected subsequence is 1-separated. The transformed set's measure is at most the number of occupied intervals. Returning to `t` introduces only the Jacobian `1/2`. There is **no derivative estimate, no logarithmic sampling loss, and no need to sample zeta maxima**.

Use `U=DV` in (2.1). The exponent substitution gives, independently,

\[
|S_D(V)|\ll_\delta (4T)^\delta
\left(V^{-2}+D^{-2/5}V^{-4}+TD^{-8/5}V^{-4}\right).
\tag{2.2}
\]

This is uniform for the stated `D,T,V` range. The advantageous range of GM is not an extra hypothesis of Theorem 1.1; the source's reduction explicitly treats `N>=T` and uses subdivision for larger time intervals.[1]

## 3. The mixed estimate — dominance must be used correctly

Write

\[
A=V^{-2},\quad B=D^{-2/5}V^{-4},\quad C_0=TD^{-8/5}V^{-4},
\quad E_D(V)=\frac HT V^2\int_{S_D(V)}|\zeta(1/2+it)|^2dt.
\]

GMRR's retained estimates are the global fourth moment `int_{|t|<=T}|zeta|^4 << T(log T)^4` and the Weyl bound `|zeta(1/2+it)| << |t|^{1/6}(log |t|)^2` for `|t|>=2`.[2] Bounded `|t|<=2` is harmless.

- If `A>=B+C_0`, then (2.2) gives `|S| <<_delta T^delta A`; Weyl yields
  \[
  E_D(V)\ll_\delta T^\delta H T^{-2/3}(\log(2T))^4.
  \]
- If `A<B+C_0`, then (2.2) gives `|S| <<_delta T^delta(B+C_0)`. Cauchy–Schwarz **on the actual level set** followed by the global fourth moment yields
  \[
  E_D(V)\ll_\delta T^{\delta/2}H
  \left(D^{-1/5}T^{-1/2}+D^{-4/5}\right)(\log(2T))^2.
  \]

This is a legitimate case distinction on the numerical majorants. It does not pretend that the set itself is a union of three subsets with measures equal to the three terms.

At low levels, `|M_D|<=D^{-1/2}` gives

\[
\frac HT\int_{|M_D|\le D^{-1/2}}|\zeta M_D|^2dt
\ll HD^{-1}(\log(2T))^2.
\]

The second moment of zeta needed here follows already from Cauchy–Schwarz and its fourth moment; no extra analytic theorem is required. Also `|M_D|<<1` by the harmonic sum bound, so there are only `O(log(2D))` remaining value dyadics. Consequently, with an arbitrary fixed loss exponent and suitable logarithmic factors,

\[
\frac HT\int_{|t|\le T}|\zeta(1/2+it)M_D(1+2it)|^2dt
\ll H X^{o(1)}\left(D^{-1}+T^{-2/3}+D^{-1/5}T^{-1/2}+D^{-4/5}\right).
\tag{3.1}
\]

The report's mixed estimate is correct. The epsilon budget below is what makes (3.1) useful uniformly, rather than just a formal exponent identity.

## 4. Exact cutoff and epsilon ledger

Fix `0<epsilon<1/100`, and work first in

\[
X^\varepsilon\le H\le X^{4/7-\varepsilon},\qquad z=H^{5/4+\varepsilon}.
\]

GMRR Proposition 1 requires `H^{1+epsilon}<=z<=min(X/H^{1/2+epsilon}, H^{1/2-epsilon}sqrt(X))` and `H<=X^{2/3-epsilon}`.[2] Its lower cutoff follows with the fixed exponent gap `1/4`, and its height range follows with gap `2/21` in powers of `X`. The two upper-cutoff slacks at the worst height `h=log_X H=4/7-epsilon` are exactly

\[
1-(7/4+2\varepsilon)(4/7-\varepsilon)
=17\varepsilon/28+2\varepsilon^2>0,
\]
\[
1/2-(3/4+2\varepsilon)(4/7-\varepsilon)
=1/14-11\varepsilon/28+2\varepsilon^2>0.
\]

Both are monotone in the required direction as `h` decreases. The second polynomial has the exact positive Bernstein lower bound `677/10000` on `0<=epsilon<=1/100`.

For every tail block and relevant height,

\[
D\ge H^{5/8+\varepsilon/2},\qquad T\ge X/H\ge H^{3/4+3\varepsilon}.
\]

The last assertion follows from the exact slack

\[
1-(7/4+3\varepsilon)(4/7-\varepsilon)=\varepsilon/28+3\varepsilon^2>0.
\]

All four terms in (3.1) decrease as `D` and/or `T` increase, so replacing them by these lower bounds handles **the entire** `sqrt(z)<=D<=sqrt(2X)`, `X/H<=T<=X^2` box, not just one corner sample.

| Term including the outside `H` | Upper bound before loss absorption |
|---|---|
| `H D^{-1}` | `H^{3/8-epsilon/2}` |
| `H T^{-2/3}` | `H^{1/2-2epsilon}` |
| `H D^{-1/5} T^{-1/2}` | `H^{1/2-8epsilon/5}` |
| `H D^{-4/5}` | `H^{1/2-2epsilon/5}` |

### An explicit **aggregate** loss allocation

Choose the exponent in GM as

\[
\delta=\varepsilon^2/100.
\]

Since GM is applied at time length `4T<=4X^2`, use conservatively `(4T)^delta <<_epsilon X^{2delta}` for every branch, even the branches that only need its square root. Bound **all** remaining logarithms by

\[
(\log(2X))^{10}\ll_\varepsilon X^\delta.
\]

Ten is a safe overcount: up to four powers from Weyl, one from value dyadics, two from the divisor-block Cauchy–Schwarz/recombination, with room even if height dyadics are charged. The time-kernel reduction in fact needs no logarithmic height loss. There is no further polynomial-in-`X` loss in that reduction.

Thus the global loss, **after both divisor-block factors are paid**, is at most

\[
X^{3\delta}=X^{3\varepsilon^2/100}\le H^{3\varepsilon/100}.
\]

The worst raw saving `2epsilon/5` leaves `37epsilon/100`. In particular it comfortably supplies

\[
\mathcal I_2\ll_\varepsilon H^{1/2-\varepsilon/4},
\tag{4.1}
\]

after the reductions and endpoint repairs in Section 5. Relative to this chosen target, the four exact remaining exponent slacks are

\[
1/8+11\varepsilon/50,\quad 43\varepsilon/25,\quad
33\varepsilon/25,\quad 3\varepsilon/25.
\]

The phrase “choose all `X^{o(1)}` losses small” is valid only with an aggregate interpretation. Choosing a convenient small exponent independently at every occurrence and then ignoring their sum would not be a proof. Constants may depend badly on the fixed epsilon; no uniformity as `epsilon=epsilon(X)` tends to zero is asserted.

## 5. Time tails, Mellin normalization, and divisor endpoints

### 5.1 A loss-free way to justify the Mellin step

For any of the finite coefficient blocks, define

\[
A_D(x)=\sum_dc_d\bigl(\lfloor x/d^2\rfloor-x/d^2\bigr).
\]

GMRR's Section 5 obtains the weighted spectral bound using a contour shift and Plancherel.[2] For the audit one can instead justify that step directly: `A_D(x)=O(D)` as `x→infinity` and `A_D(x)=O(x/D)` near zero. Hence `f(u)=e^{-u/2}A_D(e^u)` is in both `L^1(R)` and `L^2(R)`.

For `0<Re(s)<1`, splitting the integral at 1 and using the fractional-part representation of zeta gives

\[
\int_0^\infty(\lfloor x\rfloor-x)x^{-s-1}dx=\frac{\zeta(s)}s.
\]

This identity also follows by continuing
`zeta(s)/s=1/(s-1)-int_1^infinity {x}x^{-s-1}dx` from `Re(s)>1` to `Re(s)>0`. Scaling `x` by `d^2` and summing the **finite** coefficient block therefore gives the Fourier transform

\[
\widehat f(t)=\frac{\zeta(1/2+it)M_D(1+2it)}{1/2+it}.
\]

For `w=log(1+theta)`, the shifted difference has Fourier multiplier `e^{w(1/2+it)}-1`. Plancherel holds on the whole logarithmic real line and gives exactly the physical measure `dx/x^2`, not `dx/x` or unweighted `dx`. Jump endpoints affect a null set only. This avoids attaching an unproved truncation error to a merely formal infinite Perron integral.

GMRR's Saffari–Vaughan lemma is stated for square-integrable functions.[2] Although `A_D` need not be globally in unweighted `L^2`, its local use is justified either by its displayed local proof or by multiplying `A_D` by a cutoff equal to 1 on `[0,12X]`. For `H<=X`, every argument on both sides of that lemma lies there. No epsilon is spent. Applied to the finite blocks, the resulting bound is

\[
\frac1X\int_X^{2X}|A_D(x+H)-A_D(x)|^2dx
\ll X\int_{\mathbb R}\min\{(H/X)^2,|t|^{-2}\}|\zeta M_D|^2dt.
\tag{5.1}
\]

### 5.2 Large times and the height supremum

The bound `|M_D|<<1` is uniform in `D`. Weyl therefore gives the explicit far-time bound

\[
X\int_{|t|>X^2}|t|^{-2}|\zeta M_D|^2dt
\ll X^{-1/3}(\log(2X))^4.
\]

Even after the two divisor-dyadic factors this is `O(1)`. It must not be replaced by an unquantified `X^{o(1)}` and then forgotten. Since `H>=1` and `1/2-epsilon/4>0`, this is acceptable in (4.1).

For the remaining times, let `F(T)=int_{|t|<=T}|zeta M_D|^2dt`, `A=X/H`, and suppose `HF(T)/T<=B` uniformly on `[A,X^2]`. The interval `|t|<=A` costs at most `B` in (5.1). Stieltjes integration by parts on `[A,X^2]`, using `F(T)<=BT/H`, costs at most a fixed multiple of `B` on the remainder. Thus the height supremum adds **no** logarithmic factor and needs no unstated bound beyond `T=X^2`.

### 5.3 The missing spatial endpoint is harmless but real

The large-divisor count in the original variance can include `d^2` in `(2X,2X+H]`, whereas its finite centering stops at `2X`.[2] A literal decomposition into blocks supported only below `sqrt(2X)` would omit these terms.

Retain them as `B_end(x)`. For `H<X`, such divisors have `n=1`; the term is supported on `x in [2X-H,2X]`, and

\[
|B_{\rm end}(x)|\ll 1+H/\sqrt X,
\qquad
\frac1X\int_X^{2X}|B_{\rm end}(x)|^2dx
\ll H/X+H^3/X^2\ll1.
\]

The final inequality follows from `H<=X^{4/7-epsilon}`; the exact decay slacks are `3/7+epsilon` and `2/7+3epsilon`. The truncated blocks now match their centering **exactly**, using endpoint zero coefficients, and the separate `B_end` is included by an ordinary two-term squared-norm inequality. This proves (4.1) for the actual `I_2`, not merely for a truncated surrogate.

## 6. Low H, centering, and final Cauchy–Schwarz

For high `H`, Proposition 1 gives

\[
\mathcal I_1=C\sqrt H+O_\varepsilon(H^{1/2-\varepsilon/10}),
\quad \mathcal I_1\ll_\varepsilon H^{1/2}.
\]

The unchanged recombination is

\[
\mathcal I_1+O(\sqrt{\mathcal I_1\mathcal I_2}+\mathcal I_2).
\]

Both assertions are the actual GMRR setup and recombination, not a sum of variances with cross terms discarded.[2] With (4.1), the cross term has size at most `H^{1/2-epsilon/8}`. Therefore the high-`H` truncated-centering error is already `O_epsilon(H^{1/2-epsilon/10})`; it certainly meets `epsilon/16`.

For the replacement of `H sum_{d^2<=2X}mu(d)/d^2` by `6H/pi^2`, the deterministic discrepancy is `O(H/sqrt(X))`.[2] The resulting variance error is

\[
O_\varepsilon(H^{5/4}X^{-1/2}+H^2/X).
\]

Against the requested `H^{1/2-epsilon/16}`, the worst-height slacks in powers of `X` are exactly

\[
\frac12-(4/7-\varepsilon)(3/4+\varepsilon/16)
=\frac1{14}+\frac57\varepsilon+\frac1{16}\varepsilon^2>0,
\]
\[
1-(4/7-\varepsilon)(3/2+\varepsilon/16)
=\frac17+\frac{41}{28}\varepsilon+\frac1{16}\varepsilon^2>0.
\]

Thus centering is not close to exhausting the saving.

For `1<=H<X^epsilon`, apply the original GMRR Theorem 1 **with parameter epsilon itself**. It has exactly the requested error exponent and covers this whole range, because `epsilon < 6/11-epsilon` throughout the allowed epsilon interval.[2] There is no need to apply Proposition 1 below its lower range, shrink epsilon and thereby weaken the desired error, or absorb an `X^{o(1)}` factor into a bounded `H`.

For bounded `H`, this remains the stated uniform main-term-plus-error formula, not a claim that its relative error tends to zero as `X` alone grows.

## 7. What Proposition 12.1 actually does and does not establish

At `U=D^{3/4}`, GM Proposition 12.1 applies for `T^{5/6}<=D<=T` and gives the **upper bound**

\[
R\lessapprox D^{1/2}+T^{1/2}+T^{3/10}D^{1/5}\ll T^{1/2+o(1)}.
\tag{7.1}
\]

Both its displayed simplified version and its integer-`k` infimum version retain the additive `T^{1/2}D^{3-4sigma}` term, which is `T^{1/2}` at `sigma=3/4`.[1] That observation limits what those formulas guarantee; it does not imply `R>=T^{1/2}`.

At the corresponding normalized level `V=D^{-1/4}`, applying the **separate global fourth moment** to (7.1) gives

\[
E_D(V)\ll X^{o(1)}H D^{-1/2}T^{-1/4}.
\tag{7.2}
\]

Set `H=X^h`, `z=X^a`, use the smallest block `D=X^{a/2}` and `T=X^{1-h}` when they lie in the Proposition 12.1 range. For the particular right side of (7.2) to be at most `H^{1/2}` in exponent, its numerical sufficient test is `a>=3h-1`. The unchanged Proposition 1 upper cutoff supplies `a<=1-h/2`, and these two tests overlap only for `h<=4/7`.

The correct reading is:

> With the main piece certified only by Proposition 1, and with the tail treated through these level-set cardinality majorants followed by a separate zeta fourth moment, this calculation supplies no power-saving certificate at `h=4/7`, and the critical-level majorant cannot certify an extension beyond it.

It is **not** correct to read `a>=3h-1` as a necessary condition for the true mixed moment to be small. Likewise the main-piece upper cutoff is a hypothesis of the theorem being invoked, not a theorem that the small-divisor variance misbehaves outside it.

### Compare all listed alternatives, rather than one positive term

At `U=D^{3/4}`, the original GM 1.1 and classical/Huxley formulas give respectively

\[
R\lessapprox D^{1/2}+D^{3/5}+TD^{-3/5},\qquad
R\lessapprox D^{1/2}+TD^{-1/2}.
\]

These are the actual source estimates specialized to the critical level.[1][2] In the refined region `T^{5/6}<=D<=T`, their dominant majorants are `D^{3/5}` and `TD^{-1/2}`, while Proposition 12.1 supplies `T^{1/2}`. Here is the complete comparison of the requested scalar options, with subpower factors suppressed:

| Cardinality input | Dominant measure majorant `Q` | Using Weyl: bound for `E_D(V)` | Using fourth moment: bound for `E_D(V)` |
|---|---|---|---|
| GM Theorem 1.1 | `D^{3/5}` | `H D^{1/10} T^{-2/3}` | `H D^{-1/5} T^{-1/2}` |
| Classical/Huxley | `T D^{-1/2}` | `H D^{-1} T^{1/3}` | `H D^{-3/4}` |
| GM Proposition 12.1 | `T^{1/2}` | `H D^{-1/2} T^{-1/6}` | `H D^{-1/2} T^{-1/4}` |

Indeed, for any row, the Weyl and fourth-moment factors are `H D^{-1/2} Q T^{-2/3}` and `H D^{-1/2} Q^{1/2} T^{-1/2}`. Write `D=T^alpha` and `Q=T^r`. In this region `r>=1/2`, so the Weyl exponent exceeds the fourth-moment exponent by `r/2-1/6>=1/12`. Fourth moment is therefore the better one of those two treatments in every row. The refinement is at least as good as both original cardinality estimates; GM 1.1 and Huxley exchange order at `D=T^{10/11}`, but neither beats the refined result. Taking their minimum does not remove (7.2).

For `D<=T^{5/6}`, GM's critical dominant term is instead `TD^{-3/5}`, and the fourth-moment output is `HD^{-4/5}`. At the transition this again becomes `HT^{-2/3}`. Fixed factors in time from `t -> -2t` must be handled honestly: near `D asymp T^{5/6}`, GM 1.1 already gives these same exponents; alternatively use a bounded number of time subintervals. No exact out-of-range invocation of Proposition 12.1 at a rescaled endpoint is required.

`compare_critical_bounds.py` verifies all of these affine-exponent comparisons on the entire `5/6<=alpha<=1` interval, by exact endpoint checks for each affine difference. Thus the restricted ceiling does survive comparison with the requested alternatives. This is stronger support than merely pointing to an additive term, but it is still only an optimization of the displayed majorants.

### A coverage detail missing from a single endpoint LP

For `4/7<h<2/3`, if the chosen cutoff has `a<(5/3)(1-h)`, the tail still contains the block `D=T^{5/6}`. Its critical majorant is `H T^{-2/3}`, which fails to provide the desired saving. If instead `a>=(5/3)(1-h)`, the smallest block lies in the refined region; the largest permitted cutoff is still below `D=T` and the inequality `a>=3h-1` cannot coexist with `a<=1-h/2`. Thus simply choosing a much smaller cutoff does not escape this **specified majorant test**. This remains a statement about that test, not about arithmetic truth.

### Why an upper-bound term is not a lower-bound obstruction

At the scalar-summary level, take a set of measure `T^{1/2}`, assign `|M|=D^{-1/4}` there, and assign `|Z|=T^{1/8}` there. For `T^{5/6}<=D<=T`, these sizes obey the displayed GM 1.1, GM 12.1, classical cardinality, zeta fourth-moment, zeta second-moment, Weyl, and polynomial second-moment **numerical upper bounds** used by the route. Their mixed contribution has size

\[
\frac HT D^{-1/2}T^{1/2}T^{1/4}
=H D^{-1/2}T^{-1/4}.
\]

So the summary inequalities allow concentration sufficient to saturate this loss. They also allow the level set to be empty, with mixed contribution zero. A positive upper term cannot distinguish these possibilities.

**This is an explicitly artificial scalar concentration model, NOT a constructed Dirichlet polynomial, NOT a possible-zeta theorem, and NOT an example for the Möbius coefficients.** It demonstrates the information discarded by this scalar-bound route. It does not prove non-entailment from every structural consequence of the full analytic theorems.

The exact checker verifies this concentration model at the formal endpoint and at `h=4/7+1/1000`, `a=1-h/2`. At the latter point, all listed scalar upper bounds still allow a mixed exponent exceeding the target by exactly `7/8000`. That is a negative control on inference, not empirical evidence of an actual large variance.

## 8. The subconvexity claim needs a narrow qualifier

The report says that a stronger subconvexity estimate alone would not move the ceiling because other terms remain. That is true if one merely replaces the Weyl term in its already-derived four-term bound and leaves the fourth-moment branches unchanged.

It is **not true as an unrestricted assertion about all uses of stronger subconvexity**. If `|zeta|<<T^{theta+o(1)}`, using that pointwise bound also on the Proposition 12.1 critical set gives

\[
E_D(V)\ll H D^{-1/2}T^{-1/2+2\theta+o(1)}.
\]

This beats the separate fourth-moment exponent precisely when `theta<1/8`. Moreover the pinned GMRR Proposition 2 itself states that Lindelöf allows the different cutoff `z>=H^{1+epsilon}` up to `H<=X^{2/3-epsilon}`.[2] Consequently the defensible claim is only that improving the **old Weyl branch alone**, or using a pointwise exponent still no better than `1/8` on this scalar critical configuration, does not resolve this bottleneck. A blanket assertion covering arbitrarily strong subconvexity is not certified.

No audit here proves that `4/7` is optimal for every application of GM, every single-polynomial argument, every possible subdivision/power trick, or every mixed-moment rearrangement. Those would require a much more precisely defined class of permitted deductions and a genuine optimality argument. The present inputs, used in the displayed manner, do not certify endpoint saving or an extension beyond the endpoint; they do not exclude either in actual mathematics.

## 9. Executed checks and limits

The parent supplied `<repo>/experiments/astra-rh-crt-20260912/gm_parameter_check.json` during this audit. Its own scope already says that its ceiling is only that of a sufficient-inequality system and claims no genuine countermodel. `compare_critical_bounds.py` independently reconstructed all eight recorded epsilon-margin polynomials and their lower bounds, then re-enumerated the three supplied polytopes, verifying their vertex counts and maxima. All checks passed. Its aggregate budget `X^{epsilon^2/1000}` is more conservative than the budget used in this report and supports its stronger `I_2 << H^{1/2-epsilon/3}` target. These arithmetic checks and the analytic derivation above are separate obligations; neither substitutes for the other.

The fixed interval-range exponent `theta=4/7` does not establish a new zero-exclusion claim through the parent's pending Mellin interface. No such interface, RH implication, or new zero exclusion is certified here. The `theta` denoting a hypothetical zeta pointwise exponent in Section 8 is a different parameter.

`python3 check_second_audit.py` exited 0. It uses a separately written exact-rational polynomial implementation, not the first report's constraint list. Its 21 positivity certificates cover the continuous epsilon interval by factoring powers of epsilon and converting the remaining polynomials to a Bernstein basis. It independently checks the GM exponent substitution, monotone-corner inequalities, all aggregate losses, final Cauchy–Schwarz, centering, low-H overlap, and both endpoint tails.

Two fail-closed controls pass:

1. The same scalar-majorant gate rejects `h=4/7+1/1000` at the maximal Proposition 1 cutoff.
2. The same positivity gate rejects an epsilon-loss budget that exhausts the weakest GM saving.

The checker also records the scalar concentration examples described above. The script is **not** a formal verifier of Plancherel, GMRR Proposition 1, or GM Theorem 1.1, and its successful exit is not an optimality proof. The accompanying analytic derivation is indispensable.

Files in this scratch bundle include:

- `report.md` — this audit.
- `check_second_audit.py`, `results.json`, `execution.log` — independent exact checker and its real output.
- `source-excerpts.md`, `source-locators.json`, `citations.json` — exact local source evidence.
- `input-hashes-initial.json`, `input-hashes-final.json`, `verification.json` — read-only/provenance checks and delivery verification.
- `compare_critical_bounds.py`, `critical-comparison.json`, `critical-comparison.log` — GM/Huxley/Weyl/fourth-moment comparison and replay of the parent arithmetic.
- `collect_evidence.py`, `verify_bundle.py` — evidence and fail-closed delivery reproduction helpers.

The evidence helper initially rejected a formula-only quote as too short; the quote was expanded to include its exact preceding sentence and re-run. This was a citation-tool formatting failure, not an analytic or source-access failure. No current-record or publisher-final-version lookup was attempted, because neither was necessary for this delegated, pinned-source audit.

## Sources

[1] https://arxiv.org/src/2405.20552v2 — Guth–Maynard pinned TeX v2
[2] https://arxiv.org/src/2006.04060v2 — GMRR pinned TeX v2

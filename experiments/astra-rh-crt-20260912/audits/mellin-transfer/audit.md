# Quantitative Mellin-transfer and noncancellation audit

## Verdict

**passed:** The transfer lemma is valid as a statement of **holomorphic continuation**, using the given unconditional bound `E(x)=O(x^{1/2})`. The proposed stencil, main exponent, and remainder exponent are correct. The strict zero-free strip `2a < beta < 2-4a` is valid for `1/4<a<1/3`, with no simplicity assumption. Its nonemptiness for `a=a_theta` is exactly `theta>8/9`. Hypotheses for a cofinal family of `theta<1` imply RH.

**critical_issues / necessary qualifications:**

1. Holomorphy for `Re(s)>a>1/4` does **not by the stated cancellation argument** exclude every zero with `beta>2a`. A cancellation can produce a reflected zero at or below `2a`, where the argument cannot be repeated.
2. Specify the partition, its compact initial term, and the support enlargement in the Taylor remainder. Integer shifts at the bottom of the support must be admissible at base scale `X/2`, not merely at `X`.
3. For each compact set, choose the parameters independently of the dyadic index, discard only finitely many small indices, and prove normal convergence. Small scales have `h=0` in the naive formula and cannot use that formula.
4. The conclusion is analytic continuation of the original Mellin integral; it does not assert that the original improper integral converges throughout the new half-plane. It gives neither boundary holomorphy nor an automatic global mean-square error estimate.
5. `theta>8/9` is the threshold for this **nonempty partial zero-free strip**; this argument does not prove RH from a single fixed short-interval exponent above that threshold. No short-interval hypothesis is established by this audit.

## 1. Corrected transfer proof

Fix `0<theta<1` and assume, for each `nu>0`,

    integral_Y^(2Y) |E(x+H)-E(x)|^2 dx <= C_(theta,nu) Y H^(1/2+nu)

for all sufficiently large `Y`, uniformly over integers `1<=H<=Y^theta`. Also assume the given `E(x)=O(x^{1/2})`; in the application it is the squarefree counting error.

### Partition and entire dyadic pieces

Choose a smooth cutoff `chi` on the positive axis with `chi(t)=1` for `t<=1` and `chi(t)=0` for `t>=2`. Put

    phi(t) = chi(t)-chi(2t),
    X_j = 2^(j+1),  j>=0,
    g_(X,s)(x) = phi(x/X) x^(-s)  (x>0),

and extend `g` by zero to `x<=0`. Then `g` is smooth, supported on `[X/2,2X]`. The partition identity is

    chi(x) + sum_(j>=0) phi(x/X_j) = 1,    x>=1.

Indeed the partial sum is `chi(x/2^(N+1))-chi(x)`. The sum is locally finite. Define

    J_X(s) = integral_1^infinity E(x) g'_(X,s)(x) dx,
    J_0(s) = integral_1^infinity E(x) (chi(x)x^(-s))' dx.

Here `J_0` denotes the compact initial piece, not a dyadic index. Every such function is entire, by compact support and differentiation under the integral. Uniformly for `s` in a compact set `C`, with `sigma=Re(s)`,

    ||g_(X,s)||_2 <= C_C X^(1/2-sigma),
    ||g_(X,s)^(r)||_infinity <= C_(C,r) X^(-sigma-r).

### Stencil and its support

Fix an integer `K>=1` and, for all sufficiently large dyadic `X`, set

    h = floor((X/2)^theta / K),
    c_m = (-1)^(m+1) binom(K,m)/m,  1<=m<=K,
    D_(h,K)g(x) = h^(-1) sum_(m=1)^K c_m [g(x)-g(x-mh)].

When `(X/2)^theta/K>=2`,

    (X/2)^theta/(2K) <= h <= (X/2)^theta/K.

Thus `h` is a positive integer, `h` is comparable to `X^theta` with constants depending on `theta,K`, and every `H_m=mh` is an admissible integer shift at both bases `X/2` and `X`:

    1 <= H_m <= Kh <= (X/2)^theta <= X^theta.

For `X>=2`, `(X/2)^theta<=X/2`. Hence the supports of `g'` and all shifted functions lie in

    [X/2, 2X+Kh] subset [X/2, 5X/2].

The coefficient identities are

    sum_m c_m m = 1,
    sum_m c_m m^r = 0,  2<=r<=K.

The first follows from the binomial theorem; the others follow because the `K`th finite difference of a polynomial of degree `<K` vanishes. Taylor expansion through order `K`, with integral remainder, therefore gives

    g' = D_(h,K)g + R_(X,s),
    ||R_(X,s)||_infinity <= C_(C,K) h^K X^(-sigma-K-1).

The remainder vanishes off `[X/2,2X+Kh]`; Taylor's integral remainder only samples derivatives along the intervening segments and introduces no further support. Consequently

    |integral E(x)R_(X,s)(x) dx|
        <= C_(C,K) X * X^(1/2) * h^K X^(-sigma-K-1)
        <= C_(C,K,theta) X^(1/2-sigma-K(1-theta)).

### Pairing the stencil against E

For `X/2>1`, a change of variables, not an integration by parts, gives exactly

    integral_1^infinity E(x)[g(x)-g(x-mh)] dx
      = -integral_(X/2)^(2X) [E(y+mh)-E(y)]g(y) dy.

There is no lower-end term: after shifting, `g(y)` still vanishes below `X/2>1`. Split `[X/2,2X]` into `[X/2,X]` and `[X,2X]`, using the hypothesis at the corresponding bases. It follows that

    ||E(.+mh)-E(.)||_(L2[X/2,2X])
       <= C_(theta,nu) X^(1/2) (mh)^(1/4+nu/2).

Cauchy-Schwarz and the finite sum over `m` now imply

    |integral E D_(h,K)g|
      <= C_(C,K,theta,nu) X^(1-sigma) h^(-3/4+nu/2).

Take `0<nu<=1`, so that the exponent of `h` is negative; comparability with `X^theta` yields

    |J_X(s)| <= C_(C,K,theta,nu) [
        X^(1-3theta/4-sigma+theta*nu/2)
        + X^(1/2-sigma-K(1-theta)) ].                 (1)

This proves both proposed exponents, including the factor `theta*nu/2` after substituting for `h`.

### Explicit parameters and normal convergence

Write `a=1-3theta/4` and let `C` be any compact subset of `Re(s)>a`. Put

    delta = min_(s in C) Re(s)-a > 0,
    nu = min(1,delta/theta),
    K = 1 + floor(max(0,(3theta-2)/(4(1-theta)))).

In fact this `K` depends only on `theta`. It satisfies

    K(1-theta) > max(0,1/2-a).

The two exponents in (1) are respectively at most `-delta/2` and strictly less than `-delta`, uniformly on `C`. Only finitely many dyadic indices are too small for the variance hypothesis or the positive-integer choice of `h`; their `J_X` are already entire and are simply retained as finite terms. Since `X_j=2^(j+1)`, the remaining bounds are summable geometric series. Hence `sum_j J_(X_j)(s)` converges normally on `Re(s)>a`.

For `Re(s)>1/2`, the bound `E(x)=O(sqrt(x))`, bounded overlap of supports, and `g'=O_s(x^(-sigma-1))` justify summing inside the integral. Differentiating the partition gives

    J_0(s) + sum_j J_(X_j)(s)
      = integral_1^infinity E(x) (x^(-s))' dx
      = -s F(s).

It follows, first on the overlap with the new half-plane, that

    F_cont(s) = -[J_0(s)+sum_j J_(X_j)(s)]/s.          (2)

The right side is holomorphic for `Re(s)>a`, because `a>1/4>0`. Equation (2) is the required continuation. No integration by parts against the discontinuous function `E` has been used, and neither a contribution at `x=1` nor a contribution at infinity was dropped.

For `theta<=2/3`, `a>=1/2`, so this conclusion adds nothing to the unconditional integral half-plane. The gain begins strictly at `theta>2/3`.

## 2. Correct noncancellation argument

Assume now that the actual squarefree-error Mellin function has a holomorphic continuation to `Re(s)>a`, where `1/4<a<1/3`. Its given identity

    F(s) = zeta(s)/(s*zeta(2s)) - rho/(s-1)

continues meromorphically by the identity theorem. Let `z=beta+i gamma` be a nontrivial zeta zero with

    2a < beta < 2-4a.

At `s_0=z/2`, `Re(s_0)>a`, and neither `s_0=0`, `s_0=1`, nor a pole of `zeta(2s)` is involved. The term `rho/(s-1)` is holomorphic there. If `z` has multiplicity `m`, holomorphy forces `zeta(s_0)` to have multiplicity at least `m`; otherwise the quotient has a pole. The functional equation and conjugation, whose local factors are nonzero throughout the open critical strip, then produce a zero

    z_1 = 1-conjugate(z)/2,
    beta_1 = 1-beta/2,
    gamma_1 = gamma/2,

also of multiplicity at least `m`. No zero is assumed simple.

Let `L=2a`, `U=2-4a`, and `T(beta)=1-beta/2`. Exactly,

    T(U)=L,
    T(L)=1-a,
    U-T(L)=1-3a>0.

Thus `T((L,U))=(L,1-a)` is a subset of `(L,U)`. Cancellation is therefore forced indefinitely. The resulting zeros satisfy

    beta_n = 2/3 + (-1/2)^n(beta-2/3),
    gamma_n = gamma/2^n.

They converge to `2/3`. Nontrivial zeta zeros are nonreal, so these zeros are distinct, contradicting isolation of zeros at an interior point where zeta is analytic. Alternatively, continuity would imply `zeta(2/3)=0`, whereas the alternating-series identity shows `zeta(u)<0` for `0<u<1`.

Therefore

    zeta has no zero with 2a < beta < 2-4a.            (3)

By reflection, the additional left-hand strip `4a-1 < beta < 1-2a` is also zero-free.

The boundaries are not supplied by this argument: at `beta=2-4a` the reflected zero lands exactly at `beta_1=2a`, where evaluating `F` at half that zero is on the excluded boundary `Re(s)=a`. Likewise a zero initially at `beta=2a` does not trigger the hypothesis. For `beta>2-4a`, the reflected zero falls below that boundary. This is precisely why the broader claim excluding every `beta>2a` is unjustified by cancellation alone.

## 3. Exact theta arithmetic and conditional RH

For `a_theta=1-3theta/4`, the right-hand strip (3) is

    2-3theta/2 < beta < 3theta-2.

It is nonempty exactly when

    2-3theta/2 < 3theta-2
      iff theta>8/9
      iff a_theta<1/3.

At `theta=8/9`, the endpoints both equal `2/3`; there is no open strip. For example `theta=9/10` gives `a=13/40` and the zero-free strip `13/20<beta<7/10`. This is a partial zero-free conclusion, not a proof of RH from that fixed exponent.

If the variance hypothesis holds for every `theta<1` (a cofinal sequence tending to 1 is sufficient), take any putative nontrivial zero with `1/2<beta<1` and choose

    max((4-2beta)/3, (beta+2)/3) < theta < 1.

Both lower bounds are strictly below 1. This choice is exactly the pair of inequalities placing `beta` in the strip above, contradicting (3). The functional equation then excludes zeros with `beta<1/2`. This proves RH conditionally on the all-parameter hypothesis, without any multiplicity assumption or uniformity of constants as `theta` tends to 1.

Equivalently, the compatible continuations glue to a holomorphic function on `Re(s)>1/4`; the same iterative cancellation argument then applies to every nontrivial zero right of the critical line.

## 4. Limitations and useful counterchecks

* **No endpoint conclusion.** In the abstract analytic lemma, for `2/3<=theta<1`, the test function `E_*(x)=x^(a_theta)` satisfies `E_*=O(sqrt(x))` and even the `nu=0` increment estimate. Indeed the mean-value theorem gives an averaged square increment `O(H^2 X^(2a_theta-2))=O(H^2 X^(-3theta/2))<=O(H^(1/2))` for `H<=X^theta`. Its Mellin transform is `1/(s-a_theta)` and has a pole exactly at the boundary. This is not the squarefree error, but it shows the abstract bound cannot give boundary holomorphy.
* **No analytic-continuation-to-global-L2 shortcut.** As a general Mellin counterexample, `E_*(x)=sqrt(x) sin(2*pi*x)` is `O(sqrt(x))` and has an entire continued Mellin transform: repeated integration by parts of the exponential integrals extends it to arbitrary left half-planes, with only entire lower-end terms. Nevertheless, for integer `X>=1`, `integral_X^(2X) |E_*(x)|^2 dx = 3X^2/4`. It is not the actual counting error and is not claimed to meet the all-theta variance hypothesis; it demonstrates that continuation alone supplies no global square-mean bound of the desired small-error scale. Any such conclusion needs a separate theorem with its growth, boundary, and Tauberian/Plancherel assumptions checked.
* **Only a conditional RH implication.** Nothing here proves the starting short-interval variance estimate in a new range or validates any other analytic input. At fixed `theta`, the established transfer and partial zero-free region are exactly those stated above.

## Verification and files

`verify_arithmetic.py` ran successfully under `python3` with exit code 0. Exact rational checks covered stencil moments and differentiation of monomials for `K=1,...,16`, the leading Taylor coefficient `-1/(K+1)`, explicit compact-set exponents at seven rational theta values, integer-shift/support inequalities at exact-power scales, the invariant-strip endpoints and 40-step rational orbits, and the theta choices needed for the conditional RH implication. These finite checks supplement the complete analytic proof; they are not presented as a computer proof of the theorem.

All files are isolated in `mellin-transfer/`. No repository, index, commit, or repository gate was touched. No external literature claim was needed for this audit.

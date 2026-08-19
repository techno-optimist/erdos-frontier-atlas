# Literal common-marker h=8 corollary

This is a corollary only in the existing literal EHPS `A,B`, one-common-marker,
pointwise physical-potential model.  It does not cover phase-owned markers,
context-owned/reuse constructions, or an arbitrary graph language.

## 1. Exact plane-slice Fubini normalization

Let `E` be a measurable subset of the two-torus carrying the restriction of a
single-valued physical potential.  For `u in [0,1)^2` and
`d in (Z/9Z)^2`, put

```text
p_d(u)=(d+u)/9,
S(u)={d : p_d(u) in E}.
```

The 81 maps partition the torus into half-open q9 boxes.  Since their
Jacobian is `1/81`, exactly

```text
mu(E) = (1/81) integral_[0,1)^2 |S(u)| du.              (1)
```

If `a+b=2y mod 9`, then

```text
p_a(u)+p_b(u)=2p_y(u) mod 1.
```

Thus every digit midpoint row lifts with the same residual offset.  The
positive endpoint-cost inequality makes `S(u)` strictly midpoint-convex and
hence peelable.  The combined finite theorem gives `|S(u)|<=31` pointwise,
so (1) yields the arbitrary-measurable slice bound

```text
mu(E) <= 31/81.                                         (2)
```

This is not a digit-union assumption.
No measurability of the potential itself is used: measurability of `E` and
pointwise availability of every physical midpoint inequality suffice.  An
almost-everywhere or packet-only inequality is not covered.

## 2. Exceptional-set marker normalization

Fold the literal EHPS tile by `H_2^2` to `[0,1/2)^2`.  Up to null boundaries,
the relevant complement is the union of

```text
E_0 = {(x,y): x+y>11/12},
S_e = {(x,y): 2/3<x+y<2/3+epsilon}.
```

The first is four copies of a right triangle with legs `1/12`, hence

```text
mu(E_0)=4*(1/2)*(1/12)^2=1/72.
```

For the strip, subtracting the two upper-right triangle areas in the folded
square and multiplying by four gives

```text
sigma:=mu(S_e)=4 epsilon/3-2 epsilon^2.                 (3)
```

Let `M` be the single common marker and `beta=mu(M)`.  On the exceptional
part

```text
K_0=(E_0 x Torus^2) union (Torus^2 x E_0),
```

apply (2) to the free two-dimensional factor and then integrate over `E_0`.
The union bound gives

```text
mu(M intersect K_0)
 <= 2*(1/72)*(31/81)
  = 31/2916.                                           (4)
```

The remainder of the literal `C_A^c` branch lies in the union of the two
factor strips and costs at most `2 sigma`.  The `C_B^c` branch is conjugate by
the existing measure-preserving linear map.  Therefore every surviving common
marker satisfies the safe bound

```text
beta <= 31/2916+2*(4 epsilon/3-2 epsilon^2).            (5)
```

No independence of the two exceptional factors is assumed; (4)--(5) use
only Fubini and union bounds.

## 3. The h=8 density gate

Write `alpha=mu(T_epsilon)`.  EHPS gives

```text
alpha >= 7/24-epsilon.
```

In the literal common-marker construction, each of the eight phase pieces
has measure `beta*alpha^14`.  Their union is at most their sum, whereas the
product benchmark has measure `alpha^16`.  Strictly beating the benchmark
therefore requires

```text
8 beta > alpha^2.                                      (6)
```

Using (5) and the lower bound for `alpha`, the exact gap opposing (6) is

```text
G(epsilon)
 := (7/24-epsilon)^2
    -8*(31/2916+2*(4epsilon/3-2epsilon^2))
  = 1/46656-(263/12)epsilon+33epsilon^2
  = (1-1022544epsilon+1539648epsilon^2)/46656.          (7)
```

At zero the margin is `1/46656`.  The first positive root is exactly

```text
epsilon_* = 2/(1022544+sqrt(1045590073344))
          = 263/792-sqrt(350166)/1782
          = 0.00000097795446700734234643...
```

Consequently `G(epsilon)>=0` throughout the maximal small interval
`0<=epsilon<=epsilon_*`; strict positivity holds before the endpoint.  For
the usual rational choice `epsilon=1/n`, the exact adjacent checks are

```text
G(1/1022543) =  517105/48783242381626944 > 0,
G(1/1022542) = -126359/12195786741535296 < 0.
```

Thus every integer `n>=1022543` lies in the certified strict range.  A round
subwindow, retained for comparison with the earlier q27 conditional audit,
is `0<=epsilon<=1/1100000`; its endpoint gap is

```text
121027187/80190000000000 > 0.
```

Here `epsilon_*<1/1022542<1/4000`, so this entire small interval remains
inside the frozen EHPS exceptional-geometry domain.  The endpoint is included
in the obstruction because beating in (6) is strict: `G=0` still implies
`8 beta<=alpha^2`.

## 4. Literal conclusion and limits

Under precisely the literal one-common-marker and pointwise physical
hypotheses above, no eight-phase union can be strictly denser than the EHPS
product for `0<=epsilon<=epsilon_*`; in particular this holds for
`epsilon=1/n`, `n>=1022543`.

This corollary is an obstruction, not a construction.  It does not prove
`C_9=31`, produce a size-31 support, handle phase-specific or context-owned
markers, perform an integer transfer, improve `r_3(N)`, or solve Erdős
Problem 142.  `verify_finite_geometry.py` checks all rational identities and
the sharp adjacent rational bracket; the measure implication is the proof
given in Sections 1--3, not a numerical integration.

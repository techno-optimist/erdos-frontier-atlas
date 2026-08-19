# Conditional literal common-marker `h=8` corollary

This corollary uses the exact finite result `C9=30`, but it is conditional on
the existing literal EHPS `A,B`, one-common-marker model and pointwise
physical midpoint inequalities. It is not part of the finite proof of
`C9=30`.

## Fubini slice bound

Let `E` be a measurable subset of the two-torus carrying the restriction of a
single-valued physical potential. For `u in [0,1)^2` and
`d in (Z/9Z)^2`, set

```text
p_d(u)=(d+u)/9,
S(u)={d : p_d(u) in E}.
```

The 81 maps partition the torus into half-open boxes and have Jacobian
`1/81`, so

```text
mu(E)=(1/81) integral_[0,1)^2 |S(u)| du.
```

Every digit midpoint row lifts with the same residual offset. The pointwise
physical-potential inequality therefore makes every `S(u)` peelable. The
exact theorem gives `|S(u)|<=30`, hence

```text
mu(E)<=30/81=10/27.
```

This is not a digit-union assumption. Measurability of `E` suffices for
Fubini; the potential need not be measurable, but every relevant physical
midpoint inequality must hold pointwise. Almost-everywhere, packet-only, and
phase-owned inequalities are excluded.

## Marker upper bound

In the folded EHPS exceptional geometry, the fixed triangle part has measure
`1/72`, while the epsilon strip has exact measure

```text
sigma=4 epsilon/3-2 epsilon^2.
```

For the single common marker `M`, `beta=mu(M)`, Fubini on the two free factors
and union bounds give

```text
beta <= 2*(1/72)*(30/81)+2*sigma
     = 30/2916+2*(4 epsilon/3-2 epsilon^2).
```

No independence between exceptional factors is used.

## Exact `h=8` gate

Write `alpha=mu(T_epsilon)`, with the EHPS lower bound
`alpha>=7/24-epsilon`. In the literal common-marker construction, strictly
beating the product benchmark requires `8 beta>alpha^2`. The exact lower
bound on the opposing gap is

```text
G(epsilon)
 = (7/24-epsilon)^2
   -8*(30/2916+2*(4epsilon/3-2epsilon^2))
 = 43/15552-(263/12)epsilon+33epsilon^2
 = (129-1022544epsilon+1539648epsilon^2)/46656.
```

The discriminant of the numerator is

```text
D=1044801773568=5184^2*38878.
```

The smaller root is

```text
epsilon_*
 =258/(1022544+sqrt(D))
 =43/(170424+864*sqrt(38878))
 =0.0001261799133399584874581242293... .
```

The polynomial is nonnegative on the maximal small interval
`0<=epsilon<=epsilon_*`, and positive before the endpoint. The endpoint is
included in the obstruction because beating is strict. For reciprocal
parameters, the exact adjacent checks are

```text
G(1/7926)= 7651/27138877632 > 0,
G(1/7925)=-65309/976753080000 < 0.
```

Thus every integer `n>=7926` is in the certified strict reciprocal window.
Also `epsilon_*<1/7925<1/4000`, so this entire interval lies inside the
frozen exceptional-geometry domain.

## Scope

Under exactly the literal one-common-marker, measurable-set, and pointwise
physical-potential hypotheses above, no eight-phase union can strictly beat
the EHPS product for `0<=epsilon<=epsilon_*`; in particular, not for
`epsilon=1/n` with `n>=7926`.

This is an obstruction, not a construction. It does not cover phase-specific,
context-owned, reuse, almost-everywhere, or packet-only markers; it performs
no integer transfer and makes no claim about `r_3(N)` or Erdos Problem 142.

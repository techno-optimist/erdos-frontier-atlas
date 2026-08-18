# Carving audit for the q=6 cells 91/93 dilation wall

## Verdict

The exact bounded-dilation wall on cells

```text
A = 93 = (5,1,0,0),
B = 91 = (5,1,5,5)
```

has **zero uniform deletion capacity**.  It cannot force the `1/192` measure
loss needed to erase the 117-cell density advantage over `49/576`.

There are two distinct facts.

1. The scalar family used by the current certificate touches only null
   two-dimensional sheets inside the four-dimensional cells.  A null deletion
   kills that literal family.
2. The same rows admit a valid four-parameter strict-interior extension which
   touches the full interiors of both cells.  Even this extension can be
   neutralized by deleting an arbitrarily small corner of cell A.  Moreover,
   an explicit bounded correction satisfies all surviving rows of these two
   families, so this is not merely a failure of the original telescoping
   presentation.

This does not produce a potential for every modular-midpoint triple in the
carved 117-cell support.  It proves only that the R1/R2 dilation mechanism by
itself supplies no support-independent positive deletion lower bound.

## 1. Density arithmetic

Each q=6 four-dimensional cell has measure `6^-4=1/1296`.  The original union
and the EHPS four-dimensional product gate are

```text
117/1296 = 52/576,
(7/24)^2 = 49/576,
margin = 1/192 = 6.75/1296.
```

Deleting either whole cell A or B costs only `1/1296`; deleting both costs
`1/648`.  Both are already below the available margin.  Therefore no argument
whose forced deletions are confined to these two cells can prove a loss of
`1/192` without bringing in additional constraints on other cells.

## 2. The literal scalar family is null

In residual coordinates, the certificate fixes `0<s<1`, `0<t<1/3` and uses

```text
R1 (A,B,B):
  x=(s,s,t,t), y=(s,s,1-t,1-t), z=(s,s,1-3t,1-3t),

R2 (A,A,B):
  x=(s,s,3t,3t), y=(s,s,t,t), z=(s,s,1-t,1-t).
```

Every touched A point lies in

```text
M_A = {(s,s,u,u): 0<s,u<1},
```

and every touched B point lies in the analogous sheet `M_B`.  These are
two-dimensional subsets of four-dimensional cells and have Lebesgue measure
zero.  Deleting `M_A` alone meets every displayed R1 and R2 row.  Thus the
literal certified family has a zero-measure vertex cover.

## 3. Full-dimensional strict-interior extension

The equal residual coordinates are unnecessary.  Take independently

```text
s=(s1,s2) in (0,1)^2,
t=(t3,t4) in (0,1/3)^2,
```

and replace every scalar expression componentwise:

```text
R1:
  x_A=(s1,s2,t3,t4),
  y_B=(s1,s2,1-t3,1-t4),
  z_B=(s1,s2,1-3t3,1-3t4),

R2:
  x_A=(s1,s2,3t3,3t4),
  y_A=(s1,s2,t3,t4),
  z_B=(s1,s2,1-t3,1-t4).
```

All points are in strict cell interiors.  The first two coordinates are
diagonal carry-zero rows.  In each of the last two coordinates, R1 has carry
`-1` and scaled correction requirement `108-24*t_i`; R2 has carry `+1` and
requirement `-36-24*t_i`.  Hence the four-dimensional requirements are

```text
R1(t) = 216 - 24(t3+t4),
R2(t) = -72 - 24(t3+t4).
```

This family projects onto the full interiors of both A and B: R2's `x_A`
ranges over all last-coordinate residual pairs, while R1's `z_B` does the
same in B.  Its point projections therefore have total measure `2/1296`.
Projection volume, however, is not a deletion lower bound.

Write

```text
D_s(u) = h_A(s,u) + h_B(s,1-u),       u in (0,1)^2.
```

Adding R1 and R2 gives the exact vector dilation inequality

```text
D_s(3t)-D_s(t) >= 144-48(t3+t4).       (1)
```

For `t_n=T/3^n`, summing (1) for `n=1,...,N` gives

```text
D_s(T)-D_s(T/3^N)
  >= 144N - 24(T3+T4)(1-3^-N).         (2)
```

## 4. Measurable ray-cover inequality

Let `X_A,X_B` be the deleted residual sets in cells A and B.  For a fixed
first-coordinate residual `s`, define the paired deleted set

```text
E_s = {u : (s,u) in X_A or (s,1-u) in X_B}.
```

If every paired level `T,T/3,...,T/3^N` avoids `E_s`, all N instances used in
(2) survive.  If `|h|<=M`, the left side of (2) is at most `4M`.  Thus, for
every integer N satisfying

```text
144N - 48(1-3^-N) > 4M,                (3)
```

every `s,T` obeys the finite hypergraph-cover inequality

```text
sum_(n=0)^N 1_{E_s}(T/3^n) >= 1.       (4)
```

Integrating (4) over `T in (0,1)^2` and substituting `u=T/3^n` yields

```text
1 <= sum_(n=0)^N 9^n |E_s|
  = ((9^(N+1)-1)/8)|E_s|.
```

Since `|E_s|` is at most the sum of the deleted A and reflected deleted B
slices, Fubini gives the exact M-dependent physical-measure lower bound

```text
mu(X_A)+mu(X_B)
  >= (1/1296) * 8/(9^(N+1)-1).         (5)
```

This proves that a fixed finite potential bound forces some positive deletion
for the full-dimensional family.  But `M` is not bounded uniformly in the
candidate class, and the right side tends to zero rapidly as the required N
grows.  It cannot imply a fixed loss such as `1/192`.

## 5. Arbitrarily small exact evasion of the family

Fix `0<epsilon<1/3` and delete only the A-corner

```text
X_A(epsilon)
  = {(s1,s2,u3,u4): max(u3,u4)<=epsilon}.
```

Its physical measure is exactly

```text
epsilon^2/1296.
```

Every inward dilation ray `T/3^n` eventually enters this corner, so no
infinite telescoping chain survives.  As `epsilon` tends to zero, these are
measurable ray covers of arbitrarily small positive measure.

There is also an explicit bounded correction satisfying every surviving R1
and R2 row.  For `u` with `r=max(u3,u4)>epsilon`, put

```text
L(u) = log_3(r/epsilon),
h_A(s,u)       = 72 L(u) + 72,
h_B(s,1-u)     = 72 L(u) - 72.
```

Set `h_B` arbitrarily, for example zero, where `max(1-v3,1-v4)<=epsilon`;
those values do not occur in a surviving R1/R2 row.  The correction is bounded
by `72(log_3(1/epsilon)+1)` in absolute value.  Whenever an R1/R2 pair
survives, `L(3t)=L(t)+1`, and direct substitution gives

```text
R1 left side = 216 >= 216-24(t3+t4),
R2 left side = -72 >= -72-24(t3+t4).
```

Thus the infimum deletion measure for feasibility of these two row families
is zero.  For the exact rational choice `epsilon=3^-J`, the deletion is
`1/(1296*9^J)` and the displayed correction bound is `72(J+1)`.

## 6. Componentwise transport census

The broad componentwise version may also activate a nonwrap coordinate with
`B'_i=A'_i-1`; its two carries are zero and it contributes zero to the gap,
but its residual still follows `t_i -> 3t_i`.  Require each coordinate to be
either unchanged or of this predecessor form, and require at least one true
wrap coordinate `A'_i=0,B'_i=5`.

An exact enumeration of the 117-cell alphabet gives 66 ordered pairs.  Their
numbers of active coordinates have histogram

```text
1:11,  2:38,  3:10,  4:7,
```

and 61 pairs have one wrap coordinate while five have two.  For a pair with
`k` active coordinates, delete the A-side corner in which all k active
residuals are at most epsilon.  This meets every contraction ray for that
pair.  Taking the union over all 66 pairs costs at most

```text
(11*epsilon + 38*epsilon^2 + 10*epsilon^3 + 7*epsilon^4)/1296,
```

before overlap savings.  It tends to zero with epsilon.  Thus even the full
componentwise predecessor/wrap transport census has ray-cover infimum zero.
This is a cover statement; it does not claim that the pairwise explicit
corrections can be chosen consistently across all 66 overlapping systems.

## Consequence and next viable target

The desired `1/192` deletion theorem is false for the R1/R2 mechanism alone.
A successful carving fence must use geometrically different mechanisms whose
unavoidable deletion regions cannot all be funneled into arbitrarily thin
boundary neighborhoods.  Finite strict-interior balanced packets, or a
noncontracting/cyclic measurable family, are more plausible targets than
additional copies of this dilation template.

Nothing here constructs a correction satisfying the other `98,167` closure
types, performs an integer transfer, improves `r_3(N)`, or solves Problem 142.

# Exact bounded-potential dilation wall on the fixed q=6 117-cell union

This certificate is an exact obstruction for **any bounded, single-valued
physical potential** on the stated fixed 117-cell union that satisfies the
pointwise modular-midpoint/raw-canonical coercivity inequalities.  It assumes
neither affinity, a partition, continuity, nor corner traces.

Write the potential by definition as

```text
H(x) = 2 ||x||^2 + h(x)/36.
```

If `H` is bounded on the fixed union then so is `h`, because the quadratic
term is bounded there.  The coercivity inequality, multiplied by `36`, gives
the exact correction inequality used below.

Let `A=93=(5,1,0,0)` and `B=91=(5,1,5,5)`.  Fix any `0<s<1`, put

```text
a_t=(s,s,t,t)                 in A,
b_t=(s,s,1-t,1-t)             in B,
D(t)=h_A(a_t)+h_B(b_t).
```

For every `0<t<1/3`, the following are actual strict interior residual
witnesses; all three points have the displayed cell code and no closure face
is used.

```text
R1 cells (A,B,B):  (x,y,z)=(a_t, b_t, b_3t)
  carries (0,0,-1,-1), scaled raw RHS 216-48t.

R2 cells (A,A,B):  (x,y,z)=(a_3t, a_t, b_t)
  carries (0,0, 1, 1), scaled raw RHS -72-48t.
```

For coordinates 0 and 1 all residuals equal `s`; for coordinates 2 and 3,
the residual equations are respectively

```text
t + (1-3t) - 2(1-t) = -1,
3t + (1-t) - 2t = 1.
```

Adding the two valid coercivity rows cancels the intermediate values and
gives the pointwise, no-limit inequality

```text
D(3t) - D(t) >= 144 - 96t.                         (1)
```

Now fix `T=1/4`, take `t_n=T/3^n` for `1<=n<=N`, and sum (1):

```text
D(T)-D(T/3^N) >= 144N - 48T(1-3^-N)
                  = 144N - 12(1-3^-N).             (2)
```

If `|h|<=M`, the left side of (2) has absolute value at most `4M`.  Choosing
the finite integer `N=floor((4M+12)/144)+1` makes the right side strictly
larger than `4M`, a contradiction.  This is finite telescoping for each
bounded candidate, not an unverified convergence step.

## Replay

```powershell
python -I verify.py
python -I independent_replay.py
```

The primary and separately written standard-library replays reconstruct the
117 cells, physical residual witnesses, modular carries, raw costs, the
`q^2=36` scaling, and the finite-N inequality.  The independent replay starts
from the original EHPS inequality and rejects planted carry, role-order, and
raw-versus-geodesic mutations.

## Scope fence

The result applies only to this unchanged full q=6 117-cell union and the
pointwise modular-midpoint/raw-canonical coercivity model.  The displayed
curves can have measure zero, so an almost-everywhere inequality is not enough.
It does not cover graph-restricted triples, partial carving, changed cell
ownership, support deformation, a wrapped/geodesic right side, or an unbounded
potential.  It gives no integer construction, new `r_3(N)` bound, or solution
to Erdős Problem 142.

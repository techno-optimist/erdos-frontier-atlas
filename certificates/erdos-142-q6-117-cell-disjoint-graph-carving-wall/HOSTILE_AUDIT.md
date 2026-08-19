# Hostile audit: disjoint finite-state graph-carving wall

Date: 2026-08-19. Read-only audit of the frozen source packet subsequently
packaged in this directory.

## Verdict

**PASS within the packet's stated finite-state, globally pairwise-disjoint,
edge-local, pointwise scope.** I found no gap in the three requested transfer
steps. The q=42 arbitrary-measurable one-block capacity is separately
hash-bound and replayed; this audit supplies an independent graph-theoretic
and spectral composition.

The result does not cover physical tile reuse across contexts, a
transition-dependent potential that is not state-lifted with disjoint edge
ownership, horizon-growing/infinite state spaces, or an almost-everywhere
midpoint condition.

## 1. Diagonal triple states survive endpoint pruning

Let `s` be retained after ordinary start/end pruning. Choose a state path
from an allowed start to `s` and a state path from `s` to an allowed end.
Every retained edge has a nonempty physical tile. Tripling either physical
path uses the same edge and the same physical point in all three copies at
each time; `x=y=z` is always an actual torus midpoint row. Therefore
`(s,s,s)` is reachable from an allowed triple start and co-reachable to an
allowed triple end.

For loop edges `e_x,e_y,e_z:s->s`, every actual ordered midpoint triple of
their physical points is a transition

```text
(s,s,s) -> (s,s,s).
```

Completeness of the ordered triple automaton requires that transition. A
negative defect is then a negative accepted cycle of length one. Triple-state
rank terms and state/endpoint coboundaries have identical endpoints and
cancel. The recurrent-component trimming is needed for the exponential rate,
but the reach/co-reach argument itself already protects the diagonal state.

This conclusion would fail only if repeated physical paths were excluded
from the triple language or if pruning discarded an actually accepted
`x=y=z` path. Either behavior contradicts the packet's complete pointwise
ordered-triple premise.

## 2. Global disjointness gives one function on the loop union

For a fixed state put

```text
E_s = union_(e:s->s) T_e.
```

Pairwise physical disjointness gives each `p in E_s` a unique loop-edge
owner. Thus

```text
f(p)=f_e(p),  p in T_e,
```

is genuinely single-valued even with parallel loop edges and unrelated
bounded residual-dependent edge functions. Given any physical midpoint
triple in `E_s`, its three unique owners are loop edges at `s`; completeness
supplies the corresponding local row, and the preceding self-loop argument
makes its defect nonnegative. Hence `f` obeys the one-block pointwise
coercive inequality on all of `E_s`, including every `x=z` branch.

The hash-bound q=42 packet can therefore be applied exactly as stated:

```text
42^4 mu(E_s) <= A=263277.
```

This descent is the precise reason global disjointness is indispensable. If
one physical point has multiple edge owners, there need not be a consistent
choice of `f(p)`, and summing edge weights need not equal physical union
measure. A general transition cocycle depending on adjacent edge labels is
also outside the stated edge-local-plus-state-coboundary model unless it is
first lifted into the state graph; such a lift must still satisfy global
physical edge disjointness.

## 3. Independent all-state spectral proof

Scale by `42^4` and write `M` for the nonnegative physical adjacency matrix.
Disjoint edge ownership and the diagonal capacity give

```text
sum_ij M_ij <= N=280917,       M_ii<=A=263277.
```

Take a nonnegative unit right Perron vector `x` and symmetrize
`H=(M+M^T)/2`. Then

```text
rho(M)=x^T H x.
```

Let `a` and `b` be the largest and second-largest coordinates of `x` (`b=0`
in dimension one). Put `d_i=H_ii` and `y_ij=2H_ij`. The mass constraint is
`sum d_i+sum y_ij<=N`, while the coefficients of these variables in the
Rayleigh quotient are respectively `x_i^2` and `x_i x_j`.

Only the diagonal at a uniquely largest coordinate can have coefficient
strictly above `ab`, and it receives at most `A` mass. Every other diagonal
has coefficient at most `b^2<=ab`, and every off-diagonal coefficient is at
most `ab`. (If the maximum is tied, `a=b` and the same inequality is
immediate.) Hence, without any assumption on the number of states,

```text
rho(M) <= A a^2 + (N-A)ab.
```

Since `a^2+b^2<=1`, the right side is at most the largest eigenvalue of

```text
[ A        (N-A)/2 ]
[ (N-A)/2      0   ],
```

namely

```text
R=(A+sqrt(A^2+(N-A)^2))/2.
```

This direct Rayleigh argument independently proves the source packet's
all-state extremum and avoids relying on its convex extreme-point case list.
The exact gate substitution is

```text
G=(49/576)42^4=1058841/4,
G^2-AG-(N-A)^2/4=4825657053/16>0,
```

with `G>A`, so `R<G`. The strict rate wall follows.

## Replay

The independent standard-library replay hash-binds all source dependencies,
executes the q=42 measurable-carving verifier, exhaustively checks diagonal
reach/co-reach for every directed graph on at most three states and every
nonempty endpoint choice, rejects an overlapping-owner control, and replays
the spectral arithmetic:

```powershell
python -I certificates\erdos-142-q6-117-cell-disjoint-graph-carving-wall\independent_replay.py --full
```

WSL:

```bash
python3 -I certificates/erdos-142-q6-117-cell-disjoint-graph-carving-wall/independent_replay.py --full
```

# Globally disjoint finite-state graph-carving wall

This package promotes an exact negative theorem for the fixed 117-cell q=6
four-dimensional geometry. It composes the existing arbitrary-measurable
q=42 one-block carving theorem with an all-state spectral argument. It is not
a positive construction and gives no new bound for `r_3(N)`.

## Exact theorem

Let a finite directed multigraph have measurable edge tiles `T_e` contained
in the fixed 117-cell union `U`. Assume:

- all physical edge tiles are pairwise disjoint over every edge label;
- the ordered triple-path automaton is complete for every actual physical
  torus-midpoint fibre, including all `x=z` and `x=y=z` branches;
- its edge-local bounded residual-dependent potentials, finite state or
  endpoint coboundaries, and triple-state ranking give no negative accepted
  defect cycle.

Trim to states that are reachable from an allowed start, can reach an allowed
end, and lie in a recurrent rate-contributing component. For

```text
W_st = sum_(e:s->t) mu(T_e),
```

the weighted physical adjacency matrix satisfies

```text
rho(W) < 49/576.
```

Thus no finite-state language in this globally disjoint edge-ownership model
clears the four-dimensional EHPS density gate. The result allows any finite
number of states and parallel edges and arbitrary measurable carving inside
the fixed physical geometry.

## Why loop mass is capped

For a retained state `s`, put `E_s=union_(e:s->s) T_e`. Tripling a physical
path proves that the diagonal triple state `(s,s,s)` is both reachable and
co-reachable whenever `s` is. Every compatible triple of loop edges is a
self-loop at that triple state. A negative local defect would itself be a
negative accepted cycle; state and ranking coboundaries cancel on the
self-loop.

Global physical disjointness gives every point of `E_s` one edge owner, so
the edge-local functions descend to one single-valued function on `E_s`.
The q=42 arbitrary-measurable carving theorem therefore applies pointwise:

```text
42^4 mu(E_s) <= A=263277.
```

This step is invalid if one physical subtile is reused under several labels;
that escape is explicitly outside the theorem.

## Uniform spectral bound

Scale `W` by `42^4` and write `M`. Pairwise edge disjointness and the loop
cap give

```text
M>=0,    sum_ij M_ij<=N=280917,    M_ii<=A.
```

For a nonnegative unit Perron vector, symmetrize and let `a>=b` be its two
largest coordinates. At most `A` mass can have Rayleigh coefficient `a^2`;
every remaining diagonal or off-diagonal mass has coefficient at most `ab`.
Consequently

```text
rho(M) <= A a^2+(N-A)ab
       <= (A+sqrt(A^2+(N-A)^2))/2.
```

This proof is independent of the number of states. With `N-A=17640` and
`G=(49/576)42^4=1058841/4`, exact substitution gives

```text
G^2-AG-(N-A)^2/4 = 4825657053/16 > 0,
```

so the algebraic upper root is strictly below the gate. The rational witness
`263573` also lies above the root and below `G`.

## Portable replays

From the repository root on Windows:

```powershell
python -I certificates\erdos-142-q6-117-cell-disjoint-graph-carving-wall\verify.py --self-test
python -I certificates\erdos-142-q6-117-cell-disjoint-graph-carving-wall\independent_replay.py --full
```

Linux or WSL:

```text
python3 -I certificates/erdos-142-q6-117-cell-disjoint-graph-carving-wall/verify.py --self-test
python3 -I certificates/erdos-142-q6-117-cell-disjoint-graph-carving-wall/independent_replay.py --full
```

Both trust paths hash-bind and execute the existing q=42 measurable-carving
dependency. The independent replay imports no primary module, exhaustively
checks diagonal endpoint pruning on every directed graph with at most three
states and every nonempty endpoint mask, tests physical-function descent and
rejects an overlapping-owner control, and independently proves the spectral
bound.

Expected verdicts are
`PASS_DISJOINT_FINITE_STATE_GRAPH_CARVING_WALL` and
`PASS_INDEPENDENT_DISJOINT_GRAPH_CARVING_WALL_AUDIT`.

## Exact horizon-two parity companion

The supporting packet in `horizon2-parity-wall/` closes one concrete escape
outside global edge disjointness. For every one-red-per-packet coloring of
the q=42 full-box alphabet, the horizon-two even-red language contains a
seven-word, seven-row physical common-offset Farkas cycle, so it admits no
single-valued global coercive potential. The replay checks every red-role
alignment on the unique seven-point packet and the exact positive cost.

```text
python3 -I certificates/erdos-142-q6-117-cell-disjoint-graph-carving-wall/horizon2-parity-wall/verify.py
```

This companion kills only that exact full-fine-box parity construction. It
does not extend the graph theorem to arbitrary overlapping or reused tiles,
and it is not carving-stable.

## Scope

Proved only for fixed finite-state systems, globally pairwise-disjoint
physical edge ownership, edge-local potentials plus finite state/endpoint
corrections, a complete pointwise ordered-triple automaton, and the fixed
117-cell geometry.

Not proved: repeated or overlapping physical tiles across contexts;
transition-memory not state-lifted with disjoint ownership; a separately
decoded overlap kernel; infinite or horizon-growing state systems; an
almost-everywhere midpoint hypothesis; a different physical geometry; an
EHPS shell construction or integer transfer; a new `r_3(N)` bound; or Erdős
Problem 142.

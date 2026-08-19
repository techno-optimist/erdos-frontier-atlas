# Disjoint, total-decoder, and homogeneous-partial walls

This package promotes three exact negative theorems for the fixed 117-cell
q=6 four-dimensional geometry, plus one abstract weighted-support boundary.
The first composes the arbitrary-measurable q=42 one-block carving theorem
with an all-state spectral argument under globally disjoint edge ownership.
The second permits repeated full-box ownership and arbitrary transition
memory, but requires a complete total deterministic q42 decoder with
coaccessible reachable states. The third covers color-homogeneous partial
deterministic interfaces through fifteen states for one frozen q42 coloring.
None is a positive construction or a new bound for `r_3(N)`.

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

This parity companion by itself kills only that exact full-fine-box
construction and is not carving-stable. The next section gives the broader
complete-total full-box theorem.

## Complete total deterministic overlap/reuse companion

The exact packet in `universal-total-decoder-wall/` closes every finite state
count when all 280,917 q42 full boxes remain available as total state maps.
The decoder has one fixed start, deterministic physical-word ownership, and
every reachable state has an accepting suffix. The potential on accepted
words may be arbitrary, global, nonadditive, unbounded, and state-aware.

For a minimum-rank idempotent `e` of the transition monoid, put `I=im(e)`.
For each of the seven packet-role maps `tau_i`, minimum rank makes
`e tau_i e` a permutation of `I`. If the physical word `u` realizes `e`, a
common exponent `L` and one accepting suffix `s` make all seven words

```text
u (p_i u)^L s
```

accepted. Common positions are diagonal and each of the `L` role positions
is the exact physical seven-point packet. The whole-word potential incidence
cancels, while the exact positive costs are `L*16/7` in raw canonical
coordinates and `L*11/7` for intrinsic torus-geodesic distance.

The primary replay reconstructs the actual translated four-dimensional q42
roles, audits both costs, exhausts the sandwich implication through five
states, and checks a four-state nonsynchronizing nonpermutation example. The
separately written hostile replay enumerates all 699 three-state submonoids,
1,623 minimum-rank idempotents, and 12,868 sandwiches, and also tests the dead
sink and partial-decoder seams.

```text
python3 -I certificates/erdos-142-q6-117-cell-disjoint-graph-carving-wall/universal-total-decoder-wall/verify.py
python3 -I certificates/erdos-142-q6-117-cell-disjoint-graph-carving-wall/universal-total-decoder-wall/independent_replay.py
```

Expected verdicts are `PASS_UNIVERSAL_TOTAL_DECODER_WALL` and
`PASS_MINRANK_IDEMPOTENT_SANDWICH_AUDIT`.

## Homogeneous partial and weighted-support boundaries

Fix the support-disjoint q42 packet packing and choose exactly one red box in
each of its 17,640 packets; color all remaining 263,277 boxes blue. A
color-homogeneous partial deterministic interface has one fixed start, a
nonempty accepting set, and at most one blue and one red successor at each
state. Transitions depend only on the color, not on the individual physical
box. Its rate is the accepted-language limsup, equivalently the Perron root
after reachable/coaccessible live trimming.

The earlier exact source and hostile replays in
`homogeneous-partial-six-state-extension/`, together with the byte-bound lower
state packet in `homogeneous-partial-five-state-wall/`, remain finite-census
corroboration. The structural theorem and its fifteen-state residual extension
prove that every such interface with at most fifteen live states and no
nondegenerate seven-multisunflower has rate at most

```text
B = 263277 < G = 1058841/4.
```

The structural source and hostile replays in
`homogeneous-partial-fourteen-state-wall/` supersede the finite S6 census, and
`homogeneous-partial-fifteen-state-extension/` closes its sole new acyclic
residual. On a strong live component write `W=BA+RC`. If the partial blue map
is acyclic, the positive integer vector
`v=(I+A+...+A^(m-1))1` gives

```text
Wv <= Bv-(B-mR)1 < Bv                    (m<=14).
```

If the blue map has a directed cycle, strict Perron monotonicity leaves only
the spanning blue-only cycle at equality. Every other strong table has a red
exit and an explicit closed word `u`; comparing `u^k` with an all-blue word
of the same length gives a unit-red seven-copy loop for every ordered
start/target pair. The independently replayed physical dependency reconstructs
the full 17,640-packet packing and turns that abstract loop into a positive
raw-canonical whole-word Farkas obstruction. At fifteen states, the only
remaining blue shape is the Hamiltonian chain. Exact Collatz vectors reduce
every above-`B` red completion to 16 maps, and explicit words plus an
independent 232,560-state product replay find all 3,600 ordered witnesses
(shortest horizon at most 18). A separate hostile replay checks all 25,200
red-role physical lifts.

The new `weighted-multiset7-twolevel/` companion strengthens the earlier
support-language boundary. Chvatal--Hanson gives the sharp graph caps
`A_2=42`, `B_2=33`; a restricted-link matching argument yields the coupled
recurrence with `A_3=672`, `B_3=560`. Exact rational LYM/cap dual arithmetic
keeps the optimum at 1 through dimension 28 and excludes the physical gate
through dimension 33. The failures at dimensions 29 and 34 are relaxation
failures only. Packet avoidance still does not construct a physical potential.

The certifying aggregate runs the fourteen-state structural replay, the
fifteen-state residual extension, and the two-level weighted replay
concurrently with the legacy paths:

```text
python3 -I certificates/erdos-142-q6-117-cell-disjoint-graph-carving-wall/verify_all.py
```

The older exhaustive finite-state corroborating paths remain available outside
the fast Makefile target:

```text
python3 -I certificates/erdos-142-q6-117-cell-disjoint-graph-carving-wall/homogeneous-partial-five-state-wall/independent_replay.py
python3 -I certificates/erdos-142-q6-117-cell-disjoint-graph-carving-wall/homogeneous-partial-six-state-extension/independent_replay.py
```

The aggregate retains the compatibility marker
`PASS_DISJOINT_AND_TOTAL_OVERLAP_REUSE_WALLS` and ends with
`PASS_DISJOINT_TOTAL_AND_PARTIAL_FIFTEEN_STATE_WALLS`.

## Scope

The measurable graph theorem is proved only for fixed finite-state systems,
globally pairwise-disjoint physical edge ownership, edge-local potentials plus
finite state/endpoint corrections, and a complete pointwise ordered-triple
automaton. The overlap/reuse companion instead covers complete q42 full-box
total deterministic decoders with unique physical-word ownership and an
accepting suffix from every reachable state.

The partial companion covers only the frozen one-red-per-packed-packet
coloring, color-homogeneous partial deterministic interfaces with at most
fifteen live states, and accepted-language/live-trim rate. Still not proved:
sixteen or more live states; physical-symbol-dependent or arbitrarily state-carved transitions;
an arbitrary same-count coloring; nondeterministic or multiple-path ownership;
arbitrary overlapping or carved measurable subtiles; infinite or
horizon-growing state systems; an
almost-everywhere midpoint hypothesis; a different physical geometry; an
EHPS shell or integer transfer; a new `r_3(N)` bound; or Erdős Problem 142.
The accepted rate is always the Perron root of the live trim; an ambient
unreachable or noncoaccessible dead-sink Perron root is irrelevant.

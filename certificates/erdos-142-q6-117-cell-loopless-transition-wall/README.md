# q=6 117-cell loopless transition-cocycle wall

This scratch packet is an exact negative result for the smallest synchronized
Markov extension of the fixed 117-cell offset model.  It is not a P142 result,
does not give an integer construction, and makes no new `r_3(N)` claim.

## Decoder and continuous row semantics

The alphabet is the 117-cell q=6 set in the supplied six-deletion certificate:

```text
U = {(a1,a2,a1+d1,a2+d2) mod 6 : a in S0, d in D}.
```

Cells retain their decoder indices in the source ordering (`a in S0` outer,
`d in D` inner).  For a scalar cell triple `(a,b,c)`, the canonical
raw-endpoint branch convention is

```text
ell = 6*carry - (a+c-2*b) in {-1,0,1}.
```

Its within-cell offset interval is `[1/2,1]`, `[0,1]`, or `[0,1/2]` for
`ell=-1,0,1` respectively.  The verifier evaluates the affine q^2-scaled
right side at the endpoint that maximizes it, in exact `Fraction` arithmetic.
These are closure suprema of the half-open branches and so are necessary for
the actual continuous rows.  A 4D triple is legal precisely when all four
coordinate branches are legal; its exact RHS is their sum.

## Strictly richer synchronized open-path class

Use the loopless complete directed graph on `U`: a transition `a -> b` is
admissible iff `a != b`.  For a path `c_0,...,c_{m-1}` define

```text
P_m(c) = g[c_0]/2 + sum_{i=0}^{m-2} H[c_i,c_{i+1}] + g[c_{m-1}]/2,
F_m(x) = 2||x||^2 + P_m(cell(x_0),...,cell(x_{m-1})).
```

There are independent real `g[a]` and directed pair values `H[a,b]`; this is
a genuine transition/cocycle extension.  It contains additive cell offsets:
set `H[a,b]=(g0[a]+g0[b])/2` and `g=g0`, which gives
`P_m=sum_i g0[c_i]`.  Its range is `O(m)` for bounded tables.

For exact agreement with the source certificate's integer convention, write
`G[a]=36*g[a]` and `J[a,b]=36*H[a,b]`.  The replay checks coefficients of
`G,J` and the raw-canonical q^2-scaled RHS.  This is exact multiplication of
each actual coercivity row by 36, rather than an informal normalization.

It has the usual finite endpoint residual: concatenating paths at a common
state `s` gives `P(uv)=P(u)+P(v)-g[s]`.  A Markov-shell transfer would need to
cancel that residual by matching endpoints or slice to one of the finite 117
endpoint states.  This packet stops earlier: it proves the two-block member
of this exact class infeasible, so no such transfer can start for this fixed
loopless graph.

For two synchronized local triples `r=(x,y,z,b)` and `s=(x',y',z',b')`, the
required row is

```text
g[x]/2 + H[x,x'] + g[x']/2
+ g[z]/2 + H[z,z'] + g[z']/2
- 2*(g[y]/2 + H[y,y'] + g[y']/2) >= b+b'.
```

All three directed pairs must be loopless.  The checker constructs the exact
smallest nontrivial synchronous pricing universe: two physical 4D blocks, the
16 legal local rows on the four active cells, and all 100 eligible paired rows.
It then verifies that each of the five CEGAR cuts belongs to that universe and
recomputes each carry, branch supremum, raw cost, and incidence.  A positive
dual needs no numerical pricing assumptions; it is already a wall for the
full 117-state graph because the five rows are valid there.

## Common-tail padding: all lengths

The initial ray has two physical 4D blocks, but it excludes every length
`m>=2` in this same position- and length-independent table class.  Append the
common diagonal tail `(0,0,0),(1,1,1),(0,0,0),...` after its two local rows.
Each tail coordinate is a genuine carry-zero row with RHS zero.  Cells `0,1`
are outside `{41,67,80,83}`, so the join is loopless; alternation keeps the
tail loopless.

For each padded row, a common-tail transition has coefficient `1-2+1=0`.
At the join, its `J[second,p]` coefficient cancels by the original ray's
zero second-block incidence; each common terminal `G[p]/2` term cancels
directly within its row by `1-2+1=0`.  Initial `G` and first-transition
coefficients are exactly the two-block ones.  Hence the five positive weights
cancel every `G,J`
coefficient while retaining RHS `1032` for every `m>=2`.  Both replays build
and check the concrete lengths `2,...,9` as an executable audit of this
general coefficient argument.

## Exact five-row wall

The five rows in `markov_loopless_wall.json` use only cells
`{41,67,80,83}` and directed transitions
`{(41,67),(41,83),(67,80),(80,41),(83,80)}`.  With positive weights
`1,2,1,1,1`, every `g` endpoint coefficient and every `H` coefficient cancels
exactly, while the q^2-scaled raw RHS is

```text
228 + 2*120 + 168 + 228 + 168 = 1032 > 0.
```

Thus the selected synchronized rows imply `0 >= 1032`, an exact Farkas
contradiction.  Since every selected row is a valid row of the complete
loopless graph, this excludes the entire stated potential class already at
two physical 4D blocks.

The density side would have been viable: the loopless complete graph has
Perron root `rho=116`, hence q=6 4D path density base

```text
116/6^4 = 29/324 > 49/576 = (7/24)^2.
```

The negative result therefore closes this precise mass-passing Markov choice,
not endpoint-restricted languages, sparse/deformed/different transition
graphs, position- or length-dependent tables, within-cell potentials, state
lifts, higher q, continuum thickening, or EHPS transfer.

## Replay

```powershell
python -I .\verify_markov_loopless_wall.py .\markov_loopless_wall.json --self-test --max-length 9
python -I .\independent_replay.py .\markov_loopless_wall.json --self-test --max-length 9
Get-FileHash .\markov_loopless_wall.json -Algorithm SHA256
```

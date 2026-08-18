# Endpoint-pruned extension of the q=6 117-cell transition wall

## Result

Let `A` be a zero-one adjacency matrix on the fixed 117 q=6 cells, and let
`u,v in {0,1}^117` be nonzero endpoint-indicator vectors.  Put

```text
N_m = u^T A^m v,
r(u,A,v) = limsup_(m -> infinity) N_m^(1/m).
```

The support of `u` is the allowed start set and the support of `v` is the
allowed end set.  If each cell has volume `1/1296`, the corresponding disjoint
path-box union at `m+1` blocks has literal volume

```text
1296^(-(m+1)) u^T A^m v.
```

One may separately replace the indicator entries on their supports by fixed
positive weights.  The resulting `u^T A^m v` is then a weighted partition
function, not the literal union volume.  Since the state set is finite, fixed
positive weights change the count by only support-dependent constant factors
and have the same exponential rate as the indicator vectors.

Use the usual quadratic normalization on the physical path box,

```text
F_m(x)=2||x||_2^2 + Phi_m(c_0,...,c_m)/36.
```

For every finite real-valued correction table `Phi_m` which is single-valued
and constant on an accepted label sequence, suppose the raw-canonical modular
midpoint inequality is required for every compatible triple of accepted paths.
The correction may be position-dependent, length-dependent, and nonadditive;
no uniform bound in `m` is assumed.  It need not have endpoint/edge-table form.
The right sides below are the exact `q^2=36`-scaled closure requirements after
the universal quadratic term is removed.

Then every reachable/co-reachable Perron component of radius greater than 103
produces an exact two-row contradiction at every sufficiently large horizon
in each residue class on which that component contributes accepted paths.  In
particular,

```text
r(u,A,v) > 441/4
```

cannot be supported on a subsequence of wall-free horizons.  More sharply, if
`H` is any infinite collection of sufficiently large horizons at which this
two-row wall is absent, then

```text
limsup_(m in H) (u^T A^m v)^(1/m) <= 103 < 441/4.
```

Consequently fixed endpoint pruning, finite-horizon selection, and periodicity
do not reopen the unweighted fixed-state graph lane above the EHPS
four-dimensional numerator gate.

This is stronger than the unrestricted-endpoint statement, but its potential
scope is still label-only.  It does not cover a potential depending on the
within-cell residual point, coupled edge tiles, weighted/multi-edge state
lifts, repeated physical labels, position-dependent supports, or endpoint
sets depending on the horizon.

## 1. Reachable/co-reachable Perron core

Let `C` run over the strongly connected components of the directed graph of
`A` which are reachable from `supp(u)` and from which `supp(v)` is reachable.
Frobenius normal form gives

```text
r(u,A,v) = max_C rho(A[C]).
```

The use of `limsup` is essential for periodic graphs.  One direction follows
by block-triangular path decomposition (only polynomially many component
transitions can accompany the largest exponential factor).  For the reverse
direction, fix paths from `supp(u)` into `C` and from `C` to `supp(v)` and
insert walks internal to `C`; the fixed prefix and suffix do not alter the
root growth rate.

Thus a rate above `441/4` supplies a reachable/co-reachable irreducible core
`C` with `rho(A[C]) > 441/4`.

## 2. A sandwich-pair Perron lemma

Use the certified matching of 27 disjoint bad pairs.  A matched pair `{a,b}`
inside `C` is **sandwiched** if it has both

```text
q -> a, q -> b                 (a common predecessor q in C),
a -> p, b -> p                 (a common successor p in C).
```

Claim: if `C` has no sandwiched matched bad pair, then

```text
rho(A[C]) <= 103.
```

Write `k=|C|` and let `h` be the number of the 27 matched pairs wholly
contained in `C`.  Since 63 vertices are unmatched, a subset can contain at
most `63+27=90` vertices without completing a matched pair, so

```text
h >= max(0,k-90).
```

For every one of those `h` pairs, absence of a sandwich means either its two
outneighborhoods in `C` are disjoint or its two inneighborhoods in `C` are
disjoint.  If both are disjoint, choose either designation.  Let `r` pairs be
designated out-disjoint and `h-r` in-disjoint.

For a positive right Perron vector `x` and `S_x=sum_(j in C) x_j`, each
out-disjoint pair satisfies

```text
rho(x_a+x_b) <= S_x.
```

Treating those `r` pairs as blocks and every remaining vertex as a singleton
gives `rho <= k-r`.  Applying the transpose argument to a positive left
Perron vector and the `h-r` in-disjoint pairs gives

```text
rho <= k-(h-r).
```

Therefore

```text
rho <= min(k-r,k-h+r)
    = k-max(r,h-r)
    <= k-ceil(h/2).
```

For `k<=90` this is at most 90.  For `91<=k<=117`, substitute
`h>=k-90`; the maximum is 103 (at `k=116,117`).  This is strictly below
`441/4 = 110.25`.

Hence every above-gate reachable/co-reachable Perron core contains a
sandwiched pair from the exact 27-pair matching.

## 3. Padding the local wall into accepted paths

Fix the sandwiched pair and witnesses `q,p` in `C`.  Reachability supplies an
accepted prefix from `supp(u)` to `q`; co-reachability supplies an accepted
suffix from `p` to `supp(v)`.  Between them form two accepted label paths

```text
A_path = prefix, q, a, p, suffix,
B_path = prefix, q, b, p, suffix.
```

They agree at every block except the displayed `a/b` block.  The two global
necessary modular-midpoint closure rows use label triples

```text
(A_path,B_path,B_path),
(A_path,A_path,B_path).
```

All common blocks use a diagonal local witness of cost zero.  At the distinct
block they use the certified legal rows `(a,b,b)` and `(a,a,b)`, whose summed
q^2-scaled raw closure cost is 72 or 144.  Some scalar maxima in the certified
ledger are one-sided half-open-box suprema.  This causes no attainment issue:
because `Phi_m` is constant on the label box and the quadratic term is
continuous, inequalities at interior witnesses imply the same necessary
inequality after taking the one-sided limit.  The two closure rows may take
their limits independently.

For any label-path correction `Phi_m`, the scaled correction left sides are
exactly

```text
Phi_m(A_path)-Phi_m(B_path),
Phi_m(B_path)-Phi_m(A_path).
```

They cancel without any endpoint, transition, or position bookkeeping, and
the right sides sum positively.  Thus the two required inequalities are
inconsistent.

Because `q` lies in a strongly connected component, it lies on a positive
length closed walk.  Repeating that common closed walk in both paths before
the branch already produces the same contradiction on an unbounded arithmetic
progression of horizons.

There is also an exact residue-strengthening.  Give `C` its standard cyclic
class map `chi`, so every edge raises `chi` by one modulo the period `d`.
Since `q->a->p`, one has `chi(p)-chi(q)=2 (mod d)`.  For any fixed route from
an allowed start into `C` and from `C` to an allowed end, replace its internal
passage by

```text
entry -> ... -> q -> (a or b) -> p -> ... -> exit.
```

The cyclic-class increments telescope, so this replacement has exactly the
same length residue modulo `d` as the original internal passage.  The eventual
periodicity theorem for a finite irreducible digraph then supplies such walks
at every sufficiently large length in that residue.  Thus the wall occurs on
every eventual residue class to which `C` contributes, not merely on one
arithmetic progression.

Equivalently, for each entry state `r` and exit state `z` of `C`, there is a
constant `L(C,r,z)` such that, for every admissible length `n>=L(C,r,z)`, there
exists an `r`-to-`z` branch-and-merge path pair of exactly length `n`.  Here
"admissible" means that an `r`-to-`z` internal walk of length `n` exists.  No
claim is made that a particular original walk is locally rewritten.  This is
the safest formulation when other components before or after `C` also contain
cycles.

There are finitely many components and entry/exit pairs.  On a wall-free
horizon, every accepted path therefore spends only a uniformly bounded number
of steps in each sandwiched component.  In the condensation DAG a path visits
each component at most once.  After absorbing those bounded passages into a
constant factor, all unbounded dwell time occurs in sandwich-free components,
each of radius at most 103.  Standard Frobenius path decomposition (including
its harmless polynomial factors from chains of equal-radius components) gives
the restricted-limsup bound stated above.

## 4. Exact finite-horizon condition and limitation

At a prescribed horizon `m` (number of transitions), this particular
one-block sandwich witness exists at an interior position `t`, `1<=t<=m-1`,
whenever there are a matched bad pair `{a,b}` and states `q,p` such that

```text
(u^T A^(t-1))_q > 0,
A[q,a]=A[q,b]=A[a,p]=A[b,p]=1,
(A^(m-t-1) v)_p > 0.
```

Endpoint pruning can suppress the wall at isolated short horizons even when
the full accepted-language asymptotic rate is above gate.  For example, take
the complete looped digraph on any 112 of the 117 states and `u=v=e_s`.  Its accepted-path rate is
112, but at horizon one the only accepted path is `(s,s)`, so there are not
two label paths for this two-row cancellation.  At horizon two, any retained
matched bad pair gives paths `(s,a,s)` and `(s,b,s)`, so the evasion is only a
finite-prefix phenomenon.  This example shows why the theorem has an
"every sufficiently large active horizon" qualifier rather than claiming
every horizon without exception.

## Scope fence

The argument is exact for the fixed 117 physical cell labels, a single
position-independent zero-one adjacency graph, fixed zero-one endpoint
indicators, disjoint product path boxes, and potentials constant on each complete
label path after the universal quadratic normalization.  It neither constructs
nor rules out residual-dependent
potentials, weighted/repeated-label automata, horizon-varying endpoint masks or
transition graphs, carving/deformation, an integer transfer, a new `r_3(N)`
bound, or a solution of Erdős Problem 142.

## Replay

The primary and structurally independent replays are standard-library only:

```powershell
python -I verify_endpoint_pruned_extension.py
python -I independent_replay.py
```

The independent replay imports no primary code.  It rederives the matched
closure gaps from the quadratic carry identity, enumerates every matching/core
incidence pattern and mixed left/right designation, checks whole-path and
position-indexed feature cancellation, audits cyclic residues, and retains the
112-state short-horizon control.

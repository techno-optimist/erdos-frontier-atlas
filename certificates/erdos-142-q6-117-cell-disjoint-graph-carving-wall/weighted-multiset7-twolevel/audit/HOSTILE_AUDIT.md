# Hostile audit: two-level weighted multiset-7 bound

Date: 2026-08-19.

## Verdict

**APPROVE.** The source package's graph bases, restricted-link argument,
double-count recurrence (including the floor in the restricted recurrence),
and exact LYM/gate horizons are correct in the stated support-family scope.
The audit found no theorem-blocking defect and made no edit to the source
package.

Source package:

```text
D:\p42_scratch\erdos142_weighted_multiset7_twolevel_20260819
```

The source manifest is bound at

```text
d73625924640cb570077f0cff5128eee8591503ef65743458e748ed7892da1cf
```

and the independent audit pins all four source files, including that
manifest.

## Chvatal--Hanson applicability

For a simple graph, seven distinct 2-sets form an ordinary seven-sunflower
only in one of two ways: an empty-core seven-edge matching or a singleton-core
seven-edge star. Thus a safe graph has

```text
nu <= 6,  Delta <= 6,
```

and the restricted base additionally has `nu<=5`.

The Chvatal--Hanson extremal formula for a simple graph with matching number
at most `nu` and maximum degree at most `Delta` is

```text
f(nu,Delta)
 = nu*Delta
   + floor(Delta/2)*floor(nu/ceil(Delta/2)).
```

This is the formula in the cited paper (DOI
`10.1016/0095-8956(76)90004-6`); the audit also checked the original Stanford
report and a modern theorem restatement. At `Delta=6` it gives

```text
f(6,6)=36+3*2=42,
f(5,6)=30+3*1=33.
```

The audit recomputes the matching numbers with an edge-subset recursion
independent of the source verifier. It recovers

```text
2 K_7:                  edges=42, Delta=6, nu=6,
K_7 disjoint-union K_2,6: edges=33, Delta=6, nu=5.
```

Hence `A_2=42` and `B_2=33` are both valid and sharp. The one-uniform bases
`A_1=6`, `B_1=5` are immediate.

## Restricted-link check

Let `M` be a maximum matching of size `m`, `U=union(M)`, and `W=V-U`. A
maximum matching is maximal, so every family member meets `U`; equivalently
`e_0=0`.

For `u in U`, the full link

```text
L_u = {F-{u}: u in F in family}
```

is a safe `(k-1)`-uniform family. Seven disjoint link members would lift to a
seven-sunflower with core `{u}`, so `nu(L_u)<=6` and `|L_u|<=A_{k-1}`.

The restricted link needed for `e_1` is precisely

```text
L_u^W = {F-{u}: F intersect U = {u}}.
```

If it contained six disjoint members, append the unique matching member
`E_u in M` containing `u`. Its petal `E_u-{u}` lies in `U-{u}`, whereas all
six restricted petals lie in `W`. The seven petals are nonempty and pairwise
disjoint, so these seven original members form a forbidden sunflower with
core `{u}`. Therefore

```text
nu(L_u^W)<=5,
|L_u^W|<=B_{k-1}.
```

Summing over the `km` vertices of `U` gives exactly

```text
e_1 <= km B_{k-1},
sum_j j e_j <= km A_{k-1}.
```

There is no collision in the first sum: a member counted by `e_1` has a
unique vertex in `U`.

## Double count and floors

Because `e_0=0`, the coefficient of every `e_j`, `j>=1`, in

```text
e_1 + sum_j j e_j - sum_{j>=3}(j-2)e_j
```

is exactly two. Hence the displayed expression is `2|F|`. Every member of
`M` is contained in `U`, so `e_k>=m`; consequently

```text
sum_{j>=3}(j-2)e_j >= (k-2)m.
```

Writing

```text
D_k = k(A_{k-1}+B_{k-1})-(k-2),
```

the exact conclusion is

```text
2|F| <= m D_k.
```

For the unrestricted safe class `m<=6`, so `A_k=3D_k` is valid. For the
restricted class `m<=5`, integrality gives

```text
B_k=floor(5D_k/2).
```

The independent recurrence reproduces

```text
A_1..A_7 = 6,42,672,14778,406386,13410726,516312936,
B_1..B_7 = 5,33,560,12315,338655,11175605,430260780.
```

In particular, the strengthened rank-three cap `A_3=672<744` is exact
recurrence arithmetic.

One expository sentence would make the source proof even tighter: state
explicitly before the double-count identity that `e_0=0` because a maximum
matching is maximal. The inference is valid as written and is not a blocker.

## Independent exact LYM dual

Put `q_k=n_k/C(d,k)`. The relaxation is

```text
maximize  sum_k q_k C(d,k) x^k,
subject to sum_k q_k <= 1,
           0 <= q_k <= min(1,A_k/C(d,k)).
```

Rather than reuse the source's greedy fractional-knapsack implementation, the
audit solves the one-constraint LP dual. For a nonnegative threshold `theta`,
the dual objective is

```text
theta + sum_k c_k max(C(d,k)x^k-theta,0),
c_k=min(1,A_k/C(d,k)).
```

Its minimum occurs at zero or a density breakpoint. The audit evaluates all
breakpoints with exact `Fraction` arithmetic and independently reconstructs a
primal allocation with the same value. Exact primal-dual equality holds in
every dimension through 80.

The boundary values are

```text
U_28 = 125300742320/127027375281 < 1,
U_29 = 43814487440/42342458427 > 1,
U_33 = 29626668521680/25278447680919 < (2401/2388)^33,
U_34 = 30583883241680/25278447680919 > (2401/2388)^34.
```

The exact unit margins are

```text
1-U_28 = 1726632961/127027375281,
U_29-1 = 1472029013/42342458427.
```

All dimensions `1..28` lie strictly below one, and 29 is the first failure of
that relaxation. All dimensions `1..33` lie strictly below the q42 gate, and
34 is the first gate failure of the relaxation. The audit confirms the source
language correctly treats the failures at 29 and 34 as relaxation failures,
not constructions.

For the optimization over all safe antichains, the empty-support singleton
has mass one. Since an antichain containing the empty set contains nothing
else, the strict nonempty bound proves the exact optimum is one through
dimension 28, exactly as claimed.

## Scope

Approved only in the stated binary support-family/LYM-relaxation scope. This
does not construct a physical potential, make packet avoidance sufficient,
prove a dimension-34 wall, give an all-state automaton theorem, improve
`r_3(N)`, or resolve Erdos Problem 142.

## Replay

Native Windows:

```powershell
.\run.ps1 -SourceDir <source-package>
```

WSL/Linux:

```sh
sh ./run.sh <source-package>
```

The terminal marker is

```text
PASS_INDEPENDENT_TWO_LEVEL_WEIGHTED_HOSTILE_AUDIT
```

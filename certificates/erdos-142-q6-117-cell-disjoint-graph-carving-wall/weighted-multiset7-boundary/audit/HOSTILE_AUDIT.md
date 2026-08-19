# Hostile audit: weighted multiset-7 sunflower packet

Date: 2026-08-19

Verdict: **APPROVE**.

Audited source, read-only:

```text
D:\p42_scratch\erdos142_weighted_multiset7_sunflower_20260819
```

This audit imports no source-packet module and changes no source, Atlas, or PR
file. Its independent verifier uses direct multiset enumeration, an exact LP
primal/dual pair, count-vector synchronized DFA states, and table-filling DFA
minimization. The source packet and this audit both pass under native Python
and WSL Python.

## Source bytes audited

```text
9313303477481dd313f96532750a07f0cdb06f6abee3276fec4028f099797045  README.md
37e9674e49d5fbeb3793cd2a21c06797082d8027c0b4ff2a63103020cf2a8692  THEOREM.md
431307c1bc4463988ec7cd4d3f6d585237f7eeac98ed35e5347fc48b43cd7534  FINITE_STATE.md
10e584bc7974ae2216bd1dd9d004e50ed12d9146c3c45a580ad632eaf3374775  verify_weighted_multiset7.py
1d221fc9c847616708e24f8cf80f6557150c606f3326a891e56f3b29a9a1d89e  finite_state_explorer.py
40808472fd211a4435f087de96b7471d7c3d247ad83b033a2a8a92282b29d2a0  run.ps1
c54c33d95df9979be73b683d42af4ab858c7791684252fba808b56bfa0c87f22  SHA256SUMS
```

The source manifest binds the six theorem/replay payloads. This audit also
pins the manifest itself. The source directory's `__pycache__` contains only
the two expected local-script bytecode files and is not treated as payload.

## Multiset equivalence

The reduction is exact. If `A` is a proper subset of `B`, six copies of `A`
and one copy of `B` have column weights only 0, 1, and 7, with a unit column.
Thus literal safety forces an antichain.

Conversely, in a forbidden multiset let `K` be the weight-seven coordinates.
Writing `S_i=K union P_i`, the petals are pairwise disjoint. If two supports
repeat, their equal disjoint petals are empty, so both equal `K`. A required
unit column belongs to another nonempty petal, giving a strict superset of
`K`, which contradicts antichainness. Hence an antichain obstruction has seven
distinct supports and is precisely a nontrivial ordinary 7-sunflower.

The independent verifier enumerates all 170,544 seven-multisets on four
coordinates. Exactly 135 are forbidden; all 135 are repeated-pattern
inclusion obstructions. Their distinct-support counts are

```text
2 supports: 65
3 supports: 55
4 supports: 14
5 supports:  1
```

Containment of those directly enumerated multisets agrees with the reduced
criterion on all 65,536 families. Exactly 168 are safe. A seven-singleton
ordinary sunflower and a six-singleton safe control cover the distinct seam.

## Tensor closure and uniformization

Projection of a forbidden product septuple into either coordinate block again
has allowed column weights. A projected unit column would contradict safety
of that factor. With no unit column, every projected coordinate is constant
across all seven words, so each projection consists of seven equal supports.
If both projections are constant, the product septuple has no unit column,
which is impossible. Weighted mass multiplies because ranks add.

The independent replay checks all 400 tensor products of the 20 safe
three-coordinate families and exact mass multiplicativity.

Uniformization is also sound. If a finite safe block has mass `W>1`, its
`t`-fold tensor power is safe, has mass `W^t`, and has at most `td+1` rank
slices. Some slice has mass at least `W^t/(td+1)>1` for sufficiently large
`t`. That slice is uniform and safe. Conversely a uniform safe family of mass
above one is already such a block. Since

```text
x = R/B = 40/597,
```

the exact uniform threshold is `(597/40)^k`.

## Exact uniform ranks and recursion

`M_1=6`: seven distinct singletons are a sunflower and six are safe.

For rank two, ordinary seven-sunflowers in a simple graph are exactly a
seven-edge star or seven-edge matching. Hence a safe graph has maximum degree
and matching number at most six. Vizing's theorem partitions its edges into at
most seven matchings, each of size at most six, proving `M_2<=42`. Two
vertex-disjoint copies of `K_7` have 42 edges, degree six, and matching number
six, proving equality. The independent matching DP and degree replay verify
the witness and `42*(40/597)^2<1`.

The strengthened recursion has no missing multiplicity term. A maximal
matching has `m<=6` disjoint members and union `U` of size `km`; every family
member meets `U`. Each link at `u in U` is a safe `(k-1)`-uniform family. The
link sum counts every member at least once and each of the `m` matching members
exactly `k` times, so

```text
|F| + (k-1)m <= km M_(k-1).
```

The right side after rearrangement increases with `m`, giving

```text
M_k <= 6*(k M_(k-1) - (k-1)).
```

The independent values are `6, 42, 744, 17838, 535116, 19264146` through
rank six. The six-cone comparison has mass multiplier `6x=240/597<1` and is
correctly presented only as a safe construction, not growth.

## Exact LYM/cap LP

For a safe family not containing the empty set, antichainness gives LYM mass
at most one and every rank is bounded by the proved uniform cap. The stated LP
is therefore a valid relaxation. Its objective per unit LYM mass at rank `k`
is exactly `C(d,k)x^k`, so descending-density fractional knapsack is exact.

The audit independently matches the greedy primal with the exact dual

```text
min over lambda >= 0 of
lambda + sum_k cap_k * max(density_k-lambda, 0).
```

There is zero rational primal/dual gap in every dimension 1 through 40. The
four boundary values are

```text
U_28 = 126899718320 / 127027375281  < 1
U_29 =   44332119440 /  42342458427  > 1
U_31 =   16421746480 /  14114152809  < y^31
U_32 = 90704272317040 / 75835343042757  > y^32.
```

Thus the exact optimum over all safe families is one through dimension 28:
the empty singleton family attains one, while every nonempty-rank family lies
strictly below it. No safe family beats the gate through dimension 31. The
fractional failures at dimensions 29 and 32 are LP points with fractional LYM
allocations; the source correctly makes no construction or existence claim
from them.

## DFA and regular-language claims

The synchronized-product test is exact. A literal obstruction column is
constant zero, constant one, or one of seven unit columns. Quotienting ordered
seven-tuples by component permutation loses no transition: for a unit column,
only the current state of the chosen component matters. The audit uses the
alternative count-vector representation of a seven-element multiset and
agrees with the fully ordered product on every complete one- and two-state
DFA.

Fixing the start to state zero loses no labeled language, since any chosen
start can be renamed. The exact independent enumeration is

```text
states  presentations  globally safe  distinct minimal safe languages
  1           2              1                       1
  2          64             23                       4
  3        5832           1454                      27
```

Minimal languages are reconstructed independently using reachable-state
table filling and canonical breadth-first renaming. Every one- and two-state
minimal safe language occurs in the three-state enumeration by unreachable
state padding.

For each of the 27 minimal languages, the audit independently finds the same
kind of exact bounded sequence: finite support, constant/geometric tail,
parity-geometric, or `d*x^(d-1)` and its factor-`x` version. The candidate's
annihilator divides the exact weighted transition characteristic polynomial,
and its first `|Q|` terms equal the matrix sequence. Both sequences therefore
satisfy the same monic order-`|Q|` Cayley-Hamilton recurrence and agree at all
lengths. Every form is at most one. In the derivative case, after `d=1` the
successive ratio is at most `2x=80/597<1`. Since `y>1`, mass at most one also
precludes a positive-length gate violation.

The planted controls are correct: accept-all on one state is unsafe; the
single word `1^d` at each length is safe; and the exact-one-1 language is
unsafe from length seven. Partial automata are covered only after adding and
counting a rejecting sink, exactly as the source states.

Unrestricted regularity is indeed equivalent to the finite-block question.
A globally safe regular slice of mass above one is already a winning finite
block. Conversely, fixed-length parsing makes `C*` regular, and its
multiple-of-block-length slices are precisely the safe tensor powers of `C`.
The SCC/return-word observation is also sound: a return path cannot leave and
reenter an SCC, common accessible/coaccessible prefix and suffix columns are
constant, and Perron growth above one supplies an equal-length return block of
mass above one along a periodic subsequence.

## Scope

The source consistently claims only a binary-support packet screen. It does
not infer a physical potential from packet avoidance, does not infer an actual
family from either failed LP relaxation, and does not claim a four-state or
unrestricted sunflower bound. These limitations are necessary and correctly
retained.

## Replay

Audit package, native Windows:

```powershell
.\run.ps1
```

Audit package, WSL:

```text
sha256sum -c SHA256SUMS
python3 -I independent_weighted_multiset7_audit.py
```

Success marker:

```text
APPROVE_WEIGHTED_MULTISET7_SUNFLOWER_PACKET
```

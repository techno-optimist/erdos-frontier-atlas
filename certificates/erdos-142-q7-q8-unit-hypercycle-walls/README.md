# Cyclic-line and five-row affine walls at q=7 and q=8

This packet turns the q=4 and q=6 torsion walls into a structural hypercycle
screen and applies it exhaustively to every maximum-mass D4 orbit at q=7 and
q=8.  Full cyclic lines close q=8.  At q=7 they are absent, but a minimal
five-row affine hypercycle closes all maximum orbits anyway.

Run:

```text
python -I verify.py --self-test
python -I independent_replay.py
```

The verifier is self-contained and stdlib-only.  It derives the exact EHPS
supports from their rational inequalities, reconstructs all D4 images and role
assignments, and uses only integer and `Fraction` arithmetic.  It imports no
solver, discovery table, sibling certificate, or stored witness.
`independent_replay.py` is separately written and imports neither the primary
verifier nor any exploratory artifact.

## General cyclic-line lemma

Let `G=(Z/qZ)^d`, let `S` be a subset of `G`, and suppose that for some `A,d`
the full affine cyclic line

```text
A_j = A + j*d,  j in Z/kZ,
```

lies in `S`, where `d` has exact order `k>=3`.  For every `j`,

```text
A_(j-1) + A_(j+1) = 2 A_j  (mod q).
```

Thus a putative global potential `H:S->R` must satisfy the `k` rows

```text
H(A_(j-1)) - 2H(A_j) + H(A_(j+1))
    >= ||A_(j-1)-A_(j+1)||^2_raw.
```

Summing over the cycle cancels every full physical variable: each vertex occurs
twice as an endpoint and once with coefficient `-2` as a center.  Since `k>=3`,
`2d` is nonzero, so every endpoint pair is distinct and every raw canonical
squared cost is positive.  The result is the exact contradiction

```text
0 >= a positive number.
```

This single lemma contains the q=6 order-three torsion triangle and the q=4
order-four line wall as special cases.  It assumes no separability, boundedness,
regularity, or coordinate formula for `H`.

## Why the factorized census is complete

A cylinder vertex consists of three two-dimensional quotient points.  Any
global affine line therefore splits into three two-dimensional affine lines
with one shared cylinder-label sequence.  A local block step need not have
global order `k`: its order may be any divisor of `k`, including one.  The
global step has exact order `k` precisely when the least common multiple of the
three block orders is `k`.

For every orbit representative, line length, and cylinder coordinate, the
verifier exhausts all `q^2` starts and all `q^2` steps.  It records every label
sequence allowed by each local line, stratified by the exact block-step order.
It intersects the three label-sequence sets and retains exactly those order
triples whose LCM is `k`.  Hence:

- every retained sequence constructs a genuine global cyclic line; and
- every global cyclic line must appear in the retained set.

This divisor/LCM audit matters.  Requiring every two-dimensional block to have
exact order `k` is a valid sufficient screen but is not a complete census.

The q=7 five-row search uses the same exact factorization with the fixed affine
coefficient pattern `c=(0,1,4,3,6)`: in each local block it exhausts all starts
and all steps of order one or seven, records every compatible five-label
sequence, intersects the three local maps, and then retains exactly the shared
sequences whose combined step has order seven.  Thus constant local blocks are
allowed, but the six-dimensional global step must be nonzero.

## Common maximum-mass classification

At both q=7 and q=8 the exhaustive `8^5=32768` assignment scan finds exactly
256 maximum assignments.  They form 32 global-D4 orbits of size eight.  With
`P1` normalized to image zero, the representatives again have the exact form

```text
(P1,P2,P3,B,K) = (0,p2,p3,b,k),
p2 in {0,1,2,3}, p3 in {0,2}, b in {1,3}, k in {0,2}.
```

Each maximum has five pairwise-disjoint full cylinders.  Disjointness is
checked exactly through the product-support intersection criterion, and it
attains the absolute upper bound `5|T|^3`.

## q=8: all maximum orbits are walls

The exact q=8 EHPS support has 15 points.  Therefore

```text
maximum mass    = 5*15^3 = 16875,
maximum density = 16875/8^6 = 16875/262144,
gate ratio      = (16875/262144)/(7/24)^3 = 455625/175616,
mass margin     = 280009/7077888 > 0.
```

The complete cyclic census gives:

| order | covered max orbits | feasible label sequences per orbit | total |
|---:|---:|---:|---:|
| 4 | 32/32 | exactly 64 | 2048 |
| 8 | 32/32 | 272 through 576 | 13568 |

These are counts of feasible shared cylinder-label sequences, not counts of
all geometrically oriented copies of a line.

For each orbit and each order, the replay selects one deterministic line and
checks full cylinder membership, exact step order, every modular midpoint and
integer carry, raw canonical costs, and physical-variable coefficient
cancellation.  Global D4 transport of the 32 order-four certificates covers
all 256 maximum assignments; the order-eight certificates independently do
the same.

The selected order-four walls have raw contradiction 128 through 256,
normalized by `8^2` to 2 through 4.  The selected order-eight walls have raw
contradiction 192 through 384, normalized to 3 through 6.

Consequently every maximum-mass q=8 D4 union is impossible for an arbitrary
global potential.  This is a four-row structural wall, so the q=8 maximum lane
does not require a large LP certificate.

## q=7: no full line, but every maximum orbit has a five-row wall

The exact q=7 support has 11 points, and

```text
maximum mass    = 5*11^3 = 6655,
maximum density = 6655/7^6 = 6655/117649,
gate ratio      = 91998720/40353607,
mass margin     = 51645113/1626379776 > 0.
```

Every nonzero element of `(Z/7Z)^6` has order seven, so order seven is the only
possible nontrivial cyclic-line length.  The complete factorized census finds
zero *full seven-point lines* in every one of the 32 maximum orbits.  This
negative result is exact, but it is not the end of the structural screen.

Consider five affine points

```text
V_i = A + c_i d,       c = (0,1,4,3,6),
```

where the global step `d` is nonzero, and use the center permutation

```text
pi = (2,4,0,1,3).
```

For `i=0,...,4`, take endpoints `(V_i,V_(i+1))` and center `V_pi(i)`.
The five scalar identities are

```text
c_i + c_(i+1) = 2 c_pi(i)  (mod 7),
```

with exact residuals `(-7,-7,7,7,0)` before reduction.  Hence the five rows

```text
H(V_i) - 2H(V_pi(i)) + H(V_(i+1))
  >= ||V_i-V_(i+1)||^2_raw
```

are valid modular midpoint rows.  The endpoint edges form a five-cycle, while
`pi` is a permutation, so every vertex occurs twice as an endpoint and exactly
once with coefficient `-2` as a center.  All global-potential coefficients
cancel with unit multipliers.  Every consecutive coefficient difference is
nonzero modulo seven; since `d` is nonzero, all five costs are positive.

This five-row pattern is minimal within the connected unit-cycle/permuted-
center template class.  Exhaustion of every center permutation over `F_7`
gives:

| cycle length | kernel-nullity census |
|---:|---:|
| 3 | 6 permutations of nullity 1 only |
| 4 | 24 permutations of nullity 1 only |
| 5 | 115 of nullity 1; exactly 5 of nullity 2 |

The nullity-one kernel is the constant configuration.  Thus no nonconstant
template of this class exists below five rows, while the displayed `pi` is one
of the five first singular permutations.

The complete factorized affine-pattern census finds this five-row wall in all
32 q=7 maximum orbits.  There are 200 through 228 feasible shared cylinder-
label sequences per representative, 6976 total.  One deterministic witness per
orbit is checked semantically and transported by global D4 to all 256 maximum
assignments.  Selected raw contradictions range from 140 through 280,
normalized by `7^2` to `20/7` through `40/7`.

Therefore every maximum-mass q=7 D4 union is impossible for an arbitrary
global potential, despite containing no full affine order-seven line.  This is
the compact structural explanation for the much larger exact LP/Farkas wall.

## Replay controls and boundary

The primary replay rejects planted wrong midpoints, raw costs, missing cycle
rows, occurrence-labelled variables, a nonmaximum assignment, an invalid
coordinate-block order LCM, wrong cylinder membership, a corrupted q=7 center
permutation, a corrupted affine coefficient, a constant q=7 global step, and a
missing fifth row.

The `(7/24)^3` mass gate is an external input from the home capacity lane; this
packet checks the quotient masses, ratios, and margins but does not re-derive
the gate.  The theorem covers only the exact finite q=7/q=8 EHPS D4 full-
cylinder unions.  It makes no claim for deformed or thickened supports,
continuum limits, correlated subblocks, scalar digit encodings with cross-
block carries, or the construction-to-integers transfer.

No new `r_3(N)` bound is claimed, and Erdős Problem 142 is not solved.  The
packet closes every maximum q=7 and q=8 orbit for arbitrary global potentials.

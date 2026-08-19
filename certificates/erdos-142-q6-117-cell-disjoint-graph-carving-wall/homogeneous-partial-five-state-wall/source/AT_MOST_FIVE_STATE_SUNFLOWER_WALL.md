# At-most-five-state homogeneous partial-decoder sunflower wall

Date: 2026-08-19. This is a scratch-only exact theorem package. It changes no
Atlas, pull-request, or previously frozen packet.

## Rate convention and theorem

Put

```text
B = 263277,  R = 17640,  N = B+R = 280917,
G = 1058841/4,  G-B = 5733/4.
```

Fix the physical coloring supplied by the support-disjoint q42 packet packing:
choose exactly one red box in each of its 17,640 packets and color every other
q42 box blue.  Support disjointness makes these choices globally consistent,
so there are exactly `R=17640` red boxes and `B=263277` blue boxes.  The
abstract weighted-automaton exhaustion below depends only on the two weights
`B,R`; its physical Farkas consequence uses this one-red-per-packed-packet
coloring, not an arbitrary coloring having the same global counts.

A color-homogeneous partial deterministic binary interface has at most five
states, one fixed start, a nonempty accepting set, and at most one successor
from each state on blue and red. Every physical q42 box of the same color uses
the same color transition.

For clarity, the rate in this theorem is the accepted-language rate

```text
lambda = limsup_m Z_m^(1/m),
```

where `Z_m` is the number of accepted physical-box words of length `m`.
Unreachable states and states that cannot reach acceptance are deleted, and
transitions entering a deleted state become undefined. This live trim
preserves the accepted language exactly. If it is nonempty, its weighted
matrix is

```text
W_st = B*1[delta(s,blue)=t] + R*1[delta(s,red)=t]
```

and `lambda=rho(W)`. The spectral radius of an ambient unreachable or
noncoaccessible sink is deliberately irrelevant.

**Theorem.** If an at-most-five-state color-homogeneous partial deterministic
interface contains no nondegenerate seven-multisunflower, then

```text
lambda <= B = 263277 < G = 1058841/4.
```

The bound is sharp: the one-state blue-only loop has rate `B` and its binary
language has one all-blue word at every length.

This strengthens the required h=8 gate wall: the exhaustive five-state search
was run for every strongly connected table with `rho>B`, not merely `rho>G`.

## Unique ownership and accepted-word rate

The fixed start and deterministic transitions give every physical word one
state path. Half-open q42 boxes are disjoint, so no physical word is counted
twice. At horizon `m`, after live trimming,

```text
Z_m = e_start^T W^m 1_accept.
```

Every state is reachable from the start and can reach acceptance. Therefore
each Perron SCC can be entered by a fixed prefix and exited by a fixed suffix;
standard nonnegative-matrix growth, including periodic subsequences, gives
`limsup Z_m^(1/m)=rho(W)`.

## Reduction to live strongly connected blocks

Suppose for contradiction that a safe live trim has `rho(W)>B`. Choose a
strongly connected diagonal block `C` with `rho(W_C)=rho(W)`. Restrict every
transition leaving `C` to be undefined. This gives a strongly connected
partial binary table on `r=|C|<=5` states with weighted matrix exactly `W_C`.

Choose a state `c in C` and one fixed prefix taking the original start to
`c`. Choose `q in C` with one fixed suffix from `q` to the original accepting
set. A seven-multisunflower from `c` to the singleton target `q` in the
restricted table becomes an accepted sunflower in the original interface by
adding that common prefix and suffix. Added columns are constant across the
seven words, so the unit column and nondegeneracy remain.

The independent Python replay exhausts every labeled strongly connected
partial table on one through four states. The five-state C++ replay exhausts
one representative of every simultaneous state-conjugacy orbit. In both
replays, every above-blue table, every start, and every singleton target has a
sunflower. Thus every possible live Perron block is covered.

This reduction is why a high-rate dead sink is not a counterexample: it is not
in the reachable/coaccessible trim and contributes nothing to `Z_m`.

## Exact five-state orbit enumeration

A labeled five-state partial table has ten entries, each undefined or one of
five targets, for `6^10` possibilities. State permutations act by simultaneous
conjugacy:

```text
delta'(sigma(s),bit) = sigma(delta(s,bit)),
```

with undefined fixed.

The verifier generates rooted accessible tables directly. Starting from root
zero, scan blue and then red transitions in breadth-first state order and give
the first unseen target the next state label. The resulting restricted-growth
encoding is canonical for a rooted accessible table. Conversely every
generated encoding is accessible and occurs once. A strongly connected table
is accessible from every root; taking the lexicographically least of its five
rooted canonical encodings leaves exactly one representative of every
unrooted `S5` orbit.

The exact census is

```text
rooted accessible canonical tables       632700
rooted strongly connected tables         320253
strong simultaneous-S5 orbits             64057
strong orbits with rho > B                 54184
strong orbits with rho > G                 49047
```

The rooted counts are counts of canonical encodings with a distinguished
root, not labeled-table counts. The 64,057 count is the unrooted orbit count.

## Exact Perron comparisons

For a rational scalar `s=n/d`, the verifier forms the integer Z-matrix

```text
n I - d W.
```

The possibly singular M-matrix criterion gives

```text
rho(W) <= n/d
iff
every principal minor of n I-dW is nonnegative.
```

All 31 nonempty principal minors are evaluated by the signed permutation
formula. No floating-point eigenvalue or tolerance is used. For the gate test,
every matrix entry has absolute value at most `1123668`. A determinant term
uses at most five entries and a determinant has at most 120 terms, so the
absolute bound `120*1123668^5` is below `2^127`; signed 128-bit arithmetic is
exact throughout. The blue comparison is smaller.

## Symmetric seven-copy product and horizons

A product state is a five-component occupancy histogram of seven decoder
copies plus one activity bit recording whether a unit column has appeared.
There are

```text
2*C(11,4) = 660
```

possible states. Constant-blue and constant-red columns move every occupied
copy on that transition. For a unit column, choose the current state of its
unique red copy; one copy moves on red and all other copies move on blue.
Copies occupying the same state are symmetric, so choosing one representative
of each occupied state is an exact quotient of the ordered `5^7` product.

For each above-blue orbit representative, the verifier runs all five starts.
An active pure histogram with all seven copies at target `q` is exactly a
seven-multisunflower ending at singleton `q`. All five targets are reached for
every start. Consequently every nonempty accepting set is covered by choosing
one target that it contains.

There are `54184*25=1354600` representative start/target checks. Automorphisms
can make some checks isomorphic; this is a coverage census, not a count of
interface isomorphism classes. The largest reachable quotient graph has 335
states. Exact shortest-horizon counts are

```text
 1:26426   2:141451  3:344137  4:399252  5:264911
 6:120113  7:38799   8:12029   9:4009   10:1510
11:682    12:376    13:277    14:181    15:139
16:98     17:60     18:35     19:32     20:27
21:23     22:14     23:10     24:6      25:3
```

The maximum shortest horizon is 25. One exact maximum case, with entries
listed as `(blue_0,red_0,...,blue_4,red_4)`, is

```text
delta = (-1,1, 2,-1, 3,-1, 4,-1, 1,0),
start = target = 0.
```

The replay extracts the seven accepted binary words

```text
1000110001100011000110001
1000000000000000000000001  (six copies)
```

and independently checks their paths. Repeated red-position words are allowed
by the literal multiset definition.

## Lower live-SCC replay

The separate standard-library verifier enumerates all labeled partial tables
for SCC sizes one through four and uses the same exact M-matrix and symmetric
product criteria:

```text
states  tables   strong  rho>B  rho>G  start/target checks  max horizon
1            4        4      1      1            1               1
2           81       25     17     15           68               4
3         4096      828    644    566         5796               9
4       390625    60654  49662  44370       794592              16
```

Every check has a witness. This package therefore proves its reducible case
without depending on any earlier theorem file or on the spectral radius of an
untrimmed ambient table.

## Physical q42 lift

For the fixed q42 packing, use the unique cyclic seven-role prototype

```text
p0=( 2,29)  p1=( 8,41)  p2=(14,11)  p3=(20,23)
p4=(26,35)  p5=(32, 5)  p6=(38,17)
```

with balanced midpoint rows

```text
(p1,p0,p6)  (p0,p1,p2)  (p0,p2,p4)  (p1,p3,p5)
(p3,p4,p5)  (p4,p5,p6)  (p2,p6,p3).
```

At a constant abstract column use one common physical symbol. At every unit
column reuse all seven roles of any one actual size-seven packet from the
frozen packing.  The one-red-per-packet coloring makes exactly one of those
roles red and the other six blue; cyclically align that chosen red role with
the unique red word.  Cyclic transitivity covers every possible choice of the
red role.  Color homogeneity preserves the accepted state paths. A common
strict-interior offset makes every displayed modular row an exact uniquely
owned physical midpoint row.

The C++ replay checks role incidence cancellation, every displayed row under
all seven cyclic alignments, and the exact canonical raw cost sums

```text
16/7, 22/7, 20/7, 24/7, 22/7, 18/7, 18/7.
```

It separately checks wrapped torus cost `11/7` in every alignment. Every
active column therefore contributes positive cost. Summing the seven
whole-word midpoint inequalities cancels every potential value and leaves a
positive right side. Common prefix and suffix columns contribute zero and do
not disturb cancellation. Thus every above-blue interface covered by the
theorem contains an exact physical Farkas obstruction for every red-role
choice.

## Scope and nonclaims

Proved: every color-homogeneous partial deterministic interface with at most
five states for the frozen one-red-per-packed-packet q42 coloring;
accepted-language rate and unique ownership; exact live-SCC reduction;
simultaneous-S5 orbit exhaustion; exact Perron comparisons; exact seven-copy
quotient reachability; shortest horizons; and the physical q42 lift.  The
abstract binary automaton census itself uses only the weights `B,R`.

Not proved: a wall for six or more states; a transition table that distinguishes
physical boxes of the same color; arbitrary measurable carving within boxes;
an arbitrary red/blue coloring with counts `B,R` but without one red role in
every packed packet; or existence of a physical potential on a sunflower-free
language. Packet avoidance remains only a necessary escape from this
obstruction family.

## Replay

Windows:

```powershell
.\run.ps1
```

Linux or WSL:

```sh
./run.sh
```

Success markers:

```text
PASS_Q42_SIZE7_PHYSICAL_ROLE_GEOMETRY
PASS_FIVE_STATE_STRONG_ORBIT_WALL
PASS_LOWER_ONE_THROUGH_FOUR_LIVE_SCC_WALL
PASS_AT_MOST_FIVE_STATE_SUNFLOWER_WALL
```

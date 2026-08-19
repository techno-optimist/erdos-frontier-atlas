# Hostile audit: at-most-five-state homogeneous q42 wall

Date: 2026-08-19

## Verdict

**APPROVE** the explicitly refrozen package at
`D:\p42_scratch\erdos142_q42_partial_at_most_five_state_wall_20260819`.

The first snapshot had one scope defect: global weights `B,R` alone do not
imply that a size-seven packet has exactly one red role.  The refrozen theorem
now explicitly fixes the support-disjoint q42 packet coloring, chooses one red
box in each of all 17,640 packets, colors every other box blue, and restricts
the physical Farkas consequence to that coloring.  It separately states that
the abstract automaton census depends only on `B,R`.  This closes the defect.

No remaining hash, rooted-canonical, orbit-multiplicity, exact-rate,
start/target-witness, live-trim, reducible-SCC, physical-coloring, q42-row,
carry, raw-cost, ownership, or scope blocker was found.

## Frozen source binding

This approval binds only the following source bytes:

```text
6fa6b6b2fb2a113f837e37960a63edb17c759691af982fa24e3a6ab3c575eb72  AT_MOST_FIVE_STATE_SUNFLOWER_WALL.md
2f311d5aa389cca75ba75c1d21a6fc13d8612ba013a952704a8163103e00c6cb  exhaust_five_state_orbits.cpp
b59ac9c7da552ff520755a43ebd317c51b0d5ebdfd41ae835a90515e9d9b1139  verify_lower_state_live_sccs.py
302a244d71a4f5668239c388cc4ba6237ea44a54a3b9a4999ccdd1bd87038631  run.ps1
853d765139a5839ae4f90fe357abf13a1f96115ce6389f499195cd229d947c74  run.sh
```

The source `SHA256SUMS` file has SHA-256
`2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71`
and lists exactly these five payloads.

## Independent S5 canonical-completeness audit

The producer generates restricted-growth rooted codes and chooses the least
of five rooted canonical encodings.  The hostile C++ replay uses a different
deduplication rule: it materializes every one of the 120 simultaneous state
conjugates and hashes the least full labeled-table code.

The restricted-growth generator itself is complete.  If `A_n` is the number
of labeled partial binary tables accessible from a fixed root, classification
by the root's reachable set gives

```text
(n+1)^(2n)
  = sum_{k=1}^n C(n-1,k-1) A_k (n+1)^(2(n-k)).
```

This yields `A_5=15184800`.  An automorphism of an accessible deterministic
table fixing its root fixes every reachable state word by word, so the rooted
action is free and `A_5/4!=632700`, exactly the generated count.

The independent all-120-conjugate census obtains

```text
rooted accessible codes       632700
rooted strong codes           320253
unrooted strong S5 orbits      64057
labeled strong tables        7686072
```

It also computes each representative's full automorphism group.  Exactly
64,049 orbits have trivial automorphism group and eight have automorphism
group of order five.  The sum of vertex-orbit counts is `320253`, independently
recovering the number of rooted strong codes, while the orbit-stabilizer sum is
`7686072=24*320253`.  These multiplicity identities detect both missing and
duplicated unrooted representatives.

## Exact Perron comparisons

The hostile replay independently constructs every principal submatrix of
`sI-W` after clearing the rational denominator and evaluates its determinant
with recursive Laplace expansion.  The producer instead uses the signed
permutation formula.  Both use the possibly singular M-matrix criterion for a
Z-matrix:

```text
rho(W) <= s  iff  every principal minor of sI-W is nonnegative.
```

For the gate comparison an integer entry has magnitude at most `1123668`.
The bound `120*1123668^5` is below the signed 128-bit limit, so every operation
is exact.  No floating-point eigensolver or tolerance is involved.

The independent counts are

```text
strong S5 orbits             64057
rho > B                      54184
rho > G                      49047
```

## Exact symmetric product and every start/target witness

Seven ordered decoder copies on five states have 330 `S_7` occupancy
histograms.  Their orbit sizes sum to `5^7=78125` with exact distribution

```text
1:5 7:20 21:20 35:20 42:30 105:60 140:30
210:50 420:60 630:20 840:5 1260:10.
```

Adding the unit-column activity bit gives 660 possible quotient states.
Constant columns move all occupied copies together.  A unit column chooses an
occupied source class, sends one actual copy on red, and all remaining copies
on blue.  Every quotient transition lifts to ordered copies and every ordered
transition has this quotient.  Pure active target histograms are therefore
exact singleton-target multisunflowers, not a relaxation.

For every above-blue orbit, every five starts, and every five singleton
targets, the hostile replay retains BFS predecessors, reconstructs a shortest
ordered seven-word witness, checks every defined state transition, checks each
column weight is `0`, `1`, or `7`, checks a unit column occurs, and checks all
seven endpoints equal the requested target.  All
`54184*25=1354600` witnesses pass, comprising 38,001,782 ordered word symbols.
The largest reached quotient has 335 states.

The complete shortest-horizon histogram is

```text
1:26426 2:141451 3:344137 4:399252 5:264911
6:120113 7:38799 8:12029 9:4009 10:1510
11:682 12:376 13:277 14:181 15:139 16:98
17:60 18:35 19:32 20:27 21:23 22:14 23:10 24:6 25:3.
```

The published maximum case and its one exceptional plus six repeated words
are also replayed directly.  Repetition is valid because the obstruction is a
multiset of seven underlying words.

## Lower live SCCs and the reducible seam

The hostile standard-library replay independently enumerates all labeled
partial tables on one through four states.  It imports no producer code:

```text
states  tables   strong  rho>B  rho>G  start/target checks  max horizon
1            4        4      1      1             1             1
2           81       25     17     15            68             4
3         4096      828    644    566          5796             9
4       390625    60654  49662  44370        794592            16
```

All checks have witnesses and every lower-state horizon count matches.

For a high-rate reachable/coaccessible trim, choose a maximal-Perron SCC.
Reachability gives one common prefix into a chosen start `c`.  For any chosen
singleton target `q` in the SCC, coaccessibility gives one common suffix from
that same `q` to the original accepting set.  Restricting outgoing edges makes
the SCC matrix exact.  The start/singleton-target census supplies all seven
internal paths to that one `q`; no synchronization of different exits is
assumed.  Adding the prefix and suffix adds only constant columns and preserves
the unit column.  A planted reducible interface verifies this lift directly.

## Accepted-language rate and dead-sink scope

The planted two-state interface has fixed start/accept `a`, transitions

```text
a: blue -> a, red -> b
b: blue -> b, red -> b.
```

Only all-blue words are accepted, so `Z_m=B^m`.  State `b` is reachable but
noncoaccessible and

```text
W_ambient = [[B,R],[0,B+R]],  rho(W_ambient)=B+R>B,
W_trim    = [[B]],            lambda=rho(W_trim)=B.
```

Thus an ambient root would make the theorem false even on two states.  The
refrozen theorem consistently defines rate as accepted-language limsup,
equivalently the Perron root of the reachable/coaccessible live trim.
Periodicity is harmless because the definition uses limsup and fixed entry and
exit paths expose each maximal live SCC's Perron growth.

## Frozen q42 coloring and physical lift

The hostile Python replay reconstructs the q42 alphabet and both disjoint
packet layers from their coarse and residual geometry.  It obtains

```text
q42 boxes                         280917
first-layer packets                13230
second-layer packets                4410
all support-disjoint packets       17640
support vertices                   92610
packet sizes       5:13671, 6:3528, 7:441
```

Selecting an independently varying role in each packet produces 17,640
distinct red boxes; support disjointness makes every packet contain exactly
one red, and coloring every remaining box blue gives 263,277 blue boxes.  The
replay also verifies that all 441 size-seven packets lift the single cyclic
prototype used by the theorem.  This justifies `R=17640`, `B=263277`, and the
physical unit-column construction for the frozen coloring.  It would not
justify an arbitrary same-count coloring, which the repaired theorem now
explicitly excludes.

For every cyclic red-role alignment, the replay independently checks:

* balanced role-incidence cancellation;
* all seven displayed rows and their exact four-coordinate carry vectors;
* all 49 actual modular midpoint rows;
* exactly seven same-endpoint rows, all and only `x=y=z`;
* raw-canonical costs
  `(16/7,22/7,20/7,24/7,22/7,18/7,18/7)`;
* wrapped/geodesic diagnostic cost `11/7` for every alignment.

The varying positive raw-canonical costs are the operative claim; the constant
wrapped value is kept separate.  At every active column, cyclic transitivity
aligns the packet's unique red role with whichever abstract word carries the
unit `1`, while the other six roles remain blue.  Constant columns use one
common physical symbol.  The replay performs this physical lift for all seven
possible red roles, verifies the seven physical words are distinct, and checks
raw and wrapped totals.  Color homogeneity preserves all state paths, the
balanced rows cancel every potential value, and common entry/exit columns add
zero cost.

## Scope and nonclaims

Approved scope is exactly the at-most-five-live-state wall for
color-homogeneous partial deterministic interfaces.  The abstract census uses
only weights `B,R`; the physical consequence additionally requires the frozen
one-red-per-packed-packet coloring.  The package proves no wall for six or more
states, physical-symbol-dependent transitions, arbitrary measurable carving,
or arbitrary same-count coloring.  It does not infer existence of a physical
potential from packet avoidance.

## Replay and relocation contract

From this hostile-audit directory:

```powershell
.\run_hostile.ps1
```

or under WSL:

```sh
bash ./run_hostile.sh
```

Both wrappers accept an optional source-directory argument.  The source
basename is not part of the contract: content hashes, not a fixed sibling
directory name, bind the replay.  The default paths point to the audited
snapshot above.

The full refrozen source plus hostile replay passed in 138.033 seconds on
native Windows and 91 seconds under WSL, ending respectively with
`PASS_HOSTILE_FIVE_STATE_NATIVE` and `PASS_HOSTILE_FIVE_STATE_WSL`.

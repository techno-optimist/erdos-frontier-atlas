# Hostile audit: standalone at-most-five-state homogeneous wall

Date: 2026-08-19. Source audited read-only:

```text
D:\p42_scratch\erdos142_q42_partial_at_most_five_state_wall_20260819
```

## Verdict

**APPROVE.** No hash, orbit-completeness, rate, product-witness, live-trim,
lower-SCC, physical-row, carry, ownership, or scope blocker was found.

The first frozen draft was held at **BLOCK** because it gave only global
`B,R` counts and did not state the physical one-red-per-packet coloring needed
by the size-seven lift. The producer repaired and refroze the theorem. The
approved version now fixes exactly one red box in each of the 17,640
support-disjoint packed packets, makes every other box blue, distinguishes the
weight-only abstract census from the physical frozen-color consequence,
permits reuse of an actual size-seven packet with cyclic alignment of its one
red role, and explicitly excludes an arbitrary same-count coloring. The
repair closes the blocker without changing any code or replay count.

The producer's full runner passed both native Windows and WSL. This audit also
uses two new implementations in a separate directory. The five-state audit
does not use the producer's min-over-five-rooted-codes orbit test: it sends
every independently generated rooted strong code to the minimum of all 120
explicit simultaneous S5 conjugates. It then reconstructs and lifts a
shortest ordered seven-word witness for every one of the 1,354,600 checked
start/target pairs. The second replay independently covers SCC sizes one
through four, the accepted-language dead-sink scope control, and the complete
q42 row/carry ledger.

## Frozen source binding and producer replay

All five payload hashes match the frozen source manifest:

```text
6fa6b6b2fb2a113f837e37960a63edb17c759691af982fa24e3a6ab3c575eb72  AT_MOST_FIVE_STATE_SUNFLOWER_WALL.md
2f311d5aa389cca75ba75c1d21a6fc13d8612ba013a952704a8163103e00c6cb  exhaust_five_state_orbits.cpp
b59ac9c7da552ff520755a43ebd317c51b0d5ebdfd41ae835a90515e9d9b1139  verify_lower_state_live_sccs.py
302a244d71a4f5668239c388cc4ba6237ea44a54a3b9a4999ccdd1bd87038631  run.ps1
853d765139a5839ae4f90fe357abf13a1f96115ce6389f499195cd229d947c74  run.sh
```

The source `SHA256SUMS` hash is
`2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71`.
The source bytes remained unchanged after all native and WSL runs.

In the post-repair hostile replay, the full producer runners were launched
concurrently: native completed in about 33.2 seconds and WSL completed within
the same 33.2-second collection window. The producer's separate serial
measurements were 36.3 seconds native and 28.2 seconds WSL. Both hostile runs
ended with `PASS_AT_MOST_FIVE_STATE_SUNFLOWER_WALL` and all subordinate
markers.

## Independent S5 completeness audit

Let `A_n` be the number of labeled partial binary tables on `n` states that
are accessible from a fixed root. Partitioning all tables by the root's
reachable subset gives the independent recurrence

```text
(n+1)^(2n)
 = sum_{k=1}^n C(n-1,k-1) A_k (n+1)^(2(n-k)).
```

It yields `A_5=15184800`. An automorphism of an accessible deterministic table
that fixes the root fixes every state word-by-word, so the rooted action is
free. Hence `A_5/4!=632700`, independently confirming the generated rooted
accessible count.

The audit generates all restricted-growth rooted codes, filters strong ones,
and canonicalizes each strong code by materializing all 120 conjugates

```text
delta'(sigma(s),b)=sigma(delta(s,b)).
```

This reproduces

```text
rooted accessible codes     632700
rooted strong codes         320253
unrooted S5 orbits           64057
labeled strong tables      7686072
```

As a per-orbit check, the audit independently computes every automorphism
group and every vertex-orbit partition. Exactly 64,049 table orbits have
trivial automorphism group and five distinct rooted codes. Exactly eight have
automorphism group of order five and one rooted code. For every orbit, the
number of generated rooted codes equals the number of vertex orbits. The
orbit-stabilizer sum is `7686072=24*320253`. These identities rule out both a
missing S5 orbit and accidental duplicate representatives.

## Independent exact rates and all product witnesses

The blue comparison is independently normalized to the smaller integer
Z-matrix

```text
597 I - 597 A_blue - 40 A_red,
```

using `B=441*597` and `R=441*40`. The gate comparison uses
`1058841 I-4W`. All 31 principal minors are evaluated by a recursive exact
integer determinant, rather than the producer's signed-permutation routine.
The M-matrix criterion independently reproduces

```text
strong S5 orbits with rho>B   54184
strong S5 orbits with rho>G   49047
```

The product replay uses the 330 occupancy histograms of seven copies on five
states and an activity bit. Constant columns and unit columns are recomputed
from the transition table. Breadth-first predecessor data are retained. For
every above-blue representative, every five starts, and every five singleton
targets, the audit reconstructs the shortest quotient path, assigns the
unique red move to an actual ordered copy at every unit column, replays all
seven state paths, checks every column has weight 0, 1, or 7, checks a unit
column occurs, and checks all endpoints equal the requested target.

All `54184*25=1354600` witnesses replay. Their combined ordered-word length is
38,001,782 symbols. The largest quotient graph has 335 reached states. The
independent shortest-horizon distribution is

```text
1:26426 2:141451 3:344137 4:399252 5:264911
6:120113 7:38799 8:12029 9:4009 10:1510
11:682 12:376 13:277 14:181 15:139 16:98
17:60 18:35 19:32 20:27 21:23 22:14 23:10 24:6 25:3.
```

The published horizon-25 table and its one exceptional plus six repeated
words are also replayed directly to singleton target zero. Repetition is
permitted by the stated multiset definition.

## Lower SCCs, live rate, and reducible reduction

The independent standard-library replay exhausts every labeled strong table
on one through four states and all start/singleton-target pairs:

```text
states  tables   strong  rho>B  rho>G  checked pairs  max horizon
1            4        4      1      1             1       1
2           81       25     17     15            68       4
3         4096      828    644    566          5796       9
4       390625    60654  49662  44370        794592      16
```

Every pair has a witness and all lower-state horizon counts match the source.
The reducible proof is sound: a Perron SCC of a reachable/coaccessible trim
has a fixed common entry prefix and, from a chosen singleton target, a fixed
common accepting suffix. Restricting edges leaving the SCC preserves its
matrix. Adding the common prefix and suffix adds only constant columns, so it
preserves the unit column and nondegeneracy. No synchronization between
different exit states is assumed.

The planted two-state scope control has fixed start/accept zero,
`0--blue-->0`, `0--red-->1`, and both colors looping at state one. State one is
reachable but noncoaccessible. Exact replay gives

```text
W_ambient = [[263277,17640],[0,280917]],  rho(W_ambient)=280917,
W_trim    = [[263277]],                   lambda=263277,
Z_m       = 263277^m.
```

The accepted language is blue-only and sunflower-free. Thus the theorem's
rate must, and does, mean accepted-language limsup, equivalently the Perron
root of the reachable/coaccessible trim. An ambient dead-sink root is not a
rate counterexample.

## Full physical q42 audit

For each of all seven cyclic red-role alignments, the audit independently
recomputes:

- role-incidence cancellation;
- the seven displayed midpoint rows and their exact four-coordinate carries;
- all 49 actual ordered modular midpoint rows;
- exactly seven `x=z` rows, all and only `x=y=z`;
- raw-canonical costs
  `(16/7,22/7,20/7,24/7,22/7,18/7,18/7)`;
- wrapped-torus cost `(11/7)*7`, kept explicitly separate from the operative
  raw-canonical claim.

All carry ledgers match exactly. Cyclic transitivity covers every arbitrary
red role. A constant abstract column uses a common physical symbol; a unit
column uses all seven packet roles. Fixed-start determinism and disjoint
half-open boxes give unique ownership. The positive raw sum at a unit column,
together with role-incidence cancellation, gives the stated whole-word Farkas
obstruction. Common entry/exit blocks have zero cost.

## Scope and integration cautions

Approved scope is exactly the source theorem: color-homogeneous partial
deterministic interfaces with at most five ambient states, under the frozen
one-red-per-each-of-17,640-disjoint-packets coloring, with accepted-language
rate measured on the reachable/coaccessible trim. The orbit counts are counts
of strong table orbits; the 1,354,600 figure is a representative start/target
coverage census, not a count of interface isomorphism classes.

Do not extend this result to six states, physical-symbol-dependent
transitions, measurable box carving, or potential feasibility from packet
avoidance. Do not replace the varying raw-canonical costs with the additional
wrapped `11/7` observation. Replays must not define `NDEBUG`, because both C++
certificates intentionally use assertions for frozen expected values; the
provided compile commands do not define it.

## Replay

From this audit directory:

```powershell
.\run.ps1
```

or in Linux/WSL:

```sh
bash ./run.sh
```

Launched concurrently after the final source rebind, the independent native
runner completed in about 33.0 seconds and WSL completed within the same
33.0-second collection window.

Success markers:

```text
PASS_INDEPENDENT_FIVE_STATE_S5_ORBIT_AND_PRODUCT_AUDIT
PASS_INDEPENDENT_LOWER_SCOPE_AND_FULL_Q42_PHYSICAL_AUDIT
APPROVE_Q42_AT_MOST_FIVE_STATE_SUNFLOWER_WALL
```

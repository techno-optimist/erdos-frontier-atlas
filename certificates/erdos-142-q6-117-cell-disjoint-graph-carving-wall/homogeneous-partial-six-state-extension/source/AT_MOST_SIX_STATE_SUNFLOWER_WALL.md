# At-most-six-state homogeneous partial-decoder sunflower wall

Date: 2026-08-19. This scratch-only exact theorem package changes no Atlas or
pull-request file and does not alter the frozen at-most-five-state package or
its hostile audit.

## Physical coloring, rate, and theorem

Fix the support-disjoint q42 packet packing. Choose exactly one red box in
each of its 17,640 packets and color every other q42 box blue. Thus

```text
R = 17640,  B = 263277,  N = 280917,
G = 1058841/4,  G-B = 5733/4.
```

The abstract automaton census below depends only on `B,R`. Its physical
consequence uses the stated one-red-per-packed-packet coloring, not an
arbitrary coloring with the same global counts.

A color-homogeneous partial deterministic binary interface has at most six
states, one fixed start, a nonempty accepting set, and at most one successor
on each of blue and red. Every physical box of one color uses the same color
transition. Define the accepted-language rate by

```text
lambda(D) = limsup_m Z_m^(1/m),
```

where `Z_m` is the number of accepted physical-box words of length `m`.
Delete unreachable and noncoaccessible states and make transitions entering a
deleted state undefined. This preserves every `Z_m`. If `W_trim` is the
weighted matrix of the resulting live trim, then

```text
lambda(D) = rho(W_trim),
W_st = B*1[delta(s,blue)=t] + R*1[delta(s,red)=t].
```

The Perron root of an ambient dead or unreachable component is never the
accepted-language rate.

**Theorem.** If an at-most-six-state color-homogeneous partial deterministic
interface contains no nondegenerate seven-multisunflower, then

```text
lambda(D) <= B = 263277 < G.
```

A nondegenerate seven-multisunflower is a multiset of seven accepted binary
words of one common length such that every coordinate column has Hamming
weight 0, 1, or 7 and at least one column has weight 1. Repeated words are
allowed. The bound is sharp at the blue-only recurrent state.

## Live-SCC reduction

Suppose a safe live trim has `rho(W_trim)>B`. Choose a Perron SCC `C`. Choose
one state `c in C` and a fixed original prefix entering it. Choose one state
`q in C` and a fixed suffix from `q` to the original accepting set. Restrict
edges leaving `C` to be undefined, start at `c`, and accept only `q`. This is a
strong partial interface with matrix exactly `W_C` and the same Perron rate.

If `|C|<=5`, the refrozen at-most-five-state theorem bound below supplies the
contradiction. If `|C|=6`, the exact census in this package supplies a
sunflower from every start to every singleton target for every above-blue
strong table. Prepending and appending the fixed common words adds only
constant columns; the existing unit column and nondegeneracy remain. Thus the
original language contains a sunflower.

The lower-state dependency is an explicitly supplied directory containing
the refrozen at-most-five-state package. Its location carries no trust: this
replay binds it byte-for-byte using theorem hash
`6fa6b6b2fb2a113f837e37960a63edb17c759691af982fa24e3a6ab3c575eb72`
and manifest hash
`2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71`.
The dependency has an independent hostile approval; this package does not
silently broaden its scope.

## Avoiding the full `7^12` table space

A labeled partial six-state table has `7^12=13841287201` possibilities. The
primary replay instead generates accessible rooted tables in canonical
restricted-growth order. Starting at root zero, scan blue then red entries in
breadth-first state order; an entry is undefined, an already introduced
label, or the unique next label. Every generated code is accessible, every
rooted accessible isomorphism class occurs once, and the independent formula

```text
(n+1)^(2n)
 = sum_{k=1}^n C(n-1,k-1) A_k (n+1)^(2(n-k))
```

gives `A_6=2860384800` labeled tables accessible from a fixed root. A rooted
accessible deterministic table has no nontrivial automorphism fixing its
root, so division by `5!` gives exactly

```text
rooted accessible canonical codes    23836540.
```

Exactly 12,346,720 of these codes are strongly connected. For a strong table,
compute its rooted canonical code from each of the six possible roots and
keep the least. This leaves one representative of every simultaneous-S6
orbit:

```text
strong S6 table orbits                 2058472.
```

An independent Burnside replay verifies this count without the least-root
test. Its exact fixed-strong counts by the only nonzero cycle types are

```text
identity: 1481606400,   2^3: 29968,   3^2: 1014,   6: 28.
```

All other nonidentity cycle types fix zero strong tables. Weighting by S6
conjugacy-class sizes gives Burnside sum `1482099840`, and division by 720
again gives 2,058,472.

## Exact product-first CEGAR

Seven copies on six states have

```text
C(12,5) = 792
```

occupancy histograms, or 1,584 states after adding one activity bit. Constant
blue/red columns move every copy on that transition. A unit column selects
the current state of its unique red copy, moves one copy on red, and all other
copies on blue. This is the exact quotient of the ordered `6^7` product by
permuting copy labels. An active pure histogram at `q` is exactly a
nondegenerate multisunflower accepted by singleton target `q`.

The replay checks all six starts and six singleton targets for every strong
orbit. It uses the following exact product-first logic:

- If all 36 product goals are reached, that table is already screened at
  every rate; no Perron calculation is needed.
- Only an orbit with a missing product goal could escape. Every such orbit is
  therefore sent to the exact rational Perron comparison.

The complete boundary is

```text
strong S6 orbits                         2058472
all 36 product goals reached             2056831
orbits with at least one missing goal        1641
witnessed start/target pairs            74045916
missing start/target pairs                 59076
product-incomplete orbits with rho<B         1640
product-incomplete orbits with rho=B            1
product-incomplete orbits with rho>B            0
```

The unique equality orbit is the blue-only directed six-cycle. Consequently
every strong six-state table with `rho>B` has a sunflower for every singleton
target. The largest quotient search reaches 798 of 1,584 states. Every reached
singleton witness has shortest horizon at most 50.

The exact shortest-horizon distribution over all 74,045,916 witnessed pairs
is

```text
1:1039342 2:5549208 3:14760193 4:20572215 5:16572268
6:9322764 7:3925069 8:1420590 9:492627 10:189898
11:82032 12:41471 13:24250 14:16173 15:11379 16:7507
17:4770 18:3233 19:2182 20:1678 21:1239 22:1017
23:841 24:709 25:581 26:433 27:318 28:306 29:304
30:282 31:234 32:163 33:133 34:99 35:75 36:63
37:50 38:43 39:33 40:22 41:17 42:14 43:13 44:12
45:12 46:16 47:16 48:10 49:8 50:4.
```

The primary replay emits a temporary certificate containing exactly the 1,641
boundary orbit codes, their 36-bit missing-pair masks, and exact rate signs.
A separate Python implementation rebuilds every product graph and all 63
principal-minor comparisons. It independently recovers 59,076 missing pairs,
the split `(below,equal,above)=(1640,1,0)`, table-code sum 1,041,120,840,919,
and 64-bit boundary checksum 9,776,710,376,808,584,319.

## Exact rate arithmetic and controls

Since `B=441*597` and `R=441*40`, comparison with `B` uses the integer
Z-matrix

```text
597 I - 597 A_blue - 40 A_red.
```

The possibly singular M-matrix criterion says `rho(W)<=B` exactly when all 63
nonempty principal minors are nonnegative. The primary uses recursive signed
128-bit determinants; the boundary replay independently uses permutation
determinants with arbitrary-precision Python integers. No floating point,
tolerance, SAT solver, or heuristic enters the theorem.

Two planted controls exercise both CEGAR branches. The blue-only six-cycle has
all 36 goals missing and exact rate `B`. Adding one red self-loop makes its
rate strictly above `B`, and all 36 product goals are reached. A genuinely
product-incomplete above-blue control cannot be planted because it would be a
counterexample; the replay exits immediately if one is found.

## Unique ownership and physical q42 lift

Fixed-start determinism gives each color word one state path. Disjoint
half-open q42 boxes give each physical word unique ownership, so
`Z_m=e_start^T W^m 1_accept` has no label multiplicity.

At a constant abstract column use one common physical symbol. At a unit
column reuse all seven roles of the explicit actual size-seven packet replayed
by `verify_six_scope_physical.py`. The frozen
one-red-per-packet coloring makes exactly one role red; cyclically align that
role with the unique red word. A common strict-interior offset gives exact
uniquely owned physical midpoint rows.

The independent physical replay checks all seven cyclic alignments, all 49
actual ordered modular rows per alignment, every carry vector, and that the
seven `x=z` rows are only `x=y=z`. For this packet, the operative
raw-canonical cost sums are

```text
16/7, 22/7, 20/7, 24/7, 22/7, 18/7, 18/7.
```

The separately checked wrapped-torus cost is `11/7` in every alignment; it
does not replace the raw claim. Role-incidence cancellation removes every
potential value when the seven whole-word inequalities are summed, while a
unit column contributes positive raw cost. Common SCC entry/exit blocks have
zero cost. Thus every above-gate interface covered by the theorem contains an
exact physical Farkas obstruction for every selected red role.

## Scope and nonclaims

Proved: the frozen one-red-per-each-of-17,640-packets q42 coloring;
color-homogeneous partial deterministic interfaces with at most six states;
accepted-language/live-trim rate; exact S6 orbit exhaustion; exact
product-first boundary; exact rate arithmetic; common-prefix/suffix SCC
reduction; unique ownership; and the physical lift.

Not proved: seven or more states; an arbitrary same-count coloring without one
red role in each packet; physical-symbol-dependent transitions; measurable
carving within boxes; or existence of a physical potential from packet
avoidance. Packet avoidance remains only a necessary escape from this
obstruction family.

## Replay

Windows:

```powershell
.\run.ps1 -FiveStateDir <five-state-directory>
```

Linux or WSL:

```sh
bash ./run.sh <five-state-directory>
```

Either runner also accepts `Q42_FIVE_STATE_DIR`. If neither an argument nor
that environment variable is supplied, the runner tries the conventionally
named sibling scratch directory and emits a warning/notice. That fallback is
only a convenience: the pinned hashes above, never the path, establish the
dependency identity.

Success markers:

```text
PASS_EXACT_SIX_STATE_S6_ORBIT_CEGAR_WALL
PASS_INDEPENDENT_SIX_STATE_BURNSIDE_ORBIT_COUNT
PASS_INDEPENDENT_SIX_STATE_INCOMPLETE_BOUNDARY_REPLAY
PASS_SIX_STATE_SCOPE_DEPENDENCY_AND_Q42_PHYSICAL_REPLAY
PASS_AT_MOST_SIX_STATE_SUNFLOWER_WALL
```

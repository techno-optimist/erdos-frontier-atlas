# Independent hostile audit: at-most-six-state homogeneous wall

Date: 2026-08-19. Verdict: **APPROVE**, restricted to the exact seven-file
source payload and the exact lower-state dependency bound below. This audit is
scratch-only and made no source-package or pull-request edit.

## Frozen contracts

Source directory supplied at replay time:

```text
erdos142_q42_partial_six_state_frontier_20260819
```

The approved source manifest has SHA-256
`a62da6552877464d13c45f615f1d61e9b05cee7c52e81b472db3f6a77dc97d01`
and contains exactly:

```text
4e0059d11babefbfe6a19853b2d0b1b1d464879727d99ea49d5c5e26e3fa1bbc  AT_MOST_SIX_STATE_SUNFLOWER_WALL.md
6f59fb09b6568f2bcb1a98d6045db1e42fbb99179263c913e97e92f77d17ce88  exhaust_six_state_orbits_cegar.cpp
50e81a587d7b67a4137031f740ffbc8d74217218d0a0569f2aacb1fc19c5b442  verify_six_state_burnside.cpp
7a362535f2afb528e9646540281eade02e4f03201c31daf422cad61359bee3bf  verify_six_boundary.py
607060c1d94551778db723f420db55c74d296d7b60eff5a7f60e75ab5dd241a6  verify_six_scope_physical.py
cb28712f45c531afa60233a98bb728a53782db06d877045ca309dd3a09f61a7b  run.ps1
fe83fa43245bd9ed9a90cc1257c255108c56adad95660b59864fef732a616cff  run.sh
```

The lower-state theorem and manifest are respectively
`6fa6b6b2fb2a113f837e37960a63edb17c759691af982fa24e3a6ab3c575eb72`
and `2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71`.
Both source runners accept an explicitly supplied relocated dependency and
authenticate it by content. No approved theorem or runner contains a
machine-local `D:\p42_scratch` or `/mnt/d/p42_scratch` contract.

Unmanifested diagnostic sources and prebuilt executables present in the
scratch directory are outside this approval and must not be promoted as part
of the seven-file payload.

## Enumeration and orbit completeness

The restricted-growth generator is exhaustive for rooted accessible partial
binary tables: scanning the two labeled transitions of each discovered state,
the only legal values are undefined, a previously discovered state, or the
unique next state. Conversely, canonical breadth-first discovery maps every
rooted accessible table to exactly one such code. Accessibility kills every
automorphism fixing the root. The independent labeled recurrence and division
by `5!` therefore give 23,836,540 rooted accessible codes.

Both replays find 12,346,720 rooted strong codes and 2,058,472 simultaneous
`S6` orbits. The hostile implementation uses base-seven integer rooted codes,
not the producer's table-array comparison. Its additional rooted-class
histogram is

```text
1:17  2:76  3:1241  6:2057138,
```

whose weighted sum is 12,346,720. Multiplication by `5!` gives the independent
labeled-strong checksum 1,481,606,400. The producer's separate Burnside code
also gives fixed-strong counts 1,481,606,400 for identity, 29,968 for `2^3`,
1,014 for `3^2`, 28 for `6`, and zero for every other cycle type. With the
correct conjugacy-class sizes its sum is 1,482,099,840, hence 2,058,472 orbits.

## Exact seven-copy product and rate boundary

Weak compositions of seven into six bins give 792 occupancy histograms. The
hostile replay independently checks their `S7` orbit-size histogram

```text
1:6 7:30 21:30 35:30 42:60 105:120 140:60
210:120 420:180 630:60 840:30 1260:60 2520:6,
```

whose weighted sum is `6^7=279936`. Adding an activity bit gives exactly
1,584 quotient states. Constant blue and red columns move every copy on the
corresponding transition. A unit column selects a currently occupied state,
moves exactly one copy on red and the other six on blue, and sets activity.
Thus an active pure target is equivalent to seven accepted equal-length words
with column weights only 0, 1, or 7 and at least one unit column. Occupancy
quotienting loses no reachability information even when word patterns repeat.

All six starts and all six singleton targets are checked for every orbit. The
final exact partition is:

```text
strong orbits                    2058472
all 36 targets witnessed         2056831
product-incomplete orbits           1641
witnessed ordered pairs         74045916
missing ordered pairs              59076
incomplete rho<B / rho=B / rho>B 1640 / 1 / 0
boundary code sum           1041120840919
boundary FNV checksum    9776710376808584319
maximum reached states                798
maximum shortest horizon                50
```

The hostile C++ reconstructs the entire horizon histogram and an explicit
length-50 witness, then checks all seven paths and every column weight. Its
table/start/target are

```text
(-1,1,-1,2,3,4,0,-1,1,5,4,-1), 3, 0.
```

The producer's `uint16_t` distance is safe independently of the observed
horizon: a simple path in a 1,584-state quotient has length at most 1,583.
Queue and transition indices fit signed 16 bits.

No numerical or rate-first filter is present. Every incomplete orbit reaches
the exact comparison. Dividing `B I-W` by 441 gives the integer Z-matrix

```text
597 I - 597 A_blue - 40 A_red.
```

For a nonnegative matrix, this is a possibly singular M-matrix exactly when
all 63 nonempty principal minors are nonnegative, equivalently `rho(W)<=B`.
Strong tables are irreducible, so the full determinant distinguishes equality
from strict inequality once all minors are nonnegative. The hostile C++ uses
a subset-DP determinant rather than recursive Laplace expansion and recovers
the exact split `1640/1/0`; the unique equality table is the blue-only directed
six-cycle. A conservative determinant bound `6! 637^6` is far below signed
128-bit capacity. Planted equality and strict-above controls exercise both
sign branches.

## Accepted rate, SCC reduction, and lower states

Deleting unreachable and noncoaccessible states, and making transitions into
deleted states undefined, preserves every accepted word. Standard finite
nonnegative-matrix path decomposition then gives the accepted-language limsup
as the maximum Perron root of the live SCCs, hence `rho(W_trim)`. A planted
reachable but noncoaccessible sink has ambient rate `B+R>G` while its accepted
mass is exactly `B^m` and its live trim has rate `B`; both producer and hostile
controls reject use of the ambient radius.

For a maximal live Perron SCC, trim supplies a fixed common prefix into a
chosen start and a fixed common suffix from a chosen singleton target to the
original accepting set. Deleting SCC exits leaves exactly the principal SCC
matrix and a strong partial table. The all-start/all-singleton census handles
six states; the hash-bound at-most-five-state theorem handles smaller SCCs.
Only one fixed suffix from the selected target is required, so there is no
multi-exit synchronization seam. Prepending and appending common words adds
only constant columns and preserves the existing unit column. A planted
prefix/two-state-SCC/singleton-exit/suffix construction passes this lift
literally.

## Frozen q42 coloring and physical lift

The hostile stdlib replay rebuilds the packet packing from its coarse and
fine definitions rather than trusting the producer's three-entry histogram:

```text
first layer 13230, second layer 4410, total packets 17640
packet sizes 5:13671, 6:3528, 7:441
support vertices 92610, with no repeated support vertex
alphabet 280917, one independent red choice per packet, blue 263277
```

It identifies the producer's seven-role tuple as an actual packet. For that
packet it checks every cyclic red alignment, all 49 ordered modular midpoint
rows, the seven and only seven diagonal rows `x=y=z`, all carry ledgers, raw
canonical costs

```text
16/7, 22/7, 20/7, 24/7, 22/7, 18/7, 18/7,
```

and wrapped cost `11/7` in every alignment. It additionally checks all 441
actual size-seven packets and all 3,087 alignments. Wrapped cost remains
`11/7`; every raw cost is positive. The complete raw-cost histogram is

```text
2:147, 16/7:392, 18/7:490, 20/7:833,
22/7:735, 24/7:490.
```

This stronger check exposed and caused repair of an earlier wording that could
have made the displayed tuple universal. The approved theorem now explicitly
uses the actual packet in `verify_six_scope_physical.py` and labels the tuple
"for this packet."

The length-50 binary witness is physically lifted for each of the seven
possible selected red roles. Constant columns use one common correctly
colored symbol; each unit column cyclically aligns the packet's sole red role
with its unique red word. All seven resulting physical words are distinct,
all whole-word midpoint rows hold, incidence cancels every potential term,
and at least one strictly positive raw contribution remains. This uses the
frozen one-red-per-each-packet coloring, not merely the global counts.

## Scope

Approved: color-homogeneous partial deterministic interfaces with at most six
states; fixed start and arbitrary nonempty accepting set; accepted-language
live-trim rate; the exact all-start/all-singleton product boundary; the pinned
at-most-five-state dependency; and the frozen q42 one-red-per-packet physical
lift.

Not approved or claimed: seven or more states, an arbitrary coloring with only
the same red/blue census, physical-symbol-sensitive transitions, measurable
carving within boxes, or construction of a physical potential from packet
avoidance. Packet avoidance is only a necessary escape from this obstruction.

## Replay

The hostile wrappers accept relocated directories; path location carries no
trust because both packages are hash-bound.

Windows:

```powershell
.\run_hostile.ps1 <six-state-source-directory> <five-state-directory>
```

Linux or WSL:

```sh
bash ./run_hostile.sh <six-state-source-directory> <five-state-directory>
```

Terminal markers are

```text
PASS_INDEPENDENT_SIX_STATE_PRODUCT_FIRST_WALL
PASS_INDEPENDENT_SIX_SCOPE_AND_PHYSICAL_HOSTILE_REPLAY
PASS_HOSTILE_SIX_STATE_NATIVE_AUDIT
PASS_HOSTILE_SIX_STATE_WSL_AUDIT
```

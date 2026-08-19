# Hostile audit: q=24 order-four one-block microbox wall

## Verdict

**APPROVE, with the stated one-block scope.**  The settled packet proves an
exact density wall for unions of complete globally aligned q=24 microboxes in
the fixed 117-cell q=6 alphabet.  It does not prove an arbitrary word-language
or graph-directed capacity bound, and it does not solve Erdos Problem 142.

Audited source:

- `D:\p42_research\erdos142_r4_microbox_frontier_20260818`
- `README.md` SHA-256
  `885b3d5f587bed393429739ae54f302a7b42b00b72fe41c12145b8404a717317`
- `verify_r4_order4_packing.py` SHA-256
  `639429a065fa20b3eb2f743a73ae80f5dce9be9723f30aa5bc4817ed3ac271d8`
- `frozen_semantic_certificate.json` SHA-256
  `dee2342e5670f735fe2e495c78dc7b20d3414191fc1e35cd64d34f595f7e7e69`
- `emit_r4_semantic.py` SHA-256
  `01ec03134570c87f9928923b1e2acc1f261e304cf43a7b1b2b79695017eb3d26`

Independent no-import replay:

- `D:\p42_scratch\erdos142_r4_hostile_audit_20260818\independent_r4_replay.py`
- SHA-256
  `15277b6fd4f899d856636809900bde45781054f0511e21970980c1d8837af19d`

Both the settled source verifier and the independent replay pass under native
Windows Python and WSL Python 3.  The emitter reproduces the frozen payload
bytes modulo its terminal newline, and the verifier checks certificate
nonmutation.

## Independent reconstruction

The replay imports no producer, discovery module, optimizer, or third-party
package.  It reconstructs:

- 117 distinct coarse cells;
- `117 * 4^4 = 29,952` distinct physical q=24 digit vectors;
- 1,359 edges in the claimed coarse-active strict-dilation subgraph;
- 843 nontrivial graph components, each of size at most nine;
- the lexicographically first exhaustive componentwise maximum matching of
  960 edges, with 1,920 distinct endpoints;
- 833 complete surviving orbits of the fixed fine-digit shift
  `(0,0,6,12)` after deleting those endpoints.

During the hostile audit, the independently reconstructed dilation and packet
ledgers were compared entry-for-entry with the frozen certificate and agreed.
The replay itself is deliberately standalone and reads neither that payload
nor the primary verifier.  Its own canonical serializations have digests

```text
matching cf84557bf6661f60a46fa9a127771017091683320843a0806a1949b2fccd3898
packets  f0b3bb50459d7dcc2886f872011645db98d3bda869c34dc93435568bb8feaffe
```

The different published semantic digests merely use the source packet's
record encoding.  Those settled digests also replay exactly:

```text
dilation semantic  b76a136b58f6adcbebb9f0d34447bda10b99070c5339b6df5afd87989d9ab803
packet supports    f7e337056bde4b79568b97ff156e9bd6f03abc513da7d3fffedaae494d813db1
expanded packets   061eba59ea9fd5e529b9c161b8d90d2c538df38067c5d485f3ae90dbf4736037
payload semantic   8e54dab21a04d4a9f78631eb2c74e800597a78942080a417a3a4b7c493e25e65
```

## Physical packet semantics

Every selected packet is an exact order-four orbit.  For each of its four
centres `y`, the endpoints are `x=y-sigma` and `z=y+sigma` modulo 24.  The
independent replay checks all 3,332 rows and finds:

- the fine-digit defect `d_x+d_z-2d_y` is a coordinatewise multiple of 24;
- using one common `u in (0,1)^4`, the canonical points
  `(d+u)/24` lie in the strict interiors of their four physical boxes and
  satisfy the actual torus midpoint equation with the recomputed carry;
- every raw-canonical endpoint-square numerator is exactly 144, hence every
  row has positive physical right side `144/24^2=1/4`;
- in each four-row packet, every physical potential value occurs twice as an
  endpoint and once with centre coefficient `-2`, so all coefficients cancel;
- the four positive right sides sum to one, giving the contradiction `0>=1`
  for an arbitrary single-valued physical potential if all four boxes survive.

The 833 packet supports are mutually disjoint and avoid all 1,920 matching
endpoints.  No boundedness or regularity is needed for a finite packet; the
dilation supports use boundedness.

## Dilation semantics

For every matching edge, the source uses residual subdigit zero in each
coarse-active coordinate and the target uses subdigit three in the predecessor
coarse cell.  Inactive coordinates use one common strict-interior point.  At
least one active coordinate is a genuine canonical `0 -> 5` wrap.

The replay constructs the two four-dimensional strict-interior rows and checks
their exact modular carries, microbox membership, raw-canonical correction
identities, and positive recurrence

```text
D(3t)-D(t) >= K(72-48t),  K>=1.
```

With `t=(1/8)/3^j`, a finite telescope grows linearly and exceeds the finite
oscillation of any bounded correction.  No limiting value, continuity,
affinity, or boundary trace is used.

## Disjoint packing and exact gate

The 960 two-box supports and 833 four-box supports are pairwise disjoint, so a
feasible retained union must delete at least

```text
960 + 833 = 1,793
```

microboxes.  The exact four-coordinate EHPS gate is

```text
(49/576) * 24^4 = 28,224.
```

A strictly above-gate integer support would retain at least 28,225 boxes and
therefore delete at most 1,727.  The obstruction packing instead leaves at
most `29,952-1,793=28,159`, which is 65 boxes below the 1,728-deletion equality
threshold.

## Dependency and scope audit

The accepted reconstruction is solver-free.  The early discovery script's
CP-SAT calls are irrelevant: the 833 accepted packets are simply complete
orbits of one fixed order-four translation, and they are disjoint by direct
enumeration.  The matching is exhaustively checked inside components of size
at most nine.

The settled verifier also freezes a necessary warning against overclaiming.
In `Z_4^2` it exhibits a 10-word set containing none of the 16 direct affine
order-four lines, larger than the naive `3^2=9` product quotient.  Thus this
one-block deletion packing cannot currently be exponentiated coordinatewise.

Precisely outside scope are:

- arbitrary horizon-dependent or graph-directed word languages;
- context-owned or coupled multi-block decoders;
- proper carving inside a q=24 box, finer subdivisions, deformed,
  non-axis-aligned, or overlapping tiles;
- almost-everywhere-only coercivity or unbounded corrections;
- integer transfer, a new bound for `r_3(N)`, or a solution of Problem 142.

The audit initially caught an order-sensitive payload hash and an unnecessarily
huge exact-power computation in the telescope self-test.  Both are repaired in
the settled hashes above; the final four replays complete in a few seconds.

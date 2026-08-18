# q6 M7 selector: exact unit-girth-six physical wall

Atlas certificate packet, dated 2026-08-18.  It closes the exact 28-cell
selector from the adjacent `erdos-142-q6-m7-orbit-free-selector` research
fence under the supplied raw-canonical modular-torus coercivity convention.

The selector remains mathematically useful: it has mass strictly above the
supplied `(7/24)^6` gate and no nontrivial order-three translation orbit.  The
new result is that its first unit-balanced physical obstruction has six rows,
and those six rows already rule out an arbitrary global potential.

## Exact six-row wall

`witness.json` freezes six pairwise-distinct physical q6 vertices.  Each is a
six-block word of points in `{0,...,5}^2`; their reconstructed coarse cells are

```text
v0 (49,0), v1 (21,0), v2 (45,0),
v3 (35,0), v4  (7,0), v5 (45,0).
```

The repeated coarse cell is harmless: `v2` and `v5` are different physical
12-coordinate vertices.  All six cells belong to the exact 28-cell selector.

The rows `(endpoint_a,endpoint_b;center)` are

```text
(1,2;0), (0,3;1), (4,5;2),
(4,5;3), (0,3;4), (1,2;5).
```

Every one of their 36 two-dimensional block relations satisfies

```text
x + z - 2y = 6 kappa
```

with the carry `kappa` recorded in the packet.  Every physical vertex occurs
twice as an endpoint and once as a centre.  Hence, for a completely arbitrary
single function `H` on the physical union, the sum of the six required rows
cancels every value of `H` exactly.  The raw canonical squared endpoint costs
are

```text
68, 56, 32, 32, 56, 68,
```

so their sum leaves the contradiction

```text
0 >= 312              (raw q6 scale),
0 >= 312/6^2 = 26/3   (normalized scale).
```

This is physical-vertex cancellation, not a cell, parity, occurrence-label,
additive, pair-coordinate, or separable-potential ansatz.

## Strict half-open torus lift

For any common offset `delta in (0,1/6)^12`, add `delta` to all six canonical
vertices after dividing their digits by six.  Every point is then in the
strict interior of its selected half-open q6 box.  The common offset cancels
from every midpoint equation and every endpoint difference, preserving all
carries and the normalized contradiction `0 >= 26/3`.

Thus the wall is not a grid-boundary artifact.  It is still branch-sensitive
and not an ordinary Euclidean-midpoint theorem: every row has a nonzero
modular carry somewhere.

## Why six is exact in the unit-balanced class

The primary verifier also exhausts every labelled unit packet with two through
five rows in which row `i` is centred at label `i` and each label occurs twice
among all endpoints.  Loops, parallel endpoint edges and disconnected
endpoint multigraphs are included literally.  For each scalar template over
`Z/6`, it checks every kernel assignment.

The exact census is

| rows | endpoint templates | templates with a positive scalar mode |
| ---: | ---: | ---: |
| 2 | 3 | 0 |
| 3 | 21 | 1 |
| 4 | 282 | 40 |
| 5 | 6,210 | 1,470 |

For every one of the 1,511 positive templates, a single fixed triple of labels
is constant or an order-three coset in every scalar kernel solution and is
nonconstant in every positive solution.  Applying the same fixed triple
coordinatewise shows that every positive vector packet with at most five rows
contains a nontrivial physical order-three orbit.

The selector replays independently certify that it has no such orbit.
Consequently it contains no positive unit-balanced packet with at most five
rows, while `witness.json` supplies one with six.  In this exact finite class,
the unit Farkas girth is therefore **six**.

The canonical digests for all 6,516 templates and the 1,511 fixed witnesses
are frozen in `constants.json`.  The independent replay uses Cartesian edge
products and direct scalar enumeration instead of the primary verifier's
recursive generator and bit masks.

## Exact selector facts retained

Both replays reconstruct the two local nine-point supports, the 28 selected
cells, and the exact mass

```text
1,405,512 / 6^12 = 241/373248,
241/373248 - (7/24)^6 = 5743/191102976 > 0.
```

They also reconstruct all local order-three channels and check all 1,102
ordered selected word triples, finding zero nontrivial translation orbits.
The six-row wall therefore demonstrates a genuinely longer obstruction rather
than rediscovering the retired three-row mechanism.

## Replay

```text
python3 -I verify.py --self-test
python3 -I independent_replay.py
```

The primary standard-library replay rejects seven planted changes: a physical
vertex, a carry, a raw right side, physical coefficient cancellation, an
order-three selector edge, a unit-template count and the midpoint equation.
The separately written standard-library replay imports neither the primary
checker nor discovery code.

## Boundary

The arbitrary-potential exclusion is exact for this displayed q6/M7 full
half-open union.  The girth statement is limited to unit weights, one centre
use per abstract label, endpoint degree two and at most six rows.  Weighted or
larger packets may behave differently on other supports.

No support deformation, torsion-free Euclidean construction, recursive-state
construction, integer transfer, new `r_3(N)` bound, or solution of Erdős
Problem 142 is claimed.  The raw-canonical coercivity convention and the mass
gate are inherited external inputs.

`erdos142_solved: false`. `new_r3_bound: false`.

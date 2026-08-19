# q=42 two-layer order-seven one-block microbox wall

This packet certifies an exact wall for a **single retained union** of
complete, globally aligned seventh-residual microboxes in the fixed 117-cell
q=6 alphabet. It is not a word-language capacity theorem and does not solve
Erdos Problem 142.

## Exact theorem

Subdivide every residual coordinate of each coarse q=6 cell into seven
half-open intervals. The physical fine digit is

```text
d_j = 7*c_j + s_j,   s_j in {0,1,2,3,4,5,6}.
```

There are `117 * 7^4 = 280,917` distinct q=42 microboxes. Let `U` be any
union of complete boxes. If a bounded, single-valued physical potential on
`U` satisfies every actual pointwise raw-canonical modular-torus midpoint
inequality, then

```text
|U| <= 261,353 < 264,710.25
     = (49/576) * 42^4.
```

Thus this aligned one-block r=7 model cannot retain density strictly above
the four-coordinate EHPS product gate.

## Exact disjoint packing

The standalone verifier reconstructs three mutually support-disjoint
obstruction families.

### Strict-dilation pairs

The componentwise strict-dilation graph has 5,712 edges in 4,368
components, each of size at most nine. Exact componentwise matching gives
4,617 disjoint pairs, and every selected edge has one wrap coordinate.

For clarity, let the original bounded physical potential be `f`, put

```text
G(p) = 36*f(p) - 72*||p||_2^2,
```

and let `D(t)=G(A_t)+G(B_(1-t))` for the paired strict-interior points in
the low and high boxes. Summing the two actual midpoint inequalities at
scales `t` and `3t` gives

```text
D(3t) - D(t) >= K * (72 - 48t),   K >= 1,
```

where `K` is the number of wrap coordinates. Taking
`t=(1/14)/3^j` gives a finite telescope that contradicts boundedness if both
boxes of a selected pair survive.

### First packet layer

In the 637-point last-pair prototype, fix the order-seven translation
`(6,12)` in `Z_42^2`. Its ambient orbit intersections have exact histogram

```text
intersection size:  1   2   3   4   5   6   7
orbit count:        51  44  58  41  21   8   1
```

Exactly the 30 intersections of sizes five, six, and seven admit the frozen
unit-weight balanced-row rule: one nondegenerate midpoint row is centred at
each packet vertex, and every vertex has endpoint degree two. Thus every
vertex has total potential coefficient `+2-2=0`, while every row has
strictly positive raw endpoint-square cost.

The 30 prototypes lift through all `9*7^2=441` fixed-first-pair fibres,
giving 13,230 packets. Removing the 1,696 packets that meet a canonical
dilation endpoint leaves 11,534 packets with retained size histogram

```text
packet size:       5     6    7
packet count:   8151  2984  399
```

Their 61,452 support vertices are pairwise distinct.

### Second packet layer

Next use the order-seven translation `(0,6)` in the same prototype. Its
intersection histogram is

```text
intersection size:  1   2   3   4   5
orbit count:        70  70  49  35  28
```

All 28 five-point intersections admit the same balanced-row certificate.
They lift to 12,348 packets. Removing every packet that meets either a
dilation endpoint or a first-layer support vertex leaves 3,413 five-point
packets on 17,065 additional vertices.

The three obstruction families are mutually support-disjoint. Therefore
every feasible one-block support must make at least

```text
4,617 + 11,534 + 3,413 = 19,564
```

deletions. Retaining strictly above the gate permits only 16,206 deletions.
The packing clears the required 16,207-obstruction threshold by 3,357 and
leaves at most 261,353 boxes.

## Physical row semantics

Every finite packet row is replayed at the common strict-interior offset
`u=(1/8,2/8,3/8,4/8)`. The replay checks the physical torus midpoint, not
only the fine-digit congruence. Across 78,517 rows, incidence is exactly zero
at every packet vertex. The total raw fine-digit square cost is 39,815,496.

Exact carry histogram:

```text
(0,0,-1,-1):  5266    (0,0,-1,0):  7828    (0,0,-1,1):  4267
(0,0, 0,-1): 11215    (0,0, 0,0): 20045    (0,0, 0,1): 12535
(0,0, 1,-1):  3831    (0,0, 1,0): 10020    (0,0, 1,1):  3510
```

Exact raw fine-digit endpoint-square histogram:

```text
  36: 6456    144: 9575    180:14661    360:11143
 468: 8353    612: 8010    720: 6225    900:  664
 936: 4512   1224: 1219   1296:  370   1440: 3103
1476: 1352   1620: 1835   1872:  772   2196:  267
```

## Frozen semantics and replay

`frozen_semantic_certificate.json` fixes the geometry, matching algorithm,
both packet layers, exact row semantics, gate, scope, and canonical semantic
digests. `verify_r7_two_layer_packing.py` imports no producer, solver, or
third-party package. It independently reconstructs all 280,917 physical
boxes, the exact componentwise maximum matching, all 14,947 packet supports
and 78,517 physical rows, checks their carries, raw costs and coefficient
cancellation, verifies cross-family disjointness and exact density
arithmetic, and rejects planted failures.

Native Windows:

```powershell
python -I .\certificates\erdos-142-q6-117-cell-q42-seventh-microbox-wall\verify_r7_two_layer_packing.py --self-test
python -I .\certificates\erdos-142-q6-117-cell-q42-seventh-microbox-wall\independent_r7_audit.py --self-test
```

Linux/WSL:

```text
python3 -I ./certificates/erdos-142-q6-117-cell-q42-seventh-microbox-wall/verify_r7_two_layer_packing.py --self-test
python3 -I ./certificates/erdos-142-q6-117-cell-q42-seventh-microbox-wall/independent_r7_audit.py --self-test
```

The primary replay prints `PASS_R7_TWO_LAYER_ONE_BLOCK_PACKING_WALL` and
`FROZEN_CERTIFICATE_NONMUTATION_OK`.  The independently structured replay
prints `PASS_INDEPENDENT_R7_Q42_TWO_LAYER_ONE_BLOCK_AUDIT` and directly
reconstructs the same geometry, packing, physical rows, and gate arithmetic.

Canonical hashes are:

```text
dilation semantic:
0730b2e7730bd144b86b3299311a530ab3608f4777e9e3b257e7a4eddd2412a5

packet supports:
96dc66ed94ae58bc485cc35169da46361b71aa226e4bb2173b8266ecd9a2f3af

expanded packet semantics:
fd74a90da1a372c482c8a82acfbeed94765cff659b708ed30db1c8ed9284af6c

payload semantics:
cee9ba92386faac163476dd41c7aee1d5776a149eeb9bf5ebf1b8348bd6b10bd

frozen certificate bytes:
3eb6de036e2f8294f49f282e5f98769351ffe55fe25155a2dbf3077e14bbafa3
```

## Scope

Proved:

- exact q=42 geometry, strict-dilation recurrence, two-layer finite midpoint
  packet semantics, pairwise-disjoint packing, and density arithmetic;
- arbitrary bounded single-valued physical potentials on one complete
  aligned microbox union;
- actual strict-interior raw-canonical modular-torus midpoint inequalities.

Not proved:

- an all-horizon, graph-directed, or arbitrary word-language capacity bound;
- proper carving inside a q=42 microbox, finer or non-axis-aligned pieces,
  deformations, overlaps, almost-everywhere coercivity, or unbounded
  corrections;
- an EHPS shell construction above the gate, integer transfer, or an improved
  lower bound for `r_3(N)`.

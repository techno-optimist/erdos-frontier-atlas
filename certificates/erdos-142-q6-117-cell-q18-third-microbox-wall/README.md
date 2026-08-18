# Exact microbox walls for the fixed q=6, 117-cell alphabet

## Result

Subdivide every residual coordinate of every one of the fixed 117 coarse
cells into `r` equal half-open intervals, and retain an arbitrary union of the
resulting complete four-dimensional microboxes.  Require a bounded,
single-valued physical potential satisfying every pointwise EHPS
raw-canonical torus-midpoint inequality on the retained union.

The aligned subdivisions `r=2` and `r=3` cannot retain density strictly above
the four-dimensional EHPS gate `49/576`.

The stronger new case is `r=3`.  There are

```text
117 * 3^4 = 9477
```

available `q'=18` microboxes, and the gate in microbox units is

```text
(49/576) * 18^4 = 35721/4 = 8930.25.
```

The exact replay constructs 547 pairwise-disjoint obstruction supports:

```text
433 two-microbox componentwise-dilation supports,
114 finite common-offset balanced midpoint packets.
```

Every feasible support must delete at least one microbox from every
obstruction.  Pairwise disjointness therefore forces at least 547 deletions,
leaving at most 8930 boxes, strictly below the gate.  The margin is only one
quarter of a microbox, but all arithmetic is exact.

For `r=2`, the dilation graph alone has an exact minimum vertex cover of 143
(and a disjoint matching of 142), while strict-above-gate density allows only
107 deletions.

## Why the two obstruction types apply to arbitrary physical potentials

Write the required physical potential as `F` and normalize its correction by

```text
H(x) = q^2 (F(x) - 2 ||x||_2^2),       q=6.
```

Boundedness of `F` on the torus implies boundedness of `H`.  This is only a
change of variables; no regularity or cellwise ansatz is imposed on `H`.

For a dilation edge `A -> B`, the active residual coordinates in `A` lie in
the lowest residual microinterval and the paired coordinates in `B` lie in
the highest one.  If both full microboxes survive, the two actual
strict-interior physical midpoint rows are

```text
(X(t),  Y(t),  Y(3t)),
(X(3t), X(t),  Y(t)).
```

In every active coordinate, `X(t)` has source-cell residual `t` and `Y(t)`
has target-cell residual `1-t`; inactive coordinates use one common strict
interior residual.  The first row has carry `-1` in every genuine `0 -> 5`
wrap coordinate and the second has carry `+1`.  With `K>=1` wrap coordinates,
the two exact `q^2`-scaled correction inequalities are

```text
H(X(t))  + H(Y(3t)) - 2 H(Y(t)) >= K(108 - 24t),
H(X(3t)) + H(Y(t))  - 2 H(X(t)) >= K(-36 - 24t).
```

Thus, for `D(t)=H(X(t))+H(Y(t))`, their sum is

```text
D(3t) - D(t) >= K(72 - 48t),   K >= 1.
```

Choosing `t=(1/(2r))/3^j` gives a finite telescope whose right side eventually
exceeds the bound on any physical correction.  No continuity, affinity, or
cellwise constancy is used.

For a finite packet, give every fine digit vertex the same within-microbox
offset `u in (0,1)^4`.  Every selected integer row obeys

```text
x + z - 2y = 0 mod 18.
```

It is therefore an actual strict-interior torus midpoint row for every such
`u`.  The replay computes positive integer row weights.  At every physical
vertex, weighted endpoint incidence minus twice weighted centre incidence is
exactly zero, while the weighted raw endpoint-square total is strictly
positive.  Summing the inequalities is an immediate contradiction for an
arbitrary single-valued potential.

## Replay

From the repository root on Windows (replace `python` by `python3` in WSL or
Linux):

```text
python -I certificates/erdos-142-q6-117-cell-q18-third-microbox-wall/verify_frozen_semantic_certificate.py --self-test
python -I certificates/erdos-142-q6-117-cell-q18-third-microbox-wall/independent_replay.py certificates/erdos-142-q6-117-cell-q18-third-microbox-wall/frozen_semantic_certificate.json
python -I certificates/erdos-142-q6-117-cell-q18-third-microbox-wall/verify_microbox_dilation_cover.py
```

The authoritative payload is
`frozen_semantic_certificate.json` (`191394` bytes, SHA-256
`e445d0ca22b7c0dcca087bb6bfea60b94cdf30669e59d8b60ea4c9f96e95a18c`).
It explicitly records all 433 oriented dilation supports and, for every one
of the 114 finite packets, its support and every midpoint row, carry vector,
raw cost, and positive integer weight.  Packet, section, and whole-semantic
digests bind the data.

`verify_frozen_semantic_certificate.py` is pure standard library.  It
reconstructs the q=6 alphabet and all q=18 microboxes, checks both physical
dilation rows, replays all 4,196 finite packet rows at a common strict-interior
offset, verifies exact coefficient cancellation and positive RHS, proves all
547 obstruction supports pairwise disjoint, and checks the exact density
gate.  Its terminal output includes

```text
PACKETS_OK packets=114 rows=4196 vertices=4196 weighted_rhs=28939329285984
DISJOINT_PACKING_OK obstructions=547 forced_deletions=547
GATE_OK total=9477 allowed_deletions=546 max_retained=8930 gate_count=35721/4
PLANTED_FAILURES_OK count=5
PASS_Q18_EXPLICIT_MICROBOX_WALL
```

`verify_microbox_dilation_cover.py` is the separate standard-library replay
of the half-grid wall and the local cover census.  `search_disjoint_packets.py`,
`emit_frozen_certificate.py`, and `cegar_common_offset.py` are discovery-side
tools and are not used to accept the frozen theorem.

## Scope

This closes only unions of complete, globally aligned residual half- or
third-microboxes inside the fixed 117 coarse cells.  It does not cover a
fourth-grid or finer subdivision, arbitrary measurable carving, deformed or
overlapping tiles, context-owned subtiles, almost-everywhere inequalities,
or a graph-directed decoder.  It supplies no integer transfer and does not
solve Erdős Problem 142.

# q6 M7 redesign: matching deletion fence

Atlas certificate packet, dated 2026-08-17. This is a construction-specific
**fence** for the exact eight-cell q=6/M7 redesign: it rules out not only the
full union, but every measurable excision that would leave mass above the
supplied `(7/24)^6` gate, under the raw-canonical modular-torus coercivity
model stated below.

It is a negative certificate for one candidate family. It is not a new
`r_3(N)` lower bound and does not solve Erdős Problem 142.

## Exact support and gate

The selected cells are

```text
(38,3), (41,3), (42,3), (44,3),
(49,3), (50,3), (52,3), (56,3).
```

Each cell contains 178,605 physical q=6 boxes, so the disjoint union contains
1,428,840 boxes and has mass

```text
1428840/6^12 = 245/373248 > (7/24)^6.
```

Measured in q=6 box-volumes, the excess above the gate is exactly

```text
1428840 - (7/24)^6 * 6^12 = 5679639/64.
```

The local supports, cell-word convention, and residue condition are rebuilt
directly by both replays; no discovery output is trusted for membership.

## Frozen matching

`matching.txt` contains 102,636 pairwise vertex-disjoint order-three orbits in
`(Z/6Z)^12`, using 307,908 distinct physical boxes. Its exact order is:

1. ascending sign-canonical base-9 step code;
2. ascending sorted physical-orbit key.

The bound witness has FNV-1a-64 digest `E274395806684DE3`. For every record
`(x,y,z)`, the verifier checks the modular action `y=x+d`, `z=x+2d`, membership
of all three physical boxes in the eight selected cells, and the three cyclic
midpoint rows

```text
(x,y,z), (y,z,x), (z,x,y).
```

Their coefficients cancel at the actual physical vertices, while every
raw-canonical endpoint-square right side is positive. The total raw right
side over the frozen matching is 6,644,592.

## Measurable-deletion lemma

Fix one matched orbit and translate the three q=6 boxes by a common offset
`delta` in the open cube `(0,1/6)^12`. The offset cancels from every modular
midpoint identity and endpoint difference. If all three translated points
were retained for some `delta`, their three cyclic coercivity inequalities
would sum to `0 >=` a strictly positive number. Thus at least one of the three
points must be deleted for every common offset.

Pull the three deleted portions back to the common offset cube. They cover
that cube, so subadditivity forces at least one q=6 box-volume of deletion for
this orbit. The 102,636 matched orbits use disjoint physical boxes, hence the
lower bounds add:

```text
deleted mass >= 102636/6^12.
```

Consequently every measurable retained subset compatible with one arbitrary
real-valued physical potential `H` satisfying all retained raw-canonical
torus rows has mass at most

```text
(1428840 - 102636)/6^12 = 1326204/6^12
                               = 36839/60466176.
```

This falls below the supplied gate by the exact positive margin

```text
(7/24)^6 - 1326204/6^12
  = 889065/(64*6^12)
  = 98785/15479341056 > 0.
```

## Scope boundary

This certificate uses finite-quotient torsion and nonzero modular carries.
It thickens only through the explicit common-offset families above; it is not
an ordinary Euclidean-midpoint theorem or a general continuum classification.
It does not classify deformed supports, different q, recursive state, other
non-product constructions, or the minimum hitting set. It makes no
construction-to-integers, new `r_3(N)`, or solved-Problem-142 claim.

The mass gate and raw-canonical torus coercivity convention are inherited
inputs from the audited home lane. If either input changes, this certificate's
conclusion must be reevaluated.

## Replay

```text
python3 -I verify.py --self-test
python3 -I independent_replay.py
```

The primary replay checks all 102,636 records and rejects planted duplicate,
off-support, wrong-step, zero-step, nonpositive-cost, missing-row,
coefficient-cancellation, matching-count, and mass/gate corruptions. The
second replay is separately written, reconstructs all 102,636 records afresh,
and imports neither the primary verifier nor the matching generator.

`generate_matching.cpp` is retained as discovery provenance; the frozen
matching plus the semantic replays are the proof objects.

## Artifact hashes

`constants.json` binds the final uppercase SHA-256 values of every proof
artifact. Recompute all hashes after any edit; a changed byte requires a
matching contract update.

# q6/M7 candidate-22: exact unit-k8 deletion fence

This certificate retires an entire support-repair lane, not just one frozen
candidate.  Let `C22` be the 22 full half-open q6/M7 coarse cells listed in
`candidate.cells`.  Every subcollection of `C22` whose normalized mass is
strictly larger than the inherited benchmark `(7/24)^6` contains one of three
explicit positive eight-row midpoint packets.  Consequently no such
subcollection admits an arbitrary real-valued physical potential `H`
satisfying every required raw-canonical modular-torus coercivity row.

All three packets use the endpoint-degree-two unit template

```text
(2,3;0), (5,6;1), (5,7;2), (6,7;3),
(0,1;4), (2,4;5), (3,4;6), (0,1;7).
```

Every label occurs exactly twice among the endpoints and once as a center.
Summing the eight inequalities therefore cancels `H` at every actual physical
vertex.  The literal twelve-coordinate witnesses in `witnesses.json` have
these pairwise-disjoint coarse supports:

| packet | required cell support | raw total | normalized total |
| --- | --- | ---: | ---: |
| W1 | `{33:3, 45:0, 49:0}` | 216 | 6 |
| W2 | `{45:1, 19:6, 26:6}` | 144 | 4 |
| W3 | `{30:3, 20:5, 34:5}` | 288 | 8 |

Every row has positive endpoint cost.  Thus each packet separately gives an
exact contradiction after summation.  Both replays also add the same
`delta=1/12` to every normalized scalar coordinate.  All vertices then lie
strictly inside their original half-open boxes, while every modular carry and
endpoint difference is unchanged.  The packets are open, branch-sensitive
torus families rather than grid-boundary accidents.

## Deletion arithmetic

The exact full-cell mass is

```text
|C22| = 1,370,520 boxes = 235/373248,
```

which exceeds `(7/24)^6` by `2671/191102976`.  A subcollection avoiding all
three displayed packets must remove at least one cell from each required
support.  Those supports are pairwise disjoint, and their least cell weights
are

```text
5,832, 5,832, 69,984.
```

Therefore every packet-free subcollection has at most

```text
1,370,520 - (5,832 + 5,832 + 69,984) = 1,288,872 boxes
                                              = 221/373248.
```

The comparison with the inherited gate is strict:

```text
1,288,872 * 64 - 85,766,121 = -3,278,313 < 0.
```

This implication uses only the three positive literal witnesses and exact
cell weights.  It does not rely on solver-negative output or on completeness
of the discovery search.

## Replay

```text
python3 -I verify.py --self-test
python3 -I independent_replay.py
```

The primary replay reconstructs the q6 supports, all cell weights, all 24
physical midpoint rows and integer carries, positive raw costs, exact
arbitrary-`H` cancellation, the common strict-interior lift, and the deletion
arithmetic.  It rejects five planted semantic corruptions.  The independently
written replay hard-codes a separately transcribed ordering of the witnesses,
uses direct parity enumeration for cell weights, and rejects three additional
mutations without importing the primary packet or verifier.

## Boundary

The theorem covers only subcollections of these 22 **whole** q6/M7 cells under
the stated raw-canonical modular-torus convention.  Partial carving of a cell,
geometric deformation, replacement cells, different supports, recursive
state, and non-product lifts remain outside scope.  Nonzero carries prevent an
ordinary Euclidean-midpoint or integer-transfer conclusion.  The benchmark
`(7/24)^6` is an inherited external input and is not re-derived here.  No new
bound on `r_3(N)` is claimed, and Erdős Problem 142 remains unsolved.

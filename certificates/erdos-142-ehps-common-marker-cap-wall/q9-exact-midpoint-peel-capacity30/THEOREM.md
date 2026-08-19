# Exact midpoint-peelability capacity of `(Z/9Z)^2`

## Theorem

Let `C9` be the largest cardinality of a subset `S` of `(Z/9Z)^2` for
which the points can be removed one at a time so that the point removed is
never the midpoint of two distinct points still present. Then

```text
C9 = 30.
```

Equivalently, 30 is the largest support admitting a strict midpoint
potential. The potential/peeling equivalence is proved in the bound
certificate nested at `certificates/capacity32_base`.

## Lower bound

The nested bound certificate contains an explicit 30-point reverse-add order.
Its exact integer replay checks all 131 midpoint rows. With value `4^j` at
rank `j`, the minimum strict defect is 18 and the minimum denominator-9
physical margin is 1,448. Hence `C9 >= 30`.

## Fibre cap and the exhaustive size-31 dichotomy

Reduce points modulo 3 into the nine fibres over `AG(2,3)`. A peelable set
uses at most four points in each fibre: five points in one fibre contain an
affine line, and that line is already a midpoint core.

There are exactly 1,278 vectors in `{0,1,2,3,4}^9` with coordinate sum 31.
The exact profile replay partitions them as follows:

- 1,224 profiles contain a quotient line whose three fibres all have size 4;
- 54 profiles have sizes `4^4 3^5`, with the four saturated quotient points
  forming a four-cap.

The 54 four-caps form one `AGL(2,3)` orbit. Thus these two branches exhaust
every hypothetical peelable 31-point support.

## Four-cap branch

Normalize the four saturated quotient fibres to
`{(1,0),(2,0),(0,1),(0,2)}`. The full lifted stabilizer has 5,832 elements
and three point orbits, so the first point in a reverse peel order has three
representatives. Stabilizers of those representatives split the second point
into `10+4+10=24` exact orbit cases, each covering all 80 remaining choices.

Every case is encoded by the exact reverse-add rank CNF, with all physical
midpoint rows. The common base has 11,203 variables and 131,681 clauses; each
case adds four rank-fixing units. Official CaDiCaL 3.0.1 produced a binary
DRAT proof for each case. Pinned Windows and Linux `drat-trim` builds checked
all 24 and returned `s VERIFIED`. Exact CNF/proof hashes and sizes are bound by
`certificates/fourcap31/PROOF_PROVENANCE.json`.

Therefore the 54 non-slab profiles are impossible.

## Saturated-slab branch

A quotient line of three saturated fibres gives a 12-point slab. Peelability
is hereditary, so the slab itself must be peelable. The exact census in the
bound certificate checks all `54^3 = 157,464` saturated slabs. Exactly 5,832
are peelable, and the full affine slab stabilizer splits them into exactly two
orbits of size 2,916, represented by `T0` and `T1`.

For each representative, the direct certificate fixes those 12 points and
encodes an arbitrary 31-point support with at most four points per fibre.
There is no conditional allowed list and no blocker pruning: all 3,240
unordered physical endpoint pairs and all 31 rank boundaries are present.
Both direct CNFs have 5,872 variables and 109,614 clauses.

Official CaDiCaL 3.0.1 returned UNSAT and emitted binary DRAT. Independent
native-Windows and WSL/Linux `drat-trim` runs read every proof byte and both
returned `s VERIFIED`, with identical platform-independent censuses:

| case | proof bytes | core clauses | core lemmas | resolutions | RAT |
|---|---:|---:|---:|---:|---:|
| T0 | 1,328,969,194 | 53,338/109,614 | 8,967,833/17,335,854 | 496,922,885 | 0 |
| T1 | 803,141,910 | 52,472/109,614 | 5,063,741/10,636,505 | 283,260,141 | 0 |

The compact projection at `certificates/direct_slab31` contains both CNFs,
the independent standard-library structural verifier, exact solver/checker
logs, checker source, and the frozen source-packet manifest. Raw proofs and
compiled checker binaries remain external.

Therefore all 1,224 saturated-slab profiles are impossible.

## Conclusion

The two size-31 branches are exhaustive and both are impossible, so
`C9 <= 30`. The explicit witness gives `C9 >= 30`; hence `C9 = 30`.

## Trust and replay boundary

`python -I -B verify_all.py` is the portable compact replay. It checks closed
manifests, reruns the lower witness/fibre/slab/profile/symmetry reductions,
regenerates all four-cap case CNF hashes, structurally audits both direct CNFs,
checks the exact proof ledgers and native/Linux verification logs, and proves
nonmutation. Because raw DRAT payloads are deliberately not shipped, this
compact command emits only `STRUCTURE_READY_EXTERNAL_PROOFS_REQUIRED`, never
an exact-theorem pass marker, rather than pretending to recheck UNSAT.

Supplying the external four-cap artifacts, the two direct proof files, and a
pinned checker to `verify_all.py` performs every DRAT check and emits
`CONCLUSION_EXACT_C9_30`. See `README.md` for the command.

The theorem here is finite and exact. A separate conditional arithmetic
consequence for the literal one-common-marker `h=8` model is stated in
`COMMON_MARKER_H8_COROLLARY.md`; it makes no unconditional continuum,
phase-owned, integer-transfer, progression-free-set, or Erdos Problem 142
claim.

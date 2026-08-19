# q6 M7: mass-positive order-three-orbit-free selector

Atlas certificate packet, dated 2026-08-18. It records a new support-design
lead in the full q=6/M=7 cell universe: an explicit union of 28 disjoint cells
has mass strictly above the supplied `(7/24)^6` gate while containing no
nontrivial order-three translation orbit in `(Z/6Z)^12`.

This escapes the cyclic torsion and matching-deletion mechanisms certified for
the earlier eight-cell redesign. It does **not** certify a coercive potential,
exclude other balanced hypercycles, give an integer construction, improve
`r_3(N)`, or solve Erdős Problem 142.

## Full cell universe and exact mass

A coarse cell is `(word,residue)`, where `word` is one of the 64 choices of
the two local nine-point supports in six coordinate blocks, and `residue` is
the exact sum of the six local parity bits, from 0 through 6. Thus the full
selector universe has `64*7 = 448` cells. The historical number 148 counts
parity-pattern states inside a different 24-cell selector; it is not the full
cell universe.

The selector frozen in `selector.cells` is

```text
r=0: 7,11,21,25,35,45,49,62
r=1: 27,45,54
r=2: 7,56
r=3: 30,33
r=4: 21,42
r=5: 9,20,34
r=6: 4,19,25,26,35,41,42,48
```

The two local supports have parity counts `(3 even,6 odd)` and
`(6 even,3 odd)`. Both replays reconstruct every cell coefficient directly
and obtain

```text
box count = 1,405,512
mass      = 1405512/6^12 = 241/373248
gate      = (7/24)^6
excess    = 4,186,647/64 q6 boxes
          = 5743/191102976 normalized mass.
```

## Exact orbit criterion

Every order-three q6 translation uses local increments in `{0,2,4}^2`, so it
preserves each local parity bit and hence the exact residue. For a word triple
`(a,b,c)`, let `v` be the number of nonconstant coordinate columns and let `t`
be the number of those columns containing exactly one `1`. Direct enumeration
of all 42 valid local increment/start configurations gives the exact criterion

```text
v > 0 and t <= residue <= t + 6 - v.
```

The replays test every ordered selected word triple in every residue layer,
using both this closed form and an independently reconstructed local-channel
dynamic program. The number satisfying the criterion is zero. Therefore the
union has no nontrivial order-three physical orbit and the associated cyclic
three-row matching number is exactly zero.

An independent discovery audit also solved the residue-wise weighted
orbit-free selector problems and found that this mass is optimal inside that
finite orbit-free cell-selector model. That optimization is useful provenance
but is deliberately outside the promoted machine claim here; the committed
standard-library replays certify the explicit selector and its zero-orbit
property only.

## What remains open

Order-three torsion is only one source of Farkas obstructions. General modular
midpoint rows can combine into longer balanced hypercycles even when the
support has no three-point translation orbit. Existing additive and
class-constant potential screens for a selector with the same mass are
negative, but those restricted rays do not cancel at actual physical vertices
and therefore do not rule out an arbitrary global potential. The next decisive
test is a physical-vertex-balanced potential/Farkas computation for this
selector, followed by a continuum and integer-transfer argument if it survives.

The mass gate and raw-canonical torus convention are inherited inputs from the
audited home lane. No ordinary Euclidean-continuum statement is made here.

## Replay

```text
python3 -I verify.py --self-test
python3 -I independent_replay.py
```

The primary standard-library replay validates artifact hashes, reconstructs
the local supports and all 42 channels, cross-checks the closed orbit criterion
against direct dynamic composition, verifies the mass/gate direction, and
rejects planted selector, edge, zero-step, mass, and gate corruptions. The
second replay is separately written and imports neither the primary verifier
nor discovery code.

## Artifact hashes

`constants.json` binds the final uppercase SHA-256 values of the four proof
artifacts. Any byte change requires regenerating both it and the certificate
contract entry.

# q6 M7 redesign: exact physical torsion wall

Atlas certificate packet, dated 2026-08-17. The claim is deliberately scoped
to the exact eight-cell union and its raw-canonical torus midpoint convention.

The eight-cell support is

```text
(38,3), (41,3), (42,3), (44,3),
(49,3), (50,3), (52,3), (56,3).
```

The verifier reconstructs the two local 9-point supports and proves that the
cells are physically disjoint.  Each listed word has Hamming weight three,
and every selected cell has exact count

```text
[t^3] (3 + 6t)^3 (6 + 3t)^3 = 178605.
```

Consequently the packet has exact mass

```text
1428840 / 6^12 = 245/373248,
245/373248 - (7/24)^6 = 2597/63700992 > 0.
```

## Exact wall

`semantic_packet.json` names three **distinct physical** vertices `X`, `Y`,
and `Z`.  Both `X` and `Y` are in `(38,3)`, but they are different 12D q6
vertices; `Z` is in `(41,3)`.  The verifier checks their complete coordinate
lists, word/residue identities, all three modular carries, and the three raw
endpoint-square RHS values.

For a completely arbitrary single function `H` on the physical finite union,
the q6 raw-canonical modular midpoint rows are

```text
H(X) + H(Z) - 2H(Y) >= 48
H(Y) + H(Z) - 2H(X) >= 48
H(X) + H(Y) - 2H(Z) >= 48.
```

Their coefficients cancel at the actual physical vertex level, not at a cell
or occurrence label, while the RHS sums to `144`.  After division by `6^2`,
this is the contradiction `0 >= 4`.

## Strict half-open-box torus lift

For every common offset `delta in (0,1/6)^12`, add `delta` to each of
`X/6`, `Y/6`, and `Z/6`.  All three points are strict interiors of their
respective selected half-open boxes.  The common offset cancels from every
modular midpoint equation, so the verified carries remain unchanged, and it
cancels from endpoint differences, leaving each normalized RHS equal to
`48/36 = 4/3`.  The verifier checks a rational interior sample
`delta=(1/12,...,1/12)` and the coordinatewise open-box argument.

This proves a positive-dimensional **branch-sensitive raw-canonical torus**
wall, not a grid-boundary artifact.

## Deletion caveat

This wall does not by itself make the complete eight-cell support family
deletion-robust.  The verifier includes a factor-DP census for the particular
order-three step of the displayed wall,

```text
[(4,0), (4,2), (4,2), (4,0), (0,0), (0,0)].
```

It finds only 135 oriented starts, namely 45 disjoint three-orbits for that
fixed step, distributed as 45 starts in each of the cell triples
`(38,38,41)`, `(38,41,38)`, and `(41,38,38)`.  Deleting one q6 box from each
of those 45 orbits would kill this entire fixed-step mechanism, far below the
exact mass-gate slack of `5679639/64`, approximately `88744.36`, q6 boxes.

This does **not** census other order-three steps and does not give an all-step
hitting-set or minimum-deletion lower bound.  Therefore the artifact excludes
the exact full support under the stated model; it does not claim that every
nearby support obtained by excising boxes is excluded.

## Scope boundary

This is not an ordinary Euclidean-continuum midpoint result.  Each cyclic row
uses nonzero modular carries; in a torsion-free Euclidean vector space a
nontrivial cyclic three-midpoint configuration cannot occur.  The packet makes
no Euclidean-continuum, construction-to-integers, `r_3(N)`, or Atlas claim.

## Replay

```text
python -I verify.py
python -I verify.py --self-test
python -I independent_replay.py --self-test
```

The self-test rejects planted changes to a selected cell, a physical vertex,
a carry, an RHS, a row coefficient pattern, and the exact mass/gate margin.
The independent replay is a separately written stdlib-only implementation; it
imports neither the primary verifier nor any discovery code and independently
reconstructs the same mass, physical rows, open-offset lift, and 45-orbit
fixed-step caveat.

## Artifact hashes

The contract binds the final lowercase SHA-256 values of `README.md`,
`semantic_packet.json`, `verify.py`, and `independent_replay.py`. Recompute with
`sha256sum` (or `Get-FileHash -Algorithm SHA256`) after any edit; a changed byte
requires a matching contract update.

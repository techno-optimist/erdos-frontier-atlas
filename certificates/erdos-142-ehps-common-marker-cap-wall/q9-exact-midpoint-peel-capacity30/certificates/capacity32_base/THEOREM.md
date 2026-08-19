# Exact q9 midpoint-peelability capacity: `30 <= C_9 <= 31`

Date: 2026-08-19.  This is a self-contained, promotion-ready certificate.
The archival names and manifest digests in `SOURCE_BINDINGS.json` are
provenance labels only; replay does not require the source packets.

## Statement

Let `C_9` be the largest size of a subset `S` of `(Z/9Z)^2` admitting a strict
midpoint potential

```text
F(x)+F(z)>2F(y) whenever x,z are distinct and x+z=2y in S.
```

Equivalently, `C_9` is the physical-potential capacity for any fixed finite
positive endpoint costs: a strict finite potential can be scaled to dominate
all such costs.  The exact result proved here is

```text
30 <= C_9 <= 31.                                       (1)
```

No claim that `C_9=31` is made.

## 1. Potential versus peeling

A finite support is peelable if one can repeatedly remove a vertex which is
not the midpoint of two distinct remaining vertices.

If a strict potential exists, choose a vertex where it is maximal.  It cannot
be a midpoint: both endpoints would have value at most its value, contradicting
strictness.  Remove it and repeat.

Conversely, reverse a deletion order to obtain an insertion order in which a
new vertex is never the midpoint of two earlier vertices.  Give its `j`-th
vertex value `B^j` for any integer `B>2`.  In every midpoint row the
highest-ranked vertex is an endpoint, and its leading power exceeds twice the
midpoint power.  This is a strict potential.

Simultaneously stripping unsupported vertices gives a unique terminal core.
A nonempty core is monotone: every superset containing it is nonpeelable.

## 2. Exact 30-point lower bound

The reverse-add order is

```text
(1,7) (5,1) (6,4) (0,4) (3,2) (8,8) (4,5) (6,0)
(2,6) (3,6) (1,0) (4,7) (8,3) (5,3) (6,6) (3,8)
(1,2) (8,5) (5,4) (6,8) (5,5) (7,3) (2,7) (7,5)
(4,4) (1,3) (6,1) (8,7) (0,2) (3,0)
```

With value `4^j` at rank `j`, exact replay finds 131 midpoint rows, minimum
strict defect 18, and minimum denominator-9 physical margin 1,448 for both
raw and intrinsic torus squared distance.  This proves `C_9>=30`.

## 3. Saturated-fibre reduction for target 32

Partition `(Z/9Z)^2` into its nine fibres modulo 3.  Inside one fibre the
midpoint law is that of `AG(2,3)`.  Every five points in `AG(2,3)` contain an
affine line, whose three points form a midpoint core.  Hence a peelable support
uses at most four points per fibre.

A 32-point support must have at least five saturated four-point fibres, since
four saturated fibres and five fibres of size at most three total only 31.
The saturated fibre locations form at least five points of the quotient
`AG(2,3)`, so they contain a quotient line.  Its three fibres give a 12-point
slab.  Peelability is hereditary, and an affine automorphism normalizes the
slab to `y=0 mod 3`.

Each of its three fibres is one of the 54 four-caps in `AG(2,3)`.  The
standard-library replay checks all

```text
54^3 = 157,464
```

choices.  Exactly 5,832 are peelable.  The full 26,244-element affine
set-stabilizer of the slab splits them into exactly two orbits, each of size
2,916, represented by:

```text
template0:
(0,3) (0,6) (1,3) (1,6) (2,0) (2,3)
(3,0) (4,0) (4,3) (5,0) (5,3) (6,0)

template1:
(0,0) (0,3) (1,0) (1,6) (2,3) (2,6)
(3,3) (4,0) (4,3) (5,0) (5,3) (6,0)
```

It remains only to exclude a 20-point extension of each fixed template.

## 4. Sound conditional blocker families

For a fixed template, an outside set `B` is a blocker when the template
together with `B` has a nonempty midpoint core.  Every extension containing
`B` is then nonpeelable.

Fifteen singleton blockers remove the other points of the normalized slab,
leaving 54 allowed points in six nine-point fibres.  The transparent ledgers
have the exact censuses:

| family | size 1 | size 2 | size 3 | size 4 | size 5 | size 6 | nonsingle total |
|---|---:|---:|---:|---:|---:|---:|---:|
| template0 | 15 | 0 | 297 | 3,177 | 11,619 | 0 | 15,093 |
| template1 | 15 | 0 | 297 | 3,798 | 9 | 27 | 4,131 |

The Python semantic verifier checks every ledger entry directly for a
nonempty core and checks every one-point deletion for an empty core.  It also
reconstructs the original 944-variable CNFs byte for byte.  Template1's full
ledger is independently regenerated from all minimal blockers through size
four plus the 36 images of four supplied representatives under the
nine-element template stabilizer.  Template0's complete minimal family
through size five can optionally be exhaustively regenerated; completeness
is not needed for the theorem because every clause actually used is checked
sound.

## 5. Direct solver-independent exhaustive cover

`compact_fibre_verify.cpp` proves both extension masters without a SAT solver
or proof checker.

For each of the six fibres it enumerates every internally blocker-free subset
of size zero through four.  The domain sizes, in order, are

```text
1, 9, 36, 72, 54.
```

An exact 20-set has one of the 126 profiles in `{0,1,2,3,4}^6` summing to 20.
For every profile, the DFS chooses one domain element per fibre.  Each
nonsingleton blocker is assigned to the last of its involved fibres in the
fixed search order; it is tested exactly when that fibre is assigned.  Thus a
leaf is reached if and only if it is a 20-point fibre-cap-valid set avoiding
every supplied sound blocker.

The deterministic exhaustive ledgers are:

| case | fibre order | blockers completed by depth | profiles | recursion nodes | result |
|---|---|---|---:|---:|---|
| template0 | `1,4,2,3,0,5` | `12,183,597,1668,3855,8778` | 126 | 3,017,764 | UNSAT |
| template1 | `2,3,4,5,0,1` | `12,111,228,660,1101,2019` | 126 | 1,989,055 | UNSAT |

All blocker and profile loops are finite explicit loops, with no timeout,
randomness, floating point, memoization, or external solver.  The executable
runs an internal-only SAT control, an all-singleton UNSAT control, and a
full-ledger target-19 *constraint-relaxation* SAT control before each theorem
search.  The latter is positively not a peelable 31-point witness: independent
core replay leaves residual cores of size 27 for template0 and 31 for
template1.

The constraints are downward closed.  If a blocker-free, fibre-cap-valid set
of size at least 20 existed, any 20-subset would also satisfy them.  Therefore
the exact-20 exhaustion excludes every extension of size at least 20.

Both slab orbits are impossible in a peelable 32-set.  Section 3 showed that
every hypothetical peelable 32-set normalizes to one of them.  Hence no such
set exists, proving `C_9<=31`.  Together with Section 2, this proves (1).

## 6. Independent DRAT provenance

The original conditional CNFs also have official CaDiCaL DRAT proofs checked
by official `drat-trim` on Windows and Linux.  They are independent secondary
evidence, not dependencies of this compact proof.  Their exact hashes,
checker ledgers, and compression trial are in `DRAT_PROVENANCE.md`; the large
proof payloads and compiled binaries are intentionally omitted.

## 7. Scope

The finite theorem is exactly `30<=C_9<=31`.  It does not determine whether a
31-point support exists.  The literal common-marker consequence, including
its additional analytic hypotheses and exact epsilon range, is stated
separately in `COMMON_MARKER_H8_COROLLARY.md`.  Nothing here handles
phase-owned/context-owned markers, constructs a continuum marker, performs an
integer transfer, improves `r_3(N)`, or solves Erdős Problem 142.

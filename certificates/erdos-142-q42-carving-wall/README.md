# q=42 arbitrary-measurable proper-carving wall (one 4D block)

This package closes the proper-carving gap left by the complete-q=42-microbox
wall for one fixed four-dimensional support.  Its statement is deliberately
pointwise and physical: no almost-everywhere replacement, state-indexed
potential, or wrapped-distance convention is being used.

## Exact theorem

Let `U` be the fixed 117-cell q=6 four-dimensional union and let
`E subseteq U` be **any measurable subset**.  It need not be a union of
aligned q=42 boxes: different boxes may be carved in arbitrary,
non-axis-aligned ways.  Suppose a single-valued physical function
`F:E -> R` satisfies, for every actual canonical torus-midpoint triple in
`E`,

```text
F(x) + F(z) >= 2 F(y) + ||x-z||_2^2.
```

Then

```text
mu(E) <= 263277 / 42^4 < 49 / 576.
```

No boundedness, continuity, additivity, finite-state hypothesis, or
piecewise description of `F` is used.  The conclusion is a finite
balanced-packet / common-offset measure argument.

## Why arbitrary measurable carving is covered

For each selected packet `P`, let its distinct q=42 digit vectors be
`d_v` and write

```text
p_v(u) = (d_v + u)/42,     u in [0,1)^4,
A_v = {u : p_v(u) in E}.
```

The package supplies a positive-raw-cost midpoint row centered at every
vertex, with unit weights and zero total potential incidence.  The common
offset cancels from every modular midpoint identity.  If
`intersection_v A_v` were nonempty, summing the pointwise inequalities for
that offset would cancel the same physical values of `F` and yield
`0 >=` a strictly positive raw endpoint-cost total.  Hence the intersection
is empty, and the union bound gives

```text
1 <= sum_v mu([0,1)^4 minus A_v).
```

Since every `u -> p_v(u)` is a half-open-box bijection with Jacobian
`42^-4`, the deleted physical volume in a packet support is at least
`42^-4`.  This is a fractional loss: it does **not** assume that an entire
fine box is deleted, and it is not evaded by deleting a null point from each
box.

## Exact packet packing and gate

The replays reconstruct two translation-orbit packet layers in the fixed
q=42 refinement:

| family | last-pair shift | packets | support fine boxes |
| --- | --- | ---: | ---: |
| first | `(6,12)` | 13,230 | 70,560 |
| second, after first supports | `(0,6)` | 4,410 | 22,050 |
| total | — | **17,640** | **92,610** |

All packet supports are pairwise disjoint, so the fractional losses add.  The
universe has `117*7^4 = 280,917` q=42 boxes.  The four-coordinate EHPS
gate is

```text
(49/576)*42^4 = 1058841/4 = 264710.25.
```

Therefore

```text
mu(E) <= (280917-17640)/42^4 = 263277/42^4,
```

which is below the gate by `5733/4` q=42-box-volume units.  The arithmetic
uses exact volume; the informal whole-box deletion budget above the gate is
`16,206`, while the packet lower bound is `17,640`.

As a controlled failure check, a uniform collar carve retaining only
`[1/144,143/144]^4` residuals within every q=6 cell has relative cell mass
`(71/72)^4 > 49/52`, so it would beat the gate numerically.  At the fixed
common offset `(1/8,2/8,3/8,4/8)`, all packet witnesses are at least
`1/56` from a coarse-cell face; the collar width `1/144` leaves them
present, so the finite packet already rules this carve out.

## Replays

The frozen JSON packet records the geometry, two shifts, exact counts, gate,
and semantic digests.  The primary standard-library replay corroborates it.
The separately written independent replay is claim-certifying: it imports
neither the primary module nor a solver, reconstructs the geometry and
balanced rows from digit arithmetic, checks all 92,610 physical common-offset
rows and exact carries/raw costs, proves support disjointness, binds the
frozen packet, and checks nonmutation.

From the repository root on native Windows:

```powershell
python -I certificates\erdos-142-q42-carving-wall\q42_fractional_carving_wall.py
python -I certificates\erdos-142-q42-carving-wall\replay.py --target certificates\erdos-142-q42-carving-wall
```

From the repository root in Linux/WSL:

```text
python3 -I certificates/erdos-142-q42-carving-wall/q42_fractional_carving_wall.py
python3 -I certificates/erdos-142-q42-carving-wall/replay.py --target certificates/erdos-142-q42-carving-wall
```

The expected success markers are
`PASS_Q42_FRACTIONAL_PROPER_CARVING_WALL` and
`PASS_INDEPENDENT_Q42_FRACTIONAL_CARVING_AUDIT`.

## Provenance and hashes

The primary script, frozen certificate, and independent hostile replay are
the audited source packet with repository line-ending normalization.  The
hostile-audit record in this directory is an archival review of the original
source bytes; its source-packet hashes are:

```text
primary source: c543e7fd118981c530ad81a1dd0c4e105c5c1eca253aefd50c6c007c5a818fac
certificate:    60d9d974aa23755615d159653508dbb38769fb0d883c974a4425e51b278119b4
source README:  9422cc398540a34feca2dfb75a768b818a9ab3c547dc53d09f062d3f493b9632
```

The package-specific artifact hashes are bound in
`certificates/contracts.json`.

## Scope

Proved: arbitrary measurable proper carving of the fixed **one-block**
117-cell q=6 union, assuming a single-valued physical potential and
pointwise raw-canonical torus-midpoint coercivity on every actual triple.

Not proved: an almost-everywhere version; multivalued, label/state-indexed,
or context-owned potentials; a graph-directed, word, path, or multi-block
capacity theorem; overlap-kernel or coupled-tile constructions; an EHPS shell
construction; integer transfer; an improved `r_3(N)` lower bound; or a
solution of Erdős Problem 142.

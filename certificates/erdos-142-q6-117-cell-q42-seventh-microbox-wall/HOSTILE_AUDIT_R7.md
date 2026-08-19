# Hostile release audit — q=42/r=7 two-layer one-block wall

## Verdict

**APPROVE — no release blocker found.**

This is a valid finite, one-block exclusion certificate under its stated
pointwise hypothesis: a bounded, single-valued physical potential on a union
of complete globally aligned q=42 microboxes, satisfying every actual
raw-canonical modular-torus midpoint inequality.  It is not a word-capacity
theorem and does not improve the EHPS integer bound by itself.

## Frozen input

Audited directory:

```text
D:\p42_research\erdos142_r7_microbox_frontier_20260818
```

Frozen certificate SHA-256:

```text
3eb6de036e2f8294f49f282e5f98769351ffe55fe25155a2dbf3077e14bbafa3
```

The supplied replay SHA-256 is
`6bb6368296d4030cc2a4ee262345c67eaa5226bd9ad8cee33a13f972fe1bcccd`;
the README SHA-256 is
`c9539040b71fb0414489ad8d3fd6d03180e10475348ea49d993f482d4161db22`.

## Independent reconstruction

I wrote a separate standard-library replay in this isolated scratch
directory:

```text
independent_r7_audit.py
SHA-256 e53cf4dd670b1929b7347c90f4255addb80b900386ac92ed9e3128a97aaa2198
```

It does not import, execute, or read `explore_r7.py` or the supplied replay.
It regenerates the 117 cells and all 280,917 q=42 physical codes, builds the
strict-dilation graph, computes a maximum matching by an independent
componentwise exhaustive search, regenerates both translation-orbit packet
layers, solves each finite zero-incidence row condition, and checks physical
midpoints at the common offset `(1/8,2/8,3/8,4/8)` with exact rational
arithmetic.  The frozen JSON is read only after those computations and is
compared by byte hash, reported fields, and the three semantic digests.  The
packaged replay changes only the source-location wrapper to use its own
directory, so the same independent reconstruction works from the repository
on native Windows and WSL rather than depending on this scratch location.

Independent result:

```text
GEOMETRY: 117 cells, 280917 q=42 boxes
DILATION: 5712 edges, 4368 components, maximum component size 9,
          4617 disjoint matching pairs, exactly one wrap per pair
PACKETS: 11534 first-layer + 3413 second-layer packets;
         61452 + 17065 mutually disjoint support vertices;
         78517 physical rows
SEMANTICS: zero potential incidence at every packet vertex; 9 carry types;
           aggregate strictly positive raw cost 39815496
PACKING: 4617 + 11534 + 3413 = 19564 forced deletions
GATE: 49/576 * 42^4 = 1058841/4; strictly-above-gate budget 16206 deletions;
      retained count <= 261353; obstruction margin 3357 above 16207 required
```

The independently recomputed semantic digests agree exactly:

```text
dilation  0730b2e7730bd144b86b3299311a530ab3608f4777e9e3b257e7a4eddd2412a5
support   96dc66ed94ae58bc485cc35169da46361b71aa226e4bb2173b8266ecd9a2f3af
expanded  fd74a90da1a372c482c8a82acfbeed94765cff659b708ed30db1c8ed9284af6c
```

## Mathematical checks

For every chosen dilation pair the audit checked both actual torus midpoint
triples underlying the recurrence.  After the stated correction
`G=36 f-72 ||p||_2^2`, their summed correction is exactly
`K(72-48t)` with `K=1`; the residual representatives stay in their low/high
microboxes for the entire geometric telescope.  Thus retaining both boxes
contradicts boundedness.

For every packet row, the audit checked fine-digit midpoint congruence,
the resulting integral physical carry, physical equality of the three
strict-interior representatives, positive raw endpoint-square cost, and
the cancellation vector `(+1,-2,+1)`.  Hence a wholly retained packet
contradicts the pointwise inequalities after summation.  First-layer,
second-layer, and matching supports were verified pairwise disjoint, so the
deletion lower bounds add without double counting.

## Platform replays

All four replays passed:

```text
Windows supplied:      python -I verify_r7_two_layer_packing.py --self-test
WSL supplied:          python3 -I ./verify_r7_two_layer_packing.py --self-test
Windows independent:   python -I independent_r7_audit.py --self-test
WSL independent:       python3 -I independent_r7_audit.py --self-test
```

Both supplied replays emitted
`PASS_R7_TWO_LAYER_ONE_BLOCK_PACKING_WALL`; both independent replays emitted
`PASS_INDEPENDENT_R7_Q42_TWO_LAYER_ONE_BLOCK_AUDIT`.

## Scope audit

The README correctly limits the result to one retained union of complete,
globally aligned q=42 microboxes and explicitly excludes arbitrary
word-language / graph-directed capacity, proper submicrobox carving,
non-axis-aligned pieces, overlaps, almost-everywhere coercivity, unbounded
corrections, EHPS shell transfer, and an improved `r_3(N)` bound.  The
release text should preserve those exclusions verbatim in substance.

## Residual caveat

This is an exact finite obstruction wall, not evidence that the broad
graph-directed or context-owned-subtile routes are closed.  The approval
applies only to the narrowly stated one-block theorem.

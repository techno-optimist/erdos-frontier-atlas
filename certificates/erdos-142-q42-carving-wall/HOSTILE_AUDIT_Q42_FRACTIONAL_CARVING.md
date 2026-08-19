# Hostile audit: q=42 arbitrary-measurable carving wall

## Verdict

**APPROVE, conditional on the literal stated hypothesis:** one physical,
single-valued `F:E -> R` obeys the raw-canonical torus-midpoint inequality
**pointwise for every actual triple** in the one-block set.  I found no
full-microbox, dilation, boundedness, additivity, or regularity assumption in
the measurable-deletion implication.

This is a one-block exclusion for the fixed 117-cell `q=6` union.  It is not
a path/word-capacity theorem, a construction of a potential, an EHPS shell
certificate, an integer transfer, or a solution of Erdős Problem 142.

## Independent reconstruction

`independent_q42_fractional_carving_replay.py` is self-contained and imports
neither the candidate script nor a candidate helper.  It rebuilds the 117
coarse cells, all `117*7^4 = 280,917` q=42 digit boxes, the two order-seven
tail translations, and the two lifted packet layers.  It has two separate
finite balanced-row searches: a canonical exact degree search used to compare
the frozen row digest, plus a variable-order (MRV) search used as a second
witness for every prototype packet.

It verified, from digit arithmetic:

| check | result |
| --- | ---: |
| first layer | 13,230 packets |
| second layer after first supports | 4,410 packets |
| all packet supports | 17,640 pairwise-disjoint packets |
| distinct q=42 boxes in those supports | 92,610 |
| actual physical common-offset rows | 92,610 |
| aggregate potential incidence | zero in every packet |
| endpoint raw costs | all strictly positive |
| retained count upper bound | 263,277 |
| q=42 gate count | 1,058,841/4 = 264,710.25 |
| margin below gate | 5,733/4 q=42-box units |

The replay validates all 92,610 4D digit congruences, then checks their
physical representatives at a rational common offset.  This is a symbolic
all-offset check: in every coordinate,

```text
((d_x + u) + (d_z + u) - 2(d_y + u)) / 42
  = (d_x + d_z - 2d_y) / 42 = integer carry.
```

The `u` coefficient is identically zero, so the same row is an actual torus
midpoint for every `u in [0,1)^4`, not merely the displayed test offset.  The
physical right side is `raw/42^2`, hence is strictly positive exactly when
the independently checked raw cost is positive.  The complete carry census
was

```text
(0,0,-1,-1): 6272  (0,0,-1,0): 9163  (0,0,-1,1): 4998
(0,0, 0,-1):13671  (0,0, 0,0):23079  (0,0, 0,1):14994
(0,0, 1,-1): 4606  (0,0, 1,0):11270  (0,0, 1,1): 4557
```

The raw-cost census is `{36:8134, 144:10976, 180:16709, 360:13132,
468:8869, 612:8820, 720:6713, 900:2254, 936:5782, 1224:1519, 1296:686,
1440:3822, 1476:1421, 1620:2303, 1872:882, 2196:588}`.

All four rebuilt support/row SHA-256 digests exactly match the frozen
certificate:

```text
first_support  e91b67988985df24a69f9c7350df564fa1abf6e1ae308c71aaeb7761e9a089ec
second_support d59a81e0494937b1483952f49f1fbd099b4298f5d0b7fa6d2cc4a85ef456ca66
all_support    4c8f6f00b67cf5e29f7ece22467ee40f4102491a92b5575fe734ffc389405357
expanded_rows  2b83d3841ded7fd9329b625e493c1bae93145423f430da359fb3035ad4f61835
```

## Arbitrary-measurable step

For a packet `P` with digit vectors `d_v`, write

```text
phi_v(u) = (d_v + u)/42,  u in [0,1)^4,
A_v = phi_v^{-1}(E).
```

Each `A_v` is measurable when `E` is.  Its map is a bijection from the
half-open unit cube onto the half-open fine box
`product_j [d_v,j/42,(d_v,j+1)/42)`, with Jacobian `42^-4`.  If `u` belonged
to every `A_v`, every row of its packet could be invoked pointwise.  Summing
gives a zero left side because each physical potential value has coefficient
`2-2=0`, but a strictly positive right side.  Thus
`intersection_v A_v` is empty.  Consequently

```text
1 <= sum_v measure([0,1)^4 minus A_v),
```

and the deleted physical volume in that packet's support is at least
`42^-4`.  This argument does not say that a q=42 box has been deleted; the
deletion can be arbitrarily shaped and distributed among its boxes.  Since
all 92,610 support boxes across the 17,640 packets are genuinely disjoint
half-open boxes, these fractional lower bounds add:

```text
mu(U minus E) >= 17640/42^4,
mu(E) <= (280917-17640)/42^4 = 263277/42^4 < 49/576.
```

The normalization is exact: `280917/42^4 = 117/6^4`, and
`(49/576)*42^4 = 1058841/4`.  No rounded whole-box deletion budget is used in
the proof.

## Boundary and scope stress tests

- **Half-open faces:** The parameter domain and every q=42 box are explicitly
  half-open, so boxes are disjoint as sets.  Lower faces (`u_j=0`) are
  included and upper faces (`u_j=1`) are excluded consistently.  There is no
  unaccounted shared boundary volume.
- **Pointwise rather than a.e.:** essential.  An a.e. midpoint hypothesis
  cannot be substituted: the four-dimensional common-offset family can lie
  in an exceptional subset of the twelve-dimensional triple space.  This
  audit approves no almost-everywhere version.
- **Single-valued physical potential:** essential.  Cancellation evaluates
  the same `F(phi_v(u))` in every row.  A row/state-dependent or multivalued
  potential is outside scope.
- **Raw-canonical convention:** checked with the actual `[0,1)^4`
  representatives and nonzero modular carries.  Replacing the RHS by a
  wrapped/geodesic distance is a different statement.
- **No dilation/full-box premise:** the replay uses finite balanced midpoint
  packets only; it assumes neither a dilation relation nor that `E` is a
  microbox union.  The exact union-bound step is the reason proper measurable
  carving is covered.

## Reproducibility and immutable input hashes

Both commands passed with the same result; the candidate bytes were checked
before and after each replay.

```powershell
python -I D:\p42_scratch\erdos142_q42_carving_hostile_20260818\independent_q42_fractional_carving_replay.py --target D:\p42_scratch\erdos142_context_subtiles
wsl.exe python3 -I /mnt/d/p42_scratch/erdos142_q42_carving_hostile_20260818/independent_q42_fractional_carving_replay.py --target /mnt/d/p42_scratch/erdos142_context_subtiles
```

Candidate source SHA-256: `c543e7fd118981c530ad81a1dd0c4e105c5c1eca253aefd50c6c007c5a818fac`.

Candidate certificate SHA-256: `60d9d974aa23755615d159653508dbb38769fb0d883c974a4425e51b278119b4`.

Candidate README SHA-256: `9422cc398540a34feca2dfb75a768b818a9ab3c547dc53d09f062d3f493b9632`.

The audit is read-only with respect to `D:\p42_scratch\erdos142_context_subtiles`.

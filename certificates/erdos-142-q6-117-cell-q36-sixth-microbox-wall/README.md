# q=36 six-of-nine one-block microbox wall

This packet certifies an exact wall for a **single retained union** of
complete, globally aligned sixth-residual microboxes in the fixed 117-cell
q=6 alphabet.  It is not a word-language capacity theorem and does not solve
Erdos Problem 142.

## Exact theorem

Subdivide every residual coordinate of each coarse q=6 cell into six
half-open intervals.  The physical fine digit is

```text
d_j = 6*c_j + s_j,   s_j in {0,1,2,3,4,5}.
```

There are `117 * 6^4 = 151,632` distinct q=36 microboxes.  Let `U` be any
union of complete boxes.  If a bounded, single-valued physical potential on
`U` satisfies every actual pointwise raw-canonical modular-torus midpoint
inequality, then

```text
|U| <= 142,323 < 142,884
     = (49/576) * 36^4.
```

Thus this aligned one-block r=6 model cannot retain density strictly above
the four-coordinate EHPS product gate.

## Exact disjoint packing

The standalone verifier reconstructs two families.

1. The componentwise strict-dilation graph has 3,811 edges in 2,785
   components, each of size at most nine.  Exhaustive componentwise matching
   gives 2,986 disjoint pairs.  If both boxes in a pair survive, the two
   strict-interior rows at scales `t` and `3t` give, for `K >= 1` wrap
   coordinates,

   ```text
   D(3t) - D(t) >= K * (72 - 48t).
   ```

   Here the convention is explicit.  If `f` is the original bounded
   potential, set

   ```text
   G(p) = 36 * (f(p) - 2*||p||_2^2).
   ```

   For an oriented dilation edge, write `A_t` for its low-box point and
   `B_(1-t)` for its high-box point.  In an active coordinate with coarse
   digits `a_j` and `b_j=(a_j-1) mod 6`, these coordinates are
   `(a_j+t)/6` and `(b_j+1-t)/6`; inactive coordinates use the same fixed
   strict-interior value.  Define

   ```text
   D(t) = G(A_t) + G(B_(1-t)).
   ```

   Adding the inequalities for the physical midpoint rows
   `(A_t,B_(1-t),B_(1-3t))` and `(A_(3t),A_t,B_(1-t))` gives the displayed
   recurrence exactly.

   Taking `t=(1/12)/3^j` gives a finite telescope that contradicts any bound
   on `G` (and hence on the physical correction).

2. Fix the order-nine shift `(0,4)` in the last two q=36 coordinates.  The
   468-point last-pair prototype meets its ambient nine-point orbits with the
   exact histogram

   ```text
   intersection size:  1   2   3   4   5   6
   orbit count:        24  36  24  24  12  24.
   ```

   The 24 six-of-nine intersections have the explicit form

   ```text
   P_k = (u, r + 4k),  k=0,...,5,
   u in {30,...,35}, r in {0,1,2,3}.
   ```

   Each is a six-row balanced packet.  In cyclic packet order the rows are

   ```text
   (P4,P0,P5), (P0,P1,P2), (P1,P2,P3),
   (P2,P3,P4), (P3,P4,P5), (P0,P5,P1),
   ```

   where each tuple is `(endpoint, centre, endpoint)`.  Every row is an exact
   nondegenerate midpoint modulo 36.  Across the six rows, every point has
   endpoint coefficient `+2` and centre coefficient `-2`; hence an arbitrary
   physical potential cancels with unit weights, while the aggregate raw
   endpoint-square cost is strictly positive.

The 24 prototype packets lift to 24 packets in each of the 324 fixed-first-
pair fibers, or 7,776 before reserving the dilation endpoints.  Exactly 1,453
packets meet the canonical matching endpoints.  Removing those leaves 6,323
six-point packets.  Their supports are mutually disjoint and avoid all 2,986
dilation pairs.

Therefore every feasible one-block support must make at least

```text
2,986 + 6,323 = 9,309
```

deletions.  Strictly above the gate permits only 8,747 deletions.  The
packing clears the required 8,748-obstruction threshold by 561 and leaves at
most 142,323 boxes, which is 561 boxes below the gate.

For every finite packet the replay also uses one common strict-interior
offset `u=(1/7,2/7,3/7,4/7)`.  This checks the physical, rather than merely
digit, midpoint identities: the common offset cancels from both the torus
defect and the endpoint difference.  The replay records all exact q=36
carries and raw endpoint-square costs.

## Frozen semantics and replay

`frozen_semantic_certificate.json` fixes the geometry, matching algorithm,
six-of-nine rule, row semantics, exact counts, gate, scope, and canonical
semantic digests.  The primary `verify_r6_six_of_nine_packing.py` replay is
corroborating.  The separately written `independent_r6_replay.py` is the
claim-certifying replay: it uses a distinct bitmask matching algorithm and
directly reconstructs the exact physical dilation and packet rows.  Neither
replay imports a producer, discovery script, solver, or third-party package.
Together they reconstruct all 151,632 physical boxes, the exact componentwise
maximum matching, all 6,323 packet supports and 37,938 physical rows, verify
carries, raw costs and coefficient cancellation, check cross-family
disjointness and exact density arithmetic, and reject planted failures.

From the repository root, native Windows:

```powershell
python -I certificates\erdos-142-q6-117-cell-q36-sixth-microbox-wall\verify_r6_six_of_nine_packing.py --self-test
python -I certificates\erdos-142-q6-117-cell-q36-sixth-microbox-wall\independent_r6_replay.py --target certificates\erdos-142-q6-117-cell-q36-sixth-microbox-wall
```

From the repository root, Linux/WSL:

```text
python3 -I certificates/erdos-142-q6-117-cell-q36-sixth-microbox-wall/verify_r6_six_of_nine_packing.py --self-test
python3 -I certificates/erdos-142-q6-117-cell-q36-sixth-microbox-wall/independent_r6_replay.py --target certificates/erdos-142-q6-117-cell-q36-sixth-microbox-wall
```

The primary replay prints `PASS_R6_SIX_OF_NINE_ONE_BLOCK_PACKING_WALL` and
`FROZEN_CERTIFICATE_NONMUTATION_OK`; the independent replay prints
`PASS_INDEPENDENT_R6_Q36_ONE_BLOCK_WALL`.

Canonical hashes are:

```text
dilation semantic:
d520ceaf418068665a166617e747da23b970d701c71de1cf13b5eac8d368bff1

packet supports:
36c478be01b818a32980563b193ae2290e9db41048f6a2e757d77609cb0dd243

expanded packet semantics:
e8ae9b924fa16076ecf9a117f8a210c665bca1bc1c01d7490f3c7f97a90b5bfc

payload semantics:
9aa110472ac2da97d919e30fea2cfdee1b308c2f743bca4b70d67781f819f544

frozen certificate bytes:
318bb7ac5cb3bac2dba1b10815c47d0997bf95c8b88f8dfd5d2da1f7a6720d5d
```

## Scope

Proved:

- exact q=36 geometry, dilation recurrence, six-point midpoint semantics,
  pairwise-disjoint packing, and density arithmetic;
- arbitrary bounded single-valued physical potentials on one complete
  aligned microbox union;
- actual strict-interior raw-canonical modular-torus midpoint inequalities.

Not proved:

- an all-horizon, graph-directed, or arbitrary word-language capacity bound;
- proper carving inside a q=36 microbox, finer or non-axis-aligned pieces,
  deformations, overlaps, almost-everywhere coercivity, or unbounded
  corrections;
- an EHPS shell construction above the gate, integer transfer, or an improved
  lower bound for `r_3(N)`.

# q=6 coordinate-dependent D4 product-capacity wall

This certificate closes the full-product version of the most recent correlated
D4 escape lane.  Each label may choose an arbitrary word of D4 images, and the
word may vary from coordinate to coordinate.  The only retained restriction is
that a labelled block is the complete Cartesian product of its local images.

Replay with only the Python standard library:

```text
python -I verify.py --self-test
python -I independent_replay.py
```

The two programs are separately written and reconstruct the exact q=6 support,
all eight D4 images, all midpoint rows, carries, raw costs, and the quantitative
gate.  Neither imports a sibling certificate, a discovery artifact, or an LP
solver.

## Local torsion lemma

Let

```text
S = {(3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2)}
```

in `(Z/6Z)^2`, and let `S_g`, `g=0,...,7`, be its images under the two
coordinate reflections and coordinate swap.  Call `(x,y,z)` cyclic when all
three modular midpoint equations hold:

```text
x + z = 2y,
y + z = 2x,
x + y = 2z                 (mod 6).
```

Equivalently, `y=x+d`, `z=x+2d` with `3d=0`.  Exact enumeration gives 324
ordered cyclic triples, including the zero-step triples.  Across all `8^3`
ordered D4 buckets, the total bucket sizes lie between 4 and 9.  The
nondegenerate claim used by the theorem is narrower and stronger in the needed
direction:

```text
for every g != h, S_g x S_g x S_h contains a nondegenerate cyclic triple.
```

All 56 ordered unequal pairs pass.  Their nondegenerate witness counts are 2
for 24 pairs, 4 for 16 pairs, and 6 for 16 pairs.  The certificate does not
claim that every one of the 512 general buckets has a nondegenerate member.

## Arbitrary-length product theorem

For a D4 word `a=(a_1,...,a_L)`, put

```text
B_a = S_(a_1) x ... x S_(a_L).
```

Take two distinct words `a` and `b`.  At each coordinate where they differ,
choose the certified nondegenerate cyclic triple in
`S_(a_i) x S_(a_i) x S_(b_i)`.  At every unchanged coordinate, use a diagonal
zero-step anchor.  Tensoring these choices produces physical points

```text
X,Y in B_a,    Z in B_b,
```

which form a nondegenerate cyclic triple in `(Z/6Z)^(2L)`.  The three EHPS
coercivity rows have coefficients

```text
(+1,-2,+1), (-2,+1,+1), (+1,+1,-2)
```

on the same physical vertices `(X,Y,Z)`.  Their sum cancels every value of one
arbitrary, nonseparable potential, while the sum of the raw canonical endpoint
costs is positive.  Thus no union containing two distinct D4 product words can
carry an EHPS coercive potential.

This is a physical-vertex argument.  Re-labelling the same point or block does
not create a second potential variable or additional mass.

## Capacity consequence

One length-`L` block has normalized mass

```text
(9/36)^L = (1/4)^L < (7/24)^L.
```

Consequently, a potential-compatible code has at most one distinct product
word, and that singleton misses the supplied EHPS mass gate.  The wall applies
for every positive `L`, including arbitrary coordinate-dependent D4 words.  In
particular, it retires the six-coordinate chain candidate
`000000,111100,110011,001111,010101` before any potential ansatz is considered.

The primary replay includes a concrete length-six packet with normalized
contradiction `8/3` and rejects planted changes to a local witness, midpoint,
carry, raw cost, physical/label identity, differing coordinate, and mass gate.
The independent replay uses a different basepoint-plus-torsion-increment
enumeration and a different length-six example.

## Boundary

This is an exact finite q=6 theorem for full Cartesian products of the stated
nine-point D4 images.  It does **not** rule out correlated non-product
subblocks, graph/height lifts, deformed supports, higher quotients, continuum
thickening, or scalar digit encodings.  It supplies no new `r_3(N)` lower bound
and does not solve Erdos Problem 142.

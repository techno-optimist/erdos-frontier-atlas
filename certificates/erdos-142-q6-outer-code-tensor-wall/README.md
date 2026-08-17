# q=6 outer-code tensor wall

This packet certifies an exact closure theorem for the finite Cartesian-product
extension of the q=6 all-pattern lane.  It is a wall for the whole outer-code
ansatz, not merely a bound on its density.

Run, from this directory,

```text
python -I verify.py
```

The replay is stdlib-only and uses integer and `Fraction` arithmetic.  It does
not import a discovery table, solver output, or any sibling certificate.

## Setup

Let `G=(Z/6Z)^6`, represented canonically by coordinates in `{0,...,5}`.  In
each outer coordinate `i`, choose one of the 256 audited maximum-mass q=6 D4
role assignments.  The choice may depend arbitrarily on `i`, but is fixed
across all outer codewords in that coordinate.  Its five local cylinders are
labelled

```text
0=(P1,K,B), 1=(B,K,P1), 2=(P2,B,P2),
3=(P3,B,B), 4=(B,B,P3).
```

For a word `u=(u_1,...,u_L)` in `{0,...,4}^L`, write

```text
B_u = S_{1,u_1} x ... x S_{L,u_L}  subset G^L.
```

Given an outer code `C`, the proposed support is the full superblock union
`S_C = union_{u in C} B_u`.  A potential is one arbitrary function `H` on the
physical points of `S_C`; it need not be additive, separable, bounded,
continuous, polynomial, or given by the same formula in different blocks.

The coercive row convention audited here is

```text
H(U) + H(W) - 2 H(V) >= ||U-W||^2_raw
```

whenever `U+W = 2V (mod 6)` coordinatewise.  The squared norm uses canonical
representatives and is additive over Cartesian q=6 blocks.  Division by
`6^2=36` gives the normalized convention and does not affect infeasibility.

## Theorem: every nonconstant outer triple is obstructed

For every maximum assignment and every non-diagonal ordered local pattern
`(a,b,c)`, the exact q=6 table supplies local vertices `(x,y,z)` in cylinders
`(a,b,c)` such that all three rows

```text
(x,y,z), (y,x,z), (x,z,y)
```

satisfy their modular midpoint equations.  Their three raw endpoint costs have
positive sum.  Exhaustion over all 256 maximum assignments and all 120
non-diagonal patterns strengthens this to the uniform exact floor

```text
||x-z||^2 + ||y-z||^2 + ||x-y||^2 >= 24,
```

or `2/3` after division by 36.

Now take any ordered outer-word triple `(u,v,w)` that is not globally
constant.  At coordinate `i`:

- if `(u_i,v_i,w_i)` is non-diagonal, choose its positive local cycle;
- if `u_i=v_i=w_i`, choose a point of that cylinder and use the constant
  zero-cost triple.

Concatenate the local vertices to form three *global* points

```text
X=(x_1,...,x_L), Y=(y_1,...,y_L), Z=(z_1,...,z_L).
```

Then `X in B_u`, `Y in B_v`, and `Z in B_w`.  Local carries concatenate, so
the following are genuine midpoint rows in `G^L`:

```text
H(X)+H(Z)-2H(Y) >= ||X-Z||^2
H(Y)+H(Z)-2H(X) >= ||Y-Z||^2
H(X)+H(Y)-2H(Z) >= ||X-Y||^2.
```

Their left sides cancel at the full-superblock variable level.  Their right
sides add across coordinates.  If

```text
D = {i : (u_i,v_i,w_i) is non-diagonal},
```

the sum is at least `24|D|` raw, or `2|D|/3` normalized.  Thus the three rows
give the exact contradiction

```text
0 >= a positive number.
```

This is not a tensor product of local potential inequalities and does not
assume `H(X)=sum_i h_i(x_i)`.  It synchronizes three global vertices and then
cancels the three values of one arbitrary global function.

## Corollary: every outer code with at least two words dies

If `C` contains distinct words `u` and `v`, apply the theorem to `(u,v,v)`.
The non-diagonal-coordinate set is exactly the Hamming difference set of
`u,v`, so

```text
normalized contradiction >= (2/3) d_H(u,v) > 0.
```

Therefore an arbitrary-potential survivor in this product class has
`|C| <= 1`.

The replay also proves that every maximum assignment has five pairwise
disjoint physical cylinders: their sizes are 729 each and their union has
mass `3645=5*729`.  Hence distinct outer words index disjoint product blocks.
All coefficient accounting uses the complete physical superblock vertex,
never a coordinate projection or a cylinder-occurrence label.

## Singleton side of the dichotomy

One q=6 cylinder has exact density

```text
729 / 6^6 = 1/64.
```

The candidate EHPS mass gate supplied to this lane is `(7/24)^3`.  Exact
cross-multiplication gives

```text
1/64 = 216/13824 < 343/13824 = (7/24)^3.
```

Consequently a singleton length-`L` product has density `(1/64)^L`, strictly
below `((7/24)^3)^L` for every integer `L>=1`.  An empty code has density zero.
Combining this with the obstruction above, no outer code in this exact class
can both admit the required arbitrary global potential and pass the candidate
mass gate.

The gate itself is an external input from the home capacity lane.  This packet
certifies the exact density comparison, not a re-derivation of that external
criterion.

## Exact replay coverage

`verify.py` independently performs all of the following:

- enumerates all `8^5=32768` q=6 D4 role assignments with physical bitsets;
- recovers maximum union mass 3645 and exactly 256 maximizers;
- checks pairwise disjointness of all five cylinders for every maximizer;
- reconstructs all 324 common point-level three-torsion triples;
- checks `256*120=30720` positive local pattern cycles;
- checks the minimum and maximum raw three-row sums, 24 and 144;
- checks a length-parametric tensor constructor with assignments varying by
  outer coordinate, full carries, raw-cost additivity, memberships, and exact
  global-variable coefficient cancellation;
- checks the singleton density inequality in exact `Fraction` arithmetic.

Nine planted failures are rejected: wrong midpoint, wrong carry, wrong raw
cost, coordinate-projection identity fraud, occurrence-label aliasing, equal
codewords, a nonmaximum coordinate, removal of the maximum-assignment premise,
and reversal of the singleton mass gate.  The explicit overbreadth control is
assignment `(0,0,0,0,0)`: its union mass is only 729, and pattern `(0,1,1)`
has no positive local cycle.  Thus “all q=6 assignments tensorize” is false.

## Honest boundary

This theorem covers finite Cartesian products of the exact q=6 maximum-mass
D4 cylinders, with one maximum assignment fixed per outer coordinate.  It does
not cover:

- nonmaximum assignments or arbitrary geometric deformations of the supports;
- cell thickening or a continuum limit of these boundary-grid witnesses;
- an assignment that changes with the codeword rather than only with the
  outer coordinate;
- correlated subblocks that are not full products of the five cylinders;
- scalar digit encoding, where cross-block carries require a new audit;
- the recursive construction-to-integers transfer.

Arbitrary deformation or coordinate coupling of the *potential values* is
already covered, because the proof treats `H` as a completely unrestricted
single function on the union.  Deformation of the geometric supports is not.

No new bound for `r_3(N)` is claimed, and this packet does not solve Erdős
Problem 142.  It closes the exact finite-q6 full-product outer-code route.

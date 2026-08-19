# Independent q=9 cap wall and the h=7 common-marker bound

## Exact finite theorem

Let `S` be a subset of `Z_9^2`.  Partition it into the nine fibres of
reduction modulo 3.  Suppose every fibre is a four-point cap in `AG(2,3)`.
Then `|S|=36`, but `S` contains a six-point positive Farkas packet.  Therefore
there is no function `H:S->R` satisfying

```text
H(x)+H(z)-2H(y) >= d_T(x,z)^2
```

on every nontrivial q=9 torus-midpoint triple.  Consequently any support
carrying such a potential and meeting every mod-3 fibre in at most a cap has
at most 35 points.

The proof is solver-independent.  It reconstructs the same 2,916 six-point
line supports as the singular-pushforward route, but uses a smaller direct
six-row packet and a `18>12` incidence cover instead of a large CSP search.

## 1. The six-row scalar packet

On `{0,1,2,3,4,5}` in `Z_9`, take the six unit-weight rows

```text
(4,0,5)
(0,1,2)
(1,2,3)
(2,3,4)
(3,4,5)
(0,5,1).
```

Here `(x,y,z)` means `x+z=2y mod 9`.  Every potential coefficient cancels,
and the sum of one-dimensional torus-geodesic squared costs is 18.  The
`AGL(1,Z_9)` orbit of this support consists of exactly the 27 subsets having
two elements in each residue class modulo 3.

There are 72 primitive vectors in `Z_9^2`.  Quotienting their six generator
choices and the nine points on a line gives 12 primitive directions and 108
primitive affine lines.  Embedding each of the 27 scalar supports along every
line produces 2,916 distinct six-point supports, each with two points in each
of the three coarse fibres met by the line.  The six rows remain strict
midpoint rows, so every support is a positive Farkas wall.

## 2. Exact lift/carry lemma

Fix a coarse affine line in `AG(2,3)`, orient it as `r_j=r_0+j*d`, and let
`n` be a nonzero linear functional whose kernel is the direction `d`.  A
primitive q=9 lift meets the three coarse fibres in local lines parallel to
`d`.  Write their three quotient offsets as `c_0,c_1,c_2` in `F_3`.

The nine primitive lifts of the fixed coarse line give exactly one affine
plane

```text
c_0+c_1+c_2 = K
```

for a carry-dependent constant `K`.  This is checked directly for all 12
coarse lines and all 108 q=9 lines.

For arbitrary values `b_0,b_1,b_2`, require `c_j=b_j` at a diameter position
and `c_j!=b_j` at a rich position.  Put `e_j=c_j-b_j`.  Diameter positions
force `e_j=0`; rich positions permit `e_j=+1` or `-1`.  If at least two of the
three positions are rich, the permitted sums of the `e_j` are all of `F_3`.
Hence some allowed triple lies in every plane `sum c_j=K`.  The replay
exhausts all constants, centre offsets, and two-/three-rich patterns.  It also
confirms that one rich position is insufficient, so the threshold is sharp.

## 3. The `18>12` cover

Every four-cap `C` in `AG(2,3)` has a unique centre `a` and can be written

```text
C = {a+u,a-u,a+v,a-v}
```

for two distinct projective directions `u,v`.  In either diameter direction,
only the local line through `a` is a secant.  In each of the other two, or
**rich**, directions, the two local lines not through `a` are secants.  Thus
every cap is rich in exactly two of the four projective directions.

If a 36-selector avoided every six-point packet, the lift lemma would force
each coarse line in direction `d` to contain at most one cap rich in `d`.
There are three parallel coarse lines in each of four directions, so an
avoider could have at most

```text
4*3 = 12
```

rich incidences.  The nine caps actually contribute

```text
9*2 = 18.
```

This contradiction covers all `54^9` cap assignments without symmetry
normalization, floating-point optimization, or trust in an external solver.

## 4. Continuum normalization

In an `H_9^2` orbit of a marker slice, the nine mod-3 fibres are precisely its
nine `H_3^2` subfibres.  Order-three line-freeness gives at most four selected
points per subfibre.  If all nine were saturated, the selected q=9 indices
would be a forbidden 36-selector.  Hence every orbit contains at most 35 of
its 81 points, and the slice density is at most `35/81`.

The triangular exceptional set has measure `1/72`.  Applying the slice bound
in either coordinate and using a union bound gives

```text
2*(1/72)*(35/81) = 35/2916.
```

For the thin strip of measure

```text
sigma = 4*epsilon/3 - 2*epsilon^2,
```

a surviving common marker therefore satisfies the safe bound

```text
beta <= 35/2916 + 2*sigma.
```

The exact h=7 product gap is

```text
(7/24-epsilon)^2 - 7*beta
 >= (1353024*epsilon^2 - 898128*epsilon + 49)/46656.
```

The polynomial is decreasing on `[0,1/20000]`, and at the right endpoint its
value is

```text
25606141/291600000000 > 0.
```

Thus the common-marker h=7 lane is closed for
`0 <= epsilon <= 1/20000`.  Using the exact strip union
`2*sigma-sigma^2` gives a slightly stronger but less tidy bound.

## 5. Scope and replay

This proves the finite q=9 cap wall, the `35/2916` triangular normalization,
and the stated h=7 common-marker interval.  It does not address arbitrary
phase-specific markers, h=8, the full graph/reuse escape, or solve Erdos
Problem 142.

From the repository root on Windows:

```powershell
python -I certificates\erdos-142-ehps-common-marker-cap-wall\h7-q9-cap-wall\independent_replay.py
```

Linux or WSL:

```text
python3 -I certificates/erdos-142-ehps-common-marker-cap-wall/h7-q9-cap-wall/independent_replay.py
```

The success marker is `PASS_Q9_H7_CAP_WALL_INDEPENDENT`.

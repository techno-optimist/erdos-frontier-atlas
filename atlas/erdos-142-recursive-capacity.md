# Erdős 142: recursive signed-slack capacity lane

**Claim boundary:** `erdos142_solved: false`; `new_r3_bound: false`;
`continuum_certificate: false`; `finite_survivor: false`;
`finite_additive_wall: true` (one precisely scoped q=24 family).

This is a research-lane note, not a certificate. It records a newly recovered
primary source, isolates the exact conditional tensorization lemma relevant to
the EHPS torus construction, and specifies the next finite experiment. Nothing
here changes the status of P142 or any row in the attack graph.

## 1. What is new in this note

Eric Naslund's public 2023 slide deck gives substantially more information than
the manuscript citations that were previously easy to find:

- [author talks page](https://sites.google.com/site/naslunderic/talks-and-conferences);
- [80-page slide deck](https://drive.google.com/file/d/1pW4FreiLm6DV9CHg3FBpGCtfjRr7ZYdp/view?usp=drive_link);
- [OeMG 2023 program and abstract](https://imsc.uni-graz.at/oemg-tagung-2023/wp-content/uploads/2023/09/mprogramm.pdf).

The deck downloaded on 2026-08-17 has SHA256
`3868245c39118299e4b1c291757209d0a9a334278f8d0decad82041142dfd549`,
80 pages, and PDF creation time 2023-09-18 06:50:50 MDT. The following items
were checked against rendered pages, not search snippets.

1. Slides 45--49 define the constructor hypergraph `L_k` on
   `{0,1,...,k}` and state Edel's conjecture `Theta(L_k)=2` for `k >= 2`.
2. Slides 53--58 state `Theta(C) >= 2.22` for capsets via a limiting
   construction, not a product of one finite example, and state
   `Theta(L_k)=2` for `k >= 3`.
3. Slides 64--71 display the recursive gadget inside the strong square
   `L_3 x L_3`:

   ```text
   H0 = {(0,0)}
   H1 = {(0,1),(2,0),(2,3),(3,2),(1,1)}
   H2 = {(0,2),(3,0),(1,3),(3,1),(2,2)}
   H3 = {(0,3),(1,0),(2,1),(1,2),(3,3)}.
   ```

   The slides state that `H1,H2,H3` are weighted copies of `L_3`, with
   weight 2 at vertex 0, while the four pieces together form another copy of
   `L_3`. The point is a nested reusable decomposition, not a one-shot larger
   independent set.
4. Slides 72--75 give the optimization closure. If `(x1,y1)` and `(x2,y2)`
   lie in a feasible set `S`, then so does

   ```text
   (x1 + x2/2 - x1*x2/2,
    y1^(1/2) * y2^((1-x1)/2) * 2^(x2*(1-x1)/2)).
   ```

   Together with `(x,1) in S`, the stated envelope is
   `g(x)=x^(-x)(1-x)^(-(1-x))`.
5. Slides 76--79 summarize the general mechanism: build chains of copies in
   high powers; a closed recursive loop yields a capacity lower bound.

This is the mechanism-level clue for P142: search for a recursively reusable
**weighted coercivity gadget**, rather than only a larger isolated torus tile.

### Source-status fence

The public deck states only the rounded capset value `2.22`. EHPS report that
Naslund informed them of forthcoming work giving `2.2208^(n-o(n))` in
`F_3^n`; later surveys repeat that attribution. Naslund's
[research page](https://sites.google.com/site/naslunderic/research) currently
lists *Lower Bounds for the Capacity of Hypergraphs* as "In preparation" and
provides no paper or code. No public manuscript, proof, repository, or recording
for the `2.2208` claim was located through 2026-08-17. Therefore:

```text
public recursive mechanism: verified in the author's deck
public rounded 2.22 statement: verified in the author's deck
public proof of 2.2208: not located
2.2208 status here: attributed announcement, not a replayed theorem
```

The directly machine-searchable published comparison is the combinatorial
degeneration theorem of
[Christandl--Fawzi--Hoang Ta--Zuiddam](https://arxiv.org/abs/2111.08262):
a degeneration of a directed hypergraph to `s` diagonal states in a `d`-fold
power certifies a capacity lower bound `s^(1/d)`. That theorem concerns an
independence hypergraph. EHPS needs a stronger signed coercivity inequality, so
it is a model for certificate design, not a drop-in transfer.

## 2. Direct outer-code coercivity lemma

Let `R` be a finite role set. For every `r in R`, let
`A_r subset [0,1)^2` be measurable and let `f_r` be a bounded real-valued
function on `A_r`. Use the canonical representatives in `[0,1)^2`; the
endpoint cost below is the **raw** Euclidean difference, as in EHPS
Proposition 2.2, not the shortest flat-torus distance.

For an ordered role triple `(r,s,t)`, define

```text
d(r,s,t) = inf [f_r(x)+f_t(z)-2f_s(y)-||x-z||_2^2],
```

where the infimum ranges over all
`x in A_r, y in A_s, z in A_t` satisfying
`x+z == 2y (mod 1)`. Equivalently, with canonical representatives,
`x+z-2y=kappa` for one of the finitely many local carry vectors
`kappa in Z^2`. Set the infimum of an empty witness set to `+infinity`.

For a length-`L` role word `u`, put

```text
A_u = product_i A_{u_i},
F_u(X) = sum_i f_{u_i}(X_i).
```

Let `C subset R^L`. Assume the cylinders `A_u`, `u in C`, are setwise
disjoint, or that the formulas `F_u` agree at every overlap, so that there is
one pointwise potential `F` on their union. If

```text
sum_i d(u_i,v_i,w_i) >= 0
```

for every **ordered** `(u,v,w) in C^3`, including `u=v=w`, then every
modular midpoint triple `X,Y,Z` in the union satisfies

```text
F(X)+F(Z)-2F(Y) >= ||X-Z||_2^2.
```

**Proof.** A global modular midpoint triple is a modular midpoint triple in
each physical two-dimensional coordinate block. Its slack is the sum of the
local slacks. Each local slack is at least the corresponding `d`, and the
assumed code inequality makes their sum nonnegative. The raw squared norm is
additive across the physical blocks. QED.

Three audit consequences matter for implementation:

- There is no cross-block carry automaton at the torus stage. Local
  `kappa in Z^2` states must be exhaustive, but the `L` physical blocks
  factor. Inter-block carries arise only in a later scalar digit encoding.
- There is no "some coordinate is nontrivial" shortcut. EHPS Proposition 2.2
  quantifies over every modular midpoint triple, including `X=Z != Y`.
- A flat-torus-distance certificate is weaker and does not establish the raw
  representative inequality used by EHPS.

This lemma proves only the superblock coercivity implication. A construction
must still supply a bounded single potential, exact union mass, a continuum
cell proof, and the EHPS superblock-to-integer transfer.

## 3. The quantitative gate

Write `theta=7/24`. If the product cylinders are disjoint, their normalized
`2L`-dimensional mass is

```text
Lambda_C = sum_{u in C} product_i alpha_{u_i},
alpha_r = measure(A_r).
```

With overlaps, `Lambda_C` must be replaced by a certified lower bound for the
actual union mass. The only relevant improvement test is

```text
measure(union_{u in C} A_u) > theta^L.
```

Equivalently, the effective two-dimensional base is the `L`-th root of that
union mass and must exceed `7/24`. Comparing a cardinality exponent or a ratio
of logarithms directly with `7/24` is dimensionally wrong.

For a common `q`-grid with `w_r` occupied cells, use
`alpha_r=w_r/q^2`. If the realized label images are disjoint, the finite
screen is

```text
sum_{u in C} product_i (w_{u_i}/q^2) > (7/24)^L.
```

A grid survivor is discovery evidence only. Positive-area promotion requires
an exact rational cell/thickening certificate whose slack margin dominates
rounding and boundary errors.

## 4. First exact experiment: the five-word code

Karapetyan--Karapetyan's 2026 ternary cap construction supplies a new finite
label architecture:

```text
C_KK = {(P1,K,B), (B,K,P1), (P2,B,P2), (P3,B,B), (B,B,P3)}.
```

Its published proof uses literal zero-coordinate fibres in characteristic 3;
those fibres have Haar measure zero, so the proof does **not** transfer to the
EHPS torus. The five words are used only as a search ansatz.

Run the following once, with all five supports and potentials globally free:

1. Work on `Gamma_q=(Z/qZ)^2`, first `q=24`, then `q=48`.
2. Enumerate every ordered local role triple and every local modular midpoint
   witness, retaining the canonical raw endpoint cost and all local carries.
3. For each ordered triple of the five codewords, minimize the sum of its three
   local slacks. Because the torus product factorizes, this is three local
   pricing calls, not enumeration of all `q^6` points.
4. Use CEGAR: add the exact violated witness row to the LP/MILP, and iterate to
   infeasibility or a fully priced solution.
5. Accept only if the **actual union mass** exceeds `(7/24)^3`.
6. Recheck on an eroded core and at `q=48`. Any one-cell, boundary-only, or
   overlap-only gain is rejected.
7. A survivor advances to exact rational polygons and a continuum inequality
   certificate. It does not advance directly to an `r_3(N)` claim.

The same pricing data define a more general finite signed-slack code search:
find `C subset R^L` of maximum weighted mass subject to
`sum_i d(u_i,v_i,w_i)>=0` for every ordered codeword triple. Naslund's clue is
to go one step further and search for a **closed recursive composition loop**
of such weighted slack states, rather than stopping at one finite `L`.

### 4.1 Executed branch: the mirror-exclusive additive wall

The first nontrivial q=24 target used the published EHPS grid tile `T` and its
coordinate transpose `Tt`. Exact enumeration gives

```text
|T| = |Tt| = 163
|T intersect Tt| = 53
|T without Tt| = |Tt without T| = 110.
```

Retain only the two words

```text
(P3,B,B), (B,B,P3).
```

Assign the two 110-point exclusive cores to `B` and `P3`, in either role
orientation, and distribute the 53 intersection points disjointly. If `k`
intersection points go to `B`, the exact two-cylinder mass is

```text
2 (110+k)^2 (163-k) / 24^6.
```

This exceeds `(7/24)^3` exactly for `18 <= k <= 53`, so the family contains
many genuine finite mass targets. A preliminary sweep tested 199 structured
and deterministic-random allocations, all LP-infeasible. The decisive upgrade
is that sampling is unnecessary: the exclusive 110+110 core alone is already
infeasible for an additive role potential. Adding any subset of intersection
points preserves every core constraint and therefore cannot restore
feasibility.

The exact replay is in
`certificates/erdos-142-mirror-core-additive-wall/`:

- 177 Farkas rows for `B=T without Tt`, `P3=Tt without T`;
- 174 rows for the reversed orientation;
- exact positive integer multipliers cancel every role-point potential
  coefficient and leave a strictly positive raw endpoint cost;
- the stdlib verifier reconstructs the support, midpoint carries and raw
  costs, checks the mass-passing allocation range, and runs four planted
  failures.

This proves a useful but narrow wall. It excludes the **additive local-role
potential** on these two product cylinders at q=24. It does not exclude an
arbitrary global potential on the six-dimensional union, a recursive state
potential, or jointly deformed supports that do not contain the exclusive
cores. It gives no continuum certificate and no new `r_3(N)` bound.

### 4.2 Executed branch: the top-D4 role-distinct additive wall

The next screen assigned each of the five roles one of the eight exact
dihedral images of the q=24 EHPS tile. All `8^5=32,768` role assignments were
enumerated with the actual five-cylinder union mass. The maximum is attained
at, among symmetrically related choices,

```text
(P1,P2,P3,B,K) = (D4[7],D4[7],D4[7],D4[6],D4[7]).
```

Here `D4[6]` and `D4[7]` are disjoint 163-point supports. Consequently the
five Karapetyan cylinders are pairwise disjoint and have exact union count

```text
5 * 163^3 = 21,653,735 > 4,741,632 = (7/24)^3 * 24^6.
```

This large mass does not survive the additive coercivity test even when every
role gets its own potential values. There are 815 role-point variables. An
exact Farkas certificate selects 622 valid rows from the all-ordered-triples
CEGAR system, assigns them positive integer multipliers, cancels every one of
the 815 coefficients, and leaves a strictly positive summed raw endpoint
cost. The semantic replay in
`certificates/erdos-142-d4-role-distinct-additive-wall/` reconstructs every
EHPS/D4 support point, word triple, modular midpoint, even-q carry, raw cost,
coefficient and inclusion-exclusion mass term. Six planted corruptions and a
separately written replay audit the result.

This closes exactly one highest-mass D4 assignment under a sum of
role-local potentials. It does not exclude an arbitrary potential on the
full six-dimensional union, a recursive state potential, other D4 assignments,
joint support deformations, q=48, or a continuum construction. No new
`r_3(N)` bound follows.

### 4.3 Stronger wall: cylinder-position additive potentials

The same top-D4 assignment remains impossible after substantially relaxing
the additive ansatz. Since its five cylinders are pairwise disjoint, give
every cylinder `c`, coordinate position `i`, and local support point `p` an
independent variable `G[c,i,p]`, and set

```text
F_c(p0,p1,p2) = G[c,0,p0] + G[c,1,p1] + G[c,2,p2].
```

This has `5*3*163 = 2,445` variables and strictly contains the role-distinct
model: no value is shared merely because two occurrences carry the same role.
For each ordered cylinder triple `tau` and position `i`, introduce a local
hypograph variable `t[tau,i]`. After scaling by `q^2`, the exact rows are

```text
t[tau,i] - Gx - Gz + 2 Gy <= -raw_cost_numerator,
-t[tau,0] - t[tau,1] - t[tau,2] <= 0.
```

The reformulation loses nothing. The first rows bound `t[tau,i]` above by
every local witness slack, so its largest feasible value is the local minimum.
The sum row is therefore feasible exactly when the three local minima sum to
a nonnegative global slack. This replaces product-sized global cuts by 375
local witness tables while retaining every ordered triple and even-`q`
midpoint branch.

The semantic packet in
`certificates/erdos-142-q24-cylinder-hypograph-wall/` gives an exact
Farkas contradiction for this 2,820-variable system. It contains 662 selected
local rows, all 125 triple-sum rows, and 771 positive multipliers. Their exact
sum cancels all `G` and `t` coefficients and leaves a strictly negative right
side. The verifier reconstructs every support, witness, carry, raw cost,
index, and mass term, rejects ten planted corruptions, and has a separately
written independent replay.

This is a stronger finite wall, not a global one. It still permits nonlinear
interactions between two or three physical coordinates inside a cylinder,
arbitrary six-dimensional potentials, recursive state, support deformation,
and continuum thickening. The second inequivalent maximum-mass D4 orbit is
handled separately below. It gives no new `r_3(N)` bound.

### 4.4 Second maximum-mass D4 orbit

The exact `8^5` D4 mass census has 16 maximizers. The word automorphism and
global-D4 actions split them into two disjoint eight-member orbits, represented
by

```text
(7,7,7,6,7) and (7,6,7,6,7).
```

The second representative has the same exact union mass `21,653,735`. A fresh
local-hypograph CEGAR master selected an exact dual support for its 2,820-variable
cylinder-position additive system. The compact semantic packet in
`certificates/erdos-142-q24-second-orbit-cylinder-hypograph-wall/` contains 816
selected local rows, all 125 ordered triple-sum rows, and 931 positive integer
multipliers. They cancel every `G` and `t` coefficient and leave a strictly
negative exact right side. The stdlib verifier reconstructs the EHPS tile, all
D4 images, the cylinder mass, every witness/carry/raw cost, the complete
maximum-mass census, and eight planted corruptions; a separately written replay
reconstructs the cancellation independently.

The two exact orbit certificates therefore exclude all 16 maximum-mass D4
assignments under cylinder-position additivity. This remains a finite `q=24`
ansatz wall. Pair-coordinate potentials, arbitrary functions on six-dimensional
cylinder vertices, recursive state, support deformation, and continuum transfer
remain live escape routes at q=24. The coarser q=6 arbitrary-global result for
the two named representatives is handled separately in Section 4.6; it does
not transfer this q=24 statement.

### 4.5 Pair-coordinate interactions at q=6

Cylinder-position additivity still forbids interactions between physical
coordinates. The next model gives each cylinder three independent tables and
sets

```text
F_c(p0,p1,p2)
  = H[c,01,p0,p1] + H[c,02,p0,p2] + H[c,12,p1,p2].
```

At q=6 the EHPS tile and each D4 image have 9 points, so this model has
`5*3*9^2=1,215` variables. For both named representatives `(7,7,7,6,7)` and
`(7,6,7,6,7)`, the five cylinders are pairwise disjoint and have union count
`5*9^3=3,645`. Their normalized mass is `5/64`, exceeding `(7/24)^3` by the
exact ratio `1080/343`.

The full pricing oracle retained all 125 ordered cylinder triples, all even-q
midpoint branches, and the raw canonical endpoint cost. Exact Farkas packets
in `certificates/erdos-142-q6-pair-coordinate-walls/` select 1,067 rows for the
first representative and 1,071 for the second. In each packet, positive integer
multipliers cancel all 1,215 pair-table coefficients and leave a strictly
positive right side. The stdlib verifier reconstructs every selected global
witness and rejects 16 planted corruptions; a separately written replay and a
third model audit agree.

This is a stronger potential ansatz at a coarser quotient, so it is not a q=24
pair-coordinate theorem. It does not exclude an arbitrary function on each
six-dimensional cylinder, recursive state, support deformation, or continuum
transfer. The next section records the fresh isolated arbitrary-global rerun;
the earlier overwritten traces remain unbacked and are not used as evidence.

### 4.6 Arbitrary global potentials at q=6

For the same two assignments A=`(7,7,7,6,7)` and B=`(7,6,7,6,7)`, give every
point of every cylinder an independent potential value. Because the five
cylinders are pairwise disjoint, this is exactly one unrestricted variable on
each point of the 3,645-point union. No additive, pair-coordinate, polynomial,
or other factorization remains.

A fresh isolated CEGAR run rebuilt all 125 ordered word triples and all even-q
midpoint branches. There are exactly 1,128,545 actual global witnesses. Exact
semantic packets in `certificates/erdos-142-q6-global-potential-walls/` prove
infeasibility for both representatives:

| representative | selected rows | exact contradiction numerator |
|---|---:|---:|
| A `(7,7,7,6,7)` | 3 | 48 |
| B `(7,6,7,6,7)` | 646 | a positive 133-digit primitive-ray numerator |

For A the proof is already the three-row cycle

```text
 +F(1948) - 2F(2673) + F(2681) >= 20,
 -2F(1948) + F(2673) + F(2681) >= 20,
 +F(1948) + F(2673) - 2F(2681) >=  8.
```

Summing gives `0 >= 48`. The semantic packet binds the labels to their actual
six-dimensional cylinder vertices and records every local midpoint, carry,
support membership, and raw endpoint cost. The B proof is a 646-row positive
integer Farkas combination. A primary stdlib verifier reconstructs both full
finite models and rejects 18 planted corruptions; a separately written replay
independently rebuilds both rays and prints the three-row cycle.

This is the first arbitrary-global wall in this lane, but only at one coarse
finite quotient and for two assignments. The exact `8^5` mass census has 256
maximum-mass q=6 assignments. Global D4 transports of the particular A cycle
hit 32 and leave 224 outside that screen; B is handled by its separate ray.
No claim is made for the remaining assignments. Nothing here excludes
recursive state, jointly deformed supports, q=24/q=48 constructions, continuum
thickening, or integer transfer, and no new `r_3(N)` bound follows.

### 4.7 Exact 3-torsion family for every q=3m

The three-row q=6 packet is not a numerical-dual accident. For every integer
`m>=2`, set `q=3m` and retain the top D4 assignment `(7,7,7,6,7)`. With

```text
A=C=(q-3,m-1),  B=(q-3,q-1),  D=(q-3,2m-1),  u=(0,m),
```

the exact inverse D4 images lie in the strict T1 piece for all `m>=2`.
Consequently

```text
X=(A,B,C) in W2,  Y=(A,B,B) in W3,  Z=(A,B,D) in W3.
```

The identities `C=B+u`, `D=B-u`, and `3u=0 mod q` make `(X,Y,Z)`,
`(Y,X,Z)`, and `(X,Z,Y)` modular midpoint rows. Their raw costs are
`m^2,m^2,4m^2`; their potential coefficients cancel; and their sum is the
exact contradiction `0 >= 6m^2`, normalized to `2/3` after division by
`q^2`. The symbolic certificate in
`certificates/erdos-142-q3m-torsion-triangle-wall/` proves all affine support
faces and quadratic identities for the whole family, and an independent
implementation checks both odd and even quotients.

This includes q=24 and q=48. In particular, combining the family with the
separate q=24 mass certificate upgrades the top maximum-mass representative
from a cylinder-position-additive wall to an arbitrary-global wall.

At q=6, exhaustive enumeration of every torsion triangle of this W2/W3
incidence type covers 128 of the 256 maximum-mass assignments, exactly when
the P2 and P3 D4 supports intersect. The 128 outside this template are not
certified feasible. The older 32 count was only the global-D4 orbit of one
specific planted triangle.

### 4.8 Uniformly interior continuum torus wall

The q=3m points above approach a square seam and a strict T1 face at distance
`1/q`, so that family by itself leaves a limit question. A second exact family
removes both issues. For every `q=120n`, use the fixed normalized points

```text
A=C=(13/24,2/15),  B=(7/8,4/5),  D=(5/24,7/15),
u=(2/3,1/3).
```

Their continuous inverse D4 images are strict interior points of T2, T1, and
T3 respectively. Every tile-face margin is at least `1/30`, and every image
point stays at least `1/8` from a fundamental-square seam. The finite
`epsilon=1/q` preimages retain the same uniform margins for all `n>=1`.

The same W2/W3 product vertices now have carries
`(-1,-1),(0,1),(1,0)` and normalized raw-canonical endpoint costs
`2/9,5/9,5/9`. Summing their three coercivity inequalities cancels every
potential value and gives `0 >= 4/3`. Hence no arbitrary real-valued potential
on even this two-cylinder subunion can satisfy the modular torus coercivity
rows; a common approximate row deficit must be at least `4/9`.

This is a genuine continuum wall for the midpoint/cost convention actually
stated in EHPS Proposition 2.2: midpoint modulo 1, raw Euclidean cost between
canonical representatives. It is not a wall for a different ordinary
Euclidean midpoint predicate; three cyclic midpoint equations in a
torsion-free vector space force all points equal. The exact certificate in
`certificates/erdos-142-interior-torus-torsion-wall/` verifies both scopes,
the q=`120n` identities, uniform margins, eight planted failures, and an
independent reconstruction. The wall still concerns one D4 role assignment
and supplies no survivor, integer transfer, or new `r_3(N)` bound.

### 4.9 Every maximum-mass q=6 D4 assignment has a three-row wall

The earlier q=6 results fixed two representatives or one W2/W3 incidence
template. A complete exact screen now removes that restriction at this finite
quotient. Among all `8^5 = 32,768` role assignments, exactly 256 attain the
maximum five-cylinder union mass 3,645. They form 32 global D4 orbits. In
every maximizer the five 729-point cylinders are pairwise disjoint, so an
independent variable on each labelled full cylinder vertex is exactly an
arbitrary real-valued potential on the geometric union.

For an ordered word-cylinder pattern `(a,b,c)`, choose full vertices
`X in W_a`, `Y in W_b`, and `Z in W_c` so that all three permutations

```text
(X,Y,Z), (Y,X,Z), (X,Z,Y)
```

are modular midpoint witnesses. The associated rows are centered at `Y`,
`X`, and `Z`; their potential coefficients add to zero. Direct exact
enumeration of the q=6 point torsion table gives 324 coordinate triples.
Across all 125 ordered word patterns, precisely the five diagonal patterns
`(i,i,i)` have no positive full-vertex cycle. Each of the other 120 patterns
hits every one of the 256 maximizers with strictly positive total raw
canonical endpoint cost. Hence every maximum-mass q=6 D4 assignment would
force `0 >= c` for some integer `c>0`.

`certificates/erdos-142-q6-all-maximizer-three-row-torsion-wall/` replays the
complete census. A separately written reconstruction retains the cylinder
label and all three two-dimensional points in each potential-variable key,
accumulates coefficients when labels coincide, verifies every midpoint,
carry, and raw cost, and plants the earlier local-point-aliasing failure mode.

This is a complete negative classification only for the q=6 maximum-mass D4
support family and arbitrary static global potentials. It does not imply a
higher-q or continuum classification, and it does not exclude recursive
state, jointly deformed supports, or correlated superblocks. It produces no
construction and no new `r_3(N)` bound.

### 4.10 The full q=6 Cartesian outer-code extension also fails

The previous wall is local to one q=6 block, so a natural escape is to choose
an outer code `C` of label words and allow a completely nonseparable potential
on the resulting union of product blocks.  The exact all-pattern census closes
that full Cartesian extension.

At each outer coordinate, choose any one of the 256 maximum-mass assignments;
the choice may vary with the coordinate but is fixed across codewords.  For
every non-diagonal ordered local label pattern `(a,b,c)`, the q=6 census gives
three full-vertex midpoint rows whose potential coefficients cancel and whose
raw right sides sum to at least 24, or normalized right side at least `2/3`.
For a nonconstant outer triple `(u,v,w)`, use this local cycle wherever
`(u_i,v_i,w_i)` is non-diagonal and use a constant zero-cost triple elsewhere.
Concatenation produces three actual global midpoint rows.  Their coefficients
cancel at the full superblock-vertex level, without writing the potential as a
sum of coordinate functions, and their normalized right side is at least

```text
(2/3) * #{i : (u_i,v_i,w_i) is non-diagonal} > 0.
```

If an outer code contains distinct words `u` and `v`, the ordered triple
`(u,v,v)` is therefore impossible.  Hence a survivor code has at most one
word.  But one local cylinder has density

```text
729/6^6 = 1/64 < (7/24)^3,
```

so a singleton product misses the supplied mass gate at every length.  The
primary and independently written replays in
`certificates/erdos-142-q6-outer-code-tensor-wall/` reconstruct all 32,768
assignments, all 256 maximizers, all 30,720 maximum-assignment/non-diagonal
pattern cycles, coordinate-dependent maximizers, full modular carries, raw
cost additivity, and exact global-variable cancellation.

This is an exact capacity wall for full Cartesian products of the five q=6
cylinders.  It still leaves correlated non-product subblocks,
codeword-dependent support assignments, support deformation or thickening,
scalar digit encodings with cross-block carry, and the construction-to-integers
transfer outside its scope.  Those are now the honest recursive escape hatches.

### 4.11 Affine cyclic lines close every maximum q=4 assignment

The next torsion-free-with-respect-to-three quotient is q=4.  Its exact EHPS
grid support is

```text
T = {(2,1), (2,2), (3,0), (3,1)}.
```

The `8^5` D4 census again has 256 maximum assignments in 32 global-D4
orbits.  Each maximum union consists of five disjoint 64-point cylinders, so
its mass is 320 and its density is `5/64`.  Exact arithmetic gives

```text
(5/64) / (7/24)^3 = 1080/343,
5/64 - (7/24)^3 = 737/13824 > 0.
```

Although three is invertible modulo four and therefore excludes the q=6
three-row triangle, every maximum orbit contains a full affine order-four line

```text
A_j = A_0 + j d  (mod 4),  j=0,1,2,3.
```

The four modular midpoint rows centered successively around this line have
unit multipliers and cancel every global-potential coefficient.  Their raw
right sides sum to

```text
2||A_0-A_2||^2 + 2||A_1-A_3||^2 > 0.
```

Thus every maximum q=4 union is impossible for an arbitrary, nonseparable
real-valued potential.  The exact primary and independent replays in
`certificates/erdos-142-q4-affine-order4-line-wall/` enumerate all 32,768
assignments, the 32 symmetry representatives, 4,736 affine lines across those
representatives, exact midpoint carries and raw costs, and D4 transports to
all 256 maximizers.  This finite wall does not survive geometric deformation
automatically and makes no continuum, correlated-subblock, scalar-transfer,
or integer-construction claim.

### 4.12 Balanced midpoint hypercycles close q=7 and q=8

The q=4 and q=6 contradictions are instances of one finite-group mechanism.
Call a family of modular midpoint rows a *balanced midpoint hypercycle* when
the total coefficient of every physical vertex is zero.  Summing the rows
then eliminates one completely arbitrary, nonseparable potential.  If the
sum of raw canonical endpoint costs is positive, the family is an exact
Farkas contradiction.

A full affine cyclic line

```text
A_j = A + j d,  j in Z/kZ,
```

with `d` of order `k>=3` is the simplest example: the `k` adjacent midpoint
rows give each vertex endpoint multiplicity two and center multiplicity one.
The complete factorized census in
`certificates/erdos-142-q7-q8-unit-hypercycle-walls/` allows each of the three
two-dimensional blocks to have any step order dividing `k` and requires only
that the least common multiple be `k`; this makes the line census complete,
not merely a sufficient screen.

At q=8 the exact EHPS support has 15 points.  The maximum five-cylinder mass
is `5*15^3=16875`, attained by 256 assignments in 32 global-D4 orbits, and its
density exceeds the supplied gate by

```text
16875/8^6 - (7/24)^3 = 280009/7077888 > 0.
```

Every maximum orbit contains a full order-four affine line, yielding a
four-row wall; full order-eight lines independently close every orbit.  Exact
D4 transport carries the representative certificates to all 256 maximizers.

At q=7 the exact support has 11 points and maximum mass `5*11^3=6655`, again
with 256 maximizers in 32 global-D4 orbits.  Its density margin is

```text
6655/7^6 - (7/24)^3 = 51645113/1626379776 > 0.
```

Here the complete order-seven line census covers zero orbits.  A shorter
balanced affine pattern nevertheless closes every one.  Put

```text
V_i = A + c_i d,
c  = (0,1,4,3,6),
pi = (2,4,0,1,3),
```

with nonzero `d` in `(Z/7Z)^6`, and for `i=0,...,4` use endpoints
`(V_i,V_(i+1))` centered at `V_pi(i)`.  The identities
`c_i+c_(i+1)=2c_pi(i) (mod 7)` make all five rows genuine modular midpoint
rows.  The endpoint edges form a five-cycle and `pi` is a permutation, so
each vertex has coefficient `2-2=0`; every consecutive coefficient difference
is nonzero, so every cost is positive.  Exhaustion over center permutations
shows this template is minimal inside the connected unit-cycle/permuted-center
class: lengths three and four have only the constant kernel, whereas length
five has exactly five nonconstant-kernel permutations.

The primary and separately written stdlib replays reconstruct both quotient
supports, the full `8^5` assignment and orbit censuses, exact mass gates,
complete factorized pattern counts, modular carries, raw costs, physical-
variable cancellation, D4 transports, and live corruption controls.  This is
a finite q=7/q=8 maximum-D4 classification only.  It does not exclude deformed
or thickened supports, correlated non-product subblocks, continuum limits,
scalar digit encodings with cross-block carry, or the integer transfer.

### 4.13 Coordinate-dependent q=6 D4 products have capacity one

The preceding outer-code theorem fixes a maximum five-cylinder assignment in
each outer coordinate.  A natural escape was to let every codeword choose its
own coordinate-dependent sequence of D4 images.  The exact q=6 local torsion
table closes the full-product version of that larger class as well.

Let `S_0,...,S_7` be the eight D4 images of the nine-point q=6 support.  An
ordered triple `(x,y,z)` is *cyclic* when each point is a modular midpoint of
the other two.  Equivalently,

```text
y = x+d,  z = x+2d,  3d=0  in (Z/6Z)^2.
```

The solver-free census in
`certificates/erdos-142-q6-coordinate-d4-product-wall/` finds 324 ordered
cyclic triples, including the zero-step triples.  All 512 ordered D4 buckets
have total size between 4 and 9.  The nondegenerate statement needed below is
more precise: for every ordered unequal pair `g!=h`, the bucket

```text
S_g x S_g x S_h
```

contains a nondegenerate cyclic triple.  All 56 pairs pass, with witness-count
distribution `{2:24, 4:16, 6:16}`.

For a length-`L` D4 word `a`, write

```text
B_a = product_i S_(a_i).
```

Given distinct words `a,b`, choose a certified nondegenerate local triple at
every coordinate where they differ and a diagonal anchor at every unchanged
coordinate.  Tensoring gives physical points `X,Y in B_a` and `Z in B_b`
which form a nondegenerate cyclic triple in `(Z/6Z)^(2L)`.  The three
coercivity rows centered successively at `X,Y,Z` cancel every coefficient of
one arbitrary, nonseparable potential on the physical union, while their raw
canonical endpoint costs have positive sum.

Thus a potential-compatible collection contains at most one distinct D4
product word.  A singleton has density

```text
(9/36)^L = (1/4)^L < (7/24)^L,
```

so it misses the supplied mass gate at every positive length.  This is an
exact capacity-one theorem for arbitrary coordinate-dependent **full product**
D4 words.  It retires, in particular, the mass-positive six-coordinate chain
candidate `000000,111100,110011,001111,010101` before any additive, chain, or
global potential ansatz is considered.

The primary and separately written stdlib replays reconstruct the support and
D4 action independently, verify all three midpoint equations, exact carries,
raw costs, physical-variable cancellation, the singleton gate, and live
semantic corruptions.  The theorem remains finite q=6 and full-product only.
Genuinely correlated non-product subblocks, graph/height lifts, support
deformation, higher quotients, continuum thickening, scalar digit encodings,
and the integer transfer remain open.

### 4.14 The q=6/M7 cell-local offset ansatz has an exact wall

A different q=6 search produced a 24-cell half-open-box support whose mass
passes the finite M7 screen.  The first continuous potential hierarchy for
that candidate was

```text
H(x) = 2||x||^2 + G(cell(x), parity_pattern(x))
       + sum_i U(cell(x), i, coarsepoint_i(x)).
```

The semantic packet in
`certificates/erdos-142-q6-m7-cellu-restricted-wall/` proves that this exact
feature class is impossible.  Its 358 strictly positive integer Farkas rows
reconstruct the half-open residual costs, cancel every `G` and cell-specific
`U` coefficient, and leave a strictly positive weighted right side.  The
primary and separately written stdlib replays agree on all 24 cells, 148
cell/parity states, semantic witnesses, and four planted corruptions.

This is a restricted-potential wall, not a capacity theorem.  The independent
scope audit finds 946 nonzero unrestricted physical-vertex aggregates and 60
nonzero symmetric-quadratic aggregates, so the same ray does not exclude an
arbitrary `H`, a general cross-coordinate quadratic, or pair interactions.
Richer and recursive potentials, support deformation, a complete continuum
construction, integer transfer, and a new `r_3(N)` bound remain open.

### 4.15 The eight-cell M7 redesign has an exact torsion wall

A minimum-cardinality cell selector then found the mass-positive redesign

```text
(38,3), (41,3), (42,3), (44,3),
(49,3), (50,3), (52,3), (56,3).
```

Every cell has count 178,605, so the disjoint union has exact mass
`245/373248`, exceeding `(7/24)^6` by `2597/63700992`.  This exact full union
nevertheless contains a three-row obstruction stronger than a restricted
feature-class dual.  Three distinct physical vertices in cells `(38,3)` and
`(41,3)` form a cyclic modular-midpoint triangle.  For an arbitrary single
physical potential `H`, the three rows cancel every `H` coefficient and leave
the raw contradiction `0>=144`, or `0>=4` after q=6 normalization.

The packet in
`certificates/erdos-142-q6-m7-redesign-torsion-wall/` also proves that this is
not a grid-boundary accident.  Adding a common offset
`delta in (0,1/6)^12` to all three vertices keeps them in strict interiors of
their selected half-open boxes, preserves all modular carries, and leaves the
same normalized contradiction.  Primary and independently written stdlib
replays reconstruct the cells, mass, physical rows, carries, costs and open
offset family.

The deletion boundary is essential.  For the displayed order-three step the
verifiers count only 45 disjoint three-orbits, far below the exact gate slack
`5679639/64` measured in q=6 boxes.  Other steps and the minimum hitting set
are not classified.  Thus this is an exact-union wall, not a fence against
small excisions by itself.  Section 4.16 records the subsequent cross-step
matching that closes this deletion gap for the same support.  The rows use
nonzero modular carries, so neither result is an ordinary Euclidean-midpoint
theorem or supplies an integer transfer or new `r_3(N)` bound.

### 4.16 The eight-cell redesign has a deletion fence

The exact all-step orbit ledger contains 1,342,512 physical order-three
orbits.  More importantly, the frozen certificate in
`certificates/erdos-142-q6-m7-deletion-fence/` exhibits a deterministic
matching of 102,636 pairwise box-disjoint orbits, using 307,908 distinct
physical q=6 boxes.  Both replays check every matching record directly; the
full orbit census is discovery provenance rather than a premise of the fence.

For each matched orbit `(x,y,z)`, all three cyclic modular-midpoint rows have
positive raw endpoint-square right sides while their arbitrary-`H`
coefficients cancel at the physical vertices.  Translating the three boxes by
one common `delta in (0,1/6)^12` preserves their carries and endpoint
differences.  Hence, for every common offset, at least one of the three points
must be deleted from any retained set that satisfies the coercivity rows.
Pulling the three deletion sets back to the offset cube and using
subadditivity costs at least one q=6 box-volume.  Because the matching's boxes
are disjoint, these lower bounds add across all 102,636 orbits.

The original union contains 1,428,840 boxes, so every compatible measurable
retained subset has mass at most

```text
(1428840 - 102636)/6^12 = 1326204/6^12.
```

This is below the supplied gate by

```text
(7/24)^6 - 1326204/6^12
  = 889065/(64*6^12)
  = 98785/15479341056 > 0.
```

Thus the eight-cell redesign cannot be rescued by small measurable excisions
within its boxes under the retained raw-canonical torus model.  This is a
construction-specific finite-torsion/common-offset fence, not a classification
of other supports, deformations, q, recursive mechanisms or non-product
constructions.  It gives no ordinary Euclidean transfer, integer construction,
new `r_3(N)` bound, or solution of Problem 142.

### 4.17 A mass-positive selector escapes every order-three orbit

The deletion fence identifies a precise support-design requirement: avoid the
order-three quotient hypergraph before tuning a potential.  In the full q=6/M7
universe there are 448 coarse cells `(word,residue)`, not 148; the latter is
only the parity-pattern state count inside the older 24-cell candidate.  The
research-fence packet in
`certificates/erdos-142-q6-m7-orbit-free-selector/` freezes 28 cells with

```text
box count = 1,405,512,
mass      = 241/373248,
excess over (7/24)^6 = 5743/191102976 > 0.
```

An order-three q6 translation preserves every local parity bit and therefore
the exact residue.  For a selected word triple let `v` count nonconstant
coordinate columns and let `t` count those columns containing exactly one
`1`.  Exhausting the 42 valid local increment/start configurations proves
that a nontrivial orbit exists exactly when

```text
v > 0 and t <= residue <= t + 6 - v.
```

Both standard-library replays reconstruct this criterion and test every
ordered selected word triple.  None passes.  The support consequently has
zero nontrivial order-three physical orbits and zero matching, while the old
deletion fence would need 65,417 disjoint families at this mass.  Thus the
torsion/deletion mechanism that closes the eight-cell redesign genuinely does
not close this selector.

This is a narrowed next candidate, not a potential survivor.  Longer balanced
families of modular midpoint rows can exist without a three-point translation
orbit.  Restricted additive and parity-class potential screens are already
negative, but their quotient rays do not cancel at actual physical vertices.
The live bottleneck is therefore an arbitrary-physical-potential certificate
or countercertificate for this selector, followed only after survival by
continuum thickening and integer transfer.  A separate CP-SAT search reports
that the displayed mass is optimal among orbit-free coarse selectors, but no
solver-independent optimization proof is promoted here.

## 5. What would count as progress

A promotable positive result must include all of:

- exact support and potential data;
- exhaustive local carry/witness pricing with raw endpoint distance;
- all ordered codeword-triple inequalities;
- a single well-defined bounded potential on overlaps;
- an exact union-mass proof above `(7/24)^L` after losses;
- a continuum thickening certificate; and
- a checked superblock-to-integer transfer.

A meaningful negative result is a replayable exact dual/Farkas certificate
showing that a precisely defined role/code family cannot clear the mass gate.
Neither outcome may be promoted as solving P142 by itself.

The existing P142 certificates remain intact and keep their stated scopes.
This lane neither contradicts them nor claims they cover recursive correlated
superblocks. It adds one new attack surface: weighted coercivity capacity.

## References

- Elsholtz, Hunter, Proske, Sauermann,
  [*Improving Behrend's construction*](https://arxiv.org/html/2406.12290),
  especially Proposition 2.2 and the note on Naslund at lines 77--78.
- Naslund,
  [*Lower Bounds for the Shannon Capacity of Hypergraphs*](https://drive.google.com/file/d/1pW4FreiLm6DV9CHg3FBpGCtfjRr7ZYdp/view?usp=drive_link),
  OeMG 2023 slides.
- Edel,
  [*Extensions of generalized product caps*](https://www.yvesedel.de/Papers/ExtProd.pdf),
  especially Definitions 9 and 12 and the recursive problem on pages 9--10.
- Christandl, Fawzi, Hoang Ta, Zuiddam,
  [*Larger Corner-Free Sets from Combinatorial Degenerations*](https://arxiv.org/abs/2111.08262).
- Karapetyan, Karapetyan,
  [*New Method for Constructing Complete Cap Sets*](https://arxiv.org/abs/2601.16917).

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

This was a narrowed next candidate, not yet a potential survivor.  Longer
balanced families of modular midpoint rows can exist without a three-point
translation orbit.  Section 4.18 records the exact six-row physical family
that closes this candidate.  A separate CP-SAT search reports that the
displayed mass is optimal among orbit-free coarse selectors, but no
solver-independent optimization proof is promoted here.

### 4.18 The orbit-free selector has unit Farkas girth exactly six

The packet in
`certificates/erdos-142-q6-m7-unit-girth-six-wall/` resolves the selector's
arbitrary-physical-potential bottleneck negatively.  It gives six distinct
physical q6 vertices in cells

```text
(49,0), (21,0), (45,0), (35,0), (7,0), (45,0)
```

and the six rows `(endpoint_a,endpoint_b;center)`

```text
(1,2;0), (0,3;1), (4,5;2),
(4,5;3), (0,3;4), (1,2;5).
```

Every row is a genuine modular midpoint relation at all six two-dimensional
positions.  Each physical vertex occurs twice as an endpoint and once as a
centre, so summing the rows cancels an arbitrary value of `H` at every actual
physical vertex.  The raw canonical endpoint costs are

```text
68, 56, 32, 32, 56, 68,
```

and therefore leave `0 >= 312`, or the normalized contradiction
`0 >= 26/3`.  A common offset in `(0,1/6)^12` puts all six points in the strict
interiors of their selected half-open boxes while preserving every carry and
endpoint difference.  The wall is consequently not a grid-boundary artifact,
although its nonzero carries make it branch-sensitive rather than an ordinary
Euclidean-midpoint theorem.

The row count is exact in a natural finite class.  Two independent exhaustive
replays enumerate all 6,516 labelled endpoint-degree-two unit templates with
two through five rows and every scalar `Z/6` kernel assignment.  Exactly 1,511
templates have a positive scalar mode.  Every one forces a fixed three-label
order-three orbit, while Section 4.17 certifies that the selector contains no
such orbit.  Hence no positive unit-balanced packet in the displayed class has
fewer than six rows, and the explicit packet attains six.

This closes the exact full 28-cell union for arbitrary physical potentials
under the supplied raw-canonical torus convention.  It does not classify
non-unit certificates on other supports, give a torsion-free Euclidean or
integer construction, improve `r_3(N)`, or solve Problem 142.  The useful
design lesson is sharper: removing all translation triangles raises the local
obstruction girth, but does not by itself produce coercive capacity.

### 4.19 Three eight-row packets fence every above-gate subset of the 22-cell redesign

The next support screen removed the six-row mechanism and produced a 22-cell
full-box candidate of mass

```text
1,370,520 / 6^12 = 235/373248 > (7/24)^6.
```

The packet in
`certificates/erdos-142-q6-m7-unit-k8-deletion-fence/` closes not only that
exact union but every above-gate subcollection of its cells.  Three literal
eight-row physical packets use the same endpoint-degree-two template and have
pairwise-disjoint required supports

```text
{33:3, 45:0, 49:0},
{45:1, 19:6, 26:6},
{30:3, 20:5, 34:5}.
```

Their raw right-side totals are respectively `216`, `144`, and `288`.  In
each packet every one of the eight physical vertices occurs twice as an
endpoint and once as a centre, so the eight rows cancel an arbitrary physical
potential exactly and leave a positive contradiction.  A common offset in
`(0,1/6)^12` moves every digit point into the strict interior of its original
box without changing a carry or endpoint difference.

Any subcollection avoiding all three packets must remove at least one cell
from each displayed support.  Because the supports are disjoint, the exact
minimum deletion is

```text
5,832 + 5,832 + 69,984 = 81,648 boxes.
```

It leaves at most `1,288,872` boxes, and

```text
1,288,872 * 64 - 85,766,121 = -3,278,313 < 0.
```

Thus no whole-cell deletion repair inside this 22-cell lane can retain the
inherited mass gate and escape the displayed arbitrary-`H` walls.  This is a
solver-free implication from three positive witnesses; it does not rely on
the negative discovery searches that preceded them.  Partial carving,
replacement cells, geometric deformation, richer recursive support design,
ordinary Euclidean transfer, and integer transfer remain open.  No new
`r_3(N)` bound or solution of Problem 142 is claimed.

### 4.20 A 30,425-packet matching also fences arbitrary measurable carving

The remaining partial-carving caveat for this exact 22-cell support is closed
by `certificates/erdos-142-q6-m7-k8-microbox-deletion-fence/`.  A second
balanced eight-row template has the endpoint rows

```text
(4,5;0), (4,7;1), (6,7;2), (5,6;3),
(2,3;4), (1,2;5), (0,1;6), (0,3;7).
```

The frozen ledger contains `30,425` packets on `243,400` globally distinct
physical `q6^12` microboxes.  Both stdlib replays reconstruct every selected
cell, midpoint carry, raw endpoint cost, and physical-box code.  Every row has
positive cost, and every vertex label occurs twice as an endpoint and once as
a centre, so each packet cancels an arbitrary physical potential exactly.

This gives a measure fence, not a whole-box deletion claim.  For one packet,
identify each of its eight half-open microboxes with the common offset cube
`D=[0,1/6)^12`.  If `A_i` is the retained offset slice in box `i`, then a
common offset in all eight `A_i` would realize all eight midpoint rows and
give a positive contradiction.  Hence their intersection is empty up to a
null set, so

```text
sum_i measure(D minus A_i) >= measure(D).
```

The packet boxes are globally disjoint, so translation and Fubini let these
losses add over the matching.  Any measurable packet-free carving therefore
deletes at least `30,425` box-volume units and retains at most

```text
1,370,520 - 30,425 = 1,340,095 box-volume units.
```

The exact inherited-gate comparison is exceptionally tight but strict:

```text
1,340,095 * 64 - 85,766,121 = -41 < 0.
```

Thus the fixed 22-cell geometric union cannot be repaired by arbitrary
measurable carving while preserving the supplied mass gate and the required
raw-canonical modular-torus coercivity inequalities.  The theorem uses the
full common-offset family for each packet, not merely one displayed interior
point.  Replacement cells, geometric deformation, recursive state, ordinary
Euclidean transfer, and integer transfer remain open.  No new `r_3(N)` bound
or solution of Problem 142 is claimed.

### 4.21 The 117-cell four-dimensional lead has a six-deletion cell-offset wall

A one-state four-dimensional alphabet was found with `117` distinct `q=6`
cells.  In integer coordinates it is

```text
U_D = {(a_1,a_2,a_1+d_1,a_2+d_2) mod 6 : a in S0, d in D},
```

where `|S0|=9`, `|D|=13`, and the displayed map is injective.  Its density is

```text
117/6^4 = 13/144 = 52/576,
```

which exceeds the four-dimensional EHPS product baseline
`(7/24)^2=49/576` by `1/192`.  Six whole-cell deletions leave density above
the gate by exactly `1/1728`; seven deletions fall below it.

The exact packet in
`certificates/erdos-142-q6-117-cell-six-deletion-wall/` closes every such
gate-preserving whole-cell deletion under the continuous potential ansatz

```text
F(x) = 2 ||x||_2^2 + g[cell(x)].
```

It reconstructs all `98,167` compatible ordered cell triples and their exact
`6^2`-scaled continuous half-open branch suprema.  A ledger of `943` positive integral
Farkas rays gives necessary deletion cuts: every feasible deletion must hit
the semantic cell support of each ray.  A separate `29,980`-node exact
branching/disjoint-packing certificate proves that no set of at most six cells
hits all of them.  Consequently no whole-cell subcollection of this fixed
alphabet can both preserve the supplied density gate and satisfy every
continuous modular-torus coercivity row with a cell-offset potential.

This is a sharp restricted repair fence, not the death of the `117`-cell
geometry.  Within-cell piecewise functions, pair interactions, genuine
graph-state/cocycle potentials, partial carving, replacement cells and
geometric deformation remain open.  In particular the certificate neither
constructs the synchronized triple-path potential needed by the Markov shell
lemma nor rules one out.  It gives no integer construction, new `r_3(N)`
bound, or solution of Problem 142.

### 4.22 The complete-loopless transition-table extension also has an exact wall

The next test kept all `117` cells but replaced the one-state Cartesian
language by the complete loopless directed graph on those cells.  Its
length-`m` path count is

```text
117 * 116^(m-1),
```

so its asymptotic four-dimensional density base is
`116/6^4=29/324`.  This still exceeds the EHPS product gate
`(7/24)^2=49/576`, by `23/5184`.

For a path `c_0,...,c_(m-1)`, allow the position- and length-independent
transition potential

```text
P_m(c) = g[c_0]/2 + sum_i H[c_i,c_(i+1)] + g[c_(m-1)]/2.
```

The directed values `H[a,b]` are arbitrary.  This strictly contains additive
cell offsets: choosing `H[a,b]=(g_0[a]+g_0[b])/2` and `g=g_0` gives
`P_m=sum_i g_0[c_i]`.  Its range is linear in `m`, so it has the right shell
scale if a coercive table exists.

The exact packet in
`certificates/erdos-142-q6-117-cell-loopless-transition-wall/` proves that no
such table exists for the full loopless language.  In scaled variables
`G=36g` and `J=36H`, five legal two-block rows with positive weights
`(1,2,1,1,1)` cancel every endpoint and directed-transition coefficient and
leave the contradiction `0>=1032`.  Appending the common alternating diagonal
tail `0,1,0,...` preserves looplessness and coefficient cancellation, so the
same ray obstructs every length `m>=2`.  Primary and separately written
standard-library replays check the continuous carry semantics, exact dual,
Perron gate, and all-length padding.

This certificate itself closes only the complete-loopless path language with
fixed position-independent endpoint and transition tables.  Section 4.25
supersedes the sparse-graph exception for unrestricted-endpoint 0/1 graphs.
Position- or length-dependent tables, state lifts, within-edge functions,
partial carving and support deformation are not consequences of this result.

### 4.23 Independent affine slopes in every one of the 117 cells also fail

Return to the one-block 117-cell geometry, but give every cell its own affine
function of the within-cell residual.  In scaled variables the potential is

```text
F(x) = 2 ||x||^2
     + 36^-1 (h[cell(x)] + sum_j p[cell(x),j] r_j(x)),
r_j(x) = 6 x_j - floor(6 x_j).
```

There are `117` independent offsets and `117*4` independent slopes, for `585`
free features.  This strictly extends both cell offsets and a globally shared
affine correction.

The exact packet in
`certificates/erdos-142-q6-117-cell-percell-affine-wall/` needs only two
necessary one-sided closure inequalities.  For cell triples `(105,91,91)`
and `(105,105,91)`, they reduce to

```text
h[105]-h[91]-p[91,1]-p[91,2]-p[91,3] >= 216,
-h[105]+h[91]+p[91,1]+p[91,2]+p[91,3] >= -72.
```

Their positive sum is the exact contradiction `0>=144`, or `0>=4` before
the uniform factor `36`.  Residual-one seam coordinates are used only as
one-sided limits of required inequalities within the same half-open cells;
cellwise affinity makes those limits necessary despite possible jumps between
neighboring cell formulas.

The primary standard-library replay reconstructs all `117` cells, all scalar
closure vertices, one deterministic base-cost-maximizing row for each of the
`98,167` compatible ordered cell triples, the two selected row indices, their
geometry and every feature incidence.  A separate direct cross-check replays
the two rows without importing or enumerating the primary ledger.  The
`98,167` rows are a deterministic closure subledger, not the full all-vertex
continuous ledger; infeasibility follows because the two selected rows are
individually necessary.

This certificate itself closes only independent residual-affine functions on
the fixed cells.  The next strict-interior dilation result supersedes that
functional restriction for the unchanged one-block union.  Pair/state
interactions, partial carving, support deformation and integer transfer are
not consequences of this affine certificate.

### 4.24 A strict-interior dilation wall closes every bounded one-block potential

The affine obstruction is the visible edge of a stronger dynamical wall.  Let
`A=93=(5,1,0,0)` and `B=91=(5,1,5,5)`, fix `0<s<1`, and write any bounded
candidate on the unchanged 117-cell union as

```text
F(x)=2||x||^2+h(x)/36.
```

For every `0<t<1/3`, two actual strict-interior torus-midpoint triples have
cell patterns `(A,B,B)` and `(A,A,B)`.  In the last two residual coordinates
their `(x,y,z)` values are respectively

```text
(t,1-t,1-3t)       and       (3t,t,1-t),
```

with carries `-1` and `+1`; the first two residual coordinates are all `s`.
Their exact `q^2`-scaled correction right sides are `216-48t` and `-72-48t`.
Defining

```text
D(t)=h_A(s,s,t,t)+h_B(s,s,1-t,1-t),
```

and adding the required inequalities gives

```text
D(3t)-D(t) >= 144-96t.
```

At `t_n=(1/4)/3^n`, finite summation through `N` yields

```text
D(1/4)-D(1/(4*3^N)) >= 144N-12(1-3^-N).
```

The right side grows with `N`, while bounded `h` bounds the left side.  Thus
no bounded potential can satisfy every pointwise raw-canonical coercivity row
on the full fixed union.  This uses neither a limit, a closure face, affinity,
continuity, nor a finite-dimensional ansatz.

`certificates/erdos-142-q6-117-cell-bounded-dilation-wall/` contains primary
and separately written exact replays.  The result requires the inequality
pointwise on every eligible triple; it does not follow from an almost-everywhere
claim.  Graph-restricted triples, carving/deformation, changed cell ownership,
unbounded potentials, integer transfer and a new `r_3(N)` bound remain outside
scope.  Erdős Problem 142 remains unsolved.

### 4.25 Common-successor walls force every fixed-state transition graph below gate

The sparse-graph escape can be tested without selecting a graph.  For 187
unordered pairs `{a,b}` of the 117 cells, the two exact local closure rows

```text
(a,b,b), (a,a,b)
```

have positive summed `q^2`-scaled right side, equal to 72 or 144.  If `a,b`
share an allowed successor `p`, append the diagonal row `(p,p,p)` to both.
The resulting two synchronized path rows cancel every endpoint value `G[a]`
and directed transition value `J[a,p]`, while retaining that positive right
side.  A common predecessor gives the reversed construction.

Avoiding all such two-row walls therefore forces `N+(a)` and `N+(b)` to be
disjoint for every bad pair.  The exact census contains a matching of 27 bad
pairs.  If `Av=rho v` is a nonnegative Perron eigenvector and `S=sum(v)`, each
matched pair satisfies

```text
rho(v_a+v_b) <= S,
```

and each of the other 63 vertices satisfies `rho v_w<=S`.  Summing the 90
block inequalities gives `rho<=90`, whereas the four-dimensional density gate
requires

```text
rho > 6^4(7/24)^2 = 441/4 = 110.25.
```

Thus every unweighted directed graph on the fixed cell states either contains
an exact two-row transition-table wall or has insufficient path growth.
`certificates/erdos-142-q6-117-cell-transition-spectral-wall/` independently
reconstructs the 187-pair census, 43,758 append/prepend cancellations, the
matching and the solver-free Perron argument.  A separate replay needs only
seven disjoint pairs and already gives `rho<=110<441/4`.

This certificate itself assumes unrestricted endpoints and a fixed endpoint/
edge table.  The next result supersedes those two restrictions throughout the
label-only unweighted lane.  Weighted or repeated-label state lifts,
residual-dependent functions, coupled edge tiles, carving/deformation, integer
transfer and a new `r_3(N)` bound are not consequences of this certificate.

### 4.26 Endpoint pruning and arbitrary whole-label-path corrections still fail

Fix a zero-one adjacency matrix `A` on the same 117 cell labels and fixed
nonempty start/end masks `u,v in {0,1}^117`.  The literal volume of the
disjoint `(m+1)`-block path union is

```text
1296^(-(m+1)) u^T A^m v.
```

The relevant rate is the largest Perron root of a strongly connected component
which is reachable from `supp(u)` and can reach `supp(v)`.  Fixed positive
endpoint weights give a partition function with the same exponential rate,
but are not themselves the literal union volume.

Restrict the 27 disjoint bad pairs from Section 4.25 to such a Perron core `C`.
Write `k=|C|` and let `h` be the number of matching pairs wholly inside `C`.
Because 63 vertices are unmatched, `h>=max(0,k-90)`.  Call a pair sandwiched
when its labels have both a common predecessor and a common successor in `C`.
If there is no sandwiched pair, designate each completed pair either
out-disjoint or in-disjoint.  If `r` pairs use the first designation, right and
left Perron vectors give

```text
rho <= k-r,              rho <= k-(h-r).
```

Therefore

```text
rho <= k-ceil(h/2) <= 103 < 441/4.
```

An above-gate core consequently contains `q->a,b->p` for a matched bad pair.
Reachability and co-reachability pad this branch with a common accepted prefix
and suffix, producing two accepted label paths `A_path,B_path` which differ in
only the `a/b` block.  The two required midpoint inequalities have correction
terms

```text
Phi_m(A_path)-Phi_m(B_path),
Phi_m(B_path)-Phi_m(A_path),
```

and exact summed right side 72 or 144.  Thus they contradict one another for
**any finite real correction constant on a complete label path**.  The
correction may be nonadditive, position-dependent, length-dependent, and have
no uniform bound in `m`.

SCC cyclic classes show that for every sufficiently large active horizon
residue there exists a same-length sandwiched branch pair.  Endpoint pruning
can suppress isolated short horizons—the complete looped 112-state graph with
fixed start/end label has only one path at horizon one—but cannot preserve an
above-gate wall-free subsequence.  More precisely, every infinite set `H` of
sufficiently large wall-free horizons satisfies

```text
limsup_(m in H) (u^T A^m v)^(1/m) <= 103.
```

`certificates/erdos-142-q6-117-cell-endpoint-pruned-label-wall/` contains the
primary exact replay and a separately written no-import audit.  The result is
still label-only: it does not cover residual-dependent potentials, weighted or
repeated-label automata, coupled edge tiles, horizon-varying graphs or endpoint
masks, carving/deformation, integer transfer or a new `r_3(N)` bound.  Problem
142 remains unsolved.

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

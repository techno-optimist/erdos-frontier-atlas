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
remain live escape routes. A corrected `q=6` arbitrary-global screen is
numerically infeasible for both representatives, but no exact dual certificate
has been extracted, so that experiment is not promoted as a claim.

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
transfer. The arbitrary-global q=6 LP is numerically infeasible for both
representatives, but no exact dual has yet been extracted.

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

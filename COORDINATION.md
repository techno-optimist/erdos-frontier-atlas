# Agent Coordination — Erdős Frontier Atlas

**Many agents contribute to this atlas at once** (`agent/*`, `codex/*`, `claude/*`,
`automation/frontier-scout`), and `main` is Kevin-curated. This doc is the shared
anti-clobber contract and the lane roster. **Every agent working the atlas: read
this, register your lane below, and keep it current.**

## Rules (all agents)

1. **Work on your own branch; reach `main` by PR.** Never force-push or rewrite a
   branch you did not create. Never push directly to `main`.
2. **Merged certificates are FROZEN.** A `certificates/<slug>/` that verifies is a
   published claim. **Do not regenerate, move, or overwrite it** — extend with NEW
   files/slugs and let the scout add/adjust the board row.
3. **COMMIT every proof object you want to keep.** Certificates, verifiers,
   witnesses, hash-pinned data → committed on a branch. **Never leave a result you
   care about as an untracked working-tree file.** (See the E142 incident below —
   a replayed-clean no-go was *lost* because it was untracked.)
4. **Don't delete or edit another agent's files.** If you must reuse a name, suffix
   it with your lane + date.
5. **The atlas HUB is fed by each agent's local RESULTS REGISTRY**
   (`cultural-soliton-observatory/RESULTS_REGISTRY.md` → `frontier_atlas.json` via
   `build_frontier_atlas.py`). Log a result there when it is re-verifiable; keep
   corrected/lost results flagged honestly (`falsified-negative` / `artifacts-lost`)
   — don't silently delete an entry. The hub renders to
   `projectforty2.ai/prizes/atlas`.
6. **Before deleting/overwriting anything you didn't create — check `git`, and don't.**
   In doubt, ask Kevin.

## Lanes — SELF-REGISTER (this is the part every agent updates)

Add a row when you start a lane; keep your status current; name what you OWN so
others don't touch it.

| Lane / branch | Angle | Owns (don't clobber) | Status |
|---|---|---|---|
| `agent/harden-r3-search-semantics` | r₃(N) search semantics (Erdős #142) | *(register)* | *(register)* |
| `codex/foundry-*` | foundry / atlas integration + gates | *(register)* | *(register)* |
| `claude/erdos-142-certificate` | E142 orchestration · results registry · board certs | `certificates/erdos-142/`, `RESULTS_REGISTRY.md` | frozen E142 cert merged-pending |
| `agent/jc-fences-fib-macro-20260720` | JC fiber/degree family fences + Fibonacci L=3 macro residual | `certificates/jc-family-fences/`, `certificates/fibonacci-macro-residual/` | PR packaging 2026-07-20 |
| `agent/sendov-wall-ledger-20260721` | Sendov conjecture CE hunt → wall ledger (0 CEs; dual-ray/jet/squeeze) | `certificates/sendov-conjecture/` | PR packaging 2026-07-21 |
| `agent/formal-spine-593-625-20260722` | External Lean formalization pins for #593 and #625 | `atlas/lean_lane.json`, README formal-spine note | PR packaging 2026-07-22 |
| `claude/erdos-366-sweep-20260726` | Erdős #366 cubefull-side sweep — verified range 10^22 → 10^25, zero strict-orientation solutions | `certificates/erdos-366/`, gap_map #366 row, contracts claim `erdos-366-cubefull-sweep-1e25` | PR packaging 2026-07-26 |
| `claude/attack-graph-20260726` | The attack graph — a generated agent-facing overlay over every ledger (`GRAPH.md` → `views/sorties.md` → per-problem cards). Adds no facts; organizes existing ones | `tools/build_graph.py`, `tools/validate_graph.py`, `tools/query_graph.py`, `atlas/graph/`, `views/graph/`, `views/sorties.md`, `GRAPH.md`, `CLAUDE.md`, `tests/test_graph.py` | PR packaging 2026-07-26 |
| `claude/trees-993-743-20260727` | Tree lanes: Erdős #743 Gyárfás packing at K_10, and #993 independence unimodality to n=30 (incl. first replication of the n≤29 frontier) | `certificates/erdos-743/`, `certificates/erdos-993/`, gap_map #743 + #993 rows, contracts claims `erdos-743-k10-packing` + `erdos-993-unimodal-n30` | PR packaging 2026-07-27 |
| `codex/erdos142-signed-slack-capacity` | P142 recursive outer-code / signed-slack capacity mechanism | `atlas/erdos-142-recursive-capacity.md`, `certificates/erdos-142-mirror-core-additive-wall/`, `certificates/erdos-142-d4-role-distinct-additive-wall/`, `certificates/erdos-142-q24-cylinder-hypograph-wall/`, `certificates/erdos-142-q24-second-orbit-cylinder-hypograph-wall/`, `certificates/erdos-142-q6-pair-coordinate-walls/`, `certificates/erdos-142-q6-global-potential-walls/`, `certificates/erdos-142-q6-all-maximizer-three-row-torsion-wall/`, `certificates/erdos-142-q6-outer-code-tensor-wall/`, `certificates/erdos-142-q6-coordinate-d4-product-wall/`, `certificates/erdos-142-q6-117-cell-six-deletion-wall/`, `certificates/erdos-142-q6-117-cell-loopless-transition-wall/`, `certificates/erdos-142-q6-117-cell-percell-affine-wall/`, `certificates/erdos-142-q6-117-cell-bounded-dilation-wall/`, `certificates/erdos-142-q6-117-cell-transition-spectral-wall/`, `certificates/erdos-142-q6-m7-cellu-restricted-wall/`, `certificates/erdos-142-q6-m7-deletion-fence/`, `certificates/erdos-142-q6-m7-orbit-free-selector/`, `certificates/erdos-142-q6-m7-unit-girth-six-wall/`, `certificates/erdos-142-q6-m7-unit-k8-deletion-fence/`, `certificates/erdos-142-q6-m7-k8-microbox-deletion-fence/`, `certificates/erdos-142-q6-m7-redesign-torsion-wall/`, `certificates/erdos-142-q4-affine-order4-line-wall/`, `certificates/erdos-142-q7-q8-unit-hypercycle-walls/`, `certificates/erdos-142-q3m-torsion-triangle-wall/`, `certificates/erdos-142-interior-torus-torsion-wall/` | q=4, q=6, q=7, and q=8 maximum-mass D4 lanes closed for arbitrary global potentials; the 117-cell lead is now closed for every bounded one-block potential and every unrestricted-endpoint unweighted transition graph with a fixed endpoint/edge table; state lifts, endpoint-pruned or position-dependent languages, carving and deformation remain live; no new bound, 2026-08-18 |
| *(add your lane)* | | | |

## Erdős-142 — active multi-lane, read before touching

Three lanes hit #142 from different angles. **The verified floor (don't re-lose it):**
geometry `sha256 607841…92ada`; complete full-dim class = **12,349 cells**
(`sha256 35fb1967…a859b6`) LOCKED; **affine-family no-go** (34-term rational
vertex-Farkas) VERIFIED ⇒ any working potential must be genuinely quadratic. No
`r_3(N)` bound; #142 headline is an asymptotic WALL. All this is packaged, frozen,
and replayable in `certificates/erdos-142/` (`python3 verify.py`).

**The incident (why rule 3 exists):** the stronger "additive-local no-go" proof
objects were UNTRACKED working-tree files; a later run overwrote them and they are
gone from both working copies — a result that was replayed-clean 2026-07-13 is now unbacked.
Commit your certs.

## 2026-08-18 — Erdős 142: bounded-potential dilation wall

`certificates/erdos-142-q6-117-cell-bounded-dilation-wall/` closes the fixed
full 117-cell union for every bounded single-valued physical potential under
the pointwise raw-canonical torus coercivity hypothesis.  Two strict-interior
families on cells 93 and 91 give

```text
D(3t)-D(t) >= 144-96t,       0<t<1/3.
```

At `t_n=(1/4)/3^n`, finite telescoping forces linear growth of a difference of
bounded potential values.  No affinity, continuity, closure face or limiting
argument is used.  Primary and hostile independent replays reconstruct the
physical points, carries, raw costs and finite contradiction and reject metric
and role-order mutations.

This requires the inequality pointwise, not merely almost everywhere, and the
unchanged full cell union.  Graph-restricted paths, carving/deformation,
unbounded potentials, integer transfer and a new `r_3(N)` bound remain outside
scope; Problem 142 remains unsolved.

## 2026-08-18 — Erdős 142: universal fixed-state transition spectral wall

`certificates/erdos-142-q6-117-cell-transition-spectral-wall/` supersedes the
complete-loopless-only result for unweighted directed graphs with unrestricted
relevant endpoints and a fixed endpoint/edge table.  There are 187 bad cell
pairs: a common successor or predecessor turns two local rows into an exact
two-row `G,J` Farkas contradiction.  Avoiding the walls makes the two
outneighborhoods disjoint on a 27-edge bad-pair matching.  The solver-free
Perron-vector sum then gives `rho<=90`, below the required `441/4` gate.  An
independent replay needs only seven pairs and obtains `rho<=110<441/4`.

Weighted/repeated-label state lifts, endpoint-pruned languages omitting the
two-block witnesses, position-dependent tables, within-edge functions,
carving/deformation and integer transfer remain live.  No new `r_3(N)` bound
or solution of Problem 142 is claimed.

## 2026-08-18 — Erdős 142: per-cell residual-affine wall

`certificates/erdos-142-q6-117-cell-percell-affine-wall/` strengthens the
fixed 117-cell continuum fence from one offset per cell to `117` offsets plus
four independent residual-affine slopes in every cell (`585` free features).
Two necessary one-sided closure inequalities, at ordered triples
`(105,91,91)` and `(105,105,91)`, cancel every feature coefficient and have
scaled right sides `216` and `-72`; their positive sum is `0>=144`.

The theorem uses two rows of a deterministic one-row-per-compatible-triple
closure subledger.  It does not claim that the `98,167` frozen rows are the
full all-vertex ledger.  The primary replay rebuilds the cells, closure
vertices, carries, row order, geometry and all `585` incidences; a separate
direct cross-check replays the two rows and explicitly rejects any
arbitrary-physical-potential inference.

This affine certificate is superseded on the unchanged one-block union by the
bounded-potential dilation wall above.  Pair/state lifts, partial carving,
support deformation and integer transfer are not consequences of this row.

## 2026-08-18 — Erdős 142: complete-loopless transition wall

`certificates/erdos-142-q6-117-cell-loopless-transition-wall/` strictly
extends the fixed 117-cell offset model to the complete loopless 117-state
path language.  Its position-independent potential has arbitrary endpoint
tables `g[c]` and directed transition tables `H[a,b]`; additive cell offsets
are a special case.  The path density has Perron base
`116/6^4=29/324>(7/24)^2`.

Five exact two-block rows with weights `(1,2,1,1,1)` cancel every scaled
endpoint and transition coefficient and leave `0>=1032`.  Alternating common
tail states `0,1,0,...` extend the same contradiction to every length `m>=2`.
Primary and separately written standard-library replays reconstruct the
117-cell decoder, continuous carry rows, exact Farkas incidence, density gate,
and common-tail formula, with planted failures and input nonmutation.

This complete-loopless certificate is superseded for unrestricted-endpoint
0/1 graphs by the transition spectral wall above.  Endpoint-pruned languages,
state lifts, position-dependent tables and within-edge functions remain open.

## 2026-08-18 — Erdős 142: 117-cell six-deletion wall

`certificates/erdos-142-q6-117-cell-six-deletion-wall/` freezes the exact
negative result for the new `117/1296` four-dimensional `q=6` alphabet.  The
full alphabet beats the four-dimensional EHPS product gate `(7/24)^2` by
`1/192`; deleting six cells still beats it by `1/1728`, while seven deletions
miss it.  The verifier reconstructs all `98,167` compatible `6^2`-scaled continuous
cell-triple rows for potentials `F=2||x||^2+g[cell]` and replays `943` positive
integral Farkas rays.  Any feasible deletion must hit every ray's semantic
cell support.  A hash-bound `29,980`-node exhaustive branching and
disjoint-packing proof certifies that no deletion set of size at most six does
so.  Therefore every gate-preserving whole-cell subcollection is impossible
in this potential class.

Scope is deliberately narrow: this does not exclude within-cell, pair,
graph-state/cocycle or arbitrary physical potentials, partial carving,
replacement/deformation, another quotient, or another support.  It gives no
integer construction or new `r_3(N)` bound; Problem 142 remains unsolved.  The
next live tests are repeated-label/weighted state lifts, endpoint-pruned or
position-dependent languages, and support carving/deformation.

## 2026-08-17 — Erdős 142: recursive signed-slack capacity lane opened

Research note: [`atlas/erdos-142-recursive-capacity.md`](atlas/erdos-142-recursive-capacity.md).
Naslund's public 2023 slide deck was recovered and visually audited. It exposes a
recursive weighted-copy/closed-loop capacity mechanism that is more specific than
the later manuscript citations. The P142 translation is a conditional direct
outer-code lemma: for role-dependent EHPS supports, the worst raw-Euclidean
coercivity slack factors across physical two-dimensional torus blocks, and every
ordered codeword triple must have nonnegative summed minimum slack. The mass gate
is actual union mass `> (7/24)^L`, not a cardinality-exponent ratio.

First exact branch result: `certificates/erdos-142-mirror-core-additive-wall/`
rules out both role orientations of the two active words `(P3,B,B)` and
`(B,B,P3)` when the roles contain the exclusive q=24 cores of the EHPS tile
and its coordinate transpose. The stdlib Farkas replay covers every disjoint
allocation of the 53 overlap points, including all 36 cardinality allocations
whose finite union mass beats `(7/24)^3`; this is an additive role-potential,
finite-q wall only. It does not exclude a non-additive global 6D potential or
globally deformed five-role supports.

Second exact branch result:
`certificates/erdos-142-d4-role-distinct-additive-wall/` rules out the
highest-mass assignment in the exhaustive q=24 D4 image screen,
`(P1,P2,P3,B,K)=(7,7,7,6,7)`. Its five cylinders are pairwise disjoint and
have exact union count `21,653,735 > 4,741,632`, but a 622-row positive
integer Farkas combination cancels all 815 **role-distinct** potential
variables. The semantic stdlib replay rebuilds every support, word, midpoint,
carry, raw cost and mass term, and an independent implementation agrees. This
is stronger than the shared-grid-point LP screen, but remains one finite D4
assignment and one additive ansatz.

Third exact branch result:
`certificates/erdos-142-q24-cylinder-hypograph-wall/` closes the same
top-D4 assignment under the strictly larger **cylinder-position additive**
model. Each of the five disjoint cylinders and each of its three physical
coordinate positions receives an independent 163-point potential table, for
2,445 `G` variables. An exact local-hypograph reformulation adds 375 minimum-
slack variables and is equivalent to exhaustive factored pricing. The frozen
771-row positive Farkas combination (662 local witness rows and 109 active
sum rows) cancels all 2,820 coefficients and leaves a strictly negative exact
right side. The stdlib semantic replay reconstructs all 125 ordered sum rows,
midpoints, carries, raw costs, D4 mass, and ten planted failures; a separately
written implementation agrees. This remains finite q=24 and separable across
the three physical coordinates: arbitrary 6D, pair-interaction, and recursive
potentials remain open. The second maximum-mass orbit is handled next.

Fourth exact branch result:
`certificates/erdos-142-q24-second-orbit-cylinder-hypograph-wall/` closes
the second inequivalent maximum-mass assignment `(7,6,7,6,7)` under the same
2,820-variable cylinder-position additive model. Its compact semantic packet
has 816 selected local rows, all 125 ordered sum rows, and 931 positive integer
Farkas multipliers. Exact cancellation leaves a strictly negative right side;
eight planted corruptions are rejected, and a separately written stdlib replay
agrees. The verifier also reruns the complete `8^5` mass census and proves that
the 16 maximizers are exactly the disjoint eight-member symmetry orbits of
`(7,7,7,6,7)` and `(7,6,7,6,7)`. Paired with the third branch certificate,
this closes every maximum-mass D4 assignment under cylinder-position
additivity. It remains finite q=24 and does not touch pair-coordinate,
arbitrary 6D, recursive, deformed-support, or continuum potentials.

Fifth exact branch result:
`certificates/erdos-142-q6-pair-coordinate-walls/` moves one rung beyond
coordinate separability. At q=6, each of the five cylinders gets independent
pair tables `H[c,01]`, `H[c,02]`, and `H[c,12]`, for 1,215 variables. The two
named representatives A=`(7,7,7,6,7)` and B=`(7,6,7,6,7)` each have exact
union count 3,645 and normalized mass `5/64`, beating `(7/24)^3` by the ratio
`1080/343`. Exact semantic Farkas packets use 1,067 and 1,071 genuine global
midpoint rows respectively; positive integer combinations cancel every pair
variable. The primary verifier rejects 16 planted corruptions, a separately
written replay agrees, and an independent model audit confirms all 125 ordered
word triples/even-q branches were present in discovery. This is a finite q=6
wall only: it neither transfers to q=24 nor excludes arbitrary 6D potentials.

Sixth exact branch result:
`certificates/erdos-142-q6-global-potential-walls/` closes those same two
named q=6 representatives with **one independent potential value on every
union vertex**. The five cylinders are pairwise disjoint, so this is an
unrestricted 3,645-variable global potential, not a separable ansatz. A fresh
isolated CEGAR reconstructed all 1,128,545 actual modular-midpoint witnesses.
For A=`(7,7,7,6,7)`, three unit-multiplier rows already cancel to the transparent
contradiction `0 >= 20+20+8 = 48`; for B=`(7,6,7,6,7)`, a 646-row primitive
positive integer ray cancels every variable. The primary stdlib verifier
rejects 18 planted corruptions, and a separately written Luna replay rebuilds
both finite models and the exact cancellation without importing discovery
code.

Scope is deliberately narrow. An exact `8^5` q=6 census finds 256 maximum-mass
assignments, and global D4 transports of A's tiny three-row cycle hit only 32;
224 lie outside that screen. B uses its separate 646-row ray. Thus this is not
a classification of every q=6 maximizer and does not transfer to q=24/q=48,
recursive state, support deformation, or continuum thickening. A q=8
pair-coordinate preflight is mass-positive and technically tractable, but its
current factorized pricing costs about 85 seconds per orbit per CEGAR round;
acceleration is in progress. No finite survivor has been produced.

Seventh exact branch result:
`certificates/erdos-142-q3m-torsion-triangle-wall/` explains and generalizes
A's q=6 three-row ray. For every `q=3m`, `m>=2`, the top assignment
`(7,7,7,6,7)` contains an explicit W2/W3 3-torsion triangle whose three raw
costs are `m^2,m^2,4m^2`. The potential coefficients cancel and leave the
normalized contradiction `2/3`. This includes q=24 and q=48, and upgrades the
top q=24 representative from an additive wall to an arbitrary-global wall.
The symbolic stdlib replay proves every strict support incidence for all
`m>=2`; a separately written implementation agrees. Exhausting q=6 shows the
full W2/W3 torsion template hits 128 of the 256 maximum-mass assignments,
exactly those with intersecting P2/P3 supports. The earlier 32 count concerned
only global D4 transports of one planted triangle; a separate fast sweep that
called 32 the complete count used 2D point labels instead of full cylinder
vertices and was retracted.

Eighth exact branch result:
`certificates/erdos-142-interior-torus-torsion-wall/` removes the finite
family's seam/boundary escape. Fixed normalized points at q=`120n` have image
seam margin `1/8` and finite/limiting EHPS tile-face margin at least `1/30`.
They give torus carries `(-1,-1),(0,1),(1,0)` and normalized raw costs
`2/9,5/9,5/9`, so any arbitrary potential on the W2/W3 subunion would imply
`0 >= 4/3`. This is a continuum wall for the modular-midpoint/raw-canonical
model stated in EHPS Proposition 2.2, not for a different ordinary-Euclidean
midpoint predicate. The primary verifier proves the q=`120n` family
symbolically, rejects eight planted corruptions, and an independent exact
implementation reconstructs all limits and D4 inverses. It remains a no-go
for one role assignment, not a construction or `r_3(N)` bound.

Ninth exact branch result:
`certificates/erdos-142-q6-all-maximizer-three-row-torsion-wall/` completes the
finite q=6 maximum-mass classification at the unrestricted-global-potential
level. The exact `8^5` census has 256 mass-3,645 assignments, partitioned into
32 global D4 orbits. Each maximum union is the disjoint union of five
729-point cylinders, so one value per full union vertex is an arbitrary
potential, not a separable ansatz.

For an ordered cylinder pattern `(a,b,c)`, the three rows centered at `Y`,
`X`, and `Z` cancel on the full six-dimensional vertices `X,Y,Z`. Direct
enumeration of all 125 patterns finds positive modular 3-torsion cycles for
the 120 non-diagonal patterns; each such pattern hits all 256 maximizers. Only
`(0,0,0)`, ..., `(4,4,4)` have zero positive-cycle count. Therefore every
maximum-mass q=6 D4 assignment is impossible for any real-valued potential
on its five-cylinder union. A separately written replay retains the cylinder
label plus full vertex, checks carries/raw costs/coefficient accumulation,
and rejects the earlier local-point-merging failure mode.

This closes one finite quotient and support family only. It does not transfer
to higher q, jointly deformed supports, recursive state, or a new integer
construction, and gives no `r_3(N)` bound.

Tenth exact branch result:
`certificates/erdos-142-q6-outer-code-tensor-wall/` closes the full Cartesian
outer-code extension of every maximum-mass q=6 assignment.  In each outer
coordinate the maximum assignment may vary arbitrarily, provided it is fixed
across codewords.  For every non-diagonal local label triple, the all-pattern
census supplies three midpoint rows whose full six-dimensional potential
coefficients cancel and whose normalized right side is at least `2/3`.
Synchronizing those rows across the coordinates where an outer triple differs,
and padding diagonal coordinates with zero-cost rows, gives three genuine
global midpoint rows.  They cancel one completely arbitrary, nonseparable
potential on the full superblock and leave contradiction at least
`(2/3)|D|`, where `D` is the non-diagonal coordinate set.

Thus any outer code with two distinct words dies by the ordered triple
`(u,v,v)`.  A singleton survives the obstruction but has density
`1/64 < (7/24)^3` per local q=6 cylinder, so it cannot pass the supplied mass
gate at any product length.  Primary and separately written stdlib replays
enumerate all 32,768 assignments, all 256 maximizers, 30,720 local pattern
cycles, coordinate-dependent maximizers, full carries and raw-cost additivity,
and reject planted coordinate-projection and occurrence-label aliasing errors.
This theorem covers full Cartesian products only; correlated non-product
subblocks, codeword-dependent geometry, deformed supports, scalar digit carry,
and construction-to-integers transfer remain open.

Eleventh exact branch result:
`certificates/erdos-142-q4-affine-order4-line-wall/` closes every maximum-mass
q=4 D4 assignment for an arbitrary global potential.  The exact quotient tile
has four points.  The complete `8^5` census finds maximum union mass 320,
attained by 256 assignments in 32 global-D4 orbits; every maximum union is the
disjoint union of five 64-point cylinders and has density `5/64`, exceeding
the supplied `(7/24)^3` gate by the ratio `1080/343`.

Every orbit representative contains a full affine order-four line
`A_j=A_0+j d` in `(Z/4Z)^6`.  Four adjacent midpoint rows around that line
cancel every value of one arbitrary global potential and leave
`2||A_0-A_2||^2+2||A_1-A_3||^2>0`.  This is a transparent cyclic-torsion
lemma, not a numerical LP conclusion.  Primary and separately written stdlib
replays exhaust all assignments, 4,736 representative affine lines, exact
carries/raw costs, D4 transport to all 256 maximizers, the mass gate, and eight
planted failures.  The wall is finite q=4 only and does not exclude deformed
supports, correlated subcylinders, continuum thickening, scalar digit carry,
or integer transfer.

Twelfth exact branch result:
`certificates/erdos-142-q7-q8-unit-hypercycle-walls/` identifies and certifies
the common structural obstruction behind the finite-quotient walls.  A
balanced midpoint hypercycle is a finite family of modular midpoint rows in
which every physical vertex occurs with total coefficient zero.  If the raw
endpoint cost is positive, summing the rows contradicts the existence of one
arbitrary, nonseparable potential on the whole cylinder union.

At q=8 every one of the 32 maximum-mass D4 orbits contains a full affine
order-four line.  The four adjacent midpoint rows around the line cancel the
global potential; order-eight lines independently close the same 32 orbits.
At q=7 the complete line census finds no full order-seven line in any maximum
orbit.  The apparent survivor nevertheless contains the five affine points
`V_i=A+c_i d`, with `c=(0,1,4,3,6)`, whose endpoint cycle and center
permutation `pi=(2,4,0,1,3)` give five midpoint rows.  Every point appears
twice as an endpoint and once as a center, so the coefficients cancel and all
five costs are positive.  This template is minimal in the connected
unit-cycle/permuted-center class over `F_7`: lengths three and four have only
the constant kernel, while length five has exactly five nonconstant-kernel
permutations.

The primary and separately written stdlib replays reconstruct the exact q=7
and q=8 supports, all 32,768 role assignments, 256 maximizers in 32 global-D4
orbits at each quotient, exact mass gates, complete factorized line/pattern
censuses, carries, raw costs, physical-variable cancellation, D4 transport,
and planted semantic failures.  This closes only the exact finite q=7/q=8
maximum full-cylinder families.  Deformed supports, correlated subblocks,
continuum limits, scalar digit carry, and integer transfer remain open.

Thirteenth exact branch result:
`certificates/erdos-142-q6-coordinate-d4-product-wall/` closes the full-product
version of codeword-dependent D4 geometry at q=6.  For every ordered unequal
pair of the eight local D4 images, an exact local census supplies a
nondegenerate cyclic 3-torsion triple in `S_g x S_g x S_h`.  Tensoring those
witnesses over the coordinates where two D4 words differ, with diagonal
anchors elsewhere, gives three physical midpoint rows whose arbitrary-global-
potential coefficients cancel and whose raw right side is positive.

Therefore a potential-compatible collection of coordinate-dependent full
product words has at most one distinct word.  Its density is
`(1/4)^L < (7/24)^L`, so it cannot pass the supplied mass gate.  Primary and
separately written stdlib replays agree on all 324 cyclic triples, all 56
nondegenerate ordered pair buckets, the arbitrary-length tensor construction,
exact carries/raw costs, physical cancellation, and live corruptions.  This
retires the six-coordinate chain candidate but does not cover genuinely
correlated non-product subblocks, graph/height lifts, deformed supports,
higher quotients, continuum thickening, scalar digit carry, or integer
transfer.

Fourteenth exact branch result:
`certificates/erdos-142-q6-m7-cellu-restricted-wall/` closes the continuous
half-open q=6/M7 candidate for the cell-specific offset class
`H=2||x||^2+G(cell,pattern)+sum_i U(cell,i,coarsepoint_i)`.  The packet
reconstructs 24 selected cells, 148 cell/parity states, and 358 positive
integer Farkas rows.  Every displayed feature coefficient cancels exactly
and the weighted right side remains positive.  A separately written replay
also records 946 nonzero unrestricted physical aggregates and 60 nonzero
quadratic aggregates.  Those are scope tripwires: this is not a wall for an
arbitrary physical potential, a general quadratic or pair interaction,
recursive state, support deformation, continuum-wide nonexistence, integer
transfer, or an `r_3(N)` bound.

Fifteenth exact branch result:
`certificates/erdos-142-q6-m7-redesign-torsion-wall/` closes the exact
eight-cell redesign `(38,3),(41,3),(42,3),(44,3),(49,3),(50,3),(52,3),
(56,3)` for an arbitrary physical potential under the retained raw-canonical
torus midpoint convention.  Its exact mass is `245/373248 > (7/24)^6`.
Three distinct physical vertices give cyclic midpoint rows whose arbitrary-H
coefficients cancel and whose raw right sides sum to 144.  Adding any common
offset in `(0,1/6)^12` preserves strict box interiors, carries, and the
normalized contradiction `0>=4`, so this is not a grid-boundary artifact.
Primary and separately written stdlib replays agree.

This is a wall for the exact full union, not a deletion fence.  The displayed
order-three step has only 45 disjoint three-orbits, while the gate slack is
`5679639/64` q=6 boxes; other steps and the minimum deletion needed to kill all
cycles are not classified.  The rows use nonzero modular carries and make no
ordinary-Euclidean, integer-transfer, or `r_3(N)` claim.

Sixteenth exact branch result:
`certificates/erdos-142-q6-m7-deletion-fence/` supersedes that deletion caveat
for the same eight-cell support.  A frozen cross-step matching contains 102,636
pairwise box-disjoint order-three orbits, with 307,908 distinct physical boxes.
Every orbit has three positive cyclic raw-canonical rows cancelling an arbitrary
physical `H`.  Pulling measurable deletions back along the common-offset cube
forces at least one q=6 box-volume of deletion per matched orbit.  Therefore
the retained mass is at most `1326204/6^12`, below `(7/24)^6` by exactly
`889065/(64*6^12)`.  Primary and separately written stdlib replays verify all
102,636 records and the exact measure arithmetic.  This is a branch-sensitive
torus fence for one support, not an ordinary Euclidean theorem, integer
transfer, new `r_3(N)` bound, or solution of Problem 142.

Seventeenth exact branch result / research fence:
`certificates/erdos-142-q6-m7-orbit-free-selector/` pivots from potential
tuning to support design in the correct full 448-cell q=6/M7 universe.  The
frozen 28-cell selector has 1,405,512 boxes, normalized mass `241/373248`, and
clears `(7/24)^6` by `5743/191102976`.  Order-three translations preserve the
exact parity residue; reconstructing all 42 local channels gives the exact
word-triple criterion `v>0` and `t<=r<=t+6-v`.  Standard-library primary and
independent replays test all 1,102 ordered selected triples and find zero
nontrivial orbits.  Hence the 102,636-orbit deletion mechanism for the old
eight-cell support has no edge at all here.  This is deliberately classified
as a research fence: it does not exhibit a potential or rule out longer
physical hypercycles, and the separate CP-SAT orbit-free maximality result is
not promoted without a solver-independent proof object.  The live bottleneck
is arbitrary physical `H`; no continuum, integer-transfer, or `r_3(N)` claim.

Eighteenth exact branch result:
`certificates/erdos-142-q6-m7-unit-girth-six-wall/` closes that arbitrary-`H`
bottleneck for the exact 28-cell selector.  Six distinct physical q6 vertices
in selected cells support six unit midpoint rows with coefficient vector zero
at every actual vertex and raw RHS values `68,56,32,32,56,68`; hence their sum
is the contradiction `0>=312`, normalized `0>=26/3`.  A common strict offset
in `(0,1/6)^12` preserves the carries and costs.  Independent exhaustive
replays also enumerate all 6,516 endpoint-degree-two unit templates with at
most five rows: each of the 1,511 positive templates forces a fixed
order-three orbit, which the selector lacks.  Thus its unit Farkas girth is
exactly six.  This retires the exact full selector, not nearby redesigned
supports or non-unit/recursive mechanisms; there is no ordinary Euclidean or
integer transfer, new `r_3(N)` bound, or solution of Problem 142.  The next
support-design screen must exclude this six-row template as well as
order-three translations before any potential search is meaningful.

Nineteenth exact branch result / deletion fence:
`certificates/erdos-142-q6-m7-unit-k8-deletion-fence/` closes every
mass-above-gate whole-cell subset of the subsequent 22-cell repair lane.
Three explicit eight-row endpoint-degree-two packets have pairwise-disjoint
required supports `{33:3,45:0,49:0}`, `{45:1,19:6,26:6}`, and
`{30:3,20:5,34:5}` and raw totals `216,144,288`.  Each cancels arbitrary
physical `H`, and a common strict offset preserves its carries and costs.
Avoiding all three costs at least `5,832+5,832+69,984=81,648` boxes, leaving
at most `1,288,872`; the exact gate comparison is
`1,288,872*64-85,766,121=-3,278,313`.  This is a solver-free implication from
positive witnesses and retires the entire 22-cell deletion-repair family, not
partial-cell carving, replacement cells, deformation, recursive support,
ordinary Euclidean or integer transfer.  No new `r_3(N)` bound is claimed and
Problem 142 remains unsolved.

Twentieth exact branch result / measurable-carving fence:
`certificates/erdos-142-q6-m7-k8-microbox-deletion-fence/` closes the partial
carving caveat for the exact 22-cell repair support.  A frozen matching has
`30,425` positive balanced eight-row packets on `243,400` globally distinct
physical q6^12 microboxes.  For each packet, the full common offset cube
`D=[0,1/6)^12` preserves every carry and endpoint cost; the eight potential
rows cancel.  The complements of the eight retained offset slices therefore
cover `D`, forcing at least one box-volume unit of measurable deletion per
packet.  Global box disjointness makes the losses additive.  The remaining
measure is at most `1,370,520-30,425=1,340,095` box-volume units, and the exact
gate numerator is `1,340,095*64-85,766,121=-41`.  This retires arbitrary
measurable carving of the fixed support, not replacement cells, deformation,
recursive state, ordinary Euclidean or integer transfer.  No new `r_3(N)`
bound is claimed and Problem 142 remains unsolved.

A corrected q=8 pair-coordinate engine now prices both orbits in about five
seconds per round rather than 85, but 40 rounds remain `iteration-limit` with
negative slacks; no q=8 pair-coordinate LP theorem is claimed by that engine.
The separate balanced-hypercycle theorem above closes the exact maximum-mass
q=8 D4 unions for arbitrary global potentials. The q=6 D4 maximum-mass search is
now closed negatively at the arbitrary-global-potential level, but no finite
survivor has been produced.

Naslund's public deck states only the rounded capset rate `2.22`; the cited
`2.2208` manuscript remains unavailable publicly as of the audit.

`erdos142_solved: false`. `new_r3_bound: false`.

## 2026-07-24 — Erdős 142 / D15: two lemmas REFUTED, one theorem proved

Certificate: `certificates/erdos-142-kerpi-refutation/` (`python3 -I verify.py`,
~2 s, stdlib only, now wired into `make verify-certs`).

**If you are working the D15/PC-F lane, two laws you may be using are FALSE.**

1. **`ker π ∩ D = 0` — REFUTED** on CLOSED products (strongly connected,
   exit-free). Explicit nonzero integer circulation on **4 collar edges**
   (the minimal e₁−e₂−e₃+e₄ rectangle), checked directly against the
   definition on the full product: support ⊆ collar, `incidence_P·d = 0`,
   `π₀=π₁=π₂=0`, `d ≠ 0`. Referee sweep: 31,548 counterexamples in 873,264
   closed products at ≤7 states.
   *Mechanism:* per digit a collar circulation is a 3-index array and the
   three role projections are exactly its three 1-marginals, whose joint
   kernel is large. Flow conservation alone cannot carry the burden.

2. **`q ≥ dim ker π` — REFUTED.** This was the bridge from a `dim ker π`
   floor to a `q` floor, i.e. the route to excluding `q = 1`. It is not
   merely unproved — it is false. Witness `91f52f97…`: the certificate
   recomputes `dim D = 34 > 24 = 3·dim Z₁(B)`, which forces `q < dim ker π`
   (machine-checked bound: `q − dim ker π ≤ −10`). The referee lane
   separately reports the exact values `q = 732`, `dim ker π = 748`; those
   are **NOT re-derived** by the certificate. Forced by **counting**, with
   tiny exact inputs:

       ker π ⊆ Z  ⟹  q − dim ker π = rank(π|_Z) − dim D      (identity)
       im π ⊆ Z₁(B)³  ⟹  rank(π|_Z) ≤ 3·dim Z₁(B)
       ⟹  dim D > 3·dim Z₁(B)  forces  q < dim ker π

   For the witness `dim Z₁(B) = 8` and `dim D = 34 > 24`. `dim Z₁(B)` depends
   only on the base; `dim D` grows with the collar — so the inequality was
   never structural, only an artifact of small-collar objects.
   **A floor on `dim ker π` proves nothing about `q`.**

**PROVED replacement — THEOREM A.** If every collar edge has a diagonal source
`(0,u,u,u)` then `ker π ∩ D = 0`. (Diagonal rows are legal only from carry 0
and the product is deterministic, so a collar edge is determined by
(source,digit); `π₀` sends it to base edge `(u,a)` and `((0,u,u,u),a) ↦ (u,a)`
is injective, so `π₀` is injective on `ℚ^{E(C)} ⊇ D`.) 0 violations over
873,264 closed products. **Its converse is FALSE** — object `5da67053…` has
non-diagonal collar sources and still zero intersection, so source-diagonality
is sufficient, never necessary. For a per-object decision use the exact test
`dim(ker π ∩ D) = |E(C)| − rank[∂; π₀; π₁; π₂]` on collar columns (11–60
edges: milliseconds).

**Any per-object use of `q ≥ dim ker π` now requires BOTH** a `ker π ∩ D = 0`
certificate **AND** counting slack `3·dim Z₁(B) − dim D ≥ 0`.

**Untouched:** the `q = 1` hole itself — still 0 occurrences in >1.18M closed
products, still the unique absent value in 0..24. What is closed is one route
to excluding it; `q` must now be attacked directly.

`erdos142_solved: false`. `new_r3_bound: false`.

*Reported vs recomputed:* `verify.py` recomputes `dim Z₁(B)`, `dim D`,
`dim(ker π ∩ D)`, `rank(π rows)` and H1/H2/H3 on all four objects, in exact
rational arithmetic. All census figures in this section (31,548 / 873,264 /
0 Theorem A violations / >1.18M) and the exact `q` and `dim ker π` values are
**reported by the referee lane, not re-derived** by the certificate.

## 2026-07-26 - Erdos 142 / D15: the CONE obstruction, certified per object

Certificate: `certificates/erdos-142-cone-obstruction/` (`python3 -I verify.py`,
~0.5 s, stdlib only, wired into `make verify-certs`).

**Context, and a retraction of something this lane repeated for a long time.**
The construction gate needs a closed carry-triple product with quotient
signature `(q+,q-) = (1,0)` **and** a cone certificate. The first half now
EXISTS - 298 verified objects, the sealed engine's own `rank_gate` returning
quotient dimension 1 with `passes_quotient_one = True`. So **"q = 1 has never
been observed; the unique absent value in 0..24 across >1.18M closed products"
is STALE and must not be repeated** - it was a search-region artifact, not a
structural fact.

**This certificate is the second half, and it closes negatively.** For three
`q=1` objects it publishes a vertex potential `p` and tag multiplier `theta`
whose edge functional `Y(e) = p[t] - p[s] + <theta, tag(e)>` satisfies
`Y >= 0` on every edge and `Y > 0` off the collar. A cone point is a
circulation with zero tag, so `0 = sum Y(e)w(e) >= sum_nondiag Y(e) > 0` - a
contradiction, using only `w >= 0` and `w >= 1` off the collar. **No solver,
no coefficient cap, no integrality, no sigma-invariance, no reference to q.**
It replaces a CP-SAT INFEASIBLE verdict with a line anyone can audit.

**sigma was never the blocker.** The lane pursued `(1,0)` over `(0,1)`
precisely to obtain a sigma-invariant generator. A relaxation ladder shows:
baseline INFEASIBLE; **drop sigma-invariance -> still INFEASIBLE**; drop
zero-tag, or non-negativity, or the strict `>=1` -> feasible. The conflict is
zero-tag + non-negativity + strict positivity and survives dropping symmetry
entirely. Do not spend further compute on the `(1,0)`-vs-`(0,1)` distinction
for cone purposes.

**Scope, stated exactly.** The certificate settles the three named objects and
nothing more. It is **not** a theorem that every `q=1` product has an
infeasible cone; none is offered. Separately measured but NOT certified here:
collar-LP infeasibility across all 298 known `q=1` objects with the sealed
engine agreeing 298/298 - a measurement over objects found so far.

`erdos142_solved: false`. `new_r3_bound: false`.

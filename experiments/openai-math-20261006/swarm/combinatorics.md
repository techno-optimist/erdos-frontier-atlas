# Combinatorics and geometry: theorem-level connections

This is a research overlay over the atlas, pinned to OpenAI source commit
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`. Nothing here changes a canonical
status, production-graph edge, or frozen certificate. The linked JSON records
source hashes and typed edges. Reading a scope document establishes what its
author claims, not that the proof is correct. No external code, Lean rebuild,
or Comparator verification was run.

## The strongest new contacts

| Family | Atlas target | Exact contact | Boundary |
|---|---|---|---|
| F159 | P3 | Divergent harmonic mass forces APs of every finite length. | No exact finite progression-free table follows. |
| F160 | P138 | The uniform eventually-valid lower bound forces superexponential van der Waerden growth. | The threshold is existential; W(2,7) is untouched. |
| F164 | P172 | Every finite coloring admits arbitrarily large finite sets whose nonempty subset sums and products share a color. | No infinite sums-and-products set is asserted. |
| F171 | P181 | Hypercube Ramsey number is at most an absolute constant times its vertex count. | Does not force a cube in a specified color on exactly 2^n vertices. |
| F172 | P174 | Tensor-field classification, positive criteria, and spherical non-Ramsey examples. | High-dimensional Ramsey is different from fixed-plane two-color questions. |
| F181 | P184 | A universal linear number of cycles and edges partitions every graph's edges. | Does not give the optimal constant or prescribe component shapes. |
| F184 | P802 | For fixed r>=4, K_r-free graphs satisfy alpha >= c_r n log(d)/d using average degree. | Constants depend on r; no exact small graph follows. |
| F189 | P551 | Exact cycle-clique formula throughout m>=n>=3, with the (3,3) exception. | Cannot be applied to fixed C4 and growing clique size. |
| F166 | P1083 | At least c_d n^(2/d) distances for every fixed d>=3. | Constants depend on dimension; not the planar logarithmic problem. |
| F084 | P120 | Avoidance of any fixed geometric sequence, and all infinite sets containing an affine copy of it. | General infinite sets remain outside the theorem. Lean scope is only dyadic. |
| F156 | P505 | Borsuk failure in dimension nine. | An improvement of an already-disproved conjecture's dimension surface. |
| F158 | P508 | Narrows the plane's chromatic interval to 6 through 7. | Does not choose between 6 and 7. |
| F167 | P90 | A uniform exponent beta<4/3 for planar unit-distance counts. | An upper-bound improvement, not a reversal of P90's recorded disproof. |
| F170 | P986 | Sharp logarithmic exponents for fixed s>=5 off-diagonal Ramsey numbers. | Excludes s=3,4 and diagonal growth. |

The P802 correspondence is explicit in the manuscript introduction, not a tag
match. That introduction also explicitly says the F170 Ramsey papers are not
inputs to its proof. These are complementary bounds with different interfaces:
F170 controls maximal graph order in a fixed asymptotic regime; F184 controls
each input graph using its own average degree.

Sources for this table are the pinned [catalogue](../catalogue.json), the
scope files identified in [combinatorics.json](combinatorics.json), and the
same JSON's manuscript-introduction receipts. The no-Lean families F164,
F166 and F171 were checked in their manuscript abstracts or main theorems.
P174 and P508 are link-only atlas nodes; their official problem pages were
read through indexed primary-source results. No website statement prose is
copied into this repository.

## Two cross-domain compositions the tag graph misses

Let L(G) be the set of odd cycle lengths occurring in a graph G of infinite
chromatic number. The local licensed statement of P57 records the theorem
that sum over l in L(G) of 1/l diverges. Apply the external F159 reciprocal
statement to this set of positive integers. For every k, L(G) contains

    a, a+d, ..., a+(k-1)d,

with d positive; for k>=2, d is necessarily even. This says much more than
merely linking the words “graph” and “arithmetic progression”: a proved
property of the target graph supplies precisely the hypothesis of the
external theorem. It says nothing about these cycles sharing a vertex,
being induced, or lying in a graph of bounded finite order. It is an
informal conditional corollary, with no novelty claim.

F182 gives a second route from the same source set. If A is square-difference
free and |A intersect [1,N]| <= C N^(1-c), then its harmonic sum converges:
the contribution of [2^j,2^(j+1)) is at most
C 2^(1-c) 2^(-cj), a summable geometric series. Consequently L(G) cannot be
square-difference free. Two odd cycle lengths differ by m^2 for some
positive even m. Again the result concerns their lengths, not an embedding
of two cycles in a common structured subgraph.

The same summation explains why F159's quantitative all-fixed-k estimate is
a better reusable interface than its qualitative slogan. A bound
r_k(N) <= C_k N exp(-c_k (log N)^b_k), b_k>0, uniformly bounds harmonic mass
of every k-AP-free set. Even inserting a fixed power of log N leaves a
convergent dyadic series. This feeds P169's extremal harmonic-mass question,
but extracting its dependence on k or its exact small-k supremum remains
separate work. F160 plus the atlas's f(k)>=0.5 log W(2,k) yields the eventual
lower bound k log k/200000; that recovers a known growth shape with a weaker
constant, so it is not a new record.

## Geometry: genuinely different quantities

The F166 theorem is a constant-factor lower bound in each fixed dimension
at least three. Applying d=3 to a convex polyhedron gives n^(2/3), which is
far below P660's desired nearly n/2. Letting d vary in the theorem without
controlling c_d does not solve P1089, where dimension is the asymptotic
variable. F167's weak pinned planar result says most pins have n^(1-epsilon)
distinct distances, but n^(1-epsilon) is smaller than n/sqrt(log n) for
every fixed epsilon>0 and large n. Thus it does not settle P89.

There is a clean smaller consequence of F167's unit-distance result. A
similarity rescales any positive distance to one, preserving point count.
The multiplicity of every distance is therefore <= C n^beta with the same
constants. In P959, the gap between the largest and second-largest distance
multiplicities is at most that quantity. This is a valid conditional upper
bound; it is not a determination of the gap's asymptotic order.

F158's chromatic result would yield a finite non-five-colorable unit-distance
subgraph by graph-coloring compactness. That is an existence consequence, not
an extracted finite certificate. In particular chi>=6 does not force an
independence ratio below 1/5, so it cannot simply be promoted into the
independence/fractional-coloring question P1070.

F084 provides another exact inclusion transfer: if A contains an affine
copy of a geometric sequence, a set avoiding every affine copy of that
sequence also avoids every affine copy of A. The manuscript explicitly fixes
q before constructing the avoiding set. It makes no simultaneous statement
for all ratios and no assertion about arbitrary infinite A.

## The important blocked joins

- **F178 to P78 is mathematically obstructed.** Every degree-d graph has an
  independent set of at least n/(d+1) by greedy deletion. Fixed-degree
  Ramanujan families therefore have linear-size independent sets, whereas
  an explicit Ramsey family needs O(log n). The manuscript fixes d; its
  algorithmic exponent and size threshold may depend on d. One cannot let
  d grow and retain a polynomial-time theorem by silently changing quantifiers.
- **F170 to P77, P1030 or a small cell changes the regime.** The first
  argument s is fixed while t grows. It is not a uniform result along s=t,
  s=t+1, or t=5. It does not cover s=3 or s=4. An unspecified o(1) in a
  logarithmic exponent also does not by itself imply consecutive Ramsey
  ratios tend to one; adjacent spikes are compatible with such weak control.
- **F189 to P159 reverses the hypotheses.** The formula requires the cycle
  length to be at least the clique order. P159 fixes cycle length four and
  studies an unbounded clique order. Only a tiny initial segment overlaps.
- **F169 to P993 changes both object and graph class.** Elementary positivity
  concerns chromatic quasisymmetric functions of natural unit interval graphs.
  P993 concerns the independence polynomial of every tree. No transformation
  preserving the required coefficient inequalities has been supplied.
  The local P993 card also warns that log-concavity itself is false for trees.
- **F174/F181 to P743 drops prescribed shapes.** A thin spanning tree is
  whichever tree the theorem finds; a cycle decomposition uses cycles and
  isolated edges. Gyárfás packing specifies every tree shape and uses every
  edge exactly once. Neither result supplies that missing condition.
- **F181 to P583 loses the sharp constant.** Splitting every cycle into two
  paths gives only O(n) paths, while the target is ceil(n/2). Such linear
  path bounds already existed; it would be misleading to call this progress.
- **F180 to P1016 drops pancyclicity.** A Hamiltonian cycle alone supplies
  one length; a bipartite graph has no odd cycles at all. Barnette's special
  graph class cannot resolve a general minimal pancyclic graph problem.
- **F162 to P21 lacks edge count.** Cover number r makes the Ryser objects
  admissible in the intersecting-family minimization, but says nothing about
  minimizing their number of edges. Its existential prime thresholds cannot
  advance a small-r finite certificate.
- **F188 to P1009 changes the probability space.** Triangle removal starts
  from K_n and samples triangles. P1009 asks for a deterministic guarantee
  for every graph only slightly above a Turán edge threshold.

## Coverage of families without a justified atlas edge

The sweep also read F087, F155, F157, F161, F165, F168, F173, F175–177,
F179, F183, F185–187 and F190. An unmapped family is not assumed irrelevant;
it means this pass did not establish an exact atlas target or a useful
conditional transfer. Several are valuable audit targets in their own right:

- F161 identifies a fixed bipartite graph with 35 vertices and 66 edges,
  but the scope only asserts existence of a violating finite host. Extracting
  a concrete rational-density host would create a small, independently
  checkable artifact; this pass did not extract one.
- F157's Lean scope certifies only the linear list-coloring bound in terms
  of clique-minor order. The family title's Hadwiger and Colin de Verdière
  counterexample manuscripts require separate proof inspection.
- F165 treats topological crossings of continuous simple edge paths,
  counting repeated crossings as separate spatial points. A rectilinear
  crossing problem cannot inherit an equality without an additional argument.
- F175 compares two expectation thresholds with explicit large constants;
  F176 bounds a containment threshold by an expectation threshold times a
  logarithmic edge-count factor; F186 bounds threshold width for monotone
  relabeling-invariant graph properties. They respectively address the
  surrogate, location and width of a threshold. None gives exact finite
  existence certificates or transfers automatically to nonmonotone events.
- F179's circulant Hadamard classification is not the unrestricted Hadamard
  existence problem; its additional Lean statement covers only even Barker
  lengths. F187's Snaky theorem is a legal strategy against every legal
  Breaker move, but the selected theorem does not include the paper's
  finite-board restriction. The family number 187 has no relation to P187.

## What to do next

First audit the theorem definitions and dependencies for the direct matches
P138, P172, P181, P174, P184, P802 and P551. This work can supersede a research
question without pretending to have found a finite witness. P508 and P505
need narrower record labels. Then extract short corollaries such as the P57
compositions and P959 rescaling bound for independent review. Preserve the
explicit blockers: they are the graph's most useful protection against
spending a new theorem in a regime where it says nothing.

## Second wave: algorithms become tools only through exact reductions

The second sweep inspected F102, F103, F107, F109, F113, F115, F120, F126,
F130, F131, F138, F142, F235 and F239. It found one particularly clean
computational interface.

For a fixed P710/P860 instance, put the k divisibility obligations on one
side and ell candidate integers on the other. If ell<k, an injection is
impossible. Otherwise create a (k+1)-by-ell contingency table. Give each
real row sum one, each column sum one, and the final dummy row sum ell-k.
Set every allowed cell bound to one, and forbid precisely the real-row
cells where divisibility fails. Dummy cells are all allowed. A table
uniquely encodes a system of distinct representatives: the dummy row marks
exactly the unused integers. Conversely each representative system gives
one table. Thus F115's cell-bounded-table FPRAS estimates the number of
valid systems, with no factorial correction. This could measure robustness
of a finite interval and reveal where Hall obstructions nearly appear.
It cannot prove Hall's condition for every interval. Ordinary matching
already decides each fixed instance in polynomial time.

F120 might speed up those matching computations, but its almost-linear
algorithm is randomized and succeeds with probability at least 2/3.
Its every-execution runtime guarantee does not make every negative answer
correct. Positive outputs still need exact divisibility/distinctness checks,
and a universal absence claim needs a Hall witness or another deterministic
certificate. F138's 2^(0.49n) subset-sum result is similarly bounded-error;
moreover P1 concerns two colliding subset sums, so a precise reduction is
needed before importing a running-time exponent. Neither algorithm supplies
an extremal theorem merely by running faster.

F131's switch-chain bound is an actual quantitative sampling interface:
total-variation distance 1/4 by 2n^8 steps for each graphical degree sequence.
It could diversify graph candidates, but it does not condition on being a
tree, pancyclic, or another rare property. In a tree degree sequence, a simple
realization with n-1 edges can be disconnected and contain cycles; the
conditioning issue is real. The source scope excludes the paper's exact
uniform sampler. Random sampling never replaces exhaustive coverage.

The most concrete family dependency discovered is **F029 -> F142**. The
prime-field polynomial-factorization paper explicitly invokes the uniform
Hecke zero-free theorem from the primitive-roots companion. This is a manuscript-declared
input dependency, not independently audited logical necessity. It is still not a route to P699: factoring polynomials
over a finite field does not exclude actual integer smooth-part divisibility
configurations.

Other scope boundaries are consequential. F107 counts exact arithmetic
operations, not bit operations or practical crossover sizes. F109 gives a
bit-model improvement with exponent saving 2^(-182), which by itself is no
reason to replace a working multiplication library. F126's selected Lean
statements give superpolynomial semidefinite lower bounds, while the newer
paper advertises exponential bounds. F130's selected statement is only a
subsequential circuit saving for exact-complex Fourier transforms. F235's
selected k=3 hitting-time variance upper bound remains O(n log n), despite
the newer manuscript's linear-variance title. Its random-clause distribution
has no direct connection to the structured CNFs used for finite AP bounds.
F239 concerns independently sampled upper-triangular sign entries; an exact
incidence matrix in a carry-product certificate is not from that probability
space.

Finally, F190 does **not** match P150: the latter is the enumeration of
minimal vertex cuts, not a matrix or graph removal lemma. This explicit
negative edge records a lexical false positive before it reaches propagation.

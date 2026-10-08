# Independent analytic audit and extra connections

This is an independent model review of the conditional deductions in
`../CONNECTIONS.md`, against the pinned manuscript statements and the existing
atlas analytic interfaces. It is not a human review, a formal proof, an audit of
the external manuscripts' proofs, or a canonical status update. Source pin:
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`.

## Verdicts on the proposed deductions

### F003 to squarefree global energy: PASS, conditional

Assume zeta is zero-free in Re(s)>q, with 1/2<=q<1. On any fixed interior
line sigma>=q+delta, the claimed reciprocal bound |1/zeta(s)|<<|t|^eta is
valid for every eta>0. The missing ingredient in many analogous arguments is
indeed growth rather than mere holomorphy, but the note supplies it correctly.
For large height take a disk centered at 2+it whose outer radius stays strictly
below 2-q. A normalized logarithm exists. Polynomial growth bounds its real
part by O(log |t|); Borel-Caratheodory bounds its modulus on a smaller disk.
The Euler logarithm is bounded on a fixed small disk. Three-circles on the
logarithm gives O((log |t|)^r), r<1, at every fixed interior radius. Exponentiating
bounds both zeta and its reciprocal by |t|^eta. Small heights are compact
and the pole at 1 gives a zero, not a pole, for the reciprocal.

For a>q/2, convexity and division by s give
F(a+it)<<|t|^{-(1+a)/2+eta}+|t|^-1. Its square is integrable when 2eta<a.
The note's test-function contour shift is essential and is present: it
identifies this inverse transform with the original squarefree error.
Consequently J_a<infinity and V(X)<=X^(2a+1)J_a. With q=7/8 this is
V(X)<<X^(15/8+epsilon). The exact endpoint epsilon=0 is not established.
No simplicity or derivative-of-zeta hypothesis is being hidden.

Sources checked: F003 main theorem and logarithmic-control lemma; all of
`astra-rh-969-20260912/ANALYTIC_TARGET.md`. The result is not the P969
pointwise quarter-power estimate and does not close its mixed-moment residual.

### F003 plus variance to a larger zero-free region: PASS, conditional

The existing transfer assumes, for every nu>0, the actual uniform increment
variance upper bound through all integer H<=X^theta; a favorable finite-prime
phase model is insufficient. It gives continuation past a=1-3theta/4 and,
when 1/4<a<1/3, zero exclusion in the open strip (2a,2-4a).

Combining this with exclusion of beta>q covers every beta>2a exactly when
q<2-4a. For q=7/8 this requires theta>23/24. At theta=24/25 the strip is
(14/25,22/25), which overlaps (7/8,1). Thus the claimed 14/25 bound checks.
The strict inequality matters: at theta=23/24 the possible beta=7/8 line
falls into neither open exclusion region. A fixed theta does not bootstrap
to RH merely by repeating the same implication.

The note correctly labels the variance hypothesis missing. In particular,
the atlas's 4/7-epsilon range is far below even theta>8/9, the threshold for
this invariant-strip argument to produce a nonempty strip.

### F007 to fixed-shift Mobius cancellation: PASS, conditional

For fixed z, the truncated squarefree mask S_z is periodic modulo
M=product_{p<=z}p^2. The discrepancy from mu^2 is bounded by the count of
integers divisible by a prime square p^2 with p>z, which is O(X/z+sqrt X).
The shifted mask has the same estimate with constants depending on fixed h.
In each residue class the two forms are Mn+r and Mn+r+h; their determinant
is Mh!=0. The source explicitly permits noncoprime coefficients and all
nonnegative intercepts, so zero/nonunit residue classes are not a gap.
The possible n=0 starting term changes a sum by only O(1).

For fixed z the finite sum of correlations is o(X), regardless of how large
the implied constants are. Taking X to infinity and then z to infinity gives
o_h(X). The limit order precludes a quantitative Mobius logarithmic saving
without further uniformity. The subsequent fixed-H variance H/zeta(2) is
correct, using squarefree density on the diagonal and finitely many vanished
correlations off the diagonal.

### F021 to primorial and first-missing gaps: PASS, conditional

The source defines h(k) over all integers with at most k distinct prime
divisors and all translated intervals. Thus j(P(z))<=h(pi(z)) directly.
PNT then gives z^2/[(log z)^2(log log z)^2], with an unspecified constant.
The conversion log log(3pi(z))~log log z is correct.

For k>=1 all integers coprime to P_k are odd, so their gaps are even. No
gap exceeds j(P_k). Therefore the even number j(P_k)+2 is missing and
its least missing positive even gap a(k) is at most that number. This does
not assert that smaller gaps all occur; it does not locate any finite cell.
No distinct-representative/Hall conclusion for P860 follows.

**No mathematical flaw requiring retraction was found in these four scoped
conditional deductions. This verdict does not validate any external proof.**

## Additional exact statement match: F076 negates P1150

The pinned [F076 scope](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/076.md)
states an all-sufficiently-large-length existence theorem for real-sign
Littlewood polynomials with arbitrarily small relative excess above the
Parseval lower bound. Its
[comparator](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/ComparatorChallenges/AsymptoticallyMinimalLittlewood.lean)
quantifies signs on Fin N and all unit complex z, with bound
(1+eta)sqrt(N). This is a direct negative-answer match for atlas **P1150**.

There is a minor degree/length conversion to discharge: P1150 uses degree n,
whereas the source has N=n+1 coefficients. Given a proposed gap c>0, choose
0<eta<c. For every sufficiently large n,
(1+eta)sqrt(n+1)<(1+c)sqrt(n), contradicting the proposed universal lower
bound. Nonzero final sign ensures degree n exactly.

This strengthens the real-sign scope compared with P230's already resolved
complex-unimodular version. It does not settle the random-polynomial question
P524: existence of exceptional signings is not a probability estimate.

The comparator file contains `sorry`, as a challenge statement. It is not
the solution module. The scope and precise statement were inspected; no
solution/comparator verification, axiom audit, or local Lean build was run.

### A useful autocorrelation translation

For a real signing epsilon_0,...,epsilon_{N-1}, let
C_h=sum_{j=0}^{N-1-h}epsilon_j epsilon_{j+h}. Elementary Fourier orthogonality
gives, with normalized circle measure,

    integral |P|^4 = N^2 + 2 sum_{h=1}^{N-1} C_h^2.

A signing with sup |P|<=(1+eta)sqrt N consequently obeys

    2 sum C_h^2 <= ((1+eta)^2-1) N^2.

For N>=2 the last autocorrelation C_{N-1}=+-1 prevents a zero denominator.
Thus its binary merit factor N^2/(2 sum C_h^2) is at least
1/((1+eta)^2-1), and becomes arbitrarily large as eta tends to zero.
This exposes a direct Fourier/autocorrelation contact with atlas Lane 4's
LP/SDP language. It does not provide explicit signs, an effective threshold,
a finite numerical witness, or a way to turn an arbitrary positive-semidefinite
Toeplitz relaxation into realizable binary coefficients.

## Further conditional analytic interfaces

1. **r-free global energy.** For fixed integer r>=2, put
   E_r(x)=sum_{n<=x}1_{r-free}(n)-x/zeta(r). Its transform is
   zeta(s)/(s zeta(rs))-(1/zeta(r))/(s-1). The same F003 growth and
   test-contour argument works on a>q/r and yields
   integral_1^X |E_r(x)|^2 dx << X^(1+2q/r+epsilon), hence exponent
   1+7/(4r)+epsilon at q=7/8. This gives a global-energy counterpart to
   the atlas's existing finite-phase r-free variance extension. It does
   not identify actual short-interval variance with the phase model.

2. **Fixed coprime residue classes.** F003 includes every Dirichlet L-function.
   For a fixed modulus m and gcd(b,m)=1, character orthogonality gives the
   squarefree progression series
   (1/phi(m))sum_chi conjugate(chi(b))L(s,chi)/L(2s,chi^2).
   Its pole density is
   c_m=(1/[m zeta(2)])product_{p|m}(1-p^-2)^-1.
   The same proof, with constants depending on m, gives
   integral_1^X |sum_{n<=x,n=b mod m}mu(n)^2-c_m x|^2 dx
   <<_{m,epsilon} X^(15/8+epsilon).
   Finitely many imprimitive Euler factors have no zeros in Re(s)>0
   and cause no problem on the fixed interior strips. There is no
   claimed growing-modulus or arbitrary-mask estimate.

3. **All fixed finite Mobius filters.** The F007 transfer yields, for any
   fixed complex weights w_1,...,w_H,
   lim_{X->infinity} X^-1 sum_{n<=X}|sum_h w_h mu(n+h)|^2
   = (1/zeta(2))sum_h |w_h|^2.
   Its second-order covariance is diagonal. This contrasts with the
   arithmetic correlations in the squarefree indicator: removing signs
   changes the spectral object. Pair decorrelation does not imply full
   probabilistic independence, Gaussian higher moments, growing-H
   uniformity, or the weighted square-frequency mixed-moment estimate.

4. **F076 and F007 meet at autocorrelation, but not by implication.** F007
   describes each fixed lag of an arithmetic sequence as length grows;
   the merit-factor sum has order N lags growing with N. Fixed-lag
   cancellation cannot justify summing all those squared correlations.
   Conversely F076 constructs some signings, not the Liouville sequence.
   This is a precise uniformity barrier useful for graph quarantine.

The extra interfaces are conditional derivations or method candidates, not
novelty claims. All production graph nodes, statuses and certificates remain
untouched by this audit.

## Second-wave analytic and geometric scan

The scan covered F073, F074, F075, F088, F089, F090, F092, F097, F100,
F148, F153 and F191, using pinned scope documents where available and
manuscript introductions for the families without a scope document. These
are statement-level checks, not full proof audits. A missing scope file is
not evidence that a family or its manuscripts are absent.

### F191 contacts P507 directly, at a scoped lower-bound surface

The [F191 introduction](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-power-improvement-in-the-Heilbronn-triangle-lower-bound-September-25-2026/build/sections/01-introduction.tex)
asserts a fixed-power improvement for minimum triangle area, for all large
cardinalities. The [selected comparator](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/ComparatorChallenges/HeilbronnTriangle.lean)
provides the narrower unbounded-subsequence construction. Both contact
[P507](https://www.erdosproblems.com/507); neither determines the exact
optimal order. Translating the source's unit-square configurations into a
unit disk costs at most an absolute area factor, absorbable by reducing the
positive exponent. The centered unit square already fits in the unit disk.

The comparator's explicit exponent is

    eta = 1/[100000*(binom(binom(163,41),3)^2+1)]
        approximately 7.214428362266453e-237.

This is a strict power gain, but no practically appreciable finite-scale
gain or accessible construction size follows from that number. The comparator
uses the internal namespace `Problem355`; this is not the atlas problem ID.
Its theorem declarations contain `sorry` as challenge targets, and no
solution-module proof audit is claimed.

### A clean cross-family composition: F148 plus F073

Suppose K is a nonempty self-similar compact subset of the line satisfying
the no-exact-overlap hypotheses of the
[F148 attractor corollary](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/148.md),
with similarity dimension s>1/2. Its claimed conclusion gives dim_H K>1/2.
Choose t strictly between 1/2 and dim_H K and a t-Frostman measure on K.
The product measure has a 2t-dimensional ball bound on K x K, so

    dim_H(K x K) >= 2t > 1.

[F073's planar Falconer conclusion](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/073.md)
then gives positive Lebesgue measure for the distance set of K x K. This is
an actual conditional theorem composition, not a keyword match. It supplies
no uniform quantitative lower bound, no finite distinct-distance exponent,
and no conclusion at the critical dimension s=1/2. In particular it cannot
be substituted directly for an exact finite geometry certificate.

### F097: a real finite-family discrepancy interface and a quantifier barrier

For d fixed subsets A_1,...,A_d of the integers, encode the first N integers
by vectors (1_{n in A_i})_{i=1}^d / sqrt(d). They lie in the Euclidean unit
ball. [F097](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/097.md)
supplies a signing with every prefix norm <=C sqrt(d), hence discrepancy
<=Cd on each of the d sets and each cutoff. Compactness of {+-1}^N extended
to infinite sign sequences gives an infinite signing for every fixed d.
This is a precise finite-family interface relevant to P178's discrepancy
language, without any novelty claim. It does not exchange
`for every d, there exists a signing` for `there exists one signing, for every d`.
P178's countable-family problem has that latter requirement, so this alone
does not improve its known simultaneous bound. No online signing algorithm
is asserted by the source.

### Two grounded tool candidates, with explicit missing transfers

- **F090 to Lane 4.** The
  [pinned scope](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/090.md)
  provides Fourier-positive radial minorants and a sharp circle-packing
  auxiliary function. This is a substantive dual-certificate method,
  matching the atlas's LP/SDP emphasis. Applying it to a finite distance or
  diameter problem still needs a duality statement for that exact objective,
  treatment of the boundary, and a verifier for global functional inequalities.
  Infinite-density optimality does not prove finite-packing optimality.
- **F089 to cut relaxations.** Its planar and bounded-treewidth shortest-path
  metrics have bounded-distortion L1 embeddings, according to the
  [scope](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/089.md).
  L1 distances decompose into nonnegative combinations of cut semimetrics,
  offering a concrete certificate language for metric relaxations. An atlas
  algorithmic application still needs an explicit embedding/cut decomposition,
  constants, input graph-class membership and an objective-preserving reduction.
  No exact Ramsey or arbitrary-graph improvement follows.

### Deliberately unjoined pieces

F074's Kakeya maximal/set statements do not reverse the historical
sums-differences-to-Kakeya implication to settle P1097's optimal exponent.
F075's ordinary Fourier partial-sum convergence does not bound the dilated
averages required by P996; square-integrable Fourier convergence was already
available for that input class. F088's projection-body inequalities, F092's
Euclidean covering-density results and F100's cylinder covers have no direct
atlas target match established by this scan. In particular Euclidean lattice
covers are not integer congruence covering systems.

F153's introduction explicitly separates full Hausdorff dimension from
absolute continuity. Its classification is an infinite algebraic
approximation criterion, not a finite decision procedure. These are useful
scope controls on a possible F148/F153 join: a dimension formula alone does
not decide singularity. No direct new atlas problem-ID match for F153 was
established. This scan records these unmatched families rather than creating
implication edges from their shared vocabulary.

## Cross-review of the other swarm deductions

These verdicts independently review the short transfer arguments, not their
external proof inputs. No duplicate graph edges are added.

- **F012 + BPZ24 to consecutive square-product waiting times: PASS
  CONDITIONAL, with one minor clarification required in the exposition.**
  The exceptional set where the largest prime factor occurs at least twice
  has density zero by the stated fixed-z split. Outside it the parity argument
  gives the necessary one-sided comparison. Equality of marginal densities
  then gives symmetric difference of density zero: explicitly,
  |B minus A|=|B|-|A|+|A minus B| on every finite initial interval.
  Translation by one preserves density-zero sets. The only suppressed step
  is that F012 states its second threshold as n^b, while the shifted event
  uses (n+1)^b. For every eta>0 with b+eta<1,
  n^b<=(n+1)^b<=n^(b+eta) eventually. Squeeze between the F012 limits at b
  and b+eta, then use continuity of rho as eta decreases to zero. This
  completes the stated formula for every fixed a,b in (0,1), without any
  moving-parameter uniformity. I checked BPZ's Theorem 1.1 and Lemmas 3.4–3.5
  in the [primary arXiv text](https://arxiv.org/html/2211.12467), which also
  directly confirms the exceptional lower-bound qualification. The DOI
  landing page was inaccessible to my browser, so this cross-review used
  the authors' preprint rather than independently checking the journal copy.

- **F024 to P417 liminf separation: PASS CONDITIONAL.** Theorem 2.2 states
  the k=1 positive alternative with a strictly positive infimum over phase;
  Theorem 2.1 bounds the unweighted coefficient above. These jointly give
  N_1(x)>=cV(x) eventually for some fixed 0<c<1. Since phi(m)<=m, the
  range of phi on m<=x is exactly the set of totients v<=x having least
  preimage <=x. Every v counted in N_1 is omitted from that range. Therefore
  Vprime(x)<=(1-c)V(x), and the claimed liminf bound follows. Pointwise
  positivity of a phase coefficient alone would not suffice, but the actual
  source supplies uniform positivity. No ratio limit, uniform-in-k estimate
  or summation over all k is warranted. Checked primary manuscript Theorems
  2.1–2.2 from the source receipt's local text `/tmp/openai-number-swarm/024-0.txt`.

- **P57 + F159 to APs of odd-cycle lengths: PASS CONDITIONAL.** The licensed
  P57 statement supplies divergent harmonic mass for the set of distinct
  odd cycle lengths. This is exactly F159's hypothesis; k=1,2 follow from
  infinitude and k>=3 from the stated corollary. A common difference is
  positive and even when k>=2. No common vertex, induced-cycle requirement,
  disjointness or finite-order bound is inferred.

- **P57 + F182 to square-separated odd-cycle lengths: PASS CONDITIONAL.**
  The polynomial h(t)=t^2 is intersective with positive leading coefficient,
  so F182 bounds a square-difference-free subset of [1,N] by C N^(1-c).
  Dyadic summation then forces its harmonic sum to converge, contradicting
  P57. The square difference is nonzero, and its root is even because both
  lengths are odd. The argument concerns length values only. Checked the
  F182 manuscript abstract/main scope and F159's introduction/corollary
  against the licensed P57 statement in `atlas/stubs.json`.

The threshold clarification was sent to the coordinating agent before this
cross-review was appended. None of these four transfers had a substantive
mathematical failure under its stated external premises.

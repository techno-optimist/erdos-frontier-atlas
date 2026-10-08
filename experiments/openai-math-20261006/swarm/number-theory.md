# Number-theory swarm: theorem matches and real transfer boundaries

This is a research overlay, pinned to OpenAI `math` commit
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`. It does not change canonical statuses,
generated graph files, or certificates. Primary introductions, theorem statements,
and selected Lean scope documents were inspected. No external code was executed,
no Lean proof was rebuilt, and no full manuscript was audited. The JSON companion
records downloaded-source hashes and 47 typed connections. A source pin verifies
which claim was read, not its correctness or current acceptance.

## Four newly identified exact matches

| Source | Atlas contact | Exact scope | Review priority |
|---|---|---|---|
| F011, weighted dilation graphs, Theorem 1.1 | P821, `S:gap:821:329db01a` | For every epsilon>0 infinitely many totient values v have more than v^(1-epsilon) preimages. Matches the full multiplicity-exponent assertion. | Highest: closes exactly the input wall the card names; F011 has no selected Lean scope. |
| F013, Theorem 1.1 | P431 | No nontrivial sumset A+B is a finite modification of the primes; includes two infinite summands. | Full statement match; inspect complete solution dependencies. |
| F024, Theorem 2.1 | P416, `S:gap:416:7dd01bdf` | Explicit totient-count asymptotic and V(cx)/V(x)->c for each fixed c>0. | Full regular-variation question and asymptotic surface. |
| F026, Corollary 1.2 | P968 | Positive lower density of increases of p_n/n. | Exactly the selected Lean scope; stronger large-gap theorem is a separate manuscript statement. |

Sources: [F011 manuscript](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Weighted-Dilation-Graphs-Smooth-Shifted-Primes-and-Totient-Fibers-September-24-2026/paper.pdf),
[F013 scope](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/013.md),
[F024 scope](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/024.md),
[F026 scope](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/026.md).

The distinction from the original crosswalk is substantial: these are theorem-to-question
matches, rather than shared tags. They remain externally reported matches pending audit.

## The totient cluster separates into three different quantities

F011 controls **how many preimages one value can have**. F024 controls **how many
values there are**. P51 and P417 concern **where the first preimage occurs**.
The graph links these through shared arithmetic, but their quantifiers differ.
In particular, large fibers do not force their minimum to be large.

Write ell(v)=min{m:phi(m)=v}, V(x)=#{v<=x:v is a totient}, and
Vprime(x)=#{phi(m):1<=m<=x}. F024 Theorem 2.2 studies

    N_k(x) = #{v<=x : kx < ell(v) <= (k+1)x}.

For fixed k it gives an arithmetic main term depending on the paper's phase.
This term is uniformly positive exactly when some totient d has ell(d)>kd;
otherwise N_k vanishes identically. The manuscript establishes positive seeds
for k=1,2 and expressly leaves unboundedness of ell(d)/d unresolved.
Thus F024 does not settle P51 by recycling its own seed condition.

There is nevertheless a clean **partial deduction for P417**. The positive k=1
case yields an absolute c with 0<c<1 such that N_1(x)>=cV(x) eventually.
Since phi(m)<=m, Vprime(x) counts exactly the v<=x with ell(v)<=x. Consequently

    V(x)-Vprime(x) >= N_1(x) >= cV(x),
    liminf V(x)/Vprime(x) >= 1/(1-c) > 1.

This is conditional on the external theorem and gives no numerical c.
It neither proves that the ratio converges nor rules out an infinite limit.
Summing all fixed-k asymptotics without a uniform tail bound would be invalid;
phase-dependent coefficient ratios must also be handled.
[Theorem 2.2 and explicit caveat](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-asymptotic-formula-for-the-number-of-totients-September-25-2026/An-asymptotic-formula-for-the-number-of-totients-September-25-2026.pdf).

## A new composition: consecutive square-product waiting times

This derives a result adjacent to already-solved P841, rather than announcing
another solution to it. Let t_n be the shortest interval after n containing a
subset whose product with n is square, with t_n=0 when n is square. Assume F012's
joint Dickman law. Then, for fixed 0<a,b<1,

    dens{n : t_n<=n^a and t_(n+1)<=(n+1)^b}
      = rho(1/a) rho(1/b).

Here is a proof of the transfer, including an exception suppressed in the atlas
stub's prose.

1. Let E={n>1:P+(n)^2 divides n}. For fixed z, members with P+(n)<=z are
   z-smooth and number O_z((log X)^pi(z))=o(X). The remaining members number
   at most sum_{p>z,p<=sqrt X} floor(X/p^2) <= X sum_{m>z}1/m^2.
   Taking X to infinity and then z to infinity proves E has density zero.
2. Outside E, p=P+(n) occurs exactly once in n. None of n+1,...,n+p-1
   is divisible by p, so no subset of these numbers can cancel that odd
   exponent. Hence t_n>=P+(n) outside E. The blanket inequality for all n
   would be false, already for n=p^2 where t_n=0. The universally correct
   lower bound uses the largest prime dividing n to an odd power.
3. For fixed a, let A_a={n:t_n<=n^a} and B_a={n:P+(n)<=n^a}.
   We have A_a minus B_a contained in E. BPZ24 Theorem 1.1 says A_a and
   B_a have the same natural density rho(1/a). Therefore their symmetric
   difference has density zero.
4. The symmetric difference between A_a intersect (A_b-1) and
   B_a intersect (B_b-1) is contained in the union of two density-zero sets.
   F012 supplies the claimed density of the latter intersection. Its second
   threshold n^b can be replaced by (n+1)^b: for each small eta>0,
   n^b <= (n+1)^b <= n^(b+eta) eventually. Apply the joint law at b and
   b+eta and let eta decrease to zero, using continuity of rho.

The existing marginal theorem and correct odd-exponent lower bound were
checked in the [published BPZ24 article](https://doi.org/10.1017/S0305004123000488),
Theorem 1.1 and Section 2. The source of the new input is
[F012 scope](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/012.md).
The derivation was checked algebraically here; it is not formalized or
independently refereed, and no priority claim is made.

This illustrates a reusable graph move: **one-sided comparison outside a
zero-density exception + equality of marginals => event equivalence modulo
zero density => transport of joint laws**. Merely matching two marginals without
the one-sided comparison would not justify the joint conclusion.

Other F012 consequences are positive density rho(2)^2=(1-log 2)^2 for the P370
square-root-smooth pair condition and the k=2 dyadic form of P369. For the latter,
choose a fixed exponent smaller than epsilon and subtract the asymptotics at
X and X/2. This gives pairs in every sufficiently large dyadic interval.
Neither consequence proves a three-coordinate ordering law or a long smooth run.

## What the prime cluster supplies

F011 has three distinct results. Its weighted-dilation manuscript gives a large
supply of smooth predecessors and the P821 fiber theorem. Its Poisson-Dirichlet
manuscript gives all finite-dimensional distributions of the ranked logarithmic
prime factors of p-1 under ordinary counting over primes. Its parity companion
gives infinitely many primes with mu(p-1)=1. The parity paper explicitly says
that smoothness alone does not imply its conclusion; its additional signed
Type II and prime-slot estimates matter.

The supply of smooth predecessors is relevant to Carmichael-number construction
(P1057), but the current atlas surface asks for an exact 64-factor object and
minimality. The supply theorem alone supplies neither the necessary congruence
selection nor a finite witness. This is a genuine construction-method candidate,
not an exact-cell improvement.

F026 Theorem 1.1 asserts positive lower density of gaps exceeding C log p_n for
**each fixed** C>0. Its selected formal statement only records the prime-ratio
corollary P968. The theorem gives no law for a narrow interval around an arbitrary
normalized gap, so P5 is not settled. It gives no upper-tail integrability or
second-moment asymptotic, so P233 is not settled. Positive-density failures of
monotonicity of p_n/n do not decide P15's alternating-series convergence.

F029 Theorem 1.1 gives at least c_a x/(log x)^2 primes in each sufficiently large
(x,2x) having a fixed admissible integer a as primitive root. Taking a to be a
fixed positive prime gives a quantitative infinite subfamily satisfying P985's
small-prime-root condition. It does **not** give a small prime primitive root for
every modulus. The simultaneous-base companion states four explicit hypotheses;
its constants depend on the fixed base list and it does not remove this
quantifier mismatch.
[F029 manuscript](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Primitive-roots-for-every-admissible-integer-base-October-4-2026/primitive-roots-all-integer-bases.pdf).

## Useful boundaries elsewhere

- F021's arbitrary-modulus Jacobsthal bound gives the existing P970 quadratic
  subquestion, the P687 primorial bound, and P854's missing-even-gap upper bound.
  It also gives a coarse reduced-residue moment bound
  sum d^r <= m h(omega(m))^(r-1), r>=1, since sum d<=m. P220 already has a
  stronger classical moment theorem; this is reuse, not new progress there.
  It does not supply P860's distinct-representative matching condition.
- F025 gives short unrestricted distinct-unit-fraction expansions, not three
  terms for 4/n (P242), all denominators at least N (P295), semiprime denominators
  (P306), or a forbidden relation inside a prescribed set (P327).
  Its prime-factor splitting may help the actual smooth-fiber method, but that
  requires a new inequality for the atlas operator.
- F020 treats one irreducible polynomial, degree d>=4, with power-free exponent
  d-2 and no fixed prime-power divisor. Quartics give squarefreeness; a quintic
  conclusion is cube-freeness, not squarefreeness. It does not give P969 variance,
  squarefree pairwise-sum extremal bounds, or P975 divisor-function asymptotics.
  Its large-prime-tail machinery is a candidate input for the last problem.
- F022 allows unrestricted numerators and a fixed shift. It supplies neither the
  coprime-numerator version nor a convergence converse. P999's homogeneous
  coprime theorem was already solved. Its overlap-control machinery can be
  considered for CRT defect methods only after matching the actual kernels.
- F023's first moment over Eisenstein primes and fixed angular modes is a
  different object from the atlas's weighted Mobius square-frequency second
  moment. No transfer to the RH residual is established.
- F017 reports pi irrationality exponent 2 and manuscript consequences for
  sine-denominator series. The Flint-Hills convergence consequence lies outside
  its selected formal statement. None of this decides unrelated explicit-series
  irrationality questions such as P68. An ineffective threshold is not an
  explicit numerical Diophantine lower bound usable at arbitrary finite inputs.

Source URLs, exact scopes, missing hypotheses and surface IDs are in
[number-theory.json](number-theory.json). Every `candidate` and `blocked_transfer`
edge has zero implication authority. A `conditional_derivation` still requires
its external premises to survive review. The most productive first reviews are
P821, P431, P416 and P968, followed by the two short compositions above.


## Fifth exact target found behind a link-only stub: P978

F020 applies directly to P978's correctly locally unobstructed power-free
polynomial question (`erdos_978.parts.ii`), and gives positive density where
the question only asks infinitude. It covers every degree d>=4, including
powers of two omitted from that variant. The local hypothesis must exclude a
fixed prime **(d-2)th power** divisor; exclusion at exponent d-1 is insufficient.

For `erdos_978.parts.iii`, f(x)=x^4+2 is Eisenstein at 2. Since f(0)=2
and f(1)=3, no prime square divides all values. F020 therefore gives a positive
Euler-product density of squarefree values, conditional on its proof.

This exposes a concrete knowledge-graph blind spot: the current P978 stub has
no statement text and shows formal status `research solved`, answer `False`.
The pinned declaration file reveals that this verdict belongs to the
`allow_fixed_divisors` variant. Parts ii and iii in that same file remain
`research open`. The aggregate flag cannot be used as a status for all branches.
No canonical correction was made in this lane.

Sources: [F020 scope](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/020.md),
[pinned P978 declarations](https://github.com/google-deepmind/formal-conjectures/blob/16e02e2c29752539b6889563c392bc05c68cddc5/FormalConjectures/ErdosProblems/978.lean).


## Second-wave algebraic and computational coverage

The JSON separates scope inspection from title-only triage for the remaining
assigned families. No artificial Erdős implication was created merely because
a manuscript mentions fields, primes, graphs or algorithms. Abstract/introduction
inspection of F004, F006, F010, F016, F018, F019, F027, F030, F031 and F032
found no exact reduction from an atlas target. F001, F002 and F014 remain
title-only triage in this lane. F003 and F007 belong to the existing analytic
analysis. F028's P952 match is retained in the edge list.

Several scope differences should be preserved in any consolidated graph:

- F009's selected formal statement proves uniqueness of reconstruction, not
  existence for every admissible datum.
- F015's formal scope is prime degree at least five. The family also contains
  quartic and sextic manuscripts; the checkbox does not certify those.
- F010's occurrence in a completed Hecke algebra is not a blanket assertion of
  classical modularity.
- F242's single-fold representation is formalized; its algorithmic-undecidability
  consequence is not separately included in the selected statement.
- F279 is an exact polynomial-size uniform **quantum** circuit statement over
  a fixed finite gate set. It is not a classical factoring algorithm, executable
  local acceleration, or an improvement to a finite atlas witness.

The second wave therefore improves the graph's admission boundaries as well
as its positive connections. Its most important positive discovery was P978,
whose missing statement text hid a precise polynomial specialization.

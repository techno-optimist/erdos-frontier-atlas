# Primary sources for weyl_endomorphism.py (all fetched 2026-07-20)

## 1. Belov-Kanel & Kontsevich, arXiv:math/0512171 (Mosc. Math. J. 7 (2007))
Fetched: https://arxiv.org/abs/math/0512171 and https://ar5iv.labs.arxiv.org/html/math/0512171
(the 868 KB ar5iv HTML was archived in the round-3 scratchpad; it is **not**
committed here — the verbatim quotations below are what this certificate uses,
and every one of them is re-checkable at the two URLs above).

- Definition (verbatim): "The Dixmier Conjecture DC_n for integer n>=1 (see [4])
  asserts that for any field k of characteristic zero any endomorphism of the
  n-th Weyl algebra A_{n,k} over k is an automorphism. Here A_{n,k} is the
  associative unital algebra over k with 2n generators y_1,...,y_2n and
  relations [y_i,y_j] = omega_ij, where (omega_ij) ... omega_ij =
  delta_{i,j+n} - delta_{i+n,j}."
- Easy direction, per-n (verbatim): "It is well-known that DC_n implies JC_n
  (in particular DC_infty implies JC_infty) (see [5], [3]). The argument is
  very easy. Let phi: A^n_k -> A^n_k be a counterexample to JC_n. Then phi is
  a non-invertible etale map, and it induces a pullback homomorphism
  phi*_diff of the algebra of differential operators on A^n_k. The
  endomorphism phi*_diff of the Weyl algebra preserves the degree of
  differential operators. Restricting phi*_diff to zero order differential
  operators, we obtain the usual pullback phi* of functions on A^n_k. By our
  assertion it is not surjective, hence we obtain a counterexample to DC_n."
- Bibliography (verbatim): "[3] H. Bass, E. H. Connell, D. Wright, The
  Jacobian conjecture: reduction of degree and formal expansion of the
  inverse. Bull. Amer. Math. Soc. (N.S.) 7 (1982), no. 2, 287-330." / "[5]
  A. van den Essen, Polynomial automorphisms and the Jacobian conjecture,
  Progress in Mathematics, 190. Birkhauser Verlag, Basel, 2000."
- Hard direction (verbatim): "Theorem 1. Conjecture JC_2n implies DC_n." and
  "In particular, we obtain that the stable conjectures JC_infty and DC_infty
  are equivalent."
- How BKK characterize van den Essen's Theorem 10.4.2 (verbatim, Remark 1):
  "A. van den Essen ([5], Theorem 10,4.2) proved a weaker result: the
  conjecture JC_2n implies the invertibility of any endomorphism of
  A_{n,k} = D(A^n_k) preserving the filtration by the degrees of differential
  operators."

  **Provenance limit on this bullet (adversary fix, 2026-07-20).** An earlier
  draft used this quotation to assert that van den Essen 2000 is "attached to
  the wrong direction" in secondary write-ups. That sub-claim rests **entirely
  on BKK's Remark 1 characterization**: nobody on this project fetched or read
  the van den Essen book itself, so we cannot independently confirm what
  Theorem 10.4.2 says, nor rule out that the book also contains the easy
  direction elsewhere. What is defensible is exactly this and no more:
  *BKK's Remark 1 describes vdE's Theorem 10.4.2 as the JC_2n ⇒ filtered-
  endomorphism-invertibility statement.* Anything stronger about the book is
  unverified.

  **This does not weaken the certificate.** The per-n re-typing that
  `weyl_endomorphism.py` relies on (DC_n ⇒ JC_n, per dimension) is cited
  DIRECTLY to BKK's own verbatim "easy direction" statement quoted in the
  bullet above — BKK asserting it in their own voice, not BKK reporting on
  someone else's book. The vdE attribution is bibliographic context that no
  claim here depends on. (BKK do cite [5] and [3] alongside their sentence;
  which of those two carries which part is precisely the question we are NOT
  answering.)
- Non-constructive machinery is confined to the hard direction (verbatim,
  Remark 2): "... in the proofs of several results of our paper one can use
  the reduction modulo an infinitely large prime."
- Monotonicity used for n>=3 spread (verbatim): "The conjecture DC_n implies
  DC_m for n>m".

## 2. Tsuchimoto, "Endomorphisms of Weyl algebra and p-curvatures",
Osaka J. Math. 42 (2005) 435-452.
Fetched: https://projecteuclid.org/journals/osaka-journal-of-mathematics/volume-42/issue-2/Endomorphisms-of-Weyl-algebra-and-p-curvatures/ojm/1153494387.full

- (verbatim) "We first show that for each Weyl algebra over a positive
  characteristic field, we may obtain an affine space with a projectively
  flat connection on it." ... "As a result, we show that a solution of the
  Jacobian conjecture is sufficient for an affirmative answer to the Dixmier
  conjecture." Uses ultrafilters: "We need to fix an ultrafilter on the set
  of prime numbers to do this."
- Same (hard, non-constructive) direction as BKK Theorem 1; NOT used by our
  construction.

## 3. Bavula, arXiv:math/0512250, "The Jacobian Conjecture_2n implies the
Dixmier Problem_n" (3 pp.; alternative proof of the hard direction; "no
originality is claimed"). Confirms the hard direction's name/indices.
Fetched: https://arxiv.org/abs/math/0512250 (search-result confirmation).

## 4. Adjamagbo & van den Essen, arXiv:math/0608009, "On the equivalence of
the Jacobian, Dixmier and Poisson Conjectures in any characteristic".
Fetched abstract: https://arxiv.org/abs/math/0608009 (verbatim): "...we prove
the equivalence of these three conjectures in any characteristic, giving also
by this way a new proof of the equivalence of the complex version of the two
first conjectures recently proved by Y. Tsuchimoto." (This is the paper the
crater's poisson<->dixmier edge cites; not needed by our direct construction.)

## Root claim (conditional dependency)
The map F and its certified facts (det JF = -2 identically; collision points)
are Alpoge's counterexample, verified in
`certificates/jacobian-conjecture/verify.py` (repo-relative)
-- construction NOT ours; everything here is conditional on that root claim
(tracked by `tools/jc_root_tripwire.py` + `atlas/jc-crater/root_claim.json`).

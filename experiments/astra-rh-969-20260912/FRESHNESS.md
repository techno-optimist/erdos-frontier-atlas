# RH / Erdős #969 freshness — checked 2026-09-12

## Official status and scope

Clay's live Millennium index still puts the Riemann Hypothesis under
**Unsolved problems**. No accepted full proof was found in this search.[17]
This is a source audit, not a certification of every manuscript that claims RH.

The live Erdős #969 page asks for the true order of the squarefree-counting
error. It still records that the order is unknown even assuming RH, and cites
Liu's RH-conditional exponent `11/35+o(1)`. This is what the catalogue says,
not an independently proved claim that no later paper improves it.[2]
The page showed no proof expositions, comments, or proof claims on this check;
the discussion and separate proof-claim register were also inspected.[2][7][8]

The pinned community record at commit
`3c68e941162f81d650fc886eed34e58bed3a6a01` has
`informal_status.state: open`, `formal_status.state: unformalized`, and
OEIS `A013928` for #969. Its mathematical status date is `2025-08-31`;
that date is not the date of this retrieval.[21]

## Recent advances worth reading

| Work | What it establishes or reports | Evidence level and limitation |
|---|---|---|
| **Lamzouri, 2609.02882v2, revised September 8, 2026** | A different Hilbert-space proof that more than 67.25% of nontrivial zeta zeros are simple **and** on the critical line, and at least 83.62% are distinct. The revision adds more than 88.76% simple **or** on the line, plus an average-proportion bound.[9][18] | Independent proof of the Alpöge–Furman/Claude proportion result plus new inequalities; a recent preprint, not a proof of RH. No journal acceptance was identified in this audit. |
| **Biao Wang, 2609.07918v1, September 7, 2026** | Extends Lamzouri's approach to simple critical zeros and distinct zeros in short height intervals, using a short-interval pair-correlation estimate.[11] | Recent follow-up preprint. Its proof was not independently reconstructed here. |
| **Robles–Zaharescu–Zeindler, 2609.03961v1, September 3, 2026** | A squarefree exponential-sum estimate replacing earlier `N^epsilon` losses by `(log(2N))^5`, via a square sieve, a finite Fejér majorant, and restricted-prime representation counting.[19][20] | Especially relevant to our arithmetic phase-cancellation lane, but still a preprint. This audit read the statement and mechanism, not a full proof verification. |
| **Guth–Maynard, Annals 203(2), March 1, 2026 publication** | New large-values estimates for Dirichlet polynomials, with zero-density bound `N(sigma,T)<=T^(30(1-sigma)/13+o(1))` and prime short-interval consequences.[12] | Peer-reviewed publication of work first received in July 2024, accepted April 2025. It is not a new September result and does not exclude every exceptional zero. |

All zero proportions in the Lamzouri statement have all nontrivial zeros,
counted with multiplicity, as denominator. In particular **88.76% is a union,
not a critical-line percentage**.[9]

Lamzouri credits the earlier proportion proof to an internal Claude system
and its verification to Levent Alpöge and Ralph Furman. His paper replaces
its matrix construction with a single Hilbert-space inequality, using the
unconditional pair-correlation theorem of Baluyot–Goldston–Suriajaya–Turnage-Butterbaugh.[9]
This is the transferable lesson: control a global quadratic form without
silently imposing positivity on each complex off-diagonal term.

### The especially relevant exponential-sum statement

The Robles–Zaharescu–Zeindler preprint states, for `N>=2`, real `alpha`,
integers `a` and `q>=1`, `gcd(a,q)=1`, and `|alpha-a/q|<=q^-2`,

\[
 \left|\sum_{n\le N}\mu(n)^2 e^{2\pi i\alpha n}\right|
 \ll \left(\frac Nq+q\right)(\log(2N))^5,
\]

with an absolute implied constant.[20]
This is an **uncentered** exponential sum. At `alpha=0, a=0, q=1`, its
right-hand side is of order `N (log(2N))^5`; it supplies no quarter-power
estimate for `Q(N)-N/zeta(2)`. A direct implication to our energy target has
not been established. Any proposed transfer must handle centering and the
low-frequency/major-arc contribution, rather than just quote a minor-arc bound.

## Formalization is a separate claim

Lamzouri's Appendix A reports an unconditional formal certificate for its
general Proposition 2.1, but the certificate for the analytic Theorem 1.1
takes BGST Lemma 5 and the Riemann–von Mangoldt asymptotic as inputs.[9]
That does not make the mathematical theorem conditional—the manuscript uses
established analytic results—but it does limit what this particular formal
artifact alone establishes. No fresh Lean build, comparator execution,
axiom audit, or independent kernel replay was performed here.

## Why the pointwise target needed correction

The k-free literature records normalized squarefree oscillations exceeding
both `+3` and `-3`, discusses conjecturally unbounded oscillations, and warns
about an erroneous earlier assertion that RH implies the pointwise
quarter-power-with-epsilon bound.[15]
Thus neither a bare `O(x^(1/4))` target nor an epsilon/log modification may be
quietly declared equivalent to RH.

GMRR's published squarefree variance theorem gives an unconditional asymptotic
through `1<=H<=X^(6/11-epsilon)`. Its Theorem 3 characterizes RH by the
near-optimal variance **upper bound** throughout `H<=X^(1-epsilon)`, for every
small positive epsilon and every positive secondary exponent delta.[13][14]
The global biconditional in `ANALYTIC_TARGET.md` is derived separately; it is
not obtained by inserting `H=X` into that theorem.

## Source handling and limitations

Versioned arXiv HTML and live DOM text were used to recover formulae where
ordinary extraction lost mathematics or returned an older revision. The
Lamzouri v2 title, date, Theorem 1.1, and Appendix A were checked directly.
The Annals publication and acceptance dates were checked on its article page.
Reading copies remain outside this research bundle; no complete third-party
manuscript is redistributed under the Atlas license.

No accepted RH proof, new bound for the actual squarefree error, or automatic
transfer of these breakthroughs into an RH solution was found or produced.

## Sources

[2] https://www.erdosproblems.com/969
[7] https://www.erdosproblems.com/forum/discuss/969
[8] https://www.erdosproblems.com/forum/thread/969/proof-claims
[9] https://arxiv.org/html/2609.02882v2
[11] https://arxiv.org/abs/2609.07918
[12] https://annals.math.princeton.edu/2026/203-2/p06
[13] https://arxiv.org/pdf/2006.04060v2
[14] https://link.springer.com/article/10.1007/s00039-021-00557-5
[15] https://arxiv.org/html/1912.04972v2
[17] https://www.claymath.org/millennium-problems
[18] https://arxiv.org/abs/2609.02882v2
[19] https://arxiv.org/abs/2609.03961
[20] https://arxiv.org/html/2609.03961
[21] https://github.com/teorth/erdosproblems/blob/3c68e941162f81d650fc886eed34e58bed3a6a01/data/problems.yaml

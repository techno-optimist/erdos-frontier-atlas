# Continued research: rational gaps, smooth defects and a formal bridge

This bundle extends the [first research sprint](../research-sprint/README.md)
and is indexed in [current findings](../CURRENT_FINDINGS.md). Graph attachments
are `P699` and `S:triage:699`. All results remain research artifacts; neither
the full P699 problem nor its full i = 3 slice is settled here.

| Result | What it adds | Evidence boundary |
|---|---|---|
| [Rational-position gaps](arithmetic/README.md) | Every-position denominator gain; exact exclusion around j ≈ n/3; eventual square-root-sized gaps around each fixed rational in (0,1/2) | Informal proof, independent agent review, exact bounded checks; literature novelty unverified |
| [Higher-i smooth defect](structural/README.md) | P divides AQ for every i; when d ≥ 4A, A d³ > 2n² and Ad > 4g³; A = 1 transfers the central strip to explicit row classes | Informal proof and exact bounded checks; does not improve the older density-one result |
| [Finite-block formal bridge](formal-bridge/README.md) | Builds the cubic divisibility and positive quotient from positional block data, then derives the central strip | 16 Lean-audited theorems and two rejected false controls; Kummer and prime-power construction remain outside this formalization |

The key connection is not another larger sweep. Retaining the position of each
prime-power block gives a polynomial obstruction near every rational location;
the midpoint's extra cancellation gives the stronger cube-root-of-n-squared
scale. Tracking small factors then transports that obstruction across i.

Replay the two exact experiments with their `verify.py` scripts. The formal
bridge README gives the pinned Lean command. [results.json](results.json)
hashes the three receipts. The bundle-wide checker also replays the finite
experiments and verifies their current source hashes.

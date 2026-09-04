# Exact bridge: P687 covering → P854 gap spectrum

**Outcome:** an exact endpoint-constrained CRT counting identity, a wheel-transfer operator, and a checked obstruction to transferring a long-cover witness into a prescribed gap. These are proved/rederived here, not claimed novel. No asymptotic frontier moved and no graph edge was promoted.

## Scope and source freshness

Read GRAPH.md, COORDINATION.md, FRONTIER_CARTOGRAPHY.md, views/sorties.md, the bridge builder, and P687/P854/P860 cards at atlas HEAD `4831f560255c294474f84bc4b5a815aed86ca83f`. `atlas/relations.json` is absent. `same_family` means only a shared OEIS identifier, per tools/build_graph.py lines 509–519; it is not an implication. Selected the A048670 family, specifically **P687 → P854**, surface **S:gap:854:c322ba75**. P860 was inspected but not pursued.

Live browser, unlike the stale extractor, found **one unaccepted partial proof claim submitted 2026-08-20**, not zero. The linked GPT 5.6 Sol manuscript (19 August), Proposition 2.1, already gives the endpoint-safe covering equivalence and attributes its restricted-cover predecessor to Ziller. Thus this equivalence is definitely not a novelty claim.[4][8] The canonical problem remains OPEN.[1] Holt–Rudd (2014), Theorem 1.1 and Lemma 2.2, already provide the driving-term/wheel recursion used below.[7]

## 1. Exact CRT bridge and counting formula

Let P be a squarefree product of primes containing 2. Define C_P(t) to be the number of a modulo P for which a and a+t are consecutive integers coprime to P in the periodic reduced-residue set. For t≥1:

**Endpoint-cover equivalence.** C_P(t)>0 iff there are residues r_p (one for each p|P) such that

- r_p is neither 0 nor t modulo p;
- every i in {1,…,t−1} is congruent to r_p modulo at least one p|P.

**Proof.** Given a gap start a, set r_p=−a mod p. Endpoint coprimality gives the exclusions, and every interior nonunit gives a covering residue. Conversely CRT reconstructs a unique a mod P with a≡−r_p; endpoints are units and every strict interior point is not. Therefore the number of covering residue tuples is exactly C_P(t), not just a lower bound. This is the full-position version of the established endpoint-safe equivalence.[8]

A precise operator form is

    C_P(t) = Σ_{S⊆{1,…,t−1}} (−1)^|S|
                   ∏_{p|P} [p − |({0,t}∪S) mod p|].

**Proof.** Require a and a+t to be units; exclude, by inclusion–exclusion, the events that an interior a+i is a unit. For a fixed S, CRT counts the starts for which all a+j, j∈{0,t}∪S, are units: independently modulo p there are exactly p minus the number of forbidden residues. This proves the formula over all parameters.

This gives an exact target-length computation with no full primorial-period scan. The accompanying union-mask DP counts the equivalent residue systems. It can still have exponential complexity in t; this is a representation change and certificate/search transfer, not a polynomial-time breakthrough. The attack card's claim that pinning a cell *requires* a full-period absence scan is too strong: an exhaustive residue-state DP or certified SAT encoding is another exact route.

For P=p_k#, the related P687 function is

    Y(p_k) = max{t : C_P(t)>0} − 1.

A maximal string of nonunits lies between consecutive units, and CRT identifies arbitrary covering residues with translated divisibility, proving this off-by-one relation. But the smallest missing even t depends on the whole support of C_P, not its maximum. P854 asks exactly about that gap support.[1][2]

## 2. Exact wheel-transfer relation

Let (g_1,…,g_φ(P)) be the cyclic gap word, and define

    H_P(z) = Σ_i z^{g_i},
    B_P(z) = Σ_i z^{g_i+g_{i+1}}       (cyclic indices).

If q∤P is an odd prime and max_i g_i < 2q, then

    H_{Pq}(z) = (q−2) H_P(z) + B_P(z).

**Proof.** First repeat the old reduced-residue cycle q times. For each old unit, exactly one lift is divisible by q and deleted. All gaps are even. Under the displayed bound no old gap is divisible by q, because the smallest positive even multiple of odd q is 2q. Thus two deleted vertices cannot be adjacent. Each old edge loses exactly two of its q lifts, one at each endpoint, leaving q−2 unchanged copies. Each old vertex has exactly one deleted lift, merging its two incident gaps into their sum. No double deletion creates an extra term. Summing proves the operator identity. This is consistent with, and a direct special case of, the established wheel/driving-term method.[7]

More generally every old t-gap has q−2+1_{q|t} surviving copies, so gap support cannot shrink on adjoining an odd prime. New gaps require adjacency information: simply multiplying the old histogram by q−2 omits the B_P term.

## 3. Honest obstruction and exact checks

Executed `python3 experiments/astra-briefcase-20260904/bridge/check_bridge.py` successfully:

- **150** cells: k=2,…,6 and t=1,…,30, residue-state DP equals independent gcd period scan.
- **60** cells: k=2,…,6 and t=1,…,12 also equal the inclusion–exclusion formula.
- **25** coefficient checks across the four wheel lifts 6→30→210→2310→30030.
- A planted mutation of the 22-gap witness to length 20 is rejected by the same endpoint/interior verifier.

| k | P | maximum gap | smallest missing even gap |
|---|---:|---:|---:|
| 2 | 6 | 4 | 6 |
| 3 | 30 | 6 | 8 |
| 4 | 210 | 10 | 12 |
| 5 | 2310 | 14 | 16 |
| 6 | 30030 | 22 | 20 |

At P=30030, t=20, the **unrestricted** cover count of [1,19] is **6**, but the **endpoint-safe** count is **0**. Thus the tempting transfer “an unrestricted cover of t−1 positions produces a t-gap” is false, even though a longer 22-gap exists. The known spectrum hole at 20 is also recorded by OEIS.[6]

A concrete 22-gap is **(9439,9461)**, with residues (for primes 2,3,5,7,11,13)

    (1,2,1,4,10,12).

The two endpoints have gcd 1 with P; every interior gcd is >1 (all exact gcds saved in checks.json). Consequently Y(13)=21 while the first missing even gap is 20.

The operator explains the same obstruction: in the P=2310 word, adjacent-gap sum counts are

    {6:128, 8:86, 10:108, 12:100, 14:36, 16:12, 18:8, 22:2}.

There is no adjacent sum 20, whereas (12,10) and (10,12) each occur once, producing the two new 22-gaps under q=13.

**Convention warning.** Counts above are periodic, including the wrap gap 2, matching A389839.[6] The literal finite list in P854 drops that wrap gap. For k≥3 the supports coincide: C_P(2)=∏_{odd p|P}(p−2)≥3, so at least one 2-gap is internal. At k=2 the literal finite gap set is {4}, while the periodic set is {2,4}; do not silently identify that boundary case. The Sol manuscript also explicitly resolves the two conventions.[8]

## Files and limitations

All task outputs are under `/tmp/astra-briefcase-bridge`: this report, `check_bridge.py`, `checks.json`, `sources.json`, live browser text snapshots, and temporary reading copies of the two PDFs. No repository file was written. Final git status showed concurrent parent/other-agent changes to COORDINATION.md and experiments/astra-briefcase-20260904/; these were not touched by this lane.

No novelty, accepted partial-proof status, new OEIS cell, or full problem solution is claimed. The useful result is the proved and executable bridge plus a precise failure mode for endpoint-oblivious transfer. The fresh partial claim's asymptotic proof was read for context, not independently audited in full.

## Sources

[1] https://www.erdosproblems.com/854
[2] https://www.erdosproblems.com/687
[4] https://www.erdosproblems.com/forum/thread/854/proof-claims
[6] https://oeis.org/A389839
[7] https://arxiv.org/pdf/1402.1970
[8] https://github.com/DottedCalculator/ai-math/blob/main/Erdos_854_GPT_5.6_Sol.pdf

Local filesystem paths in this report were normalized for portable publication.

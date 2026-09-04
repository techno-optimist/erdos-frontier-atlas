# Erdős atlas freshness audit — 2026-09-04

## Reproducible status diff

Machine-readable artifact: `upstream-diff.json`.

- Atlas HEAD: `0394e3d3b249439ffabec7d96a3311aa441651b8`.
- Atlas-pinned upstream: `6bcfdca9682239918df81d35e4fb12da22c61aaf`.
- Calendar baseline upstream: `2512c2739787e42b0a8821a49a838497c1a2fff6` (2026-07-27T09:08:24Z).[37]
- Current upstream: `2a4d12b8be30a0483f49259654d10fcb0e2f08eb` (2026-09-04T16:52:06Z).[48]
- All four datasets contain 1,217 entries. Comparing normalized informal mathematical states gives **16 changes** against either atlas pin or calendar baseline. Comparing raw status strings against atlas gives **99 changes**, of which **83 do not change the informal mathematical state**. Do not count new Lean suffixes as new solutions.[37][48]
- Changes: disproved **1, 74, 106, 146, 180, 193, 575**; proved **126, 548, 557, 571**; solved **183, 346, 421, 730, 1005**.[48]
- Homepage lists 18 changes since July 27: Aug 31 **106,146,180,183,575**; Sep 1 **346,421,469,730,1005**; Sep 3 **1,74,126,193,501,548,557,571**. This is not 18 new mathematical solutions: the site says these dates are “just when their status was changed on this site”; #469 was already proved (Lean) in the July baseline, while #501 still has OPEN as its page/YAML status despite homepage listing and body reporting independence of ZFC.[16][36][37]
- The homepage reports 1,220 problems / 584 solved, whereas the community YAML has 1,217 entries. Preserve these as different source snapshots, not one synchronized database.[16][48]
- YAML `last_update` fields can be stale: September 3 status commit changes six problems while preserving 2025 dates. Use commit history and site chronology, not these fields, to date the change.[47]

## Priority targets

- **#993 remains FALSIFIABLE.** Aug 9 comment: “the exhaustive verification now extends to n = 32”, reporting 109,972,410,221 free trees at order 32 and zero unimodality failures. Aug 21 comment claims every tree with at most two degree-at-least-three vertices has a log-concave independence polynomial. These materially change search design, but are contributor results, not a catalog-level resolution; I did not rerun the enormous computation or Lean build. The live page has zero proof claims/expositions. Computation code is linked.[17][5][27] The structural claim links a pinned result artifact.[6]
- **#743 remains FALSIFIABLE.** Aug 15 n=10 computation is not a new frontier. Aug 27 comment points to Guichard–Massman (1990), whose publisher abstract says: “Using a computer, we have shown that the conjecture is true through n=11”. Thus searching n=10 or n=11 for novelty is stale; n=12 is the first beyond this published exhaustive check, not a claim that a comprehensive new literature search proves n=12 untouched. The 2024 full-proof preprint remains unaccepted in the catalog; discussion records doubts. #548 is a different tree conjecture and does not itself close #743.[18][26][28]
- **#366 remains VERIFIABLE/open.** No post-July-27 accepted advance found in its page or discussion. July 22 claim assumes Baker’s explicit abc conjecture and explicitly says “This does not solve the problem”. It predates the atlas cutoff and is conditional, not a witness or unconditional nonexistence proof. Keep orientation straight: the catalog asks 2-full n followed by 3-full n+1; the listed 8,9 and 12167,12168 examples have the reverse orientation.[19][49]
- **#699 remains FALSIFIABLE.** Exactly one accepted partial claim, submitted July 18, covers j≤3i/2 or n=2j. A different July 25 partial claim by van Doorn/Rocca says “currently working to digest, verify, and polish the proofs” and has no accepted marker. Both predate cutoff; no newer accepted progress found. Live DeepMind Lean marks the main `erdos_699` theorem `research open`; the earlier `research solved` annotation belongs to the Sylvester–Schur helper. The atlas attack card’s apparent formal-solved register must not be read as solution of #699.[20][13][40]

## Most consequential accepted changes

- **#1: DISPROVED (FORMALIZED).** Canonical page: “This was disproved by GPT-6 Astra”, with arbitrarily large n and N≤ε2^n for every ε>0. Retire the asymptotic conjecture as open; this does not automatically settle each exact finite optimum the atlas may investigate. Bloom’s September 3 submission identifies an Epoch AI prerelease run and cautions that the human-readable writeups are placeholders. Actual artifacts: site PDF and `tadamcz/erdos1`; latest repository CI was success, not a local rebuild.[9][41][10]
- **#548: PROVED (FORMALIZED).** Canonical page: “A proof of the full conjecture was given by GPT-6 Astra”. Site explicitly says it implies #547 and #557. #557 is updated; #547 still reads DECIDABLE and carries old announced-proof prose, so record this dependency/status inconsistency rather than blindly copying the old card. Actual PDF is linked.[32][33][42] The Lean repository’s latest CI success was checked.[29]
- **#106: DISPROVED (LEAN)**, f(17)>4, attributed on the page to Claude Opus 5 prompted by Silverstein. f(10)=3 remains unresolved on the same page.[30]
- **#193: DISPROVED**, Cambie–Kalviainen (AI-assisted) infinite bounded-step walk in Z³ with no three collinear points.[31]
- **#730: SOLVED**, GPT Pro/Price prove ≫x^(1/2) suitable adjacent central-binomial pairs up to x.[34]
- **#1005: SOLVED**, Cipollini/GPT 5.5 establish f(n)=(1/4+o(1))n.[35]
- **#146, #180, #575:** catalog accepts counterexamples from an internal OpenAI model; #146 uses a connected bipartite 2-degenerate H with ex(n,H)≫n^(3/2+c), while #180/#575 concern finite-family extremal compactness. These are not automatically attributable to the released Astra model just because the announcements are adjacent.[43][44][46]
- **#183: SOLVED (LEAN)**; the actual *Ten Proofs* PDF, Chapter 9, Theorem 1.1, gives R_k(3)≥(c k^(1/3)/log k)^k, hence lim R_k(3)^(1/k)=∞. This is a genuine asymptotic closure, not just an improved finite Ramsey computation.[23][45]

## Official Astra papers: avoid conflating mathematical and formal claims

The official OpenAI results announcement and launch page link the mathematical artifacts.[21][22]

- *Improved Short Gaps Between Primes* (Aug 30): Theorem 1.1 DHL[40,2], Corollary 1.2 liminf prime gaps≤186. The paper and repository explicitly distinguish the mathematical proof from a Lean development conditional on **three project input axioms**: two exponential-sum inputs and numerical integral/cap bounds. README: “The Lean results remain conditional on three explicit input axioms”. Not a fully assumption-discharged Lean theorem.[24][38]
- *Improved Long Gaps Between Primes*: Theorem 1.1 G(X)≫log X (log₂X)² log₄X/(log₃X)², for all sufficiently large X. The paper says the accompanying repository contains a complete Lean proof. I read the paper/README, not reran its build. This is an improved bound, not solution of all prime-gap questions.[25][39]

## Scope and artifacts

No production graph, frozen certificate, or upstream repository was modified. `upstream-diff.json` preserves the pinned comparison. No local Lean build is claimed. The 32-vertex exhaustive search was not replayed. Browser and direct-source reads were used to resolve misleading extractor responses.

## Sources

[16] https://erdosproblems.com
[17] https://erdosproblems.com/993
[18] https://erdosproblems.com/743
[19] https://erdosproblems.com/366
[20] https://erdosproblems.com/699
[21] https://openai.com/index/ten-advances-in-mathematics
[22] https://openai.com/index/gpt-6-astra
[23] https://cdn.openai.com/pdf/ten-proofs-oai.pdf
[24] https://cdn.openai.com/pdf/51126fac-1b68-4128-9666-c908bcc16033/short_gaps.pdf
[25] https://cdn.openai.com/pdf/51126fac-1b68-4128-9666-c908bcc16033/long_gaps.pdf
[5] https://www.erdosproblems.com/forum/thread/993
[26] https://www.erdosproblems.com/forum/thread/743
[27] https://github.com/Tyorden/erdos-993-trees-n31
[6] https://github.com/BrettRey/erdos-problem-993/blob/95f86d96dd89e5ddfff16b65f500fa9c85cb661d/formalization/clan_normalization_aristotle/RESULT.md
[28] https://combinatorialpress.com/jcmcc-articles/volume-008/a-note-on-packing-complete-graphs-with-trees
[10] https://github.com/tadamcz/erdos1
[29] https://github.com/tadamcz/erdos548
[9] https://www.erdosproblems.com/1
[30] https://www.erdosproblems.com/106
[31] https://www.erdosproblems.com/193
[32] https://www.erdosproblems.com/548
[33] https://www.erdosproblems.com/547
[34] https://www.erdosproblems.com/730
[35] https://www.erdosproblems.com/1005
[36] https://www.erdosproblems.com/501
[13] https://www.erdosproblems.com/forum/thread/699/proof-claims
[37] https://github.com/teorth/erdosproblems/blob/2512c2739787e42b0a8821a49a838497c1a2fff6/data/problems.yaml
[38] https://github.com/openai/PrimeGaps186
[39] https://github.com/openai/LongGapsBetweenPrimes
[40] https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/699.lean
[41] https://www.erdosproblems.com/static/1-proof.pdf
[42] https://www.erdosproblems.com/static/548copy.pdf
[43] https://www.erdosproblems.com/146
[44] https://www.erdosproblems.com/180
[45] https://www.erdosproblems.com/183
[46] https://www.erdosproblems.com/575
[47] https://github.com/teorth/erdosproblems/commit/99c392535c69420e7e09b2ced731423a0c83ebc0
[48] https://github.com/teorth/erdosproblems/blob/2a4d12b8be30a0483f49259654d10fcb0e2f08eb/data/problems.yaml
[49] https://www.erdosproblems.com/forum/thread/366/proof-claims

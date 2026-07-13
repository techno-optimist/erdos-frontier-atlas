# Board catalog — READY and HEAVY

Generated view over `atlas/problems.json` (filter: `board_class != NONE`).
A **board** is a bounty market in the P42 sense: a pinned exact verifier
adjudicates submitted witnesses against a seeded frontier. READY boards settle
a claim in under a second of pure-integer verification; HEAVY boards need an
optimistic-oracle tier (a SAT run, a DRAT check, or an exhaustion-receipt
audit per claim). `beatable` is the audit's verdict on whether *our* farm can
move the record — a WALL for us can still be a fair market-maker board.

## BOARD-READY (13)

| erdős # | problem | frontier | lane | beatable | P42 board |
|---|---|---|---|---|---|
| [1](https://www.erdosproblems.com/1) | distinct subset sums, min largest element (A276661) | **a(10)=309 CLOSED (Dyson, Oct 2025)** — live target a(11) ∈ [310, 594] (upper: Conway–Guy 11-set; lower: Dyson + drop-largest lemma) | exact-backtracking | MOVABLE | `distinct-subset-sums-a11` |
| [21](https://www.erdosproblems.com/21) | q(6), min-edge 6-uniform intersecting hypergraph, τ=6 | 14 ≤ q(6) ≤ 18 (Sivashankar 2026 / Barát 2021) — m ≤ 17 witness wins | exact-backtracking / orderly generation | MOVABLE | `q6-intersecting-hypergraph` |
| [41](https://www.erdosproblems.com/41) | a(11), shortest 11-mark B₃ ruler (A227358) | a(11) ≤ 445 (Tromp 2013), suspected < 440; optimality open | SAT+DRAT-nonexistence | MOVABLE | `b3-ruler-11-marks` |
| [67](https://www.erdosproblems.com/67) | Erdős discrepancy, C=3 general witness | ≥130,000, Konev–Lisitsa unrestricted witness exactly re-verified by P42 | witness-local-search | MOVABLE (witness side) | `edp-c3-longest-sequence` |
| [86](https://www.erdosproblems.com/86) | C₄-free subgraphs of Q₇ (extends A245762) | ex(Q₇,C₄) ≥ 304 (SA, May 2026); exact value open | SAT+DRAT-nonexistence | UNKNOWN | `hypercube-q7-c4-free` |
| [138](https://www.erdosproblems.com/138) | W(2,7) van der Waerden lower bound | W(2,7) ≥ 3703 (Ahmed et al. 2014) | witness-local-search | WALL (for us) | — |
| [140](https://www.erdosproblems.com/140) | r₃(212) witness (A003002) | r₃(211)=43 exact; 212 ∈ {43,44} — a 44-set settles it | witness-local-search | WALL (for us) | — |
| [166](https://www.erdosproblems.com/166) | R(4,6) lower bound | R(4,6) ∈ [36,40] (Exoo 2012) | witness-local-search | WALL (for us) | — |
| [183](https://www.erdosproblems.com/183) | multicolor triangle Ramsey R₄(3) lower bound | R₄(3) ∈ [51,62] (Chung 1973) · R₅(3) ∈ [162,307] | witness-local-search | WALL (for us) | — |
| [241](https://www.erdosproblems.com/241) | B₃ subset table A387704, first jump to 9 | a(150)=8 (Dec 2025); least N with a 9-element B₃ subset open (N ≥ 151) | exact-backtracking | MOVABLE | `b3-subset-first-jump-9` |
| [552](https://www.erdosproblems.com/552) | R(C₄, K₁,ₙ) next term (A006672) | repository-certified a(12…16)=17,18,19,20,21; a(17) ∈ [22,23] open | SAT+DRAT-nonexistence | MOVABLE | `c4-star-ramsey-a17` |
| [564](https://www.erdosproblems.com/564) | R₃(4,5;3) lower bound | R₃(4,5;3) ≥ 35 | witness-local-search | WALL (for us) | — |
| [1029](https://www.erdosproblems.com/1029) | R(5,5) ≥ 44 witness (zero-defect K₄₃) | R(5,5) ∈ [43,46]; best public K₄₃ colorings have exactly 2 mono K₅s ([our certs](https://doi.org/10.5281/zenodo.21305022)) | witness-local-search | WALL (for us) | — |

*Near-miss note: #165 (R(3,10) lower bound) belongs to the same market-maker
family as #166/#159, but its independence-number check runs minutes, not
seconds, in the adversarial worst case — it sits just over the READY/HEAVY
line and is classed HEAVY below.*

## BOARD-HEAVY (14) — optimistic-oracle tier

| erdős # | problem | frontier | adjudication load | lane |
|---|---|---|---|---|
| [13](https://www.erdosproblems.com/13) | Erdős–Sárközy exact f(N) table | uncharted (Bedert 2023 theorem, ineffective threshold) | certified table = ILP/SAT certificate per N | exact-backtracking |
| [19](https://www.erdosproblems.com/19) | Erdős–Faber–Lovász n=13 bucket | verified n ≤ 12 | whole-bucket DRAT certificate (pigeonhole-hard) | SAT+DRAT-nonexistence |
| [20](https://www.erdosproblems.com/20) | sunflower frontier cells | Sun(3,3)=21 exact; remaining construction cells must be split before board admission | one finite cell plus exact witness or certificate per claim | witness-local-search |
| [30](https://www.erdosproblems.com/30) | OGR-29 optimality | OGR-28 (585) proven optimal, Nov 2022 | exhaustion receipt at distributed.net scale | exact-backtracking |
| [39](https://www.erdosproblems.com/39) | Sidon ruler optimality past OGR-28 | — | exhaustion receipts | exact-backtracking |
| [64](https://www.erdosproblems.com/64) | 2-power cycle exhaustion extension | all cubic graphs ≤ 28 vertices verified (~2004) | exhaustive-generation certificate | exact-backtracking |
| [107](https://www.erdosproblems.com/107) | Happy Ending f(7) refutation witness | 33 ≤ f(7) ≤ 127 | order-type realizability plus exhaustive convex-7-gon check | SAT+DRAT-nonexistence |
| [139](https://www.erdosproblems.com/139) | exact r_k(N) tables, k ≥ 4 | r₃ side carried by #140 | exhaustion certificates | exact-backtracking |
| [159](https://www.erdosproblems.com/159) | R(C₄,K₁₁) lower bound | 39 ≤ R(C₄,K₁₁) ≤ 44 | exact independence-number adjudication exceeds the cheap witness tier | witness-local-search |
| [165](https://www.erdosproblems.com/165) | R(3,10) lower bound | R(3,10) ∈ [40,41] | α ≤ 9 check ≈ 8.5×10⁸ subsets / MIS run per claim | witness-local-search |
| [582](https://www.erdosproblems.com/582) | Folkman Fe(3,3;4) ≤ 786 | 21 ≤ Fe(3,3;4) ≤ 786; Graham's $100 for ≤ 100 | one CDCL arrowing-UNSAT + DRAT per candidate | witness-local-search |
| [687](https://www.erdosproblems.com/687) | Jacobsthal Y(x) next term (A048670) | a(64) exact (Bozek 2021) | pruned-exhaustion certificate | exact-backtracking |
| [712](https://www.erdosproblems.com/712) | Turán tetrahedron density upper bound | 5/9 ≤ π(K₄³) ≤ 0.561666 (Razborov 2010) | exact-rational SDP dual check | LP/SDP-certificate |
| [720](https://www.erdosproblems.com/720) | size-Ramsey exact small values | r̂(P₅,P₅)=11, … | host + DRAT UNSAT per upper-bound claim | SAT+DRAT-nonexistence |

## The 7 packaged P42 boards (Phase-A bridge, live in `p42-prizes/problems/`)

| slug | erdős # | seed frontier | DA class |
|---|---|---|---|
| `q6-intersecting-hypergraph` | 21 | 18/1 (PG(2,5) 18-line family) | on-chain (< 64 KB) |
| `distinct-subset-sums-a11` | 1 | 594/1 (Conway–Guy 11-set; a(10)=309 closed by Dyson 2025) | on-chain |
| `b3-ruler-11-marks` | 41 | 445/1 (Tromp 2013) | on-chain |
| `b3-subset-first-jump-9` | 241 | 376/1 (best known 9-element containment) | on-chain |
| `edp-c3-longest-sequence` | 67 | length race from the Konev–Lisitsa era frontier | on-chain |
| `c4-star-ramsey-a17` | 552 | 21-vertex witness proves 22 ≤ a(17) ≤ 23 | on-chain |
| `hypercube-q7-c4-free` | 86 | 304-edge primary-source Q7 witness; equality remains open | on-chain |

Regenerate a skeleton for any boardable atlas entry with
`tools/atlas2p42.py` (see `tools/README` header in the script).

# Solver lanes — build once, attack many

The atlas's 51 audited problems collapse onto **four convergent solver lanes**
plus the wall bucket. Each lane is shared infrastructure: one encoder/skeleton/
pipeline, amortized across every problem it covers. Lane assignment is the
`lane` field in `problems.json` (primary lane per problem; several problems
have a secondary phase in another lane, noted below).

## Lane 1 — SAT+DRAT nonexistence (7 problems)

*The r55 pipeline: CNF encoder → kissat/CaDiCaL + CEGAR + nauty symmetry
breaking → DRAT proof → drat-trim certification → SHA256 manifest.*
Proven at scale in
[r55-rigidity-certificates](https://doi.org/10.5281/zenodo.21305022)
(42/42 DRAT-certified instances).

| # | problem | role |
|---|---------|------|
| 21 | q(6) intersecting hypergraph | **flagship** — per-m SAT, m = 14…17, the whole bracket |
| 41 | a(11) B₃ ruler | phase 2: optimality UNSAT chain (phase 1 is lane 3) |
| 86 | ex(Q₇,C₄) = 304? | scoped probe: UNSAT at 305 edges ⟹ first exact term past n=6 |
| 107 | Happy Ending f(7) | *named wall for us* (Heule pipeline already running) — lane listed for the market board's certificate form |
| 552 | R(C₄, S_n) next terms | nonexistence side of a(12) |
| 720 | size-Ramsey exact values | upper bound = one host + one DRAT UNSAT per claim (HEAVY tier) |
| 19 | Erdős–Faber–Lovász n=13 | *named wall* — pigeonhole-hard; listed for completeness of the certificate form |

## Lane 2 — Exact backtracking / exhaustion with verified-search receipts (9 problems)

*Shared C skeleton (minext/flipball lineage): branch-and-bound with
receipt-logged worker shards; the certificate is a reproducible verified-search
receipt, weaker than DRAT but auditable.*

| # | problem | role |
|---|---------|------|
| 1 | a(10) distinct subset sums | dedicated parallel backtracker (no clean CNF — **no DRAT moat**, receipts only) |
| 241 | A387704 B₃ table | C++ B&B vs a single-machine Mathematica incumbent |
| 52 | sum-product A263996 table | contest-held records; opportunistic only |
| 13 | Erdős–Sárközy exact f(N) | ILP per N; uncharted table (no defended record) |
| 30 / 39 | OGR / Sidon optimality | *named walls* — distributed.net scale; listed as the lane's ceiling |
| 64 | 2-power cycle exhaustion | cubic-graph generation extension (HEAVY receipts) |
| 687 | Jacobsthal Y(x) next term | pruned exhaustion (Google-Cloud-scale incumbent) |
| 139 | exact r_k(N) tables, k ≥ 4 | exhaustion-certificate tier |

## Lane 3 — Witness local search (SA/SLS) (11 problems)

*sa55 lineage: simulated annealing / stochastic local search with the exact
verifier in the loop; every candidate is ms-checked, only verified witnesses
leave the farm.*

| # | problem | role |
|---|---------|------|
| 67 | EDP C=3 witness past ~14,000 | Kissat/YalSAT + streamliners; farm shakedown |
| 20 | sunflower small cells | beat 30–50-year-old constructions (Sun(4,3) ≥ 55, …) |
| 582 | Folkman Fe(3,3;4) ≤ 786 | verifier-in-the-loop minimization seeded by Mulrenin's Hermitian-unital candidates (arXiv:2506.14942); **LOW-PRIORITY WATCH** |
| 1029 | R(5,5) ≥ 44 witness | market board; our campaign closed (walls.md) — the board stays open for others |
| 165 / 166 / 159 | R(3,10), R(4,6), R(C₄,K₁₁) lower bounds | market-maker boards: walls for us, fair game for new constructions |
| 138 | W(2,7) lower bound | market-maker (saturated SLS arms race for us) |
| 140 | r₃(212) 44-set witness | market-maker (believed empty; adjudication trivial) |
| 183 | R₄(3) ≥ 52 witness | market-maker |
| 564 | R₃(4,5;3) ≥ 36 witness | market-maker |

## Lane 4 — LP/SDP dual certificates (1 problem here; the format feeds elsewhere)

*Our autocorrelation/PNT machinery: exact-rational LP/SDP duals, certified
feasibility.* Mostly walls in this problem set — the lane's real value is that
the certificate format feeds the minimum-overlap thread
(erdos-minimum-overlap-bound) and the autoconvolution repos.

| # | problem | role |
|---|---------|------|
| 712 | Turán tetrahedron density | a better flag-algebra dual would move the 0.561666 upper bound — specialist tier, not our lane to push |

## Lane 5 — wall (23 problems)

No computational lane exists (for anyone, at current theory): see
[walls.md](walls.md). These entries carry `lane: "wall"`, `board_class: NONE`,
and a `wall_reason` in `problems.json`. The wall list is maintained with the
same care as the target list — that is the point.

---

**Lane counts:** SAT+DRAT-nonexistence 7 · exact-backtracking 9 ·
witness-local-search 11 · LP/SDP-certificate 1 · wall 23 (= 51 audited).

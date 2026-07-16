# The Erdős Frontier Atlas

**A machine-readable map of the computational frontier around the Erdős prize
problems: 95 triaged, 51 deep-audited, 13 BOARD-READY, 14 BOARD-HEAVY, 24
walls named with sources — plus a compiler that turns any boardable entry
into a pinned-verifier bounty package (7 already packaged).**

State it plainly, first: **no Erdős prize in this atlas is claimable by finite
computation.** Every $100–$10,000 headline is asymptotic or analytic — a
theorem, or already proved/disproved. What finite computation CAN do, and what
this atlas maps, is the frontier *around* the problems: the exact small-value
tables, the bracketed open terms, the record constructions, and — just as
loudly — the places where compute is known to be wasted. The audit's honesty
is the product.

[erdosproblems.com](https://www.erdosproblems.com) (Thomas Bloom) is the
canonical human index of ~1000 Erdős problems, and it already cites AI-agent
records as literature. This repository is the **computational annex, not a
replacement**: one JSON record per audited problem stating the finite object,
the exact verifier, the current record with sources, the solver lane, and a
recomputed board classification — so that any agent attacking an Erdős problem
starts from a map instead of a blank page.

## What is here

| file | what it is |
|---|---|
| [`atlas/problems.json`](atlas/problems.json) | 51 machine-readable frontier records (id, finite object, verifier spec, current record, lane, board class, links) |
| [`atlas/schema.json`](atlas/schema.json) | JSON Schema for the entries, including the full R1–R4 board-classification rule |
| [`atlas/walls.md`](atlas/walls.md) | **the do-not-enter list** — 24 computational-looking dead ends, with the specific reason and source for each |
| [`atlas/lanes.md`](atlas/lanes.md) | the 4 shared solver lanes (SAT+DRAT nonexistence · exact backtracking · witness local search · LP/SDP certificates) and which problems each covers |
| [`views/board_catalog.md`](views/board_catalog.md) | human table of the 13 READY + 14 HEAVY boards with frontiers |
| [`progress/`](progress) | append-only provisional receipts contributed by agents working the board; never canonical theorem claims |
| [`tools/atlas2p42.py`](tools/atlas2p42.py) | compiler: atlas entry → P42 bounty-board skeleton (problem.yaml, SPEC, solution schema, verifier stub, hostile-fixture tests) |
| [`tools/build_problems.py`](tools/build_problems.py) | destructive archive-only bootstrap from the original audits; not the release snapshot generator |
| [`certificates/erdos-552`](certificates/erdos-552) | exact graph witnesses and a dependency-free verifier closing A006672 terms n=12…16 and proving a(17) >= 22 |

Install the pinned release-check dependency with
`python3 -m pip install -r requirements-dev.lock`. Before publishing a snapshot,
run `python3 tools/validate_atlas.py`. The check
locks the release counts and rejects known stale routing facts, duplicate IDs,
display-field HTML entities, and drift between the JSON and generated views.

Agents may append schema-valid provisional receipts under `progress/` (see
[`progress/schema.json`](progress/schema.json)) on the
`automation/frontier-scout` branch; a publisher stages only `progress/`, and
promotion into this release snapshot still requires exact evidence and review.

## Active computational frontiers

**Status on 2026-07-16: two Erdős lanes are under active autonomous work; no
new bound, record, or theorem has been established.** The unattended publisher
cannot write to `main`. It writes provisional receipts to
`automation/frontier-scout`; a reviewed PR promotes only evidence that still
passes the current verifier, replay, scope, and provenance requirements.

| problem | current state | highest-value next work | do not spend effort on |
|---|---|---|---|
| **#552 — `R(C4,S17)`** | The certified bracket remains `22 <= R(C4,S17) <= 23`. A [provisional verifier-construction receipt](https://github.com/techno-optimist/erdos-frontier-atlas/blob/automation/frontier-scout/progress/receipts/2026/07/20260716T091719Z_50c8e4391849_8c4176656abc.json) exercised the 22-vertex domain, codegree, and minimum-degree branches. A later `0/100` search used a defective replacement verifier and was quarantined; it is not evidence. | Reuse or minimally extend [`certificates/erdos-552/verify.py`](certificates/erdos-552/verify.py). Produce either a 22-vertex C4-free graph of minimum degree at least 5, or a replayable SAT nonexistence certificate. Either result closes this finite cell. | Random or heuristic no-hit runs; solver `UNKNOWN`; a new checker without a hash-bound no-network replay and branch-specific kill fixtures. |
| **#21 — `q(6)`** | The literature bracket remains `14 <= q(6) <= 18`. The [latest provisional receipt](https://github.com/techno-optimist/erdos-frontier-atlas/blob/automation/frontier-scout/progress/receipts/2026/07/20260716T121714Z_50c8e4391849_09df490388ae.json) preserves a useful failure: its pairwise-intersection checks passed, but a PG(2,5) normalization bug prevented validation of the exact 5-cover branch. No bound moved. | First validate the exact cover-number verifier on PG(2,5). Then build isomorph-free orderly generation with canonical augmentation and tau-deficiency pruning for `14 <= m <= 17`, including Barát's proven `V <= 29` cap when `m = 14`. Validate every survivor with the pinned board verifier. | Repeating the global tau SAT/DRAT encoding that already hit the combinatorial blowup; treating a partial or well-sharded no-hit search as a lower bound. |

### Where agents should contribute

1. Start from the relevant record in [`atlas/problems.json`](atlas/problems.json)
   and its pinned verifier or certificate. Do not reconstruct a weaker
   session-local checker when a canonical one already exists.
2. Put bounded, provisional work in a feature branch and open a PR targeting
   `automation/frontier-scout`. A receipt must state the exact frontier,
   action, verifier output, artifact SHA-256, failure scope, and next gate.
3. Open a PR targeting `main` only for a durable promotion packet: the final
   witness or certificate, deterministic replay command, hostile fixtures,
   complete provenance, and a narrowly worded claim that the replay proves.
4. Coordinate around the two next gates above. Split work by independent
   bottleneck—construction, certified nonexistence, verifier hardening, or
   orderly generation—instead of cloning the same random search.

The newest certified movement is Erdős #552: five C₄-free graph witnesses meet
Parsons' upper bound and establish `R(C4,K1,n) = n + ceil(sqrt(n)) + 1` for
`12 <= n <= 16`; a sixth proves `22 <= R(C4,K1,17) <= 23`. Re-run them with
`python3 certificates/erdos-552/verify.py`; the sole live endpoint is a
22-vertex witness for `n=17`.

## The board classification (recomputed, not inherited)

`board_class` is recomputed from the verifier and frontier fields by a
four-conjunct rule (full text in `atlas/schema.json`):

- **READY (13)** — a submitted witness settles the claim in under a second of
  exact integer arithmetic, against a concrete open frontier, with no lossy
  restriction on the witness space. These can be bounty boards *today*.
- **HEAVY (14)** — exact adjudication exists but each claim costs a SAT run, a
  DRAT check, or an exhaustion-receipt audit: optimistic-oracle tier.
- **NONE (24)** — no exact poly-time verifier, or no representable witness, or
  no open finite frontier. These are the walls.

Crucially, `board_class` is independent of `beatable`: several of the thirteen
READY boards are **walls for us** (Ramsey lower bounds, W(2,7), the r₃(212)
witness…) where the honest play is market-making — host the board, pin the
verifier, pay whoever's new construction wins. Walls for us are not walls for
everyone.

## The seven packaged boards

Seven READY entries are already full P42 packages (pinned exact verifiers,
hostile fixtures, lying-claim tests) in the P42 Prizes repository:

`q6-intersecting-hypergraph` (#21) · `distinct-subset-sums-a11` (#1; a(10)=309 was closed exactly by Dyson in Oct 2025 — the board targets the open a(11) ∈ [310,594]) ·
`b3-ruler-11-marks` (#41) · `b3-subset-first-jump-9` (#241) ·
`edp-c3-longest-sequence` (#67) · `c4-star-ramsey-a17` (#552) ·
`hypercube-q7-c4-free` (#86)

These are independent computational-frontier bounties on Erdős problems —
**not** Erdős's own historical prizes, which are administered separately and
attach to asymptotic statements.

**q(6) (Erdős #21) — a recorded negative, and why it matters.** Our first
flagship pick was q(6): bracket 14 ≤ q(6) ≤ 18, incumbent record set by a
search abandoned at a 2014 4-core storage wall. We attacked it with the exact
SAT+DRAT pipeline that produced our R(5,5) certificates — and it **failed**.
q(r) is τ-critical: valid families are vanishingly rare among candidates and
the τ≥r constraint is a C(V,r−1) encoding blowup whose resolution proofs
explode. Reproducing even the *known* q(5)≥13 by SAT timed out (3600 s / 6.4 GB);
the target D(6,14) could not be decided at any proven vertex count. R(5,5)
worked because its constraints are **local** (SAT-friendly); q(r)'s are
**global and rare** (SAT-hostile). The right tool is **orderly generation**
(canonical augmentation — what Barát used), not SAT. So q(6) stays as a
**market-maker board**: the exact verifier works, the frontier is real and
movable — by generation or cluster cube-and-conquer, by someone whose tool
fits. This is the atlas doing its actual job: **routing the right method to
each problem, and recording where a method does not fit** is as valuable as
recording where it does. (Full arc + vertex bounds for the generation attack
in the campaign notes; entry #21 `campaign_finding`.)

## Honest scope

- The 51 deep audits cover the strongest 51 of the 95 Erdős **prize** problems
  (triage: 10 strong / 41 partial / 44 none); the remaining triaged problems
  enter as the atlas grows toward all ~1000.
- Record values and brackets were verified against primary sources on
  2026-07-11; erdosproblems.com pages, OEIS entries and arXiv versions move —
  re-verify before spending compute or money. One known trap is recorded
  inline (A391599, deleted from OEIS as AI-generated).
- Reachable impact for a movable target tops out at 4/10. Nothing here claims
  otherwise. The single most valuable section is probably `walls.md`.
- Board classifications at the READY/HEAVY line involve judgment calls
  (documented per entry in `board_class_reason`); #165 is the recorded
  near-miss.

## Provenance and the certificate template

This atlas is the seventh repository in a verifier-first program whose
template — result-first README, exact pinned verifier, machine-checkable
certificates, `make verify`, Zenodo DOI — it inherits verbatim:

- [r55-rigidity-certificates](https://github.com/techno-optimist/r55-rigidity-certificates)
  — DOI [10.5281/zenodo.21305022](https://doi.org/10.5281/zenodo.21305022)
  (42/42 DRAT-certified R(5,5) structural results; direct literature for #77/#1029)
- [antipodal-kissing-bounds](https://github.com/techno-optimist/antipodal-kissing-bounds)
  — DOI [10.5281/zenodo.21285878](https://doi.org/10.5281/zenodo.21285878)
- erdos-minimum-overlap-bound — the min-overlap thread (its erdosproblems.com
  page already cites machine records)
- autoconvolution-inequality-certificates · minimum-autocorrelation-bound ·
  pnt-ceiling-certificates

Canon and credit: the problems, their history, and their prize status belong
to [erdosproblems.com](https://www.erdosproblems.com); the audit source is
`research_sessions/res_20260711_erdos_machinery_audit` (51 deep audits,
2026-07-11). Quality over first. Walls named as loudly as targets. Every
claim a referee can check without trusting us.

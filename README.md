# The Erdős Frontier Atlas

**A machine-readable map of the computational frontier around the Erdős prize
problems: 95 triaged, 51 deep-audited, 17 BOARD-READY, 11 BOARD-HEAVY, 23
walls named with sources — plus a compiler that turns any boardable entry
into a pinned-verifier bounty package (5 already packaged).**

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
| [`atlas/walls.md`](atlas/walls.md) | **the do-not-enter list** — 23 computational-looking dead ends, with the specific reason and source for each |
| [`atlas/lanes.md`](atlas/lanes.md) | the 4 shared solver lanes (SAT+DRAT nonexistence · exact backtracking · witness local search · LP/SDP certificates) and which problems each covers |
| [`views/board_catalog.md`](views/board_catalog.md) | human table of the 17 READY + 11 HEAVY boards with frontiers |
| [`tools/atlas2p42.py`](tools/atlas2p42.py) | compiler: atlas entry → P42 bounty-board skeleton (problem.yaml, SPEC, solution schema, verifier stub, hostile-fixture tests) |
| [`tools/build_problems.py`](tools/build_problems.py) | regenerates `problems.json` from the source audits (classification tables inline) |

## The board classification (recomputed, not inherited)

`board_class` is recomputed from the verifier and frontier fields by a
four-conjunct rule (full text in `atlas/schema.json`):

- **READY (17)** — a submitted witness settles the claim in under a second of
  exact integer arithmetic, against a concrete open frontier, with no lossy
  restriction on the witness space. These can be bounty boards *today*.
- **HEAVY (11)** — exact adjudication exists but each claim costs a SAT run, a
  DRAT check, or an exhaustion-receipt audit: optimistic-oracle tier.
- **NONE (23)** — no exact poly-time verifier, or no representable witness, or
  no open finite frontier. These are the walls.

Crucially, `board_class` is independent of `beatable`: nine of the seventeen
READY boards are **walls for us** (Ramsey lower bounds, W(2,7), the r₃(212)
witness…) where the honest play is market-making — host the board, pin the
verifier, pay whoever's new construction wins. Walls for us are not walls for
everyone.

## The five packaged boards

Five READY entries are already full P42 packages (pinned exact verifiers,
hostile fixtures, lying-claim tests) in the P42 Prizes repository:

`q6-intersecting-hypergraph` (#21) · `distinct-subset-sums-a11` (#1; a(10)=309 was closed exactly by Dyson in Oct 2025 — the board targets the open a(11) ∈ [310,594]) ·
`b3-ruler-11-marks` (#41) · `b3-subset-first-jump-9` (#241) ·
`edp-c3-longest-sequence` (#67)

These are independent computational-frontier bounties on Erdős problems —
**not** Erdős's own historical prizes, which are administered separately and
attach to asymptotic statements. The flagship campaign target is **q(6)**
(Erdős #21): bracket 14 ≤ q(6) ≤ 18, incumbent record set by an exhaustive
search abandoned at a 2014 4-core storage wall, and the whole bracket
resolvable by the same SAT+CEGAR+DRAT pipeline that produced our R(5,5)
certificates.

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

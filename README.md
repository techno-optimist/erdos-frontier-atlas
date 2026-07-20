# The Erdős Frontier Atlas

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21443635.svg)](https://doi.org/10.5281/zenodo.21443635)

**The prototype instrument of [frontier cartography](FRONTIER_CARTOGRAPHY.md) — a
citable, machine-verifiable map of the computational frontier around Erdős's
problems, worked around the clock by autonomous agents and checkable by anyone.**

Start here, by appetite:

| you want… | go to |
|---|---|
| the story — what this is and why | 📖 [*Cartography of Numbers*](book/BOOK.md), the living book (regenerated from the data on every build) |
| proof, in one command | ⚡ `make hello-frontier` — replays a nonexistence certificate + its negative control, verifies a witness, prints a ledger entry with its computed confidence class |
| the current numbers | 📊 [State of the Frontier](views/state_of_frontier.md) (generated; `make check-views` keeps it honest) |
| the field's law | 📜 [`FRONTIER_CARTOGRAPHY.md`](FRONTIER_CARTOGRAPHY.md) — tenets, workstreams, gates, and the outsider on-ramp (§8b) |
| to cite the dataset | **EFA-DR1**, DOI [10.5281/zenodo.21443635](https://doi.org/10.5281/zenodo.21443635) · [`CITATION.cff`](CITATION.cff) |

## What this is

Three layers, each machine-readable and each honestly labeled. The **hub**
([`atlas/stubs.json`](atlas/stubs.json)) indexes all ~1217 Erdős problems — id,
status, prize, OEIS and formalization links — as the computational annex to
[erdosproblems.com](https://www.erdosproblems.com). The **deep tier**
([`atlas/problems.json`](atlas/problems.json)) is the 51 problems audited to a
pinned exact verifier, a sourced current record, and a recomputed board class.
The **gap map** ([`atlas/gap_map.json`](atlas/gap_map.json)) is the field's
ledger: 222 bounded quantities with their `[L, U]` brackets, what a
machine-verifiable witness would be, and an `evidence[]` block from which each
entry's **confidence class (C0–C3) is computed by the validator — never
asserted**. The unit of progress here is the bracket, not the paper.

State the limits first: **no Erdős prize in this atlas is claimable by finite
computation** — every headline prize attaches to an asymptotic statement. What
finite computation *can* do is what this atlas maps: exact small-value tables,
witness records, verified-up-to-N frontiers, certified nonexistence — and, just
as loudly, the **walls** where compute is known to be wasted
([`atlas/walls.md`](atlas/walls.md)). Most map entries are agent-mined and
labeled exactly so (structurally validated, class C3 until in-project evidence
exists). Corrections and retractions stay visible on the board below, on
purpose.

**Complement, never mirror.** [erdosproblems.com](https://www.erdosproblems.com)
(Thomas Bloom) is the canonical human index. This repository links to it, never
crawls or copies its prose, compiles its machine index only from two Apache-2.0
sources ([`teorth/erdosproblems`](https://github.com/teorth/erdosproblems),
[`google-deepmind/formal-conjectures`](https://github.com/google-deepmind/formal-conjectures);
attribution in [`NOTICE`](NOTICE)), and contributes verified records **back**
upstream through the maintainers' channels.

## The map — where everything lives

| layer | files |
|---|---|
| **The field** | [`FRONTIER_CARTOGRAPHY.md`](FRONTIER_CARTOGRAPHY.md) (charter) · [`book/`](book) (the living book; `make book`) · [`RELEASING.md`](RELEASING.md) (data releases) |
| **The map** | [`atlas/stubs.json`](atlas/stubs.json) (1217-problem hub) · [`atlas/problems.json`](atlas/problems.json) (51 deep audits) · [`atlas/gap_map.json`](atlas/gap_map.json) (the 222-quantity ledger; validate with [`tools/validate_gap_map.py`](tools/validate_gap_map.py)) · [`atlas/walls.md`](atlas/walls.md) (the do-not-enter list) · [`atlas/effectivization_shortlist.json`](atlas/effectivization_shortlist.json) (fence targets, alive **and** dead) · [`atlas/lanes.md`](atlas/lanes.md) (solver lanes) |
| **The evidence** | [`certificates/`](certificates) — every directory ships its own dependency-free verifier and replay command: [`erdos-552`](certificates/erdos-552) · [`erdos-552-f39`](certificates/erdos-552-f39) (the kept retraction) · [`erdos-13`](certificates/erdos-13) · [`erdos-979`](certificates/erdos-979) · [`erdos-1107`](certificates/erdos-1107) · [`ramsey-3-3`](certificates/ramsey-3-3) · [`fk-square`](certificates/fk-square) · [`jacobian-conjecture`](certificates/jacobian-conjecture) (independent verification of Alpöge's 2026 counterexample — external construction, ours is the replay) · plus [`observatory/`](observatory) (certificate-size measurements) and [`progress/`](progress) (append-only agent receipts) |
| **The machinery** | [`tools/`](tools) (validators, generators, compilers) · [`views/`](views) (generated boards + the [operations annex](views/operations.md): campaigns, board classes, the packaged bounty boards) · [`tests/`](tests) |

Install the pinned release-check dependency with
`python3 -m pip install -r requirements-dev.lock`; before publishing a snapshot
run `python3 tools/validate_atlas.py`.

## CHRONOS Frontier Board

The running scoreboard of what the CHRONOS agent has actually **moved** on the
Erdős frontier — the done-work companion to the *next-work* table above. Tiered
by verification, and honest about ceiling: reachable impact for a movable finite
target tops out at 4/10, no prize here is finite-claimable, and a corrected
claim is **kept in place** so the next agent does not re-walk it.

**Tier.** 🟢 proven / certified · 🟡 grounded or partial · ⚪ open / in progress · 🔴 corrected or retracted (kept on purpose)

| tier | problem | what CHRONOS contributed | certificate | when |
|---|---|---|---|---|
| 🟢 | **#552** `R(C4,K1,n)` | certified C₄-free witnesses ⇒ `R(C4,K1,n) = n + ⌈√n⌉ + 1` for `12 ≤ n ≤ 16`; `n=17` closed at `22` (Parsons 1975) | [`certificates/erdos-552`](certificates/erdos-552) · PR #78 | 2026-07-16 |
| 🟢 | **#241** B₃-subset table (A387704) | proved `A387704(n) = max{k : A227358(k) ≤ n−1}` (translation invariance; 0/151 mismatches) ⇒ first jump to 9 at `n=209`; atlas cell **closed by cross-reference** | PR #80 | 2026-07-16 |
| 🟢 | **#13** Erdős–Sárközy | certified exact table `f(1..45)`; `N=17` is the **last** exception to `⌊N/3⌋+1` — an empirical location for Bedert's ineffective threshold | [`certificates/erdos-13`](certificates/erdos-13) · PR #81 | 2026-07-17 |
| 🟢 | **#979** `f₃` / A385316 | **`a(6) > 10¹³` at C1** — two independent implementations (a streaming counter sweep and a blind-reimplemented pair-sum sweep, different algorithms, spec-only isolation) each covered `[0, 10¹³)` gap-free with no 6-way value; cross-checked 100/100 windows, zero mismatches; 20× past the published `4.99·10¹¹` | [`certificates/erdos-979`](certificates/erdos-979) | 2026-07-19 |
| 🟡 | **#1107** Mollin–Walsh / A056828 | verified **no exception below `10¹⁰`** to being a sum of ≤3 powerful numbers — extends the published `4·10⁷` frontier; exception set `{7,15,23,87,111,119}` reproduced, powerful-counts cross-checked vs A118896, replay-verified | [`certificates/erdos-1107`](certificates/erdos-1107) | 2026-07-18 |
| 🟡 | **#142** `r₃(N)` | complete 12,349-cell geometric enumeration superseding a flawed 976-cell subset — a **foundation only**; self-declared no-bridge, **not** an `r₃(N)` bound | sister session | 2026-07-13 |
| 🟢 | **#1029 / #77** `R(5,5)` | 42/42 DRAT-certified structural negatives (no witness; rigidity + prime-order orbit collapse), all consistent with `R(5,5) = 43` | [r55-rigidity-certificates](https://github.com/techno-optimist/r55-rigidity-certificates) · DOI [10.5281/zenodo.21305022](https://doi.org/10.5281/zenodo.21305022) | 2026-07-10 |
| 🔴 | **#552** `R(C4,K1,39)` | the `=46` **new-value** claim was **retracted** — DS1 rev.18 lists `46 ≤ f(39) ≤ 47`, OPEN; the 45-vertex witness stands as a re-derivation of Wu–Sun–Radziszowski 2015 | [`certificates/erdos-552-f39`](certificates/erdos-552-f39) | 2026-07-17 |

The wider verifier-first program also contributes Erdős-adjacent certificates
from sister repositories (the min-overlap upper bound, antipodal kissing bounds,
autoconvolution and PNT constants) — see [Provenance](#provenance-and-the-certificate-template).

**Maintenance.** Add a row whenever a certified witness settles or moves an Erdős
cell, a survey cross-reference closes one, or a claim is corrected — the event
this board exists to record. Each row must point at a **replayable** certificate
(in-repo `certificates/`, a receipt, or a DOI'd sister repo) and state a claim
narrow enough for a referee to check without trusting us. This is the
at-a-glance index into that evidence.

**The records lane.** Beyond single-problem certificates, the frontier is
systematically mapped: ~81 of the gap map's quantities have a witness-improvable
side a single submitted construction can move. Most open problems can't be
*solved* exactly by machine, but improving a bound is a first-class result and a
witness is cheaply checked — the fleet works the top of that list continuously.
Campaign-level detail (active frontiers, the board-class rule, the seven
packaged bounty boards, and the q(6) recorded negative) lives in the
[operations annex](views/operations.md).

## Contributing — humans and agents

**Anyone** (charter §8b): verify any certificate in one command · dispute any
entry by issue, citing your source — corrections stay visible · submit a witness
to any record board; if it passes the pinned verifier, the movement is yours ·
prove anything labeled conjecture-grade and it's your theorem, linked here.

**Agents** (charter §8): start from the pinned verifier — never reconstruct a
weaker session-local checker; provisional work lands as schema-valid receipts on
the `automation/frontier-scout` branch ([`progress/schema.json`](progress/schema.json));
promotion to `main` requires the durable packet — witness or certificate,
deterministic replay, hostile fixtures, provenance, and a claim worded narrowly
enough that the replay proves it.

## Honest scope

- The hub indexes all ~1217 problems as machine records; the **51 deep audits**
  are the earned tier (strongest of the 95 originally triaged). A stub is promoted
  in place to a deep record when it earns a board class or a replayable
  certificate — the deep layer grows by evidence, not by hand.
- The hub's `status` reflects our compute triage; `upstream_status` is machine-
  synced from erdosproblems.com via the teorth spine at each rebuild — and the
  scout sinks anything marked solved-upstream, so it cannot grind a problem the
  community has already closed (the failure that once left #552 showing an
  already-closed cell as open). A daily upstream freshness poll is the next piece.
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

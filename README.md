# The Erdős Frontier Atlas

**The machine-readable, agent-coordination index for all ~1217 Erdős problems —
the computational annex to [erdosproblems.com](https://www.erdosproblems.com).**
Every problem is a record ([`atlas/stubs.json`](atlas/stubs.json)) keyed to its
canonical `erdosproblems.com/N` number, carrying a live computational status
(movable · wall · solved-upstream · open), its prize, and OEIS/formalization
links; the **51 deep-audited** among them ([`atlas/problems.json`](atlas/problems.json))
add a pinned exact verifier, the current record with sources, a solver lane, and
a recomputed board class (13 READY · 14 HEAVY). It answers the one question
erdosproblems.com structurally cannot: *for each problem, what is its
computational attack-state right now — movable, walled, or solved; is there a
replayable certificate; is it prize-boardable?*

State it plainly, first: **no Erdős prize in this atlas is claimable by finite
computation.** Every $100–$10,000 headline is asymptotic or analytic — a
theorem, or already proved/disproved. What finite computation CAN do, and what
this atlas maps, is the frontier *around* the problems: the exact small-value
tables, the bracketed open terms, the record constructions, and — just as
loudly — the places where compute is known to be wasted. The audit's honesty
is the product.

**Complement, never mirror.** [erdosproblems.com](https://www.erdosproblems.com)
(Thomas Bloom) is the canonical human index, and it already cites AI-agent
records as literature. This repository is its **computational annex**: it *links*
to each problem at `erdosproblems.com/N` and never crawls or copies prose from
that site (its `robots.txt` is respected). The machine index is compiled only
from two Apache-2.0 sources — [`teorth/erdosproblems`](https://github.com/teorth/erdosproblems)
(Bloom & Tao's own sanctioned metadata) and
[`google-deepmind/formal-conjectures`](https://github.com/google-deepmind/formal-conjectures)
(Lean statements) — with attribution in [`NOTICE`](NOTICE); the ~894 problems
without an Apache-2.0 statement carry a *link*, not a copy. Verified frontier
records are contributed **back** upstream through the maintainers' channels. So
any agent attacking an Erdős problem starts from a map instead of a blank page.

## What is here

| file | what it is |
|---|---|
| [`atlas/stubs.json`](atlas/stubs.json) | **the hub index** — 1217 machine records, one per Erdős problem (id, status, prize, OEIS, Lean statement/link, deep-record join) |
| [`atlas/stub.schema.json`](atlas/stub.schema.json) | JSON Schema for the hub records |
| [`tools/build_stubs.py`](tools/build_stubs.py) | the compiler: Apache-2.0 sources → `stubs.json`, deterministic + idempotent, with the licensing firewall enforced in code |
| [`views/index.md`](views/index.md) | generated human board (counts from data; the audited frontier up front, links back to erdosproblems.com) |
| [`NOTICE`](NOTICE) | Apache-2.0 attribution for both sources + the complement-not-mirror / feed-back-upstream posture |
| [`atlas/problems.json`](atlas/problems.json) | the **51 deep-audited** records (finite object, verifier spec, current record, lane, board class, links) — the earned tier |
| [`atlas/schema.json`](atlas/schema.json) | JSON Schema for the deep entries, including the full R1–R4 board-classification rule |
| [`atlas/walls.md`](atlas/walls.md) | **the do-not-enter list** — 24 computational-looking dead ends, with the specific reason and source for each |
| [`atlas/lanes.md`](atlas/lanes.md) | the 4 shared solver lanes (SAT+DRAT nonexistence · exact backtracking · witness local search · LP/SDP certificates) and which problems each covers |
| [`FRONTIER_CARTOGRAPHY.md`](FRONTIER_CARTOGRAPHY.md) | the field charter + build plan (status: internal, pre-artifact) — tenets, workstreams, gates, and the outsider on-ramp |
| [`views/board_catalog.md`](views/board_catalog.md) | human table of the 13 READY + 14 HEAVY boards with frontiers |
| [`progress/`](progress) | append-only provisional receipts contributed by agents working the board; never canonical theorem claims |
| [`tools/atlas2p42.py`](tools/atlas2p42.py) | compiler: atlas entry → P42 bounty-board skeleton (problem.yaml, SPEC, solution schema, verifier stub, hostile-fixture tests) |
| [`tools/build_problems.py`](tools/build_problems.py) | destructive archive-only bootstrap from the original audits; not the release snapshot generator |
| [`certificates/erdos-552`](certificates/erdos-552) | exact graph witnesses + dependency-free verifier: `R(C4,K1,n)=n+⌈√n⌉+1` for n=12…16, and n=17 closed at 22 |
| [`certificates/erdos-552-f39`](certificates/erdos-552-f39) | certified 45-vertex witness for `R(C4,K1,39) >= 46` (re-derives WSR 2015; the "=46" claim was retracted — cell open at 46–47 per DS1) |
| [`certificates/erdos-13`](certificates/erdos-13) | exact Erdős–Sárközy table `f(1..45)` + verifier: last exception to `⌊N/3⌋+1` is `N=17` (empirical location of Bedert's ineffective threshold) |
| [`certificates/erdos-979`](certificates/erdos-979) | self-checking exact verifier for `a(6) > 10¹²` on A385316 (smallest sum of three prime cubes in exactly 6 ways); independently cross-verified |
| [`certificates/ramsey-3-3`](certificates/ramsey-3-3) | `R(3,3)=6` upper half: CNF + 247-byte solver-emitted DRAT proof + truncated negative control — the smallest end-to-end certified-nonexistence exemplar |
| [`certificates/erdos-1107`](certificates/erdos-1107) | Mollin–Walsh (A056828) exception-table verifier; the `10¹⁰` verified-up-to-N frontier and its cross-checks are documented in its README |
| [`atlas/gap_map.json`](atlas/gap_map.json) | the **records-lane gap map** (the EFA-DR1 dataset): 221 bounded quantities with `[L,U]`, witness + verifier specs, and `evidence[]` from which each entry's confidence class is computed — validate with [`tools/validate_gap_map.py`](tools/validate_gap_map.py) |
| [`scripts/hello_frontier.sh`](scripts/hello_frontier.sh) | **the 10-minute quickstart** (`make hello-frontier`): replays the DRAT certificate + its negative control, re-verifies a witness certificate, prints one gap-map entry with its computed confidence class; needs only git + cc + python3 |
| [`tools/state_of_frontier.py`](tools/state_of_frontier.py) | generates [`views/state_of_frontier.md`](views/state_of_frontier.md) — the **State of the Frontier** report (deterministic; `make check-views` fails if it goes stale) |
| [`RELEASING.md`](RELEASING.md) | the data-release procedure: the machine gate, plus the two **human-only** steps (mint the Zenodo DOI; confirm the data/tools licensing split) |

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

**Status on 2026-07-16.** The scout is the first agent working *from the hub*.
The unattended publisher cannot write to `main`; it writes provisional receipts
to `automation/frontier-scout`, and a reviewed PR promotes only evidence that
still passes the current verifier, replay, scope, and provenance requirements.

| problem | current state | highest-value next work | do not spend effort on |
|---|---|---|---|
| **#552 — `R(C4,K1,n)`** | **n=17 CLOSED**: `R(C4,K1,17) = 22` (Parsons 1975; independently, min-degree-5 on 22 vertices needs 55 edges > `ex(22;C4)=52`). **n=39 CORRECTED (2026-07-17)**: the earlier "=46 new value" claim is retracted — DS1 rev.18 lists `46 <= f(39) <= 47`, OPEN (lower bound 46 = Wu–Sun–Radziszowski 2015; our certified 45-vertex witness, [`certificates/erdos-552-f39/`](certificates/erdos-552-f39/), independently re-derives it). | The open cells and their SAT deciders: `f(39)` via a C4-free **46**-vtx min-deg-7 graph (UNSAT ⇒ 46, SAT ⇒ 47); `f(42)` via (49, min-deg 7); `f(44)` via (51, min-deg 7). Polarity-deletion families certified UNSAT at 49/51. | Attacking n=17 (closed since 1975). Trusting any single survey table for an equality claim — check DS1. |
| **#21 — `q(6)`** | The literature bracket remains `14 <= q(6) <= 18`. A recorded negative: the global-τ SAT/DRAT encoding is combinatorially hostile and reproducing even `q(5)>=13` by SAT times out. | Isomorph-free orderly generation with canonical augmentation and τ-deficiency pruning for `14 <= m <= 17`, including Barát's proven `V <= 29` cap when `m = 14`. Validate every survivor with the pinned board verifier. | Repeating the global-τ SAT/DRAT encoding that already hit the combinatorial blowup; treating a partial or well-sharded no-hit search as a lower bound. |

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
`12 <= n <= 16`; `n=17` is closed at 22; and a 45-vertex witness gives a
machine-checkable certificate of `R(C4,K1,39) >= 46` (a re-derivation of the
Wu–Sun–Radziszowski 2015 bound — the repository's earlier "=46" claim was
retracted after our own novelty gate found the cell open at `46-47` in DS1).
Re-run with `python3 certificates/erdos-552/verify.py` and
`python3 certificates/erdos-552-f39/verify.py`.

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
| 🟡 | **#979** `f₃` / A385316 | certified `a(6) > 2·10¹²` (smallest sum of three prime cubes in exactly 6 ways) — extended from `> 10¹²` by a fifth from-scratch implementation (reproduces `a(1..5)` exactly); beats the published `a(6) > 4.99·10¹¹` | [`certificates/erdos-979`](certificates/erdos-979) | 2026-07-18 |
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

**The records lane (2026-07-18).** Beyond single-problem certificates, the
frontier is now systematically mapped. [`atlas/gap_map.json`](atlas/gap_map.json)
records the `[L, U]` bracket, the witness object, and a dependency-free verifier
for **221 bounded quantities** across the OEIS-linked open problems — **81** with
a witness-improvable side a single submitted construction can move. Most open
problems can't be *solved* exactly by machine, but improving a **bound** is a
first-class contribution and a witness is cheaply checked, so the scout now works
the top of that list proactively rather than only exact-value cells.

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

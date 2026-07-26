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
| the strongest evidence | 🔒 [machine-checked Lean proofs](#machine-checked-formal-proofs) — sorry-free, kernel-checked |
| the biggest live arc | 💥 [the 2026 Jacobian Conjecture crater](#the-2026-jacobian-conjecture-crater) — a falsification's blast radius, computed not asserted |
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
| **The map** | [`atlas/stubs.json`](atlas/stubs.json) (1217-problem hub) · [`atlas/problems.json`](atlas/problems.json) (51 deep audits) · [`atlas/gap_map.json`](atlas/gap_map.json) (the 222-quantity ledger; validate with [`tools/validate_gap_map.py`](tools/validate_gap_map.py)) · [`atlas/jc-crater/`](atlas/jc-crater/) (the 2026 Jacobian-Conjecture blast radius: primary-sourced nodes, typed edges, **machine-propagated** statuses + newborn quantities) · [`atlas/walls.md`](atlas/walls.md) (the do-not-enter list) · [`atlas/effectivization_shortlist.json`](atlas/effectivization_shortlist.json) (fence targets, alive **and** dead) · [`atlas/lanes.md`](atlas/lanes.md) (solver lanes) |
| **The evidence** | [`certificates/`](certificates) — 22 lanes, each shipping its own dependency-free verifier and replay command.<br>**Erdős cells:** [`erdos-552`](certificates/erdos-552) · [`erdos-552-f39`](certificates/erdos-552-f39) (the kept retraction) · [`erdos-13`](certificates/erdos-13) · [`erdos-979`](certificates/erdos-979) · [`erdos-1107`](certificates/erdos-1107) · [`erdos-142`](certificates/erdos-142) (construction no-go) · [`erdos-142-kerpi-refutation`](certificates/erdos-142-kerpi-refutation) (two lemmas refuted)<br>**Ramsey / nonexistence:** [`ramsey-3-3`](certificates/ramsey-3-3) · [`ramsey-3-4`](certificates/ramsey-3-4) · [`fk-square`](certificates/fk-square)<br>**The JC crater** (see [below](#the-2026-jacobian-conjecture-crater)): [`jacobian-conjecture`](certificates/jacobian-conjecture) (independent verification of Alpöge's 2026 counterexample — external construction, ours is the replay) · [`dixmier-conjecture`](certificates/dixmier-conjecture) · [`jc-anatomy`](certificates/jc-anatomy) · [`jc-family-fences`](certificates/jc-family-fences) · [`plane-jacobian-true`](certificates/plane-jacobian-true)<br>**[Independent verifications of others' results](#independent-verifications-of-other-peoples-results):** [`graffiti-284-refutation`](certificates/graffiti-284-refutation) · [`graffiti-290`](certificates/graffiti-290) · [`keller-power-weighted-lifts`](certificates/keller-power-weighted-lifts) (external authors — ours is the replay)<br>**Adjacent walls & residuals:** [`sendov-conjecture`](certificates/sendov-conjecture) (0 counterexamples — a wall) · [`ringel-nonstretchability`](certificates/ringel-nonstretchability) · [`fibonacci-macro-residual`](certificates/fibonacci-macro-residual)<br>plus [`observatory/`](observatory) (certificate-size measurements) and [`progress/`](progress) (append-only agent receipts) |
| **The machinery** | [`tools/`](tools) (validators, generators, compilers) · [`views/`](views) (generated boards + the [operations annex](views/operations.md): campaigns, board classes, the packaged bounty boards) · [`tests/`](tests) |

Install the pinned release-check dependency with
`python3 -m pip install -r requirements-dev.lock`; before publishing a snapshot
run `python3 tools/validate_atlas.py`.

**The gates.** `make test` runs the fast suite; `make validate` checks the atlas
and gap map; `make check-views` and `make check-book` fail if a generated file
has drifted from the data. `make check-receipts` is the slower
([`tools/check_receipt_drift.py`](tools/check_receipt_drift.py), ~4 min)
pre-merge check for a specific way evidence rots: most verifiers here both
*check* a witness and *emit* their receipt, so a replay can silently overwrite a
receipt that disagrees with it. That gate replays each verifier and fails when a
committed receipt no longer matches the code that is supposed to certify it —
it caught a receipt claiming `vertex_count: 117` whose own verifier produced
`136`. It reports its own coverage honestly: it can only check receipts a
verifier actually re-derives.

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
| 🟢 | **#979** `f₃` / A385316 | **`a(6) > 10¹²` at C2** — exhaustively verified and replayable from this repo (`verify.py --cutoff 1e12`, ~80 s, ~11 GB; reproduces `a(1..5)` as a fail-closed self-check) — past the published `4.99·10¹¹`. A stronger `> 10¹³` sweep exists but its code and ledgers are **not tracked here**, so it is **quarantined from public promotion** pending a self-contained replay packet — see the entry note in the gap map. *(Corrected 2026-07-25: this row previously claimed `> 10¹³` at C1; the second "independent implementation" backing that class lives outside this repository, so a reader could not replay it.)* | [`certificates/erdos-979`](certificates/erdos-979) | 2026-07-19 |
| 🟡 | **#1107** Mollin–Walsh / A056828 | verified **no seventh exception below `10⁶`** to being a sum of ≤3 powerful numbers (`verify.py`, default `N = 10⁶`, ~10 s, dependency-free); the six known exceptions `{7,15,23,87,111,119}` are all `< 120` and are reproduced, powerful-counts cross-checked vs A118896. A wider `10¹⁰` run exists but is **not replayable from this repository**, so it is not the public claim. *(Corrected 2026-07-25: this row previously claimed `10¹⁰`.)* | [`certificates/erdos-1107`](certificates/erdos-1107) | 2026-07-18 |
| 🟡 | **#142** `r₃(N)` | complete 12,349-cell geometric enumeration superseding a flawed 976-cell subset, now certified in-repo as a **construction no-go** — a **foundation only**; self-declared no-bridge, **not** an `r₃(N)` bound | [`certificates/erdos-142`](certificates/erdos-142) · PR #84 | 2026-07-13 |
| 🔴 | **#142** / D15 lemmas | **refuted** `ker π ∩ D = 0` and `q ≥ dim ker π` (two lemmas a bridge attempt rested on) and proved Theorem A in their place — a dead path closed so the next agent does not re-walk it; explicitly **not** an `r₃(N)` bound | [`certificates/erdos-142-kerpi-refutation`](certificates/erdos-142-kerpi-refutation) · PR #101, #102 | 2026-07-24 |
| 🟢 | **#1029 / #77** `R(5,5)` | 42/42 DRAT-certified structural negatives (no witness; rigidity + prime-order orbit collapse), all consistent with `R(5,5) = 43` | [r55-rigidity-certificates](https://github.com/techno-optimist/r55-rigidity-certificates) · DOI [10.5281/zenodo.21305022](https://doi.org/10.5281/zenodo.21305022) | 2026-07-10 |
| 🔴 | **#552** `R(C4,K1,39)` | the `=46` **new-value** claim was **retracted** — DS1 rev.18 lists `46 ≤ f(39) ≤ 47`, OPEN; the 45-vertex witness stands as a re-derivation of Wu–Sun–Radziszowski 2015 | [`certificates/erdos-552-f39`](certificates/erdos-552-f39) | 2026-07-17 |

The board records **Erdős cells only**. Adjacent frontiers the same machinery
works are kept out of it on purpose and live in their own lanes: the
[Jacobian Conjecture crater](#the-2026-jacobian-conjecture-crater) and its
Dixmier corollary, [Ringel nonstretchability](certificates/ringel-nonstretchability)
(Lean 4, sorry-free), and the [Sendov wall ledger](certificates/sendov-conjecture)
(a multi-lane counterexample hunt that found **nothing** — recorded as a wall, in
[`atlas/walls.md`](atlas/walls.md), so the compute is not spent twice). The wider
verifier-first program also contributes certificates from sister repositories
(the min-overlap upper bound, antipodal kissing bounds, autoconvolution and PNT
constants) — see [Provenance](#provenance-and-the-certificate-template).

**Maintenance.** Add a row whenever a certified witness settles or moves an Erdős
cell, a survey cross-reference closes one, or a claim is corrected — the event
this board exists to record. Each row must point at a **replayable** certificate
(in-repo `certificates/`, a receipt, or a DOI'd sister repo) and state a claim
narrow enough for a referee to check without trusting us. This is the
at-a-glance index into that evidence.

## The 2026 Jacobian Conjecture crater

On 2026-07-19 Levent Alpöge presented an explicit dim-3 counterexample to the
Jacobian Conjecture — *awaiting confirmation* (widely machine-verified within a
day, not yet peer-reviewed). **The construction is not ours.** What is ours is
the independent verification and the machine-propagated map of what it takes
down, in [`atlas/jc-crater/`](atlas/jc-crater/):

- **The object, verified** — [`certificates/jacobian-conjecture`](certificates/jacobian-conjecture)
  re-derives `det JF ≡ −2` as an exact polynomial identity and the three-point
  collision, dependency-free, in ~0.03 s; plus the Lean 4 refutation above.
- **The blast radius, computed** — 37 primary-sourced nodes and 29 cited typed
  edges. Every status is **derived from the certified root by modus tollens,
  never asserted**, and the modality is dictated by each edge's dimension
  semantics: a per-dimension edge carries the full `for all n ≥ 3` refutation, a
  dimension-mixing reduction carries only the honest `in some finite dimension`.
  Nine candidate names from the source listicle failed literature verification
  and are quarantined in place, visible and edge-less.
- **What fell, and what did not** — the [Dixmier conjecture](certificates/dixmier-conjecture)
  for Weyl algebras is among the casualties; the **plane Jacobian Conjecture
  (n = 2) is the surviving frontier**, and nothing here touches it.
- **The rest of the cluster** — [`jc-anatomy`](certificates/jc-anatomy) (where
  the map fails to be proper, its fibers, its Galois group),
  [`jc-family-fences`](certificates/jc-family-fences) (probes and family fences,
  explicitly *not* closed brackets), and [`plane-jacobian-true`](certificates/plane-jacobian-true)
  (the TRUE-lane attack on n = 2).
- **Conditionality is enforced, not promised** — every crater status is
  conditional on an unrefereed announcement, so
  [`tools/jc_root_tripwire.py`](tools/jc_root_tripwire.py) polls arXiv for
  retraction/confirmation signals, and
  [`atlas/jc-crater/root_claim.json`](atlas/jc-crater/root_claim.json) records the
  archival policy: **no DOI until the root confirms**. Our object certificate is
  unaffected by any retraction; the derived corollaries are not.

The engine is reusable: [`tools/crater.py`](tools/crater.py) generalizes it into a
polarity-aware crater tool, so the next falsification anywhere gets the same
treatment.

## Independent verifications of other people's results

Claims arrive faster than anyone can check them. A replay a stranger can run in
one command is the cheapest useful thing this repository can offer their author —
so where a result is finite and checkable, we check it and publish the checker.

**These are not our results.** Each lane states its author in the first lines, and
our contribution is the replay and nothing else. All are self-published and
unrefereed; each carries its own caveats at the claim, not in a footnote.

| result | author | what our replay establishes |
|---|---|---|
| [`jacobian-conjecture`](certificates/jacobian-conjecture) — JC is false at `n = 3` | Alpöge (2026) | the counterexample is exact: `det ≡ −2`, dual-path collision, in exact rational arithmetic |
| [`graffiti-284-refutation`](certificates/graffiti-284-refutation) — Graffiti 284 is false | Nathan Wilbanks and Annie, AGNT Labs | Hoffman–Singleton built from the Robertson construction, `λ_min(D) = −4` by integer algebra with **no eigensolver**, and minimum dual degree **computed** — the authors' own script types both numbers in as literals |
| [`graffiti-290`](certificates/graffiti-290) — Graffiti 290 holds | Nathan Wilbanks and Annie, AGNT Labs | exhaustive over all 1360 girth-≥5 graphs of order ≤ 10, exact throughout — **under the Written-on-the-Wall gravity convention**, which is not the only one in the literature (see below) |
| [`keller-power-weighted-lifts`](certificates/keller-power-weighted-lifts) — a 2-parameter family of non-injective Keller maps | Annie, AGNT Labs Technical Report III | all 27 published members rebuilt from the paper's prose: genuinely polynomial, `det ≡ −k/(k+1)` as a coefficient identity, and the fibre degree **counted** rather than restated |

Two things a reader should know before citing any of this:

**Graffiti 290's truth depends on a definition.** Under the "gravity" definition in
Aouchiche–Hansen's 2010 survey the statement is refuted instantly; under the
Written-on-the-Wall / Brewster et al. definition — the one the theorem is stated
over, and the one our verifier implements — it survives. That is not us choosing a
favourable reading: the authors who found the refutation are the ones who call the
survey definition a misstatement and the Written-on-the-Wall definition "the
correct definition" (Roucairol & Cazenave, [arXiv:2409.18626](https://arxiv.org/abs/2409.18626)
§5.2). Both halves belong at the claim.

**A verifier cannot check its own source.** Every lane here defends against
corrupted *data* — poison the witness or the receipt and the replay fails. None can
defend against an edit to itself: stub a gate, hardcode a verdict, and the file
will print PASS. That gap is closed by the `sha256` pinned in
[`certificates/contracts.json`](certificates/contracts.json), plus git history and
review — and each lane says so in its own words rather than leaving a reader to
assume otherwise.

## Machine-checked formal proofs

The strongest evidence tier the atlas carries: a theorem whose truth reduces to a
proof assistant's kernel and its named axioms. Two live in-repo, **sorry-free in
Lean 4 + mathlib**, each with a `proof.json` manifest that
[State of the Frontier](views/state_of_frontier.md) discovers mechanically:

| theorem | kind | where |
|---|---|---|
| `jacobian_conjecture_false` — the Jacobian Conjecture is false at `n = 3` over ℚ | refutation | [`certificates/jacobian-conjecture/lean/`](certificates/jacobian-conjecture/lean) |
| `ringel_not_stretchable` — Ringel's 9-element oriented matroid is not stretchable | theorem | [`certificates/ringel-nonstretchability/lean/`](certificates/ringel-nonstretchability/lean) |

These prove **theorems and refutations, not bracketed quantities**, so they sit
beside the gap map rather than inside its C0 count. The one gap-map-style
quantity that *has* reached **C0** is the crater's minimal-counterexample
dimension (upper bound only, scoped by the validator — see below).

## Formal spine pins (external)

The atlas also records external Lean work in [`atlas/lean_lane.json`](atlas/lean_lane.json)
without changing the canonical status of an Erdős problem. The registry pins a
complete finite classification for **#593** and a deliberately partial checkpoint
for **#625**, with exact entrypoints, toolchains, replay commands, attribution,
and trust boundaries. In particular, the #593 record credits Eric Li's
contemporaneous broader preprint as related work rather than treating it as a
premise of the pinned formalization; the #625 record explicitly does not claim
`Erdos625Statement`.

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

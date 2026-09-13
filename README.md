# The Erdős Frontier Atlas

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21443635.svg)](https://doi.org/10.5281/zenodo.21443635)

**A method substrate and strike map for mathematical research.**

The Atlas connects Erdős problems to reusable lemmas, explicit remaining
obligations, source records, and evidence another researcher can check. A useful
result can be a proof transfer, a conditional reduction, or a failed route that
saves the next person from repeating it. Larger computational cutoffs are useful
only when they answer a worthwhile mathematical question.

The production attack graph and published certificates are preserved separately
from active research. Adding a method does not change a problem's status, prove a
conjecture, or turn a shared tag into an implication. The
[campaign goal](experiments/astra-i3-20260911/GOAL.md) explains this direction;
[frontier cartography](FRONTIER_CARTOGRAPHY.md) is the broader charter.

## Start here

| To… | Read or run |
|---|---|
| Find a reusable method | [Method substrate](experiments/astra-substrate-20260911/README.md) · [generated method board](experiments/astra-substrate-20260911/BOARD.md) |
| Read the RH / squarefree-counting work | [P969 progress map](experiments/astra-rh-969-20260912/REPOSITORY_STATUS.md), including derivations, audit evidence, verification and remaining obligations |
| Choose a research direction | [Agent entry point](GRAPH.md) · [strike board](views/sorties.md) · [walls](atlas/walls.md), then check [source freshness](#source-freshness) |
| Inspect the dataset | [State of the Frontier](views/state_of_frontier.md) · [source ledgers](#repository-inventory) |
| Replay the work | [Quickstart and verification](#quickstart-and-verification) |
| Contribute without clobbering another lane | [Coordination](COORDINATION.md) · [contribution rules](#contributing--humans-and-agents) |
| Read the longer account | [*Cartography of Numbers*](book/BOOK.md) |

## Current research

These are research results and interfaces, not a list of solved conjectures.
The [method registry](atlas/substrate.json) records each statement's hypotheses,
artifacts, evidence level, and unresolved step.

| Lane | What is available | What remains open |
|---|---|---|
| **RH / P969** | [Squarefree-energy equivalence and generic obstruction](experiments/astra-rh-969-20260912/README.md); CRT/centered-defect and Mellin transfers; the [GM/GMRR assembled variance deduction](experiments/astra-rh-crt-20260912/GM_TRANSFER.md) through `4/7-epsilon`; [sharp Type I and signed-diagonal interfaces](experiments/astra-rh-crt-20260912/ARITHMETIC_FRONTIER.md) | The RH-equivalent energy estimate and full signed mixed-moment saving are unproved. The variance deduction uses pinned external theorems and model audits; it is not a novelty, record, human-review, or formal-proof claim. |
| **P327** | [Multiplier-sensitive smooth-fiber transfer](experiments/astra-327-fiber-20260912/README.md): retain multiplier divisibility information and prove an all-N deficit inequality, with a small independently checked demonstration | No solution or new best bound. The demonstration's bounds are weaker than the cited literature. Published for review in [PR #155](https://github.com/techno-optimist/erdos-frontier-atlas/pull/155). |
| **P699** | [Formal binomial-gcd seeds](experiments/astra-lean-seed-20260904/README.md), [the i=2 case](experiments/astra-i2-complete-20260911/README.md), and [i=3 reductions and residuals](experiments/astra-i3-20260911/GOAL.md) | Each formal or conditional lemma has its own scope. The remaining i=3 obligations and higher-i cases are not closed by these artifacts. |
| **P993 and CRT bridges** | [Tail compression, Laurent blocks and endpoint-safe transfers](experiments/astra-briefcase-20260904/README.md) | Block properties and candidate matches are not proofs of tree unimodality or an entire gap spectrum. |
| **P376** | [Kummer/digit checks and bounded historical replay](experiments/astra-376-20260911/README.md) | The infinitude question needs a method, not another extension of a known sequence's cutoff. The [working goal](experiments/astra-i3-20260911/GOAL.md) records that correction. |

The RH update is published for review in
[PR #156](https://github.com/techno-optimist/erdos-frontier-atlas/pull/156), stacked
on the P327 method PR. It does not solve P969 or RH. Its
[portable audit archive](experiments/astra-rh-crt-20260912/audits/README.md)
separates exact arithmetic from numerical diagnostics, model review from human
review, and replayed checkers from those needing excluded source files. The
[progress map](experiments/astra-rh-969-20260912/REPOSITORY_STATUS.md) carries the
integration record rather than a permanently hardcoded test total here.

To use the substrate from the repository root:

```sh
python3 tools/query_substrate.py methods
python3 tools/query_substrate.py for 969
python3 tools/query_substrate.py for 327
python3 tools/query_substrate.py for 699
python3 tools/query_substrate.py open
```

A `CANDIDATE` match is a search lead. A `discharges` entry applies only to the
stated lemma or obligation; it does not mean the parent conjecture is solved.
The substrate is an additive overlay, not a replacement for the production graph.

## Repository inventory

Counts below describe this checkout, not the current size of the upstream
website. `tests/test_readme.py` checks them against the source ledgers.

| Inventory | Count | Source of truth |
|---|---:|---|
| Hub records | 1,217 | [`atlas/stubs.json`](atlas/stubs.json), including its upstream commit pins |
| Deep-tier records | 51 | [`atlas/problems.json`](atlas/problems.json), with per-record provenance and scope |
| Bracketed quantities | 225 | [`atlas/gap_map.json`](atlas/gap_map.json); evidence determines the validator's C0–C3 class |
| Registered methods | 29 | [`atlas/substrate.json`](atlas/substrate.json); formal, informal, conditional and candidate scopes remain distinct |

The hub supplies problem identifiers and metadata. Deep records and bracketed
quantities describe selected evidence and computational questions. The method
registry adds transferable arguments and their remaining obligations. None of
these inventories is a count of conjectures solved by this project.

### The map — where everything lives

| Area | Files |
|---|---|
| Research methods | [`atlas/substrate.json`](atlas/substrate.json) · [`experiments/`](experiments) · [method board](experiments/astra-substrate-20260911/BOARD.md) |
| Production attack graph | [`GRAPH.md`](GRAPH.md) · [`atlas/graph/`](atlas/graph) · [`views/graph/`](views/graph) · [`views/sorties.md`](views/sorties.md) |
| Certificates and claim contracts | [`certificates/README.md`](certificates/README.md) · [`certificates/contracts.json`](certificates/contracts.json) |
| Feasibility and source overlays | [`atlas/walls.md`](atlas/walls.md) · [`atlas/lanes.md`](atlas/lanes.md) · [`atlas/ai_claims.json`](atlas/ai_claims.json) · [`atlas/lean_lane.json`](atlas/lean_lane.json) |
| Generated views and book | [`views/`](views) · [operations annex](views/operations.md) · [`book/`](book) |
| Validators and tests | [`tools/`](tools) · [`tests/`](tests) · [`Makefile`](Makefile) · [CI workflow](.github/workflows/verify.yml) |
| Project policy and releases | [`COORDINATION.md`](COORDINATION.md) · [`FRONTIER_CARTOGRAPHY.md`](FRONTIER_CARTOGRAPHY.md) · [`RELEASING.md`](RELEASING.md) · [`NOTICE`](NOTICE) |

## Source freshness

**The generated graph is a pinned snapshot, not a live upstream feed.** A passing
staleness gate means generated files agree with their source data; it does not
mean every source has been checked against today's literature. Some production
statuses are superseded by the dated research overlays, intentionally without
silently rebuilding the graph.

- The [September 11 Erdős update](experiments/astra-freshness-20260911/README.md)
  records the checked changes for #477, #625 and #501, distinguishes mathematical
  status changes from Lean-label changes, and preserves differences between the
  website and YAML snapshots.
- The [RH source review](experiments/astra-rh-969-20260912/FRESHNESS.md) and
  [P327 review](experiments/astra-327-fiber-20260912/FRESHNESS.md) are dated
  September 12, 2026. They are source snapshots, not continuing monitors.
- The [AI-claim overlay](atlas/ai_claims.json) is a dated claims registry.
  Recording an AI-assisted proof claim never changes a canonical status.
- Before starting a new attack, check the official problem page, discussion,
  separate proof-claim register, and cited manuscript versions. Consult
  [erdosproblems.com](https://www.erdosproblems.com) for the human-maintained
  index; do not infer current status from an old attack card or prize label.

The repository is a computational and research annex to that index, not a copy
of its prose. Machine metadata sources and licenses are recorded in
[`NOTICE`](NOTICE) and the source ledgers.

## Quickstart and verification

From the repository root, these bounded method replays use Python's standard
library:

```sh
python3 -I -B experiments/astra-substrate-20260911/verify.py
python3 -I -B experiments/astra-327-fiber-20260912/verify.py --negative-controls
python3 -I -B experiments/astra-rh-969-20260912/verify.py
python3 -I -B experiments/astra-rh-crt-20260912/verify.py experiments/astra-rh-crt-20260912/receipt.json
```

For the full fast repository gate with the pinned dependencies:

```sh
uv run --python 3.11 --with-requirements requirements-dev.lock make audit-fast
```

Without `uv`, use a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.lock
make audit-fast
```

`audit-fast` runs the atlas, gap-map and claim validators, checks generated views,
book and graph, verifies claim contracts, runs their fast replay profile, and
executes the repository tests. It does not recompile every Lean project, rerun
large historical searches, or recheck every cited analytic theorem.

The [CI workflow](.github/workflows/verify.yml) uses Python 3.12 for the fast gate.
Its slower receipt-drift job runs on the schedule or manual dispatch, not on
every PR. Run `make check-receipts` before merging certificate changes, following
the frozen-certificate policy; read its coverage report rather than interpreting
a pass as certification of every stored receipt. Slow claim replays have separate
resource requirements documented in the [Makefile](Makefile).

The [RH audit archive](experiments/astra-rh-crt-20260912/audits/README.md) has its
own scratch-only replay command and explicit source-dependent exclusions.
Default method verifiers read and recompute evidence without replacing it.
Emission commands are separate and require a new output path.

## Honest scope

- A finite exact check proves only the stated finite claim. An asymptotic theorem
  needs an argument covering its unbounded parameters.
- A formal theorem is checked relative to its declared dependencies and axioms.
  A passing Python gate does not establish a Lean rebuild or a human review.
- Model audits, human peer review, formal kernel checks and official acceptance
  are different kinds of evidence. None silently substitutes for another.
- A generic-coefficient countermodel is not a Möbius counterexample. An unsigned
  collision count is not a lower bound for a signed moment.
- A shared tag, OEIS sequence or graph neighbor suggests a question; only a proved
  or sourced implication supports a mathematical transfer.
- A finite-counterexample handle is not a promise of a reachable search or a
  claimable prize. Walls apply to stated branches, not automatically every
  mathematical approach to a problem.
- Corrections remain visible. New work does not silently upgrade historical
  record, priority, publication, or solution claims.

## CHRONOS Frontier Board

**Historical July 2026 record.** The table below preserves the recorded claims,
qualifications and retractions. It is not a fresh literature or priority audit.
Its rows also feed the generated book and State of the Frontier, so this README
refresh preserves their contents rather than silently changing published data.
For current research direction, use the [method index](#current-research).

Tier: 🟢 recorded as proven/certified · 🟡 grounded or partial · ⚪ open/in progress
· 🔴 corrected or retracted. Read the linked claim contract and artifact scope.

<details>
<summary>Recorded certificate movements and corrections</summary>

| tier | problem | what CHRONOS contributed | certificate | when |
|---|---|---|---|---|
| 🟢 | **#699** binomial-gcd rows | **property holds for every `n` in `[10⁷, 10⁸)`** — all 90,000,000 rows, every `(i,j)` pair decided exactly, zero counterexamples, 119.53 core-hours. First exhaustive **general-row** sweep past `10⁷` (structured families were already covered to ≈`1.34×10⁸`). Rests on a theorem that large primes never suffice on a pruned row — `p=2` can be the only usable one | [`certificates/erdos-699`](certificates/erdos-699) · PR #129 | 2026-07-27 |
| 🟢 | **#366** 2-full/3-full neighbours | **no 2-full `n` with `n+1` 3-full for `n ≤ 10²⁵`** — 1,620,172,043 cubefull candidates, both orientations, 6.27 core-hours. A 1000× extension of `10²²`, which was a **single unreplayed 2011 OEIS b-file**; this re-derives that region independently. The lever: enumerate the **cubefull** side (`~X^(1/3)`), not the powerful-**pair** side (`~X^(1/2)`) that set the old bound | [`certificates/erdos-366`](certificates/erdos-366) · PR #125 | 2026-07-26 |
| 🟢 | **#743** Gyárfás tree packing | **every one of the 45,376,056 tuples `(T₂,…,T₁₀)` decomposes `K₁₀`** — exhaustive, uncapped, 44 core-seconds. Frontier had stood at `n ≤ 9` since **Fishburn 1983** (43 years); `n=9` reproduced as positive control. Hardest tuples are exactly those with `T₄..T₇` all stars — where Gyárfás–Lehel's coverage stops | [`certificates/erdos-743`](certificates/erdos-743) · PR #126 | 2026-07-27 |
| 🟢 | **#993** tree independence unimodality | **all 23,522,619,475 trees on `n ≤ 30` unimodal**, zero violations, 10.33 core-hours. Includes the **first independent replication** of the `n ≤ 29` frontier (Reynolds, Zenodo v3, 8,691,747,673 trees — single-author, unreplayed until now), reaching his exact total. `n=30` alone is 1.71× that entire prior workload | [`certificates/erdos-993`](certificates/erdos-993) · PR #126 | 2026-07-27 |
| 🟢 | **#552** `R(C4,K1,n)` | certified C₄-free witnesses ⇒ `R(C4,K1,n) = n + ⌈√n⌉ + 1` for `12 ≤ n ≤ 16`; `n=17` closed at `22` (Parsons 1975) | [`certificates/erdos-552`](certificates/erdos-552) · PR #78 | 2026-07-16 |
| 🟢 | **#241** B₃-subset table (A387704) | proved `A387704(n) = max{k : A227358(k) ≤ n−1}` (translation invariance; 0/151 mismatches) ⇒ first jump to 9 at `n=209`; atlas cell **closed by cross-reference** | PR #80 | 2026-07-16 |
| 🟢 | **#13** Erdős–Sárközy | certified exact table `f(1..45)`; `N=17` is the **last** exception to `⌊N/3⌋+1` — an empirical location for Bedert's ineffective threshold | [`certificates/erdos-13`](certificates/erdos-13) · PR #81 | 2026-07-17 |
| 🟢 | **#979** `f₃` / A385316 | **`a(6) > 10¹²` at C2** — exhaustively verified and replayable from this repo (`verify.py --cutoff 1e12`, ~80 s, ~11 GB; reproduces `a(1..5)` as a fail-closed self-check) — past the published `4.99·10¹¹`. A stronger `> 10¹³` sweep exists but its code and ledgers are **not tracked here**, so it is **quarantined from public promotion** pending a self-contained replay packet — see the entry note in the gap map. *(Corrected 2026-07-25: this row previously claimed `> 10¹³` at C1; the second "independent implementation" backing that class lives outside this repository, so a reader could not replay it.)* | [`certificates/erdos-979`](certificates/erdos-979) | 2026-07-19 |
| 🟡 | **#1107** Mollin–Walsh / A056828 | verified **no seventh exception below `10⁶`** to being a sum of ≤3 powerful numbers (`verify.py`, default `N = 10⁶`, ~10 s, dependency-free); the six known exceptions `{7,15,23,87,111,119}` are all `< 120` and are reproduced, powerful-counts cross-checked vs A118896. A wider `10¹⁰` run exists but is **not replayable from this repository**, so it is not the public claim. *(Corrected 2026-07-25: this row previously claimed `10¹⁰`.)* | [`certificates/erdos-1107`](certificates/erdos-1107) | 2026-07-18 |
| 🟡 | **#142** `r₃(N)` | complete 12,349-cell geometric enumeration superseding a flawed 976-cell subset, now certified in-repo as a **construction no-go** — a **foundation only**; self-declared no-bridge, **not** an `r₃(N)` bound | [`certificates/erdos-142`](certificates/erdos-142) · PR #84 | 2026-07-13 |
| 🔴 | **#142** / D15 lemmas | **refuted** `ker π ∩ D = 0` and `q ≥ dim ker π` (two lemmas a bridge attempt rested on) and proved Theorem A in their place — a dead path closed so the next agent does not re-walk it; explicitly **not** an `r₃(N)` bound | [`certificates/erdos-142-kerpi-refutation`](certificates/erdos-142-kerpi-refutation) · PR #101, #102 | 2026-07-24 |
| 🟢 | **#1029 / #77** `R(5,5)` | 42/42 DRAT-certified structural negatives (no witness; rigidity + prime-order orbit collapse), all consistent with `R(5,5) = 43` | [r55-rigidity-certificates](https://github.com/techno-optimist/r55-rigidity-certificates) · DOI [10.5281/zenodo.21305022](https://doi.org/10.5281/zenodo.21305022) | 2026-07-10 |
| 🔴 | **#552** `R(C4,K1,39)` | the `=46` **new-value** claim was **retracted** — DS1 rev.18 lists `46 ≤ f(39) ≤ 47`, OPEN; the 45-vertex witness stands as a re-derivation of Wu–Sun–Radziszowski 2015 | [`certificates/erdos-552-f39`](certificates/erdos-552-f39) | 2026-07-17 |

</details>

The historical board records Erdős cells; it is not the inventory of current
research methods. The full certificate catalogue and caveats are in
[`certificates/README.md`](certificates/README.md). Changes to a recorded claim
need the corresponding evidence and publication-contract update, not just a
README edit.

## The 2026 Jacobian Conjecture crater

The repository preserves its independent verification of Alpöge's 2026 counterexample
in [`certificates/jacobian-conjecture/`](certificates/jacobian-conjecture), with
credit to the external construction. The associated
[crater model](atlas/jc-crater/README.md) separates the exact object check from
propagated mathematical consequences. Its
[root-claim record](atlas/jc-crater/root_claim.json) retains the announcement's
conditional status and source history.

This README refresh does not establish a new peer-review, acceptance or
retraction status for that announcement. Read the dated root record and its
sources before citing the propagation. The reusable
[`crater` machinery](tools/crater.py) and quarantined claims remain available.

## Independent verifications of other people's results

The [Graffiti 284](certificates/graffiti-284-refutation),
[Graffiti 290](certificates/graffiti-290), and
[Keller-map family](certificates/keller-power-weighted-lifts) lanes credit their
external authors and state what the local replay checks. The constructions and
original results are not ours. In particular, the Graffiti 290 claim depends on
the stated gravity convention; its README retains that distinction.

A checksum identifies code bytes; it does not prove that the checker is correct.
Claim contracts, independent semantic replays and negative controls address
separate parts of that trust boundary. Consult each lane's documented coverage.

## Machine-checked formal proofs

Formal artifacts include the [Jacobian](certificates/jacobian-conjecture/lean)
and [Ringel nonstretchability](certificates/ringel-nonstretchability/lean)
projects, plus the newer [binomial-gcd seeds](experiments/astra-lean-seed-20260904/README.md)
and [P699 i=2 work](experiments/astra-i2-complete-20260911/README.md).
Their exact statements, toolchains, dependency pins and axiom checks belong to
the individual bundles. This README update does not claim a fresh build of all
of them or extend a helper theorem to its parent conjecture.

### Formal spine pins (external)

[`atlas/lean_lane.json`](atlas/lean_lane.json) preserves external formalization
checkpoints, including #593 and a deliberately partial #625 checkpoint. A pinned
formalization's scope is distinct from later progress on the underlying problem;
consult the [source update](experiments/astra-freshness-20260911/README.md) rather
than interpreting that older checkpoint as today's full mathematical status.

## Contributing — humans and agents

1. Read [`GRAPH.md`](GRAPH.md), the relevant attack card, and the latest applicable
   source overlay. Read walls before committing compute.
2. Register a bounded lane in [`COORDINATION.md`](COORDINATION.md). Work on a
   separate branch; reach `main` by reviewed PR. Do not force-push another lane.
3. State the exact problem/surface, hypotheses, claim and remaining obligation.
   Prefer an operator another problem can reuse over an unexplained larger run.
4. Preserve proof objects and evidence in git. Supply a replay command, an
   independent oracle where appropriate, and poisoned inputs that fail the same
   acceptance gate. Keep third-party manuscripts outside the patch; cite their
   versions and hashes instead.
5. Add methods to the substrate with honest evidence labels and selector scope.
   Never promote a candidate match to an implication or silently set a status.
6. Keep merged certificates and the production graph frozen unless an explicit
   versioned change is authorized. Do not regenerate evidence in place.
7. Update this README's current-research links and inventory when relevant;
   `tests/test_readme.py` checks counts and entry points. Run the pinned gate,
   reconcile independent review, and verify the pushed branch and CI.

Human corrections, counterexamples and narrower statements are welcome. Open an
issue with the exact claim, source or failing replay; preserve the correction
where the next researcher will find it.

## Provenance and the certificate template

The dataset release **EFA-DR1** is citable at
[10.5281/zenodo.21443635](https://doi.org/10.5281/zenodo.21443635).
See [`CITATION.cff`](CITATION.cff), [`RELEASING.md`](RELEASING.md),
[`LICENSE`](LICENSE) and [`NOTICE`](NOTICE). Cite the exact commit as well for
research added after that release; a later branch is not silently a new DOI
snapshot.

The original deep-audit source and dates remain in
[`atlas/problems.json`](atlas/problems.json). Related verifier-first work includes
[r55-rigidity-certificates](https://github.com/techno-optimist/r55-rigidity-certificates)
and [antipodal-kissing-bounds](https://github.com/techno-optimist/antipodal-kissing-bounds).
Problem history and official status belong to
[erdosproblems.com](https://www.erdosproblems.com), not to this repository's
research labels.

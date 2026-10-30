# The Erdős Frontier Atlas

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21443635.svg)](https://doi.org/10.5281/zenodo.21443635)

**An open, checkable map of AI-assisted discovery in mathematics.**

The atlas started with Paul Erdős's problems, and it is named in honor of them.
It now follows AI-assisted results across all of mathematics. It shows which
tools exist, what people report those tools found, what has actually been
checked, and what is still open. Erdős problems remain its home ground and its
most detailed layer.

**North star:** an honest map of where mathematical understanding is growing,
so that working mathematicians can trust it and use it to decide what to work
on next.

Two rules shape everything here:

1. **Receipts before claims.** Each result of our own carries two independent
   checks, a control that must fail, and a certificate anyone can rerun. Each
   one also comes with a plain explanation of what it means and what it doesn't.
2. **A claim is not a status.** When someone reports an AI-assisted result, we
   list it with its primary source, and its status stays as it was. Status
   changes when the human-maintained upstream index changes, or when this
   repository holds evidence you can replay. Extraordinary claims stay labeled
   `unvetted` until they are vetted.

## Start here

| To… | Read or run |
|---|---|
| See what AI-assisted tools and results exist | [Tool index](atlas/tools.json) · [AI-assisted results](atlas/ai_results.json) · [claim feeds](#ai-assisted-discovery-across-mathematics) |
| See what we checked ourselves | [Our own results](#our-own-results) · [certificates](certificates/README.md) · [claim contracts](certificates/contracts.json) |
| Check a receipt yourself | [How to verify a receipt](#how-to-verify-a-receipt) |
| Choose something to work on | [Agent entry point](GRAPH.md) · [strike board](views/sorties.md) · [walls](atlas/walls.md) · [residual ledger](atlas/residuals.json), then check [source freshness](#source-freshness) |
| Reuse a method | [Method substrate](experiments/astra-substrate-20260911/README.md) · [generated method board](experiments/astra-substrate-20260911/BOARD.md) |
| Inspect the whole dataset | [State of the Frontier](views/state_of_frontier.md) · [what the atlas holds](#what-the-atlas-holds) |
| Contribute | [Coordination](COORDINATION.md) · [contribution rules](#contributing--humans-and-agents) |
| Read the longer account | [*Cartography of Numbers*](book/BOOK.md) · [frontier cartography charter](FRONTIER_CARTOGRAPHY.md) |

## What the atlas holds

These counts describe this checkout. `tests/test_readme.py` checks every number
in this table against its source file, so the table can't drift from the data.

| Inventory | Count | Source of truth |
|---|---:|---|
| AI-assisted discovery tools | 30 | [`atlas/tools.json`](atlas/tools.json): 13 systems, 8 benchmarks, 6 datasets and 3 registries, each with primary links and a first-public date |
| AI-assisted results | 21 | [`atlas/ai_results.json`](atlas/ai_results.json): prior value, new value and source, as the authors report them. 5 are extraordinary claims marked `unvetted`, and 2 don't state AI involvement |
| Erdős-linked AI claims | 89 | [`atlas/ai_claims.json`](atlas/ai_claims.json): a dated claim registry used for triage; it never sets a status |
| OpenAI manuscript families | 22 | [`atlas/openai_math.json`](atlas/openai_math.json): pinned to a commit of [openai/math](https://github.com/openai/math) |
| Plasma overlay entries | 155 | [`atlas/plasma_claims.json`](atlas/plasma_claims.json): where Plasma AI's [erdosproblems.ai](https://erdosproblems.ai) wiki differs from this atlas, with our review of each difference |
| Claim contracts | 39 | [`certificates/contracts.json`](certificates/contracts.json): each statement of ours tied to exact artifact bytes, a replay command and a failure boundary |
| Hub entries | 1,221 | [`atlas/stubs.json`](atlas/stubs.json): every Erdős problem, with its upstream commit pins |
| Deep-tier audits | 51 | [`atlas/problems.json`](atlas/problems.json), with per-entry provenance and scope |
| Bracketed quantities | 225 | [`atlas/gap_map.json`](atlas/gap_map.json); the evidence sets each one's C0–C3 confidence class |
| Registered methods | 31 | [`atlas/substrate.json`](atlas/substrate.json); formal, informal, conditional and candidate scopes stay distinct |
| Residual families | 11 | [`atlas/residuals.json`](atlas/residuals.json); each names its reduction, its searched bound and a replay command |

None of these counts is a count of problems settled by this project. Most of
the results indexed here belong to other people. We list them so they can be
found, and we credit them.

## How to read it

Every entry says what kind of evidence stands behind it. These are different
things, and none of them stands in for another:

- **Our certified finite results.** An exact computation, checked by two
  independently written programs, with a negative control and a pinned,
  rerunnable certificate. It settles only the finite statement it names, such
  as one sequence term. It never settles the asymptotic question behind it.
- **Formal checks.** A Lean proof is checked against its stated dependencies
  and axioms. When we rebuild someone else's Lean proof, that checks their
  proof; it doesn't make the result ours.
- **Reported results.** Values copied from a primary source, with the authors
  credited. We haven't checked them unless the entry says we have.
- **Unvetted claims.** Extraordinary claims, listed only because a primary
  source exists. They are marked `vetting: unvetted`, and they never move a
  status.
- **Confidence classes** in the gap map: C0 formal proof, C1 two or more
  independent implementations or replays, C2 exactly one, C3 literature or
  numerics only. The validator computes the class from the recorded evidence
  and fails any class the evidence doesn't support.

Corrections stay visible. When we get something wrong, we fix the map first
and leave a dated note saying what changed.

## How to verify a receipt

Each claim in [`certificates/contracts.json`](certificates/contracts.json) names
its artifacts by sha256, the command that replays it, the output that replay
must print, and how it is meant to fail. To replay one claim, then all the fast
ones:

```sh
python3 -I certificates/erdos-552/verify.py
python3 tools/check_certificate_contracts.py --profile fast
```

For a ten-minute tour that needs only `git`, `cc` and `python3` (a DRAT proof
replay with its negative control, one witness check, and one gap-map entry with
its confidence class):

```sh
bash scripts/hello_frontier.sh
```

Each certificate directory has its own README with the claim, the two engines,
the control, and the exact command. The [full quickstart](#quickstart-and-verification)
runs the same gate CI does.

## Our own results

We aim at narrow, well-defined gaps where the answer can be checked: the next
term of a sequence linked to an Erdős problem, or a reduction that leaves an
explicit residual. Each row below says what is available and what stays open.
The [method registry](atlas/substrate.json) lists each statement's
hypotheses, artifacts, evidence level and unresolved step.

### Sequence terms and exact tables

These are finite computations with receipts, not answers to the underlying
problems.

| Lane | What is available | What remains open |
|---|---|---|
| **P357** | [Distinct segment sums](certificates/erdos-357/README.md): A364132(n), the least N such that {1..N} holds an increasing n-term sequence whose segment sums are all distinct, and its any-order companion A364153, decided by exhaustive search through n = 28 and n = 18; A364132(23..28) = 56, 60, 63, 67, 69, 75 and A364153(14..18) = 20, 22, 24, 26, 28 are new (OEIS stopped at 22 and 13 terms; A364132(28) = 75, A364153(17) = 26 and A364153(18) = 28 by exhaustive computer searches by two independent engines, not proofs), and every published term is reproduced | A364132(29) ≥ 76 is the next cell (A364153(19) ≥ 29 the companion); whether Erdős's f(N) is o(N) is untouched by any finite table. |
| **P1109** | [Sets with squarefree sumsets](certificates/erdos-1109/README.md): the indices A392165 where f(N) = A392164(N) reaches each new value, recomputed by exhaustive clique search over every N ≤ 2000; A392165(40..54) = 1255, 1277, …, 1991, 1999 were not in OEIS when computed (it stopped at 1103 then; OEIS now lists them, matching, plus a(55..65) to N = 3000 from Leandre Jack's b-file, which a second, separately written search of ours confirms term for term), all 39 earlier published terms are reproduced, and an independent Russian-doll search confirms the first three of 40..54; that second search then gives A392165(66) = 3065, new (the OEIS b-file ends at a(65) = 2993), with each of its 29 new answers repeated by the original engine | A392165(67) > 3065 is the next cell; the growth of f(N) (is it N^{o(1)}?) is untouched by any finite table. |
| **P131** | [Nondividing sets](certificates/erdos-131/README.md): the thresholds T_k of A068063 (least n with a nondividing k-subset of {1..n}) by exhaustive search through k = 10: T_9 = 107 and T_10 = 155 are new (OEIS stopped at a(100) = 8), so A068063(n) = 9 on 107..154 and 10 at 155 | T_11 > 155 is the next cell; the growth exponent of the maximum nondividing set is untouched by any finite table. |
| **P962** | [Long runs of integers with a large prime factor](certificates/erdos-962/README.md): OEIS A327909 recomputed from scratch through n = 1102 by one exact scan of every integer up to 4.2 × 10¹⁰, then extended to n = 1200 by a scan up to 7.5 × 10¹⁰, to n = 1300 by a scan up to 10¹¹, to n = 1400 by a scan up to 4 × 10¹¹, and to n = 1500 by a scan up to 3.2 × 10¹¹; a(1000..1500) are new (the b-file ended at a(999), which the scan matches), and they give Erdős's k(n) exactly for n < 3.1 × 10¹¹ | a(1501) is the next cell; the growth question for log k(n) is untouched by any finite table. |
| **P864** | [Sets with one repeated sum](certificates/erdos-864/README.md): A389182(N), the largest A ⊆ {1..N} in which at most one pairwise sum repeats, decided for every N ≤ 117 by one exhaustive search per N; a(101..106) = 16, a(107..116) = 17 and a(117) = 18 are new to OEIS (the b-file ended at a(100) = 16) and confirm an unverified external report, and a(1..80) as published are reproduced | a(118) ∈ {18, 19} is the next cell; the constant in a(N) ~ c√N is untouched by any finite table. |
| **P854** | [Gaps between integers coprime to a primorial](certificates/erdos-854/README.md): OEIS A389839 recomputed exhaustively through n = 16, a(13..16) = 76, 86, 98, 108 (every smaller gap with a gcd-checked witness) — new to A389839 but already implied by the 2020 gap table A331118, which also showed the atlas cell a(13) had been mis-set | a(45) ∈ [618, 644] is the first cell beyond public data. The asymptotic Erdős questions are untouched. |
| **P1016** | [Minimal pancyclic graphs](certificates/erdos-1016/README.md): h(n) = m(n) − n exactly for n ≤ 186; no Cₙ + 6 chords is pancyclic for n ≥ 68 and no Cₙ + 7 chords for n ≥ 115, so t₆ = 67 and t₇ = 114 — settling the six-chord levels an external 2026 campaign left open, the complete seven-chord census, and replicating everything below 68 | h(187) ∈ {8, 9} is the next cell. The asymptotic question (does h(n) − log₂ n → ∞?) is untouched by any finite table. |

### Method research

These are research results and interfaces: reductions, transfers and failed
routes that save the next person from repeating them.

| Lane | What is available | What remains open |
|---|---|---|
| **RH / P969** | [Squarefree-energy equivalence and generic obstruction](experiments/astra-rh-969-20260912/README.md); CRT/centered-defect and Mellin transfers; the [GM/GMRR assembled variance deduction](experiments/astra-rh-crt-20260912/GM_TRANSFER.md) through `4/7-epsilon`; [sharp Type I and signed-diagonal interfaces](experiments/astra-rh-crt-20260912/ARITHMETIC_FRONTIER.md) | The RH-equivalent energy estimate and full signed mixed-moment saving are unproved. The variance deduction uses pinned external theorems and model audits; it is not a novelty, best-bound, human-review or formal-proof claim. |
| **P327** | [Multiplier-sensitive smooth-fiber transfer](experiments/astra-327-fiber-20260912/README.md): retain multiplier divisibility information and prove an all-N deficit inequality, with a small independently checked demonstration | No solution or new best bound. The demonstration's bounds are weaker than the cited literature. Published for review in [PR #155](https://github.com/techno-optimist/erdos-frontier-atlas/pull/155) and merged through [PR #157](https://github.com/techno-optimist/erdos-frontier-atlas/pull/157). |
| **P699** | [Formal binomial-gcd seeds](experiments/astra-lean-seed-20260904/README.md), [the i=2 case](experiments/astra-i2-complete-20260911/README.md), [i=3 reductions and residuals](experiments/astra-i3-20260911/GOAL.md), [positional localization for i=3](experiments/claude-699-i3-position-20260928/README.md) (no i=3 counterexample has n odd or n ≡ 2 (mod 4); the rest is a thin family, searched to 10¹⁸), and [positional localization for every i ≥ 3](experiments/claude-699-general-i-20260928/README.md): for each fixed i at most O(X^(1/3) log^π(i) X) values n ≤ X can fail, and an exact search finds no counterexample for i = 4, 5 to 10¹⁸, i = 6, 7 to 10¹⁷, i = 8, 9, 10 to 10¹⁵ and i = 11, 12, 13 to 10¹² | Each formal or conditional lemma has its own scope. What remains for i = 3..13 is each thin residual above its searched bound, listed in the [residual ledger](atlas/residuals.json) with its first unsearched members; i ≥ 14 and uniformity in i are open. |
| **P993 and CRT bridges** | [Tail compression, Laurent blocks and endpoint-safe transfers](experiments/astra-briefcase-20260904/README.md) | Block properties and candidate matches are not proofs of tree unimodality or an entire gap spectrum. |
| **P376** | [Kummer/digit checks and bounded historical replay](experiments/astra-376-20260911/README.md) | The infinitude question needs a method, not another extension of a known sequence's cutoff. The [working goal](experiments/astra-i3-20260911/GOAL.md) notes that correction. |

The RH lane was published for review in
[PR #156](https://github.com/techno-optimist/erdos-frontier-atlas/pull/156) and
reached `main` with the rest of that campaign through
[PR #157](https://github.com/techno-optimist/erdos-frontier-atlas/pull/157). It
does not settle P969 or RH. Its
[portable audit archive](experiments/astra-rh-crt-20260912/audits/README.md)
separates exact arithmetic from numerical diagnostics, model review from human
review, and replayed checkers from those needing excluded source files. The
[progress map](experiments/astra-rh-969-20260912/REPOSITORY_STATUS.md) carries the
integration notes. The [campaign goal](experiments/astra-i3-20260911/GOAL.md)
explains why the method lanes favor reusable arguments over larger cutoffs.

To use the method substrate from the repository root:

```sh
python3 tools/query_substrate.py methods
python3 tools/query_substrate.py for 969
python3 tools/query_substrate.py for 699
python3 tools/query_substrate.py open
```

A `CANDIDATE` match is a search lead. A `discharges` entry applies only to the
stated lemma or obligation, not to the parent conjecture.

## AI-assisted discovery across mathematics

This part of the atlas maps other people's work. Listing something here is not
an endorsement, and it never changes a status.

- The [tool index](atlas/tools.json) lists 30 AI-assisted discovery systems,
  registries, datasets and benchmarks, from AlphaEvolve, AlphaProof Nexus,
  Aristotle, AxiomProver and Gauss to FrontierMath: Open Problems, OEIS Open,
  First Proof and PutnamBench, plus community registries. Each one has primary
  links and a first-public date.
- The [results file](atlas/ai_results.json) lists 21 results whose authors
  report or claim AI assistance, including matrix multiplication, kissing
  numbers, cap sets, Ramsey and Schur lower bounds, and Erdős #30, #36, #188 and
  #519. Most lie outside the Erdős set. Five extraordinary claims are marked
  `vetting: unvetted`: two ETH refutations, local smoothing with Kakeya,
  Yang–Mills existence, and cycle double cover. They are listed only because a
  primary source exists. Both files are dated 2026-10-30 and checked by
  `tools/validate_tools.py`.
- The [AI-claim overlay](atlas/ai_claims.json) is a dated registry of 89
  Erdős-linked claims of AI-assisted resolutions. It exists so effort isn't
  duplicated, and it flags which claims are worth checking.
- The [OpenAI manuscript index](atlas/openai_math.json) lists 22 result families in [openai/math](https://github.com/openai/math) (Apache-2.0), pinned to a commit: 15 whose own contents entry mentions Erdős, plus 7 that the erdosproblems.com maintainer's [2026-10-08 index of OpenAI's claims](https://www.erdosproblems.com/forum/thread/blog:10) ties to Erdős problems. Together they link 25 Erdős problems; each link says whether it comes from the manuscript or from that index (cited as a link only). They are external claims. For two of them (025, Erdős #304; 184, Erdős #802) P42 rebuilt OpenAI's Lean proof, found it compiles with only the standard axioms, re-checked it with an independent kernel (nanoda), and reviewed the Lean statement as faithful (025 covers #304 only, not #293 or #148). These are checks of OpenAI's proofs, not P42 results, and no entry changes a status here.
- The [Plasma overlay](atlas/plasma_claims.json) lists 155 places where
  Plasma AI's erdosproblems.ai wiki differs from this atlas, each with our
  review. It uses metadata only, with attribution, under CC BY 4.0.
- [`atlas/lean_lane.json`](atlas/lean_lane.json) pins external Lean
  formalization checkpoints, including #593 and a deliberately partial #625
  checkpoint. A pinned formalization's scope is distinct from later progress on
  the problem; see the [source update](experiments/astra-freshness-20260911/README.md).

## Source freshness

**The generated graph is a pinned snapshot, not a live upstream feed.** A passing
staleness gate means generated files agree with their source data; it does not
mean every source has been checked against today's literature. Some production
statuses are superseded by the dated research overlays, intentionally without
silently rebuilding the graph.

- **Upstream status.** From 2026-10-06 erdosproblems.com no longer displays
  problem statuses ([blog:9](https://www.erdosproblems.com/forum/thread/blog:9);
  see also [blog:8](https://www.erdosproblems.com/forum/thread/blog:8)). Atlas
  statuses follow [teorth/erdosproblems](https://github.com/teorth/erdosproblems)
  `data/problems.yaml`, pinned in `atlas/stubs.json` (currently `bcd2fbd`), and
  later claims don't update them.
- The [September 11 Erdős update](experiments/astra-freshness-20260911/README.md)
  lists the checked changes for #477, #625 and #501, distinguishes mathematical
  status changes from Lean-label changes, and preserves differences between the
  website and YAML snapshots.
- The [September 27 strike-board check](experiments/claude-freshness-20260927/README.md)
  compares every board surface with upstream at `af83692` and lists T3 cells
  settled elsewhere since the July mining (#1016, #1062, #1057, #302, #156 and
  others), marking which findings were replayed and which are only reported.
- The [RH source review](experiments/astra-rh-969-20260912/FRESHNESS.md) and
  [P327 review](experiments/astra-327-fiber-20260912/FRESHNESS.md) are dated
  September 12, 2026. They are source snapshots, not continuing monitors.
- Before starting a new attack, check the official problem page, its discussion,
  the separate proof-claim register, and the cited manuscript versions. Consult
  [erdosproblems.com](https://www.erdosproblems.com) for the human-maintained
  index; don't infer current status from an old attack card or prize label.

The repository is a computational and research annex to that index, not a copy
of its prose. Machine metadata sources and licenses are listed in
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

`audit-fast` runs the atlas, gap-map, tool and claim validators, checks the
generated views, book and graph, verifies claim contracts, runs their fast
replay profile, and runs the repository tests. It does not recompile every Lean
project, rerun large historical searches, or recheck every cited analytic
theorem.

The [CI workflow](.github/workflows/verify.yml) uses Python 3.12 for the fast gate.
Its slower receipt-drift job runs on a schedule or by manual dispatch, not on
every PR. Run `make check-receipts` before merging certificate changes, following
the frozen-certificate policy, and read its coverage report rather than taking a
pass as certification of every stored receipt. Slow claim replays have separate
resource requirements, documented in the [Makefile](Makefile).

The [RH audit archive](experiments/astra-rh-crt-20260912/audits/README.md) has its
own scratch-only replay command and explicit source-dependent exclusions.
Default method verifiers read and recompute evidence without replacing it.
Emission commands are separate and require a new output path.

## Honest scope

- A finite exact check settles only the stated finite claim. An asymptotic
  theorem needs an argument covering its unbounded parameters.
- A formal theorem is checked relative to its declared dependencies and axioms.
  A passing Python gate does not establish a Lean rebuild or a human review.
- Model audits, human peer review, formal kernel checks and official acceptance
  are different kinds of evidence. None silently substitutes for another.
- A generic-coefficient countermodel is not a Möbius counterexample. An unsigned
  collision count is not a lower bound for a signed moment.
- A shared tag, OEIS sequence or graph neighbor suggests a question; only a
  sourced implication, or one with a complete argument, supports a mathematical
  transfer.
- A finite-counterexample handle is not a promise of a reachable search or a
  claimable prize. Walls apply to stated branches, not automatically to every
  mathematical approach to a problem.
- Corrections remain visible. New work does not silently upgrade earlier
  priority, publication or resolution claims.

## CHRONOS Frontier Board

**Historical board, July to October 2026.** This table keeps the claims,
qualifications and retractions as they were written down, row for row. It is
not a fresh literature or priority audit. Its rows also feed the generated book
and State of the Frontier, and several are bound to claim contracts, so they
change only with their evidence. For current work, see
[our own results](#our-own-results).

Tier: 🟢 certified finite or formal claim · 🟡 grounded or partial · ⚪ open or in
progress · 🔴 corrected or retracted. Read the linked claim contract and artifact
scope.

<details>
<summary>Certificate movements and corrections</summary>

| tier | problem | what CHRONOS contributed | certificate | when |
|---|---|---|---|---|
| 🟢 | **#699** binomial-gcd rows | **property holds for every `n` in `[10⁷, 10⁸)`** — all 90,000,000 rows, every `(i,j)` pair decided exactly, zero counterexamples, 119.53 core-hours. First exhaustive **general-row** sweep past `10⁷` (structured families were already covered to ≈`1.34×10⁸`). Rests on a theorem that large primes never suffice on a pruned row — `p=2` can be the only usable one | [`certificates/erdos-699`](certificates/erdos-699) · PR #129 | 2026-07-27 |
| 🟢 | **#366** 2-full/3-full neighbours | **no 2-full `n` with `n+1` 3-full for `n ≤ 10²⁵`** — 1,620,172,043 cubefull candidates, both orientations, 6.27 core-hours. A 1000× extension of `10²²`, which was a **single unreplayed 2011 OEIS b-file**; this re-derives that region independently. The lever: enumerate the **cubefull** side (`~X^(1/3)`), not the powerful-**pair** side (`~X^(1/2)`) that set the old bound | [`certificates/erdos-366`](certificates/erdos-366) · PR #125 | 2026-07-26 |
| 🟢 | **#743** Gyárfás tree packing | **every one of the 45,376,056 tuples `(T₂,…,T₁₀)` decomposes `K₁₀`** — exhaustive, uncapped, 44 core-seconds. Frontier had stood at `n ≤ 9` since **Fishburn 1983** (43 years); `n=9` reproduced as positive control. Hardest tuples are exactly those with `T₄..T₇` all stars — where Gyárfás–Lehel's coverage stops | [`certificates/erdos-743`](certificates/erdos-743) · PR #126 | 2026-07-27 |
| 🟢 | **#993** tree independence unimodality | **all 23,522,619,475 trees on `n ≤ 30` unimodal**, zero violations, 10.33 core-hours. Includes the **first independent replication** of the `n ≤ 29` frontier (Reynolds, Zenodo v3, 8,691,747,673 trees — single-author, unreplayed until now), reaching his exact total. `n=30` alone is 1.71× that entire prior workload | [`certificates/erdos-993`](certificates/erdos-993) · PR #126 | 2026-07-27 |
| 🟢 | **#552** `R(C4,K1,n)` | certified C₄-free witnesses ⇒ `R(C4,K1,n) = n + ⌈√n⌉ + 1` for `12 ≤ n ≤ 16`; `n=17` closed at `22` (Parsons 1975) | [`certificates/erdos-552`](certificates/erdos-552) · PR #78 | 2026-07-16 |
| 🟢 | **#241** B₃-subset table (A387704) | proved `A387704(n) = max{k : A227358(k) ≤ n−1}` (translation invariance; 0/151 mismatches) ⇒ first jump to 9 at `n=209`; atlas cell **closed by cross-reference** | PR #80 | 2026-07-16 |
| 🟢 | **#13** Erdős–Sárközy | certified exact table `f(1..45)`; `N=17` is the **last** exception to `⌊N/3⌋+1` — an empirical location for Bedert's ineffective threshold | [`certificates/erdos-13`](certificates/erdos-13) · PR #81 | 2026-07-17 |
| 🟢 | **#979** `f₃` / A385316 | **`a(6) > 10¹²` at C2** — a replayable certificate in this repo (`verify.py --cutoff 1e12`, ~80 s, ~11 GB; reproduces `a(1..5)` as a fail-closed self-check). It is not the best known bound: [OEIS A385316](https://oeis.org/A385316) reports `a(6) > 3.166·10¹⁴` (comment by Morfis Sallis, Oct 16 2026); ProjectForty2 has not re-verified that bound. A stronger `> 10¹³` sweep exists but its code and ledgers are **not tracked here**, so it is **quarantined from public promotion** pending a self-contained replay packet — see the entry note in the gap map. *(Corrected 2026-07-25: this row previously claimed `> 10¹³` at C1; the second "independent implementation" backing that class lives outside this repository, so a reader could not replay it. Corrected 2026-10-26: removed "past the published 4.99·10¹¹" after an OEIS cross-check.)* | [`certificates/erdos-979`](certificates/erdos-979) | 2026-07-19 |
| 🟡 | **#1107** Mollin–Walsh / A056828 | verified **no seventh exception below `10⁶`** to being a sum of ≤3 powerful numbers (`verify.py`, default `N = 10⁶`, ~10 s, dependency-free); the six known exceptions `{7,15,23,87,111,119}` are all `< 120` and are reproduced, powerful-counts cross-checked vs A118896. A wider `10¹⁰` run exists but is **not replayable from this repository**, so it is not the public claim. *(Corrected 2026-07-25: this row previously claimed `10¹⁰`.)* | [`certificates/erdos-1107`](certificates/erdos-1107) | 2026-07-18 |
| 🟡 | **#142** `r₃(N)` | **status: open.** Certified no-go results showing a family of constructions cannot beat `7/24` on one fixed geometry: complete 12,349-cell geometric enumeration (superseding a flawed 976-cell subset) with the affine-family no-go, plus the recovered additive piece-local and pair-context affine lift no-gos. **No new bound** on `r₃(N)` | [`certificates/erdos-142`](certificates/erdos-142) · [`certificates/erdos-142-complete-sos`](certificates/erdos-142-complete-sos) · PR #84 | 2026-10-29 |
| 🔴 | **#142** / D15 lemmas | **refuted** `ker π ∩ D = 0` and `q ≥ dim ker π` (two lemmas a bridge attempt rested on) and proved Theorem A in their place — a dead path closed so the next agent does not re-walk it; explicitly **not** an `r₃(N)` bound | [`certificates/erdos-142-kerpi-refutation`](certificates/erdos-142-kerpi-refutation) · PR #101, #102 | 2026-07-24 |
| 🟢 | **#1029 / #77** `R(5,5)` | 42/42 DRAT-certified structural negatives (no witness; rigidity + prime-order orbit collapse), all consistent with `R(5,5) = 43` | [r55-rigidity-certificates](https://github.com/techno-optimist/r55-rigidity-certificates) · DOI [10.5281/zenodo.21305022](https://doi.org/10.5281/zenodo.21305022) | 2026-07-10 |
| 🔴 | **#552** `R(C4,K1,39)` | the `=46` **new-value** claim was **retracted** — DS1 rev.18 lists `46 ≤ f(39) ≤ 47`, OPEN; the 45-vertex witness stands as a re-derivation of Wu–Sun–Radziszowski 2015 | [`certificates/erdos-552-f39`](certificates/erdos-552-f39) | 2026-07-17 |
| 🟢 | **#357** segment-sum sequences (A364132 / A364153) | new sequence terms **A364132(28) = 75**, **A364153(17) = 26** and **A364153(18) = 28**, from exhaustive computer search confirmed by a second independent program — a computer search, not a proof; problem #357 stays open. Kevin's comment: https://erdosproblems.ai/problems/357#discussion | [certificates/erdos-357](https://github.com/techno-optimist/erdos-frontier-atlas/tree/main/certificates/erdos-357) (https://github.com/techno-optimist/erdos-frontier-atlas/tree/main/certificates/erdos-357) · PR #186, PR #187, PR #192 | 2026-10-30 |

</details>

The board covers Erdős cells only; it is not the inventory of current research
methods. The full certificate catalogue and caveats are in
[`certificates/README.md`](certificates/README.md). Changing a board claim needs
the matching evidence and claim-contract update, not just a README edit.

## Independent checks of other people's results

Much of what we do is check work that belongs to others, and say exactly what
the check covered.

- **The 2026 Jacobian Conjecture crater.** The repository preserves its independent verification of Alpöge's 2026 counterexample
  in [`certificates/jacobian-conjecture/`](certificates/jacobian-conjecture), with
  credit to the external construction. The
  [crater model](atlas/jc-crater/README.md) separates the exact object check from
  propagated consequences, and its
  [root-claim file](atlas/jc-crater/root_claim.json) keeps the announcement's
  conditional status and source history. Read those dated sources before citing
  the propagation; this README doesn't set a peer-review, acceptance or
  retraction status. The reusable [`crater` machinery](tools/crater.py) and
  quarantined claims remain available.
- **Graffiti and Keller.** The [Graffiti 284](certificates/graffiti-284-refutation),
  [Graffiti 290](certificates/graffiti-290) and
  [Keller-map family](certificates/keller-power-weighted-lifts) lanes credit
  their external authors and state what the local replay checks. The
  constructions and original results are not ours. The Graffiti 290 claim
  depends on the stated gravity convention, and its README keeps that
  distinction.
- **Formal artifacts.** These include the [Jacobian](certificates/jacobian-conjecture/lean)
  and [Ringel nonstretchability](certificates/ringel-nonstretchability/lean)
  projects, the [binomial-gcd seeds](experiments/astra-lean-seed-20260904/README.md)
  and the [P699 i=2 work](experiments/astra-i2-complete-20260911/README.md). Their
  exact statements, toolchains, dependency pins and axiom checks belong to the
  individual bundles. This README doesn't claim a fresh build of all of them, or
  extend a helper theorem to its parent conjecture.

A checksum identifies code bytes; it doesn't show that the checker is correct.
Claim contracts, independent semantic replays and negative controls cover
separate parts of that trust boundary. See each lane's documented coverage.

## Where everything lives

| Area | Files |
|---|---|
| AI-assisted discovery map | [`atlas/tools.json`](atlas/tools.json) · [`atlas/ai_results.json`](atlas/ai_results.json) · [`atlas/ai_claims.json`](atlas/ai_claims.json) · [`atlas/openai_math.json`](atlas/openai_math.json) · [`atlas/plasma_claims.json`](atlas/plasma_claims.json) · [`atlas/lean_lane.json`](atlas/lean_lane.json) |
| Certificates and claim contracts | [`certificates/README.md`](certificates/README.md) · [`certificates/contracts.json`](certificates/contracts.json) |
| Research methods | [`atlas/substrate.json`](atlas/substrate.json) · [`experiments/`](experiments) · [method board](experiments/astra-substrate-20260911/BOARD.md) |
| Executable reductions | [`tools/briefcase.py`](tools/briefcase.py) · [`tools/briefcaselib/`](tools/briefcaselib) · [`tools/briefcase.html`](tools/briefcase.html) · [`atlas/residuals.json`](atlas/residuals.json) |
| Production attack graph | [`GRAPH.md`](GRAPH.md) · [`atlas/graph/`](atlas/graph) · [`views/graph/`](views/graph) · [`views/sorties.md`](views/sorties.md) |
| Feasibility overlays | [`atlas/walls.md`](atlas/walls.md) · [`atlas/lanes.md`](atlas/lanes.md) · [`atlas/gap_map.json`](atlas/gap_map.json) |
| Generated views and book | [`views/`](views) · [operations annex](views/operations.md) · [`book/`](book) |
| Validators and tests | [`tools/`](tools) · [`tests/`](tests) · [`Makefile`](Makefile) · [CI workflow](.github/workflows/verify.yml) |
| Project policy and releases | [`COORDINATION.md`](COORDINATION.md) · [`FRONTIER_CARTOGRAPHY.md`](FRONTIER_CARTOGRAPHY.md) · [`RELEASING.md`](RELEASING.md) · [`NOTICE`](NOTICE) |

## Contributing — humans and agents

Corrections, counterexamples, narrower statements and new sources are all
welcome. The most useful contribution is often telling us where we are wrong.

1. **Point us to a result.** Open an issue with the primary source (paper,
   repository, preprint or post), the exact claim, and what AI assistance the
   authors describe. We add it with its source and the right label.
2. **Correct us.** Open an issue with the exact claim, source or failing replay.
   We fix the map first and keep the correction where the next reader will find
   it.
3. **Add a result of your own.** Read [`GRAPH.md`](GRAPH.md), the relevant
   attack card and the walls before committing compute, and register a bounded
   lane in [`COORDINATION.md`](COORDINATION.md). Work on your own branch and
   reach `main` by reviewed PR. Never force-push another lane.
4. **Bring receipts.** State the exact statement, hypotheses and remaining
   obligation. Commit the evidence, a replay command, an independent second
   check where appropriate, and a planted input that fails the same gate. Cite
   third-party manuscripts by version and hash rather than copying them in.
5. **Label honestly.** Add methods to the substrate with honest evidence labels.
   Never promote a candidate match to an implication, and never set a status by
   hand. Keep merged certificates and the production graph frozen unless a
   versioned change is authorized.
6. **Keep this page true.** If you change a count or an entry point, update this
   README. `tests/test_readme.py` checks the counts and links. Run the pinned
   gate and confirm CI on the pushed branch.

## Credits

This atlas rests on other people's work, and we try to credit it wherever it
appears.

- **Paul Erdős**, whose problems started all of this.
- **Thomas Bloom** and the contributors to [erdosproblems.com](https://www.erdosproblems.com),
  the human-maintained index, and to
  [teorth/erdosproblems](https://github.com/teorth/erdosproblems) (Apache-2.0),
  including **Terence Tao**, which supplies the problem data the hub is built from.
- **The Formal Conjectures authors** at [google-deepmind/formal-conjectures](https://github.com/google-deepmind/formal-conjectures)
  (Apache-2.0), for statements and formalization metadata.
- **Plasma AI**, for the [erdosproblems.ai wiki](https://github.com/plasma-ai/erdos)
  (CC BY 4.0), whose metadata the Plasma overlay uses with attribution.
- **[OEIS](https://oeis.org)** and its editors and contributors, whose sequences
  and b-files every finite result here is checked against.
- **OpenAI**, for publishing [openai/math](https://github.com/openai/math) under
  Apache-2.0 with Lean proofs anyone can rebuild.
- **The authors of every tool and result** in [`atlas/tools.json`](atlas/tools.json)
  and [`atlas/ai_results.json`](atlas/ai_results.json), and the mathematicians
  whose constructions and theorems we check, among them Alpöge (the 2026
  Jacobian counterexample) and Reynolds (the n ≤ 29 tree census). Each entry
  names its own authors.

The atlas is maintained by Kevin Russell ([ProjectForty2](https://projectforty2.ai))
with the P42 research agents. Machine metadata sources and licenses are listed
in [`NOTICE`](NOTICE).

## Citing

The dataset release **EFA-DR1** is citable at
[10.5281/zenodo.21443635](https://doi.org/10.5281/zenodo.21443635).
See [`CITATION.cff`](CITATION.cff), [`RELEASING.md`](RELEASING.md),
[`LICENSE`](LICENSE) and [`NOTICE`](NOTICE). For work added after that release,
cite the exact commit too; a later branch is not silently a new DOI snapshot.

The original deep-audit sources and dates remain in
[`atlas/problems.json`](atlas/problems.json). Related verifier-first work includes
[r55-rigidity-certificates](https://github.com/techno-optimist/r55-rigidity-certificates)
and [antipodal-kissing-bounds](https://github.com/techno-optimist/antipodal-kissing-bounds).
Problem history and official status belong to
[erdosproblems.com](https://www.erdosproblems.com), not to this repository's
research labels.

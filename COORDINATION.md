# Agent Coordination — Erdős Frontier Atlas

**Many agents contribute to this atlas at once** (`agent/*`, `codex/*`, `claude/*`,
`automation/frontier-scout`), and `main` is Kevin-curated. This doc is the shared
anti-clobber contract and the lane roster. **Every agent working the atlas: read
this, register your lane below, and keep it current.**

## Rules (all agents)

1. **Work on your own branch; reach `main` by PR.** Never force-push or rewrite a
   branch you did not create. Never push directly to `main`.
2. **Merged certificates are FROZEN.** A `certificates/<slug>/` that verifies is a
   published claim. **Do not regenerate, move, or overwrite it** — extend with NEW
   files/slugs and let the scout add/adjust the board row.
3. **COMMIT every proof object you want to keep.** Certificates, verifiers,
   witnesses, hash-pinned data → committed on a branch. **Never leave a result you
   care about as an untracked working-tree file.** (See the E142 incident below —
   a replayed-clean no-go was *lost* because it was untracked.)
4. **Don't delete or edit another agent's files.** If you must reuse a name, suffix
   it with your lane + date.
5. **The atlas HUB is fed by each agent's local RESULTS REGISTRY**
   (`cultural-soliton-observatory/RESULTS_REGISTRY.md` → `frontier_atlas.json` via
   `build_frontier_atlas.py`). Log a result there when it is re-verifiable; keep
   corrected/lost results flagged honestly (`falsified-negative` / `artifacts-lost`)
   — don't silently delete an entry. The hub renders to
   `projectforty2.ai/prizes/atlas`.
6. **Before deleting/overwriting anything you didn't create — check `git`, and don't.**
   In doubt, ask Kevin.

## Lanes — SELF-REGISTER (this is the part every agent updates)

Add a row when you start a lane; keep your status current; name what you OWN so
others don't touch it.

| Lane / branch | Angle | Owns (don't clobber) | Status |
|---|---|---|---|
| `openai-math/source-and-proofs` | Pinned release crosswalk and exact arithmetic/formal components | `experiments/openai-math-20261006/`; root discovery links | mathematical source package: historical catalogue and 133 scoped connections; P699/P841 local proof components and P969 obstruction; no canonical status change |
| `openai-math/weighted-p699` | Explicit weighted positional blocks to a cubic strip | `experiments/openai-math-20261006/lead-phase/weighted-formal/` | retained Lean component: 13 algebraic declarations and two numerical controls; binomial-to-block extraction remains informal |
| `openai-math/upstream-20261008` | Dated withdrawals, revised editions and formalization scope | `experiments/openai-math-20261006/upstream-update/` | metadata comparison: three withdrawals, 27 replacement editions, 11 formalization additions; F130 ideal all-length scope updated, numerical and analytic transfers remain blocked; no external proof replay |
| `agent/harden-r3-search-semantics` | r₃(N) search semantics (Erdős #142) | *(register)* | *(register)* |
| `codex/foundry-*` | foundry / atlas integration + gates | *(register)* | *(register)* |
| `claude/erdos-142-certificate` | E142 orchestration · results registry · board certs | `certificates/erdos-142/`, `RESULTS_REGISTRY.md` | frozen E142 cert merged-pending |
| `agent/jc-fences-fib-macro-20260720` | JC fiber/degree family fences + Fibonacci L=3 macro residual | `certificates/jc-family-fences/`, `certificates/fibonacci-macro-residual/` | PR packaging 2026-07-20 |
| `agent/sendov-wall-ledger-20260721` | Sendov conjecture CE hunt → wall ledger (0 CEs; dual-ray/jet/squeeze) | `certificates/sendov-conjecture/` | PR packaging 2026-07-21 |
| `agent/formal-spine-593-625-20260722` | External Lean formalization pins for #593 and #625 | `atlas/lean_lane.json`, README formal-spine note | PR packaging 2026-07-22 |
| `claude/erdos-366-sweep-20260726` | Erdős #366 cubefull-side sweep — verified range 10^22 → 10^25, zero strict-orientation solutions | `certificates/erdos-366/`, gap_map #366 row, contracts claim `erdos-366-cubefull-sweep-1e25` | PR packaging 2026-07-26 |
| `claude/attack-graph-20260726` | The attack graph — a generated agent-facing overlay over every ledger (`GRAPH.md` → `views/sorties.md` → per-problem cards). Adds no facts; organizes existing ones | `tools/build_graph.py`, `tools/validate_graph.py`, `tools/query_graph.py`, `atlas/graph/`, `views/graph/`, `views/sorties.md`, `GRAPH.md`, `CLAUDE.md`, `tests/test_graph.py` | PR packaging 2026-07-26 |
| `claude/trees-993-743-20260727` | Tree lanes: Erdős #743 Gyárfás packing at K_10, and #993 independence unimodality to n=30 (incl. first replication of the n≤29 frontier) | `certificates/erdos-743/`, `certificates/erdos-993/`, gap_map #743 + #993 rows, contracts claims `erdos-743-k10-packing` + `erdos-993-unimodal-n30` | PR packaging 2026-07-27 |
| `agent/astra-structural-probes-20260904` | Official-source freshness, P699 near-central strip, P993 structural probes | [Research bundle](experiments/astra-20260904/README.md) — `experiments/astra-20260904/` only | ready for repository review; unpromoted |
| `agent/astra-briefcase-transfers-20260904` | Proof transfer: compressed P993 tree tails, general hub blocks, arithmetic bridges, P699 residual strip | [Research bundle](experiments/astra-briefcase-20260904/README.md) — `experiments/astra-briefcase-20260904/` only | reviewed and replayed; PR stacked on #135; no promoted claims |
| `agent/astra-lean-seed-20260904` | Lean-checked adjacent-binomial gcd and divisor transfer; explicit proof obligations | `experiments/astra-lean-seed-20260904/` only | formal seed, not full P699; stacked on briefcase lane |
| `agent/astra-i2-family-20260911` | Kernel-checked P699 i=2, n=2j+3 infinite family; official-status delta since 2026-09-04 | `experiments/astra-i2-family-20260911/` only | formal family, not full P699; stacked on lean-seed lane |
| `agent/astra-substrate-20260911` | Reusable method substrate over the attack graph (queryable; no generated-graph edits) | `atlas/substrate.json`, `tools/query_substrate.py`, `tests/test_substrate.py`, `experiments/astra-substrate-20260911/` | overlay, not a status change |
| `agent/astra-i2-complete-20260911` | Elementary complete i=2 case of P699: gcd(C(n,2),C(n,j))>1 | `experiments/astra-i2-complete-20260911/` | kernel-checked gcd form; not full P699 |
| `agent/astra-i3-20260911` | Elementary i=3 slice of P699: gcd≥2 always; p≥3 when n≡3 (mod 4) | `experiments/astra-i3-20260911/` | gcd form kernel-checked; 2-adic residual open |
| `agent/astra-i3-residual-20260911` | i=3 2-adic residual: coprime-to-j! cancel; o|P only three pairs | `experiments/astra-i3-20260911/` (residual files + I3 cancel lemmas) | not full P699; o\|P unbounded remainder |
| `agent/astra-i3-close-20260911` | Close i=3 gcd form: Case1 kernel; n=2p only (10,5); type B to 1e5 | `experiments/astra-i3-20260911/` | i=3 gcd-odd not fully unbounded |
| `agent/astra-i3-typeA-20260911` | Type A cracked: P+(o)>n/4 implies o|P only (10,5),(16,7) | `experiments/astra-i3-20260911/typeA.*` | Type B last i=3 class |
| `agent/astra-i3-typeB1-20260911` | Type B1: n/6<p≤n/4 only (65,15); campaign STACK.md | `experiments/astra-i3-20260911/typeB1.*`, `STACK.md` | Type B2 P+≤n/6 |
| `agent/astra-i3-typeB2a-20260911` | Type B2a: n/8<p≤n/6 empty | `experiments/astra-i3-20260911/typeB2a.*` | Type B2b P+≤n/8 |
| `agent/astra-i3-mod4-band89-20260911` | n≡3 (mod 4) o\|P empty; band m=8,9 | `experiments/astra-i3-20260911/mod4.*`, `bands.*` | B2b P+≤n/10 |
| `agent/astra-freshness-376-20260911` | YAML freshness 477/625/501; #376 Kummer digit checker | `experiments/astra-freshness-20260911/`, `experiments/astra-376-20260911/` | #376 infinitude / 10^70 cell |
| `agent/astra-376-search-20260911` | #376 complete A030979 prefix through 3^24 | `experiments/astra-376-20260911/search.md` | infinitude; next >10^70 |
| `agent/astra-376-csearch-20260911` | #376 C search complete through 3^31 (18 terms) | `experiments/astra-376-20260911/search_base3.c` | infinitude; >10^70 |
| `agent/astra-376-d35-20260911` | #376 C search complete through 3^35 (43 terms) | `experiments/astra-376-20260911/hits-d35.txt` | infinitude; >10^70 |
| `agent/astra-goal-b2b-20260911` | Campaign GOAL north star; Type B2b structural leftover | `experiments/astra-i3-20260911/GOAL.md`, `typeB2b.*` | smoothness of n-1 vs 3-consecutive P |
| `agent/astra-ppower-20260911` | prime-power n-1 ⇒ o∤P | `experiments/astra-i3-20260911/typeB2b.*` | two-prime n-1; n≡1 mod 4; n≡4 mod 6 |
| `agent/astra-327-fiber-20260912` | P327 multiplier-sensitive smooth fibers: exact density-transfer operator, not a next-cell search | `experiments/astra-327-fiber-20260912/`; additive substrate entry | exact checker and hand certificates pass; independent model reviews; no status or production-graph changes |
| `agent/astra-rh-969-20260912` | RH / P969: energy equivalence, generic obstruction, CRT/defect and Mellin transfers, GM/GMRR deduction, sharp Type I and signed-diagonal interfaces; README refresh | [Progress map](experiments/astra-rh-969-20260912/REPOSITORY_STATUS.md); both RH experiment directories, additive substrate entries, replay tests, root README and its freshness guards | [PR #156](https://github.com/techno-optimist/erdos-frontier-atlas/pull/156); independent software review passed (33 Python files); model-audited 4/7-epsilon variance deduction from named inputs; full signed residual and RH remain open; no canonical status, production-graph or frozen-certificate changes |
| `chronos/quirky-gates-dalhc4` | P699 positional localization for every i ≥ 3 (`experiments/claude-699-general-i-20260928/`, substrate method `general-i-positional-localization`): a counterexample forces R_0 | j and R_t | ∏(t·m − r·S_0) at every position, hence 4(n−1) ≤ S_0²S_1 and 6√3(n−1)(n−2) ≤ S_0³S_1S_2; for fixed i the failing n up to X are O(X^(1/3) log^π(i) X); an exact C search (pinned to a Python reference) finds no counterexample for i = 4, 5 to 10¹⁸, i = 6, 7 to 10¹⁷, i = 8, 9, 10 to 10¹⁵ and i = 11, 12, 13 to 10¹² (research note, no status change); briefcase v2: `tools/briefcase.py` + `tools/briefcaselib/` (exact row decider with checkable row certificates), `tools/briefcase.html` (in-browser calculator) and the residual ledger `atlas/residuals.json`; P699 i=3 positional localization (`experiments/claude-699-i3-position-20260928/`, substrate method `i3-positional-localization`): odd n and n ≡ 2 (mod 4) closed, 4 | n reduced to odd part ≲ 0.66·n^(1/3), exact search clean to 10¹⁸ (research note, no status change); Erdős #864 sets with one repeated sum: A389182 through N = 117 by one exhaustive search per N (`certificates/erdos-864/`, contracts `erdos-864-a389182-published` and `-new`; a(101..117) new, confirming the unverified external report; gap_map #864 re-pointed to a(118)); Erdős #357 distinct segment sums: A364132 through n = 27 and A364153 through n = 16 by exhaustive search (`certificates/erdos-357/`, contracts `erdos-357-a364132-a364153-published` and `-new`; A364132(23..27) = 56, 60, 63, 67, 69 and A364153(14..16) = 20, 22, 24 new; gap_map #357 re-pointed to A364132(28)); Erdős #131 nondividing sets: A068063 thresholds T_1..T_10 by exhaustive search (`certificates/erdos-131/`, contracts `erdos-131-a068063-t1-t8` and `-t9-t10`; T_9 = 107 and T_10 = 155 new; gap_map #131 re-pointed to T_11); Erdős #1109 squarefree sumsets: A392165 records through N = 2000 by exhaustive clique search (`certificates/erdos-1109/`, contracts `erdos-1109-a392165-1-39` and `-1-54`; A392165(40..54) new; gap_map #1109 re-pointed to A392165(55)); Erdős #962 long runs with a large prime factor: A327909 through n = 1102 by an exact smooth-number scan to 4.2e10 (`certificates/erdos-962/`, contracts `erdos-962-a327909-1-400` and `-1-1102`; a(1000..1102) new; gap_map #962 re-pointed to a(1103)); Erdős #854 coprime-gap spectrum: A389839 through n = 16 (exhaustive; `certificates/erdos-854/`, contracts `erdos-854-a389839-2-15` and `-16`; gap_map #854 re-pointed to a(45)); atlas upstream snapshot refresh (teorth 39cde0f); Erdős #1016 minimal pancyclic graphs: exact h(n) for n ≤ 186, t₆ = 67 and t₇ = 114 (settles the six-chord levels 72–79, 81, 83–85 left open by the 2026 external campaign; complete seven-chord census; replicates everything below 68); strike-board freshness overlay dated 2026-09-27, then curated into the gap map (#156, #302, #451, #1057, #1062, #1095 re-pointed past externally settled cells; #376 and #1005 closed; #301 re-pointed to A390394(73) and an A006065 source conflict flagged on #588/#101 by the new `tools/oeis_cell_freshness.py`; #791 re-pointed to A001212(25), its cell A066063(51) = 12 being implied by the postage-stamp table; #20 lower bound 39 → 40; #458, #773, #864, #1100 carry dated external reports; offline re-checks in `curation_checks.py`); contract schema: `overclaim_guards` separated from retraction pins (`must_not_contain`) so preventive guards stop rendering as withdrawals | `experiments/claude-699-general-i-20260928/`, `tools/briefcase.py`, `tools/briefcase.html`, `tools/briefcaselib/`, `atlas/residuals.json`, `tests/test_briefcase.py`, `tests/test_readme.py` (residual count), `experiments/claude-699-i3-position-20260928/`, `atlas/substrate.json` (two appended methods; the i=3 entry's `remaining` now points at the general method), `experiments/astra-substrate-20260911/BOARD.md` (regenerated), `certificates/erdos-864/`, gap_map #864 row, `certificates/erdos-357/`, gap_map #357 row, `certificates/erdos-131/`, gap_map #131 row, `certificates/erdos-1109/`, gap_map #1109 row, `certificates/erdos-962/`, gap_map #962 row, `certificates/erdos-1016/`, gap_map #1016 row, contracts claims `erdos-1016-h-table-t6-67` and `erdos-1016-t7-114`, `experiments/claude-freshness-20260927/`, gap_map rows #20 #101 #156 #301 #302 #376 #451 #458 #588 #773 #791 #864 #1005 #1057 #1062 #1095 #1100; guard migration in `certificates/contracts.json` (366, 699, 743, 993, 1016), `tools/check_certificate_contracts.py`, `tools/build_graph.py`, `tools/oeis_cell_freshness.py` | PR packaging 2026-09-27; k ≤ 6: two in-repo implementations agree; k = 7: C port pinned to the Python reference, independent C check where reachable; no formal proof |
| *(add your lane)* | | | |

## Erdős-142 — active multi-lane, read before touching

Three lanes hit #142 from different angles. **The verified floor (don't re-lose it):**
geometry `sha256 607841…92ada`; complete full-dim class = **12,349 cells**
(`sha256 35fb1967…a859b6`) LOCKED; **affine-family no-go** (34-term rational
vertex-Farkas) VERIFIED ⇒ any working potential must be genuinely quadratic. No
`r_3(N)` bound; #142 headline is an asymptotic WALL. All this is packaged, frozen,
and replayable in `certificates/erdos-142/` (`python3 verify.py`).

**The incident (why rule 3 exists):** the stronger "additive-local no-go" proof
objects were UNTRACKED working-tree files; a later run overwrote them and they are
gone from both working copies — a result that was replayed-clean 2026-07-13 is now unbacked.
Commit your certs.

## 2026-07-24 — Erdős 142 / D15: two lemmas REFUTED, one theorem proved

Certificate: `certificates/erdos-142-kerpi-refutation/` (`python3 -I verify.py`,
~2 s, stdlib only, now wired into `make verify-certs`).

**If you are working the D15/PC-F lane, two laws you may be using are FALSE.**

1. **`ker π ∩ D = 0` — REFUTED** on CLOSED products (strongly connected,
   exit-free). Explicit nonzero integer circulation on **4 collar edges**
   (the minimal e₁−e₂−e₃+e₄ rectangle), checked directly against the
   definition on the full product: support ⊆ collar, `incidence_P·d = 0`,
   `π₀=π₁=π₂=0`, `d ≠ 0`. Referee sweep: 31,548 counterexamples in 873,264
   closed products at ≤7 states.
   *Mechanism:* per digit a collar circulation is a 3-index array and the
   three role projections are exactly its three 1-marginals, whose joint
   kernel is large. Flow conservation alone cannot carry the burden.

2. **`q ≥ dim ker π` — REFUTED.** This was the bridge from a `dim ker π`
   floor to a `q` floor, i.e. the route to excluding `q = 1`. It is not
   merely unproved — it is false. Witness `91f52f97…`: the certificate
   recomputes `dim D = 34 > 24 = 3·dim Z₁(B)`, which forces `q < dim ker π`
   (machine-checked bound: `q − dim ker π ≤ −10`). The referee lane
   separately reports the exact values `q = 732`, `dim ker π = 748`; those
   are **NOT re-derived** by the certificate. Forced by **counting**, with
   tiny exact inputs:

       ker π ⊆ Z  ⟹  q − dim ker π = rank(π|_Z) − dim D      (identity)
       im π ⊆ Z₁(B)³  ⟹  rank(π|_Z) ≤ 3·dim Z₁(B)
       ⟹  dim D > 3·dim Z₁(B)  forces  q < dim ker π

   For the witness `dim Z₁(B) = 8` and `dim D = 34 > 24`. `dim Z₁(B)` depends
   only on the base; `dim D` grows with the collar — so the inequality was
   never structural, only an artifact of small-collar objects.
   **A floor on `dim ker π` proves nothing about `q`.**

**PROVED replacement — THEOREM A.** If every collar edge has a diagonal source
`(0,u,u,u)` then `ker π ∩ D = 0`. (Diagonal rows are legal only from carry 0
and the product is deterministic, so a collar edge is determined by
(source,digit); `π₀` sends it to base edge `(u,a)` and `((0,u,u,u),a) ↦ (u,a)`
is injective, so `π₀` is injective on `ℚ^{E(C)} ⊇ D`.) 0 violations over
873,264 closed products. **Its converse is FALSE** — object `5da67053…` has
non-diagonal collar sources and still zero intersection, so source-diagonality
is sufficient, never necessary. For a per-object decision use the exact test
`dim(ker π ∩ D) = |E(C)| − rank[∂; π₀; π₁; π₂]` on collar columns (11–60
edges: milliseconds).

**Any per-object use of `q ≥ dim ker π` now requires BOTH** a `ker π ∩ D = 0`
certificate **AND** counting slack `3·dim Z₁(B) − dim D ≥ 0`.

**Untouched:** the `q = 1` hole itself — still 0 occurrences in >1.18M closed
products, still the unique absent value in 0..24. What is closed is one route
to excluding it; `q` must now be attacked directly.

`erdos142_solved: false`. `new_r3_bound: false`.

*Reported vs recomputed:* `verify.py` recomputes `dim Z₁(B)`, `dim D`,
`dim(ker π ∩ D)`, `rank(π rows)` and H1/H2/H3 on all four objects, in exact
rational arithmetic. All census figures in this section (31,548 / 873,264 /
0 Theorem A violations / >1.18M) and the exact `q` and `dim ker π` values are
**reported by the referee lane, not re-derived** by the certificate.

## 2026-07-26 - Erdos 142 / D15: the CONE obstruction, certified per object

Certificate: `certificates/erdos-142-cone-obstruction/` (`python3 -I verify.py`,
~0.5 s, stdlib only, wired into `make verify-certs`).

**Context, and a retraction of something this lane repeated for a long time.**
The construction gate needs a closed carry-triple product with quotient
signature `(q+,q-) = (1,0)` **and** a cone certificate. The first half now
EXISTS - 298 verified objects, the sealed engine's own `rank_gate` returning
quotient dimension 1 with `passes_quotient_one = True`. So **"q = 1 has never
been observed; the unique absent value in 0..24 across >1.18M closed products"
is STALE and must not be repeated** - it was a search-region artifact, not a
structural fact.

**This certificate is the second half, and it closes negatively.** For three
`q=1` objects it publishes a vertex potential `p` and tag multiplier `theta`
whose edge functional `Y(e) = p[t] - p[s] + <theta, tag(e)>` satisfies
`Y >= 0` on every edge and `Y > 0` off the collar. A cone point is a
circulation with zero tag, so `0 = sum Y(e)w(e) >= sum_nondiag Y(e) > 0` - a
contradiction, using only `w >= 0` and `w >= 1` off the collar. **No solver,
no coefficient cap, no integrality, no sigma-invariance, no reference to q.**
It replaces a CP-SAT INFEASIBLE verdict with a line anyone can audit.

**sigma was never the blocker.** The lane pursued `(1,0)` over `(0,1)`
precisely to obtain a sigma-invariant generator. A relaxation ladder shows:
baseline INFEASIBLE; **drop sigma-invariance -> still INFEASIBLE**; drop
zero-tag, or non-negativity, or the strict `>=1` -> feasible. The conflict is
zero-tag + non-negativity + strict positivity and survives dropping symmetry
entirely. Do not spend further compute on the `(1,0)`-vs-`(0,1)` distinction
for cone purposes.

**Scope, stated exactly.** The certificate settles the three named objects and
nothing more. It is **not** a theorem that every `q=1` product has an
infeasible cone; none is offered. Separately measured but NOT certified here:
collar-LP infeasibility across all 298 known `q=1` objects with the sealed
engine agreeing 298/298 - a measurement over objects found so far.

`erdos142_solved: false`. `new_r3_bound: false`.

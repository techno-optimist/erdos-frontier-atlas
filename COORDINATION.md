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
| `agent/harden-r3-search-semantics` | r₃(N) search semantics (Erdős #142) | *(register)* | *(register)* |
| `codex/foundry-*` | foundry / atlas integration + gates | *(register)* | *(register)* |
| `claude/erdos-142-certificate` | E142 orchestration · results registry · board certs | `certificates/erdos-142/`, `RESULTS_REGISTRY.md` | frozen E142 cert merged-pending |
| `agent/jc-fences-fib-macro-20260720` | JC fiber/degree family fences + Fibonacci L=3 macro residual | `certificates/jc-family-fences/`, `certificates/fibonacci-macro-residual/` | PR packaging 2026-07-20 |
| `agent/sendov-wall-ledger-20260721` | Sendov conjecture CE hunt → wall ledger (0 CEs; dual-ray/jet/squeeze) | `certificates/sendov-conjecture/` | PR packaging 2026-07-21 |
| `agent/formal-spine-593-625-20260722` | External Lean formalization pins for #593 and #625 | `atlas/lean_lane.json`, README formal-spine note | PR packaging 2026-07-22 |
| `claude/erdos-366-sweep-20260726` | Erdős #366 cubefull-side sweep — verified range 10^22 → 10^25, zero strict-orientation solutions | `certificates/erdos-366/`, gap_map #366 row, contracts claim `erdos-366-cubefull-sweep-1e25` | PR packaging 2026-07-26 |
| `claude/attack-graph-20260726` | The attack graph — a generated agent-facing overlay over every ledger (`GRAPH.md` → `views/sorties.md` → per-problem cards). Adds no facts; organizes existing ones | `tools/build_graph.py`, `tools/validate_graph.py`, `tools/query_graph.py`, `atlas/graph/`, `views/graph/`, `views/sorties.md`, `GRAPH.md`, `CLAUDE.md`, `tests/test_graph.py` | PR packaging 2026-07-26 |
| `claude/trees-993-743-20260727` | Tree lanes: Erdős #743 Gyárfás packing at K_10, and #993 independence unimodality to n=30 (incl. first replication of the n≤29 frontier) | `certificates/erdos-743/`, `certificates/erdos-993/`, gap_map #743 + #993 rows, contracts claims `erdos-743-k10-packing` + `erdos-993-unimodal-n30` | PR packaging 2026-07-27 |
| `codex/erdos142-signed-slack-capacity` | P142 recursive outer-code / signed-slack capacity mechanism | `atlas/erdos-142-recursive-capacity.md`, `certificates/erdos-142-mirror-core-additive-wall/`, `certificates/erdos-142-d4-role-distinct-additive-wall/`, `certificates/erdos-142-q24-cylinder-hypograph-wall/`, `certificates/erdos-142-q24-second-orbit-cylinder-hypograph-wall/` | exact q=24 mirror-core and role-distinct walls; both maximum-mass D4 orbits closed under cylinder-position additivity; no survivor / no new bound, 2026-08-17 |
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

## 2026-08-17 — Erdős 142: recursive signed-slack capacity lane opened

Research note: [`atlas/erdos-142-recursive-capacity.md`](atlas/erdos-142-recursive-capacity.md).
Naslund's public 2023 slide deck was recovered and visually audited. It exposes a
recursive weighted-copy/closed-loop capacity mechanism that is more specific than
the later manuscript citations. The P142 translation is a conditional direct
outer-code lemma: for role-dependent EHPS supports, the worst raw-Euclidean
coercivity slack factors across physical two-dimensional torus blocks, and every
ordered codeword triple must have nonnegative summed minimum slack. The mass gate
is actual union mass `> (7/24)^L`, not a cardinality-exponent ratio.

First exact branch result: `certificates/erdos-142-mirror-core-additive-wall/`
rules out both role orientations of the two active words `(P3,B,B)` and
`(B,B,P3)` when the roles contain the exclusive q=24 cores of the EHPS tile
and its coordinate transpose. The stdlib Farkas replay covers every disjoint
allocation of the 53 overlap points, including all 36 cardinality allocations
whose finite union mass beats `(7/24)^3`; this is an additive role-potential,
finite-q wall only. It does not exclude a non-additive global 6D potential or
globally deformed five-role supports.

Second exact branch result:
`certificates/erdos-142-d4-role-distinct-additive-wall/` rules out the
highest-mass assignment in the exhaustive q=24 D4 image screen,
`(P1,P2,P3,B,K)=(7,7,7,6,7)`. Its five cylinders are pairwise disjoint and
have exact union count `21,653,735 > 4,741,632`, but a 622-row positive
integer Farkas combination cancels all 815 **role-distinct** potential
variables. The semantic stdlib replay rebuilds every support, word, midpoint,
carry, raw cost and mass term, and an independent implementation agrees. This
is stronger than the shared-grid-point LP screen, but remains one finite D4
assignment and one additive ansatz.

Third exact branch result:
`certificates/erdos-142-q24-cylinder-hypograph-wall/` closes the same
top-D4 assignment under the strictly larger **cylinder-position additive**
model. Each of the five disjoint cylinders and each of its three physical
coordinate positions receives an independent 163-point potential table, for
2,445 `G` variables. An exact local-hypograph reformulation adds 375 minimum-
slack variables and is equivalent to exhaustive factored pricing. The frozen
771-row positive Farkas combination (662 local witness rows and 109 active
sum rows) cancels all 2,820 coefficients and leaves a strictly negative exact
right side. The stdlib semantic replay reconstructs all 125 ordered sum rows,
midpoints, carries, raw costs, D4 mass, and ten planted failures; a separately
written implementation agrees. This remains finite q=24 and separable across
the three physical coordinates: arbitrary 6D, pair-interaction, and recursive
potentials remain open. The second maximum-mass orbit is handled next.

Fourth exact branch result:
`certificates/erdos-142-q24-second-orbit-cylinder-hypograph-wall/` closes
the second inequivalent maximum-mass assignment `(7,6,7,6,7)` under the same
2,820-variable cylinder-position additive model. Its compact semantic packet
has 816 selected local rows, all 125 ordered sum rows, and 931 positive integer
Farkas multipliers. Exact cancellation leaves a strictly negative right side;
eight planted corruptions are rejected, and a separately written stdlib replay
agrees. The verifier also reruns the complete `8^5` mass census and proves that
the 16 maximizers are exactly the disjoint eight-member symmetry orbits of
`(7,7,7,6,7)` and `(7,6,7,6,7)`. Paired with the third branch certificate,
this closes every maximum-mass D4 assignment under cylinder-position
additivity. It remains finite q=24 and does not touch pair-coordinate,
arbitrary 6D, recursive, deformed-support, or continuum potentials.

Next exact test: admit pair-coordinate, non-additive global, or recursive-state
potentials where cylinder-position separability is still too rigid. A corrected
q=6 arbitrary-global sweep is numerically LP-infeasible for both representatives,
but has no exact dual and is not a claim. Accelerate the pair-coordinate oracle,
then reprice at `q=8`/`q=12` or `q=48` and attempt rational continuum thickening
only for a survivor. No finite survivor has been produced.
Naslund's public deck states only the rounded capset rate `2.22`; the cited
`2.2208` manuscript remains unavailable publicly as of the audit.

`erdos142_solved: false`. `new_r3_bound: false`.

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

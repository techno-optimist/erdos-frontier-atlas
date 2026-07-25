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
gone from Mac and DGX — a result that was replayed-clean 2026-07-13 is now unbacked.
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

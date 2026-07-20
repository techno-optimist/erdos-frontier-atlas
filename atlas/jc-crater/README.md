# The JC crater — a machine-propagated implication graph

On 2026-07-19 Levent Alpöge presented an explicit dim-3 counterexample to the
Jacobian Conjecture — *awaiting confirmation* (widely machine-verified within a
day, not yet peer-reviewed; see **Scope** below), with [our independent
certificate](../../certificates/jacobian-conjecture/) of the exhibited object.
Everything the crater derives is conditional on that counterexample.
JC was not an isolated statement: it sat at the center of the densest
implication network in affine algebraic geometry. When the center falls, the
*justified* status of every neighboring statement changes — but by **different
modalities** depending on how each is connected, and prose surveys reliably
botch exactly that distinction.

This directory is the falsification's blast radius as a **versioned,
machine-checked object**:

- [`implication_graph.json`](implication_graph.json) — nodes (each with a
  primary-source statement) and **typed edges** (each with a citation for the
  implication itself): `implies` / `equivalent`, crossed with
  `dimension_preserving` / `dimension_mixing`.
- [`computed_statuses.json`](computed_statuses.json) — **generated**: every
  node's status is derived by
  [`tools/validate_jc_crater.py`](../../tools/validate_jc_crater.py) from the
  certified root via modus tollens. Nothing is hand-asserted; the committed
  view is staleness-gated.
- [`padding_check.py`](padding_check.py) — the stabilization edge
  (FALSE at n=3 ⇒ FALSE for all n≥3, via F ↦ F × id) is **executed**, not
  cited: exact polynomial proof that the padded dim-4 map still has
  det ≡ −2 and still collides.
- [`quantities.json`](quantities.json) — the newborn bounded quantities the
  falsification minted (minimal counterexample dimension, minimal degree, …),
  with `evidence[]` and computed confidence classes, gap_map-style.

## The modality discipline (the point of the whole thing)

A statement `X` connected to JC dies in the way its edge type dictates, and in
no other way:

| edge to JC | JC now FALSE (all n ≥ 3) means | status vocabulary |
|---|---|---|
| `X implies JC`, dimension-preserving | X false for every n ≥ 3 | `REFUTED_ALL_N_GE_3` |
| `X implies JC`, dimension-mixing (reduction with dimension blowup) | X false **in at least one finite dimension**, location unknown | `REFUTED_SOME_FINITE_DIM` |
| `X equivalent to JC`, dimension-preserving | X false for every n ≥ 3 | `REFUTED_ALL_N_GE_3` |
| `JC implies X` | **nothing about X's truth** — its conditional support is void | `OPEN` + `orphaned_conditional_support` |
| no edge | untouched | `OPEN` |

For statements **not indexed by dimension** — Mathieu's conjecture (quantified
over compact Lie groups), the Unimodular conjecture (over primes) — read
`REFUTED_SOME_FINITE_DIM` as "fails for some finite value of the reduction
chain's parameter"; the node's own notes give the exact reading (e.g. "false
for at least one compact group"). The binary preserving/mixing model is
deliberately coarse: a `dimension_mixing` edge always yields the weak floor, and
any sharper per-parameter claim lives in the node notes as hand analysis, never
as a computed status.

If an edge chain ever derives a refutation for a node marked as a **proven
theorem**, the validator halts with `INCONSISTENCY` — that is not a status, it
is a proof that some edge's direction or semantics is wrongly recorded.

## Admission rules (anti-hallucination gate)

The candidate node list originated partly from LLM output. Therefore:

1. **No node without a primary source.** Every candidate was researched by an
   independent verification agent; candidates whose statements could not be
   sourced are stored with `verification: UNVERIFIED_CANDIDATE`, are **excluded
   from propagation**, and may not carry edges. They are kept visible — a
   confabulated conjecture list is itself a finding.
2. **No edge without a citation** for the implication itself (who proved it,
   where), plus an adversarial direction-check: a flipped implication poisons
   every downstream status, so each admitted edge was re-verified against its
   cited source by a second, hostile agent.
3. **Machine checks are executed.** The root certificate and the stabilization
   lift run on every validation; if either exits nonzero the graph is invalid.

## Replay

```
python3 tools/validate_jc_crater.py          # validate + drift-check (runs the machine checks)
python3 tools/validate_jc_crater.py --write  # regenerate computed_statuses.json
python3 -m pytest tests/test_jc_crater.py    # propagation-rule unit tests
```

## Scope, honestly

The graph records what the counterexample **justifies saying**, per edge, per
modality — nothing more. The counterexample itself is Alpöge's ("awaiting
confirmation": widely machine-verified, not yet peer-reviewed); the certificate
this graph roots in is ours; the statuses are computed. Where the literature
was ambiguous about an edge, the edge was left out — an absent edge understates
the blast radius, which is the safe direction to be wrong in.

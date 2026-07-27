# Erdős #617 — a feasibility fence, and a lane that closed while we worked

**Not a certificate.** Working notes preserved so the next agent does not
re-walk this. Nothing here is promoted, and no ledger status is set from it.

## 1. The lane closed upstream — r=5 was settled five times in nine days

Our triage (2026-07-26) called r=5 a TARGET with the frontier at r=4
(Erdős–Gyárfás 1999). A freshness check on 2026-07-27 found
[erdosproblems.com/617](https://www.erdosproblems.com/617) carrying **six
claimed proofs, all submitted 18–25 July 2026**, five of them for r=5:

- **Robert Sneiderman** (2026-07-18) — non-computational extremal argument
- **Conner Silverstein** (2026-07-21) — local-floor induction plus 12
  DRAT-certified UNSAT instances; **independently reproduced** by Marco Del Pin
  (2026-07-23), who regenerated all 12 CNFs byte-identically and re-verified
  12/12
- **Anthony Rose** (2026-07-25) — 458 DRAT-certified instances, ~13.4 GiB
- **Johan Land** (2026-07-23) — independent route, no public artefact
- **Ramazan Kara** (2026-07-24) — **Lean 4 formalization** whose finite
  obstruction is discharged by 89 LRAT certificates *replayed inside the Lean
  kernel*, so no solver output is a trusted premise

Sneiderman additionally claims r=6, 7, 8, 9. Our triage was nine days stale.

## 2. The SAT encoding is intractable — measured, not guessed

Our triage priced this lane as a "SAT encoding of sane size (1,625 vars / 1.15M
clauses)". **Size is not difficulty.** Measured here:

| instance | truth | cadical result |
|---|---|---|
| K_25 balanced 5-colouring | **SATISFIABLE** — we hold an explicit witness | **UNKNOWN at 300 s** |
| K_26 balanced 5-colouring | open at the time | **UNKNOWN at 2400 s** |

The encoding is not at fault: the AG(2,5) witness satisfies **all 888,800
clauses** of the K_25 CNF, checked directly.

Independently corroborated by Rose's companion paper, which ran the same
monolithic encoding and reports it "verified hard at laptop budget (UNKNOWN at
all probes ... ~1.8 CPU-hours)", concluding the bottleneck is "a
representation/symmetry issue, not missing constraints". The plain encoding
carries the full `S_26 × S_5` symmetry, about 4.8e28. One of his instances went
from ≥14,400 s to **0.45 s** under residue symmetry-breaking — a ~32,000× gap
that is entirely symmetry, not search.

**The fence: never price a SAT lane by variable and clause count alone.**

## 3. What we did verify, and it is worth keeping

- **AG(2,5) gives a balanced 5-colouring of K_25** — checked exhaustively over
  all C(25,6) = 177,100 six-subsets, zero misses. So `R^5_4(K_6) ≥ 26`, and the
  open case sat exactly one vertex above a known construction.
- **A trap our ledger hides:** AG(2,5) has **six** parallel classes, not five.
  Colouring by parallel class with only five colours leaves 50 of the 300 edges
  uncoloured. The fix is sound but must be stated: adding edges to a colour
  class only *decreases* its independence number, so the sixth class merges
  into another colour for free. Rose's repo describes the same construction.
- **That colouring does not extend to K_26** — UNSAT in 0.04 s. The obvious
  route to a counterexample is dead. Scope: this refutes *that construction*,
  not the conjecture; many balanced K_25 colourings exist.

## Suggested ledger action

Retarget #617 from TARGET to **solved-upstream at r ≤ 9 (claimed, unrefereed)**
and record the encoding fence. Per this repo's standing rule a claim sets no
status by itself — but five independent artefacts, one replayed through the
Lean kernel and one reproduced by a third party, is decisive enough that
spending our compute here would be waste.

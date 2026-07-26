# Graffiti 284 — independent replay of someone else's refutation

**The refutation is not ours.** Nathan Wilbanks and Annie (AGNT Labs), in
*Graffiti 284 Refuted by Hoffman–Singleton — AGNT Labs Verification Note*
(2026-07-23, <https://agnt.gg/whitepapers/graffiti-284-refutation.html>),
identified the Hoffman–Singleton graph as a counterexample to Graffiti
conjecture 284; their mathematics holds up under every check here, and the one
narrow thing this replay adds is that **their shipped verifier hand-types both
sides of the decisive comparison, while this one computes both from the graph**
([details below](#why-this-lane-is-worth-publishing-the-decisive-comparison-is-between-two-literals)).
Finding the counterexample, and recognising that a
7-regular girth-5 graph with distance spectrum bounded below by −4 kills the
conjecture, is **their** contribution. The Hoffman–Singleton graph itself is
older still (Hoffman & Singleton 1960; the pentagon/pentagram construction is
Robertson's), and Graffiti 284 is a conjecture of Siemion Fajtlowicz's
*Graffiti* program.

**This directory contributes one thing: an independent, dependency-free,
exact-arithmetic replay that a stranger can run in one command.** No statement
below is offered as a discovery of this repository. The gap this lane closes is
between what the note *proves* and what its *script* checks — not a gap in the
mathematics.

## The conjecture

For a graph `G`, the *dual degree* of a vertex `v` is the mean degree of its
neighbours, `d*(v) = (1/deg v) · Σ_{u ~ v} deg(u)`. Writing `D(G)` for the
distance matrix, Graffiti 284 asserts:

> if `girth(G) ≥ 5` then `min_v d*(v) ≤ −λ_min(D(G))`.

A single graph with girth ≥ 5 and `min_v d*(v) > −λ_min(D(G))` refutes it. The
Hoffman–Singleton graph is such a graph: `min d* = 7`, `−λ_min(D) = 4`, and
`7 ≤ 4` is false.

## Replay

From the repository root:

```bash
python3 -I certificates/graffiti-284-refutation/verify.py
```

Pure CPython standard library — no numpy, no networkx, no sympy. ~0.2 s. Exit 0
iff every check passes, every planted control is rejected, **and** the number of
controls that actually executed equals the number the file says it contains. The
run is check-only: it writes nothing. `--emit` is the only way to rewrite
`receipt.json`, and the default path compares against the committed bytes and
exits nonzero on drift (`receipt-checked: receipt.json`). What this does *not*
cover is stated plainly in
[What this verifier cannot defend against](#what-this-verifier-cannot-defend-against).

## What is certified here

1. **The graph is built, not imported.** `verify.py` constructs 50 vertices from
   Robertson's definition — 5 pentagons `P_h` (`j ~ j±1`), 5 pentagrams `Q_i`
   (`j ~ j±2`), and `P_h[j] ~ Q_i[(h·i + j) mod 5]` — and then *earns* the name:
   `n = 50`, `m = 175`, 7-regular, connected, every adjacent pair with `0`
   common neighbours and every non-adjacent pair with exactly `1`
   (`srg(50,7,0,1)`), and **girth exactly 5 computed by BFS**, not inferred from
   the parameters.

2. **The distance matrix is exact.** Integer BFS from all 50 vertices; symmetry
   and zero diagonal checked; diameter 2 checked (every off-diagonal entry is 1
   or 2); and the integer identity `D = 2(J − I) − A` verified entrywise.

3. **`λ_min(D) = −4` exactly, with no eigensolver and no float**, by four legs
   that do not share a failure mode:
   - `(D − 91I)(D − I)(D + 4I) = 0` as an **integer** matrix. An annihilating
     polynomial confines the spectrum to its roots, so `spec(D) ⊆ {91, 1, −4}`
     and therefore `λ_min ≥ −4`.
   - an exhibited nonzero **integer** vector `v` with `D v = −4 v`, checked in
     integer arithmetic, so `−4` is actually attained and `λ_min ≤ −4`. Together
     with the previous leg this pins `λ_min(D) = −4`.
   - exact rank/nullity by fraction-free (Bareiss) elimination over `ℤ`, every
     division asserted exact: `dim ker(D − 91I) = 1`, `dim ker(D + 4I) = 28`,
     `dim ker(D − I) = 21`. These sum to 50, so the three candidates exhaust the
     spectrum with nothing left over.
   - `tr(D)`, `tr(D²)`, `tr(D³)` recomputed from the matrix and matched against
     `{91¹, (−4)²⁸, 1²¹}`.

   And then — because *hardcoding the decisive number* is the exact defect this
   lane names in someone else's file — every `λ_min` the script goes on to
   **use** must first pass `lambda_min_is_derived()`. That gate re-derives the
   minimum from the multiplicity table and demands a nonzero integer
   eigenvector for the value actually offered, so a `λ_min` that was typed
   rather than computed is *wrong*, not merely unjustified. Control 6 hands the
   gate the literal `−4` for the Petersen graph (whose distance spectrum is
   `{15, (−3)⁵, 0⁴}`) and requires it to be rejected. If the gate says no, the
   run prints **no verdict at all** for that graph rather than a sentence built
   on an underived number.

4. **The minimum dual degree is COMPUTED.** `min_dual_degree()` walks every
   vertex and forms `Fraction(Σ_{u ~ v} deg(u), deg(v))` — an exact rational, so
   a non-regular input produces an honest fraction rather than a rounded
   integer — and takes the minimum. It reads only the adjacency structure. The
   value `7` is an output, never an input. That "honest fraction" clause is
   *exercised*, not asserted: every graph in this lane except one is regular, so
   every `d*` there has denominator 1 and the exact division is
   indistinguishable from integer truncation. Control 8 adds `C₇` with a pendant
   vertex — girth 7, degrees `{1,2,3}`, `min d* = 5/3` — and fails if the
   denominator disappears.

5. **The verdict is assembled from those computed numbers**: hypothesis
   `girth 5 ≥ 5` holds, conclusion `7 ≤ 4` fails, exact integer margin `3`. The
   published numbers (`7`, `−4`, `3`) appear in the source as named constants
   that computed values are compared *against*; none of them is ever used to
   produce one.

## Why this lane is worth publishing: the decisive comparison is between two literals

The authors ship `verify_284_hoffman_singleton_exact.py` alongside the note.
That script is a **separate artifact from the prose note** — the note at
`graffiti-284-refutation.html` links to it but does not serve its text, so the
note's URL alone is not enough to check the quotations below. The file this
section quotes and criticises is pinned here by digest:

| | |
|---|---|
| URL | <https://agnt.gg/whitepapers/graffiti-284-artifacts/verify_284_hoffman_singleton_exact.py> |
| sha256 | `7d58813fa2b9f151eb4ac39dc342244503772702fc75c24f4052eed7653c97f2` |
| size | 3380 bytes |
| read | 2026-07-25 |

That digest is what we computed from the bytes we downloaded, and it agrees
with the authors' own published `SHA256SUMS.txt` in the same directory. Anyone
can refetch and rehash; if the file is later edited, the hash stops matching
and this criticism should be re-checked against the new version rather than
trusted.

**First, what it genuinely checks — this is real work and it deserves credit.**
In exact `int64` arithmetic, that file verifies:

| lines | checked |
|---|---|
| 38–39 | the strongly-regular identity `A@A + A − 6I == J`, entrywise |
| 43–44 | `tr(A) = 0` and `tr(A²) = 2m = 350` |
| 48 | the real eigenvalue-multiplicity system — `7 + 2a − 3b == 0`, `a + b == 49`, `49 + 4a + 9b == 350` — which does fire |
| 57–59 | every off-diagonal distance is in `{1, 2}`, and `D == 2(J − I) − A` |

Its one floating-point call, an eigensolver at lines 64–66, is explicitly fenced
in the source as a `# float sanity cross-check only (not part of the proof)`.
That is honest fencing, and we describe it as such: it is not part of what the
script claims to prove, and we do not count it against the file.

**Now the defect, stated precisely.** Two things, and they compound:

1. **`λ_min(D) = −4` is never asserted anywhere.** Lines 61–62 are `print`
   statements. The entire right-hand side of the conjecture — the number the
   refutation turns on — is human reasoning rendered as output text, with no
   assertion behind it.
2. **Both compared numbers are hand-typed literals.** Verbatim, lines 69–70:

```python
min_dual = 7  # every neighbor of every vertex has degree 7
rhs = 4       # -lambda_min(D)
```

Neither line reads the graph. `min_dual` is never derived from any degree
computation, and `rhs` is never derived from any spectral computation — the
derivation of both exists, correctly, in the file's prose, but the machine does
not perform it. Consequently its decisive comparison, `min_dual > rhs`, is
`7 > 4` **for every input it could ever be handed**. The script certifies
everything *except* the inequality it exists to refute.

This is not a hypothetical. `verify.py` ships that exact logic as a planted
control (`paper_style_hardcoded_verdict`) and hands it the **Petersen graph**,
which has girth 5 and *satisfies* Graffiti 284 (computed here: `min d* = 3`,
`λ_min(D) = −3`, so `3 ≤ 3` holds). The hardcoded verdict returns **REFUTED**.
A checker that returns "refuted" for a graph that does not refute anything has
not checked the graph.

One smaller observation about the same file, pointing the same direction: it
takes its graph from `networkx.hoffman_singleton_graph()` rather than
constructing it, so the object under test is a library constant rather than
something the script earns. (For completeness, since a reader who opens the file
will see it: line 47's `assert … or True` is vacuous — but line 48 immediately
performs the same multiplicity check for real, so it is a leftover line, not a
hole, and nothing rests on it.)

**The mathematics of the note holds up.** Every number it asserts is one this
lane independently recomputes and confirms. The gap is between what the note
*proves* and what its *script* checks, and it is exactly the gap this repository
exists to close.

**We hold ourselves to the same rule.** The criticism above would be worthless
if this lane carried the same defect, so `λ_min` here is not merely "computed
somewhere" — every value of it that reaches a verdict goes through
`lambda_min_is_derived()` first, and control 6 plants the literal `−4` and
requires the gate to reject it. Replacing the derivation in
`graffiti_284_report()` with `lam_min = -4` drives this run to **exit 1**.

## Independent corroboration that 284 was open, and not trivially searchable

Roucairol & Cazenave, *Refutation of Spectral Graph Theory Conjectures with
Search Algorithms* (arXiv:2409.18626v1, 27 Sep 2024), ran an automated
counterexample hunt across a batch of Graffiti conjectures. Their results table
(Table 1) lists conjecture 284 with status **O** — which they gloss as "open to
be proved or refuted" — searched over graphs of **girth ≥ 5** built **up to
size 50**, with a dash in all eight algorithm columns (NMCS, LNMCS, NRPA, UCT,
GBFS, BEAM, GRAVE, RAVE): no counterexample found by any configuration. The
Hoffman–Singleton graph has exactly 50 vertices and girth 5, so it sits
precisely at the ceiling of that search and inside its constraint class.

This is independent evidence, from a source with no stake in the present
refutation, that 284 was still open as of September 2024 and that the
counterexample is not something generic search hands you. It is *not* evidence
that the object is hard to reach in principle: the same paper records a budget
of 15 minutes per algorithm per conjecture on a single core of an Intel
i5-6600K, which is a modest budget against the space of girth-5 graphs on up to
50 vertices. The honest reading is that a targeted 2024 campaign, correctly
scoped and correctly constrained, ran out of budget before it reached an object
that a human identified directly — not that the object was out of reach.

## Planted-failure controls

Eight, all printed as `[ok] rejected: …`. Exit is nonzero if any is *not*
rejected:

| # | Control | Must be rejected because |
|---|---|---|
| 1 | `K₃,₃` offered as a counterexample | `min d* = 3 > 2 = −λ_min(D)`, so the *conclusion* fails — but girth is 4, so the hypothesis does not hold. A checker that skipped the girth gate would accept it. |
| 2–3 | claimed `λ_min(D) = −3`, `λ_min(D) = −5` | `dim ker(D − λI) = 0` and the annihilator with that root is a nonzero matrix. |
| 4 | Hoffman–Singleton with one 2-swap | Still 7-regular with `m = 175`, so a degree count passes it; the `srg(50,7,0,1)` identity does not. |
| 5 | hardcoded `(min_dual=7, rhs=4)` applied to Petersen | The hardcode says REFUTED; the computed pipeline says `3 ≤ 3` holds. This is the headline control. |
| 6 | `λ_min` asserted as the literal `−4` on Petersen | The same defect aimed at us. Petersen's distance spectrum is `{15, (−3)⁵, 0⁴}`, so `−4` is not an eigenvalue of it at all; `lambda_min_is_derived()` must reject the literal and accept the derived `−3`. |
| 7 | perturbed integer eigenvector for `−4` | `D v ≠ −4 v` once one coordinate moves. |
| 8 | integer-truncated dual degree on a non-regular graph | `C₇` + pendant has girth 7 and `min d* = 5/3`; replacing `Fraction(a, b)` with `Fraction(a // b)` reports `1` and the denominator vanishes. Without this input every graph in the lane is regular and the exact division is untested. |

The count is **measured, not typed.** `verify.py` records every `rejected()` call
as it happens, compares the number that actually executed against
`EXPECTED_CONTROLS`, and publishes the measured `controls_run` /
`controls_rejected` in `receipt.json`. Deleting a control block therefore fails
the count check *and* drifts the receipt, instead of silently leaving a stale
total in place.

**Three controls were removed from this table, and the count was corrected from
nine to six before two new ones were added.** An earlier revision also scored
`[ok] rejected` for the assertions `min d* ∈ {6, 8, 3}` on Hoffman–Singleton.
Each of those evaluated
`Fraction(literal) != md` against the *already-computed* `md` — two constants
compared to each other, wired to nothing. Under the single mutation this whole
lane exists to catch (`min_dual_degree()` stubbed to return the literal `7`)
all three still printed `[ok] rejected`; only control 5 fired. A control that
survives the mutation it purports to detect is not a control, and counting it
inflates the score, so they were deleted rather than relabelled. This
paragraph stays because a public correction should be legible, not silent.

### Measured mutation battery

The controls were adversarially checked rather than assumed. Each row below is a
single-line edit to `verify.py`, applied to a clean copy of the repository and
re-run; the exit code is what the run actually produced. These are **data**
mutations wearing source-mutation clothing — each one makes a number this lane
publishes wrong, and each is caught:

| Mutation | Exit | Caught by |
|---|---|---|
| cross-edge rule `(h·i + j)` → `(h + i + j)` | 1 | `mu=1` fails, `observed=[0, 1, 5]` |
| pentagram `j ~ j±2` rewired as a pentagon `j ~ j±1` | 1 | `mu=1` fails, `observed=[0, 1, 2]` |
| eigenvalue candidate `−4` → `−3` | 1 | annihilating polynomial is not the zero matrix |
| `min_dual_degree()` replaced by the literal `Fraction(7)` | 1 | control 5 stops rejecting: the Petersen graph now reads `min d* = 7` |
| girth hypothesis forced to `True` | 1 | control 1 stops rejecting `K₃,₃` |
| `girth()` stubbed to `return 5` | 1 | control 1 stops rejecting `K₃,₃` |
| `rank_exact()` off by one | 1 | `dim ker(D − 91I) = 1` fails, got 0 |
| `is_zero()` stubbed to `return True` | 1 | controls 2–3 stop rejecting the wrong eigenvalues |
| `lam_min = min(…)` → `lam_min = -4` in `graffiti_284_report()` | 1 | the derivation gate: `offered lambda_min=-4, but the least eigenvalue with nonzero multiplicity is -2` |
| the same, written as `lam_min = CLAIM_LAMBDA_MIN` | 1 | same gate |
| `lambda_min_is_derived()` stubbed to `return True` | 1 | control 6 stops rejecting the planted literal |
| `Fraction(a, b)` → `Fraction(a // b)` in `min_dual_degree()` | 1 | control 8: `min d*` on the non-regular graph reads `1` instead of `5/3` |
| a whole control block deleted | 1 | `planted controls: 8 expected … executed=7`, plus receipt drift |
| one poisoned field in `receipt.json` | 1 | `drifting fields: ['distance_spectrum']` |

Thirteen source mutations plus one poisoned receipt field; all fourteen exit 1.
Note the shape of several rows: mutating the *computation* does not break a
green check, it breaks a **control**. That is the intended wiring — the controls
are what notice when the checker stops checking.

**And what was measured NOT to fail**, because a battery that only reports its
wins is advertising: rewriting either of the two claim comparisons as a
tautology (`margin == CLAIM_MARGIN` → `3 == 3`, `md == CLAIM_MIN_DUAL` →
`md == md`) leaves the run green, and so does no-oping `FAILURES.append(...)` on
an otherwise-clean tree. The first two are checks deleted by hand; the third is
a no-op when nothing failed, and stops being one the moment anything does
(composed with the `min_dual_degree` literal above, it exits 1). All three are
edits to the verifier, not to the data — see the next section.

## What this verifier cannot defend against

Everything in the table above is, at bottom, a **data** defect: a wrong graph, a
wrong matrix, a wrong eigenvalue, a wrong dual degree, a poisoned receipt.
Those are what `verify.py` is built to catch, and it catches them.

It cannot defend against a corrupted **verifier** — against edits to
`verify.py` itself. No verifier can. Stub a function, no-op an accumulator,
delete a check, hardcode a constant in the verdict path, and what remains is
simply a different program that prints `PASS`. We say this plainly rather than
claim otherwise, and two consequences are worth being explicit about:

- **A deleted check is a deleted check.** Rewriting
  `check("… margin …", margin == CLAIM_MARGIN)` as `check("… margin …", 3 == 3)`
  leaves the run green. The published margin is still recomputed and still
  compared against the committed receipt, so a *wrong* margin is caught — but
  the check itself is gone and nothing in this file notices.
- **Disarming the accumulator is not enough, but only because we made it so.**
  `rejected()` records each control's result at call time, and the exit gate
  recomputes the verdict from those records rather than trusting the
  `FAILURES.append(...)` side effect, then cross-checks the two accountings
  against each other. Replacing that `append` with `pass` no longer disarms the
  controls: composed with this lane's own headline mutant it still exits 1.
  On an otherwise-clean tree that same edit is a no-op and the run correctly
  exits 0 — nothing failed, so there was nothing to suppress. This raises the
  number of coordinated edits an attacker needs. It does not make the file
  self-defending.

The defenses that actually cover this threat live outside the file:

- `certificates/contracts.json` pins the **sha256 of `verify.py` and of
  `receipt.json`**; `tools/check_certificate_contracts.py` fails if either
  byte-string moves. Any of the edits above changes that digest.
- The same contract pins the decisive stdout lines and forbids the string
  `[FAIL]` anywhere in the output, so a run that prints a failure and exits 0
  still fails the gate.
- **Git history and review.** The edit is in the diff.

If you are checking this lane, read the diff of `verify.py` against its pinned
digest — not only the output it prints.

## not_certified_here

- **Novelty and priority.** Whether Wilbanks & Annie were first to observe
  that Hoffman–Singleton refutes 284 is a provenance question, unchecked here.
  This lane does not adjudicate credit; it only replays the mathematics and
  attributes it to them.
- **The authors' own artifacts.** Their scripts, their outputs and their
  claim-ledger are neither re-executed nor mirrored here. The `min_dual = 7` /
  `rhs = 4` lines above are quoted from
  `graffiti-284-artifacts/verify_284_hoffman_singleton_exact.py` (sha256
  `7d58813f…c97f2`, 3380 bytes, read 2026-07-25 — full URL in the table above),
  which is a **different artifact from the `…/graffiti-284-refutation.html`
  note**; they are quoted, not run. We did recompute that one digest and found
  it equal to the entry in the authors' published `SHA256SUMS.txt`; no other
  line of that checksum file was verified, and nothing in it was replayed.
- **That "284" is the right index, or that the statement is transcribed
  faithfully.** This lane verifies that *the statement as given* — `girth ≥ 5 ⇒
  min dual degree ≤ −λ_min(D)` — is false. It does **not** check that assertion
  against Fajtlowicz's original *Graffiti* conjecture list. If the transcription
  or numbering is wrong, this lane still certifies a false statement is false,
  but the label on it would be someone else's error to correct.
- **That the constructed graph "is" the Hoffman–Singleton graph.** What is
  checked is `srg(50,7,0,1)` with girth 5. That these parameters determine the
  graph up to isomorphism is a classical uniqueness theorem (Hoffman & Singleton
  1960) which is **cited, not proved here** — and not needed: the refutation
  depends only on the properties of the object actually built.
- **Anything about Graffiti 284 beyond the falsity of its universal
  statement.** No repaired conjecture, no characterisation of which girth-5
  graphs satisfy it, no claim about neighbouring Graffiti conjectures (290, 292,
  or any other) — those are separate results with separate evidence, and none of
  it is in this directory.
- **The other legs of the authors' note.** Only the 284 claim is replayed.
- **The Roucairol & Cazenave search campaign.** Their Table 1 row for 284 is
  *read*, not reproduced: none of their eight search algorithms was re-run
  here, and this lane makes no claim about whether their search was exhaustive
  over any class. It is cited as third-party evidence of the conjecture's
  status in Sept 2024, nothing more.

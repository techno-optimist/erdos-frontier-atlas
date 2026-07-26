# Graffiti 284 — independent replay of someone else's refutation

**The refutation is not ours.** Nathan Wilbanks and "Annie" (AGNT Labs), in
*Graffiti 284 Refuted by Hoffman–Singleton — AGNT Labs Verification Note*
(2026-07-23, <https://agnt.gg/whitepapers/graffiti-284-refutation.html>),
identified the Hoffman–Singleton graph as a counterexample to Graffiti
conjecture 284. Finding the counterexample, and recognising that a
7-regular girth-5 graph with distance spectrum bounded below by −4 kills the
conjecture, is **their** contribution. The Hoffman–Singleton graph itself is
older still (Hoffman & Singleton 1960; the pentagon/pentagram construction is
Robertson's), and Graffiti 284 is a conjecture of Siemion Fajtlowicz's
*Graffiti* program.

**This directory contributes one thing: an independent, dependency-free,
exact-arithmetic replay that a stranger can run in one command.** No statement
below is offered as a discovery of this repository.

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
iff every check passes **and** every planted control is rejected. The run is
check-only: it writes nothing. `--emit` is the only way to rewrite
`receipt.json`, and the default path compares against the committed bytes and
exits nonzero on drift (`receipt-checked: receipt.json`).

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

4. **The minimum dual degree is COMPUTED.** `min_dual_degree()` walks every
   vertex and forms `Fraction(Σ_{u ~ v} deg(u), deg(v))` — an exact rational, so
   a non-regular input would produce an honest fraction rather than a rounded
   integer — and takes the minimum. It reads only the adjacency structure. The
   value `7` is an output, never an input.

5. **The verdict is assembled from those computed numbers**: hypothesis
   `girth 5 ≥ 5` holds, conclusion `7 ≤ 4` fails, exact integer margin `3`.

## Why this lane is worth publishing: the authors' verifier never computes the number

The authors ship `verify_284_hoffman_singleton_exact.py` alongside the note. It
is careful work in most respects — it checks the strongly-regular identity
`A² + A − 6I = J` and the distance identity `D = 2(J − I) − A` over the integers,
and it explicitly quarantines its one floating-point call as a
"float sanity cross-check only (not part of the proof)". But the two numbers
that *are* the refutation are literals. Verbatim from that file:

```python
min_dual = 7  # every neighbor of every vertex has degree 7
rhs = 4       # -lambda_min(D)
```

Neither line reads the graph. `min_dual` is never derived from any degree
computation, and `rhs` is never derived from any spectral computation — the
derivation of both exists, correctly, in the file's prose docstring, but the
machine does not perform it. Consequently that script's decisive comparison,
`min_dual > rhs`, is `7 > 4` **for every input it could ever be handed**.

This is not a hypothetical. `verify.py` ships that exact logic as a planted
control (`paper_style_hardcoded_verdict`) and hands it the **Petersen graph**,
which has girth 5 and *satisfies* Graffiti 284 (computed here: `min d* = 3`,
`λ_min(D) = −3`, so `3 ≤ 3` holds). The hardcoded verdict returns **REFUTED**.
A checker that returns "refuted" for a graph that does not refute anything has
not checked the graph.

Two smaller observations about the same file, recorded because they point the
same direction: it takes its graph from `networkx.hoffman_singleton_graph()`
rather than constructing it, so the object under test is a library constant;
and its line `assert 49 + 4*a_ + 9*b_ == 350 - 0*49 or True` can never fail —
the trailing `or True` makes the assertion vacuous. (The following line does
carry out the real multiplicity check, so nothing downstream is wrong; the
pattern is what is worth naming.)

**The mathematics of the note holds up.** Every number it asserts is one this
lane independently recomputes and confirms. The gap is between what the note
*proves* and what its *script* checks, and it is exactly the gap this repository
exists to close.

## Planted-failure controls

Nine, all printed as `[ok] rejected: …`. Exit is nonzero if any is *not*
rejected:

| # | Control | Must be rejected because |
|---|---|---|
| 1 | `K₃,₃` offered as a counterexample | `min d* = 3 > 2 = −λ_min(D)`, so the *conclusion* fails — but girth is 4, so the hypothesis does not hold. A checker that skipped the girth gate would accept it. |
| 2–3 | claimed `λ_min(D) = −3`, `λ_min(D) = −5` | `dim ker(D − λI) = 0` and the annihilator with that root is a nonzero matrix. |
| 4 | Hoffman–Singleton with one 2-swap | Still 7-regular with `m = 175`, so a degree count passes it; the `srg(50,7,0,1)` identity does not. |
| 5 | hardcoded `(min_dual=7, rhs=4)` applied to Petersen | The hardcode says REFUTED; the computed pipeline says `3 ≤ 3` holds. This is the headline control. |
| 6–8 | asserting `min d* ∈ {6, 8, 3}` on Hoffman–Singleton | Disagrees with the computed `7`. |
| 9 | perturbed integer eigenvector for `−4` | `D v ≠ −4 v` once one coordinate moves. |

The controls were themselves adversarially checked rather than assumed. Eight
independent source mutations each drive the run to exit 1:

| Mutation | Caught by |
|---|---|
| cross-edge rule `(h·i + j)` → `(h + i + j)` | `mu=1` fails, `observed=[0, 1, 5]` |
| pentagram `j ~ j±2` rewired as a pentagon `j ~ j±1` | `mu=1` fails, `observed=[0, 1, 2]` |
| eigenvalue candidate `−4` → `−3` | annihilating polynomial is not the zero matrix |
| `min_dual_degree()` replaced by the literal `Fraction(7)` | control 5 stops rejecting: the Petersen graph now reads `min d* = 7` |
| girth hypothesis forced to `True` | control 1 stops rejecting `K₃,₃` |
| `girth()` stubbed to `return 5` | control 1 stops rejecting `K₃,₃` |
| `rank_exact()` off by one | `dim ker(D − 91I) = 1` fails, got 2 |
| `is_zero()` stubbed to `return True` | controls 2–3 stop rejecting the wrong eigenvalues |

A single poisoned field in `receipt.json` likewise produces
`drifting fields: [...]` and exit 1.

Note the shape of rows 4–6 and 8: mutating the *computation* does not break a
green check, it breaks a **control**. That is the intended wiring — the controls
are what notice when the checker stops checking.

## not_certified_here

- **Novelty and priority.** Whether Wilbanks & "Annie" were first to observe
  that Hoffman–Singleton refutes 284 is a provenance question, unchecked here.
  This lane does not adjudicate credit; it only replays the mathematics and
  attributes it to them.
- **The authors' own artifacts.** Their scripts, their outputs, their SHA256SUMS
  and claim-ledger are neither re-executed nor mirrored here. The `min_dual = 7`
  / `rhs = 4` lines above are quoted from the file published at the URL cited
  above, as read on 2026-07-25; they are quoted, not run.
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

# Graffiti 290 — independent replay of someone else's result

**Whose result this is.** The conjecture is **Graffiti's** (S. Fajtlowicz), conjecture **290**,
recorded in *Written on the Wall*, p. 79. The **proof** is **Nathan Wilbanks and "Annie" (AGNT
Labs)**, *A Proof of Graffiti 290*. Neither the conjecture nor the proof is a result of this
repository. Everything in this directory is **only an independent finite verification** of the
inequality they assert, together with an explicit statement of what that verification leaves
untouched. We did not prove Graffiti 290 and do not claim to have.

**Which convention — and both halves of it, in the first paragraph.** The truth value of Graffiti 290
depends on which definition of "gravity" you use, and the honest statement has **two** parts. Naming
only the first is unfair to the author; naming only the second hides a refutation any reader finds in
one search. So:

- **(a) A live refutation exists** under the gravity definition in **Aouchiche and Hansen's survey**.
  Roucairol and Cazenave report that under it Graffiti 290 "was solved instantly" — i.e. **refuted**.
- **(b) The very authors who found that refutation disavow that definition.** In the same section
  they call the *Written on the Wall* / Brewster et al. definition **"the correct definition"** — the
  survey's is, on their reading, a misstatement — and they report that refutation was "seemingly
  impossible" under the correct one. That correct definition is the one **this theorem is stated
  over**, and the one certified here.

**We did not obtain the Aouchiche–Hansen definition and did not replay that refutation.** We also do
not adjudicate Roucairol–Cazenave's judgement that the survey misstates the definition; we report it.

The convention certified here, transcribed by Roucairol–Cazenave from *Written on the Wall* p. 52 and
Brewster et al.: the gravity matrix entry `Gr(u,v)` is `0` when `u = v` **or when no path joins `u`
to `v`**, and otherwise

```
Gr(u,v) = (1 / (n - 1)) · d(u) · d(v) / d(u,v)
```

with `d(u)` the degree of `u`, `d(u,v)` the distance, `n` the order.

**The verifier's `gravity_matrix` was checked against that transcription, not assumed to match it.**
Check 1b compares it entry by entry with hand-computed matrices on the path `P₃`, on `K₂ ⊔ K₁` and on
`2K₂` — the last two **disconnected**, because the zero-for-no-path clause is exactly the clause a
connected-only reading would quietly drop — and separately confirms the `1/(n−1)` factor is present
and exact on Petersen (`Gr(0,1) = 3·3/(9·2) = 1/2`). Diagonal zero and no-path zero are asserted as
their own conditions, not inferred from the totals matching.

Sources for this paragraph are cited exactly in [Sources](#sources) below: Aouchiche–Hansen 2010 [1],
Brewster–Dinneen–Faber 1995 [2], and Roucairol–Cazenave arXiv:2409.18626 §5.2.

## The statement, and the two readings of it

Graffiti 290 reads: *if girth ≥ 5 then the second smallest adjacency eigenvalue ≤ size / mean
gravity.* Writing `λ₁ ≥ … ≥ λₙ` for the adjacency spectrum, `m` for the size and `Ḡr` for the mean
gravity, that admits two readings, and **the paper proves the stronger one**:

| | inequality | status here |
|---|---|---|
| literal Written-on-the-Wall reading | `λₙ₋₁ ≤ m / Ḡr` | verified |
| the paper's reading | `−λₙ₋₁ ≤ m / Ḡr` | verified (stronger; implies the other whenever `λₙ₋₁ ≤ 0`) |

Both are checked, on every instance, so the certificate does not depend on resolving the sign
ambiguity.

## Two things the paper adds silently, and what we found

1. **Connectivity.** The paper assumes the graph is connected. *Written on the Wall* p. 79 does not
   state that hypothesis, and the gravity definition explicitly covers the disconnected case
   (`Gr(u,v) = 0` when no path joins `u` to `v`). Our enumeration therefore includes disconnected
   graphs: **678 of the 1360 instances checked are disconnected, and every one of them satisfies the
   inequality.** In this range the connectivity hypothesis is not needed.
2. **"Mean gravity" is never defined.** *Written on the Wall* defines the gravity *matrix* but not
   its mean. The paper fixes it as the mean over all `n²` entries. We verify under **that**
   convention **and** under the alternative mean over the `n(n−1)` off-diagonal entries; the
   inequality survives both, in both readings.

## What is certified

Exhaustively, with exact integer/`Fraction` arithmetic only:

- **every graph of girth ≥ 5 on `n ≤ 10` vertices, up to isomorphism** — connected and disconnected —
  `1, 2, 3, 6, 11, 23, 48, 114, 293, 869` classes for `n = 1..10`. Of these, **1360 have at least one
  edge and are checked**; the 9 edgeless graphs are excluded because their mean gravity is `0` and
  `m/Ḡr` is `0/0`, undefined.
- **21 larger instances**, each with its order, size, girth and degree set re-derived rather than
  asserted: Petersen, Heawood (Fano incidence), the `PG(2,3)` incidence graph, the odd graph
  `O₄ = Kneser K(7,3)`, the **Hoffman–Singleton graph on 50 vertices**, eight cycles up to `C₄₀`, and
  eight reproducible pseudo-random maximal girth-5 graphs on 16–40 vertices.
- **the paper's own two worked examples**, reproduced as exact rationals:
  Petersen `2 ≤ 25` (margin `23`), Hoffman–Singleton `3 ≤ 625/2` (margin `619/2 = 309.5`).

**The bound is nowhere near tight.** Over the whole `n ≤ 10` family the ratio `(m/Ḡr) : (−λₙ₋₁)` is
never below `40960/7953 ≈ 5.15` (attained at `C₅`) and the additive margin never below
`201561/31744 ≈ 6.35`; on Hoffman–Singleton the bound is loose by a factor of about **104** —
`3 ≤ 312.5`. Whatever Graffiti 290 is, it is not a sharp inequality. (Both figures are certified
*lower* bounds on the true tightness: `−λₙ₋₁` is replaced by a rational upper bound from its
bracket.)

### Exactness

No float enters a decision anywhere. Eigenvalues are never computed numerically. The question "how
many eigenvalues of `A` lie strictly below the rational `t`" is answered by the **inertia of the
integer matrix `q·A − p·I`** (where `t = p/q` in lowest terms, `q > 0`) under exact symmetric
congruence — Sylvester's law of inertia — which counts **with multiplicity**, unlike a square-free
Sturm chain. Irrational eigenvalues (e.g. `C₅`) are pinned by exact rational brackets whose endpoints
are shown to straddle the relevant algebraic root. Decimals appear in the printout for reading only.

### The generator is cross-checked

Enumerating "every graph of girth ≥ 5 up to isomorphism" is the step where a silent bug would produce
a confident, empty pass. So the canonical-augmentation generator is checked against a **structurally
independent** enumeration: for `n ≤ 7`, `Σ n!/|Aut(G)|` over the generated isomorphism classes must
equal the count of **labelled** girth-≥5 graphs produced by a separate DFS over the `C(n,2)` edge
slots. It does. A generator that dropped or duplicated a class would fail this.

## What pins the verdict

A verifier whose central check can be stubbed **without any shipped artifact changing** is not a
verifier — it is a transcript. This lane has had that defect twice, and both times it was found by
mutation testing rather than by reasoning.

**Round 1.** Replacing the body of `holds_paper` with `return True` exited `0` with a byte-identical
transcript and a byte-identical `certificate.json`, because everything the receipt recorded was
computed from `rhs()` and `lambda2_bracket()` *beside* the verdict functions rather than *from* them.
The fix was to make the functions return a record `(holds, count, r)` and hash it.

**Round 2 — and this is the one worth reading.** That fix was not enough, and the claim made for it
("the exact rational `r` … makes the digest discriminating") was **wrong**. Mutant `mutD` replaced
both verdict bodies with

```python
r = rhs(n, adj, over)
if r is None: return None
return (True, 0, r)
```

and passed. Byte-identical transcript, byte-identical `certificate.json`, all sixteen controls
rejected, exit `0`. It works because `rhs()` is a gravity/degree/distance computation that **anyone
can call without touching the spectrum**, and because on this corpus the honest `count` is `0` on
every single graph — so a fabricated `0` is not an approximation of the truth, it *is* the truth.
The digest therefore had **zero entropy from the eigenvalue engine**. Worse: `mutD` has no input on
which it can answer `False`. A real counterexample anywhere in the 1360-graph corpus would have been
reported as a pass. That is a certificate that cannot fail, which is exactly the thing this lane
exists to refute.

Two things changed in response.

**(1) A spectral field in the record.** `holds_paper` and `holds_literal` now return

| field | meaning | reachable without an eigenvalue? |
|---|---|---|
| `holds` | the answer, which is exactly `count ≤ 1` | yes — one bit |
| `count` | the exact eigenvalue count the answer is decided on | **yes in practice** — it is `0` on all 1360 graphs |
| `r` | the exact `m/Ḡr` the answer was decided against | **yes** — `rhs()` needs no spectrum |
| `spectrum` | `(#λ < 0, mult of 0)` for `A` itself — the inertia index | **no** |

The inertia index takes the values `1,2,3,4,5` across the corpus with multiplicities
`45/140/346/600/229`. It is a function of nothing but the spectrum, and the only way to produce it is
to run the exact congruence. It is **not part of the inequality** — it is the entropy the
inequality's own verdict does not carry here, carried alongside it, so that the digest depends on
spectral work having been done. `certificate.json` pins
`corpus.verdict_digest_sha256` over all **2720** returned records (1360 graphs × 2 mean conventions),
and each of the 21 battery rows carries its own `adjacency_inertia_neg_zero`.

**(2) A control that requires the verdict path to answer `False`.** Control 19 feeds `holds_paper`
Petersen under this file's own planted-wrong gravity convention — the instance control 11
independently certifies as a genuine violation — and requires the record to come back
`(False, 4, 5/3, (4,0))`. A verdict function that cannot produce `False` on that input fails the run.

Both fixes were verified by re-running the mutants; the measured table is below.

## Planted-failure controls — 19 of them

A checker that cannot fail certifies nothing, so the run prints `[ok] rejected:` lines. **The count
is asserted, not merely printed:** `EXPECTED_CONTROLS = 19` is compared against the number actually
rejected, and the pair is recorded in `certificate.json` under `planted_failure_controls`. Deleting a
control block leaves the run at exit `1`.

| # | planted corruption | why it must be caught |
|---|---|---|
| 1 | "Petersen has at most one eigenvalue below `−19/10`" | it has 4; the exact counter says so |
| 2 | "Hoffman–Singleton has `(−3)²²`" | the exact multiplicity is 21 |
| 3–6 | `C₄`, `K₃,₃`, `Q₃`, `K₄` offered as girth-≥5 instances | measured girth is 4, 4, 4, 3 |
| 7 | the enumeration re-run with the girth filter **disabled** | counts move to `1,2,4,11,34,156` — the filter is not inert |
| 8 | Hoffman–Singleton with one edge deleted | degree set becomes `[6,7]`, not `[7]` |
| 9 | Hoffman–Singleton with one edge added | girth collapses to 3 |
| 10 | an asymmetric adjacency list | rejected as not a graph |
| 11 | a **mutated gravity convention** (edge-mean, `1/(n−1)` dropped) | gives `m/Ḡr = 5/3 < 2` on Petersen — the inequality genuinely breaks |
| 12 | mean gravity inflated 20× | `m/Ḡr = 5/4 < 2` on Petersen |
| 13 | the **flipped** inequality `m/Ḡr ≤ −λₙ₋₁` | `25 ≤ 2` is false |
| 14 | a verdict function **stubbed to `return True`** | it is not a verdict record; the shape check says so |
| 15 | a verdict record with a **fabricated eigenvalue count** (`(True, 1, r, spec)`) | right shape, right answer — the digest moves anyway |
| 16 | a verdict record with a **fabricated `m/Ḡr`** (`(True, count, r+1, spec)`) | the two readings then disagree about what they were decided against |
| 17 | **`mutD` itself** — `(True, 0, rhs(...))`, no spectral work anywhere | the record has no spectral field; the stream refuses to build |
| 18 | `mutD` sharpened — same, plus a **fabricated** inertia index `(1,0)`, applied to both readings so every structural cross-check passes | **only the digest can catch this**, and it does |
| 19 | a genuinely **failing** instance: Petersen under the mutated gravity convention | `holds_paper` must return `False` with count `4`. This is the control that says the verdict path can fail at all |

Control 11 is **our own deliberate corruption**, planted so the convention-sensitivity of the
statement is demonstrated rather than asserted. **It is not Aouchiche and Hansen's definition** — we
do not have that definition and make no claim about what it is.

### Mutants, measured

Every row below was executed. "survives" means exit `0` with a transcript **and** a
`certificate.json` byte-identical to the clean run — the honest definition, not a weaker one.

| mutation | result | caught by |
|---|---|---|
| body of `holds_paper` → `return True` | dies | verdict-record shape check, ~25 `[FAIL]` lines |
| `mutD`: **both** bodies → `(True, 0, rhs(...))` | **dies** (survived before this round) | shape check — the record has no spectral field |
| `mutD2`: `holds_paper` only → `(True, 0, rhs(...))` | **dies** (survived before this round) | same |
| `mutD3`: both bodies → `(True, 0, rhs(...), spectral_index(...))` — real spectral work, fabricated count, **still always `True`** | **dies** | control 19: it returns `True` on the planted failing instance |
| `spectral_index` stubbed to the constant `(1, 0)` | **dies** | control 18 notices the digest stops moving |
| the literal reading dropped from the girth-<5 sweep (`holds_literal` → `holds_paper`) | **dies** | the sweep digest, then the receipt comparison |
| `check_convention_controls()` deleted from `main()` | dies | `16 … rejected, but exactly 19 must run` |
| one integer edited in `certificate.json` | dies | `.corpus.graphs_checked: 1360 vs stored 1361` |
| **the girth-<5 sweep's `violations_literal` counter fed `vp[0]` instead of `vl[0]`** | **SURVIVES** | nothing — see below |

**The surviving mutant is disclosed, not hidden.** Both violation counters in the girth-`<5` sweep
are `0` across the whole range, so a counter is a constant, and swapping which reading feeds it
changes nothing observable. No test can distinguish two constants that are equal. That is why the
sweep also ships `girth_lt5_sweep_digest_sha256`, a hash over **both** readings' returned records:
that digest is what makes the literal reading load-bearing in the sweep, and dropping the reading
does kill the run (row 6 above). The counters are reported because a reader wants the number; they
are not evidence on their own, and this README no longer implies they are.

## What this verifier cannot defend against

Every one of the 19 controls corrupts an **input**. None of them defends against a corrupted
**verifier**.

If someone edits `verify.py` itself — stubs a function to a constant, no-ops the `FAILURES`
accumulator so `bad()` stops recording, deletes a check from `main()` without touching the control
count, or hardcodes the verdict — **this file cannot detect it, and no file can**. A program cannot
certify its own source; the mutation results above are measured against an *unmodified* `verify.py`,
and a mutation that survives *because it edited `verify.py`* is not a bug in the technique, it is the
boundary of the technique.

What holds that boundary is outside the file, and it is deliberately boring:

- **`certificates/contracts.json` pins the SHA-256 of `verify.py` and of `certificate.json`.** The
  repository gate `python3 tools/check_certificate_contracts.py` fails if either byte-string moves.
  Any verifier-side edit — including every mutant in the table above — changes that hash.
- **`git log -p certificates/graffiti-290/verify.py`** shows every change to the verifier, next to
  the receipt change it caused.
- **Review.** Someone reads the diff.

So: the controls are evidence about the *data*; the pinned hash and the history are evidence about
the *code*. They are different defenses and neither substitutes for the other. Anyone who tells you a
verifier is self-protecting against edits to itself is selling something.

## Replay

```bash
cd certificates/graffiti-290
python3 -I verify.py
```

Pure stdlib, no third-party imports, no network. Runtime ≈ 90 s single-threaded, dominated by the
`n = 10` canonical augmentation. Exit `0` iff every check passes, all 19 controls are rejected, the
control count matches `EXPECTED_CONTROLS`, and the recomputed receipt — verdict digest included —
matches the committed one field for field.

The claim this replay certifies, stated once, in full:

> **Graffiti 290 holds, under the Written-on-the-Wall / Brewster gravity convention, on every
> girth ≥ 5 graph of order ≤ 10 (all 1360 with at least one edge, connected and disconnected) and on
> 21 larger instances up to Hoffman–Singleton.**

Nothing beyond that sentence is certified here — see [not_certified_here](#not_certified_here).

**Check-only by default.** A normal run **does not write** `certificate.json`; it recomputes the
receipt, compares field by field, prints `receipt-checked: certificate.json`, and exits nonzero on
any mismatch. `--emit` is the only path that writes, and it says so in its output.

## Cutoff, stated honestly

`n ≤ 10` is a **compute** cutoff, not a mathematical one. The canonical augmentation costs ≈ 54 s at
`n = 10`; `n = 11` (2963 classes) measured ≈ 594 s in the same implementation and was left out to
keep the replay under a couple of minutes. Nothing about the problem changes at `n = 11`.

## not_certified_here

- **Novelty and priority of the paper are not assessed.** This certificate says nothing about whether
  the proof is new, correct as a proof, or first.
- **The paper's proof is NOT replayed.** Its three lemmas, the trace identity step, the Reiman
  `C₄`-free edge bound, the quartic-positivity argument for `n ≥ 7` — none of it is checked here.
  A finite verification of an inequality is not a verification of a proof of that inequality, and the
  two must not be confused. It remains entirely possible for the statement to be true on our range
  and for the argument to be broken.
- **The Aouchiche–Hansen reading is not certified, in either direction.** We neither confirm nor
  refute 290 under that convention; we did not obtain the definition. Control 11 is a synthetic
  mutation of our own and stands in for nothing. Nor do we adjudicate Roucairol–Cazenave's own
  judgement that the survey's definition is a misstatement — we report that they say so, and that
  they call the Brewster definition the correct one, because a reader is entitled to both facts.
- **Nothing is certified for `n > 10`** beyond the 21 explicitly listed larger instances.
- **The primary texts were not read by this certificate.** *Written on the Wall* p. 79 (the
  conjecture) and p. 52 (the gravity matrix) are quoted here **at second hand**, via
  Roucairol–Cazenave's restatement and via the paper. We did not consult the original.
- **The girth hypothesis is not shown to be necessary — and this is a disclosure, not a result.**
  Check 3b sweeps all **30092** labelled graphs of girth `< 5` on `n ≤ 6` and finds **0** violations
  under the paper's reading and **0** under the literal one. That is a fact about a small range, not
  a theorem, and emphatically not a reason to drop the hypothesis: the paper's proof uses girth ≥ 5
  essentially, via the Reiman `C₄`-free edge bound. It is reported because a reader deserves to know
  that our data does not, on its own, exhibit the hypothesis doing any work. Because both counts are
  `0`, neither counter is by itself evidence that both readings were consulted — the sweep's
  `girth_lt5_sweep_digest_sha256`, hashed over both readings' returned records, is what carries that.
- **The `Gr(u,v) = 0`-when-no-path convention** for disconnected graphs is taken from
  Roucairol–Cazenave's restatement of the definition, not from the original page.
- The pseudo-random instances are reproducible but **arbitrary**; they are evidence of breadth, not
  of coverage.

## Sources

- S. Fajtlowicz, *Written on the Wall* (conjecture 290, p. 79; gravity matrix, p. 52) — cited at
  second hand, see above.
- N. Wilbanks and "Annie" (AGNT Labs), *A Proof of Graffiti 290*,
  <https://agnt.gg/whitepapers/a-proof-of-graffiti-290.html> — the external result being replayed.
- **[1]** M. Aouchiche and P. Hansen, *A survey of automated conjectures in spectral graph theory*,
  **Linear Algebra and its Applications**, 432(9):2293–2322, April 2010 — the survey whose gravity
  definition admits the refutation, and which Roucairol–Cazenave identify as a misstatement. **Not
  obtained by us; not replayed.**
- **[2]** T. L. Brewster, M. J. Dinneen, V. Faber, *A computational attack on the conjectures of
  graffiti: New counterexamples and proofs*, **Discrete Mathematics**, 147(1–3):35–55, 1995 — with
  *Written on the Wall* p. 52, the source of the gravity definition certified here.
- M. Roucairol and T. Cazenave, *Refutation of Spectral Graph Theory Conjectures with Search
  Algorithms*, [arXiv:2409.18626](https://arxiv.org/abs/2409.18626) (v1, 27 Sep 2024), **Sec. 5.2
  "Erratum"** — both halves of the convention split, and the transcription of the Written-on-the-Wall
  / Brewster gravity matrix that check 1b verifies the implementation against.

<!-- GENERATED FILE — do not edit. Edit book/chapters/*.md and run
     `make book`; `make check-book` fails when this file is stale. -->
> **STATUS: SEED EDITION — this book accretes as the frontier moves; it
> circulates externally only after the EFA-DR1 DOI is live and the first
> observatory note exists.**

# Cartography of Numbers

*The living book of frontier cartography — the observational practice of the
mathematical frontier.*

<!-- DRAFT: lead pass pending -->

Conway drew maps of number-theoretic objects — the topograph; Hatcher built a
book on that map; this book maps the frontier itself. Both are cited here as
inspiration only: nothing below derives from either work.

This is a **living book**. The prose is hand-written; every table, count, and
number is generated at build time from the repository's ledgers
([`atlas/gap_map.json`](../atlas/gap_map.json), the certificates, the
observatory records, the Frontier Board) and carries its confidence class where
one applies. When the data moves, the book moves — and when the book falls
behind the data, the build gate (`make check-book`) fails loudly rather than
letting a stale number circulate. A static text about a moving frontier would
be wrong within weeks; this one is wrong for at most one build.

It is written for two audiences at once: **agents** joining the practice, who
need the field's objects, gates, and honest scope in one place before touching
the ledgers; and **humans** — mathematicians, tool-builders, skeptics — who
want to check, use, or attack the map. The charter
([`FRONTIER_CARTOGRAPHY.md`](../FRONTIER_CARTOGRAPHY.md)) is the field's
normative document; this book is its narrative form. Where they disagree, the
charter wins.

The state of this edition, generated from the data:

| this edition | state |
|---|---|
| data through | **2026-07-19** (latest provenance/evidence date in the gap map) |
| the ledger | **222** bounded quantities |
| confidence | C0 0 · C1 1 · C2 3 · C3 218 |
| movements on the board | **8** (🟢 5 · 🟡 2 · 🔴 1) — corrected claims kept visible |

---

# 1 · The Map

<!-- DRAFT: lead pass pending -->

The unit of progress in this practice is not the theorem and not the paper —
it is the **bracket**. Knowledge state is a versioned ledger of `[L, U]` gaps
on bounded quantities of open problems, and a result is a monotone movement of
that ledger: a lower bound raised by a witness, an upper bound lowered by a
nonexistence certificate, a verified-up-to-N frontier pushed outward. Improving
a bound is a first-class result, not a consolation prize (charter Tenet 2).

The gap map is that ledger. Each entry records the bracket, its sources, what
a machine-verifiable witness would be, how feasible one is, and an `evidence[]`
block from which the entry's confidence class is *computed* — never asserted.
Most entries are agent-mined and honestly labeled as such: structurally
validated, literature-grade, class C3 until an in-project verification
artifact exists. The map does not pretend its own entries are verified; the
labeling *is* the release gate.

- **222 bounded quantities** on the map ([`atlas/gap_map.json`](../atlas/gap_map.json)).
- Provenance (mechanical, from `provenance.added_by`): **12** curated seed, **2** lane-added, **208** agent-mined.
- Confidence distribution (computed from `evidence[]`, never asserted): **C0** 0 · **C1** 1 · **C2** 3 · **C3** 218.
- **81 witness-workable**: still open, with a side a single submitted
  construction — checked by the entry's stated verifier — can move.

| kind | entries | witness-workable |
|---|---|---|
| `value_gap` | 30 | 5 |
| `next_cell` | 81 | 56 |
| `verified_range` | 28 | 16 |
| `bounded_below_only` | 16 | 4 |
| `bounded_above_only` | 1 | 0 |
| `not_gap_shaped` | 66 | 0 |

Movements against this ledger are recorded on the Frontier Board — the done-work
record, tiered by verification, with corrected claims kept in place so no one
re-walks them:

8 movements recorded on the
[CHRONOS Frontier Board](../README.md#chronos-frontier-board) (🟢 5 · 🟡 2 · 🔴 1).
Corrected claims stay on the board by design (charter Tenet 5).

| tier | problem | movement | certificate | when |
|---|---|---|---|---|
| 🟢 | **#552** `R(C4,K1,n)` | certified C₄-free witnesses ⇒ `R(C4,K1,n) = n + ⌈√n⌉ + 1` for `12 ≤ n ≤ 16`; `n=17` closed at `22` (Parsons 1975) | [`certificates/erdos-552`](certificates/erdos-552) · PR #78 | 2026-07-16 |
| 🟢 | **#241** B₃-subset table (A387704) | proved `A387704(n) = max{k : A227358(k) ≤ n−1}` (translation invariance; 0/151 mismatches) ⇒ first jump to 9 at `n=209`; atlas cell **closed by cross-reference** | PR #80 | 2026-07-16 |
| 🟢 | **#13** Erdős–Sárközy | certified exact table `f(1..45)`; `N=17` is the **last** exception to `⌊N/3⌋+1` — an empirical location for Bedert's ineffective threshold | [`certificates/erdos-13`](certificates/erdos-13) · PR #81 | 2026-07-17 |
| 🟢 | **#979** `f₃` / A385316 | **`a(6) > 10¹³` at C1** — two independent implementations (a streaming counter sweep and a blind-reimplemented pair-sum sweep, different algorithms, spec-only isolation) each covered `[0, 10¹³)` gap-free with no 6-way value; cross-checked 100/100 windows, zero mismatches; 20× past the published `4.99·10¹¹` | [`certificates/erdos-979`](certificates/erdos-979) | 2026-07-19 |
| 🟡 | **#1107** Mollin–Walsh / A056828 | verified **no exception below `10¹⁰`** to being a sum of ≤3 powerful numbers — extends the published `4·10⁷` frontier; exception set `{7,15,23,87,111,119}` reproduced, powerful-counts cross-checked vs A118896, replay-verified | [`certificates/erdos-1107`](certificates/erdos-1107) | 2026-07-18 |
| 🟡 | **#142** `r₃(N)` | complete 12,349-cell geometric enumeration superseding a flawed 976-cell subset — a **foundation only**; self-declared no-bridge, **not** an `r₃(N)` bound | sister session | 2026-07-13 |
| 🟢 | **#1029 / #77** `R(5,5)` | 42/42 DRAT-certified structural negatives (no witness; rigidity + prime-order orbit collapse), all consistent with `R(5,5) = 43` | [r55-rigidity-certificates](https://github.com/techno-optimist/r55-rigidity-certificates) · DOI [10.5281/zenodo.21305022](https://doi.org/10.5281/zenodo.21305022) | 2026-07-10 |
| 🔴 | **#552** `R(C4,K1,39)` | the `=46` **new-value** claim was **retracted** — DS1 rev.18 lists `46 ≤ f(39) ≤ 47`, OPEN; the 45-vertex witness stands as a re-derivation of Wu–Sun–Radziszowski 2015 | [`certificates/erdos-552-f39`](certificates/erdos-552-f39) | 2026-07-17 |

(Certificate links in this table are relative to the repository root,
as on the board itself.)

---

# 2 · Fences

<!-- DRAFT: lead pass pending -->

Some theorems are true "for all sufficiently large N" — and silent about where
sufficiently large begins. When the proof runs through compactness, ergodic
limits, or the Subspace Theorem, no computable threshold falls out at all: the
theorem is **ineffective**. Its finite side, though, is often computable, and
that asymmetry is a place where machine work adds something a theorem cannot:
compute the exact values in a finite range and record where the asymptotic
statement is last violated. That last violation is a **lower fence** for the
ineffective threshold — a measured point the threshold provably sits above.

A fence is not a location. Sporadic exceptions beyond the computed range are
never excluded — the theorem itself is what forbids claiming otherwise — and
every fence table must say so in the same breath as its data. The exemplar is
Erdős–Sárközy #13: Bedert proved `f(N) ≤ ⌊N/3⌋ + 1` for all large N with an
ineffective threshold, and the certified exact table locates the last
exception in the computed range.

Computed range: `N = 1…45` ([`certificates/erdos-13/table.json`](../certificates/erdos-13/table.json); replay: `python3 certificates/erdos-13/verify.py`).

```
f(1..45) = 1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 14, 15, 15, 15, 16
```

The bound `⌊N/3⌋ + 1` (Bedert's theorem, ineffective threshold) is exceeded
at exactly **10** values of N in the computed range:

| N | f(N) | ⌊N/3⌋+1 | extremal witness |
|---|---|---|---|
| 2 | 2 | 1 | `{1, 2}` |
| 4 | 3 | 2 | `{2, 3, 4}` |
| 5 | 3 | 2 | `{2, 3, 4}` |
| 7 | 4 | 3 | `{3, 4, 6, 7}` |
| 8 | 4 | 3 | `{3, 4, 6, 7}` |
| 10 | 5 | 4 | `{4, 5, 8, 9, 10}` |
| 11 | 5 | 4 | `{3, 5, 6, 8, 11}` |
| 13 | 6 | 5 | `{4, 5, 8, 9, 10, 13}` |
| 14 | 6 | 5 | `{4, 5, 8, 9, 10, 13}` |
| 17 | 7 | 6 | `{6, 8, 9, 11, 12, 14, 17}` |

**N = 17 is the last exception in the computed range**: `f(N) = ⌊N/3⌋ + 1` for every `18 ≤ N ≤ 45`. Because the
theorem's threshold is ineffective, sporadic exceptions at larger N are
**not excluded** — this is a lower fence on the threshold, not its location.

Fence-hunting generalizes. The WS4 shortlist below is the result of a graded
hunt across three thematic slices for more theorems with this shape —
ineffective threshold, computable finite side. The hunt's discipline is the
point: every candidate passed an effectivization check (a literature search
for a later effective bound) *before* grading, and the candidates that failed
it are recorded as dead rather than discarded, so the search is never repeated.

The WS4 hunt ([`atlas/effectivization_shortlist.json`](../atlas/effectivization_shortlist.json)): **5 candidates alive, 4 dead** — the dead are kept
so no one re-hunts them.

> Shortlist entries are HUNT RESULTS, conjecture-grade research directions — not claims. A fence table for any of them requires: re-verifying the ineffectivity at build time (the frontier moves), a dependency-free per-N verifier validated on known values, and a verified-up-to-N certificate. The trap-check killed 5 of 9 hunted candidates — the gate is the product.

**Alive (graded, effectivization-checked):**

| candidate | grade |
|---|---|
| Multidimensional Szemerédi (Furstenberg–Katznelson): the 2×2 axis-aligned square in [N]² | weak |
| Polynomial Szemerédi (Bergelson–Leibman): a 1-D configuration on the ineffective side of the Peluse–Prendiville frontier | plausible |
| Block complexity of the base-b expansion of an algebraic irrational (Adamczewski–Bugeaud) | plausible |
| Erdős–Rademacher exact minimum triangle count (Lovász–Simonovits, full-density refinement) | plausible |
| Polynomial Szemerédi / polynomial van der Waerden (Bergelson–Leibman), general non-effectivized pattern | plausible |

**Dead — do not re-hunt (each with the specific reason recorded):**

| candidate | why it is dead |
|---|---|
| Erdős #865 (Erdős–Sós pairwise-sums, 5/8 threshold) — trap-(a) illustration | This is where trap (a) FIRES. Read arXiv:2606.29361: the resolving proof is itself effective/finitary, so there is no ineffective theorem with a genuinely-unknown threshold to fence. What r… |
| Erdős #283 — integers as sums of polynomial values over a unit-fraction partition | DEAD — trap (a) fully triggered. Every instance anyone has examined is EFFECTIVE with an explicit threshold: Graham 1963 gives p(x)=x with every m ≥ 78 representable (largest exception exac… |
| Consecutive-gap growth of S-smooth numbers (S-units) | DEAD — trap (a) triggered, and this is the instructive exhibit for the whole slice. Tijdeman used Baker's theorem to prove the EFFECTIVE lower bound a_{n+1} − a_n ≫ a_n / (log a_n)^C. Since… |
| Exact hypergraph Turán numbers 'for large n' via the (strong) removal lemma (Pikhurko / Frankl–Füredi lineage) | TRAP (a) PARTIALLY FIRES — and this is the honest weakness. The removal lemma is technically EFFECTIVE (tower/Ackermann-type via regularity, or Fox's tower-of-height-log(1/ε)), so a computa… |

---

# 3 · The Observatory

<!-- DRAFT: lead pass pending -->

The observatory measures **emitted-proof sizes**: how large a machine-checkable
proof one *pinned pipeline* — encoding, solver version, configuration, seed,
all recorded — happens to emit for members of a parameterized formula family.
This is observational science, and its central discipline is knowing what the
instrument measures. An emitted size is an achievable upper bound on proof
length under that pipeline; it is **not** a minimal certificate, and the two
can diverge exponentially (the charter's cautionary exhibit: CDCL emits
exponential DRAT for pigeonhole formulas whose minimal DRAT certificates are
polynomial). Every number below carries that caveat structurally — it is
recorded in the data file itself, not appended by an editor.

The first family under observation is the upper half of `R(3,k)`: the CNF
statement that a 2-coloring of `K_n` at `n = R(3,k)` avoiding a red triangle
and a blue `K_k` exists, which is unsatisfiable — so each point is a
solver-emitted, independently checked DRAT refutation. Variance is measured
before trend: seeds within a pipeline, and two clause orders of the same
clause set, are separate axes, and a family trend would be meaningful only if
it dominated that spread. So far it is reported as ratios, not a law — the
honest no-fit posture is itself the result.

> Every size below is the size of the proof EMITTED by the pinned pipeline — an achievable upper bound on proof length under that pipeline, NOT a minimal certificate. Minimal proof size is a proof-complexity quantity solvers do not compute; no claim about shortest proofs is made anywhere in this file.

Family: R(3,k) upper half: the r3k-edge-cnf encoding (two pinned clause orders of the SAME clause set — see pipeline manifest) of 'K_n (n = R(3,k)) admits a 2-coloring with no red triangle and no blue K_k', which is UNSAT at n = R(3,k). Instances: (k=3, n=6), (k=4, n=9), (k=5, n=14 — lex pipeline; completed off-Mac at a 6 GiB cap after the 300 MB-cap DNFs proved to be cap artifacts).

Completed family points: **3** of 3 attempted. Raw records with commands and
sha256s: [`observatory/measurements.json`](../observatory/measurements.json);
pinned pipelines: [`observatory/pipeline.json`](../observatory/pipeline.json).

| family point | n | order | seed | emitted DRAT bytes | result |
|---|---|---|---|---|---|
| R(3,3) upper half | 6 | lex | 1 | 247 | `s VERIFIED` |
| R(3,3) upper half | 6 | lex | 2 | 247 | `s VERIFIED` |
| R(3,3) upper half | 6 | lex | 3 | 247 | `s VERIFIED` |
| R(3,4) upper half | 9 | lex | 1 | 565,470 | `s VERIFIED` |
| R(3,4) upper half | 9 | lex | 2 | 574,869 | `s VERIFIED` |
| R(3,4) upper half | 9 | lex | 3 | 561,523 | `s VERIFIED` |
| R(3,5) upper half | 14 | lex | 1 | > 316,940,288 at abort | DNF at proof-size cap (later shown a **cap artifact** — superseded) |
| R(3,5) upper half | 14 | lex | 2 | > 316,313,600 at abort | DNF at proof-size cap (later shown a **cap artifact** — superseded) |
| R(3,5) upper half | 14 | lex | 3 | > 315,756,544 at abort | DNF at proof-size cap (later shown a **cap artifact** — superseded) |
| R(3,3) upper half | 6 | interleaved | 1 | 247 | `s VERIFIED` |
| R(3,3) upper half | 6 | interleaved | 2 | 247 | `s VERIFIED` |
| R(3,3) upper half | 6 | interleaved | 3 | 247 | `s VERIFIED` |
| R(3,4) upper half | 9 | interleaved | 1 | 577,593 | `s VERIFIED` |
| R(3,4) upper half | 9 | interleaved | 2 | 559,037 | `s VERIFIED` |
| R(3,4) upper half | 9 | interleaved | 3 | 547,216 | `s VERIFIED` |
| R(3,5) upper half | 14 | lex | 1 | 5,253,767,512 | `s VERIFIED` — aarch64-linux (separate series) |
| R(3,5) upper half | 14 | lex | 2 | 6,033,729,549 | `s VERIFIED` — aarch64-linux (separate series) |
| R(3,5) upper half | 14 | lex | 3 | — | aborted by the operator (shared-host protection) — no datum |

**Growth fit claimed: none.**
No growth-law fit is claimed. Three family points are now completed (the charter's bare minimum): 247 B / ~564 KB pooled mean / 5.25-6.03 GB (2 seeds). Ratios: ~x2,284 then ~x10,000. A fit is still withheld: n=3 points, the R(3,5) order-variance axis is unmeasured, and cross-machine emitted-size comparability (arm64-darwin vs aarch64-linux) is untested at small instances. Relative seed spread grows with size: 0% (R33, degenerate) -> 2.4-5.4% (R34) -> ~13.8% over 2 seeds (R35). Points from different pipelines/machines are separate series, never mixed.

---

# 4 · Walls

<!-- DRAFT: lead pass pending -->

Silicon does not melt walls. Combinatorial explosion did not change when
verification became cheap, and the largest single category on the map is the
problems whose exact value needs a nonexistence proof with no feasible
certificate. The project's own measurements say so plainly: in one 12-candidate
triage (2026-07-17, drawn from a difficulty-ranked feed that over-selects hard
problems), **11 of 12 were walls**. The honest territory is everything *around*
them — the witness side of every bracket, the verified-up-to-N frontier of
every conjecture — plus the incompressible region no biological practice could
enter.

A wall on the map is a contribution, not an admission. Every named wall — with
the specific reason it is walled and the source that walled it — is compute
that no agent, ours or anyone else's, burns rediscovering the dead end. An
atlas that only lists targets is advertising; an atlas that names its walls is
a map. And a wall for *us* is not always a wall for *everyone*: several walled
problems keep a fair witness side where the honest play is market-making —
host the board, pin the verifier, and let whoever's new construction passes
claim the movement.

The discipline is mechanical, not rhetorical. Each gap-map entry carries an
`exact_feasibility` field pricing its exact-value attack-state, and the
do-not-enter list records the four recurring reasons: someone already walled
it with our tools at larger scale; the verifier is not exact-poly-time; the
witness is not representable; there is no finite frontier at all.

Exact-value attack-state over the gap map's 222 quantities (field `exact_feasibility`):

| attack-state | meaning | entries |
|---|---|---|
| `cell` | an uncomputed exact cell current exact tools can plausibly settle | 55 |
| `drat-candidate` | exact settlement looks reachable via a certified-UNSAT (DRAT) route | 7 |
| `unknown` | attack-state not yet priced | 20 |
| `wall` | the exact value needs an infeasible nonexistence proof — do not spend search compute here | 140 |

Against that: **81** quantities remain witness-workable — the
honest territory *around* the walls. The named do-not-enter list, with the
specific reason and source for each wall, is
[`atlas/walls.md`](../atlas/walls.md).

---

# 5 · Methods — the field's instruments

<!-- DRAFT: lead pass pending -->

The unit of knowledge is the **certificate**: a claim exists when a stranger's
machine can verify it from the artifact alone — witness plus dependency-free
checker, solver-emitted DRAT proof replayed through an independent checker
(parse the `s VERIFIED` line, never the exit code, and ship a truncated-proof
negative control that must fail), a replayable enumeration receipt, or a formal
proof. No trust, no authority. Every certificate in this repository ships its
own verifier and replay command; `make hello-frontier` walks a stranger
through the loop end-to-end.

On top of certificates sits the **epistemic ledger**: every map entry carries
recorded evidence, and a mechanical rule computes its confidence class from
that evidence — the validator fails any stored class the artifacts do not
prove. Replication counts only when it is *evidence, not echo*: two
implementations are independent when the second is blind-reimplemented from
the spec alone, on different algorithms, and cross-checked against the first
only after both have run. An echo of the same code path replicates nothing.

Classes are computed from recorded `evidence[]` by
[`tools/validate_gap_map.py`](../tools/validate_gap_map.py) — the validator
fails any stored class the recorded evidence does not prove.

| class | meaning | entries |
|---|---|---|
| C0 | formal proof, machine-checked | 0 |
| C1 | &ge;2 independent implementations or replays with distinct artifacts at the claimed range | 1 |
| C2 | exactly one verified, replayable implementation | 3 |
| C3 | literature- or numerics-grade — no independent in-project verification artifact | 218 |

The remaining instruments are refusals. The **freshness gate**: no claim of
"new" ships before a survey-literature check — this project's one retraction
was caught by its own gate, and the retracted row stays on the board. The
**quarantine rule**: evidence is never deleted and history is never
force-pushed; a corrected claim is quarantined with a reason, visibly, so the
next agent does not re-walk it. And the **no-fit posture**: below the charter's
minimum family points, or with a variance axis unmeasured, a curve is reported
as points and ratios — declining to claim is an instrument, not a weakness.

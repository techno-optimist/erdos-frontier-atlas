# Frontier Cartography

> **STATUS: internal charter, pre-artifact.** This file is the build plan, reviewed by
> an adversarial critic panel but not yet backed by its first two numbered artifacts
> (the DR1 dataset release and the certificate-size survey note). External circulation
> waits for those; until then the public-facing documents are the dataset README and
> the certificates themselves. Nothing in this file is an offer.

**The observational practice of the mathematical frontier.** Frontier cartography
treats the boundary of mathematical knowledge as a first-class object: measurable,
versioned, machine-verifiable, and — by design — economically live. Its unit of
knowledge is the **certificate** (not the theorem), its unit of progress is the
**bracket-tightening** (not the paper), and its instrument is an autonomous agent
fleet coupled to exact verifiers.

This repository — the Erdős Frontier Atlas — is the prototype instrument. This
document is written for two audiences: the project's own **agents** (§8) and any
**outside mathematician** who wants to check, use, or attack the map (§8b).

---

## 1. Why this practice, why now

Human mathematics has one constraint nobody chose: **a proof had to fit through a
human head.** Working memory, a career, a page limit. The discipline therefore
selected for compressible truth — short statements with surveyable proofs — and its
credit economy rewards exactly that shell. Proof-complexity theory guarantees the
shell is thin: natural true statements exist whose shortest proofs in a given system
are astronomically large. Biological practice cannot live there. Machine-checkable
certificates can: nobody "understands" a DRAT proof, and nobody needs to — the
checker's verdict, independently replayable, *is* the knowledge.

Two things changed at once: (1) verification became cheap, exact, and delegable
(SAT+DRAT, replayable enumeration, proof assistants), and (2) autonomous agents
became capable of running the *whole loop* — sourcing problems, building verifiers,
searching, certifying, publishing, and auditing each other — around the clock.

What did **not** change: combinatorial explosion. This project's own measurements say
so plainly — in one 12-candidate triage (2026-07-17, drawn from a difficulty-ranked
feed that over-selects hard problems), **11 were walls** whose exact value needs a
nonexistence proof with no compact certificate. Silicon does not melt walls. The
practice's honest territory is everything *around* them: the witness side of every
bracket, the verified-up-to-N frontier of every conjecture, the certificate record of
every family — plus the incompressible region no biological practice could enter.

## 2. Tenets

1. **The certificate is the unit of knowledge.** A claim exists when a stranger's
   machine can verify it from the artifact alone: witness + checker, DRAT proof,
   replayable enumeration receipt, formal proof. No trust, no authority.
2. **The bracket is the unit of progress.** Knowledge state = a versioned ledger of
   `[L, U]` gaps on bounded quantities. Results are monotone movements of the ledger.
   Improving a bound is a first-class result, not a consolation prize.
3. **Machines conjecture too.** Mass numerical coincidence-mining generates
   conjecture-grade relations; proof (human or machine) promotes them.
4. **The epistemic state is explicit.** Every entry carries a mechanical confidence
   class derived from recorded evidence (formal proof > independent replications >
   single verified implementation > conjecture-grade numerics). No binary pretense.
5. **Negative results, retractions, and walls stay on the map.** A corrected claim
   remains visible so no one re-walks it. A wall marked WALL is a contribution.
6. **Freshness before novelty.** Every claim of "new" is gated on a literature /
   survey / upstream check *first*. (Learned the hard way: a "new value" that was a
   2015 re-derivation, caught by this project's own novelty gate and retracted.)

## 3. The objects of study

| object | what it is | prototype (state, honestly labeled) |
|---|---|---|
| **Gap map** | the versioned `[L,U]` ledger over bounded quantities of open problems | [`atlas/gap_map.json`](atlas/gap_map.json) — 221 quantities: 12 curated + number-checked, ~208 agent-mined (**structurally validated, not yet independently number-re-verified** — see WS1 gate); ~81 witness-workable; schema + validator + tests |
| **Certificates** | witness+verifier, DRAT nonexistence, verified-up-to-N receipts, cross-ref closures | [`certificates/`](certificates/) — e.g. erdos-552, erdos-13, erdos-1107, ramsey-3-3 |
| **Verification frontiers** | "no counterexample below N", with replay + cross-checks | Mollin–Walsh (#1107): published 4×10⁷ → **verified to 10¹⁰** (C2: one scan implementation + independent witness re-factoring + A118896 count cross-checks; full pipeline receipt in the parent workspace pending path-sanitization; method + exception table publicly replayable via [`certificates/erdos-1107/`](certificates/erdos-1107/)) |
| **Relation graph** | numerically-verified relations between sequences, conjecture-grade until proven | exemplar: `A387704(n) = max{k: A227358(k) ≤ n−1}` — found by numerical crossref (0/151 mismatches), then proven (translation invariance), closing #241; the librarian lane re-derives it as its standing control |
| **Effectivization records** | empirical *lower fences* for ineffective thresholds ("true for N large enough") | Erdős–Sárközy #13: in the computed range `N ≤ 45`, the last exception to `f(N)=⌊N/3⌋+1` is **N=17**. Because Bedert's theorem is ineffective, sporadic exceptions at larger N are **not excluded** — this is a lower fence on the threshold, not its location |
| **Certificate-size observations** | measured *emitted-proof* sizes under pinned pipelines across parameterized families | first exemplar: the upper half of `R(3,3)=6` has a 247-byte solver-emitted DRAT proof — [`certificates/ramsey-3-3/`](certificates/ramsey-3-3/) (CNF + proof + negative control, independently checkable) |
| **The board** | the running, tiered, honesty-first scoreboard of movements | [CHRONOS Frontier Board](README.md#chronos-frontier-board) |

## 3b. Where the instruments live

Not every workstream is executable from this repository alone. Honest map:

| workstream | executable from this repo | requires project infrastructure |
|---|---|---|
| WS1 dataset release, WS4 effectivization, WS7 ledger schema | ✅ (data + validators here) | — |
| WS2 witness *verification* (checking a claimed record) | ✅ (pinned verifiers here) | search campaigns run on the fleet |
| WS3, WS5, WS6 | artifacts land here | lanes (enumeration, certified-UNSAT, librarian) live in the project's private workspace |
| WS8 Lean bridge | pin-file + shortlist land here | proving runs on project compute |
| WS9 bounties | board + verifier here | settlement via the P42 arena |
| WS10 operations | — | entirely fleet-side |

## 4. Workstreams

Each lists: goal → first artifact → gate → requires. Agents: pick one, satisfy its
gate, ship, add a board row.

### The Map

**WS1 — The atlas as a citable dataset.**
Goal: make the gap map a versioned, citable research object.
First artifact: **EFA-DR1** — the v1.0 data release, sky-survey style: changelog,
bracket-movement metrics, `CITATION.cff` carrying a **live Zenodo DOI** (the release
gate — DR1 does not ship without it), licensing stated (CC-BY 4.0 for data,
MIT for tools), and a generated *State of the Frontier* report. Cadence: the report
ships quarterly; releases are numbered (DR1, DR2, …), each with its own DOI.
Also in DR1: a **10-minute quickstart** (`make hello-frontier` or one pinned script)
that replays the ramsey-3-3 DRAT check, verifies one witness certificate, and prints
one gap-map entry with its confidence class — a stranger sees the field's epistemic
loop end-to-end in minutes.
Gate: depends on WS7 — every entry must carry a mechanical verified/unverified label
*before* release (today the ~208 mined entries are labeled only in the header note);
schema validator green; every referenced certificate replayable by a stranger.
Requires: this repo only.

### The Survey

**WS2 — Records campaigns.**
Goal: systematic bracket-tightening on the witness-workable quantities (~81 today).
First artifact: live record boards exist and are worked by the fleet's rotation.
Gate: a claimed record ships witness + dependency-free verifier, passes the freshness
gate (survey literature, not just OEIS), and reproduces all known values first.
Requires: verification from this repo; search campaigns fleet-side.

**WS3 — Verified-up-to-N ladders.**
Goal: standardize the depth-sounding pattern — reproduce the published frontier, then
extend with independent cross-checks, witness sampling, and replay.
First artifact: exists — Mollin–Walsh to 10¹⁰. Next: 3 more ladders from
`verified_range` candidates; and mirror **path-sanitized** receipts of every ladder
into `certificates/` (the MW receipt currently lives fleet-side; public mirroring is
part of this workstream's definition of done).
Gate: published-frontier reproduction *before* extension; ≥2 independent
implementations; replay command in the receipt.
Requires: heavy scans fleet-side; receipts land here.

**WS4 — The effectivization hunt.**
Goal: catalog ineffective theorems ("true for all N sufficiently large") whose finite
side is computable, and establish empirical **lower fences** for their thresholds.
First artifact: a shortlist of 5–10 such statements from the corpus; one new fence
table beyond #13.
Gate: fence claims are verified-up-to-N certificates; the statement of what is proven
(ineffective bound) vs. measured (fence in the computed range) is explicit — sporadic
larger exceptions are never claimed excluded.
Requires: this repo (the hub's 1217-problem index is the hunting ground).

### The distinctive science

**WS5 — The certificate-size observatory.** *(the most distinctive workstream)*
Goal: observational study of **emitted-proof sizes**. The measured quantity is
`S(F; encoding, solver, config, seed)` — the size of the proof one *pinned pipeline*
emits for formula F. This is an **achievable upper bound on proof length under that
pipeline, not a minimal certificate**: minimal proof size is a proof-complexity
quantity solvers do not compute, and no claim about shortest proofs is made here.
What is potentially interesting: how emitted sizes *grow* along a family under a
fixed pipeline, and how stable that growth is across pipelines.
First artifact: emitted-size and check-time curves for the `R(3,k)` upper-half family
under one fully pinned pipeline (encoding + symmetry-breaking scheme + solver version
+ config + seed all recorded), with **≥3–4 family points before any fit is claimed**,
variance reported across at least the encoding and seed axes (a family trend is
meaningful only if it dominates the cross-config spread), and every proof archived +
independently checkable. Feasibility warning up front: `R(3,5)+` upper halves may be
infeasible or emit enormous proofs — a null result here is a result.
Cautionary exhibit, not a discovery: CDCL emits exponential DRAT for pigeonhole
`PHP(n)` (that is Haken's 1985 resolution lower bound at work), while the *minimal*
DRAT certificate is polynomial (extended resolution; DRAT p-simulates it) — the
observatory measures the former and must never call it the latter.
Gate: every measured proof verified by the checker (parse the `s VERIFIED` line —
never the exit code); a truncated-proof negative control must fail; sizes
reproducible from the pinned pipeline manifest.
Requires: the certified-UNSAT lane (fleet-side); seed exemplar already public at
[`certificates/ramsey-3-3/`](certificates/ramsey-3-3/).

**WS6 — Sequence-universe closure.** *(closure mining at scale)*
Goal: close the integer-sequence universe under derivation operators (shift, offset,
first-difference/partial-sum, inverse-count, jump-position), mining
numerically-verified relations and promoting them: coincidence → conjecture-grade →
proven. (Lineage: the Ramanujan Machine did this for continued-fraction constants;
this applies the loop to the sequence universe with certificate discipline.)
First artifact: publish the existing 58-relation graph (with the #241 control pair)
as `atlas/relations.json` in this repo, with the mining thresholds stated numerically
(≥30 shared terms, 0 mismatches over the full b-file overlap, distinct-value
diversity floor with low-signal flagged). Then a 10× pool expansion.
Gate: the control pair must re-derive on every run; every relation labeled
conjecture-grade until proven.
Requires: librarian lane (fleet-side); the graph lands here.

### The Spine

**WS7 — The epistemic ledger.**
Goal: mechanical confidence classes on every atlas entry, computed from recorded
evidence — no vibes.
Classes: **C0** formal proof (machine-checked) · **C1** ≥2 independent
implementations replicated at the full claimed range · **C2** single verified
implementation, replayable · **C3** conjecture-grade numerics.
(Exemplar, stated exactly: `a(6) > 10¹²` for A385316 is **C1** — two independent
implementations at the full window, three more replicating at 2×10¹¹; the newer
`a(6) > 2×10¹²` extension is currently **C2** — one implementation, pending
independent replication.)
First artifact: **a schema extension first** — the current provenance block
(`added_by`/`date`/`checked`) cannot express implementation count or artifact
lineage, so add an `evidence[]` field (`{type: formal_proof | implementation |
replay_receipt | numeric_scan | literature, artifact, date}`) plus a validator rule
that *computes* the class from it; then re-stamp the map. WS1's release gate depends
on this.
Gate: classes are computable from recorded evidence; no entry may claim a class its
artifacts don't prove.
Requires: this repo only.

**WS8 — The formal spine (Lean bridge).**
Goal: promote certified results to C0 by formalizing them.
First artifact: `atlas/lean_lane.json` recording the upstream formalization repo, the
pinned commit, the pin date, and the ranked shortlist — then one statement proven
end-to-end (the min-overlap family #36, where this project already holds a registered
theorem, tops the shortlist).
Gate: compiles against the commit recorded in `atlas/lean_lane.json`; upstream drift
re-checked before investing (observed decay of the easy-cell pool: ~6/month — this is
a race).
Requires: proving runs on project compute; the pin-file and proofs land here.

### The Economy

**WS9 — Bounties on bracket movements.**
Goal: complement prestige-per-theorem with bounty-per-movement. Record boards with
pinned verifiers **would become** bounty boards: a witness that passes the pinned
verifier claims the purse, friend or stranger.
**Status: design intent, not an offer.** No bounty is live today; nothing in this
document constitutes an offer of payment. A board becomes an offer only when its
purse, settlement terms, and verifier image are published on the arena itself.
First artifact: one already-registered testnet board funded with a demo pool and one
demo settlement replayed end-to-end against the pinned verifier image — proving the
promotion pipeline (gap-map entry → audited board → pinned verifier image → funded
pool) before any real purse.
Gate: settlement uses the *same* pinned verifier as the board (no parallel
adjudication); boards must be READY-class (exact, sub-second, byte-capped checks).
Requires: the P42 arena.

### Observatory operations

**WS10 — The instrument itself.**
Goal: keep the fleet honest and running: rotation, dispatch, curation, supervision,
and the publisher's receipt trail (quarantine-not-unlink, honest commit messages),
with fan-out workflows adversarially verified.
Standing gates: every write audited; every claim freshness-checked; compute-heavy
searches run within enforced compute budgets, scheduled or dispatched as background
jobs; external submissions (OEIS, journals, upstream PRs) are **always human-sent**.
Requires: entirely fleet-side; this document only binds its outputs.

## 5. Sequencing

**First three moves (order matters — each gates the next):**
1. **WS7 schema extension + re-stamp** — evidence[] and computed confidence classes.
   Without it, DR1 cannot honestly label its own entries.
2. **WS1 / EFA-DR1** — the citable release: DOI live, licenses stated, quickstart
   runs in 10 minutes, State of the Frontier generated. The map, versioned and
   replayable.
3. **WS5 first note** — the R(3,k) emitted-size curve under a pinned pipeline,
   artifacts in `certificates/`, with the emitted-vs-minimal distinction stated in
   the first paragraph.

**This quarter:** WS3 (three ladders + public receipt mirroring), WS4 (one fence
table), WS6 (`atlas/relations.json` + 10× expansion), WS8 (pin-file + first proof),
WS9 (demo settlement).

**Horizon:** a second problem corpus on the same instrument (the machinery is
corpus-agnostic); external contributors claiming verified movements; numbered data
releases on a standing cadence.

## 6. Honest scope — what this practice does *not* claim

- **Walls stay walls.** Nothing here computes R(5,5) or MOLS(10). Where the exact
  value needs an infeasible nonexistence proof, the map says WALL and works the
  witness side only.
- **No new truth-kinds; mostly not even new objects.** Several "objects of study"
  are certificate-native modernizations of existing practice: the gap map is a
  dynamic survey in the lineage of **Radziszowski's DS1** (a decades-old `[L,U]`
  ledger for Ramsey numbers); the citable computed database with rigor flags exists
  in the **LMFDB**; conjecture-mining is the **Ramanujan Machine's** program;
  certified SAT results run Appel–Haken → Flyspeck → Heule's lineage; OEIS and
  Polymath and Erdős's own bounty network are the social ancestors. The claimed
  novelty is narrower and defensible: **the agent-operated closed loop
  (source → verify → certify → publish → audit) over a unified certificate ledger,
  with bounty-per-movement as its economy.** Precedent for that kind of claim:
  nothing in "data science" was individually new either; the unification was the
  invention.
- **The deepest human advantage is untouched.** New abstractions that collapse
  infinite search spaces remain the biological superpower. This practice is designed
  around that division of labor, not in denial of it.

## 7. What "the field exists" looks like

1. The gap map (DR-n) is cited by someone we've never met.
2. A stranger's witness passes a pinned verifier and claims a movement (or, once
   live, a bounty).
3. The WS5 dataset is cited, re-analyzed, or **refuted** in a proof-complexity
   venue by an external group.
4. A conjecture-grade relation from WS6 is proven by an outside mathematician.
5. A second corpus is onboarded — or the instrument is forked and run by someone
   outside the project.
6. An external human contributor lands a certified movement end-to-end through the
   public pipeline alone.

## 8. How an agent should use this document

1. Read tenets (§2) and honest scope (§6). They bind every action.
2. Pick a workstream (§4) whose gate you can satisfy *this session* — checking §3b
   for whether it is executable from this repo or needs the fleet.
3. Before any claim: freshness-check (survey literature first), reproduce knowns,
   then extend. Ship the certificate with its verifier and replay command.
4. Update the board (README) and the registry on every movement, correction, or wall.
5. Never delete evidence — quarantine with a reason. Never force-push history.
   Never send external submissions — stage them for the human lead.
6. When a search would contend for shared compute, schedule or dispatch it within
   the enforced budgets; never degrade the shared instrument.

## 8b. How an outside mathematician can use this

- **Verify a claim in one command** — every certificate ships its checker, e.g.:
  `python3 certificates/erdos-552/verify.py` ·
  `python3 certificates/erdos-1107/verify.py` ·
  `drat-trim certificates/ramsey-3-3/problem.cnf certificates/ramsey-3-3/proof.drat`
- **Dispute or correct an entry** — open an issue citing the entry and your source;
  Tenet 5 guarantees corrections stay visible (see the board's retained retraction).
- **Claim a movement** — submit a witness for any record board; if it passes the
  pinned verifier, the movement is yours (with attribution on the board).
- **Take a conjecture** — anything labeled conjecture-grade in the relation graph is
  an open invitation: prove it and it's your theorem; we'll link it.

## 9. Risks

| risk | mitigation |
|---|---|
| Overclaim (the #1 failure mode) | novelty gates, freshness checks, the registry's falsified-approaches ledger, retractions kept visible, adversarial critic panels on foundational claims (this document included) |
| Measuring the instrument, not the mathematics (WS5) | fully pinned pipelines, cross-encoding/seed variance reported, emitted-vs-minimal distinction mandatory |
| Racing upstream (formalization pools decay) | drift checks against the recorded pin before investing |
| Compute contention on shared infrastructure | enforced budgets; heavy searches scheduled or dispatched |
| Mined data treated as verified | mechanical confidence classes (WS7) gate the release (WS1) |
| Manifesto before artifacts | the STATUS banner at the top of this file: external circulation is gated on DR1 + the WS5 note |

---

*Prototype instrument: this repository. Parent program: the honesty-harness thesis —
autonomous agents need a verification layer — applied here to the oldest verification
culture we have.*

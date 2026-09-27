# Strike-board freshness — 2026-09-27

Overlay only. **Nothing here sets a status**: statuses come from
`atlas/stubs.json` and replayable evidence (standing rule 1). The production
graph is not rebuilt from this file. The one production change made in the same
lane — the #1016 gap-map row — is backed by a certificate
([`certificates/erdos-1016`](../../certificates/erdos-1016/README.md)), not by
this overlay.

**Why it exists.** The strike board (`views/sorties.md`) was mined on
2026-07-18. Since then many teams, often AI-assisted, have worked the same
finite cells: prize issues, erdosproblemaday.com reports, arXiv preprints and
public repositories. Two lanes in this atlas learned this the hard way (#617,
[FINDINGS](../../certificates/erdos-617/FINDINGS.md); and #1016, whose board cell
m(38) had been settled on 2026-07-29 by the time this lane opened). Read the rows
below before spending compute on a board target.

## Pins

| what | pin |
|---|---|
| production snapshot (`atlas/stubs.json`) | teorth/erdosproblems `6bcfdca9682239918df81d35e4fb12da22c61aaf` |
| previous overlay ([2026-09-11](../astra-freshness-20260911/README.md)) | `3c68e941162f81d650fc886eed34e58bed3a6a01` (2026-09-09) |
| this overlay | `af83692edd2aee68d512e04fb7b9b9c175a29bb0` (2026-09-26) |

Machine-readable: [`strike-board.json`](strike-board.json) (127 surfaces:
traps, T1–T4, every T3 cell, hot claims) and
[`upstream-diff.json`](upstream-diff.json) (the delta since the previous
overlay). `python3 experiments/claude-freshness-20260927/recompute.py PATH/problems.yaml`
re-derives every status pair in `strike-board.json` from a local YAML at the
pinned commit and fails on any mismatch.

## Since the previous overlay: 3 informal changes, 4 new records

| # | YAML before → after | on the board? |
|---|---|---|
| 547 | decidable → **proved** | **T4 MAYBE target** — do not spend on it |
| 501 | independent → not disprovable | hot-claim row |
| 1171 | open → not disprovable | no |

Records 1218–1221 were added (2026-09-12). Nineteen further rows changed only
their formal suffix (`→ (Lean)`), e.g. #193, #1019, #1129; see the JSON.

## Board surfaces whose parent status moved against the production snapshot

| tier | # | snapshot → now | consequence |
|---|---|---|---|
| trap | 548 | falsifiable → **proved (Lean)** | the DO-NOT-SPEND row is stale: nothing left to spend on |
| T2 | 1 | open → **disproved (Lean)** | the $500 headline is settled; the a(11) table cell is a finite question in its own right |
| T3 | 193 | open → **disproved (Lean)** | parent settled; the NE-path cell A231255(7) did not move |
| T3 | 730 | open → **solved** | parent settled; the gap-k record cell is unchanged |
| T3 | 1005 | open → **solved** | the cell itself is settled (below) |
| T4 | 106 | falsifiable → **disproved (Lean)** | T4 MAYBE target settled upstream |
| T4 | 547 | decidable → **proved** | T4 MAYBE target settled upstream |
| hot | 477 | open → solved | hot-claim queue entry resolved upstream |
| hot | 501 | open → not disprovable | |
| T2 | 13, 21 | proved → proved (Lean) | formal suffix only |

## T3 cells settled or moved outside this atlas since 2026-07-18

From a sweep of all 81 T3 cells (web search, public repositories, and the OEIS
data mirror at github.com/oeis/oeisdata, export of 2026-09-27). "Reported"
means read from a source, not replayed here; the three **spot-checked** rows
were re-run in this session.

| # | cell | finding | evidence level |
|---|---|---|---|
| 1016 | m(38) | settled (m(38) = 43, 2026-07-29); this lane now certifies h(n) for n ≤ 186, t₆ = 67 and t₇ = 114 | **replayed**: `certificates/erdos-1016` |
| 1062 | A038372(45) | = 30 (witness + DRAT refutation, MaliciousMusic/A038372-certificates, 2026-09-22; also a(46..68)) | **spot-checked**: its verifier passes |
| 1057 | A006931(40) | an explicit 84-digit Carmichael number with 40 prime factors (jewebste/small-carmichael-numbers, 2026-09-06) gives an upper bound; minimality reported | **spot-checked**: Korselt holds |
| 302 | A390395(732) | = 606 = a(731): {122,183,244,366,732} is an isolated component (VibeMathed, 2026-09-08) | **spot-checked** (conditional on the OEIS a(731)) |
| 156 | A382397(66) | = 6 (OEIS b-file extended to n = 183, 2026-08-22) | reported (OEIS mirror) |
| 376 | A030979(1375) | computed (71 digits) with the published successor-closure method (jaredwilder/erdos376-successor-frontier) | reported; a sweep agent recomputed it |
| 451 | A386620(184) | computed (b-file to n = 209, 2026-08-22) | reported (OEIS mirror) |
| 1005 | A386893(101) | exact formula for f(n) (arXiv:2608.15681); parent solved | reported |
| 1095 | A003458(378) | = 11243132307156301763663607287294 (b-file to 400, 2026-09-18) | reported; admissibility re-checked by a sweep agent |
| 773 | A390813(69) | reported = 32 (erdosproblemaday.com; page not reachable) | reported, unverified |
| 864 | A389182(101) | reported = 16 (erdosproblemaday.com; page not reachable) | reported, unverified |
| 20 | Sun(3,4) | bracket [39,163] → [40,50] claimed (arXiv:2609.06175; lower side Lean-checked) | reported; lower witness re-checked by a sweep agent |
| 458 | verified range | claimed to 1.1 × 10²⁷ (RajveerKapoor/erdos-work) vs the board's 10¹² | reported, unverified |
| 1100 | g(k) growth | claimed liminf g(k)^{1/k} ≥ φ (Zenodo preprint) | reported, unverified |

Eight more rows are marked `uncertain` in the JSON (for example parent-level
claims on #131, #301 and #327, an unread erdosproblemaday.com result for #295,
and unexplained OEIS edits touching #588 and #779). Fifty-seven cells showed
no public movement; that is absence of evidence, not a certificate that they
are open.

## Follow-up, same day: the production snapshot was refreshed

After this check, `atlas/stubs.json` was rebuilt from teorth/erdosproblems
`39cde0f` and google-deepmind/formal-conjectures `16e02e2` (both 2026-09-27),
with `tools/build_stubs.py`. The rebuild at the old pins reproduces the old file
byte for byte, so the diff is upstream's. It carries 21 genuine status moves
(including #1, #106, #547 and #548 above), records 1218–1221, and 342 more Lean
statements. The trap #548 and the MAYBE targets #106 and #547 left the board by
the board's own rules; their triage entries moved to `retired` in
`atlas/finite_handle_triage.json`, verdicts kept as history. The pins above
describe the snapshot as it stood when this check ran.

## Limits of this check

- The session could not open erdosproblems.com, erdosproblemaday.com or
  oeis.org directly; OEIS was read through its GitHub data mirror. Web search
  ran until the session's search budget was exhausted, so a few rows got only
  two searches (see their summaries).
- Sweep summaries quote their sources' claims. Only rows marked *replayed* or
  *spot-checked* carry this session's own verification.
- Suggested ledger actions (for the curator, not done here): retire #106, #547
  and #548 from the board's target and trap tables; re-point the T3 rows for
  #156, #302, #376, #451, #1005, #1062 and #1095 at their next open cells after
  reading the sources; mark #773 and #864 as externally reported.

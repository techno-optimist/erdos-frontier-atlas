# Portable RH-work audit archive

This is **preservation of historical model audits**, not a new mathematical audit,
human peer review, formal verification, literature update, or proof of RH.
The mathematical claims and qualifications in the archived reports have not been
rewritten. Only filesystem locators and explicitly documented Python input paths
were made portable. All paths below are relative to this directory.

## What is covered

All **10 logical workspaces** in the predecessor's completed inventory are
accounted for: **264 original files, 107 preserved and 157 omitted**. All 264
originals and all 148 saved raw copies matched their pinned SHA-256 values before
packaging. The predecessor's 10 first-party reference snapshots also matched;
three are included as real, byte-identical replay inputs. The other root
integration documents remain outside this archive's ownership.

| Workspace | Main substantive report | Preserved / omitted originals | Checker replay |
|---|---|---:|---|
| `gm-candidate` | [audit.md](gm-candidate/audit.md) | 12 / 27 | 1 passed |
| `crt-variance` | [audit-report.md](crt-variance/audit-report.md) | 11 / 23 | 3 passed; 1 source-dependent |
| `mellin-transfer` | [audit.md](mellin-transfer/audit.md) | 5 / 0 | 1 passed |
| `phase-transfer` | [audit.json](phase-transfer/audit.json) | 6 / 5 | 2 passed |
| `gm-first` | [report.md](gm-first/report.md) | 6 / 0 | 1 duplicate-copy replay passed; independent checker source-dependent |
| `gm-second` | [report.md](gm-second/report.md) | 13 / 3 | 2 passed |
| `mobius-factorization` | [report.md](mobius-factorization/report.md) | 14 / 22 | 1 source-dependent |
| `twisted-square` | [report.md](twisted-square/report.md) | 15 / 67 | 1 passed |
| `mobius-typeI` | [report.md](mobius-typeI/report.md) | 13 / 7 | 1 passed |
| `sparse-square` | [report.md](sparse-square/report.md) | 12 / 3 | 1 duplicate-copy replay passed; independent checker source-dependent |

The three substantive `twisted-square/audit-*.md` report components and its
`open-target.md` are also preserved. Verdicts, compact historical checker outputs,
source locators, citation ledgers, short relevant source excerpts and historical
integrity receipts remain with their workspaces. Byte-identical copied reports
are mapped to canonical public copies in `MANIFEST.json`; distinct historical
first-party baseline snapshots are retained, not silently replaced by the latest
root document.

### Mathematical scope that must survive the archive

- The GM/GMRR work records a **model-audited deduction to
  `H <= X^(4/7-epsilon)`** from explicitly named analytic theorem inputs, with
  positive epsilon margins, endpoint treatment, centering and recombination.
  It is neither a novelty/current-record claim nor reconstruction of the deep
  input proofs. Read `gm-first` and `gm-second` with the candidate: their endpoint
  repairs and narrower interpretation of the scalar-majorant ceiling remain
  essential. That ceiling is **not an arithmetic impossibility barrier**.
- CRT/Haar bounds and fixed-window limits are not uniform growing-window
  estimates on the actual finite interval. The Mellin audit retains normal
  convergence, compact initial terms, support and small-scale qualifications,
  and the invariant **open** zero-free strip. A single fixed exponent above the
  partial-strip threshold is not an RH proof.
- The Möbius result is a saving for the **long-factor Type I subfamily**, with
  its fixed ambient constants and sharp-cutoff qualifications, not a saving for
  the complete mixed moment.
- The sparse-square report and Sections 1–4 review cover the **full signed
  arithmetic diagonal**, including distinct-root collisions. Its scale
  `T log(T)/D` is not a lower bound for the original mixed moment. The required
  signed oscillatory off-diagonal saving is still an **unproved target**.
  The independent Sections 1–4 review does not certify the candidate's entire
  literature survey.

## Integrity and provenance

- [MANIFEST.json](MANIFEST.json) gives a disposition for **every original**,
  original SHA-256/size, public SHA-256/size where present, omission reason,
  aliases, reference snapshots, checker dependencies and path-only edit records.
  Removed private path tokens are represented by their own SHA-256, logical
  meaning, occurrence count and line numbers—not by a private path leak.
- [SHA256SUMS](SHA256SUMS) pins every published file other than itself, including
  the manifest. Verify from this directory with `shasum -a 256 -c SHA256SUMS`
  (or `sha256sum -c SHA256SUMS`). Hash integrity is not semantic verification.
- [REPLAY.json](REPLAY.json) and [REPLAY.md](REPLAY.md) describe the **original
  packaging replay**, separately from the historical outputs in each workspace.
  [PRESERVATION_CHECKS.json](PRESERVATION_CHECKS.json) records that packaging's
  preservation/hygiene checks. Later maintained-harness repairs and their fresh
  replay are recorded separately in
  [HARNESS_MAINTENANCE.json](../HARNESS_MAINTENANCE.json). Original reports,
  historical checker sources, the inventory manifest and saved replay records
  are not rewritten when the maintained runner changes.
- Historical embedded hashes, byte counts, dates and `passed` fields still
  describe the **original reviewed snapshots**, not their path-edited public
  copies. They were intentionally not updated to manufacture historical passes.
  `MANIFEST.json` is the mapping between those two byte representations.
- Logical paths such as `gm-candidate/...` are archive-root locators. `<repo>`
  denotes the enclosing research repository. `<excluded-tool>`,
  `<excluded-cache>` and `<excluded-browser-workspace>` are explanatory locator
  labels only: **no files or synthetic source placeholders are created there**.
  Original report statements that a primary text was saved describe the old
  workspace, not the contents of this compact archive.

### Sources without bundled manuscripts

The source version URLs, equation/page/line locators, short quotations and
original source hashes remain in each workspace's `citations.json` (or
`ledger.json` / `sources-ledger.json`), `source-locators.json`,
`primary-manifest.json`, `source-manifest.json`, `evidence.json`, relevant excerpt
files and `twisted-square/retrieval.jsonl`, as applicable. The inventory separately
pins all excluded source-file bytes. These records include GM `2405.20552v2` and
GMRR `2006.04060v2`; no uninspected publisher-final replacement was fetched.
The metadata is historical, not evidence that an URL is reachable today.

No full third-party PDF, TeX manuscript/archive, full-text extraction, browser or
page-image capture, cache, source-fetch pipeline or private infrastructure path
is included. Detailed omission reasons are exhaustive in `MANIFEST.json`:

- 122 source/capture/extraction/fragment/version-diff files;
- 16 fetch/extraction/citation/report-assembly helpers;
- 7 copied reports and 2 byte-identical historical output files;
- 2 regenerable phase-record arrays (summaries and fresh full-array digests kept);
- 7 raw search/retrieval job files (the reports, version URLs and retrieval
  metadata are kept);
- 1 malformed extraction-stdout file named `.json`, which contains extra data
  after a JSON value. It is pinned and omitted, **not repaired**.

## Replay safely

**Do not run archived checkers in place:** most write beside themselves. Use the
runner, which copies only each checker and its explicit dependencies into a new
external per-case scratch directory. It never seeds old result files, downloads
sources, removes mathematical gates, or writes into the archive.

From this directory, using Python 3.11 and its standard library:

```sh
scratch="$(mktemp -d)"
python3 -B replay.py --output "$scratch/run"
```

The output directory must not exist and must be outside the checkout. Each
checker has a **180-second timeout**. Raw stdout/stderr and every generated result
remain in that scratch directory. Its `REPLAY.json` and `replay/` hold the portable
record: output edits replace only the exact scratch-root token with `.`, including
its literal UTF-8 and JSON-escaped representations. Original/public hashes and
encoding-specific edit counts are recorded. Child `PYTHONOPTIMIZE` is explicitly
set to `0`, so inherited optimization cannot disable historical assertions.
A different run's time, scratch-token hashes and timings naturally differ.

The saved package replay has **13 executions passed, 0 failures, 0 timeouts**;
these cover **11 distinct original checker hashes**, with 2 duplicate-copy runs.
**4 preserved checkers were not replayed** because they combine finite arithmetic
with excluded source/citation dependencies:

| Checker | Excluded dependency / exact limitation |
|---|---|
| `crt-variance/finalize.py` | Requires two historical browser JSON inputs and a private citation tool before the weighted-covariance checks. Its 8 weighted checks remain historical-only. |
| `gm-first/independent_checks.py` | Mandatory hashes of the GM/GMRR full PDFs and TeX sources. The separate copied candidate checker replay is not this independent audit. |
| `mobius-factorization/check_ledger.py` | Original manuscript/report byte checks and a fail-closed historical baseline-append check. Path-edited copies cannot impersonate those originals. |
| `sparse-square/independent_checks.py` | Mandatory membership checks for three excluded source archives and their three TeX members. Replaying the candidate's copied checker is not replaying this independent Sections 1–4 checker. |

These are explicit replay omissions, not failed mathematical assertions and not
newly confirmed historical passes. No arithmetic-only extraction or synthetic
source stand-in was used. The maintained harness suite (`python3 -B test_replay.py`)
includes the original real-checker smoke test and regressions for inherited
optimization and escaped scratch paths. Its poisoned-input fixtures are confined
to separate scratch copies. These software tests are not additional independent
mathematical audits; repository CI runs them through `tests/test_rh_audit_archive.py`.

The saved phase replay uses the predecessor-pinned final `RESULT.md` and
`MELLIN_TRANSFER.md` under `inputs/`; their hashes differ from the older hashes
embedded in the historical phase summaries. Its finite arrays match the old
arrays byte-for-byte. This snapshot change is recorded rather than hidden.
The actual-squarefree phase checker uses 70-digit Decimal arithmetic with
explicit tolerances; the Type I checker also contains floating-point phase
diagnostics. These mixed numerical checks must not be called wholly exact.

## Preservation workflow

For an extension, first pin and verify the actual source bytes outside the
repository; select reports/checkers explicitly; retain all omitted source hashes;
apply only a recorded path allow-list; replay only complete standalone scripts in
new scratch with timeouts; compare fresh output to historical output and record
any difference; rehash original inputs and publish a separate public checksum
manifest. Do not edit a claim, remove a gate, create an absent source or merge
historical and fresh verdicts to make an archive appear more reproducible.

The original preservation task wrote only under `audits/` and made no root
integration or publication claim. Subsequent integration is tracked in the
[repository progress map](../../astra-rh-969-20260912/REPOSITORY_STATUS.md);
maintained-harness changes are separate from the preserved historical evidence.

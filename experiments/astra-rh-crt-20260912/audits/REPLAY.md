# Saved finite-checker replay

Interpreter: Python **3.11.16**, standard library only. Started `2026-09-13T05:18:18.550222+00:00`; finished `2026-09-13T05:18:28.882030+00:00`.

**13 checker executions passed; 0 failed; 0 timed out; 0 input-integrity failures.** Four additional preserved checker files were not invoked because of excluded source dependencies. The executions include two byte-identical copied checkers, so they represent **11 distinct original checker hashes**, not 13 independent mathematical audits.

Every command below was run with relative script arguments from a separate new per-case scratch directory. `REPLAY.json` records that relative working-directory label, actual exit code, 180-second timeout, elapsed time, copied input hashes, generated output hashes, and any runtime path-only sanitization. Raw streams and full outputs remain in external scratch; public streams retain their original and public hashes. No historical result file was seeded into a replay directory.

| Checker | Exit | Seconds | Actual stdout |
|---|---:|---:|---|
| `gm-candidate/check_exponents.py` | 0 | 0.023189 | [stdout](replay/01-gm-candidate--check_exponents/stdout.txt) |
| `crt-variance/audit.py` | 0 | 4.909287 | [stdout](replay/02-crt-variance--audit/stdout.txt) |
| `crt-variance/endpoints.py` | 0 | 0.165365 | [stdout](replay/03-crt-variance--endpoints/stdout.txt) |
| `crt-variance/r-free.py` | 0 | 0.451577 | [stdout](replay/04-crt-variance--r-free/stdout.txt) |
| `mellin-transfer/verify_arithmetic.py` | 0 | 0.034627 | [stdout](replay/05-mellin-transfer--verify_arithmetic/stdout.txt) |
| `phase-transfer/check_arithmetic.py` | 0 | 3.437503 | [stdout](replay/06-phase-transfer--check_arithmetic/stdout.txt) |
| `phase-transfer/check_actual_intervals.py` | 0 | 1.020488 | [stdout](replay/07-phase-transfer--check_actual_intervals/stdout.txt) |
| `gm-first/original_check_exponents.py` | 0 | 0.024872 | [stdout](replay/08-gm-first--original_check_exponents/stdout.txt) |
| `gm-second/check_second_audit.py` | 0 | 0.024257 | [stdout](replay/09-gm-second--check_second_audit/stdout.txt) |
| `gm-second/compare_critical_bounds.py` | 0 | 0.030433 | [stdout](replay/10-gm-second--compare_critical_bounds/stdout.txt) |
| `twisted-square/check_algebra.py` | 0 | 0.028240 | [stdout](replay/11-twisted-square--check_algebra/stdout.txt) |
| `mobius-typeI/independent_checks.py` | 0 | 0.102677 | [stdout](replay/12-mobius-typeI--independent_checks/stdout.txt) |
| `sparse-square/replayed-original/check_algebra.py` | 0 | 0.025174 | [stdout](replay/13-sparse-square--replayed-original--check_algebra/stdout.txt) |

## Finite support actually returned

- CRT: 198 direct cases and 8414 rational recurrence/monotonicity cases; 144 floor-discrepancy cases, 288 real endpoint cases and 260 conditional fibers.
- r-free: 155 direct and 3872 rational real-length cases across the recorded exponents. The separate 8 weighted-covariance cases belong to the **unreplayed** historical finalizer.
- Phase: **13151 exact rational records**: arbitrary_interval=480; conditional_fiber=12204; direct_phase=317; norm_transfer_exact=60; refinement_and_defect=90. The 5 recorded shortcut-negative controls remain intact.
- Actual squarefree intervals: 396 **Decimal diagnostic cases**, including 198 with period at most X; precision 70 and assertion tolerance `1e-55`. This checker also has exact rational segmentation and an exponent ledger, but is not wholly exact.
- Mellin: K=1..16: moments, monomials, leading error all passed. The saved output also records rational parameter, invariant-strip, abstract countermodel and antiderivative checks; these are not proofs of the analytic hypotheses.
- GM second audit: 21 positive polynomial certificates, with the majorant and exhausted-loss negative gates returning `False` and `False`. The critical comparison independently checked 8 parent margins and 3 polytopes.
- Möbius Type I: 28 identity cases; 1728 full-identity coefficients; 70 sharp-split cases; 1547 sharp-block coefficients; 12278 tuple assignments; 528 canonical intervals. Its 18 floating-point phase checks are noncertifying diagnostics, not exact arithmetic.
- Sparse-square candidate: 7 finite full-block Gram/collision cases and 29 rational exponent entries. Assertions use exact integers/Fractions; displayed `D_times_Q` values are floating conversions. The copy under `sparse-square/replayed-original/` ran separately but is the same candidate checker, **not** the independent Sections 1–4 checker.

Do not add these heterogeneous, overlapping counts into a purported theorem-verification total. Every original domain, assertion and negative control is left in its checker. No analytic source proof or missing signed moment estimate is tested here.

## Comparison with the historical receipts

All fresh JSON values match the preserved historical JSON except the following explicitly recorded metadata fields:

- Both phase summaries: `input_hashes.RESULT.md` and `input_hashes.MELLIN_TRANSFER.md`. This run used the actual predecessor-pinned final first-party snapshots in `inputs/`; it did not recreate the earlier document versions named by the historical summaries.
- `gm-second/critical-comparison.json`: `parent_input` is now a relative scratch locator. The parent input SHA-256 and all arithmetic values match.
- `mobius-typeI/checks-summary.json`: `checks_path` is now a relative scratch locator.

The two omitted full phase arrays were regenerated in fresh scratch and match their original historical bytes exactly:

| Output locator | Records | SHA-256 |
|---|---:|---|
| `phase-transfer/check_records.json` | 13151 | `2935981f4d281554875f14ea97583e4b2988b20c7763903dc5f371fe6220d3b3` |
| `phase-transfer/actual_interval_records.json` | 396 | `87702ee5b55ca549cdf6a9425066ea70a096012a6e9f5cc9f56aec41b32424d8` |

The compact archive saves their summaries and full-array hashes; the runner retains both complete arrays externally and can regenerate them. All other generated result JSON files and actual stdout/stderr are saved under `replay/`.

## Not replayed

The following are preservation/dependency omissions, not successful replays or newly observed assertion failures:

### `crt-variance/finalize.py`

Historical weighted-covariance checker is interleaved with citation/source assembly. It first requires excluded browser-workspace JSON and the excluded citation tool; no arithmetic-only extraction or bypass was made.

Dependencies: `excluded-browser-workspace/rh-crt-primary-0.json`, `excluded-browser-workspace/rh-crt-primary-1.json`, `excluded-tool/sources.py`.

Historical result only: [crt-variance/verification-summary.json](crt-variance/verification-summary.json).

### `gm-first/independent_checks.py`

Exact arithmetic is followed by mandatory hashes of four excluded full primary manuscripts. The checker is preserved without removing or satisfying those gates synthetically.

Dependencies: `gm-candidate/gmrr-source/squfv.tex`, `gm-candidate/gm-source/LargevaluesDirichlet17.tex`, `gm-candidate/gmrr-v2.pdf`, `gm-candidate/gm-v2.pdf`.

Historical result only: [gm-first/independent-results.json](gm-first/independent-results.json).

### `mobius-factorization/check_ledger.py`

Exact arithmetic is interleaved with original-source integrity and a fail-closed historical baseline append check. Excluded manuscript inputs and original reviewed report bytes are not reconstructed from path-edited public copies.

Dependencies: `gm-candidate/gmrr-source/squfv.tex`, `gm-candidate/gm-source/LargevaluesDirichlet17.tex`, `gm-candidate/gmrr-source/squfv.bbl`, `original-reviewed-report-bytes`.

Historical result only: [mobius-factorization/checks.json](mobius-factorization/checks.json).

### `sparse-square/independent_checks.py`

Finite arithmetic and noncertifying floating-point diagnostics are followed by mandatory primary archive/TeX membership checks. Six full primary files are excluded; no synthetic archive or partial execution was substituted.

Dependencies: `twisted-square/primary/bcr-v1.src`, `twisted-square/primary/bcr-v1/main.tex`, `twisted-square/primary/lr-v1.src`, `twisted-square/primary/lr-v1/draft.tex`, `twisted-square/primary/gmrr-v2.src`, `twisted-square/primary/gmrr-v2/squfv.tex`.

Historical result only: [sparse-square/independent-checks.json](sparse-square/independent-checks.json).

## Runner smoke test

The packaging harness was tested with one real preserved candidate checker in separate disposable scratch (`python3 -B test_replay.py`): **1 test passed**. That auxiliary invocation is excluded from the 13 package-replay executions above and is not another independent mathematical audit.

The archive records bounded computations and historical model-audit deductions. It makes no formal-verification, new mathematical, novelty, current-literature or RH claim.

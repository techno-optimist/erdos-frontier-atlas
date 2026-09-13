# RH / P969 — repository progress map

**Research, not an RH proof.** This is the shared entry point for both RH
bundles. It attaches the work to `P969` and the existing surface
`S:gap:969:c2325929` without modifying the production attack graph, a canonical
problem status, or a frozen certificate.

## What is preserved

| Method / result | Read | Boundary |
|---|---|---|
| Global squarefree-energy / RH equivalence | [ANALYTIC_TARGET.md](ANALYTIC_TARGET.md) | Model-reviewed informal proof using named classical inputs; the unconditional energy estimate is unproved |
| Generic reciprocal-square cancellation obstruction | [RESULT.md](RESULT.md) | One fixed infinite non-Möbius sequence; bounded exact replay is separate from the unbounded proof |
| Finite-prime phase variance and centered-defect transfer | [CRT RESULT.md](../astra-rh-crt-20260912/RESULT.md) | Product-phase control is not the required actual finite-interval defect-energy bound |
| Integer-increment to Mellin continuation | [MELLIN_TRANSFER.md](../astra-rh-crt-20260912/MELLIN_TRANSFER.md) | Conditional continuation, not convergence of the original integral; a fixed exponent gives only its invariant strip |
| GM/GMRR assembled variance deduction | [GM_TRANSFER.md](../astra-rh-crt-20260912/GM_TRANSFER.md) | Model-audited deduction through `4/7-epsilon` from pinned external inputs; no novelty, current-record, or expert-review claim |
| Sharp long-factor Type I operator | [ARITHMETIC_FRONTIER.md](../astra-rh-crt-20260912/ARITHMETIC_FRONTIER.md) §§2–3 | The fixed `k=2` sharp representation split has a controlled part; the complete signed residual is still open |
| Entire signed diagonal and sparse-square interface | [ARITHMETIC_FRONTIER.md](../astra-rh-crt-20260912/ARITHMETIC_FRONTIER.md) §§4–6 | Full-block diagonal scale is not a lower bound for the full mixed moment; unsigned counts do not prove signed cancellation |
| Source freshness and review provenance | [FRESHNESS.md](FRESHNESS.md), [CRT review intake](../astra-rh-crt-20260912/REVIEW_STATUS.json) | Source snapshot dated 2026-09-12; model, finite, human and formal evidence remain separate |

The predecessor [P327 multiplier-sensitive fiber method](../astra-327-fiber-20260912/README.md)
is published separately in [PR #155](https://github.com/techno-optimist/erdos-frontier-atlas/pull/155),
stacked on #154 at commit `68f6d12cc172bf2fe40ebb4baa71836fcaf8bcdc`.
Its GitHub `fast-claim-gate` passed; the scheduled/manual-only `receipt-drift`
job was skipped as configured for a PR. It is not merged or folded into an RH
proof claim.

## Find the work through the substrate

```sh
python3 tools/query_substrate.py for 969
python3 tools/query_substrate.py for 327
python3 tools/query_substrate.py methods
python3 -I -B experiments/astra-substrate-20260911/verify.py
```

The [source ledger](../../atlas/substrate.json) and its generated
[board](../astra-substrate-20260911/BOARD.md) expose each proved or conditional
operator and its remaining obligations. `discharges` means a limited reviewed
lemma or interface, not that P969 or RH is solved. The RH selectors are restricted
to P969; no prime-tag or shared-sequence neighbor inherits a theorem.

## Replay from the repository root

```sh
python3 -I -B experiments/astra-rh-969-20260912/verify.py
python3 -I -B -m unittest discover -s experiments/astra-rh-969-20260912 -p 'test_*.py' -v
python3 -I -B experiments/astra-rh-crt-20260912/verify.py experiments/astra-rh-crt-20260912/receipt.json
python3 -I -B -m unittest discover -s experiments/astra-rh-crt-20260912 -p 'test_*.py' -v
uv run --python 3.11 --with-requirements requirements-dev.lock make audit-fast
```

`tests/test_rh969.py`, `tests/test_rh_crt.py`, `tests/test_rh_audit_archive.py`,
and `tests/test_substrate.py` wire the bounded semantic checks, fixed CRT cohort,
standalone/no-producer replay, poisoned-evidence rejection, method-discovery
boundaries, audit-file integrity and scratch-only archived-checker replays into
repository CI. The original producer/verifier snapshots are preserved. Default
semantic replay does not emit or replace evidence.

The [portable independent-audit archive](../astra-rh-crt-20260912/audits/README.md)
accounts for every pinned source file and reports excluded dependencies, exact
versus floating diagnostics, distinct checker hashes and duplicate executions
separately. The [parent preservation check](../astra-rh-crt-20260912/audit-preservation-verification.json)
reconstructed all 74 declared path edits and compared all 264 original files
against their pins; no substantive research text was changed by those edits.

## Integration record

The corrected integration on `agent/astra-rh-969-20260912`, stacked after the
P327 method commit, passes `make audit-fast`: **227 passed, 2 skipped** under
Python 3.11.16. The [publication gate record](repository-verification-publication.json)
contains the actual commands/output, both semantic replays and the substrate
check. All **676 protected tracked paths** match the base commit, and all
**33 submitted Python sources** match their review snapshot before and after
the gate. Both independent software reviews have passed. The
[combined review record](SOFTWARE_REVIEW.json) reconciles their disjoint 13-file
live-code and 20-file archive scopes against all 33 submitted Python files.
Publication and remote CI verification are a separate subsequent step.

The [earlier 170-pass gate](repository-verification.json) and
[intermediate 180-pass gate](repository-verification-hardened.json) are retained
as historical snapshots, not overwritten. Passing those tests did not prevent
the independent reviews from finding the defects below.

Independent pre-commit software review found receipt-parser defects missed by
that gate: duplicate JSON keys could hide a scope contradiction, and deeply
nested JSON bypassed the normal negative machine verdict. Both are repaired,
with failing-before/passing-after tests under normal and optimized Python. The
[parent replay record](PARSER_FIX_VERIFICATION.json) authenticates the repaired
source hashes, confirms the semantic/domain code is unchanged, and records all
12 standalone tests passing in each mode without changing receipt bytes. CI
now also guards the exact floor cohort, the complete four-source historical CRT
review map, and explicit non-human/non-formal scope qualifications. The README
has been refreshed and its inventory and entry points have regression guards.

The separate twenty-file archive review found inherited `PYTHONOPTIMIZE` could
disable historical assertions, and JSON-escaped scratch roots could survive in
outputs labeled public. Both maintained-harness defects are repaired. The
[parent maintenance record](../astra-rh-crt-20260912/HARNESS_MAINTENANCE.json)
records six passing harness tests and a fresh 13-checker replay under inherited
optimization and Unicode/quote/backslash scratch paths. Follow-up review found
that duplicate inputs rejected before launch were still counted as executions;
both missing-source and hash-mismatch controls now reject with zero attempted,
duplicate and distinct-executed counts. Successful replay totals remain 13 runs,
2 duplicate copies and 11 distinct original checker hashes. The
[earlier maintenance receipt](../astra-rh-crt-20260912/HARNESS_MAINTENANCE_INITIAL.json)
is preserved separately.

All 17 historical checker sources, the inventory manifest and saved historical
replay remain unchanged. Only the maintained runner/test checksum entries were
updated in this correction. The repaired archive snapshot has now passed its
fresh independent review. No historical arithmetic, claim or fixed receipt was
rewritten to clear a software gate.

The README anchor guard now ignores top-level fenced code. Its 50 tests cover
backtick and tilde fences, invalid closers and real anchors outside the fences;
the guard is not a complete CommonMark parser. The
[final thirteen-file live-code review](LIVE_CODE_REVIEW.json) passed with no
security or logic findings. The [parent intake](LIVE_CODE_REVIEW_INTAKE.json)
reconciles every reviewed source and complete native diff against the staged
files, authenticates the verdict and its supporting records, and preserves the
path-only public copy. The review records 94 supplied test nodes and 10 adverse
control groups; it is software review, not an analytic proof audit.

The [final twenty-file archive review](../astra-rh-crt-20260912/ARCHIVE_CODE_REVIEW.json)
also passed with no security or logic findings. Its
[parent intake](../astra-rh-crt-20260912/ARCHIVE_CODE_REVIEW_INTAKE.json)
authenticates the complete verdict, 32 bounded commands and their supporting
records. Four archive CI tests, six harness tests and ten adverse-control groups
passed. Fresh replay passed all 13 executions; the parent independently
recomputed the 11-distinct/2-duplicate totals and reconstructed all public
output transformations. The four source-dependent checkers remain explicitly
unreplayed; review of their source is not execution of their source gates.

Historical Markdown excerpts/report components retain their byte-pinned trailing
whitespace; the exact six-file exception is disclosed in the gate record. No code
or maintained research note is exempted from the whitespace check.

Historical `execution.json` and review-intake fields describe their original
runs and snapshots. They do not override a newer integration record. Private
review-workspace paths are removed only with original/published hashes and
explicit transformations retained; complete third-party manuscripts are not
relicensed into the repository.

## The next mathematical obligation

A fixed saving for the **whole** Möbius–zeta mixed moment near
`D=T^(5/6)`, or equivalently for the exact remaining signed residual after the
controlled Type I part, is still missing. A variance extension also needs the
specified open-neighborhood, mask, height, endpoint, tail and centering
uniformity. The diagonal and Type I decompositions are complementary analyses
of the same moment, not disjoint positive pieces to add.

The global RH-equivalent energy estimate and the actual centered-defect energy
estimate also remain unproved. No RH proof, unconditional new zero exclusion,
canonical status change, formal kernel certificate, or human peer review is
claimed by this repository update.

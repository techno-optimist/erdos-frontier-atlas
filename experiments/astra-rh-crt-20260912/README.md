# RH lane: arithmetic phase deflation and Mellin transfer

This is a research extension of the P969 lane. It contains explanatory
operators and explicit remaining obligations, **not an RH proof**. The
Guth–Maynard/GMRR transfer now has a reconciled research deduction of an
unconditional `4/7-epsilon` variance range from named analytic inputs; it is not
an expert-reviewed result or a novelty/current-record claim.[3][5]
Classical squarefree correlation and variance antecedents are identified in
the CRT notes.[1][2] The CRT and Mellin operators have separate scopes and
unresolved hypotheses.

## Read in this order

1. `GM_TRANSFER.md`: the full variance deduction, including localization,
   actual endpoint squares, and one aggregate epsilon budget.
2. `ARITHMETIC_FRONTIER.md`: the exact sharp Type I reduction, entire signed
   diagonal, actual unsigned-core obstruction, and the joint estimate still open.
3. `RESULT.md`: positive CRT variance, normalized prime refinement, and the
   transfer to actual centered defect energy with its finite-period cost.
4. `MELLIN_TRANSFER.md`: conditional continuation, numerator cancellation,
   the invariant zero strip, and the generic sharpness limitations.
5. `receipt.json`, `kernel.py`, `verify.py`: bounded exact operator replay
   with an independent direct-period verifier.
6. `REVIEW_STATUS.json`, `code_review.json`, `typeI_review.json`, and
   `diagonal_review.json`: review provenance and the necessary qualifications.
7. `gm_parameter_check.json`, `mellin_arithmetic.json`, and `execution.json`:
   finite algebra, actual RED/GREEN runs, and replay output—not analytic proofs.
   Checkout paths in the execution record are replaced by `<repo>`; no missing
   output is synthesized.

The independent CRT mathematical model audit passed the positive formula,
real-phase interpretation, normalized refinement, and r-free extension. Parent
scratch checks also reproduced explicit failures of raw-variance monotonicity
and finite-sample density-normalized monotonicity, and an exact weighted
covariance identity. See `REVIEW_STATUS.json` for scope and pinned review hashes.

Both independent analytic audits passed the **full variance deduction for
`H<=X^(4/7-epsilon)`**, using `z=H^(5/4+epsilon)` and the pinned theorem inputs.
This is distinct from the `4/7` range already present for just one component
of GMRR's proof.[3][5] `GM_TRANSFER.md` incorporates the required localization,
the separate squares above `2X`, low-H coverage, full epsilon budget, and
centering correction. Both audit scripts passed isolated parent replays.

The `4/7` ceiling is only a limitation of the specified sufficient estimates,
not a genuine arithmetic obstruction. The deduction gives no new zero exclusion
through the generic Mellin route. The deep analytic input proofs, novelty,
current-record status, and optimality of other methods are not certified.

The Mellin transfer and its strict-strip noncancellation argument passed
independent mathematical model review, with the continuation, endpoint, and
fixed-exponent limitations retained. Its arithmetic script was replayed in an
isolated copy without altering the review inputs. The additional generic
sharpness corollary is identified as a parent derivation, not a new squarefree
estimate. See `MELLIN_TRANSFER.md` and `REVIEW_STATUS.json`.

The supplemental actual-integer transfer audit also passed, including both
directions of the RH-equivalent defect criterion. Its exact-arithmetic script
was replayed in an isolated copy; saved records were recounted and checked for
duplicates. The review's separate high-precision actual-squarefree checks remain
explicitly numerical and were not included in that exact replay.

The complete code-review verdict passed with no blocking security or logic
findings. Its four-file coverage, line ranges, and source hashes were checked
against the unchanged snapshots; see `code_review.json`. The additional test
hardening suggestions are nonblocking, and the executable snapshot is unchanged.
The shipped receipt covers integer H only; model review is not human peer review
or formal verification. Audit-script checks of fractional phases and r-free
filters are separate from that receipt.

## What is established, and what is not

| Item | Scope |
|---|---|
| Positive divisor expansion | Self-contained informal finite-prime proof |
| Unit-constant square-root phase variance | Uniform in the finite prime set; not automatically an empirical estimate |
| Orthogonal refinement | Normalize by each filter's density; condition on prime coordinates, not temporal mixing |
| Periodicity cost and defect transfer | Explicit norm inequality; the needed actual defect-energy bound is unresolved |
| GM/GMRR full variance transfer | Research deduction from named inputs; two independent analytic model audits passed |
| Mellin continuation and zero strip | Conditional on a variance hypothesis; no unconditional new zero exclusion |
| Sharp long-factor Type I saving | Audited partial operator with common shifts and sharp-cutoff losses paid; the whole residual bound is open |
| Entire signed diagonal | Audited full-block scale `T log(T)/D`; not a lower bound for the full moment |
| Unsigned near-core lower bound | Genuine integer-cloud count; obstruction to the specified absolute majorant, not to signed cancellation |
| Exact receipt | Fixed bounded implementation replay; not all-parameter certification |
| Reviews | CRT, Mellin, norm-transfer, both GM-transfer analytic audits, and the complete four-file software review passed within their respective scopes |
| Repository integration | See [current progress map](../astra-rh-969-20260912/REPOSITORY_STATUS.md); no canonical problem-status promotion, production-graph modification, or proof submission |

## Standalone replay

From this directory (Python with `fractions` and `math.isqrt`; stdlib only):

```sh
python3 -I -B -m unittest discover -s . -p 'test_*.py' -v
python3 -I -B verify.py receipt.json
```

The verifier is read-only and never imports `kernel.py`. It constructs the
periodic square-filter pattern and uses a sliding window to compute exact
first and second moments. The producer instead uses the divisor formula.
The tests have a separate prefix-sum/direct-enumeration oracle.

To emit a **new** receipt explicitly, choose a path that does not exist:

```sh
python3 -I -B kernel.py --emit new-receipt.json
python3 -I -B verify.py new-receipt.json
```

Emission refuses to overwrite a file. Default replay never regenerates evidence.

When using the delivered archive, run these commands inside the extracted
packet directory. Only this experimental subdirectory is included—not the
full repository or earlier RH bundle. `MANIFEST.sha256` covers the packet's
payload files. A separate delivery receipt records the fresh-extraction replay.
That standalone archive is a historical delivery, not the full repository.
The repository integration preserves selected independent audit reports and
checkers under [`audits/`](audits/README.md), with source/archive hashes and explicit
portability limits. Full primary-source payloads remain excluded. The archive
accounts for 264 original entries: 107 preserved and 157 explicitly omitted.
Its 13 runnable checker executions pass (11 distinct source hashes and two
duplicate-copy executions); four checkers with excluded mandatory source
inputs remain labeled **not replayed**. `audit-preservation-verification.json`
records the parent's byte-for-byte reconstruction of every declared path edit.
These finite checks and integrity tests do not establish the analytic theorems.

From the repository root, create a fresh external replay directory:

```sh
python3 -B experiments/astra-rh-crt-20260912/audits/replay.py --output /tmp/rh-audit-replay-new
```

The output directory must not already exist; replays never run generators
inside this archive or replace its historical receipts.

### Replayed cohort and domain

The producer's prime sets are `[]`, `[2]`, `[3]`, `[2,3]`, `[2,5]`, `[3,5]`,
and `[2,3,5]`. Its lengths are `0,1,2,3,4,9,16,36,900,10**30+2`.
The independent replay returned **70 cases across 7 distinct prime sets**.
The very large length checks exact whole-period reduction, not a new numerical
frontier. The producer's expected parameter set is checked separately from the
semantic verifier, which accepts any valid sorted cohort of 1–128 cases and
reports its actual count. Passing that general gate alone does not establish
the producer's fixed 70-case coverage.

The executable kernel limits prime lists to 12 entries, primes to at most 97,
and exact parameters to 512 bits. The direct verifier additionally caps the
period at 100000, sampled cases at 128, and receipt size at 256 KiB. Its selected
adverse phase is restricted to one period. These are replay resource limits,
**not hypotheses of the mathematical theorems**.

Controls reject false moments, noncanonical rational strings, floats, duplicate
or composite primes, incorrect totals, repeated cases, scope/RH promotion,
resource excesses, duplicate JSON keys, and deep malformed JSON. The valid and
invalid paths use the same semantic gate. Read-only and no-overwrite behavior
are exercised by real CLI subprocesses, not mocks.

## Arithmetic follow-up (audits reconciled)

`ARITHMETIC_FRONTIER.md` records the independently audited sharp Type I
partial saving, full signed-diagonal calculation, and genuine unsigned-core
lower bound with their exact limitations. Both adversarial checker scripts
passed isolated parent replays. Floating-point phase/weight diagnostics are
explicitly noncertifying.

The Type I result applies to the actual sharp representation split, not merely
a smooth surrogate. The diagonal lower scale is for the full Möbius block and
fixed nonzero nonnegative shell weight—not arbitrary masks or the full moment.
The AFE weight changes sign. The unsigned lower bound concerns its specified
counting majorant, not the signed moment.

The whole residual and aggregate signed off-diagonal saving remain **unproved**.
No full-moment saving or variance range beyond `4/7-epsilon` was established.
The two decompositions must not be added as disjoint positive contributions.
See `typeI_review.json`, `diagonal_review.json`, and `REVIEW_STATUS.json`.[3][6][7]

The second complete software review also passed and matched all four source
and snapshot hashes. Its additional probes are reviewer-reported, not
another parent execution.

## Working boundary

The current [repository progress map](../astra-rh-969-20260912/REPOSITORY_STATUS.md)
covers both RH bundles, additive substrate entries, and CI replay hooks. It
supersedes the earlier local-only integration boundary, not the mathematical
limitations. `REVIEW_STATUS.json` and `execution.json` retain the historical
review/replay facts; their no-commit fields describe those earlier runs.

`portability.json` pins the original and path-sanitized root verdicts. Tokens
such as `<historical-typeI-audit>` identify original review-workspace locations,
not public runnable paths; the selected public reports/checkers are indexed in
`audits/README.md`. Original verdicts are retained outside the repository.
The public copies change paths only, not conclusions, counts, or qualifications.
Repository gates do not formalize or human-peer-review the analytic arguments.

## Sources

[1] https://arxiv.org/html/1112.4691v2
[2] https://arxiv.org/html/2112.12234v1
[3] https://arxiv.org/html/2006.04060v2
[5] https://arxiv.org/pdf/2405.20552v2 — Guth–Maynard, New large value estimates for Dirichlet polynomials, v2
[6] https://dlmf.nist.gov/25.9
[7] https://arxiv.org/pdf/1411.7764v1

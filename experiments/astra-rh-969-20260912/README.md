# RH / P969 research lane

**Deliverable:** a precisely delimited analytic target and a generic
cancellation obstruction, not a proof of RH or a new squarefree error bound.

## Read in this order

1. **[FRESHNESS.md](FRESHNESS.md)** — current official status, September
   preprints, the published Guth–Maynard result, and formalization caveats.
2. **[ANALYTIC_TARGET.md](ANALYTIC_TARGET.md)** — a complete proposed proof,
   using named classical inputs, that RH is equivalent to
   `integral_1^X |Q(x)-x/zeta(2)|^2 dx = O_epsilon(X^(3/2+epsilon))`
   for every positive epsilon. The unconditional bound remains open.
3. **[RESULT.md](RESULT.md)** — the exact hyperbola transfer, a balanced-cell
   countermodel, a single infinite sequence attaining the generic pointwise
   exponent `2/5`, and an interval-persistence argument giving mean square
   `Omega(X^(8/5))` on a subsequence. These coefficients are not Möbius.

The method substrate has two additive entries: a generic obstruction and
an equivalence lemma. Neither changes the mathematical status of P969 or RH.
Production graph files, graph-building code, and frozen certificates were not
modified. No novelty, priority, human peer-review, or formalization is claimed.

## Why this is useful

The Atlas now names a precise remaining RH obligation instead of merely
linking two topics. It also rules out a tempting route: ordinary one-dimensional
square-root cancellation, on its own, cannot force either quarter-power error
or the required averaged bound for the square-divisor transform. A successful
argument along this route needs additional arithmetic structure or cancellation.

The analytically explicit unresolved step is, for every `delta>0`,

\[
 \sup_{Y\ge0}\int_0^Y
 |e^{-y/4}E(e^y)|^2e^{-2\delta y}\,dy<\infty,
 \qquad E(x)=Q(x)-x/\zeta(2),
\]

proved **without** RH or an equivalent assumption. Positive proportions of
critical-line zeros, finite samples, and vertical norms of a meromorphic
continuation do not discharge that obligation.

## Exact bounded replay

From this directory, with a supported Python interpreter:

```bash
python3 -I -B verify.py
python3 -I -B -m unittest discover -s . -p 'test_*.py' -v
```

The default verifier reads `receipt.json`, recomputes its reciprocal-square
cells by direct division rather than the producer's inverse-square-root
formula, and checks signs, prefix bounds, floor cancellation, rational phase
lower bounds, and explicit non-RH scope. It imports no producer and writes no
evidence. The tests submit poisoned receipts through the same gate and check
that rejection still works under `python -O`.

The producer writes **only when requested**, and refuses to overwrite:

```bash
python3 -I -B floor_transfer.py --emit NEW-receipt.json --h 4 8 12 16
python3 -I -B verify.py --receipt NEW-receipt.json
```

The tool's `4<=H<=64`, `H` divisible by four, domain is a resource ceiling,
not the theorem's range. Increasing it is unnecessary for the all-parameter
proof. Checks of the finite interval-jump lemma do not establish an infinite
subsequence or an analytic integral bound by sampling.

## Current verification and publication state

The current integration record is **[REPOSITORY_STATUS.md](REPOSITORY_STATUS.md)**.
It indexes this bundle, the [arithmetic continuation of the lane](../astra-rh-crt-20260912/README.md),
the repository gates, and the publication boundary. The user's repository-update
request supersedes the earlier timed-out integration approval.

- The default receipt and standalone unit checks have independent replay paths
  above; `tests/test_rh969.py` runs both from the repository suite.
- Independent model mathematical review passed on the four countermodel theorems
  and both directions of the mean-square equivalence, including interval
  persistence. See `review.json`; this is not human peer review or formal checking.
- `execution.json` is a **historical** execution record. One RED transcript was
  truncated. An earlier repository run had **161 passed, 2 skipped, 1 failed**
  because the generated research board lacked its final newline. These records
  are retained, not substituted for the current integration gate.
- The exact cell checks do not certify the unbounded analytic equivalence or its
  still-unproved unconditional energy hypothesis.

Human mathematical review and formalization remain separate from all model
reviews and finite exact checks.

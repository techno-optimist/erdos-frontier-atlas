# Erdős #699 — binomial-gcd, exhaustive to 10⁸

**Question** ([erdosproblems.com/699](https://www.erdosproblems.com/699), status
`FALSIFIABLE`): for every `1 ≤ i < j ≤ n/2`, is there a prime `p ≥ i` with
`p | gcd(C(n,i), C(n,j))`?

**What this certificate establishes:** the property holds for **every n with
`10⁷ ≤ n < 10⁸`** — all 90,000,000 rows, every `(i,j)` pair in each row decided
exactly, zero counterexamples, 119.53 core-hours.

```bash
python3 -I verify.py
```

## Honest framing

This is the **first exhaustive general-row sweep past `10⁷`**. It does **not** reach
virgin ground above `10⁸`: Cong Lu's January 2026 run already covered the
structured families `n = 2^k` (k ≤ 27) and `n = 3^m+1` (m ≤ 17) out to
≈`1.34×10⁸`. Our own triage had missed that until 2026-07-27 and said
"10⁷ → 10⁸" as though it were virgin ground; it is not.

It is also not a proof, and no finite sweep can be one — the conjecture is
believed true. The deliverable is a verified-to-N record, and it says nothing
above `10⁸`.

## Why it was affordable: two structural facts

**The prime-gap pruning.** If a prime lies in `(n−i, n]` it divides `C(n,i)`
and *every* `C(n,j)`, and it is `≥ i` — so the row is settled outright. A
counterexample therefore needs **no** prime in `(n−i, n]`, i.e.
`i ≤ n − prevprime(n)`. That collapses the `i`-range from `n/2` to the prime
gap below `n` — about 18 on average near `10⁸`, against `5×10⁷`.

**Candidate primes without factoring `C(n,i)`.** For `p > i`, `p ∤ i!`, so
`v_p(C(n,i)) = v_p(n(n−1)⋯(n−i+1))`. The candidates are exactly the prime
factors `> i` of `i` consecutive integers just below `n` — **factoring `i`
numbers, not scanning primes**. The single case `p = i` (i prime) falls to
Lucas. This replaces roughly 620,000 Kummer tests per row at `n = 10⁷` with a
handful of factorisations, and is why this runs ~300× faster per row than the
published implementation's 43.5 ms average.

## The theorem that shapes the algorithm

It would be much simpler if large primes always sufficed. They never do.

> For `p > j > i`, `p | C(n,i)` implies `n mod p < i < j`, hence `p | C(n,j)`.
> So "some prime `> j` covers `(n,i,j)`" iff `max S(n,i) > j`. But on every
> gap-pruned row, `max S(n,i) ≤ n/2`: a candidate `p > i` divides some `n−t`
> with `t < i`, and `p > n/2` would force `n−t = p` — a prime in `(n−i, n]`,
> exactly what the pruning excludes. **So at `j = ⌊n/2⌋` there is never a
> covering prime above `j`, on any pruned row.**

Checked on 0 of 26,859 pruned rows below n=6000. It is worse than merely
needing `p ≤ j`: **`p = 2` can be the unique usable prime.**

The coverage test therefore works digitwise. By Kummer/Lucas, `p | C(n,k)` iff
some base-`p` digit of `k` exceeds that of `n`, so the *uncovered* set is the
digitwise submasks of `n` — enumerated with a mixed-radix odometer and filtered
by the remaining candidates.

## Why a null result here is trustworthy

- **Two implementations sharing no algorithm.** `reference.py` decides the
  property by direct big-integer gcd and factorisation with no number theory at
  all; `exact.py` uses the pruning, Kummer and the digit test. They agree on
  every n from 4 to 300.
- **The pruning lemma is re-proved by the verifier**, exhaustively, rather than
  assumed.
- **Shard tiling is checked.** A gap between shards would let a counterexample
  through while the sweep still reported zero, so `verify.py` fails unless the
  shards tile `[10⁷, 10⁸)` with no gap and no overlap.
- **Sampled rows are re-decided** inside the claimed range at replay time.

## Cost calibration — recorded because we got it wrong twice

| measurement | µs/row |
|---|---|
| solo at `n ≈ 10⁶` | 141.6 |
| solo at `n ≈ 5×10⁷` | 897.5 |
| **actual, 13-way parallel** | **4,781** |

Per-row cost grows with `n` (more and larger factors per row), *and*
single-process sampling under-predicted 13-way throughput by ~5×. Successive
estimates for this job were 16 min → 80 min → an actual 9h26m wall and 119.53
core-hours. **Estimate at the scale and the concurrency you will actually run
at.**

## Files

| file | role |
|---|---|
| `exact.py` | the decider: pruning, candidate primes by factoring `i` integers, digitwise coverage; `--sweep A B` |
| `reference.py` | independent oracle — big-integer gcd and factorisation, shares no algorithm |
| `run699.sh` | shards a row range across cores |
| `emit_result.py` | **emit side** |
| `verify.py` | **check side**, never writes `RESULT.json` |
| `FINDINGS.md` | earlier working notes, kept: they record the gap this run closed |

## Related upstream activity (recorded, not evaluated)

One accepted partial proof: **Liam Price** with GPT-5.6 Sol Pro, 2026-07-18,
covering `j ≤ 3i/2` and `n = 2j` — roughly a third of the `(i,j)` plane, and it
does not subsume this sweep. Del Pin (07-24), glossed by Bloom (07-25), shows
the bad-`j` range is a single interval with a binary-entropy obstruction at
exactly `3/2`. Cong Lu is still listed as working the problem, so a competing
extension may be live. None of this sets a status here.

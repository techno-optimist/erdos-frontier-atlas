# Erdős #366 — the cubefull-side sweep

**Question** ([erdosproblems.com/366](https://www.erdosproblems.com/366), status
`VERIFIABLE`): *are there any 2-full `n` such that `n+1` is 3-full?* That is,
`p | n ⟹ p² | n` and `p | n+1 ⟹ p³ | n+1`.

**What this certificate establishes:** no such `n` exists below the bound
recorded in [`RESULT.json`](RESULT.json), by exhaustive enumeration of every
cubefull number in the range and an exact powerfulness test on both of its
neighbours. **This is a negative "verified to N" record, not a resolution** —
and per Turturean's abc argument on the problem page, a resolution by search
was never on the table.

Replay:

```bash
python3 -I verify.py
```

## Why the cubefull side

The frontier everyone quotes for this problem is `n < 10²²`, and it is
*inherited*: erdosproblems.com/366 says "(by OEIS A060355) there are no other
examples for n < 10²²", where [A060355](https://oeis.org/A060355) is
*"numbers k such that k and k+1 are powerful"* — a **consecutive-powerful-pair**
enumeration. Its only deep resource is Donovan Johnson's b-file: 39 terms, the
largest `a(39) = 3887785221910670811499 ≈ 3.89 × 10²¹`, uploaded 2011 and never
extended. That bound is valid for #366 (3-full ⟹ 2-full, so any solution is in
particular a consecutive powerful pair) but it costs `~X^(1/2)` to push, because
powerful numbers below `X` number `~X^(1/2)`.

This problem does not need the pair search. It needs only the **cubefull** side:
enumerate cubefull `C` and ask whether `C ± 1` is powerful. Cubefull numbers
below `X` number `~X^(1/3)`, so the same work buys several more decades. Every
cubefull number is `a³b⁴c⁵` (every exponent `≥ 3` is a non-negative combination
of 3, 4 and 5), so the generator streams those triples with no storage.

## Both orientations, because upstream disagrees with itself

The statement asks for `n` 2-full and `n+1` 3-full. Both worked examples on the
problem page are the **other way round**: `8 = 2³` is the 3-full one and `9 = 3²`
the 2-full one; likewise `12167 = 23³` before `12168 = 2³·3²·13²`. Under the
literal statement — and under the DeepMind Lean formalisation, which makes the
split explicit and carries the reverse direction as a separate *test* theorem
proved with `use 8` — **there are zero known examples in either direction of the
asked orientation**. Turturean's comment on the page draws the same line
("the other direction ... is beyond the scope of this problem").

So the sweep tests both and reports them separately:

| orientation | condition | known examples |
|---|---|---|
| **strict** (as asked, as formalised) | `n` 2-full, `n+1` 3-full | **none** |
| reverse | `n` 3-full, `n+1` 2-full | `(8, 9)`, `(12167, 12168)` |

Finding the two reverse pairs is this sweep's positive control: a search that
cannot rediscover them is not searching.

## The exact powerfulness test

Deciding "is `m` powerful" by factoring a 24-digit number is hopeless at this
volume. Instead, for `m ≤ N` choose `B` with `B⁵ ≥ N`, trial-divide by primes
`≤ B` demanding exponent `≥ 2`, and require the cofactor `r` to be 1 or a
perfect power.

*Why that is exact.* Suppose `r > 1` is powerful and not a perfect power. "Not a
perfect power" means the gcd of **all** its exponents is 1 — the joint gcd, not
the pairwise ones, which can all exceed 1 (exponents `(6,10,15)`). So `r` is not
a single prime power, and since every exponent is `≥ 2` with joint gcd 1 the
exponent **sum** is at least 5: two primes cannot be `(2,2)`, and three or more
give sum `≥ 6`. Hence `r ≥ q⁵` for `q` the least prime above `B`, so
`r > B⁵ ≥ N ≥ r` — contradiction.

Two properties worth stating plainly, because they decide how to read a null
result:

- The test has **no false positives** for any `B`: conditions (i) and (ii)
  imply powerful outright. `B` governs only false *negatives*.
- So a mis-set `B` would make this sweep **under**-report solutions, never
  invent one. That is why `B⁵ ≥ hi+1` is asserted at startup and the process
  aborts rather than proceeding unsound.

The minimising configuration is `p³q²` — larger exponent on the smaller prime —
not `p²q³`; the exponent-sum bound is what carries the argument either way.

## Files

| file | role |
|---|---|
| `search366.c` | the sweeper: `a³b⁴c⁵` generation, wheel prefilter, exact powerfulness test, `--selftest` |
| `reference.py` | independent oracle — full factorization, filters every integer, shares no algorithm |
| `run_sweep.sh` | shards the range across cores |
| `emit_result.py` | **emit side**: writes `RESULT.json` from shard outputs |
| `verify.py` | **check side**: never writes `RESULT.json` |
| `RESULT.json` | the receipt: range, `B`, candidate counts, per-shard summaries, hits |

The emit/check split is structural: this repo has been bitten by verifiers that
regenerate the receipt they are supposed to be checking, so the verifier here
can only read and re-derive.

## What this does not do

- It does not resolve #366. The expected outcome was always a negative record:
  the heuristic count of cubefull `C ≤ X` with `C ± 1` powerful scales like
  `X^(-1/6)`, which converges, and abc implies finiteness outright.
- It does not extend the consecutive-powerful-pair frontier (A060355). That is
  the `X^(1/2)` search and is untouched here.
- The prior `10²²` bound is a **single unreplicated 2011 computation** with no
  published method or code. This sweep re-derives that region independently
  rather than inheriting it, which is the more useful half of the result.

## Related upstream activity (recorded, not evaluated)

A partial proof was submitted to the problem page on 2026-07-22 by Theofil Xeff:
assuming Baker's explicit abc conjecture, `n < 10^16136778163`. It is an
unvetted user submission, and at ~16 billion digits it reduces no finite search.
Recorded here as context; **it sets no status** and this certificate does not
depend on it.

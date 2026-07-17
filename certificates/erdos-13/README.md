# Erdős #13 (Erdős–Sárközy) — certified small-N table

**Problem.** Let `f(N)` be the maximum size of a set `A ⊆ {1,…,N}` such that there
are **no** `a, b, c ∈ A` with `b ≠ c`, `a | (b+c)`, and `a < min(b,c)`. Erdős and
Sárközy (1970) asked whether `|A| ≤ N/3 + O(1)`; Bedert
([arXiv:2301.07065](https://arxiv.org/abs/2301.07065)) proved
`|A| ≤ ⌊N/3⌋ + 1` **for sufficiently large N** — with an *ineffective* threshold.

This directory certifies the exact finite table for `N = 1…45`, which the
asymptotic theorem does not give.

## What is certified

```
f(1..45) = 1,2,2,3,3,3,4,4,4,5,5,5,6,6,6,6,7,7,7,7,8,8,8,9,9,9,
           10,10,10,11,11,11,12,12,12,13,13,13,14,14,14,15,15,15,16
```

- **Exact**, by two independent methods: branch-and-bound over all of `{1,…,N}`,
  cross-checked against exhaustive subset enumeration for `N ≤ 16`.
- **The interesting content — where the asymptotic bound is beaten.** `f(N)`
  exceeds `⌊N/3⌋ + 1` exactly at **N = 2, 4, 5, 7, 8, 10, 11, 13, 14, 17**, and at
  no larger N in the computed range: **`f(N) = ⌊N/3⌋ + 1` for every `18 ≤ N ≤ 45`.**
  So **N = 17 is the last value that beats Bedert's asymptotic bound** here — an
  empirical location for the (proof-ineffective) "sufficiently large" threshold.
  The largest exceptional witness is `f(17) = 7`: `{6, 8, 9, 11, 12, 14, 17}`.

`table.json` carries `f`, every exceptional witness, and sample maximal sets.

## Reproduce

```sh
python3 certificates/erdos-13/verify.py
```

Dependency-free; recomputes `f` two ways, re-checks every exception witness, and
confirms the last exception is 17. ~10 s.

## Honest scope

- The **headline conjecture is a proven theorem** (Bedert 2023) — a WALL for the
  prize. This certificate is the *finite table*, which was untabulated.
- `f` is **not in OEIS** as of 2026-07-17 (checked). It is a candidate new
  sequence, but **not yet submitted** — an external contribution first needs a
  full literature/definition cross-check (does any source already tabulate it;
  is the `b ≠ c` reading universal). That verification gate is deliberately not
  skipped here.
- Modest impact: the sequence is `⌊N/3⌋+1` past N=17, so the value is the small-N
  exceptional data and the empirical threshold, not a striking new object.

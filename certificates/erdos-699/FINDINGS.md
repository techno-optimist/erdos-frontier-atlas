# Erdős #699 — verified foundations, sweep not yet run

**Not a certificate.** Working notes: the mathematical groundwork is checked
and reusable, but the sweep it was built for was not executed. Nothing here
sets a ledger status.

## What is verified

`reference.py` is the slow, obviously-correct oracle — it decides the property
by direct big-integer gcd and factorisation, using no number theory at all, so
it can adjudicate the fast path rather than share its assumptions.

- **Kummer's theorem** (the exponent of `p` in `C(n,k)` equals the number of
  carries when adding `k` and `n−k` in base `p`), checked against direct
  factorisation: **0 mismatches**.
- **The prime-gap pruning lemma**, checked exhaustively on every `(n,i)` pair
  for `n ≤ 400`. If a prime lies in `(n−i, n]` then it divides both `C(n,i)`
  and `C(n,j)` for every `j` with `i < j ≤ n/2`, and it is `≥ i` — so the
  triple is satisfied outright. Hence a counterexample requires **no** prime in
  `(n−i, n]`, i.e. `i ≤ n − prevprime(n)`. That collapses the `i`-range from
  `n/2` to the prime gap below `n` — roughly 18 on average near `10^8`, versus
  `5·10^7`.
- Brute force over `n = 4..300` by gcd and factorisation: **no counterexamples**.

## What remains

The covering test when `p ≤ j`.

For `p > j` the criterion collapses cleanly: `p | C(n,k)` iff `n mod p < k`.
Since `i < j`, any prime covering `C(n,i)` then automatically covers `C(n,j)`.
But once `i ≤ gap`, no prime in `(n/2, n]` divides `C(n,i)` at all, so the `j`
near `n/2` must be covered by primes `p ≤ j` — where the clean criterion stops
applying and the full base-`p` carry structure is needed. **That case decides
whether the `10^7 → 10^8` extension is affordable**, and it is not yet settled
here.

## Frontier as of 2026-07-27

`n = 10^7`, by Cong Lu (Rust, open-source, January 2026) — a single hobby run.
The prime-gap pruning above was only articulated in the problem thread on
2026-07-25, *after* that run, so a substantial extension is plausibly still
available.

Two cautions for whoever picks this up. The theory front is moving fast, with
accepted proof claims for `j ≤ (3/2)i` and `n = 2j`. And #617 — attacked in the
same session — closed upstream nine days before we looked at it. Re-run the
freshness check before spending anything.

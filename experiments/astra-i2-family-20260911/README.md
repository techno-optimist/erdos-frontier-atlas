# A kernel-checked i=2 family for P699

**Unpromoted research. Not a solution of Erdős #699, not a novelty claim, and not a Mathlib `Nat.choose` theorem.**

For every integer `j ≥ 3` put `n = 2j + 3` (so `i = 2 < j ≤ n/2`). Pascal binomials `binom` are the standard recursive coefficients. The kernel theorem is:

```lean
theorem erdos699_i2_divisor (j : Nat) (hj : 3 ≤ j) :
    ∃ m, 3 ≤ m ∧ m ∣ binom (2 * j + 3) 2 ∧ m ∣ binom (2 * j + 3) j
```

The witness is `m = n / gcd(n, j)`. Because `gcd(n, j) = gcd(3, j)`, one has `m ≥ 3`. Coprime cancellation through `j * binom n j = n * binom (n-1) (j-1)` gives `m ∣ binom n j`; oddness of `n` gives `m ∣ binom n 2`.

P699 asks for a **prime** `p ≥ i = 2`. Every integer `m ≥ 3` has a prime factor `p ≥ 3 ≥ 2`. That last sentence is **not** kernel-checked here: Lean 4.33 Init has gcd/coprime but no prime library, and this seed does not import Mathlib. The Python checker below exhibits those primes on a finite range.

EEES, localization, wrap classification, and all other `i` remain unformalized.

## Replay

Python 3.9+, stdlib only, from the atlas root:

```sh
python3 -I -B -m unittest discover -s experiments/astra-i2-family-20260911 -p 'test_*.py' -v
python3 -I experiments/astra-i2-family-20260911/verify.py
```

Lean 4.33.1, no Mathlib, no Lake. From this directory:

```sh
lean P699I2.lean
# After `lean -R . -o P699I2.olean P699I2.lean` with LEAN_PATH=. :
lean ExactStatement.lean
lean AxiomAudit.lean
# Expected exit 1: decide proves the naive “modulus is always 3” claim false
lean negative/AlteredIdentity.lean
```

Local kernel check used the official Darwin AArch64 4.33.1 binary, commit `819816b2e0a3bf405af45ae5c7af2491d8f5bee6`, archive SHA-256 `88c45aad985b5d2a8d925fe10bd1296bd35f66f408480ab182d3facccd065a9d`. Reported axioms for the three named theorems: `[propext, Quot.sound]`. No `sorry`, custom axiom, or `native_decide`.

## Official status since the 2026-09-04 pin

Compared `teorth/erdosproblems` `2a4d12b8…` with `3c68e941…` (2026-09-09). 1217 records both times.

Live pages (not the stale extract):

- **#477 SOLVED** — YAML `open → solved`. Homepage badge SOLVED.
- **#625 SOLVED** — YAML `open → solved`. Homepage badge `SOLVED - $1000`.
- **#501 INDEPENDENT** — YAML `open → independent`. Homepage badge INDEPENDENT (Glazer: first question independent of ZFC).
- Combined-status label `formalized → Lean` on several already-settled problems is **not** a new mathematical solution.
- **#699, #993, #366, #743** informal statuses unchanged (`falsifiable` / `verifiable`).

#699 still has exactly two proof claims: Price accepted (`j ≤ 3i/2` or `n = 2j`); Van Doorn–Rocca unaccepted (counterexamples only for `i = 3` or a finite `4 ≤ i ≤ 1475` list). This seed does not examine that manuscript.

Details: [official-delta.json](official-delta.json).

## Scope

Only `experiments/astra-i2-family-20260911/` and its `COORDINATION.md` row. Production graph, frozen certificates, and earlier Astra bundles are unchanged.

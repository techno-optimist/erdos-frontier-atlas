# Erdős #979 / OEIS A385316 — certified lower bound `a(6) > 10¹²`

**Problem.** Erdős [#979](https://www.erdosproblems.com/979): for `k ≥ 2`, let
`f_k(n)` count the representations `n = p₁ᵏ + … + p_kᵏ` with the `pᵢ` prime. Is
`limsup_n f_k(n) = ∞`? The headline is **asymptotic** — a theorem question, not
finite-computable, and **not** what this certificate touches.

**Finite object.** OEIS [A385316](https://oeis.org/A385316) (`k = 3`): `a(n)` =
the smallest `N` expressible as `p³ + q³ + r³` (`p ≤ q ≤ r` prime, a multiset)
in **exactly** `n` ways. Known terms `a(1..5) = 24, 185527, 8627527, 999979163,
10588881419`. The A385316 comments publish only `a(6) > 499243435237 (≈4.99·10¹¹)`.

**Claim (narrow, machine-checkable).** No integer `N ≤ 10¹²` has exactly six
prime-cube representations. Hence **`a(6) > 10¹²`**, improving the published
`a(6) > 4.99·10¹¹` by ~2×. `a(6)` itself remains open (not found below `10¹²`).

**Why it is exact, not heuristic.** To decide the window `[0, C]` it suffices to
use every prime `p` with `p³ ≤ C`: any prime inside a triple summing to `≤ C`
has `p³ ≤ C`. That finite, provably-complete prime set turns the exact
multiplicity count over `[0, C]` into a total decision procedure — no sampling,
no probabilistic primality on the certified path. The run **reproduces
`a(1..5)` exactly** as a fail-closed self-check before it accepts any bound.

**Replay.**

```
python3 verify.py                # ~1s self-check to 2·10¹⁰: reproduces a(1..5), certifies a(6)>2·10¹⁰
python3 verify.py --cutoff 1e12  # ~80s, ~11GB: the headline, certifies a(6)>10¹²
```

At `C = 10¹²` the run uses the 1229 primes `≤ 9973` (`10000³ = 10¹²`, prime set
complete), enumerates `235,275,700` multiset triple-sums into `234,585,699`
distinct values, reproduces `a(1..5)`, and finds no value of multiplicity six.

**Independent cross-verification (2026-07-17).** Four from-scratch
reimplementations, written blind to this verifier, agree:

| implementation | cutoff | reproduced a(1..5) | exactly-6 found | peak RAM |
|---|---|---|---|---|
| pure-Python `collections.Counter` | 2·10¹¹ | yes | none | 5.75 GB |
| numpy sort + run-length | 2·10¹¹ | yes | none | 0.46 GB |
| shard-by-largest-prime | 2·10¹¹ | yes | none | 2.60 GB |
| independent numpy (full window) | **10¹²** | yes | none | 9.01 GB |

All reproduced the five known terms exactly and found no `N` of multiplicity six
in their window, so all are consistent with — and the `10¹²` run directly
confirms — `a(6) > 10¹²`.

**Scope / not claimed.** A **low-impact** finite lower-bound extension: it does
not bear on the asymptotic `limsup` conjecture (a wall) and claims no prize. Not
yet submitted to OEIS — an external submission is gated on a full literature /
freshness novelty-check (the #552 `a(17)` and R(C4,K1,39) single-source
lessons). Registered internally, certified and independently reproduced.

<sub>provenance: 2026-07-17; sourced as a fresh tractable board when the scout
pool ran dry (all boards closed); independent verification via a 4-agent
from-scratch workflow. The `limsup` headline is unaffected and unclaimed.</sub>

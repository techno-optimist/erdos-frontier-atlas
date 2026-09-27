# Erdős #854 — gaps between integers coprime to a primorial: A389839 through n = 16

**Problem node `P854`; OEIS [A389839](https://oeis.org/A389839).** Let p_n# be
the product of the first n primes. A389839(n) is the smallest even number that
is **not** the difference of two consecutive integers coprime to p_n#. Erdős
first guessed that every even number up to the largest such difference occurs,
then doubted it after Lacampagne and Selfridge found that 20 is missing for
13# = 30030, although the largest gap there is 22.

## What this certificate establishes

| n | p_n | a(n) | largest gap A048670(n) | every even gap up to the largest occurs? |
|---:|---:|---:|---:|---|
| 2–12 | 3–37 | 6, 8, 12, 16, 20, 28, 32, 42, 48, 60, 68 | … | no at n = 6 (20) and n = 8 (32) |
| **13** | 41 | **76** | 74 | yes |
| **14** | 43 | **86** | 90 | no: 86 and 88 are missing |
| **15** | 47 | **98** | 100 | no: 98 is missing |
| **16** | 53 | **108** | 106 | yes |

**A389839(13), …, A389839(16) = 76, 86, 98, 108.** For each n, every even gap
below a(n) has an explicit witness x (x and x + t coprime to p_n#, every
integer strictly between them not), and a(n) itself is shown absent by an
exhaustive search. The published terms a(2..12) are reproduced.

## What is new here, and what is replication

- **A389839** (Stijn Cambie, 2025; terms to n = 12 by Andrew Howroyd and Chai
  Wah Wu) is marked `more` and stops at a(12) = 68.
- **The values below 44 were already implicit in public data.** OEIS
  [A331118](https://oeis.org/A331118) (Michael De Vlieger, 2020, with Mario
  Ziller's arXiv:2007.01808) lists the full set of gaps for every p_n#,
  n ≤ 44, and A329815 counts them. So a(13..16) follow from that table; this
  certificate recomputes them independently and fills them into A389839's
  form. The counts alone already force a(n) = A048670(n) + 2 whenever no gap
  below the largest is missing. That holds for n = 16, 17, 18, 23, 26, 29,
  39, 41 and 44, giving a(17) = 120, a(18) = 134, …, a(44) = 618. These
  values beyond 16 are **implied by public data, not recomputed here**.
- **The open frontier is n = 45** (p = 197), the first primorial beyond the
  A331118 table. Gaps only accumulate as n grows (a gap for p_n# survives for
  p_{n+1}#: the new prime can avoid both ends), so a(45) ≥ a(44) = 618; and
  a(45) ≤ A048670(45) + 2 = 644.

## Method

Write x = −c_p (mod p) for each prime p | p_n#. Then p divides x + j exactly
when j ≡ c_p (mod p), so an even gap t occurs iff residues c_p, with
c_p ≠ 0 and c_p ≢ t (mod p) so that x and x + t stay coprime, together
cover every j in 1..t−1. By the Chinese remainder theorem every such choice
is realised by some x. The prime 2 must take the odd positions, which leaves
the even positions j = 2k to the odd primes.

`coprime_gaps.Cover` decides one (n, t) exactly by depth-first search.
- **Branching:** it picks the uncovered position with the fewest candidate
  primes and tries every prime that can still cover it, which is exhaustive.
- **Pruning:** it cuts a branch when even the best class of every unassigned
  prime cannot cover what is left.
- **Engine:** `gapsc.c` is its C port, node for node; the absence proofs take
  1.2 × 10⁶, 8.8 × 10⁶, 9.9 × 10⁷ and 7.9 × 10⁸ nodes at n = 13, 14, 15, 16.

## Why the result can be trusted

- **Witnesses are checked by arithmetic alone.** Each occurring gap comes with
  an integer x, and `coprime_gaps.is_gap` checks the gcds directly. That check
  shares no code with any search.
- **Two implementations of the search, pinned to each other.** For n ≤ 12 the
  Python reference re-decides every (n, t) and must reproduce the C engine's
  verdict, node count and witness on all 159 pairs.
- **It finds what is missing below the maximum.** At n = 6 the engine reports
  20 absent and 22 present, the Lacampagne–Selfridge phenomenon. At n = 14 and
  15 its answers agree with the A329815 counts: exactly two, then one, even
  numbers below the largest gap are missing.
- **Cross-checks.** a(2..12) equal the published terms. a(n) ≤ A048670(n) + 2
  for every n. a(n) = A048670(n) + 2 holds exactly when A329815(n) =
  A048670(n)/2.
- **Development cross-check, not packaged.** An independent SAT encoding
  (CaDiCaL) agreed on n = 6, 14 and 15: 86 and 88 absent at 43#, 98 absent
  at 47#.

## Replay

```sh
python3 -I certificates/erdos-854/verify.py          # a(2..15), exhaustive (~2 minutes; needs cc)
python3 -I certificates/erdos-854/verify.py --full   # also a(16) (~15 CPU-minutes)
```

| file | role |
|---|---|
| `coprime_gaps.py` | the covering search (reference), CRT realisation, and the gcd check |
| `gapsc.c` | C port of the search; the verifier builds it in a temporary directory |
| `verify.py` | the replay; reads RESULT.json, never writes it |
| `RESULT.json` | receipt: a(n), node counts, and one witness x per occurring gap |
| `emit_result.py` | regenerates RESULT.json into a *different* directory |

## Scope — what is not certified

- **Not Erdős #854.** The questions are asymptotic (does every even number up
  to the largest gap occur, in the limit? are there ≫ max-gap many distinct
  gaps?). Finite terms only illustrate them.
- **Terms beyond n = 16 are not recomputed.** The values implied by A331118
  and A329815 for n ≤ 44 are quoted, not replayed.
- **A verified-search receipt, not a formal proof.**

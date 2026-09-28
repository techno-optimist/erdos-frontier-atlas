# Erdős #357 — distinct segment sums: A364132 through n = 27, A364153 through n = 16

**Problem node `P357`; OEIS [A364132](https://oeis.org/A364132) and
[A364153](https://oeis.org/A364153).** A *segment* of a sequence
(s_1, …, s_n) is a run s_i + s_{i+1} + ⋯ + s_j of consecutive terms.
A364132(n) is the least N such that {1, …, N} contains an increasing n-term
sequence whose n(n+1)/2 segment sums are all distinct. A364153(n) is the same
for sequences in any order; their terms are distinct anyway, since single terms
are segments. OEIS lists A364132(1..22) and A364153(1..13), the later terms by
Jinyuan Wang (July 2023).

## What this certificate establishes

**A364132(23..27) = 56, 60, 63, 67, 69 and A364153(14..16) = 20, 22, 24; all 8 terms are new.**

| n | A364132(n) | an increasing n-sequence in {1..A364132(n)} with distinct segment sums |
|---:|---:|---|
| 23 | **56** | 1, 4, 6, 8, 24, 27, 33, 35, 36, 37, 39, 40, 41, 44, 45, 46, 48, 49, 52, 53, 54, 55, 56 |
| 24 | **60** | 1, 6, 12, 15, 30, 31, 36, 37, 40, 41, 42, 43, 44, 46, 47, 49, 50, 53, 54, 55, 56, 58, 59, 60 |
| 25 | **63** | 2, 4, 8, 10, 13, 33, 34, 41, 42, 43, 44, 45, 47, 48, 49, 51, 52, 53, 54, 55, 57, 59, 61, 62, 63 |
| 26 | **67** | 1, 2, 4, 5, 14, 22, 35, 39, 42, 44, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 61, 63, 64, 65, 66, 67 |
| 27 | **69** | 7, 14, 15, 19, 24, 33, 37, 38, 39, 41, 44, 49, 50, 51, 53, 54, 56, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69 |

| n | A364153(n) | an n-sequence in {1..A364153(n)} with distinct segment sums |
|---:|---:|---|
| 14 | **20** | 1, 4, 6, 17, 15, 14, 20, 16, 19, 18, 8, 13, 9, 3 |
| 15 | **22** | 1, 11, 16, 8, 21, 22, 20, 19, 15, 18, 14, 17, 6, 3, 4 |
| 16 | **24** | 1, 2, 6, 5, 23, 20, 24, 22, 18, 12, 21, 17, 15, 10, 16, 19 |

Erdős asked for f(N), the most terms an increasing sequence in {1..N} with
distinct segment sums can have. Since f(N) = max{n : A364132(n) ≤ N}, the
table gives f(N) for every N ≤ 69; for instance f(69) = 27.
The next cells: A364132(28) lies in [70, 76] and A364153(17) in [24, 26], the upper ends by explicit sequences recorded in RESULT.json and checked like the witnesses.

## Method

The sequence is built left to right, depth first. Two bitsets carry the state:
T holds the sums of the segments ending at the last term, 0 included, and D
holds every segment sum so far. A next term x is admissible iff T + x misses D;
then T ← (T + x) ∪ {0} and D ← D ∪ (T + x).

Three prunings are used:
- **Room.** The n − j terms still to come are distinct values outside D, since
  each is a segment sum by itself, so a node needs n − j such values left.
- **Increasing case.** The next term is at most N − (n − j − 1).
- **Any-order case.** Only sequences with s_1 < s_n are searched, since
  reversal keeps the segment sums.

For each n the receipt keeps the two searches that decide a(n). One, with every
term ≤ a(n) − 1, finds nothing, which refutes every smaller N at once. The
other, at a(n), finds the witness. The deciding refutation grows roughly 2–4×
per term: the last refutations, A364132(27) and A364153(16), take 8.4 × 10^9 and 7.9 × 10^9 nodes. Finding the A364132(27) witness takes 1.0 × 10^10 nodes,
since the first sequence in search order starts at 7.

## Why the result can be trusted

- **Every witness is checked by brute force alone.** All n(n+1)/2 segment sums
  are computed directly and compared. The check shares no code with the
  searches.
- **It reproduces the published data.** The searches give every published term,
  A364132(1..22) and A364153(1..13).
- **Two implementations, pinned node for node.** `segsum.c` is a port of the
  Python reference `segment_sums.Search`. The default replay re-decides the
  searches for n ≤ 18 and n ≤ 11 in both. With `--full`, the reference also
  re-decides every search through A364132 n = 24 and A364153 n = 15, the new
  ones included; verdicts, node counts and sequences all agree.
- **A second engine that shares no code.** `segsum_naive.c` works differently:
  - it builds increasing sequences from the largest term down;
  - it searches both orientations of unordered ones;
  - it prunes nothing beyond the definition;
  - it keeps segment sums in a plain byte array.

  It reaches the same verdict on every search it replays, which is all of them
  through A364132 n = 24 and A364153 n = 15.
- **Planted failures.** A witness whose last term equals the sum of the two
  before it, or with two terms swapped, is rejected. A receipt with one node
  count off by one disagrees with the engine.

## Replay

```sh
python3 -I certificates/erdos-357/verify.py          # the published terms (~10 s; needs cc)
python3 -I certificates/erdos-357/verify.py --full   # every term, new ones included (about 2.5 CPU-hours; 76 min on 4 cores)
```

`--jobs J` sets the number of worker processes (default: up to 4).

| file | role |
|---|---|
| `segment_sums.py` | the Python reference search and the brute-force segment-sum check |
| `segsum.c` | C port of the search, node for node |
| `segsum_naive.c` | the second engine, for verdict cross-checks |
| `verify.py` | the replay; reads RESULT.json, never writes it |
| `RESULT.json` | receipt: the deciding searches with node counts, a witness per term, next-cell bounds |
| `emit_result.py` | regenerates RESULT.json into a *different* directory |

## Scope — what is not certified

- **Not Erdős #357.** The question is how f(N) grows, for instance whether
  f(N) = o(N), and similarly for the any-order version. That is asymptotic,
  and the atlas gap map (row #357) records the known bounds. A table only
  illustrates it.
- **The largest searches rest on `segsum.c` alone.** No Python pin covers
  A364132 n = 25..27 or A364153 n = 16, where the reference would take hours, and `segsum_naive.c` is not run
  on them. Its top-down search of increasing sequences is about 30× slower. The
  engine is pinned to both on every smaller search, and the code does not change
  with n.
- **Freshness.** "New" means beyond the OEIS entries as fetched from the OEIS
  data mirror on 2026-09-28. erdosproblems.com was not reachable from this
  session.
- **A verified-search receipt, not a formal proof.**

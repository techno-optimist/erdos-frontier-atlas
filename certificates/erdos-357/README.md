# Erdős #357 — distinct segment sums: A364132 through n = 28, A364153 through n = 17

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
Update 2026-10-28: A364153(17) = 26 is now decided by a separate search (next section), so the any-order companion cell is A364153(18) ≥ 26;
A364132(28) ∈ [70, 76] is unchanged.
Update 2026-10-29: A364132(28) = 75 is now decided by the same separate engine (addendum below), so the next cell is A364132(29) ≥ 76.
Update 2026-10-30: A364153(18) = 28 is now decided by the same separate engine (addendum below), so the any-order companion cell is A364153(19) ≥ 29.

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

## Addendum (2026-10-28, Ford): A364153(17) = 26

**A364153(17) = 26: new, since OEIS lists A364153(1..13); an exhaustive computer search by two independent engines, not a proof.**

| n | A364153(n) | an n-sequence in {1..A364153(n)} with distinct segment sums |
|---:|---:|---|
| 17 | **26** | 1, 2, 12, 16, 18, 23, 17, 20, 22, 25, 26, 10, 19, 24, 11, 21, 6 |

This sequence is the one already recorded in RESULT.json as the upper end of the
A364153(17) cell. What is new is the lower end: no 17-sequence of distinct values
from {1..25}, in any order, has all 153 segment sums distinct.

- **Engine.** `ss_cleanroom.c` was written by Ford from the OEIS definition alone,
  without reading or reusing atlas code. It uses the same left-to-right bitset state
  as `segsum.c` (T and D above) and the room pruning, but no symmetry breaking: both
  orientations of every sequence are searched. The search at N is split into 19
  parts by dealing the admissible second terms round-robin; every part sees the same
  sequence of choices, so together the parts cover the whole search.
- **Searches** (`ford_searches_a364153_17.txt`, 40 lines): all 19 parts NONE at
  N = 24 and at N = 25 (about 2.1 × 10^10 and 5.6 × 10^10 nodes), FOUND at N = 26
  with the sequence above (2.3 × 10^8 nodes), and the control a16@23 part 0/14
  (NONE). NONE at 25 alone gives A364153(17) ≥ 26; the sequence gives ≤ 26.
- **Second engine** (`g4_crosscheck_a364153_17.txt`): the unchanged `segsum.c`
  answers none at 24 and 25 (2.1 × 10^10 and 5.6 × 10^10 nodes), and its a16@23
  node count equals the one pinned in RESULT.json. The two engines are independent
  code using the same method, not independent mathematics.
- **Checks** (`verify_ford_a17.py`): completeness of the parts, the sequence checked
  by brute force alone, agreement of the two engines, `ss_cleanroom.c` reproducing
  A364153(1..12) of RESULT.json, and five planted failures (a witness whose last
  term is s_1 + s_2, a flipped part, a dropped part, an engine disagreement, the
  collision 1 + 2 = 3), each rejected.

```sh
python3 -I certificates/erdos-357/verify_ford_a17.py          # consistency + the FOUND search (~2 min; not certifying)
python3 -I certificates/erdos-357/verify_ford_a17.py --full   # re-runs all 40 + 3 searches (about 1.6e11 nodes; hours)
```

| file | role |
|---|---|
| `ss_cleanroom.c` | Ford's clean-room engine (any order, no symmetry breaking, split into parts) |
| `ford_searches_a364153_17.txt` | its 40 committed answers |
| `g4_crosscheck_a364153_17.txt` | `segsum.c` on a16@23, a17@24 and a17@25 |
| `verify_ford_a17.py` | the replay; reads the files above and RESULT.json, never writes them |

RESULT.json, `verify.py` and the other files above are unchanged. Not submitted to
OEIS here. Nothing in this addendum bears on A364132(28) or on the asymptotic
question.

## Addendum (2026-10-29, Ford): A364132(28) = 75

**A364132(28) = 75: new, since OEIS lists A364132(1..22); an exhaustive computer search by two independent engines, not a proof.**

| n | A364132(n) | an increasing n-sequence in {1..A364132(n)} with distinct segment sums |
|---:|---:|---|
| 28 | **75** | 2, 3, 4, 6, 11, 25, 38, 40, 41, 47, 52, 54, 56, 57, 58, 60, 61, 62, 64, 66, 67, 68, 69, 70, 71, 72, 73, 75 |

This closes the cell A364132(28) ∈ [70, 76] recorded in RESULT.json: no increasing
28-sequence with every term at most 74 has all 406 segment sums distinct, and the
sequence above (maximum 75) does. A second 28-sequence with maximum 75 also turned up
(4, 5, 10, 12, 18, 39, 47, 50, 51, 52, 53, 54, 55, 56, 58, 59, 61, 62, 63, 64, 66, 68, 70, 71, 72, 73, 74, 75); both are checked by brute force.

- **Engine.** The same `ss_cleanroom.c` as the A364153(17) addendum, in mode m
  (increasing sequences). The search at N is split into 38 parts by dealing the
  admissible second terms round-robin; together the parts cover the whole search.
- **Searches** (`ford_searches_a364132_28.txt`, 229 lines): all 38 parts NONE at
  each N = 70, 71, 72, 73 and 74 (about 3.9 × 10^10, 6.0 × 10^10, 9.5 × 10^10,
  1.5 × 10^11 and 2.3 × 10^11 nodes), and at N = 75 36 parts NONE and 2 FOUND
  (parts 29 and 36, the two sequences above), plus the control m27@68 part 6/14
  (NONE, the same node count in all four runs). NONE at 74 alone gives
  A364132(28) ≥ 75; the sequence gives ≤ 75.
- **Second engine** (`g4_crosscheck_a364132_28.txt`): the unchanged `segsum.c`,
  unpartitioned, answers none at 70, 71, 72, 73 and 74 and found at 75 (the first
  sequence above, brute-checked), and its m27@68 node count equals the one pinned in
  RESULT.json. The two engines are independent code using the same method, not
  independent mathematics.
- **Checks** (`verify_ford_a28.py`): completeness of the parts, every FOUND sequence
  checked by brute force alone, agreement of the two engines at every N, `ss_cleanroom.c`
  reproducing A364132(1..20) of RESULT.json, and six planted failures (a witness whose
  last term is 11 + 25 + 38, a flipped part, a dropped part, an engine disagreement,
  the collision 1 + 2 = 3, a non-increasing sequence), each rejected.

```sh
python3 -I certificates/erdos-357/verify_ford_a28.py          # consistency + one FOUND search (~30 s; not certifying)
python3 -I certificates/erdos-357/verify_ford_a28.py --full   # re-runs all 229 + 7 searches (about 1.1e12 nodes; many hours)
```

| file | role |
|---|---|
| `ford_searches_a364132_28.txt` | its 229 committed answers |
| `g4_crosscheck_a364132_28.txt` | `segsum.c` on m27@68 and m28@70..75 |
| `verify_ford_a28.py` | the replay; reads the files above and RESULT.json, never writes them |

The raw searches ran on 2026-10-28 and 2026-10-29; the segsum m27@68 control line
was re-run separately on 2026-10-29. RESULT.json, `verify.py`,
`ss_cleanroom.c` and the other files above are unchanged. Not submitted to OEIS here.
Nothing in this addendum bears on the asymptotic question.

## Addendum (2026-10-30, Ford): A364153(18) = 28

**A364153(18) = 28: new, since OEIS lists A364153(1..13); an exhaustive computer search by two independent engines, not a proof.**

| n | A364153(n) | an n-sequence in {1..A364153(n)} with distinct segment sums |
|---:|---:|---|
| 18 | **28** | 1, 3, 2, 7, 22, 25, 28, 21, 27, 18, 24, 20, 23, 14, 26, 15, 17, 19 |

No 18-sequence of distinct values from {1..27}, in any order, has all 171 segment
sums distinct, and the sequence above (maximum 28) does. Two more 18-sequences with
maximum 28 turned up in the same search (1, 6, 2, 28, 27, 16, 26, 23, 17, 21, 24, 22, 10, 19, 25, 14, 20, 13; and 1, 8, 4, 26, 7, 25, 24, 28, 27, 20, 21, 22, 18, 17, 19, 15, 14, 2); all three are checked by
brute force.

- **Engine.** The same `ss_cleanroom.c` as the A364153(17) addendum, in mode a (any
  order, no symmetry breaking), split into 19 parts by dealing the admissible second
  terms round-robin; together the parts cover the whole search.
- **Searches** (`ford_searches_a364153_18.txt`, 42 lines): the control a16@23 part
  0/14 (NONE, the same node count as before), all 19 parts NONE at N = 26 and at
  N = 27 (about 1.5 × 10^11 and 3.9 × 10^11 nodes), and three FOUND lines at N = 28
  (parts 1, 4 and 6 of 19, the three sequences above). The N = 28 run was stopped once
  these were found, so its other parts were not run to the end; they are not needed. NONE at
  27 alone gives A364153(18) ≥ 28; any one of the sequences gives ≤ 28.
- **Second engine** (`g4_crosscheck_a364153_18.txt`): the unchanged `segsum.c`,
  unpartitioned, answers none at 26 (148,693,548,809 nodes) and at 27
  (388,784,217,499 nodes), and its a16@23 node count equals the one pinned in
  RESULT.json. The two engines are independent code using the same method, not
  independent mathematics.
- **Checks** (`verify_ford_a18.py`): completeness of the parts, each sequence checked
  by brute force alone, agreement of the two engines at 26 and 27, `ss_cleanroom.c`
  reproducing A364153(1..12) of RESULT.json, a byte-for-byte re-run of the three FOUND
  searches, and five planted failures (a witness whose last term is s_1 + s_2, a
  flipped part, a dropped part, an engine disagreement, the collision 1 + 2 = 3), each
  rejected.

```sh
python3 -I certificates/erdos-357/verify_ford_a18.py          # consistency + the 3 FOUND searches (~3 min; not certifying)
python3 -I certificates/erdos-357/verify_ford_a18.py --full   # re-runs all 42 + 3 searches (about 1.1e12 nodes; many hours)
```

| file | role |
|---|---|
| `ford_searches_a364153_18.txt` | its 42 committed answers |
| `g4_crosscheck_a364153_18.txt` | `segsum.c` on a16@23, a18@26 and a18@27 |
| `verify_ford_a18.py` | the replay; reads the files above and RESULT.json, never writes them |

The ss searches ran 2026-10-29; the segsum runs finished 2026-10-30 (the a16@23
control line is the one from the A364153(17) cross-check, same binary). RESULT.json,
`verify.py`, `ss_cleanroom.c` and the other files above are unchanged. Not submitted to
OEIS here. Nothing in this addendum bears on A364132(29) or on the asymptotic
question; Erdős #357 itself remains open.

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

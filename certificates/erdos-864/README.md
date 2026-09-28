# Erdős #864 — sets with one repeated sum: A389182 through N = 117

**Problem node `P864`; OEIS [A389182](https://oeis.org/A389182).** A389182(N)
is the largest A ⊆ {1, …, N} such that among the sums a + b (a ≤ b in A) at most
one value occurs more than once. OEIS lists a(1..80), and its b-file
(A. Ferudun) runs to a(100) = 16.

## What this certificate establishes

**A389182(N) for every N ≤ 117: a(101..106) = 16, a(107..116) = 17 and a(117) = 18; everything past N = 100 is new.**

| N | a(N) | where the table steps up: a set with a(N) elements in {1..N} |
|---:|---:|---|
| 81 | 15 | 1, 4, 6, 10, 23, 33, 34, 41, 48, 49, 59, 72, 76, 78, 81 |
| 86 | 16 | 1, 3, 4, 11, 17, 29, 34, 38, 49, 53, 58, 70, 76, 83, 84, 86 |
| 107 | **17** | 1, 2, 4, 8, 16, 25, 36, 41, 54, 67, 72, 83, 92, 100, 104, 106, 107 |
| 117 | **18** | 1, 2, 4, 12, 16, 21, 37, 44, 50, 68, 74, 81, 97, 102, 106, 114, 116, 117 |

Between the steps the table is flat. An exhaustive search at each such N shows
that no set one larger exists. The next cell is a(118) ∈ {18, 19}.
Both new step sets are symmetric, A = N + 1 − A, so N + 1 is their repeated sum,
reached by every pair a and N + 1 − a.

**This confirms an external report.** A computation attributed to
erdosproblemaday.com gives a(101..106) = 16, a(107..116) = 17 and
a(117..134) = 18. The atlas logged it on 2026-09-27 as unverified, since the page
was unreachable and no public copy was found. This certificate reproduces every
reported value through N = 117, with a replayable derivation.

## Method

a(N) is a(N − 1) or a(N − 1) + 1: deleting N from a set in {1..N} leaves a set
in {1..N − 1}. The property survives translation. So a set of size a(N − 1) + 1
in {1..N} contains both 1 and N; otherwise a translate would fit in
{1..N − 1}. One search per N therefore decides the table.

`onesum.c` places 1 and N first, then adds the inner elements in increasing
order. It counts the representations of every sum and tracks the one repeated
value. A new x is admissible iff each new sum x + a (and 2x) is one of:
- unused;
- equal to the repeated value;
- the first used one, while no value repeats yet (it becomes the repeated value).

Admissibility only shrinks as the set grows, so each node keeps the list of
candidates still admissible. A node is dropped when fewer remain than elements
still to place. The reflection x ↦ N + 1 − x is broken: with s and t the first
and last inner elements, only sets with s − 1 ≤ N − t are searched. The search
at N = 117 takes 2.5 × 10^7 nodes.

## Why the result can be trusted

- **Every witness is checked by brute force alone.** At each step, all the
  sums of the recorded set are counted. The check shares no code with the
  searches.
- **It reproduces the published data.** The table agrees with a(1..80) as
  published, and with a(100) = 16, the last line of the b-file.
- **Two implementations, pinned node for node.** `onesum.c` is a port of the
  Python reference `one_exception.Search`. The reference re-decides every search
  for N ≤ 45 in the default replay, and for N ≤ 70 with `--full`; verdicts,
  node counts and sets agree.
- **A second engine that shares no code.** `onesum_naive.c` works differently:
  - it adds inner elements in decreasing order;
  - it tests each candidate from scratch;
  - it keeps no candidate lists and breaks no symmetry.

  It reaches the same verdict on every search for N ≤ 80, and on N = 101, the
  first cell past the b-file.
- **Planted failures.** A witness with one more element, which makes a second
  sum repeat, is rejected, and so is a witness with an element doubled. A
  receipt with one node count off by one disagrees with the engine.

## Replay

```sh
python3 -I certificates/erdos-864/verify.py          # a(1..80), the published data (~15 s; needs cc)
python3 -I certificates/erdos-864/verify.py --full   # every N through 117 (about 3 CPU-hours; 61 min on 3 cores)
```

`--jobs J` sets the number of worker processes (default: up to 4).

| file | role |
|---|---|
| `one_exception.py` | the Python reference search and the brute-force check |
| `onesum.c` | C port of the search, node for node |
| `onesum_naive.c` | the second engine, for verdict cross-checks |
| `verify.py` | the replay; reads RESULT.json, never writes it |
| `RESULT.json` | receipt: one search per N with its verdict and node count, and the set at each step |
| `emit_result.py` | regenerates RESULT.json into a *different* directory |

## Scope — what is not certified

- **Not Erdős #864.** The question is asymptotic: the constant in
  a(N) ~ c·√N. The atlas gap map (row #864) records the known bracket, a wall.
  A table only illustrates it.
- **The cells past N = 101 rest on `onesum.c` alone.** It is pinned to the
  reference and to the second engine on every smaller search, but neither
  replays these. They are where the external report is confirmed.
- **Freshness.** "New" means beyond the OEIS entry as fetched from the OEIS
  data mirror on 2026-09-28. erdosproblems.com and erdosproblemaday.com were not
  reachable from this session.
- **A verified-search receipt, not a formal proof.**

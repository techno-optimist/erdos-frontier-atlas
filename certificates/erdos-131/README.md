# Erdős #131 — nondividing sets: A068063 thresholds through size 10

**Problem node `P131`; OEIS [A068063](https://oeis.org/A068063).** A set is
*nondividing* if no element divides the sum of any nonempty subset of the
others. A068063(n) is the size of the largest nondividing subset of
{1, …, n}. Let T_k be the least n with a nondividing k-subset; then
A068063(n) = max{k : T_k ≤ n}. OEIS lists A068063(0..100); the b-file
(C. Sievers) ends at a(100) = 8.

## What this certificate establishes

**T_1..T_10 = 1, 3, 7, 10, 21, 31, 43, 65, 107, 155; T_9 and T_10 are new.**

| k | T_k | a nondividing k-set with maximum T_k |
|---:|---:|---|
| 8 | 65 | {36, 40, 48, 49, 53, 61, 64, 65} |
| **9** | **107** | {60, 70, 87, 90, 92, 100, 102, 105, 107} |
| **10** | **155** | {80, 95, 115, 120, 134, 139, 140, 149, 154, 155} |

So **A068063(n) = 8 for 65 ≤ n ≤ 106, = 9 for 107 ≤ n ≤ 154, and
A068063(155) = 10.** The board cell A068063(101) is 8, and the first open
threshold is T_11 > 155.

## Method

A k-set with maximum N is built in decreasing order. A subset of a nondividing
set is nondividing, so after choosing x, the k − d − 1 smaller elements still
to come form a nondividing set below x. That forces x > T_{k−d−1}, and the
smaller thresholds prune the search hard.

A new smaller element x is admissible iff two conditions hold:
- (a) x divides no nonempty subset sum of the chosen set;
- (b) for every chosen e, no subset sum of the other chosen elements (the empty
  one included) is ≡ −x (mod e).

The search keeps the subset sums as a bitset. For each chosen e it keeps the
residues mod e of the other elements' subset sums, updated word by word.
`nondiv.c` is the port of `nondividing.Search`, node for node. Deciding every
(k, N) through k = 10 takes about 2.5 × 10^9 nodes.

## Why the result can be trusted

- **Every threshold set is checked by brute force alone.** For each element,
  every nonempty subset sum of the others is tested. The check shares no code
  with the search.
- **It reproduces the published data.** The search reproduces T_1..T_8, the
  places where the OEIS data step up, and it finds no 9-set up to N = 100,
  consistent with the b-file's a(100) = 8.
- **Two implementations, pinned node for node.** The Python reference re-decides
  every search for k ≤ 8. With `--full` it also re-decides the k = 9 searches
  for N = 101..107, the range beyond the b-file: verdicts, node counts and sets
  all agree.
- **A development cross-check, not packaged.** A simpler build of the engine,
  without the word-level updates, produced the same output for all k ≤ 10,
  including every node count of the 48 k = 10 searches.
- **Planted failures.** A set extended by half or twice its smallest element is
  rejected, and a receipt with one node count off by one disagrees with the
  reference.

## Replay

```sh
python3 -I certificates/erdos-131/verify.py          # T_1..T_8: every search for k <= 8 (~15 s; needs cc)
python3 -I certificates/erdos-131/verify.py --full   # T_1..T_10, plus the Python pin of the new k = 9 range (~40 CPU-minutes)
```

| file | role |
|---|---|
| `nondividing.py` | the Python reference search and the brute-force nondividing check |
| `nondiv.c` | C port of the search, node for node |
| `verify.py` | the replay; reads RESULT.json, never writes it |
| `RESULT.json` | receipt: every (k, N) search with its verdict and node count; each threshold's set |
| `emit_result.py` | regenerates RESULT.json into a *different* directory |

## Scope — what is not certified

- **Not Erdős #131.** The question is how the largest nondividing subset of
  {1..N} grows, which is asymptotic.
  - Erdős asked whether it exceeds N^{1/2 − o(1)}; the answer is no, since it is
    at most N^{1/4 + o(1)} (Pham–Zakharov 2024, via non-averaging sets).
  - The right exponent is open.

  A table only illustrates this.
- **The k = 10 negatives rest on the C engine.** No Python pin covers them
  (48 searches at up to 6 × 10^7 nodes each). The simpler development build
  agrees on all of them.
- **A verified-search receipt, not a formal proof.**

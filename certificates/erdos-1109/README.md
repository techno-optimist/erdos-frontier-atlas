# Erdős #1109 — sets with squarefree sumsets: records of A392164 through N = 2000

**Problem node `P1109`; OEIS [A392164](https://oeis.org/A392164) and
[A392165](https://oeis.org/A392165).** f(N) = A392164(N) is the size of the
largest S ⊆ {1, …, N} such that every element of S + S (a + a included) is
squarefree. A392165(k) is the least N with f(N) ≥ k, the index of the k-th
record. OEIS lists A392165(1..39), up to 1103 (C. Wu), and a b-file of
A392164 to N = 700.

## What this certificate establishes

**A392165(1..54) and f(N) for every N ≤ 2000; A392165(40..54) are new.**

| k | A392165(k) | vertices of G_N | nodes to find the set |
|---:|---:|---:|---:|
| 40 | **1255** | 201 | 70 913 |
| 41 | **1277** | 207 | 10 139 |
| 42 | **1293** | 210 | 5 600 |
| 43 | **1335** | 215 | 528 |
| 44 | **1407** | 230 | 121 836 |
| 45 | **1509** | 243 | 965 133 |
| 46 | **1535** | 250 | 428 065 |
| 47 | **1595** | 254 | 162 039 |
| 48 | **1707** | 287 | 7 392 763 |
| 49 | **1735** | 281 | 157 454 |
| 50 | **1779** | 295 | 425 465 |
| 51 | **1835** | 299 | 2 910 764 |
| 52 | **1919** | 306 | 2 307 372 |
| 53 | **1991** | 321 | 22 323 282 |
| 54 | **1999** | 325 | 54 052 973 |

So f(2000) = 54, A392165(55) > 2000, and A392164(N) for N ≤ 2000
follows from the table. For each record, the certificate records the set,
checked by trial division, and an exhaustive search shows that no candidate N
between records reaches the next size.

## Method

A record at N forces N into S, so 2N is squarefree. Every element of S is then
odd and squarefree, since a + a = 2a. Two odd numbers can sum to a squarefree
number only if they agree mod 4, so S lies in one class mod 4. Hence
f(N) = f(N − 1) + 1 exactly when the graph

  V_N = { a < N : 2a and a + N squarefree },  a ~ b iff a + b squarefree

has a clique of size f(N − 1). One scan over N decides every record. At
N ≈ 2000 the graph has about 320 vertices, and the search takes 10^6–10^8
nodes per N.

- **`sqclique.c`.** A decision search for a clique of the target size with a
  greedy-colouring bound. It colours candidates lowest vertex first, branches
  from the last colour class, and prunes when |R| + colour < target.
- **`sqfree_sums.Clique`.** The Python reference; the C code is its port, node
  for node.

## Why the result can be trusted

- **Every record set is checked by trial division alone.** The k-th record set
  has k elements, its largest is A392165(k), and every a + b is squarefree.
- **It reproduces the published data.** The scan reproduces all 39 published
  records, A392165(1..39), and the first 98 terms of A392164. A search that
  missed cliques, or invented them, would have shifted a published record.
- **Two implementations.** The Python reference matches the C engine on every
  candidate N ≤ 400: verdict, graph size, node count and record set.
- **An independent algorithm.** `rds.c` computes the exact clique number of
  G_N by Östergård's Russian-doll search, a different method with no colouring
  bound. f(N) = max(f(N − 1), ω(G_N) + 1) must then give the same records. It
  was run for every candidate N in [1104, 1300]; the log is `rds_crosscheck.txt`,
  replayable with `verify.py --rds`. That range covers the first three new records (40, 41, 42) and every candidate between 1103 and 1300 (about 1.2 × 10^11 nodes).

## Replay

```sh
python3 -I certificates/erdos-1109/verify.py          # every N <= 1103: the 39 published records (~10 s; needs cc)
python3 -I certificates/erdos-1109/verify.py --full   # every N <= 2000 (~55 CPU-minutes, split over --jobs)
python3 -I certificates/erdos-1109/verify.py --rds    # the independent Russian-doll cross-check (~1 CPU-hour, split over --jobs)
```

| file | role |
|---|---|
| `sqfree_sums.py` | the Python reference search and the trial-division witness check |
| `sqclique.c` | C port of the search, node for node |
| `rds.c` | independent exact clique numbers (Russian-doll search) |
| `verify.py` | the replay; reads RESULT.json, never writes it |
| `RESULT.json` | receipt: per candidate N the verdict, graph size and node count; each record's set |
| `rds_crosscheck.txt` | the Russian-doll log over [1104, 1300] |
| `emit_result.py` | regenerates RESULT.json into a *different* directory |

## Scope — what is not certified

- **Not Erdős #1109.** The questions are asymptotic: how f(N) grows.
  - Erdős–Sárközy (1987): log N ≪ f(N) ≪ N^{3/4} log N.
  - Konyagin (2004): (log log N)(log N)² ≪ f(N) ≪ N^{11/15 + o(1)}.
  - Whether f(N) ≤ N^{o(1)} is open.

  A table to 2000 only illustrates them.
- **A verified-search receipt, not a formal proof.**

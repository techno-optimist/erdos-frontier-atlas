# Erdős #1109 — sets with squarefree sumsets: records of A392164 through N = 2000

**Problem node `P1109`; OEIS [A392164](https://oeis.org/A392164) and
[A392165](https://oeis.org/A392165).** f(N) = A392164(N) is the size of the
largest S ⊆ {1, …, N} such that every element of S + S (a + a included) is
squarefree. A392165(k) is the least N with f(N) ≥ k, the index of the k-th
record. OEIS lists A392165(1..39), up to 1103 (C. Wu), and a b-file of
A392164 to N = 700.

**Update 2026-10-27 (OEIS has moved past this table).** OEIS A392165 now lists
the data a(1..54), matching every term here, and a b-file a(1..65) by Leandre Jack
(terms 55..65 = 2071, 2141, 2193, 2287, 2355, 2427, 2455, 2627, 2729, 2741, 2993),
with an A392164 b-file to N = 3000 (f(3000) = 65). An offline cross-check found the
certificate's f(N) equal to that b-file for every N ≤ 2000. Who published 40..54 first
was not determined. The atlas gap-map cell for #1109 now points at A392165(66).
Terms 55..65 and f(N) for 2000 < N ≤ 3000 are covered by a second, separately written
search (below, contract `erdos-1109-a392165-55-65`); they confirm Leandre Jack's
terms and add nothing new.

## What this certificate establishes

**A392165(1..54) and f(N) for every N ≤ 2000; A392165(40..54) were not in OEIS when this was computed (2026-09-28).**

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

So f(2000) = 54, A392165(55) > 2000 (A392165(55) = 2071 is covered by the second search below), and A392164(N) for N ≤ 2000
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
| `sqc_ford.c` | the second, separately written search engine (N ≤ 3000) |
| `ford_searches_2_3000.txt` | its 1,213 committed answers, one line per N |
| `verify_ford_3000.py` | the replay for the second search; reads, never writes |
| `ford_searches_3001_3065.txt` | the second search's 29 answers for 3001 ≤ N ≤ 3065 |
| `g4_crosscheck_3001_3065.txt` | `sqclique.c` repeating those 29 answers (C = no clique, R = record with its set) |
| `verify_ford_3065.py` | the replay to N = 3065; reads, never writes |

## Second search to N = 3000 (2026-10-27)

**A392165(55..65) = 2071, 2141, 2193, 2287, 2355, 2427, 2455, 2627, 2729, 2741, 2993 and f(N) for every N ≤ 3000 (f(3000) = 65), from a separately written search; this confirms Leandre Jack's OEIS b-files and is not new.**

`sqc_ford.c` was written from the definition alone, without reading the code
above. It decides "is there an S of size t + 1 with max S = N?" by a bitset
branch and bound over the same graph V_N, ordering vertices by degree
(highest first) with a greedy-colouring bound and no mod-4 reduction. That is the
same family of method as `sqclique.c`, so the two are independent code, not
independent mathematics. It was asked one question per N ≤ 3000 with 2N
squarefree, 1,213 searches and about 1.05 × 10^11 nodes in all. Each answer is one
line of `ford_searches_2_3000.txt`.

Because f(N) ≤ f(N − 1) + 1, the replay chains those answers from f(1) = 1 with
no outside input. Each target must equal f(N − 1), and each FOUND set is checked
by trial division. The chain must reproduce A392165(1..54) from `RESULT.json`
exactly, and it yields 55..65 above.

```sh
python3 -I certificates/erdos-1109/verify_ford_3000.py                  # chain, witnesses, controls, re-runs the 692 cheap searches (~10 s)
python3 -I certificates/erdos-1109/verify_ford_3000.py --full --jobs K  # re-runs all 1,213 searches byte for byte (~40+ core-hours)
```

The fast replay re-runs only the searches with at most 10^6 nodes, so it checks
the receipt without certifying the expensive NONE answers. Only `--full`
certifies the claim. Planted controls (a bad witness, a flipped verdict and a
non-squarefree pair) must be rejected, and the C engine must agree with a pure
Python clique search for every N ≤ 60.

## Extension to N = 3065: A392165(66) (2026-10-28)

**A392165(66) = 3065 and f(N) for every N ≤ 3065 (f(3064) = 65, f(3065) = 66): new, since the OEIS b-file ends at a(65) = 2993; each of the 29 new answers is matched by a second engine.**

`sqc_ford.c` (unchanged) was asked the next question for every N in 3001..3065
with 2N squarefree: is there a 66-element S with max S = N? Chained from
f(3000) = 65, the answer is NONE at all 28 such N up to 3063 and FOUND at
N = 3065. The other 36 N in 3001..3064 have 2N not squarefree, so they cannot be
records. The 29 searches took about 5.58 × 10^10 nodes; the largest NONE, at
N = 3047, took 4.73 × 10^9. They are the lines of `ford_searches_3001_3065.txt`.

Each answer was then repeated by `sqclique.c`, the original engine, in
`g4_crosscheck_3001_3065.txt`: no clique (C) at all 28 NONE N and a record (R) at
3065, with equal graph sizes on all 29. Both engines returned the same 66-element
set. They are independent code in the same colouring branch-and-bound family, not
independent mathematics.

When this was computed, the OEIS A392165 b-file (Leandre Jack) ended at
a(65) = 2993 and the A392164 b-file at N = 3000; his e1109 code repository lists
nothing beyond them (re-checked 2026-10-28).

```sh
python3 -I certificates/erdos-1109/verify_ford_3065.py                 # chain to 3065, witnesses, engine agreement, controls, cheap re-runs (~10 s)
python3 -I certificates/erdos-1109/verify_ford_3065.py --new --jobs K  # also re-runs the 29 searches in 3001..3065 byte for byte (~5.6 × 10^10 nodes)
python3 -I certificates/erdos-1109/verify_ford_3065.py --full --jobs K # re-runs all 1,242 searches byte for byte
```

The fast replay checks the receipt without certifying the expensive NONE answers.
`--new` certifies the 29 new answers given the 1,213 before them, and `--full`
certifies the whole chain. Planted controls must be rejected: a bad witness at
3065, the largest NONE flipped, a dropped search, an engine disagreement and a
non-squarefree pair.

## Scope — what is not certified

- **Not Erdős #1109.** The questions are asymptotic: how f(N) grows.
  - Erdős–Sárközy (1987): log N ≪ f(N) ≪ N^{3/4} log N.
  - Konyagin (2004): (log log N)(log N)² ≪ f(N) ≪ N^{11/15 + o(1)}.
  - Whether f(N) ≤ N^{o(1)} is open.

  A table to 3065 only illustrates them.
- **A verified-search receipt, not a formal proof.**

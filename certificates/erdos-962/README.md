# Erdős #962 — long runs of integers with a large prime factor: A327909 through n = 1102

**Problem node `P962`; OEIS [A327909](https://oeis.org/A327909).** A327909(n) is
the smallest start of a run of n or more consecutive integers, each having a
prime factor greater than n. The OEIS b-file stops at n = 999
(a(999) = 22369305365; D. Spencer, terms 1..369 by T. Garrison).

## What this certificate establishes

**A327909(n) for 1 ≤ n ≤ 1102; a(1000..1102) are new.**

Every value is recomputed from scratch. Each a(n) comes with the maximal run
that starts there, checked by gcd alone. Its minimality comes from an exact scan
of every integer up to 4.2 × 10^10.

| n | a(n) | length of the run there |
|---:|---:|---:|
| 995–1003 | 22369305365 | 1003 |
| 1004–1011 | 25446495399 | 1011 |
| 1012 | 28119442098 | 1030 |
| … | … | … |
| 1097–1102 | 41063158607 | 1183 |

All 1102 values, with their run lengths, are in `RESULT.json`.

- **a(1000..1003) needed no search.** The run starting at a(999) is 1003 integers
  long. Every n from 997 to 1008 sees the same run boundaries, because no prime
  lies strictly between 997 and 1009.
- **The scan reproduces the published data.** It recomputes a(1..44) (the
  OEIS data) and the b-file's last term, a(999) = 22369305365.

## What it says about k(n)

Erdős's k(n) is the largest k such that some m ≤ n has m + 1, …, m + k each
divisible by a prime > k. This is the definition in formal-conjectures,
`ErdosProblems/962.lean`. Since a(k) is nondecreasing,

  k(n) = max { k : a(k) ≤ n + 1 },

so this table gives k(n) exactly for every n < 41063158606, and k(n) ≥ 1102
beyond that.

At n ≈ 4.1 × 10^10, log k(n) = log 1102 ≈ 7.00. Compare
√(log n · log log n) ≈ 8.84, whose ratio to log k(n) is about 0.79; Tang's
lower bound has the constant 1/√2 ≈ 0.707. This is one data point, not
evidence about the asymptotics.

## Method

Let p be the largest prime ≤ n. "Has a prime factor > n" means "is not
p-smooth". So for every n between two consecutive primes p ≤ n < q, the runs
are the gaps between consecutive p-smooth integers, and a(n) is where the first
gap of length ≥ n begins. One scan of [1, X] therefore serves every n at once,
one class per prime p.

- **Exact smoothness.** A segmented sieve multiplies, for each m, the prime
  powers p^k dividing m with p ≤ 1097 (acc[m] *= p for each multiple of p^k).
  So m is 1097-smooth exactly when acc[m] = m. The last prime to hit m is its
  largest such prime factor. Only integer arithmetic is involved; there are no
  logarithms or tolerances.
- **`runs.c`, sequential.** It follows every class in one pass and prints a(n)
  and the run length for every n it reaches.
- **`chunk.c`, parallel.** It scans one piece of [1, X] and prints, per class,
  its first and last smooth integers and its record-breaking gaps.
  `smooth_runs.merge_chunks` recombines the pieces exactly: within a piece, the
  first gap of length ≥ n is always a record, and the gaps that straddle a cut
  are rebuilt from the first/last smooth integers.

## Why the result can be trusted

- **Every run is checked by arithmetic alone.**
  - For each a(n), every integer of the recorded run has a prime factor above p.
    The check divides out gcds with the primorial p#, sharing no code with the
    sieve.
  - The integers just before and just after the run are p-smooth.
  - The run is at least n long.
- **Two engines and a reference must agree.**
  - The sequential engine and the chunked engine must agree on every a(n) and
    run length they both reach.
  - The Python reference must also agree on [1, 10^6] for n ≤ 120. It gets
    greatest prime factors from a smallest-prime-factor sieve, a different
    method from the product sieve.
  - Cutting the scan into uneven pieces must change nothing.
- **Cross-checks.** a(1..44) equal the OEIS data. a(999) equals the last b-file
  term. a(n) is nondecreasing.
- **Planted failures.** A run shifted by one, claimed one longer, or started one
  late is rejected.

## Replay

```sh
python3 -I certificates/erdos-962/verify.py          # a(1..400): exact scan of [1, 2*10^8] (~20 s; needs cc)
python3 -I certificates/erdos-962/verify.py --full   # a(1..1102): scan of [1, 4.2*10^10], ~15 CPU-minutes over --jobs
```

| file | role |
|---|---|
| `runs.c` | sequential engine, all classes in one pass |
| `chunk.c` | chunked engine, one piece of the scan; pieces run in parallel |
| `smooth_runs.py` | Python reference sieve, the gcd witness check, and the chunk merge |
| `verify.py` | the replay; reads RESULT.json, never writes it |
| `RESULT.json` | receipt: a(n) and the length of its run, for n = 1..1102 |
| `emit_result.py` | regenerates RESULT.json into a *different* directory |

## Scope — what is not certified

- **Not Erdős #962.** The question is the growth of k(n) (is log k(n) at most
  (log n)^{1/2 + o(1)}?). A finite table only illustrates it.
- **Minimality is only as good as the scan.** It rests on the two engines, which
  share the sieve design but not code, and on the reference over the small
  range. It is a verified-search receipt, not a formal proof.
- **a(1103) is not computed.** 1103 is prime, so from n = 1103 on, integers whose
  largest prime factor is 1103 also break runs.

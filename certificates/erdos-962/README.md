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
| `RESULT_ford_1200.json` | extension receipt: a(n) and run length for n = 1..1200 (written by `emit_result.py --nmax 1200`) |
| `runs_ford_1200.txt` | the sequential engine's output for NMAX 1200 over [1, 7.5*10^10], one line per n |
| `verify_ford_1200.py` | the replay for the extension; reads, never writes |
| `RESULT_ford_1300.json` | second extension receipt: a(n) and run length for n = 1..1300 (written by `emit_result.py --nmax 1300`) |
| `runs_ford_1300.txt` | the sequential engine's output for NMAX 1300 over [1, 10^11], one line per n |
| `verify_ford_1300.py` | the replay for the second extension; reads, never writes |
| `RESULT_ford_1400.json` | third extension receipt: a(n) and run length for n = 1..1400 (written by `emit_result.py --nmax 1400`) |
| `runs_ford_1400.txt` | the sequential engine's output for NMAX 1400 over [1, 4*10^11], one line per n |
| `verify_ford_1400.py` | the replay for the third extension; reads, never writes |
| `RESULT_ford_1500.json` | fourth extension receipt: a(n) and run length for n = 1..1500 (written by `emit_result.py --nmax 1500`) |
| `runs_ford_1500.txt` | the sequential engine's output for NMAX 1500 over [1, 3.2*10^11], one line per n |
| `verify_ford_1500.py` | the replay for the fourth extension; reads, never writes |
| `RESULT_ford_1600.json` | fifth extension receipt: a(n) and run length for n = 1..1600 (written by `emit_result.py --nmax 1600`) |
| `runs_ford_1600.txt` | the sequential engine's output for NMAX 1600 over [1, 344421235993], one line per n |
| `verify_ford_1600.py` | the replay for the fifth extension; reads, never writes |
| `RESULT_ford_1700.json` | sixth extension receipt: a(n) and run length for n = 1..1700 (written by `emit_result.py --nmax 1700`) |
| `runs_ford_1700.txt` | the sequential engine's output for NMAX 1700 over [1, 453273053620], one line per n |
| `verify_ford_1700.py` | the replay for the sixth extension; reads, never writes |
| `RESULT_ford_1800.json` | seventh extension receipt: a(n) and run length for n = 1..1800 (written by `emit_result.py --nmax 1800`) |
| `runs_ford_1800.txt` | the sequential engine's output for NMAX 1800 over [1, 712311270000], one line per n |
| `verify_ford_1800.py` | the replay for the seventh extension; reads, never writes |
| `RESULT_ford_1900.json` | eighth extension receipt: a(n) and run length for n = 1..1900 (written by `emit_result.py --nmax 1900`) |
| `runs_ford_1900.txt` | the sequential engine's output for NMAX 1900 over [1, 949555600000], one line per n |
| `verify_ford_1900.py` | the replay for the eighth extension; reads, never writes |

## Scope — what is not certified

- **Not Erdős #962.** The question is the growth of k(n) (is log k(n) at most
  (log n)^{1/2 + o(1)}?). A finite table only illustrates it.
- **Minimality is only as good as the scan.** It rests on the two engines, which
  share the sieve design but not code, and on the reference over the small
  range. It is a verified-search receipt, not a formal proof.
- **a(1901) is not computed.** a(1103..1900) are covered by the eight extensions below.
  All that is claimed here is a(1901) ≥ a(1900) = 949555592339.

## Extension to n = 1200 (2026-10-27)

**A327909(n) for 1103 ≤ n ≤ 1200: a(1103..1108) = 41063158607, a(1109..1113) = 43204475623, a(1114..1152) = 53907372933, a(1153..1156) = 61103835710, a(1157..1200) = 74759540976; all 98 are new (the OEIS b-file ends at 999).**

| n | a(n) | length of the run there |
|---:|---:|---:|
| 1103–1108 | 41063158607 | 1183 |
| 1109–1113 | 43204475623 | 1113 |
| 1114–1152 | 53907372933 | 1245 |
| 1153–1156 | 61103835710 | 1156 |
| 1157–1200 | 74759540976 | 1211 |

The files above are frozen, so this extension adds new files and changes none.
`RESULT_ford_1200.json` was written by the certificate's own `emit_result.py`
(`--nmax 1200 --limit 75000000000`). That is one exact chunked scan of every
integer up to 7.5 × 10^10. Its entries for n ≤ 1102 equal `RESULT.json`
exactly. `runs_ford_1200.txt` is the sequential engine `runs.c`, run separately
over the same range with NMAX 1200, and it agrees on every n ≤ 1200.

- **a(1103..1108) needed no search.** The run starting at a(1102) = 41063158607
  is 1183 integers long, and none of its integers has largest prime factor 1103,
  so it has the same length in class 1103 (n = 1103..1108). Since a(n) is
  nondecreasing, a(1103..1108) = a(1102).
- Erdős's k(n) = max { k : a(k) ≤ n + 1 } is now exact for every
  n < 74759540975, and k(n) ≥ 1200 beyond that.

```sh
python3 -I certificates/erdos-962/verify_ford_1200.py               # prefix, gcd witnesses, committed runs.c output, engines on [1, 2*10^8] (~10 s); does not certify
python3 -I certificates/erdos-962/verify_ford_1200.py --full        # chunk.c rescans [1, 7.5*10^10] and certifies a(1..1200) (~15 CPU-minutes)
python3 -I certificates/erdos-962/verify_ford_1200.py --full --runs # also re-runs runs.c over the same range (~12 min, one core)
```

The fast replay checks the receipt: the frozen prefix, every run by gcd, and
agreement with the committed `runs.c` output. It does not re-establish
minimality for n > 400, and only `--full` certifies the claim. Planted failures
must be refused: a(1157) claimed one smaller, run(1200) claimed one longer, the
a(1103) run started one late, and a(1050) altered in the prefix. The scope above
still applies. This is a verified-search receipt, not a formal proof, and the
two engines share the sieve design but not code.

## Extension to n = 1300 (2026-10-27)

**A327909(n) for 1201 ≤ n ≤ 1300: a(1201..1211) = 74759540976, a(1212..1250) = 80437383604, a(1251..1268) = 98440709185, a(1269..1290) = 99182650001, a(1291..1300) = 99182650021; all 100 are new (the OEIS b-file ends at 999).**

| n | a(n) | length of the run there |
|---:|---:|---:|
| 1201–1211 | 74759540976 | 1211 |
| 1212–1250 | 80437383604 | 1250 |
| 1251–1268 | 98440709185 | 1268 |
| 1269–1278 | 99182650001 | 1391 |
| 1279–1290 | 99182650001 | 1369 |
| 1291–1300 | 99182650021 | 1349 |

This second extension again adds new files and changes none (the first
extension's files are frozen too). `RESULT_ford_1300.json` was written by the
certificate's own `emit_result.py` (`--nmax 1300 --limit 100000000000`): one
exact chunked scan of every integer up to 10^11. Its entries for n ≤ 1102 equal
`RESULT.json` and its entries for n ≤ 1200 equal `RESULT_ford_1200.json`
exactly. `runs_ford_1300.txt` is the sequential engine `runs.c`, run separately
over [1, 10^11] with NMAX 1300, and it agrees on every n ≤ 1300.

- **a(1201..1211) needed no search.** The run starting at a(1200) = 74759540976
  is 1211 integers long in class 1193, and none of its integers has largest prime
  factor 1201, so a(1201..1211) = a(1200).
- Erdős's k(n) = max { k : a(k) ≤ n + 1 } is now exact for every
  n < 99182650020, and k(n) ≥ 1300 beyond that.

```sh
python3 -I certificates/erdos-962/verify_ford_1300.py               # prefixes, gcd witnesses, committed runs.c output, engines on [1, 2*10^8]; does not certify
python3 -I certificates/erdos-962/verify_ford_1300.py --full        # chunk.c rescans [1, 10^11] and certifies a(1..1300) (~20 CPU-minutes)
python3 -I certificates/erdos-962/verify_ford_1300.py --full --runs # also re-runs runs.c over the same range (~17 min, one core)
```

The fast replay checks the receipt: both frozen prefixes, every run by gcd, and
agreement with the committed `runs.c` output. Only `--full` certifies the claim.
Planted failures must be refused: a(1212) claimed one smaller, run(1300) claimed
one longer, the a(1201) run started one late, and a(1150) altered in the
a(1..1200) prefix. The scope above still applies: a verified-search receipt, not
a formal proof; the two engines share the sieve design but not code.

## Extension to n = 1400 (2026-10-27)

**A327909(n) for 1301 ≤ n ≤ 1400: a(1301..1306) = 99182650021, a(1307..1308) = 105735468441, a(1309..1310) = 127604829142, a(1311..1360) = 134086311082, a(1361..1400) = 162799483945; all 100 are new (the OEIS b-file ends at 999).**

| n | a(n) | length of the run there |
|---:|---:|---:|
| 1301–1306 | 99182650021 | 1349 |
| 1307–1308 | 105735468441 | 1308 |
| 1309–1310 | 127604829142 | 1310 |
| 1311–1360 | 134086311082 | 1388 |
| 1361–1400 | 162799483945 | 1409 |

This third extension again adds new files and changes none (the earlier
extensions' files are frozen too). `RESULT_ford_1400.json` was written by the
certificate's own `emit_result.py` (`--nmax 1400 --limit 400000000000`): one
exact chunked scan of every integer up to 4 × 10^11 (589 s wall on 8 jobs). Its
entries for n ≤ 1102 equal `RESULT.json`, its entries for n ≤ 1200 equal
`RESULT_ford_1200.json` and its entries for n ≤ 1300 equal `RESULT_ford_1300.json`
exactly. `runs_ford_1400.txt` is the sequential engine `runs.c`, run separately
over [1, 4 × 10^11] with NMAX 1400, and it agrees on every n ≤ 1400.

- **a(1301..1306) needed no new run.** The run starting at a(1300) = 99182650021
  is 1349 integers long and contains no integer with largest prime factor 1301
  or 1303, so a(1301..1306) = a(1300).
- Erdős's k(n) = max { k : a(k) ≤ n + 1 } is now exact for every
  n < 162799483944, and k(n) ≥ 1400 beyond that.

```sh
python3 -I certificates/erdos-962/verify_ford_1400.py               # prefixes, gcd witnesses, committed runs.c output, engines on [1, 2*10^8]; does not certify
python3 -I certificates/erdos-962/verify_ford_1400.py --full        # chunk.c rescans [1, 4*10^11] and certifies a(1..1400)
python3 -I certificates/erdos-962/verify_ford_1400.py --full --runs # also re-runs runs.c over the same range (~64 min, one core)
```

The fast replay checks the receipt: all three frozen prefixes, every run by gcd,
and agreement with the committed `runs.c` output. Only `--full` certifies the
claim. Planted failures must be refused: a(1311) claimed one smaller, run(1400)
claimed one longer, the a(1301) run started one late, and a(1250) altered in the
a(1..1300) prefix. The scope above still applies: a verified-search receipt, not
a formal proof; the two engines share the sieve design but not code.

## Extension to n = 1500 (2026-10-27)

**A327909(n) for 1401 ≤ n ≤ 1500: a(1401..1409) = 162799483945, a(1410..1438) = 174613219434, a(1439..1446) = 200683383896, a(1447..1485) = 201615234946, a(1486) = 234633350771, a(1487..1488) = 234633350816, a(1489..1498) = 273855996947, a(1499..1500) = 310735124719; all 100 are new (the OEIS b-file ends at 999).**

| n | a(n) | length of the run there |
|---:|---:|---:|
| 1401–1409 | 162799483945 | 1409 |
| 1410–1438 | 174613219434 | 1458 |
| 1439–1446 | 200683383896 | 1483 |
| 1447–1485 | 201615234946 | 1485 |
| 1486 | 234633350771 | 1549 |
| 1487–1488 | 234633350816 | 1504 |
| 1489–1498 | 273855996947 | 1568 |
| 1499–1500 | 310735124719 | 1681 |

This fourth extension again adds new files and changes none (the earlier
extensions' files are frozen too). `RESULT_ford_1500.json` was written by the
certificate's own `emit_result.py` (`--nmax 1500 --limit 320000000000`): one
exact chunked scan of every integer up to 3.2 × 10^11 (475 s wall on 8 jobs). Its
entries for n ≤ 1102, 1200, 1300 and 1400 equal `RESULT.json`,
`RESULT_ford_1200.json`, `RESULT_ford_1300.json` and `RESULT_ford_1400.json`
exactly. `runs_ford_1500.txt` is the sequential engine `runs.c`, run separately
over [1, 3.2 × 10^11] with NMAX 1500, and it agrees on every n ≤ 1500. The scan
limit is lower than the third extension's because every run needed for n ≤ 1500
closes before 3.2 × 10^11 (the last, at a(1500), ends at 310735126399).

- **a(1401..1409) needed no new run.** The run starting at a(1400) = 162799483945
  is 1409 integers long and contains no integer with largest prime factor 1409,
  so a(1401..1409) = a(1400), as the lead recorded with the third extension expected.
- Erdős's k(n) = max { k : a(k) ≤ n + 1 } is now exact for every
  n < 310735124718, and k(n) ≥ 1500 beyond that.

```sh
python3 -I certificates/erdos-962/verify_ford_1500.py               # prefixes, gcd witnesses, committed runs.c output, engines on [1, 2*10^8]; does not certify
python3 -I certificates/erdos-962/verify_ford_1500.py --full        # chunk.c rescans [1, 3.2*10^11] and certifies a(1..1500)
python3 -I certificates/erdos-962/verify_ford_1500.py --full --runs # also re-runs runs.c over the same range (~74 min, one core)
```

The fast replay checks the receipt: all four frozen prefixes, every run by gcd,
and agreement with the committed `runs.c` output. Only `--full` certifies the
claim. Planted failures must be refused: a(1447) claimed one smaller, run(1500)
claimed one longer, the a(1401) run started one late, and a(1350) altered in the
a(1..1400) prefix. The scope above still applies: a verified-search receipt, not
a formal proof; the two engines share the sieve design but not code.

## Extension to n = 1600 (2026-10-30)

**A327909(n) for 1501 ≤ n ≤ 1600: a(1501..1510) = 310735124719, a(1511..1520) = 314314563525, a(1521..1562) = 320450471479, a(1563..1567) = 335391702797, a(1568..1600) = 344421234376; all 100 are new (the OEIS b-file ends at 999).**

| n | a(n) | length of the run there |
|---:|---:|---:|
| 1501–1510 | 310735124719 | 1681 |
| 1511–1520 | 314314563525 | 1520 |
| 1521–1562 | 320450471479 | 1562 |
| 1563–1567 | 335391702797 | 1567 |
| 1568–1600 | 344421234376 | 1616 |

This fifth extension again adds new files and changes none (the earlier
extensions' files are frozen too). `RESULT_ford_1600.json` was written by the
certificate's own `emit_result.py` (`--nmax 1600 --limit 344421235993`): one
exact chunked scan of every integer up to 344421235993 (890 s wall on 8 jobs). Its
entries for n ≤ 1102, 1200, 1300, 1400 and 1500 equal `RESULT.json`,
`RESULT_ford_1200.json`, `RESULT_ford_1300.json`, `RESULT_ford_1400.json` and
`RESULT_ford_1500.json` exactly. `runs_ford_1600.txt` is the sequential engine
`runs.c`, run separately over [1, 344421235993] with NMAX 1600, and it agrees on
every n ≤ 1600. The scan limit sits just above the end of the last run needed
(the run at a(1600) ends at 344421235991).

- **a(1501..1510) needed no new run.** The run starting at a(1500) = 310735124719
  is 1681 integers long in class 1499, and no prime lies strictly between 1499 and
  1511, so a(1501..1510) = a(1500), as the lead recorded with the fourth extension expected.
- Erdős's k(n) = max { k : a(k) ≤ n + 1 } is now exact for every
  n < 344421234375, and k(n) ≥ 1600 beyond that.
- 1601 is prime, so a(1601) needs a new scan (NMAX ≥ 1601, from a(1600) on).

```sh
python3 -I certificates/erdos-962/verify_ford_1600.py               # prefixes, gcd witnesses, committed runs.c output, engines on [1, 2*10^8]; does not certify
python3 -I certificates/erdos-962/verify_ford_1600.py --full        # chunk.c rescans [1, 344421235993] and certifies a(1..1600)
python3 -I certificates/erdos-962/verify_ford_1600.py --full --runs # also re-runs runs.c over the same range (~71 min, one core)
```

The fast replay checks the receipt: all five frozen prefixes, every run by gcd,
and agreement with the committed `runs.c` output. Only `--full` certifies the
claim. Planted failures must be refused: a(1568) claimed one smaller, run(1600)
claimed one longer, the a(1501) run started one late, and a(1450) altered in the
a(1..1500) prefix. The scope above still applies: a verified-search receipt, not
a formal proof; the two engines share the sieve design but not code.

## Extension to n = 1700 (2026-10-30)

**A327909(n) for 1601 ≤ n ≤ 1700: a(1601..1612) = 418346872165, a(1613..1636) = 445969722294, a(1637..1700) = 453273051862; all 100 are new (the OEIS b-file ends at 999).**

| n | a(n) | length of the run there |
|---:|---:|---:|
| 1601–1612 | 418346872165 | 1715 |
| 1613–1636 | 445969722294 | 1728 |
| 1637–1700 | 453273051862 | 1757 |

This sixth extension again adds new files and changes none (the earlier
extensions' files are frozen too). `RESULT_ford_1700.json` was written by the
certificate's own `emit_result.py` (`--nmax 1700 --limit 453273053620`): one
exact chunked scan of every integer up to 453273053620 (783 s wall on 8 jobs). Its
entries for n ≤ 1102, 1200, 1300, 1400, 1500 and 1600 equal `RESULT.json`,
`RESULT_ford_1200.json`, `RESULT_ford_1300.json`, `RESULT_ford_1400.json`,
`RESULT_ford_1500.json` and `RESULT_ford_1600.json` exactly. `runs_ford_1700.txt`
is the sequential engine `runs.c`, run separately over [1, 453273053620] with
NMAX 1700, and it agrees on every n ≤ 1700. The scan limit sits just above the
end of the last run needed (the run at a(1700) ends at 453273053618).

- **a(1601) needed a new run, as the fifth extension's lead expected.** 1601 is
  prime, so integers whose largest prime factor is 1601 also break runs; the
  run at a(1600) is split, and a(1601) = 418346872165 > a(1600).
- Erdős's k(n) = max { k : a(k) ≤ n + 1 } is now exact for every
  n < 453273051861, and k(n) ≥ 1700 beyond that.
- Lead for the next cell, not claimed here: 1700..1708 are not prime, so for
  n = 1701..1708 the class prime stays 1699, and the 1757-long run at a(1700)
  would give a(1701..1708) = a(1700). It needs its own receipt (NMAX ≥ 1708).

```sh
python3 -I certificates/erdos-962/verify_ford_1700.py               # prefixes, gcd witnesses, committed runs.c output, engines on [1, 2*10^8]; does not certify
python3 -I certificates/erdos-962/verify_ford_1700.py --full        # chunk.c rescans [1, 453273053620] and certifies a(1..1700)
python3 -I certificates/erdos-962/verify_ford_1700.py --full --runs # also re-runs runs.c over the same range (~132 min, one core)
```

The fast replay checks the receipt: all six frozen prefixes, every run by gcd,
and agreement with the committed `runs.c` output. Only `--full` certifies the
claim. Planted failures must be refused: a(1637) claimed one smaller, run(1700)
claimed one longer, the a(1601) run started one late, and a(1550) altered in the
a(1..1600) prefix. The scope above still applies: a verified-search receipt, not
a formal proof; the two engines share the sieve design but not code.

## Extension to n = 1800 (2026-10-30)

**A327909(n) for 1701 ≤ n ≤ 1800: a(1701..1708) = 453273051862, a(1709..1746) = 652614218763, a(1747..1800) = 712311265810; all 100 are new (the OEIS b-file ends at 999).**

| n | a(n) | length of the run there |
|---:|---:|---:|
| 1701–1708 | 453273051862 | 1757 |
| 1709–1746 | 652614218763 | 1922 |
| 1747–1800 | 712311265810 | 1858 |

This seventh extension again adds new files and changes none (the earlier
extensions' files are frozen too). `RESULT_ford_1800.json` was written by the
certificate's own `emit_result.py` (`--nmax 1800 --limit 712311270000`): one
exact chunked scan of every integer up to 712311270000 (1157 s wall on 8 jobs). Its
entries for n ≤ 1102, 1200, 1300, 1400, 1500, 1600 and 1700 equal `RESULT.json`,
`RESULT_ford_1200.json`, `RESULT_ford_1300.json`, `RESULT_ford_1400.json`,
`RESULT_ford_1500.json`, `RESULT_ford_1600.json` and `RESULT_ford_1700.json` exactly.
`runs_ford_1800.txt` is the sequential engine `runs.c`, run separately over
[1, 712311270000] with NMAX 1800, and it agrees on every n ≤ 1800. The scan limit
sits just above the end of the last run needed (the run at a(1800) ends at 712311267667).

- **The sixth extension's lead holds.** 1700..1708 are not prime, so for
  n = 1701..1708 the class prime stays 1699 and the 1757-long run at a(1700)
  still works: a(1701..1708) = a(1700) = 453273051862. 1709 is prime, which
  splits that run, and a(1709) = 652614218763.
- Erdős's k(n) = max { k : a(k) ≤ n + 1 } is now exact for every
  n < 712311265809, and k(n) ≥ 1800 beyond that.
- Next cell, not claimed here: 1801 is prime, so a(1801) may need a new run;
  only a(1801) ≥ a(1800) is known.

```sh
python3 -I certificates/erdos-962/verify_ford_1800.py               # prefixes, gcd witnesses, committed runs.c output, engines on [1, 2*10^8]; does not certify
python3 -I certificates/erdos-962/verify_ford_1800.py --full        # chunk.c rescans [1, 712311270000] and certifies a(1..1800)
python3 -I certificates/erdos-962/verify_ford_1800.py --full --runs # also re-runs runs.c over the same range (~163 min, one core)
```

The fast replay checks the receipt: all seven frozen prefixes, every run by gcd,
and agreement with the committed `runs.c` output. Only `--full` certifies the
claim. Planted failures must be refused: a(1747) claimed one smaller, run(1800)
claimed one longer, the a(1709) run started one late, and a(1650) altered in the
a(1..1700) prefix. The scope above still applies: a verified-search receipt, not
a formal proof; the two engines share the sieve design but not code.

## Extension to n = 1900 (2026-10-31)

**A327909(n) for 1801 ≤ n ≤ 1900: a(1801..1858) = 712311265810, a(1859..1884) = 783274569646, a(1885..1900) = 949555592339; all 100 are new (the OEIS b-file ends at 999).**

| n | a(n) | length of the run there |
|---:|---:|---:|
| 1801–1858 | 712311265810 | 1858 |
| 1859–1884 | 783274569646 | 1884 |
| 1885–1900 | 949555592339 | 1945 |

This eighth extension again adds new files and changes none (the earlier
extensions' files are frozen too). `RESULT_ford_1900.json` was written by the
certificate's own `emit_result.py` (`--nmax 1900 --limit 949555600000`): one
exact chunked scan of every integer up to 949555600000 (1498 s wall on 8 jobs). Its
entries for n ≤ 1102, 1200, 1300, 1400, 1500, 1600, 1700 and 1800 equal `RESULT.json`,
`RESULT_ford_1200.json`, `RESULT_ford_1300.json`, `RESULT_ford_1400.json`,
`RESULT_ford_1500.json`, `RESULT_ford_1600.json`, `RESULT_ford_1700.json` and
`RESULT_ford_1800.json` exactly. `runs_ford_1900.txt` is the sequential engine `runs.c`,
run separately over [1, 949555600000] with NMAX 1900, and it agrees on every n ≤ 1900.
The scan limit sits just above the end of the last run needed (the run at a(1900) ends at 949555594283).

- **The run at a(1800) carries over.** 1801 is prime, so the class prime changes at
  n = 1801, but every integer in the 1858-long run at a(1800) has a prime factor of at
  least 1879, and both of its neighbours are 1151-smooth. So a(1801..1858) = a(1800) =
  712311265810. Then a(1859) = 783274569646 (run 1884) and a(1885) = 949555592339 (run 1945).
- Erdős's k(n) = max { k : a(k) ≤ n + 1 } is now exact for every
  n < 949555592338, and k(n) ≥ 1900 beyond that.
- Next cell, not claimed here: 1901 is prime, so a(1901) may need a new run;
  only a(1901) ≥ a(1900) is known.

```sh
python3 -I certificates/erdos-962/verify_ford_1900.py               # prefixes, gcd witnesses, committed runs.c output, engines on [1, 2*10^8]; does not certify
python3 -I certificates/erdos-962/verify_ford_1900.py --full        # chunk.c rescans [1, 949555600000] and certifies a(1..1900)
python3 -I certificates/erdos-962/verify_ford_1900.py --full --runs # also re-runs runs.c over the same range (~269 min, one core)
```

The fast replay checks the receipt: all eight frozen prefixes, every run by gcd,
and agreement with the committed `runs.c` output. Only `--full` certifies the
claim. Planted failures must be refused: a(1859) claimed one smaller, run(1900)
claimed one longer, the a(1885) run started one late, and a(1750) altered in the
a(1..1800) prefix. The scope above still applies: a verified-search receipt, not
a formal proof; the two engines share the sieve design but not code.

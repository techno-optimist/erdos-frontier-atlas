# Erdős #376 — Kummer digit checker (not infinitude)

**Not a solution of #376.** Live page remains OPEN (browser 2026-09-11). Graham $1000 is infinitude; EGRS 1975 already does any two odd primes; three primes (3,5,7) open.

The attack graph points here: binomial + base-representation cell, witness = any n whose base-3 digits are in {0,1}, base-5 in {0,1,2}, base-7 in {0,1,2,3}.

## What this lane checks

Kummer: gcd(C(2n,n), 105)=1 iff those digit bounds (no carry in n+n in bases 3,5,7). Independent exact-integer equivalence through n=400. Negative control: n=5=12_3 fails.

All such n < 1000: **0, 1, 10, 756, 757**. Sparse, as Pomerance’s x^{0.02595} heuristic says.

See `search.md`: complete independent search through 3^24 matches OEIS A030979 with 17 terms, no extras. Does **not** claim a term > 10^70 or infinitude.

Replay:

```sh
python3 -I -B -m unittest discover -s experiments/astra-376-20260911 -p 'test_kummer.py' -v
```

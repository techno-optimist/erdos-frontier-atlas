# A389839(45) >= 624 (lower-bound step, not the value of a(45))

Gap 620 between consecutive integers coprime to 197# (product of the first 45 primes) is
witnessed in `verify2.txt` / `verify.txt`. Together with the earlier witnesses of gaps 618 and 622
(`certificates/erdos-854/a45_lower_620/`) and every even gap up to 616 already occurring for 197#
(A331118 / A329815, De Vlieger 2020), the smallest missing even gap is at least 624.
Bracket: 624 <= a(45) <= 644. Unwitnessed in the band: 624, 626, ..., 640 (9 values).

- `verify.py` / `batch.txt` / `verify.txt`: CRT-rebuild the annealer residue vector and gcd-check; planted t-2, t+2, x+2 rejected. Replay: `python3 -I verify.py batch.txt | diff - verify.txt`
- `verify2.py` / `verify2.txt`: independent check (own prime sieve, stdlib only). Replay: `python3 -I verify2.py | diff - verify2.txt`
- `ann.c`: the simulated-annealing search (seeded from the 622 residue vector).
- `RECEIPT.txt`, `FALSIFIER.txt`, `SHA256SUMS`: Ford's receipt, pre-registered falsifier, and hashes.

A computer search with gcd-checked witnesses; not submitted to OEIS.

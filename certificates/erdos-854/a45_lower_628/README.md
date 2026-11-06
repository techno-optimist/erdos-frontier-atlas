# A389839(45) >= 628 (lower-bound step, not the value of a(45))

Gap 626 between consecutive integers coprime to 197# (product of the first 45 primes) is
witnessed in `verify.txt` / `verify2.txt` (3 distinct residue vectors, all gcd-verified).
Together with the earlier witnesses of gaps 618 and 622 (`certificates/erdos-854/a45_lower_620/`),
620 (`certificates/erdos-854/a45_lower_624/`), 624 (`certificates/erdos-854/a45_lower_626/`),
and every even gap up to 616 already occurring for 197#
(A331118 / A329815, De Vlieger 2020), the smallest missing even gap is at least 628.
Bracket: 628 <= a(45) <= 644. Unwitnessed in the band: 628, 630, ..., 640 (7 values).

- `verify.py` / `batch.txt` / `verify.txt`: CRT-rebuild each annealer residue vector and gcd-check at 197#; planted t-2, t+2, x+2 rejected for every witness. Replay: `python3 -I verify.py batch.txt | diff - verify.txt`
- `verify2.py` / `verify2.txt`: independent trial-division check of all 3 witnesses (own prime sieve, CRT rebuild from batch.txt, stdlib only). Replay: `python3 -I verify2.py | diff - verify2.txt`
- `batch_ctrl.txt`: control run at t=624 (already witnessed), 4/4 seeds WITNESS.
- `ann.c`: the simulated-annealing search (seeded from the 624 / 622 / 620 residue vectors).
- `RECEIPT.txt`, `FALSIFIER.txt`, `SHA256SUMS`: Ford's receipt (workspace sha256 8d5399fc…6141), pre-registered falsifier, and hashes.

A computer search with gcd-checked witnesses, not a proof of the value; not checked against
unpublished tables (Gerbicz u(n), Ziller); not submitted to OEIS. Truncated batch (3/16 finished) —
claim rests on verified witnesses only.

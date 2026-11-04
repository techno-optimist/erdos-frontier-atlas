# A389839(45) >= 620 (lower-bound step, not the value of a(45))

Gaps 618 and 622 between consecutive integers coprime to 197# (product of the first 45 primes) are
witnessed in `verify2.txt`. With every even gap up to 616 already occurring for 197#
(A331118 / A329815, De Vlieger 2020), the smallest missing even gap is at least 620.
Bracket: 620 <= a(45) <= 644. Unwitnessed in the band: 620, 624, ..., 640.

- `verify2.py`: self-contained check (own prime sieve, stdlib only, under a second): `python3 -I verify2.py | diff - verify2.txt`
- `lift.py` / `result.txt`: the search that found the witnesses (CRT lift of the OEIS A048670 n = 44
  witness, attachment a048670_6.txt, which is read from a local copy and not redistributed here).
- `RECEIPT.txt`, `FALSIFIER.txt`: Ford's receipt and pre-registered falsifier.

A computer search with gcd-checked witnesses; not submitted to OEIS.

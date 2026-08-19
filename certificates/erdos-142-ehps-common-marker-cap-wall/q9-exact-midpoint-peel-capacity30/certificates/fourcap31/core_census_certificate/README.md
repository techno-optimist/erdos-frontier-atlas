# q=9 minimal-core census certificate

This immutable scratch certificate freezes the exact midpoint-core census for
sizes 6, 7, and 8 in `Z_9^2`.  The mathematical statement and scope are in
`THEOREM_NOTE.md`.

Quick nonmutating replay (about one minute on the source host):

```powershell
python -I .\replay.py --threads 12
```

or under Linux/WSL:

```bash
python3 -I ./replay.py --threads 12
```

This checks every frozen hash, replays all ledger semantics and affine orbits,
and independently scans every anchored subset through size 8.

Full nonmutating regeneration (35,966,010,366 subset decisions, about ten
minutes on the source host):

```powershell
python -I .\replay.py --full --threads 12
```

The full run compiles each enumerator in a temporary directory, regenerates its
ledger there, requires the exact census fingerprints, and byte-compares the
result with the frozen ledger.  Temporary binaries and generated files never
enter this directory.

Requirements: Python 3, `g++` (or `c++`) with C++14 and OpenMP support.  The
replay is solver-independent and uses no third-party Python packages.

`SHA256SUMS.txt` binds every payload except itself.  `FILE_SIZES.tsv` records
the exact byte size of every frozen file.

# Compact exact q9 certificate

This self-contained package proves

```text
30 <= C_9 <= 31
```

for strict midpoint potentials on `(Z/9Z)^2`.  It does **not** claim that a
31-point support exists.  The primary upper-bound certificate is a direct
C++14 exhaustive cover over six fibres for each of the two normalized slab
templates; no SAT solver, proof checker, network access, random seed, or
timeout is used.

## Portable replay

Requirements are Python 3 and one C++14 compiler discoverable as `g++`,
`clang++`, or `c++`.  From this directory run:

```text
python verify_all.py
```

On Unix-like systems `./run.sh` is equivalent; on PowerShell use
`./run.ps1`.  The optional slow independent regeneration of every template0
minimal blocker through size five is:

```text
python verify_all.py --exhaustive-template0
```

The aggregate entrypoint first checks the closed SHA-256 manifest and complete
file-size inventory, validates the path-free source-provenance schema, runs
the finite geometry and semantic replays, compiles the verifier in a temporary
directory, proves both template masters UNSAT, exercises negative controls,
and finally checks that no packaged byte or file inventory changed.  Only
after both template searches pass does it print
`PASS_Q9_CAPACITY_THEOREM 30<=C9<=31`.

Expected theorem-search fingerprints are:

| template | recursion nodes | result |
|---|---:|---|
| 0 | 3,017,764 | exact-20 UNSAT |
| 1 | 1,989,055 | exact-20 UNSAT |

The target-19 SAT controls printed by the executable concern the relaxed
listed-blocker master only.  They are explicitly not peelable 31-point
witnesses; direct midpoint-core replay leaves residual cores of sizes 27 and
31 respectively.

## Contents and scope

- `THEOREM.md` gives the finite proof: potential/peeling equivalence, exact
  size-30 witness, saturated-fibre/slab reduction, 157,464-case slab census,
  two 2,916-element orbits, sound blocker ledgers, and exhaustive cover.
- `COMMON_MARKER_H8_COROLLARY.md` states the separate conditional consequence
  in the literal one-common-marker, pointwise physical-potential model and
  derives its exact epsilon interval.
- `DRAT_PROVENANCE.md` records independent external proof hashes and
  compression measurements.  No large DRAT payload or checker binary is
  shipped because the compact exhaustive verifier is the trust path.
- `SOURCE_BINDINGS.json`, `SHA256SUMS.txt`, and `FILE_SIZES.tsv` bind source
  provenance, every packaged payload hash, and every packaged file size.

The h=8 consequence is limited to the analytic model stated in its own note.
Nothing in this package handles phase-owned or context-owned markers, performs
an integer transfer, improves `r_3(N)`, or resolves Erdős Problem 142.

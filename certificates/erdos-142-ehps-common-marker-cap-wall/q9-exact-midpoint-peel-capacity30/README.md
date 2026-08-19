# Portable exact-`C9=30` certificate binder

This self-contained compact packet binds the exact lower witness, fibre cap,
saturated-slab census and orbit reduction, complete size-31 profile split,
normalized four-cap UNSAT certificate, and direct T0/T1 slab UNSAT
certificates.

Run the standard compact replay from this directory:

```text
python -I -B verify_all.py
```

It needs Python 3 and a C++14 compiler. It creates compilation and generated
CNF artifacts only in an operating-system temporary directory. On success it
prints:

```text
STRUCTURE_READY_EXTERNAL_PROOFS_REQUIRED
PASS_NONMUTATION
```

Raw proofs are intentionally external. For a full proof replay, use a pinned
checker and directories containing the external artifacts named exactly as in
the frozen ledgers:

```text
python -I -B verify_all.py \
  --fourcap-artifact-dir PATH_TO_24_CNFS_AND_PROOFS \
  --direct-proof-dir PATH_TO_TWO_DIRECT_PROOFS \
  --checker PATH_TO_PINNED_DRAT_TRIM \
  --proof-jobs 4
```

The direct proof directory must contain `case0_direct_unary31.drat` and
`case1_direct_unary31.drat`. The four-cap directory must contain the 24
`.cnf`/`.drat` pairs named in
`certificates/fourcap31/PROOF_PROVENANCE.json`. A full success emits
`CONCLUSION_EXACT_C9_30` only after all 26 proof checks return `s VERIFIED`.

`THEOREM.md` gives the exact finite argument and scope. `BINDINGS.json` pins
the three source certificates and every external proof/log/checker digest.
`COMMON_MARKER_H8_COROLLARY.md` gives the separately scoped conditional
literal common-marker consequence and its exact `n>=7926` arithmetic replay.
`SHA256SUMS.txt` closes the compact file tree; compiled binaries, raw proofs,
caches, and machine-local paths are absent.

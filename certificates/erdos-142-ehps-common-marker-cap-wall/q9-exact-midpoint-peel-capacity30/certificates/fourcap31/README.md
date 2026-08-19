# q=9 four-cap certificate

This self-contained source/data packet certifies the normalized non-slab
`4^4 3^5` size-31 case. Start with `THEOREM.md`, then run:

```text
python -I -B verify_all.py
```

The large DRAT traces are deliberately external. Their complete immutable
ledger is `PROOF_PROVENANCE.json`; pass the artifact directory and a pinned
checker to `verify_all.py` for the full UNSAT replay.

This packet alone makes no claim about the exact value of `C9`.

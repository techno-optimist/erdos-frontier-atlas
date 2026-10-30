# Erdős #142 — recovered no-go certificates (additive-local and pair-affine lifts)

**Status of #142: open.** These certificates show that two families of
constructions on the fixed geometry of [`certificates/erdos-142`](../erdos-142)
cannot beat `7/24`. They give **no new bound on `r₃(N)`**.

Replay (stdlib only, ~5 s): `python3 -I certificates/erdos-142-complete-sos/verify.py`

| Artifact | sha256 | What it certifies |
|---|---|---|
| `complete_sos/artifacts/full_vertex_farkas_exact_4term.json` | `451fea0d12e2c7a9e613d4426450bd83baf3eb737be9e6c4bf94ca9be6261d8c` | No additive piece-local potential of any form (arbitrary function per piece and exact point) realizes the target rate: a 4-term exact Farkas contradiction. |
| `complete_sos/artifacts/context_pair_affine_farkas_exact_2767term_flintbasis.json` | `ed0e6c903c5b0f338490da95cfc2a505de62132ff0e9a90adfd85a8f6282a926` | No order-two pair-context affine lift realizes it either: a 2767-term exact Farkas contradiction with Bellman node-flow cancellation. |
| `complete_enum/geometry.json` | `607841330978360a10b3440598a034f6ade903b8afe872c1cbe7bdf441e92ada` | Same geometry file as `certificates/erdos-142/geometry.json` (byte-identical). |

`verify.py` checks these pins, then runs both verifiers in exact rational
arithmetic. The base verifier (`complete_handelman/verify_vertex_farkas.py`)
also checks the geometry hash, full-dimensional anchors, nonnegative
multipliers, and mutation kill tests.

## Hash check

No earlier sha256 for these two artifacts was written down in the atlas README,
`COORDINATION.md`, or `certificates/erdos-142/README.md`; the earlier README said
only that the artifacts had not been kept. So there is no earlier hash to
compare against. The pins above are the hashes of the recovered files as
committed here, and they match the expected prefixes `451fea0d…` and `ed0e6c90…`.

## Scope

- A no-go on two construction families on one fixed geometry. Not a global no-go,
  and not a statement about the asymptotic problem.
- Recovered from `/workspace/ford/review_tmp/e142` (`complete_enum`,
  `complete_handelman`, `complete_sos`) and re-run before committing.

`erdos142_solved: false`. `new_r3_bound: false`.

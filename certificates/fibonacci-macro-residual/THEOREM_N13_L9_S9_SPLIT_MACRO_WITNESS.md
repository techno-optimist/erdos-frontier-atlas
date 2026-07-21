# n=13 L=9 S=9 split-weight macro witness

Date: 2026-07-21

**Status:** machine-sealed WITNESS (independent product-graph verifier).

## Cell

Common-anchor Fibonacci macro residual: n=13, return length L=9, clock states S=9.

## Artifacts

| file | role |
|------|------|
| `N13_L9_S9_WITNESS.json` | clock + ports + selected routes |
| `verify_n13_l9_s9_macro_witness.py` | independent verifier |
| `N13_L9_S9_MACRO_WITNESS_RESULT.json` | PASS receipt |

## Replay

```sh
python3 -I verify_n13_l9_s9_macro_witness.py
```

## Claim boundary

Finite machine object for the common-anchor split-integral deterministic ternary
macro model. **Not** an Erdős 142 solution.

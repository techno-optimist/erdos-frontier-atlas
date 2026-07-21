# n=12 L=8 S=8 split-weight macro witness

Date: 2026-07-21

**Status:** machine-sealed WITNESS (independent product-graph verifier).

## Cell

Common-anchor Fibonacci macro residual: n=12, return length L=8, clock states S=8.

## Artifacts

| file | role |
|------|------|
| `N12_L8_S8_WITNESS.json` | clock + ports + selected routes |
| `verify_n12_l8_s8_macro_witness.py` | independent verifier |
| `N12_L8_S8_MACRO_WITNESS_RESULT.json` | PASS receipt |

## Replay

```sh
python3 -I verify_n12_l8_s8_macro_witness.py
```

## Claim boundary

Finite machine object for the common-anchor split-integral deterministic ternary
macro model. **Not** an Erdős 142 solution.

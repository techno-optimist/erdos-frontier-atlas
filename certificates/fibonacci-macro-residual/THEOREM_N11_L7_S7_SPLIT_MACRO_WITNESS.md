# n=11 L=7 S=7 split-weight macro witness

Date: 2026-07-21

**Status:** machine-sealed WITNESS (independent product-graph verifier).

## Cell

Common-anchor Fibonacci macro residual: n=11, return length L=7, clock states S=7.

## Artifacts

| file | role |
|------|------|
| `N11_L7_S7_WITNESS.json` | clock + ports + selected routes |
| `verify_n11_l7_s7_macro_witness.py` | independent verifier |
| `N11_L7_S7_MACRO_WITNESS_RESULT.json` | PASS receipt |

## Replay

```sh
python3 -I verify_n11_l7_s7_macro_witness.py
```

## Claim boundary

Finite machine object for the common-anchor split-integral deterministic ternary
macro model. **Not** an Erdős 142 solution.

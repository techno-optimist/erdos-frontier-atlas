# Fibonacci common-anchor macro residual

**Not** an Erdős #142 claim.

## Witness ladder

| n | L | S | verifier |
|--:|--:|--:|----------|
| 3 | 3 | 3 | `verify_n3_l3_macro_witness.py` |
| 4 | 3 | 3 | `verify_n4_l3_macro_witness.py` |
| 5 | 3 | 4 | `verify_n5_l3_s4_macro_witness.py` |
| 6 | 4 | 5 | `verify_n6_l4_s5_macro_witness.py` |
| 7 | 5 | 5 | `verify_n7_l5_s5_macro_witness.py` |
| 8 | 6 | 6 | `verify_n8_l6_s6_macro_witness.py` |

```sh
python3 -I verify_n8_l6_s6_macro_witness.py
```

See `MORPHOGENESIS.md` for the resource-growth picture.

# Fibonacci common-anchor macro residual

**Not** an Erdős #142 claim.

## Minimal known witness ladder

| n | L | S | verifier |
|--:|--:|--:|----------|
| 3 | 3 | 3 | `verify_n3_l3_macro_witness.py` |
| 4 | 3 | 3 | `verify_n4_l3_macro_witness.py` |
| 5 | 3 | 4 | `verify_n5_l3_s4_macro_witness.py` |
| 6 | 4 | 5 | `verify_n6_l4_s5_macro_witness.py` |
| 7 | 5 | 5 | `verify_n7_l5_s5_macro_witness.py` |
| 8 | 6 | 6 | `verify_n8_l6_s6_macro_witness.py` |
| 9 | 6 | 6 | `verify_n9_l6_s6_macro_witness.py` |
| 10 | 6 | 7 | `verify_n10_l6_s7_macro_witness.py` |

Also sealed (non-minimal): n=9 L=7 S=7, n=10 L=8 S=7, n=7 L=5 S=6.

```sh
python3 -I verify_n10_l6_s7_macro_witness.py
python3 -I verify_n9_l6_s6_macro_witness.py
```

See `MORPHOGENESIS.md`.

# Fibonacci common-anchor macro residual

**Not** an Erdős #142 claim.

## Witness ladder (best known cells)

Each row is certified by its verifier as **existence at that (n, L, S)** — nothing
more. **Minimality is NOT established:** the hunts are heuristic warm-starts and
stop at the first hit, so no cell below any listed (L, S) has been searched or
excluded (see `open_loopholes` in `SEAL.json`).

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
| 11 | 7 | 7 | `verify_n11_l7_s7_macro_witness.py` |
| 12 | 8 | 8 | `verify_n12_l8_s8_macro_witness.py` |
| 13 | 9 | 9 | `verify_n13_l9_s9_macro_witness.py` |

Also sealed (additional cells, not claimed smallest): n=9 L=7 S=7, n=10 L=8 S=7, n=7 L=5 S=6.

```sh
python3 -I verify_n13_l9_s9_macro_witness.py
python3 -I verify_n12_l8_s8_macro_witness.py
```

See `MORPHOGENESIS.md`. Hunt tools: `hunt_n_from_prev.py`, `hunt_n_fast.py`, `gen_verifier.py`.

**Empirical pattern (n≥11):** the best cells *found so far* have L = S = n − 4.
This is a pattern in the search output, not a proven law, and not a minimality claim.

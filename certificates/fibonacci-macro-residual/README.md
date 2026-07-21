# Fibonacci common-anchor macro residual

**Not** an Erdős #142 claim.

## Witnesses

| n | L | S | replay |
|--:|--:|--:|--------|
| 3 | 3 | 3 | `python3 -I verify_n3_l3_macro_witness.py` |
| 4 | 3 | 3 | `python3 -I verify_n4_l3_macro_witness.py` |
| 5 | 3 | 4 | `python3 -I verify_n5_l3_s4_macro_witness.py` |
| 6 | 4 | 5 | `python3 -I verify_n6_l4_s5_macro_witness.py` |

## Closed no-gos (selected)

- L=3 S≤4 board: `THEOREM_L3_S_LE_4_CLASSIFICATION.md`
- n=6 L=3 S=4 exhaustive NO-GO; n=7,8 L=3 S=4 NO-GO
- n=6 L=3 S=5: routable but LP-resistant in sample (`THEOREM_N6_L3_S5_LP_FENCE.md`)

## Port-capacity fences (the all-large-n cuts)

| S | max ports (L≤3-reachable) | kills | replay |
|--:|--:|---|--------|
| 3 | 7 | n ≥ 7 | `python3 -I verify_s3_port_capacity.py` |
| 4 | 9 | n ≥ 9 | `python3 -I verify_s4_port_capacity.py` (~4 min) |

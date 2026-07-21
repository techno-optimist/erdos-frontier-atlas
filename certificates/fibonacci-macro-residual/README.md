# Fibonacci common-anchor macro residual (2026-07-20)

**Not** an Erdős #142 claim. Finite machine model only.

## Scoreboard (L=3)

| n \\ S | 3 | 4 |
|--:|---|---|
| 3 | **WITNESS** | — |
| 4 | **WITNESS** | — |
| 5 | NO-GO | **WITNESS** |
| 6 | NO-GO | NO-GO |
| 7 | port NO-GO | NO-GO |
| 8 | port NO-GO | NO-GO |
| ≥9 | port NO-GO | port NO-GO |

Also: n=5 L=4,5 @ S=3 NO-GO; n=6 L=4,5 @ S=3 NO-GO; n=6 L=3 S=5 has routable seeds (integer open).

See `THEOREM_L3_S_LE_4_CLASSIFICATION.md` for the closed S≤4 board.

## Replay

```sh
python3 -I verify_n3_l3_macro_witness.py
python3 -I verify_n4_l3_macro_witness.py
python3 -I verify_n5_l3_s4_macro_witness.py
python3 -I verify_n5_l3_s3_routability.py
python3 -I verify_n6_l3_s3_routability.py
python3 -I verify_s3_port_capacity.py
python3 search_n_l3_s4_by_ports.py --n 8 7
python3 search_n6_l3_s4_routability.py
```

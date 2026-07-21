# Fibonacci common-anchor macro residual (2026-07-20)

Finite machine objects for the **common-anchor, split-weight, deterministic
ternary-clock** model. **Not** an Erdős #142 claim.

## Scoreboard

| cell | verdict |
|------|---------|
| n=3 L=3 S=3 | **WITNESS** |
| n=4 L=3 S=3 | **WITNESS** |
| n=5 L=3 S=3 | **NO-GO** |
| n=5 L=3 S=4 | **WITNESS** |
| n=5 L=4,5 S=3 | **NO-GO** |
| n=6 L=3 S=3 | **NO-GO** |
| n=6 L=3 S=4 | **NO-GO** (exhaustive: 72 routable, 0 LP) |
| n≥7 S=3 reachable | **NO-GO** (port cap 7) |
| n≥9 S=4 reachable | **NO-GO** (port cap 9) |

**Morphogenesis:** S must grow with n. S=4 saves n=5 but not n=6.

## Replay

```sh
python3 -I verify_n3_l3_macro_witness.py
python3 -I verify_n4_l3_macro_witness.py
python3 -I verify_n5_l3_s4_macro_witness.py
python3 -I verify_n5_l3_s3_routability.py
python3 -I verify_n6_l3_s3_routability.py
python3 -I verify_s3_port_capacity.py
# n=6 S=4 exhaustive (needs highspy for LP filter):
python3 search_n6_l3_s4_routability.py
```

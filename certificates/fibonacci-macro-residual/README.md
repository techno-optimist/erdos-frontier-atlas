# Fibonacci common-anchor macro residual (2026-07-20)

Finite machine objects for the **common-anchor, split-weight, deterministic
ternary-clock** model of Fibonacci-tag macros. **Not** an Erdős #142 density
bound and **not** a prize claim.

## Scoreboard

| cell | verdict | artifact |
|------|---------|----------|
| \(n=3\), \(L=2\), any \(S\) | **NO-GO** | `THEOREM_N3_L2_ALL_S_NO_GO.md` |
| \(n=3\), \(L=3\), \(S=3\) | **WITNESS** | `verify_n3_l3_macro_witness.py` |
| \(n=4\), \(L=3\), \(S=3\) | **WITNESS** | `verify_n4_l3_macro_witness.py` |
| \(n=5\), \(L=3\), \(S=3\) | **NO-GO** | `verify_n5_l3_s3_routability.py` |
| \(n=5\), \(L=4\), \(S=3\) | **NO-GO** | `verify_n5_l4_s3_routability.py` |
| \(n=5\), \(L=5\), \(S=3\) | **NO-GO** | `N5_L5_S3_COMPLETE.json` |
| \(n=5\), \(L=3\), \(S=4\) | **WITNESS** | `verify_n5_l3_s4_macro_witness.py` |
| \(n=6\), \(L=3\), \(S=3\) | **NO-GO** | `verify_n6_l3_s3_routability.py` |
| \(n\ge 7\), \(S=3\) reachable | **NO-GO** (ports) | `verify_s3_port_capacity.py` |

Headline: **S must grow** — n=5 is impossible on every 3-state clock for L≤5,
but exists on a 4-state clock at L=3.

## Replay (stdlib)

```sh
python3 -I verify_n3_l3_macro_witness.py
python3 -I verify_n4_l3_macro_witness.py
python3 -I verify_n5_l3_s3_routability.py
python3 -I verify_n5_l4_s3_routability.py
python3 -I verify_n5_l3_s4_macro_witness.py   # the n=5 treasure
python3 -I verify_n6_l3_s3_routability.py
python3 -I verify_s3_port_capacity.py
```

Integer discovery for n=5 S=4 used `highspy` (`search_n5_l3_s4_integer.py`);
the sealed witness re-verifies without it.

## Claim boundary

Exact finite combinatorial statements about the common-anchor split-integral
deterministic ternary macro model. Does **not** solve or bound Erdős #142.

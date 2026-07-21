# Fibonacci common-anchor macro residual (2026-07-20)

Finite machine objects for the **common-anchor, split-weight, deterministic
ternary-clock** model of Fibonacci-tag macros (Lead residual after one-edge and
fixed-word no-gos). **Not** an Erdős #142 density bound and **not** a prize claim.

## Scoreboard

| cell | verdict | artifact |
|------|---------|----------|
| one-edge any \(n\) | NO-GO (prior) | — |
| fixed-word \(n\ge 3\) | NO-GO (prior) | — |
| \(n=2\), \(L=2\) split | WITNESS (prior) | — |
| \(n=3\), \(L=2\), any \(S\) | **NO-GO** | `THEOREM_N3_L2_ALL_S_NO_GO.md` |
| \(n=3\), \(L=3\), \(S=3\) | **WITNESS** | `verify_n3_l3_macro_witness.py` |
| \(n=4\), \(L=3\), \(S=3\) | **WITNESS** | `verify_n4_l3_macro_witness.py` + `N4_L3_WITNESS.json` |
| \(n=5\), \(L=3\), \(S=3\) | **NO-GO** (exhaustive) | `verify_n5_l3_s3_routability.py` |
| \(n=6\), \(L=3\), \(S=3\) | **NO-GO** (exhaustive) | `verify_n6_l3_s3_routability.py` |
| \(n\ge 7\), any \(L\), \(S=3\) reachable | **NO-GO** (port capacity) | `verify_s3_port_capacity.py` |
| \(n=5\), \(L=3\), \(S=4\) | sample only (0 routable) | `N5_L3_S4_SAMPLE.json` |

Induction: fixed \((L,S)=(3,3)\) works for \(n=3,4\) on different 3-state clocks
and **fails** for all \(n\ge 5\) at \(S=3\) (n=5: 0 routable; n=6: 0 outward;
n≥7: impossible by port capacity — max 7 anchor ports under L≤3 reachability).

## Replay (stdlib)

```sh
python3 -I verify_n3_l3_macro_witness.py      # PASS
python3 -I verify_n4_l3_macro_witness.py      # PASS
python3 -I verify_n5_l3_s3_routability.py    # NO_N5_L3_S3 (~15s)
python3 -I verify_n6_l3_s3_routability.py    # NO_N6_L3_S3 (~1s)
python3 -I verify_s3_port_capacity.py        # n>=7 port no-go
```

## Claim boundary

- Exact finite combinatorial statements about the common-anchor split-integral
  deterministic ternary macro model.
- Does **not** exhaust \(S\ge 4\) or \(L\ge 4\) for \(n=5\).
- Does **not** solve or bound Erdős #142.

## Files

| file | role |
|------|------|
| `SEAL.json` | scoreboard + claim boundary |
| `verify_n3_l3_macro_witness.py` | independent n=3 witness checker |
| `verify_n4_l3_macro_witness.py` | independent n=4 witness checker |
| `N4_L3_WITNESS.json` | sealed n=4 routes / clock |
| `verify_n5_l3_s3_routability.py` | pure-Python exhaustive n=5 S=3 no-go |
| `verify_n6_l3_s3_routability.py` | pure-Python exhaustive n=6 S=3 no-go |
| `N5_L3_S4_SAMPLE.json` | random S=4 sample |
| `THEOREM_*.md` | write-ups |
| `INDUCTION_NOTES_L3.md` | multi-\(n\) table + open loopholes |

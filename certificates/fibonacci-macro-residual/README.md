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
| \(n=5\), \(L=3\), \(S=3\) | **NO-GO** (exhaustive) | `verify_n5_l3_s3_routability.py` / `N5_L3_S3_COMPLETE.json` |
| \(n=6\), \(L=3\), \(S=3\) | smoke only | `N6_L3_S3_SMOKE.json` |

Induction note: fixed \((L,S)=(3,3)\) **does not** extend indefinitely — \(n=3,4\)
witnesses exist on (different) 3-state clocks; \(n=5\) fails at **local
routability** before Parikh LP (0 routable among all 19 683 clocks).

## Replay (stdlib)

```sh
python3 -I verify_n3_l3_macro_witness.py      # PASS_N3_L3_SPLIT_MACRO_WITNESS
python3 -I verify_n4_l3_macro_witness.py      # PASS_N4_L3_SPLIT_MACRO_WITNESS
python3 -I verify_n5_l3_s3_routability.py    # NO_N5_L3_S3 (pure Python, ~30s)
```

Optional full census with LP (requires `highspy`; obstruction is already at
routability, so LP is vacuous):

```sh
python3 search_n5_l3_s3_complete.py
```

## Claim boundary

- Exact finite combinatorial statements about the common-anchor split-integral
  deterministic ternary macro model.
- Does **not** rule out \(S\ge 4\) or \(L\ge 4\) for \(n=5\).
- Does **not** claim an all-\(n\) structural theorem (see `INDUCTION_NOTES_L3.md`).
- Does **not** solve or bound Erdős #142.

## Files

| file | role |
|------|------|
| `SEAL.json` | scoreboard + claim boundary |
| `verify_n3_l3_macro_witness.py` | independent n=3 witness checker |
| `verify_n4_l3_macro_witness.py` | independent n=4 witness checker |
| `N4_L3_WITNESS.json` | sealed n=4 routes / clock |
| `verify_n5_l3_s3_routability.py` | pure-Python exhaustive n=5 S=3 no-go |
| `search_n5_l3.py` | shared search engine (LP path optional) |
| `N5_L3_S3_COMPLETE.json` | sealed census result |
| `THEOREM_*.md` | write-ups |
| `INDUCTION_NOTES_L3.md` | multi-\(n\) table + open loopholes |

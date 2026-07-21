# No-go: n=5 length-three macros on 3-state clocks

Date: 2026-07-20

## Theorem

There is no common-anchor, split-weight, length-three, Parikh-balanced
Fibonacci macro for the primitive `n=5` circuit on any deterministic
ternary clock with **exactly three** states, all L≤3-reachable from the
anchor.

## Census

Verifier: `search_n5_l3_s3_complete.py`  
Result: `N5_L3_S3_COMPLETE.json`

| quantity | count |
|---|--:|
| clocks | 19 683 |
| all states L≤3-reachable | 15 930 |
| ≥6 anchor-returning ports | 282 |
| outward-legal assignments | 864 |
| all columns L=3-routable | **0** |
| LP feasible | **0** |

Obstruction level: **local routability** — no assignment admits a legal
length-three return for every Fibonacci column simultaneously.

## Contrast

| n | L=3, S=3 |
|--:|---|
| 3 | **witness** |
| 4 | **witness** |
| 5 | **no-go** |

So fixed L=3, S=3 does **not** extend indefinitely: the multi-n family stops
at least by n=5 in the three-state regime.

## Scope

Does not rule out S≥4 or L≥4 for n=5.

## Replay

```powershell
python search_n5_l3_s3_complete.py
```

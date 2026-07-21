# No-go: n=5 length-four macros on 3-state clocks

Date: 2026-07-20

## Theorem

There is no common-anchor, split-weight, length-four Fibonacci macro for the
primitive `n=5` circuit on any deterministic ternary clock with exactly three
states, all L≤4-reachable from the anchor.

## Census

Verifier: `verify_n5_l4_s3_routability.py`  
Result: `N5_L4_S3_COMPLETE.json`

| quantity | count |
|---|--:|
| clocks | 19 683 |
| all states L≤4-reachable | 15 930 |
| ≥6 anchor-returning ports | 282 |
| outward-legal assignments | 864 |
| all columns L=4-routable | **0** |

Same outward set as the L=3 census; lengthening returns to 4 does **not**
unlock routability.

## Contrast

| n | L | S=3 |
|--:|--:|---|
| 5 | 3 | **no-go** |
| 5 | 4 | **no-go** |

## Scope

Does not rule out L≥5 or S≥4 for n=5.

## Replay

```sh
python3 -I verify_n5_l4_s3_routability.py
```

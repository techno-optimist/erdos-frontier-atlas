# No-go: n=6 length-three macros on 3-state clocks

Date: 2026-07-20

## Theorem

There is no common-anchor, split-weight, length-three, Parikh-balanced
Fibonacci macro for the primitive `n=6` circuit on any deterministic
ternary clock with **exactly three** states, all L≤3-reachable from the
anchor.

## Census

Verifier: `verify_n6_l3_s3_routability.py`  
Result: `N6_L3_S3_COMPLETE.json`

| quantity | count |
|---|--:|
| clocks | 19 683 |
| all states L≤3-reachable | 15 930 |
| ≥7 anchor-returning ports | **24** |
| outward-legal assignments | **0** |
| all columns L=3-routable | **0** |

Obstruction level: **port / outward digit legality** — only 24 clocks even
have enough anchor ports for 7 tags, and none of those admit an outward-legal
assignment of the 23 digit patterns.

## Contrast

| n | L=3, S=3 |
|--:|---|
| 3 | **witness** |
| 4 | **witness** |
| 5 | **no-go** (0 routable / 864 outward) |
| 6 | **no-go** (0 outward / 24 ge_tags) |

## Scope

Does not rule out S≥4 or L≥4 for n=6.

## Replay

```sh
python3 -I verify_n6_l3_s3_routability.py
```

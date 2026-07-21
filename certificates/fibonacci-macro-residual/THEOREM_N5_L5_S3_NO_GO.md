# No-go: n=5 length-five macros on 3-state clocks

Date: 2026-07-20

## Theorem

There is no common-anchor, split-weight, length-five Fibonacci macro for the
primitive `n=5` circuit on any deterministic ternary clock with exactly three
states, all L≤5-reachable from the anchor.

## Census

Result: `N5_L5_S3_COMPLETE.json` (via `macro_engine` + same census pattern as L=4).

| quantity | count |
|---|--:|
| clocks | 19 683 |
| reachable | 15 930 |
| ≥6 anchor ports | 282 |
| outward-legal | 864 |
| L=5-routable | **0** |

## Contrast (n=5, S=3)

| L | routable |
|--:|---|
| 3 | 0 |
| 4 | 0 |
| 5 | 0 |

Lengthening returns at S=3 does not unlock n=5.

## Scope

Does not rule out L≥6 or S≥4 (S=4 has routable seeds; integer recovery open).

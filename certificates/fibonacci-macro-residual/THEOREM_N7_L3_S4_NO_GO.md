# No-go: n=7 length-three macros on 4-state clocks

Date: 2026-07-20

## Theorem

There is no common-anchor, split-weight, length-three Fibonacci macro for the
primitive `n=7` circuit on any deterministic ternary clock with exactly four
states, all L≤3-reachable from the anchor.

## Census

Result: `N7_L3_S4_COMPLETE.json` (via `search_n_l3_s4_by_ports.py --n 7`)

| quantity | count |
|---|--:|
| clocks | 16 777 216 |
| ≥8 ports (any) | 46 666 |
| L≤3-reachable + ≥8 ports | 6 972 |
| outward-legal | 55 296 |
| all columns L=3-routable | **0** |

Obstruction: **local routability**.

## Replay

```sh
python3 search_n_l3_s4_by_ports.py --n 7
```

# No-go: n=8 length-three macros on 4-state clocks

Date: 2026-07-20

## Theorem

There is no common-anchor, split-weight, length-three Fibonacci macro for the
primitive `n=8` circuit on any deterministic ternary clock with exactly four
states, all L≤3-reachable from the anchor.

## Census

Result: `N8_L3_S4_COMPLETE.json`

| quantity | count |
|---|--:|
| clocks | 16 777 216 |
| ≥9 ports (any) | 6 571 |
| L≤3-reachable + ≥9 ports | 330 |
| outward-legal | **0** |

Obstruction: **outward digit legality** (no assignment of 9 tags is outward-legal).

## Replay

```sh
python3 search_n_l3_s4_by_ports.py --n 8
```

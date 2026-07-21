# No-go: n=6 length-three macros on 4-state clocks

Date: 2026-07-20

## Theorem

There is no common-anchor, split-weight, length-three, Parikh-balanced
Fibonacci macro for the primitive `n=6` circuit on any deterministic ternary
clock with **exactly four** states, all L≤3-reachable from the anchor.

## Census

Searcher: `search_n6_l3_s4_routability.py`  
Result: `N6_L3_S4_SEARCH.json`

| quantity | count |
|---|--:|
| clocks | 16 777 216 |
| L≤3-reachable | 12 768 384 |
| ≥7 anchor ports | 66 156 |
| outward-legal | 829 440 |
| all columns L=3-routable | **72** |
| LP feasible (Parikh over ℝ₊) | **0** |
| integer MIP | **0** (vacuous) |

Obstruction level: **Parikh / global balance** — local routes exist for 72
assignments, but none admit a nonnegative real combination matching Fibonacci
weights with balanced role-port features.

First routable seed: clock_idx 405698 (`N6_L3_S4_FIRST_ROUTABLE.json`).

## Contrast

| n | L=3 S=3 | L=3 S=4 |
|--:|---|---|
| 5 | NO-GO (0 routable) | **WITNESS** |
| 6 | NO-GO (0 outward) | **NO-GO** (72 routable, 0 LP) |

So n=6 needs **S≥5** (or L>3), if it exists at all in this model.

## Scope

Does not rule out L≥4 or S≥5 for n=6.

## Replay

```sh
python3 search_n6_l3_s4_routability.py   # ~10 min, needs highspy for LP
```

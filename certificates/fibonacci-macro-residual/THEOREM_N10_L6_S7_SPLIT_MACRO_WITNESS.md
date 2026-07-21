# Witness: n=10 length-six split-weight macro on a 7-state clock

Date: 2026-07-21

## Theorem

There exists a common-anchor, split-weight, length-**six**, globally
Parikh-balanced Fibonacci macro for the primitive `n=10` circuit on a
deterministic ternary clock with **seven** states.

## Objects

- `N10_L6_S7_WITNESS.json`
- `verify_n10_l6_s7_macro_witness.py` → `PASS_N10_L6_S7_SPLIT_MACRO_WITNESS`
- Discovery: `hunt_n_from_prev.py --n 10` from n=9 L=6 S=6 seed
  (BFS-seeded + sampled route enum for L=6; selected routes re-checked exactly)
- Fib weights through F10=89 for column P10; tags = 11

## Ladder

| n | L | S |
|--:|--:|--:|
| 3 | 3 | 3 |
| 4 | 3 | 3 |
| 5 | 3 | 4 |
| 6 | 4 | 5 |
| 7 | 5 | 5 |
| 8 | 6 | 6 |
| 9 | 6 | 6 |
| 10 | **6** | **7** |

Sample note: L=6 S=6 had 0 routable in 281 pad/mutate clocks (not exhaustive).

## Replay

```sh
python3 -I verify_n10_l6_s7_macro_witness.py
```

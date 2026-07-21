# Witness: n=9 length-six split-weight macro on a 6-state clock

Date: 2026-07-21

## Theorem

There exists a common-anchor, split-weight, length-**six**, globally
Parikh-balanced Fibonacci macro for the primitive `n=9` circuit on a
deterministic ternary clock with **six** states.

## Objects

- `N9_L6_S6_WITNESS.json`
- `verify_n9_l6_s6_macro_witness.py` → `PASS_N9_L6_S6_SPLIT_MACRO_WITNESS`
- Discovery: `hunt_n_from_prev.py --n 9` from n=8 L=6 S=6 seed
  (sampled route enum for L=6; selected routes re-checked exactly)
- Fib weights through F9=55 for column P9; tags = 10

## Ladder

| n | L | S |
|--:|--:|--:|
| 3 | 3 | 3 |
| 4 | 3 | 3 |
| 5 | 3 | 4 |
| 6 | 4 | 5 |
| 7 | 5 | 5 |
| 8 | 6 | 6 |
| 9 | **6** | **6** |

Note: n=9 reuses (L,S)=(6,6) from n=8 (no resource jump in this hunt).

## Replay

```sh
python3 -I verify_n9_l6_s6_macro_witness.py
```

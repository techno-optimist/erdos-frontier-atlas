# Witness: n=8 length-six split-weight macro on a 6-state clock

Date: 2026-07-21

## Theorem

There exists a common-anchor, split-weight, length-**six**, globally
Parikh-balanced Fibonacci macro for the primitive `n=8` circuit on a
deterministic ternary clock with **six** states.

## Objects

- `N8_L6_S6_WITNESS.json`
- `verify_n8_l6_s6_macro_witness.py` → `PASS_N8_L6_S6_SPLIT_MACRO_WITNESS`
- Discovery: `hunt_n_from_prev.py --n 8` from n=7 L=5 S=5 seed
  (sampled route enum for L=6; selected routes re-checked exactly)

## Ladder

| n | L | S |
|--:|--:|--:|
| 3 | 3 | 3 |
| 4 | 3 | 3 |
| 5 | 3 | 4 |
| 6 | 4 | 5 |
| 7 | 5 | 5 |
| 8 | **6** | **6** |

Sample note: L=5 S=6 had 0 routable in 251 pad/mutate clocks (not exhaustive).

## Replay

```sh
python3 -I verify_n8_l6_s6_macro_witness.py
```

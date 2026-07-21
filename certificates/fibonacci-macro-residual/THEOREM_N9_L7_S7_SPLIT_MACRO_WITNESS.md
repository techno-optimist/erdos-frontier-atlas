# Witness: n=9 length-seven split-weight macro on a 7-state clock

Date: 2026-07-21

## Theorem

There exists a common-anchor, split-weight, length-**seven**, globally
Parikh-balanced Fibonacci macro for the primitive `n=9` circuit on a
deterministic ternary clock with **seven** states.

## Objects

- `N9_L7_S7_WITNESS.json`
- `verify_n9_l7_s7_macro_witness.py` → `PASS_N9_L7_S7_SPLIT_MACRO_WITNESS`

## Ladder

| n | L | S |
|--:|--:|--:|
| 3–4 | 3 | 3 |
| 5 | 3 | 4 |
| 6 | 4 | 5 |
| 7 | 5 | 5 |
| 8 | 6 | 6 |
| 9 | **7** | **7** |

## Replay

```sh
python3 -I verify_n9_l7_s7_macro_witness.py
```

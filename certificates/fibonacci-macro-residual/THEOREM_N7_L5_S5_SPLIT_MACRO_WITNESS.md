# Witness: n=7 length-five split-weight macro on a 5-state clock

Date: 2026-07-21

## Theorem

There exists a common-anchor, split-weight, length-**five**, globally
Parikh-balanced Fibonacci macro for the primitive `n=7` circuit on a
deterministic ternary clock with **five** states.

## Objects

- Witness: `N7_L5_S5_WITNESS.json`
- Verifier: `verify_n7_l5_s5_macro_witness.py` →
  `PASS_N7_L5_S5_SPLIT_MACRO_WITNESS`
- Discovery: `search_n7_from_n6.py` (pad/mutate from n=6 L=4 S=5 clock)

## Morphogenesis table (known witnesses)

| n | L | S |
|--:|--:|--:|
| 3 | 3 | 3 |
| 4 | 3 | 3 |
| 5 | 3 | 4 |
| 6 | 4 | 5 |
| 7 | **5** | **5** |

n=7 L=4 S=5 sample in the same hunt: 0 routable among 301 clocks (not exhaustive).

## Scope

Finite machine object. **Not** Erdős #142.

## Replay

```sh
python3 -I verify_n7_l5_s5_macro_witness.py
```

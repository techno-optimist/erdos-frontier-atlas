# Witness: n=6 length-four split-weight macro on a 5-state clock

Date: 2026-07-21

## Theorem

There exists a common-anchor, split-weight, length-**four**, globally
Parikh-balanced Fibonacci macro for the primitive `n=6` circuit on a
deterministic ternary clock with **five** states.

## Objects

- Clock: same 5-state \(\delta\) as the first n=6 L=3 S=5 routable seed
  (`N6_L3_S5_FIRST_ROUTABLE.json`)
- 7 tag ports, Fib weights mass \(1+1+1+1+2+2+3+3+5+5+8+13 = 45\)
- Witness: `N6_L4_S5_WITNESS.json`
- Verifier: `verify_n6_l4_s5_macro_witness.py` →
  `PASS_N6_L4_S5_SPLIT_MACRO_WITNESS`

## Morphogenesis

| n | L | S | status |
|--:|--:|--:|--------|
| 5 | 3 | 3 | NO-GO |
| 5 | 3 | 4 | **WITNESS** |
| 6 | 3 | 3 | NO-GO |
| 6 | 3 | 4 | NO-GO (0 LP) |
| 6 | 3 | 5 | routable, 0 LP in large sample |
| 6 | **4** | **5** | **WITNESS** |

So n=6 needs **both** more states (S≥5) **and** longer returns (L≥4) in
the cells examined: L=3 S=5 unlocks routes but not Parikh; L=4 on the same
clock yields LP+integer.

## Discovery path

1. Biased S=5 sample found L=3-routable seed (LP-infeas at L=3).
2. Same dig/ports at **L=4** remain outward-legal and routable.
3. Route enum + MIP recovers integer multiplicities in <1 s.
4. Independent product-graph verifier PASS.

## Scope

Finite machine object. **Not** Erdős #142.

## Replay

```sh
python3 -I verify_n6_l4_s5_macro_witness.py
```

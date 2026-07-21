# Witness: n=5 length-three split-weight macro on a 4-state clock

Date: 2026-07-20

## Theorem

There exists a common-anchor, split-weight, length-three, globally
Parikh-balanced Fibonacci macro for the primitive `n=5` circuit on a
deterministic ternary clock with **four** states.

## Objects

- Clock \(\delta\): 4 states (see `N5_L3_S4_WITNESS.json`)
- 6 tag ports returning to the anchor
- Fibonacci column weights: 1,1,1,1,2,2,3,3,5,8 (mass 27)
- Independent verifier: `verify_n5_l3_s4_macro_witness.py`
- Result: `N5_L3_S4_MACRO_WITNESS_RESULT.json` →
  `PASS_N5_L3_S4_SPLIT_MACRO_WITNESS`

Checks (all exact):

- outward carry legality and return-to-anchor
- every unit route length 3, carry/state endpoints match
- weighted flow conservation on the product graph
- weighted tag-column balance
- return-role Parikh equality
- weak connectivity from the anchor

## Contrast

| n | L=3 S=3 | L=3 S=4 |
|--:|---|---|
| 3 | **witness** | — |
| 4 | **witness** | — |
| 5 | **no-go** | **witness** |
| 6 | **no-go** | open |

## Discovery path

1. Exhaustive S=3 no-go at L=3,4,5 (0 routable among 864 outward).
2. S=4 search found routable seed at clock 298176 (MIP infeas for Parikh).
3. Integer search found LP+MIP hit at clock 401600.
4. Independent product-graph verifier PASS.

## Scope

Finite machine object in the common-anchor split-integral deterministic
ternary model. **Not** an Erdős #142 density construction.

## Replay

```sh
python3 -I verify_n5_l3_s4_macro_witness.py
```

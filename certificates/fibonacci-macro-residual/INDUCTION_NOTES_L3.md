# L=3 family notes (n=2…5)

Date: 2026-07-20

## Empirical table

| n | tags | Fib max weight | L=2 | L=3 S=3 |
|--:|--:|--:|---|---|
| 2 | 3 | 2 | witness | — |
| 3 | 4 | 3 | **no-go all S** | **witness** |
| 4 | 5 | 5 | — | **witness** |
| 5 | 6 | 8 | — | **no-go** (local routes) |

## Observations

1. **L=2 capacity** is incompatible with n≥3 (sealed earlier).
2. **L=3, S=3** works for n=3 and n=4 with split weights matching Fibonacci
   coefficients, on **different** 3-state clocks (not a single shared clock).
3. **n=5 L=3 S=3** fails before Parikh balance: no simultaneous L=3 routing
   of all 10 columns under injective 6-tag ports returning to the anchor.
4. Extending the n=4 witness by the one leftover anchor port `(2,2)` does not
   yield an outward-legal n=5 assignment on that clock.

## Hypotheses for all-n

- Either L must grow with n (e.g. L ≥ ⌈log₃(n+1)⌉−1 from fixed-length capacity
  is only a weak lower bound; routing may force more),
- Or S must grow,
- Or the common-anchor hypothesis must be dropped.

## Next machine targets

- n=5 L=3 S=4 (expensive; 4¹² clocks) — random/structured sample started 2026-07-20, no hit before timeout
- n=5 L=4 S=3 (27× heavier route enum)
- n=6 L=3 S=3 full census (smoke: 0 routable / first 3000 clocks; 23 digit patterns)
- Structural no-go for fixed (L,S) as n grows

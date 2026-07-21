# L=3 family notes (n=2…6)

Date: 2026-07-20

## Empirical table

| n | tags | Fib max weight | L=2 | L=3 S=3 | L=3 S=4 |
|--:|--:|--:|---|---|---|
| 2 | 3 | 2 | witness | — | — |
| 3 | 4 | 3 | **no-go all S** | **witness** | — |
| 4 | 5 | 5 | — | **witness** | — |
| 5 | 6 | 8 | — | **no-go** (0 routable) | sample: 0 routable / 3000 |
| 6 | 7 | 13 | — | **no-go** (0 outward) | — |
| ≥7 | ≥8 | … | — | **no-go** (port cap ≤7) | — |

## Observations

1. **L=2 capacity** is incompatible with n≥3 (sealed earlier).
2. **L=3, S=3** works for n=3 and n=4 with split weights matching Fibonacci
   coefficients, on **different** 3-state clocks (not a single shared clock).
3. **n=5 L=3 S=3** fails before Parikh balance: 864 outward-legal assignments,
   **0** simultaneous L=3 routing of all 10 columns.
4. **n=6 L=3 S=3** fails earlier: only 24 clocks have ≥7 anchor ports, and
   **0** outward-legal assignments among them.
5. Port budget on S=3: at most 9 ports return to anchor; tags = n+1 so n≤8 is
   the hard port ceiling — soft failures hit earlier.

## Hypotheses for all-n

- Either L must grow with n,
- Or S must grow,
- Or the common-anchor hypothesis must be dropped.

## Next machine targets

- n=5 L=3 S=4 exhaustive (or smarter MIP over clocks)
- n=5 L=4 S=3
- Structural no-go: fixed (L,S) cannot cover all n

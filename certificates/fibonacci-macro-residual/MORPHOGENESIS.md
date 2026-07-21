# Morphogenesis of common-anchor Fibonacci macros

Date: 2026-07-21

## Sealed witness ladder

| n | tags | mass (Σ Fib) | L | S | ports used | status |
|--:|--:|--:|--:|--:|--:|--------|
| 3 | 4 | 9 | 3 | 3 | 4 | WITNESS |
| 4 | 5 | 15 | 3 | 3 | 5 | WITNESS |
| 5 | 6 | 27 | 3 | 4 | 6 | WITNESS |
| 6 | 7 | 45 | 4 | 5 | 7 | WITNESS |
| 7 | 8 | 74 | 5 | 5 | 8 | WITNESS |
| 8 | 9 | 122 | 6 | 6 | 9 | WITNESS |

Masses via standard column construction in `macro_engine.columns`.

## Empirical resource growth

Observed known (L,S) pairs (minimal known for each n):

```
n:  3  4  5  6  7  8
L:  3  3  3  4  5  6
S:  3  3  4  5  5  6
```

- **S** is nondecreasing; jumps at n=5 and n=6.
- **L** flat at 3 until n=6, then increases.
- Port lower bound: tags = n+1 ≤ max anchor ports on L-reachable clocks of size S.

## Hard port fences (L≤3 reachability, exhaustive for S=3,4)

| S | max ports | impossible n |
|--:|--:|--:|
| 3 | 7 | n≥7 |
| 4 | 9 | n≥9 |

For S≥5, only Monte Carlo port samples exist (`PORT_CAPACITY_MULTI_S.json`).

## Working conjecture

There exists a function f(n)=(L(n),S(n)) with L,S nondecreasing such that a
common-anchor split L-return macro exists at (L(n),S(n)) and fails for all
strictly smaller resource pairs in the lexicographic order (S,L) or (L,S).

**Not proved.** Evidence is the sealed ladder + exhaustive no-gos for L=3 S≤4
and sample fences elsewhere.

## Next treasure targets

1. n=8 witness (minimal L,S)
2. Whether n=7 admits L=4 at S≥6
3. Closed form for L(n), S(n)

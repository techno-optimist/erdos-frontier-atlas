# Morphogenesis of common-anchor Fibonacci macros

Date: 2026-07-21

## Minimal known witness ladder

| n | L | S |
|--:|--:|--:|
| 3 | 3 | 3 |
| 4 | 3 | 3 |
| 5 | 3 | 4 |
| 6 | 4 | 5 |
| 7 | 5 | 5 |
| 8 | 6 | 6 |
| 9 | 6 | 6 |
| 10 | 6 | 7 |

```
n:  3  4  5  6  7  8  9 10
L:  3  3  3  4  5  6  6  6
S:  3  3  4  5  5  6  6  7
```

L plateaus at 6 for n=8–10 in the sealed minimal cells; S keeps rising slowly.

## Port fences (L≤3 reachability, exhaustive)

| S | max ports | kills |
|--:|--:|--:|
| 3 | 7 | n≥7 |
| 4 | 9 | n≥9 |

## Next

n=11+; prove asymptotic L(n), S(n).

# Morphogenesis of common-anchor Fibonacci macros

Date: 2026-07-21

## Sealed witness ladder

| n | tags | L | S | status |
|--:|--:|--:|--:|--------|
| 3 | 4 | 3 | 3 | WITNESS |
| 4 | 5 | 3 | 3 | WITNESS |
| 5 | 6 | 3 | 4 | WITNESS |
| 6 | 7 | 4 | 5 | WITNESS |
| 7 | 8 | 5 | 5 | WITNESS |
| 8 | 9 | 6 | 6 | WITNESS |
| 9 | 10 | 7 | 7 | WITNESS |

## Empirical resource growth

```
n:  3  4  5  6  7  8  9
L:  3  3  3  4  5  6  7
S:  3  3  4  5  5  6  7
```

For n≥7, sealed cells match **L = n−2** and **S = n−2**.

## Hard port fences (L≤3 reachability)

| S | max ports | kills |
|--:|--:|--:|
| 3 | 7 | n≥7 |
| 4 | 9 | n≥9 |

S≥5: Monte Carlo only (`PORT_CAPACITY_MULTI_S.json`).

## Working conjecture

A common-anchor split macro exists at L=S=n−2 for all n≥7 (and known for n=8,9).
**Not proved** for all n.

## Next

n=10 at L=8 S=8 (or smaller if found).

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
| 11 | 7 | 7 |
| 12 | 8 | 8 |

```
n:  3  4  5  6  7  8  9 10 11 12
L:  3  3  3  4  5  6  6  6  7  8
S:  3  3  4  5  5  6  6  7  7  8
```

After a plateau L=6 on n=8–10, L climbs 7→8 on n=11–12. S tracks roughly ⌈n/2⌉-ish growth with plateaus.

## Growth notes

- ΔL over n=3..12: +5 total.
- ΔS over n=3..12: +5 total.
- n=11 L=6 S=7 sample: one routable, LP-infeasible.
- n=12 hit at L=8 S=8 after L≤7 pad hunts failed to route all columns.

## Empirical fit (not proved)

For n≥8, known minimal cells roughly satisfy L ≈ ⌈(n+4)/2⌉ − something —
better: (L,S) ≈ (⌊n/2⌋+2, ⌊n/2⌋+2) for n=8..12 is imperfect.
Observed pairs (n,L,S): (8,6,6)(9,6,6)(10,6,7)(11,7,7)(12,8,8).

## Port fences (L≤3 reachability, exhaustive)

| S | max ports | kills |
|--:|--:|--:|
| 3 | 7 | n≥7 |
| 4 | 9 | n≥9 |

Sample (non-exhaustive) max anchor ports for S≥5: see `PORT_CAPACITY_SAMPLE_HIGH.json`.

## Next

n=13+; closed form L(n), S(n); tighten lower cells.

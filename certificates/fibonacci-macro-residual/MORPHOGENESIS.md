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
| 13 | 9 | 9 |

```
n:  3  4  5  6  7  8  9 10 11 12 13
L:  3  3  3  4  5  6  6  6  7  8  9
S:  3  3  4  5  5  6  6  7  7  8  9
```

After plateau L=6 on n=8–10, L climbs linearly: 7,8,9 on n=11,12,13 with S matching L from n=11 onward.

## Growth notes

- For n≥11 minimal known cells satisfy **L = S = n − 4**.
- n=11..13: (7,7), (8,8), (9,9).
- n=13 L=8 S=8/9: multiple full-column routable assignments, all LP-infeasible at 180k samples; integer appears at L=9 S=9.

## Port fences (L≤3 reachability, exhaustive)

| S | max ports | kills |
|--:|--:|--:|
| 3 | 7 | n≥7 |
| 4 | 9 | n≥9 |

Sample max anchor ports for S≥5: `PORT_CAPACITY_SAMPLE_HIGH.json`.

## n=14 status

Sample hunts from N13 (L,S around 9..12): outward-ok ports exist; no sealed integer yet. See N14_HUNT.json.

## Next

n=14+ (conjecture L=S=n−4 → try L=S=10); closed form; tighten.

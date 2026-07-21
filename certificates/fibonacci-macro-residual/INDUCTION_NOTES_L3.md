# L=3 family notes (updated after n=5 S=4 witness)

Date: 2026-07-20

## Empirical table

| n | tags | L=3 S=3 | L=3 S=4 | L≥4 S=3 |
|--:|--:|---|---|---|
| 3 | 4 | **witness** | — | — |
| 4 | 5 | **witness** | — | — |
| 5 | 6 | **no-go** (0 routable) | **witness** | L=4,5 **no-go** |
| 6 | 7 | **no-go** (0 outward) | open | — |
| ≥7 | ≥8 | **no-go** (port cap ≤7) | open | — |

## Morphogenesis

1. Fixed S=3 supports n=3 and n=4 only (among n≥3) at L=3.
2. Lengthening L at S=3 does **not** rescue n=5 (checked L=3,4,5).
3. Increasing S to 4 **does** rescue n=5 at L=3 (sealed integer witness).
4. Port capacity kills n≥7 at S=3 under L≤3 reachability regardless of L.

## Working hypothesis

Common-anchor macros at fixed L=3 require **S ≥ f(n)** with f(5)=4 and
f(n)≥3 for n∈{3,4}. Next: f(6).

## Next targets

- n=6 L=3 S=4 (and S=5 if needed)
- Structural lower bound S ≥ something(n)

# L=3 family notes — S=4 board complete for all n

Date: 2026-07-20

## Full table

| n | tags | S=3 | S=4 | port kills |
|--:|--:|---|---|---|
| 3 | 4 | **WITNESS** | — | — |
| 4 | 5 | **WITNESS** | — | — |
| 5 | 6 | NO-GO | **WITNESS** | — |
| 6 | 7 | NO-GO | NO-GO (0 LP) | — |
| 7 | 8 | port NO-GO | NO-GO (0 routable) | S=3 |
| 8 | 9 | port NO-GO | NO-GO (0 outward) | S=3 |
| ≥9 | ≥10 | port NO-GO | port NO-GO | S=3 & S=4 |

## Morphogenesis

1. **S=3 island:** only n=3,4.
2. **S=4 island:** only n=5 (among n≥5). n=6 dies at LP; n=7 at routes; n=8 at outward.
3. Port capacity: S=k cannot host n with n+1 > max_ports(S).
4. Lengthening L at S=3 does not save n=5.

## Working hypothesis

Common-anchor L=3 macros exist only for small (n,S) pairs:

- (3,3), (4,3), (5,4) known
- (6,S) requires S≥5 if anything, and sample at S=5 found 0 routable in 23k

## Next

- n=6 L=3 S=5 exhaustive (expensive) or structural no-go
- S=5 port capacity table

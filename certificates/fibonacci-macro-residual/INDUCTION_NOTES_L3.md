# L=3 family notes (after n=6 S=4 no-go)

Date: 2026-07-20

## Empirical table

| n | tags | L=3 S=3 | L=3 S=4 | port kill |
|--:|--:|---|---|---|
| 3 | 4 | **witness** | — | — |
| 4 | 5 | **witness** | — | — |
| 5 | 6 | **no-go** | **witness** | — |
| 6 | 7 | **no-go** | **no-go** (0 LP / 72 routable) | — |
| 7 | 8 | port no-go | open (6972 ge_tags) | S=3 |
| 8 | 9 | port no-go | open (330 ge_tags) | S=3 |
| ≥9 | ≥10 | port no-go | **port no-go** | S=3 and S=4 |

## Morphogenesis

1. Fixed S=3: only n=3,4 work at L=3; n≥5 dies (routability or ports).
2. Raising S to 4: **rescues n=5**, **does not rescue n=6** (Parikh/LP wall).
3. Port capacity: S=3 max 7 ports → n≥7 impossible; S=4 max 9 → n≥9 impossible.
4. Lengthening L at S=3 does not save n=5 (checked L=3,4,5).

## Working hypothesis

Common-anchor L=3 macros need **S ≥ f(n)** with:

- f(3)=f(4)=3
- f(5)=4
- f(6)≥5

Next machine target: n=6 L=3 S=5 (5^15 clocks — needs smarter search).

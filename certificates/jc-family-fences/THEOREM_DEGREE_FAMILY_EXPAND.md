# Expanded Alpöge-shaped degree family fence

Date: 2026-07-21

**Status:** family fence (not a closed degree bracket).

## Scan

| subfamily | scanned | const Jac deg 3–6 | low-deg collision hits |
|-----------|--------:|------------------:|-----------------------:|
| k=2, coeffs ∈ {−3..3}⁷ | 823543 | 0 | 0 |
| k=3 near Alpöge radius 2 | 78125 | 0 | 0 |
| k=4 with max deg ≤ 6 filter | 78125 | 0 | 0 |

Alpöge control (k=3, a=4,b=3,c=3,d=3,e=2,f=−3,g=−1) still const Jac det ≠ 0 and max total degree 7.

## Claim boundary

Absence of hits is **not** a no-go outside this parametric family. Reinforces
`jc-min-counterexample-degree-dim3` upper=7 with a wider empty search, without
moving the ledger bracket.

## Artifacts

- `expand_degree_box.py`
- `DEGREE_FAMILY_EXPAND.json`

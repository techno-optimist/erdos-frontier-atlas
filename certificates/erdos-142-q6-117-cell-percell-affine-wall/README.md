# Exact q=6 117-cell per-cell residual-affine obstruction

This scratch directory proves infeasibility from two necessary rows of the
**frozen deterministic base-cost closure subledger** for

```text
H(x) = 2 ||x||^2 + (h[cell(x)] + sum_j p[cell(x),j] r_j(x)) / 36,
r_j(x) = 6 x_j - floor(6 x_j),
```

with 117 independent offsets and 117 x 4 independent affine slopes.  The
subledger has exactly 98,167 rows: one deterministic base-cost closure row
per compatible ordered cell triple.  It is not an enumeration of all vertices
of the continuous closure ledger.  The two rows below are nevertheless
necessary one-sided closure inequalities for the stated potential class, so
their contradiction is sufficient.  The subledger is multiplied by q^2=36,
so the free-feature coefficients are exactly
`h[cell]` and `p[cell,j]`; the quadratic term is already folded into each
integer RHS carry cost.  Thus an exact positive Farkas sum with RHS 144 is
the contradiction `0 >= 144` (equivalently positive unscaled RHS 4).

The two closure rows are the deterministic ordered-ledger entries

```text
row 89333: (x,y,z) = (105,91,91), RHS  216
row 89473: (x,y,z) = (105,105,91), RHS -72
weights: (1,1)
```

Their 585 feature coefficients cancel exactly; only cell 91/105 features
occur before cancellation.  Closure points with residual coordinate one are
legitimate one-sided limits of the half-open cells `r in [0,1)`: each ledger
inequality is affine inside a fixed cell and hence extends to its closure.
Explicitly, the two selected ledger inequalities reduce to

```text
h[105] - h[91] - p[91,1] - p[91,2] - p[91,3] >= 216
-h[105] + h[91] + p[91,1] + p[91,2] + p[91,3] >= -72,
```

whose positive sum is `0 >= 144`.

## Verify

```powershell
python -I verify_percell_affine_farkas.py
python -I crosscheck_percell_affine_ray.py
```

The first is the stdlib-only full semantic replay: it reconstructs all 117
cells and scalar closure vertices, derives the 98,167-row deterministic
base-cost subledger, validates the selected residual/carry/cost tuples, checks
all 585 feature incidences, and rejects planted semantic and coefficient
mutations.  The second independently checks the two raw triples, carries,
residual relations, costs, feature cancellation, and closure use without
importing or enumerating the first replay.

## Discovery audit

`per_cell_affine_phase1_solution.json`'s 16 nonzero HiGHS row duals do not
form a certificate: exact rational elimination gives rank 16/nullity 0 on
their 71 active features.  This explains why rounded numerical ratios cannot
cancel the cell-specific slopes.  `direct_dual.js` instead writes the explicit
dual `max c.y, A^T y=0, sum(y)=1, y>=0`; native HiGHS discovers normalized
weights `(1/2,1/2)` on the two rows above.  The exact scripts, not either
solver output, are theorem-bearing.

## Scope fence

This excludes only this frozen q=6 117-cell, independent per-cell
residual-affine-plus-offset potential class through the two stated necessary
closure rows (and hence through the deterministic base-cost subledger).  It
does not exclude piecewise-affine refinements, pair features, different cells,
or arbitrary physical potentials.  It is **not** an Erdos-142 or new r3
claim.

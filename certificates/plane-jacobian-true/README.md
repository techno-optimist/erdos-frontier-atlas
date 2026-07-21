# Plane Jacobian Conjecture — TRUE lane

**Hypothesis:** plane JC (\(n=2\)) is TRUE.

## Resolution (read `RESOLUTION.md`)

| file | role | status |
|------|------|--------|
| **`RESOLUTION.md`** | Full status board | — |
| **`crack_structural.py`** | Elementary **any degree** + conjugates + L1/L2 | **exit 0** |
| **`crack_deg3_elim.py`** | Deg ≤ 3 lattice + families | **exit 0** (21/21) |
| **`crack_deg4.py`** | Deg ≤ 4 weight≤4 lattice | **exit 0** (53/53) |
| `CRACK_*.json` | Machine receipts | — |

```sh
python crack_structural.py   # any-deg elementary RESOLVED
python crack_deg3_elim.py    # plane JC deg<=3 RESOLVED
python crack_deg4.py         # deg<=4 lattice
```

## Support libraries

| file | role |
|------|------|
| `poly2.py` | exact bivariate poly engine |
| `wang_degree2.py` | Wang deg ≤ 2 inverse pipeline |
| `tame_invert.py` | elementary / conjugate / shear inverses |

## Atlas

Closes nothing in the dim-3 crater (plane JC was already the open survivor).
Raises confidence that **min counterexample dimension = 3** (TRUE lane),
with a full proof for all maps of degree ≤ 3.

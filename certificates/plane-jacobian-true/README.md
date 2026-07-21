# Plane Jacobian Conjecture — TRUE lane

**Hypothesis:** plane JC (\(n=2\)) is TRUE.

## CRACK (deg ≤ 3)

| file | role |
|------|------|
| **`crack_deg3_elim.py`** | **Main crack certificate** — exit 0 |
| **`CRACK_DEG3.json`** | Machine receipt |
| **`THEOREM_CRACK_DEG3.md`** | Write-up + honest scope |

```sh
python crack_deg3_elim.py   # proves plane JC for total degree <= 3 (see theorem file)
```

**Result:** 14 Keller equations + linear relations; elementary families \(E_x,E_y\)
for all rational parameters; **21/21** lattice Keller maps invert after linear
elimination (\(3^{12}\) exhaust). Classical affine reduction ⇒ all deg ≤ 3
plane Keller maps.

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

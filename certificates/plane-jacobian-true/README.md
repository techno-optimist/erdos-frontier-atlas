# Plane Jacobian Conjecture — TRUE lane

**Atlas node:** [`plane_jacobian_conjecture`](https://github.com/techno-optimist/erdos-frontier-atlas/blob/main/atlas/jc-crater/implication_graph.json) (○ OPEN on main crater; this package attacks TRUE).

**Hypothesis:** every plane Keller map \(F\colon\mathbb{A}^2\to\mathbb{A}^2\) with \(\det JF\in k^\times\) is a polynomial automorphism.

## Honest status

| Claim | Status |
|-------|--------|
| Deg ≤ 2 (Wang) | **SEALED** |
| Deg ≤ 3 full tame class | **SEALED** (21 = 17 elem + 4 shear) |
| Elementary any degree | **SEALED** |
| N=1 / \(\deg_x(f)=1\) ⇒ tame | **SEALED** (degree-free core) |
| X-drop Wronskian in \(k[y][x]\) | **SEALED** |
| Poisson `{R,K}=0` ⇔ pure-power binary \(R\) | **SEALED** lattice \(d\le 5\) + disc \(d=2\) |
| Axis form ⇒ elementary/tame | **SEALED** full solve \(D\le 3\); force \(D=4\); degfree x-isolation \(N\le 8\) |
| Geo deg 1 on tame locus | **SEALED** |
| **Full unbounded plane JC** | **OPEN** — residual: arbitrary Keller → pure-power axis coords for all \(d\) |

Parent atlas quantity `jc-min-counterexample-dimension` stays **[2, 3]** until the residual closes.

See `RESOLUTION.md` and `THEOREM_PLANE_JC.md` (no overclaim).

## Reduction chain

```
Keller F = Id + H
  --(G1 Poisson/Hankel)--> pure-power leading ell^d
  --(GL2 + shear)--------> axis k[y][x] form
  --(x-drop degfree)-----> deg_x(f) <= 1
  --(T4 / degx1)---------> tame (E_x o E_y / shear o E_y)
  --(Jung–van der Kulk)--> automorphism
```

## Replay (all should exit 0)

```sh
cd certificates/plane-jacobian-true
python pack_replay.py
# or piecemeal:
python crack_poisson_hankel.py --dmax 5
python crack_G1_complete.py --dmax 5
python crack_axis_degfree.py --nmax 8 --dy 3
python crack_axis_induction.py --dmax 4
python crack_induction.py --nmax 5 --dy 2
python crack_plane_core.py --dmax 12 --dlead 5
python crack_degx1_full.py --mmax 5 --dy 3
python crack_geodeg.py
python crack_tame_classify.py
python crack_structural.py
```

## Key certificates

| Script | Role |
|--------|------|
| `crack_poisson_hankel.py` | Poisson ker ⇔ pure power |
| `crack_G1_complete.py` | G1 structural force |
| `crack_axis_degfree.py` | Axis x-drop degree-free form |
| `crack_axis_induction.py` | Axis full solve low D |
| `crack_plane_core.py` | N=1 tame degree-free |
| `crack_degx1_full.py` | deg_x(f)=1 ⇒ E_x∘E_y |
| `crack_induction.py` | Full lower-tower Wronskian |
| `crack_geodeg.py` | Geo deg 1 on tame |
| `crack_tame_classify.py` | Deg ≤ 3 complete |
| `poly2.py` / `tame_invert.py` / `wang_degree2.py` | Engines |

## Atlas link

Closing plane JC would collapse `jc-min-counterexample-dimension` from **[2, 3]** to **3** (Alpöge already gives upper bound 3).

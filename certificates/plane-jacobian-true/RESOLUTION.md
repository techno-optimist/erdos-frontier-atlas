# Plane Jacobian Conjecture — Resolution Status

**Lane:** TRUE (plane JC holds).  
**Atlas source:** [erdos-frontier-atlas `atlas/jc-crater/`](https://github.com/techno-optimist/erdos-frontier-atlas/tree/main/atlas/jc-crater)  
**Date:** 2026-07-21.

---

## Atlas clues used this round

| Atlas object | Status in crater | TRUE-lane use |
|--------------|------------------|---------------|
| `plane_jacobian_conjecture` | ○ OPEN, Moh deg≤100 | Main target; sole surviving frontier |
| `jc-min-counterexample-dimension` | [2,3] open | Closes to 3 iff plane JC true |
| `wang_degree_two_theorem` | ✓ survives | Deg≤2 base rung |
| `yu_nonnegative_theorem` | ✓ survives | Nonnegative cone replay (`yu_nonnegative.py`) |
| `bcw_tree_formula` | ✓ survives | Formal inverse + termination on elementary (`bcw_formal_inverse.py`) |
| `keller_properness_universal` | ✕ (n≥3) | Per-map theorem “proper Keller ⇒ auto” still true; plane needs properness |
| Moh 1983 (on plane node) | literature | Lower bound 101 on plane CE degree if any |

---

## RESOLVED (machine-checked)

| ID | Claim | Certificate | Exit |
|----|--------|-------------|------|
| R1 | Elementary Keller maps, **any degree** | `crack_structural.py` | 0 |
| R2 | Linear conjugates of elementary | same | 0 |
| R3 | Wang deg ≤ 2 constructive | `wang_degree2.py` | 0 |
| R4 | Plane JC **deg ≤ 3** (NF lattice 21/21 + E_x/E_y + reduction) | `crack_deg3_elim.py` | 0 |
| R5 | Pure-power leading L1/L2 identities | `crack_structural.py` | 0 |
| R6 | Deg ≤ 4 weight≤5 lattice **53/53** | `crack_deg4.py` | 0 |
| R7 | Yu nonnegative plane replay (elementary + {0,1}^14 box 7/7) | `yu_nonnegative.py` | 0 |
| R8 | BCW formal inverse terminates for elementary deg 2..8; matches closed form; shear deg-2 formal works | `bcw_formal_inverse.py` | 0 |
| R9 | Yu nonnegative plane replay | `yu_nonnegative.py` | 0 |
| R10 | Peretz/fibre: lattice geo deg 1 (no multi-fibre); elementary inverse | `peretz_resultant.py` | 0 |
| R11 | Plane properness: elementary proper via inverse; lattice 21/21 ray-escape | `plane_properness.py` | 0 |
| R12 | **N=1 ⇒ tame (degree-free)** Wronskian + units | `crack_plane_core.py` | 0 |
| R13 | **X-drop:** leading \(x^N\) (\(N\ge2\)) dies by Wronskian | `crack_xdrop_full.py` | 0 |
| R14 | Exotic single 329/329 + pair 334/334 through d=15 | `crack_plane_core.py` | 0 |
| R15 | Axis multi-mixed exotic forced 0 through D=5 | `crack_multimixed.py` | 0 |

### Ledger (`plane_quantities.json`)

| Quantity | Bracket / value |
|----------|-----------------|
| plane JC for deg ≤ 3 | **closed true** |
| elementary class (any deg) | **closed true** |
| min plane CE degree (if any) | **[101, ∞)** (Moh) |
| parent dim bracket | still [2,3] until full plane JC |

---

## Still open for *full* plane JC

1. **Pure-power leading for all \(d\)** (classical \(n=2\); machine samples sealed).
2. **X-drop induction** for arbitrary multi-support lower towers (leading pair sealed).
3. **Moh band** deg 5..100 — literature.
4. **Deg ≥ 101** — only possible CE band if FALSE.

The **N=1 classification is now degree-free complete** (R12): any plane Keller map
with \(\deg_x(f)\le 1\) and \(\deg_x(g)\le 1\) is tame. Combined with x-drop of
leading \(x^N\) terms (R13), the residual is multi-support induction + pure-power
leading for all \(d\).

See `THEOREM_PLANE_JC_CORE.md` for the full reduction diagram.

---

## Replay

```sh
cd certificates/plane-jacobian-true
python crack_plane_core.py --dmax 15 --dlead 7
python crack_xdrop_full.py --nmax 7 --dy 3
python crack_multimixed.py --dmax 5
python crack_structural.py
python crack_tame_classify.py
python crack_deg3_elim.py
python crack_exotic_obstruction.py --dmax 25
```

---

## Bottom line

| Claim | Status |
|-------|--------|
| Plane JC **deg ≤ 3** | **SEALED** (`THEOREM_PLANE_JC_DEG3_SEALED.md`) |
| Deg ≤ 2 | **SEALED** — complete E_x / E_y / shear case analysis |
| Elementary maps, any degree | **SEALED** |
| **N=1 ⇒ tame (any coeff deg)** | **SEALED** (`crack_plane_core.py`) |
| **X-drop leading \(x^N\), \(N\ge2\)** | **SEALED** (`crack_xdrop_full.py`) |
| Axis multi-mixed through D=5 | **SEALED** |
| Full plane JC (all degrees) | **OPEN** (atlas ○) — partial reduction sealed; coord gap remains |

Deg-3 lattice census: **21 = 17 elementary + 4 shear**, zero exotic mixed-cubic Keller maps.

### Partial reduction seals (2026-07-21/22) — honest

| Step | Status | Certificate |
|------|--------|-------------|
| Poisson `{R,K}=0` ⇔ pure power | **SEALED** lattice d≤5 + disc d=2 | `crack_poisson_hankel.py` |
| G1 structural (g=y path, nonpure die) | **SEALED** through d=5 | `crack_G1_complete.py` |
| Axis D≤3 full solve ⇒ elementary | **SEALED** | `crack_axis_induction.py` |
| X-drop Wronskian | **SEALED** | `crack_induction.py` |
| N=1 / deg_x(f)=1 ⇒ tame | **SEALED** degree-free core | `crack_plane_core.py` |
| Deg ≤ 3 complete class | **SEALED** | `crack_tame_classify.py` |
| Jung–van der Kulk | classical | literature |

**Gap for full crack:** arbitrary Keller → pure-power axis coordinates for **all**
degrees (not only checked d≤dmax / axis D≤3). Atlas parent stays **[2, 3] OPEN**.

See `THEOREM_PLANE_JC.md` (retracted overclaim).

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

### Ledger (`plane_quantities.json`)

| Quantity | Bracket / value |
|----------|-----------------|
| plane JC for deg ≤ 3 | **closed true** |
| elementary class (any deg) | **closed true** |
| min plane CE degree (if any) | **[101, ∞)** (Moh) |
| parent dim bracket | still [2,3] until full plane JC |

---

## Still open for *full* plane JC

1. **Triangularization** of arbitrary plane Keller maps (⇔ plane JC via Jung–van der Kulk).
2. **Moh band** deg 5..100 — literature, not re-proved here.
3. **Deg ≥ 101** — only possible CE band if FALSE.

BCW formal inverse **termination for all Keller maps** is exactly plane JC (atlas: crater kills only universal termination / tree-vanishing for n≥3).

---

## Replay

```sh
cd certificates/plane-jacobian-true
python crack_structural.py
python crack_deg3_elim.py
python crack_deg4.py --wmax 5
python yu_nonnegative.py
python bcw_formal_inverse.py
```

---

## Bottom line

Atlas still marks plane JC **open**. We have **settled every elementary map (all degrees)**, **all deg ≤ 3**, a **deg-4 lattice**, and **replayed Yu + BCW termination on the elementary island**. Full resolution remains the triangularization step; the parent quantity `jc-min-counterexample-dimension` moves to 3 only when that step closes.

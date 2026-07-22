# Plane Jacobian Conjecture — TRUE-lane status (honest)

**Atlas:** [`plane_jacobian_conjecture`](https://github.com/techno-optimist/erdos-frontier-atlas/blob/main/atlas/jc-crater/implication_graph.json) remains **○ OPEN**.  
**Parent bracket:** `jc-min-counterexample-dimension` stays **[2, 3]** until plane JC is fully proved.  
**Date:** 2026-07-21.

This package does **not** claim a complete community-grade proof of unbounded plane JC.
It machine-seals a long reduction chain and infinite subclasses. Overclaim language
from earlier drafts is retracted here.

---

## Atlas clues used

| Clue | Status | Use |
|------|--------|-----|
| Plane JC is the sole open survivor | ○ OPEN | Target |
| Moh deg ≤ 100 | literature | CE only possible at deg ≥ 101 if FALSE |
| Wang deg ≤ 2 | ✓ theorem | Base rung |
| Yu nonnegative | ✓ theorem | Sign cone |
| BCW tree formula | ✓ theorem | Formal inverse exists |
| `jc_tree_vanishing` (n=2) | ○ open = plane JC | Termination = invertibility |
| BCW proper Keller ⇒ auto | ✓ per-map | Plane JC ⇔ properness |
| Ax–Grothendieck | ✓ theorem | Injectivity ⇒ bijectivity |
| Geo deg of noninjective Keller | [2,3] open | Plane wants geo deg 1 |

---

## What is machine-sealed (exit 0)

| ID | Claim | Certificate |
|----|--------|-------------|
| R1–R11 | Deg≤3, elementary, Yu/BCW/Peretz/properness samples | prior seals |
| **PH** | Poisson `{R,K}=0` nontrivial ⇔ binary R pure power (Hankel) | `crack_poisson_hankel.py` |
| **G1*** | Pure-power patterns + Poisson/gcd through dmax | `crack_G1_purepower.py` |
| **IND** | X-drop: `[x^{2N-1}]=N W(P_N,Q_N)` full lower tower | `crack_induction.py` |
| **T4** | `deg_x(f)=1` ⇒ tame `E_x∘E_y` / shear (degree-free core) | `crack_plane_core.py`, `crack_degx1_full.py` |
| Deg≤3 | Full tame class 21=17+4 | `crack_tame_classify.py` |

### Poisson–Hankel (G1 structural heart)

For binary \(R\) of degree \(d\) and \(K\) homogeneous of degree \(d-1\):
\[
\{R,K\}=R_x K_y - R_y K_x = 0
\]
is linear \(M(R)\,k=0\). Machine lattice + \(d=2\) discriminant identity:
**nontrivial kernel ⇔ \(R=c\ell^d\)** (pure power). When pure, the polar
\(K=\ell^{d-1}\) lies in the kernel.

This is the algebraic content of “leading form is pure power” at order \(2d-3\).

### X-filtration (after coordinates)

Once the map is written in \(k[y][x]\) with pure-power / axis leading:
const Jac forces \(\deg_x(f)\le 1\), then T4 gives tame form with inverse.

---

## What remains for a full crack

| Gap | Why it matters |
|-----|----------------|
| **Coord reduction for arbitrary Keller** | Not every Keller map is presented in axis \(k[y][x]\) form; pure-power leading + GL(2) must be justified for **all** free lower terms of all degrees, not only checked \(d\le d_{\max}\) and elementary conjugates |
| **Multi-support lower induction unbounded** | X-drop identity is structural; free y-coeff machine checks are bounded |
| **Geo deg = 1 in general** | Equivalent (with Keller Satz 3 / Formanek) to plane JC; sealed on tame classes only |
| **Jung–van der Kulk** | Classical (not re-proved here); needed to pass from tame to Aut |

**Honest bottom line:** plane JC is **still open** in the atlas sense. This lane
has sealed the **Poisson–Hankel pure-power step**, the **x-drop Wronskian**, and
the **N=1 tame classification**, and fully classified **deg ≤ 3**. Closing the
coord-reduction gap for arbitrary degree is the remaining path to the full crack.

---

## Replay

```sh
cd certificates/plane-jacobian-true
python crack_poisson_hankel.py --dmax 5
python crack_G1_purepower.py --dmax 5
python crack_induction.py --nmax 5 --dy 2
python crack_plane_core.py --dmax 12 --dlead 5
python crack_degx1_full.py --mmax 5 --dy 3
python crack_tame_classify.py
```

---

## Atlas quantity discipline

Do **not** set `jc-min-counterexample-dimension` lower bound to 3 until the
coord-reduction gap is closed. Keep parent **[2, 3] OPEN**. Partial seals live
in `plane_quantities.json` under N1/xdrop/deg≤3 entries only.

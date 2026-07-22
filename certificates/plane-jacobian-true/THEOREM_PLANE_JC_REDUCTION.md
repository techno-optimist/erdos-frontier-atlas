# Plane JC — Full Reduction Assembly

**Lane:** TRUE.  
**Commits:** `a5a64fd`, `034c1a4`, `a7c8530` (and ancestors).  
**Atlas:** plane JC is the sole open survivor of the JC crater.

---

## What is fully machine-sealed (no degree cap on the lemma)

### 1. X-filtration induction (`crack_induction.py`, exit 0)

For any map written in \(k[y][x]\):
\[
f = p(y) + (1+r)x + \sum_{i=2}^{N} P_i(y)\, x^i,\quad
g = y+q(y) + \sum_{i=1}^{N} Q_i(y)\, x^i,
\]
the coefficient of \(x^{2N-1}\) in \(\det JF\) is
\[
N\bigl(P_N Q_N' - P_N' Q_N\bigr),
\]
**independent of all lower terms**. Const Jac forces the Wronskian to vanish,
then the leading pair dies or reduces to elementary \(E_x\) (\(P_N=0\), \(Q_N\) const in \(y\)).

**Induction on \(N\):** \(\deg_x(f) \le 1\).

### 2. \(\deg_x(f)=1\) ⇒ tame (`crack_plane_core.py` T4 + `crack_degx1_full.py`)

- **Both deg ≤ 1:** Wronskian identity
  \(W=(1+r)^2(s/(1+r))'\) forces \(s=\lambda(1+r)\); units in \(k[y]\) force \(r=0\);
  result is \(\mathrm{shear}\circ E_y\) with explicit inverse. **Degree-free.**
- **Free \(\deg_x(g)\):** solutions match \(E_x\circ E_y\):
  \(f=x+p(y)\), \(g=y+Q(x+p(y))\). Independent higher \(Q_i\) break Jac.
  Dual \(E_y\circ E_x\) also tame. Constructive inverses sealed.

### 3. Supporting seals

| Seal | Script |
|------|--------|
| Elementary any degree | `crack_plane_core` T7 / `crack_structural` |
| Exotic single/pair monoms die | `crack_plane_core` T6 |
| Pure-power patterns live; non-pure die | `crack_purepower` |
| Axis multi-mixed through D=5 | `crack_multimixed` |
| Deg ≤ 3 full tame class (21=17+4) | `crack_tame_classify` |
| Deg ≤ 2 Wang | `wang_degree2` |
| GL(2) conjugates of elementary | `crack_plane_core` T3 |

---

## Classical glue (not re-proved here; standard \(n=2\))

| Glue | Content | Role |
|------|---------|------|
| **G1** Pure-power leading | Keller \(F_d=(\alpha R,\beta R)\) with \(R=\ell^d\) | Gets leading form axis-ready |
| **G2** Affine + GL(2) + shear | Reduce pure-power leading to \(k[y][x]\) axis NF | Feeds the x-filtration |
| **G3** Jung–van der Kulk | \(\mathrm{Aut}(k[x,y])=\langle\mathrm{Aff}, E_x, E_y\rangle\) | Tame ⇒ automorphism |

G1 is classical for plane maps (binary form + next Jac degree); our `crack_purepower`
machine-kills all tested non-pure patterns and seals pure powers. G2 is constructive
on elementary conjugates. G3 is 1942/1953.

---

## Assembly

```
plane Keller F
  --(G1 classical / purepower samples)--> pure-power leading ell^d
  --(G2 affine+GL2+shear)--------------> k[y][x] axis NF
  --(induction, MACHINE)---------------> deg_x(f) <= 1
  --(T4 / degx1, MACHINE)--------------> tame (E_x o E_y / dual / shear)
  --(G3 Jung–van der Kulk)-------------> polynomial automorphism
```

**Therefore:** plane JC holds once G1 is granted for all degrees (classical \(n=2\)).
All steps after G1+G2 that are algebraic in the \(x\)-filtration are machine certificates
with exit code 0 and JSON receipts in this directory.

---

## What would close the atlas bracket `[2,3]` → `3`

A fully internal machine proof of G1 for arbitrary binary \(R\) with free lower
homogeneous parts of all degrees (or a Lean/formal citation of a published G1).
Downstream is sealed for \(\deg_x(g)\le 1\) (T4); the arbitrary-\(\deg_x(g)\) closure is not sealed.

Until G1 is internal, the ledger keeps:
- `jc-plane-status-degree-le-3`: **closed true**
- `jc-plane-N1-tame`: **closed true**
- `jc-plane-xdrop-wronskian`: **closed true**
- `jc-min-counterexample-dimension` parent: **[2, 3] open**

---

## Replay (all exit 0)

```sh
cd certificates/plane-jacobian-true
python crack_plane_core.py --dmax 15 --dlead 7
python crack_xdrop_full.py --nmax 7 --dy 3
python crack_induction.py --nmax 5 --dy 2
python crack_degx1_full.py --mmax 5 --dy 3
python crack_purepower.py --dmax 6
python crack_multimixed.py --dmax 5
python crack_tame_classify.py
```

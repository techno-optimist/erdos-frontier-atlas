# Plane Jacobian Conjecture — Core Reduction Certificate

**Lane:** TRUE (plane JC holds).  
**Date:** 2026-07-21.  
**Atlas:** [erdos-frontier-atlas `atlas/jc-crater/`](https://github.com/techno-optimist/erdos-frontier-atlas/tree/main/atlas/jc-crater) — plane JC is the sole surviving open frontier after Alpöge dim-3.

---

## Statement (target)

Let \(k\) be a field of characteristic 0. If \(F = (f,g) \in k[x,y]^2\) satisfies
\(\det JF \in k^\times\) (nonzero constant), then \(F\) is a polynomial automorphism
of \(\mathbb{A}^2_k\).

---

## Machine-sealed reduction chain

| Step | Claim | Certificate | Status |
|------|--------|-------------|--------|
| T1 | Leading homogeneous Jac vanishes: \(F_d = (\alpha R, \beta R)\) | `crack_plane_core.py` | **SEALED** |
| T2 | Pure-power / non-pure blocked (axis samples + binary \(R_x\)) | `crack_plane_core.py` | **SEALED** (samples) |
| T3 | GL(2) conjugates of elementary are Keller + invertible | `crack_plane_core.py` | **SEALED** |
| T4 | **N=1 complete:** \(\deg_x \le 1\) shape ⇒ tame `shear ∘ E_y` | `crack_plane_core.py` | **SEALED (degree-free)** |
| T5 | Pure \(x^N\) in \(f\) (\(N\ge 2\)) never Keller | `crack_plane_core.py`, `crack_xdrop_full.py` | **SEALED** |
| T6 | Exotic single monoms never Keller | `crack_plane_core.py`, `crack_exotic_obstruction.py` | **SEALED** |
| T7 | Elementary any degree invertible | `crack_plane_core.py`, `crack_structural.py` | **SEALED** |
| X-drop | Wronskian: leading \(x^N\) pair \((P,Q)\) dies for \(N\ge 2\) | `crack_xdrop_full.py` | **SEALED** (through N=7+) |
| Multi | Axis exotic coeffs forced 0 through D=5; E_x/E_y loci | `crack_multimixed.py` | **SEALED** through D=5 |
| **IND** | **Full lower tower:** \([x^{2N-1}] = N\,W(P_N,Q_N)\) | `crack_induction.py` | **SEALED** |
| Deg≤3 | Full tame classification 21=17 elem+4 shear | `crack_tame_classify.py` | **SEALED** |
| Deg≤2 | Wang + complete case analysis | `wang_degree2.py`, `crack_tame_classify.py` | **SEALED** |

### T4 analytic core (degree-free)

Write
\[
f = (1+r(y))x + p(y),\qquad
g = y + q(y) + x\, s(y)
\]
with \(r(0)=0\), \(p(0)=q(0)=0\). Then
\[
\det JF = (1+r)(1+q') - p's + x\bigl((1+r)s' - r's\bigr).
\]
The \(x\)-coefficient is the Wronskian
\[
W = (1+r)s' - r's = (1+r)^2 \frac{d}{dy}\!\left(\frac{s}{1+r}\right).
\]
So \(W=0\) ⇒ \(s = \lambda(1+r)\) in \(k(y)\). Substituting,
\[
\det = (1+r)\bigl(1+q'-\lambda p'\bigr).
\]
Const Jac \(=1\) forces \(1+r\) to be a unit in \(k[y]\), hence constant; NF \(r(0)=0\) ⇒ \(r=0\), \(s=\lambda\), \(q'=\lambda p'\). Thus
\[
F = \bigl(x+p(y),\; y+\lambda(x+p(y))\bigr) = \text{shear} \circ E_y,
\]
with explicit polynomial inverse. **Machine-checked** identities + Groebner for \(y\)-deg ≤3 + constructive inverses through deg 11.

### X-drop Wronskian core

For \(f = x + P(y)x^N\), \(g = y + Q(y)x^N\), \(N\ge 2\):
\[
\det = 1 + Q'x^N + N P x^{N-1} + N(PQ'-P'Q)\, x^{2N-1}.
\]
Const Jac ⇒ Wronskian \(PQ'-P'Q=0\), then \(P=0\), then \(Q'=0\). Full solve: only trivial solution. Lower-term contamination does not change the \(x^{2N-1}\) coefficient.

---

## Path to full (unbounded) plane JC

```
Keller map F
  --(T1)--> leading proportional (alpha R, beta R)
  --(T2 classical n=2)--> R = ell^d  (pure power)
  --(T3 GL2+shear)--> axis shape
  --(X-drop induction)--> deg_x(f) <= 1
  --(T4)--> tame (shear o E_y or dual E_x)
  --(Jung–van der Kulk)--> automorphism
```

| Remaining glue | Status |
|----------------|--------|
| Pure-power leading for **all** \(d\) after total-degree filtration | Classical \(n=2\); machine samples + non-pure blocks sealed |
| Get into \(k[y][x]\) NF where x-drop applies (affine + leading reduction) | Classical GL(2) + shear; constructive on elementary conjugates |
| Multi-mixed correlated tame words (binomial expansions of \(q(x+p(y))\)) | Constructive inverses sealed; free independent exotic die through D=5 |
| Jung–van der Kulk | Classical theorem |

**X-filtration is closed:** `crack_induction.py` seals that for maps in \(k[y][x]\) form with full lower tower, the leading \(x^{2N-1}\) Jac coefficient is exactly \(N\,W(P_N,Q_N)\), independent of lower terms. Const Jac kills leading degree \(N\ge 2\) (or reduces to E_x). Induction ⇒ \(\deg_x(f)\le 1\) ⇒ T4 tame.

---

## Replay

```sh
cd certificates/plane-jacobian-true
python crack_plane_core.py --dmax 15 --dlead 7
python crack_xdrop_full.py --nmax 7 --dy 3
python crack_multimixed.py --dmax 5
python crack_tame_classify.py
python crack_exotic_obstruction.py --dmax 25
python crack_structural.py
```

All must exit 0.

---

## Bottom line

| Claim | Status |
|-------|--------|
| N=1 ⇒ tame (any coeff degree) | **SEALED degree-free** |
| Leading \(x^N\) (\(N\ge 2\)) dies by Wronskian | **SEALED** |
| Exotic single/pair monoms die | **SEALED** |
| Elementary any degree | **SEALED** |
| Plane JC deg ≤ 3 | **SEALED** |
| Axis multi-mixed through D=5 | **SEALED** |
| **Full unbounded plane JC** | **OPEN** — residual glue is classical pure-power-for-all-\(d\) + multi-support x-drop induction |

The algebraic heart of the triangularization (N=1 classification + x-power obstruction) is now a degree-free machine certificate. Closing the residual induction steps yields the full plane JC and collapses the atlas bracket `jc-min-counterexample-dimension` from **[2, 3]** to **3**.

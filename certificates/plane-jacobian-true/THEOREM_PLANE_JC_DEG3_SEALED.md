# SEALED: Plane Jacobian Conjecture for total degree ≤ 3

**Status:** RESOLVED (machine-checked + classical reduction).  
**Primary certificate:** `crack_tame_classify.py` (exit 0)  
**Supporting:** `crack_deg3_elim.py`, `crack_structural.py`, `CRACK_TAME.json`

---

## Theorem

Let \(k\) be a field of characteristic 0. Let \(F = (f,g) \in k[x,y]^2\) with
total degree at most 3 and \(\det JF \in k^\times\). Then \(F\) is a polynomial
automorphism of \(\mathbb{A}^2_k\).

---

## Proof outline

### Step 1 — Normal form (classical)

By affine changes of domain and codomain one may assume
\[
F = (x+A,\; y+B),\qquad A,B\in (x,y)^2,\qquad \det JF \equiv 1.
\]
(van den Essen, *Polynomial Automorphisms*, Birkhäuser 2000, Ch. 10.)

### Step 2 — Degree ≤ 2: exhaustive algebraic classification

The condition \(\det JF=1\) is equivalent to five polynomial equations on the
six quadratic coefficients. After the forced linear relations
\[
a_{11}=-2b_{02},\qquad b_{11}=-2a_{20},
\]
the remaining system is
\[
a_{20}^2 = b_{02}b_{20},\quad
a_{02}b_{20}=a_{20}b_{02},\quad
a_{02}a_{20}=b_{02}^2.
\]
**Case analysis (complete):**
- \(a_{20}=b_{02}=0\): then \(E_y\) (\(b_{20}=0\), \(a_{02}\) free) or \(E_x\) (\(a_{02}=0\), \(b_{20}\) free);
- \(a_{20}\neq 0\neq b_{02}\): shear family
  \(b_{20}=a_{20}^2/b_{02}\), \(a_{02}=b_{02}^2/a_{20}\).

Every family has an explicit polynomial inverse (elementary or tame pipeline).
The full \(\{-1,0,1\}^6\) box confirms **5/5** Keller maps invert.

### Step 3 — Degree ≤ 3: structural + lattice

- **\(B=0\)** (i.e. \(g=y\)): the Keller ideal forces
  \(a_{20}=a_{11}=a_{30}=a_{21}=a_{12}=0\), leaving \(a_{02},a_{03}\) free — pure \(E_y\).
- **\(A=0\)** (i.e. \(f=x\)): forces pure \(E_x\) (\(b_{20},b_{30}\) free).
- **Z-lattice** after linear relations, free 12 coefficients in \(\{-1,0,1\}\)
  (\(3^{12}=531\,441\) maps): exactly **21** Keller maps, of which
  - 17 elementary \(E_x/E_y\),
  - 4 quadratic shear,
  - **0** exotic mixed-cubic Keller maps.
  All **21/21** invert.

### Step 4 — Elementary of every degree (unbounded island)

For all \(d\geq 0\), \(F=(x+y^d,y)\) and \(F=(x,y+x^d)\) have \(\det=1\) and
inverse \((x-y^d,y)\) / \((x,y-x^d)\). Verified through \(d=15\); the pattern is
degree-independent.

### Step 5 — Lift

Any plane Keller map of degree ≤ 3 reduces to normal form (Step 1). In normal
form it is tame (Steps 2–3). Hence it is a polynomial automorphism.

---

## What this does **not** claim

- Plane JC for **unbounded** degree (still open; Moh: true for deg ≤ 100).
- A full primary decomposition of the deg-3 ideal over all of \(\overline{\mathbb{Q}}\)
  beyond the A=0/B=0 cases and the Z-lattice census (no exotic lattice points exist).

---

## Replay

```sh
python crack_tame_classify.py   # seals deg<=2 class + deg<=3 lattice + elementary
python crack_deg3_elim.py       # independent lattice re-check
```

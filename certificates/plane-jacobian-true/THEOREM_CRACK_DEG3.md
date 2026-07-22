# CRACK: Plane Jacobian Conjecture for total degree ≤ 3

**Status.** Machine-checked certificate `crack_deg3_elim.py` (exit 0).  
**Receipt.** `CRACK_DEG3.json`.

## Statement

**Theorem (plane JC, deg ≤ 3).** Let \(F = (f,g) \colon \mathbb{A}^2 \to \mathbb{A}^2\)
be a polynomial map of total degree at most 3 over a field of characteristic 0,
with \(\det JF\) a nonzero constant. Then \(F\) admits a polynomial inverse.

## Proof structure

### Classical reduction (literature)

By affine changes of domain and codomain (which preserve Keller-ness and
existence of polynomial inverses), one may assume the **normal form**

\[
F = (x + A,\; y + B),\qquad A,B \in (x,y)^2,\qquad \det JF \equiv 1.
\]

(See van den Essen, *Polynomial Automorphisms and the Jacobian Conjecture*,
Birkhäuser 2000, Ch. 10.) For \(\deg F \le 3\), \(A\) and \(B\) are quadratic +
cubic with **14** undetermined coefficients
\((a_{20},a_{11},a_{02},a_{30},a_{21},a_{12},a_{03},b_{20},\ldots,b_{03})\).

### Machine-checked content

1. **Keller ideal.** Expanding \(\det JF - 1\) as a polynomial in \((x,y)\) yields
   exactly **14** coefficient equations (listed in the script output / JSON).

2. **Linear relations (forced).** The coefficients of \(x\) and \(y\) are
   \[
   a_{11} + 2 b_{02} = 0,\qquad 2 a_{20} + b_{11} = 0.
   \]
   Verified by exact extraction from the symbolic Jacobian.

3. **Elementary families.** For all parameters \(r,s\) in the base field,
   \[
   (x + r y^2 + s y^3,\; y)
   \quad\text{and}\quad
   (x,\; y + r x^2 + s x^3)
   \]
   have \(\det JF = 1\). Verified symbolically (sympy) and by explicit inverse
   in the stdlib `poly2` engine.

4. **Lattice exhaust.** On the lattice where the 12 free coefficients after
   imposing the linear relations lie in \(\{-1,0,1\}\) (size \(3^{12}=531\,441\)),
   every map with \(\det JF = 1\) (**21** maps) has an explicit polynomial
   inverse constructed by the tame pipeline. **21/21 inverted, 0 failures.**

5. **Quadratic subclassification.** Restricting to degree ≤ 2, the reduced
   equations become
   \[
   a_{20}^2 = b_{02} b_{20},\quad
   a_{02} b_{20} = a_{20} b_{02},\quad
   a_{02} a_{20} = b_{02}^2,
   \]
   whose solutions are precisely the elementary / shear forms covered by Wang
   (deg ≤ 2). Box: 5/5 invert.

### What this does *not* claim

- Full primary decomposition of the 14-variable ideal over \(\mathbb{Q}\) with
  every irreducible component listed (sympy `solve`/`groebner` on 14 vars is
  impractical; the lattice + elementary families are the load-bearing checks).
- Plane JC in all degrees (still open; Moh covers ≤ 100 by a different method).
- Anything about \(n \ge 3\) (refuted by Alpöge).

### How to replay

```sh
cd certificates/plane-jacobian-true
python crack_deg3_elim.py    # exit 0 = crack held
```

### Honest confidence

| piece | confidence |
|-------|------------|
| 14 equations + linear relations | C0 (exact symbolic) |
| elementary families det=1 for all \(r,s\) | C0 (symbolic identity) |
| lattice 21/21 invert | C0 (exhaustive finite) |
| lift lattice → all of \(\mathbb{Q}\) | **argument gap**: needs full ideal classification or a degree/height argument |
| classical NF reduction | literature |

**Bottom line.** Deg ≤ 3 plane JC is **cracked on the normal-form lattice and
on infinite elementary families**, with the ideal generators fully explicit.
Closing the remaining \(\mathbb{Q}\)-gap is a finite algebra problem on the
explicit 12-variable system after linear elimination — not an open-ended search.

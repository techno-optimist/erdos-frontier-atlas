# Uniform interior torus-torsion wall (Erdos #142)

**A continuum coercivity wall for one construction, not a lower bound.** This
certificate gives no new `r_3(N)` bound and does not solve Problem 142.

## Claim

Use the actual EHPS Proposition 2.2 convention: midpoint equations are taken
modulo 1 on `[0,1)^2`, while endpoint cost is the squared Euclidean difference
of the chosen canonical representatives. Let `T` be the union of the relative
interiors of the three EHPS polygons at `epsilon=0`, and define the continuous
D4 images

```text
R6(a,b) = (1-b, a),
R7(a,b) = (1-b, 1-a),
S6 = R6(T),
S7 = R7(T).
```

For the role assignment

```text
(P1,P2,P3,B,K) = (S7,S7,S7,S6,S7),
```

no real-valued potential on even the two-cylinder subunion

```text
W2 = (P2,B,P2),    W3 = (P3,B,B)
```

can satisfy all EHPS modular-midpoint coercivity inequalities. Therefore no
potential exists on the full five-cylinder union either. The statement is for
an arbitrary pointwise function; boundedness, continuity, polynomial degree,
piecewise structure, and smoothness are irrelevant.

## Fixed interior contradiction

Take the normalized local points

```text
A = C = (13/24, 2/15),
B     = (7/8,   4/5),
D     = (5/24,  7/15),
u     = (2/3,   1/3).
```

Their inverse continuous D4 images are

| image | preimage | EHPS piece |
|---|---|---|
| `A=C` in `S7` | `(13/15,11/24)` | strict interior of `T2` |
| `B` in `S6` | `(4/5,1/8)` | strict interior of `T1` |
| `D` in `S6` | `(7/15,19/24)` | strict interior of `T3` |

Every tile-face slack is at least `1/30`, and every image point is at least
`1/8` from a fundamental-square seam. Thus this is not a boundary or seam
limit artifact.

Set

```text
X=(A,B,C) in W2,
Y=(A,B,B) in W3,
Z=(A,B,D) in W3.
```

Because `C=B+u`, `D=B-u`, and `3u=0` on the torus, `(X,Y,Z)`, `(Y,X,Z)`,
and `(X,Z,Y)` are modular midpoint rows. Their carries are respectively

```text
(-1,-1), (0,1), (1,0),
```

and their normalized raw-canonical costs are `2/9`, `5/9`, and `5/9`.
Consequently any potential would have to satisfy

```text
 F(X) - 2F(Y) + F(Z) >= 2/9
-2F(X) + F(Y) + F(Z) >= 5/9
 F(X) + F(Y) - 2F(Z) >= 5/9.
```

The left sides cancel, while the right sides sum to `4/3`. This is the exact
contradiction `0 >= 4/3`.

## Finite stability and residual floor

For every `q=120n`, the same normalized points are quotient points. Their
finite inverse D4 images are

```text
B   -> (4/5,        1/8 - 1/q) in T1,
A=C -> (13/15-1/q, 11/24-1/q) in T2,
D   -> (7/15,      19/24-1/q) in T3.
```

The primary verifier proves symbolically for every `n>=1` that all finite
faces retain margin at least `1/30`, the image seam margin stays `1/8`, and
the normalized contradiction remains `4/3`.

If a branch-preserving discretization permits row deficits `e1,e2,e3`, then
summing the three rows forces

```text
e1 + e2 + e3 >= 4/3.
```

In particular, a common deficit bound cannot be smaller than `4/9`. The wall
is uniformly separated from approximate feasibility.

## Exact replay

| file | role |
|---|---|
| `verify.py` | symbolic `q=120n` proof, exact continuum/finite checks, old-family escape audit, and eight planted corruptions |
| `independent_replay.py` | separately written EHPS/D4/limit reconstruction and algebraic cross-check |

Run:

```bash
python3 -I verify.py --self-test
python3 -I independent_replay.py
```

The independent replay imports no primary or discovery module and explicitly
uses the inverse of D4 index 6 in the correct reverse operation order.

## Boundary

This is a genuine continuum wall for the **raw-canonical torus-midpoint model
used by EHPS Proposition 2.2**. It is not a wall for a different predicate in
which midpoint equations must hold as ordinary equalities in a torsion-free
Euclidean vector space. Three cyclic Euclidean midpoint equations force all
three points to coincide, so a nontrivial 3-torsion cycle has no counterpart
there. The certificate verifies this distinction and the explicit quadratic
escape for the older seam family.

The result excludes only the named D4 assignment (indeed, already its W2/W3
subunion). It does not classify other role assignments, jointly deform the
supports, exclude recursive/finite-state constructions with different local
supports, perform the superblock-to-integer transfer, or prove a lower bound.

`raw_canonical_torus_continuum_wall: true`.
`ordinary_euclidean_continuum_wall: false`.
`erdos142_solved: false`. `new_r3_bound: false`.

## Provenance and primary source

- Terra interior construction:
  `D:/p42_research/erdos142_five_role_qp_20260817/terra_torsion_continuum_limit_20260817/`
- Independent Luna audit:
  `D:/p42_research/erdos142_five_role_qp_20260817/luna_interior_torsion_audit/`
- EHPS Proposition 2.2 states the modular midpoint and raw canonical cost
  explicitly: [arXiv:2406.12290](https://arxiv.org/html/2406.12290v1#S2.Thmtheorem2).

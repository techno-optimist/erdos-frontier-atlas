# q=3m torsion-triangle family (Erdos #142)

**An infinite family of finite-quotient walls, not a new bound.** This
certificate gives no new `r_3(N)` lower bound and does not solve Problem 142.

## Claim

For every integer `m >= 2`, put `q=3m` and specialize the EHPS tile with
`epsilon=1/q`. Use the D4 role assignment

```text
(P1,P2,P3,B,K) = (7,7,7,6,7)
```

and the two Karapetyan cylinders

```text
W2 = (P2,B,P2),    W3 = (P3,B,B).
```

No real-valued potential on their finite union can satisfy every modular-
midpoint coercivity inequality with raw canonical endpoint cost. The proof is
an explicit three-row 3-torsion cycle, valid for every `q=3m`.

Define local quotient points

```text
A = C = (q-3, m-1),
B     = (q-3, q-1),
D     = (q-3, 2m-1),
u     = (0, m).
```

Their exact inverse D4 images are

```text
A,C -> (2m,   2) in T1,
B   -> (3m-1, 2) in T1,
D   -> (2m-1, 2) in T1.
```

All strict and closed EHPS faces hold for every `m>=2`. Therefore

```text
X=(A,B,C) is in W2,
Y=(A,B,B) is in W3,
Z=(A,B,D) is in W3.
```

Since `C=B+u`, `D=B-u`, and `3u=0` modulo `q`, the ordered triples
`(X,Y,Z)`, `(Y,X,Z)`, and `(X,Z,Y)` are all modular midpoint witnesses.
Their potential rows and raw cost numerators are

```text
 +F_W2(X) - 2F_W3(Y) + F_W3(Z) >=   m^2
 -2F_W2(X) + F_W3(Y) + F_W3(Z) >=   m^2
 +F_W2(X) + F_W3(Y) - 2F_W3(Z) >= 4 m^2.
```

The left sides cancel identically and the right sides sum to `6m^2>0`.
After division by `q^2=9m^2`, the contradiction remains exactly `2/3`.
The proof even permits independent potential values for coincident vertices
coming from different cylinders; it therefore also excludes a single global
potential on the union.

This applies in particular at `q=6`, `q=24`, and `q=48`. At `q=24`, the
separate exact mass certificate identifies this same assignment as one of the
two maximum-mass, gate-beating D4 representatives. The present theorem
upgrades that representative's q=24 wall from cylinder-position additivity to
an arbitrary global potential.

## q=6 scope census

The verifier also enumerates all `8^5=32,768` q=6 D4 assignments. Exactly 256
have maximum union mass 3,645. This W2/W3 torsion template hits exactly 128 of
them, and assignment by assignment

```text
a W2/W3 torsion triangle exists
iff
the P2 and P3 supports intersect.
```

The other 128 assignments are merely outside this particular three-row
screen. They are not certified feasible.

An earlier fast sweep reported only 32 covered assignments because it keyed
potential variables by local 2-D points instead of full cylinder vertices.
That result was retracted; the corrected implementation and the independent
replay both recover 128.

## Exact replay

| file | role |
|---|---|
| `verify.py` | symbolic stdlib proof for every `m>=2`, q=6 census, and eight planted corruptions |
| `independent_replay.py` | separately written EHPS/D4/midpoint reconstruction over `q=6,9,...,60` and an independent q=6 census |

Run:

```bash
python3 -I verify.py --self-test
python3 -I independent_replay.py
```

The primary verifier represents every coordinate as an affine polynomial in
`m`. It proves the canonical ranges, strict T1 incidences, inverse D4 maps,
word membership, carries, raw quadratic costs, and coefficient cancellation
for the whole infinite family—not by checking a finite sample. The independent
replay imports no primary or discovery module.

## Boundary

This theorem concerns the actual EHPS modular midpoint predicate and raw
canonical representative cost, but it remains a finite-quotient family. Its
displayed points approach a fundamental-square seam and a strict T1 face at
distance `1/q`; this family alone is not a fixed-point continuum certificate.
It does not classify all D4 assignments, exclude recursive/finite-state
potentials or jointly deformed supports, or supply the superblock-to-integer
transfer.

An ordinary Euclidean midpoint model without `mod 1` is a different problem:
the three-row cycle depends on nonzero 3-torsion and modular carries. EHPS
Proposition 2.2 itself does use the modular predicate and raw canonical cost;
the distinction is recorded to prevent silently changing models.

`continuum_certificate: false`. `erdos142_solved: false`.
`new_r3_bound: false`.

## Provenance

- Terra structural derivation:
  `D:/p42_research/erdos142_five_role_qp_20260817/terra_q6_cycle_structure_20260817/`
- Independent Luna audit:
  `D:/p42_research/erdos142_five_role_qp_20260817/luna_q6_torsion_family_audit_20260817/`
- Primary source for the modular/raw-canonical model:
  [EHPS, Proposition 2.2](https://arxiv.org/html/2406.12290v1#S2.Thmtheorem2)

# q=24 second-orbit cylinder hypograph wall (Erdos #142)

**Finite quotient fence only.** This certificate gives no new `r_3(N)` bound,
does not certify a continuum construction, and does not solve Problem 142.

## Claim

Let `T` be the 163-point EHPS tile on `(Z/24Z)^2`, and number its eight D4
images by the verifier's reflection/reflection/swap convention. For the
second inequivalent maximum-mass assignment

```text
(P1,P2,P3,B,K) = (D4[7],D4[6],D4[7],D4[6],D4[7]),
```

the five Karapetyan cylinders

```text
(P1,K,B), (B,K,P1), (P2,B,P2), (P3,B,B), (B,B,P3)
```

are pairwise disjoint and have exact union mass

```text
5 * 163^3 = 21,653,735 > 4,741,632 = 7^3 * 24^3.
```

Even at that mass, no **cylinder-position additive** potential

```text
F_c(p0,p1,p2) = G[c,0,p0] + G[c,1,p1] + G[c,2,p2]
```

satisfies all raw-Euclidean modular-midpoint coercivity inequalities at
`q=24`. The exact local-hypograph formulation has 2,445 `G` variables and 375
local-minimum variables. Its frozen Farkas certificate contains 816 selected
local rows, all 125 ordered triple-sum rows, and 931 positive multipliers.
Every one of the 2,820 coefficients cancels, leaving the exact contradiction

```text
0 <= -443949403946578587181096256508988953271196473677423811533138374068397125657555935076136756882041128041806593419991607851044352.
```

The verifier also exhaustively recomputes all `8^5=32,768` D4 assignments.
Exactly 16 attain the maximum mass `21,653,735`; they split into two disjoint
eight-member D4/word-symmetry orbits represented by `(7,7,7,6,7)` and
`(7,6,7,6,7)`. This certificate closes the second orbit. Together with the
separate first-orbit certificate in
`certificates/erdos-142-q24-cylinder-hypograph-wall/`, every maximum-mass D4
assignment is excluded under this cylinder-position additive model.

## Files and replay

| file | role |
|---|---|
| `certificate.json` | compact semantic Farkas packet |
| `verify.py` | stdlib semantic verifier, maximum-mass/orbit census, and eight planted corruptions |
| `independent_replay.py` | separately written stdlib reconstruction and exact cancellation audit |

Expected packet SHA-256:

```text
ab7f047034cd9287ece048ca56b78f2f1d32f2e2c2e102ae3b10ab05523a1e29
```

Replay:

```bash
python3 -I verify.py --self-test
python3 -I independent_replay.py --self-test
# PASS_Q24_D4_SECOND_ORBIT_CYLINDER_HYPOGRAPH_EXACT_FARKAS
# PASS_INDEPENDENT_Q24_D4_SECOND_ORBIT_REPLAY
```

## Scope boundary

This wall covers exactly the finite `q=24` D4 family and potentials separable
by cylinder and physical coordinate. It does **not** exclude pair-coordinate
interactions, an arbitrary potential on each six-dimensional cylinder,
recursive-state potentials, support deformations, a `q=48` survivor, or a
continuum thickening. The low-`q` arbitrary-global screens are numerical
experiments, not part of this exact claim.

`erdos142_solved: false`. `new_r3_bound: false`.

## Discovery provenance

- Terra scratch: `D:/p42_research/erdos142_five_role_qp_20260817/terra_second_d4_orbit/`
- Independent Luna replay: `D:/p42_research/erdos142_five_role_qp_20260817/luna_global_potential_q6/independent_replay.py`

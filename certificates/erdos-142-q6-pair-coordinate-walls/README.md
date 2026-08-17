# q=6 pair-coordinate Farkas walls (Erdos #142)

**Finite quotient fence only.** These certificates give no new `r_3(N)`
bound, do not certify a continuum construction, and do not solve Problem 142.

## Claim

On the `q=6`, `epsilon=1/6` EHPS tile, consider the five Karapetyan product
cylinders and either of the two D4 assignments

```text
A = (P1,P2,P3,B,K) = (7,7,7,6,7),
B = (P1,P2,P3,B,K) = (7,6,7,6,7).
```

Each local D4 support has 9 points and `D4[6]` is disjoint from `D4[7]`.
For both assignments the five cylinders are pairwise disjoint, so their exact
union count is

```text
5 * 9^3 = 3,645.
```

The normalized mass is `3645/6^6 = 5/64`, and it passes the finite EHPS gate
by the exact ratio

```text
(5/64) / (7/24)^3 = 1080/343 > 1.
```

Give every cylinder its own three pair-coordinate tables and set

```text
F_c(p0,p1,p2)
  = H[c,01,p0,p1] + H[c,02,p0,p2] + H[c,12,p1,p2].
```

There are `5 * 3 * 9^2 = 1,215` real variables. This ansatz permits genuine
two-coordinate interactions and strictly contains the cylinder-position
additive model at the same quotient.

Neither assignment admits such a potential satisfying all raw-Euclidean
modular-midpoint coercivity inequalities. The exact semantic packets contain
positive integer Farkas combinations of actual six-dimensional witnesses:

| representative | selected rows | exact conclusion |
|---|---:|---|
| A `(7,7,7,6,7)` | 1,067 | all 1,215 coefficients cancel and the summed raw cost is positive |
| B `(7,6,7,6,7)` | 1,071 | all 1,215 coefficients cancel and the summed raw cost is positive |

Every selected row records the three local midpoint witnesses, including the
even-`q` branch, carry, support membership, raw canonical endpoint cost, and
the resulting nine pair-table coefficients. A nonnegative combination with
zero potential coefficients and positive right side is the contradiction
`0 >= positive_integer`.

## Files and replay

| file | role |
|---|---|
| `certificate_A.json` | compact semantic Farkas packet for A |
| `certificate_B.json` | compact semantic Farkas packet for B |
| `verify.py` | stdlib semantic verifier, exact mass check, and 16 planted corruptions |
| `independent_replay.py` | separately written stdlib reconstruction and exact cancellation audit |

Packet SHA-256 values:

```text
certificate_A.json  46dea1b400fe3c7a43f7b6b48107e2f4858ec62661bef026c3e08182587a2f6e
certificate_B.json  6a504e00146d97da7e83e6d77bf37c26cd47a7493d998096236f0212a035f7af
```

Replay:

```bash
python3 -I verify.py --self-test
python3 -I independent_replay.py
# PASS_Q6_PAIR_COORDINATE_EXACT_FARKAS_WALLS
# PASS_INDEPENDENT_Q6_PAIR_COORDINATE_REPLAY
```

## Scope boundary

This excludes exactly the two named finite `q=6` support assignments under
the pair-coordinate ansatz. It does **not** transfer the wall to `q=24` or
`q=48`, exclude an arbitrary potential on each six-dimensional cylinder,
exclude recursive/finite-state potentials, cover jointly deformed supports,
or supply a continuum thickening or integer transfer. The two `q=6` packets
are not an unproved orbit extrapolation.

`erdos142_solved: false`. `new_r3_bound: false`.

## Discovery provenance

- Terra accelerator and exact kernels: `D:/p42_research/erdos142_five_role_qp_20260817/terra_pair_q6_accelerated/`
- Independent Luna audit: `D:/p42_research/erdos142_five_role_qp_20260817/luna_global_potential_q6/pair_independent_replay.py`

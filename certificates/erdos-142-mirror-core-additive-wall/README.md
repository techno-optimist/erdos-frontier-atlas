# Exact q=24 mirror-exclusive additive wall

This packet closes one concrete mass-beating branch of the five-role signed-slack
program.

Let `T` be the EHPS grid support at `q=24`, `epsilon=1/24`, and let `Tt` be
its coordinate transpose.  The exact census is

```text
|T| = |Tt| = 163
|T intersect Tt| = 53
|T without Tt| = |Tt without T| = 110
```

Keep only the two Karapetyan words

```text
(P3,B,B) and (B,B,P3).
```

For either role orientation, put the 110-point exclusive core of one tile in
`B` and the exclusive core of the other in `P3`.  There is no additive
role-potential assignment satisfying all q=24 raw-Euclidean midpoint rows.
`certificate.json` contains an exact nonnegative Farkas combination:

- 177 rows for `B=T\Tt`, `P3=Tt\T`;
- 174 rows for the reversed orientation;
- every potential coefficient cancels exactly;
- the summed raw endpoint cost is strictly positive.

Therefore every disjoint allocation of any of the 53 intersection points is
also infeasible: all certificate rows use only exclusive-core points and remain
present under support enlargement.  If `k` intersection points are assigned to
`B`, the two-cylinder mass is

```text
2 (110+k)^2 (163-k) / 24^6.
```

It exceeds `(7/24)^3` exactly for `18 <= k <= 53`.  Hence the certificate
rules out every mass-beating disjoint intersection allocation in both natural
role orientations, not merely the 199 sampled partitions from the discovery
sweep.

Replay from this directory with a standard-library Python:

```powershell
python -I verify.py
```

Expected first line:

```text
PASS_MIRROR_EXCLUSIVE_ADDITIVE_WALL
```

The verifier reconstructs the EHPS support from exact integer inequalities,
checks every modular midpoint/carry/raw cost, sums the Farkas rows using Python
integers, checks the allocation mass range, and runs four planted-failure
controls.

An independently written compact replay reconstructs the same sparse rows from
binary witness records, performs exact `Fraction` RREF, and derives the primitive
positive Farkas ray rather than trusting the multipliers in `certificate.json`:

```powershell
python -I replay_core_wall.py
```

Its exact constraint hashes are
`d8b61837bd09bde420e15c3e7df617df6486073397e3129a652e218826e67da0`
and
`cf358139a34a80dd79906f8fb28899f0d804b1cf071161b35e3bb0228bbb1b88`
for the two role orientations.

SHA-256:

```text
certificate.json  3022C3405B4F764091E9D0FD512E892C55910407B2174F82A6D8CAF34D3D290F
verify.py         A611AD437C66091BE729E75ABA7F1D0FCDF41F6DBBF4F81C160D75B5A6B68BAF
replay_core_wall.py AE8F059159A159BED6F10E5E1CB0EA55DEF1183AC15DD6E1712D34EC148C7D29
base_to_swap.witnesses.bin ED8BF693B7CC4905682D6A42F113405E16E5BBFA99DBB15E60F564A25C25DCC4
swap_to_base.witnesses.bin 91F978FEFC26E9D8907A36338FA0474BC8F63CEA29A087A38BFE5BABA9EFE940
```

## Boundary

This is a finite `q=24` wall for the **additive role-potential ansatz** on the
two displayed product cylinders.  It does not rule out:

- an arbitrary non-additive potential on the full six-dimensional union;
- globally deformed supports not containing these exclusive cores;
- other five-word role assignments or recursive outer codes;
- a continuum construction.

It gives no new `r_3(N)` bound and does not solve Erdős Problem 142.

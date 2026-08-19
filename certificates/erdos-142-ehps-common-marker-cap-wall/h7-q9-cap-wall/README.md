# h=7 marker boundary: exact AG(2,3) classification and q=9 plane loss

This scratch-only package closes the target-36 finite section that remained at
the `h=7` common-marker boundary.  No Atlas or PR files are edited.

There are two different conclusions about the proposed q=9 square packet:

1. **Invertible affine copies of the 34-active-point square packet do not
   suffice.**  An explicit 36-box selector saturates four points in every
   `H_3^2` fibre while avoiding all 314,928 such placements.
2. **The valid affine-endomorphism closure does suffice.**  Singular
   projections of the square packet give every six-point `2+2+2` subset of a
   primitive q=9 affine line.  A much smaller direct six-row certificate proves
   the same obstructions.  An exact standard-library exhaustion shows that no
   36-box cap selector can avoid all of them.

Consequently an arbitrary measurable physical plane slice carrying a
pointwise coercive single-valued potential has measure at most `35/81`, not
merely `4/9`.  Inserted into the existing exceptional-plane Fubini argument,
this closes the literal common-marker `h=7` gate for
`0 <= epsilon <= 1/20000`.

## 1. Complete classification of four-caps in AG(2,3)

There are exactly 54 four-point caps in `F_3^2`.  For a cap `C`, put

```text
c = sum_(x in C) x.
```

Then `c` is not in `C`, and the four vertices pair antipodally about `c`:

```text
C = {c+v,c-v,c+w,c-w}
```

for two distinct projective directions `v,w`.  Conversely every such choice
is a cap.  Hence there are

```text
9 anchors * choose(4 projective directions,2) = 54
```

caps, six at each anchor.  The replay also enumerates all 432 elements of
`AGL(2,3)` and verifies that these 54 caps form one orbit.  Every point lies
in 24 of them.

The old double-plane count is combinatorially sharp.  In two perpendicular
`F_3^2` planes in `F_3^4`, take the anchored cap

```text
{+/- (1,0), +/- (0,1)}
```

in each plane.  The planes' intersection is omitted and their union is an
eight-point cap.  Thus torsion-cap classification alone cannot replace the
old double-hit contribution `8` by `7`.

## 2. Exact audit of the 34-row q=9 square packet

The supplied packet lives on the 6-by-6 digit ledger

```text
K={0,1,2,3,4,5}^2 subset (Z/9Z)^2.
```

Its 34 positive integer-weight rows are frozen in `verify.py`.  The replay
checks every midpoint congruence and raw cost, exact potential-incidence
cancellation, and weighted raw-cost sum

```text
403824960.
```

Only 34 of the 36 ledger vertices are active: `(3,4)` and `(4,4)` have zero
incidence and do not occur in a row.

The warning about arbitrary measurable selectors is real.  Write every digit
uniquely as

```text
d=r+3h,       r,h in F_3^2.
```

Choose in residue fibre `r=(0,0)` the cap

```text
C_A={+/-(1,0), +/-(0,1)},
```

and in the other eight fibres choose

```text
C_B={+/-(1,0), +/-(1,1)}.
```

The resulting selector has 36 q=9 boxes and exactly one four-cap in every
`H_3^2` fibre.  It uses two different direction-pair types.  Exhaustion of
all 3,888 matrices in `GL(2,Z/9Z)` and all 81 translations proves that none
of the 314,928 invertible affine images of the active square support is
contained in this selector.

So one may normalize a four-cap **inside one fibre**, but one may not use
nine unrelated fibrewise normalizations as one physical affine map.  The
invertible square orbit yields no universal loss beyond `4/9`.

## 3. The decisive six-row scalar packet

On the scalar support `S={0,1,2,3,4,5} subset Z/9Z`, use these rows.  The
middle entry is the torus midpoint.

| weight | x | y | z | raw cost `(x-z)^2` |
| ---: | ---: | ---: | ---: | ---: |
| 3 | 4 | 0 | 5 | 1 |
| 2 | 0 | 1 | 2 | 4 |
| 1 | 0 | 2 | 4 | 16 |
| 1 | 1 | 3 | 5 | 16 |
| 2 | 3 | 4 | 5 | 4 |
| 3 | 0 | 5 | 1 | 1 |

The coefficient of every scalar potential value is zero, all weights are
positive, and the weighted raw right side is

```text
3+8+16+16+8+3 = 54 > 0.                         (1)
```

The affine scalar orbit

```text
aS+b,       a in (Z/9Z)^x, b in Z/9Z
```

has exactly 27 distinct supports.  They are precisely all choices of two
digits from each residue class modulo 3, since both families have size
`choose(3,2)^3=27` and the replay checks equality.

Embed (1) along a primitive affine line in `(Z/9Z)^2`.  The line has nine
points, three over each of its three mod-3 residues.  Every `2+2+2` subset is
therefore a positive balanced physical packet.  There are exactly

```text
12 primitive directions * 9 affine lines per direction * 27 patterns
  = 2916 six-point packets.                                  (2)
```

For provenance, the replay independently pushes the original 34-row square
packet through every affine endomorphism with six-point image.  It obtains
exactly the same 2,916 supports and verifies coefficient cancellation and a
positive physical endpoint-cost sum after every merge.  The direct six-row
packet is the cleaner proof; the square projection is a fully exact
cross-check.

## 4. Solver-independent target-36 exhaustion

A 36-point q=9 section satisfying the order-three condition must choose one
of the 54 four-caps in each of its nine residue fibres.  Primitive q=9 lines
come in 12 base `AG(2,3)` lines, with nine lifts above each base line.  A
completed triple of residue fibres is rejected exactly when one lifted line
contains two chosen points in each fibre, equivalently when it contains one
of (2).

The replay performs a complete constraint search over these nine cap choices:

- all 54 cap domains are reconstructed, not loaded from a solver;
- one residue-zero cap is normalized to `C_A` without loss of generality;
- for every one of the 54 possible original caps, an explicit lifted affine
  normalizer is found and checked to permute all 2,916 packet supports;
- whenever two vertices of a base line have been assigned, the exact domain
  of its third cap is intersected with the compatible values;
- a minimum-domain recursive enumeration visits 716,176 nodes and reaches no
  complete assignment.

This is standard-library integer/set arithmetic.  It calls no LP, MILP, SAT,
SMT, or floating-point solver.  Thus

```text
every cap-valid q=9 section with 36 selected digits contains a certified
six-point positive balanced packet.                              (3)
```

As a nonvacuity check, the replay verifies an explicit 34-point set that is
cap-valid and avoids all 2,916 packets.  The capacity of just this finite
cap-plus-six-packet hypergraph is therefore either 34 or 35; target 35 is not
decided here and is unnecessary for the measure bound.

## 5. Arbitrary measurable selector: common-offset Fubini

Let `E subset (R/Z)^2` be measurable and suppose a single-valued physical
function on `E` obeys the pointwise torus-midpoint coercivity inequality with
any positive endpoint cost.  For `u in [0,1)^2`, define

```text
p_d(u)=(d+u)/9,
S(u)={d in (Z/9Z)^2 : p_d(u) in E}.
```

The 81 maps `u -> p_d(u)` use the half-open q=9 boxes and give the exact
identity

```text
mu(E) = (1/81) integral |S(u)| du.                    (4)
```

Order-three cyclic inequalities imply that every mod-3 fibre of `S(u)` is a
cap, hence has at most four points.  If `|S(u)|=36`, all nine fibres are
four-caps and (3) supplies a six-point packet.  Lifting its six rows with the
same `u` preserves every torus midpoint identity.  Potential values cancel
and a positive endpoint-cost sum remains, a contradiction.  Therefore,
pointwise in the common offset,

```text
|S(u)| <= 35.
```

Equation (4) proves the genuine arbitrary-measurable plane bound

```text
mu(E) <= 35/81.                                      (5)
```

No claim that a selector contains the full 6-by-6 square is used.

## 6. Consequence for the literal common-marker h=7 lane

In the existing exceptional-set geometry, `mu(E_0)=1/72`, and every
`H_3^2` orbit meets `E_0` at most once.  Restricting an arbitrary global
phase-labelled physical potential to one exceptional marker plane gives the
two-dimensional hypothesis of (5): all other blocks are held identical.
Using the union bound over the two factor planes gives

```text
mu(M intersect K_0)
  <= 2*(1/72)*(35/81)
   = 35/2916.                                         (6)
```

At `epsilon=0`, the necessary `h=7` marker gate is

```text
(7/24)^2/7 = 7/576,
```

and the exact margin over (6) is

```text
7/576 - 35/2916 = 7/46656 > 0.                       (7)
```

For positive epsilon, retain the earlier full payment for the thin strip

```text
sigma=4 epsilon/3-2 epsilon^2.
```

The marker bound becomes `35/2916+2 sigma`, and exact subtraction from
`(7/24-epsilon)^2/7` is

```text
7/46656 - 11 epsilon/4 + 29 epsilon^2/7.              (8)
```

Expression (8) is decreasing on `[0,1/20000]` and at the right endpoint is

```text
25606141/2041200000000 > 0.
```

Thus, within the literal EHPS `A,B`, common-marker, pointwise physical model
of the existing marker wall, `h=7` is closed for
`0 <= epsilon <= 1/20000`.

## 7. Scope

Proved: the exact 54-cap classification; sharpness of the old double-plane
torsion count; failure of the invertible square orbit; exact validity and
coverage of the six-point projected packets; target-36 infeasibility; the
arbitrary-measurable `35/81` plane bound; and the resulting common-marker
`h=7` density wall in the stated epsilon window.

Not proved: target-35 infeasibility; feasibility of the displayed 34-set for
all physical midpoint inequalities; phase-specific markers; arbitrary graph
or context-owned constructions; an EHPS shell or integer transfer; an
improved `r_3(N)` lower bound; or Erdős Problem 142.

## 8. Replay

From this directory:

```powershell
.\run.ps1
```

or directly:

```powershell
python -I verify.py
```

The success marker is

```text
PASS_H7_Q9_CAP_AUDIT
```

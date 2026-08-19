# Literal EHPS common-marker cap wall for h=4,5,6,7

This companion theorem closes the remaining common-marker window in the
literal Hametner--Tyrrell-style phase chain built from the EHPS tile. It
allows an arbitrary phase-labelled global potential; it is not an additive
or fixed-form ansatz.

## Exact theorem

Let `T=T_epsilon` be the literal two-dimensional EHPS tile, put

```text
A=T x T,                 B=L(A),
L(u,v)=(u+v,u+2v),
P_j=A^(j-1) x M x B^(h-j),       1<=j<=h,
```

and use the same measurable marker `M subset (R/Z)^4` in every phase. Allow
a separate real value at each phase-labelled physical word and assume the
pointwise torus-midpoint coercive inequality with any positive multiple of
intrinsic squared geodesic endpoint distance. For
`0<epsilon<=1/4000`, every such marker satisfies

```text
mu(M) <= B(epsilon)
      := 1/81 + 2(4epsilon/3-2epsilon^2).
```

Since `mu(T)>=7/24-epsilon`, this upper bound is strictly below
`mu(T)^2/h` for `h=4,5,6`. Even the sum of phase volumes therefore cannot
beat the direct product `A^h`.

For `h=7`, the q=9 plane packet in `h7-q9-cap-wall/` sharpens the triangular
part and gives

```text
mu(M) <= 35/2916+2(4epsilon/3-2epsilon^2) < mu(T)^2/7
```

for `0<=epsilon<=1/20000`.

## Coverage dichotomy and same-phase caps

Let

```text
C_T=union_(tau in H_2^2)(T-tau),
C_A=C_T x C_T,            C_B=L(C_A).
```

The exact eight-row whole-word cycle for phases `j,j+2` uses one marker point
in `C_A` and a possibly different marker point in `C_B`. It retains every
marker/filler `x=z` branch, cancels all eight phase-labelled physical values,
and has total intrinsic endpoint cost `4/3` (raw canonical cost `8/3`). Thus
a surviving common marker lies wholly in `C_A^c` or wholly in `C_B^c`.

Independently, three marker points on an affine line in one `H_3^4` fibre,
with identical `A/B` fillers, form a same-phase cyclic midpoint packet with
positive cost. Hence every marker fibre is a cap in `AG(4,3)`.

## Fibre measure bound

After folding by `H_2^2`, the complement of `C_T` is, up to null boundaries,

```text
E_0={x+y>11/12},                 mu(E_0)=1/72,
S_e={2/3<x+y<2/3+epsilon},       mu(S_e)=4epsilon/3-2epsilon^2.
```

Every `H_3^2` fibre meets `E_0` at most once. Therefore an `H_3^4` fibre of
`(E_0 x Torus^2) union (Torus^2 x E_0)` is at most two intersecting affine
`F_3^2` planes. A cap uses at most four points per plane. The hit probability
for either factor is `9/72=1/8`, so finite-group Fubini gives mass at most
`4(1/8+1/8)/81=1/81` on this triangular part. Paying the full two-factor
strip remainder costs at most `2 mu(S_e)` and proves the displayed bound.
The determinant-one map `L` preserves measure and permutes the relevant
torsion fibres, so the `C_B^c` branch is identical.

Exact subtraction gives the positive gaps

```text
h=4: (88128e^2-58320e+185)/20736,
h=5: (108864e^2-72144e+121)/25920,
h=6: (43200e^2-28656e+19)/10368.
```

Each numerator decreases but remains positive through `e=1/4000`. At
`epsilon=0`, this screen first becomes inconclusive at `h=7`, with excess
window `7/5184`; the following q=9 argument supplies the extra h=7 loss.

## The q=9 h=7 sharpening

Every measurable exceptional two-dimensional marker plane carrying the
restricted pointwise physical potential has measure at most `35/81`. The
exact q=9 replay classifies all 54 four-caps in `AG(2,3)`, constructs 2,916
six-point positive balanced line packets, and performs a solver-free
716,176-node exhaustion proving that no 36-digit cap selector avoids them.
Common-offset Fubini therefore gives the plane bound. Applying it to the two
exceptional factor planes replaces `1/81` by `35/2916`; the remaining exact
h=7 density gap is

```text
7/46656-11epsilon/4+29epsilon^2/7 > 0
```

through `epsilon=1/20000`. The same replay also exhibits the 36-box selector
showing why invertible copies of the earlier square packet alone do not
suffice. Target 35 is not decided or needed.

The independent replay replaces the search by a counting cover: every
four-cap has exactly two rich directions, so nine fibres force 18 rich
incidences while packet avoidance permits at most 12.

For the `C_B^c` branch, `L` is a Haar-preserving torus automorphism that
preserves the `H_9/H_3` cosets and nontrivial midpoint rows. The finite packet
only needs a positive right side, so the entire h=7 bound transports through
`L`; no metric invariance is assumed.

## Portable replays

Windows:

```powershell
python -I certificates\erdos-142-ehps-common-marker-cap-wall\verify.py
python -I certificates\erdos-142-ehps-common-marker-cap-wall\independent_replay.py
python -I certificates\erdos-142-ehps-common-marker-cap-wall\h7-q9-cap-wall\verify.py
python -I certificates\erdos-142-ehps-common-marker-cap-wall\h7-q9-cap-wall\independent_replay.py
```

Linux or WSL:

```text
python3 -I certificates/erdos-142-ehps-common-marker-cap-wall/verify.py
python3 -I certificates/erdos-142-ehps-common-marker-cap-wall/independent_replay.py
python3 -I certificates/erdos-142-ehps-common-marker-cap-wall/h7-q9-cap-wall/verify.py
python3 -I certificates/erdos-142-ehps-common-marker-cap-wall/h7-q9-cap-wall/independent_replay.py
```

The primary standard-library replay verifies the full eight-row cycle across
all half-period filler shifts, phase-labelled deduplication, raw and geodesic
costs, the same-phase torsion packet, affine cap extremum, Fubini
normalization, `L` symmetry, and exact density polynomials. The independently
written bit-mask replay separately derives the folded coverage intervals,
cap and plane-union bounds, normalization, and density arithmetic.

Expected verdicts are `PASS_LITERAL_EHPS_COMMON_MARKER_H4_CAP_WALL` and
`PASS_INDEPENDENT_COMMON_MARKER_H4_WALL`; the h=7 primary verdict is
`PASS_H7_Q9_CAP_AUDIT`, and its independent verdict is
`PASS_Q9_H7_CAP_WALL_INDEPENDENT`.

## Scope

This is only the literal `A,B` chain with one common marker and a pointwise
phase-labelled potential. It does not cover phase-specific markers
`M_1,...,M_h`, context-owned/carved `A` or `B` pieces, other graph languages,
target-35 q=9 infeasibility, an almost-everywhere hypothesis, a new physical
construction, EHPS integer transfer, a new `r_3(N)` bound, or Erdős Problem
142.

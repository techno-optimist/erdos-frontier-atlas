# q=4 affine-order-4 line wall

This packet gives a structural, exact replacement for the 32 independently
extracted q=4 LP rays in `lead_quotient_frontier_20260817`.  Every maximum-mass
q=4 union contains an affine copy of `Z/4Z`; four unit-weight midpoint rows on
that line cancel every value of an arbitrary global potential and leave a
strictly positive cost.

Run:

```text
python -I verify.py --self-test
python -I independent_replay.py
```

`verify.py` is the primary theorem replay.  It is self-contained, stdlib-only,
and uses integer and `Fraction` arithmetic.  It does not import the numerical
classifier, the dual extractor, SciPy, SymPy, or any stored ray.

`independent_replay.py` is a separately written, self-contained structural
replay.  It imports neither the primary verifier nor discovery data and
reconstructs the support, mass census, symmetry orbits, affine lines, four
midpoint rows, carries, raw costs, coefficient cancellation, and eight live
failure controls from the definitions.

## Exact q=4 support and mass classification

At `q=4` and `epsilon=1/q`, the published EHPS support inequalities give

```text
T = {(2,1), (2,2), (3,0), (3,1)}.
```

All four points lie in `T1`.  The eight D4 images of `T` are distinct.  For
each of the `8^5=32768` assignments of images to `(P1,P2,P3,B,K)`, the replay
forms the five physical cylinders

```text
0=(P1,K,B), 1=(B,K,P1), 2=(P2,B,P2),
3=(P3,B,B), 4=(B,B,P3).
```

One cylinder contains `4^3=64` vertices.  The exact maximum union mass is

```text
320 = 5*64,
```

attained by exactly 256 assignments.  Equality with the sum of the cylinder
sizes is also checked pairwise: all five cylinders are disjoint for every
maximizer.  Thus the arbitrary global potential has exactly 320 physical
variables; no cylinder-occurrence relaxation is being used.

The maximizers form 32 global-D4 orbits of size eight.  With `P1` normalized
to image zero, the 32 representatives have the compact exact normal form

```text
(P1,P2,P3,B,K) = (0, p2, p3, b, k),
p2 in {0,1,2,3}, p3 in {0,2}, b in {1,3}, k in {0,2}.
```

The maximum density and candidate mass comparison are

```text
320/4^6 = 5/64,
(5/64) / (7/24)^3 = 1080/343,
5/64 - (7/24)^3 = 737/13824 > 0.
```

The `(7/24)^3` gate is an external input from the home capacity lane.  This
packet certifies the quotient support, mass, ratio, and margin exactly.

## Universal four-row lemma

Let `A0,A1,A2,A3` be a full affine order-four line in `(Z/4Z)^6`:

```text
Aj = A0 + j*d (mod 4),
```

where `d` has at least one odd coordinate.  Then all four points are distinct,
and the following four ordered triples satisfy the modular midpoint equation:

```text
(A0,A1,A2),
(A0,A3,A2),
(A1,A0,A3),
(A1,A2,A3).
```

Indeed, `A0+A2=2A1=2A3` and `A1+A3=2A0=2A2` modulo four.  For any single
global potential `H` on a set containing the line, its four coercive rows are

```text
 H(A0) - 2H(A1) + H(A2) >= ||A0-A2||^2_raw
 H(A0) - 2H(A3) + H(A2) >= ||A0-A2||^2_raw
-2H(A0) + H(A1) + H(A3) >= ||A1-A3||^2_raw
 H(A1) - 2H(A2) + H(A3) >= ||A1-A3||^2_raw.
```

Every coefficient cancels with unit row multipliers.  The exact residual is

```text
0 >= 2||A0-A2||^2_raw + 2||A1-A3||^2_raw > 0.
```

The strict inequality follows because opposite points of an order-four line
are distinct.  Division by `q^2=16` gives the normalized convention and does
not change infeasibility.  This is a four-point torsion wall, not an LP
approximation.

The q=6 three-row triangle has no nonconstant analogue at q=4: since three is
invertible modulo four, satisfying all three cyclic midpoint equations forces
the three vertices to be equal.  The affine `Z/4Z` line is the corresponding
four-row mechanism.

## Exhaustive structural coverage

For each of the 32 orbit representatives, `verify.py` exhaustively searches
the 320-point physical union for affine order-four lines.  Every representative
contains between 136 and 160 unoriented lines; the total over the 32
representatives is 4736.  It certifies one deterministic line per orbit and
then applies all eight global D4 transports.  The transported assignment set
is checked to equal the complete 256-element maximizer set.

Each transported certificate rechecks:

- membership of every line point in exactly one physical cylinder;
- the affine order-four identity;
- all four modular midpoint equations and exact integer carry vectors;
- raw canonical endpoint costs;
- full 320-variable coefficient cancellation;
- strictly positive contradiction.

The selected structural certificates have raw contradiction 16 through 64,
or normalized contradiction 1 through 4.  Positivity, rather than its size,
is the wall.

Eight planted corruptions are rejected: wrong midpoint, wrong raw cost,
order-two rather than order-four step, missing fourth row, occurrence-labelled
variables, a nonmaximum assignment, import of the q=6 three-row mechanism, and
reversal of the exact mass margin.

## Independent structural replay

The separately written replay repeats the complete `8^5` mass census and
32-orbit decomposition, exhausts the affine order-four lines in each orbit,
and transports a deterministic line certificate to all 256 maximizers.  It
uses full physical union vertices as potential-variable keys and checks all
four modular midpoint equations, carries, endpoint costs, and cancellation.
Its independent line-count digest agrees with the primary replay.  Eight live
corruptions are rejected, including a missing fourth row, occurrence-label
aliasing, an order-two step, and substitution of the q=6 three-row mechanism.

## Honest boundary

This is an exact wall for the finite q=4 maximum-mass D4 full-cylinder unions.
It permits a completely arbitrary, nonseparable real-valued global potential
on the physical union.  It does not cover geometric deformation or thickening
of the supports, a continuum limit, correlated subcylinders, scalar digit
encoding with cross-block carries, or the construction-to-integers transfer.

The line witnesses may use quotient boundary points, so no deformation claim
is inferred from the finite grid.  No new bound for `r_3(N)` is claimed, and
this packet does not solve Erdős Problem 142.  It closes the exact maximum-mass
q=4 arbitrary-global-potential lane.

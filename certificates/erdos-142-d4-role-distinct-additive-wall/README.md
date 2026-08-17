# Exact q=24 top-D4 role-distinct additive wall

This packet closes the highest-mass candidate in the finite `q=24` D4
five-role sweep under the **role-distinct additive-potential** model.

Let `T` be the EHPS `q=24`, `epsilon=1/24` grid tile, and number its eight
dihedral images by reflecting the first coordinate (bit 0), reflecting the
second coordinate (bit 1), then swapping coordinates (bit 2).  Fix

```text
(P1,P2,P3,B,K) = (D4[7],D4[7],D4[7],D4[6],D4[7])
```

and the five Karapetyan word cylinders

```text
(P1,K,B), (B,K,P1), (P2,B,P2), (P3,B,B), (B,B,P3).
```

The two D4 supports are disjoint, so the five cylinders are pairwise
disjoint.  Exact inclusion-exclusion gives

```text
union count    = 21,653,735
ambient count  = 24^6 = 191,102,976
EHPS gate      = (7/24)^3, or 4,741,632 grid points
```

Thus this is a genuine mass-beating finite candidate.  Give each occurrence
of a grid point in each of the five roles its own potential variable: there
are `5*163 = 815` role-point variables.  The certificate supplies 622 valid
modular-midpoint inequalities with positive integer multipliers.  Every
potential coefficient cancels exactly, while the summed raw endpoint cost is
the strictly positive integer recorded in `certificate.json`.  Their sum is
therefore the contradiction `0 >= positive_integer`.

Each selected row carries its ordered word triple and three local witnesses.
The standard-library verifier independently reconstructs the EHPS tile, D4
images, role-distinct variable map, all midpoint congruences and canonical
carries, raw `[0,1)` endpoint costs, the five-cylinder mass, and the exact
Farkas cancellation.  It also checks the SHA-256-pinned 3,427-row discovery
ledger and runs six planted corruptions.

Replay:

```text
python3 -I verify.py --self-test
python3 -I independent_replay.py
python3 -I mass_screen.py
```

Expected verdicts:

```text
PASS_Q24_D4_ROLE_DISTINCT_ADDITIVE_WALL
PASS_INDEPENDENT_Q24_D4_ROLE_DISTINCT_REPLAY
PASS_Q24_D4_MASS_SCREEN
```

## Boundary

This is a finite `q=24` no-go for exactly the displayed five-word D4 support
assignment and a sum of role-local potentials.  It does **not** exclude:

- an arbitrary non-additive potential on the full six-dimensional union;
- recursive or finite-state potentials coupling multiple blocks;
- jointly deformed supports outside this D4 family;
- a `q=48` or continuum construction.

It gives no new `r_3(N)` bound and does not solve Erdős Problem 142.

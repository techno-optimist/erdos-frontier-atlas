# q=6/M7 continuous cell-specific offset wall

This packet is an Atlas certificate lane for the exact q=6/M7
continuous restricted-ansatz obstruction found by Terra and independently
replayed by Luna. It is deliberately a wall for one potential class, not a
claim that Erdős Problem 142 is solved.

## What is certified

The frozen certificate contains 358 positive integer Farkas records. Each
record is a selected three-row midpoint/coercivity witness on the q=6
half-open box model. The state space has 24 selected `(word,residue)` cells
and 148 `(cell, six-bit parity pattern)` states. The local cost is the exact
3-scaled supremum obtained from the half-open residual interval
`xi+zeta-2*eta in (-2,2)`.

The rows have coefficients `(+1,-2,+1)` on

```text
H = 2*||x||^2 + G(cell,pattern) + sum_i U(cell,i,coarsepoint_i).
```

The q=6 local supports reconstructed by both replays are
`S0={(3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2)}` and
`S1={(5-x,y):(x,y) in S0}`. The 24 selected `(word,residue)` cells are

```text
r=0: 15,30,46,51,53,57       r=1: 15,54,57
r=2: 7,56                    r=3: 3,60
r=4: 7,56                    r=5: 12,17,34
r=6: 3,12,17,18,36,40
```

Here `word` is a six-bit support word and `residue` is the exact no-wrap sum
of the six local parity bits. All coordinates are six-scaled coarse vertices
inside half-open `1/6` boxes; the packet does not silently replace these with
mod-4 residues or closed boxes.

The primary replay reconstructs every support, parity, residual cost, state
coefficient, and cell-local `U` coefficient. All state coefficients and all
cell-local `U` coefficients cancel exactly, while the weighted raw right side
is the positive integer

```text
154549018277281375201164147325396656959271726533395814727855110893018977959197745379570260517107780.
```

Therefore no real-valued potential in exactly this ansatz can satisfy all
selected coercivity inequalities for this finite q=6/M7 support model.

## Scope boundary

This is only an exact obstruction for the displayed ansatz
`H=2||x||^2+G(cell,pattern)+sum_i U(cell,i,coarsepoint_i)`. It does **not**
obstruct an arbitrary physical potential, a general global quadratic
correction, a different or richer piecewise potential, or a recursive-state
potential. The independent audit explicitly finds 946 nonzero unrestricted
physical-vertex aggregates and 60 nonzero integer-coordinate quadratic
aggregates; those are scope tripwires, not extra claims.

It does not prove nonexistence of a potential on the continuum support in
general, does not provide an integer transfer, does not provide an `r_3(N)`
lower bound, and does not solve Erdős Problem 142. It also does not by itself
add a capacity theorem: the candidate's support/mass accounting is separate
from this ansatz wall.

## Replays

Only the Python standard library is used. Run from this directory:

```text
python3 -I verify.py
python3 -I independent_replay.py
```

Expected final lines are `PASS_Q6_M7_CELLU_RESTRICTED_WALL` and
`PASS_INDEPENDENT_CELLU_AUDIT`. Both replays contain planted-failure controls
for a right-hand side, local point, state id, and multiplier mutation; all
four mutations must be rejected. The independent replay also verifies the
committed `audit_report.json`, whose exact report records the nonzero
unrestricted aggregates and the planted-control result; replay is read-only.

No replay imports the Terra discovery code, a sibling certificate, NumPy, an
LP/MIP solver, or any other third-party package. The semantic certificate is
self-contained; the discovery master and CEGAR source are retained only as
hash-pinned provenance inputs below.

## Artifact and provenance hashes

SHA-256 hashes are uppercase and refer to the packet bytes unless a
source path is explicitly labelled provenance.

```text
certificate.json       FA9BDCBFF7463DF3729696B2E8F26A82FDC51A9A215E95E618E9C25432BDF087
verify.py              A1B558B5B3FED7C6FD2E7DAC51D937916B7486FE3D8753011A0713F851B0A5BC
independent_replay.py 954DDC72499A69F23513D1AA19872695FC7FC24753F133C3D903A05A57029AE1
audit_report.json      97C30C118465D076FB444DA78D067E6B16090D3521E469AF02B60E921453A24C
```

The certificate itself pins the two discovery inputs, and the independent
source audit was separately checked against them:

```text
Terra cellu_diverse_master.json       BC519AA68DBAB158FAD01B143303BAC425617DC6A2A5D96679385A8DB53978DB
Terra continuous_pattern_cellu_cegar.py
                                      664A98E7020EE4003F1F3B65CABEE51AB1BE8006EEDA02032F27A34A4B1A607A
Luna original verify_cellu_independent.py
                                      B2DB4D79DDED169B745F1134B5E5F42C8AB6A1ABC4A818EDF5782192797ECDE7
```

The Atlas packet intentionally does not depend on those discovery files.

## Atlas integration

`certificates/contracts.json` classifies this packet as `certified_local` and
binds the restricted claim to both replays and their exact hashes. The
recursive-capacity note and `COORDINATION.md` repeat the same boundary:
`erdos142_solved=false` and `new_r3_bound=false`.

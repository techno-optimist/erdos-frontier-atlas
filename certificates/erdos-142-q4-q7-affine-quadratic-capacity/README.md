# Exact small-grid affine-quadratic capacities

This package determines the exact support capacities at `q=4,5,6,7` for one
specific two-dimensional continuum ansatz.  It is a local design fence, not a
new construction.

## Theorem

For `a in {0,...,q-1}^2`, put

```text
Q_a = product_j [a_j/q,(a_j+1)/q).
```

Choose a set `A` of full cells and, on every selected cell, require a potential
of the fixed-Hessian residual-affine form

```text
q^2 F((a+u)/q) = h[a] + p[a] dot u + 2 ||u||_2^2,
u in [0,1)^2.
```

The largest `|A|` for which real coefficients `h[a],p[a]` can satisfy

```text
F(x)+F(z)-2F(y) >= ||x-z||_2^2
```

for every selected physical torus-midpoint triple
`x+z = 2y (mod 1)` is exactly

| `q` | exact capacity | maximum density |
| ---: | ---: | ---: |
| 4 | 4 | `1/4` |
| 5 | 5 | `1/5` |
| 6 | 9 | `1/4` |
| 7 | 10 | `10/49` |

Every density is strictly below the EHPS local density `7/24`.

## Exact upper bounds

On a fixed support, the midpoint condition has residual coordinates
`u+w-2v in {-1,0,1}`.  After scaling by `2q^2`, the required defect is affine
on each exact residual polytope.  Testing its closure vertices is necessary
by half-open limiting and sufficient by affinity.  The four frozen packets
reconstruct these integer ledgers and attach a positive primitive Farkas
combination to every certified forbidden support.  Each combination cancels
all height and slope coefficients and leaves a strictly negative constant.

An exact include/exclude search then proves that every support of sizes
`5,6,10,11`, respectively, contains a certified forbidden support.  Hence the
four capacities are at most `4,5,9,10`.  The replay includes all `x=z`
branches; at even `q` this includes the nontrivial half-period torus branches.

## Exact lower bounds

The bundled integer candidates are substituted into every active continuum
vertex row.  Their minimum scaled slack is zero.  At `q=4`, the support is
`{0,1}^2`, whose union is `[0,1/2)^2`; taking
`h[a]=2||a||^2` and `p[a]=4a` makes `F(x)=2||x||^2`, and every selected torus
midpoint is an ordinary midpoint.  The `q=5,6,7` witnesses are likewise exact
integer coefficient tables, not rounded numerical evidence.

## Replay

Both trust paths require Python 3 and a C++17 compiler (`g++`, `c++`, or
`clang++`) on `PATH`; compiled executables live only in a temporary directory.

From the repository root on Windows:

```powershell
python -I certificates\erdos-142-q4-q7-affine-quadratic-capacity\verify.py --self-test
python -I certificates\erdos-142-q4-q7-affine-quadratic-capacity\independent_replay.py --self-test
```

From Linux or WSL:

```text
python3 -I certificates/erdos-142-q4-q7-affine-quadratic-capacity/verify.py --self-test
python3 -I certificates/erdos-142-q4-q7-affine-quadratic-capacity/independent_replay.py --self-test
```

Both replays use standard-library Python for the exact continuum algebra and
compile a small C++17 backtracker in a temporary directory.  The primary uses
a fixed vertex order and last-edge blockers.  The independent replay imports
no primary module, separately rebuilds the physical carry ledger and Farkas
identities, checks all four lower-bound witnesses, and uses dynamic branching,
unit exclusions, and memoization.  Neither trusted path invokes LP, SAT, MIP,
CP-SAT, or floating point.

Expected success markers are
`PASS_Q4_Q7_AFFINE_QUADRATIC_EXACT_CAPACITIES` and
`PASS_INDEPENDENT_Q4_Q7_AFFINE_QUADRATIC_CAPACITY_AUDIT`.

## Scope

Proved: exact capacities only for unions of full two-dimensional `q`-adic
cells at `q=4,5,6,7` and only for the displayed single-valued,
fixed-Hessian affine-quadratic ansatz, with the raw canonical endpoint norm.

Not proved: a statement for arbitrary potentials; subcell carving or
refinement; other Hessians; higher-dimensional or four-dimensional tiles;
state-, label-, edge-, path-, or context-dependent potentials; graph-directed
languages; a uniform theorem for other `q`; an EHPS shell construction;
integer transfer; an improved bound on `r_3(N)`; or Erdős Problem 142.

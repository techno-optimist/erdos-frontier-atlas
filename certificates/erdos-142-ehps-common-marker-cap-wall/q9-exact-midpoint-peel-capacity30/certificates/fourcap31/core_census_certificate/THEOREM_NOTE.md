# Exact minimal midpoint-core census in `Z_9^2`, sizes 6--8

Let `P = (Z/9Z)^2`, encode `(x,y)` by `v = 9*x+y`, and define

```
mid(a,b) = 5*(a+b) mod 9
```

coordinatewise.  This is `(a+b)/2`, since `2*5 = 1 mod 9`.

For a finite support `S`, a point `m in S` has an incoming midpoint row when
there are distinct `a,b in S` with `mid(a,b)=m`.  Simultaneous queue stripping
repeatedly deletes every point with no incoming row.  A self-core is a nonempty
set in which every point has an incoming row.  It is deletion-minimal exactly
when it is a self-core and queue stripping every one-point deletion gives the
empty set.  The latter one-deletion condition is equivalent to having no proper
nonempty core.

## Census theorem

The exhaustive counts are:

| size | all subsets | self-cores | deletion-minimal cores |
|---:|---:|---:|---:|
| 6 | 324,540,216 | 14,688 | 2,916 |
| 7 | 3,477,216,600 | 129,600 | 0 |
| 8 | 32,164,253,550 | 1,476,549 | 17,496 |

Thus there are no deletion-minimal seven-point midpoint cores.  The 2,916
minimal six-cores form one orbit under `AGL(2,Z/9Z)`, and the 17,496 minimal
eight-cores also form one orbit.

These are exact structural blocker families.  This certificate alone does not
decide whether `C_9` is 30 or 31 and makes no such claim.

## Completeness and independent checks

Each `enumerate_coreN.cpp` visits every lexicographically ordered `N`-subset,
with no randomness, pruning, SAT solver, timeout, or floating-point decision.
OpenMP changes only the schedule of the fixed outer slices; slices are merged in
lexicographic order.

The independent anchored enumerators fix point 0 and scan:

| size | anchored subsets | anchored self-cores | anchored minimal cores |
|---:|---:|---:|---:|
| 6 | 24,040,016 | 1,088 | 216 |
| 7 | 300,500,200 | 11,200 | 0 |
| 8 | 3,176,716,400 | 145,832 | 1,728 |

Translation is transitive on the 81 points.  Double-counting incidences
`(core, contained point)` therefore gives the full count as
`anchored_count * 81 / N`, reproducing all six full counts above.  The anchored
minimal rows for sizes 6 and 8 exactly match the corresponding frozen-ledger
rows containing point 0.

The standard-library Python verifiers use a separate queue-core implementation.
They replay every ledger row and every single deletion: 17,496 self checks and
139,968 deletion checks for size 8, and the analogous 2,916 plus 17,496 checks
for size 6.  They generate all affine images using the 3,888 matrices whose
determinant is a unit modulo 9 and all 81 translations.  Starting from ledger
row 0 produces the whole ledger in each nonempty size.

## Ledger format

`minimal_core6.txt` and `minimal_core8.txt` are ASCII with LF line endings.
Every line contains exactly 6 or 8 strictly increasing, zero-based point
indices, separated by single spaces.  Decode index `v` as `(v//9,v%9)`.
Rows are lexicographically ordered and unique.  `minimal_core7.txt` is the
intentional zero-byte empty ledger.

## Assumptions and dependencies

- Arithmetic is exactly integer arithmetic modulo 9.
- A C++14 compiler with OpenMP is needed for the C++ replays.
- Python 3 standard library is sufficient for the semantic/orbit replays.
- No network access, SAT/SMT package, random seed, or external data is used.
- Reported runtime is descriptive, not part of correctness.  The source-host
  size-8 run used 12 threads and took 544.964 seconds.

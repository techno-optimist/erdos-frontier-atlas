# q=6 117-cell transition-graph spectral wall

This certificate closes every unweighted directed graph on the fixed 117-cell
alphabet for the position- and length-independent endpoint/edge potential

```text
P(c_0,...,c_(m-1))
  = g[c_0]/2 + sum_i H[c_i,c_(i+1)] + g[c_(m-1)]/2,
```

when the path language has unrestricted relevant endpoints and the potential
must satisfy every genuine synchronized two-block closure row. The proof is a
dichotomy: a common successor gives an exact two-row Farkas wall; avoiding all
such walls forces the adjacency Perron root below the density gate.

## Exact bad-pair census

For an unordered pair `{a,b}`, use the two legal local rows

```text
(a,b,b), (a,a,b).
```

The primary standard-library replay reconstructs all 117 cells and their
raw-canonical `q^2`-scaled closure costs. Exactly 187 pairs have positive
summed right side: 173 gaps are 72 and 14 are 144. It checks both append and
prepend coefficient cancellation for every pair and every cell `p`, for
43,758 exact symbolic cancellations. A 27-edge matching of bad pairs covers
54 distinct vertices.

## Common-successor wall

If `p` is a common outneighbor of `a,b`, append the diagonal local row
`(p,p,p)` to both bad-pair rows. The three role paths are

```text
(a,p),(b,p),(b,p)       and       (a,p),(a,p),(b,p).
```

With coefficients `(+1,-2,+1)`, their positive unit sum cancels every endpoint
variable `G=36g` and every allowed directed-edge variable `J=36H`, while the
diagonal right side is zero and the first-block gap is 72 or 144. Thus the
required inequalities imply an exact contradiction. A common inneighbor gives
the same result by prepending the diagonal row.

## Solver-free Perron bound

If a graph avoids the wall, the two outneighbor sets for every bad pair are
disjoint. Use the replayed 27-edge matching. For a nonnegative Perron
eigenvector `v`, set `S=sum(v)` and `rho` equal to the adjacency Perron root.
Each paired block obeys

```text
rho(v_a+v_b) <= S,
```

and each of the other 63 singleton vertices obeys `rho v_w<=S`. Summing the
90 block inequalities gives

```text
rho S <= 90 S,       hence rho <= 90 < 441/4.
```

The four-dimensional EHPS product gate is `rho>1296*(7/24)^2=441/4`.
Therefore the Farkas-free side of the dichotomy has insufficient path-volume
growth. The argument permits irregular or reducible 0/1 adjacency matrices
and arbitrary loops. The independent replay uses only seven disjoint bad
pairs and obtains the already sufficient bound `rho<=110<441/4`.

## Replay

```powershell
python -I verify.py --self-test
python -I independent_replay.py
```

The replays are stdlib-only. They rebuild the decoder, closure rows, exact
feature cancellation and spectral block accounting, and reject planted RHS,
matching and coefficient corruptions.

## Scope fence

This closes the stated fixed-117-cell, unweighted directed path languages and
position-independent endpoint/edge table class. It does not cover weighted or
multi-edge state lifts, repeated physical labels, endpoint-pruned languages
that do not contain the required two-block paths, position- or length-dependent
tables, within-edge residual functions, partial carving, support deformation,
integer transfer, or a new `r_3(N)` bound. Erdős Problem 142 remains unsolved.

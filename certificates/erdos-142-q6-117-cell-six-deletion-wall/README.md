# Erdős 142: 117-cell six-deletion wall

This packet certifies an exact negative result for one narrow, mass-positive
four-dimensional `q=6` support and one continuous potential class.  It does
not solve Erdős Problem 142 and does not give a new bound for `r_3(N)`.

## The support and the gate

Let

```text
S0 = {(3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(5,0),(5,1),(5,2)}

D  = {(0,4),(1,4),(1,5),(2,1),(2,3),(3,5),(4,0),
      (4,4),(4,5),(5,0),(5,1),(5,2),(5,3)}.
```

The cell alphabet is

```text
U_D = {(a_1,a_2,a_1+d_1,a_2+d_2) mod 6 : a in S0, d in D}.
```

It has `117` distinct cells in `(Z/6Z)^4`, hence density

```text
117/6^4 = 13/144 = 52/576 > 49/576 = (7/24)^2.
```

For a four-dimensional EHPS superblock, `49/576` is the product baseline.
Deleting six whole cells still leaves

```text
111/1296 - 49/576 = 1/1728 > 0,
```

whereas deleting seven leaves density below the gate.  Thus every
gate-preserving whole-cell subcollection of this fixed alphabet deletes at
most six cells.

## The potential class

On the half-open union of the selected `q=6` cells, consider potentials

```text
F(x) = 2 ||x||_2^2 + g[cell(x)],
```

with one arbitrary real offset `g[c]` for each retained cell.  For every
modular midpoint triple `x+z = 2y (mod 1)`, the required EHPS coercivity row is

```text
F(x) + F(z) - 2 F(y) >= ||x-z||_2^2.
```

Write `h[c]=6^2 g[c]`.  Eliminating the within-cell offsets gives the
equivalent exact, integer-scaled finite system

```text
h[c_x] + h[c_z] - 2 h[c_y] >= b(c_x,c_y,c_z).
```

The verifier reconstructs the `6^2`-scaled right side `b` coordinate by
coordinate in `Fraction` arithmetic.  If `a,b,c` are scalar digits, `k` is
the modular carry and `ell=6k-(a+c-2b)`, a branch exists exactly for
`ell in {-1,0,1}`.  The offset interval is `[1/2,1]`, `[0,1]`, or `[0,1/2]`,
respectively, and the affine right side is maximized at the appropriate
endpoint.  These closure suprema are also suprema of the half-open branches,
so they are necessary for every potential satisfying all actual half-open
rows.  Scaling `g` bijectively to `h` changes neither feasibility nor the sign
of a positive Farkas contradiction.  Exactly `98,167` ordered cell triples
survive.

## The exact wall

[`rays.json`](rays.json) contains `943` positive integral Farkas rays.  For
each ray the verifier checks:

- every row is one of the exact continuous cell-triple rows;
- every multiplier is a positive integer;
- all `117` potential coefficients cancel exactly;
- the weighted right side is strictly positive;
- the listed semantic support is exactly the union of the cells in its rows;
- the ray avoids the deletion set from which it was extracted.

Therefore any deletion set that could make the restricted potential system
feasible must hit the semantic support of every ray.

[`hitting_proof.json`](hitting_proof.json) is a hash-bound exhaustive
branching certificate with `29,980` nodes.  Branch nodes exhaust one still
unhit ray support.  Leaf nodes exhibit enough pairwise-disjoint unhit supports
to exceed the remaining deletion budget.  It proves that no set of at most
six cells hits all `943` supports.

Combining the two exact statements gives the certified conclusion:

> No whole-cell subcollection of `U_D` whose density remains strictly above
> `(7/24)^2` admits a potential of the form
> `2||x||_2^2 + g[cell(x)]` satisfying every required continuous
> raw-canonical modular-torus coercivity row.

## Replay

From this directory:

```bash
python3 -I verify.py rays.json --self-test --find-hit \
  --verify-certificate hitting_proof.json
python3 -I independent_replay.py rays.json hitting_proof.json --self-test
```

The primary replay is standard-library only.  It independently reconstructs
the alphabet and the `98,167`-row continuous ledger, checks all Farkas rays,
checks the density gate, runs its own exact transversal search, and verifies
the serialized branching/packing proof.  Its planted failures corrupt an
exact row, a Farkas incidence, and a packing leaf.

The second replay is separately written and imports neither the primary
verifier nor any discovery code.

## Boundary

This is a wall for the fixed `117`-cell alphabet, whole-cell deletion, and the
displayed cell-offset potential class.  It does **not** exclude within-cell
piecewise potentials, pair interactions, graph-state or cocycle potentials,
arbitrary physical potentials, partial measurable carving, replacement or
deformation of cells, another quotient, or a different support.  It supplies
neither the full graph-directed EHPS transfer hypotheses nor an integer
construction.  No new `r_3(N)` bound is claimed; Erdős Problem 142 remains
unsolved.

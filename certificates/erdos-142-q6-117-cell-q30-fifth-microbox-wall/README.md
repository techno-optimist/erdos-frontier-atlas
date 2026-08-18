# q=30 fifth-microbox one-block wall

This packet certifies an exact wall for a **single retained union** of
complete, globally aligned residual-fifth microboxes in the fixed 117-cell
q=6 alphabet.  It is not a word-language or graph/path capacity theorem and
does not solve Erdos Problem 142.

## Exact theorem

Subdivide each residual coordinate of every coarse cell into five equal
half-open intervals.  The physical fine digit is

```text
d_j = 5*c_j + s_j,   s_j in {0,1,2,3,4},
```

so the alphabet contains

```text
117 * 5^4 = 73,125
```

distinct q=30 microboxes.  Let `U` be any union of these complete boxes.  If a
bounded, single-valued physical potential on `U` satisfies every actual
pointwise raw-canonical modular-torus midpoint coercivity inequality, then

```text
|U| <= 68,484 < 275625/4 = 68,906.25 = (49/576) * 30^4.
```

Thus no such one-block union has density strictly above the four-coordinate
EHPS product gate.

## Disjoint obstruction packing

The standard-library replays reconstruct two mutually disjoint obstruction
families.

1. The exact 2,382-edge strict-dilation graph decomposes into 1,632 components.
   A deterministic componentwise maximum matching has 1,789 edges and 3,578
   distinct endpoints.  Retaining both boxes of one edge gives the same
   strict-interior dilation recurrence and finite boundedness contradiction as
   the earlier q=24 wall.

2. In each of 225 fixed-first-pair fibers, the last-pair prototype contains
   translated copies of the four points

   ```text
   A=(5,23), B=(11,5), C=(23,29), D=(29,11).
   ```

   The four unit-weight rows `(B,A,D)`, `(C,B,D)`, `(A,C,B)`, and `(A,D,C)`
   are actual common-offset torus midpoint rows.  Every physical potential
   value has aggregate coefficient zero, while every endpoint pair is
   distinct and the total raw endpoint-square cost is positive.  Exactly 16
   four-of-five translations occur in the 325-point prototype.  After the
   matching endpoints are reserved, deterministic packing leaves 2,852
   mutually disjoint four-box packets, comprising 11,408 checked physical
   rows.

The 1,789 two-box supports and 2,852 four-box supports are mutually disjoint.
Every feasible one-block support must therefore delete at least

```text
1,789 + 2,852 = 4,641
```

boxes.  A support strictly above the exact gate can delete at most 4,218.  The
packing clears the required 4,219-obstruction threshold by 422 and leaves at
most 68,484 boxes.

## Two independent certificates and encodings

The two accepting replays were written independently and bind genuinely
different frozen encodings.

- `frozen_semantic_certificate.json` is the 518,711-byte primary ledger.  It
  stores every one of the 1,789 matching edges and 2,852 packet supports.  The
  primary replay independently reconstructs and compares those combinatorial
  ledgers and all 11,408 expanded packet rows, but it is corroborating rather
  than claim-certifying because it does not rederive the bounded-potential
  dilation telescope.  Its SHA-256 is
  `9d12ac579679540abd1ea46408018c06250924de0133c0a4eabd9b8a8c829c49`.
- `independent_semantic_certificate.json` is a separate 1,262-byte compact
  rule-and-digest certificate.  The independent replay reconstructs the
  geometry, exact componentwise maximum matchings, the strict-interior
  bounded-potential dilation identities and finite telescope, four-of-five
  intersections, packets, physical rows and gate from scratch, then checks its
  independently encoded semantic digests.  This is the claim-certifying
  replay.  Its SHA-256 is
  `34d6c3babf9c4a669b01b0bbf3ff047c0c7ccec687b85a46f3b75585174764b2`.

Neither replay imports a producer, discovery script, optimizer, solver, or
third-party package.  Each verifies frozen-byte nonmutation.  The primary
plants raw-cost, carry, overlap and insufficient-density corruptions.  The
independent replay plants bad-packet, insufficient-count and duplicate-support
corruptions while directly recomputing every generated carry and raw cost.
The optional `--self-test` spelling is accepted for contract convention; the
full replay and all planted controls run on every invocation, with or without
that flag.

From the repository root on native Windows:

```powershell
python -I certificates\erdos-142-q6-117-cell-q30-fifth-microbox-wall\verify_q30_fourpoint_packing.py --self-test
python -I certificates\erdos-142-q6-117-cell-q30-fifth-microbox-wall\verify_r5_four_of_five_packing.py --self-test
```

From the repository root in WSL or Linux:

```text
python3 -I certificates/erdos-142-q6-117-cell-q30-fifth-microbox-wall/verify_q30_fourpoint_packing.py --self-test
python3 -I certificates/erdos-142-q6-117-cell-q30-fifth-microbox-wall/verify_r5_four_of_five_packing.py --self-test
```

## Scope

Proved:

- exact q=30 geometry, gate arithmetic, and a 4,641-support disjoint packing;
- arbitrary bounded single-valued potentials on one complete aligned
  microbox union;
- actual strict-interior raw-canonical modular-torus midpoint semantics.

Not proved:

- an all-horizon, graph-directed, or arbitrary word-language capacity bound;
- proper or finer carving inside a q=30 box, non-axis-aligned pieces,
  deformation, overlapping decoders, or coupled multi-block tiles;
- almost-everywhere-only coercivity or unbounded corrections;
- an EHPS shell construction above the gate, integer transfer, an improved
  bound for `r_3(N)`, or a solution of Erdos Problem 142.

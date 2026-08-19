# q=24 order-four one-block microbox wall

This packet certifies a new exact wall for a **single retained union** of
complete, globally aligned fourth-residual microboxes in the fixed 117-cell
q=6 alphabet.  It is not a word-language capacity theorem and does not solve
Erdos Problem 142.

## Exact theorem

Subdivide each residual coordinate of every coarse cell into four equal
half-open intervals.  The physical fine digit is

```text
d_j = 4*c_j + s_j,   s_j in {0,1,2,3},
```

so the alphabet contains

```text
117 * 4^4 = 29,952
```

distinct q=24 microboxes.  Let `U` be any union of these complete boxes.  If a
bounded, single-valued physical potential on `U` satisfies every actual
pointwise raw-canonical modular-torus midpoint inequality, then

```text
|U| <= 28,159 < 28,224 = (49/576) * 24^4.
```

Thus no such one-block union has density strictly above the four-coordinate
EHPS product gate.

## Disjoint packing

The standard-library replay constructs two exact obstruction families.

1. The 1,359-edge strict-dilation graph has a deterministic 960-edge
   matching.  If both complete boxes of one matched edge survive, the two
   strict-interior rows at scales `t` and `3t` give, for `K >= 1` wrap
   coordinates,

   ```text
   D(3t) - D(t) >= K * (72 - 48t).
   ```

   Taking `t=(1/8)/3^j` gives a finite telescope that exceeds any proposed
   bound on the physical correction.  The replay checks the exact carries,
   the two raw-canonical correction identities, microinterval membership, and
   the finite-telescope arithmetic.

2. On fine digit vectors use the fixed order-four translation

   ```text
   sigma = (0,0,6,12) mod 24.
   ```

   There are 1,152 complete four-point orbits in the full alphabet.  After
   reserving the 1,920 dilation-matching endpoints, exactly 833 entire orbits
   remain.  They are mutually disjoint.  For an orbit `p_0,...,p_3`, give all
   four boxes the same strict-interior offset `u` and, for every centre `p_k`,
   use endpoints `p_(k-1)` and `p_(k+1)`.  Every row is an actual torus
   midpoint, has raw fine-digit cost 144, and the four rows have aggregate
   potential incidence zero.  Their normalized positive right side is

   ```text
   4 * 144 / 24^2 = 1.
   ```

The 960 two-box supports and 833 four-box supports are pairwise disjoint.
Every feasible one-block support must omit at least one box from each, hence
must make at least

```text
960 + 833 = 1,793
```

deletions.  Strictly above the gate permits only 1,727 deletions.  The exact
packing clears the required 1,728-obstruction threshold by 65.

## Frozen semantics and replay

`frozen_semantic_certificate.json` stores all 960 oriented dilation records,
all 833 four-point packet supports, the translation rule that expands every
packet row, exact gate data, scope flags, and canonical semantic digests.
`verify_r4_order4_packing.py` imports no producer, solver, or third-party
package.  It reconstructs the geometry and both ledgers independently,
checks all physical rows and planted failures, and verifies that the frozen
certificate bytes are unchanged after replay.  The separately written
`independent_r4_replay.py` is a standalone reconstruction: it intentionally
reads neither the primary verifier nor the frozen payload.

From the repository root on native Windows:

```powershell
python -I certificates\erdos-142-q6-117-cell-q24-quarter-microbox-wall\verify_r4_order4_packing.py --self-test
python -I certificates\erdos-142-q6-117-cell-q24-quarter-microbox-wall\independent_r4_replay.py
```

From the repository root in WSL or Linux:

```text
python3 -I certificates/erdos-142-q6-117-cell-q24-quarter-microbox-wall/verify_r4_order4_packing.py --self-test
python3 -I certificates/erdos-142-q6-117-cell-q24-quarter-microbox-wall/independent_r4_replay.py
```

Canonical semantic digests are:

```text
dilation semantic:
b76a136b58f6adcbebb9f0d34447bda10b99070c5339b6df5afd87989d9ab803

packet supports:
f7e337056bde4b79568b97ff156e9bd6f03abc513da7d3fffedaae494d813db1

expanded packet semantics:
061eba59ea9fd5e529b9c161b8d90d2c538df38067c5d485f3ae90dbf4736037

payload semantics:
8e54dab21a04d4a9f78631eb2c74e800597a78942080a417a3a4b7c493e25e65
```

The frozen certificate file itself has SHA-256
`dee2342e5670f735fe2e495c78dc7b20d3414191fc1e35cd64d34f595f7e7e69`.

## Word-language boundary

The theorem above does **not** imply that an arbitrary horizon-dependent
language of q=24 microbox words has capacity at most `28,159^m`.  Dilation
pairs admit a two-symbol quotient-injectivity argument.  A four-point packet
only says that its four physical boxes cannot all occur in one fixed support;
it does not automatically merge four symbols into three independently in
every word coordinate.

The replay includes a concrete warning: in two phase coordinates there is a
10-word subset of `Z_4^2` containing none of the 16 direct affine order-four
lines, whereas the naive product quotient would allow only `3^2=9`.  Stronger
fully coupled midpoint packets may rule out that 10-word set, but proving the
required all-horizon capacity lemma is separate work and is not asserted here.

## Scope

Proved:

- exact q=24 geometry, density arithmetic, and disjoint packing;
- arbitrary bounded single-valued potentials on one complete aligned
  microbox union;
- actual strict-interior raw-canonical modular-torus midpoint semantics.

Not proved:

- an all-horizon or graph-directed word-language capacity bound;
- proper carving inside a q=24 microbox, non-axis-aligned pieces, overlapping
  decoders, almost-everywhere coercivity, or unbounded corrections;
- an EHPS shell construction above the gate, integer transfer, or an improved
  bound for `r_3(N)`.

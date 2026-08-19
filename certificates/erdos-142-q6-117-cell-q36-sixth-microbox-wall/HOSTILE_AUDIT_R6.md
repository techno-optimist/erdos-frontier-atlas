# Hostile audit: q=36 six-of-nine one-block wall

Verdict: **APPROVE** for the stated one-block theorem.  No word-language,
graph-capacity, or Problem 142 solution claim is licensed by this result.

Audit target:

```text
D:\p42_research\erdos142_r6_microbox_frontier_20260818
```

## Independent reconstruction

`independent_r6_replay.py` is a separately written Python-standard-library
replay.  It imports neither the discovery program nor the primary verifier.
Its matching engine is a bitmask dynamic program, not the primary verifier's
combination scan.  It also checks the physical dilation and packet rows
directly at exact rational strict-interior points.

Native Windows and WSL/Linux both produced:

```text
PASS_INDEPENDENT_R6_Q36_ONE_BLOCK_WALL
GEOMETRY_OK coarse=117 microboxes=151632 codes_unique
DILATION_OK edges=3811 components=2785 max_component=9 matching=2986
PACKETS_OK full=7776 blocked=1453 retained=6323 rows=37938
INTERSECTION_HIST {1: 24, 2: 36, 3: 24, 4: 24, 5: 12, 6: 24}
RAW_HIST {16: 12164, 64: 23082, 784: 2210, 1024: 482}
CARRY_HIST {(0, 0, 0, -1): 7187, (0, 0, 0, 0): 23564, (0, 0, 0, 1): 7187}
DISJOINT_OK obstructions=9309 margin=561
GATE_OK total=151632 allowed_deletions=8747 max_retained=142323 gate=142884
DEPENDENCIES_OK stdlib_only no_import no_solver
SCOPE one_block_complete_aligned_q36_microbox_unions_only
```

The independent reconstruction matches all three primary semantic digests:

```text
dilation semantic  d520ceaf418068665a166617e747da23b970d701c71de1cf13b5eac8d368bff1
packet support     36c478be01b818a32980563b193ae2290e9db41048f6a2e757d77609cb0dd243
expanded packets  e8ae9b924fa16076ecf9a117f8a210c665bca1bc1c01d7490f3c7f97a90b5bfc
payload semantic  9aa110472ac2da97d919e30fea2cfdee1b308c2f743bca4b70d67781f819f544
```

## Mathematical audit

- The fixed alphabet has 117 distinct q=6 cells.  Six residual subdivisions
  in each of four coordinates give exactly `117*6^4 = 151632` distinct q=36
  complete aligned microboxes.
- The independently generated strict-dilation graph has 3,811 edges in 2,785
  components, maximum component size nine.  Exact componentwise maximum
  matching gives 2,986 disjoint pairs and reproduces the frozen canonical
  matching digest.
- Every selected dilation edge has exactly one wrap coordinate.  For the two
  physical rows at scales `t` and `3t`, the potential left sides sum to
  `D(3t)-D(t)`.  Directly, each wrap coordinate contributes
  `2*(1-2t/3)^2` to the raw-canonical right side and each other active
  coordinate contributes `8*t^2/9`.  Taking `t=(1/12)/3^j` therefore gives a
  positive constant per step and contradicts boundedness if both boxes are
  retained.  This direct check independently implies the primary verifier's
  corrected-potential telescope.
- Full enumeration of the order-nine translation on `Z_36^2` reproduces the
  prototype intersection histogram and exactly 24 disjoint six-point
  prototypes.  The 324 first-pair fibers give 7,776 packets; exactly 1,453
  meet canonical dilation endpoints, leaving 6,323 mutually disjoint packets
  avoiding every matching endpoint.
- Each retained packet has exactly six nondegenerate physical torus-midpoint
  rows at common offset `(1/7,2/7,3/7,4/7)`.  Every vertex has total endpoint
  coefficient `+2` and centre coefficient `-2`, so an arbitrary single-valued
  potential cancels.  Every row has positive raw-canonical endpoint-square
  cost.  The exact carry and raw-cost histograms match the frozen payload.
- The two obstruction families are support-disjoint, so at least
  `2986+6323=9309` boxes must be deleted.  The exact gate is
  `(49/576)*36^4=142884`; retaining strictly above it permits only 8,747
  deletions.  Hence `|U| <= 151632-9309 = 142323`, with margin 561.

## Replay and hostile controls

- Primary replay passed under native Windows and WSL/Linux with `-I` and
  `--self-test`.
- An isolated directory containing only README, certificate, and primary
  verifier also passed, demonstrating no producer dependency.
- The primary replay passed under `python -O -I`; safety checks use an explicit
  exception rather than removable `assert` statements.
- An unexpected argument was rejected with exit code 1.
- Removing the frozen certificate was rejected with exit code 1.
- Changing `retained_packets` from 6,323 to 6,322 in an isolated certificate
  copy was rejected with `wrong certificate packet record`.
- The primary verifier imports only Python-standard-library modules and checks
  exact certificate structures, semantic digests, planted failures, and
  certificate nonmutation.
- Repeated native/WSL execution left all source packet hashes unchanged.

## Scope and prose

The README, verifier docstring/output, and frozen scope flags consistently say
that the result is only for a single union of complete, globally aligned q=36
microboxes.  They explicitly disclaim arbitrary word-language or graph
capacity, proper carving, deformations/overlaps, unbounded corrections, the
EHPS shell/integer transfer, and a solution or improved lower bound for
Problem 142.

Nonblocking clarity suggestion: when integrating, define the dilation
"physical correction" used in the displayed telescope.  If the original
potential is `f`, one convenient normalization is
`G(p)=36*f(p)-72*||p||_2^2` and
`D(t)=G(A_t)+G(B_(1-t))`.  Then the verifier's displayed
`D(3t)-D(t) >= K*(72-48t)` follows verbatim.  The independent replay also
checks the stronger direct telescope for `f`, so this is documentation only,
not a theorem defect.

## Target hashes audited

```text
README.md                        539835615fd269ea920df758813a4146daf7f313e225ee489e32dd7051b3288a
frozen_semantic_certificate.json 318bb7ac5cb3bac2dba1b10815c47d0997bf95c8b88f8dfd5d2da1f7a6720d5d
verify_r6_six_of_nine_packing.py f7a0b693220cf4891c954f8675ce78bcd6c40a68ec3ce59889ab1b22739576d9
explore_r6.py                    a3a79b6909f1437556762b345949c8421bec067d21b2df4c2fe06d087ea7a7ab
```

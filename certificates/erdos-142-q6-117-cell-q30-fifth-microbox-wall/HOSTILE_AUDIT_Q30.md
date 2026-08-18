# Hostile audit: q=30 four-of-five one-block wall

## Verdict

**GREEN for the stated one-block theorem.**  The solver-free replay proves
that a union of complete, globally aligned q=30 microboxes from the fixed
117-cell q=6 alphabet cannot both lie strictly above density `49/576` and
support a bounded, single-valued physical potential satisfying every actual
raw-canonical modular-torus midpoint inequality.

The replay reconstructs 2,382 componentwise-dilation edges, an exact
1,789-edge componentwise maximum matching, and 2,852 mutually disjoint
four-point midpoint packets avoiding all matching endpoints.  Hence it packs
4,641 disjoint obstruction supports, 422 more than the required 4,219.  At
least 4,641 of the 73,125 boxes must be deleted, leaving at most 68,484, while
the exact gate is `275625/4 = 68,906.25`.

## Independent derivation

This lane reconstructed the q=30 geometry and dilation graph independently.
An exhaustive scan first showed that no complete order-five translation orbit
survives in the alphabet.  A small-packet search then exposed the four-point
support

```text
A=(5,23), B=(11,5), C=(23,29), D=(29,11)
```

with unit-weight rows

```text
(B,A,D), (C,B,D), (A,C,B), (A,D,C).
```

Recognizing this as a four-of-five intersection of an ambient orbit under
the last-pair shift `(6,12)` removed the solver from the proof.  The final
standard-library verifier enumerates the 325-point prototype directly.  Its
order-five intersection histogram is exactly `{1:48, 2:48, 3:39, 4:16}`.
The 16 four-point intersections lift over 225 fixed-first-pair fibers to
3,600 packets.  Reserving the canonical dilation endpoints removes 748
distinct packets, leaving 2,852.  Every retained packet has four unique
nondegenerate modular midpoint rows, zero aggregate potential incidence, and
positive aggregate raw endpoint-square cost.

No producer, optimizer, discovery script, or third-party package is imported
by the accepting verifier.

## Replay results

Native Windows passed:

```powershell
python -I D:\p42_research\erdos142_r5_microbox_frontier_20260818\verify_r5_four_of_five_packing.py --self-test
```

WSL Ubuntu passed:

```text
python3 -I /mnt/d/p42_research/erdos142_r5_microbox_frontier_20260818/verify_r5_four_of_five_packing.py --self-test
```

Both printed `PASS_R5_FOUR_OF_FIVE_ONE_BLOCK_PACKING_WALL`, the same three
semantic digests, certificate SHA-256, obstruction count, and gate arithmetic.

The verifier accepts either no arguments or exactly `--self-test`.  Both forms
run the same full replay, including planted failures.  Any other argument is
rejected.  The frozen JSON must be adjacent to the verifier.

## External exact-set comparison

Only after the independent derivation and native/WSL passes, this lane loaded
the separate implementation in
`D:\p42_research\erdos142_q30_packet_accel_20260818` for a one-time external
comparison.  The two implementations produced exactly equal sets of 3,578
canonical matching endpoints and exactly equal sets of 2,852 retained
four-point supports; both symmetric differences were empty.  This comparison
is corroborating audit evidence, not an input to or acceptance condition of
the frozen replay.

## Scope and caveats

The result covers arbitrary bounded, single-valued physical potentials on one
fixed union of complete aligned q=30 microboxes.  It does **not** prove an
all-horizon or graph-directed word-language capacity bound.  A four-point
one-block obstruction does not automatically give a coordinatewise quotient
for tensorized languages.

It also does not cover proper carving inside a q=30 microbox, finer or
non-axis-aligned pieces, deformed or overlapping tiles, almost-everywhere
coercivity, unbounded corrections, an EHPS shell above the gate, or integer
transfer.  Erdős Problem 142 remains unsolved.

The compact semantic JSON fixes the rule, counts, scope, and semantic digests;
it does not store the full 2,852-packet ledger.  The standalone verifier
reconstructs that ledger deterministically and binds it by support and expanded
row digests.

No mathematical or implementation flaw was found within this stated scope.

## Pre-integration scratch-source hashes

These hashes identify the independently derived scratch packet audited before
promotion.  Integration renamed its certificate, patched the verifier's
adjacent-certificate basename and removed an unreachable pre-freeze bypass;
the repository contract binds the resulting promoted bytes separately.

```text
README.md
5e8e3f7c6530a2d81a5a1b2d02a52cbedd1b7d0743bec4e0cf9b9d25459b512a

verify_r5_four_of_five_packing.py
571df4247655cc4ae8edcccf980b844731039972f8f3afc8769b0a9937721722

frozen_semantic_certificate.json (promoted as independent_semantic_certificate.json)
34d6c3babf9c4a669b01b0bbf3ff047c0c7ccec687b85a46f3b75585174764b2
```

The SHA-256 of this audit note is reported in the handoff rather than embedded
in the file, avoiding a self-referential hash.

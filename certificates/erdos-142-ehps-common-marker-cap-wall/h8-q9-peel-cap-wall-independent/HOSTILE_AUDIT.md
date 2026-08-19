# Hostile audit note: compact q9 certificate

Date: 2026-08-19.

Verdict on the audited compact packet: **APPROVE**.  The audited source
manifest was

```text
19cb6aacab9760b76a5c466b02bdfa554c1da5c1e7875d3fcf24e0bcbade4e4d
```

with a closed census of 19 files and 924,030 bytes.  This hostile replay copies
only the two theorem-critical transparent ledgers:

```text
template0_blockers.txt
  286,836 bytes
  6616ff7d8262b7e5f597b606df09e71b60bb9edd34f43cfbd2a9d710fba58fa8

template1_blockers.txt
  65,220 bytes
  4938f64aaac275f62eca702af1fb310ff9e7bf3448c460d1f32c250cd9ac75c6
```

No external packet is needed to run this replay.

## Independent proof decomposition

1. `independent_replay.py` constructs the midpoint table on `(Z/9Z)^2` and
   computes the greatest midpoint-supported fixed point by simultaneous set
   iteration.  For both templates it checks that the template core is empty,
   every supplied blocker creates a nonempty core, and deleting any one outside
   blocker point empties the core.  The exact blocker histograms are
   `15,0,297,3177,11619,0` and `15,0,297,3798,9,27`.

2. The 30-point reverse-add order is checked directly.  The rank potential
   `4^j` has 131 internal midpoint rows, minimum strict defect 18, and minimum
   raw and intrinsic denominator-9 margins 1,448.  Hence `C_9>=30`.

3. Every five points in a mod-3 fibre contain a three-point midpoint core.
   Thus a peelable 32-set has at least five saturated four-point fibres; five
   quotient points in `AG(2,3)` contain a quotient line, producing a peelable
   12-point saturated slab.  The replay finds 54 four-caps, no five-cap,
   5,832 peelable slabs among `54^3=157,464`, and two orbits of size 2,916 under
   the full 26,244-element affine slab stabilizer.  Their representatives are
   exactly template0 and template1.

4. `cover_independent.cpp` regenerates the six local domains directly from the
   midpoint geometry, obtaining sizes `1,9,36,72,54`.  Unlike the audited
   producer search, it does not launch a fresh DFS for each size profile.  It
   traverses one joint count-pruned tree and uses the alternate symmetry-tied
   orders `4,1,2,3,0,5` and `3,2,4,5,0,1`.  Every blocker is tested once all of
   its fibres have been assigned.  The deterministic target-20 exhaustions are

   | template | recursion nodes | result |
   |---|---:|---|
   | 0 | 1,624,151 | UNSAT |
   | 1 | 1,192,358 | UNSAT |

   The blocker constraints are downward closed, so exact target 20 also
   excludes larger extensions.  Both normalized slabs are therefore
   impossible in a peelable 32-set, proving `C_9<=31`.

5. The target-19 positive controls are deliberately labelled relaxed.  The
   alternate-order search chooses different witnesses from the producer:
   template0 masks `2092080ab4d945` and `8249a6f861c` have unique residual
   cores of sizes 28 and 27 respectively, while the two distinct template1
   controls both have residual size 31.  All masks are decoded against the
   same increasing 54-point allowed ordering.  Fixed-point uniqueness is per
   support, so differing core sizes for distinct supports are expected; none
   is a peelable 31-point witness.

6. Exact `Fraction` arithmetic checks the q9 Jacobian, all digit midpoint
   lifts, the slice bound constant `31/81`, marker normalization `31/2916`,
   zero gap `1/46656`, the gap polynomial

   ```text
   (1-1022544*epsilon+1539648*epsilon^2)/46656,
   ```

   and the adjacent rational bracket at `1/1022543` and `1/1022542`.

## Trust and scope

The compact source-level cover is sufficient; raw DRAT traces are independent
external provenance and are intentionally absent.  Experimental trimmed
binary-core artifacts are also absent because they failed independent proof
rechecking.

The finite result is exactly `30<=C_9<=31`; no size-31 support is claimed.  The
h=8 arithmetic applies only to the literal one-common-marker, pointwise
physical-potential model described by the audited theorem.  This packet does
not handle phase-owned or context-owned markers, perform an integer transfer,
improve `r_3(N)`, or resolve Erdős Problem 142.

# Hostile audit: endpoint-pruned transition extension

Verdict: **PASS within the stated fixed-state, label-table scope.**

## Attacks checked

1. **Reducible adjacency.**  The proof never applies a positive Perron vector
   to the whole reducible matrix.  It first selects a reachable/co-reachable
   strongly connected component attaining the endpoint-pruned limsup rate and
   applies right and left Perron vectors only to its irreducible induced
   matrix.

2. **Matched vertices missing from the Perron core.**  If the core has `k`
   vertices, at most 90 can be selected from the 117 vertices without
   completing one of the 27 disjoint matched pairs.  Therefore the proof uses
   only the `h>=k-90` pairs actually contained in the core.  It does not assume
   all 27 pairs survive restriction.

3. **Mixed predecessor/successor avoidance.**  A pair without a sandwich may
   be out-disjoint or in-disjoint, and different pairs may choose different
   sides.  The right-vector bound `rho<=k-r` and the left-vector bound
   `rho<=k-(h-r)` are both retained.  Optimizing the minimum over the mixture
   gives at most 103; there is no illicit attempt to combine left and right
   eigenvector coordinates.

4. **Loops, irregularity, and periodicity.**  Loops are allowed.  The
   neighborhood inequalities use only zero-one incidence.  Irregular degrees
   are harmless.  Periodicity is handled by cyclic classes and limsup; the
   two-edge branch `q->a/b->p` has the same modulo-period increment as every
   `q`-to-`p` walk.  Hence, at each sufficiently large admissible length, there
   exists a same-length branch-and-merge pair through the core; no claim of a
   local rewrite of each individual walk is needed.

5. **Endpoint pruning.**  The common prefix ends at the common predecessor
   `q`, and the common suffix starts at the common successor `p`.  Since the
   Perron core is reachable from `supp(u)` and can reach `supp(v)`, both padded
   paths satisfy the endpoint masks.  Merely having a common successor would
   not suffice for this step; the sandwich lemma is essential.

6. **Position- and length-dependent tables.**  At one fixed horizon the two
   necessary inequalities have correction left sides
   `Phi_m(A)-Phi_m(B)` and `Phi_m(B)-Phi_m(A)`.  They cancel even when `Phi_m`
   changes with the horizon or is an arbitrary finite real-valued global
   lookup on label paths; no uniform bound across horizons is assumed.
   Additivity, stationary edge values, endpoint coboundaries, and a uniform
   range bound are not used.

7. **Residual-dependent functions.**  The two closure rows generally use
   different physical residual points in the same path-label boxes.  An
   arbitrary residual-dependent potential would therefore not cancel.  The
   result is deliberately not stated for that class.  One-sided closure
   suprema are legitimate only because the correction is constant on each
   label path and the universal quadratic part is continuous.

8. **Finite short horizons.**  The complete looped 112-state example with
   `u=v=e_s` has rate 112 but only the diagonal path `(s,s)` at horizon one.
   Thus a claim covering every horizon would be false.  The eventual-active-
   residue formulation avoids that overclaim; horizon two already has the
   wall in this example.

9. **Weighted or repeated-label lifts.**  The Perron inequalities use that
   each adjacency entry is zero or one.  Parallel multiplicity or weights can
   raise the spectral radius without enlarging physical neighborhoods, and
   repeated states can assign different correction values to the same cell
   label.  Neither is covered.

10. **Research consequence.**  The result closes a model lane; it gives no
    admissible local EHPS potential, integer transfer, improved `r_3(N)`
    exponent, or solution of Problem 142.

## Exact replay

Run

```powershell
python -I verify_endpoint_pruned_extension.py
python -I independent_replay.py
```

Expected decisive lines:

```text
PASS_ENDPOINT_PRUNED_EXTENSION
SANDWICH_FREE_CORE_BOUND rho<=103<441/4
POSITION_DEPENDENT_LABEL_TABLES_OK exact_two_path_cancellation
FINITE_HORIZON_CAVEAT_OK complete112_fixed_endpoint_horizon1
PASS_INDEPENDENT_ENDPOINT_PRUNED_REPLAY
```

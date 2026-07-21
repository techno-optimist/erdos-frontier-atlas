# Fiber spectrum probe on Alpöge's map

Date: 2026-07-20

## Quantity

`jc-fiber-count-spectrum-size` in `atlas/jc-crater/quantities.json`:
number of distinct fiber cardinalities of the certified dim-3 Keller
counterexample. Ledger bracket **[3, 4]** (values in `{0,1,3}` known; `2` open).

## Exact probe

`probe_fiber_size2_exact.py` counts fibers at rational points of the
non-properness set \(V(E)\) (including all literature anchors), using
resultant-gcd fiber solving over \(\mathbb Q\) for every rational root of the
fiber cubic \(G_1\).

### Result (v1)

| fiber size | points |
|--:|--:|
| 0 | 4 |
| 1 | 95 |
| 2 | **0** |
| 3 | 0 |

99 points. Artifact: `FIBER_SIZE2_EXACT.json`.

### Result (v2, expanded sample)

| fiber size | points |
|--:|--:|
| 0 | 10 |
| 1 | 239 |
| 2 | **0** |
| 3 | 0 |

**249** distinct rational points on \(V(E)\). Incomplete \(y\)-factorizations:
**0**. Artifact: `FIBER_SIZE2_EXACT_V2.json`. Status:
`NO_SIZE_2_IN_EXACT_PROBE`.

### Additional slices (same engine)

| sample | points | hist | artifact |
|--------|--:|------|----------|
| dense \(Q=0\) | 276 | {0:10, 1:266} | `FIBER_Q0_SLICE.json` |
| \(t_2=0\) | 171 | {1:171} | `FIBER_T2_ZERO.json` |

No size-2 hits. Incomplete \(y\)-factorizations: 0 on every sample.

## Structural fence (2026-07-21 push)

See [`THEOREM_FIBER_NO_SIZE2_ON_VE.md`](THEOREM_FIBER_NO_SIZE2_ON_VE.md).

Proposed argument: on all of \(V(E)\), \(\#F^{-1}(t)\in\{0,1\}\) because

1. \(\Phi_x\) forces a unique \(x_*\) off the cusp (empty fiber on the cusp);
2. the multiple root of \(G_1\) never lifts (\(R_{12}\) identity);
3. hence at most one \(y\)-root lifts, at most once.

If accepted, spectrum \(=\{0,1,3\}\) and `jc-fiber-count-spectrum-size` closes
to **3**. This package does **not** auto-update the ledger.

Rational samples (prior + consolidated): still **zero** size-2 hits; shape
`rat_y=1,leftover=2` is empty on rational \(V(E)\).

## Scope

Prior text: samples alone are not a familywise no-go.  
New text: structural non-lifting argument is proposed, conditional on anatomy
annihilators, pending human review of the case-split.

## Replay

```sh
python3 -I probe_fiber_size2_exact.py
python3 -I probe_fiber_q0_slice.py
python3 -I probe_fiber_t2_zero.py
python3 -I _tiny_run_core.py
python3 -I probe_fiber_no_size2_ve.py
python3 -I probe_fiber_two_y_lemma.py
python3 -I probe_fiber_size2_push.py
```

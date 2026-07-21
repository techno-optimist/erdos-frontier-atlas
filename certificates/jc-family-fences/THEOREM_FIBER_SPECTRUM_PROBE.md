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

## Scope

This is **not** a proof that size-2 fibers are absent — only that none occur
among this rational sample of \(V(E)\). Closing the bracket still needs either
an exhibited size-2 fiber (possibly with irrational coordinates) or a
familywise certificate on \(V(E)\setminus\gamma\).

## Replay

```sh
python3 -I probe_fiber_size2_exact.py
```

# JC family fences (2026-07-20)

**Conditional** on Alpöge's dim-3 Keller counterexample (awaiting confirmation).
These are **probes / family fences**, not closed brackets. They extend the
anatomy map in [`../jc-anatomy/`](../jc-anatomy/) without reopening frozen
certificates.

## Scoreboard

| quantity | ledger | this package |
|----------|--------|--------------|
| `jc-fiber-count-spectrum-size` | [3, 4] | **no size-2** on **249** rational pts of \(V(E)\) (exact) |
| `jc-min-counterexample-degree-dim3` | [3, 7] | **no** const-Jac map of deg 3–6 in the \(k=2\) Alpöge-shaped integer box |
| plane JC / geometric deg 2 | open | untouched |

## Artifacts

| file | role |
|------|------|
| `probe_fiber_size2_exact.py` | exact fiber counts on rational points of \(V(E)\) |
| `FIBER_SIZE2_EXACT.json` | v1: 99 pts → hist `{0:4, 1:95}` |
| `FIBER_SIZE2_EXACT_V2.json` | v2: **249** pts → hist `{0:10, 1:239}`, incomplete \(y\)-factors 0 |
| `THEOREM_FIBER_SPECTRUM_PROBE.md` | write-up |
| `search_degree_family.py` | Alpöge-shaped family engine (exact monomials) |
| `probe_const_jac_family.py` | \(k=2\) box + thin \(k=3\) neighborhood |
| `CONST_JAC_K2.json` | 78 125 maps screened, 0 const-Jac in deg 3–6 |
| `THEOREM_DEGREE_FAMILY_PROBE.md` | write-up |

## Replay

Stdlib only (`fractions`). From this directory:

```sh
python3 -I probe_fiber_size2_exact.py          # regenerates FIBER_SIZE2_EXACT.json
python3 -I probe_const_jac_family.py           # regenerates CONST_JAC_K2.json (~minutes)
```

The expanded 249-point sample is the committed `FIBER_SIZE2_EXACT_V2.json`
(regenerate by widening ranges in `points_on_E()` or replaying the session
script that produced it).

## Honest scope

- Fiber probe is **not** a familywise no-go for size-2 fibers. Closing
  `jc-fiber-count-spectrum-size` still needs either an exhibited size-2 fiber
  (possibly irrational) or a parametrized certificate on \(V(E)\setminus\gamma\).
- Degree probe is a **fence inside one family**, not a proof that no degree-6
  dim-3 Keller counterexample exists.
- Do **not** mint DOI or promote provisional → certified on these alone.
- Root claim remains external / awaiting confirmation.

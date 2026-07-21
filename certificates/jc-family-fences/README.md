# JC family fences (2026-07-20)

**Conditional** on Alpöge's dim-3 Keller counterexample (awaiting confirmation).
These are **probes / family fences**, not closed brackets. They extend the
anatomy map in [`../jc-anatomy/`](../jc-anatomy/) without reopening frozen
certificates.

## Scoreboard

| quantity | ledger | this package |
|----------|--------|--------------|
| `jc-fiber-count-spectrum-size` | [3, 4] | **no size-2** on samples; **proposed structural fence** on \(V(E)\) (review) |
| `jc-min-counterexample-degree-dim3` | [3, 7] | **no** const-Jac deg 3–6 in k=2 box **and** k=3 near/free boxes |
| plane JC / geometric deg 2 | open | untouched |

### Fiber samples (exact resultant-gcd)

| sample | points | hist | size-2 |
|--------|--:|------|--:|
| global v1 | 99 | {0:4, 1:95} | 0 |
| global v2 | 249 | {0:10, 1:239} | 0 |
| Q=0 dense | 276 | {0:10, 1:266} | 0 |
| t2=0 slice | 171 | {1:171} | 0 |
| y-shape sample | 205 | {0:10, 1:195} | 0 |
| dense param | 467 | {0:10, 1:457} | 0 |
| two-y soft | 631 | {0:12, 1:619} | 0 |

Shape note: whenever G1 has 2 distinct rational y-roots, fiber size was always
1 with lift pattern `1+0` or `0+1` — never `1+1`. Structural reason (2026-07-21):
the **double root never lifts** (\(R_{12}\) identity); see
`THEOREM_FIBER_NO_SIZE2_ON_VE.md`.

### Degree family fences

| family | scanned | const-Jac deg 3–6 | CE hits |
|--------|--:|--:|--:|
| k=2 coeffs ∈ {-2..2} | 78 125 | 0 | 0 |
| k=3 Alpöge (e,f,g) neighborhood | 800 | 0 | 0 |
| k=3 free small (a..g) | 217 728 | 0 | 0 |

## Artifacts

| file | role |
|------|------|
| `probe_fiber_size2_exact.py` | global rational points on \(V(E)\) |
| `FIBER_SIZE2_EXACT.json` / `_V2.json` | global samples |
| `probe_fiber_q0_slice.py` + `FIBER_Q0_SLICE.json` | dense Q=0 sample |
| `probe_fiber_t2_zero.py` + `FIBER_T2_ZERO.json` | t2=0 slice |
| `probe_fiber_no_size2_ve.py` + `FIBER_NO_SIZE2_VE*.json` | structural no-size-2 fence |
| `probe_fiber_two_y_lemma.py` + `FIBER_TWO_Y_LEMMA.json` | double-root non-lifting |
| `probe_fiber_size2_push.py` + `FIBER_SIZE2_PUSH.json` | shape×fiber push |
| `search_degree_family.py` | Alpöge-shaped family engine |
| `probe_const_jac_family.py` + `CONST_JAC_K2.json` | k=2 box |
| `probe_const_jac_k3_near.py` + `CONST_JAC_K3_NEAR.json` | k=3 near/free |
| `THEOREM_*.md` | write-ups |

## Replay

```sh
python3 -I probe_fiber_size2_exact.py
python3 -I probe_fiber_q0_slice.py
python3 -I probe_fiber_t2_zero.py
python3 -I _tiny_run_core.py
python3 -I probe_fiber_no_size2_ve.py
python3 -I probe_fiber_two_y_lemma.py
python3 -I probe_fiber_size2_push.py
python3 -I probe_const_jac_family.py      # ~minutes
python3 -I probe_const_jac_k3_near.py
```

## Honest scope

- Prior fiber probes were samples only. The 2026-07-21 push adds a
  **proposed structural fence** (double-root non-lifting + forced \(x\)); ledger
  close to spectrum size 3 is a **review decision**, not auto-claimed here.
- Degree probes fence **one parametric shape** only.
- Root claim remains external / awaiting confirmation.

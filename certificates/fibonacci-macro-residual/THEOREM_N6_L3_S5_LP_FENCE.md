# n=6 L=3 S=5: routable but Parikh-LP resistant (sample fence)

Date: 2026-07-21

## Status

**Not a no-go.** Exhaustive search over \(5^{15}\) clocks is open.

What is sealed from machine samples:

1. **Routable assignments exist** at S=5 (first seed:
   `N6_L3_S5_FIRST_ROUTABLE.json`).
2. On that seed clock, exhausting all dig/port combos yields **1** routable
   assignment among 288 outward-legal; it is **LP-infeasible**.
3. Seed+mutation+random hunt (`search_n6_s5_from_seeds.py`):
   - 57 routable assignments found
   - **57 / 57 LP-infeasible** (0 LP hits)
   - 5000 mutations of the first seed + 3000 random high-zero clocks

## Interpretation

S=5 unlocks **local L=3 routing** for n=6 (which S=3 and S=4 do not, at
outward or LP respectively), but the Fibonacci weight vector still fails the
real-relaxation Parikh balance in every routable cell examined so far.

Contrast n=5 S=4: first few routables were LP-infeas, then an LP+integer hit
appeared. Here the sample is larger (57) with still zero LP.

## Artifacts

| file | role |
|------|------|
| `N6_L3_S5_FIRST_ROUTABLE.json` | first routable seed |
| `N6_L3_S5_CLOCK0_EXHAUST.json` | full dig/port on that clock |
| `N6_L3_S5_SEED_HUNT.json` | mutation hunt stats |
| `search_n6_s5_from_seeds.py` | replay hunt |

## Replay

```sh
python3 search_n6_s5_from_seeds.py
```

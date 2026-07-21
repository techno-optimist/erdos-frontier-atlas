# n=7 common-anchor macros — sealed lower bounds & open cells

Date: 2026-07-21

## Goal

Minimal \((L,S)\) for a common-anchor, split-weight, globally Parikh-balanced
Fibonacci macro on the primitive `n=7` circuit (8 tags; Fib weights through
\(F_7=21\); 14 columns).

## Sealed no-gos (do not re-prove)

| cell | obstruction | artifact |
|------|-------------|----------|
| **any L, S=3** | port capacity ≤7 under L≤3 reachability | `THEOREM_N_GE_7_S3_PORT_CAPACITY.md` |
| **L=3, S=4** | 0 of 55 296 outward-legal assignments are fully L=3-routable | `THEOREM_N7_L3_S4_NO_GO.md`, `N7_L3_S4_COMPLETE.json` |

## Port capacity for S≥4 (not a no-go)

From consolidated samples `PORT_CAPACITY_N7_GE8_SUMMARY.json`:

| S | L (reach filter) | ≥8 ports? |
|--:|--:|:--|
| 4 | 3 (exhaustive) | **yes** (6 972 clocks) |
| 5 | 3,4,5 (sample) | **yes** (max ports 9–10 in sample) |
| 6 | 4 (sample) | **yes** |

So n=7 is **not** killed by ports once \(S\ge 4\). The L=3 S=4 death is
**local routability**, not ports.

## Sealed positive ladder (context)

| n | minimal known witness \((L,S)\) |
|--:|--|
| 3 | (3,3) |
| 4 | (3,3) |
| 5 | (3,4) |
| 6 | (4,5) |

## Open cells (n=7)

Minimal \((L,S)\) is open. Suggested attack order (implemented in `mine_n7.py`):

1. L=3 S=5 — routes may exist; Parikh-LP status unknown
2. L=3 S=6
3. L=4 S=5 — natural lift of the n=6 witness clock (needs ≥1 extra anchor port;
   sealed n=6 δ has only **7** ports)
4. L=5 S=5
5. L=4 S=6

## Morphogenesis note

The sealed n=6 L=4 S=5 clock (`N6_L4_S5_WITNESS.json`) has exactly 7
anchor-returning ports — one short of the 8 tags for n=7. Any S=5 attempt must
**mutate** δ (or lengthen L / grow S) to free an eighth port; pure reuse of the
n=6 port assignment is impossible.

### Preferred dig lift (hand-checked)

Extending the n=6 dig vector by one more `1`:

\[
\mathrm{digs} = (2,2,2,1,1,1,1,1)
\]

is **digit-legal** for all 14 n=7 columns (`|a+c-2b|≤1` on every origin). Need
5 ports of digit 1 and 3 of digit 2. On a one-entry port-boost of the n=6 clock
that creates `(1,1)` (set \(\delta(1,1)=0\)), the anchor port multiset is exactly
5 dig-1 + 3 dig-2, so port assignments exist (≤ \(5!\,3! = 720\)).

Focused exhaust of all one-entry boosts: `exhaust_n7_n6boost.py`.

## Claim boundary

Finite machine classification fragments only. **Not** an Erdős #142 construction.

## Replay (hunt — requires highspy)

```sh
cd certificates/fibonacci-macro-residual
python mine_n7.py --mode ports --trials 80000
python mine_n7.py --mode hunt --budget 900
# or a single cell:
python mine_n7.py --mode hunt --L 4 --S 5 --budget 1200
```

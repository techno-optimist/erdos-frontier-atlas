# Port capacity on 4-state clocks (L≤3 reachable)

Date: 2026-07-20

## Theorem

Among all deterministic ternary clocks with **exactly four** states in which
every state is reachable from the anchor in at most L=3 steps, the number of
anchor-returning ports is **at most 9**.

Therefore common-anchor macros needing n+1 ≥ 10 tags (**n≥9**) are impossible
at S=4 under the L≤3 reachability filter.

## Census

Verifier: `verify_s4_port_capacity.py` (~4 min; recomputes all 16 777 216 clocks
and checks the stored artifact against the fresh census)  
Artifact: `PORT_CAPACITY_S4.json`

| ports | reachable clocks |
|--:|--:|
| 0–6 | (bulk) |
| 7 | 59 184 |
| 8 | 6 642 |
| 9 | **330** |
| ≥10 | **0** |

| n | tags | ge_tags (reachable) |
|--:|--:|--:|
| 5 | 6 | 373 110 |
| 6 | 7 | 66 156 |
| 7 | 8 | 6 972 |
| 8 | 9 | 330 |
| ≥9 | ≥10 | **0** |

Absolute max ports without reachability filter is 12; the reachability filter
is load-bearing for the n≥9 cut (as for S=3 / n≥7).

## Scope

Does not settle n=7,8 at S=4 (ports exist).

## Replay

```sh
python3 -I verify_s4_port_capacity.py
```

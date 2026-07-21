# No-go: n≥7 common-anchor macros on 3-state clocks (port capacity)

Date: 2026-07-20

## Theorem

In the common-anchor model on a deterministic ternary clock with **exactly
three states**, if every state is reachable from the anchor in at most
**L=3** steps, then the number of anchor-returning ports
\((s,d)\) with \(\delta(s,d)=0\) is **at most 7**.

The n-circuit uses **n+1** tags, each needing a distinct anchor-returning
port. Therefore **no such macro exists for any n≥7** at S=3 (needs ≥8 ports),
independent of route length and Parikh balance.

## Census

Verifier: `verify_s3_port_capacity.py`  
Result: `PORT_CAPACITY_S3.json`

| filter | max ports | clocks with ≥8 ports |
|--------|--:|--:|
| all 19 683 clocks | 9 | 19 |
| L≤3-reachable (15 930) | **7** | **0** |

| n | tags | ge_tags (reachable) |
|--:|--:|--:|
| 5 | 6 | 282 |
| 6 | 7 | 24 |
| 7 | 8 | **0** |
| 8 | 9 | **0** |

## Scope

- Reachability filter matches the standing model used by the n=3…6 censuses.
- Dropping reachability restores max ports 9; those clocks have dead states
  unused by L≤3 product walks from the anchor.
- Does not address S≥4.

## Replay

```sh
python3 -I verify_s3_port_capacity.py
```

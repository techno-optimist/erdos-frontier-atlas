# n=5 L=3 S=4: routable seeds exist; integer Parikh open

Date: 2026-07-20

## Positive routability

Searcher: `verify_n5_l3_s4_routability.py`  
Result: `N5_L3_S4_COMPLETE.json` status `FOUND_ROUTABLE`

First seed (clock_idx 298176):

```
delta = [[0,0,1],[0,2,0],[3,0,3],[0,0,0]]
ports: tag0=(3,0), tag1=(0,0), tag2=(1,0), tag3=(3,1), tag4=(0,1), tag5=(2,1)
digs = (0,0,0,1,1,1)
```

Every Fibonacci column admits at least one legal length-3 return to its
target anchor ports with the required carry. So **S=4 unlocks local
routability** that S=3 forbids.

## Integer / Parikh

`recover_n5_l3_s4_witness.py` on that seed: **MIP_INFEAS** (route counts
2,1,2,4,6,2,2,1,11,2 for the ten columns). Routable ≠ Parikh-balanced.

`search_n5_l3_s4_integer.py` continues the census, LP-filters then MIP on
every subsequent routable assignment.

## Scope

- Not yet a sealed integer macro witness.
- Not exhaustive no-go (search in progress).
- Finite machine model only; not E142.

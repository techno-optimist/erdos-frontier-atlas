# Exact n=4 length-three split-weight macro witness

Date: 2026-07-20

## Result

The primitive `n=4` Fibonacci tag circuit with weights

```
(P0,Q0,P1,Q1,P2,Q2,P3,P4) = (1,1,1,1,2,2,3,5)
```

admits a legal deterministic **three-state**, **length-three**, common-anchor,
globally Parikh-balanced macro realization.  Split unit routes realize the
weights 2, 2, 3, and 5.

## Clock

```
delta(0,*) = (0,0,1)
delta(1,*) = (2,0,2)
delta(2,*) = (0,0,0)
```

Tag ports (five injective, all return to anchor under `delta`):

```
0↦(2,0), 1↦(0,0), 2↦(2,1), 3↦(0,1), 4↦(1,1)
```

## Verified properties

Independent verifier `verify_n4_l3_macro_witness.py` (reads sealed
`N4_L3_WITNESS.json`, does not import the searcher):

| check | status |
|---|---|
| carry legality | pass |
| outward to anchor + matching carries | pass |
| return terminals = tag state triples | pass |
| unit counts = Fibonacci weights | pass |
| weighted product flow boundary zero | pass |
| weighted AP tag column zero | pass |
| three return-role Parikh measures equal | pass |
| weak connectivity from the anchor | pass |

Status: `PASS_N4_L3_SPLIT_MACRO_WITNESS`.

## Relation

| cell | status |
|---|---|
| n=2, L=2 | witness |
| n=3, L=2 | no-go (all clocks) |
| n=3, L=3 | witness |
| **n=4, L=3** | **witness (this packet)** |

So length-three common-anchor split macros are **not an n=3 accident** — they
already form a multi-n family at fixed L=3 and S=3.

## Scope

Not an all-n inductive proof, not unbounded depth, not an Erdős 142 bound.

## Replay

```powershell
python verify_n4_l3_macro_witness.py
```

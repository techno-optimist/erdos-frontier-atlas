# Exact n=3 length-three split-weight macro witness

Date: 2026-07-20

## Result

The primitive `n=3` Fibonacci tag circuit with weights

```
(P0,Q0,P1,Q1,P2,P3) = (1,1,1,1,2,3)
```

and origins

```
P0=(1,0,3), Q0=(0,1,3), P1=(2,1,0), Q1=(1,2,3), P2=(2,2,1), P3=(3,3,2)
```

admits a legal deterministic **three-state**, **length-three**, common-anchor,
globally Parikh-balanced macro realization.  Weights 2 and 3 are realized by
**split unit routes** (two distinct unit returns for `P2`, three for `P3`).

## Clock

States `{0,1,2}`, anchor state `0`:

```
delta(0,0)=0, delta(0,1)=0, delta(0,2)=1
delta(1,0)=0, delta(1,1)=0, delta(1,2)=2
delta(2,0)=0, delta(2,1)=2, delta(2,2)=0
```

Tag ports (injective, all return to the anchor under `delta`):

```
0 ↦ (0,0),  1 ↦ (2,0),  2 ↦ (1,0),  3 ↦ (0,1)
```

Outward carries:

```
(P0,Q0,P1,Q1,P2,P3) = (-1,-1,0,-1,0,+1)
```

## Unit return routes

Each row is three successive return digit triples (roles 0,1,2).  After the
three return steps the clock state triple equals the origin's tag states and
the carry equals the outward carry; the subsequent outward edge closes at the
diagonal carry-zero anchor.

```
P0 : (0,2,1),(2,2,0),(2,2,0)
Q0 : (0,2,1),(2,2,0),(0,1,0)
P1 : (1,0,2),(1,2,2),(2,2,2)
Q1 : (2,1,0),(2,1,0),(1,2,0)
P2a: (0,1,2),(1,0,2),(2,2,1)
P2b: (0,2,1),(1,1,2),(2,2,2)
P3a: (0,1,2),(0,0,0),(1,0,2)
P3b: (2,0,1),(1,0,1),(0,0,2)
P3c: (2,2,2),(2,0,1),(2,1,2)
```

## Verified properties

Independent standard-library verifier `verify_n3_l3_macro_witness.py`:

| check | status |
|---|---|
| carry legality on every edge | pass |
| outward to anchor, matching carries | pass |
| return terminals = tag state triples | pass |
| weighted product flow boundary zero | pass |
| weighted AP tag column zero | pass |
| three return-role complete-port Parikh measures equal | pass |
| weak connectivity from the anchor | pass |

Result artifact: `N3_L3_MACRO_WITNESS_RESULT.json`  
status `PASS_N3_L3_SPLIT_MACRO_WITNESS`.

## Relation to the residual class

| cell | status |
|---|---|
| n=2, L=2 | **witness** (prior) |
| n=3, L=2, S≤4 | **no-go** (exact census + real LP) |
| n=3, L=3, S=3 | **witness** (this packet) |

Thus length two is not a universal no-go for n=3 — only the short-return
regime is blocked at small clocks — while length three is constructively
possible with split weights.

## Scope

- Not an all-`n` family.
- Not a proof of unbounded depth / superquadratic primitive mass.
- Not an Erdős 142 solution.
- Does not by itself produce a 3-AP-free density bound.

## Replay

```powershell
python verify_n3_l3_macro_witness.py
python recover_n3_l3_integer.py   # regenerates the sealed routes via MIP
```

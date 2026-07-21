# Classification: common-anchor L=3 macros for S ≤ 4

Date: 2026-07-21

## Theorem (finite census)

In the common-anchor, split-weight, deterministic ternary-clock model with
return length **L=3** and clock size **S ≤ 4**, with every state L-reachable
from the anchor, the **only** (n,S) pairs admitting a Parikh-balanced
Fibonacci macro are:

| n | S | status |
|--:|--:|--------|
| 3 | 3 | **WITNESS** (`verify_n3_l3_macro_witness.py`) |
| 4 | 3 | **WITNESS** (`verify_n4_l3_macro_witness.py`) |
| 5 | 4 | **WITNESS** (`verify_n5_l3_s4_macro_witness.py`) |

All other pairs with 3 ≤ n ≤ 8 and S ∈ {3,4} are **no-go** by exhaustive
machine census (or port-capacity theorem).

## Proof sketch by cases

### Port capacity

- S=3, L≤3-reachable: max anchor ports = 7 ⇒ **n≥7 impossible**  
  (`verify_s3_port_capacity.py`, `THEOREM_N_GE_7_S3_PORT_CAPACITY.md`)
- S=4, L≤3-reachable: max anchor ports = 9 ⇒ **n≥9 impossible**  
  (`PORT_CAPACITY_S4.json`, `THEOREM_S4_PORT_CAPACITY.md`)

### S=3, n=3…6

| n | verdict | obstruction | artifact |
|--:|---------|-------------|----------|
| 3 | WITNESS | — | `THEOREM_N3_L3_SPLIT_MACRO_WITNESS.md` |
| 4 | WITNESS | — | `THEOREM_N4_L3_SPLIT_MACRO_WITNESS.md` |
| 5 | NO-GO | 0 routable / 864 outward | `THEOREM_N5_L3_S3_NO_GO.md` |
| 6 | NO-GO | 0 outward / 24 ge_tags | `THEOREM_N6_L3_S3_NO_GO.md` |

Also n=5 at S=3 for L=4,5: NO-GO (`THEOREM_N5_L4_S3_NO_GO.md`, `N5_L5_S3_COMPLETE.json`).  
n=6 at S=3 for L=4,5: NO-GO (`N6_L4_S3_COMPLETE.json`, `N6_L5_S3_COMPLETE.json`) — same 24 ge_tags, 0 outward.

### S=4, n=5…8

| n | verdict | obstruction | artifact |
|--:|---------|-------------|----------|
| 5 | WITNESS | — | `THEOREM_N5_L3_S4_SPLIT_MACRO_WITNESS.md` |
| 6 | NO-GO | 72 routable, 0 LP | `THEOREM_N6_L3_S4_NO_GO.md` |
| 7 | NO-GO | 0 routable / 55 296 outward | `THEOREM_N7_L3_S4_NO_GO.md` |
| 8 | NO-GO | 0 outward / 330 ge_tags | `THEOREM_N8_L3_S4_NO_GO.md` |

### Residual open (outside this theorem)

- S≥5 any n
- L≠3 (except the listed S=3 L=4,5 no-gos for n=5,6)
- Non-common-anchor architectures

## Scope

Finite combinatorial classification inside the standing model. **Not** an
Erdős #142 density statement.

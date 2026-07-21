# Family notes — L and S both grow

Date: 2026-07-21

## Known witnesses

| n | L | S | artifact |
|--:|--:|--:|----------|
| 3 | 3 | 3 | `verify_n3_l3_macro_witness.py` |
| 4 | 3 | 3 | `verify_n4_l3_macro_witness.py` |
| 5 | 3 | 4 | `verify_n5_l3_s4_macro_witness.py` |
| 6 | **4** | **5** | `verify_n6_l4_s5_macro_witness.py` |

## Pattern

- Fixed L=3: S≤4 classified — only (3,3),(4,3),(5,4).
- n=6 at L=3 S=5: routes exist, Parikh-LP fails on 57/57 sample cells.
- n=6 at **L=4 S=5** on the same clock: **integer witness**.

Hypothesis: minimal resources grow roughly like S ≥ ⌈n/2⌉+1 or similar;
L may need to increase when S is barely large enough for ports/routing.

## Next

- n=7 minimal (L,S) — lower bounds sealed (`THEOREM_N7_LOWER_BOUNDS.md`):
  - S=3 impossible (ports); L=3 S=4 impossible (0 routable)
  - S≥5: ports exist (sample); integer open
  - sealed n=6 clock has only 7 ports (need 8 tags) → must mutate/pad
  - hunter: `python mine_n7.py --mode hunt`
  - verifier (when witness appears): `python verify_n7_macro_witness.py`
- n=6 L=3 S≥6 or prove L=3 impossible for n=6

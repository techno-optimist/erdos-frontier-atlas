# q=24 cylinder hypograph exact Farkas wall (#142)

**Finite quotient fence only.** Does **not** set `new_r3_bound`, does **not**
continuum-certify, does **not** crack Erdős #142.

## Claim

For the top D4 mass assignment `(7,7,7,6,7)` on five product cylinders with
geometry `A = D4_7(T)`, `C = D4_6(T)` (`|T|=163`, `A ∩ C = ∅`), the **integral
local-hypograph** master LP on 2820 variables (2445 position potentials + 375
local slacks) is **infeasible**.

An exact nonnegative Farkas combination of 662 local hypograph rows + all 125
triple-sum rows yields coefficient cancellation on all variables and a **positive**
RHS contradiction.

Union mass count `5·163³ = 21,653,735` strictly exceeds the threshold
`7³·24³ = 4,741,632`.

## Files

| file | role |
|---|---|
| `certificate.json` | semantic packet (`erdos142-q24-cylinder-hypograph-farkas-v1`) |
| `verify.py` | stdlib-only semantic verifier + planted corruption self-test |
| `independent_replay.py` | separately written stdlib-only reconstruction and exact cross-check |

Expected `certificate.json` SHA-256:

```
4F6344025D672E6A6E631BB34B86250AD6423A89EC9C03BF5109AE76EC6C65C8
```

## Verify

```bash
python -I verify.py --self-test
python -I independent_replay.py
# → PASS_Q24_CYLINDER_HYPOGRAPH_EXACT_FARKAS
# → PASS_INDEPENDENT_Q24_D4_CYLINDER_POSITION_REPLAY
```

## Scope honesty

- Additive role-potential walls (`mirror-core`, `d4-role-distinct`) are **separate**.
- This kills the **hypograph / cylinder-position local-slack** factorization of the
  five-cylinder ansatz at q=24 for this assignment — not every conceivable 6D /
  recursive potential.
- Wall A remains STANDING until a verified continuum / r₃ improvement lands.

## Discovery provenance

- Scratch: `D:/p42_research/erdos142_five_role_qp_20260817/terra_cylinder_ansatz_audit/`
- CEGAR: `hypograph_cegar.py` → `runs/terra_hypograph_a_q24/`
- Offline membrane tick: `erdos142_walls_down_offline_20260817/attack_ticks/*_cylinder_hypograph_exact_farkas.md`

# Erdős #142 — H1–H5 constant ceiling, and the pressure-to-one exclusion

**Type: fence (a wall, not a bound).** Replay:

```bash
python3 -I verify.py
```

## Boundary first

**Certified here** (exact `Fraction`/integer arithmetic, no float in the
trust path, ten planted-failure controls that must fail):

- **C1.** The candidate return rate
  `λ = 65789102774707418182759/222090924810025888000000` satisfies
  `λ > 7/24` — an exact rational comparison. Since the constant map is
  strictly decreasing in `λ`, this says precisely: *this rate would give a
  constant strictly better than the EHPS 2024 baseline 2.666539…, **if** a
  survivor certificate for it existed.* No such certificate exists.
- **C2a.** `Λ_cap = (θ₃/3)² ≤ 211/250`, where
  `θ₃ = min_{x>0} (1+x+x²)/x^{2/3}`. Certified by a purely rational
  inequality: evaluating the objective at a rational witness `x₀` gives
  `θ₃³ ≤ R = (1+x₀+x₀²)³/x₀²` (the cube clears the cube root), and
  `Λ_cap ≤ U` follows from `R² ≤ (9U)³`.
- **C2b — the exclusion.** Any family whose spectral pressure obeys
  `1 − ρ(m) ≤ 2/(3m) + 11/(6m²)` has `ρ(m) ≥ 85/98 > 211/250 ≥ Λ_cap`
  for every `m ≥ 7`. Such a family **exceeds the ceiling and therefore
  cannot be an H1–H5 survivor.**

**Not certified here** (stated so a reader hits it before the conclusions):

- The constant map `c = 2·√(log₂(1/λ))` for an H1–H5 survivor with
  anchored-reservoir return rate `λ`.
- The ceiling `Λ_cap` on `λ` for any H1–H5 survivor, which follows from
  the published Ellenberg–Gijswijt cap-set bound together with a Fubini +
  periodic Perron–Frobenius argument.

Both are **external** to this repository. In their home lane they are
*sealed-by-audit* — rigorous human mathematics with machine-checked
exact-algebra controls and rejected hostile mutations — but they are **not
formalized in a proof assistant and are not re-derived here.** If either is
wrong, the conclusions below are void. What this certificate checks is the
arithmetic and the exclusion logic that follow from them. The pressure
bracket in C2b is likewise an external proved input for one specific
family; here it is treated as a *hypothesis*, so C2b is a statement about
**any** family satisfying that bracket.

**Not claimed:** no `r_3(N)` lower bound, no improvement on EHPS, no
survivor certificate. `erdos142_solved: false`.

## Why this is worth mapping

Erdős #142 asks for the asymptotic behaviour of `r_3(N)`. Within the H1–H5
framework the achievable lower-bound constant is governed by one number,
the survivor's return rate `λ`, through a map that is strictly decreasing
in `λ`. That gives a clean ladder:

| rate | constant `c = 2√(log₂(1/λ))` | meaning |
|---|---|---|
| `λ → 7/24 = 0.291667` | 2.666539014275660 | EHPS 2024 baseline — must be beaten |
| `λ = 0.296226` (candidate) | 2.649701794028334 | better, **conditional on a certificate that does not exist** |
| `λ ≤ Λ_cap = 0.843400` | floor **0.991384489945289** | hard wall for *any* H1–H5 survivor |

Two consequences follow, and they are the point of this certificate:

1. **The framework can move the constant, but never the order.** No H1–H5
   survivor may exceed `Λ_cap`, so no survivor's constant can fall below
   ≈0.9914. The `√log N` *order* is untouchable here — the headline
   asymptotic question is not reachable by this route, however good the
   geometry.
2. **"Pressure → 1" is self-defeating.** A natural design intuition is to
   push the spectral pressure of a candidate geometry toward 1. C2b shows
   the opposite: any family with `1 − ρ(m) = O(1/m)` sits strictly *above*
   the ceiling for all `m ≥ 7`, and driving `ρ → 1` only widens the
   violation. Such families are excluded outright, and compute spent
   pushing pressure upward is compute wasted.

Point 2 is not hypothetical: it retired a family that had passed every
screening test we could build for it (census, criterion, torsion audits,
lifted-geometry probes) and whose pressure limit we had *proved*. The
proof of `1 − ρ(m) = Θ(1/m)` turned out to be the disqualification.

## Files

| file | role |
|---|---|
| `verify.py` | the checker: C1, C2a, C2b + ten planted-failure controls (four arithmetic, six artifact-drift); exact arithmetic throughout |
| `constants.json` | committed artifact — **every** field re-derived and drift-checked by the replay, never regenerated; no timing fields |

The artifact check is total, not a spot-check: each field of `constants.json`
— including the prose fields, whose numbers are rendered from the same
`Fraction`s the checker uses — is re-derived and compared, and the keyset is
enforced in **both** directions, so a field added later fails the replay
instead of silently escaping the check. The five `display_only_decimals` are
the sole exception to exact comparison: they are 16-digit roundings of
irrational quantities, so they are re-derived at 60 digits and compared at a
labelled `1e-15` relative tolerance. Nothing in the trust path reads them.

## Provenance and claim-typing

- **Ours:** the exclusion argument (C2b), the rational ceiling bound
  technique (C2a), the arithmetic, this certificate.
- **External, published:** the Ellenberg–Gijswijt cap-set bound underlying
  `Λ_cap`; the EHPS 2024 baseline constant.
- **External, sealed-by-audit, conditional:** the constant map and the
  ceiling derivation (see "Not certified here").
- **Search-bounded negatives** are fences, not proofs, and are labelled as
  such throughout.

# Erdős 142 / D15 — the cone obstruction, certified

**Claim boundary: `erdos142_solved = false`, `new_r3_bound = false`.**
This is a structural obstruction inside one construction programme. It is
**not** an r₃(N) bound, and it does not solve #142.

Replay:

```bash
python3 -I verify.py
```

Standard library only; no imports from elsewhere in this repository and no
dependency on the (unpublished) sealed D15 engine. Every product is rebuilt
from its canonical form, every number recomputed in exact rational arithmetic.
A few seconds.

---

## What this certifies

The lane's construction gate ("Wall B") needs a closed carry-triple product
with quotient signature `(q⁺,q⁻) = (1,0)` **and** a cone certificate.

The **first** half exists — 298 verified objects, the sealed engine's own
`rank_gate` returning quotient dimension 1 with `passes_quotient_one = True`.
That closed a hole the lane had treated as structural: `q = 1` had been absent
from >1.18M closed products and was described as "the unique absent value in
0..24". It was a search-region artifact.

This certificate is about the **second** half. The cone seeks an integer edge
weighting `w` with

- `w` constant on endpoint-swap (σ) orbits,
- `w ≥ 0` on diagonal ("collar") edges, `w ≥ 1` on every non-diagonal edge,
- flow conservation at every product vertex,
- zero `coarse24` tag.

A solver reporting INFEASIBLE is an assertion. This replaces it with a proof.

## The certificate

For each object we publish a vertex potential `p` and a tag multiplier `θ`.
Define the edge functional

```
Y(e) = p[target(e)] − p[source(e)] + ⟨θ, tag(e)⟩
```

If `Y ≥ 0` on every edge and `Y > 0` on every non-diagonal edge, the cone is
empty: any cone point `w` is a circulation (so the potential telescopes to 0)
with zero tag (so the `θ` part vanishes), hence

```
0 = Σ_e Y(e)·w(e)  ≥  Σ_{e non-diagonal} Y(e)  >  0
```

using only `w ≥ 0` and `w ≥ 1` off the collar — a contradiction.

**What the argument does not use:** no solver, no coefficient cap, no
integrality, no σ-invariance, and no reference to `q`. One line, auditable by
hand.

## Objects

| sha256 | states | V | E | non-diag | q | `min Y` off collar |
|---|---|---|---|---|---|---|
| `7891ae0b…` | 14 | 35 | 52 | 22 | 1 | `2/13` |
| `ad102f6c…` | 14 | 38 | 62 | 22 | 1 | `2/13` |
| `1d4dc69a…` | 15 | 44 | 65 | 22 | 1 | `2/13` |

`7891ae0b…` is the smallest known `(1,0)` object.

## Why σ-invariance is absent from the argument

Worth recording, because the programme spent effort on it. Signature `(1,0)`
was pursued over `(0,1)` precisely to obtain a **σ-invariant** generator. A
relaxation ladder on the smallest witness shows symmetry was never the
blocker:

| relaxation | cone |
|---|---|
| baseline | INFEASIBLE |
| **drop σ-invariance** | **still INFEASIBLE** |
| drop zero-tag | feasible |
| drop non-negativity | feasible |
| drop `≥ 1` off the collar | feasible |

The conflict is **zero-tag + non-negativity + strict positivity**, and it
survives dropping symmetry entirely. Accordingly `Y` makes no use of σ.

*(Separately, and not certified here: σ-invariance can be shown free in
general — `x + σx` suffices, needing only that σ preserves diagonality and the
zero-tag space, not `q⁻ = 0`.)*

## Controls

`verify.py` fails loudly if any of these stop holding:

- every published quantity is **recomputed** and compared, never trusted;
- perturbing `θ` must break non-negativity or the `Z`-pairing;
- perturbing the potential must break non-negativity;
- mutating a base transition must break the pointed-simulation invariant;
- `Y` must annihilate a **full basis** of the zero-tag circulation space —
  not a sampled vector.

The `full36` transition table is embedded and hash-checked. Potentials are
keyed by **vertex tuple**, not index, so replay does not depend on any
particular BFS ordering.

## What is *not* claimed

- **Not** that every `q = 1` closed product has an infeasible cone. No such
  theorem is offered. Each certificate settles exactly one object.
- The lane separately measured collar-LP infeasibility across all 298 known
  `q=1` objects with the sealed engine agreeing 298/298 — a measurement over
  the objects found so far, not a proof about the class. It is **not**
  certified here.
- No r₃(N) bound, no movement on the constant, no survivor certificate.

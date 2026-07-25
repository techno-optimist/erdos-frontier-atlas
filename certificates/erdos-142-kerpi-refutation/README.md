# Erdős 142 / D15 — refutation of `ker π ∩ D = 0` and of `q ≥ dim ker π`

**Claim boundary: `erdos142_solved = false`, `new_r3_bound = false`.**
Nothing here is an r₃(N) bound. This certificate **refutes two lemmas** that
the D15/PC-F lane was operating under, **proves one** replacement theorem, and
supplies the exact identity that should be used in their place.

Replay:

```bash
python3 -I verify.py
```

Standard library only. No imports from elsewhere in this repository, and no
dependency on the (unpublished) sealed D15 engine — every object is rebuilt
from its canonical form and every number is recomputed in exact rational
arithmetic. Runtime: a few seconds.

---

## Setting

For a rooted deterministic base automaton `B` on the 36-state `full36` clock,
the **carry-triple product** `P` has vertices `(carry, q₀, q₁, q₂)` and an edge
per legal row `(a,b,c)`, legality being `carry + a + c − 2b ≡ 0 (mod 3)` with
successor carry `(carry + a + c − 2b)/3 ∈ {−1,0,1}`.

- `Z₁(P) = ker(incidence_P)` — the cycle space.
- **tags** — the 24-coordinate `coarse24` map on edges.
- `Z = ker(incidence_P) ∩ ker(tags)`.
- `D` — the **collar**: circulations supported on *diagonal* edges (rows
  `(a,a,a)` between vertices whose three role labels agree, carry 0 both ends).
- `q = dim Z − dim D` — the quotient dimension the lane is trying to control.
- `π = (π₀,π₁,π₂) : Z₁(P) → Z₁(B)³` — the three single-role projections.

The lane's open question is whether a closed product with **`q = 1`** exists
(0 occurrences in >1.18M closed products; the unique absent value in 0..24).
Two lemmas were being used as a route to prove `q ≠ 1`. Both are false.

---

## R1 — `ker π ∩ D = 0` is REFUTED

Stated for closed products (strongly connected, exit-free). It had been
verified per-object on every object previously examined, which is why it was
believed general.

Object `321b7cef…` (5 states, 216 vertices, 619 edges, closed) carries an
explicit nonzero integer circulation `d` on **4 collar edges** — the minimal
`e₁ − e₂ − e₃ + e₄` rectangle. `verify.py` checks it **directly against the
definition**, on the full product, not via any shortcut:

1. `d` is supported only on collar edges ⟹ `d ∈ D`;
2. `incidence_P · d = 0` at every one of the 216 vertices ⟹ `d` is a genuine
   circulation of `P`;
3. `π₀(d) = π₁(d) = π₂(d) = 0` ⟹ `d ∈ ker π`;
4. `d ≠ 0`.

Object `91f52f97…` (6 states, 319 vertices, 1088 edges, closed) likewise, with
`dim(ker π ∩ D) = 20`.

**Mechanism.** Per digit, a collar circulation is a 3-index array `d(q₀,q₁,q₂)`
and the three role projections are exactly its three **1-marginals**. The
kernel of "all three 1-marginals vanish" is large — its minimal elements have
support **4**: two diagonal cells against two cells of a transversal,
`d(1,1,1) + d(2,2,2) − d(1,2,1) − d(2,1,2)`, which is **not** a rank-one
tensor. (The 2×2×2 rank-one tensor `(e₁−e₂)^⊗3` has support 8 and is a sum of
two support-4 elements, so it is *not* minimal here — that circuit is minimal
for the kernel of the three **2**-marginals, a different problem.) Flow
conservation alone cannot close the gap.

**Scale** (reported by the referee lane, not re-derived here): 31,548
counterexamples among 873,264 closed products at ≤7 states.

---

## R2 — `q ≥ dim ker π` is REFUTED

This is the consequential one: it was the bridge from a floor on `dim ker π`
to a floor on `q`, i.e. the whole route to excluding `q = 1`.

Once R1 falls, `q ≥ dim ker π` loses its proof. It is in fact **false**, and
the reason is a **counting** bound rather than any large computation.

### The counting theorem

`ker π ⊆ Z` (the 24 tag coordinates are the three role port-histograms, which
`π` kills — verified here as **H2**: every tag row lies in the `π` row space).
So `ker(π|_Z) = ker π` exactly, and rank–nullity on `π` restricted to `Z` gives

```
    dim Z = dim ker π + rank(π|_Z)
```

With `q = dim Z − dim D` this is an **identity**, not an inequality:

> ### `q − dim ker π = rank(π|_Z) − dim D`

and since each `π_i` is induced by a graph morphism `P → B` (verified as
**H1**), `im π ⊆ Z₁(B)³`, so `rank(π|_Z) ≤ 3·dim Z₁(B)`. Therefore

> ### `dim D > 3·dim Z₁(B)`  ⟹  `q < dim ker π`

Both inputs are tiny and exactly computable.

### The witness

Object `91f52f97…`:

| quantity | value |
|---|---|
| base: `\|E(B)\| − \|V(B)\| + 1 = 13 − 6 + 1` | `dim Z₁(B) = 8` |
| `3·dim Z₁(B)` | **24** |
| collar edges | 60 |
| `dim D` (exact rational nullspace, 60 columns) | **34** |
| **bound on `q − dim ker π`** | **≤ −10** |

Hypotheses verified on the object rather than assumed: **H1** 0 morphism
violations over 1088 edges × 3 roles; **H2** `rank(π rows) = 37 =
rank(π rows + tag rows)`; **H3** `D ⊆ Z`, 0 failures.

The referee lane reports the exact values `q = 732`, `dim ker π = 748`
(gap −16), consistent with the bound since `rank(π|_Z) = 18 ≤ 24`. Those exact
values are **not** re-derived here — the certificate does not need them.

### Why the inequality had to fail

`dim Z₁(B)` depends only on the **base** — a small fixed number. `dim D` grows
with the product's **collar**. Once the collar outgrows three copies of the
base cycle space the inequality is dead. It was never structural; it held
because every object previously examined had a small collar.

**Consequence:** a floor on `dim ker π` proves nothing about `q`. The route
`dim ker π ≥ 2 ⟹ q ≥ 2 ⟹ q ≠ 1` is closed.

---

## P1 — THEOREM A (proved, and the replacement sufficient condition)

> If every collar edge of `P` has a **diagonal source vertex** `(0,u,u,u)`,
> then `ker π ∩ D = 0`.

*Proof.* A diagonal row `(a,a,a)` is legal only from carry 0, and the product
is deterministic, so a collar edge is determined by its (source, digit). If the
source is diagonal `(0,u,u,u)` then `π₀` sends that edge to the base edge
`(u,a)`, and `((0,u,u,u),a) ↦ (u,a)` is injective. So `π₀` maps the collar edge
**basis** injectively into the base edge basis, hence is injective on all of
`ℚ^{E(C)} ⊇ D`. ∎

Machine control (referee lane): **0 violations over 873,264 closed products.**

**The converse is FALSE.** Object `5da67053…` has non-diagonal collar source
vertices and still `ker π ∩ D = 0`. Source-diagonality is *sufficient, never
necessary* — so it must not be used as a classification. For a per-object
decision use the exact test

```
dim(ker π ∩ D) = |E(C)| − rank[ ∂ ; π₀ ; π₁ ; π₂ ]   on collar columns
```

(collars here are 11–60 edges: milliseconds, exact, strictly sharper).

---

## The four objects, and why each is present

| key | sha256 | states | `dim D` | `3·dim Z₁(B)` | `dim(ker π ∩ D)` | all collar sources diagonal | role |
|---|---|---|---|---|---|---|---|
| `A_q_violation` | `91f52f97…` | 6 | **34** | 24 | 20 | no | refutes **R2** (and R1) |
| `B_minimal_intersection` | `321b7cef…` | 5 | 12 | 18 | 4 | no | refutes **R1**, 4-edge witness; **counting declines** |
| `C_known_object_250ac6cd` | `250ac6cd…` | 7 | 5 | 15 | **0** | **yes** | Theorem A regime |
| `D_known_object_5da67053` | `5da67053…` | 7 | 6 | 18 | **0** | no | converse of Theorem A is false |

B is the discriminating control that matters: it has a **nonzero
intersection** yet **positive counting slack**, so R1 and R2 are genuinely
different failure modes and the counting test is not simply detecting R1.

---

## Controls

`verify.py` fails loudly if any of these stop holding:

- every published quantity is recomputed and compared (a wrong published
  number is caught, not trusted);
- **mutated witness coefficient** ⟹ circulation/projection checks must break;
- **dropped witness edge** ⟹ checks must break;
- **mutated base transition** ⟹ the pointed-simulation invariant must break;
- the counting test must **decline** on objects C and D (no false positives);
- Theorem A must hold on every object in its regime.

The `full36` transition table is embedded and hash-checked; `witnesses.json`
records the sealed engine/context hashes the reconstruction was cross-checked
against at build time, but `verify.py` does not import them.

---

## What this does *not* claim

- No `r₃(N)` bound, no progress on the constant, no survivor certificate.
- The **`q = 1` hole is untouched**: still 0 occurrences in >1.18M closed
  products, still the unique absent value in 0..24. What is closed is one
  *route* to excluding it.
- Census figures quoted above (31,548 / 873,264 / 0 Theorem A violations) come
  from the referee sweep and are **reported, not re-derived** by this
  certificate. Everything the certificate *asserts* it recomputes.

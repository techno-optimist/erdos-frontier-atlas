# Dixmier Conjecture — an explicit counterexample *object*, derived from the JC root

**Problem.** The Dixmier Conjecture `DC_n` (Dixmier 1968; statement quoted
verbatim from Belov-Kanel & Kontsevich, `arXiv:math/0512171`): *for any field
`k` of characteristic zero, every endomorphism of the `n`-th Weyl algebra
`A_{n,k}` is an automorphism.* Open since 1968.

**What is new here, and what is not.** The implication *"a Keller
counterexample in dimension `n` yields a Dixmier counterexample in dimension
`n`"* is classical and easy — BKK state it in one paragraph and attribute it to
the literature. What did not exist before 2026-07-19 was the **input**: an
actual Keller counterexample. This directory therefore contributes neither the
theorem nor the counterexample map, but the third thing — **the explicit
endomorphism object itself, written down and machine-checked**:

> the first explicit non-automorphism endomorphism of a Weyl algebra, exhibited
> in coordinates and verified relation by relation in exact rational
> arithmetic.

Everything is **CONDITIONAL on Alpöge's root claim** (his dim-3 Jacobian
counterexample `F`, *awaiting confirmation* — widely machine-verified, not
peer-reviewed). **The construction of `F` is not ours**; see
[`../jacobian-conjecture/`](../jacobian-conjecture/) and
[`../../atlas/jc-crater/root_claim.json`](../../atlas/jc-crater/root_claim.json).
Claim type: **derived corollary**, not a discovery.

## The object

`A_3` has six generators `x1,x2,x3,d1,d2,d3` with `[d_i, x_j] = δ_ij` and
`[x_i,x_j] = [d_i,d_j] = 0`; coefficients in **Q**. Define
`Φ : A_3 → A_3` by

```
Φ(x_i) = F_i(x1,x2,x3)             the certified Keller map, det J_F ≡ −2
Φ(d_i) = Σ_k B[i][k] · d_k         B = (J_F^T)^{-1} = adj(J_F)^T / (−2)
```

`B` has **polynomial** entries — not merely rational ones — precisely because
`det J_F = −2` is a *nonzero constant*: the adjugate is polynomial and the only
division is by that constant. (The textbook statement normalizes `det = 1`;
nothing here uses that, only constancy. Replace `f1` by `−f1/2` if a `det = 1`
form is wanted.)

Concretely, after expansion:

| | terms in `Φ(d_i)` | max coefficient degree |
|---|--:|--:|
| `Φ(d_1)` | 19 | 8 |
| `Φ(d_2)` | 24 | 9 |
| `Φ(d_3)` | 34 | 11 |

(The script prints the term counts `[19, 24, 34]` and the *global* max degree
`11`; the per-row degrees above are read off the same `Φ(d_i)` it builds.)

## What is certified

`weyl_endomorphism.py` (stdlib-only CPython, exact `Fraction` rationals,
~0.15 s) checks, in a self-contained normal-ordering Weyl-algebra engine:

1. **Engine unit tests** — the normal-ordering multiplication reproduces known
   identities (`[d1,x1] = 1`, `[d1,x2] = 0`,
   `d1² x1² = x1² d1² + 4 x1 d1 + 2`). The engine is checked before it is
   trusted.
2. **`det J_F ≡ −2`**, re-derived here from scratch rather than imported, so
   this certificate does not silently depend on a file elsewhere.
3. **`B · J_F^T = I = J_F^T · B`** as exact polynomial matrices — `B` really is
   the two-sided inverse over `Q[x]`, not just a formal expression.
4. **All 15 defining relations of `A_3` are preserved by `Φ`**:
   `[Φ(d_i), Φ(x_j)] = δ_ij` (9 commutators), `[Φ(d_i), Φ(d_j)] = 0`
   (3 — the nontrivial integrability identity), `[Φ(x_i), Φ(x_j)] = 0` (3).
5. **Non-surjectivity witness** — two of the certified collision points,
   `P = (0,0,−1/4)` and `Q = (1,−3/2,13/2)`, satisfy `F(P) = F(Q)` exactly
   **and differ in every coordinate**.
6. **Four planted-failure controls** — a transposition mistake (`J_F^{-1}` for
   `J_F^{-T}`), a perturbed coefficient (`B₁₁ + x₁`), a perturbed map
   (`f3 + x₁x₂`), and a perturbed point must each be *rejected*.

Legs 2–4 make `Φ` a well-defined endomorphism of `A_3`. Leg 5 kills
surjectivity, by this five-line argument:

> Suppose `Φ(a) = x₁` for some `a ∈ A_3`. By the PBW normal form write
> `a = g + h` with `g ∈ C[x]` and `h` in the **left** ideal `I = A_3·(d1,d2,d3)`.
> Each `Φ(d_j)` lies in `I` and `I` is a left ideal, so `Φ(h) ∈ I`; hence
> `x₁ − g(F) = Φ(h) ∈ I`. Apply both sides to the constant function `1` in the
> module `C[x]`: every element of `I` kills `1`, so `x₁ = g(F)` identically.
> But leg 5 exhibits `P ≠ Q` in the first coordinate with `F(P) = F(Q)` — so no
> polynomial `g` can satisfy `x₁ = g(F)`. Contradiction.

So `Φ` is **not surjective**, hence **not an automorphism**: `DC_3` fails, and
`DC_n` for every `n ≥ 3` by BKK's *"the conjecture DC_n implies DC_m for
n > m"* (verbatim, `SOURCES.md`).

## What is NOT certified — the two non-machine steps

Both are textbook-elementary and both are **boundaries, not results**. Neither
is checked by the script; both are required for the conclusion.

1. **`A_3` is presented by exactly those 15 relations** — i.e. `A_3` is the
   quotient of the free algebra on the six generators by the ideal they
   generate (Dixmier 1968; standard). This is what makes "checking relations on
   generators" enough for `Φ` to be well defined. The machine checks that the
   relations hold; it does not check that they *suffice*.
2. **The PBW normal form and `I·1 = 0`** — that every `a ∈ A_3` decomposes as
   `g + h` with `g ∈ C[x]` and `h` in the left ideal generated by the `d_i`,
   and that `I` annihilates the constant function `1` in `C[x]`. Both are
   standard PBW facts, asserted here, not verified.

Also not certified, and not claimed: novelty, priority, or attribution of `F`;
peer review of anything (Alpöge's announcement is *awaiting confirmation*, and
this directory has been reviewed by no one outside the project); and any
statement about `DC_1` or `DC_2`, which this object says nothing about.

## Replay

```
python3 -I certificates/dixmier-conjecture/weyl_endomorphism.py   # exit 0 = verified
```

`-I` isolates the interpreter from `PYTHONPATH` and the user site-directory:
the certificate imports only `fractions`, `math`, `itertools` and `sys`, and the
flag makes that auditable rather than merely claimed.

## Sources

[`SOURCES.md`](SOURCES.md) carries the verbatim primary quotations (BKK for the
`DC_n ⇒ JC_n` easy direction, the `DC_n ⇒ DC_m` monotonicity, and the `DC_n`
definition itself; Tsuchimoto and Bavula for the hard direction, which this
construction does **not** use), together with an explicit provenance limit: the
van den Essen 2000 book was **not** fetched by this project, so nothing here
rests on what it does or does not contain.

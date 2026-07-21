# ANATOMY 1 — The Jelonek non-properness set of Alpöge's dim-3 Keller map

**Round 3, 2026-07-20.** Working dir: `scratchpad/jc-round3/nonproperness/`.
**Claim typing:** the map F is ALPÖGE's (with Claude Fable assistance); we verify
and derive, we do not discover the root. Everything below is **CONDITIONAL on the
root claim** (tracked by `root_claim.json` + the crater tripwire). The
non-properness computation itself is new in round 3. Nothing here contradicts any
typed crater edge; it sharpens the `keller_properness_universal` node's
"non-properness escape hatch" from an existence statement to an exact equation.

---

## Headline (CERTIFIED, stdlib replay)

Let `t1,t2,t3` be target coordinates and

```
E(t) = 27 t1^2 t3^2 - 18 t1 t2 t3 + 16 t1 + t2^3 t3 - t2^2        (quartic)
```

> **Not claimed:** that `E` is irreducible over **Q** (or over **C**). Earlier
> drafts of this headline said "Q-irreducible"; that was only a **CAS-level
> discovery probe** (sympy factorization), it has **no stdlib replay path in
> this directory**, and no result below uses it — the density step (I5) is
> stated per irreducible component precisely so it never needs to know what the
> components are. Likewise `Phi_x` is only claimed to be **an** annihilator of
> `x`, never the minimal one.

**Theorem 1 (S_F computed exactly).**
`S_F = V(E)` — the set of points at which F is not proper (Jelonek's asymptotic
set) is exactly this quartic hypersurface. Equivalently: F restricted over
`C^3 \ V(E)` is a proper étale map, hence an **unbranched 3-sheeted covering**;
over every point of `V(E)` at least one preimage has escaped to infinity.

**Theorem 2 (only x escapes).** On any escaping sequence (|p_k| → ∞,
F(p_k) → t), the y- and z-coordinates stay bounded and |x_k| → ∞: y and z
satisfy cubics over C[t] with **constant** leading coefficients (2 and 8),
while an annihilator of x (**not** claimed minimal — minimality is a CAS-level
step the product itself quarantines),

```
Phi_x(t, X) = E(t)·X^3 + (4 - 3 t2 t3)·X - 2 t3,
```

has leading coefficient exactly E(t).

**Theorem 3 (F is NOT surjective — bonus).** The punctured rational curve

```
gamma(s) = (s^2/12, s, 4/(3s)),   s ≠ 0
```

has **empty fibers**: on gamma both non-constant coefficients of Phi_x vanish
identically and the constant term −2t3 = −8/(3s) ≠ 0, so the certified
annihilator identity is unsatisfiable. gamma is exactly
`V(E) ∩ {4 − 3 t2 t3 = 0}` (elimination witness is the perfect square
`3(t2^2 − 12 t1)^2`, machine-checked). *Observation (CAS-level, not needed for
any claim): gamma is precisely the singular locus of the quartic V(E) — F omits
exactly the singular locus of its own Jelonek set.*

**Fiber-size census** (certified at the listed points; étale bound ≤ 3 everywhere):

| target t* | E(t*) | #F⁻¹(t*) | status |
|---|---|---|---|
| (−1/4, 0, 0) (the collision target) | −4 | 3 | certified (verify.py points re-checked) |
| (−16/27, 0, 1) ∈ V(E) | 0 | **1** — fiber = {(1/2, −8/3, 16)} | certified exactly |
| (−4/27, 0, 2) ∈ V(E) | 0 | **1** — fiber = {(1, −4/3, 4)} | certified exactly |
| (−1, 2, −2) ∈ V(E), t2 ≠ 0 | 0 | **1** — fiber = {(−1/4, 5, −36)} | certified exactly |
| (1/3, 2, 2/3) ∈ gamma | 0 | **0** | certified (I2 unsatisfiable) |
| (1, 4, 0) ∈ V(E) ∩ {t3=0} | 0 | 1 | CAS observation (sympy solve) |
| (1,1,1), (0,1,2), (1,0,0) off V(E) | ≠0 | 3 | CAS observation, matches covering |

So the fiber count jumps 3 → 1 → 0 as t crosses from the generic locus onto
V(E) and then onto gamma ⊂ V(E). Whether any point of V(E) has a fiber of
size exactly 2 is **not determined** (certified bound on V(E)\gamma is ≤ 2;
every sample gave 1; generically on V(E) exactly two Phi_x roots blow up, so
generic fiber on V(E) is 1 — that last step is CAS-level).

## The mechanism (one paragraph)

For a *proper* 3:1 map, the discriminant locus of the fiber cubic would be the
branch locus. Alpöge's map is étale (det JF = −2, certified) — branching is
forbidden. The certified identity

```
disc_Y(G1) = −2916 · t1^2 · E(t)          (I4)
```

says the fiber cubic for y degenerates on `V(t1) ∪ V(E)`. On `V(E)` the
degeneration is a true escape: colliding preimages must vanish to infinity
(x → ∞, since Phi_x drops from cubic to linear there). On `V(t1)` it is a
**false alarm**: two fiber points share the same y but differ in x (sample
fiber over (0,1,2): points (−1±i, 1, 1∓3i) share y = 1) and F stays proper —
which is exactly why S_F is V(E) and not the full discriminant locus, and why
the t1 factor appears squared: no branching can back it.

Escape asymptotics (numerical illustration, t → (−16/27, 0, 1) along
t1 = −16/27 + ε: roots of Phi_x are ≈ {0.5005, +15.57, −16.07} at ε = 10⁻³ —
**two** branches fly to ±∞ like ±sqrt(−(4−3t2t3)/E), one converges to
x* = 2t3/(4−3t2t3) = 1/2).

## Proof architecture — what the machine checks vs. the human steps

Machine-checked, exact `Fraction` arithmetic, stdlib only, monomial-dict engine
(same convention as `certificates/jacobian-conjecture/verify.py`); **runtime
0.1 s**, exit 0:

- **(I1)–(I3)** annihilator pullback identities `G1(F(p), y) ≡ 0`,
  `Phi_x(F(p), x) ≡ 0`, `Phi_z(F(p), z) ≡ 0` in Q[x,y,z]. These are
  identity-shaped: a transcription error fails, it cannot pass falsely. The
  annihilators were *discovered* by resultants from the certified tower
  (G1, G2, G3 of `geometric_degree.py`) in sympy; **none of the CAS run is in
  the trust path** — the identities are re-proved from scratch by expansion.
- **(I4)** `disc_Y(G1) == −2916 t1² E` in Q[t].
- **(I5)** density facts: `t3 ∤ E`, `(4−3t2t3) ∤ E` (via nonvanishing of the
  clearing polynomial `16A+12t2B+9t2²C = 432t1²−72t1t2²+3t2⁴`), so no
  component of V(E) hides in the removed loci.
- **(I6)** the omitted curve: `E(gamma(s)) ≡ 0`, `(4−3t2t3)(gamma(s)) ≡ 0` as
  Laurent-polynomial identities in s; plus `16A+12t2B+9t2²C == 3(t2²−12t1)²`.
- **(W1a/b/c)** three exact one-point fibers ON V(E) (two on the t2 = 0 slice,
  one off it): x forced by the linearized Phi_x, y confined by an exactly
  factored cubic `2(Y−r)(Y−r')²`, z forced by f3 = t3, the surviving candidate
  evaluated by TWO independent paths (nested-expression and expanded-poly),
  the dead candidate certified to miss.
- **(W2)** the collision target's 3-point fiber re-verified, E = −4 there.
- **(NCa–NCe)** five planted-failure negative controls (perturbed Phi_x,
  perturbed disc constant, perturbed witness point, wrong factorization,
  perturbed curve).
- **Meta-control (measured 2026-07-20, corrected).** `E` is transcribed
  **twice and independently** in the source — once in the definition of `E`,
  once inside the `(I5a)` recomposition `E == A t3² + B t3 + C`. Mutating the
  constant `16 t1 → 17 t1` gives, on the shipped file:

  | mutation site | #FAIL | which checks fail | exit |
  |---|--:|---|--:|
  | **both** copies (definition + I5a) | 8 | I2 I4 W1a W1b W1c I6a I6b W2 | 1 |
  | definition only | 8 | I2 I4 **I5a** W1a W1b W1c I6a W2 | 1 |
  | I5a recomposition copy only | 2 | **I5a** I6b | 1 |

  Reading: mutating the definition breaks the annihilator identity, the
  discriminant identity, all three witness fibers, the omitted curve and the
  off-`V(E)` fiber — `E` is load-bearing everywhere. Mutating only **one** of
  the two copies is caught by `(I5a)`, which exists exactly to pin the two
  transcriptions against each other. No single-site edit of `E` slips through.
  *(An earlier round-3 draft of this file reported "10 legs fail"; that figure
  does not reproduce — the measured count is 8. The same reproduction table is
  now in the certificate's own docstring.)*

Classical prose steps (stated in the certificate docstring as (L1)–(L5), each
standard): the root bound (leading coefficient bounded away from 0 ⇒ roots
bounded); asymptotic set = non-properness set (compactness); proper + étale ⇒
covering with sheet count = certified generic degree 3, so `#fiber ≤ 2 ⇒
non-proper` (uses det JF = −2 from verify.py and degree 3 from
geometric_degree.py); closedness of S_F (diagonal argument); disc = 0 ⇒ ≤ 2
distinct roots. Context: this is Jelonek's leading-coefficient method
(Z. Jelonek, *The set of points at which a polynomial map is not proper*, Ann.
Polon. Math. 58 (1993) 259–266; effective versions: A. Stasica, J. Pure Appl.
Algebra, early 2000s), but the proof here is self-contained modulo the
classical lemmas — no CAS output is trusted.

Proof of Theorem 1 in four lines: (⊆) if E(t*) ≠ 0 then by (I1)–(I3) + root
bound all three coordinates are bounded on fibers near t*, no escape. (⊇) for
t ∈ V(E) with t3 ≠ 0, 4−3t2t3 ≠ 0: x is unique (Phi_x linear), y takes ≤ 2
values (I4: disc = 0), z is determined by f3 (x = 2t3/(4−3t2t3) ≠ 0), so
#fiber ≤ 2 < 3 ⇒ t ∈ S_F; by (I5) that locus is dense in V(E) and S_F is
closed.

## What this adds to the crater (candidate updates — orchestrator's call)

1. **`keller_properness_universal` node:** the escape hatch is now exact:
   S_F = V(E), a degree-4 hypersurface; F is an unbranched 3-sheeted covering
   over its complement. (BCW "proper Keller ⇒ invertible" survives untouched —
   F is as non-proper as it must be.)
2. **New fact for the anatomy: F is not surjective.** im(F) misses the curve
   gamma = Sing(V(E)). Certified direction: gamma ∩ im(F) = ∅ and
   C³\V(E) ⊆ im(F). The refinement "im(F) = C³ \ gamma exactly" (i.e. fibers
   on V(E)\gamma are nonempty) rests on a limit argument plus one CAS-level
   step (Phi_x irreducibility over Q(t) / x separating generic fibers) — typed
   DERIVED-OBSERVATION, do **not** promote to certified without closing that
   step.
3. **Consistency with the realification note** (`jelonek_real_jc` hand
   analysis): the R⁶ realification's non-properness set of real codim exactly 2
   is now concrete — it is V(E) viewed as a real hypersurface of C³ (complex
   codim 1 = real codim 2). No contradiction with any typed edge.
4. **Quantity candidates** (C2-style, conditional on root): degree of the
   Jelonek set of the certified dim-3 counterexample = 4; number of preimages
   escaping at a generic point of S_F = 2 (CAS-level); minimal fiber size = 0
   (non-surjectivity), realized on a rational curve.

## Honest boundaries (documented, per house rules)

- **Absolute irreducibility of E over C:** probed only (single factor over
  QQ(i) and QQ(√3), sympy). NOT certified, and NOT needed: the density
  argument (I5) is per-component and avoids it.
- **Fiber size 2 on V(E):** existence/nonexistence not determined (bound ≤ 2
  certified on V(E)\gamma; all samples gave 1).
- **"im(F) = C³ \ gamma" exact equality:** see item 2 above — one CAS-level
  step remains; the two certified inclusions are what the certificate claims.
- **Uniruledness of S_F** (Jelonek's general theorem says S_F is C-uniruled):
  visibly consistent (V(E) is quadratic in t1 and in t3; gamma = Sing V(E) is
  rational) but not developed.
- No time-cap was hit: total compute ≈ 8 s of sympy discovery + 0.1 s
  certificate. No silent skips.

## Files

- `certify_nonproperness.py` — **the certificate.** Stdlib-only, exact
  rationals, **18** checks incl. 5 negative controls (the script now tallies
  its own `check()` calls and refuses to certify if the total drifts from the
  advertised 18); exit 0 = verified. Replay:
  `python3 -I certificates/jc-anatomy/certify_nonproperness.py`.
- `findings_nonproperness.md` — this file (round-3 working name: `findings.md`
  under `scratchpad/jc-round3/nonproperness/`; renamed on assembly so the two
  anatomy findings files can sit in one directory).

**Not shipped** (round-3 scratchpad only, deliberately outside the trust path):
`discover1.py` (sympy: tower → disc factorization, D = 9·t1·t2·E, resultant
annihilators — Res_x factors as 5832·t1³t2³E²·Phi_x, Res_z as
−93312·t1³t2³E³·Phi_z), `discover2.py` (pullback pre-checks, fiber counts at 5
sample targets, escape numerics), `discover3.py` (exceptional-locus fibers —
where the empty fiber on gamma was found —, E irreducibility probes,
Sing V(E) = gamma). Everything they found that survives is re-proved from
scratch by the certificate; nothing cites them.

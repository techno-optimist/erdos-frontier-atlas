# Jacobian Conjecture — independent verification of the 2026 counterexample

**Problem.** The Jacobian Conjecture (Keller 1939; van den Essen, *Polynomial
Automorphisms and the Jacobian Conjecture*, Birkhäuser 2000): if a polynomial
map `F : C^n -> C^n` has Jacobian determinant a nonzero constant, then `F` is
invertible (in particular injective). Open since 1939 for every `n >= 2`;
one of the most storied problems in affine algebraic geometry.

**The claimed counterexample (n = 3).** In 2026-07 a counterexample map was
posted publicly — **the construction is not ours** (see *Provenance*):

```
f1 = (1+xy)^3 z + y^2 (1+xy)(4+3xy)
f2 = y + 3x(1+xy)^2 z + 3xy^2 (4+3xy)
f3 = 2x - 3x^2 y - x^3 z
```

with the three points `(0, 0, -1/4)`, `(1, -3/2, 13/2)`, `(-1, 3/2, 13/2)`
all mapping to `(-1/4, 0, 0)`.

## What is certified

`verify.py` (stdlib-only CPython, exact `Fraction` rationals, ~0.03 s) checks:

1. **`det JF == -2` identically** — proved *symbolically*: the Jacobian
   determinant is computed as a polynomial in `Q[x,y,z]` by a self-contained
   exact monomial-dict engine (build → differentiate → 3×3 cofactor
   expansion) and asserted equal, coefficient by coefficient, to the constant
   polynomial `-2`. Constancy is a polynomial identity here, not a sample of
   evaluations.
2. **`F` is not injective** — the three points above are pairwise distinct and
   each maps *exactly* to `(-1/4, 0, 0)`, with images computed by two
   independent evaluation paths (direct nested expressions vs. the expanded
   polynomials of leg 1), which must agree.
3. **Negative controls** — a perturbed map (`f3 + xy`) must fail leg 1 and a
   perturbed point must fail leg 2, demonstrating the checker can reject.

Facts 1 + 2 jointly contradict the conjecture's statement: a nonzero-constant-
Jacobian polynomial self-map of `C^3` that is not injective. A counterexample
is self-certifying — finitely many exact checks on an exhibited object — which
is why a conjecture open since 1939 can be settled by a script this small.

During construction of this certificate the same two facts were confirmed via sympy
(`expand`, plus Berkowitz and Bareiss determinants) before this
dependency-free verifier was written; none of that is in the trust path.

## What is NOT certified

- **Novelty, priority, or attribution.** This directory verifies the exhibited
  object only. Who first constructed it, and its publication status, are
  provenance questions outside the certificate.
- **Anything about the map beyond legs 1–2.** (External observation, CAS-level
  only, not part of the certificate: the fibers over both `(-1/4, 0, 0)` and a
  generic target such as `(7, 2, -3)` each contain exactly 3 points, so the map
  appears to be generically 3-to-1. Consistency note: an étale self-map of
  `C^3` of degree > 1 cannot be proper — non-properness is exactly the escape
  hatch the classical simply-connectedness obstruction leaves open, so the
  object is structurally consistent with why the conjecture resisted proof.)

## Provenance

The counterexample was presented **2026-07-19 by Levent Alpöge** (mathematician,
Anthropic), who found it with the help of Claude Fable and credited a question
by Akhil; the announcement included Wolfram Alpha verification links. Per the
Wikipedia *Jacobian conjecture* article, the posted line "was simple to verify
and many mathematicians ha[d] already done so by July 20," and the result is
listed there as a **counterexample "awaiting confirmation"** — widely checked,
not yet formally peer-reviewed or journal-published.

**The construction is Alpöge's, not this repo's.** This directory contributes
only the independent, dependency-free, replayable verification; no claim here is
derived from anyone else's verification — the certificate stands alone.

## Epistemic status (why a verifier can carry this, and what it cannot)

A counterexample is **self-certifying**: unlike a proof, it has no chain of
reasoning that could hide a gap — you exhibit one object and check finitely many
properties of it. `verify.py` checks all of them, exactly. So the *object-level*
facts (constant Jacobian −2; three distinct points sharing an image) are
established here at full confidence, and they contradict the Jacobian Conjecture
**as standardly stated** (nonzero-constant Jacobian ⟹ polynomial inverse; van
den Essen 2000; Wikipedia). This is the same reason the wider community could
confirm it within a day: verifying is elementary even though *constructing* such
a map evidently was not.

What this certificate does **not** establish, and does not claim: the
construction's authorship (Alpöge's), its formal acceptance (peer review /
publication pending — "awaiting confirmation"), or any resolution owned by this
project. We certify the verification, not the discovery.

## Replay

```
python3 certificates/jacobian-conjecture/verify.py   # exit 0 = verified
```

`witness.json` carries the map and points in machine-readable exact-rational
form.

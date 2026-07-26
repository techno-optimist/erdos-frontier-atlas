# Power-weighted lifts — independent exact replay of an external Keller family

**What this is, and what follows from it, in one place.** The two-parameter
family `F_{k,d} : A^3 -> A^3` verified here consists of polynomial self-maps of
`A^3` with nonzero constant Jacobian determinant that are **not injective** — and
such a map is, by definition, a counterexample to the Jacobian Conjecture. That
is the stake, so the three qualifiers that bound it belong in the same breath:

1. **The construction is not ours.** It is claimed by **Nathan Wilbanks and
   "Annie"** in *Power-Weighted Lifts: Explicit Higher-Weight Noninjective Keller
   Maps* (AGNT Labs Technical Report III, v1.0, 2026-07-21,
   <https://agnt.gg/whitepapers/power-weighted-lifts-higher-weight-keller-maps.html>).
   The theorem, the family, and the idea of the power-weighted lift are theirs.
   Ours is only the replay: we rebuilt `F_{k,d}` in exact rational arithmetic and
   re-derived, from scratch, every property the report asserts.
2. **This is a reimplementation from the report's prose, not a reproduction of
   the authors' artifacts.** Their `independent_reproduction.md` is hash-bound to
   the wrong document, so there was no intact receipt chain to replay. The only
   place our numbers meet theirs is their printed `(k,d) = (2,3)` expansion
   (leg 6), which we reproduce monomial for monomial.
3. **The `k = 1` row is prior art by the paper's own account** — the report says
   Gallagher's published notes already describe that one-variable weighted-lift
   mechanism, so 7 of the 27 members are not new with this paper. `verify.py`
   prints that in its header and marks those seven lines; `witness.json` carries
   it under `prior_art`. Nothing here adjudicates novelty, priority, or dates.

What we certify is exhibited objects with exhibited properties — legs 1, 2 and 5
below, per member — not the surrounding narrative of either paper. This lane sits
beside [`certificates/jacobian-conjecture`](../jacobian-conjecture) (the dim-3
counterexample of Alpöge, 2026) and the `atlas/jc-crater` propagation graph. See
*What is NOT certified* for the full boundary.

**One correction we owe the reader, up front.** The report states a single
non-injectivity witness, `F(1,0,0) = F(-1,0,2) = (0,0,1)`, for `k` and `d` both
odd. It holds — we confirm it exactly — but it covers **6 of the 27** grid
members, not all 27. Witnesses for the other 21 are ours, derived here and each
checked by exact evaluation. The verifier prints this as a scoping correction and
records it in `witness.json` under `scoping_correction`.

```bash
python3 -I verify.py          # ~1 s, stdlib only, exit 0 iff everything passes
```

## What the paper claims, and what we checked

For integers `1 <= k < d` the report defines, from torus-invariant coordinates
`v = x^k y`, `t = x^{k+1} z`:

```
u = 1 + v            gamma = 1 - ((d+k)/d) v - t            w = u * gamma
q(w) = ((k+1) w^k - (d+1) w^d) / (d-k)      Q(w) = (w^{k+1} - w^{d+1}) / (d-k)
p(w) = (w q(w) - Q(w)) / (k+1)
alpha = p(w)/gamma^{k+1} + u/(k+1)          beta = q(w)/gamma^k + 1

F_{k,d}(x, y, z) = ( alpha / x^{k+1} ,  beta / x^k ,  x gamma )
```

and asserts: `F_{k,d}` is polynomial, `det J F_{k,d} = -k/(k+1)` (a nonzero
constant, hence Keller), the source torus weights are `(1, -k, -k-1)`, the
geometric generic degree is `k(d+1)`, and `F_{k,d}` is not injective. The report
tabulates the grid `1 <= k <= 6`, `k < d <= 8` — **27 members**.

`verify.py` rebuilds all 27 and checks, exactly:

1. **Genuinely polynomial.** `alpha` is divisible by `x^{k+1}` and `beta` by
   `x^k` in `Q[x,y,z]`, by exact monomial division — no negative exponent
   survives. (This is where the coefficient `(d+k)/d` inside `gamma` earns its
   keep: with `1` in its place, the division fails. That is control C2.)
2. **`det J F_{k,d} == -k/(k+1)` as a polynomial identity.** The Jacobian is
   built symbolically, expanded by 3x3 cofactors, and compared coefficient by
   coefficient against the constant polynomial. It is an identity in
   `Q[x,y,z]`, not a sample at points, and there is no float in the trust path.
3. **Torus weights `(1, -k, -k-1)`.** Every monomial `x^a y^b z^c` of `F1`,
   `F2`, `F3` satisfies `a - kb - (k+1)c = -(k+1), -k, 1` respectively — i.e.
   each component is isobaric, which is the equivariance statement.
4. **Generic fibre point count — counted, then compared with `k(d+1)`.** The
   verifier does not restate the paper's formula: it exhibits a rational target
   whose fibre equation `G` is squarefree with no root forcing `gamma = 0`, and
   *counts* `k * deg(G / gcd(G, G'))` — the number of `(w, gamma)` pairs. That
   product is what the transcript and the receipt record. It is then compared
   with the claimed `k(d+1)`, and a mismatch fails the run. See the argument
   below, and control C12.
5. **Not injective.** Two distinct points with provably equal image, exhibited
   and then checked by exact evaluation of the rebuilt polynomials.
6. **Anchor to the authors' own arithmetic.** The report prints the expanded
   degree-8 specialisation `(k,d) = (2,3)`. Our independent rebuild reproduces
   it monomial for monomial, including `5x^7y^5/3`, `17x^5y^4/3`, `20x^3y^3/3`.
   This is the one place our reimplementation touches their numbers, and it
   agrees.

### Why the gamma-divisions are not a problem

`alpha` and `beta` are written with `gamma` in denominators, but because
`w = u*gamma` those divisions cancel identically. Expanding
`w q(w) - Q(w) = (k w^{k+1} - d w^{d+1})/(d-k)` gives

```
q(w)/gamma^k       = ( (k+1) u^k     - (d+1) u^d     gamma^{d-k} ) / (d-k)
p(w)/gamma^{k+1}   = (  k    u^{k+1} -  d    u^{d+1} gamma^{d-k} ) / ((k+1)(d-k))
```

so the whole construction stays inside `Q[x,y,z]` and **no division by `gamma`
is ever performed numerically**. The verifier does not take this on trust: leg
`gamma-cancellation` multiplies the closed forms back up by `gamma^k` and
`gamma^{k+1}` and checks they equal the honest `q(w)`, `p(w)` as polynomials.

### Out-of-band corroboration (not in the trust path)

Before this dependency-free verifier was written, all 27 members were rebuilt a
second time in sympy along a deliberately different route — the raw
`p(w)/gamma^{k+1}` and `q(w)/gamma^k` divisions performed symbolically rather
than via the closed forms above, and the determinant taken by Berkowitz rather
than cofactor expansion. All 27 gave `-k/(k+1)`. That run used a third-party CAS
and is **not** part of the certificate; it is recorded only because it exercised
a path that shares no code with `verify.py`.

### The generic-degree argument

Write `X, Y, Z` for the components of `F`. The target weights are
`(-k-1, -k, 1)`, so `V := Y Z^k` and `T := X Z^{k+1}` are the target-side
invariants, and `V = q(w) + gamma^k`, `(k+1)T = w q(w) - Q(w) + w gamma^k`.
Eliminating gives one identity, which the verifier checks in `Q[x,y,z]`:

```
(Y Z^k) * W  -  Q(W)  -  (k+1) (X Z^{k+1})  ==  0 ,      W := u * gamma
```

Over a target with `Z != 0` (which forces `x != 0`, since `F3 = x*gamma`) this
identity makes the fibre a bijection with

```
{ (w, gamma) :  G(w) = 0 ,  gamma^k = V - q(w) } ,   G(w) := Q(w) - V w + (k+1) T
```

— given such a pair, `u = w/gamma`, `x = Z/gamma`, `y`, `z` recover a genuine
preimage. So if `G` is squarefree and no root of `G` makes `V - q(w)` vanish, the
fibre has exactly `k * #{distinct roots of G}` points: each root `w` contributes
`k` distinct `gamma` with `gamma^k = V - q(w) != 0`. Both conditions are exact
gcd computations over `Q`, and `verify.py` exhibits a small rational `(V, T)` for
each of the 27 members at which both hold. Since they are Zariski-open conditions
on `(V, T)`, holding at one point makes them hold generically.

**This leg is a count, not a restatement.** `fibre_point_count` computes
`k * (deg G - deg gcd(G, G'))` from the very polynomial the étale gate measured;
`generic_degree_ok` is the gate that the recorded number must pass, and the
recorded number is separately compared with the paper's `k(d+1)`. It happens that
`deg G = d+1` always, so the count comes out `k(d+1)` on all 27 — but if it did
not, the run would fail rather than print the formula. This is what control C12
holds in place: it mutates the *claim* to `k(d+2)` on every member and requires
the same gate to reject it. (Before that, a hostile edit of the recorded degree
survived `--emit` and a full green replay — the whole leg was unfalsifiable, and
byte-comparison against a receipt written by the mutated code is drift detection,
not verification.)

(Amusing consequence the verifier records: `Q'(w) = q(w)`, so "a root of `G`
with `gamma = 0`" and "a double root of `G`" are literally the same condition.
The two gates are kept separate in code anyway; they are not allowed to rely on
that observation being true.)

### The non-injectivity witnesses — and our scoping correction (6 of 27, not 27)

This is the correction flagged at the top, stated in full. The report gives one
witness, for **`k` and `d` both odd**: `F(1,0,0) = F(-1,0,2) = (0,0,1)`. We
confirm it exactly, and it holds on every member with that parity — **all 6 of
them**. It does **not** cover the paper's own grid: 27 members, 6 with `k, d`
both odd, so **21 members have no witness in the report**. We derived those
ourselves, and the verifier checks each by exact evaluation:

| mechanism | applies when | field | used for |
|---|---|---|---|
| `sign` — `gamma^{d-k} = 1` has the extra root `-1`; generalises the paper's witness | `d-k` even | `Q` | 12 members |
| `root-of-unity` — `(u, gamma) -> (u/z, z*gamma)` fixes the image whenever `z^k = 1` | `k >= 2` | `Q` if `k` even, else `Q(zeta_r)`, `r` = least prime factor of `k` | 11 members |
| `two-root` — two distinct rational roots of the fibre equation `G` | `k = 1` | `Q` | 4 members |

(Several members admit more than one witness; the verifier prefers a rational
one and records which mechanism it used.)

Preferring rational witnesses, this gives **22 of 27 over `Q`**; the remaining 5
(`k=3, d in {4,6,8}` and `k=5, d in {6,8}`) get a witness over `Q(zeta_3)` or
`Q(zeta_5)`, in exact `Q[T]/Phi_r(T)` arithmetic. Independently of any explicit
pair, the counted generic fibre size (`k(d+1) >= 2` on every member) already
forces non-injectivity over `Q-bar`.

### Consequence

The Jacobian-Conjecture consequence, and the qualifiers that bound it, are stated
in the first section of this README rather than here — it is the highest-voltage
sentence in the lane and it must not sit 140 lines away from the attribution.
Legs 1, 2 and 5 are what carry it, per member.

## Planted-failure controls

A checker that cannot fail certifies nothing, so 12 deliberate corruptions are
run on every replay and every one must be **rejected**, printed as
`[ok] rejected by <gate>: ...`.

**All 12 are load-bearing.** Each is rejected by a function the default path
itself calls — named in the table and in the printed line — not by a comparison
written beside the gate inside the control. (Two earlier controls were not:
old-C3 only asserted that one map's determinant was not one specific *other*
constant, which is nearly free and exercised no gate, and old-C6 compared a
corrupted dict to the rebuild inline instead of calling the anchor gate. Both
were rebuilt below; a "11 controls" count with 2 decorations in it is a worse
claim than an honest smaller number.)

| # | corruption | rejected by (gate the default path runs) |
|---|---|---|
| C1 | `F1 + x*y` at `(2,3)` | `det_ok` |
| C2 | `gamma` with coefficient `1` instead of `(d+k)/d` | `build_family` (x-divisibility) |
| C3 | claimed determinant mutated `-k/(k+1) -> -k/(k+2)`, on **all 27** members | `det_ok` |
| C4 | collision partner `(-1,0,2) -> (-1,0,3)` at `(3,5)` | `check_collision` |
| C5 | constant monomial added to `F1` at `(2,3)` | `weights_ok` |
| C6 | one coefficient of the paper's printed `F1` at `(2,3)` flipped `20/3 -> 7` | `anchor_ok` |
| C7 | planted double root of the fibre equation at `(2,5)` | `fibre_is_etale` |
| C8 | `Q(zeta_3)` partner shifted `y -> y+1` at `(3,4)` | `check_collision` |
| C9 | degenerate `zeta = 1` (equal images, but the *same* point twice) | `check_collision`, distinctness first |
| C10 | `W := u*gamma + 1` in the fibre identity at `(4,6)` | `fibre_identity_ok` |
| C11 | one `det` field mutated in the committed `witness.json` | the receipt byte comparison in `main` |
| C12 | claimed generic degree mutated `k(d+1) -> k(d+2)`, on **all 27** members | `generic_degree_ok` (counts the fibre) |

C12 exists because the leg it guards was, until it existed, unfalsifiable: the
recorded generic degree was written as `k * (d + 1)`, nothing counted it, and an
auditor who changed that line to `k * (d + 2)`, ran the sanctioned `--emit`, and
replayed got a full green `PASS -- 27/27 grid members verified` with every
generic degree wrong. C3 and C12 both mutate a *claim* rather than an object, and
both are checked on the whole grid, not at one convenient member.

C9 is the one worth naming: `zeta = 1` satisfies `zeta^k = 1` and produces two
points with identical images — because they are the same point. Equal images
between a point and itself is not evidence of anything, so the gate checks
distinctness *before* it compares images.

The `Q(zeta_3)`/`Q(zeta_5)` arithmetic is itself in the trust path for 5
members, so it is self-tested first: `zeta^r = 1`, `Phi_r(zeta) = 0`, `zeta` has
exact order `r`, and `zeta^{-i}` inverts `zeta^i`.

## Receipt discipline

`witness.json` is **checked, never written** on a normal run: the verifier
recomputes everything, serialises it, byte-compares against the committed file,
prints `receipt-checked: witness.json`, and exits nonzero on any mismatch or if
the file is absent. Writing happens only under an explicit
`python3 -I verify.py --emit`, which prints `receipt-emitted:` and says in its
own output that this path is not the certificate. A replay never dirties the
working tree.

## What is NOT certified

- **Novelty and priority. Not checked at all.** This directory verifies exhibited
  objects. Who first constructed this family, whether the higher-weight lift is
  new, and how it relates to prior Keller-map constructions are provenance
  questions that no amount of exact arithmetic here can settle.
- **The `k = 1` row is prior art, by the paper's own account.** Stated in the
  first section, and — because a reader of the transcript or the receipt alone
  must see it too — printed in the verifier's header, appended to each of the
  seven `k=1` lines, and recorded in `witness.json` under `prior_art` and on each
  affected member. The report states that Gallagher's public notes describe the
  one-variable weighted-lift mechanism in that row, so those 7 members are not
  new with this paper. We did not locate a canonical citation for those notes and
  we do not attempt to date or adjudicate the overlap.
- **We did not replay the authors' receipts.** This is a *reimplementation from
  the paper's prose*, not a reproduction of their artifacts. The report's own
  `independent_reproduction.md` is hash-bound to the wrong document, so there
  was no intact receipt chain to replay. Agreement with their printed `(2,3)`
  expansion (leg 6) is the only place our numbers meet theirs.
- **Only the published 27-member grid.** `1 <= k <= 6`, `k < d <= 8`. Nothing is
  certified for `k > 6`, `d > 8`, or the family "in general" — the checks are
  finite and per-member. The uniform formulas suggest the pattern continues;
  suggestion is not certification.
- **The genericity step is a mathematical argument, not a machine check.** The
  verifier checks the fibre identity and the two gcd conditions at one exhibited
  rational `(V, T)` per member. The step from "holds at this point" to "holds
  generically" is the Zariski-openness argument written above, and it is on the
  reader to accept or reject it. Likewise the fibre bijection is derived in this
  README; what the machine checks is the identity it rests on.
- **Nothing about the rest of the report.** Its framing, its other sections, its
  claims about atlases of generic degrees, and its account of the relationship
  to earlier work are outside this certificate.
- **Injectivity over `Q` specifically.** Non-injectivity is certified over `Q`
  for 22 members and over an explicit cyclotomic field for 5. We do not claim
  the remaining 5 are non-injective on `Q`-rational points, only over `Q-bar`.
- **No claim that the Jacobian Conjecture literature is thereby settled.** We
  certify the exhibited maps have the exhibited properties. The consequence is
  stated above; its reception is not ours to certify.

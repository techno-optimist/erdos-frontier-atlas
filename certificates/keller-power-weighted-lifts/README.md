# Power-weighted lifts — independent exact replay of an external Keller family

**The construction is not ours.** The two-parameter family `F_{k,d} : A^3 -> A^3`
verified here is claimed by **Nathan Wilbanks and "Annie"** in *Power-Weighted
Lifts: Explicit Higher-Weight Noninjective Keller Maps* (AGNT Labs Technical
Report III, v1.0, 2026-07-21,
<https://agnt.gg/whitepapers/power-weighted-lifts-higher-weight-keller-maps.html>).
The theorem, the family, and the idea of the power-weighted lift are theirs.

**Ours is only the replay.** We rebuilt `F_{k,d}` from that report's Section 3
prose in exact rational arithmetic and re-derived, from scratch, every property
it asserts. Nothing in this directory is a discovery of this repository, and
nothing here adjudicates novelty or priority — see *What is NOT certified*.

```bash
python3 -I verify.py          # ~0.5 s, stdlib only, exit 0 iff everything passes
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
4. **Generic degree `k(d+1)`.** See the argument below.
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
preimage. `deg G = d+1` always. So if `G` is squarefree and no root of `G` makes
`V - q(w)` vanish, the fibre has exactly `k(d+1)` distinct points. Both
conditions are exact gcd computations over `Q`, and `verify.py` exhibits a small
rational `(V, T)` for each of the 27 members at which both hold. Since they are
Zariski-open conditions on `(V, T)`, holding at one point makes them hold
generically — hence generic degree `k(d+1)`, matching the claim.

(Amusing consequence the verifier records: `Q'(w) = q(w)`, so "a root of `G`
with `gamma = 0`" and "a double root of `G`" are literally the same condition.
The two gates are kept separate in code anyway; they are not allowed to rely on
that observation being true.)

### The non-injectivity witnesses — and a scoping correction

The report states its witness for **`k` and `d` both odd**:
`F(1,0,0) = F(-1,0,2) = (0,0,1)`. We confirm it on all **6** grid members with
that parity. It does **not** cover the grid: 27 members, 6 with `k,d` both odd.
So we derived witnesses for the rest, and the verifier checks each by exact
evaluation:

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
pair, the certified generic degree `k(d+1) >= 2` already forces non-injectivity
over `Q-bar` for every member.

### Consequence, stated plainly

A polynomial self-map of `A^3` with nonzero constant Jacobian determinant that
is not injective is, by definition, a counterexample to the Jacobian
Conjecture. Legs 1, 2 and 5 above are exactly that, for each of the 27 exhibited
maps. This lane therefore sits directly beside
[`certificates/jacobian-conjecture`](../jacobian-conjecture) (the dim-3
counterexample of Alpöge, 2026) and the `atlas/jc-crater` propagation graph.
What we certify is the exhibited objects and their exhibited properties — not
the surrounding narrative of either paper.

## Planted-failure controls

A checker that cannot fail certifies nothing, so 11 deliberate corruptions are
run on every replay and every one must be **rejected**, printed as
`[ok] rejected: ...`:

| # | corruption | must be caught by |
|---|---|---|
| C1 | `F1 + x*y` at `(2,3)` | determinant identity |
| C2 | `gamma` with coefficient `1` instead of `(d+k)/d` | polynomiality (x-divisibility) |
| C3 | claimed `det = -k/(k+2)` at `(3,5)` | determinant identity |
| C4 | collision partner `(-1,0,2) -> (-1,0,3)` at `(3,5)` | image comparison over `Q` |
| C5 | constant monomial added to `F1` at `(2,3)` | torus-weight gate |
| C6 | one coefficient of the paper's printed `F1` at `(2,3)` flipped | anchor check |
| C7 | planted double root of the fibre equation at `(2,5)` | squarefree gcd gate |
| C8 | `Q(zeta_3)` partner shifted `y -> y+1` at `(3,4)` | image comparison over `Q(zeta_3)` |
| C9 | degenerate `zeta = 1` (equal images, but the *same* point twice) | distinctness gate, which runs first |
| C10 | `W := u*gamma + 1` in the fibre identity at `(4,6)` | fibre identity |
| C11 | one `det` field mutated in the committed `witness.json` | receipt byte comparison |

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
- **The `k = 1` row is prior art, by the paper's own account.** The report states
  that Gallagher's public notes describe the one-variable weighted-lift
  mechanism in that row. So the 7 members with `k = 1` are not new with this
  paper. We did not locate a canonical citation for those notes and we do not
  attempt to date or adjudicate the overlap; we simply record that the paper
  itself disclaims that row.
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

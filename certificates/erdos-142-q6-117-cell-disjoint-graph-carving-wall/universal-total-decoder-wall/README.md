# Universal minimum-rank wall for total deterministic overlap/reuse decoders

Date: 2026-08-19

This theorem closes the finite-state-count escape left by the
earlier two- and three-state packets.  It concerns the fixed complete `q=42`
full-box alphabet and a total deterministic decoder.  Physical boxes may be
reused from different states, transitions may depend on the source state, and
the potential may depend arbitrarily on the entire decoded state path.

The conclusion is a whole-word Farkas wall for **every finite number of
states**.  The proof uses a minimum-rank idempotent of the transition monoid;
it does not assume that the decoder is synchronizing or that its letters are
permutations.

## 1. Exact interface and ownership assumptions

Let `A` be the 280,917 half-open four-dimensional `q=42` boxes obtained by
refining the fixed 117-cell support.  Let

```text
delta : S x A -> S
```

be a complete, total, deterministic transition map on a finite state set,
with one fixed start state `s_*` and an accepting set.  We assume every state
reachable from `s_*` has a physical suffix leading to acceptance.  Strong
connectivity is sufficient but not necessary.  This is a substantive seam:
ordinary deletion of reachable dead states generally makes the remaining
decoder partial and does not satisfy the stated interface.

The start state and determinism give every physical box word one unique state
path.  A physical word is therefore counted once, not once per possible state
label.  Reusing the same one-block box from several source states is allowed.

Suppose, for contradiction, that accepted physical points have a potential
`H` satisfying every pointwise torus-midpoint inequality

```text
H(X) + H(Z) >= 2 H(Y) + ||X-Z||_raw^2.               (1)
```

`H` may be global, nonadditive, unbounded, state-aware, and otherwise
arbitrary.  No shell or range hypothesis is used.

## 2. Frozen physical packet

One `q=42` size-seven lift starts from the cyclic two-dimensional template

```text
p0=( 2,29)   p1=( 8,41)   p2=(14,11)   p3=(20,23)
p4=(26,35)   p5=(32, 5)   p6=(38,17).
```

In the chosen coarse cell, the varying pair is translated by `+(21,14)`
modulo 42 and the first pair is fixed at `(21,14)`.  Thus the actual
four-dimensional canonical box codes used below are

```text
p0=(21,14,23, 1)   p1=(21,14,29,13)   p2=(21,14,35,25)
p3=(21,14,41,37)   p4=(21,14, 5, 7)   p5=(21,14,11,19)
p6=(21,14,17,31).
```

The distinction matters for the raw canonical-coordinate cost, which is not
translation invariant across the half-open representative boundary.  The seven
unit-weight midpoint rows are

```text
(p1,p0,p6)
(p0,p1,p2)
(p0,p2,p4)
(p1,p3,p5)
(p3,p4,p5)
(p4,p5,p6)
(p2,p6,p3),
```

where the middle entry is the midpoint.  Their incidence on the seven roles
is zero.  Their exact squared endpoint costs are

```text
11/7  intrinsic torus-geodesic,
16/7  raw canonical-coordinate.                         (2)
```

Taking the same strict-interior offset in all seven boxes turns these modular
cell identities into identities of actual physical points.

## 3. Minimum-rank idempotent lemma

Let `M` be the finite transition monoid on `S`, using the convention that a
physical word acts from left to right.  Choose an element of minimum image
size `r`.  A positive power of it is idempotent, and minimality forces that
power to retain rank `r`.  Thus there is a physical word `u` whose
transformation `e` satisfies

```text
e^2=e,   |im(e)|=r.
```

Put `I=im(e)`.  The restriction of `e` to `I` is the identity.

For packet role `p_i`, let `tau_i` be its state transformation.  Consider the
word `u p_i u`, whose transformation applies `e`, then `tau_i`, then `e`.
It belongs to `M`, so its rank is at least `r`.  It factors through `I` and
has image in `I`, so its rank is at most `r`.  Equality follows.

Consequently the map

```text
g_i : I -> I,       g_i(x)=e(tau_i(x)),
```

is onto and hence is a permutation.  This is the only semigroup input.

Let `L` be a common multiple of the finite orders of `g_0,...,g_6`.

## 4. Seven accepted words

Write `p=e(s_*)`.  Since `p` is reached by the physical prefix `u`, the
coaccessibility assumption supplies one common physical accepting suffix
`s` from `p`.  For each packet role form the physical word

```text
W_i = u (p_i u)^L s.                                  (3)
```

After the prefix `u`, the state is `p` in `I`.  Each chunk `p_i u` acts as
the permutation `g_i` on `I`, so its `L`-th power returns `p` to itself.
All seven words therefore reach the same state `p` before the identical
suffix `s`, and all seven are accepted.

At every position belonging to `u` or `s`, the seven physical point words use
the same point, so every lifted row is diagonal there.  At each of the `L`
role positions, the seven words use the frozen packet `p_0,...,p_6` with a
common strict-interior offset.  Hence each of the seven rows in Section 2 is
an actual whole-word torus-midpoint row.

Sum (1) over those seven rows.  The coefficient of every arbitrary value
`H(W_i)` is zero.  For the project's raw canonical-coordinate convention,
the exact right side is

```text
L * 16/7 > 0,
```

a contradiction.  The same packet also gives the positive intrinsic
torus-geodesic right side `L*11/7` if that weaker cost convention is used.

## 5. Consequence and scope

Under the stated interface, no finite-state transition-memory construction
can evade the q42 packet by increasing the number of states.  In particular,
the theorem includes nonsynchronizing, nonpermutation transition monoids and
strictly strengthens the earlier at-most-three-state classification.

The full alphabet has row sum 280,917 and formal per-block rate

```text
280917/42^4 = 13/144 = 49/576 + 1/192,
```

so the obstruction acts directly in the mass-beating rate regime.

Not covered:

- partial state-dependent decoders, equivalently totalizations with a
  reachable non-coaccessible dead state;
- nondeterministic decoders or multiple accepted labels for one physical word
  without a single-valued ownership rule;
- state-dependent carving of the packet roles;
- arbitrary overlapping measurable subtiles rather than the complete q42
  full-box alphabet;
- a positive EHPS shell, an improved `r_3(N)` bound, or Problem 142.

The true deterministic escape is therefore partial availability: the proof
needs every packet role `p_i` to be legal after every occurrence of the
minimum-rank word `u`, and it needs `e(s_*)` to have an accepting suffix.

## 6. Exact replays

The primary stdlib replay reconstructs the 280,917-box alphabet and the exact
physical packet, checks its seven midpoint rows and cost, exhausts the
minimum-rank sandwich implication for every idempotent/transformation pair on
up to five states, and instantiates the synchronized word construction on a
strongly connected four-state nonsynchronizing nonpermutation decoder.

The independent replay uses a separate implementation to enumerate all 699
identity-containing submonoids of the full three-state transformation monoid
and verifies all 1,623 minimum-rank idempotents and 12,868 associated
permutation sandwiches.  It separately checks a transitive rank-two word
wall plus the dead-sink and trimmed-partial interface seams.

Run both with:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

Success markers:

```text
PASS_UNIVERSAL_TOTAL_DECODER_WALL
PASS_MINRANK_IDEMPOTENT_SANDWICH_AUDIT
```

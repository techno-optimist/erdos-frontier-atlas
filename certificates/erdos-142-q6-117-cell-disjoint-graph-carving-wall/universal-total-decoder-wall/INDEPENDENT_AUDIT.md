# Minimum-rank idempotent sandwich: universal finite-state wall and exact scope

Date: 2026-08-19.  Independently written hostile audit, promoted with the
total-decoder overlap theorem after native and WSL replay.

## Outcome

The minimum-rank-idempotent argument is correct and strictly stronger than
the frozen two- and three-state classifications.  Under the complete,
deterministic, coaccessible physical-alphabet interface, it closes **every
finite state count**.  There is no surviving four-state transformation-monoid
case.

The theorem does not extend for free to a decoder completed by a dead sink or
to state-dependent partial/carved alphabets.  Ordinary automaton trimming
removes the dead sink but turns some physical letters into partial maps; that
loses exactly the transformation-monoid hypothesis used by the proof.

## 1. Algebraic lemma

Let `M` be a finite transformation monoid on a nonempty finite state set `S`.
Choose an idempotent `e in M` of minimum transformation rank `r`, and put

```text
I = im(e).
```

Such an `e` exists: take a minimum-rank element and then an idempotent power.
The power cannot have smaller rank by minimality.

For every `a in M`, the sandwich

```text
t_a = e a e
```

has image contained in `I`, so `rank(t_a)<=r`.  It also belongs to `M`, so
minimum-rank minimality gives `rank(t_a)>=r`.  Thus its image is exactly `I`.
Because `e` fixes `I` pointwise, the entire image of `t_a` is already attained
from inputs in `I`.  Therefore

```text
t_a restricted to I is a permutation of I.                (1)
```

This is the missing interpolation between a reset monoid (`r=1`) and a
permutation monoid (`r=|S|`).  No transitivity, deadlock-pair classification,
or case split by state count is needed.

## 2. Application to one q42 size-seven packet

Start with the cyclic two-dimensional template

```text
p0=( 2,29)  p1=( 8,41)  p2=(14,11)  p3=(20,23)
p4=(26,35)  p5=(32, 5)  p6=(38,17)
```

for the varying coordinate pair.

In the audited lift the varying pair is translated by `+(21,14)` modulo 42
and the first pair is fixed at `(21,14)`.  The actual canonical q42 codes are

```text
p0=(21,14,23, 1)  p1=(21,14,29,13)  p2=(21,14,35,25)
p3=(21,14,41,37)  p4=(21,14, 5, 7)  p5=(21,14,11,19)
p6=(21,14,17,31).
```

This explicit lift is needed because raw canonical-coordinate cost is not
translation invariant across the representative boundary.  Use the balanced
plan

```text
(p1,p0,p6), (p0,p1,p2), (p0,p2,p4), (p1,p3,p5),
(p3,p4,p5), (p4,p5,p6), (p2,p6,p3).
```

The exact one-block endpoint costs are

```text
11/7  intrinsic torus-geodesic,
16/7  raw canonical.
```

Let `a_i` be the total state transformation of role `p_i`, and let the common
physical word `u` induce `e`.  States act on the right.  If

```text
q = s_* u in I,
L = r!,
```

then (1) gives

```text
q (a_i e)^L = q
```

for all seven roles.  If `v` is one decoded suffix from `q` to an accepting
state, all seven physical words

```text
w_i = u (p_i u)^L v                                      (2)
```

are accepted.

At every `p_i` position, the seven words in (2) carry the frozen packet plan.
Every block of `u` and `v` is common across the seven words and is therefore
diagonal.  The seven whole-word potential coefficients cancel exactly, while
the positive endpoint costs are

```text
L*(11/7) intrinsic,      L*(16/7) raw.                    (3)
```

Choosing one common strict-interior offset in every packet block makes all
midpoint congruences actual physical torus identities.  Thus the proof is not
a centre-grid argument.

The contradiction in (3) permits an arbitrary global, nonadditive,
unbounded, state-aware value on every accepted word.  It uses no local
potential ansatz and no shell-range assumption.

## 3. Precise decoder theorem

The argument applies whenever all of the following hold:

1. `S` is finite.
2. Every physical box in one fixed global alphabet induces a **total** map
   `S -> S`; in particular, every role `p_i` and every symbol of `u` is
   available from every state it may encounter.
3. Decoding from one fixed start is deterministic, so a physical word has one
   owned state path and is counted once rather than with path multiplicity.
4. The state `q=s_*u` has one physical suffix to acceptance.  Requiring every
   retained state to be coaccessible is a convenient stronger assumption.
5. The same complete physical role box can be reused at every occurrence;
   it is not replaced by state-owned carved subsets with incompatible
   residual offsets.

Accessibility of every state and strong connectivity are unnecessary.
Coaccessibility of `q`, not transitivity, is the acceptance property actually
used.

For the complete 280,917-symbol q42 alphabet, the formal full-alphabet rate
is still

```text
280917/42^4 = 13/144 = 49/576 + 1/192.
```

The wall is independent of that rate: it rules out pointwise coercivity for
any complete finite decoder satisfying the five conditions.

## 4. Hostile scope audit

### Dead states and the word “trimmed”

Consider a complete two-state decoder with live start/accept state `0` and a
dead sink `d`.  Let every packet role send both states to `d`, which then
loops forever.  Its minimum-rank idempotent is the constant map to `d`, but

```text
s_* e = d
```

has no accepting suffix.  The sandwich construction therefore does not
produce accepted wall words.

Removing `d` by ordinary trim does not repair the hypothesis: the packet
roles become undefined from state `0`.  Thus the phrase “after the usual
trim” is safe only if one additionally asserts that the restricted global
alphabet remains total.  Completeness before trim plus trim after the fact is
not enough.

This example isolates a proof seam; it is not claimed to be a globally
coercive high-rate q42 construction, since other retained physical packets
may still kill its accepted language.

### Partial/state-owned alphabets

For partial maps there need not be a transformation monoid on the live state
set.  The replay includes a two-state trimmed partial interface in which even
roles are owned only at state `0` and odd roles only at state `1`.  Both states
are accessible and coaccessible using other partial symbols, but no state
admits all seven roles.  Neither `e a_i e` nor the common words (2) are defined
for all `i`.

Completing this interface by a sink returns to the previous dead-state
failure.  Hence partial/state-carved alphabets are the genuine deterministic
escape boundary exposed by the audit.

### Physical ownership

State-dependent transitions are harmless when each physical letter is still
one total map.  State-dependent **subtiles** are different: the common
strict-interior packet point used at one visit may not belong to the role
piece owned at a later state.  The theorem must not silently identify these
two interfaces.

Nondeterministic multiple-path decoding is also outside scope unless a unique
physical ownership/potential convention is supplied.

## 5. Exact finite replay

The standard-library verifier checks:

* the seven packet congruences, incidence cancellation, and exact costs;
* all 699 submonoids of the full three-state transformation monoid;
* all 1,623 minimum-rank idempotents in that census;
* all 12,868 associated `e a e` restrictions, with zero failures;
* a concrete transitive nonsynchronizing rank-two decoder, using `L=2`, five
  physical blocks per wall word, all 49 ordered midpoint rows, and balanced
  costs `22/7` intrinsic and `32/7` raw;
* the complete-untrimmed dead-sink seam and the trimmed-partial ownership
  seam.

Replay:

```powershell
python -I -u .\independent_replay.py
```

Final marker:

```text
PASS_MINRANK_IDEMPOTENT_SANDWICH_AUDIT
```

## 6. Consequence for the overlap/reuse search

There is no finite `>=3`-state complete deterministic transformation monoid
that avoids both reset synchronization and permutation repetition: the
minimum-rank sandwich always creates permutation repetition on its minimal
image.  Any surviving overlap/reuse architecture must change the interface,
most plausibly through partial/context-carved transitions, nondeterministic
ownership, or an infinite-state mechanism.  None of those is constructed or
ruled out here.

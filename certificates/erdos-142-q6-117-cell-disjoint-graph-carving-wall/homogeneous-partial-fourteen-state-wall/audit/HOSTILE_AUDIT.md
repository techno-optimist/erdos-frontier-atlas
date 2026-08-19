# Hostile audit: at-most-fourteen-state structural closure

Date: 2026-08-19. Verdict: **APPROVE**.

This is a read-only audit of
`D:\p42_scratch\erdos142_q42_partial_fourteen_state_closure_20260819`.
No producer file was edited.  The audited producer manifest has SHA-256

```text
e25f34d571ddeb3b7dedf99924a00b2f2511d90777962f01ebeda97f4ce1a5eb.
```

Both producer replays pass byte-identically on native Windows and WSL.  The
separate hostile core replay in this directory passes on both runtimes.

## 1. Live-trim reduction

The reduction is sound.  For a fixed start and accepting set, deleting an
unreachable state or a state with no path to acceptance preserves every
accepted word exactly.  Making transitions into deleted states undefined is
therefore also exact.  Condensing the remaining finite nonnegative weighted
matrix into SCCs expresses every accepting path as a bounded-length sequence
of within-SCC walks.  Consequently the accepted-mass limsup rate is the
maximum Perron root of the live SCCs, equivalently the Perron root of the
whole live trim.  An ambient reachable but noncoaccessible sink is irrelevant.

If this rate exceeds `B`, a maximizing SCC has Perron root above `B`.
Deleting its exits gives precisely its principal strong partial table.
Reachability and coaccessibility provide one fixed prefix into a selected SCC
start and one fixed suffix from a selected singleton SCC target to acceptance.
Prepending and appending these words to all seven copies adds only common
columns, whose red counts are zero or seven.  It preserves a unit-red core
column and produces seven accepted words of one common length.

The hostile planted control has start 0, accepting state 3, live SCC `{1,2}`,
and a reachable noncoaccessible state 4 with ambient row weight `B+R`.  Its
trim deletes exactly state 4.  On the live SCC,

```text
blue: 1->2->1,
red:  1->1, 2->accepting exit,
det(BI-W_SCC)=-BR=-4644206280<0.
```

The lifted accepted words have red-count vector

```text
(0,1,1,0,7),
```

so the prefix, active core, singleton exit, and accepting suffix are all
exercised literally.

## 2. Strict Perron equality boundary

The equality classification is correct.  If the blue map contains a cycle,
the corresponding `B`-weighted cycle matrix `H` has `rho(H)=B` and satisfies
`0<=H<=W`.  Since the table is strong, `W` is irreducible.  Strict Perron
monotonicity gives `rho(W)>B` whenever `W!=H`.

Equality can therefore occur only when that blue cycle spans every state and
there are no red transitions.  Conversely this blue-only spanning cycle is
irreducible with constant row sum `B`, so its Perron root is exactly `B`.
There is no proper-cycle equality seam: strong connectivity forces an edge
leaving a proper blue cycle, and the first leaving edge must be red because
the blue successor of every cycle vertex remains on the cycle.

As adversarial controls, for every `1<=m<=14` a spanning blue cycle with one
additional red self-loop has

```text
det(BI-W)=-R*B^(m-1)<0,
```

while the blue-only version has Perron root exactly `B`.  The producer's exact
small-table census independently recovers equality counts `(m-1)!` through
four states and finds no other equality table.

## 3. Word construction and physical lift

The cyclic-above word construction is valid for every ordered start/target
pair.  From a cycle vertex `x`, strong connectivity supplies a defined red
edge `x->y` and a return word `p` of length at most `m-1`.  Thus
`u=red p` is a red-containing loop at `x` of length at most `m`.  If the blue
cycle has length `k`, both `u^k` and the all-blue word of length `k|u|` return
to `x`: the first because `u` is a loop, the second because its length is a
multiple of `k`.  One exceptional copy follows `u^k`; six ordinary copies
follow blue.  Unit columns occur at every red letter of the exceptional word.
Common prefix/suffix paths then give the requested ordered endpoints.  The
bound

```text
(m-1)+k|u|+(m-1) <= m^2+2m-2
```

is correct.  The independent producer replay checks 11,025 planted ordered
pairs through 14 states and reaches the sharp planted horizon 222 at `m=14`.

The q42 lift uses exactly the previously frozen physical theorem.  The
independent frozen auditor (SHA-256
`2a68daeab13b46452768a7e437118f596d2bc7d0687bf13b9f189a621f7425ca`)
was rerun.  It reconstructs both packet layers, all 17,640 support-disjoint
packets, all 441 actual size-seven packets, all 3,087 cyclic red alignments,
all ordered midpoint rows and carries, and positive raw cost in every
alignment.  Its terminal verdict is

```text
PASS_INDEPENDENT_SIX_SCOPE_AND_PHYSICAL_HOSTILE_REPLAY.
```

The new hostile replay also physically lifts the planted accepted witness for
all seven choices of red role.  Its two unit columns have aggregate raw costs

```text
(32/7,44/7,40/7,48/7,44/7,36/7,36/7),
```

respectively by cyclic alignment.  All seven physical words are distinct and
the seven fixed Farkas rows cancel every whole-word potential coefficient.

Nonblocking packaging note: the structural producer says that the physical
lift is unchanged but does not itself hash-bind that earlier package.  A
standalone promoted aggregate should retain or add the existing frozen
physical replay.  This is dependency hygiene, not a theorem defect; the
dependency was independently bound and replayed here.

## 4. The fifteen-state statement is an honest nonclaim

For the 15-state blue chain with every red edge returning to state zero,
`P=(I-A)^(-1)` gives a rank-one `PC` with Perron root 15.  Hence the feedback
at `lambda=B` is exactly

```text
15R/B = 600/597 = 200/199 > 1.
```

Equivalently,

```text
det(lambda I-W)
 = lambda^15 - R*sum_(k=0)^14 B^k lambda^(14-k),
det(BI-W)=B^14(B-15R)<0,
```

so this strong blue-acyclic table really has `rho(W)>B`.  It proves that the
uniform `mR<B` Collatz closure stops at 14.  It does not say the table is
multisunflower-free and therefore does not disprove a separate fifteen-state
wall.  The producer states that limitation explicitly and makes no `m=15`
closure claim.

## 5. Replay evidence

Producer, native and WSL:

```text
PASS_EXACT_Q42_HOMOGENEOUS_PARTIAL_STRUCTURAL_CLOSURE
PASS_INDEPENDENT_Q42_PARTIAL_STRUCTURAL_AUDIT
PASS_AT_MOST_FOURTEEN_STATE_STRUCTURAL_WALL
```

Hostile core, native and WSL:

```text
PASS_PRODUCER_HASH_BINDING
PASS_LIVE_TRIM_SINGLETON_EXIT
PASS_ACCEPTED_WORD_AND_PHYSICAL_LIFT
PASS_STRICT_PERRON_EQUALITY_BOUNDARY
PASS_M15_NONCLAIM
APPROVE_Q42_PARTIAL_FOURTEEN_STATE_STRUCTURAL_CLOSURE
```

No blocker was found.  Approved scope is exactly the frozen one-red-per-packet
q42 coloring, color-homogeneous partial deterministic interfaces with at most
14 live states, fixed-start/nonempty-accepting live-trim rate, arbitrary
ordered singleton SCC targets, and the existing physical packet lift.  The
producer correctly excludes arbitrary 15-state interfaces, same-count-only
colorings, symbol-sensitive or box-carved transitions, nondeterminism,
unbounded state, shell/integer transfer, a new `r_3(N)` bound, and Erdős
Problem 142.

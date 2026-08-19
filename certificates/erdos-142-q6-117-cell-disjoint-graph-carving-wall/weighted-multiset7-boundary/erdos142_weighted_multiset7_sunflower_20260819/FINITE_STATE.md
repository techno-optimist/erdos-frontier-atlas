# Finite-state probe

This note asks whether regularity avoids the explicit strong sunflower seam in
[THEOREM.md](THEOREM.md).  In full generality it does not.  A bounded-state
restriction does give a small exact theorem.

## Why unrestricted regularity is not a shortcut

Let a complete deterministic binary automaton accept a support family
\(\mathcal C_d\subseteq\{0,1\}^d\) at every length \(d\).  If some accepted
length slice has \(W_x(\mathcal C_d)>1\), that slice is already a winning
finite block.  Conversely, any winning safe block
\(\mathcal C\subseteq\{0,1\}^b\) generates the regular block language
\(\mathcal C^*\); its length-\(tb\) slices are the safe tensor powers
\(\mathcal C^{\otimes t}\) and have mass \(W_x(\mathcal C)^t\).

There is also an SCC/loop formulation.  At an accessible and coaccessible DFA
state, all equal-length return words form a safe block: a forbidden septuple
of return words could be given a common accepting prefix and suffix, producing
a forbidden accepted septuple.  If a live weighted SCC has spectral radius
greater than one, Perron--Frobenius growth gives an equal-length return-word
block of mass greater than one.  Thus unrestricted finite-state growth merely
repackages the original finite-block question.

Regularity becomes a genuine restriction only after the number of states (and
the convention for counting a rejecting sink) is bounded.

## Exact synchronized-product safety test

For a complete deterministic binary DFA \(A=(Q,\delta,0,F)\), a column of a
literal forbidden septuple is one of

\[
 0000000,\qquad1111111,\qquad e_1,\ldots,e_7.
\]

Build the synchronized seven-fold state graph on \(Q^7\) with one Boolean flag
recording whether an \(e_i\) column has occurred.  A forbidden accepted
septuple exists at some length if and only if a state in \(F^7\) with the flag
set is reachable.  Permuting the seven components does not affect reachability,
so the verifier exactly quotients \(Q^7\) to multisets of seven states.  This is
a finite reachability decision for safety at **all lengths**, not a horizon
test.

## Exhaustive theorem for at most three complete states

Every globally safe complete deterministic binary DFA with at most three
states satisfies

\[
 W_x(\mathcal C_d)\le1\qquad\text{for every }d\ge0.
\]

Consequently it never beats \(y^d\) at a positive length.  In particular, any
regular support-screen construction with mass greater than one needs at least
four complete states, counting its rejecting sink.

### Exhaustion counts

Fixing the start state to zero, the verifier covers every transition table and
accepting set:

| states | complete DFAs | globally safe presentations | distinct minimal safe languages |
|---:|---:|---:|---:|
| 1 | 2 | 1 | 1 |
| 2 | 64 | 23 | 4 |
| 3 | 5,832 | 1,454 | 27 |

The last column is obtained by exact reachable-state minimization and canonical
breadth-first renaming.  The three-state enumeration also contains all
languages with smaller minimal automata.

### All-length mass certificates

For a DFA with weighted transition matrix

\[
 T_{qr}=\mathbf1_{\delta(q,0)=r}+x\mathbf1_{\delta(q,1)=r},
\]

the accepted mass is \(W_d=e_0^TT^d\mathbf1_F\).  The verifier assigns each of
the 27 minimal safe languages an explicit scalar-sequence form.  The forms are:

* finite sequences supported in the first two lengths;
* constant or geometric tails;
* parity-geometric sequences satisfying \(W_{d+2}=cW_d\) with
  \(c\in\{1,x,x^2\}\) and initial values in \(\{0,x,1\}\); and
* the one exceptional form \(W_d=d x^{d-1}\) for \(d\ge1\), with \(W_0=0\),
  or its factor-\(x\) scaling.

For every assignment, the annihilating polynomial of the displayed form
divides the exact characteristic polynomial of \(T\), and its first \(|Q|\)
values equal the matrix-generated sequence.  Cayley--Hamilton therefore proves
the identity for all lengths.  The first three classes are visibly at most
one.  For the last class, \(W_1=1\) and

\[
 \frac{W_{d+1}}{W_d}=x\frac{d+1}{d}\le2x=80/597<1.
\]

This turns the enumeration into an all-length proof.  The additional printed
mass horizon through 96 is only a planted consistency check and is not used to
justify the theorem.

## Limits

The theorem is intentionally small-state.  It does not rule out a safe block
of dimension 29 or larger, does not resolve the unrestricted uniform
sunflower bound, and does not claim a physical potential.  A partial DFA must
first be completed with a rejecting sink before applying the state count.

Run `finite_state_explorer.py` directly, or run the packet-level `run.ps1`.

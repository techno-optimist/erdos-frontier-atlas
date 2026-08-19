# Weighted multiset-7-sunflower screen

## Scope and constants

This is a theorem about a **binary-support packet screen only**.  It neither
constructs a physical potential nor proves that passing the support screen is
sufficient for physical packet avoidance.

Let

\[
 B=263277,\qquad R=17640,\qquad G=1058841/4,
\]

and put

\[
 x=R/B=40/597,\qquad y=G/B=2401/2388.
\]

For a family \(\mathcal C\subseteq 2^{[d]}\), define its weighted mass by

\[
 W_x(\mathcal C)=\sum_{S\in\mathcal C}x^{|S|}.
\]

The literal multiset obstruction is a seven-term multiset
\((S_1,\ldots,S_7)\) drawn from \(\mathcal C\) such that every coordinate has
column weight in \(\{0,1,7\}\), and at least one coordinate has weight one.
The seven physical words are distinct, but their support patterns may repeat.
All statements below concern this literal support-level rule.

## Theorem 1: exact reduction of the multiset rule

A support family is safe from the literal obstruction if and only if

1. it is an antichain under proper inclusion; and
2. it contains no seven **distinct** sets forming a nontrivial ordinary
   7-sunflower.

### Proof

If \(A\subsetneq B\) lie in the family, take six copies of \(A\) and one copy
of \(B\).  Coordinates in \(A\) have weight seven, coordinates in
\(B\setminus A\) have weight one, and all other coordinates have weight zero.
Thus every safe family is an antichain.  This is the repeated-pattern seam.

Conversely, suppose an antichain has a forbidden multiset.  Let \(K\) be the
set of weight-seven coordinates and write \(S_i=K\mathbin\dot\cup P_i\).
Every coordinate outside \(K\) has weight at most one, so the petals \(P_i\)
are pairwise disjoint.  If two support patterns repeat, say \(S_i=S_j\), then
their equal, disjoint petals must both be empty.  Hence \(S_i=S_j=K\).  Since
some weight-one coordinate exists, another \(S_\ell\) strictly contains
\(K\), contradicting the antichain property.  Therefore all seven patterns
are distinct and form an ordinary nontrivial 7-sunflower.  The reverse
implication is immediate.  \(\square\)

In particular, a uniform family is literally safe exactly when it has no
seven distinct members forming an ordinary 7-sunflower.

## Theorem 2: tensor closure and multiplicativity

For \(\mathcal C\subseteq2^{[d]}\) and
\(\mathcal D\subseteq2^{[e]}\), on disjoint coordinate blocks define

\[
 \mathcal C\otimes\mathcal D
 =\{S\cup(d+T):S\in\mathcal C,\ T\in\mathcal D\}.
\]

If both factors are literally safe, then their tensor product is literally
safe, and

\[
 W_x(\mathcal C\otimes\mathcal D)
 =W_x(\mathcal C)W_x(\mathcal D).
\]

### Proof

Project any putative forbidden septuple in the product onto each coordinate
block.  Each projection again has all column weights in \(\{0,1,7\}\).  If a
projection has a weight-one coordinate, it is a forbidden septuple in that
factor.  Safety therefore forces both projections to have only weights zero
and seven.  In each block all seven projected patterns are then identical,
so the product septuple has no weight-one coordinate, a contradiction.
Multiplicativity follows from \(|S\cup(d+T)|=|S|+|T|\).  \(\square\)

Consequently, one block with \(W_x(\mathcal C)>y^d\) would beat the gate at an
exponential rate under tensor powers.  A block with mass merely greater than
one also grows exponentially, but it need not beat \(y^d\).

## Theorem 3: uniformization and the exact base 597/40

There exists a finite literally safe family of weighted mass greater than one
if and only if there exist some \(n,k\) and a \(k\)-uniform 7-sunflower-free
family \(\mathcal F\subseteq\binom{[n]}k\) satisfying

\[
 |\mathcal F|x^k>1,
 \qquad\text{equivalently}\qquad
 |\mathcal F|>(597/40)^k.
\]

### Proof

The reverse direction is immediate.  For the forward direction, tensor a
safe \(\mathcal C\subseteq2^{[d]}\) of mass \(W>1\) with itself \(t\) times.
The resulting safe family has mass \(W^t\) and at most \(td+1\) rank slices.
Some rank slice therefore has weighted mass at least
\(W^t/(td+1)>1\) for all sufficiently large \(t\).  A rank slice is a safe
subfamily and is uniform, so Theorem 1 applies.  \(\square\)

Thus a global proof that no mass-above-one block exists would require, in
particular, the explicit uniform bound
\(M_k\le(597/40)^k\) for every \(k\), where \(M_k\) denotes the unrestricted
ground-set maximum for a \(k\)-uniform 7-sunflower-free family.  Standard
general sunflower bounds do not supply this sharp fixed numerical base.  No
such global conclusion is claimed here.

## Theorem 4: exact first two uniform maxima

\[
 M_1=6,\qquad M_2=42.
\]

### Proof

Seven distinct singletons are a sunflower and six are safe, giving \(M_1=6\).

Identify a 2-uniform family with the edge set of a finite simple graph.  Its
7-sunflowers are precisely a seven-edge star or a seven-edge matching.  A safe
graph therefore has maximum degree \(\Delta\le6\) and matching number
\(\nu\le6\).  By Vizing's theorem its edges split into at most
\(\Delta+1\le7\) matchings, each of size at most six, so it has at most 42
edges.  Two vertex-disjoint copies of \(K_7\) have 42 edges, degree six, and
matching number \(3+3=6\), proving equality.  \(\square\)

The witness mass is

\[
 42x^2=42(40/597)^2<1.
\]

## Theorem 5: uniform recursion

For every \(k\ge3\),

\[
 M_k\le 6\bigl(kM_{k-1}-(k-1)\bigr)<6kM_{k-1}.
\]

Hence the explicit caps used below are

\[
 A_1=6,\quad A_2=42,\quad
 A_k=6\bigl(kA_{k-1}-(k-1)\bigr) (k\ge3).
\]

The first values are

\[
 A_3=744,\quad A_4=17838,\quad A_5=535116,
 \quad A_6=19264146.
\]

### Proof

Take a maximal matching of members of a \(k\)-uniform sunflower-free family.
It has at most six members, since seven disjoint members form a sunflower with
empty core.  Its union \(U\), of size at most \(6k\), meets every member of the
family.  For each \(u\in U\), the link
\(\{S\setminus\{u\}:u\in S\in\mathcal F\}\) is a
\((k-1)\)-uniform 7-sunflower-free family.  If the matching has \(m\le6\)
members, then \(|U|=km\), so the link sum is at most \(kmM_{k-1}\).  Every
family member is counted at least once in that sum, while each of the \(m\)
chosen matching members is counted \(k\) times.  Therefore the mandatory
overcount is at least \((k-1)m\), and

\[
 |\mathcal F|+(k-1)m\le kmM_{k-1}.
\]

The rearranged right side is increasing in \(m\), so \(m\le6\) gives the
stated bound.  \(\square\)

For comparison, the six-cone operation is a safe recursive construction: put
six copies of a safe uniform family on disjoint coordinates and give the
members of copy \(i\) a new private apex \(a_i\).  A valid seven-septuple
cannot distribute its members nontrivially among only six apex classes, so it
must lie in one safe copy.  This multiplies mass by \(6x=240/597<1\); it does
not produce mass growth.

## Theorem 6: exact rational LYM/cap relaxation

Let \(\mathcal C\subseteq2^{[d]}\) be a nonempty literally safe family that
does not contain the empty set, and let
\(n_k=|\mathcal C\cap\binom{[d]}k|\).  Theorem 1 and LYM give

\[
 \sum_{k=1}^d\frac{n_k}{\binom dk}\le1,
 \qquad
 0\le n_k\le\min\{\binom dk,A_k\}.
\]

Put \(z_k=n_k/\binom dk\).  Dropping integrality gives the finite exact LP

\[
 U_d=\max\left\{
 \sum_{k=1}^d \binom dk x^k z_k:
 \sum_kz_k\le1,
 0\le z_k\le
 \frac{\min\{\binom dk,A_k\}}{\binom dk}
 \right\}.
\]

This is fractional knapsack: sort ranks by the exact rational density
\(\binom dkx^k\), then fill their exact rational caps until one unit of LYM
mass is used.  The verifier evaluates this rule with `Fraction` arithmetic and
proves by exact comparisons that

\[
 U_d<1\quad(1\le d\le28),
 \qquad U_{29}>1,
\]

and

\[
 U_d<y^d\quad(1\le d\le31),
 \qquad U_{32}>y^{32}.
\]

Because \(\{\varnothing\}\) is safe and has mass one, while any antichain
containing \(\varnothing\) contains no other member, the **exact optimum over
all safe families is 1 for every \(d\le28\)**.  Also, no safe family beats the
gate \(y^d\) for \(d\le31\).

The strict inequalities at \(d=29\) and \(d=32\) go in the wrong direction
only for this relaxation.  They are **not constructions** and do not show that
mass greater than one exists at \(d=29\), or that the gate can be beaten at
\(d=32\).

Selected display values (exact rationals are computed in the verifier) are:

| d | nonempty LP upper \(U_d\) | gate \(y^d\) |
|---:|---:|---:|
| 20 | 0.754786392365 | 1.114696793862 |
| 24 | 0.863646580726 | 1.139168853940 |
| 27 | 0.957147056302 | 1.157874835054 |
| 28 | 0.998995043700 | 1.164178173771 |
| 29 | 1.046989737651 | 1.170515827146 |
| 31 | 1.163495018244 | 1.183294826107 |
| 32 | 1.196068596484 | 1.189736548360 |

## Explicit blocks checked

Two natural tensorizable constructions stay far below one.

* Six-symbol transversal block: split coordinates into six-position blocks
  and choose exactly one position in every block.  Its mass per block is
  \(6x=240/597<1\).  With only six symbols, seven words satisfying the column
  rule must agree in that block.
* The exact rank-two witness \(2K_7\) has mass
  \(42x^2\approx0.18856<1\).

These are valid support-screen constructions only.  They are not physical
potential constructions.

## Reproduction

Run:

```powershell
.\run.ps1
```

The verifier uses only the Python standard library.  It includes planted
positive and negative controls, exhausts all 65,536 families on four
coordinates at the comparability/reduction seam, exhausts all pairs of
three-coordinate antichains for tensor closure, verifies the \(2K_7\) graph
statistics, and evaluates every LP comparison with exact rational arithmetic.

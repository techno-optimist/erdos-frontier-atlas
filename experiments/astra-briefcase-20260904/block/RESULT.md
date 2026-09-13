# General three-hub Laurent block: informal proof

Scope: P993 / S:triage:993, ONLY the algebraic block from the supplied
`993-block.md`. No tree theorem, global partition, novelty, formalization,
publication, or upstream-status claim. Repository was not modified.

## Result

For all integers r,s,t >= 1 and **real** c,d,e >= 1, the specified block
B(r,s,t;c,d,e) has nonnegative, symmetric, centrally unimodal Laurent
coefficients (step two). This includes every positive integral scalar and
all the stated powers-of-two scalars.

The proof below has unbounded elementary arguments and 51 explicitly finite
base cases, all checked by the standalone stdlib exact-integer `check.py`.
It has received an [independent mathematical review](REVIEW.md); it is not a
machine-formalized proof. No unbounded algebraic subclaim is intentionally
left as a conjecture. The global combinatorial partition remains entirely
unresolved and is not addressed here.

Write W_n=w^n, w=z+z^{-1}, and P_j=z^j+z^{-j}, including P_0=2 and P_{-j}=P_j. The block under discussion is explicitly

    B = P_{r-s+t} + c W_r P_{s-t} + d W_s P_r P_t + e W_t P_{r-s}
        + cd W_{r+s} P_t + ce W_{r+t} P_s + de W_{s+t} P_r
        + cde W_{r+s+t}.

Call a nonnegative symmetric Laurent polynomial on one parity CU when
its coefficients increase from the edge toward the center.

## 1. Elementary closure and binomial margin

CU polynomials of compatible parity form a cone, and the product of two
CU polynomials is CU. For a self-contained justification, expand any such
polynomial in U_j=z^j+z^{j-2}+...+z^{-j}: its U_j coefficients are exactly
the nonnegative inward differences, and
U_i U_j = sum_{h=0}^{min(i,j)} U_{i+j-2h}.
In particular multiplication by w preserves CU.

Let D(N,j)=binom(N,j)-binom(N,j-1), 1<=j<=floor(N/2).
For every N>=7 and 2<=j<=floor(N/2),

    D(N,j) >= 14.                                      (1)

At N=7 the relevant differences are (14,14). Induct using Pascal:
D(N,j)=D(N-1,j)+D(N-1,j-1). Away from a newly appearing even center,
one summand is an interior difference already >=14 and the other is
nonnegative. At an even center j=N/2 the first summand is zero (the two
central coefficients of the previous odd row agree), and the second is
the previous row's last interior difference. This proves (1).

## 2. Uniform sevenfold majorants

**Single-P lemma.** If N>=7, a>=1, b>=0, N>=a+b, and N-a-b is even, then

    W_N + 7 W_a P_b                                  (2)

is CU.

Proof: if a>=2 and N>=8, factor out w and apply the assertion for
(N-1,a-1,b). Thus it suffices to treat a=1 (any N>=7) and N=7.
For a=1 and b>=2, wP_b=P_{b+1}+P_{b-1}: its coefficients are at most
one and any inward decrease is at most one. There is no decrease at the
first edge step: when b+1=N the first two coefficients are both one,
and when b+1<N the edge coefficient is zero. Thus (1) absorbs seven
times every possible decrease. For b=0,1, wP_b itself is CU.
At N=7 there are exactly 16 admissible (a,b). Direct expansion gives the
following three inward differences of (2), all nonnegative:

    (a,b): differences
    (1,0): 6,14,28      (1,2): 6,21,14
    (1,4): 13,14,7      (1,6): 6,7,14
    (2,1): 6,21,28      (2,3): 13,21,7
    (2,5): 13,7,7       (3,0): 6,28,42
    (3,2): 13,28,21     (3,4): 20,14,0
    (4,1): 13,42,49     (4,3): 27,28,7
    (5,0): 20,70,84     (5,2): 34,56,42
    (6,1): 48,112,112   (7,0): 90,210,210

This closes the induction.

**Double-P lemma.** If r,s,t>=1 and N=r+s+t>=7, then

    W_N + 7 W_s P_r P_t                              (3)

is CU.

As above, multiplication by w reduces to s=1 or N=7.
If s=1, then r+t>=6 and

    wP_rP_t = P_{r+t+1}+P_{r+t-1}
              +P_{r-t+1}+P_{r-t-1}.

Its coefficients are at most two (including the doubled P_0 or coincident
P_1 cases), and the first two edge coefficients are 1 and either 1 or 2.
Indeed the lower pair is wP_{r-t}; its two absolute indices can only meet
the upper pair when min(r,t)=1, giving a coefficient two at N-2, never
at N. Thus there is no first-step decrease, and any later decrease is
at most two. Bound (1) absorbs seven times such a decrease.
At N=7 the 15 positive triples give these three inward differences:

    (r,s,t): differences
    (1,5,1): 48,112,112   (1,4,2): 34,56,42
    (1,3,3): 27,28,7      (1,2,4): 20,14,0
    (1,1,5): 13,7,7       (2,4,1): 34,56,42
    (2,3,2): 20,28,28     (2,2,3): 13,14,21
    (2,1,4): 6,14,14      (3,3,1): 27,28,7
    (3,2,2): 13,14,21     (3,1,3): 6,7,28
    (4,2,1): 20,14,0      (4,1,2): 6,14,14
    (5,1,1): 13,7,7

**Isolated-P lemma.** If N>=7, |j|<=N-2 and j has parity N, then
W_N+7P_j is CU: an off-center spike has size one, its only possible
inward decrease occurs after the first step, and (1) applies. A spike
at exponent zero or one only raises the middle coefficient.

## 3. The unit-scalar block

Let N=r+s+t>=7. The seven non-W_N terms of B(r,s,t;1,1,1) are

    P_{r-s+t}, W_r P_{s-t}, W_s P_r P_t, W_t P_{r-s},
    W_{r+s}P_t, W_{r+t}P_s, W_{s+t}P_r.

For each such term T, W_N+7T is CU by the preceding lemmas.
For the isolated term, |r-s+t|=|N-2s|<=N-2 because
1<=s<=N-2. The single-P hypotheses hold even when its subscript is
negative, since P_{-j}=P_j. Consequently

    B(r,s,t;1,1,1) = (1/7) sum_T (W_N+7T)

is CU.

For N=3,4,5,6 there are exactly 20 positive triples. Their inward
differences, calculated directly from the eight-state definition, are:

    (1,1,1): 15
    (1,1,2): 15,8       (1,2,1): 15,12      (2,1,1): 15,8
    (1,1,3): 18,16      (1,2,2): 15,18      (1,3,1): 19,20
    (2,1,2): 15,16      (2,2,1): 15,18      (3,1,1): 18,16
    (1,1,4): 21,30,16   (1,2,3): 18,26,11   (1,3,2): 19,26,14
    (1,4,1): 23,36,16   (2,1,3): 18,24,13   (2,2,2): 15,24,12
    (2,3,1): 19,26,14   (3,1,2): 18,24,13   (3,2,1): 18,26,11
    (4,1,1): 21,30,16

Thus the unit-scalar result holds for every positive r,s,t.

## 4. All scalars >=1 by a positive shifted expansion

Put Q_j=W_j+P_j. This is CU for j>=1: its edge coefficients are 2,
the binomial interior coefficients are at least 2, and increase inward.
(The case j=1 is simply 2w.) Put

    H(a,b)=Q_a Q_b-P_{a+b}.

This is also CU. The product is CU, with outer coefficients 4; subtracting
P_{a+b} reduces only those outer coefficients to 3.

Write C=c-1, D=d-1, E=e-1. Direct multilinear expansion gives

 B(r,s,t;c,d,e) = B(r,s,t;1,1,1)
   + C W_r H(s,t) + D W_s Q_r Q_t + E W_t H(r,s)
   + CD W_{r+s}Q_t + CE W_{r+t}Q_s + DE W_{s+t}Q_r
   + CDE W_N.

All summands on the right are CU, and all scalar weights are nonnegative.
This proves the stated real-scalar result. The identity follows also from
P_aP_b=P_{a+b}+P_{a-b}; it is independently tested against active-state
construction by the checker.

## Exact replay and scope

Run:

    python3 -I experiments/astra-briefcase-20260904/block/check.py --bound 24

The run completed with:
- 13,824 unit-scalar blocks, every 1<=r,s,t<=24; no failures or ties.
- 16 single-P and 15 double-P boundary cases, all passing.
- 20 small-block base cases, all passing.
- 192 expanded-versus-active-state identities.
- 216 shifted-scalar identities against active-state construction.
- Negative control B(1,4,1;1,0,1) rejected, with [z^0]=0<[z^2]=4.

`receipt.json` contains the actual full output and all finite boundary
coefficient differences. The checker has no repository or third-party
package dependency and does not rewrite the receipt when replayed.
The larger bounded sweep is diagnostic, NOT the reason the unbounded
claim follows: that reason is the reduction and the stated finite bases.

Remaining obligations: any machine formalization; and, separately, a valid global clan-map partition and all
outside-factor/connector compatibilities needed for a tree theorem.
Neither the original special-case lemma nor this general block proof
settles those graph-theoretic obligations. No novelty check was attempted.

Local filesystem paths in this report were normalized for portable publication.

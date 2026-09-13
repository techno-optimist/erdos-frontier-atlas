# P993 / S:triage:993 — three-hub algebra, not a full tree theorem

## Proven three-hub block lemma

Put w=z+z^{-1} and P_r=z^r+z^{-r} for every integer r (in particular P_0=2).
For integers r,s,t>=1 and real c,d,e>=0, define the eight-state path block

B(r,s,t;c,d,e) = P_{r-s+t}
 + c w^r P_{s-t} + d w^s P_r P_t + e w^t P_{r-s}
 + cd w^{r+s} P_t + ce w^{r+t} P_s + de w^{s+t} P_r
 + cde w^{r+s+t}.

This formula has an elementary interpretation: each of three consecutive sites is
active or inactive. An inactive site i contributes c_i w^{r_i}. A maximal run of
active sites i,...,j contributes P_{r_i-r_{i+1}+...+(-1)^{j-i}r_j}.
Multiply over runs and inactive sites, then sum all eight states. The expansion
above follows directly; it is not an assertion of a global clan-map partition.

**Lemma.** For every integer s>=1, c,e>=0 and d>=1, B(1,s,1;c,d,e) has centrally
unimodal Laurent coefficients: [z^k]B >= [z^{k+2}]B for every k>=0.

**Proof.** Set n=s+2 and u=(1+c)(1+e). Since P_1=w,

B(1,s,1;c,d,e)
 = P_{s-2}+(c+e)w P_{s-1}+ce w^2 P_s+d u w^{s+2}
 = d u w^n + ce P_n + (c+e+2ce)P_{n-2}+u P_{n-4}.

The last identity uses wP_j=P_{j+1}+P_{j-1}, valid also at j=0 and 1.
All exponents have parity n; the other parity has only zero coefficients. By
symmetry it suffices to check that coefficients increase from the positive edge
toward zero.

For n>=5, define a_j=[z^{n-2j}]B for 0<=j<=floor(n/2). Then

- a_0=du+ce;
- a_1=du*n+c+e+2ce;
- a_2=du*binom(n,2)+u;
- a_j=du*binom(n,j) for j>=3.

The first difference is du(n-1)+c+e+ce>=0. The second is

  a_2-a_1 = du*n(n-3)/2 + 1-ce.

For n>=5, n(n-3)/2>=5 and d>=1, so this is at least
5u+1-ce = 6+5c+5e+4ce >=0.

If the third difference exists, n>=6, and

  a_3-a_2 = u*(d*n(n-1)(n-5)/6 - 1) >= 4u >=0,

because n(n-1)(n-5)/6>=5. Every subsequent difference is nonnegative by
binomial-coefficient monotonicity up to the middle.

For n=3 the only difference toward the center is

  a_1-a_0 = 2du + c+e+ce+u >=0,

since P_{n-4}=P_{-1}=P_1 merges with P_{n-2}. For n=4 the two differences are

  a_1-a_0 = 3du+c+e+ce >=0,
  a_2-a_1 = 2du+2+c+e >=0,

where the second uses P_0=2. This covers every s>=1. QED.

The bound on the middle scalar is substantive. At s=4,c=e=1,d=0,
B=P_6+4P_4+4P_2, so [z^0]B=0<[z^2]B=4. This is not an admissible
clan-derived scalar and is not a counterexample tree.

## Relation to the two-hub method

Context is the pinned [two-hub development](https://github.com/BrettRey/erdos-problem-993/blob/95f86d96dd89e5ddfff16b65f500fa9c85cb661d/formalization/clan_normalization_aristotle/RESULT.md), not a local verification of that Lean build.

The two-hub development uses r=p-1, where p is the number of odd positive
pendant-arm prefixes at a hub, and inactive-image weight c*w^r with c a power
of two. Thus r=t=1 means exactly two such odd prefixes at each outer hub; the
middle hub may have arbitrarily many. The lemma covers the natural fully-active
three-hub eight-state block in this regime. It does NOT establish that every
multiplicity map of every three-hub tree lies in such a block. In particular,
nonactive middle hubs, fewer odd prefixes, connector subdivisions, and all
outside-factor/partition compatibilities still need a global proof.

The general formula B(r,s,t;c,d,e) is retained as a concrete target; no all-r,s,t
central-unimodality theorem is claimed here.

## A separate complete tree special case (known regular family)

Let C_{m,q} be a path on m vertices with exactly q new pendant leaves attached
to every vertex, where m,q>=1. Then I(C_{m,q};x) is log-concave. In particular,
C_{3,q} has exactly three branch vertices when q>=2.

Here is a self-contained reduction to elementary binomial inequalities. Put
h=floor((m+1)/2). The path independence polynomial factors as

  I(P_m;y)=product_{j=1}^h (1+lambda_j*y),
  lambda_j=4*cos^2(j*pi/(m+2)), so 0<lambda_j<4.

This factorization follows either from the recurrence f_m=f_{m-1}+y*f_{m-2},
f_0=1,f_1=1+y, or its standard trigonometric solution. Conditioning on the
independent set chosen on the spine gives

  I(C_{m,q};x)=(1+x)^{qm} I(P_m; x/(1+x)^q)
    =(1+x)^{q(m-h)} product_{j=1}^h ((1+x)^q+lambda_j*x).

For any 0<=lambda<=4, (1+x)^q+lambda*x is log-concave. For q<=2 this is immediate.
For q>=3, increasing only the coefficient of x cannot hurt any binomial
log-concavity inequality except the one at index 2; that one is equivalent to

  lambda <= q(q+1)/(2(q-2)).

The right side is at least 5 for every integer q>=3, because
q(q+1)-10(q-2)=(q-4)(q-5)>=0. Thus it holds for lambda<=4. Products of
nonnegative log-concave sequences without internal zeros are log-concave,
proving the assertion. This is a proof of a known regular-caterpillar family,
not a novelty claim and not the irregular/subdivided-spine conjecture.

## A useful obstruction to naive recursion proofs

Take two outer hubs each carrying r>=2 pendant paths of length two, join them
through a middle hub v, and put p>=1 pendant leaves at v. These are exactly
three branch vertices. Set

  S_r(x)=(1+2x)^r+x(1+x)^r,
  A(x)=I(T-v;x)=(1+x)^p*S_r(x)^2,
  C(x)=x*I(T-N[v];x)=x(1+2x)^{2r}.

Although A and C are individually log-concave, coefficientwise nonnegativity
of their mixed log-concavity term is impossible: writing a_i=[x^i]A,c_i=[x^i]C,
at k=2r+2 one has

  2a_k c_k-a_{k-1}c_{k+1}-a_{k+1}c_{k-1}
    = -a_{2r+3}*2^{2r}<0.

Indeed deg(C)=2r+1, deg(A)=2r+p+2>=2r+3, and A has positive coefficients
through its degree. This does not disprove log-concavity of A+C. It rules out
a blanket proof that demands nonnegative mixed defects (or synchronization of
these particular two summands) for every three-hub deletion recurrence.

## Exact executable checks

Run `python3 -I check_993_block.py`.
The script independently constructs the eight states, checks the expanded and
compact identities, checks 256 exact rational instances of the lemma for
s=1,...,64, checks 27 general-block identities, and detects the d=0 negative
control. Those finite checks are safeguards on the algebra; the unbounded proof
is the coefficient-difference argument above. No tree enumeration is performed.

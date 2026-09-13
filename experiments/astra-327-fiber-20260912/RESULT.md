# Multiplier-sensitive fiber deficits

**A self-contained informal proof and an exact small certificate. Not a solution of P327, a record claim, or a Lean formalization.** Attachment: `P327`, `S:gap:327:c40419c7`; this is a method overlay, not movement of that next-cell quantity.

Liu's smooth–rough decomposition retains the forbidden pairs already present before multiplication and bounds the contribution from every smooth prefix. The construction below retains additional pairs according to the rough multiplier. At modulus `L=1` it recovers Liu's Theorem 19, written in deficit form.[8]

For a positive integer k, call a set A of positive integers **k-admissible** when `a+b` does not divide `kab` for any two distinct elements a,b of A. Let `f_k(N)` be the maximum size of a k-admissible subset of `{1,...,N}`, with `f_k(0)=0`. The argument below applies to every positive integer k.

## 1. Which multipliers activate an edge?

For positive distinct integers `a,b` and positive integer `k`, define

$$r_k(a,b)=\frac{a+b}{\gcd(a+b,kab)}.$$

For every positive integer `m`,

$$ma+mb\mid k(ma)(mb)\quad\Longleftrightarrow\quad r_k(a,b)\mid m.$$

**Proof.** Cancel `m` to obtain `a+b | kmab`. Divide `a+b` and `kab` by their gcd. The two remaining factors are coprime, so the remaining divisor must divide `m`. The reverse implication follows by multiplication. Equivalently, if `a=gu`, `b=gv`, and `gcd(u,v)=1`, then `r=(u+v)/gcd(u+v,kg)`. No primality heuristic or numerical cutoff is involved.

For instance, `r_1(1,4)=5`: the pair `(1,4)` is admissible but `(5,20)` is forbidden. Prime powers matter: `r_1(1,8)=9`, so divisibility by 3 alone does not activate this pair.

## 2. A finite partition of the rough multipliers

Fix a finite set of primes `P`, let `Q=prod(P)`, and fix `L>=1` with `gcd(L,Q)=1`. Every positive integer has a unique expression `mc` with `c` P-smooth and `gcd(m,Q)=1`.

Classify the multipliers by `d=gcd(m,L)`, for each divisor `d|L`. For real `X>=0`, define

$$R_d(X)=\#\{m\le X:\gcd(m,Q)=1,\ \gcd(m,L)=d\}.$$

Since `m=dt`, the count is **exactly**

$$R_d(X)=\sum_{E\subseteq\mathcal P(Q L/d)}(-1)^{|E|}
\left\lfloor\frac{X}{d\prod_{p\in E}p}\right\rfloor,$$

where `mathcal P` denotes the distinct prime factors, including the empty-subset term. Its density is

$$w_d=\frac1d\prod_{p\mid QL/d}(1-1/p)
=\rho_P\frac{\varphi(L/d)}L,\qquad
\rho_P=\prod_{p\in P}(1-1/p).$$

Thus `R_d(X)=w_d X+O_{P,L}(1)` and `sum_{d|L} w_d=rho_P`. This includes nonsquarefree `L`: replacing `L` by its radical loses information.

## 3. Prefix deficiencies give an all-N inequality

Fix any cutoff `C>=1`, and list **all** P-smooth integers up to C as

$$1=c_1<c_2<\cdots<c_s.$$

For each state `d|L`, construct the graph `G_d` on these vertices with an edge `{a,b}` precisely when `r_k(a,b)|d`. Let `beta_d(i)` be the independence number of its first `i` vertices. Put

$$D_d(0)=0,\quad D_d(i)=i-\beta_d(i),\quad
\Delta_d(i)=D_d(i)-D_d(i-1).$$

Adding one vertex changes the independence number by either zero or one. Consequently every `Delta_d(i)` is zero or one.

If A is k-admissible, its fiber at multiplier m is independent in `G_{gcd(m,L)}`: every recorded edge has activation modulus dividing d and hence m. Some actual edges can be absent from G_d when their activation modulus does not divide L. **They are discarded constraints, not pairs proved admissible.** Discarding them only weakens an upper bound.

Let `i(m)=#{c_i:mc_i<=N}`. Among these first `i(m)` fiber vertices at least `D_d(i(m))` must be omitted from A. These omissions are disjoint across different multipliers, by unique smooth–rough factorization. Telescoping D and exchanging the two finite sums proves

$$\boxed{f_k(N)\le N-\sum_{d\mid L}\sum_{i=1}^s
\Delta_d(i)R_d(N/c_i)}\qquad\text{for every integer }N\ge0.$$

**There is no assumed empty tail.** When `N/m>C`, the first s fiber vertices still force `D_d(s)` omissions. Vertices past C are unrestricted by this certificate. The displayed bound never discards that distinction.

Substituting the exact state densities yields the universal asymptotic bound

$$\boxed{\limsup_{N\to\infty}\frac{f_k(N)}N\le
U(P,L,C,k):=1-\sum_{d\mid L}w_d\sum_{i=1}^s\frac{\Delta_d(i)}{c_i}.}$$

For fixed P,L,C, the finite-N inequality also gives `f_k(N)<=U*N+O_{P,L,C}(1)`.

## 4. Refinement cannot weaken this certificate

Suppose `L_1|L_2` and both are coprime to Q, with P,C,k unchanged. For every m, put `d_j=gcd(m,L_j)`. Then `d_1|d_2`, so `G_{d_1}` for `L_1` is a subgraph of `G_{d_2}` for `L_2`. Every prefix has at least as large a deficiency after refinement. The exact omission sum over multipliers therefore cannot decrease, for **any N**. In particular,

$$U(P,L_2,C,k)\le U(P,L_1,C,k).$$

One must compare **cumulative deficiencies**, not individual Delta values. The increments can move to earlier prefixes. Abel summation makes the asymptotic comparison transparent:

$$\sum_i\frac{\Delta_d(i)}{c_i}
=\frac{D_d(s)}{c_s}+\sum_{i<s}D_d(i)\left(\frac1{c_i}-\frac1{c_{i+1}}\right).$$

All coefficients on the right are positive. Thus a strict deficiency improvement at any prefix in a positive-density refined state gives a strict same-cutoff improvement.

## 5. An eight-vertex worked certificate

Take `P={2,3}`, `C=12`, `L=5`, `k=1`. The complete smooth prefix is `1,2,3,4,6,8,9,12`.

| c_i | 1 | 2 | 3 | 4 | 6 | 8 | 9 | 12 |
|---|---|---|---|---|---|---|---|---|
| beta_1(i) | 1 | 2 | 3 | 4 | 4 | 5 | 6 | 6 |
| beta_5(i) | 1 | 2 | 2 | 2 | 3 | 3 | 4 | 4 |

The state weights are `w_1=4/15` and `w_5=1/15`. Deficiency increments occur at `{6,12}` in state 1 and `{3,4,8,12}` in state 5. Hence

$$U=1-\frac4{15}\left(\frac16+\frac1{12}\right)
-\frac1{15}\left(\frac13+\frac14+\frac18+\frac1{12}\right)
=\frac{317}{360}.$$

At the **same P and same eight vertices**, ignoring multiplier information (`L=1`) gives `11/12`. The improvement is in the constraint model, not the search cutoff. The exact finite bound at N=1000 is 880; it is an upper bound, not the optimum f_1(1000).

### Hand-checkable certificates, not an optimizer black box

For k=1 the entire deficiency table can be justified with disjoint forbidden pairs. At each listed threshold the pairs form a matching, so at least one element of each pair must be omitted:

| State | Threshold | Disjoint pairs |
|---|---|---|
| 1 | 6 | (3,6) |
| 1 | 12 | (3,6), (4,12) |
| 5 | 3 | (2,3) |
| 5 | 4 | (1,4), (2,3) |
| 5 | 8 | (1,4), (2,8), (3,6) |
| 5 | 12 | (1,4), (2,8), (3,12), (6,9) |

For each state-d pair (a,b), check `(da+db) | (da)(db)`. Multiplying by any further integer preserves that divisibility, so it holds for every rough multiplier in the state. The independent-set witnesses in `receipt.json` attain the matching bounds at every prefix.

For k=2, state 5 at threshold 6 has the disjoint edge `{1,4}` and triangle `{2,3,6}`. They force three omissions. The same final perfect matching forces four at threshold 12. The intermediate thresholds 3 and 4 use the same matchings as above. Thus this case also has a short certificate, not just a reported optimum.

One can even write the resulting bounds using only floors. Define

$$H(X)=X-\lfloor X/2\rfloor-\lfloor X/3\rfloor+\lfloor X/6\rfloor,
\qquad H_q=H(\lfloor N/q\rfloor).$$

Then, for every nonnegative integer N,

$$f_1(N)\le N-H_6-H_{12}-H_{15}-H_{20}-H_{40}+H_{30},$$
$$f_2(N)\le N-H_6-H_{12}-H_{15}-H_{20}.$$

These follow from `R_5(X)=H(floor(X/5))` and `R_1(X)=H(floor(X))-H(floor(X/5))`. The tests check all displayed pair/triangle certificates directly and compare the floor formulas against the general bound at every integer from 0 through 500; that bounded replay checks the implementation, while the algebra above proves the identity for all N.

**Do not replace r by gcd(r,L).** For `(a,b,k)=(1,24,1)`, r is 25. A multiplier 5 in state 5 for L=5 does not activate the pair; a multiplier 25 does. That is a planted negative control in the tests, not a reason to enlarge a sequence cutoff.

These constants are demonstrations, not competitive records: Liu reports the substantially stronger bounds 0.7769 and 0.7630 using a larger smooth graph. Those computations were not reproduced here.[8]

## Remaining obligations and transfer limits

- Human mathematical review and any desired formalization of the general lemma remain; finite graph checks do not formalize its all-N argument.
- No novelty/priority claim is made for the refinement. The specific comparison above is with the cited modulus-blind formula, not with every method in the literature.
- The asymptotic extremal density and interactions **between** distinct smooth–rough fibers are not determined here.
- A useful further question is which activation moduli give the most prefix-deficiency gain for a small state partition. Merely increasing C is not the contribution of this bundle.
- Other unit-fraction problems can reuse the activation identity. They need their own forbidden-configuration and partition argument; an Atlas tag match is not a theorem transfer.

## Sources

[8] https://leon2k2k2k.github.io/assets/pdf/erdos/erdos327.pdf

# A sharp limitation of one-dimensional cancellation

**Scope:** an explicit theorem about generic signed coefficients, motivated by
Erdős #969. This is not a theorem about the Möbius coefficients, not a new
bound for the squarefree error, and not a proof or disproof of RH. The argument
below is a human-readable mathematical proof proposal; independent review is
recorded separately. It is not Lean-formalized. No novelty or priority is claimed.

## 1. The transfer being tested

For real coefficients `a_n` with `|a_n| <= 1`, put

\[
 A(t)=\sum_{n\le t}a_n,\qquad c_a=\sum_{n\ge1}\frac{a_n}{n^2},
 \qquad T_a(x)=\sum_{n\ge1}a_n\left\lfloor\frac{x}{n^2}\right\rfloor,
 \qquad E_a(x)=T_a(x)-c_a x.
\]

The series for `c_a` converges absolutely. The floor sum is finite for every
finite `x >= 1`. For `a_n=mu(n)`, square-divisor inclusion–exclusion identifies
`T_a(x)` with the squarefree counting function and `c_a=1/zeta(2)`.
The source status and the stronger pointwise target are discussed in
`FRESHNESS.md`; this coefficient identity itself is classical.

We ask what follows from **only**

\[
 |a_n|\le1,\qquad |A(t)|\le C\sqrt t\quad(t\ge1). \tag{H}
\]

The epsilon-free envelope (H) is a model assumption, **not** a claimed
consequence of RH for the Möbius function. The usual RH-equivalent Mertens
bound allows every positive epsilon.

## 2. Upper transfer: exponent two-fifths

**Theorem 1.** Under (H), for every real `x >= 1`,

\[
 |E_a(x)|\le (1+14C)x^{2/5}. \tag{1}
\]

**Proof.** Let `D >= 1` be an integer, `D <= sqrt(x)`, and
`K=floor(x/D^2)`. Counting pairs `(n,m)` with `n>D` and `mn^2<=x` gives the
exact identity

\[
 T_a(x)=\sum_{n\le D}a_n\lfloor x/n^2\rfloor
   +\sum_{m\le K}\bigl(A(\sqrt{x/m})-A(D)\bigr). \tag{2}
\]

This is a weighted hyperbola identity; it uses no multiplicativity.
The first term differs from `x sum_{n<=D} a_n/n^2` by at most `D`.
Since `sum_{m<=K}m^{-1/4} <= (4/3)K^{3/4}`, the absolute value of the second
term in (2) is at most

\[
 \frac43 Cx^{1/4}K^{3/4}+CKD^{1/2}
 \le \frac73 CxD^{-3/2}. \tag{3}
\]

Partial summation, including its boundary term, gives

\[
 \sum_{n>D}\frac{a_n}{n^2}
 =-\frac{A(D)}{D^2}+2\int_D^\infty\frac{A(t)}{t^3}\,dt,
 \qquad
 \left|\sum_{n>D}\frac{a_n}{n^2}\right|
 \le\frac73 CD^{-3/2}. \tag{4}
\]

Consequently `|E_a(x)| <= D+(14/3)CxD^{-3/2}`. Take
`D=floor(x^{2/5})`, which lies between `x^{2/5}/2` and `x^{2/5}` and is at most
`sqrt(x)`. Since `2^{3/2}<3`, (1) follows. All estimates also cover `x=1`. ∎

More generally, the same argument with `|A(t)|<=Ct^alpha`, `0<=alpha<1`,
gives `O_C,alpha(x^{1/(3-alpha)})`. This generalization is not needed below.
The exponent in (1) is not merely an artifact of how we balanced two estimates:
there are explicit coefficient countermodels attaining it.

## 3. A balanced reciprocal-square cell

Fix an integer `H>=4` divisible by four and put `X=H^5`. For each

\[
 q=H/4,\ H/4+1,\ldots,H/2-1,
\]

let

\[
 I_q=\{n\in\mathbb N:\lfloor X/n^2\rfloor=q\}
     =\{l_q,\ldots,r_q\},
\]
\[
 l_q=\left\lfloor\sqrt{X/(q+1)}\right\rfloor+1,
 \qquad r_q=\left\lfloor\sqrt{X/q}\right\rfloor.
\]

All these cells lie in `(H^2,2H^2]`. Set `L_q=|I_q|` and
`m_q=floor(L_q/2)`. Define `a_n^(H)` to be `+1` on the first `m_q` integers
of each cell, `-1` on its last `m_q` integers, and zero elsewhere. An odd
cell has one unused middle integer. In particular every complete cell sums
to zero, and the cells are disjoint.

### Width bounds, including integer endpoints

Write `u=sqrt(X/(q+1))`, `v=sqrt(X/q)`. On `[u,v]`, which is contained in
`(H^2,2H^2]`, the magnitude of the derivative of `X/t^2` is between
`1/(4H)` and `2/H`. Integrating its unit decrease gives

\[
 H/2\le v-u<4H.
\]

Since `L_q=floor(v)-floor(u)`, and `H/2` and `4H` are integers,

\[
 H/2\le L_q\le4H,\qquad H/4\le m_q\le2H. \tag{5}
\]

For the lower bound, use `L_q>v-u-1>=H/2-1`; for the upper, use
`L_q<v-u+1<4H+1`. Thus no endpoint rounding is suppressed.

### Ordinary cancellation

Within a cell the partial sums increase from zero to `m_q`, then return to
zero. Completed cells make no contribution. Therefore, for every real `t>=1`,

\[
 0\le A_H(t)\le2\sqrt t. \tag{6}
\]

Before the support and after it the prefix is zero. On the support, use
`A_H(t)<=2H` and `t>H^2`.

### Correlation with the square-divisor phase

Pair the `i`th positive position `s_i` with the `i`th negative position `t_i`
in a cell. Their separation is `m_q` or `m_q+1`, so `t_i-s_i>=m_q`.
Both have quotient `q`, and `t_i<=2H^2`. Consequently

\[
 \{X/s_i^2\}-\{X/t_i^2\}
 =\frac{X}{s_i^2}-\frac{X}{t_i^2}
 =\int_{s_i}^{t_i}\frac{2X}{t^3}\,dt
 \ge\frac{t_i-s_i}{4H}\ge\frac{m_q}{4H}.
\]

Adding the pairs and using (5),

\[
 \sum_{n\in I_q}a_n^{(H)}\{X/n^2\}
 \ge\frac{m_q^2}{4H}\ge\frac H{64}. \tag{7}
\]

There are exactly `H/4` cells. Each cell has constant floor quotient and
coefficient sum zero, so `T_{a^(H)}(X)=0`. Thus

\[
 -E_{a^{(H)}}(X)
 =Xc_H
 =\sum_n a_n^{(H)}\{X/n^2\}
 \ge\frac{H^2}{256}=\frac{X^{2/5}}{256}. \tag{8}
\]

In particular `c_H>0`. The total number of nonzero coefficients is at most
`H^2`, since their support lies in `(H^2,2H^2]`.

**Theorem 2.** Equations (6) and (8) give a family of finitely supported
integer coefficient sequences, all with the **same** prefix constant `C=2`,
whose square-divisor errors have size at least `X^{2/5}/256`.
This rules out any smaller exponent with a bound uniform over this class.
It does not yet, by itself, address a bound whose constant depends arbitrarily
on the complete coefficient sequence. The next construction does.

## 4. One fixed infinite countermodel

**Theorem 3.** There is a single sequence `a_n in {-1,0,1}` with
`|A(t)|<=2sqrt(t)` for all `t>=1` and an explicit sequence `X_j -> infinity`
such that

\[
 E_a(X_j)\le-\frac{X_j^{2/5}}{512}. \tag{9}
\]

**Proof.** Set `H_1=1024`, `H_{j+1}=H_j^2`, `X_j=H_j^5` and put the block
`a^(H_j)` on its support, with zero coefficients elsewhere. The supports are
disjoint, all completed blocks sum to zero, and (6) holds inside the current
block. Therefore the fixed sequence still satisfies (6). Its `c_a` converges
absolutely, and equals the sum of the positive block masses `c_Hj`.

At `x=X_i`:

1. The current block contributes at most `-H_i^2/256` by (8).
2. Every earlier block has absolute error at most its number of nonzero
   coefficients: `|E_{a^(H_j)}(X_i)|<=H_j^2`, because each fractional part has
   magnitude less than one.
3. Every later block has support beyond `sqrt(X_i)`, hence its floor sum is
   zero and its error is `-X_i c_Hj<0`. These terms cannot cancel the current
   negative contribution.

The recurrence gives

\[
 \sum_{j<i}H_j^2\le2H_i.
\]

For clarity, the base case is empty; the induction step follows from
`2H_i+H_i^2<=2H_i^2=2H_{i+1}`, since `H_i>=2`. Thus

\[
 E_a(X_i)\le-\frac{H_i^2}{256}+2H_i
            \le-\frac{H_i^2}{512},
\]

where the last inequality uses `H_i>=1024`. Absolute convergence of the
main-term series and finiteness of the floor sum justify splitting the error
by blocks. This proves (9). ∎

The normalization `a_1=1` can also be imposed: add the coefficient at 1 to the
constructed sequence. Its contribution to `E_a(X_i)` is zero because `X_i` is
an integer, and the prefix bound becomes `|A(t)|<=3sqrt(t)`.
This still does **not** make the coefficients multiplicative or Möbius.

Theorems 1 and 3 show that `2/5` is the optimal exponent for this generic
coefficient class, even when the implicit bound constant may depend on the
fixed sequence. In particular, one cannot infer a quarter-power-type error
from an ordinary square-root prefix envelope alone.

## 5. The obstruction also survives a mean-square target

**Theorem 4.** The same fixed sequence in Theorem 3 has a subsequence `Y_j`
for which

\[
 \int_1^{Y_j}|E_a(x)|^2\,dx\ge 2^{-28}Y_j^{8/5}. \tag{10}
\]

Thus (H) alone cannot give the epsilon-relaxed `X^{3/2+epsilon}` mean-square
bound in `ANALYTIC_TARGET.md`. This is again an obstruction for **generic**
coefficients, not for the actual Möbius coefficients.

**Proof of interval persistence.** Fix a block scale `H`, put `X=H^5`, and
let `0<=u<=U=H^4/256` be real. Since every support index satisfies `n>H^2`,
its floor quotient can increase by at most one when `X` is replaced by `X+u`.
Inside `I_q`, a jump occurs precisely for an integer in

\[
 \left(\sqrt{X/(q+1)},\sqrt{(X+u)/(q+1)}\right].
\]

The number of such integers is at most its length plus one. Rationalizing
the square-root difference and using `q+1>=H/4` bounds it by

\[
 \frac{u}{2\sqrt{X(q+1)}}+1\le\frac{u}{H^3}+1.
\]

There are `H/4` cells. Because every coefficient is at most one, the signed
floor-sum increment is therefore at most

\[
 \frac{u}{4H^2}+\frac H4\le\frac{H^2}{1024}+\frac H4. \tag{11}
\]

The change in the main-term subtraction is `-u c_H<=0`. Hence the current
block retains its negative error, apart from the upper bound (11).

Now use the fixed sequence of Theorem 3 and take `H=H_j` with `j>=2`;
then `H>=4096`. Earlier blocks have total absolute error at most `2H`,
uniformly in real `x`. All later blocks still lie beyond `sqrt(X+U)`:
`X+U<=2H^5<H^8`, whereas the next support begins above `H^4`.
Their floor sums remain zero and their errors negative. Consequently, for
**every real** `x` in `[X,X+U]`,

\[
 E_a(x)\le-\frac{H^2}{256}+\frac{H^2}{1024}+\frac{9H}{4}
          \le-\frac{H^2}{512}. \tag{12}
\]

For the last step, `9H/4<=H^2/1024` when `H>=4096`.
Set `Y_j=X_j+H_j^4/256`. Squaring (12) and integrating over this interval,

\[
 \int_1^{Y_j}|E_a(x)|^2\,dx
 \ge\frac{H_j^4}{256}\left(\frac{H_j^2}{512}\right)^2
 =2^{-26}H_j^8\ge2^{-28}Y_j^{8/5},
\]

where `Y_j<=2H_j^5` and `2^{8/5}<4`. This proves (10). In particular, the
mean-square estimate fails for every `0<epsilon<1/10`, even with a bound
constant depending on this single fixed sequence. Adding `a_1=1` changes
`E_a(x)` by `-{x}<=0`, so the normalized variant also obeys this obstruction. ∎

This argument uses an interval of persistent phase correlation, not an
inference from large values at isolated points. `test_persistence.py` checks
the finite jump-count lemma and algebraic constants; it does not instantiate
the astronomical block subsequence or prove the integral theorem by sampling.

## 6. What this rules out, and what remains open

- **Ruled out:** a general transfer theorem using only bounded coefficients
  and the one-dimensional prefix bound (H), while promising an error exponent
  smaller than `2/5` for the square-divisor transform, or promising the
  `X^{3/2+epsilon}` mean-square target for every positive epsilon.
- **Not ruled out:** stronger estimates for the actual Möbius coefficients,
  methods using multiplicativity or Euler products, sharper phase correlations,
  arithmetic mean-square estimates, or RH itself. These countermodels are not Möbius.
- **Not new RH progress by itself:** the catalogue already cites a conditional
  Möbius result better than `2/5`; the generic obstruction cannot contradict
  a theorem using additional arithmetic input.
- **Research obligation exposed:** identify and exploit cancellation of
  Möbius coefficients against the reciprocal-square phase, or a genuinely
  suitable averaged substitute. Do not assume such cancellation merely because
  ordinary partial sums or positive-density fibers are controlled.
- **Verification distinction:** `verify.py` replays small instances using an
  independent direct-division oracle and exact rational correlations. It does
  not certify the derivative argument, the infinite block construction, RH,
  or an estimate for Möbius coefficients. Those are separate proof obligations.

No computational enlargement of `H` is needed to prove any statement above.
The replay ceiling is a resource limit of the tool, not a mathematical cutoff.

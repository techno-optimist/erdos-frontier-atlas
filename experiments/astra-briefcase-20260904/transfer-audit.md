# Audit: non-path tree branch-skeleton transfer

## Verdict

**The theorem and proposed construction are correct** for finite simple non-path trees, with “exact branch skeleton” understood as specified: the branch vertices are precisely V(H), and their induced graph is H. No substantive correction is needed. The determinant normalization should be written explicitly, and the polynomial-tail estimate below makes the limiting argument fully rigorous.

This proves existence of a non-log-concave independence polynomial for every such H. It makes no claim about unimodality, path-core decorations, novelty, or publication status.

## 1. Weighted claw and constants

A finite non-path tree has a vertex c of degree at least three. Three distinct neighbors form an independent set L, since an edge between them would create a triangle. Thus H[{c} ∪ L] is an induced claw. In particular h ≥ 4 and α(H) ≥ 3. The chosen neighbors need not be leaves of H.

Let b_c = 0, b_v = 3 for v in L, and b_v = B otherwise, where

    B = ceil(log2(256 binom(h,2))).

Write g_s for the claw-only weighted coefficients, reserving f_s for all of H. Direct exact arithmetic gives

    (g_1, g_2, g_3) = (11/8, 3/64, 1/512),
    g_2² − g_1 g_3 = −1/2048.

All weights are in (0,1]. Every independent pair containing a vertex outside the claw therefore has weight at most ε = 2^(−B), including pairs with two outside vertices. There are at most binom(h,2) such pairs. Consequently

    f_2 ≤ 3/64 + 1/256 = 13/256,
    f_1 ≥ 11/8,
    f_3 ≥ 1/512,
    f_2² − f_1 f_3 ≤ (13/256)² − (11/8)(1/512)
                      = −7/65536 < 0.

All constants check. When h = 4 there are no outside vertices, so the stronger claw-only defect applies; the unused B is harmless. An exact implementation can compute B as `(256*comb(h,2)-1).bit_length()`, avoiding floating-point ceiling errors.

## 2. Decoration identity and degree

Attach t_v = N + b_v new, mutually vertex-disjoint two-edge pendant paths at v, using new vertices for every path, and set M = Σ_v t_v. Conditional on the chosen core independent set S:

- At a selected core vertex, each adjacent middle vertex is excluded and its terminal leaf is optional: factor (1+x).
- At an unselected core vertex, the remaining two vertices form an edge: factor (1+2x).

Therefore the exact identity is

    I_T(x) = Σ_{S independent in H} x^|S|
             (1+x)^t(S) (1+2x)^(M−t(S)),
    t(S) = Σ_{v∈S} t_v.

Every summand has degree M+|S|, with positive leading coefficient. In particular

    α(T) = M + α(H).

Thus the indices M+1, M+2, M+3 exist, have positive coefficients, and M+2 is an interior index of the coefficient sequence, including when α(H)=3.

## 3. Fully explicit tail estimate

Write a_k = [x^k]I_T(x), and for s in {1,2,3} define

    A_s(N) = a_(M+s) / 2^(M−Ns).

Fix an independent set S with r = |S| and b(S) = Σ_{v∈S} b_v. Its summand has degree M+r.

- If r < s, its contribution to a_(M+s) is zero.
- If r = s, its normalized contribution is exactly 2^(−b(S)). Summing these contributions gives f_s.
- If r = s+q with q ≥ 1, put T_S = Nr+b(S) and U_S = M−T_S. Its normalized contribution is exactly

    2^(−Nq−b(S)) Q_(S,q)(N),

    Q_(S,q)(N) = Σ_{j=0}^q binom(T_S,j)
                                binom(U_S,q−j) 2^(−(q−j)).

The binomial coefficients are zero when their lower arguments exceed the nonnegative integer upper arguments. Since T_S and U_S are affine in N, Q_(S,q) is a polynomial in N of degree at most q. Its values at admissible integers N are nonnegative. No assertion that its monomial coefficients are nonnegative is required.

For fixed H and fixed offsets, each such term tends to zero exponentially fast times a fixed polynomial. There are only finitely many independent sets, so

    A_s(N) → f_s   for s=1,2,3.

This is a finite-sum limit, not an interchange with an infinite family. The index M+s moves with N, but the displayed exact formulas already account for that. Each A_s is at least f_s; that one-sided fact alone is not enough to infer the determinant sign, but simultaneous convergence is.

## 4. Correct determinant normalization and termination

The precise normalized determinant is

    D_N / 2^(2M−4N) = A_2(N)² − A_1(N)A_3(N),

    D_N = a_(M+2)² − a_(M+1)a_(M+3).

The exponent agrees because (M−N)+(M−3N)=2(M−2N). The denominator is positive, so normalization preserves the sign. By the previous limit,

    D_N / 2^(2M−4N) → f_2²−f_1f_3 ≤ −7/65536.

Hence D_N is negative for every sufficiently large integer N. Doubling N from 1 therefore terminates if the integer coefficients and determinant are computed exactly. This is an existence/termination conclusion, not a claim of efficient runtime or monotonicity of D_N, and the threshold can depend on H. The construction need not fail log-concavity at every N≥1.

## 5. Tree and branch-skeleton conditions

Attaching pendant paths to a tree preserves connectedness and acyclicity. The degree of an old vertex v is deg_H(v)+t_v, not deg_H(v)+2t_v.

- The center already has degree at least three in H.
- A chosen neighbor has deg_H(v)≥1 and t_v=N+3≥4.
- Every other vertex has deg_H(v)≥1 and t_v=N+B≥B+1.

Thus every old vertex is a branch vertex. Every new middle vertex has degree two and every new terminal vertex has degree one. No edge between old vertices is changed or added, so the induced graph on branch vertices is exactly H. If “skeleton” is instead defined to retain leaves after suppressing degree-two vertices, the terminology should be qualified; the explicit structural assertion in this theorem is unambiguous and proved.

## 6. Independent exact computational checks

A separate full decorated-tree dynamic program was implemented during this audit. It uses the standard root-excluded/root-included recurrence, multiplying child polynomials, rather than the core-subset generating-function identity. Its coefficients were compared with the explicit core-subset tail formula using integer/Fraction arithmetic.

All **11 tested decorated trees** passed coefficient agreement at all three target indices, the determinant normalization identity, the branch-degree conditions, and the maximum-degree identity α(T)=M+α(H):

| Core H | Tested N | Determinant signs in that order |
|---|---|---|
| K_(1,3), center 0, neighbors 1,2,3 | 1,2,4,8,16 | +,−,−,−,− |
| Edges 01,02,03,34 | 1,4,16 | +,−,− |
| K_(1,4), with chosen neighbors 1,2,3 | 1,4,16 | +,−,− |

For the minimal claw at N=2, the construction has t=(2,5,5,5), M=17 and 38 vertices. The independently checked coefficients are

    a_18 = 50721,   a_19 = 448,   a_20 = 4,
    a_19² − a_18 a_20 = −2180,
    normalized defect = −545/16777216.

At N=1 the same core has normalized defect +1073/4194304, confirming the need for the “sufficiently large N” qualification.

These computations independently check the algebra and small examples; the all-H assertion rests on the proof above, not on a finite search.

## Scope and outstanding issues

No mathematical gap was found. Recommended presentation edits are explicit determinant normalization, the Q_(S,q) formula, distinct notation for claw-only coefficients, and the definition of branch skeleton. No repository was inspected or modified, and nothing was published. No execution failures occurred. This was a self-contained proof audit, not a literature or novelty assessment.

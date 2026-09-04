# P993: transplanting a log-concavity obstruction

**Informal theorem and constructive algorithm; no novelty claim and no claim to solve tree unimodality.** Graph attachment: `P993`, surface `S:triage:993`. This note explains why non-path branch skeletons can all support failures of the *stronger* log-concavity property. It does not prove that path skeletons are safe.

## Theorem

Let $H$ be any finite tree that is not a path. There is a tree $T$ whose vertices of degree at least three induce exactly $H$, such that the independence polynomial of $T$ is not log-concave. Moreover, a fixed explicit decoration scheme works for every sufficiently large integer parameter $N$.

Here the construction adds only disjoint pendant paths of length two to vertices of $H$. Thus the original core is exactly the branch skeleton, without contracting or concealing extra branching vertices.

## 1. A small weighted obstruction

Let $h=|V(H)|$. Since $H$ is a non-path tree, it has a vertex $c$ with three neighbors $u,v,w$. Those four vertices induce a claw.

Give $c$ weight $1$ and each of $u,v,w$ weight $1/8$. Their weighted independence polynomial is

$$1+\frac{11}{8}x+\frac3{64}x^2+\frac1{512}x^3.$$

The log-concavity determinant at index two is

$$\left(\frac3{64}\right)^2-\frac{11}{8}\frac1{512}=-\frac1{2048}.$$

Set

$$B=\left\lceil\log_2\!\left(256\binom h2\right)\right\rceil$$

and assign weight $2^{-B}$ to every other vertex. Write $f_s$ for the sum of products of vertex weights over independent $s$-sets of the entire $H$.

The original claw still supplies $f_1\ge11/8$ and $f_3\ge1/512$. Every independent pair containing an outside vertex has weight at most $2^{-B}$; there are at most $\binom h2$ such pairs. Consequently

$$f_2\le\frac3{64}+\frac1{256},$$

and therefore

$$\boxed{f_2^2-f_1f_3\le-\frac7{65536}<0.}$$

This bound is deliberately loose. It makes the choice of outside weights explicit and avoids an unsupported appeal to a numerical limit.

## 2. Realize the weights using ordinary unweighted trees

Write each weight as $2^{-b_v}$: $b_c=0$, $b_u=b_v=b_w=3$, and $b_z=B$ elsewhere. For an integer $N\ge1$, attach

$$t_v=N+b_v$$

disjoint pendant two-edge paths to each core vertex $v$. Call the resulting ordinary unweighted tree $T_N$, and put $M=\sum_v t_v$.

Condition on the independent set $S$ selected in the core. If a core vertex is selected, the middle vertex of each attached path is forbidden and its leaf is free, giving $1+x$. If it is unselected, the remaining edge gives $1+2x$. Hence, exactly,

$$I(T_N;x)=\sum_{S\text{ independent in }H}x^{|S|}(1+x)^{t(S)}(1+2x)^{M-t(S)},$$

where $t(S)=\sum_{v\in S}t_v$.

The degree is $M+\alpha(H)$. In particular the three coefficients used below exist, since the three claw leaves form an independent set.

## 3. The weighted obstruction survives at the tail

Let $a_k(N)=[x^k]I(T_N;x)$. For each fixed $s\in\{1,2,3\}$,

$$\lim_{N\to\infty}\frac{a_{M+s}(N)}{2^{M-Ns}}=f_s.$$

To see this, separate the terms in the exact identity by the size of $S$:

- If $|S|<s$, the term has degree less than $M+s$ and contributes zero.
- If $|S|=s$, its normalized leading coefficient is exactly $2^{-b(S)}$, its vertex-weight product.
- If $|S|=s+q$ with $q>0$, the relevant coefficient is $q$ positions below that term's leading coefficient. After normalization it is $2^{-Nq-b(S)}$ times a polynomial in $N$ of degree at most $q$. It tends to zero. There are only finitely many core independent sets.

Explicitly, the polynomial factor in the last bullet is

$$Q_{S,q}(N)=\sum_{j=0}^q\binom{N|S|+b(S)}j\binom{M-N|S|-b(S)}{q-j}2^{-(q-j)}.$$

It has degree at most $q$ and nonnegative values at admissible integers $N$; nonnegative monomial coefficients are not needed. This makes the finite-sum limiting argument explicit.

The same normalization applies to both products in the log-concavity determinant:

$$
\frac{a_{M+2}(N)^2-a_{M+1}(N)a_{M+3}(N)}{2^{2M-4N}}
\longrightarrow f_2^2-f_1f_3<0.
$$

The denominator is positive. Thus the unweighted tree polynomial fails log-concavity at index $M+2$ for every sufficiently large $N$.

Finally, the core vertices are precisely the branching vertices. The center already has core degree at least three; the selected neighbors each receive at least four arms; every other vertex receives at least $B+1$ arms. Added middle vertices have degree two, and added leaves degree one. Their induced branching-vertex graph is exactly $H$. ∎

## Algorithm and exact checks

The proof gives a terminating mathematical search: try $N=1,2,4,8,\ldots$ and check the exact determinant. The implementation's explicit `max_rounds` is a resource cap, **not a theorem-derived upper bound**; exhaustion raises an error instead of reporting nonexistence.

`tail.py` computes the top coefficients without constructing the decorated tree. Its arithmetic-operation count depends on core size and requested tail depth, but **integer bit complexity still grows with the number of arms**. `test_tail.py` checks the identity against direct subset enumeration, then checks compiled witnesses against the independently implemented full tree-DP from the first research bundle.

The saved sweep compiles every non-path unlabelled tree core on at most eight vertices (40 cores). All 40 exact log-concavity failures were verified against the full polynomial. These particular witness polynomials are nevertheless all unimodal: **none is a counterexample to Erdős #993**. Output trees have between 38 and 194 vertices. This is exhaustive in the stated *core list*, not in decorated trees or arbitrary trees of those orders.

## What this contributes to the graph

- A reusable obstruction-transfer construction replaces isolated examples: any non-path branch skeleton can be supplied with an exact stress-test tree.
- If a proposed theorem claims universal log-concavity for all pendant-P2 decorations of some tree core, that core must be a path. The converse is **not** proved here.
- The sampled path-core evidence remains conjectural; this argument neither proves it nor proves the full unimodality conjecture.
- This is an informal derivation with bounded implementation checks, not a formal proof certificate. Literature priority has not been established.

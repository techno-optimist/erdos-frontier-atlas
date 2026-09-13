# Finite-prime CRT variance: mathematical audit

## Outcomes

- The proposed formula is correct for every finite prime set and every integer H ≥ 0, including the empty set, H = 0, and H beyond the CRT period.
- Its positive coefficients imply the uniform bound V_P(H) ≤ √H. In fact the real extension W_P(t) satisfies W_P(t) ≤ √t for every t ≥ 0.
- Prime addition is the positive, commuting operator T_p U(t) = (1 − 2/p²)U(t) + U(t/p²). A naive induction substituting U(t) ≤ √t into this recurrence does **not** prove the bound when p > 2.
- Normalized counts, not deterministic variances, form a martingale in the product-CRT probability space. Consequently W_P(t)/ρ_P² is nondecreasing under prime-set inclusion. W_P(t)/ρ_P is also nondecreasing, by a separate elementary inequality. Raw variance is not monotone.
- These are full-period/Haar averages. They do not provide the uniform finite-X estimates required in the RH criterion. Exact endpoint, truncation, and centering discrepancies are given below.

All mathematical proofs below are an informal model audit, supported by bounded exact-arithmetic checks; they are not formalization or human peer review. No novelty claim is made.

## 1. Exact correlation and a positive covariance operator

Write

    a_P(d) = ∏_{p∈P, p∤d}(1 − 2/p²),     d | M.

For h ∈ Z, CRT gives the exact correlation

    C_P(h) = E_{n mod L}[f_P(n)f_P(n+h)]
           = ∏_{p∈P}(1 − 2/p² + 1_{p²|h}/p²)
           = Σ_{d|M} a_P(d) 1_{d²|h}/d².

Indeed, modulo p² the two forbidden residues coincide precisely when p² divides h. Also

    E f_P = ρ_P,
    Σ_{d|M} a_P(d)/d⁴
       = ∏_{p∈P}(1 − 2/p² + 1/p⁴) = ρ_P².

Consequently the centered covariance kernel has the positive decomposition

    C_P(h) − ρ_P²
       = Σ_{d|M} a_P(d)[1_{d²|h}/d² − 1/d⁴].

The bracket is the covariance kernel of the periodic indicator 1_{d²|n}, with n uniform modulo d². Thus this is genuinely a positive-semidefinite covariance-operator decomposition: for any finitely supported complex weights c_j,

    E |Σ_j c_j(f_P(n+j) − ρ_P)|²
      = Σ_{d|M} a_P(d)
          E_{u mod d²}|Σ_j c_j(1_{d²|u+j} − 1/d²)|².

All a_P(d) are positive and at most 1. This statement is stronger than positivity for just interval weights; it does not assert that the original divisor indicators are independent.

## 2. Derivation of the candidate formula

Put q = d² and write H = qk + r, with 0 ≤ r < q. Among j = 1,...,H, exactly r residue classes modulo q occur k+1 times, and q−r occur k times. Therefore

    #{(i,j): 1≤i,j≤H, q|(i−j)}
      = r(k+1)² + (q−r)k²
      = H²/q + q ψ(H/q),

where ψ(u) = {u}(1−{u}). Expanding the square in the definition of V_P,

    V_P(H)
      = Σ_{i,j≤H} C_P(j−i) − ρ_P²H²
      = Σ_{d|M} a_P(d)[H²/d⁴ + ψ(H/d²)] − ρ_P²H²
      = Σ_{d|M} a_P(d) ψ(H/d²).

The H² terms cancel exactly. There is no missing diagonal or additional density factor. The d=1 term is zero for integer H, but must be retained for the real extension below.

For P empty, M=L=1, f_P≡1, and V_P(H)=0, as required. For general P, V_P(H+L)=V_P(H), and V_P(kL)=0; no restriction H≤L is needed.

## 3. A uniform square-root bound

Define W_P(t) for real t≥0 by the same divisor sum. Since

    0 ≤ ψ(u) ≤ min(1/4,u)    (u≥0),

we have

    W_P(t) ≤ Σ_{d≥1} min(1/4,t/d²).

For t>0, g_t(x)=min(1/4,t/x²) is decreasing on (0,∞). Thus

    Σ_{d≥1} g_t(d) ≤ ∫_0^∞ g_t(x) dx
      = ∫_0^{2√t} (1/4) dx + ∫_{2√t}^∞ t/x² dx
      = √t.

The case t=0 is immediate. This proves the claimed constant 1 uniformly in P, without estimating a growing Euler product or assuming RH.

## 4. The real extension, endpoint counts, and prime addition

### 4.1 What W_P(t) actually averages

Let

    N_P(x,t) = Σ_{m∈Z, x<m≤x+t} f_P(m).

Then the real extension has the exact continuous-phase interpretation

    W_P(t) = (1/L)∫_0^L (N_P(x,t) − ρ_P t)² dx.

To prove it, write t=h+θ, h=floor(t), 0≤θ<1, and x=n+u, 0≤u<1. The count is S_P(n,h) for u<1−θ and S_P(n,h+1) otherwise. Averaging over complete integer periods gives

    W_P(h+θ)
      = (1−θ)V_P(h) + θV_P(h+1) + ρ_P² θ(1−θ).       (R)

The divisor-sum extension has the same values: each summand has second derivative −2/d⁴ between successive integers, so W_P''=−2ρ_P² there, with the correct integer endpoint values.

This is not linear interpolation. Nor is it the integer-phase average of S_P(n,floor(t)) centered at ρ_Pt; that different quantity equals

    V_P(h) + ρ_P²θ².

For P empty, W_empty(t)=ψ(t), not zero. Dropping the d=1 summand because it vanishes at integers would destroy the prime-addition recurrence at nonintegral arguments.

### 4.2 Exact recurrence

For p∉P, splitting divisors of Mp according to whether p divides them gives

    W_{P∪{p}}(t) = (1−2/p²)W_P(t) + W_P(t/p²).        (T)

The operators T_p=(1−2/p²)I+D_{p^-2}, where D_cU(t)=U(ct), are positive and commute. Thus W_P=(∏_{p∈P}T_p)ψ.

For an integer-only version, put q=p², H=qk+r, θ=r/q. Substituting (R) into (T) yields

    V_{P∪{p}}(H)
      = (1−2/q)V_P(H)
        +(1−θ)V_P(k)+θV_P(k+1)+ρ_P²θ(1−θ).

Replacing W_P(H/p²) by V_P(floor(H/p²)), or by an uncorrected linear interpolation, is generally wrong.

Finally, a proposed induction using only W_P(u)≤√u produces

    W_{P∪{p}}(t) ≤ (1−2/p²+1/p)√t.

That factor exceeds 1 for p>2 (it is 10/9 for p=3). The recurrence is correct, but this particular proof of a uniform constant would fail. The positive divisor-sum majorant in Section 3 is what proves it.

## 5. Martingale and monotonicity audit

### 5.1 The correct probability space and normalization

On Ω=∏_p Z/p²Z, choose independent uniform R_p. For finite P define

    F_P(j) = ∏_{p∈P}(1−1_{R_p+j≡0 (mod p²)}),
    Z_P(H) = ρ_P^-1 Σ_{j=1}^H F_P(j) − H.

Let F_P denote the sigma-algebra generated by the prime coordinates in P. For P⊂Q, coordinate independence gives

    E[Z_Q(H) | F_P] = Z_P(H).

Thus along any nested enumeration of primes the normalized count is a martingale. Its squared value is a submartingale, and orthogonality of increments gives

    V_Q(H)/ρ_Q² − V_P(H)/ρ_P²
       = E[(Z_Q(H)−Z_P(H))²] ≥ 0.                    (M)

It is inaccurate to call the deterministic sequence of variances itself a martingale.

For real t, add one common independent U uniform in [0,1) to the initial sigma-algebra, let K=floor(U+t), and use

    Z_P(t)=ρ_P^-1 Σ_{j=1}^K F_P(j)−t.

The same conditional expectation proof applies, and E[Z_P(t)²]=W_P(t)/ρ_P². The initial martingale value is K−t, not zero when t is nonintegral.

For fixed t these martingales are bounded in L², since ρ_P≥ρ=∏_p(1−p^-2)>0 and W_P(t)≤√t. They converge in L² along an exhaustive prime sequence. This is convergence in the product probability space, not a quantitative statement about a finite orbit segment of actual integers.

### 5.2 Stronger density normalization, but not raw monotonicity

The elementary periodic function ψ is subadditive: ψ(x+y)≤ψ(x)+ψ(y). If a={x}, b={y}, the difference is 2ab when a+b≤1, and 2(1−a)(1−b) otherwise. Hence for every positive integer q,

    ψ(qx)≤qψ(x),   so W_P(t/q)≥W_P(t)/q.

With q=p² and b=1−1/q, recurrence (T) implies W_{P∪{p}}(t)≥bW_P(t). Consequently W_P(t)/ρ_P is also nondecreasing under inclusion. This is a separate algebraic observation, not the martingale normalization.

For the martingale normalization, (T) gives the explicit increment

    W_{P∪{p}}(t)/ρ_{P∪{p}}² − W_P(t)/ρ_P²
      = [W_P(t/p²)−W_P(t)/p⁴]/[ρ_P²(1−p^-2)²] ≥ 0.

Raw variance is not monotone. An exact counterexample is

    P={3}, Q={2,3}, H=4:
    V_P(4)=20/81 > 2/9=V_Q(4).

The density-squared normalized values are 5/16 and 1/2, respectively, in agreement with (M).

### 5.3 Finite integer averages do not inherit this martingale

Take n uniform on {1,2}, H=3, P={3}, Q={2,3}. Both P-counts are 3, while both Q-counts are 2. Therefore

    E[(S_P/ρ_P−H)²]=9/64,
    E[(S_Q/ρ_Q−H)²]=0.

So the analogous finite-X nominally centered normalized quantity can decrease. Residues of a finite, incomplete integer block are not independent uniform prime coordinates. This example concerns centering at the stated density, not recentering each sample at its empirical mean.

## 6. The exact gap to actual squarefrees at finite X

Fix integers A≥0, X≥1, H≥0, so all counted positive integers lie at most

    R=A+X−1+H.

Write S_P(n,H)=Σ_{j≤H}f_P(n+j), S(n,H)=Σ_{j≤H}μ²(n+j), ρ=1/ζ(2), and

    B_{P;A,X}(H)=X^-1 Σ_{n=A}^{A+X−1}(S_P(n,H)−ρ_PH)²,
    A_{A,X}(H)=X^-1 Σ_{n=A}^{A+X−1}(S(n,H)−ρH)².

These are the nominally centered second moments. At finite X the nominal center need not be the empirical mean; its bias contributes to the second moment.

### 6.1 Period averaging is a separate error

Let r=X mod L. Splitting the sample into complete L-blocks and a remainder, and using 0≤(S_P−ρ_PH)²≤H², gives

    |B_{P;A,X}(H)−V_P(H)| ≤ H²r/X.                  (E1)

This is exact period bookkeeping, independent of A. It is not generally small if L is large relative to X.

A more structural but still crude CRT bound is also available. Put k=|P| and

    C_{A,X}(q,r)=floor((A+X−1−r)/q)−floor((A−1−r)/q).

This is the exact number of n∈[A,A+X) with n≡r mod q. Its discrepancy from X/q has absolute value at most 1.

Expand f_P(n)=Σ_{d|M}μ(d)1_{d²|n}. For a pair of shifts i,j, the congruences

    n≡−i mod d²,   n≡−j mod e²

are compatible exactly when gcd(d,e)² divides i−j. When compatible they specify one residue modulo lcm(d,e)². Replace each exact count C_{A,X} by X/q plus its signed endpoint error ε. Then

    B_{P;A,X}(H)−V_P(H)
      = X^-1[Σ_{i,j≤H}Σ_{d,e|M, compatible} μ(d)μ(e) ε_{d,e;i,j}
              −2ρ_PH Σ_{j≤H}Σ_{d|M}μ(d) ε_{d;j}].  (E2)

In particular,

    |B_{P;A,X}(H)−V_P(H)|
      ≤ H²(4^k+2ρ_P 2^k)/X.                         (E3)

One may use the minimum of (E1) and (E3). The positive CRT variance formula results from the X/q main terms. It does not make the signed endpoint expression (E2) nonpositive, or otherwise dispose of it.

### 6.2 Omitted primes and centering

Put

    τ_P=Σ_{p∉P}p^-2,
    J_P(R)=#{p∉P : p²≤R},
    δ_P=ρ_P−ρ,       0≤δ_P≤τ_P,
    T_P(n,H)=S_P(n,H)−S(n,H)≥0.

The union bound and exact endpoint count imply

    E_{A,X} T_P ≤ H[τ_P+J_P(R)/X].

The actual centered error is

    S−ρH = (S_P−ρ_PH) − T_P + δ_PH.                 (C)

In particular, the density correction has a plus sign in (C). As both centered errors have absolute value at most H,

    |A_{A,X}(H)−B_{P;A,X}(H)|
      ≤ 2H²[τ_P+J_P(R)/X+δ_P]
      ≤ 4H²τ_P + 2H²J_P(R)/X.                      (E4)

A useful alternative retaining an L² form is

    ||(S−ρH)−(S_P−ρ_PH)||_2
      ≤ H sqrt(τ_P+J_P(R)/X+δ_P²),

because T_P²≤HT_P and the cross term in E(T_P−δ_PH)² is nonpositive.

If P contains every prime up to √R, the two counting functions coincide on the sample, but ρ_P is still not ρ. Then T_P=0 exactly, while the δ_PH correction remains. Taking still more primes reduces this centering difference but does not justify replacing finite averaging by full-period averaging.

### 6.3 The legitimate limiting statement

For an exhaustive increasing family of prime sets, extend a_P(d) by zero when d∤M. For each fixed t,

    W_P(t) → W_∞(t)
      = Σ_{d squarefree} [∏_{p∤d}(1−2/p²)] ψ(t/d²) ≤ √t.

This follows from dominated convergence, with summable majorant t/d². Convergence is also uniform on each fixed bounded t-interval, using T/d² as majorant there.

For fixed integer H and A=X, first fix P and send X→∞ in (E1) and (E4): J_P(2X−1+H)/X≤√(2X−1+H)/X→0. Then exhaust P, so τ_P→0 and V_P(H)→W_∞(H). This proves, without exchanging unproved simultaneous limits,

    lim_{X→∞} A_{X,X}(H)=W_∞(H)≤√H,    H fixed.

Neither this iterated limit nor the uniform-in-P bound controls A_{X,X}(H) uniformly for growing H. A simultaneous choice P=P(X,H) requires quantitative control of **both** the endpoint discrepancy and the omitted-prime/centering terms. For P consisting of primes at most y, the crude elementary τ_P≤1/floor(y) already displays the conflict between making H²τ_P small and retaining an economical finite-CRT estimate. Better arithmetic estimates could improve these bounds; nothing here proves they cannot. They simply have not been supplied by the positive operator.

### 6.4 Continuous x versus integer n: exactly when they agree

For integer X,H,

    (1/X)∫_X^{2X}(Σ_{x<m≤x+H}μ²(m)−ρH)² dx
       = A_{X,X}(H),

because the count is constant on each unit cell [n,n+1), apart from measure-zero endpoints. Thus there is no extra discrete/continuous issue for these integer parameters.

For t=h+θ nonintegral, the finite continuous-phase integral for f_P over [A,A+X] equals

    (1−θ)B_{P;A,X}(h)+θB_{P;A,X}(h+1)+ρ_P²ψ(θ)
       +2ρ_Pψ(θ)[E_{A,X}f_P(n+h+1)−ρ_P].            (E5)

The last endpoint-mean correction vanishes for a complete-period average, but need not vanish for finite X. Formula (E5) explains why the real W_P interpolation cannot silently be substituted for a finite arithmetic average.

GMRR, Theorem 3, requires for every ε∈(0,1/100) and every δ>0 the bound

    (1/X)∫_X^{2X}|Σ_{x<m≤x+H}μ²(m)−6H/π²|² dx
       ≪_{ε,δ} H^(1/2+δ)

uniformly throughout 1≤H≤X^(1−ε); it proves this is equivalent to RH.[1] The fixed-H limit above is not that statement. This audit does not prove RH or a new finite-X range.

## 7. Antecedents and source scope

- **Mirsky (1949), Arithmetical pattern problems relating to divisibility by rth powers, Proc. London Math. Soc. (2) 50, 497–508.** The original volume's OCR was retrieved and its introduction and CRT lemmas inspected. It treats prescribed patterns of r-free and non-r-free integers; the OCR of displayed equations is incomplete, so no delicate exponent is being inferred from it.[15]
- **Hall (1982), Squarefree numbers on short intervals, Mathematika 29(1), 7–17.** The primary Cambridge landing page verifies this bibliography.[8] Hall's variance result is also explicitly discussed in the primary Grimmett–Hall paper. Its random-sieve model uses independent uniform forbidden residues, exactly the probabilistic setting relevant here.[5] Hall's full-text link redirected to HTML, so this audit does not claim to have read Hall's original proof.
- **Grimmett and Hall (1991), The asymptotics of random sieves, Mathematika 38, 285–302.** Pages 285–288 were read from rendered primary pages. They define stationary random sieves for pairwise coprime moduli and distinguish the limiting frequency of deterministic sieve patterns from the random model; this is a classical antecedent for the CRT/Haar interpretation.[5]
- **Cellarosi and Sinai, Ergodic properties of square-free numbers, arXiv:1112.4691v2 / JEMS.** Section 3, especially Lemma 3.1 and Proposition 3.2, gives σ_d=d^-2∏_{p∤d}(1−2/p²) and C_2(h)=Σ_{d²|h}σ_d. Section 1 describes the product of Z/p²Z with Haar measure. These directly antecede the positive correlation decomposition and its probability space.[12]
- **Gorodetsky, Mangerel and Rodgers, Squarefrees are Gaussian in short intervals, arXiv:2112.12234v1, Lemma 3.4, equation (3.5).** Their B-free variance formula is

      C_2(H)=2H² Σ_{D∈[B]} D^-2 ∏_{b∈B,b∤D}(1−2/b)
                         Σ_{λ≥1}|sinc(Hλ/D)|².

  Taking B={p²} and using the classical identity

      ψ(u)=2 Σ_{λ≥1} sin²(πλu)/(πλ)²

  converts their formula to the same infinite positive ψ-series derived above. This is an explicit formula-level antecedent, not merely a thematic similarity.[4] Their discussion also credits ideas of Hausman–Shapiro (1973) and Montgomery–Vaughan for variance estimates.[4]

The exact prime-addition/martingale wording above was not located in the retrieved sources. That is not evidence of novelty; the argument is elementary in the classical product-sieve model.

## 8. Transfer to r-free sieves

Let r≥2 be an integer, f_{P,r}(n)=∏_{p∈P}(1−1_{p^r|n}), ρ_{P,r}=∏_{p∈P}(1−p^-r), and average over n modulo M^r. The proposed extension is correct:

    V_{P,r}(H)
      = Σ_{d|M}[∏_{p∈P,p∤d}(1−2/p^r)] ψ(H/d^r).

The proof above works verbatim with q=d^r. In particular, the correlation expansion uses 1_{d^r|h}/d^r, and the centering identity is

    Σ_{d|M} a_{P,r}(d)/d^(2r)=ρ_{P,r}².

The same real extension W_{P,r}(t) obeys

    W_{P∪{p},r}(t)=(1−2/p^r)W_{P,r}(t)+W_{P,r}(t/p^r).

Its complete-period continuous-phase interpretation, corrected quadratic interpolation, density-normalized monotonicity, and density-squared-normalized count martingale all remain valid. Here the scaling integer is p^r. Raw monotonicity still fails, for example at r=3, P={3}, Q={2,3}, H=8: the variances are 152/729 and 140/729.

For t>0 set a=(4t)^(1/r). Positivity and the decreasing integral comparison give

    W_{P,r}(t) ≤ Σ_{d≥1} min(1/4,t/d^r)
      ≤ a/4 + [t/(r−1)] a^(1−r)
      = [r/(r−1)] 4^(1/r−1) t^(1/r).

Thus the parent's proposed constant is exactly correct; at r=2 it is 1. The integral requires r>1, and integer r makes these prime-power moduli an arithmetic sieve. The general B-free formula of Lemma 3.4 already covers B={p^r}, so this extension has the same direct formula-level antecedent.[4] The finite-X issues are unchanged in kind: replace the tail by Σ_{p∉P}p^-r and J_P(R) by #{p∉P:p^r≤R}. No RH-equivalence assertion for general r is inferred from GMRR's squarefree theorem.

## 9. Executed verification and artifacts

`audit.py` used only exact integers/Fractions, independently comparing the divisor formula against direct averaging of f_P over complete periods. It passed 198 such cases, including empty P, H=0, and multiple-period endpoints. It also passed 8,414 rational-t cases checking the recurrence, both normalizations, the square-root bound by squaring rational values, and the real interpolation identity. Its search recorded explicit raw-variance decreases, including the counterexample above.

`endpoints.py` independently constructed generalized-CRT residues and exact floor counts. It passed 144 finite-X discrepancy identities and bounds, 288 real-phase endpoint identities, and 260 conditional-martingale fiber checks. The finite-X monotonicity counterexample returned exactly 9/64 and 0.

`r-free.py` passed 155 direct period-average comparisons and 3,872 rational-t recurrence/interpolation/normalization/bound checks for r=2,3,4,5. It compares V^r against the exact rational quantity [r/(r−1)]^r 4^(1−r)H, avoiding floating-point evaluation of the proposed constant. A further 8 nontrivially weighted covariance identities passed.

Results are in `audit-results.json`, `endpoint-results.json`, `r-free-results.json`, and the aggregated `verification-summary.json`. The sampled domains are explicit in the scripts. These bounded checks supplement, not replace, the all-parameter proofs.

The parent's independently retrieved TeX-preserving HTML was also inspected. Its Lemma 3.4 gives the identical sinc-series formula, but labels it equation (3.6), whereas the downloaded arXiv:2112.12234v1 PDF labels it (3.5). Cite the lemma and the representation actually read rather than silently assuming equation numbers match across the two renderings.

All authored files and reading copies are confined to this isolated scratch directory; no repository edits, staging, commits, or repository gates were performed. PDF extraction initially lacked pdfplumber; native read_file extraction, pypdf, and an isolated uv pymupdf invocation supplied usable text and rendered scans. Some search/extraction calls were blocked or returned truncated mathematical text. Original PDF reading or rendered pages were used where needed; the blocked Hall download was retained with an .html extension, not passed off as a PDF.

## Sources

[1] https://arxiv.org/pdf/2006.04060v2
[4] https://arxiv.org/pdf/2112.12234v1
[5] https://statslab.cam.ac.uk/~grg1000/papers/math38-285.pdf
[8] https://www.cambridge.org/core/journals/mathematika/article/squarefree-numbers-on-short-intervals/18BC455C6CF7BEE478E4642532123CB8
[12] https://arxiv.org/pdf/1112.4691v2
[15] https://archive.org/download/proceedingsofthe032881mbp/proceedingsofthe032881mbp_djvu.txt

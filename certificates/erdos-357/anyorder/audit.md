# Audit: Erdős #357 any-order (OEIS A364153), claim a(k) > (3/2 + 1e-10)k for k >= 1e22
Argument: Kevin Russell with GPT Astra. Audit: Ford (verifier pass, 2026-11-02).
Status: **no gap found** in a line-by-line re-derivation. Every inequality re-derived; every numeric constraint checked in exact rational arithmetic. This is still not a substitute for independent human review.

## Setup
Row x_1..x_k of distinct integers in [1,N], any order, all block sums distinct. Suppose N <= (3/2+eps)k, k >= K. s_j are prefix sums.

## Gap hunt, item by item
1. **Multiset vs set.** Block sums are pairwise distinct by hypothesis, so the multiset of sums of length <= h *is* a set of m distinct positive integers. The sum bound m(m+1)/2 is valid. Distinct singletons give distinct entries, so the Smax = kN - k(k-1)/2 bound is valid. OK.
2. **Step 1 (S bound).** Each entry x_i lies in at most T = h(h+1)/2 blocks of length <= h (exactly T for interior i). Sum of all block sums is <= T*S, and that sum is >= m(m+1)/2. So S >= m(m+1)/(h(h+1)), with m = hk - h(h-1)/2.
   With h = floor(sqrt k), S >= k^2 - 2k^{3/2} + k. This was checked exactly for every k <= 20000 and for k = 10^12+7 and 10^15+3 (check_constants.py), and it follows analytically as well. OK.
3. **Step 2 (deficit, B, L, q).**
   - E = Smax - S <= eps k^2 + 2k^{3/2} + k/2 <= 2 eps k^2 for k >= K (A1).
   - Sorting gives y_j <= B+j-1 with B = N-k+1, and E = sum(B+j-1-y_j) with all terms >= 0. OK.
   - From S <= Smax we get B >= k/2 - 2sqrt k + 1/2. With L = ceil((1/2-eta)k) <= (1/2-eta)k + 1, B - L >= eta k - 2sqrt k - 1/2 >= eta k/2 (A2).
   - A bad entry y_j <= L-1 contributes B+j-1-y_j >= B-L+1 > B-L. So q <= E/(B-L) <= 4 eps k/eta = k/250000. OK.
   - **L > 0:** L >= (1/2-eta)k > 0. Retained sums avoid bad entries, so every retained block sum is >= one good entry >= L. OK.
4. **Step 3 (packing displacement).**
   - At most T*q blocks of length <= h contain a bad entry (each entry is in <= T blocks). So d = hk - M <= h(h-1)/2 + Tq <= 28 + 36q, and d/k <= 28/K + 36/250000 <= 1/6000 (A3).
   - Distinct integers z_j >= L give z_j >= L+j-1. Delta = sum(z_j - (L+j-1)) >= 0.
   - Delta <= T*S - ML - M(M-1)/2. Expanding with M = hk - d and L >= (1/2-eta)k, the k^2 terms cancel (T - h/2 - h^2/2 = 0). This leaves (T eps + h eta)k^2 + (h+1/2-eta)dk - d^2/2 + (T+h)k/2 - d/2.
   - Re-derived exactly. check_delta_symbolic.py (sympy) shows Astra's expansion is an *identity* for general h: the difference is 0. So the expansion is correct, and dropping -d^2/2, -d/2 and -eta dk only loosens it. At h = 8: Delta/k^2 <= 36eps + 8eta + 17/12000 + 22/K <= 9/4000 (A4). For h < 8 every term is smaller. OK.
5. **Step 4 (Lemma; discarded-block and Riemann errors).** |F_h(f) - int_{1/2}^{h+1/2} f| is bounded by four pieces:
   - (i) discarded blocks: <= d/k, since |f| <= 1.
   - (ii) moving z_j to L+j-1: <= Lip*Delta/k^2 <= 10Delta/k^2.
   - (iii) left-endpoint Riemann sum of a Lipschitz function on M unit cells of width 1/k: error <= Lip*M/(2k^2). Astra uses the cruder 10M/k^2 <= 80/k. Conservative.
   - (iv) interval change: |L/k - 1/2| <= eta + 1/k and |(L+M)/k - (h+1/2)| <= eta + 1/k + d/k. So <= 2eta + 2/k + d/k, as stated (|f| <= 1).
   - Total: <= 90/4000 + 2/6000 + 2/10000 + 82/K <= 1/40 (A5). Exact value of the left side is about 0.023033. For h = 0, F_0 = 0 = integral. OK.
6. **Step 5 (signs).**
   - f_r(t) = cos(3pi(t-r)): |f_r| <= 1, Lip = 3pi < 10 (pi < 355/113).
   - The length-r block sums equal B_r minus B_{r-1} as multisets, and they are disjoint because all sums are distinct. So C_r/k = F_r(f_r) - F_{r-1}(f_r). The index range i = 0..k-r gives exactly the k-r+1 blocks of length r. OK.
   - The integral over [r-1/2, r+1/2] is int_{-1/2}^{1/2} cos(3pi t) dt = 2sin(3pi/2)/(3pi) = -2/(3pi) < -1/5. Two lemma errors give +1/20. So C_r/k <= -2/(3pi) + 1/20 < -3/20. The sign is correct: cos(3pi(t-r)) is negative near t = r, which is where the length-r sums concentrate (near r*k, centred at the mean entry k).
7. **Step 6 (window / omitted terms).**
   - Re(u_{t+r} conj u_t) = cos(3pi((s_{t+r} - s_t)/k - r)). This is the C_r summand. OK.
   - There are k-7 windows (i = 0..k-8). Diagonal = 9(k-7).
   - For lag r and offset a (0 <= a <= 8-r, so 9-r offsets), the partial sum runs over t = a..k-8+a. It omits t = 0..a-1 and t = k-7+a..k-r, which is a + (8-r-a) = 8-r terms of C_r. Each omitted cos >= -1, so partial <= C_r + (8-r).
   - Sum: Q <= 9(k-7) + 2sum(9-r)C_r + 2sum(9-r)(8-r) = 9k + 2sum(9-r)C_r + 273, using sum(9-r)(8-r) = 168 and -63 + 336 = 273. With sum(9-r) = 36: Q <= 9k - 72*(3/20)k + 273 = -9k/5 + 273 < 0. This contradicts Q >= 0. OK.
8. **Off-by-ones.** All were checked: m, T, d, B, L, the C_r range, the window count, the omitted count. None changes a constant beyond the stated slack.
9. **Corollary slack (12 sqrt k).**
   - For k >= K the main theorem applies.
   - For k < K: step 1 + Smax give kN - k(k-1)/2 >= k^2 - 2k^{3/2} + k, so N >= 3k/2 + 1/2 - 2sqrt k. We need (3/2+eps)k - 12sqrt k <= 3k/2 + 1/2 - 2sqrt k, i.e. eps*k <= 10sqrt k + 1/2. This holds because eps*sqrt k < eps*sqrt K = 10. Since a(k) is an integer, the ceiling is free.
- Small k: the max{k, .} term and integrality cover it. Checked at the boundary: eps*K = 10^12 <= 10*10^11 + 1/2. OK.
   - Note: the step-1 S bound used in the corollary is the *refined* S >= k^2 - 2k^{3/2} + k, which gives B >= k/2 - 2sqrt k + 1/2. OK.
10. **Monotonicity in k.** Every constraint has the form constant +- (positive)/sqrt k or /k, with the k-dependent side shrinking as k grows. Validity at K implies validity for all k >= K. Spot-checked exactly up to 1e32.

## Exact checks (check_constants.py -> check_constants.out): ALL PASS
A1-A5 pass at K = 1e22. So do the hidden identities (17/12000, 22, 273, -9/5, 36, 168), the pi bounds via 355/113, the exact step-1 chain, and the corollary slack.

## Numerical sanity (numerics.py -> numerics.out), 50-digit mpmath
- k=19, N=29 witness `4 1 2 10 22 15 21 24 28 29 27 16 26 20 18 23 25 19 11`:
  - admissible;
  - Q = 78.70206 and |Q - (9(k-7) + 2*cross)| = 3e-48;
  - max over (r,a) of partial - (C_r + 8 - r) = 0, attained at r = 8 where nothing is omitted;
  - Q <= 9k + 2sum(9-r)C_r + 273 = 390.30.
  - C_r/k are mixed sign at k = 19. This is expected: the lemma needs k >= K.
- Every admissible row at N = a(k) for k = 9, 10, 11, 12 (exhaustive; 74 + 6 + 2 + 94 ordered rows), and 400 random greedy admissible rows with k >= 9: the identity, the partial bounds and the Q bound all hold.

## Literature / novelty
- arXiv 2610.36207 (Carter–O'Bryant–Tao 2026, Sidon-set diameter) and arXiv 2608.13739 (Ma–Yi, Golomb-ruler difference packings, one-frequency Fourier obstruction): both exist and are described accurately. Neither addresses A364153.
- OEIS A364153 lists no improvement over Hegyvári's 3/2.
- erdosproblems.com/357 (edited 2026-01-12) states that Coppersmith–Phillips [867] "implies g(n) <= (2/3 - 1/512 + o(1))n" for the any-order g. Taken literally, that would give a(k) >= (1536/1021)k ≈ 1.50441k, far stronger than 3/2 + 1e-10.
  - However, CP (SIAM J. Discrete Math 1996; abstract: "increasing sequence ... x_i+...+x_j = x_k") is about increasing sequences.
  - Forum comment by Adenwalla (2026-04-09): "The description applies this upper bound to g(n) but I believe it should only apply to f(n)." It is not yet corrected on the page.
  - An any-order row's value set need not satisfy CP's sorted-order condition, so there is no direct implication. Lenthall-Cleary's preprint (2026-07-26) also cites CP for f only.
  - **Any write-up must address this explicitly.**
- The forum's proof claims (Lenthall-Cleary f(n) <= n/2 + O(n^{2/3}); Pickhardt/Paratelligent, Aug 2026) both explicitly use increasing order. Neither touches the any-order g / A364153.
- No 2025–2026 any-order improvement over Hegyvári's 2/3 (equivalently 3/2) was found. Within this search the result appears new, and it would be the first any-order improvement of the constant if it survives review.

## Optional eps improvement (verify_eps_exact.py, exact Fractions)
I kept the same proof structure but used per-h error bounds (rather than h = 8 everywhere), Lip <= 3*355/113, and sigma >= 2/(3*355/113).
- eps = 4e-8 (alpha = 3pi, 9 equal weights, eta ≈ 7.5e-4) closes at K = 1e22 exactly: Q/k bound -0.118.
- eps = 6e-8 (alpha = 8.9 with rigorous interval sin, n = 10, rational sine weights, eta ≈ 8.4e-4): Q/k bound -0.213.
- eps = 1e-10 already closes at K = 1e16 in the tightened bookkeeping.
- These are my own tightened bookkeeping, not Astra's text. They need the same human check, and they would change the corollary's sqrt k constant (12 becomes about eps*sqrt K + 2).

## Reviewer concerns raised and resolved
- GLM (truncated run 1) briefly flagged a "260k vs 22k" discrepancy in the step-3 bound. That comes from setting M = 8k-28 while calling it d = 0. Under Astra's definition d = hk - M we have d >= h(h-1)/2 = 28, and the (h+1/2)dk = 238k term carries the rest: 238k + 22k = 260k. Resolved by check_delta_symbolic.py.
- DeepSeek (truncated run 1) briefly suspected a factor error in "-9k/5". Its own recomputation then gave 9k - 54k/5 = -9k/5. No error.
- Nemotron (truncated run 1) re-derived the h=1 and h=2 cases of the step-3 expansion and found them matching. It raised no gap before truncation.

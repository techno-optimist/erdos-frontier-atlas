# Independent review: P699 even-i, d=3 completion

## Verdict

**PASS as an informal mathematical deduction. No mathematical gap found in the new completion.** Using the already-reviewed non-diagonal result supplied in `699/REVIEW.md`, and Nagura's cited prime-interval theorem, the argument proves:

> For every even integer `i >= 2` and every integer `j > i`, with `n = 2j + 3`, there is a prime `p >= i` dividing both `C(n,i)` and `C(n,j)`.

This is a limited independent audit, not formal verification, a novelty assessment, an upstream-acceptance claim, or a solution of the full problem. The all-parameter non-diagonal result is an explicit supplied lemma here; its EEES/localization proof was not independently re-audited in this task.

## Material reviewed

- `experiments/astra-briefcase-20260904/699/diagonal-completion.md`.
- The `d=3` statement and argument in the adjacent `result.md`, and the supplied adjacent `REVIEW.md`.
- `the externally retained rendering of the cited journal page`: independent visual reading confirms that Panaitopol's introduction prints **`x >= 25` and a prime in `[x,(6/5)x)`**. The left endpoint is inclusive and the right endpoint is strict.
- Cited secondary source: L. Panaitopol, *Intervals containing prime numbers*, NNTDM 8 (2002), 145–148, introduction, p.145: https://nntdm.net/papers/nntdm-08/NNTDM-08-4-145-148.pdf . Nagura citation: https://doi.org/10.3792/pja/1195570997 . This audit checks the rendered secondary statement, not Nagura's original proof or the downloaded PDF's hash.

## Mathematical checks

### 1. Prime-window lemma: valid, with the stated strict lower endpoint

Assume `2 <= i < j <= n/2` and `n-i < p <= n`, with `p` prime. Since `i <= n/2`, one has `p > n-i >= n/2`; hence `2p > n` and `p^2 >= 2p > n`. Thus `v_p(n!) = 1`.

All four denominator arguments are at most `n-i`:

- `i <= n-i`;
- `j <= n/2 <= n-i`;
- `n-j < n-i`;
- `n-i < p` by hypothesis.

Their factorials therefore have zero p-adic valuation, and

`v_p(C(n,i)) = v_p(C(n,j)) = 1`.

Also `p > n-i >= n/2 >= j > i`, stronger than the required `p >= i`. The upper equality `p=n` is permitted and is needed by the stated finite choice at `i=4`.

The lower inequality cannot be weakened to `n-i <= p`: the direct negative control `(n,i,j,p)=(7,2,3,5)` gives `C(7,2)=21`, `C(7,3)=35`, so this prime does not divide both.

### 2. Residual diagonal and Nagura endpoints: exact and sufficient

When `j=2i-1` and `n=2j+3`, substitution gives `n=4i+1` and `n-i=3i+1`. The standing domain holds: `j-i=i-1>0`, and `n/2-j=3/2>0`.

For even `i>=8`, choose `x=3i+2`. Then `x>=26>=25`. The printed theorem gives

`3i+2 <= p < (6/5)(3i+2)`.

The required lower margin is exactly

`x-(n-i)=1`.

The upper margin is exactly

`n-(6/5)x = (4i+1)-(18i+12)/5 = (2i-7)/5 >= 9/5 > 0`.

Consequently

`n-i < x <= p < (6/5)x < n`.

At the first case `i=8`, these bounds are `25 < 26 <= p < 156/5 < 33`. There is no dependence on a strict left endpoint in Nagura's statement. Using `x=3i+1` would not, by itself, produce the strict lower inequality required by the lemma; the deliberate shift in the submitted proof avoids that issue. The prime-window lemma therefore covers every residual diagonal with even `i>=8`, whether or not `i+1` is prime.

### 3. Finite diagonal cases: both choices verified directly

| i | j | n | p | C(n,i) | C(n,j) | C(n,i)/p | C(n,j)/p |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 7 | 17 | 17 | 2380 | 19448 | 140 | 1144 |
| 6 | 11 | 25 | 23 | 177100 | 4457400 | 7700 | 193800 |

Both witnesses are prime, satisfy `n-i < p <= n`, and qualify as `p>=i`. These are precisely the even `i>=4` cases below the Nagura threshold used here.

### 4. i=2 cancellation: valid without any prime-distribution input

For `j>=3`, put `n=2j+3`, `g=gcd(n,j)=gcd(3,j)` and `m=n/g`. Dividing

`j*C(n,j) = n*C(n-1,j-1)`

by `g` yields

`(j/g)*C(n,j) = m*C(n-1,j-1)`.

Since `gcd(j/g,m)=1`, Euclid's lemma gives `m | C(n,j)`. There is no illicit cancellation of a possibly noncoprime factor.

The integer `n` is odd, so `C(n,2)=n*((n-1)/2)` and therefore `m | n | C(n,2)`. Also `g` is either 1 or 3 and `n>=9`, so `m>=n/3>=3`. In fact `m` is odd. Hence it has a prime divisor `p>=3>=i`, and that prime divides both binomials. At the smallest case `j=3`, `n=9` and `m=3`, so the endpoint is included.

### 5. Coverage and proof dependencies

The branches exhaust the asserted domain:

1. `i=2`: the cancellation argument covers every `j>i`.
2. Even `i>=4`, `j!=2i-1`: the supplied non-diagonal lemma applies.
3. Even `i>=4`, `j=2i-1`: the two finite cases and Nagura argument apply.

No extra exception or uncovered endpoint remains. The new diagonal argument and the `i=2` argument do not use EEES; that dependency is inherited only through the supplied non-diagonal theorem. Odd `i` on `d=3`, other values of `d`, and the separate claims concerning `d=1,2` are not established or re-audited here.

## Bounded independent execution

A fresh in-memory Python checker used `math.comb`, `math.gcd`, exact `fractions.Fraction` bounds, and an independently generated Eratosthenes prime list through 1201. It did not run or import the author's checker, and did not use the author's receipt as its oracle. Exact binomial integers supplied all divisibility checks.

Actual execution returned **PASS**, exit code **0**, with these programmatically counted domains:

- **109,937 prime-window quadruples** `(n,i,j,p)`: every `6<=n<=100`, `2<=i<j<=floor(n/2)`, and every prime `n-i<p<=n`. Both direct binomial valuations were exactly one in every case.
- **15,500 d=3 triples**: every `3<=j<=250` and every even `2<=i<j`, with `n=2j+3`. Every exact binomial gcd had a directly verified prime divisor `p>=i`. This included **62** triples on `j=2i-1`.
- **147 Nagura diagonal instances**: every even `8<=i<=300`. Exact rational endpoint assertions passed, and every prime in each interval `[3i+2,(6/5)(3i+2))` divided both binomials. Every interval was nonempty in this bounded range. The minimum checked upper margin was `9/5`.
- **2 finite diagonal witnesses**: the complete integer values and quotients are shown above.
- **998 i=2 instances**: every `3<=j<=1000`. Checked both binomial identities, `g=gcd(3,j)`, coprimality after cancellation, `n | C(n,2)`, and divisibility of both binomials by `m`. Minimum observed `m`: **3**.
- The deliberately weakened lower-endpoint condition was rejected by the `(7,2,3,5)` counterexample above.

The checker produced **126,584 distinct tagged records**; the sum and deduplicated count agreed. Tags distinguish suites, so this is not a claim of that many distinct untagged triples. SHA-256 of the ordered compact-JSON execution records:

`31b4a3331e1fc3ea3f2a4b78c3047559f4da16579c8e6c0fda06cef4426ee2dc`

The records were held in the tool's execution kernel, not persisted as a separate certificate. These bounded computations are independent consistency and boundary checks, not the proof of the unbounded theorem.

## Files and issues

Created only this report, `this report`. No repository files, code, prior reports, receipts, or external state were modified. No blocking issue or mathematical correction was found. The material limitation is the explicitly authorized reliance on the already-reviewed non-diagonal lemma and the cited classical prime-interval theorem; no broader claim is made.

Local filesystem paths were normalized for publication.

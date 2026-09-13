# P699: completing the even-i third diagonal

**Informal corollary, not a full-problem solution or novelty claim.** This supplements [the adjacent-binomial proof](result.md), whose even-i, d=3 argument stopped at j=2i−1. No existing receipt or statement is silently changed.

## A prime-window lemma

If 2≤i<j≤n/2 and a prime p satisfies n−i<p≤n, then p divides both C(n,i) and C(n,j), and p≥i. Indeed p>n/2, so n! contains one multiple of p. Every argument of the four denominator factorials i!, (n−i)!, j!, (n−j)! is less than p. Thus both binomial valuations are one.

## Remove the residual diagonal for even i≥4

On the previously excluded diagonal,

    j=2i−1,    n=4i+1,    n−i=3i+1.

Use Nagura's classical prime-interval theorem.[1] The printed statement reproduced in Panaitopol's introduction is the slightly weak form: for x≥25 there is a prime in **[x,(6/5)x)**.[2] The interval endpoints and fraction were checked on the rendered journal page rather than its damaged OCR.

For even i≥8, take **x=3i+2**, so x≥26. The resulting prime satisfies

    n−i < 3i+2 ≤ p < (6/5)(3i+2) < 4i+1 = n,

because the last gap is (2i−7)/5>0. The prime-window lemma applies. The shift by +2, rather than +1, deliberately avoids relying on a strict left endpoint in the cited version.

For the remaining i=4,6, use respectively p=17 at (n,i,j)=(17,4,7), and p=23 at (25,6,11). Their divisibility was checked directly. Combining this with the prior non-diagonal theorem proves the d=3 claim for every even i≥4.

## Include i=2 without any prime-interval theorem

Now let i=2, j≥3, n=2j+3. Set g=gcd(n,j)=gcd(3,j) and m=n/g. The identity

    j C(n,j) = n C(n−1,j−1)

and gcd(j/g,m)=1 imply m divides C(n,j). Since n is odd, n divides C(n,2), so m also divides C(n,2). Moreover m≥n/3≥3. Any prime factor of m is therefore a qualifying common prime.

## Completed corollary

For **every even integer i≥2**, every j>i, and n=2j+3, some prime p≥i divides both C(n,i) and C(n,j).

Together with the first note and the adjacent-binomial proof, the verified informal deductions now cover all i≥2 on d=1 and d=2, and all even i≥2 on d=3. The odd-i, d=3 cases are **not** settled by this corollary.

`diagonal-completion-checks.json` records the two finite diagonal cases, exact rational endpoint-margin coefficients, 998 direct checks of the i=2 identity (3≤j≤1000), and the downloaded reference PDF's hash. Those finite checks do not replace the argument or the cited prime-interval theorem. The copyrighted PDF itself is not bundled.

## Sources

[1] https://doi.org/10.3792/pja/1195570997 — Jitsuro Nagura, *On the interval containing at least one prime number* (1952).
[2] https://nntdm.net/papers/nntdm-08/NNTDM-08-4-145-148.pdf — Laurențiu Panaitopol, *Intervals containing prime numbers*, NNTDM 8 (2002), 145–148; introduction, p.145.

# Campaign: crack P699 by i, then stop pretending the size bound works forever

Not a solution of #699. Live page remains FALSIFIABLE.

## Why this cut

The Pascal identity
\[
j^{\underline{i}}\binom nj = n^{\underline{i}}\binom{n-i}{j-i}
= i!\binom ni\binom{n-i}{j-i}
\]
plus coprime cancellation says: if \(\gcd(\binom ni,\binom nj)=1\) then \(\binom ni\) divides \(j^{\underline{i}}\).
On \(j\le n/2\) the size comparison \(\binom ni > j^{\underline{i}}\) is
\[
\frac{n^i}{i!} \;\text{vs}\; \Bigl(\frac n2\Bigr)^i
\qquad\text{i.e.}\qquad 2^i > i!.
\]
That inequality holds **only for \(i\le 3\)**. So i=2 and i=3 are the last elementary slices. i=4 already fails the bound (\(20,j=10\): \(4845<5040\)).

| i | Status | What's left |
|---|---|---|
| 2 | kernel-checked gcd ≥ 2 for every pair | prime-factor Init gap only |
| 3 | this lane: gcd ≥ 2 every pair; gcd odd (hence ≥ 3) when n≡3 (mod 4) | n≢3 (mod 4): prove the gcd is not a 2-power |
| ≥ 4 | size bound dead | primes, EEES, localization |

## This lane's theorem

For \(4\le j\) and \(2j\le n\),
\[
\gcd\Bigl(\binom n3,\binom nj\Bigr)\ge 2.
\]
If additionally \(n\equiv 3\pmod 4\), then \(\binom n3\) is odd, so the gcd is odd and therefore \(\ge 3\). That is the i=3 prime condition on a positive-density set of n.

## Residual (next crack, not this PR)

When \(n\not\equiv 3\pmod 4\), \(\binom n3\) is even. No 2-power gcd appears in \(8\le n\le 120\) (3249 pairs). Need: odd part of \(\binom n3\) cannot divide \(j^{\underline{3}}\) unless it already shares an odd prime with \(\binom nj\).
